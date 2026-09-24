# Development log: The Last Observatory

## Purpose and evidence conventions

This log records the decisions, implementation work, experiments, problems, and reflections behind the project. It was first compiled retrospectively on 10 September 2026 from the development conversation and saved local evidence. Earlier discussions are recorded in sequence without inventing exact dates. Experiment timestamps in filenames and JSON are UTC; local time is Africa/Johannesburg (UTC+2).

This is a working evidence record for the report and process exam, not a finished report or a claim that all planned functionality exists. Distinguish measured results, assistant observations, user-reported actions, and proposed work. No independent user study has taken place.

## 1. Understanding the assessment and choosing a project

### Initial concept: SpoilerSense

The original project was an MTG application predicting an unreleased card's competitive viability in Standard from a spoiler image. Its proposed pipeline combined detection/cropping, OCR, language interpretation, historical retrieval, and evidence-based scoring. Historical comparisons would use mechanics rather than assume the unreleased card already existed in a database.

We reviewed `project.md`, `tasks.md`, and the university's [orchestration brief](spec.md). The brief requires at least three pretrained models operating in different domains/data spaces, integrated toward a clear objective, with model-selection and evaluation evidence. Counting OCR, language interpretation, and text embeddings as separate models did not by itself settle the data-space requirement. No professor confirmation was obtained.

We considered pretrained time-series forecasting of existing archetype popularity as another data space. The new card itself would have no usage history. Forecasts would provide metagame context, with historical cutoffs to avoid future-data leakage. This was researched conceptually but never implemented or tested.

### Data feasibility investigation

