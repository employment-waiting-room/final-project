import hashlib
import json

import pytest

from scripts.download_speech_models import MANIFEST, download, verify


def item(content=b'test'):
    return {'destination': 'model/file', 'size': len(content), 'sha256': hashlib.sha256(content).hexdigest(), 'url': 'https://example.invalid/file'}


def test_verified_existing_file_never_downloads(tmp_path):
    target = tmp_path / 'model/file'
    target.parent.mkdir()
    target.write_bytes(b'test')
    assert download(item(), tmp_path, runner=lambda *a, **k: pytest.fail('network')) == item()['sha256']


def test_partial_is_verified_before_rename(tmp_path):
    def fake(command, **kwargs):
        from pathlib import Path
        Path(command[command.index('-o') + 1]).write_bytes(b'bad!')
    with pytest.raises(ValueError, match='SHA-256'):
        download(item(), tmp_path, runner=fake)
    assert not (tmp_path / 'model/file').exists()
    assert (tmp_path / 'model/file.part').exists()


def test_complete_partial_resumes_without_network(tmp_path):
    target = tmp_path / 'model/file.part'
    target.parent.mkdir()
    target.write_bytes(b'test')
    download(item(), tmp_path, runner=lambda *a, **k: pytest.fail('network'))
    assert (tmp_path / 'model/file').read_bytes() == b'test'


def test_git_blob_and_manifest_identities(tmp_path):
    path = tmp_path / 'small'
    path.write_bytes(b'test')
    spec = item()
    spec['sha256'] = None
    spec['git_blob'] = hashlib.sha1(b'blob 4\0test').hexdigest()
    assert verify(path, spec)
    manifest = json.loads(MANIFEST.read_text())
    assert len(manifest['files']) == 32
    for f in manifest['files']:
        assert len(f['revision']) == 40
        assert f.get('sha256') or f.get('git_blob')


def test_path_escape_rejected(tmp_path):
    spec = item()
    spec['destination'] = '../outside'
    with pytest.raises(ValueError, match='escapes'):
        download(spec, tmp_path)
