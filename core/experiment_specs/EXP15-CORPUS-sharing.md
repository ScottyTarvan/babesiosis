# EXP15 CORPUS sharing: What predicts shared individual-level data

| Field | Value |
|---|---|
| Experiment code | `EXP15-CORPUS-sharing` |
| Layer | 3 corpus |
| Method token | `sharing` (goes in `experiment.method`) |
| Dataset(s) | `null`. The run reads `articles.jsonl` only (dataset status is carried on each article as `dataset_status_code`). `datasets.jsonl` is read only to check the status-1 link (`linked_articles[]`), not to model. |
| Readiness | ready |
| Python environment | `.venv` (numpy 2.5.4). Logistic regression, Firth correction, likelihood-ratio tests and Wald intervals are written in numpy. scipy and statsmodels are NOT in `.venv`; do not install them. scikit-learn 1.9.1 is in `.venv-nlp` and is needed only for the optional tree (Section 3, step 9), which is off by default. |
| Estimated build effort | small to medium (the Firth fit and permutation screen are the only non-trivial parts) |
| Suggested model for the building agent | haiku. The rules are fixed below; the work is data assembly and IRLS code. |
| Depends on | none. EXP12 shares the same country and species grouping; reuse its normalisation functions if EXP12 exists, otherwise copy them. |

## 1. Question and hypotheses

1. Among canine articles whose data could be assessed, which study features predict that the authors' individual-level data were verifiably downloadable (dataset status 1)?
2. Has that changed with publication year?
3. Separately: which features predict that the full text was inaccessible (status 5), which is a question about accessibility of the article, not about data availability?

Hypotheses (exploratory; the card names no literature hypothesis):

- H1. Recent articles (2021 onward) are more likely to share data than older ones (positive year slope).
- H2. Articles with a PubMed Central identifier (`pmcid` present, a proxy for open access) are more likely to share data.
- H3. Studies of `B. canis` are more often shared than studies of other species groups, because of the larger number of cohorts; direction not fixed in advance.

A negative finding is: no predictor's Firth likelihood-ratio test survives BH at alpha 0.05 across the univariable screen, and the year slope's interval includes an odds ratio of 1.

## 2. Data

### 2.1 Sources

- `articles.jsonl`: fields `id`, `scope_label`, `include_type`, `first_pub_date`, `journal`, `country`, `evidence_type`, `species_short`, `primary_category`, `pmcid`, `sample_size`, `n_infected_dogs`, `n_controls`, `dataset_status_code`, `dataset_status`, `fulltext_checked`, `dataset_ids[]`.
- `datasets.jsonl`: `dataset_id`, `status_code`, `linked_articles[]`, `verification_date`. Used to check that every article with `dataset_status_code == 1` is linked to a status-1 dataset record (32 CB articles in the link check; see Section 2.5).
- `datasets.md` (repository root of `core/`), section header: "Verification date: 2026-10-23 (rounds 1–3) and 2026-10-28 (round 4, articles published 2006–2016)." Quote these dates in the interpretation; the status codes were assigned by the review's own checks on those dates, so a later check could change them.
- `search-log.md` for the caveat text.

Licence: not applicable (no third-party data is redistributed; counts only).

### 2.2 Tidy file required

Not applicable.

### 2.3 Variables and filters

Analytic population (canine evidence, primary studies):

- `id` starts with `CB`;
- `include_type` is `primary` or `case_report` (drops 40 `review` records; no review has a status-1 outcome, so they would produce separation);
- `dataset_status_code` is not null (all 444 canine records have one).

Count: 444 canine minus 40 reviews = 404 analytic articles (includes case reports, which are primary studies of one dog).

Outcome A (main, data availability): `y_A = 1` if `dataset_status_code == 1`, `0` if the code is 2, 3 or 4, and the record is excluded if the code is 5 (status 5 is modelled separately as accessibility).

Outcome B (accessibility): `y_B = 1` if `dataset_status_code == 5`, `0` otherwise, over the full analytic population of 404.

Predictors. Names are the variable names in the output JSON; the source field is shown in parentheses.

