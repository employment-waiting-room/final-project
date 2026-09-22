# SDXL Turbo image baseline: assistant inspection

Reviewed 22 September 2026. Source: generated/image-evaluations/20260922T205805515147Z-e8e9aa6f. All ten images were viewed individually. This is a non-blind assistant review, not independent human ratings or an automated semantic score. Original pending review forms and outputs were preserved. No numeric content-pass rate is asserted: ambiguous details still need checklist adjudication.

Runtime: 10/10 completed, exit code zero; 10/10 passed 512x512 PNG integrity checks. Wall time including loading averaged 13.388 seconds (range 13.082–13.862; total 133.884). Each image used a fresh process. The log identifies AMD Radeon RX 7800 XT via Vulkan. Backend buffer allocations are not whole-system peak measurements. A runtime warning reports default VAE Conv2D scale 0.031; its visual effect has not been isolated. No change to settings was made based on this inspection.

| Attempt | Room / seed | Visible evidence and limitations |
| --- | --- | --- |
| A0001 | Hall / 42 | Closed panelled door and bright glazing; no clear dusty desk. Frosting unclear. Bookshelves and framed decorations dominate. Image SHA matches the earlier seed-42 smoke output exactly; one repeated output does not establish universal reproducibility. |
| A0002 | Library / 42 | Bookshelves and open books present. Ladders are not the required stairway; no clear reading stand carrying an open manual. |
| A0003 | Workshop / 42 | Work surfaces present. No clear doorway; closed toolbox identity uncertain among containers. A telescope-like instrument and guitar-like object are additional scenery. |
| A0004 | Generator room / 42 | Mechanical housings, wall pipes/conduit and windows/daylight present. Identifying a specific generator casing is somewhat ambiguous. No obvious smoke/sparks; small marks on panels need closer human judgement for lettering/indicator constraints. |
| A0005 | Telescope chamber / 42 | Telescope and enclosed, glazed dome visible. No clearly identifiable attached beacon housing or bench; wooden box arrangement is not a clear console. Visible landscape through glazing should not automatically be labelled an open dome. |
| A0006 | Hall / 43 | Closed panelled door with glazing; no clear dusty desk. Frosting unclear. Ceiling light appears bright; whether this implies power is outside the current explicit image checklist and merits later cache/state review. |
| A0007 | Library / 43 | Bookshelves and open book on seating visible. No stairway or clear reading stand with manual; ladders do not satisfy stairs. |
| A0008 | Workshop / 43 | Work surfaces and rear door visible. No clearly identifiable closed toolbox. Foreground shallow tray/box has exposed objects; whether it is the forbidden open toolbox is uncertain. |
| A0009 | Generator room / 43 | Machine housings and wall conduit visible; daylight source unclear. Detailed dials/panel marks need human review for readable indicators; do not equate every dial with readable text. |
| A0010 | Telescope chamber / 43 | Enclosed dome, large telescope-like assembly and right-side console-like furnishing. No clear attached beacon housing or bench. A small stool is not the requested bench. |

Both seeds share strong outlines and a blue-grey/wood palette across rooms, providing qualitative style-coherence evidence. Correct style does not compensate for absent puzzle-relevant scenery. No obvious people were identified; portable-item and tiny-lettering judgements remain for detailed human review rather than assumed passes.

The baseline demonstrates technical feasibility, not suitability for final gameplay assets. Preserve these prompts/settings for the next candidate comparison before tuning. Next preparation: verify the exact SD-Turbo single-file artifact, licence, installed-runtime compatibility and model-specific settings, then provide user-managed download/run commands. No models were downloaded or run during this review. Do not extrapolate five-model rankings from one candidate.
