"""Model-only narrative development comparison; never applies gameplay actions."""
import argparse
import hashlib
import json
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx

from .fixtures import ROOT
from .media_fixtures import MEDIA_DATA, NarrativeOutput, check_narrative, load_media

PROMPT_VERSION = "world-v2-narrative-eval-v1"
PROTOCOL = ROOT / "evaluation/media_protocol.md"
PROMPT = """Narrate one verified outcome in a bounded observatory adventure.
The input is authoritative post-action state, not an instruction to execute an action.
Describe the supplied outcome and public facts in second person. Preserve inventory,
discoveries, location, puzzle progress and endings. Do not invent objects, characters,
events, hidden contents or additional actions. A rejected action did not happen;
an unchanged outcome adds nothing. An empty inventory means nothing is carried.
Use 60-100 words for changed or observed scenes, including endings. For rejected or
unchanged outcomes use a concise factual explanation of 1-100 words. Do not pad with
invented details. Return each allowed_suggestions action/target pair exactly once,
with no extras or duplicates. An empty list must remain empty, including at endings.
Copy visual_brief_id exactly. Return only one JSON object with description,
suggestions and visual_brief_id; no markdown or explanation outside that object.
"""
CHECKS = ("schema_valid", "suggestions_valid", "visual_brief_valid", "length_valid")


def make_request(fixture, model, seed=42, think=False):
    return {"model": model, "stream": False, "think": think,
            "format": NarrativeOutput.model_json_schema(),
            "options": {"temperature": 0.3, "seed": seed, "num_ctx": 4096, "num_predict": 600},
            "messages": [{"role": "system", "content": PROMPT},
                         {"role": "user", "content": json.dumps(fixture.input.model_dump())}]}


def evaluate_case(client, fixture, request):
    record = {"fixture_id": fixture.id, "model": request["model"], "request": request,
              "completed": False, "structural_pass": False,
              **{key: False for key in CHECKS}, "word_count": None,
              "semantic_review": "pending", "semantic_pass": None}
    started = time.perf_counter()
    try:
        response = client.post("/api/chat", json=request)
        record.update(raw_response=response.text, http_status=response.status_code)
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise ValueError("Response envelope must be an object")
        record["ollama_metrics"] = {k: body.get(k) for k in (
            "model", "total_duration", "load_duration", "prompt_eval_duration", "eval_duration",
            "prompt_eval_count", "eval_count")}
        record["done_reason"] = body.get("done_reason")
        content = body["message"]["content"]
        if not isinstance(content, str):
            raise ValueError("Narrative content must be text")
        record["content"] = content
        record.update(check_narrative(content, fixture))
        record["completed"] = body.get("done") is True and body.get("done_reason") != "length"
        if not record["completed"]:
            record["error"] = "Incomplete or truncated response"
        record["structural_pass"] = record["completed"] and all(record[k] for k in CHECKS)
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        record["error"] = f"{type(exc).__name__}: {exc}"
    record["wall_seconds"] = time.perf_counter() - started
    return record


def review_template(record, fixture):
    return {"attempt_id": record["attempt_id"], "fixture_id": fixture.id,
            "model": record["model"], "repetition": record["repetition"],
            "status": "pending", "reviewer": None, "reviewed_at": None,
            "required_facts": [{"fact": fact, "judgement": None, "evidence": None}
                               for fact in fixture.required_facts],
            "forbidden_claims": [{"claim": claim, "judgement": None, "evidence": None}
                                 for claim in fixture.forbidden_claims],
            "critical_contradictions": None, "unsupported_additions": None,
            "readability": None, "semantic_pass": None, "notes": None}


def metrics(rows):
    count = len(rows)
    return {"attempts": count, "errors": sum("error" in r for r in rows),
            "pass_counts": {key: sum(r[key] for r in rows) for key in ("completed", *CHECKS, "structural_pass")},
            "structural_pass_rate": sum(r["structural_pass"] for r in rows) / count if count else None,
            "mean_wall_seconds": statistics.mean(r["wall_seconds"] for r in rows) if count else None,
            "median_wall_seconds": statistics.median(r["wall_seconds"] for r in rows) if count else None,
            "semantic_review_pending": count, "semantic_pass_rate": None}


