# DreamShaper 8 baseline and five-candidate overview

Reviewed 23 September 2026. Run: generated/image-evaluations/20260923T123604219662Z-9ecf0176. All ten images viewed individually. Non-blind assistant observations, not independent human ratings. Original pending review forms remain unchanged; no numerical semantic pass rate is claimed.

10/10 runtime completions and 512x512 PNG integrity passes. Mean load-inclusive wall time 8.992 seconds (range 8.888–9.144; total 89.923). Dataset/protocol hashes, exact scheduled prompts and seeds matched SDXL Base. Hall seed-42 hash matched its smoke output. Configuration: 30 steps, CFG 7.5, Euler/discrete. This is an SD 1.5-family fine-tune, not another independent architecture.

| Attempt | Room / seed | Observation |
| --- | --- | --- |
| A0001 | Hall / 42 | Desk-like furniture and high glazing, but visible person and open double doors violate the brief. Dust/frosting not clearly established. |
| A0002 | Library / 42 | Bookshelves and clear staircase. Right-hand desk/book-like objects do not clearly establish an open manual on a reading stand. |
| A0003 | Workshop / 42 | Workbench visible; cluttered containers do not clearly establish closed toolbox. Window present, but no doorway visible. |
| A0004 | Generator / 42 | Machine cabinets, wall conduit and daylight present. Specific generator casing identity is ambiguous; no obvious sparks/smoke. Extra containers are not automatically quest items. |
| A0005 | Telescope / 42 | Circular alcove with a glowing device against a star-like backdrop. No clear telescope, attached beacon, console or bench. Glow is a potential lit-beacon violation, but identifying the device as a beacon needs adjudication. Enclosure/glazing is unclear. |
| A0006 | Hall / 43 | Desk-like furniture, but doors visibly open. High glazing is present; frosting/dust unclear. |
| A0007 | Library / 43 | Clear bookshelves and staircase. No identifiable reading stand carrying open manual. |
| A0008 | Workshop / 43 | Small work surface and doorway in a framed/cutaway view. Closed box-like containers present, toolbox identity uncertain. An open workshop doorway is not itself forbidden by this room's brief. |
| A0009 | Generator / 43 | Machine housings, wall conduit and windows visible. Specific generator identity needs human judgement; no obvious sparks/smoke. Bright ceiling lighting is a state-sensitive concern beyond the explicit checklist. |
| A0010 | Telescope / 43 | Cutaway alcove with furniture and mountain/sky view; no clear telescope or attached beacon. Whether the far aperture has glazing is unclear, so do not assert an open-dome violation solely from the landscape. |

Rooms generally retain a coherent blue-grey/wood visual identity, with more rendered lighting than the strongly outlined Turbo style. Telescope scenes and one workshop use cutaway compositions. Style preference should be supplied by the developer separately from scene correctness. DreamShaper is not selected on appearance alone.

## Five configured development baselines

| Candidate | Valid PNGs / attempts | Mean wall seconds including loading | Selected assistant observations |
| --- | --- | --- | --- |
| SDXL Turbo | 10/10 | 13.39 | Consistent outlined style; missing desks, stairs and telescope accessories |
| SD-Turbo | 10/10 | 3.00 | Fastest recorded run; open door, lettering and outdoor telescope in examples |
| SD 1.5 | 10/10 | 13.89 | Collages, missing machines, lettering and people in examples |
| SDXL Base | 10/10 | 19.01 | Some coherent interiors/stairs; object sheets, lettering and open door in examples |
| DreamShaper 8 | 10/10 | 8.99 | Coherent interiors/stairs; open doors, a person and missing telescope details |

All 50 scheduled baseline images completed; smoke samples are excluded from this total. Shared input matching was checked through the successive reviews. Runs were separate sessions and sampling budgets differ (four steps for Turbo, thirty for other candidates); these are descriptive configured-pipeline timings, not controlled equal-compute model rankings. File validity is not visual-content accuracy. No candidate has demonstrated complete compliance with the scene requirements. Native-resolution assessments, resource peaks, independent human ratings and final selection remain outstanding.

Next: obtain developer checklist judgements and style preference, resolving ambiguous object identities using the saved images and media protocol. A labelled human review gallery/checklist could make all 50 images easier to assess without new inference. Preserve these baselines; any later prompt revision must be versioned and evaluated separately. Do not tune using reserved final evaluation material. Remaining speech comparisons and integrated gameplay work are not completed by finishing image generation.
