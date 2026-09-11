# The Last Observatory task list

Working title: an illustrated and narrated AI text adventure. Follow `project.md` and the orchestration brief in `spec.md`. Checkboxes record completed work rather than intended capabilities.

## 1. Scope and feasibility

- [x] Select an illustrated text adventure as the new direction.
- [x] Document three pretrained roles: language, image generation, and speech synthesis.
- [x] Define an initial five-location scope, small inventory, and two endings.
- [ ] Review hardware, model access, budget, and remaining submission time.
- [ ] Research at least two candidate models per role; record exact identities, documentation, licensing, and runtime requirements.
- [ ] Run one feasibility example per role and record latency, resources, and quality.
- [ ] Connect one scene through all three real models and save the resulting text, image, and audio.
- [ ] Choose an initial stack based on evidence; document failed trials and practical exclusions.
- [ ] Record provisional quality and latency targets before final evaluation.

Milestone: one state produces a valid illustrated and narrated scene on available resources.

## 2. World design and evaluation fixtures

- [ ] Finalise the observatory premise, objective, tone, and shared visual style.
- [ ] Draft and review the room map, items, puzzle prerequisites, and action effects.
- [ ] Define both endings and a valid action sequence reaching each.
- [ ] Specify world, player-state, and generated-scene schemas, including stable action IDs and state revisions.
- [ ] Write factual fallback descriptions and canonical action labels.
- [ ] Create approximately 15-20 state/action fixtures with expected facts, permitted actions, and forbidden claims.
- [ ] Create five illustration briefs and approximately ten narration passages.
- [ ] Separate development fixtures from held-out evaluation cases.
- [ ] Define evaluation rubrics and record provenance for external material.

## 3. Deterministic game engine

- [ ] Create project structure, environment configuration, and example settings without secrets.
- [ ] Implement initial state, movement, inventory, puzzle flags, and allowed-action calculation.
- [ ] Implement action validation and both endings; keep state changes outside model control.
- [ ] Implement restart and duplicate/stale-action protection.
- [ ] Unit-test transitions, item prerequisites, invalid actions, and ending conditions.
- [ ] Run scripted paths to both endings and check for unintended dead ends.

Milestone: the complete adventure works with factual placeholder text before model presentation is added.

## 4. Model integration

- [ ] Implement interchangeable adapters for the selected language, image, and speech models.
- [ ] Build narrative prompts from current state, recent events, allowed actions, and world facts.
- [ ] Validate generated schemas and action IDs; add feasible factual checks and document their limitations.
- [ ] Add bounded retries and logged fallback text without reapplying actions.
- [ ] Generate illustrations from accepted briefs and consistent style instructions.
- [ ] Cache images by visual facts and configuration; avoid changing inventory and puzzle spoilers in images.
- [ ] Synthesize the exact accepted text; cache audio by text, voice, and configuration.
- [ ] Associate media with state revisions and discard stale responses.
- [ ] Log prompts, versions, parameters, output paths, validation results, latency, and cache hits.
- [ ] Test timeout and failure recovery for each model while preserving playable state.

## 5. Player interface

- [ ] Display location, illustration, narrative, inventory, objective, and valid choice buttons.
- [ ] Add optional narration playback, stop, and replay controls.
- [ ] Show text before media finishes; provide loading, retry, and fallback states.
- [ ] Prevent repeated action submissions while processing.
- [ ] Add restart and ending screens.
- [ ] Check keyboard operation, readable text, and basic browser layout.
- [ ] Complete a browser playthrough with all three models, including fresh media generation.

Milestone: a nontechnical player can finish the adventure through the interface.

## 6. Model comparisons and evaluation

- [ ] Run feasible candidate comparisons on identical development fixtures; retain outputs and failures.
- [ ] Document selected and rejected models using quality, latency, resources, and integration evidence.
- [ ] Freeze prompts and configurations before held-out evaluation.
- [ ] Measure narrative schema success, contradictions, invalid choices, and fallback frequency.
- [ ] Rate image detail accuracy, forbidden content, and consistency using the rubric.
- [ ] Check speech omissions, substitutions, pronunciation, intelligibility, and synthesis speed.
- [ ] Compare state-grounded narrative prompts with a simpler prompt baseline.
- [ ] Report fresh-generation and cached timings separately.
- [ ] Run integration checks for endings, revisits, repeated clicks, restart, and model failures.
- [ ] Conduct a small player study, aiming for 3-5 participants if available, with minimal consented feedback.
- [ ] Record completion, confusion, coherence, perceived agency, enjoyment, and waiting-time feedback.
- [ ] Implement at least one improvement supported by findings and retest it.
- [ ] Summarise sample sizes, uncertainty, remaining failures, and limitations.

## 7. Submission

- [ ] Write reproducible setup/run instructions with exact model versions, hardware needs, and configuration steps.
- [ ] Document architecture and how shared state connects the three model outputs.
- [ ] Explain why generation is useful and why mechanics remain deterministic.
- [ ] Present model trials, software tests, evaluation tables, failure examples, and user-driven changes.
- [ ] Document model/asset licensing, generated-content provenance, costs where applicable, and limitations.
- [ ] Prepare a demonstration showing a choice changing state, generated text/image/audio, and an ending.
- [ ] Verify the documented setup and complete relevant final checks.
- [ ] Check deliverables against `spec.md`, using `example.md` as a reference for engineering and evaluation depth.

## Stretch work after the core and evaluation are complete

- [ ] Persistent save/load.
- [ ] Additional illustrations for changed room states.
- [ ] Extra adventures or configurable narrative tone.

Prioritise a working three-model pipeline, complete gameplay, and evaluation evidence over stretch features.
