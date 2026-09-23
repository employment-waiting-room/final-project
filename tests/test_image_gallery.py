import hashlib
import json

import pytest

from observatory.image_gallery import build, collect


def source(tmp_path):
    folder = tmp_path / 'run'
    (folder / 'A0001').mkdir(parents=True)
    content = b'fixture image bytes'
    (folder / 'A0001/image.png').write_bytes(content)
    dataset = json.dumps({'illustrations': [{'id': 'hall', 'required_details': ['desk'], 'forbidden_details': ['person']}]}).encode()
    (folder / 'dataset.json').write_bytes(dataset)
    (folder / 'manifest.json').write_text(json.dumps({'dataset_sha256': hashlib.sha256(dataset).hexdigest(), 'schedule': [
        {'attempt': 'A0001', 'candidate': '</script><script>bad()</script>', 'fixture': 'hall', 'seed': 42}]}))
    (folder / 'results.jsonl').write_text(json.dumps({'attempt': 'A0001', 'sha256': hashlib.sha256(content).hexdigest()}))
    return folder


def test_build_embeds_images_without_inference_and_escapes_script(tmp_path):
    folder = source(tmp_path)
    before = {str(p): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    output = build(tmp_path, ['run'], tmp_path / 'gallery.html')
    html = output.read_text()
    assert 'data:image/png;base64,' in html
    assert '</script><script>bad()' not in html
    assert '\\u003c/script>' in html
    assert '__GALLERY_DATA__' not in html
    assert before == {str(p): p.read_bytes() for p in folder.rglob('*') if p.is_file()}


@pytest.mark.parametrize('file', ['dataset.json', 'A0001/image.png'])
def test_changed_evidence_rejected(tmp_path, file):
    folder = source(tmp_path)
    with (folder / file).open('ab') as stream:
        stream.write(b'changed')
    with pytest.raises(ValueError, match='hash mismatch'):
        collect(tmp_path, ['run'])


def test_duplicate_runs_rejected(tmp_path):
    source(tmp_path)
    with pytest.raises(ValueError, match='Duplicate'):
        collect(tmp_path, ['run', 'run'])
