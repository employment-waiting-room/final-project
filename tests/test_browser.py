from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from observatory.browser import Game, Input, create_app
from observatory.world_intent import WorldIntent
from observatory.world import TARGETS


class Queue:
    def __init__(self): self.jobs = []
    def submit(self, fn, *args): self.jobs.append((fn, args))
    def finish(self):
        while self.jobs:
            fn, args = self.jobs.pop(0)
            fn(*args)


@pytest.fixture
def browser():
    queue = Queue()
    game = Game(media=False, executor=queue)
    with TestClient(create_app(game), base_url='http://127.0.0.1') as client:
        yield game, queue, client


def post(client, op, **values):
    snapshot = client.get('/state').json()
    return client.post('/api/' + op, headers={'X-Game-Token': snapshot['token']},
                       json=dict(session=snapshot['session'], revision=snapshot['revision'], **values))


def test_confirmation_cancel_replay_and_restart(browser, monkeypatch):
    game, queue, client = browser
    monkeypatch.setattr(game.interpreter, 'interpret', lambda text, state: WorldIntent(status='action', action='move', target='workshop'))
    monkeypatch.setattr(game.interpreter, 'save', lambda record: None)
    post(client, 'type', text='go to workshop')
    assert game.state.revision == 0
    queue.finish()
    proposal = game.snapshot()['proposal']['id']
    post(client, 'cancel', proposal=proposal)
    assert game.state.revision == 0 and game.pending is None
    assert post(client, 'confirm', proposal=proposal).status_code == 409
    post(client, 'type', text='go to workshop')
    queue.finish()
    proposal = game.snapshot()['proposal']['id']
    response = post(client, 'confirm', proposal=proposal)
    assert response.status_code == 200 and game.state.revision == 1
    assert post(client, 'confirm', proposal=proposal).status_code == 409
    queue.finish()
    old = game.state.session_id
    post(client, 'restart')
    assert game.state.session_id != old and game.state.revision == 0
    queue.finish()
    assert game.state.location == 'entrance_hall'


def test_restarted_session_discards_pending_interpretation(browser, monkeypatch):
    game, queue, client = browser
    monkeypatch.setattr(game.interpreter, 'interpret', lambda *args: WorldIntent(status='action', action='inspect_desk', target='desk'))
    post(client, 'type', text='inspect desk')
    post(client, 'restart')
    queue.finish()
    assert game.pending is None and not game.busy and not game.state.flags


def test_restart_during_narration_does_not_publish_old_text(browser):
    game, queue, client = browser
    class Narrator:
        def render(self, *args, **kwargs):
            game.reset()
            from observatory.narrative import Scene
            return Scene('STALE TEXT', (), 'entrance_hall', 'model')
    game.narrator = Narrator()
    post(client, 'start')
    queue.finish()
    assert 'STALE' not in game.text and not game.busy


@pytest.mark.parametrize('ending', ['rescued', 'sheltered'])
def test_api_routes_both_endings(browser, ending):
    game, queue, client = browser
    route = ['inspect_desk', 'collect_key', 'unlock_library', 'go:workshop', 'inspect_toolbox',
             'collect_fuse', 'go:generator_room', 'install_fuse', 'start_generator', 'go:workshop',
             'go:entrance_hall', 'go:library']
    if ending == 'rescued': route += ['read_manual']
    route += ['go:telescope_chamber']
    route += ['align_beacon', 'signal_rescue'] if ending == 'rescued' else ['shelter']
    for item in route:
        action, target = ('move', item[3:]) if item.startswith('go:') else (item, TARGETS[item])
        response = post(client, 'choose', action=action, target=target)
        assert response.status_code == 200
        queue.finish()
    assert game.state.ending == ending and game.snapshot()['choices'] == []


def test_local_api_token_stale_state_and_asset_restrictions(browser):
    game, queue, client = browser
    state = client.get('/state').json()
    assert client.post('/api/restart', json={'session': state['session'], 'revision': 0}).status_code == 403
    assert client.get('/asset/not-registered').status_code == 404
    assert client.get('/state', headers={'host': 'untrusted.example'}).status_code == 400
    post(client, 'choose', action='inspect_desk', target='desk')
    response = client.post('/api/choose', headers={'X-Game-Token': state['token']},
                           json={'session': state['session'], 'revision': 0, 'action': 'inspect_desk', 'target': 'desk'})
    assert response.status_code == 409
    assert client.get('/').status_code == 200


def test_text_published_before_media_and_speech_artifact(browser, tmp_path):
    game, queue, client = browser
    audio = tmp_path / 'test.wav'
    audio.write_bytes(b'fake')
    class Speech:
        def speak(self, text):
            assert game.text == text
            return {'success': True, 'audio_path': str(audio)}
    game.speaker = Speech()
    post(client, 'choose', action='inspect_desk', target='desk')
    assert 'discover' in game.text and game.busy
    queue.finish()
    assert client.get(game.audio).content == b'fake'


def test_media_error_does_not_undo_transition(browser):
    game, queue, client = browser
    class Narrator:
        def render(self, *args, **kwargs): raise OSError('test failure')
    game.narrator = Narrator()
    post(client, 'choose', action='inspect_desk', target='desk')
    queue.finish()
    assert game.state.revision == 1 and 'discover' in game.text and not game.busy
