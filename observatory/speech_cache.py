"""Content-addressed gameplay speech reuse; evaluation outputs are untouched."""
import hashlib
import json
from pathlib import Path
from threading import Lock
from uuid import uuid4

from .fixtures import ROOT
from .evaluate_speech import inspect_audio

_hashes = {}
_lock = Lock()


def fingerprint(path):
    stat = path.stat()
    key = (str(path.resolve()), stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
    with _lock:
        if key not in _hashes:
            with path.open('rb') as stream:
                _hashes[key] = hashlib.file_digest(stream, 'sha256').hexdigest()
        return _hashes[key]


def identity():
    """Fingerprint installed assets/worker/runtime metadata without loading models."""
    runtime = ROOT / '.venv-speech-kokoro'
    files = [ROOT / 'scripts/speech_worker.py', runtime / 'Scripts/python.exe',
             ROOT / 'models/speech/kokoro/config.json',
             ROOT / 'models/speech/kokoro/kokoro-v1_0.pth',
             ROOT / 'models/speech/kokoro/voices/af_heart.pt']
    metadata = sorted((runtime / 'Lib/site-packages').glob('*.dist-info/METADATA'))
    if not metadata:
        raise OSError('Speech runtime package metadata unavailable')
    files.extend(metadata)
    return {'version': 'kokoro-gameplay-cache-v1', 'candidate': 'kokoro', 'voice': 'af_heart',
            'seed': 42, 'speed': 1, 'language': 'a', 'device': 'cpu', 'threads': 4,
            'sample_rate': 24000, 'encoding': 'PCM_16',
            'files': {str(p.relative_to(ROOT)): fingerprint(p) for p in files}}


def cache_key(text, configuration):
    payload = json.dumps({'text': text, 'configuration': configuration}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


class SpeechCache:
    def __init__(self, output):
        self.output = Path(output).resolve()
        self.directory = self.output / '_cache'

    def lookup(self, key):
        entry = self.directory / (key + '.json')
        if not entry.exists():
            return None, 'not_found'
        try:
            record = json.loads(entry.read_text(encoding='utf-8'))
            path = (self.output / record['audio']).resolve()
            if record['key'] != key or not path.is_relative_to(self.output):
                raise ValueError('Invalid cache reference')
            metrics = inspect_audio(path)
            if metrics['sha256'] != record['sha256']:
                raise ValueError('Cached audio changed')
            return (path, metrics), None
        except (OSError, ValueError, KeyError, TypeError):
            return None, 'invalid_or_missing_audio'

    def save(self, key, path, sha256):
        self.directory.mkdir(parents=True, exist_ok=True)
        path = Path(path).resolve()
        record = {'key': key, 'audio': str(path.relative_to(self.output)), 'sha256': sha256}
        temporary = self.directory / (key + '-' + uuid4().hex + '.tmp')
        try:
            temporary.write_text(json.dumps(record, indent=2), encoding='utf-8')
            temporary.replace(self.directory / (key + '.json'))
        finally:
            temporary.unlink(missing_ok=True)
