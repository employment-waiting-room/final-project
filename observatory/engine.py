"""Deterministic entrance-hall rules, independent of model output."""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class GameState:
    location: str = "entrance_hall"
    inventory: frozenset[str] = frozenset()
    desk_inspected: bool = False
    library_unlocked: bool = False


ACTION_LABELS = {
    "inspect_desk": "Inspect the desk",
    "collect_key": "Collect the library key",
    "unlock_library": "Unlock the library door",
}


def allowed_actions(state: GameState) -> tuple[str, ...]:
    if state.location != "entrance_hall" or state.library_unlocked:
        return ()
    if not state.desk_inspected:
        return ("inspect_desk",)
    if "library_key" not in state.inventory:
        return ("collect_key",)
    return ("unlock_library",)


def apply_action(state: GameState, action: str) -> GameState:
    if action not in allowed_actions(state):
        raise ValueError(f"Action unavailable: {action}")
    if action == "inspect_desk":
        return replace(state, desk_inspected=True)
    if action == "collect_key":
        return replace(state, inventory=state.inventory | {"library_key"})
    return replace(state, library_unlocked=True)


def describe(state: GameState) -> str:
    if state.library_unlocked:
        return "The key turns in the lock. The library door is now unlocked."
    if "library_key" in state.inventory:
        return "You carry the library key. The library door remains locked."
    if state.desk_inspected:
        return "You discover a library key on the dusty desk. The library door is locked."
    return "You stand in the entrance hall. A dusty desk sits beside the locked library door."
