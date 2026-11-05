# EXP06 DS05 anomaly: atypical dogs in the BET cohort

| Field | Value |
|---|---|
| Experiment code | `EXP06-DS05-anomaly` |
| Layer | 1 single dataset |
| Method token | `anomaly` (goes in `experiment.method`) |
| Dataset(s) | `DS05` (150 dogs, `data/tidy/DS05.json`) |
| Readiness | ready (tidy file exists) |
| Python environment | `.venv-nlp` (numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.1 installed; `IsolationForest` and `MinCovDet` come from scikit-learn). `.venv` has only numpy 2.5.4 and cannot run this script. No new package is needed and `.venv-nlp` has no `pip`; do not install anything. Add `scipy>=1.13` and `scikit-learn>=1.5` to `scripts/requirements-experiments.txt` if EXP02 has not already (comment: EXP02 and EXP06 need `.venv-nlp`). Reading the raw workbook for the check in section 3 step 10 uses the stdlib reader `read_workbook()` in `scripts/tidy_ds05.py` (load it with `importlib.util.spec_from_file_location`; there is no openpyxl). |
| Estimated build effort | small to medium (about 2 hours of agent work, plus the manual raw-sheet check) |
| Suggested model for the building agent | sonnet: standard estimators, the care is in reporting and the raw check |
| Depends on | `data/tidy/DS05.json`. Shares preprocessing rules with EXP02 (copy them, do not import); EXP02 need not have run. |

## 1. Question and hypotheses

Q1. Which dogs have admission profiles that do not fit the rest of the cohort, by two independent methods (isolation forest, robust Mahalanobis distance), and do the two methods agree?
Q2. Do the three B. rossi + E. canis co-infected dogs, and the one B. vogeli dog, stand out? Expected: not necessarily; co-infection may not move routine admission variables. A finding that none of the four is among the top outliers is a valid negative result.

Negative finding: Spearman agreement between the two scores below 0.5 and fewer than 3 of the top-10 shared means the notion of "atypical" depends on the method; say so and report both lists. Also report if every top outlier turns out to be a data-entry or unit problem on the raw check (then the result is a data-quality list, not a biological one).

## 2. Data

### 2.1 Sources

- `data/tidy/DS05.json`: 150 subjects; `group_label`: `B. rossi only` 146, `B. rossi + E. canis` 3, `B. vogeli only` 1. The co-infected dogs are `BET023`, `BET072` and one more; the B. vogeli dog is `BET100` (from the tidy `notes`); read the exact subject codes from `subjects[].group_label`, do not hard-code them.
- Raw sheet for the check: `data/raw/DS05/BET Study Dataset.xlsx`, sheet `Entire population` (header row 1, units row 2, one dog per row, ID in the first column; find the row by ID). Read-only.
- Licence and `independent_source`: copy from `tidy["dataset"]` into `run_notes`.

### 2.2 Tidy file required

Not applicable: the tidy file exists.

### 2.3 Variables and filters

Input rule: `data_type in (N, O)` and `include_default = true` and `derived = false` and `derived_from` null or empty. This gives the same **22 variables** as EXP02:
`age_months, weight_kg, illness_days, temperature_c, pulse, respiratory_rate, lymph_node_score, haemoglobin, rcc, haematocrit, rdw, seg_neutrophils, band_neutrophils, lymphocytes, monocytes, eosinophils, platelets, nrbc_per_100_wbc, reticulocyte_pct, total_protein, albumin, habitus_score`.

`mcv, mch, mchc, wcc, arc, globulin` have `derived = false` in the tidy file but carry `derived_from` (arithmetic functions of other columns); they are excluded so that one measurement is not counted twice. Record this in `run_notes`. All `C`, `D`, `T` variables, `basophils`, `other_cells` and `month` are excluded.

Missing data: 37 dogs miss at least one of the 22 variables (`respiratory_rate` observed for 126 dogs, `temperature_c` 145, `illness_days` 148, `habitus_score` 147, haematology 148, `total_protein` and `albumin` 144). `BET065` and `BET066` have no haematology or biochemistry.

Rules:
1. Dogs missing more than 30 percent of the 22 variables (`max_missing_subject = 0.30`) are not scored: `BET065` and `BET066`. They are listed in `run_notes.dropped_subjects` with the reason, and 148 dogs are scored.
2. Remaining gaps are imputed once with `IterativeImputer(estimator=BayesianRidge(), max_iter=20, initial_strategy="median", random_state=child seed)` on the standardised matrix. Every imputed cell is recorded; an outlier whose score is driven by an imputed value is flagged (step 8).
3. Sensitivity (step 9) rescoring complete cases only checks that imputation does not create or hide outliers.

