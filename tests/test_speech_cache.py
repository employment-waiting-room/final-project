import json
from pathlib import Path
import subprocess
import wave

import pytest

from observatory.speech import Speaker
from observatory.speech_cache import cache_key, fingerprint


def write_audio(path, value=1):
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((1, 2, 24000, 0, 'NONE', 'not compressed'))
        wav.writeframes(value.to_bytes(2, 'little', signed=True) * 100)


@pytest.fixture
def setup(tmp_path):
    calls = []
    configuration = {'voice': 'af_heart', 'model': 'test', 'speed': 1, 'seed': 42}
    def runner(command, **kwargs):
        calls.append(command)
        folder = Path(command[-1]).parent
        (folder / 'worker.json').write_text(json.dumps({'success': True, 'synthesis_seconds': 1.25}))
        write_audio(folder / 'audio.wav')
        return subprocess.CompletedProcess(command, 0)
    def speaker(player=None):
        return Speaker(tmp_path, runner=runner, player=player, identity_provider=lambda: dict(configuration))
    return tmp_path, calls, configuration, speaker


def test_hit_across_instances_reuses_file_and_logs_no_synthesis(setup):
    output, calls, config, speaker = setup
    first = speaker().speak('Exact text.')
    second = speaker().speak('Exact text.')
    assert len(calls) == 1 and first['cache_hit'] is False and second['cache_hit'] is True
    assert first['audio_path'] == second['audio_path']
    assert second['synthesis_seconds'] is None and second['worker_wall_seconds'] is None
    assert first['synthesis_seconds'] == 1.25
    assert len(list(output.glob('*/result.json'))) == 2
    assert len(list(output.glob('*/audio.wav'))) == 1
    assert second['played'] is False


@pytest.mark.parametrize('change', ['text', 'voice', 'model', 'speed', 'seed'])
def test_changed_input_misses(setup, change):
    _, calls, config, speaker = setup
    first = speaker().speak('Exact text.')
    text = 'Exact text. ' if change == 'text' else 'Exact text.'
    if change != 'text': config[change] = 'changed'
    second = speaker().speak(text)
    assert len(calls) == 2 and not second['cache_hit']
    assert first['cache_key'] != second['cache_key']


@pytest.mark.parametrize('damage', ['missing', 'corrupt', 'silent', 'valid_but_changed', 'index'])
def test_invalid_cache_regenerates(setup, damage):
    output, calls, _, speaker = setup
    first = speaker().speak('Exact text.')
    audio = Path(first['audio_path'])
    if damage == 'missing': audio.unlink()
    elif damage == 'corrupt': audio.write_bytes(b'broken')
    elif damage == 'silent': write_audio(audio, 0)
    elif damage == 'valid_but_changed': write_audio(audio, 2)
    else: next((output / '_cache').glob('*.json')).write_text('broken json')
    second = speaker().speak('Exact text.')
    assert second['success'] and not second['cache_hit'] and len(calls) == 2
    assert speaker().speak('Exact text.')['cache_hit']


def test_cached_playback_failure_does_not_regenerate(setup):
    _, calls, _, speaker = setup
    speaker().speak('Exact text.')
    def fail(_): raise OSError('No audio device')
    result = speaker(fail).speak('Exact text.')
    assert result['cache_hit'] and not result['success'] and len(calls) == 1
    played = []
    result = speaker(played.append).speak('Exact text.')
    assert result['success'] and result['played'] and len(played) == 1


def test_cache_write_failure_keeps_audio_usable(setup, monkeypatch):
    _, calls, _, speaker = setup
    adapter = speaker()
    def fail(*args): raise OSError('read-only cache')
    monkeypatch.setattr(adapter.cache, 'save', fail)
    result = adapter.speak('Exact text.')
    assert result['success'] and result['cache_write_error']


def test_fingerprint_changes_when_asset_changes(tmp_path):
    asset = tmp_path / 'voice'
    asset.write_bytes(b'old')
    before = fingerprint(asset)
    asset.write_bytes(b'new contents')
    assert fingerprint(asset) != before


def test_cache_key_has_stable_dict_order():
    assert cache_key('text', {'a': 1, 'b': 2}) == cache_key('text', {'b': 2, 'a': 1})
