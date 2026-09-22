"""Entrance-hall presentation only. Bounded text checks do not prove prose truth."""
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .engine import GameState, allowed_actions

POLICY_VERSION = "hall-narrative-guards-v1"
PROMPT_VERSION = "hall-narrative-v1"
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
        sentences.append("The discovered library key remains on the desk, not yet collected.")
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
                            "Diffuse daylight provides visibility independently of electrical power.",
                            "The storm makes the mountain path unsafe.",
                            "No electricity has been restored and no rescue signal has been sent."],
            "inventory": sorted(state.inventory)}


def validate_description(description, state):
    """Conservative anchors + known failure patterns; not arbitrary semantic validation.

    Matching is deliberately conservative and may reject benign wording. Unseen
    paraphrases/inventions can still escape these checks; retain human evaluation.
    """
    reasons = []
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", description.strip())]
    anchors = required_sentences(state)
    if any(sentences.count(anchor) != 1 for anchor in anchors):
        reasons.append("missing_or_repeated_required_fact")
    count = len(re.findall(r"\b\w+(?:[-']\w+)*\b", description))
    if not 60 <= count <= 100:
        reasons.append("description_length")
    # Exclude canonical sentences: their negations/state are known to be correct.
    extra = " ".join(s for s in sentences if s not in anchors).casefold()
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

    def render(self, state: GameState):
        facts = payload(state)
        fallback = " ".join(facts["required_sentences"] + facts["scene_facts"])
        request = {"model": self.model, "stream": False, "think": False,
                   "format": GeneratedText.model_json_schema(),
                   "options": {"temperature": 0.3, "seed": 42, "num_ctx": 4096, "num_predict": 600},
                   "messages": [{"role": "system", "content": PROMPT},
                                {"role": "user", "content": json.dumps(facts)}]}
        record = {"policy_version": POLICY_VERSION, "prompt_version": PROMPT_VERSION,
                  "state": {"location": state.location, "inventory": sorted(state.inventory),
                            "desk_inspected": state.desk_inspected, "library_unlocked": state.library_unlocked},
                  "request": request, "source": "fallback", "validation_reasons": []}
        started = time.perf_counter()
        text = fallback
        try:
            if self.client is None:
                with httpx.Client(timeout=30, trust_env=False) as client:
                    response = client.post("http://127.0.0.1:11434/api/chat", json=request)
            else:
                response = self.client.post("http://127.0.0.1:11434/api/chat", json=request)
            record["raw_response"] = response.text
            response.raise_for_status()
            body = response.json()
            if not isinstance(body, dict) or body.get("done") is not True or body.get("done_reason") == "length":
                raise ValueError("Incomplete narrative response")
            generated = GeneratedText.model_validate_json(body["message"]["content"])
            reasons = validate_description(generated.description, state)
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
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid4().hex + ".json"
            (self.log_dir / name).write_text(json.dumps(record, indent=2), encoding="utf-8")
        except OSError:
            print("Warning: could not save the narrative log.")
        return scene