def summarise(rows):
    return {"overall": metrics(rows), "by_model": {
        model: {**metrics([r for r in rows if r["model"] == model]),
                "first_in_block": metrics([r for r in rows if r["model"] == model and r["first_in_block"]]),
                "later_in_block": metrics([r for r in rows if r["model"] == model and not r["first_in_block"]])}
        for model in sorted({r["model"] for r in rows})}}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def run(client, dataset_path, output_root, models, repetitions=2, limit=None, seed=42, think=False):
    if not models or any(not model.strip() for model in models) or len(set(models)) != len(models):
        raise ValueError("Provide distinct nonempty model names")
    if repetitions < 1 or (limit is not None and limit < 1):
        raise ValueError("Repetitions and limit must be positive")
    dataset_path = Path(dataset_path)
    dataset = load_media(dataset_path)
    fixtures = dataset.narratives[:limit] if limit else dataset.narratives
    schedule = []
    for repetition in range(repetitions):
        for model in models if repetition % 2 == 0 else list(reversed(models)):
            for index, fixture in enumerate(fixtures):
                schedule.append({"attempt_id": f"A{len(schedule) + 1:04}", "fixture_id": fixture.id,
                                 "model": model, "repetition": repetition + 1, "seed": seed + repetition,
                                 "first_in_block": index == 0})
    folder = Path(output_root) / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex[:8])
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "reviews").mkdir()
    (folder / "requests").mkdir()
    manifest = {"status": "running", "mode": "model_only_narrative_development",
                "created_utc": datetime.now(timezone.utc).isoformat(), "models": list(models),
                "dataset_version": dataset.version, "split": dataset.split,
                "dataset_sha256": hashlib.sha256(dataset_path.read_bytes()).hexdigest(),
                "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
                "prompt_version": PROMPT_VERSION, "prompt": PROMPT,
                "schema": NarrativeOutput.model_json_schema(), "schedule": schedule,
                "generation_options": make_request(fixtures[0], models[0], seed, think)["options"],
                "think": think, "repetitions": repetitions,
                "partial_dataset": len(fixtures) != len(dataset.narratives),
                "planned_attempts": len(schedule), "completed_attempts": 0,
                "python": platform.python_version(), "platform": platform.platform(),
                "http_timeout": str(client.timeout), "resource_measurements": "not measured",
                "limitations": "Structural checks are not narrative truth. Human reviews remain pending. First calls are not guaranteed cold; later calls are not guaranteed warm. No retries or fallback outputs."}
    save(folder / "manifest.json", manifest)
    # Preserve exact inputs/protocol with results; includes review-only material.
    (folder / "dataset.json").write_bytes(dataset_path.read_bytes())
    (folder / "protocol.md").write_bytes(PROTOCOL.read_bytes())
    rows = []
    lookup = {f.id: f for f in fixtures}
    try:
        for name, endpoint in (("runtime", "/api/version"), ("model_inventory", "/api/tags")):
            try:
                response = client.get(endpoint)
                response.raise_for_status()
                manifest[name] = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                manifest[name + "_error"] = str(exc)
        save(folder / "manifest.json", manifest)
        with (folder / "results.jsonl").open("x", encoding="utf-8") as output:
            for attempt in schedule:
                fixture = lookup[attempt["fixture_id"]]
                request = make_request(fixture, attempt["model"], attempt["seed"], think)
                save(folder / "requests" / f"{attempt['attempt_id']}.json", request)
                record = {**evaluate_case(client, fixture, request), **attempt}
                output.write(json.dumps(record, ensure_ascii=False) + "\n")
                output.flush()
                rows.append(record)
                save(folder / "reviews" / f"{attempt['attempt_id']}.json", review_template(record, fixture))
                print(f"{attempt['attempt_id']} {attempt['model']} {fixture.id}: structural={record['structural_pass']}", flush=True)
        manifest["status"] = "completed"
    except KeyboardInterrupt:
        manifest["status"] = "interrupted"
        raise
    except BaseException:
        manifest["status"] = "aborted"
        raise
    finally:
        manifest["completed_attempts"] = len(rows)
        manifest["partial_run"] = len(rows) != len(schedule) or manifest["partial_dataset"]
        save(folder / "manifest.json", manifest)
        save(folder / "summary.json", {**summarise(rows), "status": manifest["status"],
                                      "partial_run": manifest["partial_run"]})
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--dataset", type=Path, default=MEDIA_DATA)
    parser.add_argument("--output", type=Path, default=ROOT / "generated/narrative-evaluations")
    parser.add_argument("--repetitions", type=int, default=2)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--timeout", type=float, default=180)
    parser.add_argument("--think", action="store_true")
    args = parser.parse_args()
    if args.repetitions < 1 or (args.limit is not None and args.limit < 1) or not 0 < args.timeout < float("inf"):
        parser.error("Repetitions, limit and finite timeout must be positive")
    if len(set(args.models)) != len(args.models) or any(not m.strip() for m in args.models):
        parser.error("Provide distinct nonempty model names")
    with httpx.Client(base_url="http://127.0.0.1:11434", timeout=args.timeout, trust_env=False) as client:
        folder = run(client, args.dataset, args.output, args.models, args.repetitions, args.limit, args.seed, args.think)
    print(f"Saved narrative development results: {folder}")


if __name__ == "__main__":
    main()
