# Image development trials

The offline-tested `observatory.evaluate_image` adapter uses the installed stable-diffusion.cpp CLI, separately from gameplay. It never downloads weights. No new model results were collected during implementation.

## User-run commands

Preview the default schedule without launching a model:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_image
```

Run one entrance-hall compatibility image:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_image --execute --limit 1 --repetitions 1
```

Send the saved-results folder and any terminal error. Review its image/log before the full baseline:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_image --execute
```

The full default is ten images: five briefs with seeds 42/43. Every attempt starts a fresh process; wall times include loading, not warm inference alone. Hashing the checkpoint/runtime DLLs happens before inference and outside attempt timing. Default per-attempt timeout is 300 seconds (`--timeout` overrides). No retries or fallback images. Ctrl+C during an attempt records interruption and stops. Failures remain in attempted denominators.

## Configuration and evidence

`image_candidates.json` enables only the already installed SDXL Turbo. Historical Vulkan settings are retained: four steps, CFG 1, Euler, sgm_uniform, 512x512. This is a starting configuration, not proven optimal. Add alternatives only after checking local single-file checkpoint compatibility, exact revision/licence and supported settings. Strict configuration fields: ID, model identity, checkpoint path, revision, steps, CFG, sampler, scheduler. Relative checkpoint paths resolve against project root. `--config path.json` selects another configuration. Candidates run sequentially, reversing order for repetition two; equal seeds do not imply equivalent randomness.

Unique folders retain dataset/protocol snapshots and hashes, runtime/checkpoint hashes, exact prompts/argument lists, runtime logs, images, flushed results and summary. The full schedule is saved before inference. Preview creates no model outputs or artifact hashes and works without installed weights. Execution refuses missing runtime/checkpoint files before creating a run.

PNG checks validate CRCs, dimensions, compression and scanline encoding for non-interlaced 8-bit RGB/RGBA output. Other encodings fail the check. File integrity does not establish visual correctness. Complete `reviews.json` using `media_protocol.md`; ratings/content judgements start pending. Coherence applies to each full five-room set, not a smoke test. Runtime completion and PNG integrity are separate. Automatic RAM/VRAM and separate load/inference measurements are unavailable; inspect verbose runtime logs for device/timing evidence.

Generated evidence remains Git-ignored. Preserve the entire selected folder for submission, or explicitly stage only the reviewed run using `git add -f generated/image-evaluations/<run-id>` when preparing your own commit. Never include weights/runtime binaries. Source, configuration and instructions are Git-visible. Nothing was committed or pushed.

## Five-candidate target

The target is five distinct checkpoints per data space, not five unrelated architectures. Image candidates: SDXL Turbo, SD-Turbo, SD 1.5, SDXL Base 1.0 and DreamShaper 8 (a fine-tune). The shared 512px canvas tests the application constraint, not native-resolution superiority. Alternative compatibility, exact artifacts/licences, settings and resource fit remain unverified; no alternative downloads were performed.

Primary model cards checked for this shortlist: [SD-Turbo](https://huggingface.co/stabilityai/sd-turbo), [SD 1.5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5), [SDXL Base](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0), [DreamShaper 8](https://huggingface.co/Lykon/dreamshaper-8). Model-card examples do not prove pinned-runtime compatibility; do not blindly transfer Diffusers guidance values to another runtime.

Speech shortlist remains Piper Lessac, Kokoro-82M, SpeechT5, MMS-TTS-eng and XTTS-v2. Only Piper has historical local feasibility evidence. Alternative adapters, voice/licence choices and resource checks remain future work. Five language candidates already have development results; final selection and independent human evaluation remain incomplete.
