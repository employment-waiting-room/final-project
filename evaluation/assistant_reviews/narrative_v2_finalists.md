# Qwen and Phi narrative review

Reviewed 22 September 2026 by Codex assistant. This is **non-blind assistant review**, not independent human annotation, user testing or an automated factuality score. All 32 saved v2 descriptions per model were inspected, including descriptions whose surrounding JSON failed action validation. No new inference occurred. Original results and pending human-review forms were left unchanged.

Full per-attempt evidence: [narrative_v2_finalists.json](narrative_v2_finalists.json). It records source run IDs and SHA-256 hashes, description text, individual required-fact judgements, the forbidden checklist considered, exact violation/uncertainty quotations, notes and assistant readability ratings. The offline recording script validates coverage and quote provenance; it does not determine whether prose is true.

## Findings

| Assistant assessment | Qwen3:4b | Phi4-mini:3.8b |
| --- | ---: | ---: |
| Descriptions reviewed | 32 | 32 |
| Passed factual review | 14 | 4 |
| Failed factual review | 10 | 23 |
| Uncertain, awaiting developer judgement | 8 | 5 |
| Outputs with definite violations | 10 | 21 |
| Passed both original structure checks and assistant factual review | 5 | 3 |

A pass requires the required facts to be satisfied with no identified violation or unresolved uncertainty. Missing required facts cause failure; unclear facts or wording remain uncertain unless another definite failure already determines the result. Thus Phi has two failures from missing facts without a definite invented claim. Multiple excerpts can support the same violation; they are not a count of independent errors. Structural validity and prose factuality remain separate. These findings are provisional annotations, not general accuracy estimates.

Qwen generally stays closer to the supplied state, though its prose is often short, repetitive and in first person. Phi sometimes writes clear scenes, but more often inserts an extra action, an invented cause or an access rule. Readability was rated for clarity rather than factual truth; the JSON preserves the individual ratings. Neither set supports claiming all accepted prose is safe.

## Definite failures worth retaining

| Model / attempt | Evidence | Why it matters |
| --- | --- | --- |
| Qwen A0003 | `which is now unlocked` | Collecting the key must leave the door locked. |
| Qwen A0058 | `activating the generator` and `The generator is stopped; power is off` | One structurally passing response contradicts itself and the installation-only outcome. |
| Qwen A0054 | `now-open library door` | Unlocking must leave the door closed. |
| Phi A0024 | `generator room is inaccessible due to the lack of power` | Invents a route restriction absent from the world. |
| Phi A0032 | `bench is already occupied by another person` | Invents an NPC and the wrong reason shelter failed; it passed structure. |
| Phi A0030 | `insert the library key into the console` | Invents another use of the key and a console-unlocking action. |
| Phi A0074 | `installing it again doesn't change anything` | Confuses post-action facts with an already-completed/no-op action. |

Good review examples include Qwen A0055 (manual procedure and retained state), Qwen A0061 (alignment without choosing an ending), Phi A0020 (already-carried key), and Phi A0076 (missing-manual rejection). These are examples, not substitutes for the full 64-output record.

## Developer judgement requested

1. Qwen A0004/A0052: `I still carry the library key but cannot open the door.` Does this reasonably describe a door that is still locked, or does it incorrectly imply the key cannot enable access? Marked uncertain, not a definite failure.
2. Qwen A0014/A0060: `visibility without power` / `without electrical power` while the generator is running. Does this communicate daylight's independence from electricity, or falsely imply that power is off? Marked uncertain.
3. Phi A0018/A0066: `passage to the workshop remains unexplored`. This is not in the model's public input. Is this an unacceptable extra history claim, even though it is compatible with the source setup? Marked uncertain.
4. Phi A0026: `The socket is currently empty, so the fuse is successfully installed.` Is this a comprehensible before/after account or a contradiction of the post-action state? The missing explicit inventory removal also needs judgement.

These questions are illustrative priorities, not the only uncertainty records. Keep each developer decision with its reason, date and reviewer identity in a separate annotation revision. Do not relabel assistant findings as independent human review. Style preference can be recorded separately after reading the examples; it must not override factual violations.

## Provisional recommendation

Retain Qwen as the provisional language model: its existing intent result was 49/53 versus Phi's 48/53, and this review found fewer narration failures. That one-case intent difference is small, and both the prompts and this review were informed by development results. Phi remains a useful alternative with stronger ambiguous-intent handling in the measured set. Do not claim a final universal ranking, independent validation, or a safe production narrator.

Before integration, implement bounded factual checks/fallback and keep engine-owned suggestions and illustration IDs separate from generated prose. This remains a proposed implementation, not work performed by this review. Missing full resource measurements, final held-out assessment, and user evaluation still limit final selection. No further prompt expansion is recommended from these samples alone.
