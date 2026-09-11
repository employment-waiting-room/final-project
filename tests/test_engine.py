import pytest
from observatory.engine import GameState, allowed_actions, apply_action


def test_complete_sequence_preserves_previous_states():
    initial = GameState()
    inspected = apply_action(initial, "inspect_desk")
    collected = apply_action(inspected, "collect_key")
    unlocked = apply_action(collected, "unlock_library")
    assert not initial.desk_inspected and not initial.inventory
    assert inspected.desk_inspected and not inspected.inventory
    assert collected.inventory == frozenset({"library_key"})
    assert not collected.library_unlocked
    assert unlocked.library_unlocked
    assert unlocked.inventory == collected.inventory
    assert allowed_actions(unlocked) == ()


@pytest.mark.parametrize("action", ["collect_key", "unlock_library", "invent_key"])
def test_initial_state_rejects_unavailable_actions(action):
    state = GameState()
    with pytest.raises(ValueError):
        apply_action(state, action)
    assert state == GameState()


def test_revealing_key_does_not_allow_unlocking():
    state = apply_action(GameState(), "inspect_desk")
    with pytest.raises(ValueError):
        apply_action(state, "unlock_library")


@pytest.mark.parametrize("repeat", ["inspect_desk", "collect_key", "unlock_library"])
def test_repeated_action_is_rejected(repeat):
    state = GameState()
    for action in ("inspect_desk", "collect_key", "unlock_library"):
        state = apply_action(state, action)
        if action == repeat:
            break
    before = state
    with pytest.raises(ValueError):
        apply_action(state, repeat)
    assert state == before


def test_actions_cannot_be_used_in_another_room():
    state = GameState(location="library", desk_inspected=True,
                      inventory=frozenset({"library_key"}))
    assert allowed_actions(state) == ()
    with pytest.raises(ValueError):
        apply_action(state, "unlock_library")
