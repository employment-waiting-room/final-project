# SD 1.5 baseline: assistant visual inspection

Reviewed 23 September 2026. Run: generated/image-evaluations/20260923T105950381566Z-9838fd29. All ten images inspected individually. These are non-blind assistant observations, not independent human ratings. Original pending review forms remain unchanged; no numerical semantic pass rate is claimed.

10/10 runtime completions and 512x512 PNG integrity passes. Mean load-inclusive wall time 13.886 seconds, range 13.360–14.976, total 138.857. Seed-42 hall image hash matches the smoke image. Dataset/protocol hashes, exact prompts and seeds match the SD-Turbo baseline. SD 1.5 used 30 steps, CFG 7.5 and Euler/discrete, versus four steps, CFG 1 and Euler/sgm_uniform for the Turbo runs. These are different configured pipelines in separate sessions, not an equal-compute or controlled timing benchmark.

| Attempt | Room / seed | Observation |
| --- | --- | --- |
| A0001 | Hall / 42 | Stylised closed blue door, no clear dusty desk. High frosted glazing unclear. |
| A0002 | Library / 42 | Bookshelves and central pedestal-like structure. No clear open manual on reading stand or stairway. Prominent text-like lettering on rear wall/ceiling conflicts with the no-lettering brief, without establishing readable puzzle instructions. |
| A0003 | Workshop / 42 | Object-sheet composition with prominent readable QUEST lettering. No coherent room/workbench/doorway arrangement or clear closed toolbox. Small shapes should not automatically be classified as quest items. |
| A0004 | Generator / 42 | Mostly empty room with bright window. No recognisable generator casing or wall conduit. |
| A0005 | Telescope / 42 | Abstract central structure and large blue opening. No recognisable telescope, attached beacon, console or bench. Whether blue area is glazing or open sky is unclear. |
| A0006 | Hall / 43 | Collage of doors and architectural details, rather than one establishing room view. Human figures visible in lower central panel, violating no-people constraint. No clear dusty desk. |
| A0007 | Library / 43 | Multi-panel library collage with bookshelves. No clear required stairway or open manual on reading stand. |
| A0008 | Workshop / 43 | Collage of box/chest designs and isolated small objects, not a workshop establishing view. No workbench or doorway. Whether any box qualifies as a closed toolbox is uncertain. |
| A0009 | Generator / 43 | Empty room with wall panels and conduit-like lines. No clear generator casing; daylight source unclear. |
| A0010 | Telescope / 43 | Telescope-like assembly outdoors beneath open sky; violates enclosed-dome/no-open-sky requirements. Small person-like forms at the base need human adjudication rather than an asserted people count. No clear attached beacon, console or bench. |

Both seeds miss core scene objects; seed 43 repeatedly uses collage layouts. Palette is often muted, but visual presentation varies from flat illustration to more rendered scenes. These results do not establish suitability for gameplay. They also do not prove that every possible SD 1.5 prompt/configuration performs poorly: the prompts are shared development inputs and have not been optimised for this candidate.

Descriptive mean wall times: SDXL Turbo 13.388 seconds, SD-Turbo 3.004 seconds, SD 1.5 13.886 seconds. All three produced 10/10 intact files; all showed scene-content failures. Keep visual accuracy separate from file validity and speed. No final winner or human preference rating is assigned.

Next: prepare SDXL Base 1.0 as candidate four, verifying exact checkpoint, VAE/runtime requirements and settings before user-managed downloads or inference. Preserve current baselines and shared prompts. The common 512px canvas remains an application constraint and is not a claim about native-resolution performance.
