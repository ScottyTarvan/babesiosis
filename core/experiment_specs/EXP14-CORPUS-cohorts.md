# EXP14 CORPUS cohorts: Hidden cohort overlap between canine primary studies

| Field | Value |
|---|---|
| Experiment code | `EXP14-CORPUS-cohorts` |
| Layer | 3 (article corpus; one article per row, pairs derived from it) |
| Method token | `cohorts` (goes in `experiment.method`) |
| Dataset(s) | `null`: the unit is an article pair, not a subject in a tidy dataset, so there is no tidy file and `associations` and `cluster_assignments` are empty |
| Readiness | ready (full texts exist on this machine in `data/markdown/`, git-ignored) |
| Python environment | `.venv-nlp` (scikit-learn 1.9.1, scipy 1.17.1, numpy 1.26.4, joblib; checked). No package to install. `sentence-transformers`, `torch`, `pandas` and SQL drivers are NOT installed, so the default text similarity is TF-IDF cosine; a dense-embedding feature is optional (section 3, step 4). Command: `.venv-nlp/Scripts/python.exe -I scripts/experiment_cohorts.py`. Add one comment line to `scripts/requirements-experiments.txt`: `# EXP14 also needs scikit-learn>=1.9 and scipy (present in .venv-nlp)` |
| Estimated build effort | medium |
| Suggested model for the building agent | sonnet: all features and splits are specified; regexes need care but not design |
| Depends on | nothing among experiments. Needs `cohorts.json`, `articles.jsonl`, `data/markdown_report.jsonl`, `data/markdown/` |

## 1. Question and hypotheses

Q. Which pairs of canine primary studies probably report the same animals although they share no cohort identifier in `cohorts.json`?

Hypothesis: pairs of articles from the same cohort (the 38 known `CH##`) differ from unrelated pairs on a small set of observable features (similar methods text, shared authors, same country, overlapping recruitment dates, matching sample sizes, same journal), so a classifier trained on the known pairs will rank other same-cohort pairs high. Motivation: `cohorts.json` records basis text such as same first author, same group, identical design (for example CH01, CB001 and CB046, Lublin urinary cohort), so the signals are known to be author, design and site.

Negative finding: held-out known cohort pairs are not ranked above unrelated pairs better than the stated baselines (grouped cross-validated precision at k no better than the base rate), or the top unlinked pairs all fail human review. Either outcome is reported as is.

## 2. Data

### 2.1 Sources

- `articles.jsonl` (481 records). Fields used: `id`, `authors` (list of strings such as `"Crnogaj M"`, all 481 are lists), `journal`, `country` (free text; includes `null` and `"not stated in abstract"`), `first_pub_date` (ISO date string, present for all candidates), `sample_size` (free text), `n_infected_dogs` (int, null for 51 of the 338 primary studies), `n_controls`, `cohort_id`, `species_short`, `scope_label`, `include_type`, `title`, `one_sentence_finding`.
- `cohorts.json`: object `CH01`..`CH38` -> `{label, certainty ("confirmed" 3 or "probable" 35), basis (free text), members: [article ids]}`. Group sizes: 22 cohorts of 2 articles, 10 of 3, 4 of 4, 1 of 5, 1 of 6; 101 member articles in all, 100 of them canine primary studies (the 101st, `CB284`, is a case report).
- `data/markdown_report.jsonl` (540 rows incl. retired ids; join to `articles.jsonl`, take scope from there): `source_format` (`abstract` | `pdf` | `jats_xml`), `sections` (normalised list such as `["abstract","introduction","methods","results","discussion"]`), `word_count`, `language`, `quality`.
- `data/markdown/<ID>.md` (or `<ID>.en.md` when it exists: prefer the English translation): YAML front matter, then `# title`, `## Abstract`, `## Introduction`, `## Methods` with `###` subsections, `## Results`, ... (git-ignored; exists only on this machine; the experiment cannot run elsewhere without it).
- SQL (read-only context, not needed to run): `dbo.article_section` holds the same text in passages of about 500 words with `section_kind` (`methods`, `results`, ...) and a per-passage `embedding` VECTOR(1536); `dbo.search_passages` queries it. See `docs/database.md`.

