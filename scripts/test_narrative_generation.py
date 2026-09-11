"""Three local narrative checks. Run directly; no models are downloaded.

Structural checks do not establish narrative truth. Review saved prose manually.
"""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from pydantic import BaseModel, ConfigDict, Field, ValidationError

ROOT = Path(__file__).resolve().parents[1]
MODEL = "qwen3:4b"
BASE_URL = "http://127.0.0.1:11434"


class Choice(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)


class Scene(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    description: str = Field(min_length=1)
    choices: list[Choice] = Field(min_length=2, max_length=3)


CASES = [
    {
        "id": "locked_door",
        "facts": ["Location: observatory entrance hall.",
                  "Inventory: an unlit lantern. The player has no key.",
                  "The library door is locked. A dusty desk stands nearby."],
        "actions": {"inspect_desk": "Inspect the dusty desk",
                    "examine_door": "Examine the locked library door"},
        "review": ["Door remains locked", "No key is possessed or granted",
                   "Lantern has no flame and emits no light"],
    },
    {
        "id": "collected_item",
        "facts": ["Location: workshop, revisited after collecting the brass key.",
                  "Inventory: brass key and unlit lantern.",
                  "The key's hook is empty. No second key exists in this room.",
                  "A closed toolbox is on the workbench. Its contents are unknown."],
        "actions": {"inspect_toolbox": "Inspect the closed toolbox",
                    "return_hall": "Return to the entrance hall"},
        "review": ["Key remains in inventory", "Hook stays empty; no duplicate key",
                   "Toolbox remains closed; no invented contents", "Lantern stays unlit"],
    },
    {
        "id": "completed_puzzle",
        "facts": ["Location: generator room.",
                  "The player has already installed the fuse and restored power.",
                  "Inventory: brass key and unlit lantern. The fuse is no longer carried.",
                  "Electric ceiling lights are on. The generator is running.",
                  "The telescope chamber door is now unlocked.",
                  "The rescue signal has not been sent; the adventure is not finished."],
        "actions": {"enter_telescope": "Enter the telescope chamber",
                    "inspect_generator": "Inspect the running generator"},
        "review": ["Power remains on", "Fuse is installed, not in inventory",
                   "Door is unlocked", "No premature rescue or ending",
                   "Lantern remains unlit despite electric lighting"],
    },
]


def check_response(content, actions):
    checks = {"schema_valid": False, "action_ids_valid": False,
              "word_count": None, "length_valid": False}
    try:
        scene = Scene.model_validate_json(content)
    except ValidationError as exc:
        checks["validation_error"] = str(exc)
        return checks
    ids = [choice.id for choice in scene.choices]
    count = len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", scene.description))
    checks.update(schema_valid=True,
                  action_ids_valid=len(ids) == len(actions) and set(ids) == set(actions),
                  word_count=count, length_valid=60 <= count <= 100)
    return checks


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    run = ROOT / "generated" / "llm-tests" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run.mkdir(parents=True, exist_ok=False)
    schema = Scene.model_json_schema()
    summary = {"model": MODEL, "prompt_version": "state-grounded-v2",
               "run_directory": str(run), "cases": [],
               "limitation": "Three development cases, one sample each. Semantic review is separate. No retries or silent repairs."}
    with httpx.Client(base_url=BASE_URL, timeout=180, trust_env=False) as client:
        try:
            for endpoint in ("version", "tags", "ps"):
                response = client.get(f"/api/{endpoint}")
                response.raise_for_status()
                save(run / f"ollama-{endpoint}-before.json", response.json())
        except (httpx.HTTPError, ValueError) as exc:
            summary["connection_error"] = str(exc)
            save(run / "summary.json", summary)
            print(f"Cannot reach local Ollama: {exc}\nStart Ollama and rerun. Results: {run}")
            return 1
        for case in CASES:
            request = {
                "model": MODEL, "stream": False, "think": False, "keep_alive": "5m",
                "format": schema,
                "options": {"temperature": 0.3, "seed": 42, "num_ctx": 4096, "num_predict": 600},
                "messages": [
                    {"role": "system", "content":
                     "You narrate a text adventure. All supplied facts are authoritative. "
                     "Write approximately 80 words in the description field alone; "
                     "the strict acceptable range is 60-100 words, excluding choices and JSON keys. "
                     "Use five or six complete sentences describing location, known objects, "
                     "inventory, established states, and what remains unresolved. "
                     "Expand using the supplied facts and their direct implications, without padding "
                     "through invented scenery. Check the description length before returning it. "
                     "Do not perform actions, "
                     "grant items, change object states, or invent interactive objects. "
                     "Every descriptive detail must agree with the facts; an unlit lantern "
                     "has no flame or light. Do not invent materials, windows, weather, light sources, "
                     "or unseen contents. Return each allowed action exactly once and no others. "
                     "Return only JSON matching this schema: " + json.dumps(schema)},
                    {"role": "user", "content": json.dumps({"facts": case["facts"], "allowed_actions": case["actions"]})},
                ],
            }
            save(run / f"{case['id']}-request.json", request)
            result = {"id": case["id"], "review_checklist": case["review"],
                      "semantic_review": "pending human review", "schema_valid": False,
                      "action_ids_valid": False, "length_valid": False, "word_count": None,
                      "completed": False}
            started = time.perf_counter()
            try:
                response = client.post("/api/chat", json=request)
                result["wall_seconds"] = round(time.perf_counter() - started, 3)
                (run / f"{case['id']}-raw.txt").write_text(response.text, encoding="utf-8")
                response.raise_for_status()
                body = response.json()
                content = body["message"]["content"]
                result.update(check_response(content, case["actions"]))
                result["content"] = content
                result["done_reason"] = body.get("done_reason")
                result["completed"] = body.get("done") is True and body.get("done_reason") != "length"
                for key in ("total_duration", "load_duration", "prompt_eval_duration", "eval_duration"):
                    result[key.replace("duration", "seconds")] = body.get(key, 0) / 1e9
                result["generated_tokens"] = body.get("eval_count")
                result["automated_pass"] = all(result[k] for k in ("schema_valid", "action_ids_valid", "length_valid", "completed"))
            except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                result.update(error=str(exc), automated_pass=False,
                              wall_seconds=round(time.perf_counter() - started, 3))
            save(run / f"{case['id']}-result.json", result)
            summary["cases"].append(result)
            save(run / "summary.json", summary)
            print(f"{case['id']}: schema={result['schema_valid']}, "
                  f"actions={result['action_ids_valid']}, "
                  f"length={result['length_valid']} ({result['word_count']} words), "
                  f"completed={result['completed']}, {result['wall_seconds']}s", flush=True)
        try:
            response = client.get("/api/ps")
            response.raise_for_status()
            save(run / "ollama-ps-after.json", response.json())
        except (httpx.HTTPError, ValueError) as exc:
            summary["gpu_snapshot_error"] = str(exc)
        summary["pass_counts"] = {
            check: sum(case[check] for case in summary["cases"])
            for check in ("schema_valid", "action_ids_valid", "length_valid", "completed", "automated_pass")
        }
        save(run / "summary.json", summary)
    print(f"Saved results: {run}")
    return 0 if summary["pass_counts"]["automated_pass"] == len(CASES) else 1


if __name__ == "__main__":
    raise SystemExit(main())
