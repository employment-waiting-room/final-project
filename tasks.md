# The Last Observatory task list

## Goal and working agreement

Build a free, local browser adventure that understands natural-language player actions and generates context-sensitive narrative, illustrations, and speech while preserving consistent world rules.

Follow Project Idea 1 in spec.md, the engineering expectations in example.md, and the submission requirements in report_spec.md. The AI challenge is interpreting varied requests and generating coherent media; the engine owns feasibility and state transitions. Three working standalone models are preparation, not the final integrated system.

Keep five rooms, a small inventory, and two endings. Free-text input and optional suggested actions are core. The broader object-based free-roam redesign is paused. NPCs, extra voices, unrestricted mechanics, and extra adventures are not approved core requirements.

Checkboxes mean completed work supported by evidence. Existing prototypes do not complete application-wide tasks. Follow the phases below; record findings in development_log.md and obtain confirmation before new implementation or installation work. Report preparation runs alongside development.

## 0. Completed groundwork and known limitations

- [x] Review hardware, free/local constraints, assessment documents, and submission dates.
- [x] Set up the Python 3.11 environment and initial FastAPI/testing dependencies.
- [x] Generate a local SDXL Turbo illustration through the Vulkan runtime and save timing/output evidence.
- [x] Run Qwen3:4b narrative trials with saved prompts, structural checks, timings, and failure observations.
- [x] Generate Piper Lessac speech and record timing; obtain informal confirmation that the sample reads correctly.
- [x] Implement and manually play the desk -> collect key -> unlock library terminal sequence.
- [x] Add an initial Qwen intent interpreter, engine prerequisite checks, numbered fallback, and request logging.
- [x] Run 27 software tests and an eight-case development intent trial after local guard adjustments.
- [x] Record the free-text direction and keep a development log.

Known limitations: the eight-case result was for a tuned model-and-rule pipeline, not general model accuracy. User testing subsequently mapped 'look around the room' to inspecting the desk and 'knock on the door' to unlocking it. These errors remain unresolved. Generated narrative still has factual errors. Text, images, and speech are not yet integrated into one playable scene.

## 1. Finish candidate research and feasibility planning — next

- [ ] Complete a two-candidate research table for each role: exact checkpoint/version, runtime, documentation, licensing, hardware needs, and selection rationale.
- [x] Complete the missing second image-model candidate; a second runtime for the same weights is not a second model. SD-Turbo shortlisted in model_candidates.md; not yet downloaded or tested.
- [x] Consolidate existing Qwen/Gemma and Piper/Kokoro research, distinguishing researched candidates from tested candidates. See model_candidates.md.
- [ ] Fill gaps in baseline feasibility evidence, especially RAM/VRAM measurement and explicit quality observations; rerun only where necessary.
- [ ] Define a small shared comparison protocol, provisional quality/latency targets, and a feasible alternative-model trial plan before further model-specific tuning.
- [ ] Record hardware/access exclusions honestly; keep research findings separate from measured comparisons.

Gate: candidate identities, practical constraints, and the next experiments are concrete. The current stack is provisional until comparative evidence supports selection.

## 2. Define the world, action contract, and evaluation fixtures

Working world/action contract accepted on 21 September 2026, including shelter with restored power but without manual reading or beacon alignment. evaluation/development.json contains 53 validated development cases: 24 state/action cases, 20 intent cases and nine matched controls. Development intent runs have been reviewed. A separate 30-case intent set was reserved on 22 September without model execution. development_fixtures.md retains the source cases and draft illustration/narration material. Held-out evaluation, media comparisons and detailed visual review remain outstanding.

