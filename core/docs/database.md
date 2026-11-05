# Database (SQL Server)

`../console/Babesiosis.Console` (from `core/`) loads `articles.jsonl` and the `articles/*.md` notes, then the papers' own text from `data/markdown/`, then the terms from `data/terms/`, into SQL Server. The schema is in `Database/schema.sql`; the search procedures are installed by `Database/Setup-SemanticSearch.ps1`. The `babesiosis-local-db` MCP server connects to it. The database has no datasets or NLP concepts.

- `dbo.category`: the 11 category codes.
- `dbo.article`: one row per article. `article_code` is the article ID. The note sections are split into `abstract_summary`, `authors_conclusion`, `reviewer_interpretation`, `key_limitations` and `evidence_basis`. `species`, `dataset_ids` and `source_json` are JSON columns. `embedding` is `VECTOR(1536)`. `has_full_text`, `text_source` (`abstract` / `jats_xml` / `pdf`), `text_quality`, `text_flags`, `text_language`, `text_translated` and `text_word_count` describe the paper's own text in `dbo.article_section`.
- `dbo.article_category`: secondary tags (`tag_type = 'secondary'`) and the `HU` comparator categories (`'comparator'`). The primary category is in `article.primary_category_id`.
- `dbo.article_section`: the paper's own text (`data/markdown/<ID>.md`, or the English translation `<ID>.en.md` when there is one) in passages of about 500 words, in reading order (`section_order`). `section_kind` normalises the heading (`abstract`, `introduction`, `methods`, `results`, `results_discussion`, `discussion`, `conclusion`, `case`, `limitations`, `abbreviations`, `body`, `other`); `heading` keeps the paper's own, as `Results > Pooled prevalence`. A long section is split into `chunk_count` parts. Abstract-only articles have one `abstract` passage. Each passage has its own `embedding`.
- `dbo.term`, `dbo.article_term`: the disorder terms per article (see [nlp-and-severity.md](nlp-and-severity.md)).
- `EXEC dbo.search_articles @question = N'…', @top, @category_code, @from_year, @to_year, @max_distance`: semantic search over articles by cosine distance, with `has_full_text`. A distance under about 0.6 is usually on topic.
- `EXEC dbo.search_passages @question = N'…', @top, @article_codes = N'["CB004","CB010"]', @section_kinds = N'["methods","results"]', @max_per_article, @category_code, @from_year, @to_year, @max_distance`: semantic search over passages, optionally inside a shortlist of articles. The web app's article agent uses the two procedures in that order: narrow to articles, then read passages, a section, or the whole paper.

Copyright: `data/fulltext/` and `data/markdown/` are git-ignored, and `dbo.article_section` holds the same text. Do not expose the table, or the agent's section and full-text tools, to anonymous users. `AppSettings:AiAgents:FullText = false` turns those tools off.

The database is only as current as the last loader run. If it disagrees with `articles.jsonl`, the file is correct.

## Datasets and experiments

Loaded from `data/tidy/*.json` and `data/experiments/*.json` by `Babesiosis.Console --datasets-only` (DatasetLoader, then ExperimentLoader). Rebuild: run the tidy script, run the experiment script, then the console. The web app reads these tables on its Experiments screen (`/experiments/<code>`, endpoints `experiments-list-get` and `experiments-detail-get`); the screen renders the `interpretation` result as the note under the visuals, so every experiment script should write one.

- `dbo.dataset`: one row per tidied dataset (`dataset_code` = `DS05`), linked to `dbo.article` by `article_code`, with `source_sha256` from the manifest and the cleaning `notes` (JSON).
- `dbo.variable`: the variable dictionary per dataset (`variable_code`, `name`, `unit`, `data_type` N/O/C/D/T, `domain`, `derived`, `derived_from` JSON, `include_default`, `ref_low`, `ref_high`, `levels` JSON). `canonical_code` is empty until a second dataset is mapped to the same measurements.
- `dbo.subject`: one row per animal (`subject_code` = `BET001`), with `group_label` and `outcome_label` where the dataset has them.
- `dbo.observation`: long table, one row per subject × variable × `time_point` (`''` for single-visit data); `value_num`, `value_text` or `value_date`.
- `dbo.experiment`: one row per run (`experiment_code` = `EXP01-DS05-pairwise`), `method`, `parameters` JSON, script hash, counts and a plain-text `summary`.
- `dbo.association`: one row per tested pair (`variable_a_id`, `variable_b_id`, `test`, `estimate`, `estimate_label`, `n`, `p_value`, `p_adjusted`, `significant`, `trivial`, `direction`, `detail` JSON). Filter `trivial = 0` for findings; `IX_association_experiment` covers sorting by `p_adjusted`.
- `dbo.cluster_assignment`: subject-level groupings or labels from clustering and anomaly runs (`cluster_label`, `score` = silhouette for EXP02, combined anomaly rank score 0 to 1 for EXP06 with labels `outlier` / `typical`); first filled by `EXP02-DS05-clustering` (148 dogs, two Ward groups). The JSON fields are `subject_code`, `cluster_label`, `score`.
- `dbo.experiment_result`: the full method-specific outputs as JSON (`result_kind` = `spearman_matrix`, `variable_clusters`, `top_associations`, `run_notes` for EXP01; `pca_axes`, `cluster_summary`, `cluster_stability`, `cluster_crosstabs`, `run_notes` for EXP02; `anomaly_scores`, `top_outliers`, `score_agreement`, `run_notes` for EXP06; every run also writes `interpretation`), for heatmaps and cluster views. Methods without a dedicated web view are shown as formatted JSON.

Example: the strongest non-trivial findings of a run.

```sql
SELECT va.name AS a, vb.name AS b, x.test, x.estimate_label, x.estimate, x.n, x.p_adjusted, x.direction
FROM dbo.association AS x
JOIN dbo.experiment AS e ON e.experiment_id = x.experiment_id
JOIN dbo.variable AS va ON va.variable_id = x.variable_a_id
JOIN dbo.variable AS vb ON vb.variable_id = x.variable_b_id
WHERE e.experiment_code = 'EXP01-DS05-pairwise' AND x.significant = 1 AND x.trivial = 0
ORDER BY x.p_adjusted, ABS(x.estimate) DESC;
```
