# Speech model asset downloads

## Isolated CPU runtime setup

Prepared 23 September 2026, after the 32-file asset receipt was reviewed. Run from the project root:

```powershell
.\.venv\Scripts\python.exe scripts/setup_speech_runtimes.py --install
```

This user-run command installs Python packages into `.venv-speech-hf` (SpeechT5/MMS), `.venv-speech-kokoro`, and `.venv-speech-xtts`. The existing gameplay/Piper environment is not modified; no activation is required. Python 3.11 is required. Omit --install for a command preview. Use --profile hf, kokoro or xtts to retry one profile after reviewing a failure. Existing isolated environments are reused; the script does not delete them or silently change pins.

PyTorch/torchaudio 2.8.0 use the official CPU wheel index. CPU is the initial portability choice, not a claim of GPU incompatibility or measured performance. Other top-level pins: transformers 4.57.6, numpy 1.26.4, soundfile 0.13.1, librosa 0.11.0, sentencepiece 0.2.1; Kokoro 0.9.4 with Misaki 0.9.4; maintained coqui-tts 0.27.5. These are metadata-compatible candidate configurations, not yet successfully installed/tested on this machine. Coqui documentation says PyTorch must be separately installed for this release family, with torchcodec additionally required from PyTorch 2.9; choosing 2.8 avoids that additional audio dependency. Transitive dependencies remain resolver-selected and are captured in pip reports/freezes, not claimed to be fully locked.

Kokoro's environment installs spaCy's en_core_web_sm 3.8.0 wheel plus English Misaki dependencies including espeakng-loader. This is an explicit supporting language-model download, not one of the five speech candidates. Native phonemiser loading and actual G2P still require later smoke testing. Package downloads consume additional disk space beyond the 3.21 GB speech assets; isolated environments each contain their own installed libraries. No CUDA package stack, new voice checkpoint or synthesis is requested by this setup.

After installation each profile runs pip check and an import-only check of relevant classes with Hugging Face offline flags and Python socket connections blocked. No model instances are created or checkpoints loaded. Success therefore establishes package importability only, not successful speech, usable voices, fully offline synthesis or complete runtime compatibility. Full model-load/synthesis tests remain a later user-run step. Installed package inventories, pip install reports, successful-profile freezes and setup command/status history are saved under generated/speech-runtime-setup. Failures stop subsequent profiles; send the error and evidence folder. Terminal output is not automatically copied into a log.

Sources checked: [Coqui installation](https://coqui-tts.readthedocs.io/en/latest/installation.html), [Kokoro usage](https://github.com/hexgrad/kokoro), [SpeechT5 API](https://huggingface.co/docs/transformers/model_doc/speecht5), [PyTorch installation](https://pytorch.org/get-started/locally/), and release-specific PyPI metadata. No package installation or speech inference was performed by the assistant during preparation.

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
