"""Run the local SDXL-Turbo feasibility experiment; no hosted services."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'generated' / 'feasibility'
PROMPT = ('Illustrated adventure game environment, interior of an abandoned observatory, '
          'a large brass telescope pointing through an open dome, wooden bookshelves, '
          'a desk with a glowing lantern, storm clouds outside, painterly storybook style, '
          'warm amber light and cool blue shadows, empty room, no people, no lettering.')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    runtime = ROOT / 'tools' / 'stable-diffusion' / 'd04e895' / 'sd-cli.exe'
    model = ROOT / 'models' / 'sd_xl_turbo_1.0_fp16.safetensors'
    if not runtime.is_file() or not model.is_file():
        raise SystemExit('Download and verify the runtime and model before running this script.')
    prompt_path = OUT / 'observatory-prompt.txt'
    prompt_path.write_text(PROMPT, encoding='utf-8')
    command = [str(runtime), '-m', str(model), '--prompt-file', str(prompt_path),
               '-W', '512', '-H', '512', '--steps', '4', '--cfg-scale', '1',
               '--sampling-method', 'euler', '--scheduler', 'sgm_uniform',
               '-s', '42', '-o', str(OUT / 'observatory.png'), '-v']
    metadata = {'started_utc': datetime.now(timezone.utc).isoformat(),
                'model': 'stabilityai/sdxl-turbo',
                'model_revision': '71153311d3dbb46851df1931d3ca6e939de83304',
                'expected_model_sha256': 'e869ac7d6942cb327d68d5ed83a40447aadf20e0c3358d98b2cc9e270db0da26',
                'runtime_commit': 'd04e895', 'prompt': PROMPT, 'command': command,
                'notes': 'Fresh CLI process; total time includes model loading. GPU usage must be confirmed from log.'}
    start = time.perf_counter()
    with (OUT / 'generation.log').open('w', encoding='utf-8') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, cwd=ROOT)
    metadata.update(elapsed_seconds=round(time.perf_counter() - start, 3), exit_code=result.returncode)
    output = OUT / 'observatory.png'
    if output.is_file():
        metadata['image_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
        metadata['image_bytes'] = output.stat().st_size
    (OUT / 'result.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps(metadata, indent=2))
    raise SystemExit(result.returncode)

if __name__ == '__main__':
    main()
