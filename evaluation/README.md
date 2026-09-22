# Development evaluation fixtures

`development.json` contains 53 development cases for world contract v2:

- 24 state/action cases (S20 is split into rescue and shelter).
- 20 intent cases, including the user's looking and knocking regressions.
- Nine matched controls crossing three state levels with three language categories.

Each case includes a legal setup trace, complete initial state, request, expected interpretation and transition outcome, complete expected state, required facts and forbidden claims. These are assistant-authored expectations, not model results or user-study evidence.

State complexity uses the number of true puzzle flags: 0-1 simple, 2-4 moderate, 5-7 complex. This is a reproducible project-specific proxy, not a validated measure of cognitive difficulty. Language difficulty is labelled separately: direct, paraphrase, ambiguous, compound, unsupported or adversarial. These categories are not a numerical ranking. The matched controls provide limited coverage, not a balanced experiment across every action.

From the project root, validate with:

```powershell
.\.venv\Scripts\python.exe -m observatory.fixtures
.\.venv\Scripts\python.exe -m pytest tests -q
```

`observatory/fixtures.py` provides strict schemas and a reference transition function. The builder in `scripts/build_development_fixtures.py` records reproducible expectations and refuses to overwrite an existing dataset. Validation checks setup reachability, action/target pairs, state invariants, outcomes, IDs and complexity labels. Because generation and validation share the reference rules, these checks do not independently prove the rules correct; boundary assertions provide additional checks. The application's current engine still implements only the entrance-hall prototype. Passing fixture tests does not mean the full game or models pass these cases.

All cases in `development.json` are development material. Do not report them as unseen evaluation. A separate reserved intent dataset is described below. Keep expected labels, setup traces and forbidden claims out of intent model inputs. Shared media development inputs are now in `media_development.json`, with their own protocol below.

## Shared narrative, illustration and speech development fixtures

`media_development.json` contains 16 verified post-action narrative inputs, five room illustration prompts and ten exact speech passages. Inputs were adapted from `development_fixtures.md` and the accepted world contract. Narrative references are checked against the existing development cases; no reserved intent case is used. Run the offline validator:

```powershell
.\.venv\Scripts\python.exe -m observatory.media_fixtures
```

`scripts/build_media_fixtures.py` reproduces the dataset and refuses to overwrite the saved file. `observatory/media_fixtures.py` defines strict fixture/output schemas and structural narrative checks. Its `check_narrative` function checks JSON, exact suggestion pairs, visual brief identity and description length; semantic review remains pending until a person reviews the prose. For later model input, use only each narrative fixture's `input` field. Required-fact and forbidden-claim checklists are reviewer material. Image prompts intentionally include their design constraints; speech uses the exact saved passage.

Read [media_protocol.md](media_protocol.md) for per-role scoring, rating anchors, evidence requirements, proposed repeats, timing rules and limitations. Existing standalone feasibility scripts remain unchanged and do not consume this dataset. The narrative runner below now consumes it; image/speech comparison adapters, authorised inference, human ratings and separate media holdouts remain outstanding. These files do not integrate models into gameplay or establish candidate quality.

## Narrative development comparison runner

Narrative `--prompt-version v2` is a development-informed candidate added after the 64-request v1 baseline. It emphasises the actual outcome, preservation of explicit non-effects/inventory, no inferred puzzle steps, and the existing description length. Only system-prompt text changes; source cases, schema, generation settings, schedule and scoring remain identical. Original `v1` remains the default. No improvement is established until the user runs and reviews the comparison.

