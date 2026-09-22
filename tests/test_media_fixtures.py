import json

import pytest
from pydantic import ValidationError

from observatory.fixtures import ROOMS, load_dataset
from observatory.media_fixtures import MediaDataset, check_narrative, load_media
from scripts.build_media_fixtures import build


def test_saved_media_matches_reproducible_builder_and_covers_world():
    data = load_media()
    assert data == build()
    assert len(data.narratives) == 16 and len(data.speech) == 10
    assert {row.input.location for row in data.narratives} == ROOMS
    cases = {c.id: c for c in load_dataset().cases}
    assert {cases[row.source_case_id].expected_state.ending for row in data.narratives} >= {"rescued", "sheltered"}
    assert {row.input.outcome for row in data.narratives} >= {"changed", "observed", "unchanged", "rejected"}


def test_narrative_projection_does_not_reveal_hidden_items_or_review_labels():
    rows = {row.source_case_id: row for row in load_media().narratives}
    for case_id, secret in [("S01", "key"), ("S06", "on the desk")]:
        facts = " ".join(rows[case_id].input.public_facts).lower()
        assert secret not in facts
    model_input = rows["S01"].input.model_dump()
    assert not {"required_facts", "forbidden_claims", "setup", "expected_state", "source_case_id"} & model_input.keys()
    assert rows["S20-rescue"].input.allowed_suggestions == []
    assert rows["S21"].input.allowed_suggestions == []


@pytest.mark.parametrize("change", ["inventory", "outcome", "suggestions", "reference", "room", "speech", "duplicate", "split"])
def test_corrupted_media_contract_rejected(change):
    data = load_media().model_dump(mode="json")
    first = data["narratives"][0]
    if change == "inventory": first["input"]["inventory"] = ["library_key"]
    elif change == "outcome": first["input"]["outcome"] = "changed"
    elif change == "suggestions": first["input"]["allowed_suggestions"] = []
    elif change == "reference": first["source_case_id"] = "not-a-development-case"
    elif change == "room": data["illustrations"][0]["id"] = "invented_room"
    elif change == "speech": data["speech"][0]["focus_terms"] = ["absent-word"]
    elif change == "duplicate": data["speech"][1]["id"] = data["speech"][0]["id"]
    else: data["split"] = "held_out"
    with pytest.raises(ValidationError):
        MediaDataset.model_validate_json(json.dumps(data))


def response_for(fixture, words=60):
    return {"description": " ".join(["word"] * words),
            "suggestions": [a.model_dump() for a in fixture.input.allowed_suggestions],
            "visual_brief_id": fixture.input.visual_brief_id}


@pytest.mark.parametrize("words,valid", [(59, False), (60, True), (100, True), (101, False)])
def test_successful_narrative_length_boundaries(words, valid):
    row = load_media().narratives[0]
    checks = check_narrative(json.dumps(response_for(row, words)), row)
    assert checks["length_valid"] is valid
    assert checks["semantic_review"] == "pending"  # Nonsense can still be structurally valid.


@pytest.mark.parametrize("change,check", [("duplicate", "suggestions_valid"), ("missing", "suggestions_valid"),
    ("wrong_action", "suggestions_valid"), ("wrong_brief", "visual_brief_valid"), ("malformed", "schema_valid")])
def test_narrative_response_contract_failures(change, check):
    row = load_media().narratives[0]
    output = response_for(row)
    if change == "duplicate": output["suggestions"].append(output["suggestions"][0])
    elif change == "missing": output["suggestions"] = []
    elif change == "wrong_action": output["suggestions"] = [{"action": "unlock_library", "target": "library_door"}]
    elif change == "wrong_brief": output["visual_brief_id"] = "library"
    else: output["unexpected"] = True
    assert not check_narrative(json.dumps(output), row)[check]


def test_short_rejection_is_allowed_and_invalid_json_fails():
    row = next(r for r in load_media().narratives if r.source_case_id == "S06")
    assert check_narrative(json.dumps(response_for(row, 8)), row)["length_valid"]
    assert not check_narrative("not JSON", row)["schema_valid"]
