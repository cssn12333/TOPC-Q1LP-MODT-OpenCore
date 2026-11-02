"""Relink one bounded function into a pinned kext; emulate before deployment.

LLVM's Mach-O linker does not implement -kext. This preserves the upstream
kext and its layout, replacing only a source-compiled identification function,
adjusting its existing IOLog relocation and assigning a distinct UUID.
"""
from pathlib import Path
import hashlib, json, random, struct, sys, uuid

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / '.build/rtl8168m'
HERE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'tools/emulation'))
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from unicorn import Uc, UC_ARCH_X86, UC_MODE_64, UC_HOOK_CODE
from unicorn.x86_const import *


class MachO:
    def __init__(self, data):
        self.data = bytes(data)
        assert self.data[:4] == b'\xcf\xfa\xed\xfe'
        self.sections = []; self.segments = []; self.sym = []; self.dysym = None
        pos = 32
        for _ in range(struct.unpack_from('<I', self.data, 16)[0]):
            cmd, size = struct.unpack_from('<II', self.data, pos)
            if cmd == 0x19:
                name = self.data[pos+8:pos+24].split(b'\0')[0].decode()
                vm, vmsize, fileoff, filesize = struct.unpack_from('<QQQQ', self.data, pos+24)
                self.segments.append((name, vm, vmsize, fileoff, filesize))
                nsects = struct.unpack_from('<I', self.data, pos+64)[0]
                for i in range(nsects):
                    off = pos + 72 + 80*i
                    name = self.data[off:off+16].split(b'\0')[0].decode()
                    addr, length, offset, align, reloff, nrel = struct.unpack_from('<QQIIII', self.data, off+32)
                    self.sections.append(dict(name=name,addr=addr,size=length,offset=offset,reloff=reloff,nrel=nrel))
            elif cmd == 2:
                symoff, nsyms, stroff, strsize = struct.unpack_from('<IIII', self.data, pos+8)
                strings = self.data[stroff:stroff+strsize]
                for i in range(nsyms):
                    idx, typ, sect, desc, value = struct.unpack_from('<IBBHQ', self.data, symoff+16*i)
                    name = strings[idx:].split(b'\0')[0].decode()
                    self.sym.append(dict(name=name,type=typ,sect=sect,value=value))
            elif cmd == 0xb:
                self.dysym = struct.unpack_from('<20I', self.data, pos)
            elif cmd == 0x1b:
                self.uuid_offset = pos + 8
            pos += size

    def fileoffset(self, vm):
        for _, base, _, off, size in self.segments:
            if base <= vm < base+size: return off+vm-base
        raise ValueError(hex(vm))

    def section(self, name): return next(s for s in self.sections if s['name']==name)

    def relocations(self, section):
        result=[]
        for i in range(section['nrel']):
            off=section['reloff']+8*i
            address, info=struct.unpack_from('<iI', self.data, off)
            result.append(dict(offset=off,address=address,symbol=info&0xffffff,pcrel=(info>>24)&1,length=(info>>25)&3,external=(info>>27)&1,type=info>>28))
        return result


binary = ROOT / 'vendor/upstream-original/RealtekRTL8111'
original = MachO(binary.read_bytes())
SYMBOL='__Z23rtl8168_get_mac_versionP15rtl8168_privatePVv'
entry=next(s['value'] for s in original.sym if s['name']==SYMBOL)
following=min(s['value'] for s in original.sym if s['sect']==1 and s['value']>entry)
length=following-entry
assert entry==0x4358 and length==0x4b2
functionoff=original.fileoffset(entry)
decoder=Cs(CS_ARCH_X86,CS_MODE_64)
oldinstructions=list(decoder.disasm(original.data[functionoff:functionoff+length],entry))
oldcall=next(i for i in oldinstructions if i.mnemonic=='call')
assert oldcall.address==0x4696 and oldcall.size==5


