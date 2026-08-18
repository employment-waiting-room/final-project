# SpoilerSense task list

## 1. Define the study

- [x] Select the initial target format: Standard.
- [ ] Define the prediction window after release, for example 90 or 180 days.
- [ ] Define ground truth for low, medium, and high competitive viability.
- [ ] Define the score scale and scoring factors.
- [ ] Record inclusion and exclusion criteria for cards, images, and decklists.

## 2. Research and select models

- [ ] Identify at least two candidates for card detection/cropping.
- [ ] Identify at least two OCR candidates.
- [ ] Identify at least two local language-model candidates.
- [ ] Identify at least two embedding/retrieval candidates.
- [ ] Create a small representative test set of spoiler images.
- [ ] Compare accuracy, speed, hardware requirements, and integration difficulty.
- [ ] Document selected and rejected models with evidence.

## 3. Build the historical datasets

- [ ] Obtain historical card data with release dates and oracle text.
- [ ] Obtain historical competitive decklists/results for the target format.
- [ ] Store source, date, format, and licensing/terms information for every dataset.
- [ ] Create dated snapshots so records after a cutoff cannot be retrieved.
- [ ] Create a test split containing cards from historical releases.
- [ ] Confirm that test-set cards and post-release results are excluded from each backtest.

## 4. Implement the pipeline

- [ ] Create the project structure and environment configuration.
- [ ] Implement image upload and validation.
- [ ] Implement card detection, crop, perspective correction, and image enhancement.
- [ ] Integrate OCR and capture field-level confidence where available.
- [ ] Parse OCR output into a structured card schema.
- [ ] Integrate the language model for text correction and mechanic summaries.
- [ ] Validate model output against the schema and retain the original OCR text.
- [ ] Build semantic search over historically eligible card and deck data.
- [ ] Implement an explainable viability-scoring function.
- [ ] Generate an evidence-grounded final report.
- [ ] Add error states for unreadable images, uncertain extraction, and insufficient evidence.

## 5. Test and evaluate

- [ ] Unit-test parsers, cutoff filters, score calculations, and schema validation.
- [ ] Test image handling with different resolutions, rotations, glare, borders, and layouts.
- [ ] Measure card-crop success rate.
- [ ] Measure OCR field accuracy.
- [ ] Assess relevance of retrieved comparable cards.
- [ ] Run historical backtests for multiple sets and cutoff dates.
- [ ] Compare predicted viability with post-release deck usage and results.
- [ ] Analyse false positives, false negatives, and uncertain predictions.
- [ ] Conduct a small user test with MTG players.
- [ ] Iterate on the interface and explanation based on feedback.

## 6. Finalise the project

- [ ] Prepare reproducible installation and run instructions.
- [ ] Document the architecture and model orchestration.
- [ ] Document datasets, cutoffs, and leakage controls.
- [ ] Document model selection experiments and discarded approaches.
- [ ] Summarise evaluation results, limitations, ethics, and future work.
- [ ] Prepare demonstration spoiler images and expected outputs.
