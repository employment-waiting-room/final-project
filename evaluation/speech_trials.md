# Speech development runner

Implemented preparation, 23 September 2026. Real synthesis remains user-run. From the project root, run one shared passage once per candidate:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_speech --models piper kokoro speecht5 mms xtts --limit 1 --repetitions 1
```

Send the printed saved-results folder and any errors. This launches five sequential CPU synthesis attempts with the already downloaded local weights and isolated runtimes. The first preparation hashes selected local asset files; allow time before the first audio result. Per-attempt timeout defaults to 300 seconds; --timeout changes it. Stop with Ctrl+C; an in-progress attempt is recorded as interrupted. Failed attempts are retained, without retries or replacement audio. A completed schedule may include failures: inspect valid_audio and individual errors, not status alone.

After reviewing all smoke outputs and resolving compatibility problems, the full command omits --limit 1 --repetitions 1. That schedules 100 outputs: ten passages, five models, two repetitions. Do not start it before smoke review. --models can select any subset for diagnosis. Candidate order reverses on repetition two; seeds are 42/43 where supported. Piper's current public synthesis path is not seeded, explicitly recorded as unsupported. Equal requested seeds do not imply equivalent randomness across different models.

## Local adapters and voices

| Candidate | Runtime | Fixed initial voice/settings |
| --- | --- | --- |
| Piper | Existing .venv | en_US-lessac-medium; existing defaults, CPU |
| Kokoro | .venv-speech-kokoro | af_heart, American English, speed 1, non-transformer G2P; local voice tensor and weights |
| SpeechT5 | .venv-speech-hf | cmu_us_slt_arctic-wav-arctic_b0258.npy read directly from the downloaded archive; default generation and local HiFi-GAN |
| MMS | .venv-speech-hf | English single-voice checkpoint; default VITS synthesis |
| XTTS | .venv-speech-xtts | Supplied Ana Florence speaker, English; temperature .75, top-k 50, top-p .85, repetition penalty 10, length penalty 1, speed 1, text splitting enabled |

PyTorch uses CPU, evaluation/inference mode and four intra-op threads. Piper thread settings remain library defaults. Speaker names/settings are frozen before inspecting generated audio; accents/voice preference still need listening review and are not assumed equivalent. Missing supplied speaker or phonemiser is a visible failure, not an automatic voice substitution. Kokoro refuses a missing fallback phonemiser to avoid the library's silent out-of-dictionary word skipping. Local spaCy package existence is checked before pipeline construction. No personal voice recording is needed.

Workers set Hugging Face offline flags and block Python socket connections; they use explicit local model paths. No automatic model downloads, remote dataset scripts, hosted inference or gameplay state changes. Python socket blocking is a safeguard for these adapters, not a general OS network sandbox. Native library/import compatibility and actual model-loading paths remain to be verified by the user smoke run.

## Evidence and interpretation

Each unique generated/speech-evaluations folder contains frozen dataset/protocol/worker snapshots, source hashes, actual local asset hashes, full schedule, exact request texts/settings, subprocess command lists, per-attempt runtime logs, worker results/package versions, audio WAVs, flushed results, summary and pending listening forms. Generated evidence remains Git-ignored; retain the selected run folders and completed review forms deliberately for submission. Originals are not overwritten.

Each attempt launches a fresh process. Wall time includes startup; worker load time includes imports, checkpoint loading and G2P setup. Synthesis timing includes tokenisation/phonemisation, generation and audio encoding. Real-time factor is synthesis seconds divided by saved audio duration, excluding load time. This is not warm-server throughput. Process overhead and asset hashing are not incorrectly counted as synthesis. Resource peaks remain unavailable, not zero.

Automated checks require complete nonempty mono PCM16 WAV data with nonzero samples; record sample rate, duration, peak sample, clipped-sample fraction and file hash. Neural outputs are checked for finite values before PCM conversion. Nonzero audio may still contain silence, missing words, noise or bad pronunciation; clipping observations do not establish quality. Listen against the exact passage and use media_protocol.md for word-error, intelligibility and pacing ratings. Review fields remain null until actually rated; no automated semantic pass or substitute fallback is assigned.

Software tests use fake worker subprocesses and synthetic WAV files. They verify orchestration and failure handling, not actual five-model synthesis compatibility. No completed comparative speech results are claimed at implementation time.
