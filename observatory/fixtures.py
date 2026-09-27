"""Development fixture contract, separate from the gameplay engine.

Run python -m observatory.fixtures to validate the saved dataset without inference.
The reference transitions materialise reachable states; they are not a model judge
or proof that the application's engine implements the full world correctly.
"""
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "evaluation" / "development.json"
ROOMS = {"entrance_hall", "library", "workshop", "generator_room", "telescope_chamber"}
FLAGS = {"desk_inspected", "library_unlocked", "toolbox_inspected", "manual_read",
         "fuse_installed", "power_on", "beacon_aligned"}
TARGETS = {
    "look_around": {"current_room"}, "inspect_desk": {"desk"},
    "collect_key": {"library_key"}, "unlock_library": {"library_door"},
    "move": ROOMS, "read_manual": {"manual"}, "inspect_toolbox": {"toolbox"},
    "collect_fuse": {"spare_fuse"}, "install_fuse": {"fuse_socket"},
    "start_generator": {"generator"}, "align_beacon": {"beacon"},
    "signal_rescue": {"signalling_console"}, "shelter": {"shelter_bench"},
}
EDGES = {frozenset(pair) for pair in [
    ("entrance_hall", "library"), ("entrance_hall", "workshop"),
    ("workshop", "generator_room"), ("library", "telescope_chamber")]}


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Action(Strict):
    action: str
    target: str

    @model_validator(mode="after")
    def valid_pair(self):
        if self.target not in TARGETS.get(self.action, set()):
            raise ValueError("Unknown action/target pair")
        return self


class State(Strict):
    location: str = "entrance_hall"
    inventory: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    visited: list[str] = Field(default_factory=lambda: ["entrance_hall"])
    ending: Literal["rescued", "sheltered"] | None = None
    revision: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def consistent(self):
        f, inv = set(self.flags), set(self.inventory)
        if self.location not in ROOMS or not set(self.visited) <= ROOMS or self.location not in self.visited:
            raise ValueError("Invalid location/visited rooms")
        if not f <= FLAGS or not inv <= {"library_key", "spare_fuse"}:
            raise ValueError("Unknown flag/item")
        if any(len(x) != len(set(x)) for x in (self.flags, self.inventory, self.visited)):
            raise ValueError("Duplicate state values")
        requirements = {"library_unlocked": "desk_inspected", "power_on": "fuse_installed",
                        "fuse_installed": "toolbox_inspected", "beacon_aligned": "power_on"}
        if any(a in f and b not in f for a, b in requirements.items()):
            raise ValueError("Missing prerequisite flag")
        if "library_key" in inv and "desk_inspected" not in f:
            raise ValueError("Undiscovered key")
        if "library_unlocked" in f and "library_key" not in inv:
            raise ValueError("Unlocked library must retain its key")
        if "spare_fuse" in inv and ("toolbox_inspected" not in f or "fuse_installed" in f):
            raise ValueError("Invalid carried fuse")
        if "beacon_aligned" in f and "manual_read" not in f:
            raise ValueError("Alignment requires manual")
        if self.ending and (self.location != "telescope_chamber" or "power_on" not in f):
            raise ValueError("Invalid ending location/power")
        if self.ending == "rescued" and "beacon_aligned" not in f:
            raise ValueError("Rescue requires alignment")
        return self


