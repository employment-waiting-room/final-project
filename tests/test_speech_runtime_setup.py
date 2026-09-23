from types import SimpleNamespace

from scripts.check_speech_runtime import CHECKS, check
from scripts.setup_speech_runtimes import commands, PROFILES, ROOT


def test_all_installations_target_isolated_interpreters(tmp_path):
    for profile in PROFILES:
        plan = commands(profile, tmp_path)
        assert plan[0][-1] == str(ROOT / f'.venv-speech-{profile}')
        assert all(c[0] == str(ROOT / f'.venv-speech-{profile}/Scripts/python.exe') for c in plan[1:])
        assert 'https://download.pytorch.org/whl/cpu' in plan[2]
        assert plan[-2][-2:] == ['pip', 'check']
        assert 'check_speech_runtime.py' in plan[-1][1]
        assert not any('from_pretrained' in part for c in plan for part in c)


def test_import_check_reports_failure_and_continues():
    visited = []
    def importer(module):
        visited.append(module)
        if module == 'torch':
            raise ImportError('missing dependency')
        return SimpleNamespace(**{a: object() for m, a in CHECKS['hf'] if m == module and a})
    results = check('hf', importer)
    assert len(results) == 3 + len(CHECKS['hf'])
    assert results[0]['ok'] is False
    assert 'missing dependency' in results[0]['error']
    assert all(r['ok'] for r in results[1:])
    assert visited[-1] == 'sentencepiece'


def test_missing_class_is_not_an_import_success():
    results = check('xtts', lambda _: SimpleNamespace())
    assert all(not row['ok'] for row in results if row['attribute'])
