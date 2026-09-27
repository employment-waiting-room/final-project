"""Local, model-only image development trials. Preview by default; no downloads."""
import argparse
import hashlib
import json
import platform
import struct
import subprocess
import time
import zlib
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .fixtures import ROOT, Strict
from .media_fixtures import MEDIA_DATA, load_media
from pydantic import Field

PROTOCOL = ROOT / "evaluation/media_protocol.txt"


class Candidate(Strict):
    id: str = Field(pattern=r"^[a-z0-9_-]+$")
    model: str = Field(min_length=1)
    checkpoint: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    steps: int = Field(gt=0)
    cfg: float = Field(ge=0, allow_inf_nan=False)
    sampler: str = "euler"
    scheduler: str = "sgm_uniform"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2), encoding="utf-8")


def local_path(value):
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def check_png(path):
    """Check CRCs and scanline encoding for the runtime's 512px RGB/RGBA PNGs.

    This is file integrity, never a visual/content judgement. Other formats fail.
    """
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG")
    offset, compressed, channels, ended = 8, bytearray(), None, False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Truncated PNG")
        length = int.from_bytes(data[offset:offset + 4], "big")
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        end = offset + 12 + length
        if end > len(data) or zlib.crc32(kind + body) != int.from_bytes(data[end-4:end], "big"):
            raise ValueError("PNG CRC/truncation failure")
        if offset == 8 and kind != b"IHDR":
            raise ValueError("Missing IHDR")
        if kind == b"IHDR":
            if channels is not None or len(body) != 13:
                raise ValueError("Invalid IHDR")
            width, height, depth, colour, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
            if (width, height, depth, compression, filtering, interlace) != (512, 512, 8, 0, 0, 0) or colour not in (2, 6):
                raise ValueError("Expected non-interlaced 512x512 8-bit RGB/RGBA PNG")
            channels = 3 if colour == 2 else 4
        elif kind == b"IDAT":
            compressed.extend(body)
        elif kind == b"IEND":
            if length or end != len(data):
                raise ValueError("Invalid PNG ending")
            ended = True
        offset = end
    if not ended or channels is None:
        raise ValueError("Incomplete PNG")
    stride = 512 * channels + 1
    decoder = zlib.decompressobj()
    pixels = decoder.decompress(compressed, stride * 512 + 1)
    if not decoder.eof or decoder.unused_data or len(pixels) != stride * 512 or any(pixels[i] > 4 for i in range(0, len(pixels), stride)):
        raise ValueError("Invalid PNG scanlines")
    return {"png_integrity": True, "width": 512, "height": 512, "sha256": digest(path)}


