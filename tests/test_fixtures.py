import pytest
from pydantic import ValidationError
from observatory.fixtures import Action, Case, Dataset, State, load_dataset, materialise, transition


def test_saved_cases_validate_and_cover_draft():
    dataset = load_dataset()
    ids = {c.id for c in dataset.cases}
    assert {f'S{i:02}' for i in range(1,24) if i != 20} <= ids
    assert {'S20-rescue','S20-shelter'} <= ids
    assert {f'I{i:02}' for i in range(1,21)} <= ids


def test_shelter_without_manual_and_rescue_have_different_prerequisites():
    cases = {c.id:c for c in load_dataset().cases}
    assert cases['S21'].expected_state.ending == 'sheltered'
    assert not {'manual_read','beacon_aligned'} & set(cases['S21'].state.flags)
    assert cases['S22'].expected_state.ending is None
    assert cases['S23'].expected_state.ending is None
    assert cases['S20-rescue'].expected_state.ending == 'rescued'


def test_wrong_verb_and_looking_regressions_preserve_state():
    cases = {c.id:c for c in load_dataset().cases}
    assert cases['I06'].expected_status == 'unsupported'
    assert cases['I06'].expected_state == cases['I06'].state
    assert cases['I01'].expected_action.action == 'look_around'
    assert cases['I01'].expected_state == cases['I01'].state


def test_matched_controls_cross_state_and_language_labels():
    cases = [c for c in load_dataset().cases if c.id.startswith('M-')]
    assert {(c.state_complexity,c.language_difficulty) for c in cases} == {
        (s,l) for s in ['simple','moderate','complex'] for l in ['direct','paraphrase','ambiguous']}


@pytest.mark.parametrize('change', ['expected_state','setup','expected_action','state_complexity'])
def test_corrupted_fixture_is_rejected(change):
    row = next(c for c in load_dataset().cases if c.id == 'S07').model_dump()
    if change == 'expected_state': row[change]['location'] = 'workshop'
    elif change == 'setup': row[change] = []
    elif change == 'expected_action': row[change]['target'] = 'desk'
    else: row[change] = 'complex'
    with pytest.raises(ValidationError): Case.model_validate(row)


def test_duplicate_ids_and_wrong_split_are_rejected():
    data=load_dataset().model_dump()
    data['cases'].append(data['cases'][0])
    with pytest.raises(ValidationError): Dataset.model_validate(data)
    data=load_dataset().model_dump(); data['split']='held_out'
    with pytest.raises(ValidationError): Dataset.model_validate(data)


def test_setup_rejects_illegal_route():
    with pytest.raises(ValueError):
        materialise([Action(action='move',target='library')])


def test_reference_transition_does_not_mutate_input():
    original=State()
    updated,outcome=transition(original,Action(action='inspect_desk',target='desk'))
    assert original == State() and outcome == 'changed'
    assert updated.flags == ['desk_inspected'] and updated.revision == 1


def test_installed_fuse_cannot_be_carried():
    with pytest.raises(ValidationError):
        State(location='generator_room',visited=['entrance_hall','workshop','generator_room'],
              inventory=['spare_fuse'],flags=['toolbox_inspected','fuse_installed'])
