"""User-run, resumable speech asset downloads. No imports of inference runtimes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'evaluation/speech_downloads.json'
DESTINATION = ROOT / 'models/speech'


def verify(path, item):
    if path.stat().st_size != item['size']:
        raise ValueError(f"Wrong size: {path}")
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    if item.get('sha256'):
        if sha != item['sha256']:
            raise ValueError(f"SHA-256 mismatch: {path}")
    else:
        # Small repository files use Git blob identities, not raw-file SHA-1.
        h = hashlib.sha1(f"blob {item['size']}\0".encode())
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
        if h.hexdigest() != item['git_blob']:
            raise ValueError(f"Git blob mismatch: {path}")
    return sha


def download(item, root, runner=subprocess.run):
    target = (root / item['destination']).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Destination escapes speech folder')
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return verify(target, item)
    partial = target.with_name(target.name + '.part')
    if not partial.exists() or partial.stat().st_size != item['size']:
        runner(['curl.exe', '-L', '--fail', '--retry', '3', '-C', '-', '-o', str(partial), item['url']], check=True)
    sha = verify(partial, item)
    partial.rename(target)
    return sha


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Download files; default only lists plan')
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    print(f"{len(manifest['files'])} files, {sum(f['size'] for f in manifest['files']) / 1e9:.2f} GB; Piper already installed.")
    if not args.download:
        for item in manifest['files']:
            print(item['destination'])
        print('Preview only. Add --download to fetch assets; no inference is performed.')
        return
    records = []
    for item in manifest['files']:
        print(f"Downloading/verifying {item['destination']}", flush=True)
        sha = download(item, DESTINATION)
        records.append({'destination': item['destination'], 'sha256': sha, 'revision': item['revision']})
    receipt = DESTINATION / 'download_receipt.json'
    receipt.write_text(json.dumps({'verified_utc': datetime.now(timezone.utc).isoformat(),
                                  'manifest_sha256': hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                                  'files': records}, indent=2), encoding='utf-8')
    print(f'Speech asset downloads verified: {receipt}')
    print('Model assets only: runtime packages, voice selection and compatibility tests remain pending.')


if __name__ == '__main__':
    main()
