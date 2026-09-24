import json

import httpx
import pytest

from observatory.world import WorldState, Command, perform, describe_world
from observatory.world_narrative import WorldNarrator, validate, sentences
from observatory import world_media, world_cli
from observatory.media_fixtures import load_media
from observatory.fixtures import load_dataset
from observatory.narrative import Scene


@pytest.mark.parametrize('case', load_dataset().cases, ids=lambda c: c.id)
def test_factual_world_scene_fallback_matches_verified_state(tmp_path, case):
    expected = case.expected_state
    state = WorldState(location=expected.location, inventory=frozenset(expected.inventory),
                       flags=frozenset(expected.flags), visited_rooms=frozenset(expected.visited),
                       ending=expected.ending, revision=expected.revision)
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(500))) as client:
        scene = WorldNarrator(client, tmp_path).render(state)
    assert scene.description == describe_world(state)
    assert scene.source == 'fallback' and scene.visual_brief_id == state.location


@pytest.mark.parametrize('fault', [None, 'invented', 'schema', 'timeout', 'interrupt', 'recap'])
def test_short_outcome_acceptance_and_failure(tmp_path, fault):
    state = perform(WorldState(), Command('inspect_desk', 'desk')).state
    outcome = 'You discover a library key on the desk. It is not yet collected.'
    def respond(_):
        if fault == 'timeout': raise httpx.ReadTimeout('test')
        if fault == 'interrupt': raise KeyboardInterrupt
        text = outcome
        if fault == 'invented': text += ' You open the door.'
        if fault == 'recap': text += ' The daylight fills the hall.'
        value = {'description': text}
        if fault == 'schema': value['new_state'] = {}
        return httpx.Response(200, json={'done': True, 'message': {'content': json.dumps(value)}})
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        scene = WorldNarrator(client, tmp_path).render(state, outcome, False)
    assert scene.description == outcome
    assert scene.source == ('model' if fault is None else 'fallback')


def test_room_images_reuse_restart_and_exact_speech(monkeypatch, capsys):
    events = []
    class Image:
        def __init__(self, location, prompt):
            self.path = location + '.png'
            events.append(('new_image', location, prompt))
        def show(self, location): events.append(('show', location))
        def viewer(self, path): events.append(('reuse', path))
    class Speech:
        def speak(self, text): events.append(('speech', text))
    class Narrator:
        def render(self, state, outcome, scene_mode):
            events.append(('narrative', scene_mode))
            return Scene(outcome, (), state.location, 'fallback')
    monkeypatch.setattr(world_media, 'Illustrator', Image)
    monkeypatch.setattr(world_media, 'Speaker', Speech)
    monkeypatch.setattr(world_media, 'WorldNarrator', Narrator)
    media = world_media.WorldPresentation(True, True, True)
    state = WorldState()
    media.present(state, 'Opening.', True)
    media.present(state, 'Short outcome.', False)
    workshop = perform(state, Command('move', 'workshop')).state
    media.present(workshop, 'Workshop.', True)
    returned = perform(workshop, Command('move', 'entrance_hall')).state
    media.present(returned, 'Hall again.', True)
    media.present(WorldState(), 'Restart.', True)
    assert [e[1] for e in events if e[0] == 'new_image'] == ['entrance_hall', 'workshop', 'entrance_hall']
    assert ('reuse', 'entrance_hall.png') in events
    assert [e[1] for e in events if e[0] == 'speech'] == ['Opening.', 'Short outcome.', 'Workshop.', 'Hall again.', 'Restart.']
    output = capsys.readouterr().out
    assert all(e[1] in output for e in events if e[0] == 'speech')
    assert media.briefs == {f.id: f.prompt for f in load_media().illustrations}


def test_world_cli_cancel_does_not_present_again(monkeypatch):
    from observatory.world_intent import WorldIntent
    calls = []
    class Media:
        def __init__(self, *args): pass
        def present(self, state, text, scene_mode=False): calls.append((state, scene_mode))
    class Interpreter:
        def interpret(self, text, state): return WorldIntent(status='action', action='move', target='workshop')
        def save(self, record): pass
    monkeypatch.setattr(world_cli, 'WorldPresentation', Media)
    monkeypatch.setattr(world_cli, 'WorldInterpreter', Interpreter)
    answers = iter(['go to workshop', 'no', 'go to workshop', 'yes', 'q'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    world_cli.main(True, True, True)
    assert [(s.location, mode) for s, mode in calls] == [('entrance_hall', True), ('workshop', True)]


def test_checks_are_not_semantic_proof():
    text = 'You pick up the library key.'
    assert not validate(text + ' Purple butterflies hover nearby.', sentences(text), 'outcome')