- [ ] Finalise the premise, objective, room map, tone, and shared visual style.
- [x] Specify items, discoverability, puzzle prerequisites, action effects, both endings, and a valid route to each.
- [x] Define the bounded supported action vocabulary and targets; decide explicitly how looking, knocking, and other unsupported requests behave without assuming the paused free-roam redesign.
- [x] Specify interpretation outcomes: proposed action, clarification, unsupported request, and inference failure. Keep engine feasibility separate from interpretation accuracy.
- [ ] Specify world/state/scene schemas, stable action IDs, state revisions, and duplicate-request handling.
- [ ] Write canonical labels, factual fallback descriptions, and rejection reasons that do not reveal hidden solutions.
- [x] Build approximately 15-20 state/action fixtures with expected facts, legal transitions, and forbidden claims. Expanded to 24 cases covering ending boundaries.
- [x] Label state complexity and language difficulty independently, with nine matched development controls.
- [ ] Compare model results by state complexity and language difficulty without adding extra adventures.
- [x] Build labelled intent cases covering paraphrases, missing prerequisites, wrong verbs, ambiguity, compound requests, unsupported actions, and attempts to override rules.
- [x] Add the user's 'look around' and 'knock' failures to development/regression cases, not held-out cases.
- [x] Prepare five illustration briefs and ten exact narration passages with written quality rubrics. Saved in evaluation/media_development.json and evaluation/media_protocol.md; no generation or human ratings yet.
- [x] Prepare 16 state-grounded narrative development cases with required/forbidden facts, validated post-action inputs, output schema and structural checks. Full software suite: 128 passed (22 September 2026).
- [ ] Implement comparison runners/adapters for the shared media fixtures, review trial settings and obtain approval before inference. Existing feasibility scripts still use historical inputs.
- [x] Reserve new intent phrasings and state combinations before further tuning; record provenance and annotation rules. Added 30 assistant-authored cases, a reservation hash and offline separation checks. These are unrun model inputs in known task families, not blind-author or independently annotated data.
- [ ] Independently review reserved intent labels against the frozen contract before final evaluation; do not use reserved cases to tune prompts or rules. Reserve media evaluation material separately.

Gate: the intended behaviour is defined well enough to test. Do not let a model silently decide what the game supports.

## 3. Compare candidates and demonstrate one integrated scene

- [x] Implement a configurable model-only development intent runner with raw responses, error handling, exact intent scoring, reference outcome scoring and summaries by complexity/difficulty. Kept separate from gameplay confirmation.
- [x] Run and review the Qwen3:4b development baseline before comparing an alternative language model. Recorded V1-JSON development results: Qwen 49/53, Gemma 42/53; narrative comparison and held-out evaluation remain outstanding.
- [ ] Make model identity/configuration replaceable in the trial scripts and adapters; retain raw outputs, versions, prompts, failures, and resource/timing measurements.
- [ ] Compare at least two feasible language candidates on the same development intent and narrative cases.
- [ ] Compare at least two feasible image candidates on matching scene briefs and criteria.
- [ ] Compare Piper and a feasible alternative speech model on the same passages and listening criteria.
- [ ] Explain necessary model-specific settings and exclusions; do not claim unrun comparisons or treat different voices alone as different model architectures.
- [ ] Select the initial application models using quality, correctness, latency, resource use, and integration evidence.
- [ ] Connect one typed request through interpretation, engine validation, accepted narrative, matching illustration, and narration of that exact accepted text.
- [ ] Save evidence of the shared state, verified outcome, and three real model outputs, including fresh generation.
- [ ] Demonstrate that rejected requests leave state unchanged and model failures retain a usable fallback.

Gate: one real integrated interaction works locally. Finish this before expanding the prototype across all rooms. Candidate trials here support selection; final held-out evaluation comes later.

## 4. Complete the game engine and reliable orchestration

- [x] Add an entrance-hall typed-action confirmation safeguard: display the interpreted action/target, require explicit y/yes, and preserve state on cancellation, missing confirmation or interruption. Verified with simulated model responses; this does not fix model interpretation errors or complete browser/full-world integration.
- [x] Test gameplay confirmation separately from model-only evaluation; keep ambiguous/compound prediction errors in model accuracy scores. Full software suite: 100 passed (21 September 2026).
- [ ] Carry confirmation into browser/full-world orchestration and measure user correction/cancellation separately from raw-model accuracy.
- [ ] Implement movement, inventory, puzzle flags, allowed actions, and both endings across the agreed world.
- [ ] Resolve unintended action substitutions, including the reported looking/knocking failures, against the agreed action contract.
- [ ] Implement clarification and unsupported-request handling; measure over-clarification rather than assuming heuristic guards solve ambiguity.
- [ ] Validate structured action/target references and engine prerequisites before any state change.
- [ ] Build narrative prompts from verified state, recent events, and outcomes; add feasible factual checks and document what they cannot guarantee.
- [ ] Add bounded retries and factual narrative fallback without applying an action twice.
- [ ] Implement interchangeable text/image/speech adapters with timeouts and explicit failure handling.
- [ ] Generate illustrations from accepted location briefs; avoid hidden solutions and changing inventory details.
- [ ] Cache images by visual facts/configuration and speech by exact accepted text/voice/configuration.
- [ ] Associate outputs with state revisions; prevent duplicate transitions and discard stale responses after restart or later actions.
- [ ] Log interpretation source (model or local rule), validation, transition, prompts, model versions, latency, failures, and cache use.
- [ ] Add full engine and orchestration tests: prerequisites, wrong actions, both endings, restart, repeated requests, stale responses, and model failures.
- [ ] Run scripted routes to both endings and check for unintended dead ends.

