"""Import checks only: no model loading or synthesis."""
import argparse
from datetime import datetime, timezone
from importlib import import_module, metadata
import json
import os
from pathlib import Path
import socket
import sys

CHECKS = {
    'hf': [('transformers', 'SpeechT5Processor'), ('transformers', 'SpeechT5ForTextToSpeech'),
           ('transformers', 'SpeechT5HifiGan'), ('transformers', 'VitsModel'), ('sentencepiece', None)],
    'kokoro': [('kokoro', 'KModel'), ('kokoro', 'KPipeline'), ('misaki.en', 'G2P'),
               ('en_core_web_sm', None), ('espeakng_loader', None)],
    'xtts': [('TTS.tts.configs.xtts_config', 'XttsConfig'), ('TTS.tts.models.xtts', 'Xtts')],
}


def check(profile, importer=import_module):
    results = []
    for module, attribute in [('torch', None), ('torchaudio', None), ('soundfile', None), *CHECKS[profile]]:
        try:
            loaded = importer(module)
            if attribute:
                getattr(loaded, attribute)
            results.append({'module': module, 'attribute': attribute, 'ok': True})
        except Exception as exc:
            results.append({'module': module, 'attribute': attribute, 'ok': False,
                            'error': f'{type(exc).__name__}: {exc}'})
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', choices=CHECKS)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')
    def deny(*args, **kwargs):
        raise RuntimeError('Network disabled for import check')
    socket.socket.connect = deny
    socket.socket.connect_ex = deny
    results = check(args.profile)
    report = {'profile': args.profile, 'checked_utc': datetime.now(timezone.utc).isoformat(),
              'python': sys.executable, 'python_version': sys.version,
              'checks': results, 'success': all(r['ok'] for r in results),
              'inference_performed': False, 'packages': {d.metadata['Name']: d.version for d in metadata.distributions()}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f"{args.profile}: import checks {'passed' if report['success'] else 'FAILED'}; {args.output}")
    return 0 if report['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
