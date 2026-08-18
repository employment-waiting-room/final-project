# SpoilerSense

## Predicting the competitive viability of unreleased Magic: The Gathering cards

### Project summary

SpoilerSense is a decision-support application that accepts an image of an unreleased Magic: The Gathering (MTG) card from a spoiler or reveal. It extracts the card's information, compares its mechanics with historically released cards and competitive deck archetypes, then produces an explainable prediction of the card's likely competitive viability in a selected format.

Unlike a card-identification application, SpoilerSense is designed for cards that do not yet exist in public card databases. Its goal is not to recognise the card by name or artwork; its goal is to assess a newly revealed card using its visible characteristics and rules text.

## Research question

> To what extent can pretrained vision, OCR, language, and semantic-retrieval models predict the competitive viability of unreleased MTG cards from spoiler images and historical metagame data?

## Problem statement

Players see card spoilers before a set releases and want to know whether a card is likely to be competitively useful. Making that judgement requires accurately reading a sometimes low-quality image, interpreting rules text, comparing the card with historical precedents, and considering a format's current metagame. These tasks are difficult to automate with conventional rules alone.

## System objective

Given a spoiler image, produce a Standard-format assessment containing:

- structured card data, including name, mana cost, colours, type, rules text, and power/toughness or loyalty where applicable;
- a confidence score for the extraction;
- comparable previously released cards and relevant deck archetypes;
- an explainable competitive-viability score, for example from 0 to 10;
- a plain-language rationale and caveats.

## Model orchestration

| Stage | Pretrained model type | Candidate model | Input | Output |
| --- | --- | --- | --- | --- |
| 1. Card isolation | Object detection / segmentation | YOLO or SAM | Spoiler image | Cropped, aligned card image |
| 2. Data extraction | Optical character recognition | PaddleOCR or EasyOCR | Card crop | Raw visible card text |
| 3. Rules interpretation | Language model | Local model through Ollama | OCR text | Corrected, structured card fields and mechanic summary |
| 4. Historical comparison | Text embedding / semantic retrieval | SentenceTransformers model | Structured card text | Similar released cards, archetypes, and deck contexts |
| 5. Decision support | Explainable scoring logic plus language generation | Scoring rules and local LLM | Retrieval evidence and card data | Viability score and explanation |

Stages 1--4 use distinct pretrained models. Stage 5 integrates their outputs rather than treating the models as isolated demonstrations.

## Viability score

The viability score should be evidence-based rather than a claim of certainty. Initial factors may include:

- mana efficiency and rate relative to comparable cards;
- similarity to cards that appeared in competitive decks;
- fit with known deck archetypes and colour identities;
- availability of enabling cards in the chosen historical metagame;
- card type and interaction with common strategies;
- extraction and retrieval confidence.

The report should distinguish between **high-confidence evidence** and **speculative judgement**.

## Scope

The first working version will:

- support Standard, the selected constructed format;
- analyse clear digital spoiler/reveal images;
- use a curated historical card database and decklist dataset;
- return a viability prediction, comparable cards, and an explanation;
- be evaluated using historical spoiler-time backtesting.

It will not attempt to predict limited-play viability, card prices, all formats, or every possible card layout in the first iteration.

## Historical backtesting and data leakage control

Evaluation must simulate the information available when a card was spoiled.

For each historical set used in testing:

1. Select cards from the set as unseen test examples.
2. Set a cutoff date before that set's release.
3. Exclude the test set, later sets, and all later decklists/results from the retrieval database.
4. Feed the system the historical spoiler image and only the information available before the cutoff.
5. Record its predicted score, comparable cards, and explanation.
6. Compare the prediction with observed post-release competitive evidence.

Possible ground-truth measures include tournament deck inclusion rate, number of successful decklists containing the card, top-cut appearances, and sustained use over a defined post-release period.

## Evaluation

### Per-model evaluation

- **Card isolation:** successful card-crop rate and crop quality on varied spoiler layouts.
- **OCR:** field-level accuracy for name, mana cost, type line, rules text, and stats.
- **Rules interpretation:** accuracy of structured fields against a verified card record.
- **Semantic retrieval:** relevance of retrieved comparable cards, assessed using manual labels or expert/player ratings.

### End-to-end evaluation

- exact structured-card-data accuracy;
- rate of useful completed reports from a spoiler image;
- correlation between predicted viability and observed post-release play;
- classification accuracy for categories such as low, medium, and high viability;
- user feedback on clarity, trust, and usefulness of the explanation.

## Example output

```text
Target format: Standard
Extraction confidence: 0.91
Predicted viability: 7.8 / 10 (medium-high confidence)

Comparable historical cards:
- [card A] -- similar repeatable value effect
- [card B] -- comparable mana cost and archetype role

Potential archetype fit: Rakdos Midrange

Rationale: The card provides an efficient source of repeatable value and resembles
historical cards used by midrange decks. Its score is reduced because the current
historical card pool contains limited supporting synergies.
```

## Expected deliverables

- a working application or prototype;
- a reproducible historical card and decklist data pipeline;
- tested orchestration of at least three pretrained models;
- automated tests for core data-processing and scoring components;
- model-comparison and evaluation evidence;
- a report documenting rejected model choices, design decisions, limitations, and user testing.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Poor OCR on stylised or low-resolution spoilers | Test multiple OCR models; use image pre-processing; expose confidence and allow correction. |
| Future-data leakage in backtesting | Enforce dated datasets and test-set exclusion; log each cutoff and dataset version. |
| LLM hallucination | Use structured prompts, retrieval evidence, validation rules, and clearly label uncertain conclusions. |
| Incomplete historical deck data | State coverage limits and restrict claims to the chosen dataset and format. |
| Score appears overly authoritative | Provide evidence, confidence, and uncertainty rather than only a single number. |
