# Database (SQL Server)

`/console/Babesiosis.Console` loads `articles.jsonl` and the `articles/*.md` notes, then the papers' own text from `data/markdown/`, then the terms from `data/terms/`, into SQL Server. The schema is in `Database/schema.sql`; the search procedures are installed by `Database/Setup-SemanticSearch.ps1`. The `babesiosis-local-db` MCP server connects to it. The `data/syndromes/` NLP concepts are not loaded.

If the database disagrees with `articles.jsonl`, the file is correct.

## Articles, text and terms

- `dbo.category`: the 11 category codes.
- `dbo.article`: one row per article. `article_code` is the article ID. The note sections are split into `abstract_summary`, `authors_conclusion`, `reviewer_interpretation`, `key_limitations` and `evidence_basis`. `species`, `dataset_ids` and `source_json` are JSON columns. `embedding` is `VECTOR(1536)`. `has_full_text`, `text_source` (`abstract` / `jats_xml` / `pdf`), `text_quality`, `text_flags`, `text_language`, `text_translated` and `text_word_count` describe the paper's own text in `dbo.article_section`.
- `dbo.article_category`: secondary tags (`tag_type = 'secondary'`) and the `HU` comparator categories (`'comparator'`). The primary category is in `article.primary_category_id`.
- `dbo.article_section`: the paper's own text (`data/markdown/<ID>.md`, or the English translation `<ID>.en.md` when there is one) in passages of about 500 words, in reading order (`section_order`). `section_kind` normalises the heading (`abstract`, `introduction`, `methods`, `results`, `results_discussion`, `discussion`, `conclusion`, `case`, `limitations`, `abbreviations`, `body`, `other`); `heading` keeps the paper's own, as `Results > Pooled prevalence`. A long section is split into `chunk_count` parts. Abstract-only articles have one `abstract` passage. Each passage has its own `embedding`.
- `dbo.term`, `dbo.article_term`: the disorder terms per article (see [nlp-and-severity.md](nlp-and-severity.md)).
- `EXEC dbo.search_articles @question = N'…', @top, @category_code, @from_year, @to_year, @max_distance`: semantic search over articles by cosine distance, with `has_full_text`. A distance under about 0.6 is usually on topic.
- `EXEC dbo.search_passages @question = N'…', @top, @article_codes = N'["CB004","CB010"]', @section_kinds = N'["methods","results"]', @max_per_article, @category_code, @from_year, @to_year, @max_distance`: semantic search over passages, optionally inside a shortlist of articles. The web app's article agent uses the two procedures in that order: narrow to articles, then read passages, a section, or the whole paper.

Copyright: `data/fulltext/` and `data/markdown/` are git-ignored, and `dbo.article_section` holds the same text. Do not expose the table, or the agent's section and full-text tools, to anonymous users. `AppSettings:AiAgents:FullText = false` turns those tools off.

## Datasets and experiments

Tables `dbo.dataset`, `dbo.variable`, `dbo.subject`, `dbo.observation`, `dbo.experiment`, `dbo.association`, `dbo.cluster_assignment` and `dbo.experiment_result` exist. `Babesiosis.Console --datasets-only` fills the first four from `data/tidy/*.json`; that folder was deleted on 2026-11-12, so they are empty. The experiment tables are written by each experiment package: by its own writer, or by this loader from a load file `/experiments/<package>/out/db/<code>.json` (row content and steps: `/experiments/run-instructions.md`). New experiments use `dbo.experiment` and `dbo.experiment_result` only, with no dataset link. Column definitions are in `Database/schema.sql`. The web app reads these tables on its Experiments screen (`/experiments/<code>`), and its AI agent reads `dbo.experiment` and `dbo.experiment_result` to answer questions ([ai-agent.md](ai-agent.md)).
