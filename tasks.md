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

- [ ] Complete a five-candidate research table for each data space: exact checkpoint/version, runtime, documentation, licensing, hardware needs, and selection rationale.
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
- [x] Implement a configurable model-only narrative runner for the 16 shared cases, with common prompts/settings, reversed candidate order across repetitions, saved raw outputs, structural scoring and pending human-review records. Validated using simulated responses; 150 software tests passed (22 September 2026).
- [x] Review the user-run 64-request Qwen/Gemma narrative baseline. Structural passes: Qwen 7/32, Gemma 4/32; both produced factual errors. See development_log.md entry 41. These are development results, not semantic accuracy or final model selection.
- [ ] Complete per-attempt human factuality/readability annotation separately from structure checks; consider a versioned narrative improvement with the baseline preserved. Supply commands for all user-run model experiments.
- [x] Add an opt-in narrative v2 prompt emphasising verified outcomes, unchanged facts and length; preserve v1 as default and keep fixtures/settings/scoring unchanged. Software tests: 153 passed (22 September 2026).
- [x] Review the user-run narrative v2 comparison: Qwen structural passes rose 7/32 -> 14/32; Gemma fell 4/32 -> 1/32. Factual failures persisted, including structurally passing outputs. Kept v1 default unchanged; see log entry 43.
- [x] Implement the subsequently authorised entrance-hall narrative safeguard with engine-owned suggestions/brief ID, bounded checks and factual fallback. Opt-in --narrate mode; 182 software tests passed. Live evaluation and full-world integration remain outstanding; see gameplay_narration.md.
- [ ] Implement image/speech comparison adapters for the shared media fixtures, review settings and obtain approval before inference. Existing feasibility scripts still use historical inputs.
- [x] Implement the image adapter with offline preview, shared briefs/seeds, artifact hashes, retained failures and pending visual reviews. See evaluation/image_trials.md; 200 offline tests passed. User-run smoke test, alternative compatibility and speech adapter remain outstanding.
- [x] Review the user-run SDXL Turbo image smoke test: runtime/file checks passed in 11.88 seconds; assistant inspection found the required desk missing. Full baseline and human visual ratings remain pending (log entry 51).
- [x] Review all ten full-baseline SDXL Turbo images: 10/10 runtime/PNG passes, mean 13.39 seconds including loading; assistant inspection found missing required scenery. See evaluation/assistant_reviews/image_sdxl_baseline.md and log entry 52. Human ratings and alternative-model trials remain pending.
- [x] Prepare separate SD-Turbo configuration with pinned checkpoint revision/hash, licence provenance and user-managed download/smoke commands. Local compatibility and comparative results remain unmeasured; see evaluation/image_trials.md.
- [x] Review SD-Turbo smoke test: pinned checkpoint hash matched, runtime/PNG checks passed in 4.15 seconds. Required glazing was missing/unclear and door plaque had text-like marks; full baseline and human visual ratings remain pending (log entry 54).
- [x] Review ten-image SD-Turbo baseline: 10/10 runtime/PNG passes, mean 3.00 seconds including loading. Shared prompts/seeds and dataset/protocol hashes matched SDXL. Assistant inspection found missing details and open-door/open-sky violations; see log entry 55 and evaluation/assistant_reviews/image_sd_turbo_baseline.md. Two of five image baselines completed; human ratings remain pending.
- [x] Prepare SD 1.5 candidate configuration with pinned checkpoint/hash and explicit 30-step CFG 7.5 trial settings; user-managed download and compatibility smoke test remain pending (log entry 56).
- [x] Review SD 1.5 smoke test: checkpoint hash matched, runtime/PNG checks passed in 9.94 seconds; desk absent and frosted glazing unclear in assistant inspection. Full baseline/human ratings remain pending (log entry 57).
- [x] Review full SD 1.5 baseline: 10/10 runtime/PNG passes, mean 13.89 seconds including loading. Assistant inspection found missing objects, collages, lettering, people and outdoor telescope scenery. Shared prompts/seeds and dataset/protocol hashes matched. Three of five image baselines complete; human ratings remain pending (log entry 58).
- [x] Reserve new intent phrasings and state combinations before further tuning; record provenance and annotation rules. Added 30 assistant-authored cases, a reservation hash and offline separation checks. These are unrun model inputs in known task families, not blind-author or independently annotated data.
- [ ] Independently review reserved intent labels against the frozen contract before final evaluation; do not use reserved cases to tune prompts or rules. Reserve media evaluation material separately.

