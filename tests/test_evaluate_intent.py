import json

import httpx
import pytest

from observatory.evaluate_intent import evaluate_case, make_request, run, summarise, visible_context
from observatory.fixtures import DATA, State, load_dataset


def case(identifier):
    return next(c for c in load_dataset().cases if c.id == identifier)


def client_for(payload=None, *, status=200, done=True, reason="stop", timeout=False):
    def respond(request):
        if timeout:
            raise httpx.ReadTimeout("simulated", request=request)
        return httpx.Response(status, json={"done": done, "done_reason": reason,
                             "message": {"content": json.dumps(payload)}})
    return httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(respond))


def test_prompt_uses_only_projected_context():
    request = make_request(case("I01"), "candidate")
    user = json.loads(request["messages"][1]["content"])
    assert set(user) == {"context", "player_request"}
    assert "library_key" not in user["context"]["visible_objects"]
    assert "spare_fuse" not in visible_context(State())["visible_objects"]
    assert request["model"] == "candidate"
    assert not any(k in user for k in ("setup", "expected_action", "forbidden_claims"))


def test_correct_action_and_input_immutability():
    original = case("I01")
    before = original.model_dump_json()
    with client_for({"status": "action", "action": "look_around", "target": "current_room"}) as client:
        row = evaluate_case(client, original, "test")
    assert row["intent_pass"] and row["reference_transition_pass"]
    assert original.model_dump_json() == before
    assert row["source"] == "model" and row["raw_response"]


def test_wrong_but_rejected_action_is_not_correct_intent():
    # Both actions fail prerequisites, but only unlocking expresses I04's intent.
    with client_for({"status": "action", "action": "collect_key", "target": "library_key"}) as client:
        row = evaluate_case(client, case("I04"), "test")
    assert row["structural_pass"] and row["reference_transition_pass"]
    assert not row["intent_pass"]


@pytest.mark.parametrize("kwargs", [
    {"payload": {"status": "action", "action": "unlock_library", "target": "desk"}},
    {"payload": {"status": "unsupported", "action": "inspect_desk", "target": "desk"}},
    {"payload": "invalid"}, {"done": False}, {"reason": "length"},
    {"status": 500}, {"timeout": True},
])
def test_errors_are_recorded_and_count_as_failures(kwargs):
    with client_for(**kwargs) as client:
        row = evaluate_case(client, case("I01"), "test")
    assert "error" in row and not row["structural_pass"] and not row["intent_pass"]
    assert summarise([row])["overall"]["errors"] == 1


def test_unsupported_requests_reach_model_without_local_guard():
    with client_for({"status": "unsupported", "action": None, "target": None}) as client:
        row = evaluate_case(client, case("I13"), "test")
    assert row["intent_pass"] and "raw_response" in row


def test_run_persists_errors_and_continues(tmp_path):
    calls = []
    def respond(request):
        if request.method == "GET":
            return httpx.Response(200, json={"version": "mock"})
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(500)
        return httpx.Response(200, json={"done": True, "message": {"content": json.dumps(
            {"status": "action", "action": "inspect_desk", "target": "desk"})}})
    with httpx.Client(base_url="http://127.0.0.1:11434", transport=httpx.MockTransport(respond)) as client:
        folder = run(client, DATA, tmp_path, "mock", limit=2)
    rows = [json.loads(line) for line in (folder / "results.jsonl").read_text().splitlines()]
    summary = json.loads((folder / "summary.json").read_text())
    manifest = json.loads((folder / "manifest.json").read_text())
    assert len(rows) == 2 and rows[1]["intent_pass"]
    assert summary["overall"]["intent_pass"] == 0.5
    assert summary["overall"]["errors"] == 1
    assert manifest["partial_run"] and len(manifest["dataset_sha256"]) == 64
    assert manifest["split"] == "development"
