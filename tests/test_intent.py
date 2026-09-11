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
        state, _ = handle_text(state, "player wording", fake)
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