User-run revised comparison (64 requests, no downloads):

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_narrative --models qwen3:4b gemma3:4b --prompt-version v2
```

Compare against preserved v1 run `20260922T121539136759Z-55b7d9bd`. Send the saved folder path and any errors for review. A fresh v1 control can be run with the same command and `--prompt-version v1` if runtime variation needs investigation; it adds another 64 requests. Do not claim a pure timing comparison when loading/cache conditions differ. This is one controlled prompt revision using known development failures, not held-out validation. Keep structural checks and human factuality review separate; do not promote v2 just for better length compliance. Further prompt tuning is not automatically authorised.

`observatory/evaluate_narrative.py` compares explicitly named installed Ollama candidates using identical narrative inputs, the versioned `world-v2-narrative-eval-v1` prompt and `NarrativeOutput` schema. It never interprets player actions or applies a gameplay transition. The selected outcome has already been determined by the fixture. Human review labels are excluded from model requests.

Commands below are for a **subsequently authorised model experiment**, not part of the completed implementation/test work. With Ollama running and candidates already installed:

```powershell
# Full proposed comparison: 16 cases x 2 models x 2 repetitions = 64 requests.
.\.venv\Scripts\python.exe -m observatory.evaluate_narrative --models qwen3:4b gemma3:4b
# Optional separate compatibility check: two requests, explicitly partial.
.\.venv\Scripts\python.exe -m observatory.evaluate_narrative --models qwen3:4b gemma3:4b --limit 1 --repetitions 1
```

Defaults: two repetitions, seeds 42/43, temperature 0.3, 4096-token context, 600-token output budget, thinking disabled and 180-second per-request HTTP timeout. Candidate order reverses on alternate repetitions; each candidate processes its selected cases in one block. `--models` is required; `--repetitions`, `--limit`, `--seed`, `--timeout`, `--think`, `--dataset` and `--output` are configurable. Prompt/schema and other generation settings remain common to all candidates. This configuration has been tested only with simulated responses; runtime compatibility, token-budget adequacy and narrative quality still need measurement. Nothing downloads models.

Each unique folder under `generated/narrative-evaluations/` preserves:

- `manifest.json`: exact prompt/schema, dataset/protocol hashes, model names, available runtime/model-inventory metadata (including whatever digests Ollama reports), environment, timeout, generation settings, full schedule and run status.
- `dataset.json` and `protocol.md`: exact snapshots used for the run, including review-only material that is not sent to the model.
- `requests/Axxxx.json`: exact request saved before inference, so a pending interrupted request remains identifiable.
- `results.jsonl`: one flushed row per returned/failed attempt, including request, raw HTTP response when available, content, errors, structural checks, wall time and available Ollama timing/token fields. Failures continue to the next scheduled attempt; there are no retries, silent corrections or fallback outputs.
- `reviews/Axxxx.json`: editable required-fact and forbidden-claim checklists, contradiction/addition findings, readability, reviewer/date and notes, all initially pending/null. Match the attempt ID to `results.jsonl` to inspect prose. Do not mark unreviewed fields as passing or fill in ratings for missing output.
- `summary.json`: structural pass counts/rates and wall-time summaries overall and by model, with first-in-block versus later-in-block timings separated. Semantic pass rates remain null. This summary does not ingest completed human-review files; review aggregation is separate future work.

Every recorded attempt, including HTTP, timeout, truncation and schema failures, stays in structural-score denominators. Completed HTTP requests can fail structural checks. Valid JSON can still contain false prose. Metadata failures are explicit; missing timing values remain null rather than zero. Ollama duration fields are retained in their raw nanosecond units; wall seconds include the whole attempt. First calls are not proven cold and later calls are not proven warm. No RAM/VRAM sampling or automatic human scoring is implemented.

Interrupted runs retain completed rows, request files and partial summaries, with `status=interrupted`. An in-flight request interrupted before a result is recorded is identifiable from the schedule/request files and is excluded from the recorded-attempt denominator; do not report the partial summary as a completed comparison. Run completion means the schedule finished, not that predictions passed. Do not use narrative results to claim intent accuracy, held-out generalisation or gameplay correctness. Generated run folders remain Git-ignored and must be preserved deliberately for submission.

## Reserved intent evaluation (22 September 2026)

`held_out_intent.json` contains 30 assistant-authored, unrun intent cases under world contract v2. `held_out_intent_reservation.json` records the reservation time, exact-byte SHA-256, version, category counts and release conditions. Coverage includes all 13 action IDs, both endings, all three complexity groups and six language categories: seven direct, seven paraphrase, and four each ambiguous, compound, unsupported and adversarial. This is small, uneven coverage, not a balanced factorial experiment.

The labels were assigned from the accepted contract, not model outputs. Each case includes a legal setup trace and full expected state/outcome; the reference transition function checks consistency. Shared author/reference logic is not independent verification. Independent annotation review remains pending. These cases were authored after the development experiments and cover known failure families; claim new reserved wording and some new visible state combinations, not unseen mechanics, blind authorship or proven generalisation. Some states deliberately overlap development states to test new wording under comparable conditions.

Validate offline, without inference or printing the case wording:

```powershell
.\.venv\Scripts\python.exe -m observatory.held_out
```

The validator checks the reservation hash, schema, reachable setup, reference outcomes, metadata, and separation of IDs and normalised wording from development data. It cannot detect all semantic duplicates. The existing development runner rejects the `held_out` split before any model request or output folder creation, even if passed via `--dataset`. No final-evaluation execution option has been enabled. The one-time authoring script, `scripts/reserve_intent_fixtures.py`, refuses to overwrite either reservation file; do not regenerate these cases during development.

Before release, freeze model identity/digest, prompts, runtime/settings, scoring criteria and the dataset hash; obtain separate authorisation for the final model run. Review annotations against the contract without testing candidate predictions. Keep answer labels out of requests, retain all failures in denominators and report model-only results separately from player confirmation and engine enforcement. Any case inspected for prompt/rule tuning or selected based on model outputs must be retired to development; reserve a fresh replacement set before claiming a subsequent held-out result. Record annotation corrections as explicit version changes rather than silently updating the hash.

The reservation is a workflow boundary, not access control: source files and tests can read it. Avoid exposing these cases to future tuning work. `.gitattributes` preserves dataset bytes across Git checkouts; the dataset and manifest are not ignored. Relevant documentation has explicit `.gitignore` exceptions so it can be included in the user's next commit. Nothing has been committed automatically. Shared media development fixtures are separate from this reservation; media holdouts remain outstanding.

## Intent evaluation runner

`--prompt-version v1-clarify` is an experimental, unsuccessful clarification-rule variant. Its first full development run scored 48/53 versus v1-json's 49/53, retained the four ambiguity/compound failures and introduced a dropping-request failure. Keep it for reproducibility; v1-json remains the preferred measured candidate. Prompt instructions alone have not resolved the intent-safety issue. No gameplay integration or held-out accuracy is implied.

The successful development candidate is now built in as `--prompt-version v1-json` (manifest identity `world-v2-intent-eval-v1-explicit-json`). Its complete requests were verified against all 53 saved requests from run 20260921T201645349662Z-21f0724d. This preserves the extra instruction before the canonical catalogue. Original v1 remains the default for reproducibility; select v1-json explicitly for comparisons.

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_intent --model qwen3:4b --prompt-version v1-json
.\.venv\Scripts\python.exe -m observatory.evaluate_intent --model gemma3:4b --prompt-version v1-json
```

