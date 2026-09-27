"""User-run speech development comparison; no gameplay or automatic downloads."""
import argparse
from array import array
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4
import wave

from .fixtures import ROOT
from .media_fixtures import MEDIA_DATA, load_media

CANDIDATES = {
    'piper': ('.venv', 'en_US-lessac-medium; Piper defaults; seeding unavailable'),
    'kokoro': ('.venv-speech-kokoro', 'af_heart; American English; speed=1; trf=False'),
    'speecht5': ('.venv-speech-hf', 'cmu_us_slt_arctic-wav-arctic_b0258.npy; generation defaults; HiFi-GAN'),
    'mms': ('.venv-speech-hf', 'English built-in single voice; VITS defaults'),
    'xtts': ('.venv-speech-xtts', 'Ana Florence; en; temperature=.75 top_k=50 top_p=.85 repetition_penalty=10 length_penalty=1 speed=1; text splitting'),
}


def write(path, data):
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inspect_audio(path):
    with wave.open(str(path), 'rb') as wav:
        channels, width, rate, frames = wav.getnchannels(), wav.getsampwidth(), wav.getframerate(), wav.getnframes()
        samples = wav.readframes(frames)
    if width != 2 or channels != 1 or rate <= 0 or not frames or len(samples) != frames * 2:
        raise ValueError('Expected nonempty mono PCM16 WAV with complete frames')
    values = array('h', samples)
    if sys.byteorder != 'little':
        values.byteswap()
    if not any(values):
        raise ValueError('Silent audio')
    return {'audio_valid': True, 'duration_seconds': frames / rate, 'sample_rate': rate,
            'channels': channels, 'frames': frames, 'peak_pcm': max(abs(v) for v in values),
            'clipped_sample_fraction': sum(abs(v) >= 32767 for v in values) / len(values), 'sha256': digest(path)}


