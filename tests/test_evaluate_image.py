import json
import struct
import subprocess
import zlib

import pytest

from observatory.evaluate_image import check_png, run
from observatory.media_fixtures import load_media


def png(width=512):
    def chunk(kind, body):
        return struct.pack('>I', len(body)) + kind + body + struct.pack('>I', zlib.crc32(kind + body))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, 512, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\0' + bytes(width * 3)) * 512)) + chunk(b'IEND', b''))


@pytest.fixture
def setup(tmp_path):
    model = tmp_path / 'model file.bin'
    model.write_bytes(b'fake checkpoint')
    runtime = tmp_path / 'fake.exe'
    runtime.write_bytes(b'fake runtime')
    config = tmp_path / 'config.json'
    config.write_text(json.dumps([dict(id=name, model=name, checkpoint=str(model), revision='test', steps=4, cfg=1)
                                  for name in ('first', 'second')]))
    return config, runtime, tmp_path / 'out'


def test_preview_never_launches_and_keeps_shared_prompts(setup):
    def forbidden(*args, **kwargs):
        pytest.fail('Preview launched runtime')
    folder = run(*setup, runner=forbidden)
    manifest = json.loads((folder / 'manifest.json').read_text())
    schedule = manifest['schedule']
    assert len(schedule) == 20
    assert [schedule[i]['candidate'] for i in (0, 5, 10, 15)] == ['first', 'second', 'second', 'first']
    assert {r['seed'] for r in schedule[:10]} == {42}
    assert {r['seed'] for r in schedule[10:]} == {43}
    assert [r['prompt'] for r in schedule[:5]] == [f.prompt for f in load_media().illustrations]
    assert not (folder / 'results.jsonl').exists()
    assert all(r['content_pass'] is None for r in json.loads((folder / 'reviews.json').read_text())['images'])


@pytest.mark.parametrize('failure', ['exit', 'timeout', 'missing', 'corrupt', 'interrupt', None])
def test_execution_preserves_failures_and_no_retries(setup, failure):
    calls = []
    def fake(command, **kwargs):
        calls.append(command)
        if failure == 'timeout':
            raise subprocess.TimeoutExpired(command, 1)
        if failure == 'interrupt':
            raise KeyboardInterrupt
        from pathlib import Path
        output = Path(command[command.index('-o') + 1])
        if failure != 'missing':
            output.write_bytes(b'broken' if failure == 'corrupt' else png())
        return subprocess.CompletedProcess(command, 2 if failure == 'exit' else 0)
    folder = run(*setup, execute=True, repetitions=1, limit=1, runner=fake)
    summary = json.loads((folder / 'summary.json').read_text())
    assert len(calls) == (1 if failure == 'interrupt' else 2)
    assert summary['attempted'] == len(calls)
    assert summary['png_integrity_passes'] == (2 if failure is None else 0)
    assert summary['status'] == ('interrupted' if failure == 'interrupt' else 'completed')
    assert len((folder / 'results.jsonl').read_text().splitlines()) == len(calls)
    assert json.loads((folder / 'manifest.json').read_text())['artifacts_sha256']


def test_missing_model_fails_before_creating_output(setup):
    setup[1].unlink()
    with pytest.raises(ValueError, match='Missing local file'):
        run(*setup, execute=True)
    assert not setup[2].exists()


@pytest.mark.parametrize('content', [b'', png()[:-1], png(256), png()[:-20] + b'bad crc'])
def test_invalid_png_rejected(tmp_path, content):
    path = tmp_path / 'image.png'
    path.write_bytes(content)
    with pytest.raises(ValueError):
        check_png(path)


def test_duplicate_candidate_and_bad_settings_rejected(setup):
    config = json.loads(setup[0].read_text())
    config[1]['id'] = config[0]['id']
    setup[0].write_text(json.dumps(config))
    with pytest.raises(ValueError, match='unique'):
        run(*setup)
    with pytest.raises(ValueError, match='repetitions'):
        run(*setup, repetitions=0)
    assert not setup[2].exists()
