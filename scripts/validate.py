from pathlib import Path
import json,hashlib,plistlib,sys
from prepare_audio import verify_payload
r=Path(__file__).resolve().parents[1];c=plistlib.loads((r/'EFI/OC/config.plist').read_bytes())
verify_payload(r/'EFI')
for group,base,key in [('Kernel','OC/Kexts','BundlePath'),('ACPI','OC/ACPI','Path')]:
 for x in c[group]['Add']:
  assert x['Enabled'];assert (r/'EFI'/base/x[key]).exists()
for x in c['UEFI']['Drivers']:
 if x['Enabled']:assert (r/'EFI/OC/Drivers'/x['Path']).is_file()
g=c['PlatformInfo']['Generic'];assert not any(g[x] for x in ['SystemSerialNumber','MLB','SystemUUID']);assert g['ROM']==bytes(6)
assert '-v' not in c['NVRAM']['Add']['7C436110-AB2A-4BBB-A880-FE41995C9F82']['boot-args'].split()
assert c['NVRAM']['Add']['7C436110-AB2A-4BBB-A880-FE41995C9F82']['csr-active-config']==bytes(4)
assert not any(c['Misc']['Debug'][x] for x in ['AppleDebug','ApplePanic','SysReport','Target','DisplayLevel'])
drivers=[x['BundlePath'] for x in c['Kernel']['Add']]
assert drivers.index('Lilu.kext') < drivers.index('AppleALC.kext') < drivers.index('SimpleHDA.kext')
def port_counts(v):
 if isinstance(v,dict):
  for k,x in v.items():
   if k=='ports':yield len(x)
   else:yield from port_counts(x)
assert list(port_counts(plistlib.loads((r/'EFI/OC/Kexts/UTBMap.kext/Contents/Info.plist').read_bytes())))==[15]
m=json.loads((r/'manifest.json').read_text())
for n,s in m.items():assert hashlib.sha256((r/n).read_bytes()).hexdigest()==s,n
print('Public template, active paths, USB count, privacy fields and manifest PASS')
