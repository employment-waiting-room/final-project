# The Last Observatory

## An illustrated and narrated AI text adventure

### Project summary

The Last Observatory is the working title for a short browser-based adventure combining three distinct pretrained models: a language model for narrative, an image-generation model for illustrations, and a text-to-speech model for narration. Players explore a small world, collect items, solve puzzles, and choose how the story ends.

A deterministic game engine controls locations, inventory, available actions, and outcomes. The models turn this verified state into a coherent audiovisual experience. AI can help draft the world and generate artwork; the developer reviews the resulting specification rather than needing to draw or write an extensive story manually.

## Research question

> How reliably can local pretrained models interpret free-text player actions and generate a coherent illustrated and narrated adventure while preserving an explicit game state?

## Problem and intended user

The application targets nontechnical players seeking a short interactive story. Generated fiction can contradict earlier events, invent items, or describe impossible actions. Matching its prose with illustrations and narration introduces additional consistency and performance challenges.

The engineering objective is to coordinate generative models around reliable mechanics and evaluate whether the result is understandable, consistent, and playable. Models provide variable narrative presentation and creative media; ordinary code enforces the rules.

## Alignment with the university brief

This project follows Project Idea 1 in `spec.md`: at least three pretrained models working together across different domains/data spaces. The integrated outputs are text, images, and audio.

`example.md` provides additional guidance on engineering depth, accessible interaction, component testing, and evaluation. Its finance-specific algorithms and training requirements do not apply here.

The application must invoke the model pipeline and connect its outputs through shared scene information. Three isolated demonstrations or manually assembled assets are insufficient. Caching is appropriate for responsiveness, but generation must be implemented, demonstrated, and recorded.

## Initial adventure and scope

Proposed premise: the player is trapped in an abandoned observatory during a storm and must restore its signalling equipment to call for help.

The first version includes:

- one single-player adventure, intended to take approximately 10-15 minutes;
- five locations: entrance hall, library, workshop, generator room, and telescope chamber;
- one main objective, a small inventory, and two reachable endings;
- free-text player actions, with optional engine-approved suggested actions at each decision point;
- language-model interpretation of intent, deterministic feasibility checks, and clarification of ambiguous requests;
- generated descriptions grounded in current state and action outcomes;
- one generated illustration per location, reused while its depicted facts remain valid;
- generated narration with optional playback and replay controls;
- visible inventory, current objective, restart, and clear loading/error states;
- an initial minimal prototype followed by a browser interface for nontechnical players.

Exact puzzle rules and the setting can be refined during world design without expanding scope. Typed requests are supported within a defined action vocabulary and the reviewed five-room world; arbitrary new mechanics and outcomes are excluded. The first version also excludes combat, multiplayer, voice input, animation, unlimited world generation, and training models from scratch. Persistent save/load is a stretch feature. NPCs and additional character voices are not part of the agreed core scope.

## Model orchestration

| Stage | Pretrained model role | Input | Output |
| --- | --- | --- | --- |
| Intent interpretation | Language generation (same model as narrative) | Player request, known visible entities, supported action vocabulary, and current state | Structured proposed action and target, clarification request, or unsupported-intent status |
| Narrative | Language generation | World facts, current state, validated action outcome, allowed action IDs, and short history | Structured scene text, choice labels, and a visual brief |
| Illustration | Image generation | Validated visual brief, fixed location facts, and shared style description | Location illustration |
| Narration | Speech synthesis | Exact accepted scene text | Playable narration |

Exact model identities, versions, runtimes, and local versus hosted execution remain to be selected through feasibility trials. Each role must use an identifiable pretrained model. A runtime name or placeholder asset alone does not meet that requirement.

Research at least two candidates per role. Run comparable trials where feasible and record exclusions honestly, including hardware incompatibility or unavailable access. Compare output quality, latency, memory requirements, cost where applicable, licensing, and integration effort. Keep evidence for selected and rejected models.

## Game state and generation boundaries

Maintain a reviewed world specification containing room connections, items, puzzle prerequisites, action effects, and ending conditions. Player state includes location, inventory, visited rooms, puzzle flags, ending status, and state revision.

For each action:

1. For typed input, interpret one requested action into a structured action ID and target. Validate the interpretation schema and entity/action references. Ask for clarification on ambiguous input and explain unsupported requests without changing state. Suggested-action buttons supply canonical IDs directly. Compound requests must be narrowed to one action before execution.
2. Check the proposed action's prerequisites against the current state using engine rules. For infeasible requests, give a factual reason without changing state or revealing hidden puzzle information.
3. Apply the legal transition once and record its outcome.
4. Compute new scene facts and allowed actions.
5. Request a structured narrative presentation from the language model.
6. Validate the output schema and action IDs, and check explicit factual constraints where possible.
7. Generate or retrieve the appropriate illustration and synthesize the accepted text.
8. Display outputs associated with the same state revision.

The language model cannot grant items, unlock doors, invent destinations, or decide puzzle success. Choice labels must map to engine-approved actions; canonical labels provide a fallback. Schema validation cannot guarantee semantic consistency in prose, so contradiction checks and human evaluation are still required.

