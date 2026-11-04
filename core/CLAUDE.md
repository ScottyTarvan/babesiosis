# Canine babesiosis review: data catalogue

Rapid scoping review of canine babesiosis pathophysiology, window 2006-10-23 to 2026-10-23 (rounds 1–3 + round 4, all complete). Paths are relative to this folder. This file is an index: **read the detail files in `docs/` only when the task needs them.** How each file is produced: [scripts/README.md](scripts/README.md).

## Rules for querying

- **Use the structured files for whole-set questions:** `articles.jsonl` (481 articles), `datasets.jsonl` (57 records), the CSVs in `data/syndromes/`. Never count or filter from the rendered reports `index.md`, `datasets.md`, `research-map.md`.
- **Join on the article ID** (`id`, e.g. `CB050`). `key`, `pmid`, `doi` are not in every record.
- **Never load `data/syndromes/mentions.jsonl` whole** (140 MB). Stream or grep it for an `id`/`cui`; usually use `article_concepts.csv` or `concept_summary.csv` instead.
- **Run Python with `python -I`** from this folder. NLP scripts need `.venv-nlp`; the Markdown conversion needs `.venv`.
- **Git-ignored, this machine only:** `data/fulltext/`, `data/markdown/` (copyrighted full texts).
- **Free-text fields are not normalised** (e.g. `language` = `eng`/`en`/`English`). Match on keywords, not exact values.
- `data/fulltext_status.jsonl` and `data/markdown_report.jsonl` include retired IDs and stale scope labels; join to `articles.jsonl` and take scope from there.
- Counts in `docs/` were taken 2026-10-28; re-count before quoting them as current.

## IDs at a glance

- Article ID = `<prefix><3 digits>`, also the file-name prefix in `articles/`. `CB` = canine evidence (444), `HU` = human comparator (27), `BG` = background (10). **Do not count `HU`/`BG` as canine evidence.**
- IDs are stable and append-only; gaps are retired IDs, not errors (`ids.json`).
- Cohorts `CH##` (same animals, `cohorts.json`), datasets `DS##`/`S-CB###`/`P-…`/`R-…`/`RQ-…`, independent sources `SRC-A`…`SRC-O`.
- Categories: `ERY` erythrocyte/haemolysis · `INF` inflammation/immunity · `END` endothelium/perfusion · `COA` coagulation/DIC · `REN` renal · `PUL` pulmonary · `NEU` neurological · `CAR` cardiac · `MET` hepatic/metabolic/acid-base · `OXO` oxidative stress/omics/virulence · `SEV` multisystem severity/outcome. Assigned automatically by NLP, not human-reviewed.

Full ID rules, retirement history, category definitions, dataset status codes 1–5: [docs/ids-and-codes.md](docs/ids-and-codes.md).

## Which file answers which question

| Question | Use |
|---|---|
| Articles by category / species / country | `articles.jsonl` (`primary_category`, `secondary_tags`, `species[]`, `country`, `scope_label`) |
| What did article X find; evidence strength | `articles/<ID>_*.md` |
| What the paper itself says | `data/markdown/<ID>.md` (`<ID>.en.md` = translation); check front matter `source_format` (`abstract` = abstract only) |
| Articles reporting the same dogs | `cohorts.json`; `articles.jsonl` → `cohort_id` |
| Downloadable datasets and quality | `datasets.jsonl` (`status_code` = 1, `granularity`, scores, `suitable_questions`, `limitations`) |
| A dataset's files and contents | `data/raw/<dataset_id>/`, `data/manifest.jsonl`, `data/inspection/<dataset_id>.json` |
| Why article X has no dataset | `search/dataset_negative_checks.jsonl` |
| Diseases/syndromes article X mentions or studies | `data/syndromes/article_concepts.csv` (`in_results_or_case` = studied) |
| How many articles mention concept Y | `data/syndromes/concept_summary.csv` |
| Exact sentence of a mention; negation | `data/syndromes/mentions.jsonl` (stream/grep) |
| Disorder terms per article (one file each); which terms the dashboard shows, hides or merges | `data/terms/<ID>.json`; `data/terms/term_display.csv` (curated, edit by hand) |
| NLP terms and summary for article X | `data/syndromes/article_terms.csv` / `.jsonl` |
| NLP vs agent category | `data/syndromes/article_categories.csv` |
| Markers tested against severity/outcome | `data/severity/associations.csv` (pilot, 10 articles; filter `quote_check`) |
| Full-text retrieval status | `data/fulltext_status.jsonl`, `data/markdown_report.jsonl` (230 of 481 abstract-only) |
| Research gaps and questions | `research-map.md`; `search/synthesis/QUESTIONS.md`, `<CAT>.md` (narrative only) |
| How the search was done; exclusions | `search-log.md`; `search/screening_r*.jsonl`, `search/r4/screening.jsonl` |
| Semantic / "find similar" search | SQL Server `dbo.search_articles` |

## Detail files (read on demand)

| File | Read when you need |
|---|---|
| [docs/ids-and-codes.md](docs/ids-and-codes.md) | ID schemes, retired/replaced IDs, round-4 ID history, category definitions, dataset status codes |
| [docs/core-tables.md](docs/core-tables.md) | Root output files, and the field lists of `articles.jsonl` and `datasets.jsonl` |
| [docs/data-files.md](docs/data-files.md) | `data/raw`, manifest, inspection, full texts, Markdown conversion and quality flags |
| [docs/nlp-and-severity.md](docs/nlp-and-severity.md) | `data/syndromes/` NLP files, how categories are assigned, `data/severity/` |
| [docs/search-provenance.md](docs/search-provenance.md) | `search/` working files: queries, candidates, screening, extraction, synthesis, round 4 |
| [docs/database.md](docs/database.md) | SQL Server schema, `babesiosis-local-db` MCP, `dbo.search_articles` |

## Interpretation caveats

- Article counts are not independent evidence: use `cohort_id` (articles) and `independent_source` (datasets). CB510/CB511 are one study published twice.
- Most notes appraise the abstract only; full text was not retrieved for 230 of 481 articles.
- Every verified dataset is small for its feature count: no predictive ML, do not call clusters "subtypes".
- Some included articles predate the window: the 10 `BG` papers and 13 records with `older_foundational` = true.
