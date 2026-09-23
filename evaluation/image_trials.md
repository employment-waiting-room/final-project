# Image development trials

## Offline human review gallery

The prepared `generated/image-review-gallery.html` embeds all 50 baseline images; open it directly in a browser. Rebuild offline with `.\.venv\Scripts\python.exe -m observatory.image_gallery`. The builder checks saved dataset/image hashes and leaves original results/reviews untouched. No models or network requests are used. Source: observatory/image_gallery.py and image_gallery.html.

Enter your name, then review images using Previous/Next or the image selector (grouped by room and seed). For each required/forbidden detail choose present, absent or unclear. Rate scene clarity and adherence to the displayed style separately, adding observations for failures/uncertainty. After viewing full sets, rate five-room coherence separately for each candidate/seed and record your preferred style with a reason. A developer review is not a blind or independent user study; candidate names are visible.

Browser storage is best-effort, especially with local files. Export review JSON regularly and before closing; the browser saves it to your Downloads folder or asks for a location. Partial exports retain pending fields. Resume using the import control; wrong-gallery imports are rejected and replacement requires confirmation. Send the exported file path for analysis. Original evidence is not edited. Content pass is derived only for completed image forms: all required present and all forbidden absent; unclear never counts as pass. Review completeness does not guarantee correctness or replace reviewer judgement.

Gallery and exports contain submission evidence but are not automatically committed: generated/ remains ignored. Preserve exported reviews deliberately with the selected image runs. No human ratings were prefilled.

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

### DreamShaper 8 preparation (23 September)

