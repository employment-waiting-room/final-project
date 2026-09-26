import json

import httpx
import pytest

from observatory.world import WorldState, Command, perform
from observatory.world_intent import WorldIntent, WorldInterpreter, handle_world_text


class FakeInterpreter:
    def __init__(self, action='inspect_desk', target='desk', status='action'):
        self.intent = WorldIntent(status=status, action=action, target=target)
        self.logs = []

    def interpret(self, text, state):
        return self.intent

    def save(self, record):
        self.logs.append(record)


@pytest.mark.parametrize('reply,changed', [('yes', True), (' Y ', True), ('no', False), ('sure', False), ('', False), (None, False)])
def test_confirmation_is_explicit_and_applies_once(reply, changed):
    state = WorldState()
    interpreter = FakeInterpreter()
    proposals = []
    def confirm(proposal):
        proposals.append(proposal)
        assert state.revision == 0 and not state.flags
        return reply
    result = handle_world_text(state, 'inspect desk', interpreter, confirm)
    assert result.state.revision == int(changed)
    assert 'inspect_desk' in proposals[0] and 'desk' in proposals[0]
    if changed:
        repeated = handle_world_text(result.state, 'inspect desk', interpreter, lambda _: pytest.fail('Repeated action asked again'))
        assert repeated.state is result.state
    else:
        assert result.state is state


@pytest.mark.parametrize('error', [EOFError, KeyboardInterrupt])
def test_interrupted_confirmation_cancels(error):
    state = WorldState()
    def confirm(_):
        raise error
    assert handle_world_text(state, 'inspect desk', FakeInterpreter(), confirm).state is state


@pytest.mark.parametrize('action,target,status', [('unlock_library', 'library_door', 'rejected'),
                                                 ('look_around', 'current_room', 'observed'),
                                                 ('move', 'library', 'rejected')])
def test_engine_rejection_and_observation_never_request_approval(action, target, status):
    state = WorldState()
    result = handle_world_text(state, 'request', FakeInterpreter(action, target), lambda _: pytest.fail('Unexpected confirmation'))
    assert result.status == status and result.state is state


@pytest.mark.parametrize('text,status', [('knock on the door', 'unsupported'), ('inspect desk or toolbox', 'clarify'),
                                      ('use the key', 'clarify'), ('examine it', 'clarify'),
                                      ('search desk and take key', 'clarify'), ('finish', 'clarify')])
def test_gameplay_guards_skip_model_and_state_change(tmp_path, text, status):
    with httpx.Client(transport=httpx.MockTransport(lambda _: pytest.fail('Guard ran model'))) as client:
        state = WorldState()
        result = handle_world_text(state, text, WorldInterpreter(client, tmp_path))
    assert result.status == status and result.state is state
    records = [json.loads(path.read_text()) for path in tmp_path.glob('*.json')]
    assert any(r.get('source') == 'local_guard' for r in records)


@pytest.mark.parametrize('fault', [None, 'invalid_pair', 'extra', 'truncated', 'http', 'timeout'])
def test_model_contract_and_failures(tmp_path, fault):
    def respond(request):
        payload = json.loads(request.content)
        assert 'exactly one JSON object' in payload['messages'][0]['content']
        assert payload['model'] == 'qwen3:4b'
        if fault == 'timeout':
            raise httpx.ReadTimeout('test')
        if fault == 'http':
            return httpx.Response(500)
        value = dict(status='action', action='move', target='moon' if fault == 'invalid_pair' else 'workshop')
        if fault == 'extra':
            value['state'] = 'power_on'
        return httpx.Response(200, json={'done': fault != 'truncated', 'message': {'content': json.dumps(value)}})
    state = WorldState()
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = handle_world_text(state, 'go to workshop', WorldInterpreter(client, tmp_path), lambda _: 'yes')
    assert result.status == ('changed' if fault is None else 'error')
    if fault:
        assert result.state is state
    else:
        assert result.state.location == 'workshop' and result.state.revision == 1


def test_full_world_terminal_typed_cancel_then_confirm(monkeypatch, capsys):
    from observatory import world_cli
    interpreter = FakeInterpreter('move', 'workshop')
    monkeypatch.setattr(world_cli, 'WorldInterpreter', lambda: interpreter)
    answers = iter(['go to workshop', 'no', 'go to workshop', 'yes', 'q'])
    monkeypatch.setattr('builtins.input', lambda _: next(answers))
    world_cli.main()
    output = capsys.readouterr().out
    assert 'Action cancelled; state unchanged.' in output
    assert 'You are in the workshop.' in output
    assert [record['resulting_revision'] for record in interpreter.logs] == [0, 1]


@pytest.mark.parametrize('reply', ['yes', 'no'])
@pytest.mark.parametrize('text,action,target,in_library', [
    ('check the desk', 'inspect_desk', 'desk', False),
    ('go to the telescope chamber', 'move', 'telescope_chamber', True),
    ('go to telescope room', 'move', 'telescope_chamber', True),
    ('go to the telescope chamber', 'move', 'telescope_chamber', False),
    ('look around the room', 'look_around', 'current_room', False),
])
def test_reported_wording_response_handling(tmp_path, text, action, target, in_library, reply):
    """Simulated predictions test plumbing and safety, not model accuracy."""
    state = WorldState()
    if in_library:
        for command in (Command('inspect_desk', 'desk'), Command('collect_key', 'library_key'),
                        Command('unlock_library', 'library_door'), Command('move', 'library')):
            state = perform(state, command).state
    original = state
    proposals = []

    def respond(request):
        payload = json.loads(request.content)
        assert json.loads(payload['messages'][1]['content'])['player_request'] == text
        return httpx.Response(200, json={'done': True, 'message': {'content': json.dumps(
            {'status': 'action', 'action': action, 'target': target})}})

    def confirm(proposal):
        proposals.append(proposal)
        assert state is original
        return reply

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = handle_world_text(state, text, WorldInterpreter(client, tmp_path), confirm)
    expected = perform(state, Command(action, target))
    if expected.status == 'changed':
        assert len(proposals) == 1 and target in proposals[0]
        assert result.status == ('changed' if reply == 'yes' else 'cancelled')
        assert result.state == (expected.state if reply == 'yes' else original)
        assert result.state.revision == original.revision + (reply == 'yes')
    else:
        assert not proposals
        assert result.status == expected.status
        assert result.state is original
    records = [json.loads(path.read_text()) for path in tmp_path.glob('*.json')]
    assert any(r.get('source') == 'model' and r.get('input') == text for r in records)


@pytest.mark.parametrize('action,target', [
    ('look_around/current_room', 'entrance hall'),
    ('move', 'telescope chamber'),
    ('inspect_desk', 'library_door'),
])
def test_reported_malformed_predictions_never_reach_confirmation(tmp_path, action, target):
    def respond(_):
        return httpx.Response(200, json={'done': True, 'message': {'content': json.dumps(
            {'status': 'action', 'action': action, 'target': target})}})
    state = WorldState()
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        result = handle_world_text(state, 'check the desk', WorldInterpreter(client, tmp_path),
                                   lambda _: pytest.fail('Invalid prediction requested confirmation'))
    assert result.status == 'error' and result.state is state
