# Database (SQL Server)

`../console/Babesiosis.Console` (from `core/`) loads `articles.jsonl` and the `articles/*.md` notes into SQL Server. The schema is in `Database/schema.sql`. The `babesiosis-local-db` MCP server connects to it. The database holds articles only. It has no datasets, NLP concepts or full texts.

- `dbo.category`: the 11 category codes.
- `dbo.article`: one row per article. `article_code` is the article ID. The note sections are split into `abstract_summary`, `authors_conclusion`, `reviewer_interpretation`, `key_limitations` and `evidence_basis`. `species`, `dataset_ids` and `source_json` are JSON columns. `embedding` is `VECTOR(1536)`.
- `dbo.article_category`: secondary tags (`tag_type = 'secondary'`) and the `HU` comparator categories (`'comparator'`). The primary category is in `article.primary_category_id`.
- `EXEC dbo.search_articles @question = N'…', @top, @category_code, @from_year, @to_year, @max_distance`: semantic search by cosine distance. A distance under about 0.6 is usually on topic.

The database is only as current as the last loader run. If it disagrees with `articles.jsonl`, the file is correct.