## 3. Method

One `numpy.random.default_rng(seed)`; draw child seeds with `rng.integers(0, 2**31 - 1)` in fixed order. Default `seed = 20261105`. The run reproduces bit-for-bit.

1. **Load and transform.** Subjects x variables matrix from `value_num`. For each variable that is non-negative with absolute skewness above 1.0 (`skew_threshold`) apply log1p (same rule as EXP02); record the list. Do NOT clip or winsorise: extreme values are the object of study.
2. **Standardise** after transformation: mean 0, SD 1 (ddof=1) over the scored dogs, after imputation (step above). Keep also the robust z-scores for step 7: `rz = (x - median) / (1.4826 * MAD)` on the transformed data using observed values only (a variable with MAD 0 gets rz computed with the SD instead; record which).
3. **Isolation forest.** `IsolationForest(n_estimators=1000, max_samples="auto", contamination="auto", max_features=1.0, bootstrap=False, random_state=child seed)` fit on the 22 standardised variables (148 x 22). Raw anomaly score = `-score_samples(X)` (higher is more anomalous). Stability: refit with 10 different child seeds, report the minimum pairwise Spearman correlation between the 10 score vectors (`if_seeds = 10`); the reported score is the mean over those 10 fits (so the reported value does not depend on one seed).
4. **Robust Mahalanobis distance.** `MinCovDet(support_fraction=0.75, random_state=child seed)` on the standardised matrix. If fitting fails or the MCD covariance is singular (condition number above 1e10), drop from each variable pair with absolute Pearson correlation above 0.95 the variable with more missing values (ties: the later in the list), refit, and record the dropped variables in `run_notes`; the isolation forest still uses all 22. Squared distance `d2` from `mcd.mahalanobis(X)`. Reference cut: chi-square quantile 0.975 with df = number of variables used; report how many dogs exceed it (expect many with skewed data: this is why the label below uses ranks, not this cut).
5. **Normalised scores.** For each method, `norm = (rank - 1) / (n - 1)` where rank is the average rank (1 = least anomalous, n = most), so that 1.0 is the most anomalous dog and 0.0 the most typical. `combined = mean(norm_if, norm_mcd)`. Per-dog `score` in `cluster_assignments` is `combined`.
6. **Outlier label.** `cluster_label = "outlier"` if `combined >= 0.95` (parameter `outlier_quantile = 0.95`, about the 8 most atypical of 148 dogs), else `"typical"`. The threshold is stated in the interpretation. In addition, a dog is flagged `consensus_outlier` in the `top_outliers` table (not in the label) if it is in the top 10 of both methods.
7. **Drivers.** For each of the top `top_n = 10` dogs by `combined` and, always, for the four pathogen-minority dogs (the three `B. rossi + E. canis` dogs and the one `B. vogeli only` dog) whether or not they rank in the top 10:
   a. Robust z-scores beyond +/-3 (`z_threshold = 3.0`): list variable, original value with unit, the cohort median and the reference range from `variables[].ref_low/ref_high`, and the rz.
   b. Per-feature isolation depth: for each variable fit a univariate `IsolationForest(n_estimators=200, random_state=child seed)` on that column (observed values only) and report the variable's univariate anomaly score for the dog; list the top 3 variables by that score.
   c. MCD contribution: `contribution_j = d2_full - d2_without_j`, with `d2_without_j` computed from the same MCD location and covariance with variable j removed (sub-vector and sub-matrix); list the top 3 positive contributions and their share of `d2_full`.
   d. Mark each listed variable `imputed = true` if the dog's value for it was imputed.
