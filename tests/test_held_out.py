import json

import httpx
import pytest
from pydantic import ValidationError

from observatory.evaluate_intent import run, visible_context
from observatory.fixtures import TARGETS, load_dataset
from observatory.held_out import MANIFEST, RESERVED, load_reserved, validate_separation
from scripts.reserve_intent_fixtures import reserve


def test_reserved_contract_coverage_and_separation():
    held = load_reserved()
    development = load_dataset()
    assert len(held.cases) == 30
    assert {c.expected_action.action for c in held.cases if c.expected_action} == set(TARGETS)
    assert {c.language_difficulty for c in held.cases} == {
        "direct", "paraphrase", "ambiguous", "compound", "unsupported", "adversarial"}
    assert {c.state_complexity for c in held.cases} == {"simple", "moderate", "complex"}
    assert {c.expected_state.ending for c in held.cases} >= {"rescued", "sheltered"}
    # New visible contexts, not just revision/route differences, are reserved.
    known = {json.dumps(visible_context(c.state), sort_keys=True) for c in development.cases}
    assert any(json.dumps(visible_context(c.state), sort_keys=True) not in known for c in held.cases)
    validate_separation(held, development)


def test_development_runner_refuses_reserved_before_network_or_outputs(tmp_path):
    def forbidden(request):
        pytest.fail("Reserved data must not reach the development model client")
    with httpx.Client(transport=httpx.MockTransport(forbidden)) as client:
        with pytest.raises(ValidationError):
            run(client, RESERVED, tmp_path, "not-a-real-model")
    assert not list(tmp_path.iterdir())


def test_hash_detects_changes(tmp_path):
    edited = tmp_path / "edited.json"
    edited.write_bytes(RESERVED.read_bytes() + b" ")
    with pytest.raises(ValueError, match="changed since reservation"):
        load_reserved(edited, MANIFEST)


@pytest.mark.parametrize("collision", ["id", "wording", "duplicate"])
def test_split_contamination_is_rejected(collision):
    held = load_reserved().model_copy(deep=True)
    dev = load_dataset()
    if collision == "id":
        held.cases[0].id = dev.cases[0].id
    elif collision == "wording":
        held.cases[0].request = "  " + dev.cases[0].request.upper() + "!!!"
    else:
        held.cases[0].request = held.cases[1].request
    with pytest.raises(ValueError):
        validate_separation(held, dev)


@pytest.mark.parametrize("existing", ["data", "manifest"])
def test_reservation_never_overwrites_existing_files(tmp_path, existing):
    data, manifest = tmp_path / "data.json", tmp_path / "manifest.json"
    target = data if existing == "data" else manifest
    target.write_text("preserve", encoding="utf-8")
    with pytest.raises(FileExistsError):
        reserve(data, manifest)
    assert target.read_text(encoding="utf-8") == "preserve"
    assert len(list(tmp_path.iterdir())) == 1