| Name | Definition | Levels / coding |
|---|---|---|
| `year_c` | `first_pub_date` year minus 2016 | continuous |
| `period` | 2006-2010, 2011-2015, 2016-2020, 2021-2026 | sensitivity only (2006-2010 is the reference) |
| `journal3` | journal name lowercased and stripped; top three by count of analytic articles, then `Other` | levels: `Veterinary parasitology` (34 canine articles after case folding), `Veterinarski arhiv` (10), `Journal of the South African Veterinary Association` (9); ties broken alphabetically; reference: `Other` |
| `country5` | country group as in EXP12 (Section 2.3 there): keyword rule, earliest match; keywords for Europe listed below | levels: `India` (85 canine articles), `South Africa` (36), `Europe`, `Other`, `Unstated` (100); reference: `Other` |
| `species4` | species group, EXP12 rule | levels: `B. canis` (142), `B. gibsoni` (90), `B. rossi` (43), `other/mixed` (146 + 23 `B. vogeli` = 169 under this model; B. vogeli merged here because it has few articles); reference: `B. canis` |
| `evidence` | evidence group, EXP12 rule over `evidence_type` | levels after reviews are dropped: `descriptive` (reference), `associational`, `mechanistic`, `prognostic` |
| `pmcid_present` | `pmcid` is non-empty | 0/1 |
| `log10_n` | log10 of the parsed sample size (Section 3, step 3), centred on its mean, standardised | continuous; missing for articles with no parsable number |
| `category_group` | `primary_category` collapsed: `ERY`, `INF`, `SEV`, `MET`, `REN`, `COA`, `other` | univariable screen only |

Europe keyword list for `country5` (case-insensitive substring, earliest match wins): Croatia, Poland, Ukraine, Serbia, Germany, Slovakia, Romania, Russia, Italy, Greece, Spain, France, Portugal, Hungary, Czech, Bulgaria, Netherlands, Belgium, Austria, Switzerland, United Kingdom, UK, Denmark, Sweden, Norway, Finland, Ireland, Slovenia, Bosnia, Montenegro, North Macedonia, Albania, Moldova, Belarus, Latvia, Lithuania, Estonia. Turkey and Türkiye are placed in `Other` (their continental status is contested). Note: the source contains a mojibake form of Türkiye (`T�rkiye`); match on `rkiye` and `Turkey` as `Other` regardless.

Missing-data rule. Main model: complete cases on every term in the model. `log10_n` parses for 378 of 444 canine articles (66 missing), so it is NOT in the main model. It enters the sensitivity model (Section 3, step 6), which is run on complete cases and reports its n.

Counts already computed (from `articles.jsonl`, 2026-11-05):

- Canine articles by `dataset_status_code`: 1 = 32, 2 = 1, 3 = 10, 4 = 210, 5 = 191. Total 444.
- Outcome A population: status 1 vs 2, 3, 4 among the analytic set. Status 1 in reviews = 0, so after dropping reviews the status-1 count stays 32. The assessed (non-5) analytic count is 225 (253 non-5 canine minus 28 non-5 reviews). Events: 32. Events per parameter in the main model (32 events over 14 parameters including the intercept) is about 2.3: below 10, so Firth is required (Section 3, step 5).
- Status 1 by publication period (assessed, all canine): 2006-2010 0 of 27; 2011-2015 1 of 40; 2016-2020 12 of 65; 2021-2026 19 of 121.
- Status 1 by species group (assessed, all canine): B. rossi 9 of 25; B. canis 16 of 76; B. gibsoni 2 of 60; B. vogeli 1 of 12; other/mixed 4 of 80.
- Status 1 by evidence group (assessed, all canine): associational 16 of 78; descriptive 11 of 131; mechanistic 3 of 12; prognostic 2 of 4; review 0 of 28.
- Status 1 by country group (assessed, all canine): South Africa 7 of 24; Croatia 8 of 15; Germany 3 of 5; Poland 2 of 22; India 2 of 59; Other 6 of 76; Unstated 4 of 27; Brazil, Serbia and Ukraine 0 of 10, 0 of 6 and 0 of 9.
- Status 1 with `pmcid` present: 28 of the 32 status-1 articles. `pmcid` is present on 86 of the 444 canine articles.
- Status 5 (accessibility) by period: 2006-2010 32; 2011-2015 45; 2016-2020 48; 2021-2026 66. Total 191.
- Status 5 coincides with `fulltext_checked == false` for all 191 cases, but `fulltext_checked == false` also holds for 70 status-4 and 4 status-1 articles. Do not include `fulltext_checked` as a predictor: it is part of the mechanism that defines status 5.

### 2.4 Source-group note