8. **Agreement between the two scores.** Spearman rho between `norm_if` and `norm_mcd` with a permutation p value (`perm = 5000`, copy `rankdata` and `perm_p` from `scripts/experiment_pairwise.py`; do not import it, `-I` removes the script folder from the import path) and a 95 percent bootstrap percentile interval (`ci_boot = 1000`). Overlap of the top 10: the count shared, the Jaccard index, and the list of dogs in one list only. Overlap at top 5 percent and top 20 as well. A scatter data table (`subject_code, norm_if, norm_mcd`) for the figure.
9. **Sensitivity.** Recompute both scores for (S1) complete cases only (about 111 dogs, no imputation), (S2) no log transform, (S3) the 28-variable set including the six arithmetic-derived variables. Report, against the main combined score on the shared dogs, the Spearman rho and the overlap of the top 10; and whether each of the four pathogen-minority dogs keeps its rank band (top 5 percent, top 20 percent, rest).
10. **Raw-sheet check (mandatory before interpretation).** Every dog in `top_outliers` (the top 10 by `combined`, plus the top 3 by each method if not already present, plus the four pathogen-minority dogs) is checked against the raw sheet `Entire population` of `data/raw/DS05/BET Study Dataset.xlsx`: find the row by dog ID, compare each driver variable's raw cell with the tidy value, check units against the units row 2 and against the reference range (a haematocrit of 28 instead of 0.28, a haemoglobin in g/dL instead of g/L, a cell with text such as `UNKNOWN`), and check whether the dog's `notes` in the ID cell mention anything. The building agent does this with `read_workbook()` from `scripts/tidy_ds05.py` and records the findings by hand in the file `experiment_specs/EXP06-raw-check.json` (not under `data/`, so the loader never sees it):
    `{"BET0xx": {"status": "matches_raw" | "discrepancy" | "unit_suspect" | "not_checked", "note": "plain sentence", "raw_row": int}}`.
    The script takes `--raw-check experiment_specs/EXP06-raw-check.json`; if the file is absent every `raw_check.status` is `"pending"` and the interpretation opens with a paragraph stating that none of the outliers has yet been checked against the raw sheet and must not be interpreted biologically. Workflow: run once, do the check, write the file, run again. The interpretation only discusses an outlier biologically when its status is `matches_raw`; `discrepancy` and `unit_suspect` dogs are reported as data-quality findings and the run also reports the scores with those dogs' suspect values set to missing (re-imputed) as sensitivity S4 (agreement with the main score and new top-10 list).
11. **Pathogen-minority dogs, reported individually.** In the `top_outliers` table and in the interpretation, give each of the three `B. rossi + E. canis` dogs and the one `B. vogeli only` dog its own line: subject code, `group_label`, `norm_if`, `norm_mcd`, `combined`, rank among 148 (by combined), label, its drivers (step 7) and its raw-check status. Never pool them into a group statistic; the text says "three dogs, one dog: descriptive only". Do not test co-infection against anything (n = 3 and n = 1).

## 4. Outputs

### 4.1 Experiment JSON

File `data/experiments/EXP06-DS05-anomaly.json`; top-level keys `experiment`, `associations`, `cluster_assignments`, `results`.

`experiment`: `code` = `EXP06-DS05-anomaly`; `name` = "Atypical dogs, BET cohort"; `description` one sentence (two unsupervised anomaly scores over 22 admission variables; outliers need raw-sheet checks before interpretation); `method` = `anomaly`; `dataset` = `DS05`; `script` = `scripts/experiment_anomaly.py`; `script_version` = first 12 hex of the script's SHA-256; `run_utc`; `n_subjects` = 148; `n_variables` = 22; `n_tests` = 1 (the Spearman agreement test); `summary` = one paragraph (dogs scored, labelled outliers, agreement rho, top-10 overlap, where the four pathogen-minority dogs rank, how many top outliers have been raw-checked).

`parameters` (defaults): `{"seed": 20261105, "skew_threshold": 1.0, "max_missing_subject": 0.30, "imputation": "iterative_bayesian_ridge", "imputer_max_iter": 20, "if_n_estimators": 1000, "if_seeds": 10, "mcd_support_fraction": 0.75, "mcd_collinearity_threshold": 0.95, "outlier_quantile": 0.95, "top_n": 10, "z_threshold": 3.0, "univariate_if_estimators": 200, "perm": 5000, "ci_boot": 1000, "raw_check_file": "experiment_specs/EXP06-raw-check.json", "input_variables": [the 22 codes]}`.

`associations`: empty list.

`cluster_assignments`: 148 rows `{"subject_code": "BET001", "cluster_label": "typical", "score": 0.4123}` where `score` is `combined` (0 to 1, 4 decimals) and `cluster_label` is `outlier` or `typical`. `BET065` and `BET066` are not written.

`results[]` (4 decimals; each payload well under 2 MB):

