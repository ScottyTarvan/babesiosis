# Dataset files, full texts and Markdown (`data/`)

Paths are relative to `core/`. Counts were taken on 2026-10-28; re-count before you quote them as current.

## Dataset files

| File | Format | Rows | What it holds |
|---|---|---|---|
| `data/raw/<dataset_id>/` | xlsx, docx, csv, txt, zip | 36 folders | The downloaded dataset files, unchanged. Treat them as data, read-only. |
| `data/manifest.jsonl` | JSONL | 92 | One row per downloaded file: `dataset_id`, `file`, `url`, `final_url`, `retrieved_utc`, `bytes`, `sha256`, `content_type`, `source_record` |
| `data/inspection/<dataset_id>.json` | JSON | 36 | File path → structure: format, sheets or tables, `n_rows`, `n_cols`, preview of the first rows |
| `data/fetch_log.jsonl` | JSONL | 92 | Download attempts: `dataset_id`, `url`, `status`, `bytes` |
| `data/fetch_spec_repos.json`, `data/fetch_spec_supp.json` | JSON | – | Input specs for `fetch_datasets.py` |

To view a sheet, run `python -I scripts/table_dump.py "<file>[::member]"`.

## Tidy datasets and experiments

| File | Format | What it holds |
|---|---|---|
| `data/tidy/<dataset_id>.json` | JSON | One tidied dataset, written by `scripts/tidy_<dataset>.py`: `dataset` (metadata from `datasets.jsonl`, file hash from the manifest, cleaning `notes[]`), `variables[]` (`code`, `name`, `source_name`, `unit`, `data_type` N/O/C/D/T, `domain`, `derived`, `derived_from[]`, `include_default`, `ref_low`, `ref_high`, `description`, `levels{}`), `subjects[]` (`code`, `group_label`, `outcome_label`) and `observations[]` (`subject`, `variable`, `time_point`, `value_num`, `value_text`, `value_date`). Long format: one observation per subject × variable × time point. |
| `data/experiments/<code>.json` | JSON | One experiment run, written by `scripts/experiment_*.py`: `experiment` (code, name, method, dataset, `parameters`, script and its hash, `run_utc`, counts, `summary`), `associations[]` (one per tested pair: test, estimate, n, `p_value`, `p_adjusted`, `significant`, `trivial`, `direction`, `detail`), `cluster_assignments[]` (subject-level groupings, empty for pairwise runs) and `results[]` (method-specific payloads: `spearman_matrix`, `variable_clusters`, `top_associations`, `run_notes`). |

Current files: `DS05.json` (article 1, 150 dogs, 65 variables, 39 in the default test set) and `EXP01-DS05-pairwise.json`. Variables marked `derived` are the authors' grades and classes computed from measured columns; `derived_from` lists arithmetic parents (MCV from haematocrit and RCC, globulin from total protein and albumin, and so on), and a pair with its parent counts as `trivial`, not a finding. The raw files in `data/raw/` are never changed; re-running the tidy script rebuilds the JSON from them.

## Full texts and Markdown (git-ignored)

| File | Format | Rows | What it holds |
|---|---|---|---|
| `data/fulltext/<ID>/` | XML or PDF | 256 folders | Retrieved full texts |
| `data/fulltext_status.jsonl` | JSONL | 547 (481 live articles, 66 retired IDs) | Per-article retrieval state. For the 481 live articles, `status` is one of `europepmc_xml` (99), `openalex_pdf` (119), `landing_page` (17), `recorded_link` (16) or `failed` (230). Also has `file`, `sha256`, `source_url`, `license`, `title_check`. |
| `data/fulltext_log.jsonl` | JSONL | 1,029 | Every retrieval attempt (`id`, `tier`, `url`, `outcome`, `time`) |
| `data/fulltext_missing.md` | Markdown | – | Articles to retrieve by hand, and files to check by eye |
| `data/fulltext_openalex.json` | JSON object | 442 | DOI → the OpenAlex work record (OA status, locations) |
| `data/markdown/<ID>.md` | Markdown + YAML front matter | 540 (481 live articles, 59 retired IDs) | Sectioned text of every article: full text where it was retrieved, otherwise the abstract only |
| `data/markdown/<ID>.en.md` | Markdown + YAML front matter | 33 (30 for live articles) | English translations of non-English articles |
| `data/markdown/translations/` | Markdown | – | Raw LLM-translated bodies, the input to `finish_translations.py` |
| `data/markdown_report.jsonl` | JSONL | 540 | The front matter of each Markdown file, as a table: `source_format` (live articles: `jats_xml` 99, `pdf` 152, `abstract` 230), `quality` (`ok`, `abstract_only` or `review`), `quality_flags[]`, `word_count`, `table_count`, `sections[]`, `text_coverage`, `translation{}` |
| `data/markdown_report.md` | Markdown | – | Rendered conversion report, with a translations table |
| `data/abstracts_fetched.json` | JSON object | 11 | `ID` → `{abstract, source}`: abstracts fetched where the search packets had none |

In `data/markdown/*.md`, the headings are `## Abstract`, `## Introduction`, `## Methods`, `## Results`, `## Discussion` and so on. References and administrative back matter were removed. PDF-derived files are cleaned of running heads, page numbers and, in author manuscripts, margin line numbers and the one-line-per-row layout (re-run 2026-11-05; after re-converting, run `console/Babesiosis.Console` with no flags so the passages whose text changed are reloaded and re-embedded). Check `quality_flags` before you trust a file. The flags include `garbled_text`, `no_sections_detected` and `language:cyrillic`.

In `data/fulltext_status.jsonl` and `data/markdown_report.jsonl` the round-4 IDs still carry the `scope_label` "pending extraction" that was set when they were converted, and both files keep rows for retired IDs. Join them to the `articles.jsonl` IDs, and take the scope from there, when you count the review's articles.