Status 1 does not mean independence: several status-1 articles share a dataset (`independent_source`). Analyse articles, not datasets, and report that 32 status-1 articles map to fewer independent sources (see `datasets.jsonl` `independent_source`). CB510 and CB511 are one study published twice; count them once: keep the one with `pmcid` present, and drop the other from both outcome models. Record the dropped ID in `run_notes`.

### 2.5 Link check

For each article with `dataset_status_code == 1`, confirm that some `datasets.jsonl` record with `status_code == 1` lists it in `linked_articles`. Expected: all 32 link (the 32 CB article IDs in `linked_articles` of status-1 datasets were checked: CB005, CB006, CB013, CB017, CB019, CB032, CB038, CB042, CB046, CB050, CB071, CB082, CB091, CB093, CB098, CB101, CB106, CB112, CB115, CB122, CB126, CB130, CB133, CB137, CB138, CB139, CB147, CB148, CB152, CB476, CB516, CB517). A mismatch is recorded in `run_notes` and the article keeps its `dataset_status_code`.

## 3. Method

Parameters with defaults (all written to `experiment.parameters`):

`seed` 20261105 · `permutations` 5000 · `alpha` 0.05 · `firth` `auto` (Firth when events per parameter < 10, else plain MLE; the choice is written) · `min_events_per_level` 3 · `firth_epv_cut` 10 · `tree` `off` (`on` only with `.venv-nlp`) · `tree_depth` 3 · `year_reference` 2016 · `exclude_reviews` true · `dedupe_ids` `CB510,CB511` (keep the one with `pmcid`) · `articles_path` `articles.jsonl` · `datasets_path` `datasets.jsonl`.

1. **Load.** Stream `articles.jsonl` (`json.loads` per line). Keep `id` starting with `CB`. Apply the analytic population (Section 2.3). Apply the dedupe rule. Run the link check (Section 2.5) and write its result.

2. **Coding.** Build the design matrix for each model in Section 2.3 with reference levels as stated. Level counts per term must be at least `min_events_per_level` events (status 1) or the level is merged into the reference category, and the merge is written to `run_notes`. Stop with an error if the design matrix is rank-deficient.

3. **Sample size.** `n_total` = `n_infected_dogs + n_controls` when both are integers; else the first integer in `sample_size` (string match `\d[\d,]*`, commas removed); else missing. Use `log10(n_total)`, then centre and divide by the standard deviation over non-missing values. Record how many values came from each route.

4. **Maximum-likelihood logistic regression (plain).** Newton-Raphson / IRLS in numpy: `beta <- beta + (X'WX)^-1 X'(y - p)`, with `W = diag(p(1-p))`, starting from zeros, convergence when `max|delta beta| < 1e-8` or 50 iterations. Standard errors from `(X'WX)^-1` at convergence. Odds ratio `exp(beta)`; Wald 95% interval `exp(beta +- 1.96 se)`. Wald p two-sided by `math.erfc`.

5. **Firth penalised logistic regression (default when `firth == auto` and events per parameter < `firth_epv_cut`).** Penalised log-likelihood with Jeffreys prior. IRLS update: `h_i` = diagonal of `W^{1/2} X (X'WX)^-1 X' W^{1/2}`; score `U = X'(y - p + h*(0.5 - p))`; update `beta <- beta + (X'WX)^-1 U`. Converge as in step 4. SE from `(X'WX)^-1` at convergence. Report the Firth fit as primary whenever it is used, with the plain MLE shown alongside in `odds_ratios` (field `mle_or`) for comparison. Events per parameter in the main model is about 2.3, so Firth is the default result here.

6. **Likelihood-ratio tests.** For each term (univariable and multivariable), LR statistic = 2 (loglik_full - loglik_reduced) using the penalised log-likelihood for Firth models and the plain log-likelihood otherwise; df = number of parameters removed. p value: the chi-square upper tail, computed with the Wilson-Hilferty approximation (numpy and `math.erfc` only). Also record Wald p for comparison.

7. **Univariable screen (BH family).** For each predictor in Section 2.3 (including `category_group`, `period`, `pmcid_present`, `log10_n`, `journal3`, `country5`, `species4`, `evidence`, `year_c`) fit a model with that predictor alone on the analytic population. For `log10_n`, fit on complete cases of `log10_n` and record the n. Compute the LR p value (step 6). Then the permutation p value by permuting `y` (outcome A) `permutations` times, refitting the univariable model with the same method, and taking `(1 + #{LR_perm >= LR_obs}) / (1 + permutations)`. Benjamini-Hochberg across the univariable p values (one per predictor). The screen's BH family is these predictors; say so in the output.