The second command requires a separately installed model. Official source: https://ollama.com/library/gemma3:4b (approximately 3.3 GB at review). User-managed download: `ollama pull gemma3:4b`. No Gemma download or inference was performed when adding this option. First use can check compatibility with `--limit 3`; such a partial run is not the full comparison.

Prompt revisions are explicitly selectable. The original `v1` remains the default. Run the revised prompt with `--prompt-version v2`; only the system prompt changes, while schema, context projection, fixtures and generation settings remain fixed. V2 clarifies intent versus feasibility, supplies synonyms and orders the classification rules. It was informed by development failures and is not an unseen evaluation. No improvement is claimed until measured.

The first completed baseline contained five pairs of identical request payloads. One pair (S06/I04, unlocking without the key) produced different predictions despite identical settings. Preserve this as a repeatability limitation; a single before/after run cannot establish a stable improvement. Repeat both prompt versions before making strong comparative claims. Cause of the disagreement is unconfirmed.

With Ollama running and the model already installed, run from the project root:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_intent --model qwen3:4b
```

For a short connectivity check add `--limit 3`; this is explicitly recorded as a partial run. Change `--model` for an already installed alternative. The runner never downloads models. Default timeout is 60 seconds per request; `--timeout` changes it. Thinking defaults off; `--think` enables it for supported models. Unsupported runtime settings are recorded as errors rather than silently retried with different settings.

Each unique folder under `generated/intent-evaluations/` contains `manifest.json`, incrementally saved `results.jsonl`, and `summary.json`. The manifest records the dataset SHA-256, selected IDs, prompt version, environment, requested model and available Ollama version/model inventory (including digests). Each result preserves the exact request, raw response, parsed prediction or error, wall-clock latency and available Ollama timing/token fields. Metadata failures are explicit. Resource memory measurements are not yet implemented. Interrupted runs retain flushed case records but may not have a summary.

This runner uses a new full-world evaluation prompt and schema, separately from the three-action gameplay interpreter. Every case goes to the model; existing local guards are not applied. It cannot establish current gameplay accuracy or be directly compared to the older tuned 8-case guarded trial. Prompts contain the action catalogue, player request and projected context; answer labels, setup traces and hidden item locations are excluded. Requests are independent with no conversation history or retries.

The summary reports structural validity, exact status/action/target accuracy, and reference state/outcome agreement separately, overall and by both label dimensions. All attempted cases, including errors, are in the accuracy denominator. Reference agreement alone can reward the wrong intent when two invalid actions are both rejected, so use intent accuracy as the primary measure. Latency includes errors and model loading; raw fields allow separate analysis. No warm-up is discarded. Case families may repeat requests, so these are descriptive development results, not independent statistical samples or held-out generalisation claims. Narrative factuality, illustrations, speech and production-engine correctness are outside this runner.

Generated results are ignored by Git. Preserve selected evidence deliberately with the report/submission; do not assume a push includes it.
