# Data guide: which file answers which question

Paths are relative to `core/`. Rules for querying are in [/CLAUDE.md](../CLAUDE.md). ID schemes and codes are in [ids-and-codes.md](ids-and-codes.md).

## Articles

| Question | Use |
|---|---|
| Articles by category, species or country | `articles.jsonl` (`primary_category`, `secondary_tags`, `species[]`, `country`, `scope_label`) |
| What article X found; evidence strength | `articles/<ID>_*.md` |
| What the paper itself says | `data/markdown/<ID>.md` (`<ID>.en.md` = translation). Check the front matter: `source_format: abstract` means abstract only |
| Articles that report the same dogs | `cohorts.json`; `articles.jsonl` → `cohort_id` |
| Full-text retrieval status | `data/fulltext_status.jsonl`, `data/markdown_report.jsonl`. Both keep retired IDs and stale scope labels: join to `articles.jsonl` and take the scope from there |
| Semantic or "find similar" search | SQL Server `dbo.search_articles` (articles), `dbo.search_passages` (the papers' own text). See [database.md](database.md) |

## Datasets

| Question | Use |
|---|---|
| Downloadable datasets and their quality | `datasets.jsonl` (`status_code` = 1, `granularity`, scores, `suitable_questions`, `limitations`) |
| The files and contents of a dataset | `data/raw/<dataset_id>/`, `data/manifest.jsonl` |
| Why article X has no dataset | `search/dataset_negative_checks.jsonl` |

## Terms, categories and severity

| Question | Use |
|---|---|
| Disorder terms per article; which terms the dashboard shows, hides or merges | `data/terms/<ID>.json`; `data/terms/term_display.csv` (curated, edit by hand) |
| Diseases or syndromes that article X mentions or studies | `data/syndromes/article_concepts.csv` (`in_results_or_case` = studied) |
| How many articles mention concept Y | `data/syndromes/concept_summary.csv` |
| The exact sentence of a mention; negation | `data/syndromes/mentions.jsonl` (140 MB: stream or grep, never load whole) |
| NLP terms and summary for article X | `data/syndromes/article_terms.csv` / `.jsonl` |
| NLP category against agent category | `data/syndromes/article_categories.csv` |
| Markers tested against severity or outcome | `data/severity/associations.csv` (pilot, 10 articles; filter `quote_check`) |

`data/syndromes/` is not in every checkout. If it is absent, use `data/terms/` and the category fields in `articles.jsonl`.

## Search, screening and synthesis

| Question | Use |
|---|---|
| How the search was done; exclusions | `search/rounds.json`, `search/queries.jsonl`; `search/screening_r*.jsonl`, `search/r4/screening.jsonl` |
| Research gaps and questions | `search/synthesis/QUESTIONS.md`, `CROSS.md`, `<CAT>.md` (narrative only) |
| Articles with a clinical syndrome and a treatment with outcome | `search/clinical_treatment/combined_set.csv` (`source`, `decision`, `treatment_role`). The rescued excluded records are not in `articles.jsonl`. Detail: `search/clinical_treatment/README.md` |

## Caveats when you interpret the data

- CB510 and CB511 are one study published twice. Count them once.
- Most notes appraise the abstract only: full text was not retrieved for 230 of 481 articles.
- Some included articles predate the window: the 10 `BG` papers and 13 records with `older_foundational` = true.