Population counts, taken today with `python -I` from the files above (re-count in the script and write them into `run_notes`):
- Canine primary studies = `scope_label == "core canine evidence"` and `include_type == "primary"`: 338 articles. `core canine evidence` has 404 articles (338 primary + 66 case reports); of these 101 have a `cohort_id` and 303 do not. `canine review` (40), `human comparator` (27, HU) and `background` (10, BG) never have a `cohort_id` and are excluded.
- 338 candidates give 56,953 unordered pairs. Known positive pairs (two canine primary studies in the same cohort) = 100.
- Full text with a methods section (`source_format` in `pdf`/`jats_xml` and `"methods"` in `sections`): 157 of the 338 candidates. Pairs where both have it: about 12,200 of 56,953; positives with both: 37 of 100. The other 181 candidates are abstract-only or have no methods heading.

### 2.2 Tidy file required

Not applicable (`dataset = null`).

### 2.3 Variables and filters

Articles: `--include-types primary` (default; `primary,case_report` adds the 66 case reports, one of which, `CB284`, is a cohort member). Pairs: all unordered pairs of the included articles. A pair is `positive` if both articles have the same `cohort_id`. Pair features are defined in section 3. Minimum methods text length: `min_methods_words = 80` words, else the methods feature is missing for that article.

## 3. Method

Seed `20261105` everywhere (`random.Random`, `np.random.default_rng`, every sklearn `random_state`). Fixed defaults throughout; there is no hyperparameter tuning and no feature selection, so plain grouped cross-validation is the correct validation (nested cross-validation applies only if someone adds tuning or selection).

1. Load and filter articles; build `group[id]` = `cohort_id` if present else the article id itself (singleton group). Build the positive pair set from `cohorts.json` restricted to included articles.
2. Text preparation. For each article:
   - `methods_text`: from `data/markdown/<ID>.en.md` if present else `<ID>.md`, only when `markdown_report` says `source_format` is `pdf` or `jats_xml`. Take the text from the first level-2 heading matching `(?i)^##\s+.*(method|materials|patients and|animals and|study design)` up to the next level-2 heading, including `###` subsections. If the report lists `methods` but no heading matches, treat methods as missing and count the article in `run_notes.methods_heading_unmatched`. Missing if fewer than `min_methods_words` words.
   - `abstract_text`: the `## Abstract` section when present; otherwise `title + " " + one_sentence_finding` from `articles.jsonl`. Every article has one.
   - Fallback when full text is missing: methods features are `NaN` for any pair where either article lacks `methods_text`; the abstract-based features are always available. Each pair gets `text_stratum` = `both_methods`, `one_methods` or `abstract_only`.
