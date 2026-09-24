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
