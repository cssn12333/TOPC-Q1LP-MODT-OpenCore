from pathlib import Path
import subprocess, os, shutil

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / '.build/rtl8168m'
HERE.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'vendor/RTL8111-driver-source/RealtekRTL8111'
SDK = ROOT / '.build/MacKernelSDK-3f750085caa17ec3a7880f11c11bf4f48cd6a164/Headers'
CLANG = os.environ.get('CXX') or shutil.which('clang++')
assert CLANG, 'Install LLVM 20.1.8 or set CXX'
RESOURCE = subprocess.check_output([str(CLANG), '-print-resource-dir'], text=True).strip()
text = (SOURCE / 'RealtekRTL8111Linux-804704.cpp').read_text()
start = text.index('void rtl8168_get_mac_version(')
pos = text.index('{', start)
depth = 1
end = pos + 1
while depth:
    if text[end] == '{': depth += 1
    elif text[end] == '}': depth -= 1
    end += 1
function = text[start:end]
extension = '''
        // Experimental backport of Linux commit 39f59c72ad3a:
        // XID 6c0 (RTL8168M) follows RTL8168H-2 (541), method 30.
        // All other identifiers follow the original Mieze implementation.
        if ((val32 & 0x7cf00000U) == 0x6c000000U) {
                tp->mcfg = CFG_METHOD_30;
                tp->efuse_ver = EFUSE_SUPPORT_V3;
                return;
        }
'''
patched = function.replace('        switch (reg) {', extension + '\n        switch (reg) {')
assert patched != function
flags = [str(CLANG), '--target=x86_64-apple-macos10.15', '-std=gnu++17', '-mkernel',
         '-fapple-kext', '-fno-exceptions', '-fno-rtti', '-fno-common', '-mno-red-zone',
         '-fno-builtin', '-fno-jump-tables', '-fno-stack-protector', '-Oz', '-nostdinc',
         '-DKERNEL', '-DKERNEL_PRIVATE', '-DDRIVER_PRIVATE', '-DPRIVATE',
         '-I' + str(SDK), '-I' + str(SOURCE),
         '-isystem', str(Path(RESOURCE) / 'include'),
         '-include', str(SOURCE / 'RealtekRTL8111-V2-Prefix.pch')]
for name, body in [('original', function), ('rtl8168m', patched)]:
    cpp = HERE / ('identification-' + name + '.cpp')
    cpp.write_text('#include "RealtekRTL8111.hpp"\n' + body + '\n')
    output = subprocess.run(flags + ['-c', str(cpp), '-o', str(cpp.with_suffix('.o'))], capture_output=True)
    (HERE / ('compile-' + name + '.log')).write_bytes(output.stdout + output.stderr)
    print(name, 'PASS' if output.returncode == 0 else 'FAIL')
    if output.returncode:
        print(output.stderr.decode(errors='replace')[:3500])
        raise SystemExit(output.returncode)
