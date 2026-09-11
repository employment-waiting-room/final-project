"""Run a local CPU Piper feasibility test and preserve each run's evidence."""
import hashlib
import json
import platform
import time
import wave
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from piper import PiperVoice


def main():
    root = Path(__file__).resolve().parents[1]
    model = root / "models/piper/en_US-lessac-medium.onnx"
    config = model.with_suffix(".onnx.json")
    output = root / "generated/speech-tests" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True)
    passage = (
        "You stand in the entrance hall of the abandoned observatory. "
        "An unlit lantern rests in your hand. Beside you, a dusty desk holds a folded note. "
        "The library door is locked, and you do not have its key. "
        "Somewhere beyond the hall, a telescope waits beneath the silent dome. "
        "You can inspect the desk or examine the library door. What will you do?"
    )
    (output / "passage.txt").write_text(passage, encoding="utf-8")
    result = {"piper_version": version("piper-tts"), "python": platform.python_version(),
              "device": "CPU", "settings": "Piper defaults", "success": False,
              "listening_review": "Pending user listening; automated WAV checks do not assess speech quality."}
    try:
        for name, path in (("model", model), ("config", config)):
            result[name] = {"path": str(path), "bytes": path.stat().st_size,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        (output / "voice_config.json").write_bytes(config.read_bytes())
        start = time.perf_counter()
        voice = PiperVoice.load(model, config_path=config, use_cuda=False)
        result["load_seconds"] = time.perf_counter() - start
        start = time.perf_counter()
        audio = output / "observatory.wav"
        with wave.open(str(audio), "wb") as wav:
            voice.synthesize_wav(passage, wav)
        result["synthesis_seconds"] = time.perf_counter() - start
        with wave.open(str(audio), "rb") as wav:
            frames = wav.getnframes()
            result.update(sample_rate=wav.getframerate(), channels=wav.getnchannels(),
                          sample_width_bytes=wav.getsampwidth(), frames=frames,
                          duration_seconds=frames / wav.getframerate())
            samples = wav.readframes(frames)
        result["nonzero_audio"] = any(samples)
        result["real_time_factor"] = result["synthesis_seconds"] / result["duration_seconds"]
        result["success"] = frames > 0 and result["nonzero_audio"]
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(output), **result}, indent=2))
    return 0 if result["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