def transition(state: State, command: Action):
    """Reference world-v2 rules; rejected/no-op transitions retain all fields."""
    a, t = command.action, command.target
    f, inv = set(state.flags), set(state.inventory)
    loc = state.location
    if state.ending:
        return state, "rejected"
    if a == "look_around":
        return state, "observed"
    if a == "move":
        if frozenset((loc, t)) not in EDGES or (frozenset((loc, t)) == frozenset(("entrance_hall", "library")) and "library_unlocked" not in f):
            return state, "rejected"
        values = state.model_dump()
        values.update(location=t, visited=sorted(set(state.visited) | {t}), revision=state.revision + 1)
        return State.model_validate(values), "changed"
    rules = {
        "inspect_desk": ("entrance_hall", set(), set(), "desk_inspected"),
        "collect_key": ("entrance_hall", {"desk_inspected"}, set(), None),
        "unlock_library": ("entrance_hall", set(), {"library_key"}, "library_unlocked"),
        "read_manual": ("library", set(), set(), "manual_read"),
        "inspect_toolbox": ("workshop", set(), set(), "toolbox_inspected"),
        "collect_fuse": ("workshop", {"toolbox_inspected"}, set(), None),
        "install_fuse": ("generator_room", set(), {"spare_fuse"}, "fuse_installed"),
        "start_generator": ("generator_room", {"fuse_installed"}, set(), "power_on"),
        "align_beacon": ("telescope_chamber", {"power_on", "manual_read"}, set(), "beacon_aligned"),
        "signal_rescue": ("telescope_chamber", {"beacon_aligned"}, set(), None),
        "shelter": ("telescope_chamber", {"power_on"}, set(), None),
    }
    room, required_flags, required_items, effect = rules[a]
    if loc != room:
        return state, "rejected"
    if effect in f or (a == "collect_key" and "library_key" in inv) or (a == "collect_fuse" and ("spare_fuse" in inv or "fuse_installed" in f)):
        return state, "unchanged"
    if not required_flags <= f or not required_items <= inv:
        return state, "rejected"
    if effect:
        f.add(effect)
    if a == "collect_key": inv.add("library_key")
    if a == "collect_fuse": inv.add("spare_fuse")
    if a == "install_fuse": inv.remove("spare_fuse")
    values = state.model_dump()
    values.update(flags=sorted(f), inventory=sorted(inv), revision=state.revision + 1)
    if a in {"signal_rescue", "shelter"}:
        values["ending"] = "rescued" if a == "signal_rescue" else "sheltered"
    return State.model_validate(values), "changed"


def materialise(path: list[Action]) -> State:
    state = State()
    for command in path:
        state, outcome = transition(state, command)
        if outcome != "changed":
            raise ValueError("Setup path must contain only legal state-changing actions")
    return state


class Case(Strict):
    id: str
    source: str
    setup: list[Action]
    state: State
    request: str = Field(min_length=1, max_length=500)
    state_complexity: Literal["simple", "moderate", "complex"]
    language_difficulty: Literal["direct", "paraphrase", "ambiguous", "compound", "unsupported", "adversarial"]
    expected_status: Literal["action", "clarify", "unsupported"]
    expected_action: Action | None
    expected_outcome: Literal["changed", "observed", "unchanged", "rejected", "clarify", "unsupported"]
    expected_state: State
    required_facts: list[str] = Field(min_length=1)
    forbidden_claims: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def check_oracle(self):
        if materialise(self.setup) != self.state:
            raise ValueError("Input state does not match reachable setup")
        if self.expected_status == "action":
            if self.expected_action is None:
                raise ValueError("Action response needs a canonical action")
            after, outcome = transition(self.state, self.expected_action)
        else:
            if self.expected_action is not None:
                raise ValueError("Non-action must not propose an action")
            after, outcome = self.state, self.expected_status
        if after != self.expected_state or outcome != self.expected_outcome:
            raise ValueError("Expected state/outcome contradicts contract")
        n = len(self.state.flags)
        level = "simple" if n <= 1 else "moderate" if n <= 4 else "complex"
        if level != self.state_complexity:
            raise ValueError("State complexity does not match declared flag-count rubric")
        return self


class Dataset(Strict):
    version: Literal["world-v2-development-v1"]
    split: Literal["development"]
    provenance: str
    cases: list[Case] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [case.id for case in self.cases]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate fixture IDs")
        return self


def load_dataset(path=DATA):
    return Dataset.model_validate_json(Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    dataset = load_dataset()
    print(f"Validated {len(dataset.cases)} development cases; no model inference performed.")
