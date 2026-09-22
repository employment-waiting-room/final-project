# Model candidates and comparison plan

Research date: 11 September 2026. This is a shortlist, not measured evidence that alternatives are superior. Existing local results are recorded in development_log.md. No downloads, installations, or inference runs were performed for this research step.

## Shortlist

Update, 22 September: the agreed target is now **five candidates per data space**. Language development runs covered Qwen3:4b, Gemma3:4b, Llama3.2:3b, Phi4-mini:3.8b and Granite3.3:2b. Image shortlist: SDXL Turbo, SD-Turbo, SD 1.5, SDXL Base 1.0, DreamShaper 8. Speech shortlist: Piper Lessac, Kokoro-82M, SpeechT5, MMS-TTS-eng, XTTS-v2. Only the original image/speech baselines have local feasibility evidence. The historical two-candidate research below is incomplete for this expanded target. See [image trial preparation](evaluation/image_trials.md) for current sources, commands and limitations. Alternative artifacts, licences and runtime settings remain to be verified. The current media protocol uses two repetitions (seeds 42/43), superseding the old timing proposal below.

| Role | Existing baseline | Alternative for later trial | Reason and practical requirements |
| --- | --- | --- | --- |
| Intent and narrative | Ollama qwen3:4b, Q4_K_M; tested locally | Ollama gemma3:4b, Q4_K_M, listed tag digest a2af6cc3eb7f, approximately 3.3 GB | A different model family at a comparable parameter scale using the existing runtime. The listing requires Ollama 0.6 or later. Test text only, with 4096 context initially; Gemma's vision capability is not a substitute for image generation. |
| Illustration | stabilityai/sdxl-turbo, sd_xl_turbo_1.0_fp16.safetensors; tested with stable-diffusion.cpp Vulkan | stabilityai/sd-turbo, sd_turbo.safetensors, listed approximately 5.21 GB | A distinct SD 2.1-derived distilled model, rather than another SDXL runtime. Current stable-diffusion.cpp documents SD-Turbo support. Compatibility with the installed pinned build still needs a smoke test. |
| Narration | Piper 1.8.0, en_US-lessac-medium ONNX; tested on CPU | hexgrad/Kokoro-82M v1.0 via the community kokoro-onnx runtime, kokoro-v1.0.onnx plus voices-v1.0.bin | Different speech model family. Runtime documents approximately 300 MB standard weights (voice data/dependencies extra). Use CPU for the initial comparison; choose and record one English-US voice before testing. Python/package compatibility must be verified before installation. |

Download sizes are not peak RAM/VRAM requirements. Based on the existing Ryzen 7 9700X, RX 7800 XT and approximately 16 GB system RAM, these are plausible trial candidates, not guaranteed fits. Run GPU models sequentially and record unloading/loading conditions. Capture full model hashes/revisions, runtime versions and dependencies at trial time because tags and main branches can change.

## Sources and licensing provenance

- [Gemma Ollama artifact](https://ollama.com/library/gemma3:4b): size, quantisation, runtime requirement, tag identity, and custom Gemma terms. Do not describe Gemma as Apache-licensed.
- [SD-Turbo model card](https://huggingface.co/stabilityai/sd-turbo): distinct SD 2.1 base and low-step generation. The authors recommend SDXL Turbo for quality/prompt understanding; this is their claim, not our measured result.
- [SD-Turbo files](https://huggingface.co/stabilityai/sd-turbo/tree/main): single-file checkpoint name and size. Downloading the whole repository is unnecessary for the planned runtime.
- [SD-Turbo licence](https://huggingface.co/stabilityai/sd-turbo/blob/main/LICENSE.md): retain the licence associated with the actual downloaded revision. This is a custom Stability licence, not a generic permissive software licence; historical revisions may differ.
- [stable-diffusion.cpp](https://github.com/leejet/stable-diffusion.cpp): documented model/runtime support. Current documentation does not prove the installed older build works with this exact checkpoint.
- [Kokoro model](https://huggingface.co/hexgrad/Kokoro-82M): Apache 2.0 weights.
- [Kokoro ONNX runtime](https://github.com/thewh1teagle/kokoro-onnx): MIT wrapper, required model and voice files, and indicative model sizes. ONNX conversion/runtime provenance must be recorded separately from original weights.
- Existing Qwen Apache 2.0, SDXL Turbo checkpoint licence, Piper GPL engine and Lessac dataset/voice licence distinctions are recorded in development_log.md. Preserve the exact baseline artefact licences when assembling submission provenance; do not assume an engine licence covers every voice or model.

## Planned comparison protocol

World specification and labelled fixtures come before alternative downloads and comparative inference. No alternative is selected as the winner yet.

1. Define supported actions and targets, state prerequisites, and acceptable clarification/rejection. Add known failures to development cases. Reserve unseen phrasings for final evaluation.
2. Compare language models on identical semantic inputs and output schemas with a documented common context/output budget. Record model-specific template/settings differences. Measure raw interpretation separately from local guards and engine outcomes; test narrative separately from intent.
3. Compare image models on the same five briefs at 512 by 512 with documented supported sampling settings. Use several seeds, preserve failures, and assess required/forbidden facts and visual style. Equal seeds do not imply equivalent images across models.
4. Compare speech using the same approximately ten passages and fixed voice per model. Record pronunciation, omissions, intelligibility, loading time, synthesis time and audio duration; listen without model labels where practical. Do not infer model superiority from voice preference alone.
5. Start with one load-inclusive run and three warm repetitions for timing on development inputs, then adjust only if variation warrants it. Record RAM/VRAM measurement method and its sampling limits; do not substitute model file size for memory consumption.
6. Keep first-attempt outputs and failures, distinguish model-level accuracy from combined-policy accuracy, and report resource/quality trade-offs. After selection and tuning, freeze configurations before held-out evaluation.

Proposed targets for review before final evaluation: no invalid prerequisite/state transitions in engine tests; at least 90% exact action/target accuracy on supported held-out requests; report ambiguity and unsupported categories separately; no silent execution on tested ambiguous requests; narrative schema compliance at least 95% before fallback; zero critical puzzle-state contradictions in accepted evaluation scenes; warm intent response within 3 seconds and accepted text within 6 seconds as provisional typical-latency goals; fresh illustration within 20 seconds; speech synthesis faster than audio playback. These are design targets, not university thresholds or achieved results. Report distributions and sample sizes instead of hiding misses behind averages. Resource targets must be grounded in measured headroom before concurrency is introduced.

## Remaining preparation

- Review these provisional targets against the final world and user experience.
- Complete exact baseline/alternative licence and version manifests before comparative trials.
- Fill resource-measurement gaps during planned trials rather than rerunning everything immediately.
- Next: user-run image smoke test, evidence review, then full image trials and alternative setup. World/action and media development fixtures now exist. Broader free-roam remains paused.