We researched official Magic Online decklists, Magic.gg, MTGTop8, Melee access, and the [Badaro tournament JSON archive](https://github.com/Badaro/MTGODecklistCache). The downloadable archive offered a less manual approach than gathering event URLs. Its documentation reported reduced MTGO coverage from 20 June 2024 and closure in June 2025.

After considering several releases, the proposed test set became The Lost Caverns of Ixalan (LCI). The proposed collection window was 1 June 2023 to 12 January 2024: historical inputs through 9 November, a prerelease buffer, and a 60-day MTGO adoption window from 14 November 2023. This was a study plan, not a completed dataset.

We inspected user-supplied files from Downloads:

- Five Standard League publications dated 1-5 June 2023 contained 114 decklists. Every result was 5-0; all lists contained 60 mainboard and 15 sideboard cards. Rounds and standings were null. They could demonstrate published successful appearances, but not overall metagame share or win rate.
- `standard-challenge-32-2023-07-0112562363.json` contained 43 decklists and 40 standings entries, plus quarterfinal, semifinal, and final matches. Three deck players lacked matching standings. One list had 64 mainboard cards and an empty sideboard. That composition was not inherently illegal, but was a quality-check flag.

MTGTop8 scraping was investigated as an alternative. Date/format searches, event pages, and deck exports looked usable, but publication coverage could still be incomplete. No MTG scraper or full importer was built.

**Decision:** the user discontinued MTG because collating and validating the data was too difficult for the available time. This was a data and evaluation feasibility decision, not evidence that competitive-viability prediction is impossible.

**Reflection:** investigate dataset availability, completeness, and labels before committing to a prediction project. A convenient file format does not remove sampling bias or missing outcomes.

### Alternative ideas and final selection

We discussed projects across education, coding, accessibility, games, and piano. The user considered an MTG playtest analyst but then chose an illustrated text adventure. The user was concerned about writing stories and creating art; generative models could produce this content while the developer concentrated on reviewed game rules and integration.

We also read the [financial advisor example](example.md) to understand the university's expected depth: a complete usable system, justified algorithms, substantial engineering, and critical evaluation. Its finance-specific requirements do not replace the requirements of Project Idea 1.

## 2. Current concept and architecture

Working title: **The Last Observatory**. The proposed player is trapped in an abandoned observatory during a storm and must restore signalling equipment.

The rewritten [project plan](project.md) and [task list](tasks.md) define:

- Five locations, a small inventory, one objective, and two endings.
- Two or three valid choices at each decision point.
- A pretrained language model for scene text, an image model for illustrations, and a speech model for narration.
- A browser interface with text, images, audio controls, inventory, objective, and restart.

**Key design decision:** deterministic Python code will own inventory, movement, puzzle prerequisites, and endings. Generated prose and choices must describe engine-approved facts and actions. This limits the impact of hallucinated mechanics and makes the rules independently testable.

Images are intended to show stable location facts and be cached. Narration will use the exact accepted text. Media generation should not block the availability of readable text or corrupt state after a retry. These are design intentions; the complete engine and orchestration have not been built.

**Scope controls:** no multiplayer, unrestricted typed actions, combat, animation, unlimited worlds, or model training from scratch. Persistent save/load is deferred.

## 3. Schedule, constraints, and report requirements

The user specified free, local execution and no restrictions on language/framework choice. The user also asked for confirmation before execution; downloads and experiments have been handled as explicitly approved steps.

The initial assumption that everything was due within a week was corrected:

- Process exam: Tuesday, 15 September 2026, covering decisions, problems, and reflection.
- Full application, report, and video: 28 September 2026.
- More detailed chapter guidance is expected from the user later.

The [report specification](report_spec.md) requires six chapters:

| Chapter | Maximum words |
| --- | ---: |
| Introduction | 1,000 |
| Literature review | 2,500 |
| Design | 2,000 |
| Implementation | 2,500 |
| Evaluation | 2,500 |
| Conclusion | 1,000 |

The combined maximum is **10,500 words**, even though individual caps sum to more. References, figure/table legends, and chapter titles are excluded. The introduction must identify Project Idea 1. The code repository must be publicly viewable through receipt of results; its visibility has not been verified here.

A 3-5 minute video must show the working application, contain the student's own spoken explanation, and must not use AI-generated voices or be sped up. The game's planned speech-synthesis feature does not justify replacing the student's explanation. How to demonstrate that feature within the video's wording should be checked carefully during preparation.

## 4. Local environment setup

### Hardware and storage

Hardware inspection found a Ryzen 7 9700X, Radeon RX 7800 XT, and approximately 15.6 GB usable system RAM. A later Vulkan log identified the GPU and approximately 15,405 MiB free GPU memory during that test. Windows' generic AdapterRAM field was unsuitable for establishing full VRAM capacity, so it was not treated as authoritative.

C: initially had about 18.7 GB free, so D: was considered for large downloads. After the user cleared space, a check showed about 109.9 GB free on C:, and the user requested that all tests be kept in the project folder.

### Project location and software

Work moved from the `mtg_predictor` directory to its sibling:

```text
C:\Users\PC\Desktop\Github\EmploymentWaitingRoom\final-project
```

The agreed stack is Python, FastAPI, Pydantic, and a future HTML/CSS/vanilla-JavaScript interface. HTTPX supports local model calls; pytest supports software tests. JSON files and local asset folders are the initial storage plan.

Python 3.11 was chosen for the isolated environment. Python 3.14 remained installed; subsequent inspection found an existing Python 3.11 installation, so another system Python installation was unnecessary. `.venv` uses Python **3.11.9**.

Installed direct dependencies at setup: FastAPI 0.141.1, Uvicorn 0.52.4, Pydantic 2.13.5, HTTPX 0.28.1, and pytest 9.1.1. See [requirements.in](requirements.in) and the pinned [requirements.txt](requirements.txt). The user later installed Hugging Face download tooling; the original requirements snapshot does not record those later additions.

Added [SETUP.md](SETUP.md) and [.gitignore](.gitignore), excluding the virtual environment, local secrets, model weights, generated outputs, and downloaded image runtime.

**Verification:** `pip check` passed and an in-process FastAPI health request returned the expected response. This was an environment smoke check, not an implemented application or persistent test suite. A Starlette deprecation warning about HTTPX appeared; the request still passed, and the warning remains a future compatibility consideration.

**Setup problems:** Windows sandbox restrictions required elevated tool execution for the installed Python and writes in the new sibling directory. An inline Python smoke-check command initially failed because PowerShell stripped quotes; supplying the code through standard input resolved it. These were execution/setup issues, not model failures.

## 5. Image-generation investigation and download

### Selection

Compared the documented installation routes for [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp) and [ComfyUI](https://docs.comfy.org/installation/manual_install). These are runtimes, not two pretrained model candidates.

Selected stable-diffusion.cpp's Windows Vulkan build for the first experiment because it provided a direct local executable and avoided a separate PyTorch GPU installation. ComfyUI was deferred because the exact native Windows/AMD compatibility route was uncertain. It was not installed or benchmarked.

Selected [SDXL-Turbo](https://huggingface.co/stabilityai/sdxl-turbo) for an initial low-step, 512x512 image trial. Its model page listed the Stability AI non-commercial community licence. This is a feasibility selection, not evidence that it outperforms other image models. A second image model has not been tested.

Pinned artifacts:

- Runtime: `master-849-d04e895`, Windows Vulkan x64 ZIP, 38,862,152 bytes.
- Runtime ZIP SHA256: `5a75237c5c6a7253b1079b03f6ec0fe1358393bf879f486887863ac31dea978e` (verified).
- Model: `sd_xl_turbo_1.0_fp16.safetensors`, 6,938,081,905 bytes.
- Model revision: `71153311d3dbb46851df1931d3ca6e939de83304`.
- Model SHA256: `e869ac7d6942cb327d68d5ed83a40447aadf20e0c3358d98b2cc9e270db0da26` (verified before inference).

### Download problems and reflection

The first pinned model URL contained an incorrect revision character and returned 404. Resolving the revision through the publisher's API corrected it. Downloads through curl were slow. A four-range Python downloader was attempted, but its range files stalled; it was not the successful acquisition route and should not be presented as proven tooling.

The runtime was relocated from D: into `tools/stable-diffusion/` under the current project. Model downloads were redirected into `models/`. We advised use of the official Hugging Face client with Xet support; the user encountered an unauthenticated-request warning, received authentication instructions, and subsequently reported the model download complete. The successful final file was verified locally. We did not measure or establish which transfer method was faster, or independently confirm authentication state.

Repeated progress polling and troubleshooting consumed excessive assistant interaction. The user raised this concern. Lesson: provide a download command, let the user complete long transfers, and resume with a targeted verification rather than repeatedly polling. Some earlier partial files may remain; cleanup has not been verified or performed as part of this log.

## 6. Image experiment: 10 September 2026, 16:28 UTC

Script: [test_image_generation.py](scripts/test_image_generation.py).

The prompt requested an illustrated abandoned observatory with a brass telescope, open dome, bookshelves, lantern-lit desk, storm clouds, warm/cool lighting, no people, and no lettering.

Settings: 512x512, four sampling steps, CFG scale 1, Euler sampler, `sgm_uniform` scheduler, seed 42. A fresh CLI process was used.

| Measurement | Result |
| --- | --- |
| CLI exit code | 0 |
| End-to-end elapsed time, including loading | 13.832 seconds |
| Runtime-reported generation time | 12.67 seconds |
| Saved image size | 692,052 bytes |
| GPU evidence | Computation and buffers on Vulkan0, RX 7800 XT |

Evidence: [image](generated/feasibility/observatory.png), [prompt](generated/feasibility/observatory-prompt.txt), [metadata](generated/feasibility/result.json), [runtime log](generated/feasibility/generation.log).

**Assistant visual review:** the image had a recognisable telescope, bookshelves, and illustrated aesthetic. It did not clearly fulfil the storm, open-dome, or lantern requirements. Local execution worked, but exact prompt adherence remained imperfect.

**Conclusion:** image generation is feasible on this machine. One image does not establish stylistic consistency, repeatability, or performance across the complete application. No cross-location or alternative-model benchmark has been performed.

## 7. Language-model selection and manual trial

Researched Qwen3 4B (approximately 2.5 GB Ollama download, Apache 2.0) and Gemma 3 4B (approximately 3.3 GB download, Gemma terms). Selected Qwen3 4B for the first test because of its smaller download and suitability as an instruction-following candidate. Gemma remains an untested comparison candidate, not a measured rejection.

The user installed Ollama and downloaded `qwen3:4b`. Ollama provides a local API and JSON-schema output. A schema constrains response format but cannot ensure narrative truth.

Manual prompt: narrate a locked-door scene, with an unlit lantern, no key, and exactly two allowed actions. The user pasted the response and `ollama ps` output.

- Positive: door stayed locked; no key was granted; action IDs were correct.
- Failure: the response described an "unlit lantern, its flame flickering". This is a direct contradiction.
- User-provided device output showed `100% GPU`, approximately 3.2 GB loaded, and context 4096.

This motivated explicit state constraints and a repeatable scripted test. Manual response time was not measured.

## 8. Automated narrative experiment design

Created [test_narrative_generation.py](scripts/test_narrative_generation.py) using the existing HTTPX and Pydantic dependencies. It calls only local Ollama, creates a new timestamped result folder for each run, and saves requests, raw responses, validation results, timings, model metadata, and GPU snapshots.

Three independent cases:

1. Locked library door; player carries an unlit lantern and has no key.
2. Workshop revisit; brass key already collected, hook empty, toolbox closed.
3. Generator puzzle completed; fuse installed, power on, door unlocked, rescue signal not yet sent.

Each request uses a strict schema for a description and 2-3 choices. Validation checks the schema, duplicate/missing/extra action IDs, 60-100 description words, and normal generation completion. It does not automatically prove semantic correctness or that choice-label wording is faithful. Manual review remains necessary.

Shared settings: model `qwen3:4b`, thinking disabled, temperature 0.3, seed 42, context 4096, output budget 600 tokens, keep-alive five minutes. No retries or automatic repair were used, preserving first-attempt failures.

Saved model identity: Qwen3 4B Q4_K_M, digest `359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7`. The first run recorded Ollama **0.34.0**. The post-run snapshot reported model size and VRAM allocation both 3,178,149,969 bytes.

## 9. Narrative results and prompt iteration

| Run (UTC) | Prompt | Locked door: words / seconds | Collected item: words / seconds | Completed puzzle: words / seconds |
| --- | --- | --- | --- | --- |
| 17:55:12 | v1 | 45 / 5.834 | 45 / 1.100 | 47 / 1.091 |
| 17:58:19, user rerun | v1 | 31 / 0.925 | 45 / 1.091 | 47 / 1.084 |
| 18:02:13 | v2 | 63 / 1.419 | 54 / 1.199 | 57 / 1.211 |

All nine responses passed schema and action-ID checks and completed normally. These were short outputs, so timings do not predict latency for longer scenes. The initial 5.834-second request included approximately 4.634 seconds of loading; later requests reused a loaded model.

### v1 findings

All descriptions missed the 60-word minimum. The original combined field, `structural_pass`, was false even though JSON and actions passed. This confused interpretation and was a reporting-design problem.

The flickering-unlit-lantern contradiction did not recur. However, outputs invented environmental details such as moonlight and high windows. The completed-puzzle output added an unspecified brass material to the lantern. Correctly structured output was not sufficient for factual fidelity.

### v2 changes and findings

With user approval, the script was adjusted to:

- Print schema, actions, length, word count, completion, and time separately.
- Rename the combined result to `automated_pass` and save separate pass counts.
- Target approximately 80 words in five or six sentences, retaining the unchanged 60-100 acceptance range.
- Explicitly prohibit invented materials, windows, weather, light sources, and unseen contents.
- Use prompt version `state-grounded-v2`; preserve earlier output folders.

Length compliance improved to 1/3. However, the workshop response put the carried lantern on a wall, contradicting the supplied inventory. It also invented moonlight and windows despite the explicit prohibition. The generator scene invented metal walls and gave a questionable causal description of visibility despite electric lights being on.

**Conclusion:** this revision improved one measured dimension but did not establish narrative reliability. Prompt constraints alone did not eliminate hallucinations. Do not claim a general improvement from three development cases. These prompts were tuned using known failures and are not held-out evaluation.

The locked-door response changed between v1 runs despite the same seed/settings. A fixed seed should not be presented as a guarantee of identical results in this runtime; the cause was not investigated. Future comparison should use repeated samples and record loading/cache conditions.

Evidence:

- [First v1 summary](generated/llm-tests/20260910T175512435328Z/summary.json) and [assistant review](generated/llm-tests/20260910T175512435328Z/review.md).
- [User v1 rerun](generated/llm-tests/20260910T175819768451Z/summary.json).
- [v2 summary](generated/llm-tests/20260910T180213982035Z/summary.json).

## 10. Current status and next decisions

Completed: planning documents, Python environment, runtime/model installation for image and text generation, one image feasibility test, a manual language test, three automated language runs, and one prompt/reporting iteration.

Still outstanding:

- Select and test a local speech-synthesis model: the third required role is not yet implemented.
- Finalise world rules and implement the deterministic game engine.
- Build the player interface and connect text, image, and speech into one working scene.
- Compare additional model candidates with consistent criteria.
- Decide how much atmospheric invention is permitted and separate it from mechanically important facts.
- Design and test bounded recovery for invalid outputs without hiding first-attempt failures.
- Add meaningful engine and integration tests, held-out scenarios, and repeated model trials.
- Conduct player testing and document an evidence-based interface or gameplay iteration.
- Write the report, verify repository visibility, and record the demonstration.

Generated evidence is currently ignored by Git. Before submission, deliberately preserve selected prompts, results, screenshots, and reviews in report artifacts or a suitable tracked evidence folder; local links alone will not make them available to a marker. Keep large model binaries and credentials out of the repository.

This log does not change the task checklist or mark reliability work complete. Further experiments should be approved before execution, in line with the user's preference.

## 11. Speech-model research (10 September 2026)

With approval to research the third model role, compared Piper with an English Lessac medium checkpoint and Kokoro-82M through the community `kokoro-onnx` runtime. No speech software or weights were installed and no audio was generated during this research.

| Candidate | Documented practical details | Proposed role |
| --- | --- | --- |
| Piper / en_US-lessac-medium | Approximately 63.2 MB ONNX weights plus 4.89 kB configuration; piper-tts 1.8.0 publishes a Windows x64 Python 3.9+ wheel; Python API writes WAV using CPU by default | First feasibility candidate because of small download and direct integration |
| Kokoro-82M / kokoro-onnx | Runtime documents CPU execution and Python 3.11; approximately 300 MB standard weights or 80 MB quantized, with separate voice data and dependencies | Alternative for a later same-passage listening and timing comparison |

Sources: [Piper package and Windows wheel](https://pypi.org/project/piper-tts/), [Piper Python API](https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md), [Lessac files](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium), [Lessac model card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/lessac/medium/MODEL_CARD), [Kokoro ONNX runtime](https://github.com/thewh1teagle/kokoro-onnx), and [original Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M).

Licensing distinctions: current Piper engine is GPL-3.0-or-later; voice models require their own provenance review (Lessac's card links the source dataset licence). Kokoro weights are Apache 2.0 and the ONNX wrapper is MIT; transitive dependencies still have their own licences. These are documentation findings rather than a complete redistribution assessment.

Recommendation: begin with Piper on CPU, leaving GPU resources available for text and images. Actual CPU latency, Windows installation success, and voice quality remain unmeasured. Do not claim either candidate sounds better before listening to equivalent samples. Listed model sizes exclude runtime dependencies and, for Kokoro, separate voice data.

Proposed approved-next experiment: install one candidate, synthesize a short observatory passage, save text/configuration/audio and loading/synthesis timing, measure audio duration, and review pronunciation, omitted words, intelligibility, and suitability for narration. Installation and execution still require the user's confirmation.

## 12. Piper speech feasibility test (10 September 2026)

With user approval, verified the user's installed Piper 1.8.0 in Python 3.11.9 and the Lessac medium model/configuration. No additional installation was necessary. The initial sandboxed Python launch could not access its underlying Windows Store interpreter; running the approved test with elevated sandbox permissions succeeded. This was an execution-environment restriction, not a broken virtual environment.

Created [scripts/test_speech_generation.py](scripts/test_speech_generation.py). It synthesizes a fixed, manually written observatory passage using CPU and Piper defaults, preserving a fresh timestamped folder with passage, voice configuration, WAV, version information, model/config hashes, timings, and errors if any. This tests speech independently; it does not yet narrate live LLM output.

Evidence: [result.json](generated/speech-tests/20260910T182144859261Z/result.json), [passage](generated/speech-tests/20260910T182144859261Z/passage.txt), and [audio](generated/speech-tests/20260910T182144859261Z/observatory.wav).

- Model load: 1.106 seconds; synthesis: 1.361 seconds, measured separately.
- Produced 19.551 seconds of mono, 22,050 Hz, 16-bit WAV audio.
- Synthesis real-time factor: 0.0696 (excludes loading).
- WAV readable, 431,104 frames, nonzero audio data; process exited successfully.
- Actual local configuration size is 5,377 bytes, differing from the earlier research listing; its exact bytes and hash are preserved with this run.

Interpretation: local CPU speech generation is feasible on this machine based on one run. Automated checks establish a readable nonempty audio file, not intelligibility, complete pronunciation, or subjective quality. User listening review is pending. Kokoro has not been tested, and this is not a comparative benchmark. All three model roles now have standalone feasibility outputs, but integration, narrative reliability, game implementation, and evaluation remain outstanding. Next: listen against the saved passage and record any skipped words, pronunciation issues, and pacing problems before deciding whether to adjust or compare voices.

## 13. First playable game sequence (11 September 2026)

The user confirmed the Piper sample read the text correctly. This is informal feedback on one passage, not a complete speech evaluation.

With approval, implemented the terminal sequence: inspect desk, reveal key, collect key, unlock library. [Engine](observatory/engine.py) owns immutable state and validates actions; [terminal entry point](observatory/__main__.py) displays fixed descriptions, inventory and numbered choices. Run from the project directory with `python -m observatory` using the virtual environment. No models or additional dependencies are needed for this prototype.

Decision: separate game rules from generated presentation so model errors cannot grant items or unlock doors. Each valid action returns new state. Unavailable or repeated actions raise an error without changing state; the key is retained after unlocking. This small sequence ends at the unlocked door and does not implement movement, other rooms, endings, persistence, or network stale-request protection.

Validation: `.venv/Scripts/python.exe -m pytest tests -q` passed all 9 cases in 0.02 seconds. [Tests](tests/test_engine.py) cover the full sequence, preservation of previous states, prerequisite violations, unknown actions, repeated actions, and room restrictions. A terminal smoke playthrough with inputs `bad`, `0`, `1`, `1`, `1` rejected invalid choices and completed the sequence. User playthrough remains pending. The initial file creation needed the package directories created with sandbox escalation; implementation then succeeded.

The user subsequently ran the terminal sequence and supplied its output: inspecting revealed the key while inventory stayed empty, collecting added `library_key`, and unlocking completed the sequence with the key retained. This confirms one successful manual happy-path playthrough; it is not a broader player study.

The broad engine checklist items remain incomplete because they also require the rest of the adventure. Next: agree the remaining room and puzzle rules before expanding scope.

## 14. Free-text action scope approved (11 September 2026)

The user approved adding typed player actions after discussing project depth. Updated project.md and tasks.md: the language model interprets a request into a supported action/target, while deterministic rules check feasibility and apply outcomes. Optional suggested actions remain available. Ambiguous or compound requests require clarification; unsupported requests and interpretation failures leave state unchanged. This preserves the five-room scope and does not promise arbitrary mechanics or add NPCs.

Rationale: intent interpretation introduces measurable AI work beyond narrative presentation. Planned evaluation includes held-out paraphrases, valid and infeasible actions, ambiguous references, unsupported requests, and rule-bypass attempts, plus a comparison of typed and suggested-action interaction. Measure interpretation accuracy separately from engine enforcement. Costs include another language-model call, extra latency, and additional fixtures and recovery handling. Only planning documents changed in this step; free-text input is not implemented and the existing terminal prototype remains the current playable version.

## 15. Free-text entrance-hall prototype (11 September 2026)

With approval, added `observatory/intent.py` and connected it to the terminal interface. Qwen3:4b through local Ollama interprets typed requests into validated status/action/target JSON. Temperature 0, seed 42, context 4096, output limit 180 tokens, thinking disabled, 30-second HTTP timeout; exact requests and raw responses are saved under generated/intent-logs. No new dependencies or model downloads were needed. Numbered actions remain available without model inference. Run `.venv/Scripts/python.exe -m observatory` from final-project with Ollama running for typed input.

The deterministic engine checks prerequisites and supplies factual rejection reasons. Missing prerequisites, invalid JSON/action-target pairs, unsupported requests, and timeouts leave state unchanged. Input is limited to 500 characters. Clarification asks the player to restate one action with an explicit object; it is not a conversational reference-resolution system. Successful outcomes still use fixed descriptions; image, speech, and generated narrative integration remain pending.

Added `tests/test_intent.py` and `python -m observatory.evaluate_intent`, an eight-case development experiment preserving individual requests and summary output. Initial live trial [summary](generated/intent-tests/20260911T092000925820Z/summary.json): 6/8 passed. Qwen guessed inspect_desk for 'Examine it' and selected only the first action from 'Search the desk and take the key'. Both could cause an unwanted but mechanically legal transition. Engine validation alone cannot establish user-intent accuracy.

Iteration: conservative local checks request clarification for pronouns and conjunctions, and reject explicit ignore/override/bypass-rules wording. These are narrow heuristics, not general ambiguity or injection protection. They can over-clarify valid language and miss unfamiliar constructions; held-out testing is necessary. A second trial passed 7/8 because the conjunction check classified a rule-bypass request as clarification; ordering an explicit rule-override check first restored the expected unsupported classification. During tests, timestamp-only log filenames collided and overwrote a record; UUID suffixes now prevent that collision. Local guard decisions are also logged separately from model interpretations.

Final validation: 27 automated tests passed in 0.13 seconds, covering the previous engine rules plus structured-output rejection, model timeout, input bounds, clarification, duplicate collection, and the interpreted sequence. Final [development summary](generated/intent-tests/20260911T092128228425Z/summary.json): 8/8 combined-policy cases passed (five model calls, three local guard decisions). This is not 8/8 raw-model accuracy, a held-out result, or a guarantee of semantic correctness. A piped terminal playthrough using 'Search the desk', 'Pick up the key', and 'Use the key on the library door' completed successfully with the real local model.

Next: user tries typed requests, then expand fixtures with unseen phrasings and finalise the remaining world rules. Broad integration and evaluation tasks remain incomplete.

## 16. Task plan realigned with the approved direction (11 September 2026)

At the user's request, rewrote tasks.md around an AI-dependent natural-language adventure with state-grounded narrative and integrated image/speech generation. The plan separates completed prototype evidence from application-wide work, explicitly retains the unresolved user-reported looking/knocking substitutions, and keeps the broader free-roam redesign paused. NPCs and extra voices remain deferred.

The next phase is candidate research and feasibility planning, followed by world/action contracts and fixtures, comparable model trials and one integrated scene, full engine/orchestration, browser delivery, and held-out evaluation. Report and exam preparation run alongside development. The rewrite adds explicit checkpoints, separates model interpretation from rule enforcement, and records the need to preserve assessable evidence despite ignored Markdown/generated folders. This was a planning change only; no application behaviour or model results changed.

## 17. Alternative model shortlist and protocol (11 September 2026)

With approval to proceed in task order, researched official model/runtime pages and recorded model_candidates.md. Shortlisted Gemma 3 4B through Ollama, SD-Turbo through the existing Vulkan runtime family, and Kokoro-82M v1.0 through kokoro-onnx. SD-Turbo fills the missing second image model: it is SD 2.1-derived, unlike the SDXL baseline. File sizes and documented compatibility are research findings, not local runtime measurements or proof of superiority. No models were downloaded, installed, or run.

The document includes source/licence distinctions, candidate identities, a common-input comparison protocol, provisional quality/latency targets for review, and remaining version/resource evidence gaps. Marked only the second-image-candidate and research-consolidation checklist entries complete. Next is a reviewed world/action contract and fixtures before alternative inference trials. The paused free-roam redesign remains outside this step.

## 18. World contract and development fixtures drafted (11 September 2026)

With approval to continue planning, created world_spec.md and development_fixtures.md. Proposed five-room beacon-restoration adventure with a unique key, consumable fuse, instruction prerequisite, explicit rescue/shelter endings, and return paths. Starting inventory remains empty to match the current prototype. Defined bounded look_around separately from inspect_desk and explicitly unsupported knocking/dropping; no general free-roam engine or NPCs added.

Prepared 20 state/action cases (the final case branches to both endings), 20 labelled intent examples, five stable illustration briefs, ten speech passages, and draft scoring/split rules. User-reported look/knock failures are development regressions, not held-out evidence. No new model runs or application changes occurred. Draft rules, especially the endings and action catalogue, await user review; no broad design checklist items were marked complete. A separate held-out set remains to be created before tuning.

## 19. Exam preparation from supplied papers (14 September 2026)

Read the locally supplied Example, mock, March 2024 and September 2024 exam PDFs by extracting their text streams without installing dependencies. The Example file supplied Section B material labelled pages 3-4. Questions repeatedly assess technical design, reflective process, evaluation, research quality, alternatives and future work; the mock also asks about inclusion and the September paper asks for a ten-minute presentation plan.

Created exam_preparation.md with a paper/question topic map, project-specific answer outlines, current versus planned architecture, recorded trial results, three incidents, process improvements, research/inclusion gaps, a presentation outline and revision priorities. Cross-checked current engine/interpreter and saved results. Historical exam rules are not represented as this year's rules. No tests or model experiments were rerun, and no application code changed. The guide explicitly distinguishes the 8/8 tuned combined-policy result from general model accuracy and retains unresolved looking/knocking failures. Personal knowledge, reading and backup practices require the student's own truthful detail.

## 20. Paper-by-paper completed-project answer PDF (14 September 2026)

At the user's request, reread the three PDFs now in exams: Example Exam, mock exam, and CM3070-ZB-Mar26. The folder contents differ from the previous preparation step; the March 2026 paper replaces the earlier 2024 papers for this output. Created exam_completed_project_answers.md and the new 21-page exam_completed_project_answers.pdf, preserving the earlier guide.

The document contains all 13 available questions and 36 answer blocks, including each subpart, with explicit paper start/end markers. It adopts the agreed completed-project scenario as requested, while marking unknown final measurements, personal experiences and reading as placeholders. It does not invent final comparisons, user-study findings or completed accessibility verification. The March learning-analytics case is answered as its own hypothetical case before relating the evaluation lesson to the adventure.

Generated the PDF with existing Pandoc and headless Edge; no dependencies installed. Checked question/answer and boundary counts, PDF completion and 21-page count, and visually inspected rendered pages 2 and 20 using Windows PDF rendering. Supporting primary sources were consulted for diffusion and inclusive-design explanations; course-specific terminology is flagged for alignment with teaching material. No application changes or model runs occurred.

## 21. Exam answers aligned with required readings (14 September 2026)

The user supplied seven required course readings and requested checking links and revising answers as needed. Checked MTF Open Minds, Riede et al., Cornell, and the digitally-disadvantaged languages PDF directly; used publisher alternatives for the university discovery links and inaccessible O'Reilly institutional redirect. Accessible coverage varies: Vehovar publisher text, MTF/Cornell pages and the language PDF; Riede abstract; Gilbert overview/contents; Lazar 2023 abstract. Full subscription-book/chapter access is not claimed.

Updated exam_completed_project_answers.md and regenerated its PDF (24 pages). Revisions ground radical inclusion in disabling environments, early participation and barriers to participation; distinguish Lazar's born-accessible framework from retrofitting; connect social informatics, linguistic exclusion and sustainability to the project; and qualify transfer of healthcare methodology to gaming. Added a seven-source access/reference table. Retained completed-project conditional framing and final-evidence placeholders; required reading is not represented as proof of actual co-design, multilingual evaluation or energy measurements. Verified all 13 questions, 36 answers and three paper boundary pairs remain. No application code or model runs changed.

## 22. Marker-expectation summary (14 September 2026)

At the user's request, reread spec.md and created project_scope.md. The summary distinguishes core outcomes, model investigation/evaluation expectations, grade-level descriptions, practical evidence suggestions and requirements the template does not prescribe. It explicitly identifies model comparisons and software testing as central, without inventing mark weightings or mandatory candidate/participant counts. A final section applies the expectations to the adventure while keeping project choices separate from university instructions. No application or experiment status changed.

## 23. Project-specific technical work mapping (14 September 2026)

At the user's request, appended "Project Technical Work" to project_scope.md. Its nine subsections map the specification-summary areas to general adventure tasks: problem definition, model investigation, selection, data preparation, orchestration, model evaluation, performance, software engineering and evaluation process. These are work descriptions rather than new completion claims; tasks.md remains the status tracker. No implementation or model experiments changed.

## 24. World contract accepted for continued work (21 September 2026)

The user accepted proceeding with the reviewed five-room design for now. Updated world_spec.md to working contract v2. Rescue requires beacon alignment (and therefore power and manual knowledge); shelter requires power and presence in the telescope chamber only. The key remains necessary to reach that chamber through the library. Added three draft regression cases for the distinct ending prerequisites and updated the shelter intent example. Marked only the accepted rule/action design tasks complete; added independent complexity/difficulty labelling to fixture preparation. Full schemas, executable fixtures, comparisons and game implementation remain outstanding. No model runs or application code changes occurred.

## 25. Structured development fixtures (21 September 2026)

With user approval, created evaluation/development.json containing 53 cases: 24 state/action expectations, 20 intent cases and nine matched state/language controls. Added strict schemas, legal setup traces, full expected states, required facts and forbidden claims in observatory/fixtures.py, plus a reproducible builder and tests. Both ending prerequisites and the user's looking/knocking failures are included. State complexity uses true-flag counts; language categories are independent, and the rubric's limitations are documented in evaluation/README.md.

Validation initially found that the moderate matched controls used a key-carrying state with only one true flag, which the rubric classifies as simple. Changed those controls to the unlocked-door state with two flags. Final software test result: 39 passed in 0.20 seconds. The environment's Python launcher required execution outside the restricted sandbox; no dependency installation was needed.

The reference transition rules support fixture validation only; the production engine remains the entrance-hall prototype. Generation and validation share reference logic, so passing these tests is not independent full-world verification or evidence of model accuracy. No models were run. All cases are development material; held-out data, image/speech execution and a model comparison runner remain future work. Updated only the completed fixture checklist entries in tasks.md.

## 26. Language-model intent evaluation runner (21 September 2026)

With user approval, implemented observatory/evaluate_intent.py and tests/test_evaluate_intent.py. The runner supports interchangeable installed Ollama model names, strict full-world predictions, projected player context, exact intent scoring and separate reference outcome/state checks. Local prototype guards are bypassed so this evaluates model-only interpretation. Gameplay remains unchanged. Expected labels and setup traces are excluded from prompts.

Runs save a dataset hash, model inventory/runtime metadata, exact requests, raw responses, errors, per-request timing and summaries by state complexity and language category. Each result is flushed immediately; partial runs are labelled. Timeouts, HTTP failures, incomplete output and invalid pairs count as failed attempts while subsequent cases continue. A regression test demonstrates that matching a rejected transition does not imply the model understood the intended action.

Validation: 51 software tests passed in 0.30 seconds, using simulated HTTP responses for the new runner. No model inference, downloads or comparative accuracy claims were made. README documents commands, denominators, cold-loading timing, shared-reference limitations, ignored evidence files and remaining narrative/resource-measurement work. Next step is a separately approved Qwen3:4b baseline run and review, then the same protocol for a feasible alternative.

## 27. First baseline attempt: connection failure (21 September 2026)

Reviewed the user-run evaluation in generated/intent-evaluations/20260921T185227660367Z-a40f3b1e. All 53 attempts failed with ConnectError / Windows error 10061 (connection actively refused); runtime and model inventory requests failed too. No model predictions were obtained, including the looking/knocking regressions. The summary's zero accuracy and approximately 2.05-second mean describe failed connection attempts, not Qwen reasoning accuracy or inference latency. This run is infrastructure-failure evidence only. Next action: start the local Ollama service, verify connectivity with a short run, then repeat the full baseline. A future runner improvement is a connectivity preflight that stops before attempting all fixtures when the service is unavailable. No model or application changes were made during this review.

## 28. First completed Qwen intent baseline reviewed (21 September 2026)

Reviewed user-run generated/intent-evaluations/20260921T190437752241Z-99ecb710. Ollama 0.34.2 reported qwen3:4b, 4.0B Q4_K_M, digest 359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7. All 53 requests returned structurally valid predictions with no runtime errors. Exact intent and reference-transition agreement were both 20/53 (37.7%). State groups: simple 14/30, moderate 4/11, complex 2/12; different action mixes prevent attributing the difference to state complexity alone. Language groups: direct 11/31, paraphrase 0/11, ambiguous 5/6, compound 0/1, unsupported 3/3, adversarial 1/1.

Of 33 incorrect interpretations, 24 were false unsupported responses, eight were false clarification responses, and one selected inspecting the desk from a compound request. Looking (I01) and knocking (I06) passed this evaluation prompt, which does not establish that the unchanged gameplay interpreter is fixed. Clear supported requests such as collecting the spare fuse and starting the generator were incorrectly rejected. Mean wall time was 0.414 seconds and median 0.244 seconds; the first response included approximately 8.165 seconds of model loading, so the mean is not a warm-inference measure.

This is a development baseline for the current prompt/configuration, not a general assessment of Qwen capability. Preserve it before changes. Recommended next step is inspection of prompt/schema and repeated-case consistency, then a controlled prompt revision or alternative-model comparison under the same baseline protocol. No additional inference, tuning or code changes were performed in this review.

## 29. Baseline audit and controlled prompt revision (21 September 2026)

With approval to take the next step, inspected the evaluator and saved baseline requests/raw responses. The schema permits strings but checks canonical pairs after generation; every baseline response passed validation, so schema validity alone does not explain the semantic failures. Five identical-request pairs exist; S06/I04 produced different predictions for the same unlocking request and state. This confirms a repeatability limitation but does not identify its runtime cause.

Added explicit --prompt-version v1/v2 selection, retaining v1 as the default and preserving prior results. V2 changes only the system prompt: stronger separation of intent from feasibility, explicit synonyms, and ordered rules for unsupported versus ambiguous requests. Schema, context, cases and generation settings stay fixed, allowing a prompt-only comparison. No case-specific expected labels are injected. This is development-informed tuning, not held-out validation.

Software validation: 53 tests passed in 0.36 seconds, including prompt-only request differences and version metadata persistence with simulated responses. No new model inference was performed. Next: user runs v2 and supplies its result folder; repeated runs of both versions are needed to assess stability before strong improvement claims. Gameplay interpreter remains unchanged.

## 30. Prompt v2 regression measured (21 September 2026)

Reviewed user-run generated/intent-evaluations/20260921T194922346849Z-8c451222 against the first completed v1 baseline. Dataset SHA-256, model name, runtime version and thinking-disabled configuration match. V2 returned structurally valid responses for all 53 cases with no runtime errors, but exact intent accuracy fell from 20/53 (37.7%) to 4/53 (7.5%). There were 16 formerly correct cases now incorrect and no newly correct cases. Predictions were unsupported in 52 cases and clarify in one; no action was predicted. The four correct cases were the three unsupported mechanics and the adversarial request. Knocking passed only as part of this near-universal rejection pattern, while looking regressed.

Median response time was 0.245 seconds (v1: 0.244 seconds); mean was 0.336 seconds (v1: 0.414 seconds), but loading differences prevent treating the mean difference as a reliable inference-speed improvement. All five duplicate-request pairs agreed in this run, which does not establish general repeatability. V2 is not an improvement and should not replace v1 as the default. Preserve both runs as development evidence. Next recommended investigation is a small diagnostic of the model/runtime and structured-output configuration using clear actions, changing one variable at a time before further prompt expansion or a full comparison. No new inference or code edits were performed in this review.

## 31. Paired structured-output diagnostic (21 September 2026)

With explicit user approval, added and executed scripts/diagnose_intent.py against local qwen3:4b. Saved raw requests/responses, runtime/model metadata and summary in generated/intent-diagnostics/20260921T201250Z-1a0a592d. Used four development cases (I01 looking, S16 starting the generator, I06 knocking, I09 ambiguous reference), both prompts, schema versus no format constraint, and two repetitions with mode order reversed: 32 requests total. Generation settings stayed at temperature 0, seed 42, context 4096, prediction limit 180, think false. Both modes received the same additional explicit instruction describing JSON keys and values, making these diagnostic prompts different from the original baselines.

Results: v1 plus explicit output instruction with schema scored 8/8, v2 plus the same instruction with schema 6/8. V2 consistently mapped the ambiguous 'Examine it' to inspecting the desk. All 16 unconstrained responses reached the token limit and failed completion checks; an inspected raw response contained explanatory prose despite thinking being disabled. No inference failures were silently converted into supported/unsupported labels.

The diagnostic does not support removing structured output under the current token budget. The additional explicit output instruction is a promising candidate for full-set testing with v1, but these four selected cases repeated twice cannot establish general accuracy or prove the cause of earlier collapse. An unchanged-prompt repeat would be needed to separate prompt improvement from runtime variation. Original prompts, baseline evidence and gameplay code remain unchanged. Next proposed experiment: compare unchanged v1 and v1 with the explicit output instruction on the full development set, preserving identical settings and reporting repeatability.

## 32. Full-set explicit JSON instruction comparison (21 September 2026)

Reviewed user-run 20260921T201619790279Z-3c77b1fb (unchanged v1) and 20260921T201645349662Z-21f0724d (v1-explicit-json) under generated/intent-evaluations. Both report qwen3:4b, Ollama 0.34.2 and the same development dataset hash. Original v1 scored 22/53 (41.5%), compared with 20/53 in its first run. V1 with the explicit JSON instruction scored 49/53 (92.5%): 29 cases improved relative to the immediate control and two regressed. Both runs had 53/53 structurally valid responses and zero runtime errors. Mean/median seconds: control 0.228/0.218; revised 0.236/0.237. All five identical-request pairs agreed within each run.

The revised prompt passed all 31 direct, 11 paraphrase, three unsupported and one adversarial cases, plus three of six ambiguous cases. Four errors remain: I10 compound search-and-take selected inspect_desk; I11 desk-or-toolbox selected inspect_desk; I12 unspecified use-key selected unlock_library; M-complex-ambiguous 'Examine it' selected look_around. I11 and M-complex-ambiguous were regressions from the immediate control. Looking and knocking regression cases both passed.

This is encouraging full-development-set evidence for clearer output instructions, not held-out accuracy or a proven general solution. The successful instruction was inserted before the canonical catalogue by the user's one-off command; the earlier small diagnostic appended it after the catalogue, so those prompt strings are not identical. Preserve the exact recorded requests. The variant is not yet a built-in runner option or integrated into gameplay. Recommended next step is to preserve it as a named reproducible candidate, then compare a second language model with the same cases and settings before further case-specific tuning. No model runs or gameplay changes occurred during review.

## 33. Successful prompt preserved as a permanent option (21 September 2026)

With user approval, added v1-json to the runner's prompt registry using the exact wording, position and manifest identity of the successful one-off run. Compared generated request objects against every saved request in 20260921T201645349662Z-21f0724d: all 53 matched exactly. Existing software tests: 53 passed in 0.28 seconds. Kept the original default and gameplay interpreter unchanged; documented explicit comparison commands.

Checked the official Ollama gemma3:4b page for the user-managed alternative download (approximately 3.3 GB, Q4_K_M). Provided its source and pull command. Honoured the user's explicit instruction not to download: no models downloaded and no inference performed. Gemma evaluation remains outstanding.

## 34. Gemma versus Qwen intent comparison reviewed (21 September 2026)

Reviewed user-run generated/intent-evaluations/20260921T202828708231Z-c881d93b. Gemma3:4b (4.3B Q4_K_M, digest a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a) used Ollama 0.34.2, the v1-explicit-json prompt and the same development dataset. Correct interpretations: 42/53 (79.2%) versus Qwen's 49/53 (92.5%). Gemma produced 43/53 contract-valid responses, with ten validation failures caused by clarify responses containing non-null action/target fields. Its remaining valid-but-wrong prediction interpreted unspecified 'Use the key' as unlocking. Validation failures are output-contract errors, not connection failures.

Gemma passed 30/31 direct, 8/11 paraphrase, 0/6 ambiguous, 0/1 compound, 3/3 unsupported and 1/1 adversarial cases. Mean/median latency was 0.494/0.374 seconds versus Qwen's 0.236/0.237 seconds. Gemma's first request included about 6.274 seconds of model loading; mean timings are not a controlled warm-speed comparison. Looking and knocking passed. Recorded requests were compared to the Qwen run to verify consistent settings apart from model identity.

These development runs favour retaining Qwen as the provisional intent model under this configuration. The prompt was tuned using Qwen development results, so this is a shared-prompt comparison rather than equal per-model tuning or a universal ranking. Neither model's narration quality has been compared here. No new inference or implementation changes occurred during review. Next work should address clarification/compound safety and continue the planned narrative/model integration work, preserving held-out evaluation for final assessment.

## 35. Clarification-rule experiment (21 September 2026)

With user approval to address the remaining failures, added a separately versioned v1-clarify prompt. It adds a general priority rule for multiple actions, alternative targets, unresolved references and instruments without explicit targets, while retaining the JSON instruction, output schema, fixture set and model settings. No exact fixture-answer lookup or local guard was added.

Executed a full local Qwen trial saved in generated/intent-evaluations/20260921T204705208867Z-77b90347. Result: 48/53 correct (90.6%), compared with the prior v1-json result of 49/53. All four prior failures persisted (I10, I11, I12, M-complex-ambiguous); I07 dropping the key also failed. This experiment did not solve the intended problem and is not promoted. The v1-json configuration remains available unchanged as the preferred measured candidate. Software tests: 55 passed in 0.31 seconds, including checks that prompt variants alter only the system message.

The remaining risk is that a model-selected action may be mechanically legal but not express the user's intention. Further prompt expansion is not currently supported by evidence. Before gameplay integration, consider a separately evaluated interpretation/confirmation safeguard with explicit reporting of model-only versus combined-system results; avoid claiming regex guards or this unsuccessful prompt solve arbitrary ambiguity. No gameplay changes or final-model selection occurred.

## 36. Typed-action confirmation safeguard (21 September 2026)

Implemented the requested safeguard in the entrance-hall gameplay path. Before applying a legal typed action, the terminal displayed its interpreted action label and canonical target and requested explicit y/yes approval. Blank, negative and unrecognised replies cancelled the action and preserved the original state. EOF or keyboard interruption during confirmation closed the game without applying the proposal. Numbered engine-approved choices remained direct selections. The handler required a confirmation callback and failed closed when none was supplied; it interpreted each request once and applied only the displayed proposal after approval. Existing schema and prerequisite checks rejected invalid or unavailable actions before confirmation.

Used the saved V1-JSON Qwen run (generated/intent-evaluations/20260921T201645349662Z-21f0724d, 49/53 correct, 92.5%) as context. Its compound/ambiguous failures showed why a mechanically legal action still needed player review. Confirmation did not repair the underlying predictions and could not prevent a player from approving an incorrect interpretation. The gameplay prompt and guards remained distinct from the full-world model-only evaluation. No model downloads or inference runs occurred, and the evaluator's scoring and prompt configuration were not changed by this safeguard.

Added tests for approval, all three state-changing actions on cancellation, absent confirmation, invalid replies, preview timing, single inference, rejected predictions, the looking/knocking substitution regressions, terminal interruption and numbered choices. Added an evaluation regression proving that a compound request incorrectly mapped to desk inspection still counted as a model-only error without gameplay confirmation. Validation: 100 tests passed in 1.50 seconds with simulated model responses. The Windows Python launcher could not start within the sandbox; the same test command succeeded with approved execution outside it.

Updated tasks.md to record this bounded safeguard and the already-reviewed intent baseline evidence. Browser/full-world confirmation and measurement of player correction/cancellation remain outstanding. These software checks are not new model accuracy or usability evidence.

## 37. Reserved intent evaluation data (22 September 2026)

Implemented the next preparation step before further tuning: reserved 30 intent cases in evaluation/held_out_intent.json, with version, timestamp, SHA-256, provenance and release conditions in evaluation/held_out_intent_reservation.json. Covered all 13 action IDs, both ending actions, six language categories and three state-complexity groups. Counts: seven direct, seven paraphrase, four each ambiguous/compound/unsupported/adversarial; 13 simple, eight moderate and nine complex states. Included new wording and some new visible state combinations within the accepted world.

Added observatory/held_out.py for offline contract, hash and split-separation validation and scripts/reserve_intent_fixtures.py for one-time authoring without overwrite. Kept the development loader and model-only evaluator unchanged: the held_out split was rejected before any network call or result-directory creation. Recorded a final-release protocol requiring frozen models/prompts/settings/scoring and separate authorisation before inference. Documented retirement to development if reserved cases inform tuning.

Labels were assistant-authored after the initial development experiments using world_spec v2 and shared reference transitions. They were not obtained from model outputs, independently human-reviewed or authored blind to known failure categories. The reservation therefore supports later testing of new inputs, not a claim of new mechanics or independent annotation quality. Human annotation review and separate media holdouts remain outstanding. No gameplay, model prompt or scoring changes were made; no models were downloaded or run.

Validation: 108 software tests passed in 0.73 seconds. New checks covered action/category/state coverage, genuinely different visible contexts, rejection of reserved data by the development runner before network access, hash tampering, overlapping IDs/normalised wording and overwrite prevention. Windows Python commands ran outside the sandbox through the approved launcher. Added targeted Git ignore exceptions for development_log.md, tasks.md and evaluation/README.md, and disabled line-ending conversion for the hashed dataset so these deliverables can be preserved in a later user-managed commit. No commit or push occurred.

Next: prepare shared narrative, illustration and speech comparison fixtures and written rubrics, then seek authorisation for new model experiments. Keep this reserved intent set out of those development trials.

## 38. Shared media development fixtures and scoring protocol (22 September 2026)

Implemented the authorised preparation step: evaluation/media_development.json now contains 16 narrative cases referencing verified development state/action outcomes, five room illustration prompts and ten exact speech passages. Added observatory/media_fixtures.py with strict schemas, offline validation, public post-action projection and structural narrative checks; scripts/build_media_fixtures.py reproduces the inputs without overwriting existing files. No held-out intent file was edited or used to author media cases.

Narrative coverage includes all rooms, discoveries and inventory changes, rejected prerequisites, repeated collection and both endings. Model inputs contain verified public facts, inventory, action/outcome, allowed suggestion pairs and a visual brief ID. Review checklists stay outside model input. Exact suggestion sets, duplicate suggestions, brief identity and 60-100-word successful descriptions are checked structurally; short rejected/unchanged messages are permitted. Semantic correctness remains explicitly pending human review.

Adapted the existing media drafts to the accepted world, correcting the contradictory landscape/512x512 wording to a square trial canvas, preserving toolbox closure and including both endings in speech. Kept the earlier standalone feasibility scripts unchanged because their lantern and other historical scene facts differ from this contract. They are not yet comparison runners for these fixtures.

Added evaluation/media_protocol.md with narrative required-fact/contradiction scoring, image detail and style checks, speech transcription/pronunciation criteria, anchored human ratings, evidence fields and timing/failure rules. Proposed repeated trials were documented, not executed or treated as an approved model-run budget. The protocol separates structural success from semantic correctness, raw model output from fallback behaviour, cold/loading from warm inference and pending ratings from actual results. Independent review and separate media holdouts remain outstanding.

Validation: 128 software tests passed in 1.45 seconds, including fixture reproducibility, five-room/ending coverage, hidden-fact projection, corrupted references, changed inventory/outcomes, duplicate IDs, exact suggestions, word-count boundaries and pending semantic review. The tests used no model inference. The offline builder and tests used the approved Windows Python launcher outside the sandbox. Updated tasks.md, evaluation/README.md and the source draft; added targeted Git exceptions so the new protocol and source notes can be included in a later user-managed commit. No model downloads, new inference, gameplay integration, commit or push occurred.

Next proposed implementation: a configurable narrative comparison runner consuming these inputs, preserving raw outputs and human-review fields; then review settings and obtain approval for a Qwen/Gemma narrative trial. Image/speech adapters and trials follow the same protocol. These fixtures and software tests are preparation, not measured model-selection evidence.

## 39. Configurable narrative comparison runner (22 September 2026)

Implemented the authorised runner in observatory/evaluate_narrative.py against the 16 shared media narrative cases. Each candidate received the same post-action input, schema and initial world-v2-narrative-eval-v1 prompt. Defaults were documented as temperature 0.3, context 4096, output budget 600, thinking disabled, timeout 180 seconds and two repetitions with seeds 42/43. Candidate order reversed on alternate repetitions; model names were explicit CLI arguments. These settings were implementation defaults, not measured optimal settings or authorisation to run an experiment.

Saved exact requests before inference, raw responses/content/errors, completion and structural checks, available Ollama metrics, model/runtime inventory metadata, environment, dataset/protocol snapshots and hashes, and the complete planned schedule. Flushed each result immediately. Added pending human-review records for required facts, forbidden claims, contradiction/addition evidence and readability. Summary scores covered recorded attempts including failures, with semantic scores left null; no automated truth claim or human-review aggregation was added. Interrupted runs retained completed rows, pending request evidence and an explicitly partial summary.

Kept evaluation independent of gameplay and intent scoring, with no retries, fallback substitution or best-output selection. Runtime timing fields retained raw units and absent values remained null; first-in-block and later-in-block wall times were separated without assuming cold/warm status. RAM/VRAM sampling and candidate compatibility remained unverified. Image/speech comparison adapters and review aggregation remained outstanding.

Validation: 150 software tests passed in 1.03 seconds using simulated HTTP responses. Tests covered equivalent candidate requests, exclusion of review labels, model-only boundaries, output-contract failures, timeouts, HTTP/malformed responses, truncation, error denominators, reversed scheduling, seed changes, pending reviews, metadata failures, interruption recovery and rejection of invalid configurations/dataset splits before network access. The approved Windows launcher ran the offline tests outside the sandbox. No model inference, downloads, gameplay changes, commit or push occurred. Updated tasks.md, evaluation/README.md and media_protocol.md with settings, commands and evidence limitations.

Next: review the proposed 64-request Qwen/Gemma comparison (or a separately labelled two-request compatibility check), then obtain authorisation before running models. Structural results must be followed by human factuality/readability review before model-selection claims.

## 40. User-run narrative compatibility check reviewed (22 September 2026)

Reviewed generated/narrative-evaluations/20260922T120510452882Z-8a9118f4: one N01 request per candidate, seed 42, narrative-eval-v1, Ollama 0.34.2. Both completed with stop rather than token-limit termination, valid schemas and correct visual brief IDs; there were no HTTP/runtime errors. Qwen returned 40 description words and all three expected suggestions. Gemma returned 47 words and an empty suggestion list. Both failed the 60-word minimum; Gemma additionally failed exact suggestions. Neither failure showed an exhausted 600-token budget (reported output token counts: Qwen 137, Gemma 75).

Assistant inspection found Qwen's short prose consistent with the supplied facts without revealing the key or changing state. Gemma preserved the locked door and empty inventory but invented an eastward direction for the workshop passage, which the input did not specify. This is an assistant observation, not completed independent human annotation; saved review files and semantic scores remained pending. Wall times were approximately 1.084 and 0.669 seconds respectively, with substantial prompt-cache reuse reported in raw responses; two short outputs do not establish a speed or quality ranking.

The compatibility check established that both runtimes accepted and completed this request configuration, not that their outputs met the narrative contract. Recommended next: preserve the prompt/settings and run the full 64-request development baseline before tuning from one case. The user will run all model experiments; provide commands and request the saved folder path/errors. No inference, downloads, code changes or test reruns were performed during this review.

## 41. Full narrative development baseline reviewed (22 September 2026)

Reviewed the user-run generated/narrative-evaluations/20260922T121539136759Z-55b7d9bd: 64 completed requests, 16 cases per model over two repetitions/seeds 42 and 43, reversed candidate order, narrative-eval-v1 and Ollama 0.34.2. Dataset hash matched the compatibility check. Neither model hit the output limit or returned a runtime failure. The ten recorded errors were action/target contract validation failures, five per candidate, rather than connection failures.

Qwen: schema 27/32, exact suggestions 27/32, correct visual brief 26/32, length check 7/32, complete structural pass 7/32 (21.9%). Gemma: schema 27/32, exact suggestions 5/32, correct visual brief 27/32, length check 13/32, complete structural pass 4/32 (12.5%). Component checks default to false when schema validation fails, so these are pipeline pass counts, not independent measurements of every description's length or brief. All seven Qwen structural successes were short rejected/unchanged cases; all four Gemma successes were the two endings repeated. These counts do not establish semantic accuracy.

Assistant inspection identified material factual failures: Qwen A0010 and Gemma A0026/A0042 described a running generator immediately after fuse installation, contrary to the supplied stopped-generator facts. Both described the library door opening after unlocking despite the closed-door contract (Qwen A0006/A0054; Gemma A0022/A0038). Qwen A0063 claimed daylight restored power and that the carried library key was absent. Gemma added unsupported fuse amperage, control messages and lighting; its structurally passing A0046 described rescue vehicles visible through an opening in the explicitly enclosed dome. Qwen also omitted important outcome explanations in some short structural passes. These are assistant review observations; per-attempt human review forms and semantic scores remain pending, not completed independent annotation.

Mean/median wall seconds were Qwen 1.244/1.129 and Gemma 1.138/0.912. Loading, different output lengths and two samples per case prevent a strong speed comparison. Maximum reported output token counts were 172 and 140 respectively against a 600-token allowance: no evidence supported increasing that allowance as a fix for short prose.

Preserved the baseline and recommended a separately versioned, controlled narrative prompt improvement targeting outcome fidelity, explicit non-effects and length, rather than accepting these outputs for gameplay or weakening scores after seeing failures. Deterministic copying of suggestions/brief IDs is a possible later orchestration design choice, but must remain separate from raw-model baseline scoring. No prompt/code changes, model runs, downloads or test reruns occurred during this review. The user continues to execute all model experiments from supplied commands. Final model selection and systematic human narrative scoring remain outstanding.

## 42. Controlled narrative prompt revision (22 September 2026)

Implemented the authorised single revision as --prompt-version v2 (world-v2-narrative-eval-v2) in observatory/evaluate_narrative.py. Kept v1 as the default. The revised system prompt prioritised the actual verified outcome, preservation of negative/unchanged facts and inventory, separation of discoveries from possession, and avoidance of inferred next puzzle steps. It requested approximately 80 words within the existing 60-100 range for successful scenes, while retaining concise rejected/unchanged messages. No case-ID lookup or review checklist was inserted into model inputs.

The prompt registry and CLI recorded the selected prompt identity and exact text in each run. Fixtures, schema, model settings, seeds, schedules, output limits and scoring stayed unchanged; suggestions and visual brief IDs were still evaluated as model outputs. This was development-informed prompt tuning, not a factuality guarantee or a gameplay fallback implementation. The original saved baseline remained comparison evidence.

Validation: 153 software tests passed in 1.48 seconds with simulated responses. Added checks that v2 changes only the system message across all 16 cases, two candidate names and both seeds, that v1 remains default, that the selected prompt is saved and sent, and that unknown versions fail before output creation. Updated tasks.md and evaluation/README.md with the user-run comparison command and limitations. No model inference, downloads, commit or push occurred. Next: the user runs v2 and supplies the results path; assess factual failures as well as structural counts before any adoption. Do not continue prompt tuning indefinitely if this controlled revision fails.

## 43. Narrative v2 comparison reviewed (22 September 2026)

Reviewed user-run generated/narrative-evaluations/20260922T134438589698Z-50579097 against v1 run 20260922T121539136759Z-55b7d9bd. Dataset hash, generation options, schedule and saved model inventory metadata matched; both used Ollama 0.34.2 and completed 64 requests. V2 was the selected prompt. No runtime failures occurred; the two errors were Qwen action/target validation failures.

Qwen structural passes increased from 7/32 to 14/32 (21.9% to 43.8%), with seven newly passing attempts and no previously passing attempts lost. Schema/exact suggestions improved from 27/32 to 30/32. Gemma structural passes fell from 4/32 to 1/32 (12.5% to 3.1%): one gain and four losses. Its schema improved from 27/32 to 32/32 and exact suggestions from 5/32 to 11/32, but length passes fell from 13/32 to 3/32 as descriptions commonly exceeded 100 words. Schema-failed attempts still default other checks to false; component counts are pipeline results, not independent semantic measures.

Assistant inspection showed the targeted factual failures remained. Qwen A0010 correctly retained the stopped generator after installation, but A0058 claimed it started and then also said it was stopped; A0058 passed all structural checks. Both Qwen unlocking samples still opened the closed door, and A0003 newly unlocked it during collection. Many Qwen outputs changed to first person despite the second-person instruction. Gemma still started the generator after fuse installation, invented malfunctions for rejected actions, and auto-collected/unlocked during discovery or collection. Its only structural pass, A0035, incorrectly unlocked/opened the door while collecting the key. Therefore better schema/structural scores did not establish factual safety. These are assistant observations, not completed independent human ratings; review files and semantic scores remain pending.

Mean/median wall seconds were Qwen 1.358/1.189 and Gemma 1.786/1.609, versus v1 1.244/1.129 and 1.138/0.912. Longer prompts/prose and loading/cache variation prevent isolating a model-speed effect. V2 showed a Qwen structural improvement and a Gemma regression in these development runs, not a general model ranking or a solved narration problem.

Kept both prompt versions and the v1 default unchanged. Recommended stopping further prompt expansion after this authorised revision and planning bounded gameplay narrative validation/factual fallback, with engine-owned suggestions and illustration IDs. Such structural ownership would remove copying failures from gameplay, not retroactively improve model-only scores. Factual checks must disclose their limits; arbitrary prose truth cannot be guaranteed by schema or simple keyword rules. No code/prompt changes, model runs, downloads or test reruns occurred during review. Updated tasks.md; next implementation requires user authorisation, and model experiments remain user-run.

## 44. Three additional language candidates checked (22 September 2026)

Reviewed the user-run narrative compatibility check in generated/narrative-evaluations/20260922T200559373288Z-421f7bc8. Llama3.2:3b, Phi4-mini:3.8b and Granite3.3:2b each completed N01 with narrative v2, seed 42, Ollama 0.34.2 and the existing shared settings. All three returned valid contracts, exact suggestions and correct brief IDs without runtime errors. Llama wrote 55 words and Phi 57, failing only the minimum length; Granite wrote 62 and passed structure.

Assistant prose inspection found no obvious state contradiction in the Llama or Phi samples. Granite claimed the area was dark despite the supplied diffuse daylight and used the inconsistent phrase 'generator hums lifelessly' for a stopped generator. Structural success therefore did not establish semantic superiority. Human-review records remain pending. Wall times were approximately 6.157, 5.040 and 3.995 seconds, including reported model loading of 5.066, 3.796 and 2.777 seconds respectively; these are not warm-inference speed comparisons.

These three candidates now have one-case compatibility evidence, not full narrative or intent comparisons. Recommended the user run the unchanged full narrative v2 suite for all three (96 requests) before drawing model-selection conclusions. No model runs, downloads, code changes or test reruns occurred during this review. The expanded five-candidates-per-data-space goal is evaluation scope; image/speech candidate testing remains outstanding.

## 45. Expanded language narrative comparison reviewed (22 September 2026)

Reviewed user-run generated/narrative-evaluations/20260922T200831838642Z-53330a53: 96 completed requests, 16 narrative cases twice per candidate, no runtime failures. Shared dataset hash, exact v2 prompt, schema and generation settings matched the earlier Qwen/Gemma v2 comparison; both used Ollama 0.34.2. Candidate runs occurred in separate sessions, so timing is not a controlled five-model benchmark.

Structural passes: Granite3.3:2b 18/32 (56.3%), Llama3.2:3b 17/32 (53.1%), Phi4-mini:3.8b 16/32 (50.0%). Earlier v2 results were Qwen 14/32 (43.8%) and Gemma 1/32 (3.1%). Granite and Phi each had 32/32 valid schemas, 24/32 exact suggestions and 32/32 correct brief IDs. Llama had 28/32 valid schemas/exact suggestions and 26/32 correct brief IDs; its four errors were invalid action/target contracts, including invented ending suggestions. Component checks remain gated by schema validation. No semantic pass rate has been measured.

Targeted assistant review of discovery, collection, unlocking, fuse installation and ending cases found factual failures in every new candidate. Llama A0090 passed structure while starting the generator immediately after installation; A0010 instead kept it stopped but invented an inaccessible workshop. Phi A0032 passed structure while inventing another person occupying the shelter bench as the rejection reason; its collection samples unlocked/opened the door. Granite likewise unlocked during collection, started the generator after installation and invented missing manuals and new shelter prerequisites. All three opened the library door during unlocking despite the closed-door contract. These examples prevent treating structural ranking as narrative quality or a final model-selection decision; systematic human review remains pending.

Mean/median wall seconds: Llama 0.944/0.927, Phi 1.148/1.150, Granite 0.998/1.002. Loading/cache and output-length differences limit comparisons to previous sessions. Five language candidates now have full narrative development trials, while only Qwen/Gemma have full intent results. Recommended next: user-run v1-json intent evaluations for Llama, Phi and Granite on the unchanged 53-case development set (159 requests total), then combine separate intent results and narrative review before selection. No models were run or downloaded by the assistant; no code changes or test reruns occurred during review.

## 46. Five-candidate intent comparison completed (22 September 2026)

Reviewed the three user-run intent folders, in command order: 20260922T201322393986Z-d70c9f9d (Llama3.2:3b), 20260922T201343273929Z-432f3af8 (Phi4-mini:3.8b), and 20260922T201407368129Z-0de4ecab (Granite3.3:2b). Each contained 53 development attempts with v1-explicit-json. Compared every saved request with the successful Qwen baseline, excluding only the model field: all matched for all three candidates and the earlier Gemma comparison. Thus prompts, cases, schema and requested generation settings were shared; this does not establish equivalent internal runtime behaviour or equal per-model tuning.

Exact intent results across five candidates: Qwen 49/53 (92.5%), Phi 48/53 (90.6%), Gemma 42/53 (79.2%), Llama 36/53 (67.9%), Granite 27/53 (50.9%). Contract-valid outputs: Qwen/Phi/Llama 53/53, Gemma 43/53, Granite 42/53. Llama's 17 mistakes were false unsupported classifications, including supported movement/endings and cases requiring clarification. Phi passed all 31 direct cases and five of six ambiguous cases, but misclassified the compound request, unspecified use-key, entering the library, shelter paraphrase and simple surroundings paraphrase. Granite combined false unsupported predictions with eleven output-contract validation failures and incorrect substitutions. No output-contract errors were relabelled as successful rejection.

All five failed the single compound fixture, with differing wrong responses. Phi handled more ambiguous cases than Qwen (5/6 versus 3/6), while Qwen handled all eleven paraphrases versus Phi's eight. The one-case overall difference is insufficient to declare a universal winner. These are small development samples with known duplicates, and the shared prompt was originally tuned using Qwen evidence. Preserved results are not held-out accuracy.

Qwen and Phi are reasonable provisional language finalists when considering intent alongside narrative evidence, but narrative structural scores do not establish factual correctness. Systematic human narrative review, hardware/resource evidence and final selection remain outstanding. Updated tasks.md to distinguish completed five-candidate model runs from unfinished semantic evaluation. No model runs, downloads, code changes or test reruns occurred during this review.

## 47. Systematic assistant review of language finalists (22 September 2026)

Reviewed all 64 saved v2 descriptions for Qwen (run 20260922T134438589698Z-50579097) and Phi (run 20260922T200831838642Z-53330a53), using the per-case required/forbidden facts, supplied post-action input and world contract. Recorded full annotations in evaluation/assistant_reviews/narrative_v2_finalists.json and a readable report in narrative_v2_finalists.md. Original model outputs, structural scores and pending human-review forms were not modified.

Assistant factual judgements: Qwen 14 pass, 10 fail, eight uncertain; Phi four pass, 23 fail, five uncertain. Outputs with definite violations: Qwen ten, Phi 21; Phi also had two required-fact failures without a definite invented claim. Only five Qwen and three Phi outputs passed both original structure and this review. Each entry records required-fact judgements, exact issue quotations, rationale and a readability rating; uncertain cases were not counted as passes. These are non-blind assistant annotations informed by development experience, not independent human ratings, model-evaluator scores or held-out accuracy.

Qwen was the stronger provisional finalist in this review, but still opened doors after unlocking, invented route closures and sometimes contradicted generator state. Phi additionally invented access prerequisites, a person occupying the shelter bench and key use on the signalling console. The report flagged borderline wording about opening a locked door with a carried key, daylight without power, exploration history and before/after socket state for developer judgement. Kept style preference separate from correctness.

The offline scripts/record_finalist_review.py materialised explicitly authored annotations, checked exact coverage of 32 samples per candidate, required-checklist lengths and the presence of every quoted excerpt in its source description, and recorded source hashes. It did not run models or classify prose automatically. Its assertions passed; no software test suite rerun was needed because gameplay/evaluator code was unchanged. Updated tasks.md and a targeted Git ignore exception for the review report. No downloads, model runs, commits or pushes occurred. Developer review, final selection and gameplay narrative safeguards remain outstanding.

## 48. Entrance-hall narrative validation and fallback (22 September 2026)

Following the user's instruction to do the next step, implemented the bounded gameplay safeguard in observatory/narrative.py and opt-in --narrate terminal mode. The separate developer-review question remained pending; no developer judgement or human rating was invented. Generated text is requested only after an accepted typed/numbered state change. Typed confirmation and engine prerequisites remain authoritative. Cancellation, clarification and rejected actions do not request narration.

Added a description-only model contract, canonical location/door/key sentences and conservative checks for known contradictory or unsupported wording, first-person prose and the existing 60-100-word range. Engine code supplies suggestions and the location supplies the illustration brief ID. Generation gets one attempt with a 30-second timeout; failures, invalid schema, incomplete output, interruption or failed checks select factual fallback text. The narrator cannot transition state; repeated rendering cannot duplicate an action. Scene text is retained across redraws until the next accepted change, including the final unlocked-door state.

Saved unique gameplay narrative logs containing prompt/policy identity, state, request, raw response, accepted source/text, validation reasons, deterministic scene metadata and wall time. The new hall-narrative-v1 prompt/policy is gameplay-specific; existing model-only evaluations and their results were unchanged. Exact fact anchors and conservative pattern checks may over-reject and cannot catch arbitrary invented facts. An explicit test demonstrates an unseen butterfly claim escaping checks; no claim of general semantic safety was made. No automatic generation retries or full-world/session-revision orchestration were added.

Validation: 182 tests passed in 3.05 seconds, using simulated responses only. Coverage included accepted text for each hall state, hidden-key protection, known door/power/inventory/entity violations, schema/HTTP/timeout/truncation/interruption fallback, immutable state under repeated rendering, unique logs, logging failure, confirmation gating and exactly one narration per numbered transition including completion. Tests used the approved Windows Python launcher outside the sandbox. Added gameplay_narration.md with the user-run command and limitations; updated tasks.md and Git visibility for the guide. No models were run or downloaded, and no commit or push occurred. Live narration and fallback-frequency measurement remain user-run future evaluation.

## 49. First guarded gameplay trace and false-rejection fix (22 September 2026)

Reviewed the user's terminal sequence and the three corresponding gameplay narrative logs (response times 20:35:55, 20:36:13 and 20:36:30 UTC). All three typed actions required confirmation and advanced the expected hall sequence, retaining the key and leaving the final door closed/unlocked. The user quit at the action prompt in an earlier launch; this trace did not exercise cancellation at the confirmation prompt. All three narrations used fallback. Generation completed normally; assistant inspection found no obvious factual contradiction in these three raw descriptions. All failed the 60-word minimum.

Found an implementation false rejection: collection/unlocking responses copied supplied scene facts about daylight, absent electricity and no rescue signal, but keyword checks treated those exact trusted sentences as prohibited claims. Fixed the validator to exempt whole sentences matching supplied scene facts as well as required anchors. Appended/modified contradictory claims remain checked. Incremented gameplay policy to hall-narrative-guards-v1.1; prompt and the 60-100-word requirement were unchanged. Old logs/results were preserved. These same three outputs would still fail length, so this fix does not establish a lower overall fallback rate.

Validation: 187 tests passed in 1.18 seconds, including exact supplied-fact acceptance and protection against contradictory additions. No models were run, and no downloads occurred. Live narrative quality and cancellation-at-confirmation testing remain outstanding. The results also show that this prompt often copies factual templates rather than producing varied prose; fallback correctness must not be presented as successful generative narration.

## 50. Cancellation evidence and image comparison preparation (22 September 2026)

Recorded the developer's supplied cancellation trace: typing inspect the desk and replying d at confirmation returned to the unchanged initial description, empty inventory and available inspect action. No narration request appeared. This is one manual developer test, not independent user evaluation; it complements the earlier confirmed-action/fallback trace.

Implemented observatory.evaluate_image, a model-only local stable-diffusion.cpp adapter separate from gameplay. Default preview performs no inference. Explicit --execute uses installed files only, the five unchanged media briefs, 512px canvas, seeds 42/43 and reversed candidate order on repetition two. The initial configuration retains the historical SDXL Turbo checkpoint/settings; other checkpoints require compatibility/settings review before activation. Every attempt starts a fresh CLI process. Saved evidence includes full schedule/requests, dataset/protocol snapshots and hashes, actual checkpoint/runtime/DLL hashes, verbose runtime logs, outputs, flushed failures and pending visual-review forms. No retries or fallback substitutions. PNG integrity checks and process completion remain distinct from visual correctness. Timeout/interruption preserve attempted failures; automatic resource peaks and separate load/inference timing are unavailable.

Updated the plan to five candidates per data space and preserved the image/speech shortlist with explicit untested-alternative status. Added image trial commands and Git visibility for the guide and candidate research; generated results remain ignored and require deliberate submission preservation. Read primary image model cards; current documentation does not establish installed pinned-runtime compatibility. No models were downloaded or run, no dependency was installed, and no commit/push occurred.

Validation: 200 offline tests passed in 1.77 seconds using fake subprocesses and synthetic PNG data. Coverage includes preview/no execution, shared prompts, schedule/seed order, duplicate configurations, missing files, successful file integrity, corrupt/truncated/wrong-sized output, nonzero exit, timeout, interruption and no retries. The Windows Python launcher required sandbox escalation for tests. Next: developer-run single-image SDXL Turbo smoke test, review actual output/logs, then full baseline and alternative preparation. This implementation is not a completed five-model image comparison or gameplay image integration.

## 51. Image adapter smoke test reviewed (22 September 2026)

Reviewed user-run generated/image-evaluations/20260922T205515942124Z-df846843. One SDXL Turbo entrance-hall attempt completed with exit code zero, PNG integrity passed at 512x512, and wall time was 11.880 seconds including process/model loading. The verbose log confirms Vulkan execution, sampling 6.84 seconds, VAE decode 0.97 seconds and generate_image 11.05 seconds. These overlapping/internal timings must not be summed or interpreted as warm inference latency. Reported backend buffers are not measured whole-system RAM/VRAM peaks.

Non-blind assistant visual inspection found a closed panelled door and the requested blue/wood palette, but no clearly visible dusty desk. High frosted glazing was unclear: bright window/skylight areas do not establish frosting. Additional bookshelves, framed decorations and a wall lamp appeared. No obvious person, visible key or readable door label was identified; this is not a guarantee that every small mark satisfies the lettering constraint. The missing desk prevents a content pass regardless of the successful file check. Original review forms remain pending for human annotation; no human ratings or cross-room coherence score were invented.

Compatibility succeeded; scene fidelity did not fully satisfy the brief. Recommended the unchanged ten-image SDXL Turbo baseline (five rooms, seeds 42/43) before prompt tuning or comparative conclusions. The one-case smoke test remains separate evidence. No model was run by the assistant, no downloads occurred, and no software tests were rerun for this documentation-only review.

## 52. Full SDXL Turbo development image baseline reviewed (22 September 2026)

Reviewed user-run generated/image-evaluations/20260922T205805515147Z-e8e9aa6f and viewed all ten images individually. Five rooms with seeds 42/43 completed successfully: 10/10 runtime completions and PNG integrity passes. Mean load-inclusive wall time was 13.388 seconds, range 13.082–13.862, total 133.884. Vulkan log identified the RX 7800 XT. This is fresh-process latency, not warm inference or peak-memory evidence. The seed-42 hall hash exactly matched the earlier smoke sample.

Saved a separately labelled non-blind assistant inspection in evaluation/assistant_reviews/image_sdxl_baseline.md. Both entrance halls lacked a clear desk; both libraries lacked the required stairway/reading-stand arrangement; telescope scenes did not clearly show attached beacon housing or benches. Workshop toolbox identity and generator details require human adjudication. Style/palette appeared consistent, but this cannot compensate for missing scene content. Pending human review forms were preserved; no numeric semantic pass rate, independent ratings or five-model ranking was invented. Recorded the runtime's default VAE scaling warning without attributing visual failures to it.

Next: prepare the second image candidate, SD-Turbo, checking exact artifact/licence and pinned-runtime settings before user-managed download/inference. Keep the current baseline unchanged for comparison. No model was run or downloaded by the assistant; this documentation-only review required no software test rerun.

## 53. Second image candidate prepared (22 September 2026)

Prepared evaluation/image_candidates_sd_turbo.json without changing SDXL defaults or baseline evidence. Verified the official SD-Turbo repository revision b261bac6fd2cf515557d5d0707481eafa0485ec2, approximately 5.21 GB single-file checkpoint and published SHA-256 3f067a1b943cf162f2b8f8588f6cf5824bd5b4c7d1d88d87164b9ca123616549. Recorded revision-specific Community License provenance and pinned-runtime documented SD-Turbo support. Documentation is not a successful local compatibility test.

Retained shared four-step, CFG 1, Euler/sgm_uniform, 512px settings and unchanged prompts/seeds for the initial smoke test. These are trial settings, not claimed optimal values. Added resumable user-managed download commands with hash verification, licence retention and a one-image run. Full baseline follows smoke review; separate sessions limit timing comparisons. No weights downloaded, models run, dependencies installed, commits or pushes performed by the assistant. Configuration validation uses offline preview; gameplay and evaluator source are unchanged.

## 54. SD-Turbo smoke test reviewed (22 September 2026)

Reviewed user-run generated/image-evaluations/20260922T211618420896Z-fb3ca221. The single entrance-hall attempt completed with exit code zero and passed 512x512 PNG integrity checks. Saved checkpoint SHA-256 matched the pinned published hash. Four-step Euler/sgm_uniform, CFG 1 execution succeeded through Vulkan. Load-inclusive wall time was 4.147 seconds; runtime sampling was 0.46 seconds and VAE decoding 0.61 seconds. This one separate-session sample is not a controlled speed comparison with SDXL or a whole-system resource measurement.

Non-blind assistant image inspection found a closed wooden door, bookshelves and muted grey/brown scenery. No clear high frosted glazing was visible. A partially cropped side table does not establish the required dusty desk. A plaque on the door contains text-like marks; readable words are unclear, so a readable-label violation was not asserted, but the no-lettering constraint needs human judgement. The smoke test establishes compatibility, not visual-content success. Original human review fields remain pending.

Recommended the unchanged ten-image SD-Turbo baseline on the same five briefs/seeds before drawing comparative conclusions. No model execution or downloads were performed by the assistant, and no software tests were rerun for this documentation-only review.

## 55. Full SD-Turbo image baseline reviewed (22 September 2026)

Reviewed user-run generated/image-evaluations/20260922T211752221105Z-757a7092 and viewed all ten images. Runtime and 512x512 PNG integrity both passed 10/10. Mean load-inclusive wall time was 3.004 seconds (2.909–3.308; total 30.036), compared with SDXL's 13.388-second mean in a separate session. Verified equal dataset/protocol hashes, scheduled prompts and seeds. These are descriptive timings, not a controlled warm-inference benchmark.

Saved per-image non-blind assistant observations in evaluation/assistant_reviews/image_sd_turbo_baseline.md. Missing/unclear desks, stairs, toolboxes and beacon housings persisted. Seed-43 hall visibly opened the door and added lettering; seed-43 telescope image was outdoors with open sky, violating its enclosed-dome brief. Other ambiguous panel markings and object identities were left for human judgement. No semantic pass rate or independent ratings were invented; original human review forms remain pending. The hall seed-42 hash matched the prior smoke result.

Two image candidates now have full shared development baselines. Neither is selected as a final winner. Proposed next: prepare SD 1.5 checkpoint/configuration and user-run smoke commands while keeping existing prompts/results unchanged. No models were executed or downloaded by the assistant, and no software test rerun was needed for this documentation-only review.

## 56. SD 1.5 comparison configuration prepared (23 September 2026)

Prepared separate evaluation/image_candidates_sd15.json for the third image candidate. Verified maintained repository revision 451f4fe16113bff5a5d2269ed5ad43b0592e9a14 and published SHA-256 6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa for the approximately 4.27 GB v1-5-pruned-emaonly.safetensors checkpoint. Repository metadata identifies CreativeML OpenRAIL-M. Added provenance and smoke instructions to evaluation/image_trials.md.

Predeclared project trial settings: 30 steps, CFG 7.5, Euler/discrete, unchanged 512px briefs and seeds. This differs deliberately from the distilled Turbo configurations; no claim of optimal tuning or equal-compute comparison is made. Existing baseline configurations and evidence remain unchanged. Offline preview validates configuration/schedule only; real runtime compatibility and visual results remain user-run. No model downloads, inference, dependencies, commits or pushes were performed.

## 57. SD 1.5 smoke test reviewed (23 September 2026)

Reviewed user-run generated/image-evaluations/20260923T105228086296Z-2ee0ad80. One entrance-hall image completed with exit code zero, valid 512x512 PNG integrity and matching published checkpoint SHA-256. The saved configuration used 30 steps, CFG 7.5, Euler/discrete; Vulkan execution succeeded. Load-inclusive wall time was 9.944 seconds. This is compatibility evidence, not a controlled speed comparison with the differently configured Turbo candidates.

Non-blind assistant visual inspection found a stylised blue panelled door and brown shelving/walls, but no clear dusty desk. High frosted glazing was not clearly identifiable; the upper shapes and small door panel are ambiguous. No obvious person or key was visible. This image does not establish full scene-content compliance. Human review fields remain pending. Recommended the unchanged ten-image SD 1.5 baseline before model comparison or tuning.

The earlier user-reported curl write failure occurred before this successful run; its exact cause was not established. No model downloads or inference were performed by the assistant. Documentation-only review required no software test rerun, commit or push.

## 58. Full SD 1.5 image baseline reviewed (23 September 2026)

Reviewed user-run generated/image-evaluations/20260923T105950381566Z-9838fd29 and individually viewed all ten images. Runtime completion and PNG integrity passed 10/10. Mean load-inclusive wall time was 13.886 seconds (range 13.360–14.976; total 138.857). Verified matching dataset/protocol hashes, exact prompts and seeds against SD-Turbo. The hall seed-42 hash matched the smoke output. Different sampling budgets/settings and separate sessions prevent controlled model-speed claims.

Saved non-blind assistant per-image notes in evaluation/assistant_reviews/image_sd15_baseline.md. Required desks, stairs, generator casings and telescope accessories were missing/unclear. Several images became collages/object sheets; workshop seed 42 contained QUEST lettering, hall seed 43 included human figures, and telescope seed 43 showed open sky outdoors. Ambiguous details remain for human adjudication. Original human review forms remain pending; no numerical semantic pass rate or independent ratings were invented.

Three of five image candidates now have full shared development baselines, all with scene-content failures. Recommended preparing SDXL Base 1.0 as candidate four, including checkpoint/VAE/runtime requirements, while preserving current prompts and evidence. No models were run or downloaded by the assistant; documentation-only review required no software test rerun, commit or push.

## 59. SDXL Base smoke configuration prepared (23 September 2026)

Prepared evaluation/image_candidates_sdxl_base.json for candidate four. Verified official revision 462165984030d82259a11f4367a4eed129e94a7b, approximately 6.94 GB single-file checkpoint and published SHA-256 31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b; recorded OpenRAIL++ licence provenance. Predeclared 30-step CFG 7 Euler/discrete configuration uses unchanged 512px briefs/seeds and embedded VAE with the pinned runtime's SDXL scaling path. No refiner/LoRA or external VAE was added. Decoding/resource compatibility remain subject to user-run smoke review; the 512px comparison is not a native-resolution model-quality claim.

Added configuration and documentation without changing existing baselines or evaluator source. Offline preview checks parsing/schedule only. Provided user-managed resumable download/hash verification and smoke commands. No model download, inference, dependency installation, commit or push was performed by the assistant.

## 60. SDXL Base smoke test reviewed (23 September 2026)

Reviewed user-run generated/image-evaluations/20260923T115240381325Z-054d8145. Pinned checkpoint SHA-256 matched; runtime exited zero and the 512x512 PNG passed integrity checks. Thirty-step CFG 7 Euler/discrete execution completed through Vulkan with embedded-VAE decoding. Load-inclusive wall time was 19.516 seconds; internal sampling 15.59 seconds and VAE decoding 0.64 seconds. Internal timings are not additive independent measurements or whole-system peak-memory evidence.

Non-blind assistant inspection found a coherent hall with closed wooden-framed door and an opaque/frosted-looking inset. No dusty desk was visible, and this inset does not clearly establish the required high frosted glazing. Prominent lettering appeared on a sign above the door, violating the no-lettering brief. Successful decoding therefore does not establish scene-content compliance. Original human review fields remain pending. Recommended the unchanged ten-image SDXL Base baseline before comparison or tuning; the shared 512px constraint is not a native-resolution quality assessment.

No models were run or downloaded by the assistant, and no software tests were rerun for this documentation-only review. No commit or push occurred.

## 61. Full SDXL Base image baseline reviewed (23 September 2026)

Reviewed user-run generated/image-evaluations/20260923T120515449565Z-d094ed1a and individually viewed all ten outputs. Runtime and 512x512 PNG integrity passed 10/10. Mean load-inclusive wall time was 19.006 seconds (18.696–19.669; total 190.065). Dataset/protocol hashes, exact prompts and seeds matched the SD 1.5 baseline; hall seed-42 hash matched the smoke sample. Separate sessions/configurations and the 512px task constraint limit comparative speed and native-resolution quality claims.

Saved non-blind per-image observations in evaluation/assistant_reviews/image_sdxl_base_baseline.md. Library seed 42 showed shelves and stairs but lacked a clear reading stand/manual. Hall seed 43 opened the door. Four seed-43 images became object sheets, including generator/telescope sheets with lettering. Other missing or ambiguous objects were recorded without invented human ratings or a numerical semantic pass rate. Original pending human review forms remain unchanged.

Four of five image checkpoints now have full development baselines; all have scene-content failures. Proposed next: prepare DreamShaper 8, explicitly an SD 1.5-family fine-tune, with verified provenance/configuration and user-managed smoke commands. No models were downloaded or run by the assistant. Documentation-only review required no software test rerun, commit or push.

## 62. DreamShaper 8 configuration prepared (23 September 2026)

Prepared evaluation/image_candidates_dreamshaper8.json using creator repository Lykon/DreamShaper, revision 228d79cb20811466f5c5710aa91f05dabd0b8a14 and standard DreamShaper_8_pruned.safetensors (approximately 2.13 GB). Verified published SHA-256 879db523c30d3b9017143d56705015e15a2cb5628762c11d086fed9538abd7fd. Repository API metadata required a read-only network request after browser/API access failures; no weight downloads occurred. Metadata labels licensing as other and lists no separate LICENSE file; model-card retention and final applicable-terms review remain explicit.

Matched SD 1.5 trial settings (30 steps, CFG 7.5, Euler/discrete), with shared 512px briefs/seeds and no extra embeddings/LoRA/VAE. This is an SD 1.5-family fine-tune, not an independent architecture. Added user-managed download/hash verification and smoke instructions; actual compatibility and results remain unmeasured. Offline preview validates configuration only. Existing baselines remain unchanged. No inference, model downloads, dependencies, commits or pushes were performed by the assistant.

## 63. DreamShaper 8 smoke test reviewed (23 September 2026)

Reviewed user-run generated/image-evaluations/20260923T122617633743Z-4ab0fa01. Saved checkpoint SHA-256 matched the pinned published hash. One 512x512 image completed with exit zero and passed PNG integrity. Thirty-step CFG 7.5 Euler/discrete execution and VAE decoding succeeded through Vulkan. Load-inclusive wall time was 8.850 seconds; internal generate_image time 8.55 seconds. One separate-session sample does not establish a comparative speed ranking.

Non-blind assistant inspection found an indoor hall/library-like scene with desk/cabinet-like furniture, but a clearly visible person and open double doors violate the no-people and closed-library-door requirements. Dust on the desk and high frosted glazing were not clearly established. Bright light through glazing does not establish frosting. Technical compatibility therefore succeeded while scene-content compliance failed. Original human review fields remain pending; no human ratings were invented.

Recommended the unchanged ten-image DreamShaper 8 baseline to complete the five-checkpoint development runs before comparison/tuning. No models were run or downloaded by the assistant. Documentation-only review required no software test rerun, commit or push.

## 64. DreamShaper baseline and five-image-candidate overview (23 September 2026)

Reviewed user-run generated/image-evaluations/20260923T123604219662Z-9ecf0176 and individually viewed all ten images. Runtime completion and 512x512 PNG integrity passed 10/10. Mean load-inclusive wall time was 8.992 seconds (8.888–9.144; total 89.923). Dataset/protocol hashes, prompts and seeds matched SDXL Base. Hall seed-42 hash matched the smoke image. Saved non-blind per-image observations and a five-candidate overview in evaluation/assistant_reviews/image_dreamshaper8_baseline.md.

Libraries showed clear stairs, but open-manual/reading-stand requirements remained unclear. Both hall scenes opened the doors and the first included a person. Telescope scenes lacked clearly identifiable required equipment; glow and enclosure ambiguities were left for human adjudication. Human forms remained pending; no semantic success rate, independent ratings or final model winner was invented.

All five candidates now have ten-image development baselines: 50/50 runtime/PNG successes, with scene-content failures across candidates. Recorded mean wall seconds: SDXL Turbo 13.39, SD-Turbo 3.00, SD 1.5 13.89, SDXL Base 19.01, DreamShaper 8 8.99. Different compute budgets and separate sessions limit timing comparisons. Smoke samples are separate, and successful file checks are not content accuracy. Proposed next: developer visual checklist review/style preference, potentially aided by an offline gallery, before selection or versioned prompt improvements. Speech comparisons and integration remain outstanding. No models were run/downloaded by the assistant; documentation-only work required no software test rerun, commit or push.

## 65. Offline image review gallery implemented (23 September 2026)

Built observatory/image_gallery.py and its standalone HTML/JavaScript template, then generated generated/image-review-gallery.html from the 50 existing baseline images. Dataset/image hashes are checked against saved manifests/results; images are embedded for direct browser opening without a server/network/model. Original evaluator outputs and review forms remain unchanged. Images are grouped by room/seed across candidates and identified by run/attempt/hash.

Added required/forbidden present/absent/unclear judgements, notes, separate clarity/style ratings, per-candidate/seed coherence and overall style preference. No ratings were prefilled. Exports identify the review as developer_non_blind and keep incomplete content judgements null; complete content passes require all required details present and forbidden details absent. Browser saving is best-effort with explicit export backup instructions. Import checks gallery identity/checklist values and asks before replacing current browser work. Export uses local JSON downloads, not writes into original evidence.

Validation: 204 offline tests passed in 3.43 seconds, including source integrity failures, duplicate runs, safe HTML data embedding and preservation of original files. Gallery generation succeeded against all 50 real saved images. Browser interactions still require developer verification; automated builder tests are not a claim of browser end-to-end testing. Updated tasks and image-trial instructions. Generated gallery/exports remain ignored and need deliberate submission preservation. No models, downloads, dependency installations, commits or pushes occurred.

## 66. Speech downloads prepared; image human review deferred (23 September 2026)

Following the user's request to put image review aside and get downloads done first, checked existing models and confirmed Piper Lessac ONNX/config are present. Prepared evaluation/speech_downloads.json with 32 revision-pinned files totaling 3,213,907,015 bytes: native Kokoro v1 weights/config/af_heart, SpeechT5 model/tokenizer/processor plus HiFi-GAN vocoder and speaker-embedding archive, MMS English safetensors/config/tokenizer, and XTTS-v2 model/config/vocabulary/supplied speakers/auxiliary assets. Model cards and available licence file included. Native Kokoro is an explicit change from the previous ONNX proposal; inference compatibility is not yet measured.

Added scripts/download_speech_models.py: preview by default, explicit --download, resumable curl transfers, published LFS SHA-256 or Git blob/size verification, verified existing-file reuse, and final receipt. No inference/runtime imports or dependency installation. Download metadata was read online; weights were not downloaded by the assistant. Added user commands and limitations in evaluation/speech_downloads.md. Runtime environments, phonemisation resources, fixed-voice selection and speech adapters remain separate pending work; this is not a claim that every future supporting download is resolved.

Validation: 209 offline software tests passed in 1.85 seconds, covering existing-file reuse, partial-file recovery, hash rejection before final rename, small-file Git blob verification, manifest identities and path boundaries. No model execution, commits or pushes occurred. User download receipt/errors are the next evidence required. Image ratings/selection remain deferred, not marked complete.

## 67. Speech asset download receipt reviewed (23 September 2026)

Reviewed user-generated models/speech/download_receipt.json, timestamp 2026-09-23T14:47:05.832723+00:00. Receipt manifest SHA-256 matched the current pinned download manifest. All 32 expected entries were present with matching revisions, existing local files and expected sizes (3,213,907,015 bytes total); recorded large-file hashes matched published manifest hashes. No discrepancies found. This review checked the downloader's integrity receipt and current file sizes rather than independently rehashing all downloaded bytes.

The planned speech model-asset bundle is now downloaded, alongside existing Piper. This does not establish runnable environments, successful speech synthesis or comparative quality. Runtime packages, phonemisation resources, speaker selection and adapters remain pending; additional supporting downloads may be needed during setup. Next: prepare isolated speech runtime environments and user-run installation commands without disturbing the working gameplay environment. Image human review remains deferred. No inference, dependency installation or model download was performed by the assistant, and no software tests were rerun for this documentation-only review.

## 68. Isolated speech runtime setup prepared (23 September 2026)

Added scripts/setup_speech_runtimes.py, scripts/check_speech_runtime.py and three runtime requirement files. User-run --install creates separate Python 3.11 environments for SpeechT5/MMS, Kokoro and maintained Coqui XTTS, leaving gameplay/Piper unchanged. Selected CPU PyTorch/torchaudio 2.8.0, transformers 4.57.6 and explicit core pins; Kokoro/Misaki 0.9.4 and coqui-tts 0.27.5. Checked official installation documentation and release metadata. These are proposed configurations, not proven installed compatibility. Transitive versions are resolver-selected and recorded, not fully locked.

Kokoro setup explicitly includes spaCy's English small model wheel as an additional G2P resource. User command downloads packages/supporting resources only; no speech checkpoint loading or synthesis. Post-install pip check and offline import checks record package inventories/errors. Import checks set HF offline flags and block Python socket connections; they do not establish working G2P, voice selection or synthesis. Setup stops on failure with saved status and supports individual-profile retries. Added virtual-environment Git exclusions and updated user instructions/tasks. Actual installation remains user-run.

Validation: 212 offline tests passed in 1.85 seconds, including command isolation, CPU index selection, continued collection of import failures and missing-class detection using simulated importers. No runtime packages were installed and no models were run/downloaded by the assistant. No commits or pushes occurred. Next evidence: user installation result folder and errors, then inspect import reports before preparing synthesis smoke tests. Image human review remains deferred.

## 69. Speech runtime installation reports reviewed (23 September 2026)

Reviewed generated/speech-runtime-setup/20260923T152149711580Z. Setup status completed for hf, kokoro and xtts, with successful import reports and saved package freezes for all three isolated interpreters. All 21 recorded import checks passed (8 HF, 8 Kokoro, 5 XTTS). Reports recorded PyTorch/torchaudio 2.8.0+cpu and transformers 4.57.6 throughout, Kokoro 0.9.4 and coqui-tts 0.27.5 in their respective environments. Completed sequential setup also indicates its pip check commands returned successfully. Each report explicitly recorded inference_performed false.

This confirms installed dependency/import readiness, not checkpoint loading, phonemisation, voice selection, audio correctness or synthesis latency. Next proposed implementation: a shared speech development runner and local adapters using the existing ten passages, with user-run one-passage smoke tests before full comparisons. Image human review remains deferred. No inference or installations were performed by the assistant during this documentation-only review; no software test rerun, commit or push occurred.

## 70. Shared speech evaluator and local adapters implemented (23 September 2026)

Implemented observatory.evaluate_speech with isolated scripts/speech_worker.py adapters for Piper, Kokoro, SpeechT5/HiFi-GAN, MMS English and XTTS-v2. Read installed runtime source before selecting local loading APIs. Workers use CPU/local paths with offline HF flags and blocked Python socket connections. No checkpoints were loaded or models executed by the assistant. Fixed initial voices: Lessac, af_heart, archived SLT b0258 embedding, MMS English default and supplied Ana Florence. Real voice availability/G2P/loading remain subject to the user smoke run; no silent substitution is allowed.

Runner uses the existing ten exact passages, seeds 42/43 for supported APIs (Piper unsupported), reversed candidate order on repetition two and fresh processes per attempt. Saves source snapshots/hashes, local asset hashes, full schedule/requests/commands, runtime logs, worker package versions/timings, audio, incremental failures, summary and null listening-review fields. Timeout/nonzero exit/missing or invalid audio/interruption are retained without retry/fallback. Audio checks cover nonempty complete mono PCM16 data, nonzero samples, duration/sample rate/hash and clipping observations. Real-time factor excludes loading; synthesis time includes front-end processing and WAV encoding. These file checks do not judge spoken content. Resource peaks are unavailable.

Validation: 220 offline tests passed in 3.83 seconds using fake subprocesses and synthetic WAV files. Coverage includes candidate order, seeds, shared text, failure retention, timeout, interruption, silence, missing audio, no retries, pending reviews and invalid settings. This is orchestration evidence, not real adapter synthesis success. Added evaluation/speech_trials.md with five-request smoke command and later 100-output full-run scope; updated tasks/README/Git visibility. No model downloads, dependency changes, inference, commits or pushes occurred. Next: user-run one-passage smoke results and listening before full comparison. Image review remains deferred.

## 71. Five speech smoke outputs and developer feedback reviewed (23 September 2026)

Reviewed generated/speech-evaluations/20260923T161045310963Z-219405ee: five completed attempts and valid audio files for T01. Recorded developer feedback separately in evaluation/assistant_reviews/speech_smoke_review.md: Piper/Kokoro/XTTS sounded good; SpeechT5 had lots of static and was very monotone, unclear and robotic; MMS had many mispronunciations. These are subjective developer smoke judgements, not independent ratings or complete passage annotations. Original review forms remain pending.

Inspected SpeechT5/MMS logs, output metrics, local sample-rate configs and installed/reference generation path. Both used mono PCM16 at 16 kHz without full-scale clipped samples. SpeechT5's chosen speaker embedding was finite, shape (512,), norm 1.0. No obvious sample-rate, shape or normalisation error was found; the cause of static/mispronunciations remains unresolved. No raw float waveform was retained, and no independent assistant listening or model-quality attribution was claimed.

Synthesis seconds / real-time factors: Piper 1.27/.22, Kokoro 1.32/.19, SpeechT5 3.80/.54, MMS .86/.11, XTTS 12.43/1.95. Loading was separately recorded and substantial for several models; these single samples do not establish warm inference performance or a general ranking. Full five-model development comparisons remain pending. No inference, downloads, fixes or tuning were performed by the assistant; no software test rerun was needed for this evidence review.

## 72. Speech technical summary only (24 September 2026)

At the user's explicit request, created a temporary script, summarized saved JSON records and deleted the script afterward. Saved technical_summary.json in full run generated/speech-evaluations/20260923T165609248021Z-c2e173fa; excluded the earlier five-attempt smoke run. No audio files were opened, no detailed review performed and no models executed.

All 100 unique planned attempts completed with valid-audio flags and no recorded errors: 20 per candidate. Mean synthesis seconds / mean per-clip real-time factor: Piper .176/.033, Kokoro 1.125/.171, SpeechT5 2.799/.417, MMS .659/.100, XTTS 9.859/1.516. Loading is separate; mean full wall seconds were 1.631, 7.622, 7.116, 3.971 and 23.244 respectively. XTTS synthesis exceeded audio duration in every recorded attempt. Piper had a tiny nonzero full-scale sample fraction in every clip (maximum .00268%); this is not a perceptual clipping diagnosis. Saved file checks do not establish pronunciation or quality; earlier listening feedback applies only to smoke samples. Detailed listening review remains deferred.

## 73. Developer listening subset and optional gameplay speech (24 September 2026)

Recorded user listening feedback for 15 clips (T03/T05/T10, repetition one) from speech run 20260923T165609248021Z-c2e173fa. Final preference: Kokoro, XTTS, Piper, SpeechT5, MMS. SpeechT5 was described as robotic/monotonous/static; MMS had pronunciation/enunciation problems. Preserved this as nonblind developer subset feedback without invented numeric ratings or claiming all 100 outputs were listened to. Kokoro af_heart is the provisional gameplay choice.

Added optional --speak and a text-only Speaker adapter reusing the existing local CPU worker in the isolated Kokoro environment. Accepted scene descriptions, including narrative fallback, display before synchronous Windows playback. Only accepted state changes trigger speech; initial scene, cancellation, clarification, rejection and unchanged redraws stay silent. Final hall transition is spoken once before completion. Speech synthesis timeout, missing runtime, playback errors and interruption retain usable text and the already-accepted state. No retry or automatic model substitution occurs. Saved request/runtime/worker/audio/result artifacts remain Git-ignored; review notes and run instructions are explicitly Git-visible.

Validation: 232 offline tests passed in 1.87 seconds, using fake workers/playback and synthetic WAVs. No real models, downloads or installations were run. Model-only evaluation behavior is unchanged. Fresh process loading adds latency; live playback and broader multimodal integration remain unverified. User next runs --narrate --speak, cancels once and completes the hall sequence. No commit or push was performed.

## 74. Live gameplay speech success reported (24 September 2026)

After receiving the --narrate --speak run instructions, the developer reported "it worked great". Recorded this as positive developer feedback on live playback, separate from entry 73's 232 passing offline software tests. No exact run path or per-check outcomes were supplied; cancellation, exact displayed/spoken text matching, full route completion and live failure recovery are not individually claimed as verified by this feedback.

Updated tasks.md and gameplay_narration.md to reflect the report. Confirmed the existing generated/image-review-gallery.html is present for the next developer review of saved images. Image selection and integration remain outstanding; no image ratings or model choice were inferred from speech feedback. No generated artifacts were changed, no models were run or downloaded, and no commit or push occurred. Documentation-only change; software tests were not rerun. Next: use the existing offline gallery to resume image review and record a provisional image choice before integration.

## Future entry template


- Date/time and objective.
- Decision and alternatives considered.
- Exact code/prompt/model/configuration version.
- Work performed and evidence links.
- Results, including failures, timings, and sample size.
- Interpretation and limitations.
- What would be done differently; proposed next step.