The interpreter may recognise a supported action even when it is currently infeasible (for example, unlocking a door without its key); the engine decides feasibility. Treat player text as input rather than instructions that can override world rules. Model confidence alone must not authorise an action. Invalid interpretations, timeouts, and clarification responses leave state unchanged and offer suggested actions as a fallback. This additional language-model use remains within the text data space, not a fourth model role.

Use a bounded retry for invalid output, followed by a factual template fallback. Retrying generation must never apply an action twice. Record fallback use separately from successful model generation. Prevent repeated submissions and discard stale media responses after restart or state changes.

## Media consistency and responsiveness

Use shared style instructions and stable visual facts for each location. Prefer environment-focused illustrations that do not depict changing inventory or reveal puzzle solutions. Reuse images only while their depicted facts remain valid.

Cache images by location, visual brief, style, and model configuration. Cache narration by accepted text, voice, and model configuration. Show text when ready and load media separately. Audio failure must not prevent reading or choosing actions; image failure should show a clear placeholder with a retry option.

Log model identity, prompt version, parameters, seed where supported, latency, validation result, and cache status. Report fresh-generation and cached performance separately.

## Data and evaluation fixtures

No historical tournament dataset is required. Create a small reviewed world and local test collection:

- approximately 15-20 state/action cases covering exploration, revisits, item collection, locked actions, and endings;
- a labelled intent test set with paraphrases, infeasible requests, ambiguous references, unsupported actions, compound requests, and attempts to override the rules; record expected action/target or clarification/rejection and expected state effects;
- five illustration briefs with required and forbidden details;
- approximately ten narration passages including location and item names;
- scripted playthroughs reaching both endings and exercising invalid actions.

Separate development examples from held-out evaluation cases before final tuning. Preserve prompts, configurations, generated outputs, annotations, and asset provenance. Record sources and reuse conditions for external material and distinguish generated from manually authored content.

## Evaluation

### Individual models

| Component | Measures |
| --- | --- |
| Intent interpretation | Action/target accuracy, valid-request acceptance, infeasible-request rejection, clarification appropriateness, unsupported-request handling, rule-bypass success rate, and latency |
| Language | Structured-output success, invalid action IDs, contradictions against state, readability, latency, and fallback frequency |
| Images | Human checklist of required/forbidden details, style consistency, clarity, and generation time |
| Speech | Human-checked omissions/substitutions, name pronunciation, intelligibility, and synthesis time relative to audio duration |

Use the same fixtures and written rubric for candidate comparisons. Where practical, hide model identities and vary presentation order in human ratings. Retain failures and explain selection decisions.

### Integrated application

- Unit-test transitions, inventory, puzzle prerequisites, endings, schema validation, and duplicate-action protection.
- Verify both endings are reachable and exploration does not create unintended dead ends.
- Complete a playthrough with all three real models and exercise timeout/failure recovery.
- Measure completed playthroughs, narrative contradictions, media mismatches, and waiting time.
- Compare state-grounded narrative prompts with a simpler prompt baseline on the same cases.
- Evaluate intent interpretation on held-out phrasings and report results by request category, including false acceptance and false rejection. Compare typed interaction with suggested-action interaction on equivalent tasks, recording completion, misunderstandings, perceived agency, and waiting time; distinguish model interpretation errors from engine enforcement errors.
- Conduct a small player study, aiming for 3-5 participants if available, covering choice clarity, perceived agency, coherence, and enjoyment.
- Implement at least one evidence-based improvement and retest the affected behaviour.

Record numerical quality and latency targets after initial feasibility trials and before final evaluation. Report small-sample limitations; subjective enjoyment alone does not establish model accuracy.

## Expected deliverables

- A working browser adventure integrating pretrained text, image, and audio generation.
- A reviewed world specification and deterministic game engine.
- Reproducible environment and model setup instructions.
- Model-selection experiments, saved outputs, and decision records.
- Meaningful automated tests and complete-playthrough evidence.
- Evaluation fixtures, results, user feedback, and documented iteration.
- A report explaining architecture, orchestration, limitations, model/asset licensing, and future work.
- A short demonstration including fresh generation and cached playback.

## Delivery priorities and risks

Given the short deadline, first demonstrate one scene through all three real models. Next complete a playable route, then all locations and both endings. Reserve time for evaluation and reporting before adding mechanics.

| Risk | Mitigation |
| --- | --- |
| Hardware or cost exceeds available resources | Run feasibility trials first and select an affordable executable model stack |
| Narrative contradicts mechanics | Explicit state, restricted actions, factual checks, bounded recovery, and human evaluation |
| Typed intent is misinterpreted or tries to bypass rules | Structured action interpretation, engine-owned feasibility checks, clarification, unchanged state on failure, and suggested-action fallback |
| Images contradict state or reveal solutions | Stable location briefs, forbidden-detail checks, and versioned caching |
| Slow generation interrupts play | Short passages, media caching, separate loading, and measured latency |
| Failures or repeated clicks corrupt progress | Apply transitions once and test recovery and stale responses |
| Scope leaves no time for evaluation | Limit rooms and mechanics; defer save/load and extra content |
| Creative evaluation is only subjective | Combine ratings with constraint checks, consistency measures, and software tests |