| kind | sort_order | title | payload |
|---|---|---|---|
| `interpretation` | 0 | Explanation and interpretation | `{"sections": [{"heading": str, "paragraphs": [str]}]}` |
| `anomaly_scores` | 1 | Anomaly scores per dog | `{"threshold": {"outlier_quantile": 0.95, "combined_cut": float, "n_outliers": int}, "mcd": {"variables_used": [codes], "chi2_975_cut": float, "n_above_cut": int}, "isolation_forest": {"seed_stability_min_spearman": float}, "scores": [{"subject_code": "BET001", "group_label": str, "if_score": float, "norm_if": float, "mcd_d2": float, "norm_mcd": float, "combined": float, "rank": int, "label": "typical", "n_imputed": int}]}` (all 148 dogs, ordered by rank) |
| `top_outliers` | 2 | Most atypical dogs and the variables that drive them | `{"outliers": [{"subject_code": str, "group_label": str, "rank": int, "combined": float, "norm_if": float, "norm_mcd": float, "reason_listed": "top10" or "top3_if" or "top3_mcd" or "pathogen_minority", "consensus_outlier": bool, "drivers": [{"variable": "band_neutrophils", "value": 4.2, "unit": "x10^9/L", "cohort_median": 0.4, "ref_low": 0.0, "ref_high": 0.5, "robust_z": 6.1, "univariate_if": 0.78, "mcd_contribution": 31.2, "mcd_share": 0.22, "imputed": false}], "raw_check": {"status": "pending", "note": null, "raw_row": null}}]}` |
| `score_agreement` | 3 | Agreement between isolation forest and robust Mahalanobis | `{"spearman": {"rho": float, "ci95": [lo, hi], "p_value": float}, "top10": {"shared": int, "jaccard": float, "only_if": [codes], "only_mcd": [codes], "shared_codes": [codes]}, "overlap": {"top5pct": int, "top20": int}, "points": [{"subject_code": str, "norm_if": float, "norm_mcd": float}], "sensitivity": [{"name": "S1_complete_case", "n_subjects": int, "spearman_vs_main": float, "top10_shared_with_main": int, "pathogen_minority_bands": {"BET023": "top5pct"}}]}` |
| `run_notes` | 4 | Variables, missing data, dropped dogs and raw-check status | `{"input_variables": [{"code": str, "unit": str, "n_observed": int, "n_imputed": int, "transformed": bool}], "excluded_derived_from": ["mcv","mch","mchc","wcc","arc","globulin"], "dropped_subjects": [{"subject_code": "BET065", "reason": "no haematology or biochemistry"}], "mcd_dropped_for_collinearity": [], "robust_z_sd_fallback": [], "imputation": {"method": str, "cells_imputed": int}, "raw_check": {"file": str, "file_present": bool, "n_listed": int, "n_checked": int}, "environment": {"numpy": str, "scipy": str, "scikit_learn": str}, "dataset": {"independent_source": str, "licence": str}}` |

`interpretation` section headings, exactly: "Question", "What was done", "Raw-sheet check", "Most atypical dogs", "The co-infected and B. vogeli dogs", "Agreement between the two methods", "Limits". Plain language for a veterinary reader; every number computed. "Raw-sheet check" is first in content priority: it states how many of the listed dogs have been checked and the result per dog; if the check file is absent it says no outlier may be interpreted yet. "The co-infected and B. vogeli dogs" gives one paragraph per dog (four paragraphs) with rank and drivers.

### 4.2 Other artefacts

None under `data/`. The only extra file is the hand-written `experiment_specs/EXP06-raw-check.json` (step 10 of section 3), which is an input to the second run.

## 5. Acceptance checks

1. The script runs with `.venv-nlp/Scripts/python.exe -I` with no network and no unlisted package.
2. JSON keys as in 4.1; `n_subjects` = number of `cluster_assignments` = number of `anomaly_scores.scores` = 148; labels only `outlier` or `typical`; number of `outlier` labels = ceil(0.05 x 148) = 8 give or take ties; every `subject_code` exists in `data/tidy/DS05.json`.
3. `score` and the normalised scores lie in [0, 1]; the dog with the highest `combined` has rank 1.
4. Same seed, same file (compare after removing `run_utc`).
5. Isolation-forest seed stability: the minimum pairwise Spearman across the 10 seeds is reported; if below 0.9 say so in the limits.
6. The four pathogen-minority dogs each appear in `top_outliers` with `reason_listed` including `pathogen_minority` (even when not in the top 10) and each has a paragraph in the interpretation.
7. Sanity: inject a copy of the standardised matrix with one dog's `haematocrit` multiplied by 10 (test harness only, nothing saved); that dog must reach the top 3 of both scores and the driver list must name `haematocrit`.
8. Every dog in `top_outliers` has a `raw_check` status; at final delivery none is `pending` (task 5 below), and the interpretation does not interpret biologically any dog whose status is not `matches_raw`.
9. Sensitivity S1 to S4 present with Spearman and top-10 overlap values.
10. After the console load, `dbo.cluster_assignment` holds 148 rows for this experiment (8 or so `outlier`), and `dbo.experiment_result` holds the five kinds.

