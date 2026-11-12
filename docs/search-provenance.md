# Search and extraction provenance (`search/`)

Paths are relative to `core/`. Counts as of 2026-10-28.

These are the working files. Use them for questions about how a record got in or why it was excluded. Do not use them to describe the included set: the final values are in `articles.jsonl`.

The review window (2006-10-23 to 2026-10-23) was searched in two parts (`search/rounds.json`): rounds 1–3 (2016-10-23 to 2026-10-23) and round 4 (2006-10-23 to 2016-10-22). Round 4 is complete: searched, screened, extracted, cohort-linked, dataset-mapped, run through the NLP and synthesised (2026-10-28).

| File | Rows | What it holds |
|---|---|---|
| `queries.jsonl`, `crossref_queries.jsonl`, `openalex_queries.jsonl`, `repo_queries.jsonl` | 8, 8, 1, 16 | Query strings, run dates and hit counts |
| `hits.jsonl` | 4,159 | Raw query → PMID hits |
| `citation_hits.jsonl` | 5,299 | Backward and forward citations (`seed`, `direction`, `pmid`, `title`, `year`) |
| `repo_hits.jsonl` | 906 | Dataset repository search hits |
| `candidates.jsonl`, `candidates_r2.jsonl`, `candidates_r3.jsonl`, `candidates_crossref.jsonl`, `candidates_openalex.jsonl`, `candidates_round2_all.jsonl` | 1,006, 181, 596, 88, 1,042, 269 | Deduplicated candidate records with abstract, MeSH terms and `found_by[]` |
| `screening_r1.jsonl`, `screening_r2.jsonl`, `screening_r3.jsonl` | 1,006, 269, 596 | Screening decisions per candidate `key`: `decision`, `exclude_reason`, `rationale`, `batch` |
| `screen_batches/*.md` | – | The batches given to the screening agents |
| `packets/<ID>.json` | 541 | Extraction input per article: the source record and abstract |
| `extraction_records.jsonl` | 541 | Raw agent extraction (`CB` and `BG001`). Has `dataset_leads[]`, `cohort_description` and `related_publications[]`, which `articles.jsonl` does not have. |
| `extraction_checks_r1.json`, `extraction_checks_r3.json`, `r4/extraction_checks.json` | – | Verification passes on the extraction (`ok`, `fixes`) |
| `supporting_records.jsonl` | 36 | The `HU` and `BG` records (also in `articles.jsonl`) |
| `human_papers.json`, `background_papers.json`, `human_comparators_raw.json` | 27, 9, 10 | Inputs for the comparator and background papers |
| `dataset_assessments.json`, `dataset_extra.json` | 22, 24 | Agent dataset assessments, the input to `datasets.jsonl` |
| `dataset_negative_checks.jsonl` | 401 | Articles with dataset status 4 or 5: `article_id`, `status_code`, `basis` |
| `fulltext_checks.jsonl` | 154 (rounds 1–3; round 4: `r4/fulltext_checks.jsonl`, 221) | Europe PMC checks of data availability statements, supplements and repository links |
| `duplicates.json` | 3 | Duplicate record → canonical key |
| `synthesis/<CAT>.md`, `<CAT>_secondary_digest.md`, `CROSS.md`, `QUESTIONS.md`, `inputs.json` | – | Category syntheses (2006–2026, NLP categories), one-line digests of the secondary-tagged articles, cross-cutting themes and the research questions. These are the sources for `research-map.md`. `inputs.json` lists the primary and secondary notes of each category. |
| `rounds.json` | – | The search rounds: `id`, `dir`, `start`, `end`, `run_date`, `status`, and `recheck` (earlier keys to screen again) |
| `r4/` | – | Round 4 (2006-10-23 to 2016-10-22; complete), same file names as above, plus `screening.jsonl`, `screening_criteria.md`, `EXTRACTION_GUIDE.md`, `extraction_checks.json` and `PIPELINE.md` (the end-to-end brief). `candidates_all.jsonl` is the merged screening input. Records already screened in rounds 1–3 are left out and listed in `*_prior_overlap.jsonl`. Records that already have an article ID (in-window `BG` papers, retired IDs) are kept, with `existing_id` and `existing_retired` |
