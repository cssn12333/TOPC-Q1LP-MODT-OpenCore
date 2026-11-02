from pathlib import Path
import hashlib, urllib.request, zipfile
root=Path(__file__).resolve().parents[1];out=root/'.build';out.mkdir(exist_ok=True)
url='https://codeload.github.com/acidanthera/MacKernelSDK/zip/3f750085caa17ec3a7880f11c11bf4f48cd6a164'
p=out/'MacKernelSDK.zip'
if not p.exists():
 with urllib.request.urlopen(url,timeout=60) as r:p.write_bytes(r.read())
assert hashlib.sha256(p.read_bytes()).hexdigest()=='f028466e8a18cae2e95724152f915a44afc6352a8a80ae3d85567c55b6c1d60d', 'SDK digest mismatch'
with zipfile.ZipFile(p) as z:z.extractall(out)
print('Pinned SDK ready')
