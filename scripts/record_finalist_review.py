"""Materialise explicitly authored assistant review, not an automatic prose judge.

Annotations below were written after reading all 64 outputs. No model calls.
Source model outputs and pending human-review forms are never modified.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation/assistant_reviews/narrative_v2_finalists.json"
RUNS = {
    "qwen3:4b": "20260922T134438589698Z-50579097",
    "phi4-mini:3.8b": "20260922T200831838642Z-53330a53",
}
# Each row: attempt number, required-fact judgements (satisfied/missing/unclear),
# readability 1-5, definite violation excerpts, uncertain excerpts, review note.
# Quotations are checked against the original description before writing.
ANNOTATIONS = {
    "qwen3:4b": [
        (1, "ss", 4, [], [], "Facts preserved; first person violates requested viewpoint but is not a state contradiction."),
        (2, "ss", 4, [], [], "Discovery remains separate from collection; first person."),
        (3, "sm", 3, ["which is now unlocked", "collected the library key from your inventory"], [], "Collection incorrectly unlocks the door and is described as taking an item from existing inventory."),
        (4, "s", 4, [], ["cannot open the door"], "Could mean currently closed/locked, or incorrectly imply the carried key cannot enable access; developer judgement needed."),
        (5, "ss", 3, ["closed workshop passage"], [], "Invents closure of the accessible workshop passage; empty inventory supplies lack of key."),
        (6, "sus", 3, ["now-open library door", "workshop passage remains closed"], [], "Unlocking does not open the door; workshop blockage invented. Continued key possession is only implied."),
        (7, "ss", 4, [], [], "Procedure and power-off state preserved; slightly compressed prose."),
        (8, "ss", 3, [], ["lid is sealed"], "Closed may be intended, but sealed could imply an extra access restriction; repetitive first-person prose. Schema failure assessed separately."),
        (9, "ss", 4, [], [], "Collected fuse and closed lid preserved; first person."),
        (10, "ss", 4, [], [], "Installed fuse, empty inventory and stopped generator preserved; first person."),
        (11, "ss", 3, ["fuse socket glowing with a steady light"], [], "Invents a light-emitting socket; no-ending status is conveyed by no ending having been chosen."),
        (12, "ss", 4, [], [], "Explicit missing-manual reason; power and inventory preserved; first person."),
        (13, "ss", 3, ["aligned the beacon with the telescope's dome"], [], "Invents the dome as the alignment target."),
        (14, "sss", 4, [], ["visibility without power"], "Rescue arrival implies completion; phrase may mean daylight needs no power or may assert power is absent."),
        (15, "sss", 4, [], [], "Night of shelter, retained key and no rescue preserved; ending explicit."),
        (16, "ss", 4, [], [], "Rejection and stopped generator preserved; no completed ending described, though causal explanation could be clearer."),
        (49, "ss", 4, [], [], "Observation without discovery; first person."),
        (50, "ss", 4, [], [], "Discovery not collection; first person and some repetition."),
        (51, "ss", 4, [], [], "Key collection and locked door preserved; first person."),
        (52, "s", 4, [], ["cannot open the door"], "Same access ambiguity as first repetition; do not resolve in the model's favour automatically."),
        (53, "ss", 3, ["closed workshop passage"], [], "Invented route closure; several sentence fragments."),
        (54, "sss", 4, ["now-open library door"], [], "Key and location retained but opening is an unrequested effect."),
        (55, "ss", 5, [], [], "Clear procedure, inventory, power and unresolved progress."),
        (56, "us", 3, ["toolbox being re-inspected"], [], "Changed first discovery is described as repeated inspection; whether discovery is actually communicated is unclear."),
        (57, "us", 3, ["collect the spare fuse from your inventory"], [], "Wrong collection source; continued carrying is unclear even though lid remains closed."),
        (58, "su", 2, ["activating the generator", "The generator is stopped; power is off"], [], "Explicit internal conflict: claims the generator started and also remained stopped. No longer carrying the fuse follows installation."),
        (59, "ss", 4, [], ["generator's operational state remains unchanged"], "Current running state is correct, but unchanged could incorrectly deny the start action's effect."),
        (60, "ss", 4, [], ["without electrical power"], "Missing-manual reason and running generator are explicit; daylight phrase could falsely negate the power state."),
        (61, "ss", 5, [], [], "Aligned beacon, enclosed dome, retained key and unchosen ending preserved."),
        (62, "sss", 4, [], [], "Signal receipt, post-storm arrival and completed adventure preserved."),
        (63, "sss", 4, [], ["No changes occurred to the environment"], "Could refer to unchanged furnishings, or wrongly deny the passage of the storm/ending; shelter and departure are otherwise clear."),
        (64, "su", 3, [], ["The ending hasn. been chosen"], "Malformed negation prevents confidently marking the no-ending fact satisfied; first-person prose."),
    ],
    "phi4-mini:3.8b": [
        (17, "ss", 4, [], [], "Hall and locked door preserved without discoveries; 'signal chosen' is awkward but no signal is described."),
        (18, "ss", 4, [], ["passage to the workshop remains unexplored"], "No visited-room facts were supplied; plausible but unsupported exploration-history claim."),
        (19, "sm", 3, ["you unlock the door", "now open"], [], "Key collection triggers unrequested unlocking/opening."),
        (20, "s", 5, [], [], "Explicitly preserves carried key and unchanged outcome."),
        (21, "ss", 3, ["rejected because the door is locked"], [], "Incorrect rejection explanation: missing key is the unmet prerequisite, not locked state itself."),
        (22, "suu", 3, ["door swings silently"], [], "Opens door after unlocking; key retention and remaining in the hall are not clearly stated."),
        (23, "us", 3, ["You sit down at the reading stand"], [], "Adds sitting action; full beacon procedure learning is only vaguely conveyed. Power outage is acknowledged."),
        (24, "us", 3, ["toolbox remains untouched", "generator room is inaccessible due to the lack of power"], [], "Denies completed inspection and invents a power-gated route."),
        (25, "ss", 3, ["collect the spare fuse from your inventory", "adding it to your toolkit", "generator room is still inaccessible due to the lack of power"], [], "Wrong collection source, invented toolkit and access rule."),
        (26, "us", 4, [], ["socket is currently empty"], "Narrative may be describing the before/after sequence, but currently conflicts with post-action input; removal from inventory is not explicit."),
        (27, "ss", 3, ["as you insert the fuse", "wall conduit beside the generator casing glows faintly"], [], "Adds fuse insertion to the start action and invented lighting; no further signal described."),
        (28, "ss", 3, ["beacon carries a beacon attachment"], [], "Misattributes the telescope's attachment to the beacon; meta-language about public facts is awkward."),
        (29, "ss", 5, [], [], "Alignment, retained inventory and unchosen ending are clear."),
        (30, "sss", 2, ["insert the library key into the console", "fuse and generator are not needed"], [], "Invents console unlocking with the key and contradicts rescue power prerequisites."),
        (31, "uss", 4, [], [], "Shelter and ending/no-signal are explicit, but does not establish staying until morning or departure after the storm."),
        (32, "mu", 2, ["bench is already occupied by another person"], [], "Invents an NPC and a false rejection reason; omits power-off state."),
        (65, "ss", 4, ["You decide to inspect the dusty desk"], [], "Adds a player decision after observation; no permission to choose a next action."),
        (66, "ss", 4, [], ["passage to the workshop remains unexplored"], "Discovery and locked door correct; unexplored is absent from the supplied context."),
        (67, "sm", 3, ["you unlock the door", "now open"], [], "Again unlocks and opens during collection."),
        (68, "s", 4, [], ["desk beside the locked library door remains untouched"], "Could mean no additional touching on repeated collection, or deny prior inspection; carried key is correct."),
        (69, "sm", 4, [], ["workshop is not yet entered"], "Omits missing-key fact; exploration history is not supplied."),
        (70, "suu", 3, ["door creaks open"], [], "Opens after unlocking; retention and current location unclear."),
        (71, "ss", 4, ["You sit down at the reading stand"], [], "Required facts are present, but extra sitting action remains unsupported."),
        (72, "us", 3, ["you decide to collect", "toolbox has been previously inspected"], [], "Selects next action without permission and recasts a first inspection as already completed."),
        (73, "us", 3, ["collect the spare fuse from your inventory"], ["generator room's door is still closed"], "Wrong collection source; carrying not explicit. Closed doorway is not in supplied facts."),
        (74, "us", 3, ["installing it again doesn't change anything"], [], "Recasts the changed installation outcome as a repeated no-op; no-longer-carried fact omitted."),
        (75, "ss", 3, ["as you insert the fuse", "wall conduit beside the casing glows faintly"], [], "Adds fuse insertion to generator start and invented light emission."),
        (76, "ss", 5, [], [], "Correct missing-manual rejection, unaligned beacon and retained power."),
        (77, "ss", 3, ["its light piercing through the storm"], [], "Invents beam activity before a signal and extensive unsupported embellishment."),
        (78, "sss", 3, ["insert it into the console", "emitting a bright red signal"], [], "Invents key-operated console and signal colour; rescue facts otherwise present."),
        (79, "smu", 4, [], [], "Wait-until-morning is chosen, but no-signal fact is missing and ended adventure is inconsistent with only deciding to wait."),
        (80, "ss", 2, ["there's no alignment control to adjust"], [], "Denies a supplied object and implies manual knowledge is needed for shelter rather than explaining missing power."),
    ],
}


def main():
    records = []
    sources = {}
    names = {"s": "satisfied", "m": "missing", "u": "unclear"}
    for model, run in RUNS.items():
        folder = ROOT / "generated/narrative-evaluations" / run
        raw = (folder / "results.jsonl").read_bytes()
        rows = {row["attempt_id"]: row for row in map(json.loads, raw.decode("utf-8").splitlines()) if row["model"] == model}
        fixtures = {f["id"]: f for f in json.loads((folder / "dataset.json").read_text(encoding="utf-8"))["narratives"]}
        sources[model] = {"run": run, "results_sha256": hashlib.sha256(raw).hexdigest()}
        assert len(rows) == len(ANNOTATIONS[model]) == 32
        assert set(rows) == {f"A{a[0]:04}" for a in ANNOTATIONS[model]}
        for number, required, readability, violations, uncertain, note in ANNOTATIONS[model]:
            row = rows[f"A{number:04}"]
            fixture = fixtures[row["fixture_id"]]
            scene = json.loads(row["content"])
            prose = scene["description"]
            assert len(required) == len(fixture["required_facts"])
            assert all(quote in prose for quote in violations + uncertain), (model, number)
            assert 1 <= readability <= 5
            status = "fail" if violations or "m" in required else "uncertain" if uncertain or "u" in required else "pass"
            records.append({"model": model, "source_run": run, "attempt_id": row["attempt_id"],
                "fixture_id": row["fixture_id"], "repetition": row["repetition"],
                "reviewer": "Codex assistant", "review_type": "assistant_not_independent_human",
                "description": prose, "structural_pass": row["structural_pass"],
                "required_facts": [{"fact": fact, "judgement": names[code]} for fact, code in zip(fixture["required_facts"], required)],
                "forbidden_checklist_considered": fixture["forbidden_claims"],
                "definite_violation_excerpts": violations, "uncertain_excerpts": uncertain,
                "readability_assistant_rating": readability, "assistant_semantic_status": status,
                "notes": note})
    summary = {}
    for model in RUNS:
        group = [r for r in records if r["model"] == model]
        counts = Counter(r["assistant_semantic_status"] for r in group)
        summary[model] = {"reviewed": len(group), "assistant_status_counts": dict(counts),
            "outputs_with_definite_violations": sum(bool(r["definite_violation_excerpts"]) for r in group),
            "joint_structural_and_assistant_pass": sum(r["structural_pass"] and r["assistant_semantic_status"] == "pass" for r in group),
            "readability_counts": dict(Counter(r["readability_assistant_rating"] for r in group))}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("x", encoding="utf-8") as output:
        json.dump({"version": "narrative-finalists-assistant-review-v1", "reviewed_date": "2026-09-22",
            "scope": "All 32 v2 samples for each finalist; including structurally invalid outputs with readable descriptions",
            "limitations": "Non-blind assistant-authored semantic and readability annotations, informed by development failures. Not independent human evaluation or model-scored judgement. Uncertain cases are not passes. Review considers supplied facts, outcomes and world contract; exact quotations support issues. Annotations may be revised after developer review. The existing run scores and pending human forms are unchanged.",
            "sources": sources, "summary": summary, "records": records}, output, indent=2, ensure_ascii=False)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
