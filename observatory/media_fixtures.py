"""Offline development fixtures and structural narrative checks; no inference."""
import re
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from .fixtures import Action, ROOT, ROOMS, TARGETS, Strict, load_dataset, transition

MEDIA_DATA = ROOT / "evaluation/media_development.json"
ROOM_FACTS = {
    "entrance_hall": ["A dusty desk stands beside a closed library door.", "A passage leads to the workshop."],
    "library": ["Bookshelves line the library.", "An open instruction manual rests on a reading stand.", "Stairs lead to the telescope chamber."],
    "workshop": ["A closed toolbox rests on a dusty workbench.", "A doorway leads to the generator room."],
    "generator_room": ["The generator has a fuse socket and a start switch.", "Wall conduit runs beside its casing."],
    "telescope_chamber": ["A telescope carries a beacon attachment inside an enclosed dome.", "There is an alignment control, a signalling console and a shelter bench."],
}


class NarrativeInput(Strict):
    location: str
    public_facts: list[str] = Field(min_length=1)
    inventory: list[str]
    action: Action
    outcome: str
    allowed_suggestions: list[Action]
    visual_brief_id: str


def narrative_input(case):
    """Project verified post-action facts; never expose setup or review labels."""
    state = case.expected_state
    flags = set(state.flags)
    facts = list(ROOM_FACTS[state.location])
    facts += ["Diffuse daylight allows visibility without electrical power.",
              "The mountain path is unsafe during the storm."]
    if state.location == "entrance_hall":
        facts.append("The library door is unlocked." if "library_unlocked" in flags else "The library door is locked.")
        if "desk_inspected" in flags and "library_key" not in state.inventory:
            facts.append("A discovered library key remains on the desk, not yet collected.")
    if state.location == "workshop" and "toolbox_inspected" in flags:
        facts.append("The toolbox has been inspected and its lid closed again.")
        if "spare_fuse" not in state.inventory and "fuse_installed" not in flags:
            facts.append("A discovered spare fuse remains inside the toolbox, not yet collected.")
    if state.location == "generator_room" or "fuse_installed" in flags:
        facts.append("The fuse is installed, not carried." if "fuse_installed" in flags else "No fuse has been installed.")
    facts.append("The generator is running; power is restored." if "power_on" in flags else "The generator is stopped; power is off.")
    if "manual_read" in flags:
        facts.append("You learned the procedure: install the fuse, start the generator, align the beacon, then choose an ending.")
    if state.location == "telescope_chamber":
        facts.append("The beacon is aligned." if "beacon_aligned" in flags else "The beacon is not aligned.")
        if "manual_read" not in flags:
            facts.append("You have not learned the beacon procedure from the manual.")
    if state.ending == "rescued":
        facts.append("The valley station receives your rescue signal; rescuers arrive after the storm. The adventure has ended.")
    elif state.ending == "sheltered":
        facts.append("You shelter safely until morning and leave when the storm clears. No rescue signal was sent. The adventure has ended.")
    else:
        facts.append("No ending has been chosen and no rescue signal has been sent.")
    suggestions = []
    for action, targets in sorted(TARGETS.items()):
        for target in sorted(targets):
            command = Action(action=action, target=target)
            _, outcome = transition(state, command)
            if outcome in {"changed", "observed"}:
                suggestions.append(command)
    return NarrativeInput(location=state.location, public_facts=facts, inventory=state.inventory,
                          action=case.expected_action, outcome=case.expected_outcome,
                          allowed_suggestions=suggestions, visual_brief_id=state.location)


class NarrativeFixture(Strict):
    id: str
    source_case_id: str
    input: NarrativeInput
    required_facts: list[str] = Field(min_length=1)
    forbidden_claims: list[str] = Field(min_length=1)


class IllustrationFixture(Strict):
    id: str
    prompt: str = Field(min_length=1)
    required_details: list[str] = Field(min_length=1)
    forbidden_details: list[str] = Field(min_length=1)


class SpeechFixture(Strict):
    id: str
    text: str = Field(min_length=1)
    focus_terms: list[str] = Field(min_length=1)


class MediaDataset(Strict):
    version: Literal["world-v2-media-development-v1"]
    split: Literal["development"]
    provenance: str
    image_size: tuple[int, int]
    shared_style: str
    narratives: list[NarrativeFixture] = Field(min_length=1)
    illustrations: list[IllustrationFixture] = Field(min_length=5, max_length=5)
    speech: list[SpeechFixture] = Field(min_length=10, max_length=10)

    @model_validator(mode="after")
    def references(self):
        for group in (self.narratives, self.illustrations, self.speech):
            ids = [row.id for row in group]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate media fixture IDs")
        if {row.id for row in self.illustrations} != ROOMS:
            raise ValueError("Illustration briefs must cover the five rooms")
        if self.image_size != (512, 512):
            raise ValueError("Shared trial canvas must be 512x512 square")
        sources = {case.id: case for case in load_dataset().cases}
        for row in self.narratives:
            source = sources.get(row.source_case_id)
            if source is None or source.expected_action is None or row.input != narrative_input(source):
                raise ValueError("Narrative input differs from verified development outcome")
        for row in self.speech:
            if any(term.casefold() not in row.text.casefold() for term in row.focus_terms):
                raise ValueError("Speech focus term is absent from exact passage")
        return self


class NarrativeOutput(Strict):
    description: str = Field(min_length=1)
    suggestions: list[Action]
    visual_brief_id: str


def check_narrative(content, fixture):
    """Check structure only; never infer semantic correctness from valid JSON."""
    checks = {"schema_valid": False, "suggestions_valid": False, "visual_brief_valid": False,
              "length_valid": False, "word_count": None, "semantic_review": "pending"}
    try:
        scene = NarrativeOutput.model_validate_json(content)
    except ValidationError as exc:
        return {**checks, "error": str(exc)}
    pairs = [(a.action, a.target) for a in scene.suggestions]
    expected = {(a.action, a.target) for a in fixture.input.allowed_suggestions}
    count = len(re.findall(r"\b\w+(?:[-']\w+)*\b", scene.description))
    # Rejections/no-ops may use brief factual messages; successful scenes use 60-100 words.
    minimum = 1 if fixture.input.outcome in {"rejected", "unchanged"} else 60
    checks.update(schema_valid=True, suggestions_valid=len(pairs) == len(set(pairs)) and set(pairs) == expected,
                  visual_brief_valid=scene.visual_brief_id == fixture.input.visual_brief_id,
                  word_count=count, length_valid=minimum <= count <= 100)
    return checks


def load_media(path=MEDIA_DATA):
    return MediaDataset.model_validate_json(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    data = load_media()
    print(f"Validated {len(data.narratives)} narrative cases, {len(data.illustrations)} image briefs and {len(data.speech)} speech passages; no inference.")
