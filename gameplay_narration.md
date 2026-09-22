# Entrance-hall narrative safeguard

Implemented 22 September 2026; software-tested with simulated responses only. Live gameplay generation and fallback frequency have not been evaluated. This is an entrance-hall presentation adapter, not full-world, browser, image or speech integration.

## User-run check

With the existing local Ollama service and Qwen installed, the user can opt into narration:

```powershell
cd C:\Users\PC\Desktop\Github\EmploymentWaitingRoom\final-project
.\.venv\Scripts\python.exe -m observatory --narrate
```

This command runs local models when you play; the assistant did not execute it. Without `--narrate`, the previous deterministic scene descriptions remain in use. Typed actions still invoke the existing interpreter in either mode. Numbered choices bypass interpretation.

Try cancelling a typed inspection first: state should remain unchanged and no scene generation should occur. Then confirm inspection, collect the key and unlock the library door. Each accepted change requests at most one narration. The final description should leave the door **closed and unlocked**, keep the key carried and keep the player in the hall. The prototype still ends there. You can use numbered choices to test narration independently of intent interpretation. Send the generated log filenames and any surprising text when you run it.

## Implemented behaviour

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