def relink(objpath):
    obj=MachO(objpath.read_bytes());section=obj.section('__text')
    payload=bytearray(obj.data[section['offset']:section['offset']+section['size']])
    assert len(payload)<=length
    callrel=None
    for rel in obj.relocations(section):
        assert rel['length']==2 and rel['pcrel']==1
        at=rel['address']
        if rel['external']:
            assert rel['type']==2 and obj.sym[rel['symbol']]['name']=='_IOLog'
            assert payload[at-1]==0xe8
            callrel=rel
        else:
            assert rel['type']==1
            target=obj.sections[rel['symbol']-1]
            assert target['name']=='__cstring'
            olddisp=struct.unpack_from('<i',payload,at)[0]
            literaloffset=(at+4+olddisp)-target['addr']
            literal=obj.data[target['offset']+literaloffset:].split(b'\0')[0]+b'\0'
            assert literal==b'unknown chip version (%x)\n\0'
            literalfile=original.data.index(literal)
            literalvm=next(vm+literalfile-off for _,vm,_,off,size in original.segments if off<=literalfile<off+size)
            struct.pack_into('<i',payload,at,literalvm-(entry+at+4))
    assert callrel is not None
    linked=bytearray(original.data)
    linked[functionoff:functionoff+length]=payload+b'\x90'*(length-len(payload))
    # The kext loader resolves the existing IOLog external relocation at its new site.
    extreloff,count=original.dysym[16:18];hits=[]
    for i in range(count):
        pos=extreloff+8*i
        addr,info=struct.unpack_from('<iI',linked,pos)
        if addr==oldcall.address+1:
            assert (info>>27)&1 and (info>>28)==2
            assert original.sym[info&0xffffff]['name']=='_IOLog'
            struct.pack_into('<i',linked,pos,entry+callrel['address'])
            hits.append(pos)
    assert len(hits)==1
    callsite=entry+callrel['address']-1
    return linked,callsite,hits[0],len(payload)


compiled_original, reference_call, _, original_size = relink(HERE/'identification-original.o')
patched, patched_call, relocation_offset, patched_size = relink(HERE/'identification-rtl8168m.o')

# Hardware-free differential tests: compare all writes to the real structure and
# MMIO image, and verify the callee-saved ABI for each chip signature.
CODE=0x100000; DATA=0x300000; MMIO=0x400000; STACK=0x500000; STOP=0x600000
rng=random.Random(0x8168)
initial_data=bytes(rng.randrange(256) for _ in range(4096))
initial_mmio=bytes(rng.randrange(256) for _ in range(4096))
callee=[UC_X86_REG_RBX,UC_X86_REG_RBP,UC_X86_REG_R12,UC_X86_REG_R13,UC_X86_REG_R14,UC_X86_REG_R15]


def emulator(image,call):
    uc=Uc(UC_ARCH_X86,UC_MODE_64)
    uc.mem_map(CODE,0x100000);uc.mem_write(CODE,bytes(image))
    for base in [DATA,MMIO,STACK,STOP]:uc.mem_map(base,4096)
    def skip_log(u,address,size,data):
        if address==CODE+call:u.reg_write(UC_X86_REG_RIP,address+5)
    uc.hook_add(UC_HOOK_CODE,skip_log,begin=CODE+call,end=CODE+call)
    return uc


def run(uc,tx):
    uc.mem_write(DATA,initial_data);uc.mem_write(MMIO,initial_mmio)
    uc.mem_write(MMIO+0x40,struct.pack('<I',tx))
    uc.mem_write(STACK+0xff8,struct.pack('<Q',STOP))
    uc.reg_write(UC_X86_REG_RSP,STACK+0xff8)
    uc.reg_write(UC_X86_REG_RDI,DATA);uc.reg_write(UC_X86_REG_RSI,MMIO)
    for i,reg in enumerate(callee):uc.reg_write(reg,0xaabb0000+i)
    uc.emu_start(CODE+entry,STOP,count=2000)
    assert uc.reg_read(UC_X86_REG_RIP)==STOP
    assert uc.reg_read(UC_X86_REG_RSP)==STACK+0x1000
    assert all(uc.reg_read(reg)==0xaabb0000+i for i,reg in enumerate(callee))
    return bytes(uc.mem_read(DATA,4096)),bytes(uc.mem_read(MMIO,4096))