Gate: the intended behaviour is defined well enough to test. Do not let a model silently decide what the game supports.

## 3. Compare candidates and demonstrate one integrated scene

- [x] Implement a configurable model-only development intent runner with raw responses, error handling, exact intent scoring, reference outcome scoring and summaries by complexity/difficulty. Kept separate from gameplay confirmation.
- [x] Run and review the Qwen3:4b development baseline before comparing an alternative language model. Recorded V1-JSON development results: Qwen 49/53, Gemma 42/53. An initial narrative comparison was also reviewed; systematic human narrative scoring and held-out evaluation remain outstanding.
- [ ] Make model identity/configuration replaceable in the trial scripts and adapters; retain raw outputs, versions, prompts, failures, and resource/timing measurements.
- [ ] Compare at least two feasible language candidates on the same development intent and narrative cases.
- [x] Review full narrative v2 development trials for five language candidates: Qwen, Gemma, Llama, Phi and Granite. All showed factual failures; structural counts are not semantic accuracy. See log entry 45.
- [x] Review shared v1-json intent trials for all five language candidates: Qwen 49/53, Phi 48/53, Gemma 42/53, Llama 36/53, Granite 27/53. Verified saved requests matched except model identity; see log entry 46.
- [ ] Complete systematic human narrative review and resource/feasibility assessment before final language-model selection; Qwen and Phi are provisional finalists, not proven winners. All model execution is user-run.
- [x] Complete a separately labelled assistant review of all 64 Qwen/Phi v2 narratives with per-case evidence and uncertain judgements. Qwen: 14 pass/10 fail/8 uncertain; Phi: 4 pass/23 fail/5 uncertain. See evaluation/assistant_reviews/narrative_v2_finalists.md; this does not complete independent human evaluation.
- [ ] Obtain developer judgement on the flagged narrative ambiguities and record style preference separately. Qwen remains the provisional recommendation; final selection and bounded gameplay safeguards are not complete.
- [ ] Compare at least five feasible image checkpoints on matching scene briefs and criteria; record exclusions/replacements explicitly.
- [x] Prepare DreamShaper 8 as fifth checkpoint with pinned creator artifact/hash and SD 1.5-matched settings. User-run smoke/full baseline and final licence review remain pending (log entry 62).
- [x] Review DreamShaper 8 smoke test: checkpoint matched, Vulkan/PNG checks passed in 8.85 seconds; person and open doors violated the scene brief. Full baseline/human ratings remain pending (log entry 63).
- [x] Review DreamShaper's ten-image baseline and consolidate all five candidates: 50/50 baseline runtime/PNG successes, but scene-content failures in every candidate. See log entry 64 and evaluation/assistant_reviews/image_dreamshaper8_baseline.md. Generation runs are complete; human checklist ratings, resource assessment and final selection remain pending.
- [x] Build self-contained offline review gallery for all 50 images with source-hash checks, per-detail judgements, separate style/coherence ratings, browser saving and JSON export/import. 204 offline software tests passed; developer ratings and browser interaction verification remain pending.
- [x] Prepare fourth candidate SDXL Base with pinned checkpoint/hash, embedded-VAE smoke configuration and user-run instructions. Actual compatibility/full baseline remain pending (log entry 59).
- [x] Review SDXL Base smoke test: checkpoint matched, Vulkan/embedded-VAE decoding and PNG checks passed in 19.52 seconds. Desk missing and prominent lettering observed; full baseline/human ratings remain pending (log entry 60).
- [x] Review full SDXL Base baseline: 10/10 runtime/PNG passes, mean 19.01 seconds including loading; matching shared inputs. Assistant inspection found missing objects, open door, lettering and object-sheet compositions. Four of five image baselines complete; human ratings remain pending (log entry 61).
- [x] Run five speech candidates on matching passages: 100/100 valid files; record developer listening subset (15 clips across T03/T05/T10), with Kokoro > XTTS > Piper > SpeechT5 > MMS. This is development evidence, not complete listening or held-out evaluation; see evaluation/assistant_reviews/speech_developer_review.md.
- [x] Add optional entrance-hall Kokoro speech for accepted scene text, silent cancellation/rejection and text-only failure recovery. Offline tests cover orchestration; live playback remains user-run.
- [x] Record developer-reported live speech success after the --narrate --speak instructions: "it worked great" (24 September 2026). This confirms reported playback satisfaction, not individually verified cancellation, exact-text matching or failure recovery.
- [ ] Retain live speech logs and explicitly document cancellation, three-action completion and displayed/spoken text matching for final demonstration evidence. Image integration/review remains outstanding.
- [x] Prepare pinned speech asset bundle/downloader for Kokoro, SpeechT5 plus vocoder/embeddings, MMS English and XTTS-v2; Piper already present. 209 offline tests passed. User downloads, runtime setup and actual speech trials remain pending. Image human review/selection deferred at user's request.
- [x] Review completed speech download receipt: all 32 planned assets present with expected sizes/revisions and matching manifest identity; 3.21 GB bundle downloaded. Runtime setup and synthesis tests remain pending (log entry 67).
- [x] Prepare isolated CPU speech setup for HF, Kokoro and XTTS with explicit package pins, pip checks, offline import reports and user-run installation command. 212 offline tests passed; actual installation, G2P and model-load/synthesis checks remain pending (log entry 68).
- [x] Review user-installed speech environments: all three setup profiles completed, all 21 import checks passed, CPU package versions and freezes recorded. Model loading, G2P and synthesis remain untested (log entry 69).
- [x] Implement shared speech development runner and five local adapters, with exact passages, fixed initial voices/settings, saved audio/asset hashes, separate timing/audio checks, retained failures and pending listening forms. 220 offline tests passed; real five-candidate smoke synthesis remains user-run (log entry 70).
- [x] Review five user-run speech smoke outputs and developer feedback: all file checks passed; Piper/Kokoro/XTTS sounded good, SpeechT5 static/monotone/unclear, MMS mispronunciations. Basic rate/embedding diagnostics found no obvious mismatch; cause unresolved. Full comparison and detailed listening ratings remain pending (log entry 71).
- [ ] Explain necessary model-specific settings and exclusions; do not claim unrun comparisons or treat different voices alone as different model architectures.
- [ ] Select the initial application models using quality, correctness, latency, resource use, and integration evidence.
- [x] Record developer review of first ten hall images; provisionally select SDXL Turbo, exclude SD 1.5/SDXL Base from gameplay, and retain other candidates' limitations. See evaluation/assistant_reviews/image_developer_selection.md.
- [x] Implement optional --illustrate using the approved hall brief, local SDXL Turbo, session reuse, timeout and text fallback. Combined narration/image/speech orchestration is offline-tested; browser integration remains pending.
- [x] Record developer report that the combined interaction works; repeated full-scene narration after small actions was identified as a flow issue. Detailed visual/state/log verification remains separate.
- [x] Replace CLI full-scene recaps with short narration of the verified action outcome, including brief factual fallbacks and matching speech. 254 offline tests passed; model-only evaluation unchanged.
- [x] Restore full opening narration once at startup, with optional speech, before short action outcomes. Cancellation/redraw does not replay the opening; 254 offline tests passed.
- [ ] User-test opening plus revised action-focused narration with --narrate --illustrate --speak; retain logs and verify concise outcomes, visual correctness and cancellation.
- [ ] Save evidence of the shared state, verified outcome, and three real model outputs, including fresh generation.
- [ ] Demonstrate that rejected requests leave state unchanged and model failures retain a usable fallback.

