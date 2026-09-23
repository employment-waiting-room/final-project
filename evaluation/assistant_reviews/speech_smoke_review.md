# Speech compatibility smoke review

Date: 23 September 2026. Source run: generated/speech-evaluations/20260923T161045310963Z-219405ee. One exact T01 passage per candidate, seed 42 where supported. All five completed and passed file checks. This combines explicitly attributed developer listening feedback with assistant inspection of logs/configuration; the assistant did not independently listen or assign ratings.

| Attempt / model | Developer feedback | Load s | Synthesis s | Audio s | Real-time factor |
| --- | --- | ---: | ---: | ---: | ---: |
| A0001 Piper | Good | 1.50 | 1.27 | 5.80 | 0.22 |
| A0002 Kokoro | Good | 33.46 | 1.32 | 7.08 | 0.19 |
| A0003 SpeechT5 | Lots of static; very monotone, unclear, robotic | 27.15 | 3.80 | 6.98 | 0.54 |
| A0004 MMS | Many mispronunciations | 3.49 | 0.86 | 7.55 | 0.11 |
| A0005 XTTS-v2 | Good | 20.51 | 12.43 | 6.36 | 1.95 |

These are single fresh-process timings; load includes imports/G2P and synthesis includes front-end processing and encoding. XTTS synthesis took almost twice the duration of its audio in this sample. No general latency ranking or warm-service performance is established.

Diagnostic inspection, no inference: SpeechT5 and MMS WAVs were mono PCM16 at the configured 16 kHz. Neither contained full-scale clipped samples in the saved metrics. SpeechT5's archived speaker vector has shape (512,), finite values and L2 norm 1.0, matching the expected 512-dimensional input before reshaping. Its adapter follows the installed/model-card processor -> generate_speech -> HiFi-GAN path. Runtime logs did not show errors for these two attempts. No obvious rate/shape/normalisation mismatch was found, but this does not explain or rule out adapter, vocoder or model-generation problems. No raw float waveform was saved, so the PCM-only diagnostics cannot establish where static originated.

Piper had two full-scale samples (0.00156% of frames), despite being judged good; a clipped-sample count is not a perceptual diagnosis. Do not infer pronunciation correctness from successful generation, nonzero waveform or developer's broad good judgement. Exact erroneous words/timestamps and rubric scores have not been supplied. Original listening forms remain pending, with this separate note preserving actual user feedback without invented quantitative ratings.

The three positively received samples justify provisional attention to Piper/Kokoro/XTTS, not final selection. SpeechT5/MMS issues remain first-sample findings with unresolved cause. Preserve unchanged baseline settings for any full comparison; explicitly version later fixes/tuning. The planned five-model full development run remains 100 attempts, not completed by these five smoke samples.