8. **Multivariable main model (outcome A).** Terms: `year_c`, `journal3` (2 df), `country5` (4 df), `species4` (3 df), `evidence` (3 df), `pmcid_present` (1 df). That is 14 parameters including the intercept; with 32 events, 2.3 events per parameter, so Firth is used under `auto`. Report the Firth fit, OR, interval, and LR p per term. BH across the LR p values of these terms (family = the multivariable terms, separate from the screen). Note the family in `run_notes`.

   Sensitivity model (`sensitivity_sample_size`, same method, complete cases on `log10_n`): the main terms plus `log10_n`. Report its n and events. Also a sensitivity model with `period` replacing `year_c` (reference 2006-2010; the 2006-2010 cell has zero events, so that dummy is not estimable by ML and Firth must be used; report it as not estimable if the Firth iteration does not converge in 100 steps).

   Sensitivity model (`no_species`): drop `species4` for the case where its levels dominate the data.

9. **Optional tree (off by default).** Only if `tree == on` and the script runs under `.venv-nlp` (scikit-learn 1.9.1). `sklearn.tree.DecisionTreeClassifier(max_depth=3, random_state=seed, min_samples_leaf=10, class_weight="balanced")` on the same predictors (one-hot coded, `log10_n` filled with its median and a flag). Report leaf sizes, leaf event rates, and the feature importances with a note that they are unstable at 32 events. Cross-validation: 5-fold stratified with the same seed, report AUC with a bootstrap 95% interval (1000 resamples, seed). Default run: the `tree` result is omitted and `run_notes` says so.

10. **Accessibility model (outcome B).** Full analytic population of 404 canine primary articles, same terms as step 8 (no `fulltext_checked`). Firth under `auto`. Output as `accessibility_model`. Interpret separately from outcome A.

11. **Year trend series.** Per publication year (2006 to 2026, 21 years): `n_analytic`, `n_status1`, `n_status5`, proportion status 1 among non-5 (`p_status1_assessed`), proportion status 5 among all analytic, and Wilson 95% intervals for both proportions. Also the logistic slope `year_c` from step 8 expressed as an odds ratio per year, with its interval. Output as `year_trend`, which is the data series for a plot; the plot itself is not built here.

12. **Outcome counts.** Table of status codes 1 to 5 against the analytic population: all canine, and reviews separately, and the link-check result. Output as `outcome_counts`.

13. **Multiple testing summary.** Two BH families as in steps 7 and 8, plus the accessibility family (step 10, BH across its own terms). Never pool the families.

14. **Outputs.** Section 4.1.

## 4. Outputs

### 4.1 Experiment JSON

File: `data/experiments/EXP15-CORPUS-sharing.json`.

`experiment` block:

- `code`: `EXP15-CORPUS-sharing`
- `name`: `What predicts shared individual-level data, canine primary articles`
- `description`: one sentence: predictors of verified individual-level data availability (status 1) among assessed canine primary articles, with year trend and a separate accessibility model for status 5.
- `method`: `sharing`
- `dataset`: `null`
- `parameters`: every setting in Section 3 with its default, plus `outcome_A_definition`, `outcome_B_definition`, `status_dates` (`"2026-10-23 (rounds 1-3); 2026-10-28 (round 4)"`), and the guardrail string `"status_5_is_accessibility_not_availability"`.
- `script`: `scripts/experiment_sharing.py`
- `script_version`: first 12 characters of the SHA-256 of the script file.
- `run_utc`: ISO 8601 UTC.
- `n_subjects`: 225 (assessed analytic articles in outcome A). The accessibility model n (404) goes in its payload.
- `n_variables`: number of model terms in the main model (14 parameters, 6 predictors).
- `n_tests`: LR tests in the univariable screen (9) plus terms in the multivariable model (14) plus accessibility terms (14) plus year-trend series (1).
- `summary`: one plain paragraph: n, events, the year odds ratio with its interval, and the number of predictors that pass BH in the screen.

`associations`: `[]`. `cluster_assignments`: `[]`.

`results[]`:

1. `interpretation` (sort 0): `{"sections": [{"heading": str, "paragraphs": [str]}]}`. Headings: Question; What was done; Main findings; Accessibility, not availability; Limits. Section 6 gives the required content.