Gate: one real integrated interaction works locally. Finish this before expanding the prototype across all rooms. Candidate trials here support selection; final held-out evaluation comes later.

## 4. Complete the game engine and reliable orchestration

- [x] Add an entrance-hall typed-action confirmation safeguard: display the interpreted action/target, require explicit y/yes, and preserve state on cancellation, missing confirmation or interruption. Verified with simulated model responses; this does not fix model interpretation errors or complete browser/full-world integration.
- [x] Test gameplay confirmation separately from model-only evaluation; keep ambiguous/compound prediction errors in model accuracy scores. Full software suite: 100 passed (21 September 2026).
- [x] Record developer cancellation trace: d at confirmation left the desk uninspected, inventory empty and inspect available, without requesting narration. One manual trace, not independent user evaluation.
- [ ] Carry confirmation into browser/full-world orchestration and measure user correction/cancellation separately from raw-model accuracy.
- [x] Narrate accepted entrance-hall state changes only, with one generation attempt and factual fallback on failure; cancellation/rejection triggers no narration and narration cannot apply actions. Saved source/reasons separately from raw-model evaluation.
- [ ] Review user-run guarded gameplay logs for factual errors, false rejections and fallback rate; bounded keyword/anchor checks do not guarantee prose truth.
- [x] Review the first three guarded gameplay narrations and fix exact supplied-fact false rejections (policy v1.1). All three still failed length; 187 tests passed. Confirmation cancellation and broader live acceptance/fallback measurement remain outstanding.
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
