"""Optional gameplay speech presentation. Never receives or changes game state."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
from uuid import uuid4

from .fixtures import ROOT
from .evaluate_speech import inspect_audio
from .speech_cache import SpeechCache, cache_key, identity


def play_wav(path):
    import winsound
    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_NODEFAULT)


class Speaker:
    def __init__(self, output=ROOT / 'generated/gameplay-speech', runner=subprocess.run,
                 player=play_wav, timeout=120, identity_provider=identity):
        self.output, self.runner, self.player, self.timeout = Path(output), runner, player, timeout
        self.identity_provider = identity_provider
        self.cache = SpeechCache(self.output)

    def speak(self, text):
        """One attempt; synthesis/playback/log failures retain usable text gameplay."""
        folder = None
        started = time.perf_counter()
        result = {'version': 'gameplay-kokoro-v1', 'text': text, 'candidate': 'kokoro',
                  'voice': 'af_heart', 'success': False, 'played': False, 'cache_hit': False,
                  'synthesis_seconds': None, 'worker_wall_seconds': None}
        try:
            folder = self.output / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex[:8])
            folder.mkdir(parents=True)
            request = {'candidate': 'kokoro', 'seed': 42, 'text': text}
            (folder / 'request.json').write_text(json.dumps(request, indent=2), encoding='utf-8')
            lookup_started = time.perf_counter()
            key, cached = None, None
            try:
                configuration = self.identity_provider()
                key = cache_key(text, configuration)
                result.update(cache_key=key, cache_configuration=configuration)
                cached, reason = self.cache.lookup(key)
                result['cache_miss_reason'] = reason
            except Exception as exc:
                result['cache_error'] = f'{type(exc).__name__}: {exc}'
            result['cache_lookup_seconds'] = time.perf_counter() - lookup_started
            if cached:
                path, metrics = cached
                result.update(metrics, cache_hit=True, audio_path=str(path))
                print('Reusing saved speech audio.')
                if self.player is not None:
                    self.player(path)
                result.update(success=True, played=self.player is not None)
                return result
            command = [str(ROOT / '.venv-speech-kokoro/Scripts/python.exe'),
                       str(ROOT / 'scripts/speech_worker.py'), str((folder / 'request.json').resolve())]
            result['command'] = command
            worker_started = time.perf_counter()
            with (folder / 'runtime.log').open('w', encoding='utf-8') as log:
                completed = self.runner(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                        timeout=self.timeout, check=False)
            result['worker_wall_seconds'] = time.perf_counter() - worker_started
            result['exit_code'] = completed.returncode
            worker = json.loads((folder / 'worker.json').read_text(encoding='utf-8'))
            result['worker'] = worker
            result['synthesis_seconds'] = worker.get('synthesis_seconds')
            if completed.returncode or not worker.get('success'):
                raise RuntimeError('Speech generation failed')
            result.update(inspect_audio(folder / 'audio.wav'))
            result['audio_path'] = str((folder / 'audio.wav').resolve())
            if key:
                try:
                    self.cache.save(key, folder / 'audio.wav', result['sha256'])
                except Exception as exc:
                    result['cache_write_error'] = f'{type(exc).__name__}: {exc}'
            if self.player is not None:
                self.player(folder / 'audio.wav')
            result.update(success=True, played=self.player is not None)
        except (Exception, KeyboardInterrupt) as exc:
            result['error'] = f'{type(exc).__name__}: {exc}'
            print('Speech unavailable or interrupted; continuing with the displayed text.')
        finally:
            result['request_seconds'] = time.perf_counter() - started
            if folder is not None:
                try:
                    (folder / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                except OSError:
                    print('Could not save speech log; gameplay can continue.')
        return result
