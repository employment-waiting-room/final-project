"""Small paired development diagnostic; never changes gameplay or baseline files."""
import json
import time
from datetime import datetime, timezone
from uuid import uuid4

import httpx

from observatory.evaluate_intent import Prediction, make_request
from observatory.fixtures import ROOT, load_dataset


def main():
    cases = {c.id: c for c in load_dataset().cases}
    folder = ROOT / "generated/intent-diagnostics" / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
    with httpx.Client(base_url="http://127.0.0.1:11434", timeout=60, trust_env=False) as client:
        # Fail before scheduling inference if the service is unavailable.
        version = client.get("/api/version")
        version.raise_for_status()
        tags = client.get("/api/tags")
        tags.raise_for_status()
        folder.mkdir(parents=True)
        manifest = {"runtime": version.json(), "models": tags.json(),
                    "case_ids": ["I01", "S16", "I06", "I09"],
                    "repeats": 2, "model": "qwen3:4b", "thinking": False,
                    "note": "Development diagnostic. Same explicit JSON instruction in both modes; only format differs within each prompt pair. Order reversed on repeat. Not a full accuracy estimate."}
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        rows = []
        with (folder / "results.jsonl").open("x", encoding="utf-8") as output:
            for repeat in range(2):
                for prompt in ("v1", "v2"):
                    for identifier in manifest["case_ids"]:
                        case = cases[identifier]
                        for mode in (("schema", "plain") if repeat == 0 else ("plain", "schema")):
                            request = make_request(case, "qwen3:4b", prompt_version=prompt)
                            request["messages"][0]["content"] += '\nOutput exactly one JSON object with keys status, action, target. Status must be action, clarify or unsupported. Action and target are canonical strings for action, otherwise null. No markdown or explanations.'
                            if mode == "plain":
                                del request["format"]
                            row = {"id": identifier, "repeat": repeat, "prompt": prompt, "mode": mode,
                                   "request": request, "correct": False, "valid": False}
                            start = time.perf_counter()
                            try:
                                response = client.post("/api/chat", json=request)
                                row["raw_response"] = response.text
                                response.raise_for_status()
                                body = response.json()
                                if not body.get("done") or body.get("done_reason") == "length":
                                    raise ValueError("Incomplete response")
                                prediction = Prediction.model_validate_json(body["message"]["content"])
                                row.update(valid=True, prediction=prediction.model_dump())
                                expected = {"status": case.expected_status, "action": case.expected_action.action if case.expected_action else None,
                                            "target": case.expected_action.target if case.expected_action else None}
                                row["expected"] = expected
                                row["correct"] = prediction.model_dump() == expected
                            except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                                row["error"] = str(exc)
                            row["seconds"] = time.perf_counter() - start
                            rows.append(row)
                            output.write(json.dumps(row) + "\n")
                            output.flush()
                            print(f"{repeat} {prompt} {mode} {identifier}: {row.get('prediction', row.get('error'))}", flush=True)
        summary = {}
        for prompt in ("v1", "v2"):
            for mode in ("schema", "plain"):
                group = [r for r in rows if r["prompt"] == prompt and r["mode"] == mode]
                summary[f"{prompt}/{mode}"] = {"count": len(group), "correct": sum(r["correct"] for r in group), "valid": sum(r["valid"] for r in group)}
        (folder / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
        print(f"Saved diagnostic: {folder}")


if __name__ == "__main__":
    main()