## 6. Caveats and reporting language

- Unsupervised outlier scores say a dog is unusual relative to this cohort, not that it is abnormal clinically or that it will do badly. No outcome exists in DS05. These scores are not prognostic.
- Outliers are as likely to be data-entry, unit or transcription errors as biology. Every outlier is checked against the raw sheet before it is interpreted; the text says which have and have not been.
- Imputed values can produce or hide outliers; imputed drivers are flagged.
- Skewed haematology variables mean the chi-square cut for Mahalanobis distance over-flags; the label uses ranks.
- The three E. canis co-infected dogs and the one B. vogeli dog are reported individually, as single cases. No test, no group mean.
- One hospital cohort, 148 dogs, 22 correlated variables; the isolation forest is not tuned and its top ranks can shift between seeds (stability reported).
- Wording: "atypical admission profile", not "abnormal dog"; "ranking", not "risk score".

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md`, `TEMPLATE.md`, `core/CLAUDE.md`, this spec, `scripts/experiment_pairwise.py` (docstring, `rankdata`, `perm_p`, argparse, output assembly, `script_version` hash), `scripts/tidy_ds05.py` (`read_workbook`, the `Entire population` column map), `data/tidy/DS05.json`. Done: you can name the 22 input variables and the four pathogen-minority dogs.
2. **Tidy.** None needed.
3. **Script.** Write `scripts/experiment_anomaly.py` with a module docstring (inputs, outputs, run command, dependencies numpy, scipy, scikit-learn) and an argparse option for every parameter in 4.1 with the stated defaults, including `--raw-check`. Copy shared helpers (`rankdata`, `perm_p`) rather than importing. Update `scripts/requirements-experiments.txt` if needed. Done: `--help` lists every parameter.
4. **Run (first pass).** From `core/`:
   `.venv-nlp/Scripts/python.exe -I scripts/experiment_anomaly.py --dataset DS05 --code EXP06-DS05-anomaly --name "Atypical dogs, BET cohort" --seed 20261105`
   Expected runtime about 1 to 2 minutes. Done: the JSON exists, every `raw_check.status` is `pending`.
5. **Raw check.** For every dog in `top_outliers.outliers`, compare the raw sheet (`Entire population`) with the tidy values as in section 3 step 10, and write `experiment_specs/EXP06-raw-check.json`. Rerun the same command adding `--raw-check experiment_specs/EXP06-raw-check.json`. Done: no `pending` remains and the sensitivity S4 is present if any dog is `discrepancy` or `unit_suspect`.
6. **Load.** Run `Babesiosis.Console --datasets-only` (`appsettings.json` `ReviewRoot` must point at `core/`). Check via `babesiosis-local-db` (read `docs/database.md` for the table and column names first): `dbo.cluster_assignment` for `EXP06-DS05-anomaly` has 148 rows with labels `outlier` and `typical`, and `dbo.experiment_result` has the five kinds.
7. **Verify.** Run all checks in section 5; fix and rerun.
8. **Document.** Add `experiment_anomaly.py` to `scripts/README.md`; add the experiment to `docs/database.md` if experiments are listed; update EXP06 status in `docs/ml-experiment-plan.html` if the page tracks status.
9. **Optional.** A web view under `webapp/Babesiosis.Web/src/app/modules/experiments/views/` (rank plot of both scores, outlier table with drivers), only after tasks 1 to 8 pass.

## 8. Open questions

1. Outlier threshold. Default: combined rank score at or above the 0.95 quantile (about 8 dogs); change only via `--outlier-quantile`.
2. Combined score as mean of the two rank scores. Default: yes; each method's own list is also shown.
3. If MCD is singular on 22 correlated variables. Default: drop the later variable of any pair with |r| above 0.95 and record it; the isolation forest keeps all 22.
4. Whether to keep log1p. Default: yes, same rule as EXP02; S2 shows the effect of removing it.
5. Who does the raw-sheet check. Default: the building agent does it with `read_workbook()` and records its findings in `experiment_specs/EXP06-raw-check.json`; a veterinarian should review any `discrepancy` or `unit_suspect` dog before the page is shared.
6. The exact subject codes of the three co-infected dogs beyond `BET023` and `BET072`, and the B. vogeli dog, are read from `subjects[].group_label` at run time (the tidy notes name `BET100` for B. vogeli).
