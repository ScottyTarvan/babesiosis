# Core outputs and table fields

Paths are relative to `core/`. Counts as of 2026-10-28.

## Core outputs (folder root)

| File | Format | Rows | What it holds |
|---|---|---|---|
| `articles.jsonl` | JSONL | 481 | **The main article table.** One record per article (`CB`, `HU` and `BG`). |
| `datasets.jsonl` | JSONL | 57 | **The main dataset table.** One record per dataset record. |
| `cohorts.json` | JSON object | 38 | `CH##` → `{label, certainty, basis, members[]}`. `certainty` is `confirmed` or `probable`. |
| `ids.json` | JSON object | 584 | Source key → `{id, filename, retired?, retired_reason?}` |
| `articles/<ID>_<year>_<slug>.md` | Markdown | 481 | One appraisal note per article: a metadata table, then *Abstract-derived summary*, *Critical interpretation* (evidence type, authors' conclusion, reviewer interpretation, key limitations) and *Evidence basis*. |

## `articles.jsonl` key fields

- Identity and bibliographic: `id`, `key` (`PMID:…` or `DOI:…`), `filename`, `title`, `authors[]`, `journal`, `volume_issue_pages`, `doi`, `pmid`, `pmcid`, `language`, `corrections`.
- Dates: `first_pub_date` (`YYYY`, `YYYY-MM` or `YYYY-MM-DD`; the earlier of the online and issue dates), `online_date`, `issue_date`, `date_note`.
- Scope: `scope_label`, `include_type` (`primary` 338, `case_report` 66, `review` 40, null for HU and BG).
- Study: `species[]` (`{name, status, method}`, where `status` is one of `confirmed`, `suspected`, `mixed` or `unspecified`), `species_short`, `host`, `country`, `design`, `sample_size` (free text), `n_infected_dogs` and `n_controls` (int or null), `cohort_id`.
- Classification: `primary_category` and `secondary_tags[]` (NLP categories for `CB` articles; null for HU and BG; free text for `BG001`), `category_source` (`nlp`, or `agent (NLP found no category)`), `category_confidence` (NLP `high` or `low`), `agent_primary_category` and `agent_secondary_tags` (the extraction agents' labels, kept for provenance), `evidence_type`, `one_sentence_finding`.
- Data availability: `abstract_available`, `fulltext_checked`, `fulltext_url`, `supplement_checked`, `repository_checked`, `data_availability_statement`, `dataset_ids[]`, `dataset_status_code`, `dataset_status`.
- Provenance: `source_links[]`, `access_date`, `verification_notes`.
- `HU` and `BG` records only: `study_type`, `comparator_categories[]`, `older_foundational`.

## `datasets.jsonl` key fields

- Identity: `dataset_id`, `title`, `repository`, `accession_or_doi`, `landing_url`, `direct_download_urls[]`, `licence`, `linked_articles[]`.
- Status: `status_code`, `status`, `verification_date`, `downloaded_files[]` (`{file, bytes, sha256}`), `unverified_fields[]`.
- Content, mostly on status-1 records: `species`, `design`, `granularity[]`, `raw_vs_processed`, `n_animals`, `n_animals_basis`, `n_samples`, `groups_and_controls`, `time_points`, `features`, `outcomes`, `data_dictionary`, `missingness`, `technical_requirements`, `files_summary`, `overlaps`.
- Assessment: `mechanistic_relevance`, `phenotype_richness`, `documentation` and `feasibility` (each 1–5), `priority_rank`, `rank_rationale`, `independent_source`, `suitable_questions`, `recommended_methods`, `limitations`.
- Many of these fields are prose with bullet lists inside one string. Read them; do not parse them.

Status codes are defined in [ids-and-codes.md](ids-and-codes.md#dataset-status-codes).
