# EXP10 CORPUS topics: Topic map of the canine articles versus the automatic categories

| Field | Value |
|---|---|
| Experiment code | `EXP10-CORPUS-topics` |
| Layer | 3 corpus |
| Method token | `topics` (goes in `experiment.method`) |
| Dataset(s) | `null`: the input is the article list (`articles.jsonl`) and article embeddings, not a tidy dataset; `associations` and `cluster_assignments` are therefore empty lists |
| Readiness | ready (SQL route) or ready with a weaker local substitute (see 3.1) |
| Python environment | `.venv-nlp` (Python 3.12). Present: scikit-learn 1.9.1, scipy 1.17.1, numpy 1.26.4. Absent: umap-learn, hdbscan, bertopic, sentence-transformers, pandas, pyodbc. scikit-learn 1.9.1 has `sklearn.cluster.HDBSCAN`, so the hdbscan package is not needed. Add to `scripts/requirements-experiments.txt` as optional lines: `umap-learn`, `pyodbc` (the latter only for the SQL route). If `umap-learn` is not installed, use the PCA fallback in 3.3 |
| Estimated build effort | medium |
| Suggested model for the building agent | sonnet: clear recipe, standard libraries, some judgment on cluster labels |
| Depends on | `articles.jsonl` only. For the SQL route, the articles must be loaded with embeddings (`dbo.article.embedding`) |

## 1. Question and hypotheses

Q1. Does a data-driven topic structure over the canine articles agree with the 11 automatic `primary_category` codes, and how strongly?
Q2. Which articles sit where topic and category disagree, or between topics, and so deserve a human look?
Secondary: how does topic prevalence change over four publication periods and across Babesia species?

No directional hypothesis. Expected from the way the labels are made: the category classifier (`scripts/categorise_articles.py`) scores UMLS concepts per organ system, whereas embeddings capture study type and subject (case report, prevalence survey, molecular diagnosis, treatment) as much as organ system. So topics will likely split by study aim and species as well as by organ system, and agreement with `primary_category` will be modest. A negative finding is also informative: adjusted mutual information (AMI) near 0 against `primary_category` while higher against `agent_primary_category` (or against the study aim) would mean the automatic categories are not recoverable from the meaning of the article text. Report whichever comes out.

## 2. Data

### 2.1 Sources