old=emulator(original.data,oldcall.address)
reference=emulator(compiled_original,reference_call)
new=emulator(patched,patched_call)
h2=run(old,0x54100000)[0]
assert struct.unpack_from('<I',h2,0x20)[0]==29  # CFG_METHOD_30, zero-based enum.
tests=[x<<20 for x in range(2048)]+[rng.randrange(2**32) for _ in range(512)]
normal=0;extended=0
for tx in tests:
    expected=run(old,tx)
    assert run(reference,tx)==expected, 'Pinned source/SDK does not reproduce the upstream binary ABI'
    actual=run(new,tx)
    if tx&0x7cf00000==0x6c000000:
        assert actual[0]==h2
        assert actual[1]==expected[1]
        extended+=1
    else:
        assert actual==expected,hex(tx)
        normal+=1

new_uuid=uuid.UUID(bytes=hashlib.sha256(patched).digest()[:16]).bytes
patched[original.uuid_offset:original.uuid_offset+16]=new_uuid
allowed=set(range(functionoff,functionoff+length))|set(range(relocation_offset,relocation_offset+4))|set(range(original.uuid_offset,original.uuid_offset+16))
assert all(a==b or i in allowed for i,(a,b) in enumerate(zip(original.data,patched)))
# The upstream binary is signed. A modified image must not retain a stale
# embedded signature. Remove only LC_CODE_SIGNATURE, leaving file/VM offsets
# intact, and clear its now-unreferenced trailing data. OC injects unsigned kexts.
pos=32
signature=None
commands=struct.unpack_from('<I',patched,16)[0]
commandbytes=struct.unpack_from('<I',patched,20)[0]
for _ in range(commands):
    cmd,size=struct.unpack_from('<II',patched,pos)
    if cmd==0x1d:
        assert size==16
        signature=(pos,*struct.unpack_from('<II',patched,pos+8))
        break
    pos+=size
assert signature is not None
commandpos,sigoff,sigsize=signature
assert sigoff>=max(s['offset']+s['size'] for s in original.sections)
headerend=32+commandbytes
patched[commandpos:headerend-16]=patched[commandpos+16:headerend]
patched[headerend-16:headerend]=b'\0'*16
struct.pack_into('<I',patched,16,commands-1)
struct.pack_into('<I',patched,20,commandbytes-16)
patched[sigoff:sigoff+sigsize]=b'\0'*sigsize
check=MachO(patched)
assert check.sections==original.sections and check.sym==original.sym
assert run(emulator(patched,patched_call),0x6c000000)[0]==h2
out=HERE/'RealtekRTL8111-RTL8168M-experimental'
out.write_bytes(patched)
report={'experimental':True,'method':'One source-compiled bounded function relink; not a full kext link. LLVM ld64.lld does not support -kext.','upstream_commit':'a3dad34ed4f1e72805ce42f6d506f6917fdf79a0','linux_reference':'39f59c72ad3a1eaab9a60f0671bc94d2bc826d21','original_binary_sha256':hashlib.sha256(original.data).hexdigest(),'patched_binary_sha256':hashlib.sha256(patched).hexdigest(),'new_uuid':str(uuid.UUID(bytes=new_uuid)).upper(),'function_VM':hex(entry),'original_span':length,'compiled_original_size':original_size,'compiled_patched_size':patched_size,'external_relocation_moved_from':hex(oldcall.address+1),'external_relocation_moved_to':hex(patched_call+1),'differential_cases':len(tests),'unchanged_cases':normal,'XID6c0_H2_cases':extended,'hardware_XID_confirmed':False,'macOS_hardware_tested':False,'status':'PASS_STATIC_AND_EMULATION_ONLY'}
(ROOT/'.build/rtl8168m-verification.json').write_text(json.dumps(report,indent=2))
report['stale_embedded_signature_removed']=True
report['signature_state']='Unsigned local experimental kext for OpenCore injection; SIP unchanged.'
(ROOT/'.build/rtl8168m-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
