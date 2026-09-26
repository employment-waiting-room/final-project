import json

import httpx
import pytest

from observatory import gameplay_io


@pytest.mark.parametrize('fails', [False, True])
@pytest.mark.parametrize('injected', [False, True])
def test_chat_client_ownership_and_request(monkeypatch, fails, injected):
    def respond(request):
        assert str(request.url) == 'http://127.0.0.1:11434/api/chat'
        assert json.loads(request.content) == {'model': 'test', 'stream': False}
        if fails:
            raise httpx.ReadTimeout('offline test')
        return httpx.Response(200, json={'done': True})

    client = httpx.Client(transport=httpx.MockTransport(respond))
    def create(**options):
        assert options == {'timeout': 30, 'trust_env': False}
        return client

    monkeypatch.setattr(gameplay_io.httpx, 'Client', create)
    try:
        if fails:
            with pytest.raises(httpx.ReadTimeout):
                gameplay_io.post_chat({'model': 'test', 'stream': False}, client if injected else None)
        else:
            response = gameplay_io.post_chat({'model': 'test', 'stream': False}, client if injected else None)
            assert response.json() == {'done': True}
        assert client.is_closed is not injected
    finally:
        client.close()


def test_logs_preserve_records_and_tolerate_unwritable_destination(tmp_path, capsys):
    directory = tmp_path / 'logs'
    for value in (1, 2):
        gameplay_io.save_record(directory, {'value': value}, 'log unavailable')
    assert sorted(json.loads(path.read_text())['value'] for path in directory.glob('*.json')) == [1, 2]
    blocked = tmp_path / 'file'
    blocked.write_text('keep')
    gameplay_io.save_record(blocked, {}, 'log unavailable')
    assert blocked.read_text() == 'keep'
    assert 'log unavailable' in capsys.readouterr().out