Configuration: `evaluation/image_candidates_dreamshaper8.json`. Use creator repository `Lykon/DreamShaper`, revision `228d79cb20811466f5c5710aa91f05dabd0b8a14`, file `DreamShaper_8_pruned.safetensors` (approximately 2.13 GB). Published SHA-256: `879db523c30d3b9017143d56705015e15a2cb5628762c11d086fed9538abd7fd`. [Artifact metadata](https://huggingface.co/Lykon/DreamShaper/blob/main/DreamShaper_8_pruned.safetensors). This is the standard version-8 SD 1.5-family checkpoint, not the LCM, inpainting or XL variants, and not a fifth independent architecture. The repository metadata labels licensing as `other`; retain its model card and resolve exact applicable terms before final distribution rather than assuming a permissive licence. No separate LICENSE file was listed in the checked repository metadata.

Predeclared settings match the SD 1.5 trial: 30 steps, CFG 7.5, Euler/discrete, unchanged 512px prompts/seeds. Use the checkpoint without extra embeddings, LoRAs or external VAE. These are starting comparison settings, not claimed optimal settings. Runtime/decoding compatibility remains subject to smoke review.

Download only this file from the pinned revision, verify the SHA-256 above and retain README.md as model-card provenance. Then run:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_image --config evaluation/image_candidates_dreamshaper8.json --execute --limit 1 --repetitions 1
```

Send the saved folder or error before removing the limit/repetition flags for the ten-image baseline. No weights were downloaded or executed during preparation.

### SDXL Base preparation (23 September)

Configuration: `evaluation/image_candidates_sdxl_base.json`. Official checkpoint revision `462165984030d82259a11f4367a4eed129e94a7b`, file `sd_xl_base_1.0.safetensors`, approximately 6.94 GB. Published SHA-256: `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`. [Artifact](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/462165984030d82259a11f4367a4eed129e94a7b/sd_xl_base_1.0.safetensors); [licence](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/462165984030d82259a11f4367a4eed129e94a7b/LICENSE.md) identified as OpenRAIL++ in repository metadata.

Predeclared trial settings: 30 steps, CFG 7, Euler/discrete and the shared 512px canvas. This tests the application constraint, not SDXL's native-resolution quality. Use the single-file checkpoint's embedded VAE for the smoke test, with the pinned runtime's default SDXL Conv2D scaling path; no separate VAE, refiner or LoRA is added. Inspect decoded output and logs before full evaluation; if decoding fails, preserve that failure and explicitly revise the configuration rather than silently substituting assets. Local compatibility and resource headroom are unmeasured until the user runs it. Sampling settings are project choices, not a claim of optimal tuning or equal compute with Turbo.

After user-managed download, SHA verification and licence retention, run:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_image --config evaluation/image_candidates_sdxl_base.json --execute --limit 1 --repetitions 1
```

Send the saved folder or error before running the full baseline. Existing configurations and model results remain unchanged. No weights were downloaded or executed during preparation.

### SD 1.5 preparation (23 September)

Configuration: `evaluation/image_candidates_sd15.json`. Pinned maintained mirror revision `451f4fe16113bff5a5d2269ed5ad43b0592e9a14`; checkpoint `v1-5-pruned-emaonly.safetensors`, approximately 4.27 GB. Published SHA-256: `6ce0161689b3853acaa03779ec93eafe75a02f4ced659bee03f50797806fa2fa`. [Artifact source](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/451f4fe16113bff5a5d2269ed5ad43b0592e9a14/v1-5-pruned-emaonly.safetensors). Repository metadata identifies CreativeML OpenRAIL-M; preserve model-card/licence provenance separately from the runtime licence.

Predeclared starting settings: 30 steps, CFG 7.5, Euler, discrete scheduler, 512px. These are project trial choices, not claimed optimal settings. SD 1.5 is not a Turbo checkpoint, so reusing four steps/CFG 1 would not be a useful ordinary-generation baseline. Prompts, canvas and seeds remain shared; comparisons are of configured pipelines with different compute budgets, not equal-step model rankings. Installed-runtime compatibility remains subject to the user-run smoke test. Existing Turbo configurations/results remain unchanged.

After downloading and verifying the pinned checkpoint, run:

```powershell
.\.venv\Scripts\python.exe -m observatory.evaluate_image --config evaluation/image_candidates_sd15.json --execute --limit 1 --repetitions 1
```

Send the saved folder/error before the ten-image baseline. Remove `--limit 1 --repetitions 1` only after smoke review. No model download or inference was performed during preparation.

### SD-Turbo preparation (22 September)

Separate configuration: `evaluation/image_candidates_sd_turbo.json`. The default SDXL configuration and saved baseline remain unchanged. Pinned revision: `b261bac6fd2cf515557d5d0707481eafa0485ec2`; single-file `sd_turbo.safetensors`, approximately 5.21 GB. Published SHA-256: `3f067a1b943cf162f2b8f8588f6cf5824bd5b4c7d1d88d87164b9ca123616549`. [Pinned artifact metadata](https://huggingface.co/stabilityai/sd-turbo/blob/b261bac6fd2cf515557d5d0707481eafa0485ec2/sd_turbo.safetensors).

The pinned runtime's [README](https://github.com/leejet/stable-diffusion.cpp/blob/d04e895/README.md) lists SD-Turbo support. Actual compatibility remains to be tested locally. Four steps, CFG 1, Euler and sgm_uniform are retained as the shared trial configuration, not claimed as an optimised SD-Turbo setup. The model is designed for 1–4 steps; the runtime CFG convention differs from Diffusers' guidance setting. No negative prompt is added, and the exact fixture prompt remains unchanged. Any compatibility adjustment must be documented before the full baseline.

Licence provenance: the pinned repository contains the Stability AI Community License (July 5, 2024), not Apache/MIT weights. Retain and review the [revision-specific licence](https://huggingface.co/stabilityai/sd-turbo/blob/b261bac6fd2cf515557d5d0707481eafa0485ec2/LICENSE.md), including distribution/attribution terms, separately from the MIT runtime licence. Model file size does not establish RAM/VRAM requirements.

User-managed download from project root (no package installation required). The `.part` file supports resuming; the final filename is only created after hash verification. An existing final file is verified rather than overwritten:

```powershell
$sdTurboBase = 'https://huggingface.co/stabilityai/sd-turbo/resolve/b261bac6fd2cf515557d5d0707481eafa0485ec2'
if (-not (Test-Path 'models/sd_turbo.safetensors')) {
    curl.exe -L --fail --retry 3 -C - -o models/sd_turbo.safetensors.part "$sdTurboBase/sd_turbo.safetensors"
    if ($LASTEXITCODE -ne 0) { throw 'Download failed; retain the partial file and report the error.' }
    if ((Get-FileHash models/sd_turbo.safetensors.part -Algorithm SHA256).Hash -ne '3f067a1b943cf162f2b8f8588f6cf5824bd5b4c7d1d88d87164b9ca123616549') { throw 'Checkpoint hash mismatch; do not run.' }
    Move-Item -LiteralPath models/sd_turbo.safetensors.part -Destination models/sd_turbo.safetensors
}
if ((Get-FileHash models/sd_turbo.safetensors -Algorithm SHA256).Hash -ne '3f067a1b943cf162f2b8f8588f6cf5824bd5b4c7d1d88d87164b9ca123616549') { throw 'Checkpoint hash mismatch; do not run.' }
curl.exe -L --fail -o models/sd_turbo-LICENSE.md "$sdTurboBase/LICENSE.md"
if ($LASTEXITCODE -ne 0) { throw 'Licence download failed.' }
.\.venv\Scripts\python.exe -m observatory.evaluate_image --config evaluation/image_candidates_sd_turbo.json --execute --limit 1 --repetitions 1
```

Send the saved folder path and any error. Only after smoke review, run the full ten-image trial with the same command minus `--limit 1 --repetitions 1`. This is a separate session from SDXL, so compare visual content first; timings are not a controlled interleaved benchmark. No downloads or inference were performed while preparing this configuration.

The target is five distinct checkpoints per data space, not five unrelated architectures. Image candidates: SDXL Turbo, SD-Turbo, SD 1.5, SDXL Base 1.0 and DreamShaper 8 (a fine-tune). The shared 512px canvas tests the application constraint, not native-resolution superiority. Alternative compatibility, exact artifacts/licences, settings and resource fit remain unverified; no alternative downloads were performed.

Primary model cards checked for this shortlist: [SD-Turbo](https://huggingface.co/stabilityai/sd-turbo), [SD 1.5](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5), [SDXL Base](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0), [DreamShaper 8](https://huggingface.co/Lykon/dreamshaper-8). Model-card examples do not prove pinned-runtime compatibility; do not blindly transfer Diffusers guidance values to another runtime.

Speech shortlist remains Piper Lessac, Kokoro-82M, SpeechT5, MMS-TTS-eng and XTTS-v2. Only Piper has historical local feasibility evidence. Alternative adapters, voice/licence choices and resource checks remain future work. Five language candidates already have development results; final selection and independent human evaluation remain incomplete.
