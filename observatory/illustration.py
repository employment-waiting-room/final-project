"""Optional hall illustration presentation; no engine state or transitions."""
from datetime import datetime, timezone
import os
import subprocess
import time
from uuid import uuid4

from .fixtures import ROOT
from .evaluate_image import check_png, write_json

# Approved world-v2 establishing brief, copied unchanged from the development
# comparison. Gameplay configuration is separate from evaluator configuration.
HALL_PROMPT = ('Observatory entrance hall. Restrained storybook digital painting, muted blue-grey and warm wood palette, diffuse daylight, square 512x512 establishing view, no people, no lettering, no visible portable quest items. Show: Dusty desk; Closed wooden library door; High frosted glazing. Omit: Visible key; Readable door label; Open library door; People; Lettering; Visible portable quest items.')


def open_image(path):
    os.startfile(str(path))


class Illustrator:
    def __init__(self, output=ROOT / 'generated/gameplay-images', runner=subprocess.run,
                 viewer=open_image, timeout=120):
        self.output, self.runner, self.viewer, self.timeout = output, runner, viewer, timeout
        self.attempted = False
        self.path = None

    def show(self, location):
        """Attempt once per hall session; reuse static art without reopening it."""
        if location != 'entrance_hall':
            print('No illustration brief available; continuing with text.')
            return None
        if self.attempted:
            if self.path:
                print(f'Room illustration retained: {self.path}')
            return self.path
        self.attempted = True
        folder = None
        started = time.perf_counter()
        record = {'version': 'hall-image-v1', 'location': location, 'prompt': HALL_PROMPT,
                  'model': 'stabilityai/sdxl-turbo',
                  'revision': '71153311d3dbb46851df1931d3ca6e939de83304',
                  'seed': 42, 'success': False, 'viewer_requested': False,
                  'content_review': 'pending'}
        try:
            folder = self.output / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + uuid4().hex[:8])
            folder.mkdir(parents=True)
            prompt = folder / 'prompt.txt'
            prompt.write_text(HALL_PROMPT, encoding='utf-8')
            path = (folder / 'image.png').resolve()
            command = [str(ROOT / 'tools/stable-diffusion/d04e895/sd-cli.exe'),
                       '-m', str(ROOT / 'models/sd_xl_turbo_1.0_fp16.safetensors'),
                       '--prompt-file', str(prompt.resolve()), '-W', '512', '-H', '512',
                       '--steps', '4', '--cfg-scale', '1', '--sampling-method', 'euler',
                       '--scheduler', 'sgm_uniform', '-s', '42', '-o', str(path), '-v']
            record['command'] = command
            write_json(folder / 'request.json', record)
            with (folder / 'runtime.log').open('w', encoding='utf-8') as log:
                result = self.runner(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                     timeout=self.timeout, check=False)
            record['exit_code'] = result.returncode
            if result.returncode:
                raise RuntimeError(f'Image runtime exit {result.returncode}')
            record.update(check_png(path))
            self.path = path
            print(f'Room illustration: {path}')
            self.viewer(path)
            record.update(success=True, viewer_requested=True)
        except (Exception, KeyboardInterrupt) as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
            print('Illustration unavailable or interrupted; continuing with text.')
        finally:
            record['wall_seconds'] = time.perf_counter() - started
            if folder is not None:
                try:
                    write_json(folder / 'result.json', record)
                except OSError:
                    print('Could not save illustration log; gameplay can continue.')
        return self.path
