# Entrance-hall narrative safeguard

## Full-world rules mode

The complete five-room engine supports confirmed typed actions and model-free numbered choices:

```powershell
.\.venv\Scripts\python.exe -m observatory --world
```

Choose numbered actions; use `r` to restart and `q` to quit. Explore the workshop, install the fuse and start the generator; unlock the library to reach the telescope chamber. Reading the manual and aligning the beacon enable rescue. Shelter requires power but not manual reading/alignment. Both endings are explicit choices. Look around reveals only known contents and does not advance the state revision. Restart resets progress with a new session identity.

Typed requests use local Ollama Qwen3:4b with the explicitly selected V1-JSON prompt. Run the same command with Ollama available, type `go to the workshop`, cancel once, then repeat and confirm with y/yes. The interpreted action/target is displayed before any proposed state change is accepted. Observations, completed actions and prerequisite rejections do not require confirmation or advance revision. Missing confirmation, any other reply, EOF or Ctrl+C cancels. Numbered actions remain direct and never call the model.

Gameplay-only guards reject common unsupported verbs and request clarification for ambiguous references, alternatives, compound actions, bare `use the key` and vague `finish`. These conservative checks can over-clarify; confirmation still matters and no new interpretation accuracy is claimed. Output schema/action-target validation and engine prerequisites are independent of the prompt. Logs under ignored `generated/world-intent-logs/` separate model/local-guard interpretations from confirmation decisions and include session/revision, raw model responses and timing. The model-only evaluator/results are unchanged.

Full-world generated narration, illustrations and speech are not connected yet; combining --world with media flags is rejected explicitly. The original command below still runs the integrated entrance-hall prototype. Browser integration remains outstanding.

Narration implemented 22 September 2026; optional speech and illustration added 24 September. This remains an entrance-hall presentation adapter; full-world and browser integration are incomplete. Speech integration passed offline software tests, and the developer subsequently reported that live playback "worked great". This positive report does not provide individual cancellation, exact-text or failure-recovery check results. Combined image/narration/speech playback awaits a live user check.

## Optional hall illustration

SDXL Turbo was provisionally selected from the developer's first ten image reviews. Run the combined terminal interaction with the existing local assets, runtime and Ollama service:

```powershell
cd C:\Users\PC\Desktop\Github\EmploymentWaitingRoom\final-project
.\.venv\Scripts\python.exe -m observatory --narrate --illustrate --speak
```

Cancel a typed inspection first: no image generation or speech should occur. Confirm inspection next: accepted text appears, a fresh 512x512 hall PNG is generated and opened with the Windows default viewer, then Kokoro speaks the accepted description. Return to the terminal to collect the key and unlock the door. The same image is retained without another generation/viewer launch. This is a terminal-plus-image-viewer interaction, not the browser game.

The approved establishing brief omits portable quest items and changing lock details, so it remains applicable across the three hall actions. It is selected by the engine location, never model-generated prose. Gameplay uses a separate fixed configuration matching the measured baseline: SDXL Turbo, four steps, CFG 1, Euler/sgm_uniform, seed 42. No evaluator configuration or saved results are changed.

Only one generation attempt occurs per session, with a 120-second timeout. Missing runtime, invalid PNG, generation failure, interruption or viewer failure retains text gameplay. New sessions make a new attempt; there is no persistent image cache yet. Generation is synchronous and delays speech. PNG integrity checks do not establish scene correctness: inspect the art for missing objects, open doors or unwanted people/items. The textual state remains authoritative.

`generated/gameplay-images/` records prompt, command/configuration, runtime output, image hash/integrity, elapsed time and errors. Viewer launch success does not prove the image was seen. Generated artifacts are Git-ignored; retain the run folders deliberately. Send the image folder path and any visual/playback issues after your live check. Live combined integration is still unverified.

## Optional Kokoro speech

With the existing speech assets/runtime and Ollama available:

```powershell
cd C:\Users\PC\Desktop\Github\EmploymentWaitingRoom\final-project
.\.venv\Scripts\python.exe -m observatory --narrate --speak
```

The full opening description is generated/displayed once at startup and spoken when --speak is enabled. After it finishes, cancel one typed inspection: no additional audio should play and state should remain unchanged. Then confirm inspection, collect the key and unlock the door. Each accepted transition displays and speaks its brief outcome once, including factual fallback text. Unchanged redraws are silent. Numbered choices also trigger speech after their accepted transition. Without --speak, no speech worker is launched; --speak alone reads deterministic opening/action descriptions.

Kokoro runs locally on CPU in its existing isolated environment with `af_heart`, seed 42 and the existing offline worker. Each transition starts a fresh process, so model loading adds delay. Synthesis has a 120-second timeout; Windows WAV playback is synchronous. Generation/playback errors or interruption produce a text-only continuation, with no retry, model substitution or repeated state transition. The speech adapter receives text only. It does not assess narrative truth or change evaluator prompts/results.

