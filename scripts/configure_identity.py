from pathlib import Path
import argparse, plistlib, re, uuid
p=argparse.ArgumentParser(description='Write your own MacPro7,1 identity to a copied EFI')
p.add_argument('--config',type=Path,required=True);p.add_argument('--serial',required=True);p.add_argument('--mlb',required=True);p.add_argument('--uuid',required=True);p.add_argument('--rom',required=True);p.add_argument('--ethernet-mac')
a=p.parse_args();uuid.UUID(a.uuid)
assert re.fullmatch(r'[0-9a-fA-F]{12}',a.rom),'ROM needs 12 hex digits'
assert a.serial and a.mlb
c=plistlib.loads(a.config.read_bytes());g=c['PlatformInfo']['Generic']
g.update(SystemSerialNumber=a.serial,MLB=a.mlb,SystemUUID=a.uuid.upper(),ROM=bytes.fromhex(a.rom))
a.config.write_bytes(plistlib.dumps(c,sort_keys=False))
if a.ethernet_mac:
 assert re.fullmatch(r'(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}',a.ethernet_mac)
 f=a.config.parent/'Kexts/RealtekRTL8111.kext/Contents/Info.plist';v=plistlib.loads(f.read_bytes())
 v['IOKitPersonalities']['RTL8111 PCIe Adapter']['Driver Parameters']['fallbackMAC']=a.ethernet_mac
 f.write_bytes(plistlib.dumps(v,sort_keys=False))
print('Personal identity configured locally; do not commit the resulting files')
