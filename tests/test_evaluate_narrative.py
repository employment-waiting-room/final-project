import hashlib
import json

import httpx
import pytest

from observatory.evaluate_narrative import evaluate_case, make_request, run, summarise
from observatory.media_fixtures import MEDIA_DATA, load_media


def body_for(request):
    facts = json.loads(request["messages"][1]["content"])
    return {"done": True, "done_reason": "stop", "load_duration": 123,
            "message": {"content": json.dumps({"description": " ".join(["word"] * 60),
            "suggestions": facts["allowed_suggestions"], "visual_brief_id": facts["visual_brief_id"]})}}


def test_candidate_requests_differ_only_in_model_and_do_not_leak_review_labels():
    fixture = load_media().narratives[0]
    before = fixture.model_dump_json()
    a, b = make_request(fixture, "qwen"), make_request(fixture, "gemma")
    b["model"] = "qwen"
    assert a == b
    assert json.loads(a["messages"][1]["content"]) == fixture.input.model_dump()
    assert fixture.model_dump_json() == before
    assert "required_facts" not in a["messages"][1]["content"]
    assert a["options"]["num_predict"] == 600 and not a["think"]


@pytest.mark.parametrize("fault", ["timeout", "http", "json", "envelope", "missing", "content",
    "incomplete", "truncated", "schema", "suggestions", "brief", "length"])
def test_failed_attempts_preserve_evidence_and_count_in_denominator(fault):
    fixture = load_media().narratives[0]
    request = make_request(fixture, "mock")
    calls = []
    def respond(http_request):
        calls.append(http_request)
        if fault == "timeout": raise httpx.ReadTimeout("test", request=http_request)
        if fault == "http": return httpx.Response(500, text="failed")
        if fault == "json": return httpx.Response(200, text="not JSON")
        if fault == "envelope": return httpx.Response(200, json=[])
        body = body_for(request)
        if fault == "missing": body.pop("message")
        elif fault == "content": body["message"]["content"] = 5
        elif fault == "incomplete": body["done"] = False
        elif fault == "truncated": body["done_reason"] = "length"
        else:
            content = json.loads(body["message"]["content"])
            if fault == "schema": content["extra"] = True
            elif fault == "suggestions": content["suggestions"] = []
            elif fault == "brief": content["visual_brief_id"] = "library"
            elif fault == "length": content["description"] = "Too short."
            body["message"]["content"] = json.dumps(content)
        return httpx.Response(200, json=body)
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
        row = evaluate_case(client, fixture, request)
    assert len(calls) == 1 and not row["structural_pass"]
    if fault != "timeout": assert row["raw_response"]
    assert row["semantic_pass"] is None
    summary = summarise([{**row, "first_in_block": True}])
    assert summary["overall"]["attempts"] == 1
    assert summary["overall"]["structural_pass_rate"] == 0


def test_successful_structure_does_not_claim_semantic_quality_or_mutate_gameplay(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Narrative evaluation must not invoke gameplay")
    monkeypatch.setattr("observatory.intent.handle_text", forbidden)
    monkeypatch.setattr("observatory.engine.apply_action", forbidden)
    fixture = load_media().narratives[0]
    request = make_request(fixture, "mock")
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=body_for(request)))) as client:
        row = evaluate_case(client, fixture, request)
    assert row["structural_pass"] and row["semantic_review"] == "pending"
    assert row["semantic_pass"] is None
    assert row["ollama_metrics"]["load_duration"] == 123
    assert row["ollama_metrics"]["eval_duration"] is None


def test_run_reverses_order_preserves_every_attempt_and_creates_pending_reviews(tmp_path):
    requests = []
    def respond(request):
        if request.method == "GET": return httpx.Response(200, json={"metadata": "mock"})
        payload = json.loads(request.content)
        requests.append(payload)
        if len(requests) == 1: return httpx.Response(500, text="first failed")
        return httpx.Response(200, json=body_for(payload))
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
        folder = run(client, MEDIA_DATA, tmp_path, ["a", "b"], limit=2)
    manifest = json.loads((folder / "manifest.json").read_text())
    rows = [json.loads(line) for line in (folder / "results.jsonl").read_text().splitlines()]
    summary = json.loads((folder / "summary.json").read_text())
    assert [r["model"] for r in rows] == ["a", "a", "b", "b", "b", "b", "a", "a"]
    assert [r["seed"] for r in rows] == [42] * 4 + [43] * 4
    assert len(requests) == len(rows) == 8
    assert manifest["status"] == "completed" and manifest["partial_run"]
    assert manifest["completed_attempts"] == manifest["planned_attempts"] == 8
    assert manifest["dataset_sha256"] == hashlib.sha256((folder / "dataset.json").read_bytes()).hexdigest()
    assert manifest["protocol_sha256"] == hashlib.sha256((folder / "protocol.md").read_bytes()).hexdigest()
    assert summary["overall"]["structural_pass_rate"] == 7 / 8
    assert summary["overall"]["semantic_pass_rate"] is None
    for row in rows:
        saved_request = json.loads((folder / "requests" / f"{row['attempt_id']}.json").read_text())
        assert saved_request == row["request"]
        review = json.loads((folder / "reviews" / f"{row['attempt_id']}.json").read_text())
        assert review["status"] == "pending" and review["readability"] is None
        assert review["critical_contradictions"] is None
        assert all(f["judgement"] is None for f in review["required_facts"])


def test_interruption_preserves_completed_rows_and_pending_request(tmp_path):
    calls = 0
    def respond(request):
        nonlocal calls
        if request.method == "GET": return httpx.Response(500)
        calls += 1
        if calls == 2: raise KeyboardInterrupt()
        return httpx.Response(200, json=body_for(json.loads(request.content)))
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(KeyboardInterrupt):
            run(client, MEDIA_DATA, tmp_path, ["mock"], repetitions=1, limit=2)
    folder = next(tmp_path.iterdir())
    manifest = json.loads((folder / "manifest.json").read_text())
    assert manifest["status"] == "interrupted" and manifest["completed_attempts"] == 1
    assert manifest["partial_run"] and "runtime_error" in manifest
    assert len((folder / "results.jsonl").read_text().splitlines()) == 1
    assert len(list((folder / "requests").glob("*.json"))) == 2
    assert json.loads((folder / "summary.json").read_text())["overall"]["attempts"] == 1


@pytest.mark.parametrize("kwargs", [{"models": []}, {"models": ["a", "a"]}, {"models": [" "]},
    {"models": ["a"], "limit": 0}, {"models": ["a"], "repetitions": 0}])
def test_invalid_configuration_makes_no_requests_or_files(tmp_path, kwargs):
    def forbidden(request): pytest.fail("No network access expected")
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(forbidden)) as client:
        with pytest.raises(ValueError): run(client, MEDIA_DATA, tmp_path, **kwargs)
    assert not list(tmp_path.iterdir())


def test_wrong_dataset_split_rejected_before_output_or_network(tmp_path):
    data = json.loads(MEDIA_DATA.read_text())
    data["split"] = "held_out"
    source = tmp_path / "wrong.json"
    source.write_text(json.dumps(data))
    output = tmp_path / "output"
    def forbidden(request): pytest.fail("No network access expected")
    with httpx.Client(base_url="http://test", transport=httpx.MockTransport(forbidden)) as client:
        with pytest.raises(ValueError): run(client, source, output, ["mock"])
    assert not output.exists()
