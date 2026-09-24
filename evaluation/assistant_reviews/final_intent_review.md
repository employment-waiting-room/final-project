# Reserved intent result — 25 September 2026

Run: `generated/final-intent-evaluations/20260924T223002881754Z-c981b195`. All 30 unique scheduled cases were recorded; status completed. The saved freeze matches evaluation/final_intent_freeze.json. Manifest and release receipt match freeze SHA-256 `8bbd2471df0337d051c14f11f6580cc2d68fe61f59ea495b969ea0136764843b`.

Configuration: Qwen3:4b, explicit V1-JSON, thinking off, one pass, Ollama 0.34.3. This is model-only interpretation without gameplay guards or player confirmation. Reserved labels are assistant-authored; independent annotation remains pending.

| Measure | Result |
|---|---|
| Exact status/action/target | 23/30 (76.7%) |
| Valid output contract | 30/30 (100%) |
| Reference outcome/state agreement | 23/30 (76.7%) |
| Runtime/schema errors | 0/30 |
| Direct | 7/7 |
| Paraphrase | 7/7 |
| Ambiguous | 1/4 |
| Compound | 0/4 |
| Unsupported | 4/4 |
| Adversarial | 4/4 |
| Simple / moderate / complex state | 11/13, 6/8, 6/9 |

Mean request wall time: 0.541 seconds; median 0.262 seconds; maximum 7.929 seconds; summed request wall time 16.239 seconds. These include loading effects, are not warm-inference benchmarks and do not measure browser/media latency or resource peaks.

All seven errors expected clarification but predicted an action:

| Case | Request | Predicted action |
|---|---|---|
| H15 | Put the library key to use. | unlock_library |
| H16 | Inspect that object closely. | inspect_desk |
| H18 | Open the library door, please. | unlock_library |
| H19 | Search the desk, then pick up its library key. | inspect_desk |
| H20 | Start the generator and return to the workshop. | start_generator |
| H21 | Align the beacon and transmit a rescue signal. | align_beacon |
| H22 | Unlock the library door and enter the library. | unlock_library |

H18's expected clarification follows the reserved already-unlocked-door context. The other errors resolve an unspecified reference/instrument or choose part of a compound request. Seven of eight expected-clarification cases were falsely accepted as action intentions; this does not mean seven gameplay state changes occurred. No gameplay engine execution or confirmation was measured here.

The earlier 49/53 (92.5%) development result used different examples/category proportions and tuning exposure; the difference is not a controlled estimate of degradation. These small descriptive category counts cannot establish general accuracy or universal adversarial safety. Results support the need for clarification and confirmation, but do not measure those safeguards' effectiveness.

Preserve this result and its release receipt. Do not tune on these failures and label another run unseen. This review changed no prompts, rules, labels or results and ran no models. Raw artifacts remain Git-ignored; this tracked review does not replace their deliberate retention for submission. Separate narrative/image/speech and end-to-end evaluation remain outstanding.