Logs under `generated/gameplay-speech/` retain the exact text request, runtime output, worker metadata, WAV when generated and result/error. These are ignored by Git; preserve useful run evidence separately. Send the run-folder paths and describe any silence, wrong words or playback errors after the user-run check. No real gameplay speech has been run by the assistant.

## User-run check

With the existing local Ollama service and Qwen installed, the user can opt into narration:

```powershell
cd C:\Users\PC\Desktop\Github\EmploymentWaitingRoom\final-project
.\.venv\Scripts\python.exe -m observatory --narrate
```

This command runs local models when you play; the assistant did not execute it. Without `--narrate`, the previous deterministic scene descriptions remain in use. Typed actions still invoke the existing interpreter in either mode. Numbered choices bypass interpretation.

Try cancelling a typed inspection first: state should remain unchanged and no scene generation should occur. Then confirm inspection, collect the key and unlock the library door. Each accepted change requests at most one narration. The final description should leave the door **closed and unlocked**, keep the key carried and keep the player in the hall. The prototype still ends there. You can use numbered choices to test narration independently of intent interpretation. Send the generated log filenames and any surprising text when you run it.

## Action-focused narration (24 September update)

After the developer's successful combined image/speech check, repeated full-scene narration was reported as disruptive. The CLI now supplies the before-and-after state to the narrator. The adapter identifies the one legal completed action and requests 1-3 sentences, at most 45 words, focused on its outcome. Model failure or rejected output uses these short factual responses:

- Inspect: "You discover a library key on the dusty desk. It is not yet collected."
- Collect: "You pick up the library key."
- Unlock: "You unlock the library door. It remains closed."

Speech reads the same accepted outcome text. The full opening is generated once before the first action using the existing full-scene guards/fallback, then displayed and optionally spoken. Entering other rooms and explicit look-around are not implemented. The unchanged hall illustration is reused after its first accepted-action generation. Outcome logs use hall-outcome-v1 and hall-outcome-guards-v1 and include previous state and action. These bounded checks reject known contradictions, excessive length and common room/weather recaps; they cannot prove arbitrary prose factual or eliminate every repetition.

Validation: 254 offline tests passed; real output from this revised prompt remains user-run. Use the same combined command above and report whether the three responses are brief and action-specific. Model-only evaluation prompts/results remain unchanged.

## Original full-scene behavior (retained for direct scene rendering)

- The engine applies the action before narration. Cancellation, clarification and rejection do not trigger narration. The narrator has no transition function and cannot modify the frozen state.
- Canonical required sentences describe location, lock/closed status and key discovery/possession. The initial context does not disclose the hidden key. The three-step prototype's current state uniquely determines these facts; this is not a general full-world event/history implementation.
- The generation contract contains only `description`. Suggestions come from engine `allowed_actions`; the brief ID comes from the location. Neither field is copied from the model. The CLI continues displaying engine-approved numbered choices; the brief ID is reserved for later media integration.
- The model is asked for 60-100 words with each required sentence copied exactly once. Validation checks the strict schema, length and those exact sentences, plus conservative patterns for known extra lock/inventory, door-opening, movement, power/ending, entity and first-person claims.
- One generation attempt is made, with a 30-second HTTP timeout. There is no automatic retry. HTTP/schema/completion errors, interruption during generation or failed checks use the engine-derived factual description. Re-rendering the same state cannot apply an action again. Ctrl+C during generation cancels that generation and keeps the already-confirmed action; Ctrl+C during action confirmation cancels the unconfirmed action.
- Existing text is reused while the state remains unchanged, rather than regenerated every time the terminal redraws. Restart/session revisions and asynchronous stale-response protection remain future browser/full-world work.

## Evidence and limits

Unique JSON records under `generated/gameplay-narratives/` preserve state, prompt/policy versions, exact request, raw response when available, validation reasons, accepted text, source (`model` or `fallback`), engine suggestions/brief ID and wall time. Logging failure produces a warning but does not lose the scene. These generated logs are Git-ignored and must be preserved deliberately for submission.

The gameplay prompt (`hall-narrative-v1`) and policy (`hall-narrative-guards-v1`) differ from the full-world model-only comparison. Existing v1/v2 evaluator requests, scores, fixtures and review annotations are unchanged. Do not count fallback descriptions as successful raw-model generation or compare this combined gameplay pipeline directly with narrative structural scores.

These are **bounded checks**, not semantic proof. They intentionally reject some valid paraphrases, benign mentions and first-person text. Other false claims can escape the patterns: an explicit test demonstrates that an invented sentence about purple butterflies passes the current checks. Exact truthful sentences do not prove all surrounding prose is true. Live human review, measured fallback rates and broader evaluation are still needed. No new factuality or usability accuracy is claimed from unit tests.

The developer's judgement on the earlier ambiguous review phrases remains pending; this implementation did not invent that feedback or alter the assistant-review results. Qwen remains provisional. No further prompt tuning or model downloads occurred in this step.