2. `outcome_counts` (sort 1): `{"status_codes": [{"code": int, "label": str, "n_all_canine": int, "n_primary_analytic": int}], "link_check": {"status1_articles": 32, "linked_to_status1_dataset": int, "unlinked": [str]}, "dedupe": {"dropped": [str], "kept": [str]}, "verification_dates": ["2026-10-23", "2026-10-28"]}`.

3. `odds_ratios` (sort 2): `{"outcome": "A_status1_vs_2_3_4", "firth_used": bool, "events": 32, "n": int, "epv": float, "terms": [{"term": str, "level": str|null, "or": float, "ci_low": float, "ci_high": float, "mle_or": float|null, "p_lr": float, "p_wald": float, "p_bh": float, "events_in_level": int}], "univariable": [{"predictor": str, "n": int, "events": int, "lr_stat": float, "df": int, "p_lr": float, "p_permutation": float, "p_bh": float, "passes_bh": bool, "or_per_unit": float|null, "ci_low": float|null, "ci_high": float|null}], "sensitivity": [{"name": str, "n": int, "events": int, "terms": [same shape as "terms"], "note": str}]}`.

   The `sensitivity` list contains `log10_n` (complete cases), `period` (possibly not estimable, with `note`), and `no_species`.

4. `accessibility_model` (sort 3): `{"outcome": "B_status5_vs_other", "firth_used": bool, "events": 191, "n": 404, "terms": [same shape as above], "note": "accessibility of the full text, not data availability; fulltext_checked not a predictor"}`.

5. `year_trend` (sort 4): `{"years": [int], "n_analytic": [int], "n_status1": [int], "n_status5": [int], "p_status1_assessed": [float|null], "ci_status1_assessed": [[float,float]|null], "p_status5_all": [float], "ci_status5_all": [[float,float]], "slope_or_per_year": float, "slope_ci": [float,float], "reference_year": 2016}`.

6. `tree` (sort 5, optional): only when `tree == on`. `{"leaves": [...], "feature_importance": [...], "cv_auc": float, "cv_auc_ci": [float,float], "note": "unstable at 32 events; not a classifier for use"}`.

7. `run_notes` (sort 6): `{"included": int, "excluded_reviews": int, "dedupe": {...}, "link_check": {...}, "merged_levels": [...], "firth_decisions": [...], "families_bh": ["univariable screen (9 predictors)", "main model terms (14)", "accessibility terms (14)"], "missing": {"log10_n": int}, "packages": ["numpy"], "not_used": ["scipy", "statsmodels", "sklearn (tree off)"], "fulltext_checked_excluded_as_predictor": true}`.

### 4.2 Other artefacts

None. The year-trend series is in `year_trend`. No file is written outside `data/experiments/`.

## 5. Acceptance checks

1. Analytic population: 404 canine primary articles (444 minus 40 reviews); outcome A assessed n = 225, events = 32. Outcome B n = 404, events = 191.
2. Link check: all 32 status-1 articles are linked to a status-1 `datasets.jsonl` record (or the mismatch list is written and explained in `run_notes`).
3. Dedupe: CB510 or CB511 appears once in the analytic population.
4. Firth: with `firth == auto` and EPV 2.3 < 10, the output has `firth_used = true`. Recomputed Firth score at the reported beta is within 1e-6 of zero.
5. The plain MLE on the univariable `pmcid_present` term matches a direct two-by-two calculation (OR = (a*d)/(b*c) with the cell counts from `articles.jsonl`), within the Haldane-free precision of the MLE.
6. Permutation check: with outcome A permuted (script flag `--shuffle-check`, not in the default run), the proportion of univariable predictors with `p_permutation < 0.05` is about 0.05 (record once in `run_notes`).
7. Reproduction: two runs with the same seed give identical `odds_ratios`, `accessibility_model` and `year_trend` payloads.
8. Load: the console reads the file (Section 7 step 5); `experiment.dataset` is null.
9. Interpretation reads correctly for a veterinary reader; it states the events count (32) in the first paragraph of Main findings.

## 6. Caveats and reporting language

