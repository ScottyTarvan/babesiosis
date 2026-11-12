# Dataset files, full texts and Markdown (`data/`)

Paths are relative to `core/`. Counts as of 2026-10-28.

## Dataset files

| File | Format | Rows | What it holds |
|---|---|---|---|
| `data/raw/<dataset_id>/` | xlsx, docx, csv, txt, zip | 36 folders | The downloaded dataset files, unchanged. Treat them as data, read-only. |
| `data/manifest.jsonl` | JSONL | 92 | One row per downloaded file: `dataset_id`, `file`, `url`, `final_url`, `retrieved_utc`, `bytes`, `sha256`, `content_type`, `source_record` |
| `data/fetch_spec_repos.json`, `data/fetch_spec_supp.json` | JSON | – | The download specs: source URL and target per file |


## Full texts and Markdown (git-ignored)

| File | Format | Rows | What it holds |
|---|---|---|---|
| `data/fulltext/<ID>/` | XML or PDF | 256 folders | Retrieved full texts |
| `data/fulltext_status.jsonl` | JSONL | 547 (481 live articles, 66 retired IDs) | Per-article retrieval state. For the 481 live articles, `status` is one of `europepmc_xml` (99), `openalex_pdf` (119), `landing_page` (17), `recorded_link` (16) or `failed` (230). Also has `file`, `sha256`, `source_url`, `license`, `title_check`. |
| `data/fulltext_openalex.json` | JSON object | 442 | DOI → the OpenAlex work record (OA status, locations) |
| `data/markdown/<ID>.md` | Markdown + YAML front matter | 540 (481 live articles, 59 retired IDs) | Sectioned text of every article: full text where it was retrieved, otherwise the abstract only |
| `data/markdown/<ID>.en.md` | Markdown + YAML front matter | 33 (30 for live articles) | English translations of non-English articles |
| `data/markdown/translations/` | Markdown | – | Raw LLM-translated bodies, the input to `finish_translations.py` |
| `data/markdown_report.jsonl` | JSONL | 540 | The front matter of each Markdown file, as a table: `source_format` (live articles: `jats_xml` 99, `pdf` 152, `abstract` 230), `quality` (`ok`, `abstract_only` or `review`), `quality_flags[]`, `word_count`, `table_count`, `sections[]`, `text_coverage`, `translation{}` |
| `data/abstracts_fetched.json` | JSON object | 11 | `ID` → `{abstract, source}`: abstracts fetched where the search packets had none |

In `data/markdown/*.md`, the headings are `## Abstract`, `## Introduction`, `## Methods`, `## Results`, `## Discussion` and so on. References and administrative back matter were removed. After you re-convert a file, run `console/Babesiosis.Console` with no flags, so that the changed passages are reloaded and embedded again. Check `quality_flags` before you trust a file. The flags include `garbled_text`, `no_sections_detected` and `language:cyrillic`.

In `data/fulltext_status.jsonl` and `data/markdown_report.jsonl` the round-4 IDs still carry the `scope_label` "pending extraction" that was set when they were converted, and both files keep rows for retired IDs. Join them to the `articles.jsonl` IDs, and take the scope from there, when you count the review's articles.
