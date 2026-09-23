"""User-run isolated CPU speech package setup; no synthesis."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROFILES = {'hf': 'common', 'kokoro': 'kokoro', 'xtts': 'xtts'}


def commands(profile, report):
    env = ROOT / f'.venv-speech-{profile}'
    python = env / 'Scripts/python.exe'
    requirements = ROOT / f'evaluation/speech_runtime_{PROFILES[profile]}.txt'
    return [
        [sys.executable, '-m', 'venv', str(env)],
        [str(python), '-m', 'pip', 'install', 'pip==25.3'],
        [str(python), '-m', 'pip', 'install', 'torch==2.8.0', 'torchaudio==2.8.0',
         '--index-url', 'https://download.pytorch.org/whl/cpu'],
        [str(python), '-m', 'pip', 'install', '-r', str(requirements), '--report', str(report / f'{profile}-install.json')],
        [str(python), '-m', 'pip', 'check'],
        [str(python), str(ROOT / 'scripts/check_speech_runtime.py'), profile,
         '--output', str(report / f'{profile}-imports.json')],
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--profile', choices=['all', *PROFILES], default='all')
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 11):
        parser.error('Run with the project Python 3.11 interpreter.')
    profiles = list(PROFILES) if args.profile == 'all' else [args.profile]
    folder = ROOT / 'generated/speech-runtime-setup' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    if not args.install:
        for profile in profiles:
            for command in commands(profile, folder):
                print(subprocess.list2cmdline(command))
        print('Preview only. Add --install to install packages; no speech models are run.')
        return 0
    folder.mkdir(parents=True)
    status = {'profiles': profiles, 'status': 'running', 'commands': []}
    print(f'Setup evidence folder: {folder}', flush=True)
    try:
        for profile in profiles:
            for command in commands(profile, folder):
                status['commands'].append(command)
                print(subprocess.list2cmdline(command), flush=True)
                subprocess.run(command, cwd=ROOT, check=True)
            python = ROOT / f'.venv-speech-{profile}/Scripts/python.exe'
            with (folder / f'{profile}-freeze.txt').open('w', encoding='utf-8') as stream:
                subprocess.run([str(python), '-m', 'pip', 'freeze', '--all'], stdout=stream, check=True)
        status['status'] = 'completed'
    except (OSError, subprocess.CalledProcessError, KeyboardInterrupt) as exc:
        status.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        print(f'Stopped: {exc}. Send the error and evidence folder; no automatic workaround applied.')
    finally:
        (folder / 'setup.json').write_text(json.dumps(status, indent=2), encoding='utf-8')
    print(f"Speech runtime setup {status['status']}: {folder}")
    return 0 if status['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
