# SD-Turbo baseline: assistant visual inspection

Reviewed 22 September 2026. Run: generated/image-evaluations/20260922T211752221105Z-757a7092. All ten images viewed individually. Non-blind assistant observations, not independent human ratings or an automated semantic score. Original pending review forms were preserved; ambiguous details need human adjudication.

10/10 runtime completions and 512x512 PNG integrity passes. Mean load-inclusive wall time 3.004 seconds; range 2.909–3.308; total 30.036. Each attempt starts a fresh process. The seed-42 hall output hash matches its earlier smoke sample. No general reproducibility claim follows from that single repeat.

| Attempt | Room / seed | Observation |
| --- | --- | --- |
| A0001 | Hall / 42 | Closed wooden door present. No clear high frosted glazing; cropped side table does not establish dusty desk. Plaque has text-like marks, readability uncertain. |
| A0002 | Library / 42 | Bookshelves and books present. Central ladder-like structure is not a clear stairway; no clearly identifiable reading stand carrying an open manual. |
| A0003 | Workshop / 42 | Workbench present. Multiple boxes/baskets, but required closed toolbox is unclear; no doorway visible. Extra monitor and tools appear. |
| A0004 | Generator / 42 | Machine cabinets, wall pipes and rear window present. Specific generator identity uncertain. Panels have illuminated/coloured marks; readable indicators need human judgement. Bright ceiling lamps raise state-consistency concerns beyond the explicit checklist. |
| A0005 | Telescope / 42 | Telescope-like tube mounted across a globe under an enclosed ceiling. Bench-like foreground seating appears; attached beacon and console are not clear. Star motifs may be ceiling decoration rather than open sky; do not count an open-dome violation here without further evidence. |
| A0006 | Hall / 43 | Door is visibly open, violating closed-door requirement. Sign above doorway has lettering even though it is not clearly meaningful text. No dusty desk or clear frosted glazing. |
| A0007 | Library / 43 | Bookshelves and open book visible; no stairway. Table with mechanical device does not clearly satisfy reading stand with manual. |
| A0008 | Workshop / 43 | Workbench and globe dominate. No doorway; closed toolbox identity uncertain among containers. Additional loose objects appear, but they should not automatically be labelled quest items. |
| A0009 | Generator / 43 | Wall pipework and machine-like assembly present. Right-hand panel contains large digit-like symbols; readable indicator constraint needs human judgement. Diffuse daylight source unclear; prominent overhead lamp. |
| A0010 | Telescope / 43 | Large telescope-like assembly sits outside with open sky and mountains. Clearly violates enclosed-dome requirement and forbidden open sky. No clear attached beacon or console. |

Grey/wood palette and illustrative styling broadly recur, but seed-43 telescope scene breaks the indoor setting. No obvious people were identified. Required objects and forbidden details prevent treating attractive images or file validity as content success. No numerical semantic pass rate or cross-room rating was invented.

Compared with SDXL run 20260922T205805515147Z-e8e9aa6f, dataset/protocol hashes, exact scheduled prompts and seeds match. Both produced 10/10 valid files. SDXL mean wall time was 13.388 seconds versus SD-Turbo 3.004 seconds; separate sessions and loading/cache conditions prevent treating the difference as a controlled speed benchmark. Both missed required objects. SD-Turbo additionally showed clear open-door/open-sky violations in these samples; this is descriptive development evidence, not proof of universal model ranking.

Next: prepare Stable Diffusion 1.5 as candidate three, verify exact artifact/runtime settings, then supply user-managed download and smoke commands. Preserve both existing baselines and shared prompts. Human checklist reviews and remaining three image candidates are outstanding.
