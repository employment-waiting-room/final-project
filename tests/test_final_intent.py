import json
from types import SimpleNamespace

import httpx
import pytest

from observatory import final_intent as final
from observatory.fixtures import load_dataset


@pytest.fixture
def setup(tmp_path, monkeypatch):
    # Workflow tests use development cases, never reserved model predictions.
    dataset = SimpleNamespace(cases=load_dataset().cases[:2])
    monkeypatch.setattr(final, 'load_reserved', lambda: dataset)
    config = {'identity': 'frozen'}
    monkeypatch.setattr(final, 'snapshot', lambda: dict(config))
    calls = []
    runtime = {'version': 'test', 'digest': 'test-digest'}
    def respond(request):
        calls.append(request.url.path)
        if request.url.path == '/api/version': return httpx.Response(200, json={'version': runtime['version']})
        if request.url.path == '/api/tags': return httpx.Response(200, json={'models': [{'name': 'qwen3:4b', 'digest': runtime['digest']}]})
        return httpx.Response(500, text='Simulated failure')
    with httpx.Client(base_url='http://localhost', transport=httpx.MockTransport(respond)) as client:
        yield tmp_path, client, calls, config, runtime


def test_freeze_metadata_only_and_no_overwrite(setup):
    root, client, calls, _, _ = setup
    path = root / 'freeze.json'
    final.freeze(client, path)
    final.verify(path)
    assert calls == ['/api/version', '/api/tags']
    with pytest.raises(ValueError): final.freeze(client, path)


@pytest.mark.parametrize('drift', ['source', 'model', 'runtime'])
def test_drift_blocks_before_inference(setup, drift):
    root, client, calls, config, runtime = setup
    path = root / 'freeze.json'
    final.freeze(client, path)
    if drift == 'source': config['identity'] = 'changed'
    elif drift == 'model': runtime['digest'] = 'changed'
    else: runtime['version'] = 'changed'
    with pytest.raises(ValueError): final.run(client, path, root / 'results')
    assert '/api/chat' not in calls


def test_failed_predictions_retained_and_repeat_blocked(setup):
    root, client, calls, _, _ = setup
    path = root / 'freeze.json'
    final.freeze(client, path)
    folder = final.run(client, path, root / 'results')
    summary = json.loads((folder / 'summary.json').read_text())
    assert summary['complete'] and summary['overall']['errors'] == 2
    assert summary['overall']['intent_pass'] == 0
    assert len((folder / 'results.jsonl').read_text().splitlines()) == 2
    with pytest.raises(FileExistsError): final.run(client, path, root / 'results')
    assert calls.count('/api/chat') == 2


def test_interruption_retains_release_marker_and_partial_summary(setup, monkeypatch):
    root, client, _, _, _ = setup
    path = root / 'freeze.json'
    final.freeze(client, path)
    def interrupt(*args): raise KeyboardInterrupt
    monkeypatch.setattr(final, 'evaluate_case', interrupt)
    folder = final.run(client, path, root / 'results')
    summary = json.loads((folder / 'summary.json').read_text())
    assert summary['status'] == 'interrupted' and not summary['complete'] and summary['recorded'] == 0
    assert path.with_suffix('.release.json').is_file()


def test_missing_freeze_has_no_network_requests(setup):
    root, client, calls, _, _ = setup
    with pytest.raises(FileNotFoundError): final.run(client, root / 'absent.json', root / 'results')
    assert not calls
