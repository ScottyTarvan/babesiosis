# SV-G2 spec: severity literature extraction, schema v2

Written 2026-11-12 before any extraction. SV-G2 opens no dog-level outcomes file, so the outcome lock does not apply; this spec fixes the scope, the method and the quality checks so that they are not tuned after the extractions are seen. `exposure.md` records that no outcomes file was opened.

## Scope

- `/core/data/severity/shortlist.csv` rows with `tier` A or B and `source_format` not `abstract`: 117 articles (116 CB, 1 BG), 99 independent units (cohort from `/core/cohorts.json`, else the article).
- The 10 pilot articles (`CB006 CB017 CB040 CB050 CB053 CB141 CB145 CB202 CB238 CB263`) are re-extracted under v2 first as the calibration batch (B00), without access to the pilot files. Their v2 rows are then compared with the pilot rows (same comparison as the blind second extraction).
- The 34 abstract-only tier B articles are not extracted here (later sensitivity set).
- BG007 is in the scope by the package rule; it is background, not canine evidence, and is flagged in every count.

## Method

- Schema v2 = `/core/data/severity/association_schema.json` plus the package additions, built by `scripts/make_schema_v2.py` into `association_schema_v2.json`. Additions beyond the package text, all as enum values: `summary_type` also allows `mean and SEM`, `mean and range`, `other`; `load_method` also allows `smear, site not stated` and `other`; `setting` also allows `field survey` and `mixed`; `sample_timing` also allows `days after treatment` and `mixed`; `euthanasia_included` also allows `not applicable`; a top-level `not_extracted` list records what could not be extracted.
- Guide: `/core/data/severity/EXTRACTION_GUIDE.md` with `EXTRACTION_GUIDE_v2.md`.
- Batches of 9 to 10 articles (`batches/batches.json`), one sub-agent per batch, each writing only `batches/<batch>/<ID>.json` and `marker_map_additions/<batch>.csv`. The owner checks a sample of each batch against the article text before copying files to `extractions/`.
- Checker: `scripts/check_associations.py` (restored from `8d4c6d9`, extended for v2). Every quote must be `exact` or `near`.

## Quality check (blind second extraction)

- Random 20% sample: 24 of 117 articles, `random.seed(20261112)`, `random.sample(sorted(ids), 24)` (list in `batches/batches.json`). A second agent extracts these without seeing the first extraction, into `second/<ID>.json`.
- Agreement, computed by `scripts/agreement.py`:
  1. Outcome class: for each article, the set of outcome classes in the two extractions; agreement = share of article × class pairs found by both (Jaccard over the union), and the share of articles with identical sets.
  2. Direction and significance: rows matched on (article, canonical marker, outcome class); where several rows match, the first by row order on each side. Agreement = share of matched pairs with the same direction group (up, down, null/no difference, other) and the same `significant` value. Cohen's kappa for `significant` on matched pairs.
  3. Coverage: share of first-extraction (article, marker, outcome class) keys also found by the second, and the reverse.
- Differences on matched pairs are reviewed by the owner against the text and resolved in the primary file; the resolution is logged in `out/agreement_resolutions.csv`.

## Results to report (experiment SV-G2-01-literature-extraction)

Descriptive only, no test: articles covered and articles with no severity association; records by marker class and canonical marker (articles and independent units, not rows); records by host and parasite factor; by species; by outcome class; by cohort and independent unit; definition components; setting and sample timing; load method on parasitaemia rows; `not_extracted` by reason; checker results; agreement figures. Counting unit is the independent unit; rows are never counted as evidence.

## What would count against the extraction

Agreement on significance or direction below 0.8 on matched pairs, or coverage below 0.7, means the extraction is not reliable enough for SV-03 without a second pass; the report would say so.
