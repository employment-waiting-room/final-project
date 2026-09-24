# Speech development listening subset — 24 September 2026

Source: user listening feedback on run `20260923T165609248021Z-c2e173fa` under `generated/speech-evaluations/`. This records developer feedback, not assistant listening or independent blinded evaluation.

The developer reviewed T03, T05 and T10 in repetition one: 15 clips, three per model. They reported the same observations/preferences across these passages and then supplied the final five-model order below.

| Preference | Model | Attempt IDs |
|---|---|---|
| 1 | Kokoro | A0013, A0015, A0020 |
| 2 | XTTS-v2 | A0043, A0045, A0050 |
| 3 | Piper | A0003, A0005, A0010 |
| 4 | SpeechT5 | A0023, A0025, A0030 |
| 5 | MMS English | A0033, A0035, A0040 |

The developer said all spoke the correct words, but described SpeechT5 as robotic, monotonous and static, MMS as having mispronunciations and unusual enunciation, and XTTS as alright. Correct words and pronunciation are separate subjective observations here; there was no transcript alignment or numerical rubric scoring.

Decision: use Kokoro with the tested `af_heart` voice provisionally for optional entrance-hall gameplay speech. The earlier technical summary established file validity for 100 outputs; this listening feedback covers only 15 of them. No claim of complete listening review or held-out quality follows. Original evaluation records remain unchanged. Generated audio and the technical summary are Git-ignored and must be preserved separately for submission.
