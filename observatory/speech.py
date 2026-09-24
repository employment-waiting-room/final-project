"""Optional gameplay speech presentation. Never receives or changes game state."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from uuid import uuid4

from .fixtures import ROOT
from .evaluate_speech import inspect_audio


def play_wav(path):
    import winsound
    winsound.PlaySound(str(path), winsound.SND_FILENAME | winsound.SND_NODEFAULT)


class Speaker:
    def __init__(self, output=ROOT / 'generated/gameplay-speech', runner=subprocess.run,
                 player=play_wav, timeout=120):
        self.output, self.runner, self.player, self.timeout = Path(output), runner, player, timeout

    def speak(self, text):
        """One attempt; synthesis/playback/log failures retain usable text gameplay."""
        folder = None
        result = {'version': 'gameplay-kokoro-v1', 'text': text, 'candidate': 'kokoro',
                  'voice': 'af_heart', 'success': False, 'played': False}
        try:
            folder = self.output / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex[:8])
            folder.mkdir(parents=True)
            request = {'candidate': 'kokoro', 'seed': 42, 'text': text}
            (folder / 'request.json').write_text(json.dumps(request, indent=2), encoding='utf-8')
            command = [str(ROOT / '.venv-speech-kokoro/Scripts/python.exe'),
                       str(ROOT / 'scripts/speech_worker.py'), str((folder / 'request.json').resolve())]
            result['command'] = command
            with (folder / 'runtime.log').open('w', encoding='utf-8') as log:
                completed = self.runner(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                        timeout=self.timeout, check=False)
            result['exit_code'] = completed.returncode
            worker = json.loads((folder / 'worker.json').read_text(encoding='utf-8'))
            result['worker'] = worker
            if completed.returncode or not worker.get('success'):
                raise RuntimeError('Speech generation failed')
            result.update(inspect_audio(folder / 'audio.wav'))
            result['audio_path'] = str((folder / 'audio.wav').resolve())
            if self.player is not None:
                self.player(folder / 'audio.wav')
            result.update(success=True, played=self.player is not None)
        except (Exception, KeyboardInterrupt) as exc:
            result['error'] = f'{type(exc).__name__}: {exc}'
            print('Speech unavailable or interrupted; continuing with the displayed text.')
        finally:
            if folder is not None:
                try:
                    (folder / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                except OSError:
                    print('Could not save speech log; gameplay can continue.')
        return result
