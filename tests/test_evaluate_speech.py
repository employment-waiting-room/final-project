import json
from pathlib import Path
import struct
import subprocess
import wave

import pytest

from observatory import evaluate_speech as speech


def wav(path, silent=False):
    with wave.open(str(path), 'wb') as stream:
        stream.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        stream.writeframes(struct.pack('<100h', *([0 if silent else 100] * 100)))


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    for env in {row[0] for row in speech.CANDIDATES.values()}:
        path = tmp_path / env / 'Scripts/python.exe'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'fake')
    for filename in ['evaluation/media_protocol.md', 'scripts/speech_worker.py']:
        path = tmp_path / filename
        path.parent.mkdir(exist_ok=True)
        path.write_text('test snapshot')
    monkeypatch.setattr(speech, 'ROOT', tmp_path)
    return tmp_path


@pytest.mark.parametrize('failure', [None, 'exit', 'timeout', 'silent', 'missing', 'interrupt'])
def test_run_retains_all_attempts_without_retries(workspace, failure):
    calls = []
    def fake(command, **kwargs):
        folder = Path(command[-1]).parent
        calls.append(json.loads(Path(command[-1]).read_text()))
        if failure == 'timeout':
            raise subprocess.TimeoutExpired(command, 1)
        if failure == 'interrupt':
            raise KeyboardInterrupt
        (folder / 'worker.json').write_text(json.dumps({'success': failure != 'exit', 'synthesis_seconds': .1}))
        if failure != 'missing':
            wav(folder / 'audio.wav', failure == 'silent')
        return subprocess.CompletedProcess(command, 1 if failure == 'exit' else 0)
    folder = speech.run(['piper', 'kokoro'], workspace / 'out', limit=1, runner=fake)
    summary = json.loads((folder / 'summary.json').read_text())
    assert len(calls) == (1 if failure == 'interrupt' else 4)
    assert summary['attempted'] == len(calls)
    assert summary['valid_audio'] == (4 if failure is None else 0)
    assert len((folder / 'results.jsonl').read_text().splitlines()) == len(calls)
    if failure != 'interrupt':
        assert [c['candidate'] for c in calls] == ['piper', 'kokoro', 'kokoro', 'piper']
        assert [c['seed'] for c in calls] == [42, 42, 43, 43]
        assert len({c['text'] for c in calls}) == 1
    assert all(r['content_pass'] is None for r in json.loads((folder / 'reviews.json').read_text()))


def test_invalid_settings_create_no_output(workspace):
    with pytest.raises(ValueError):
        speech.run(['piper', 'piper'], workspace / 'out')
    with pytest.raises(ValueError):
        speech.run(['piper'], workspace / 'out', timeout=float('nan'))
    assert not (workspace / 'out').exists()


def test_audio_metrics_and_invalid_file(tmp_path):
    path = tmp_path / 'audio.wav'
    wav(path)
    result = speech.inspect_audio(path)
    assert result['duration_seconds'] == 100 / 16000
    assert result['peak_pcm'] == 100
    assert result['clipped_sample_fraction'] == 0
    path.write_bytes(b'bad')
    with pytest.raises((wave.Error, EOFError)):
        speech.inspect_audio(path)
