# Shared media development comparison protocol

Version: world-v2-media-protocol-v1, 22 September 2026. Narrative development runs now exist; new image/speech comparison results and independent human ratings remain pending. Inputs are assistant-authored development material, not held-out evaluation or externally annotated ground truth. The image adapter is documented in image_trials.md; the speech adapter remains future work.

## Inputs and boundaries

`media_development.json` contains 16 narrative cases, five illustration briefs and ten exact speech passages. Narrative cases reference legal state/action cases in `development.json`; offline validation reconstructs their post-action public facts, inventory, outcome and allowed suggestions. All five rooms, both endings, rejected actions and repeated collection are covered. Setup traces and complete oracle states remain in the source development dataset. The narrative model receives only the case's `input` object, not source IDs, required-fact checklists or forbidden-claim labels.

The projection supplies verified post-action facts, not permission to change state. Suggested actions include observation and state-changing actions currently allowed by the reference rules; completed no-op actions are omitted. Ending cases have no suggestions; restart is a UI control outside this action schema. This is reference-fixture preparation, not full-world production-engine implementation.

Image candidates receive the same saved `prompt` for each room, including required scenery, omissions and shared style. Canvas: **512x512 square** (correcting the draft's contradictory description as landscape). Stable establishing views omit portable quest items, readable instructions, open doors and state-sensitive indicators. The complete required/forbidden lists remain available to reviewers. Prompt requirements are constraints, not evidence that a model obeys them.

Speech candidates receive each saved `text` exactly, including punctuation. Fix one English-US voice per candidate before running; report model and voice separately. Do not alter words or pronunciation markup for one candidate within the baseline. Focus terms guide listening, but the whole passage must be checked. The draft was adapted to preserve toolbox closure and cover both rescue and shelter. These short passages test correctness; they do not establish latency for longer gameplay scenes.

The old standalone feasibility scripts remain historical experiments with different scene facts. They do not consume this dataset. `observatory.evaluate_narrative` consumes narrative cases; `observatory.evaluate_image` consumes the five image briefs. Speech adaptation remains future work. Do not label old-script outputs as results for these fixtures.

## Narrative contract and scoring

The runner's initial common prompt, `world-v2-narrative-eval-v1`, instructs candidates to narrate only supplied facts and outcomes, preserve inventory and world state, return every supplied suggestion exactly once, copy the supplied visual brief ID, and emit only JSON matching `NarrativeOutput.model_json_schema()`. It is versioned and saved verbatim per run, but its quality has not yet been measured:

```json
{
  "description": "Scene prose",
  "suggestions": [{"action": "look_around", "target": "current_room"}],
  "visual_brief_id": "entrance_hall"
}
```

Use 60-100 description words for changed/observed scenes and endings; brief rejected/unchanged outcomes may use 1-100 words. Word counting uses the regex in `check_narrative`; contractions and hyphenated words count as single words. Empty ending suggestions are valid. Never pad an ending with new actions to satisfy a choice-count rule.

Record these measures separately for every attempt:

| Measure | Rule |
| --- | --- |
| Completion | HTTP/runtime completed without timeout, truncation or other generation error; the narrative runner records this independently of content checks |
| Schema | Strict JSON contract, no unknown fields; valid action/target pairs |
| Suggestions | Exact set supplied in input, no extras, omissions or duplicates |
| Illustration reference | Exact supplied visual brief ID |
| Length | Applicable range above; record actual count |
| Required facts | Mark each checklist item satisfied, missing or unclear; paraphrases count if meaning is preserved |
| Critical contradictions | Count each distinct false claim about inventory, discoveries, location/access, puzzle progress, endings or executed actions; cite the offending phrase and violated fact |
| Unsupported additions | Record invented objects, characters or events; atmosphere may vary only within supplied scene facts |
| Readability | 1: mostly incomprehensible; 2: frequent confusing/fragmented prose; 3: understandable with awkward/repetitive passages; 4: clear with minor flaws; 5: clear, natural and concise |

Structural pass requires completion plus all four automated content checks. Semantic pass requires every required fact satisfied, zero critical contradictions and zero unsupported additions. Report both, and their joint count, over **all attempted samples**, retaining generation and schema failures as failures. Readability is a separate rating, not a way to compensate for a contradiction. Missing/unclear human reviews remain pending; never count them as passes. `check_narrative` deliberately leaves semantic review pending even for structurally valid nonsense. Software checks do not judge prose truth.

## Illustration scoring

For every required and forbidden detail, record present, absent or unclear with a short observation. Required-detail coverage = clearly present required details / total required details. A content pass requires all required details clearly present and all forbidden details clearly absent. An unclear forbidden item prevents a content pass but is not counted as a confirmed violation. Any confirmed forbidden item is a content failure regardless of style.

| Rating | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Scene clarity | Unrecognisable | Major objects hard to identify | Main scene identifiable with ambiguity | Clear with minor clutter | Required scene immediately clear |
| Style adherence | Contrary to brief | Mostly inconsistent | Partly matches | Mostly matches | Consistently matches palette, lighting and painting style |
| Cross-room coherence | Unrelated set | Strong differences | Mixed consistency | Minor variation | Consistent visual identity across all five rooms |

Rate coherence once per candidate's five-room set, not once per image. Preserve outputs with failures. Report valid image files / attempts, content-pass count / attempts, per-detail findings and rating distributions separately. Decoder success alone does not establish visual correctness. Recheck actual illustrations before caching them across state changes; this fixture design does not prove cache validity.

## Speech scoring

Listen against the exact passage. Record omitted, substituted and inserted words with timestamps or quoted spans. Count events separately from affected words; for an optional manual word-error rate use `(substitutions + deletions + insertions) / reference word count`, with case and punctuation ignored, whitespace tokenisation, and no counting a substitution twice. This measure can exceed 1. Do not infer intelligibility from WAV validity or waveform amplitude.

Record pronunciation issues for focus terms and any other word; accept ordinary English-US accent variation that preserves the intended word. A content pass requires zero word errors and no pronunciation error that changes meaning or makes a word unintelligible. Audible pronunciation differences that preserve meaning remain notes. Keep voice preference separate from correctness.

| Rating | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- |
| Intelligibility | Mostly unintelligible | Frequent unintelligible spans | Understandable with effort/replay | Clear with occasional effort | Fully clear on first listening |
| Pacing | Severely disruptive | Frequently awkward | Acceptable with noticeable pauses/rushing | Comfortable with minor issues | Consistently natural and comfortable |

Save audio format, duration, sample rate, channel count and clipping/truncation observations. Record load and synthesis time separately; real-time factor = synthesis seconds / audio duration seconds, excluding loading. Failed/empty audio counts as failure in valid-audio and content-pass denominators; listening ratings for missing audio are N/A, never an invented score. Report how many samples were actually rated.

## Common execution and evidence rules for later trials

1. Obtain approval for model experiments and confirm candidates are already installed. No fixture command downloads or invokes models.
2. Freeze dataset/protocol versions and SHA-256 hashes, prompt text/schema, model checkpoints/digests, runtime versions, voice identity, devices and generation settings. Do not change prompts per case after seeing outputs. Preserve model-specific required settings as explicit differences; equal seeds do not guarantee equivalent randomness across models.
3. Proposed development sample plan: two runs per case/candidate, with candidate order reversed on the second run. Use seeds 42 then 43 where supported and record unsupported seeding. Report this small sample's limitations; the plan is not an executed experiment or an approved inference budget.
4. Retain every request, output, error and attempt identifier. No silent retries, best-of selection or fallback substitution in raw-model scores. Score later gameplay fallbacks separately. Save results outside fixture files.
5. Record total wall time and available load/inference timings separately. Label unavailable timing/resource measurements as unavailable, not zero. Record RAM/VRAM sampling method and peak values if measured; point snapshots are not peaks. Report cold/first calls separately from warm calls and list generation failures alongside latency summaries.
6. Use identical playback volume and listening setup for speech and equal image display size. Where practical hide candidate names and shuffle review order, retaining the mapping. Reviewer identity, date, notes and pending fields must be recorded. A second reviewer should resolve uncertain findings; do not invent agreement if only the developer reviewed outputs.
7. Suggested review record fields: run/candidate/fixture/repetition IDs, output path, completion/error, automated checks, each checklist judgement, violation quotations/timestamps, applicable ratings, reviewer/date and notes. Empty fields mean unreviewed. Avoid a single weighted score that hides correctness failures.
8. Compare factual/content correctness first, then human ratings, latency and hardware feasibility. Do not declare final selection from one attractive output. Set final application thresholds before held-out evaluation; these development rubrics are not university-prescribed targets.

The reserved intent files are not inputs to media fixture generation or tuning. Separate unseen media material and human annotation review remain outstanding. This work provides comparison preparation, not new model accuracy, media quality, player feedback or integrated-game evidence.
