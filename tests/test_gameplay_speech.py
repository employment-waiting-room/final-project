import json
from pathlib import Path
import subprocess
import wave

import pytest

from observatory import __main__ as cli
from observatory.intent import Intent
from observatory.narrative import Scene
from observatory.speech import Speaker


@pytest.mark.parametrize('reply,count', [('yes', 1), ('no', 0), ('d', 0)])
def test_only_confirmed_text_is_spoken(monkeypatch, reply, count):
    spoken = []
    class Interpreter:
        def interpret(self, text, state):
            return Intent(status='action', action='inspect_desk', target='desk')
    class Narrator:
        def render(self, state):
            return Scene('Exact accepted fallback.', (), 'entrance_hall', 'fallback')
    class FakeSpeaker:
        def speak(self, text):
            spoken.append(text)
    answers = iter(['inspect desk', reply, '', 'q'])
    monkeypatch.setattr(cli, 'Interpreter', Interpreter)
    monkeypatch.setattr(cli, 'Narrator', Narrator)
    monkeypatch.setattr(cli, 'Speaker', FakeSpeaker)
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cli.main(['--narrate', '--speak'])
    assert spoken == ['Exact accepted fallback.'] * count


@pytest.mark.parametrize('failure', [None, 'timeout', 'playback', 'interrupt', 'exit'])
def test_speaker_preserves_exact_text_and_contains_failures(tmp_path, failure):
    calls = []
    def runner(command, **kwargs):
        folder = Path(command[-1]).parent
        calls.append(json.loads((folder / 'request.json').read_text())['text'])
        if failure == 'timeout':
            raise subprocess.TimeoutExpired(command, 1)
        if failure == 'interrupt':
            raise KeyboardInterrupt
        (folder / 'worker.json').write_text(json.dumps({'success': failure != 'exit'}))
        with wave.open(str(folder / 'audio.wav'), 'wb') as wav:
            wav.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
            wav.writeframes(b'\x01\x00' * 100)
        return subprocess.CompletedProcess(command, 1 if failure == 'exit' else 0)
    def player(path):
        if failure == 'playback':
            raise OSError('no device')
    result = Speaker(tmp_path, runner, player).speak('The door remains closed.')
    assert calls == ['The door remains closed.']
    assert result['success'] == (failure is None)
    assert len(list(tmp_path.glob('*/result.json'))) == 1


def test_numbered_sequence_speaks_final_state_once(monkeypatch):
    spoken = []
    class FakeSpeaker:
        def speak(self, text):
            spoken.append(text)
    monkeypatch.setattr(cli, 'Speaker', FakeSpeaker)
    answers = iter(['1', '1', '1'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cli.main(['--speak'])
    assert len(spoken) == 3


@pytest.mark.parametrize('status', ['clarify', 'unsupported'])
def test_unaccepted_intent_is_silent(monkeypatch, status):
    class Interpreter:
        def interpret(self, text, state):
            return Intent(status=status, action=None, target=None)
    class FakeSpeaker:
        def speak(self, text):
            pytest.fail('Unaccepted action triggered speech')
    monkeypatch.setattr(cli, 'Interpreter', Interpreter)
    monkeypatch.setattr(cli, 'Speaker', FakeSpeaker)
    answers = iter(['some request', 'q'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cli.main(['--speak'])


def test_failed_speech_does_not_block_game_completion(monkeypatch, tmp_path, capsys):
    def runner(*args, **kwargs):
        raise OSError('Unavailable runtime')
    monkeypatch.setattr(cli, 'Speaker', lambda: Speaker(tmp_path, runner=runner))
    answers = iter(['1', '1', '1'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cli.main(['--speak'])
    assert 'Sequence complete.' in capsys.readouterr().out
    assert len(list(tmp_path.glob('*/result.json'))) == 3
