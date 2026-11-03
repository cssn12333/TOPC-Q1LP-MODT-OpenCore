"""Fetch the pinned upstream SimpleHDA privately; do not redistribute its payload."""
from pathlib import Path
import argparse
import hashlib
import io
import json
import plistlib
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'audio.lock.json').read_text(encoding='utf-8'))


def verify_payload(efi):
    for name, digest in LOCK['files'].items():
        path = efi / 'OC/Kexts' / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'{name} missing or changed; run scripts/prepare_audio.py')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--efi', type=Path, default=ROOT / 'EFI')
    parser.add_argument('--archive', type=Path, help='Use the official pinned RELEASE ZIP offline')
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    efi = args.efi.resolve()
    config = plistlib.loads((efi / 'OC/config.plist').read_bytes())
    enabled = [x['BundlePath'] for x in config['Kernel']['Add'] if x['Enabled']]
    order = [enabled.index(x) for x in ('Lilu.kext', 'AppleALC.kext', 'SimpleHDA.kext')]
    if order != sorted(order):
        raise ValueError('Required load order: Lilu -> AppleALC -> SimpleHDA')
    if not args.verify_only:
        if args.archive:
            blob = args.archive.read_bytes()
        else:
            request = urllib.request.Request(LOCK['url'], headers={'User-Agent': 'TOPC-Q1LP-OpenCore'})
            with urllib.request.urlopen(request, timeout=60) as response:
                blob = response.read(LOCK['bytes'] + 1)
        if len(blob) != LOCK['bytes'] or hashlib.sha256(blob).hexdigest() != LOCK['sha256']:
            raise ValueError('Upstream archive size/SHA256 mismatch; nothing installed')
        payload = {}
        with zipfile.ZipFile(io.BytesIO(blob)) as archive:
            for name, digest in LOCK['files'].items():
                if Path(name).is_absolute() or '..' in Path(name).parts or not name.startswith('SimpleHDA.kext/'):
                    raise ValueError('Invalid destination in audio.lock.json')
                data = archive.read(LOCK['archive_prefix'] + name)
                if hashlib.sha256(data).hexdigest() != digest:
                    raise ValueError(f'Upstream file SHA256 mismatch: {name}')
                payload[name] = data
        for name, data in payload.items():
            destination = efi / 'OC/Kexts' / name
            if destination.exists() and destination.read_bytes() != data:
                raise ValueError(f'Refusing to overwrite an unknown existing file: {destination}')
        for name, data in payload.items():
            destination = efi / 'OC/Kexts' / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
    verify_payload(efi)
    print('Pinned SimpleHDA 1.0.0 RELEASE verified; EFI audio dependencies ready.')
    print('Use your own SMBIOS and verify the codec layout before booting. Audio awaits hardware testing.')


if __name__ == '__main__':
    main()
