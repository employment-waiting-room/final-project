# Speech model asset downloads

Prepared 23 September 2026. Run from the project root:

```powershell
.\.venv\Scripts\python.exe scripts/download_speech_models.py --download
```

Without --download the script only lists the plan. Download total: 3,213,907,015 bytes (3.21 GB), 32 files. Existing Piper Lessac ONNX/config remain in models/piper and are not downloaded again. No model inference or package installation occurs. Models/speech is Git-ignored; preserve download_receipt.json and selected provenance files deliberately for submission.

| Candidate / support asset | Local folder | Planned purpose |
| --- | --- | --- |
| hexgrad/Kokoro-82M original v1.0 weights, config, af_heart voice | kokoro | English-US initial voice; native weights instead of earlier proposed ONNX conversion |
| microsoft/speecht5_tts | speecht5 | Text model, tokenizer and processor files |
| microsoft/speecht5_hifigan | speecht5-hifigan | Required waveform vocoder, not a sixth speech candidate |
| Matthijs/cmu-arctic-xvectors | speecht5-speakers | Speaker-embedding archive for later fixed-voice selection; downloaded only, no dataset script executed |
| facebook/mms-tts-eng | mms-eng | English model, using safetensors rather than duplicate bin weights |
| coqui/XTTS-v2 | xtts-v2 | Model, vocabulary, config, supplied speakers and auxiliary files; later choose a supplied speaker rather than requesting personal voice recordings |

evaluation/speech_downloads.json pins every repository revision, exact file, size and published LFS SHA-256 or Git blob hash. The downloader saves under models/speech, verifies existing files, resumes .part files through curl.exe, verifies before renaming, and writes a full receipt only after all files pass. On failure, stop and send the error; rerunning skips verified files. Bad hashes are not silently overwritten. All failures remain explicit. Avoid running two downloader instances concurrently.

This completes only model-asset acquisition when the user command succeeds, not runnable/offline speech environments. Runtime packages, phonemisation dependencies, speaker selection/extraction, adapters and compatibility tests still require preparation. Kokoro's native path is an explicit change from the earlier ONNX proposal, chosen to retain author-published weights and voice provenance. No extra inference dependencies are installed into the existing environment in this step. A later frozen runtime plan may identify additional supporting downloads; do not claim all future setup is complete.

Primary sources: [Kokoro](https://huggingface.co/hexgrad/Kokoro-82M), [SpeechT5](https://huggingface.co/microsoft/speecht5_tts), [vocoder](https://huggingface.co/microsoft/speecht5_hifigan), [MMS English](https://huggingface.co/facebook/mms-tts-eng), [XTTS-v2](https://huggingface.co/coqui/XTTS-v2), [speaker embeddings](https://huggingface.co/datasets/Matthijs/cmu-arctic-xvectors). Preserve their distinct model/dataset terms; availability for download does not imply identical distribution rights. XTTS's supplied LICENSE.txt is included. Final licence review and chosen voice provenance remain part of selection work.

Image human review/selection is deferred at the user's request. Five language and five image candidates have development runs; this speech download step is preparation, not five measured speech comparisons.
