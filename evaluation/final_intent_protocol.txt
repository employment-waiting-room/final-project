# Reserved intent evaluation protocol v1

Scope: the existing 30 assistant-authored intent cases reserved on 22 September. Preserve their exact bytes and original reservation. This is new wording within the known five-room domain, not unseen worlds or independently human-authored data. Independent annotation review remains pending. No narrative, image, speech or end-to-end quality claims follow from this run.

Freeze Qwen3:4b by installed digest, Ollama version, explicit V1-JSON prompt, request/scoring code, dataset hash and Python/httpx/pydantic versions before predictions. Temperature 0, seed 42, context 4096, output limit 180 tokens, thinking off, timeout 60 seconds, one pass in saved order. No warm-up, partial limit, retries, alternate prompts or automatic downloads. Stored evaluator requests contain public context and player text, never answer labels/setup traces. Gameplay guards and confirmation are excluded.

Primary metric: exact status/action/target accuracy across all 30 attempts. Count schema failures, timeouts, HTTP and completion errors as incorrect. Report counts alongside percentages. Secondary metrics: structural validity, reference transition/outcome agreement, grouped results by the reserved language and state-complexity categories, and latency including failures/load effects. Reference agreement cannot rescue a wrong intent. Report false action acceptance and clarification/unsupported confusions from raw rows separately. Do not invent a universal pass threshold or equate model accuracy with engine safety.

Retain every raw response/request, error, timing and frozen identity. An interrupted run is incomplete; recorded-attempt accuracy must not be presented as the complete 30-case result. A durable release receipt blocks casual reruns, even after interruption. Preserve it and seek a documented continuation plan; do not delete it to select a better run. Original reservation status is historical; the release receipt records actual release. These filesystem controls prevent accidents, not intentional tampering.

If any case has been used for tuning, retire it to development and reserve a replacement before claiming a fresh held-out result. Do not tune on the first final results and call a repeat unseen. Annotation corrections require a documented version/reason rather than silently changing labels. The freeze intentionally detects source changes, including otherwise unrelated observatory Python edits: resolve drift before execution rather than bypassing checks.

## User-run steps

First, with Ollama running and Qwen already installed, capture metadata only:

```powershell
.\.venv\Scripts\python.exe -m observatory.held_out
.\.venv\Scripts\python.exe -m observatory.final_intent --freeze
.\.venv\Scripts\python.exe -m observatory.final_intent --verify
```

Send the saved freeze path or any error for review before release. No final prediction is made by these commands. Freeze fails rather than overwriting an existing file. The source snapshot is prepared, but not sealed until this user command captures the actual installed digest/version.

After reviewing the freeze and deciding to release the reserved cases, the explicit command is:

```powershell
.\.venv\Scripts\python.exe -m observatory.final_intent --execute
```

This makes 30 real model requests and saves a uniquely named folder under generated/final-intent-evaluations. Do not run a connectivity smoke test against the reserved cases. Send the saved results folder; preserve it for submission because generated output is Git-ignored. The freeze and release receipt in evaluation/ are Git-visible. Reserve narrative/image/speech evaluation separately; those new sets have not been created in this step.
