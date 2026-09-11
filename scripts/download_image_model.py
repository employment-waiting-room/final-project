"""Resume the fixed SDXL-Turbo checkpoint with four verified HTTP ranges."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import shutil
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PART = ROOT / 'models' / 'sd_xl_turbo_1.0_fp16.safetensors.part'
FINAL = PART.with_suffix('')
SIZE = 6938081905
SHA = 'e869ac7d6942cb327d68d5ed83a40447aadf20e0c3358d98b2cc9e270db0da26'
URL = 'https://huggingface.co/stabilityai/sdxl-turbo/resolve/71153311d3dbb46851df1931d3ca6e939de83304/sd_xl_turbo_1.0_fp16.safetensors'

def fetch(spec):
    index, start, end = spec
    target = PART.with_name(PART.name + f'.range{index}')
    for attempt in range(4):
        received = target.stat().st_size if target.exists() else 0
        offset = start + received
        if offset > end:
            return target
        try:
            req = urllib.request.Request(URL + f'?download=true&range={index}&start={offset}', headers={'Range': f'bytes={offset}-{end}', 'User-Agent': 'LastObservatoryCoursework/0.1'})
            with urllib.request.urlopen(req, timeout=90) as response:
                expected = f'bytes {offset}-{end}/{SIZE}'
                if response.status != 206 or response.headers.get('Content-Range') != expected:
                    raise RuntimeError(f'Unexpected range response: {response.status}, {response.headers.get("Content-Range")}')
                with target.open('ab') as output:
                    shutil.copyfileobj(response, output, length=1024*1024)
            if target.stat().st_size != end-start+1:
                raise RuntimeError('Incomplete range')
            print(f'Range {index} complete', flush=True)
            return target
        except Exception as exc:
            print(f'Range {index} attempt {attempt+1}: {exc}', flush=True)
            if attempt == 3:
                raise
            time.sleep(2)

def main():
    start = PART.stat().st_size if PART.exists() else 0
    remaining = SIZE-start
    width = (remaining+3)//4
    specs = [(i, start+i*width, min(SIZE-1, start+(i+1)*width-1)) for i in range(4) if start+i*width < SIZE]
    print(f'Resuming at {start} / {SIZE} bytes', flush=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        paths = list(pool.map(fetch, specs))
    with PART.open('ab') as output:
        for path in paths:
            with path.open('rb') as source:
                shutil.copyfileobj(source, output, length=1024*1024)
    with PART.open('rb') as source:
        actual = hashlib.file_digest(source, 'sha256').hexdigest()
    if PART.stat().st_size != SIZE or actual != SHA:
        raise RuntimeError(f'Checkpoint verification failed: {actual}')
    PART.rename(FINAL)
    print('Checkpoint SHA256 verified; download complete', flush=True)

if __name__ == '__main__':
    main()
