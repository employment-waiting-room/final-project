# SDXL Base baseline: assistant inspection

Reviewed 23 September 2026. Run: generated/image-evaluations/20260923T120515449565Z-d094ed1a. All ten images viewed individually. Non-blind assistant observations, not independent human ratings. Original pending review forms remain unchanged. No numerical semantic pass rate is asserted.

10/10 runtime completions and 512x512 PNG integrity passes. Mean load-inclusive wall time 19.006 seconds (range 18.696–19.669; total 190.065). Dataset/protocol hashes, scheduled prompts and seeds matched the SD 1.5 baseline. Hall seed-42 image hash matched the prior smoke image. Configuration: 30 steps, CFG 7, Euler/discrete, embedded VAE. Separate sessions, differing candidate settings and the shared 512px task constraint limit speed/native-resolution quality comparisons.

| Attempt | Room / seed | Observation |
| --- | --- | --- |
| A0001 | Hall / 42 | Closed wooden-framed door with opaque-looking inset. No dusty desk; high frosted glazing unclear. Prominent sign lettering violates no-lettering constraint. |
| A0002 | Library / 42 | Bookshelves and a clear central stairway. No identifiable reading stand with open manual. |
| A0003 | Workshop / 42 | Work surfaces and box-like containers. No clear doorway or unambiguous closed toolbox. Bright lamp and spark-like lines add state-sensitive scenery; sparks are not an explicit forbidden item in this room's checklist, so flag separately from checklist failures. |
| A0004 | Generator / 42 | Machine casings and diffuse daylight visible. Curved pipe above large machine may satisfy wall conduit, but needs human judgement. No obvious smoke or sparks; machine identity remains somewhat stylised. |
| A0005 | Telescope / 42 | Curved glazed room with central instrument-like structure. Telescope, attached beacon and console are not clearly recognisable. Curved side seating may be a bench; enclosed dome geometry is unclear. Do not equate visible blue through glazing with an open sky violation. |
| A0006 | Hall / 43 | Door visibly open, violating closed-door requirement. No desk or clear high frosted glazing. |
| A0007 | Library / 43 | Six shelving/room fragments arranged as an object sheet, not one room view. No identifiable stairway or open manual on reading stand. |
| A0008 | Workshop / 43 | Sheet of building/box designs, not workshop interior. No clear workbench; closed boxes do not unambiguously establish toolbox identity. Signature-like marks at lower edge need lettering review. |
| A0009 | Generator / 43 | Sheet of isolated device designs with prominent label-like lettering. No room, wall conduit or evident daylight. Even if devices are generators, full scene requirements are not satisfied. |
| A0010 | Telescope / 43 | Object sheet including a lens/ring, lantern-like object, benches and text-covered page. No coherent telescope chamber/enclosed dome; no clearly attached beacon or console. Lettering present, but readable coordinates are not established. |

Seed-42 scenes generally retain an interior composition, whereas four seed-43 outputs become object sheets. This is an observed association in two seeds, not a demonstrated cause. No obvious people were identified. Required-object coverage, forbidden lettering and open-door errors prevent equating intact files with gameplay suitability.

Four configured image candidates now have full development baselines. Recorded mean wall seconds: SDXL Turbo 13.388, SD-Turbo 3.004, SD 1.5 13.886, SDXL Base 19.006. These are descriptive separate-session measurements, not equal-compute rankings. All showed content failures; no final winner or independent human preference is established.

Next: prepare DreamShaper 8 as the fifth checkpoint, verifying artifact provenance/licence and local runtime configuration before user-managed download and smoke testing. It is an SD 1.5-family fine-tune, not a fifth independent architecture. Preserve the current shared prompts and all baseline outputs before tuning.
