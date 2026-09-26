"""Entrance-hall presentation only. Bounded text checks do not prove prose truth."""
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .engine import GameState, allowed_actions, apply_action
from .gameplay_io import post_chat, save_record
from .world import OUTCOMES

POLICY_VERSION = "hall-narrative-guards-v1.1"
PROMPT_VERSION = "hall-narrative-v1"
OUTCOME_PROMPT_VERSION = "hall-outcome-v1"
OUTCOME_POLICY_VERSION = "hall-outcome-guards-v1"
OUTCOME_PROMPT = """Describe only the completed action's outcome in second person.
Return only JSON with a description string: 1-3 sentences, at most 45 words.
Copy each required sentence exactly once. You may add one brief grounded detail
about this action, but do not recap the room, weather, lighting or earlier actions.
Context is for consistency only. Do not invent events, items or people, open the
door, move the player, suggest actions or perform another transition.
"""
PROMPT = """Describe the verified entrance-hall state in second person, in 60-100 words.
Return only JSON with a description string. Copy each required sentence exactly
once as a complete sentence. Surround it with concise prose grounded only in the
supplied scene facts. The outcome has already happened; do not perform another
action. Do not invent characters, items, exits, light sources or puzzle effects.
Do not open doors or move the player. Daylight does not generate electricity.
Do not supply suggestions or illustration IDs; the application owns those fields.
"""


