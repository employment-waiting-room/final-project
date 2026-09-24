import json
from pathlib import Path
import subprocess

import pytest

from observatory import __main__ as cli
from observatory.illustration import Illustrator, HALL_PROMPT
from observatory.intent import Intent
from observatory.media_fixtures import load_media
from observatory.narrative import Scene
from test_evaluate_image import png


@pytest.mark.parametrize('failure', [None, 'timeout', 'exit', 'invalid', 'viewer', 'interrupt'])
def test_one_attempt_and_failure_containment(tmp_path, failure):
    calls, views = [], []
    def runner(command, **kwargs):
        calls.append(command)
        if failure == 'timeout':
            raise subprocess.TimeoutExpired(command, 1)
        if failure == 'interrupt':
            raise KeyboardInterrupt
        Path(command[command.index('-o') + 1]).write_bytes(b'bad' if failure == 'invalid' else png())
        return subprocess.CompletedProcess(command, 1 if failure == 'exit' else 0)
    def viewer(path):
        views.append(path)
        if failure == 'viewer':
            raise OSError('No viewer')
    adapter = Illustrator(tmp_path, runner, viewer)
    adapter.show('entrance_hall')
    adapter.show('entrance_hall')
    assert len(calls) == 1
    assert len(views) == (1 if failure in (None, 'viewer') else 0)
    result = json.loads(next(tmp_path.glob('*/result.json')).read_text())
    assert result['success'] == (failure is None)
    assert result['content_review'] == 'pending'
    assert HALL_PROMPT == load_media().illustrations[0].prompt


@pytest.mark.parametrize('reply,expected', [('yes', 1), ('no', 0)])
def test_confirmation_controls_illustration(monkeypatch, reply, expected):
    calls = []
    class Interpreter:
        def interpret(self, text, state):
            return Intent(status='action', action='inspect_desk', target='desk')
    class FakeIllustrator:
        def show(self, location):
            calls.append(location)
    monkeypatch.setattr(cli, 'Interpreter', Interpreter)
    monkeypatch.setattr(cli, 'Illustrator', FakeIllustrator)
    answers = iter(['inspect desk', reply, '', 'q'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cli.main(['--illustrate'])
    assert calls == ['entrance_hall'] * expected


def test_image_failure_preserves_sequence(monkeypatch, tmp_path, capsys):
    def runner(*args, **kwargs):
        raise OSError('Missing runtime')
    monkeypatch.setattr(cli, 'Illustrator', lambda: Illustrator(tmp_path, runner))
    answers = iter(['1', '1', '1'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cli.main(['--illustrate'])
    assert 'Sequence complete.' in capsys.readouterr().out
    assert len(list(tmp_path.glob('*/result.json'))) == 1


def test_combined_pipeline_uses_post_action_state_and_accepted_text(monkeypatch):
    events = []
    class Narrator:
        def render(self, state, previous=None):
            if previous is None:
                assert not state.desk_inspected
                events.append('opening')
                return Scene('Opening text.', (), 'entrance_hall', 'fallback')
            assert state.desk_inspected
            assert previous is not None and not previous.desk_inspected
            events.append('narrate')
            return Scene('Accepted factual text.', (), 'entrance_hall', 'fallback')
    class Image:
        def show(self, location):
            events.append(('image', location))
    class Speech:
        def speak(self, text):
            events.append(('speech', text))
    monkeypatch.setattr(cli, 'Narrator', Narrator)
    monkeypatch.setattr(cli, 'Illustrator', Image)
    monkeypatch.setattr(cli, 'Speaker', Speech)
    answers = iter(['1', '', 'q'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    cli.main(['--narrate', '--illustrate', '--speak'])
    assert events == ['opening', ('speech', 'Opening text.'), 'narrate',
                      ('image', 'entrance_hall'), ('speech', 'Accepted factual text.')]
