import json
import httpx
import pytest
from observatory.engine import GameState, apply_action
from observatory.intent import Interpreter, handle_text


def interpreter(tmp_path, payload=None, error=False):
    def respond(request):
        if error:
            raise httpx.ReadTimeout("test timeout", request=request)
        return httpx.Response(200, json={"done": True, "message": {"content": json.dumps(payload)}})
    return Interpreter(httpx.Client(transport=httpx.MockTransport(respond)), tmp_path)


def test_interpreted_sequence(tmp_path):
    state = GameState()
    for action, target in [("inspect_desk", "desk"), ("collect_key", "library_key"), ("unlock_library", "library_door")]:
        fake = interpreter(tmp_path, {"status": "action", "action": action, "target": target})
        state, _ = handle_text(state, "player wording", fake, lambda proposal: "yes")
    assert state.library_unlocked and state.inventory == frozenset({"library_key"})
    assert len(list(tmp_path.glob("*.json"))) == 3


@pytest.mark.parametrize("payload", [
    {"status": "action", "action": "unlock_library", "target": "library_door"},
    {"status": "action", "action": "collect_key", "target": "library_key"},
    {"status": "clarify", "action": None, "target": None},
    {"status": "unsupported", "action": None, "target": None},
    {"status": "action", "action": "inspect_desk", "target": "library_door"},
    {"status": "action", "action": "grant_everything", "target": "desk"},
    {"status": "clarify", "action": "inspect_desk", "target": "desk"},
    {"status": "action", "action": "inspect_desk", "target": "desk", "inventory": ["key"]},
    "not an intent object",
])
def test_non_action_or_invalid_output_preserves_state(tmp_path, payload):
    state = GameState()
    after, feedback = handle_text(state, "request", interpreter(tmp_path, payload))
    assert after is state
    assert feedback


def test_timeout_preserves_state(tmp_path):
    state = GameState()
    after, feedback = handle_text(state, "search desk", interpreter(tmp_path, error=True))
    assert after is state and "displayed number" in feedback


def test_repeated_collection_does_not_duplicate_key(tmp_path):
    state = apply_action(apply_action(GameState(), "inspect_desk"), "collect_key")
    after, feedback = handle_text(state, "take key", interpreter(tmp_path, {
        "status": "action", "action": "collect_key", "target": "library_key"}))
    assert after is state and "already" in feedback


@pytest.mark.parametrize("text", ["", " " * 4, "a" * 501])
def test_input_limits(tmp_path, text):
    state = GameState()
    after, feedback = handle_text(state, text, interpreter(tmp_path, error=True))
    assert after is state and "1-500" in feedback


@pytest.mark.parametrize("text", ["Examine it", "Search the desk and take the key", "Inspect desk; collect key"])
def test_conservative_clarification_does_not_call_model(tmp_path, text):
    state = GameState()
    after, feedback = handle_text(state, text, interpreter(tmp_path, error=True))
    assert after is state and "one action" in feedback


@pytest.mark.parametrize("answer", ["no", "n", "", "sure", "confirm", "1", "q", None, True])
@pytest.mark.parametrize("steps,action,target", [
    ([], "inspect_desk", "desk"),
    (["inspect_desk"], "collect_key", "library_key"),
    (["inspect_desk", "collect_key"], "unlock_library", "library_door"),
])
def test_cancellation_preserves_entire_state(tmp_path, answer, steps, action, target):
    state = GameState()
    for step in steps:
        state = apply_action(state, step)
    fake = interpreter(tmp_path, {"status": "action", "action": action, "target": target})
    after, feedback = handle_text(state, "player request", fake, lambda proposal: answer)
    assert after is state
    assert "cancelled" in feedback


def test_missing_confirmation_cannot_apply_legal_action(tmp_path):
    state = GameState()
    fake = interpreter(tmp_path, {"status": "action", "action": "inspect_desk", "target": "desk"})
    after, feedback = handle_text(state, "search desk", fake)
    assert after is state and "Confirmation required" in feedback


@pytest.mark.parametrize("answer", ["y", "yes", " YES "])
def test_preview_precedes_transition_and_inference_runs_once(tmp_path, answer):
    state = GameState()
    previews = []
    def confirm(proposal):
        assert state == GameState()
        previews.append(proposal)
        return answer
    fake = interpreter(tmp_path, {"status": "action", "action": "inspect_desk", "target": "desk"})
    after, _ = handle_text(state, "search desk", fake, confirm)
    assert previews == ["Interpreted action: Inspect the desk (target: desk)."]
    assert after == apply_action(state, "inspect_desk")
    assert len(list(tmp_path.glob("*.json"))) == 1


@pytest.mark.parametrize("payload", [
    {"status": "action", "action": "unlock_library", "target": "library_door"},
    {"status": "clarify", "action": None, "target": None},
    {"status": "unsupported", "action": None, "target": None},
    {"status": "action", "action": "inspect_desk", "target": "library_door"},
])
def test_rejected_predictions_never_request_confirmation(tmp_path, payload):
    def confirm(proposal):
        pytest.fail("Rejected predictions must not reach confirmation")
    state = GameState()
    after, _ = handle_text(state, "request", interpreter(tmp_path, payload), confirm)
    assert after is state


@pytest.mark.parametrize("text,steps,action,target", [
    ("look around the room", [], "inspect_desk", "desk"),
    ("knock on the door", ["inspect_desk", "collect_key"], "unlock_library", "library_door"),
])
def test_wrong_but_legal_interpretation_can_be_cancelled(tmp_path, text, steps, action, target):
    state = GameState()
    for step in steps:
        state = apply_action(state, step)
    proposals = []
    def cancel(proposal):
        proposals.append(proposal)
        return "no"
    after, _ = handle_text(state, text, interpreter(tmp_path, {
        "status": "action", "action": action, "target": target}), cancel)
    assert after is state and target in proposals[0]