def run(config, runtime, output_root, *, execute=False, repetitions=2, limit=5, timeout=300, runner=subprocess.run):
    if repetitions not in (1, 2) or not 1 <= limit <= 5 or timeout <= 0:
        raise ValueError("Use 1-2 repetitions, 1-5 briefs and positive timeout")
    candidates = [Candidate.model_validate(row) for row in json.loads(config.read_text(encoding="utf-8"))]
    if not candidates or len({c.id for c in candidates}) != len(candidates):
        raise ValueError("Candidate IDs must be nonempty and unique")
    data = load_media()
    runtime = runtime.resolve()
    if execute:
        for path in [runtime, *(local_path(c.checkpoint) for c in candidates)]:
            if not path.is_file():
                raise ValueError(f"Missing local file: {path}; no downloads performed")
    folder = output_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8])
    folder.mkdir(parents=True)
    artifacts = {}
    if execute:
        # Include runtime DLL identities, not just the launcher; hash sequentially.
        for path in [runtime, *sorted(runtime.parent.glob("*.dll")), *(local_path(c.checkpoint) for c in candidates)]:
            artifacts[str(path)] = digest(path)
    manifest = {"version": "image-development-v1", "status": "running" if execute else "preview",
                "dataset_sha256": digest(MEDIA_DATA), "protocol_sha256": digest(PROTOCOL),
                "candidates": [c.model_dump() for c in candidates], "artifacts_sha256": artifacts,
                "python": platform.python_version(), "platform": platform.platform(),
                "timeout_seconds": timeout, "schedule": [], "resource_measurements": None,
                "timing_note": "Fresh CLI process per attempt; wall time includes loading. Load/inference times and GPU identity require log review."}
    (folder / "dataset.json").write_bytes(MEDIA_DATA.read_bytes())
    (folder / "protocol.md").write_bytes(PROTOCOL.read_bytes())
    reviews, records = [], []
    for repetition in range(repetitions):
        for candidate in (candidates if repetition == 0 else candidates[::-1]):
            for fixture in data.illustrations[:limit]:
                attempt = f"A{len(manifest['schedule']) + 1:04}"
                target = folder / attempt
                target.mkdir()
                prompt = target / "prompt.txt"
                prompt.write_text(fixture.prompt, encoding="utf-8")
                command = [str(runtime), "-m", str(local_path(candidate.checkpoint)), "--prompt-file", str(prompt.resolve()),
                           "-W", "512", "-H", "512", "--steps", str(candidate.steps), "--cfg-scale", str(candidate.cfg),
                           "--sampling-method", candidate.sampler, "--scheduler", candidate.scheduler,
                           "-s", str(42 + repetition), "-o", str((target / "image.png").resolve()), "-v"]
                request = {"attempt": attempt, "candidate": candidate.id, "fixture": fixture.id,
                           "repetition": repetition + 1, "seed": 42 + repetition, "prompt": fixture.prompt, "command": command}
                write_json(target / "request.json", request)
                manifest["schedule"].append(request)
                reviews.append({"attempt": attempt, "candidate": candidate.id, "fixture": fixture.id,
                                "required": {d: None for d in fixture.required_details},
                                "forbidden": {d: None for d in fixture.forbidden_details},
                                "content_pass": None, "scene_clarity": None, "style_adherence": None,
                                "reviewer": None, "date": None, "notes": "", "image": f"{attempt}/image.png"})
    write_json(folder / "manifest.json", manifest)
    write_json(folder / "reviews.json", {"images": reviews, "coherence": [
        {"candidate": c.id, "repetition": r + 1, "rating": None, "reviewer": None}
        for c in candidates for r in range(repetitions)]})
    if not execute:
        return folder
    try:
        with (folder / "results.jsonl").open("w", encoding="utf-8") as results:
            for request in manifest["schedule"]:
                target = folder / request["attempt"]
                record = {"attempt": request["attempt"], "completed": False, "png_integrity": False,
                          "content_review": "pending", "error": None}
                started = time.perf_counter()
                interrupted = False
                try:
                    with (target / "runtime.log").open("w", encoding="utf-8") as log:
                        result = runner(request["command"], stdout=log, stderr=subprocess.STDOUT,
                                        cwd=ROOT, timeout=timeout, check=False)
                    record["exit_code"] = result.returncode
                    if result.returncode:
                        raise ValueError(f"Runtime exit {result.returncode}")
                    record["completed"] = True
                    record.update(check_png(target / "image.png"))
                except KeyboardInterrupt:
                    interrupted = True
                    record["error"] = "KeyboardInterrupt"
                except (OSError, ValueError, subprocess.TimeoutExpired, zlib.error) as exc:
                    record["error"] = f"{type(exc).__name__}: {exc}"
                record["wall_seconds"] = time.perf_counter() - started
                results.write(json.dumps(record) + "\n")
                results.flush()
                records.append(record)
                print(f"{request['attempt']} {request['candidate']} {request['fixture']}: PNG integrity={record['png_integrity']}")
                if interrupted:
                    raise KeyboardInterrupt
        manifest["status"] = "completed"
    except KeyboardInterrupt:
        manifest["status"] = "interrupted"
    except Exception:
        manifest["status"] = "failed"
        raise
    finally:
        write_json(folder / "manifest.json", manifest)
        write_json(folder / "summary.json", {"status": manifest["status"], "planned": len(manifest["schedule"]),
                   "attempted": len(records), "completed": sum(r["completed"] for r in records),
                   "png_integrity_passes": sum(r["png_integrity"] for r in records), "visual_review": "pending"})
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "evaluation/image_candidates.json")
    parser.add_argument("--runtime", type=Path, default=ROOT / "tools/stable-diffusion/d04e895/sd-cli.exe")
    parser.add_argument("--output", type=Path, default=ROOT / "generated/image-evaluations")
    parser.add_argument("--execute", action="store_true", help="Launch installed local runtime; default only saves preview")
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    try:
        folder = run(args.config, args.runtime, args.output, execute=args.execute,
                     repetitions=args.repetitions, limit=args.limit, timeout=args.timeout)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Saved image {'development results' if args.execute else 'preview (no inference)'}: {folder}")


if __name__ == "__main__":
    main()