- `articles.jsonl` (481 records). Use records whose `id` starts with `CB`: 444 articles (`scope_label` `core canine evidence` 404 and `canine review` 40). Exclude `HU` (27, `human comparator`) and `BG` (10, `background`). The literal `scope_label` values are not `canine`; select on the `CB` prefix and assert the count is 444.
- Fields used: `id`, `title`, `primary_category` (11 codes ERY, INF, END, COA, REN, PUL, NEU, CAR, MET, OXO, SEV; counts among CB on 2026-11-05: ERY 96, INF 91, SEV 59, MET 50, REN 40, COA 40, OXO 21, CAR 18, END 14, NEU 8, PUL 7; none missing), `agent_primary_category` (present for all 444; differs from `primary_category` in 190 of 444), `secondary_tags` (list), `category_source` (`nlp` 428, `agent (NLP found no category)` 16), `category_confidence` (`high` 284, `low` 144, null 16), `first_pub_date` (ISO date string; years 2006 to 2026, no nulls among CB), `species` (list of objects with `name`, `status`, `method`; one entry in 382 articles, up to 11), `species_short` (string: `B. canis` 110, `B. gibsoni` 85, `mixed/unspecified` 65, `B. rossi` 37, `Babesia sp.` 22, `B. vogeli` 18, `B. canis canis` 13, `Babesia spp.` 4), `evidence_type`, `design`, `include_type` (`primary` 338, `case_report` 66, `review` 40), `abstract_available` (true for all 444), `fulltext_checked` (true 179, false 265), `one_sentence_finding`, `cohort_id`.
- Article text: `articles/<ID>_*.md` (appraisal notes: Abstract Summary, Authors' Conclusion, Reviewer Interpretation, Key Limitations; this is what the pipeline embeds, see 3.1) and `data/markdown/<ID>.md` or `<ID>.en.md` (full text, git-ignored, this machine only; check front matter `source_format`, `abstract` means abstract only).
- SQL Server (optional route): `dbo.article.embedding` `VECTOR(1536)`, `embedding_model` (Azure OpenAI `text-embedding-3-small`), `article_code` = article ID, `primary_category_id` joined to `dbo.category`. Passage embeddings (`dbo.article_section.embedding`, same model) are not needed here.
- `data/syndromes/article_categories.csv`, `article_terms.csv`, `concept_summary.csv` are described in `docs/nlp-and-severity.md` (`article_categories.csv` columns: `aim`, `nlp_primary`, `nlp_secondary`, `nlp_mentioned`, `confidence`, `agent_primary`, `agent_secondary`, `agree_primary`, `primary_evidence`, `score_<CAT>`, `mscore_<CAT>`). **On the machine where this spec was written, `data/syndromes/` does not exist**, so the headers could not be checked. The experiment must not depend on these files; everything it needs is in `articles.jsonl`. If the folder is present, an optional third label set, the study aim (`aim`), may be added in 3.6.
- No licences or independent-source letters apply (article metadata only).

### 2.2 Tidy file required

Not applicable (no tidy dataset).

### 2.3 Variables and filters

- Articles: the 444 CB articles. No exclusions. The 16 with `category_confidence` null are kept and flagged.
- Species groups for prevalence, from `species_short`: `B. canis` (merge `B. canis`, `B. canis canis`), `B. gibsoni`, `B. rossi`, `B. vogeli`, `Other/unspecified` (`Babesia sp.`, `Babesia spp.`, `mixed/unspecified`). Record the mapping in `run_notes`. Species is a stratifier, never pooled silently.
- Periods from the year of `first_pub_date`: 2006-2010, 2011-2015, 2016-2020, 2021-2026. 2026 is a partial year (window ends 2026-10-23).
- Topics with fewer than 10 articles are shown but their trend cells carry `low_n`.

## 3. Method

Defaults, all written to `experiment.parameters`: `seed` 20261105, `embedding_route` auto, `umap_n_components` 5, `umap_n_neighbors` 15, `umap_min_dist` 0.0, `umap_metric` cosine, `umap_2d_n_neighbors` 15, `umap_2d_min_dist` 0.1, `min_cluster_size` 8, `min_samples` 3, `cluster_selection_method` leaf, `top_terms` 10, `top_articles` 5, `review_prob_threshold` 0.5, `review_margin_threshold` 0.15, `alpha` 0.05, `ami_permutations` 2000, `bootstrap` 1000, `trend_permutations` 5000, `stability_runs` 10.

1. **Obtain article embeddings** (`--embeddings sql|local|auto`; auto tries sql, then local).
   - *SQL route (preferred; matches the production semantic search).* Read `article_code` and `embedding` from `dbo.article` for the 444 CB codes (cast the vector to text with `CAST(embedding AS NVARCHAR(MAX))`, which gives a JSON array). Database `Babesiosis` per `docs/database.md`; the building agent chooses the driver and connection (for example `pyodbc` with an ODBC connection string passed as `--connection`). Check `embedding_model` has one value across rows and record it; drop rows with null embedding and list them in `run_notes`. The pipeline embedded the text built by `ArticleSource.BuildEmbeddingText` in `console/Babesiosis.Console/Source/ArticleSource.cs` (title, finding, summary and appraisal sections of the article note), not the whole paper. Model: Azure OpenAI `text-embedding-3-small`, 1536 dimensions. It cannot be recomputed offline: `.venv-nlp` has no sentence-transformers and there is no Azure key in the repository.
   - *Local route (fallback when SQL is not reachable).* Build per article the text `title + one_sentence_finding + the note's Abstract Summary, Authors' Conclusion and Reviewer Interpretation` and, where the full text exists (`data/markdown/<ID>.md` with `source_format` not `abstract`), append the first 1500 words of Results and Discussion. Embed with `TfidfVectorizer(sublinear_tf=True, min_df=3, max_df=0.5, ngram_range=(1,2), stop_words='english')`, then `TruncatedSVD(n_components=100, random_state=seed)`, then L2 normalisation (latent semantic analysis). This is a lexical substitute, not the pipeline model; set `embedding_source` to `local_tfidf_svd` in `parameters` and state it in the interpretation limits. If sentence-transformers and a local model are installed later, `all-MiniLM-L6-v2` (384 dimensions) is a better substitute; record it and do not claim it equals the pipeline model.
2. **Label text.** Whatever the embedding route, the texts used for c-TF-IDF labels (step 5) are the local-route texts above.
3. **Reduction and clustering in the BERTopic manner.**
   - Preferred (if `umap-learn` imports): `umap.UMAP(n_components=5, n_neighbors=15, min_dist=0.0, metric='cosine', random_state=seed)`, then `sklearn.cluster.HDBSCAN(min_cluster_size=8, min_samples=3, cluster_selection_method='leaf')` on the 5-dimensional points. A second `UMAP(n_components=2, n_neighbors=15, min_dist=0.1, metric='cosine', random_state=seed)` gives the map coordinates. Record the umap version.
   - Fallback (umap-learn absent, the case in `.venv-nlp` as inspected): `PCA(n_components=min(20, n-1), random_state=seed)` on the L2-normalised embeddings, then the same `HDBSCAN` on the PCA scores (euclidean on unit vectors approximates cosine). Map: `TSNE(n_components=2, metric='cosine', init='pca', perplexity=30, random_state=seed)` on the same vectors, or the first two PCA components if t-SNE is slow. Set `reduction` to `pca` or `umap` in `parameters` and state the fallback in `run_notes` and the interpretation. The fallback changes the map and possibly the topic count, not the comparison method.
   - HDBSCAN noise (label -1) stays as topic id `-1`, label `Unassigned`; report the noise share. Stability: repeat the clustering `stability_runs` times (UMAP route: different seeds; PCA route: 80% subsamples) and report the median pairwise adjusted Rand index between runs as `stability_ari_median`.
   - Sensitivity table in `run_notes`: `min_cluster_size` 6, 8, 12, 16, with topic count, noise share and AMI against `primary_category`.
4. **Per-article membership.** `topic_probability` = `HDBSCAN.probabilities_` (0 for noise). Topic centroid = mean of the reduced points of the topic; `d1` = distance to the own centroid (for noise, to the nearest centroid), `second_topic` = nearest other centroid at distance `d2`, `margin = (d2 - d1) / d1`. Category centroid = mean of the reduced points of articles with that `primary_category`; `dist_to_own_category_centroid` and `nearest_category` (closest of the 11 centroids). Distances are in the reduced space; say so.
5. **Class-based TF-IDF labels.** For each non-noise topic t, concatenate the label texts of its articles into one document. `CountVectorizer(stop_words='english', min_df=2, ngram_range=(1,2))` over the topic documents. `W[t,w] = tf[t,w] * log(1 + A / f[w])`, where `tf[t,w]` is the count of w in topic t divided by the total words of topic t, `A` the mean word count per topic document and `f[w]` the total count of w over all topic documents. Words = top 10 by W; `label` = top 4 joined by `, `. Drop from labels terms found in more than 60% of topics and the generic tokens `babesia`, `canis`, `canine`, `dog`, `dogs`, `gibsoni`, `rossi`, `vogeli`. Representative articles: 5 highest `topic_probability`, ties by smallest distance to centroid.
6. **Agreement with the automatic labels** for `primary_category` and `agent_primary_category` (and `aim` if available). Primary population: articles in a non-noise topic; also report the version where noise forms one extra cluster. Compute `adjusted_mutual_info_score` (arithmetic average), `adjusted_rand_score`, normalised mutual information, homogeneity, completeness, V-measure, with n. Permutation null: shuffle the category labels `ami_permutations` times (seeded), report null mean and 95th percentile and p = `(1 + #null >= observed) / (1 + B)` for both AMI and ARI. Bootstrap 95% interval over articles (`bootstrap` resamples, seeded). Reference ceiling: AMI and ARI between `primary_category` and `agent_primary_category` themselves. Per topic: purity (share of its majority category). Per category: share of its articles in its best-matching topic.
7. **Topic by category tables.** Counts topic x `primary_category`, with totals and standardised Pearson residuals `(O - E) / sqrt(E)`; list cells with absolute residual above 2 as a descriptive flag (no p values; cells are small). Same table for `agent_primary_category`.
8. **Review queue.** An article is queued if any rule fires (all that fire go in `reasons`): `topic_disagrees` (topic majority category, with purity at least 0.4 and topic size at least 10, differs from `primary_category`); `between_clusters` (noise, or `topic_probability < 0.5`, or `margin < 0.15`); `far_from_category` (distance to own category centroid above that category's 90th percentile; categories with at least 10 articles); `labels_disagree` (`primary_category != agent_primary_category` and `topic_disagrees` or `between_clusters` also fires; the strongest signal); `low_confidence_label` (`category_confidence == 'low'` and `topic_disagrees` or `between_clusters` also fires). Score = number of reasons; ties by lower `topic_probability`. The top 60 go in the result, all queued articles in the CSV. EXP11 may use this queue.
9. **Trends.** Per topic: count and share per period (denominator all 444 articles in the period), Wilson 95% interval. One overall chi-square of topic by period with a Monte Carlo permutation p value (shuffle period labels `trend_permutations` times, seeded) and bias-corrected Cramer's V. Per topic: Cochran-Armitage trend of membership on period scores 0 to 3 with a permutation p value, Benjamini-Hochberg adjusted across the topics (one family, `alpha` 0.05). The same by species group (shares, Wilson intervals, overall permutation chi-square, no per-topic trend tests). Species groups under 20 articles and topics under 10 articles are flagged `low_n`; do not claim a trend from them.
10. **Map data.** One record per article with the fields in 4.1 (`article_map`).

Multiple-testing family: the per-topic period trend tests (BH). The AMI and ARI permutation tests are two tests on the whole run, reported with intervals and not part of a family. Implement permutation tests, Wilson interval, Cochran-Armitage, Cramer's V and c-TF-IDF in numpy as `experiment_pairwise.py` does; use scikit-learn for TF-IDF, SVD, PCA, HDBSCAN and the information scores, which are justified here.

## 4. Outputs

### 4.1 Experiment JSON

`data/experiments/EXP10-CORPUS-topics.json`, overwritten per run. Top-level keys `experiment`, `associations`, `cluster_assignments`, `results`, as in `experiment_specs/README.md`.

`experiment`: `code` `EXP10-CORPUS-topics`; `name` "Topic map of the canine articles versus the automatic categories"; `description` one sentence; `method` `topics`; `dataset` `null`; `script` `scripts/experiment_topics.py`; `script_version` (12-character SHA-256 prefix of the script file); `run_utc`; `n_subjects` articles clustered (444 less any without an embedding); `n_variables` 11 (the categories); `n_tests` count of statistical tests (two permutation tests, two for the agent label set, the overall period and species tests, plus one trend test per topic); `summary` one plain paragraph with topic count, noise share, AMI and ARI against `primary_category` with intervals, and queue size.

`parameters`: every default listed at the head of section 3, plus `embedding_source` (`sql:text-embedding-3-small` or `local_tfidf_svd`), `embedding_dimension`, `reduction` (`umap` or `pca`), `package_versions` (numpy, scikit-learn, umap-learn if used), `scope` ("CB ids"), `periods`, `species_groups` (mapping).

`associations`: `[]`. `cluster_assignments`: `[]` (no tidy dataset exists to hold subjects; per-article topics are in `article_map`).

`results[]`:

| kind | title | sort_order | payload |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | `{"sections": [{"heading": str, "paragraphs": [str]}]}` |
| `topics` | Topics and their labels | 1 | `{"n_topics": int, "n_noise": int, "stability_ari_median": float, "topics": [{"id": 3, "label": "str", "words": [10 str], "size": int, "majority_category": "ERY", "purity": 0.52, "category_counts": {"ERY": 9}, "median_year": 2016, "top_articles": [{"id": "CB050", "title": "str", "probability": 0.93}]}]}` (noise topic -1 last, label `Unassigned`) |
| `topic_by_category` | Topic by primary category | 2 | `{"topics": [int], "categories": [11 codes], "counts": [[int]], "residuals": [[float]], "flagged_cells": [{"topic": 3, "category": "REN", "observed": 12, "residual": 3.1}], "agent_counts": [[int]], "agent_residuals": [[float]]}` |
| `agreement` | Agreement with the automatic labels | 3 | `{"comparisons": [{"labels": "primary_category", "population": "non_noise", "n": int, "ami": float, "ami_ci": [lo, hi], "ami_null_mean": float, "ami_null_p95": float, "ami_p": float, "ari": float, "ari_ci": [lo, hi], "ari_p": float, "nmi": float, "homogeneity": float, "completeness": float, "v_measure": float}], "reference": {"labels": "primary_vs_agent", "n": 444, "ami": float, "ari": float}, "category_best_topic_share": {"ERY": 0.41}}` (one comparison per label set and population) |
| `article_map` | Literature map | 4 | `{"x_label": "dim 1", "y_label": "dim 2", "reduction": "pca", "points": [{"id": "CB050", "title": "str (140 chars max)", "x": float, "y": float, "topic": int, "topic_label": str, "topic_probability": float, "primary_category": "ERY", "agent_primary_category": "ERY", "category_confidence": "high", "year": 2017, "species_group": "B. canis", "include_type": "primary", "in_review_queue": bool}]}` (444 points, about 150 KB) |
| `review_queue` | Articles for human review | 5 | `{"n_queued": int, "rules": {"topic_disagrees": int, "between_clusters": int, "far_from_category": int, "labels_disagree": int, "low_confidence_label": int}, "csv_path": "data/experiments/EXP10-CORPUS-topics-review-queue.csv", "top": [{"id", "title", "primary_category", "agent_primary_category", "topic", "topic_label", "topic_probability", "margin", "nearest_category", "dist_to_own_category_centroid", "reasons": [str], "score": int}]}` (top 60) |
| `topic_trends` | Topic prevalence by period and species | 6 | `{"periods": ["2006-2010", "2011-2015", "2016-2020", "2021-2026"], "period_totals": [int x4], "by_period": [{"topic": int, "label": str, "counts": [int x4], "shares": [float x4], "wilson": [[lo, hi] x4], "low_n": bool, "trend_stat": float, "p_value": float, "p_adjusted": float}], "overall_period_test": {"chi2": float, "cramers_v": float, "p_value": float}, "species_groups": [str], "species_totals": [int], "by_species": [{"topic": int, "counts": [int], "shares": [float], "wilson": [[lo, hi]], "low_n": bool}], "overall_species_test": {"chi2": float, "cramers_v": float, "p_value": float}}` |
| `run_notes` | What was included, dropped, substituted | 7 | `{"included": 444, "excluded_scope": {"HU": 27, "BG": 10}, "missing_embedding": [ids], "embedding_source": str, "embedding_model_values": [str], "fallbacks": [str], "min_cluster_size_sensitivity": [{"min_cluster_size": 8, "n_topics": int, "noise_share": float, "ami_primary": float}], "species_group_mapping": {"B. canis": ["B. canis", "B. canis canis"]}, "partial_year": 2026, "data_syndromes_present": bool}` |

`interpretation` headings: "What was asked", "What was done" (embedding route, clustering, labels, any fallback), "Main findings" (topic count, noise share, the largest topics with their label words and majority category, AMI and ARI with intervals against both label sets and against each other, the strongest disagreements, period trends with numbers), "How to use the review queue", "Limits". Plain language for a veterinary reader.

### 4.2 Other artefacts

- `data/experiments/EXP10-CORPUS-topics-review-queue.csv`: all queued articles. Columns `id,title,primary_category,agent_primary_category,category_confidence,topic,topic_label,topic_probability,margin,nearest_category,dist_to_own_category_centroid,reasons,score,year,species_group`. UTF-8, comma separated, `reasons` joined by `;`. Kept beside the JSON so a rerun overwrites both.
- Map data lives inside the JSON; no image files.

## 5. Acceptance checks

1. The JSON parses; `experiment.method == "topics"`, `dataset` null, `associations` and `cluster_assignments` empty; results include `interpretation`, `run_notes` and every kind in 4.1.
2. `article_map.points` has one entry per clustered article (444, or fewer by exactly the length of `run_notes.missing_embedding`); ids are unique and all start with `CB`; topic sizes plus noise sum to the point count.
3. `topic_by_category` column sums equal the category counts of the clustered articles (ERY 96, INF 91, SEV 59, MET 50, REN 40, COA 40, OXO 21, CAR 18, END 14, NEU 8, PUL 7 when all 444 are present); row sums equal topic sizes.
4. Reproducibility: two runs with the same seed give JSON that differs only in `run_utc`.
5. Null behaviour: with `--shuffle-labels` (debug flag that shuffles `primary_category` before step 6), AMI p values are above 0.05 in at least 9 of 10 seeds. The observed AMI against the real `primary_category` must exceed the null 95th percentile; if not, the interpretation says that topics do not reproduce the categories.
6. The `reference` AMI between `primary_category` and `agent_primary_category` is reported. A topic AMI above that reference is rechecked before it is reported.
7. Review queue: `n_queued` equals the CSV row count; no `HU` or `BG` id; the top-ranked rows have at least two reasons.
8. Load: `Babesiosis.Console --datasets-only` finishes with no error for this file; `SELECT experiment_code, method, n_subjects FROM dbo.experiment WHERE experiment_code = 'EXP10-CORPUS-topics'` returns one row, and `dbo.experiment_result` has 8 rows for it (one per kind).
9. The interpretation names the embedding route and any fallback, says "topics" and never "subtypes", and says the categories are automatic and unreviewed.

## 6. Caveats and reporting language

- `primary_category` comes from an NLP rule system with no human review; `agent_primary_category` from LLM agents with no human review; the two agree on 254 of 444 articles. A topic-versus-category disagreement is a flag for inspection, not an error in either direction. Topics are not ground truth.
- Topics describe similarity of text (study type, species, subject), not pathophysiology. Some topics will be about study design (case reports, diagnostics, treatment, prevalence) which the 11 categories do not cover; that is a reason for disagreement, not a fault.
- The pipeline embeddings come from the review's appraisal note text, which already carries the appraiser's wording; for many articles only the abstract was available (230 of 481 are abstract-only). The local TF-IDF substitute is lexical and weaker than `text-embedding-3-small`.
- Articles are not independent evidence: some share cohorts (`cohort_id`) and CB510 and CB511 are one study published twice. Topic sizes count articles, not studies.
- Small categories (NEU 8, PUL 7, END 14) cannot be recovered by HDBSCAN with `min_cluster_size` 8; say so.
- 2026 is a partial year. Trends are descriptive. The index reflects the search: a quiet period or topic is a gap in the index, not in the literature.
- `HU` and `BG` articles are excluded and are never canine evidence.

## 7. Build plan for the agent

1. Read: `experiment_specs/README.md`, `scripts/experiment_pairwise.py` (structure, `script_version`, output writing, interpretation pattern), `CLAUDE.md`, `docs/nlp-and-severity.md` (categories), `docs/database.md` (SQL route), `ArticleSource.BuildEmbeddingText` in `console/Babesiosis.Console/Source/ArticleSource.cs`. Done when you can state which text was embedded and with which model.
2. Tidy: not applicable.
3. Script: write `scripts/experiment_topics.py` with a module docstring (inputs, outputs, run command, dependencies) following `experiment_pairwise.py`. Command line: `--code EXP10-CORPUS-topics --name "Topic map of the canine articles versus the automatic categories" --embeddings auto --seed 20261105 --min-cluster-size 8 --min-samples 3 --umap-neighbors 15 --umap-components 5 --alpha 0.05 --ami-permutations 2000 [--connection "<ODBC string>"] [--shuffle-labels]`. Add optional `umap-learn` and `pyodbc` lines (commented) to `scripts/requirements-experiments.txt`, and note that `.venv-nlp` supplies scikit-learn and scipy.
4. Run: from `core/`, `.venv-nlp/Scripts/python.exe -I scripts/experiment_topics.py --code EXP10-CORPUS-topics --name "Topic map of the canine articles versus the automatic categories" --embeddings auto`. Expected runtime under 3 minutes on the local route.
5. Load: from `console/Babesiosis.Console`, `dotnet run -- --datasets-only` (`appsettings.json` `ReviewRoot` pointing at `core/`). Run the SQL check in section 5 item 8.
6. Verify: acceptance checks 1 to 9; fix and rerun until all pass.
7. Document: add a `scripts/README.md` row for `experiment_topics.py`; update `docs/database.md` if it lists experiments; update the `exp10` status on `docs/ml-experiment-plan.html` if that page tracks status.
8. Optional: a web view for `topics` under `webapp/Babesiosis.Web/src/app/modules/experiments/views/` (scatter of `article_map` coloured by topic or category, topic table, review queue table), only after 1 to 7 pass.

## 8. Open questions

1. Embedding route. Default: try SQL, fall back to local TF-IDF + SVD, and state which was used in the final message and in the interpretation.
2. `data/syndromes/` is absent on the machine where this spec was written, so the headers of `article_categories.csv`, `article_terms.csv` and `concept_summary.csv` were not checked. Default: do not use them; add the `aim` label set only if the file exists.
3. Cluster the 40 `canine review` articles with the primary studies? Default: yes, flagged by `include_type`; they may form their own topic. Add a `--exclude-reviews` option and report AMI both ways in `run_notes` if time allows.
4. `min_cluster_size` 8 is a guess for 444 articles. Default 8, with the sensitivity table in `run_notes`.