class GeneratedText(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    description: str = Field(min_length=1, max_length=3000)


@dataclass(frozen=True)
class Scene:
    description: str
    suggestions: tuple[str, ...]
    visual_brief_id: str
    source: str
    validation_reasons: tuple[str, ...] = ()


def required_sentences(state):
    """Canonical anchors and fallback follow the prototype's three-step sequence."""
    door = "unlocked" if state.library_unlocked else "locked"
    sentences = ["You remain in the entrance hall.", f"The library door remains closed and {door}."]
    if "library_key" in state.inventory:
        sentences.append("You carry the library key.")
    elif state.desk_inspected:
        sentences.append("A key lies on the desk.")
        sentences.append("Your inventory is empty.")
    else:
        sentences.append("Your inventory is empty.")
    return sentences


def payload(state):
    if state.location != "entrance_hall" or state.inventory - {"library_key"}:
        raise ValueError("Narrative adapter supports only the entrance-hall prototype")
    if state.library_unlocked and "library_key" not in state.inventory or state.inventory and not state.desk_inspected:
        raise ValueError("Inconsistent entrance-hall state")
    return {"required_sentences": required_sentences(state),
            "scene_facts": ["A dusty desk stands beside the library door.",
                            "Sunlight floods through the window, illuminating the room.",
                            "The storm makes the mountain path unsafe.",
                            "No electricity has been restored and no rescue signal has been sent."],
            "inventory": sorted(state.inventory)}


def outcome_payload(previous, state):
    """Derive the event from an actual legal before/after pair, not model output."""
    context = payload(state)
    matches = [action for action in allowed_actions(previous)
               if apply_action(previous, action) == state]
    if len(matches) != 1:
        raise ValueError("Expected one legal entrance-hall transition")
    action = matches[0]
    return {"action": action, "required_sentences": re.split(r'(?<=[.!?])\s+', OUTCOMES[action]),
            "context_only": context}


def validate_description(description, state, previous=None):
    """Conservative anchors + known failure patterns; not arbitrary semantic validation.

    Matching is deliberately conservative and may reject benign wording. Unseen
    paraphrases/inventions can still escape these checks; retain human evaluation.
    """
    reasons = []
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", description.strip())]
    anchors = required_sentences(state) if previous is None else outcome_payload(previous, state)["required_sentences"]
    if any(sentences.count(anchor) != 1 for anchor in anchors):
        reasons.append("missing_or_repeated_required_fact")
    count = len(re.findall(r"\b\w+(?:[-']\w+)*\b", description))
    if (previous is None and not 60 <= count <= 100) or (previous is not None and not 1 <= count <= 45):
        reasons.append("description_length")
    if previous is not None and len(sentences) > 3:
        reasons.append("outcome_sentence_count")
    # Exact supplied facts are trusted too, including negative power/ending facts.
    # Only exempt whole sentences; appended or paraphrased claims stay checked.
    trusted = set(anchors + (payload(state)["scene_facts"] if previous is None else []))
    extra = " ".join(s for s in sentences if s not in trusted).casefold()
    if previous is not None and re.search(r'\b(room|hall|weather|storm|daylight|glazing|lighting)\b', extra):
        reasons.append("scene_recap")
    patterns = {
        "door_opening": r"\b(open|opens|opened|opening|ajar|swings?)\b",
        "unrequested_movement": r"\b(enter|entered|entering|leave|left|depart|travel|walk into)\b",
        "power_or_ending_claim": r"\b(generator|electricity|power|rescue|rescued|signal|ending|daylight restores)\b",
        "invented_entity": r"\b(person|caretaker|stranger|guard|lantern|candle|torch|toolkit|map|fuse|console|portal)\b",
        "first_person": r"\b(i|my|me|we|our)\b",
        # State-sensitive claims outside anchors are rejected rather than relying
        # on fragile positive/negative keyword interpretation.
        "extra_inventory_or_lock_claim": r"\b(key|keys|inventory|carry|carried|collect|collected|lock|locked|unlock|unlocked|sealed)\b",
    }
    for name, pattern in patterns.items():
        if re.search(pattern, extra):
            reasons.append(name)
    return tuple(reasons)


class Narrator:
    def __init__(self, client=None, log_dir=None, model="qwen3:4b"):
        self.client = client
        self.model = model
        self.log_dir = Path(log_dir) if log_dir else Path(__file__).resolve().parents[1] / "generated/gameplay-narratives"

    def render(self, state: GameState, previous=None):
        facts = payload(state) if previous is None else outcome_payload(previous, state)
        fallback = " ".join(facts["required_sentences"] + (facts["scene_facts"] if previous is None else []))
        request = {"model": self.model, "stream": False, "think": False,
                   "format": GeneratedText.model_json_schema(),
                   "options": {"temperature": 0.3, "seed": 42, "num_ctx": 4096, "num_predict": 600},
                   "messages": [{"role": "system", "content": PROMPT if previous is None else OUTCOME_PROMPT},
                                {"role": "user", "content": json.dumps(facts)}]}
        record = {"policy_version": POLICY_VERSION, "prompt_version": PROMPT_VERSION,
                  "state": {"location": state.location, "inventory": sorted(state.inventory),
                            "desk_inspected": state.desk_inspected, "library_unlocked": state.library_unlocked},
                  "request": request, "source": "fallback", "validation_reasons": []}
        if previous is not None:
            record.update(policy_version=OUTCOME_POLICY_VERSION, prompt_version=OUTCOME_PROMPT_VERSION,
                          action=facts['action'], previous_state={
                              'location': previous.location, 'inventory': sorted(previous.inventory),
                              'desk_inspected': previous.desk_inspected, 'library_unlocked': previous.library_unlocked})
        started = time.perf_counter()
        text = fallback
        try:
            response = post_chat(request, self.client)
            record["raw_response"] = response.text
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, dict) or body.get("done") is not True or body.get("done_reason") == "length":
                raise ValueError("Incomplete narrative response")
            generated = GeneratedText.model_validate_json(body["message"]["content"])
            reasons = validate_description(generated.description, state, previous)
            record["validation_reasons"] = list(reasons)
            if not reasons:
                text = generated.description
                record["source"] = "model"
        except KeyboardInterrupt:
            record["validation_reasons"] = ["generation_interrupted"]
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
            record["validation_reasons"] = ["generation_or_schema_failure"]
            record["error"] = f"{type(exc).__name__}: {exc}"
        record.update(wall_seconds=time.perf_counter() - started, accepted_text=text)
        scene = Scene(text, allowed_actions(state), state.location, record["source"], tuple(record["validation_reasons"]))
        record.update(suggestions=list(scene.suggestions), visual_brief_id=scene.visual_brief_id)
        save_record(self.log_dir, record, 'Warning: could not save the narrative log.')
        return scene