def run(candidates, output, limit=10, repetitions=2, timeout=300, runner=subprocess.run):
    if not candidates or len(set(candidates)) != len(candidates) or any(c not in CANDIDATES for c in candidates):
        raise ValueError('Select unique known candidates')
    if not 1 <= limit <= 10 or repetitions not in (1, 2) or not 0 < timeout < float('inf'):
        raise ValueError('Use limit 1-10, repetitions 1-2 and finite positive timeout')
    data = load_media()
    for candidate in candidates:
        python = ROOT / CANDIDATES[candidate][0] / 'Scripts/python.exe'
        if not python.is_file():
            raise ValueError(f'Missing interpreter: {python}')
    folder = output / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex[:8])
    folder.mkdir(parents=True)
    # Hash local assets once per run; do not load weights. Retain provenance even on failures.
    artifacts = {}
    dirs = {'piper': ['models/piper'], 'kokoro': ['models/speech/kokoro'],
            'speecht5': ['models/speech/speecht5', 'models/speech/speecht5-hifigan', 'models/speech/speecht5-speakers'],
            'mms': ['models/speech/mms-eng'], 'xtts': ['models/speech/xtts-v2']}
    for candidate in candidates:
        for directory in dirs[candidate]:
            for path in sorted((ROOT / directory).rglob('*')):
                if path.is_file() and not path.name.endswith('.part'):
                    artifacts[str(path.relative_to(ROOT))] = digest(path)
    for name, source in [('dataset.json', MEDIA_DATA), ('protocol.md', ROOT / 'evaluation/media_protocol.txt'),
                         ('worker.py', ROOT / 'scripts/speech_worker.py')]:
        (folder / name).write_bytes(source.read_bytes())
    manifest = {'version': 'speech-development-v1', 'status': 'running', 'dataset_sha256': digest(MEDIA_DATA),
                'artifacts_sha256': artifacts, 'worker_sha256': digest(ROOT / 'scripts/speech_worker.py'),
                'protocol_sha256': digest(ROOT / 'evaluation/media_protocol.txt'), 'schedule': [],
                'timeout': timeout, 'resources': None, 'timing_note': 'Fresh process per attempt. Load includes imports/G2P. Synthesis includes audio encoding; no warm latency claim.'}
    reviews = []
    for repetition in range(repetitions):
        for candidate in (candidates if repetition == 0 else candidates[::-1]):
            for fixture in data.speech[:limit]:
                attempt = f"A{len(manifest['schedule']) + 1:04}"
                target = folder / attempt
                target.mkdir()
                request = {'attempt': attempt, 'candidate': candidate, 'fixture': fixture.id, 'text': fixture.text,
                           'seed': 42 + repetition, 'repetition': repetition + 1, 'voice_settings': CANDIDATES[candidate][1],
                           'torch_threads': None if candidate == 'piper' else 4}
                write(target / 'request.json', request)
                manifest['schedule'].append(request)
                reviews.append({**request, 'audio': f'{attempt}/audio.wav', 'focus_terms': fixture.focus_terms,
                                'reviewer': None, 'date': None, 'word_errors': None, 'pronunciation_issues': None,
                                'intelligibility': None, 'pacing': None, 'content_pass': None, 'notes': ''})
    write(folder / 'manifest.json', manifest)
    write(folder / 'reviews.json', reviews)
    records = []
    try:
        with (folder / 'results.jsonl').open('w', encoding='utf-8') as stream:
            for request in manifest['schedule']:
                target = folder / request['attempt']
                command = [str(ROOT / CANDIDATES[request['candidate']][0] / 'Scripts/python.exe'),
                           str(ROOT / 'scripts/speech_worker.py'), str((target / 'request.json').resolve())]
                write(target / 'command.json', command)
                record = {'attempt': request['attempt'], 'candidate': request['candidate'], 'audio_valid': False,
                          'completed': False, 'listening_review': 'pending'}
                start, interrupted = time.perf_counter(), False
                try:
                    with (target / 'runtime.log').open('w', encoding='utf-8') as log:
                        result = runner(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, timeout=timeout, check=False)
                    record['exit_code'] = result.returncode
                    if (target / 'worker.json').exists():
                        record['worker'] = json.loads((target / 'worker.json').read_text())
                    if result.returncode or not record.get('worker', {}).get('success'):
                        raise ValueError('Worker failed; see worker.json/runtime.log')
                    record['completed'] = True
                    record.update(inspect_audio(target / 'audio.wav'))
                    record['real_time_factor'] = record['worker']['synthesis_seconds'] / record['duration_seconds']
                except KeyboardInterrupt:
                    interrupted = True
                    record['error'] = 'KeyboardInterrupt'
                except (OSError, ValueError, wave.Error, EOFError, subprocess.TimeoutExpired) as exc:
                    record['error'] = f'{type(exc).__name__}: {exc}'
                record['wall_seconds'] = time.perf_counter() - start
                stream.write(json.dumps(record) + '\n')
                stream.flush()
                records.append(record)
                print(f"{request['attempt']} {request['candidate']} {request['fixture']}: audio_valid={record['audio_valid']}", flush=True)
                if interrupted:
                    raise KeyboardInterrupt
        manifest['status'] = 'completed'
    except KeyboardInterrupt:
        manifest['status'] = 'interrupted'
    except Exception:
        manifest['status'] = 'failed'
        raise
    finally:
        write(folder / 'manifest.json', manifest)
        write(folder / 'summary.json', {'status': manifest['status'], 'planned': len(manifest['schedule']),
              'attempted': len(records), 'completed': sum(r['completed'] for r in records),
              'valid_audio': sum(r['audio_valid'] for r in records), 'listening_review': 'pending'})
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', nargs='+', choices=CANDIDATES, required=True)
    parser.add_argument('--limit', type=int, default=10)
    parser.add_argument('--repetitions', type=int, default=2)
    parser.add_argument('--timeout', type=float, default=300)
    args = parser.parse_args()
    folder = run(args.models, ROOT / 'generated/speech-evaluations', args.limit, args.repetitions, args.timeout)
    print(f'Saved speech development results: {folder}')


if __name__ == '__main__':
    main()