- **Status codes are the review's own checks on particular dates** (2026-10-23 for rounds 1–3; 2026-10-28 for round 4, per `datasets.md`). A later check could change them. Quote the dates.
- **Status 5 is accessibility, not availability.** It means the full text was not accessible to the review (`fulltext_checked` false for all 191). It is modelled separately and must not be read as "did not share". Status 4 means "not located after documented checks" and is in the non-event group of outcome A. Status 2 and 3 are also non-events; status 3 is request-only access.
- **Few events.** 32 status-1 articles among 225 assessed. Events per parameter about 2.3. Firth penalised estimates are reported; intervals are wide. Do not describe any predictor as "the cause" of sharing.
- **Non-independence.** Several status-1 articles share a source dataset (`independent_source`). Articles are the unit here; the independent-source count is smaller. CB510/CB511 counted once.
- **Species and country are not comparable across cells.** Status 1 counts are very small in several cells (Brazil, Serbia, Ukraine 0 events; 2006-2010 0 events). Empty cells are merged or not estimable; say so.
- **Open-access proxy.** `pmcid` presence is a proxy for open access, not the open-access status itself. 28 of the 32 status-1 articles have a `pmcid`, so this predictor carries much of the signal; say whether it is a confounder of the year effect.
- **Sample size** is missing for a substantial share of articles and is therefore a sensitivity term only.
- **Wording.** "Verified individual-level download", not "data sharing rate". "Assessed articles", not "all articles". No model here is a usable prediction tool.

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md`, this file, `core/CLAUDE.md`, `docs/core-tables.md` (articles.jsonl and datasets.jsonl field lists), `docs/ids-and-codes.md` (dataset status codes 1 to 5), `datasets.md` header (verification dates). Do not read `index.md`, `research-map.md` or `data/syndromes/mentions.jsonl`.

2. **Tidy.** Not applicable.

3. **Script.** Create `scripts/experiment_sharing.py` in `core/`. Module docstring: inputs (`articles.jsonl`, `datasets.jsonl`), output (`data/experiments/EXP15-CORPUS-sharing.json`), the run command below, "numpy only by default; `--tree on` needs `.venv-nlp` with scikit-learn". Implement: IRLS logistic, Firth, Wilson-Hilferty chi-square tail, normal tail via `math.erfc`, Wilson score intervals for proportions, BH (copy `bh_adjust` from `scripts/experiment_pairwise.py`). Do not add anything to `scripts/requirements-experiments.txt` unless `--tree on` is used; then note scikit-learn in the docstring only. Confirm numpy first: `.venv/Scripts/python.exe -I -c "import numpy; print(numpy.__version__)"`.

4. **Run.** From `core/`:
   `.venv/Scripts/python.exe -I scripts/experiment_sharing.py --code EXP15-CORPUS-sharing --seed 20261105 --permutations 5000`
   Expected runtime: under 2 minutes (the univariable permutation screen refits about 9 models 5000 times each, with at most 11 parameters on 225 rows).

5. **Load.** From the repository root:
   `dotnet run --project console/Babesiosis.Console -- --datasets-only`
   Confirm `ReviewRoot` in `appsettings.json` points at `core/`. Then SQL check via `babesiosis-local-db`: `SELECT experiment_code, method, dataset_code FROM dbo.experiment WHERE experiment_code = 'EXP15-CORPUS-sharing';` and `SELECT kind, sort_order FROM dbo.experiment_result WHERE experiment_code = 'EXP15-CORPUS-sharing' ORDER BY sort_order;` (expect 6 rows without `tree`, 7 with it: interpretation, outcome_counts, odds_ratios, accessibility_model, year_trend, run_notes). Check column names against `docs/database.md` first.

6. **Verify.** Run Section 5 checks. Check 5.5 is a hand calculation from `articles.jsonl` cell counts, recorded in `run_notes`.

7. **Document.** Add a row for `scripts/experiment_sharing.py` to `scripts/README.md`, and a row for `EXP15-CORPUS-sharing` to the experiment table in `docs/database.md`. Update the EXP15 status on the `docs/ml-experiment-plan.html` card if the page is kept.

8. **Optional.** A year-trend plot in the web app, from `year_trend`, only after steps 1 to 7 pass. The `tree` result is an optional extra; do not add it unless the user asks.

## 8. Open questions

1. Reviews: excluded from the analytic population (no status-1 review, so they would separate). Default: excluded; `exclude_reviews` = true.
2. Whether `include_type == "case_report"` (66 articles, one dog each) should be a predictor or excluded. Default: included, with `include_type` not modelled; a sensitivity drop is a one-line change if the building agent is asked.
3. `journal3` picks the top three journals by count, which is arbitrary beyond the first. Default: as specified; a reviewer may prefer a pre-named list.
4. Whether status 4 belongs with the events or the non-events. Default: non-event (it is "not located after documented checks", not a download).
5. Whether to run the optional tree. Default: off; it needs `.venv-nlp` and is not evidence at 32 events.