3. Pair features (one row per pair; all numeric, missing as `NaN`):
   - `sim_methods`: cosine similarity of `TfidfVectorizer(sublinear_tf=True, stop_words="english", ngram_range=(1,2), min_df=2, max_df=0.5, lowercase=True)` fitted on all available methods texts. `NaN` if either is missing.
   - `sim_abstract`: same vectoriser settings fitted on all abstract texts.
   - `author_jaccard`: Jaccard index of the sets of normalised author keys. Normalisation: Unicode NFKD, strip combining marks, lowercase, remove punctuation and hyphens; an author string `"Surname Initials"` is split so the last whitespace token is the initials if it is 1 to 3 letters and all upper case in the original, and everything before it is the surname; key = surname + " " + first initial. `NaN` if either list is empty.
   - `shared_authors` (count) and `first_author_match`, `last_author_match` (0/1 on keys). Note the key set is also stored as evidence.
   - `same_country`: 1 if the normalised country sets (lowercase, split on `,;/` and the word `and`) intersect, 0 if both are known and disjoint, `NaN` if either is null, empty or `not stated in abstract`.
   - `same_journal`: 1/0 on normalised journal (lowercase, no punctuation); `NaN` if missing.
   - `year_gap`: absolute difference of publication years from `first_pub_date`.
   - `same_species`: 1/0 on `species_short` normalised; `NaN` if missing.
   - `n_ratio`: `min(n_infected_a, n_infected_b) / max(...)` from `n_infected_dogs` (positive integers only); `NaN` if either is missing. `n_equal`: 1 if both `n_infected_dogs` are equal and the `n_controls` are equal or both null, 0 if both known and different, `NaN` if either `n_infected_dogs` missing. (Nested sample sizes are captured by `n_ratio`: a study reusing a subset of another's dogs has a ratio below 1 with the larger study contributing the larger n; the evidence column shows both n values.)
   - `recruit_overlap`: overlap in days of the two parsed recruitment intervals divided by the shorter interval, 0 to 1; `NaN` if either interval is not parsed. `recruit_known` (0/1: both parsed) is carried as an extra feature.
   Recruitment interval parser (applied to `methods_text`, else to `abstract_text`): look in sentences containing one of `recruit|enrol|admitted|presented|collected|sampled|included|study period|between|from`; patterns: (a) `(between|from)? <Month> <YYYY> (and|to|until|through|-|–) <Month> <YYYY>`; (b) `<Month> (to|-|–) <Month> <YYYY>`; (c) `<YYYY> (to|-|–|and) <YYYY>` within a sentence that also contains one of `dogs|patients|animals|cases|enrol|recruit|admitted|presented|collected|study period`; (d) a single `<Month> <YYYY>` is a point interval of that month. An interval runs from the first day of the start month (or 1 January) to the last day of the end month (or 31 December). Month names English, full or three-letter. Take the earliest start and latest end over the matches in one article; discard the result if it spans more than 15 years or ends after the publication year. Store the matched sentence for evidence. Tested in the acceptance checks.
4. Optional dense feature `sim_methods_dense` (off by default): only if `--embeddings PATH` is given, a JSON mapping article id to a list of 1,536 floats (mean of the `methods` passage embeddings from `dbo.article_section`, exported by the owner; the script never connects to SQL). Cosine similarity; `NaN` if either id is absent. Default run does not use it (open question 1).
5. Labelled set. Positives: all 100 known pairs. Negatives, sampled with `random.Random(seed)` from two pools: pool A "different cohorts" = pairs where both articles have a `cohort_id` and the ids differ; pool B "different countries" = pairs where both countries are known and the normalised sets are disjoint (pairs already in pool A are removed from pool B). Draw `neg_per_pos_cohort = 5` x positives from pool A (all of pool A if smaller) and `neg_per_pos_country = 5` x positives from pool B. Mark each row `neg_kind` = `different_cohort` or `different_country`. Both pools assume distinct cohort identifiers mean distinct animals and different countries mean different animals; this is a labelling assumption, stated in the interpretation. Because pool B selects negatives by country, `same_country` would trivially separate them; this is why validation (step 7) uses all unlabelled pairs as negatives and why an ablation without `same_country` is reported. Pairs the reviewer rejected in the decisions file (section 4.2) are added to the negatives (`neg_kind = reviewed_rejected`).
6. Models (fixed settings):
   - `logistic`: `Pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, random_state=seed))`.
   - `hgb`: `HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=200, l2_regularization=1.0, class_weight="balanced", random_state=seed)` (handles `NaN` natively).
   - `logistic_no_country`: the `logistic` pipeline without `same_country`.
   Report events per variable: 100 positives / number of features.
7. Validation: node-disjoint grouped cross-validation. Each `group` (a cohort or a singleton article) is assigned to one of `folds = 5` folds (shuffle groups with the seed, then greedy assignment to the fold with the fewest articles). A model for fold k trains on labelled pairs whose two articles are both outside fold k; it is tested on every pair whose two articles are both inside fold k (labelled or not; pairs spanning folds are in neither set). Test negatives are therefore ALL non-positive pairs in the fold, including the many unlabelled same-country pairs that may contain real hidden overlaps (this makes precision a lower bound). Repeat with `repeats = 10` different fold seeds (`seed + r`). Per fold and repeat compute: ROC AUC, average precision, precision at k and recall at k for `k in {5, 10, 20}` (k capped at the number of test pairs), and the base rate (positives / test pairs) as the reference. Report mean over folds and repeats with a percentile 95% interval over the 50 fold-repeat values (non-independent; say so) and the numbers separately for `text_stratum`. A fold with no positive pair is skipped and counted.
8. Candidate scoring. Fit `rank_model` (default `logistic`) on all labelled pairs. Score every non-positive pair of the included articles (including pairs in the training negatives; mark them `was_training_negative = true`; their score is in-sample). Exclude pairs rejected in the decisions file. Rank by score. Keep the top `top_n = 100` as the review queue.
9. Evidence per queued pair: the shared author names; both countries, journals, years, `n_infected_dogs`/`n_controls`; both parsed recruitment intervals with the matched sentence; the most similar methods sentence pair (split methods text into sentences with a regex on `[.!?]` followed by a space and capital; TF-IDF over all sentences of the two papers; take the sentence pair with the highest cosine, cosine at least 0.35; fall back to the abstract sentences if methods are missing), each snippet cut to 300 characters; the cohort ids of the two articles. `suggested_action` = `extend CHxx` if one article has a cohort and the other has none, `merge CHxx and CHyy` if both have different cohorts, `new cohort` if neither. Snippets quote the papers' own text for local use only: the CSV and JSON contain at most 300 characters per snippet and are stored in the repository, whose full texts are copyrighted; keep to the short snippet limit and never copy more.
10. Corrected independent-cohort counts. Current count by the `build_outputs.py` definition (core canine articles without a `cohort_id`, plus the number of distinct `cohort_id`; computed on the same article set as `build_outputs.py`: all 404 `core canine evidence` articles, expected 303 + 38 = 341; verify against the number printed by `scripts/build_outputs.py` and report both if they differ). Scenario count if all queued pairs with `score >= score_floor` (default 0.5) were confirmed: union-find over the current cohorts plus those pairs, count the components. Report as a range for top 10, top 25 and all queued pairs above the floor. These are scenarios, not corrections.

## 4. Outputs

### 4.1 Experiment JSON

File `data/experiments/EXP14-CORPUS-cohorts.json`.

`experiment`: `code` `EXP14-CORPUS-cohorts`; `name` `Hidden cohort overlap between canine primary studies`; `description` one sentence on pair features, a grouped-cross-validated pair classifier and a human review queue; `method` `cohorts`; `dataset` `null`; `parameters`:

```
{"include_types": ["primary"], "min_methods_words": 80, "tfidf": {"ngram_range": [1,2], "min_df": 2, "max_df": 0.5, "sublinear_tf": true},
 "neg_per_pos_cohort": 5, "neg_per_pos_country": 5, "folds": 5, "repeats": 10, "k_values": [5,10,20],
 "rank_model": "logistic", "top_n": 100, "score_floor": 0.5, "embeddings": null, "decisions_file": "data/experiments/EXP14-CORPUS-cohorts-decisions.csv",
 "seed": 20261105, "models": {"logistic": {"C": 1.0}, "hgb": {"max_depth": 3, "learning_rate": 0.05, "max_iter": 200, "l2_regularization": 1.0}}}
```

`script` `scripts/experiment_cohorts.py`; `script_version` first 12 hex characters of the script's SHA-256; `run_utc`; `n_subjects` = articles included (338); `n_variables` = number of pair features; `n_tests` = number of candidate pairs scored; `summary` one paragraph (articles, pairs, positives, best cross-validated precision at 10 versus base rate, number of queued pairs, how many are across two cohorts). `associations` and `cluster_assignments`: `[]`.

`results[]`:

| kind | `title` | `sort_order` | payload |
|---|---|---|---|
| `interpretation` | `Explanation and interpretation` | 0 | `{"sections": [{"heading", "paragraphs": [str]}]}`; headings: `Question`, `What was done`, `Main findings`, `How to use the review queue`, `Limits` |
| `pair_features_summary` | `Pair features: known cohort pairs versus unrelated pairs` | 1 | `{"n_articles", "n_pairs", "n_positive_pairs", "n_negative_sampled", "text_strata": {"both_methods": {"pairs", "positives"}, "one_methods": {...}, "abstract_only": {...}}, "features": [{"name", "coverage_all", "coverage_positive", "median_positive", "median_negative", "median_all", "single_feature_auc"}]}` |
| `classifier_performance` | `Pair classifier: grouped cross-validation` | 2 | `{"folds": 5, "repeats": 10, "events_per_variable": float, "folds_skipped": int, "base_rate_mean": float, "models": [{"name", "features": [...], "auc": {"mean", "ci_low", "ci_high"}, "average_precision": {...}, "precision_at_k": {"5": {...}, "10": {...}, "20": {...}}, "recall_at_k": {...}, "by_stratum": {"both_methods": {"auc", "average_precision", "precision_at_10"}, "one_methods": {...}, "abstract_only": {...}}, "coefficients": [{"feature", "coef"}] (logistic only)}]}` |
| `candidate_links` | `Candidate cohort links for human review` | 3 | `{"rank_model": str, "score_floor": float, "queue_csv": "data/experiments/EXP14-CORPUS-cohorts-review-queue.csv", "candidates": [{"rank", "article_a", "article_b", "score", "text_stratum", "cohort_a", "cohort_b", "suggested_action", "was_training_negative", "features": {name: value}, "shared_authors": [str], "countries": [a, b], "journals": [a, b], "years": [a, b], "n_infected": [a, b], "recruitment": [{"interval", "sentence"}, {...}], "snippets": {"a": str, "b": str, "cosine": float}}], "cohort_count": {"current": int, "if_top_10": int, "if_top_25": int, "if_all_above_floor": int}, "reviewed": {"n_confirmed": int, "n_rejected": int, "precision_at_k_reviewed": {...}}}` |
| `run_notes` | `Inclusions, text coverage and caveats` | 4 | `{"counts": {...from 2.1...}, "methods_heading_unmatched": [ids], "methods_missing": int, "recruitment_parsed": int, "country_unknown": int, "positives_dropped": [pairs with an article not included], "folds_skipped": int, "notes": [str]}` |

Interpretation, in plain language for a veterinary reader: the question; what a "pair" and a "feature" are; the cross-validated numbers against the base rate; how many candidates, of which kinds; that the score ranks pairs for a person to check and is not a probability that two articles share dogs; and the limits in section 6.

### 4.2 Other artefacts

- Review queue (written by the script, overwritten on each run): `data/experiments/EXP14-CORPUS-cohorts-review-queue.csv`, UTF-8, header `rank,article_a,article_b,score,text_stratum,cohort_a,cohort_b,suggested_action,shared_authors,country_a,country_b,journal_a,journal_b,year_a,year_b,n_infected_a,n_infected_b,recruit_a,recruit_b,sim_methods,sim_abstract,snippet_a,snippet_b`. One row per queued pair (up to `top_n`). Not read by the console loader (it reads only `*.json`).
- Decisions file (maintained by hand, never written or overwritten by the script): `data/experiments/EXP14-CORPUS-cohorts-decisions.csv`, header `article_a,article_b,decision,reviewer,decision_date,note`, `decision` one of `confirmed`, `rejected`, `unsure`. The script reads it if present: `rejected` pairs leave the queue and join the negatives; `confirmed` pairs are reported in `candidate_links.reviewed` and stay out of the queue; `unsure` pairs stay in the queue. Create the file with only the header row if it does not exist.
- Nothing else outside `data/experiments/`.

No cohort link is added to `cohorts.json` without a human decision. The script never writes `cohorts.json`, `articles.jsonl` or any file other than the two outputs above. A confirmed link is recorded like this: the reviewer reads both papers, appends a row to the decisions file (`confirmed`, name, date, note), and edits `cohorts.json` by hand: add the article id to the `members` of the existing `CHxx`, or create the next free `CH##` with `{"label": ..., "certainty": "probable", "basis": "EXP14 candidate, rank N, score S, reviewed by NAME on DATE: <evidence>", "members": [...]}`; `certainty` is `confirmed` only when a paper states that the dogs are the same. Then run `python -I scripts/build_outputs.py` (it regenerates `articles.jsonl` `cohort_id` and the independent-cohort count from `cohorts.json`) and re-run this experiment, whose positives now include the new pair. The research map changes only after that step.

## 5. Acceptance checks

1. Counts: `n_subjects` equals the number of included articles (338 by default); `pair_features_summary.n_pairs` = 56,953 for 338 articles; `n_positive_pairs` = 100 (equals the number of same-cohort pairs among included articles computed independently from `cohorts.json`); the text-strata counts sum to `n_pairs`; both-methods positives about 37.
2. Reproducibility: two runs give identical JSON and CSV except `run_utc`.
3. Leakage: assert in the script, and confirm in the run, that for every fold no article appears in both the training pairs and the test pairs of that fold, and that every cohort lies entirely in one fold.
4. Label-shuffle null: permute the labels of the training pairs (quick separate check, not saved) and re-run the cross-validation for `logistic`; mean test AUC is about 0.5 and mean precision at 10 is about the base rate.
5. Sanity: `author_jaccard` and `shared_authors` are higher in positives than in sampled negatives (median) in `pair_features_summary`; `sim_methods` coverage is reported; the classifier `by_stratum` shows the abstract-only stratum (no methods text) separately.
6. Recruitment parser: print and eyeball 20 randomly chosen articles with a parsed interval (seed fixed) against their methods text and record in `run_notes.notes` how many were correct; if fewer than 15 of 20, fix the regexes before accepting. Check also that both articles of CH01 (`CB001`, `CB046`) are parsed or explain why not.
7. Review queue: the CSV has `min(top_n, available)` rows, none of them a pair that already shares a `cohort_id`, none from `HU`/`BG`/review articles; every row has non-empty `snippet_a` or states `no methods text`. Spot-check 5 queued pairs by opening the two `articles/` notes.
8. Load: `Babesiosis.Console --datasets-only` completes (the experiment has `dataset = null`; the loader must accept it, as the README states); SQL: `SELECT result_kind FROM dbo.experiment_result AS r JOIN dbo.experiment AS e ON e.experiment_id = r.experiment_id WHERE e.experiment_code = 'EXP14-CORPUS-cohorts'` returns the five kinds in 4.1 and `dbo.association` has no rows for it.
9. The interpretation says the score is a ranking for review, states the cross-validated precision at 10 next to the base rate, and says no link has been added to `cohorts.json`.

## 6. Caveats and reporting language

- Same authors, same hospital and same journal do not prove the same dogs. Each candidate needs a human decision before `cohorts.json` or the research map changes.
- Labels are weak and incomplete: the 38 known cohorts are mostly `probable` (35 of 38) and were found by the same sort of reading the features try to imitate; unlinked pairs include unrecognised true overlaps, so precision measured with all non-positive test pairs as negatives is a lower bound. Pool B negatives (different countries) make `same_country` look better than it is; the ablation without it is the fair comparison.
- Small positive set: 100 pairs in 38 cohorts, about 37 with methods text on both sides. Intervals across folds and repeats are not independent. No claim of clinical or general validity.
- Text coverage: 181 of 338 primary studies have no methods section in `data/markdown/` (abstract-only or unmatched heading); for them only abstract, author, country, journal, year and sample-size features are available and the ranking is weaker. `country` is unknown for about one in five candidates.
- Similarity is lexical (TF-IDF) by default: papers on the same protocol from different groups also score high, so shared methods text is evidence of a shared design, not of shared animals.
- Full texts are copyrighted: snippets are capped at 300 characters, `data/markdown/` is not committed, and the CSV and JSON must not be exposed to anonymous users beyond that.
- Wording: candidate links, probable overlap, not duplicate publication, never "the same dogs" unless a paper says so; counts of independent cohorts are scenarios until reviewed.

## 7. Build plan for the agent

Run from `core/` (`C:\Workspaces\Babesiosis\core`). Use `encoding="utf-8"` when opening files (Windows default is cp1252).

1. Read: `experiment_specs/README.md`, `TEMPLATE.md`, this spec, `cohorts.json` (a few cohorts), `docs/database.md` (the `dbo.article_section` and `dbo.search_passages` lines), `scripts/experiment_pairwise.py` (JSON assembly, `script_version`, interpretation style), and three of `data/markdown/CB001.md`, `CB046.md`, `CB006.md` for heading shapes. Done when the heading regex and the date patterns are written down.
2. Tidy: not applicable.
3. Script: write `scripts/experiment_cohorts.py` with a docstring (inputs, outputs, run command, dependencies numpy, scipy, scikit-learn, environment `.venv-nlp`), functions per section 3, and options `--code`, `--include-types`, `--min-methods-words`, `--neg-per-pos-cohort`, `--neg-per-pos-country`, `--folds`, `--repeats`, `--rank-model`, `--top-n`, `--score-floor`, `--embeddings`, `--seed`. Default of every option as in section 4.1. Create the decisions CSV with its header if absent.
4. Run (expected a few minutes; about 57,000 pairs and 50 model fits):
   `.venv-nlp/Scripts/python.exe -I scripts/experiment_cohorts.py --code EXP14-CORPUS-cohorts`
5. Load: `Babesiosis.Console --datasets-only` from the console project (`ReviewRoot` must point at `core/`); run the SQL check in acceptance check 8.
6. Verify: acceptance checks 1 to 9. Fix and re-run until all pass.
7. Document: add `experiment_cohorts.py` to `scripts/README.md`; add `cohorts`, `pair_features_summary`, `classifier_performance`, `candidate_links` to the `dbo.experiment_result` line of `docs/database.md`; add the requirements comment; set EXP14 Readiness in `experiment_specs/README.md` to "built"; update `docs/ml-experiment-plan.html` status if kept.
8. Optional, after 1 to 7 pass: a web view for method `cohorts` in `webapp/Babesiosis.Web/src/app/modules/experiments/views/` (candidate table with the two snippets side by side). Without it the app shows the interpretation plus formatted JSON.

## 8. Open questions

1. Dense embeddings. Default: TF-IDF only, because no embedding model or SQL driver is installed in `.venv-nlp` and the SQL vectors are 1,536-dimensional Azure OpenAI vectors that cannot be reproduced locally. If the owner exports the methods-passage means from `dbo.article_section` to JSON, pass `--embeddings` and the run adds `sim_methods_dense`.
2. Case reports. Default: excluded (66 articles; only `CB284` is a cohort member). Include with `--include-types primary,case_report` if duplicate case reports should be hunted too.
3. Pool B definition (negatives from different countries). Default: five per positive from each pool as in 3 step 5. If the owner prefers only cohort-different negatives, set `--neg-per-pos-country 0`.
4. Rank model. Default `logistic` for interpretable coefficients; switch to `hgb` or an average if the cross-validated precision at 10 is clearly better.
5. Independent-cohort count: `build_outputs.py` may count a different article set (it prints 303 + 38 = 341 for the core set by this spec's reading). Default: report both numbers when they differ.
