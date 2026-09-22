import json

import httpx
import pytest

from observatory.engine import GameState, allowed_actions, apply_action
from observatory.narrative import Narrator, payload, required_sentences, validate_description


def states():
    state = GameState()
    result = [state]
    for action in ("inspect_desk", "collect_key", "unlock_library"):
        state = apply_action(state, action)
        result.append(state)
    return result


def accepted_text(state):
    return " ".join(required_sentences(state)) + (
        " A dusty desk stands beside the door. Diffuse daylight illuminates the room."
        " The mountain path remains unsafe during the storm. You observe the desk"
        " in the daylight and the door beside it. The storm continues outside while"
        " you remain beside the dusty desk in the entrance hall."
    )


@pytest.mark.parametrize("state", states())
def test_accepted_text_uses_engine_owned_scene_metadata(tmp_path, state):
    calls = []
    def respond(request):
        calls.append(json.loads(request.content))
        return httpx.Response(200, json={"done": True, "message": {"content": json.dumps({"description": accepted_text(state)})}})
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        scene = Narrator(client, tmp_path).render(state)
    assert scene.source == "model" and scene.description == accepted_text(state)
    assert scene.suggestions == allowed_actions(state)
    assert scene.visual_brief_id == "entrance_hall"
    assert len(calls) == 1
    assert "suggestions" not in calls[0]["format"]["properties"]
    record = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert record["accepted_text"] == scene.description and record["source"] == "model"
    assert record["raw_response"]


@pytest.mark.parametrize("sentence", [
    "The door swings open.", "You enter the library.", "The generator now runs.",
    "The key is gone.", "Your inventory is empty.", "A stranger waits by the desk.",
    "A candle illuminates the room.", "I remain here.", "The lock is still locked.",
])
def test_known_hall_contradictions_trigger_fallback_even_with_correct_anchors(tmp_path, sentence):
    state = states()[-1]
    text = accepted_text(state) + " " + sentence
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json={
        "done": True, "message": {"content": json.dumps({"description": text})}}))) as client:
        scene = Narrator(client, tmp_path).render(state)
    assert scene.source == "fallback" and scene.validation_reasons
    assert sentence not in scene.description
    assert "closed and unlocked" in scene.description
    assert "You carry the library key." in scene.description
    assert scene.suggestions == ()


@pytest.mark.parametrize("fault", ["timeout", "http", "invalid_json", "extra_fields", "incomplete", "truncated", "interrupt"])
def test_errors_use_factual_fallback_without_retries(tmp_path, fault):
    state = states()[1]
    calls = []
    def respond(request):
        calls.append(request)
        if fault == "timeout": raise httpx.ReadTimeout("test", request=request)
        if fault == "interrupt": raise KeyboardInterrupt()
        if fault == "http": return httpx.Response(500, text="failure")
        content = {"description": accepted_text(state)}
        if fault == "extra_fields": content["suggestions"] = ["unlock_library"]
        return httpx.Response(200, json={"done": fault != "incomplete",
            "done_reason": "length" if fault == "truncated" else "stop",
            "message": {"content": "not JSON" if fault == "invalid_json" else json.dumps(content)}})
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        scene = Narrator(client, tmp_path).render(state)
    assert len(calls) == 1 and scene.source == "fallback"
    assert "not yet collected" in scene.description and "inventory is empty" in scene.description
    assert scene.suggestions == ("collect_key",)
    assert state == states()[1]


def test_repeated_render_cannot_change_state_or_duplicate_inventory(tmp_path):
    state = states()[2]
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(500))) as client:
        narrator = Narrator(client, tmp_path)
        assert narrator.render(state) == narrator.render(state)
    assert state == states()[2] and state.inventory == frozenset({"library_key"})
    assert len(list(tmp_path.glob("*.json"))) == 2


def test_anchors_required_and_duplicates_fail():
    state = states()[1]
    anchor = required_sentences(state)[0]
    assert "missing_or_repeated_required_fact" in validate_description(accepted_text(state).replace(anchor, ""), state)
    assert "missing_or_repeated_required_fact" in validate_description(accepted_text(state) + " " + anchor, state)
    assert "description_length" in validate_description(" ".join(required_sentences(state)), state)


def test_initial_prompt_and_fallback_do_not_disclose_hidden_key(tmp_path):
    state = GameState()
    assert "key" not in json.dumps(payload(state))
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(500))) as client:
        scene = Narrator(client, tmp_path).render(state)
    assert "key" not in scene.description


def test_log_failure_does_not_lose_scene(tmp_path, capsys):
    occupied = tmp_path / "file"
    occupied.write_text("existing")
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(500))) as client:
        scene = Narrator(client, occupied).render(states()[2])
    assert scene.source == "fallback" and "could not save" in capsys.readouterr().out


def test_unseen_inventions_are_not_claimed_to_be_detected():
    # Documents the practical boundary: these checks cannot prove arbitrary prose true.
    assert not validate_description(accepted_text(states()[2]) + " Purple butterflies hover nearby.", states()[2])


@pytest.mark.parametrize("state", states()[1:])
def test_exact_supplied_scene_facts_are_not_flagged_as_contradictions(state):
    facts = payload(state)
    text = " ".join(facts["required_sentences"] + facts["scene_facts"])
    assert set(validate_description(text, state)) <= {"description_length"}


@pytest.mark.parametrize("extra", [
    "The generator is now running.",
    "No electricity has been restored and no rescue signal has been sent, but now power returns.",
])
def test_trusted_fact_exemption_does_not_hide_appended_claims(extra):
    state = states()[2]
    text = " ".join(payload(state)["required_sentences"] + payload(state)["scene_facts"]) + " " + extra
    assert "power_or_ending_claim" in validate_description(text, state)
