"""Freeze and release reserved model-only intent evaluation. Never downloads models."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
from uuid import uuid4

import httpx

from .fixtures import ROOT
from .held_out import load_reserved, RESERVED, MANIFEST
from .evaluate_intent import evaluate_case, summarise, PROMPTS

DEFAULT_FREEZE = ROOT / 'evaluation/final_intent_freeze.json'
PROTOCOL = ROOT / 'evaluation/final_intent_protocol.txt'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2), encoding='utf-8')


def snapshot():
    files = sorted((ROOT / 'observatory').glob('*.py')) + [RESERVED, MANIFEST, PROTOCOL, ROOT / 'requirements.txt']
    return {'files': {str(p.relative_to(ROOT)): digest(p) for p in files},
            'python': platform.python_version(),
            'packages': {name: importlib.metadata.version(name) for name in ('httpx', 'pydantic')},
            'model': 'qwen3:4b', 'prompt_version': 'v1-json', 'prompt_sha256': hashlib.sha256(PROMPTS['v1-json'][1].encode()).hexdigest(),
            'think': False, 'timeout_seconds': 60, 'repetitions': 1,
            'mode': 'model_only_no_local_guards', 'scoring': 'exact_status_action_target_all_attempts_errors_in_denominator'}


def runtime_identity(client):
    version = client.get('/api/version')
    version.raise_for_status()
    tags = client.get('/api/tags')
    tags.raise_for_status()
    matches = [m for m in tags.json()['models'] if m.get('name') == 'qwen3:4b' or m.get('model') == 'qwen3:4b']
    if len(matches) != 1 or not matches[0].get('digest') or not version.json().get('version'):
        raise ValueError('Installed Qwen identity/runtime version could not be verified')
    return {'ollama_version': version.json()['version'], 'model_digest': matches[0]['digest']}


def freeze(client, path=DEFAULT_FREEZE):
    dataset = load_reserved()
    if path.exists():
        raise ValueError('Freeze already exists; it will not be overwritten')
    value = {'version': 'final-intent-freeze-v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
             'case_count': len(dataset.cases), 'configuration': snapshot(), 'runtime': runtime_identity(client)}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
    return value


def verify(path=DEFAULT_FREEZE):
    value = json.loads(path.read_text(encoding='utf-8'))
    dataset = load_reserved()
    if value.get('version') != 'final-intent-freeze-v1' or value.get('configuration') != snapshot() or value.get('case_count') != len(dataset.cases):
        raise ValueError('Frozen files/settings/environment changed; do not run or silently re-freeze')
    return value, dataset


def run(client, path=DEFAULT_FREEZE, output=ROOT / 'generated/final-intent-evaluations'):
    frozen, dataset = verify(path)
    if runtime_identity(client) != frozen['runtime']:
        raise ValueError('Installed model/runtime differs from the freeze')
    # Durable release marker exists before any inference, including interrupted runs.
    receipt = path.with_suffix('.release.json')
    folder = output / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex[:8])
    receipt.parent.mkdir(parents=True, exist_ok=True)
    with receipt.open('x', encoding='utf-8') as stream:
        json.dump({'freeze_sha256': digest(path), 'output': str(folder), 'status': 'released_do_not_tune_or_rerun'}, stream, indent=2)
    folder.mkdir(parents=True)
    save(folder / 'freeze.json', frozen)
    manifest = {'split': 'held_out', 'planned': len(dataset.cases), 'status': 'running',
                'case_ids': [case.id for case in dataset.cases], 'freeze_sha256': digest(path)}
    save(folder / 'manifest.json', manifest)
    rows = []
    try:
        with (folder / 'results.jsonl').open('x', encoding='utf-8') as stream:
            for case in dataset.cases:
                row = evaluate_case(client, case, 'qwen3:4b', False, 'v1-json')
                stream.write(json.dumps(row) + '\n')
                stream.flush()
                rows.append(row)
                print(f'{len(rows)}/{len(dataset.cases)} recorded', flush=True)
        manifest['status'] = 'completed'
    except KeyboardInterrupt:
        manifest['status'] = 'interrupted'
    except Exception:
        manifest['status'] = 'failed'
        raise
    finally:
        manifest['recorded'] = len(rows)
        save(folder / 'manifest.json', manifest)
        summary = summarise(rows) if rows else {}
        summary.update(status=manifest['status'], planned=len(dataset.cases), recorded=len(rows),
                       complete=len(rows) == len(dataset.cases) and manifest['status'] == 'completed')
        save(folder / 'summary.json', summary)
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--freeze', action='store_true', help='Capture local hashes and Ollama metadata only; no inference')
    mode.add_argument('--verify', action='store_true', help='Offline freeze/integrity check')
    mode.add_argument('--execute', action='store_true', help='Release all reserved cases for one final model run')
    parser.add_argument('--freeze-file', type=Path, default=DEFAULT_FREEZE)
    args = parser.parse_args()
    try:
        if args.verify:
            verify(args.freeze_file)
            print('Freeze verified offline; no model run.')
            return
        with httpx.Client(base_url='http://127.0.0.1:11434', timeout=60, trust_env=False) as client:
            if args.freeze:
                freeze(client, args.freeze_file)
                print(f'Saved freeze (metadata only): {args.freeze_file}')
            else:
                print(f'Saved final intent results: {run(client, args.freeze_file)}')
    except (OSError, ValueError, httpx.HTTPError, KeyError) as exc:
        parser.exit(1, f'{type(exc).__name__}: {exc}\n')


if __name__ == '__main__': main()