Gate: complete gameplay and failure recovery work before final user evaluation. A mechanically legal transition must not be counted as correct if it misrepresents the player's request.

## 5. Build the browser experience

- [ ] Display location, generated illustration, accepted narrative, inventory, and objective.
- [ ] Add free-text input with optional engine-approved suggestions and understandable clarification/rejection messages.
- [ ] Add narration playback, stop, and replay controls.
- [ ] Display text before media finishes; show loading, retry, and fallback states.
- [ ] Prevent repeated submissions while processing; add restart and ending screens.
- [ ] Check keyboard access, readable text, and browser layout.
- [ ] Complete a browser playthrough using all three models, including fresh generation and failures.

Gate: a player can reach an ending without developer intervention.

## 6. Final evaluation and evidence-based improvement

- [ ] Freeze selected models, prompts, configurations, and acceptance criteria before held-out evaluation.
- [ ] Measure action/target accuracy, false acceptance/rejection, ambiguity handling, and rule-bypass outcomes by request category.
- [ ] Report raw-model interpretation separately from local guards, engine enforcement, and end-to-end outcomes.
- [ ] Measure narrative schema compliance, contradictions, invalid choices, and fallback frequency.
- [ ] Compare state-grounded narration with a simpler prompt baseline on equivalent cases.
- [ ] Rate image detail accuracy, forbidden content, and visual consistency using the defined rubric.
- [ ] Check speech omissions, substitutions, pronunciation, intelligibility, and synthesis speed.
- [ ] Report end-to-end latency, component latency, RAM/VRAM, and fresh versus cached generation; distinguish loading from inference and repeat trials where needed.
- [ ] Compare typed and suggested-action interaction on equivalent tasks, including misunderstandings, completion, agency, and waiting time.
- [ ] Conduct a small consented player study, aiming for 3-5 participants if available; record confusion, coherence, enjoyment, and completion.
- [ ] Implement an improvement supported by findings and retest; label any reused evaluation cases as development data after tuning.
- [ ] Summarise sample sizes, uncertainty, remaining failures, and limitations without generalising from the eight tuned prototype cases.

## 7. Report, exam preparation, and submission — ongoing

- [ ] Maintain a requirements-to-evidence table showing the challenging goal, why pretrained models are needed, integration, comparisons, and software testing.
- [ ] Review relevant literature on grounded generation, language-based interaction, multimodal orchestration, and evaluation; connect it to design choices rather than only summarising sources.
- [ ] Prepare the exam decision/failure/reflection notes for Tuesday 15 September, using actual evidence and distinguishing implemented work from plans.
- [ ] Write Introduction, Literature Review, Design, Implementation, Evaluation, and Conclusion against report_spec.md; name Project Idea 1 and observe chapter limits and the total 10,500-word limit.
- [ ] Include architecture diagrams, a visual work plan, model-comparison tables, screenshots, failure examples, and justified changes.
- [ ] Write reproducible setup/run instructions with exact model versions, hardware needs, and settings; verify them.
- [ ] Document licensing, asset provenance, costs, limitations, and future work.
- [ ] Preserve selected experimental evidence for assessors. Generated folders and Markdown are currently ignored; verify deliverables are actually included before submission.
- [ ] Verify the required public repository is accessible through the results period and contains appropriate source/setup/evidence without model binaries or secrets.
- [ ] Prepare a 3-5 minute demonstration of the integrated application, a state-changing action, fresh generation, and an ending; follow the student's-own-voice and no-speed-up requirements.
- [ ] Check application, report, demonstration, and repository against spec.md and report_spec.md before the 28 September submission.

## Deferred work — requires a new scope decision

- [ ] Broader object-based free-roam redesign (explicitly paused).
- [ ] NPCs and additional character voices.
- [ ] Persistent save/load, additional adventures, and extra visual content.

Prioritise a complete AI-dependent interaction, defensible comparisons, and evaluation over extra game content. Continue candidate evidence and the planned integrated scene; the entrance-hall confirmation safeguard does not complete full-world or browser integration.
