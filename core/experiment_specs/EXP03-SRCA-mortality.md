# EXP03 SRCA mortality: Mortality marker ranking in the Onderstepoort B. rossi cohorts

| Field | Value |
|---|---|
| Experiment code | `EXP03-SRCA-mortality` (umbrella code). The build writes three runs: `EXP03-SCB050-mortality` (dataset `S-CB050`), `EXP03-SCB517-mortality` (dataset `S-CB517`) and `EXP03-SRCA-mortality` (dataset `null`, transfer and cross-file comparison) |
| Layer | 1 single dataset (two per-dataset runs) plus one cross-dataset run |
| Method token | `mortality` (goes in `experiment.method` of all three runs) |
| Dataset(s) | `S-CB050` (SRC-A, article CB050) and `S-CB517` (SRC-A, article CB517). The third run has `dataset = null` because it uses both files and the S-CB050 sub-cohorts |
| Readiness | tidy files needed (`data/tidy/S-CB050.json`, `data/tidy/S-CB517.json`) |
| Python environment | Tidy scripts: `.venv` (`tidy_s_cb050.py` is stdlib only; `tidy_s_cb517.py` needs `pymupdf`, already installed in `.venv`, version 2.0). Experiment script: `.venv-nlp` (scikit-learn 1.9.1, scipy 1.17.1, numpy 1.26.4 are installed; `.venv-nlp` has no pip, nothing to install). Add `scikit-learn>=1.5` and `pymupdf>=1.24` to `scripts/requirements-experiments.txt` |
| Estimated build effort | medium (two tidy scripts with a PDF parse, one experiment script; 4 to 6 hours of agent work; run time 30 to 90 minutes) |
| Suggested model for the building agent | opus: the cohort overlap, the structural missingness and the nested-CV permutation test are easy to get subtly wrong |
| Depends on | `scripts/tidy_ds05.py` (template), `scripts/experiment_pairwise.py` (helpers and JSON layout). No other experiment. EXP07 depends on the two tidy files made here |

## 1. Question and hypotheses

Questions:

1. Which admission markers carry the most information about death in dogs with *Babesia rossi* babesiosis at Onderstepoort, ranked with interval estimates?
2. Does the ranking and the discrimination hold when a model built on the 2011-2013 dogs is applied to the 2014 dogs?

**Critical fact found while writing this spec (verified 2026-11-05).** S-CB517 is not a second cohort. All 112 S-CB517 dogs are S-CB050 dogs: S-CB517 `Case1`-`Case97` are S-CB050 cases 1-97, and S-CB517 `Control1`-`Control15` are S-CB050 cases 201-215 (Control *n* = case 200 + *n*). All 784 cytokine values (7 cytokines x 112 dogs) are identical in both files (50000.0 in S-CB517 is 50001.0 in S-CB050, Case80), and the 12 deaths are the same dogs (Case13, 21, 34, 37, 55, 58, 59, 61, 65, 81, 84, 85). S-CB050 adds cases 101-144 (cohort 2, 2014, 44 infected dogs, 3 deaths: cases 126, 127, 131) and controls 216-220. So "train on S-CB050, test on S-CB517" would test on the training dogs. This spec therefore replaces it with a temporal transfer inside S-CB050 (cohort 1 to cohort 2), and uses S-CB517 for what it adds: SAA, CRP, lymphocytes, monocytes and eosinophils for the 97 cohort-1 dogs.

Named hypotheses (from the article notes):

- **H1 (CB517).** IL-6 and MCP-1 are higher in non-survivors (published P = 0.041 and P = 0.009, Mann-Whitney, unadjusted). Expected: both rank in the top third of the cytokine-containing feature sets; univariable AUC above 0.65.
- **H2 (CB517).** CRP and SAA do not separate survivors from non-survivors. Expected: univariable AUC CI includes 0.5; they rank in the lower half.
- **H3 (CB050).** MPXI is higher in non-survivors than in controls (P = 0.011); the article reports no direct survivor versus non-survivor difference. Expected: MPXI has a univariable AUC near 0.5 to 0.65 for death and is not a top-ranked marker.
- **H4 (exploratory, no article).** Band neutrophils (left shift) carry outcome information in the full 141-dog set.

Negative finding: every model's nested-CV AUC has a whole-pipeline permutation p above 0.05, and no univariable marker has BH-adjusted p below 0.05. That would mean the files do not support any ranking beyond noise, and the interpretation must say so plainly.

## 2. Data

### 2.1 Sources

| Dataset | Raw file (read-only) | Member and table | Licence | Source |
|---|---|---|---|---|
| S-CB050 | `data/raw/S-CB050/PMC7040022_supplementaryFiles.zip` (SHA-256 `8113a933faceb155103230eaea433f6c5b34ad7aba71531282c01707df63eb85`) | `Table_1.DOCX`, the only table in `word/document.xml`: 162 rows (1 header + 161 dogs) x 17 columns | CC BY (article licence, Europe PMC) | SRC-A, CB050, cohort CH03 plus the 2014 cohort |
| S-CB517 | `data/raw/S-CB517/PMC4783066_supplementaryFiles.zip` (SHA-256 `9098a57a707b8e750d1109abdcaba3a73edd068e16565f44290751a291eba3c7`) | `pone.0150113.s001.pdf` (S1, leukocytes, 3 pages) and `pone.0150113.s002.pdf` (S2, SAA, CRP, cytokines, 3 pages); 112 dogs each | article licence (Europe PMC open access), not separately stated | SRC-A, CB517, cohort CH03 |

Also read: `data/inspection/S-CB050.json`, `data/inspection/S-CB517.json`, the records with `dataset_id` `S-CB050` and `S-CB517` in `datasets.jsonl` (fields `title`, `licence`, `species`, `design`, `independent_source`, `linked_articles`, `repository`, `accession_or_doi`, `landing_url`, `missingness`, `overlaps`), their rows in `data/manifest.jsonl` (`sha256`), and the article notes `articles/CB050_2020_neutrophil-myeloperoxidase-index-babesiosis-caused-babesia.md` and `articles/CB517_2016_excessive-pro-inflammatory-serum-cytokine-concentrations.md`.

S-CB050 header row, exactly as in the DOCX: `Case`, `Age (mos)`, `Weight (kg)`, `Gender`, `Status`, `Outcome`, `WBC (x10^9/L)`, `Neut Seg (x10^9/L)`, `Neut Band (x10^9/L)`, `IL-2 (pg/mL)`, `IL-6 (pg/mL)`, `IL-8 (pg/mL)`, `IL-10 (pg/mL)`, `IL-18 (pg/mL)`, `GM-CSF (pg/mL)`, `MCP-1 (pg/mL)`, `MPXI`. Values are strings with decimal commas (`4,83`). `Status` is `Infected` (141) or `Control` (20). `Outcome` is `Survived` (126), `Died` (15) or `Control` (20). `Gender` is `Male` (100) or `Female` (61). Blank cells: the 7 cytokines in 49 dogs (cases 101-144 and 216-220), `Weight (kg)` in 10, `Age (mos)` in 1 (case 56), `MPXI` in 1 (case 77). No other text values. Case numbers: 1-97, 101-144, 201-220.

S-CB517 headers: S1 `Case no`, `Outcome`, `WBC (x10^9/L)`, `NEUT (x10^9/L)`, `LYMPH (x10^9/L)`, `MONO (x10^9/L)`, `EOS (x10^9/L)`; S2 `Case no`, `Outcome`, `SAA (mg/L)`, `CRP (mg/L)`, `IL-2 (pg/mL)`, `IL-6 (pg/mL)`, `IL-8 (pg/mL)`, `IL-10 (pg/mL)`, `IL-18 (pg/mL)`, `GM-CSF (pg/mL)`, `MCP-1 (pg/mL)`. PyMuPDF `page.get_text()` returns one cell per line. Control rows have no `Outcome` cell (S1: 5 values after the ID; S2: 9). The header repeats on later pages and must be skipped. Decimal points.

### 2.2 Tidy files required

Both scripts follow `scripts/tidy_ds05.py`: same module docstring layout, same `add_var` and `add_obs` helpers, the same `dataset` block built from `datasets.jsonl` and `data/manifest.jsonl`, `levels` filled for categorical variables, cleaning notes in `dataset.notes`, one JSON file written with `indent=1`, and a short printed summary. File names use underscores: `scripts/tidy_s_cb050.py` writes `data/tidy/S-CB050.json`, and `scripts/tidy_s_cb517.py` writes `data/tidy/S-CB517.json`. `time_point` is `''` everywhere (one admission sample per dog).

#### 2.2.1 `scripts/tidy_s_cb050.py` -> `data/tidy/S-CB050.json`

Reading: open the zip with `zipfile`, read member `Table_1.DOCX` into `io.BytesIO`, open that as a second zip, parse `word/document.xml` with `xml.etree.ElementTree` (namespace `http://schemas.openxmlformats.org/wordprocessingml/2006/main`). Take the first `w:tbl`. For every `w:tr`, each `w:tc` cell text is the join of its `w:t` texts, stripped. Row 1 is the header. Stop with an error if the header differs from the 17 names listed in 2.1.

Subject code: `Case` + the case number (`Case1` ... `Case144`, `Case201` ... `Case220`). This makes the infected codes identical to S-CB517 codes.

Number rule: `to_num(text)` replaces `,` with `.` and returns a float; `''` gives missing (no observation written).

| Raw column | `code` | `name` | `unit` | `data_type` | `domain` | `include_default` | Notes for `description` |
|---|---|---|---|---|---|---|---|
| `Age (mos)` | `age_months` | Age | months | N | signalment | true | Missing in case 56. |
| `Weight (kg)` | `weight_kg` | Body weight | kg | N | signalment | true | Missing in 10 dogs (9 infected, 1 control). |
| `Gender` | `sex` | Sex | null | C | signalment | true | Male / Female as recorded; neuter status not given. |
| `Status` | `status` | Infection status | null | C | group | false | `Infected` / `Control`. Duplicates `group_label`. |
| `Outcome` | `outcome` | Outcome | null | C | outcome | false | `Survived` / `Died`; `Control` stored as no observation. Survival to discharge versus death or euthanasia for poor prognosis (article). Kept as a variable so associations can name it. |
| `WBC (x10^9/L)` | `wcc` | White cell count | x10^9/L | N | haematology | true | Equals the sum of segmented + band neutrophils + S-CB517 lymphocytes, monocytes, eosinophils within 0.05 for the 112 shared dogs, so it is the differential total. Differs from the S-CB517 WBC in 24 dogs (see notes). |
| `Neut Seg (x10^9/L)` | `seg_neutrophils` | Segmented neutrophils | x10^9/L | N | haematology | true | |
| `Neut Band (x10^9/L)` | `band_neutrophils` | Band neutrophils | x10^9/L | N | haematology | true | Zeros are real zeros. |
| `IL-2 (pg/mL)` | `il2` | Interleukin-2 | pg/mL | N | cytokine | true | Floor 3.4 is the assay minimum detectable concentration (left-censored). 50001.0 in case 80 is an assay ceiling (right-censored). Blank in cohort 2 (cases 101-144) and controls 216-220 by design. |
| `IL-6 (pg/mL)` | `il6` | Interleukin-6 | pg/mL | N | cytokine | true | Floor 3.6; ceiling 50001.0 (case 80); blank as for il2. |
| `IL-8 (pg/mL)` | `il8` | Interleukin-8 | pg/mL | N | cytokine | true | Blank as for il2. |
| `IL-10 (pg/mL)` | `il10` | Interleukin-10 | pg/mL | N | cytokine | true | Floor 8.4; blank as for il2. |
| `IL-18 (pg/mL)` | `il18` | Interleukin-18 | pg/mL | N | cytokine | true | Floor 5.7; ceiling 50001.0 (case 80); blank as for il2. |
| `GM-CSF (pg/mL)` | `gm_csf` | GM-CSF | pg/mL | N | cytokine | true | Floor 9.1; ceiling 50001.0 (case 80); blank as for il2. |
| `MCP-1 (pg/mL)` | `mcp1` | Monocyte chemoattractant protein-1 (CCL2) | pg/mL | N | cytokine | true | Blank as for il2. |
| `MPXI` | `mpxi` | Neutrophil myeloperoxidase index | index (ADVIA) | N | haematology | true | Unitless analyser index; missing in case 77. |

Derived variables (`derived = true`):

| `code` | `name` | `data_type` | `domain` | `include_default` | `derived_from` | Rule |
|---|---|---|---|---|---|---|
| `cohort` | Source cohort | C | group | false | null | `cohort 1 (2011-2013)` for cases 1-97 and 201-215; `cohort 2 (2014)` for cases 101-144 and 216-220. Inferred from case-number ranges and the CB050 article's 96 + 15 / 44 + 5 split; not stated in the file. |
| `cytokine_panel` | Cytokine panel measured | C | group | false | `["cohort"]` | `yes` where all 7 cytokines are present, else `no`. |

`ref_low` and `ref_high`: null for every variable (the file and the note give no laboratory reference ranges; do not copy the DS05 ranges, which are from another laboratory).

`group_label`: `B. rossi infected` when `Status` = `Infected`, `Healthy control` when `Control`. `outcome_label`: `Survived` or `Died` for infected dogs, null for controls.

Dataset block: `code` `S-CB050`, `article_code` `CB050`, `independent_source` `SRC-A`, `source_file` `data/raw/S-CB050/PMC7040022_supplementaryFiles.zip`, `source_sha256` from the manifest, `script` `scripts/tidy_s_cb050.py`; other fields copied from `datasets.jsonl` as `tidy_ds05.py` does.

Cleaning notes to record (each a separate string in `notes`):

1. "Table_1.DOCX inside PMC7040022_supplementaryFiles.zip, single table, header row 1, 161 dog rows; figure images in the zip ignored."
2. "Decimal commas converted to points; blank cells stored as missing."
3. "141 infected dogs against 140 in the article; the extra dog could not be identified, all rows kept."
4. "Case numbers 98-100 and 145-200 are absent from the file."
5. "Cytokines missing by design in cohort 2 (cases 101-144) and controls 216-220; cohort assigned from case-number ranges."
6. "Cytokine floor values (IL-2 3.4, IL-6 3.6, IL-10 8.4, IL-18 5.7, GM-CSF 9.1 pg/mL) are left-censored minimum detectable concentrations; 50001.0 in case 80 (IL-2, IL-6, IL-18, GM-CSF) is right-censored. Values kept as recorded." Add the count of floor values per cytokine computed by the script.
7. "Outcome 'Control' stored as no outcome observation; outcome includes euthanasia for poor prognosis."
8. "The 97 cohort-1 infected dogs and 15 cohort-1 controls are the same dogs as S-CB517 (Case n = Case n; Control n = Case 200+n), cytokine values identical."

Expected counts: 161 subjects, 18 variables, about 2,300 observations.

#### 2.2.2 `scripts/tidy_s_cb517.py` -> `data/tidy/S-CB517.json`

Reading: `import pymupdf` (not `fitz`, which warns). For each of the two PDF members read from the zip with `pymupdf.open(stream=..., filetype="pdf")`, concatenate `page.get_text().splitlines()` over all pages, strip, drop empty lines. The header is every line before the first line matching `^(Case|Control)\d+$`; later repeats of header lines are skipped. After each ID line, collect the value lines up to the next ID. Infected rows: S1 has 6 values (Outcome + 5 numbers), S2 has 10 (Outcome + 9 numbers). Control rows: S1 has 5 numbers, S2 has 9. Stop with an error if any row has a different count, if the two files' ID sets differ, or if an infected dog's Outcome differs between S1 and S2.

Subject code: the ID as printed (`Case1` ... `Case97`, `Control1` ... `Control15`).

| Raw column | File | `code` | `name` | `unit` | `data_type` | `domain` | `include_default` | Notes for `description` |
|---|---|---|---|---|---|---|---|---|
| `Outcome` | S1, S2 | `outcome` | Outcome | null | C | outcome | false | `Survived` / `Died`; none for controls. |
| `WBC (x10^9/L)` | S1 | `wcc` | White cell count | x10^9/L | N | haematology | true | As printed. In 24 infected dogs it is 0.3 to 11 x10^9/L higher than the S-CB050 WBC for the same dog, which equals the differential sum; possibly an uncorrected analyser count (see section 8). |
| `NEUT (x10^9/L)` | S1 | `seg_neutrophils` | Segmented neutrophils | x10^9/L | N | haematology | true | Identical to S-CB050 `Neut Seg` in all 112 dogs, so NEUT is segmented neutrophils only; bands are not in this file. |
| `LYMPH (x10^9/L)` | S1 | `lymphocytes` | Lymphocytes | x10^9/L | N | haematology | true | |
| `MONO (x10^9/L)` | S1 | `monocytes` | Monocytes | x10^9/L | N | haematology | true | |
| `EOS (x10^9/L)` | S1 | `eosinophils` | Eosinophils | x10^9/L | N | haematology | true | 0.00 in 60 of 97 infected dogs. |
| `SAA (mg/L)` | S2 | `saa` | Serum amyloid A | mg/L | N | acute_phase | true | |
| `CRP (mg/L)` | S2 | `crp` | C-reactive protein | mg/L | N | acute_phase | true | |
| `IL-2 (pg/mL)` ... `MCP-1 (pg/mL)` | S2 | `il2`, `il6`, `il8`, `il10`, `il18`, `gm_csf`, `mcp1` | as in S-CB050 | pg/mL | N | cytokine | true | Same floors as S-CB050; ceiling printed as 50000.0 (Case80), where S-CB050 has 50001.0. |

Derived variable: `s_cb050_case` (Linked S-CB050 subject, `T`, domain `link`, `include_default` false, `derived` true, `derived_from` null): `Case<n>` for `Case<n>`, `Case<200+n>` for `Control<n>`. The script verifies the link when `data/tidy/S-CB050.json` exists: for every dog, the 7 cytokines must match S-CB050 within 0.051 (treat 50000.0 = 50001.0), `seg_neutrophils` within 0.006, and outcome must agree; it records the number of matches and of WBC disagreements in the notes, and stops with an error on any cytokine, neutrophil or outcome mismatch.

`ref_low`, `ref_high`: null. `group_label`: `B. rossi infected` for `Case*`, `Healthy control` for `Control*`. `outcome_label`: `Survived` / `Died` for cases, null for controls. Dataset block: `code` `S-CB517`, `article_code` `CB517`, `independent_source` `SRC-A`, `source_file` `data/raw/S-CB517/PMC4783066_supplementaryFiles.zip`, `script` `scripts/tidy_s_cb517.py`.

Cleaning notes: (1) the two PDF members and the parse rule; (2) "S1 and S2 joined on the ID; both hold the same 112 IDs"; (3) the floor and ceiling rule as for S-CB050; (4) "NEUT equals S-CB050 segmented neutrophils in all 112 dogs"; (5) the WBC disagreement count and the S-CB050 link check result; (6) "These 112 dogs are a subset of S-CB050; not an independent cohort."

Expected counts: 112 subjects, 16 variables, about 1,670 observations.

### 2.3 Variables and filters

Analysis population for every model and the univariable screen: infected dogs with an outcome (controls excluded). Outcome: `Died` = 1, `Survived` = 0.

| Run | Feature set | Dogs | Deaths | Candidate predictors | EPV |
|---|---|---|---|---|---|
| S-CB050 | `A_full` | 141 | 15 | `age_months`, `weight_kg`, `sex` (Male = 1), `wcc`, `seg_neutrophils`, `band_neutrophils`, `mpxi` | 15 / 7 = 2.1 |
| S-CB050 | `B_cytokine` | 97 (cohort 1) | 12 | `A_full` + `il2`, `il6`, `il8`, `il10`, `il18`, `gm_csf`, `mcp1` | 12 / 14 = 0.86 |
| S-CB517 | `C_cb517` | 97 | 12 | `wcc`, `seg_neutrophils`, `lymphocytes`, `monocytes`, `eosinophils`, `saa`, `crp`, `il2`, `il6`, `il8`, `il10`, `il18`, `gm_csf`, `mcp1` | 12 / 14 = 0.86 |

Rule: candidates are the `include_default = true`, `derived = false` variables of the tidy file that fall in the set's dogs; the table is what the rule gives. EPV = deaths / number of candidate predictor columns before selection.

Missing data: in `A_full`, `age_months` (1 dog), `weight_kg` (9 infected) and `mpxi` (1) are imputed with the median of the training fold inside every fit (fitted on training rows only). Sensitivity: complete-case refit of `A_full` (`--complete-case`, reported in `model_performance` as `A_full_cc`). `B_cytokine` and `C_cb517` use the cohort-1 dogs, which have all cytokines. No imputation of cytokines in cohort 2: this is the reason `A_full` and `B_cytokine` are separate.

Transforms (applied before standardisation, the same in every run): `log10(x + c)` for `wcc`, `seg_neutrophils`, `band_neutrophils`, `lymphocytes`, `monocytes`, `eosinophils`, `saa`, `crp` and all 7 cytokines, where `c = 0` if the variable's minimum over the analysis population is above 0, else half the smallest positive value (recorded in `run_notes`). `age_months`, `weight_kg`, `mpxi` untransformed. Censored values are used as recorded (ties at the floor; the ceiling dog Case80 is kept). Standardisation (z-score) is fitted on the training fold only.

## 3. Method

All randomness flows from `--seed` (default `20261105`). Outer repeat `r` uses `seed + r`; inner splitters use `seed + 1000 + r`; permutation `b` uses `seed + 100000 + b`; bootstrap uses `numpy.random.default_rng(seed + 7)`. Set `n_jobs` but keep results independent of it (random forest `random_state` fixed per fit).

1. **Load.** Read the tidy JSON, build a subject x variable matrix for the feature set, apply the 2.3 filters and transforms, encode `sex` as 0/1.

2. **Univariable screen** (per run, family = every candidate in the union of that run's feature sets; S-CB050: 14 variables on the dogs that have them; S-CB517: 14). For each numeric variable: Mann-Whitney U, died versus survived, on all infected dogs with a value. Effect size: AUC = U / (n_died x n_survived) (probability that a dog that died has the higher value, ties count one half), with a 95% percentile interval from 2,000 bootstrap resamples stratified by outcome. p value: two-sided permutation p (5,000 label permutations, statistic |AUC - 0.5|, `perm_p` as in `experiment_pairwise.py`). `sex`: chi-square permutation test (as `experiment_pairwise.py` `chi_square`), effect size odds ratio with a Haldane 0.5 correction and bootstrap interval, AUC field null. Benjamini-Hochberg across the run (`bh_adjust` from EXP01). Also record group medians and quartiles on the raw scale.

3. **Models, nested cross-validation** (per feature set). Outer: `RepeatedStratifiedKFold(n_splits=5, n_repeats=20)`. Inner: `StratifiedKFold(n_splits=3, shuffle=True)`; tuning metric `neg_log_loss` (AUC is too unstable with 2 or 3 deaths per inner fold). Each pipeline is `SimpleImputer(strategy="median")` -> `StandardScaler` -> model, so imputation, scaling and selection happen inside the training fold.
   - **L1 logistic**: `LogisticRegression(solver="saga", l1_ratio=1.0, C in logspace(-2, 1, 13), max_iter=20000)`; if the installed sklearn still requires it, also pass `penalty="elasticnet"` (sklearn 1.8 deprecated `penalty`; check with a one-line test).
   - **Elastic net logistic**: same with `l1_ratio in {0.25, 0.5, 0.75}`.
   - **Random forest**: `RandomForestClassifier(n_estimators=300, min_samples_leaf in {3, 10}, max_features="sqrt", class_weight="balanced_subsample", random_state=fit seed)`.
   - For each outer split, store the out-of-fold predicted probability of death for every test dog, the chosen hyperparameters, the standardised coefficients (logistic) and whether each coefficient is non-zero.

4. **Discrimination.** Per repeat, AUC of the pooled out-of-fold predictions (20 values: report min, median, max). Main estimate: AUC of the repeat-averaged out-of-fold probability per dog (`p_bar`), with a 95% interval from 2,000 bootstrap resamples of dogs stratified by outcome. Brier score of `p_bar` and the null Brier (event rate x (1 - event rate)).

5. **Calibration** of `p_bar`: calibration intercept and slope from a logistic regression of the outcome on `logit(p_bar)` (numpy Newton-Raphson, no penalty, clip `p_bar` to [1e-6, 1 - 1e-6]); reliability bins = 5 quantile bins of `p_bar`, each with mean predicted, observed death rate, n, deaths. With 12 to 15 deaths these are descriptive only.

6. **Permutation test of the whole pipeline.** For `b = 1..B`, permute the outcome among the feature set's dogs, rerun step 3 with `n_repeats = 2` (same grids, same inner CV), and compute the mean per-repeat pooled-OOF AUC. The observed statistic is computed the same way (2 repeats, seeds `seed + 1`, `seed + 2`) on the true labels. p = (1 + #{null >= observed}) / (1 + B). Defaults: `B = 200` for the two logistic models, `B = 100` for the random forest (`--perm-logistic`, `--perm-rf`). Store the null mean and 95th percentile.

7. **Permutation importance and ranking.** For each outer fit, `sklearn.inspection.permutation_importance` on the outer test fold, `scoring="neg_log_loss"`, `n_repeats=20`, `random_state` = fit seed; this gives 100 importance values per variable per model. Per model: mean importance, 2.5 and 97.5 percentiles over the 100 values, and rank per fit (1 = largest drop). For the logistic models also the selection frequency (share of the 100 fits with a non-zero coefficient) and the median standardised coefficient (sign shows direction). **Consensus rank** = rank of the mean of the three per-model mean ranks; **rank interval** = 2.5 and 97.5 percentiles of the per-fit rank pooled over the three models (300 values). This is the deliverable: a ranking, not a prognostic score.

8. **Minimal two-marker model** (per feature set, to respect EPV): inside each outer fold, choose the 2 candidates with the highest univariable |AUC - 0.5| on the training fold, fit `LogisticRegression(l1_ratio=0, C=1.0)` (ridge), and score the test fold. Report its AUC like step 4 and the selection frequency of each variable. EPV for this model is reported as deaths / 2.

9. **Temporal transfer** (third run, `EXP03-SRCA-mortality`). Use S-CB050 only, features of `A_full` (the variables measured in both sub-cohorts: `age_months`, `weight_kg`, `sex`, `wcc`, `seg_neutrophils`, `band_neutrophils`, `mpxi`).
   - **T1**: train on cohort 1 infected (cases 1-97; 12 deaths) with the step-3 tuning (inner 3-fold on all training dogs, refit), plus the step-8 two-marker model; predict cohort 2 infected (cases 101-144; 3 deaths). External AUC with a 2,000-resample stratified bootstrap interval; also the rank (1 = highest risk among 44) of each of the 3 dogs that died. Internal AUC = the nested-CV AUC of the same pipeline within cohort 1 (step 4 with these features). Transfer loss = internal AUC - external AUC.
   - **T2** (cohort 2 to cohort 1): skipped because training deaths (3) are below `--min-train-events` (default 8); recorded with the reason.
   - **T3, cross-file ranking concordance**: Spearman rho between the consensus ranks of the variables common to `B_cytokine` (S-CB050) and `C_cb517` (S-CB517): `wcc`, `seg_neutrophils`, `il2`, `il6`, `il8`, `il10`, `il18`, `gm_csf`, `mcp1`. Labelled "same dogs: agreement shows sensitivity to the other covariates, not replication". No interval (9 items).
   - **Not done, and recorded in `run_notes`**: training on S-CB050 and testing on S-CB517 (or the reverse), because all 112 S-CB517 dogs are S-CB050 training dogs.

10. **Overlap check** (third run): recompute the S-CB050 / S-CB517 link (subjects matched, cytokine cells compared and identical, outcome agreement, WBC disagreements) from the two tidy files and store it in `run_notes` and in the `transfer` payload.

11. **Comparison with published findings**: the script holds a small constant table (variable, published direction, published p, article) for H1-H3: `il6` higher in died P = 0.041 (CB517); `mcp1` higher in died P = 0.009 (CB517); `crp`, `saa` no outcome difference (CB517); `mpxi` higher in died versus controls P = 0.011, no survivor/non-survivor test reported (CB050). Each univariable row and each ranked marker gets a `published` string or null, and the interpretation states whether the direction and the significance agree.

Why scikit-learn: nested tuning of penalised logistic regression and random forests with permutation importance is a large amount of numpy code to reimplement and verify; sklearn is already in `.venv-nlp`. The univariable screen, bootstrap, BH and calibration fit stay numpy-only, copied from `experiment_pairwise.py` where possible.

## 4. Outputs

### 4.1 Experiment JSON

Three files: `data/experiments/EXP03-SCB050-mortality.json`, `data/experiments/EXP03-SCB517-mortality.json`, `data/experiments/EXP03-SRCA-mortality.json`. One script invocation with `--run all` (default) writes all three; `--run scb050|scb517|transfer` writes one.

`experiment` block (per-cohort runs):

- `code`: `EXP03-SCB050-mortality` / `EXP03-SCB517-mortality`
- `name`: "Mortality marker ranking, Onderstepoort B. rossi dogs (S-CB050)" / "(S-CB517)"
- `description`: one paragraph naming the models, nested CV, permutation test and the words "ranking, not a prognostic score".
- `method`: `mortality`; `dataset`: `S-CB050` / `S-CB517`
- `parameters`: `{"seed": 20261105, "outer_folds": 5, "outer_repeats": 20, "inner_folds": 3, "tuning_metric": "neg_log_loss", "l1_C_grid": [0.01 ... 10, 13 values], "enet_l1_ratios": [0.25, 0.5, 0.75], "rf_n_estimators": 300, "rf_min_samples_leaf": [3, 10], "rf_max_features": "sqrt", "rf_class_weight": "balanced_subsample", "perm_importance_repeats": 20, "perm_importance_scoring": "neg_log_loss", "pipeline_permutations_logistic": 200, "pipeline_permutations_rf": 100, "pipeline_permutation_repeats": 2, "bootstrap": 2000, "univariable_permutations": 5000, "alpha": 0.05, "adjustment": "benjamini_hochberg", "imputation": "median, training fold", "transform": "log10(x + c), see run_notes", "feature_sets": {...}, "complete_case_sensitivity": true, "min_train_events": 8}`
- `script`: `scripts/experiment_mortality.py`; `script_version`: first 12 hex characters of the SHA-256 of the script; `run_utc`.
- `n_subjects`: infected dogs with an outcome (141 / 97); `n_variables`: candidates in the union of feature sets (14 / 14); `n_tests`: number of association rows (univariable tests).
- `summary`: e.g. "141 infected dogs, 15 deaths. Best nested-CV AUC ... (L1) ... permutation p ... Top three markers by consensus rank: ... EPV 2.1 (A_full), 0.86 (B_cytokine). A ranking, not a prognostic score."

`associations` (per-cohort runs): one row per univariable test. `variable_a` = marker code, `variable_b` = `outcome` (exists in both tidy files), `test` = `mann_whitney` or `chi_square`, `estimate` = AUC (or odds ratio for `sex`), `estimate_label` = `auc` / `odds_ratio`, `n` = dogs with a value, `p_value`, `p_adjusted` (BH over the run), `significant` = `p_adjusted < 0.05`, `trivial` = false, `direction` = `positive` when higher (or Male) in dogs that died, else `negative`, `detail` = `{"n_died", "n_survived", "median_died", "median_survived", "q1_died", "q3_died", "q1_survived", "q3_survived", "ci_low", "ci_high", "published"}`.

`cluster_assignments`: `[]` in all three runs.

`results` (per-cohort runs):

| kind | title | sort_order | payload |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | `{"sections": [...]}` |
| `marker_ranking` | Marker ranking for death (consensus of three models) - `<feature set>` | 1, 2 (one per feature set) | see below |
| `model_performance` | Nested cross-validated discrimination and permutation test | 3 | see below |
| `calibration` | Calibration of out-of-fold predictions | 4 | see below |
| `univariable_screen` | Univariable screen, died versus survived (BH-adjusted) | 5 | see below |
| `run_notes` | Dogs, variables, transforms and choices | 6 | see below |

`marker_ranking` payload:

```json
{"feature_set": "A_full", "n": 141, "events": 15, "n_candidates": 7, "epv": 2.14,
 "wording": "ranking of markers by information about death; not a prognostic score",
 "markers": [
  {"code": "band_neutrophils", "name": "Band neutrophils", "consensus_rank": 1, "mean_rank": 1.9, "rank_interval": [1, 4],
   "univariable_auc": 0.68, "published": null,
   "models": {"l1": {"importance_mean": 0.031, "importance_interval": [-0.004, 0.09], "selection_freq": 0.86, "median_coef": 0.55},
              "enet": {"importance_mean": 0.028, "importance_interval": [-0.003, 0.08], "selection_freq": 0.93, "median_coef": 0.41},
              "rf": {"importance_mean": 0.012, "importance_interval": [-0.01, 0.05], "selection_freq": null, "median_coef": null}},
   "two_marker_selection_freq": 0.64}
 ]}
```

`model_performance` payload:

```json
{"feature_sets": [
  {"feature_set": "A_full", "n": 141, "events": 15, "epv": 2.14,
   "models": [
    {"model": "l1", "auc": 0.70, "auc_interval": [0.55, 0.83], "auc_repeats": {"min": 0.62, "median": 0.69, "max": 0.74},
     "brier": 0.088, "brier_null": 0.095, "perm_p": 0.04, "n_permutations": 200, "null_auc_mean": 0.50, "null_auc_q95": 0.63,
     "hyperparameters_chosen": {"C=0.1": 41, "C=0.316": 33}}
   ]}
 ]}
```

The `models` list covers `l1`, `enet`, `rf` and `two_marker`; `A_full_cc` appears as an extra feature set when the complete-case sensitivity runs.

`calibration` payload: `{"feature_sets": [{"feature_set": "A_full", "models": [{"model": "l1", "intercept": -0.1, "slope": 0.7, "bins": [{"mean_pred": 0.03, "observed": 0.0, "n": 28, "events": 0}]}]}]}`.

`univariable_screen` payload: `{"comparison": "died vs survived, infected dogs only", "family_size": 14, "rows": [{"variable": "il6", "name": "Interleukin-6", "n_died": 12, "n_survived": 85, "median_died": 643.9, "median_survived": 84.1, "auc": 0.69, "auc_interval": [0.52, 0.84], "p_value": 0.03, "p_adjusted": 0.2, "published": "higher in non-survivors, P = 0.041 (CB517)", "agrees_with_published": true}]}` (rows sorted by p).

`run_notes` payload: `{"population": {"infected_with_outcome": 141, "excluded_controls": 20}, "feature_sets": {"A_full": [...codes], ...}, "transforms": {"il2": {"log10": true, "c": 0}, "band_neutrophils": {"log10": true, "c": 0.005}}, "imputed": {"weight_kg": 9, "age_months": 1, "mpxi": 1}, "censoring": {"il2_floor_3.4": 27, "ceiling_case": "Case80"}, "sklearn_version": "1.9.1", "runtime_seconds": 0, "warnings": []}`.

Third run, `EXP03-SRCA-mortality`: `dataset` null, so `associations` and `cluster_assignments` are `[]`. `n_subjects` = 141 (S-CB050 infected dogs used), `n_variables` = 7, `n_tests` = number of transfer evaluations (models x analyses). `parameters` as above plus `{"transfer_features": [...], "train_subcohort": "cases 1-97", "test_subcohort": "cases 101-144"}`.

| kind | title | sort_order | payload |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | sections |
| `transfer` | Temporal transfer within SRC-A and cross-file concordance | 1 | see below |
| `run_notes` | Overlap check and analyses not done | 2 | `{"overlap": {...}, "not_done": [{"analysis": "train S-CB050, test S-CB517", "reason": "all 112 S-CB517 dogs are S-CB050 dogs"}], "skipped": [{"id": "T2", "reason": "3 training deaths < 8"}]}` |

`transfer` payload:

```json
{"overlap": {"s_cb517_subjects": 112, "matched_in_s_cb050": 112, "cytokine_cells_compared": 784, "cytokine_cells_identical": 784,
             "outcome_agree": 97, "wcc_disagree": 24},
 "analyses": [
  {"id": "T1", "train": "S-CB050 cohort 1 (cases 1-97, 2011-2013)", "test": "S-CB050 cohort 2 (cases 101-144, 2014)",
   "features": ["age_months", "weight_kg", "sex", "wcc", "seg_neutrophils", "band_neutrophils", "mpxi"],
   "n_train": 97, "events_train": 12, "n_test": 44, "events_test": 3, "epv_train": 1.71,
   "models": [{"model": "l1", "internal_auc": 0.68, "internal_auc_interval": [0.5, 0.83], "external_auc": 0.6,
               "external_auc_interval": [0.3, 0.9], "transfer_loss": 0.08, "test_death_ranks": [3, 11, 30]}]},
  {"id": "T2", "status": "skipped", "reason": "3 training deaths, below min_train_events = 8"}],
 "ranking_concordance": {"variables": ["wcc", "seg_neutrophils", "il2", "il6", "il8", "il10", "il18", "gm_csf", "mcp1"],
                         "spearman_rho": 0.7, "note": "same dogs: shows sensitivity to the other covariates, not replication"}}
```

Interpretation sections (all three runs, by heading): "The question"; "What was done"; "What the data show" (top markers with consensus rank, interval, univariable AUC and BH p; AUC with interval and permutation p; EPV next to every model); "Comparison with the published articles" (H1-H3); "How far this goes" (limits from section 6). The third run uses "The question", "Why S-CB517 is not a validation cohort", "Temporal transfer", "How far this goes".

### 4.2 Other artefacts

None. The tidy files go to `data/tidy/`, results to `data/experiments/`. No figures or CSVs.

## 5. Acceptance checks

1. **Tidy counts.** S-CB050: 161 subjects (141 `B. rossi infected`, 20 `Healthy control`), outcome labels 126 Survived / 15 Died; 18 variables; `il6` observations = 112. S-CB517: 112 subjects, 85 Survived / 12 Died; 16 variables; link check: 112 matched, 784 cytokine cells identical, 24 WBC disagreements.
2. **Spot values.** S-CB050 Case1: `wcc` 4.83, `band_neutrophils` 0.43, `il10` 532.2, `mpxi` 32.3, `weight_kg` missing. S-CB517 Case1: `saa` 1050.8, `crp` 90.9, `lymphocytes` 0.72.
3. **Published medians.** In S-CB517 infected dogs, the median `il6` is 643.9 in dogs that died and 84.1 in survivors; `il8` median 1066.3 in infected dogs and 3316.7 in controls; `mcp1` 544.2 versus 211.7 (from the dataset record and the CB517 note).
4. **Published tests.** The univariable permutation p for `il6` and `mcp1` (S-CB517 run) are within a factor of 2 of 0.041 and 0.009; same direction (higher in died). `crp` and `saa` have AUC intervals that include 0.5. If not, check the outcome coding first.
5. **Same dogs, same answers.** In the S-CB050 `B_cytokine` univariable rows and the S-CB517 rows, the cytokine and `seg_neutrophils` AUCs are identical to 3 decimals (same dogs, same values); `wcc` may differ.
6. **Null behaves.** Run `--run scb050 --shuffle-outcome --seed 1` (a debug flag that permutes the outcome once before everything): the univariable screen has no BH-significant row in at least 19 of 20 seeds tried with `--quick` (`--quick` = 3 outer repeats, 20 pipeline permutations, 500 univariable permutations), and the nested-CV AUCs fall between 0.35 and 0.65.
7. **Reproducibility.** Two runs with the same seed give byte-identical `results` and `associations` (ignore `run_utc`, `runtime_seconds`).
8. **Loader.** `Babesiosis.Console --datasets-only` loads S-CB050, S-CB517 and the three experiments without errors; SQL checks in section 7.
9. **Wording.** grep the three JSON files for "prognostic score", "predict" and "subtype": the only allowed hits are the sentence "a ranking, not a prognostic score" and model names. EPV appears next to every AUC in the interpretation.

## 6. Caveats and reporting language

- **Events.** 15 deaths in 141 dogs (12 in the 97 dogs with cytokines). EPV is 2.1 for the 7-variable set and 0.86 for the 14-variable sets, far below the 10 to 20 usually needed. Rankings are unstable and the interval on every rank must be shown. The deliverable is a ranking of markers, never a prognostic score or a clinical decision tool.
- **Not two cohorts.** S-CB517 is 112 of the S-CB050 dogs with the same cytokine values; agreement between the two runs is not replication. Both files are SRC-A (one hospital, one research group), so nothing here is independent of the wider Onderstepoort literature (CH03 holds six articles).
- **Temporal transfer has 3 test deaths.** The cohort 2 AUC interval will be very wide; report it as a sense check, not validation.
- **Outcome definition.** Death includes euthanasia for poor prognosis, so it partly reflects clinician and owner decisions.
- **Censoring.** Many cytokine values sit at the assay floor (IL-2 3.4 in about 30 dogs, GM-CSF 9.1 in about 28) and one dog sits at the ceiling; rank-based statistics and trees tolerate this, linear models less so.
- **Missing covariates.** No haematocrit, platelets, lactate, parasitaemia, days sick or treatment in either file; S-CB517 has no age, sex or weight. Markers absent from the files cannot be ranked, and confounding by days sick (which CB517 links to IL-2, IL-6, IL-18 and GM-CSF) cannot be adjusted.
- **Unexplained WBC difference** between the two files in 24 dogs.
- Wording: "carries information about death", "ranks higher"; never "predicts death", "prognostic model" or "risk score".

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md`, this spec, `scripts/tidy_ds05.py`, `scripts/experiment_pairwise.py`, the two article notes, `data/inspection/S-CB050.json`, `data/inspection/S-CB517.json`, the two `datasets.jsonl` records. Done when you can state the S-CB050/S-CB517 overlap in one sentence.
2. **Tidy S-CB050.** Write `scripts/tidy_s_cb050.py`; run `.venv/Scripts/python.exe -I scripts/tidy_s_cb050.py` from `core/`. Done when acceptance checks 1-2 pass for S-CB050.
3. **Tidy S-CB517.** Write `scripts/tidy_s_cb517.py` (imports `pymupdf`); run `.venv/Scripts/python.exe -I scripts/tidy_s_cb517.py`. Done when the link check prints 112 matched, 784 identical, 24 WBC disagreements, and acceptance checks 1-3 pass.
4. **Script.** Write `scripts/experiment_mortality.py` with a docstring giving inputs, outputs, dependencies (numpy, scikit-learn, `.venv-nlp`) and the command:
   `.venv-nlp/Scripts/python.exe -I scripts/experiment_mortality.py --run all [--seed 20261105] [--outer-repeats 20] [--perm-logistic 200] [--perm-rf 100] [--bootstrap 2000] [--complete-case] [--quick] [--shuffle-outcome]`.
   Add `scikit-learn>=1.5` and `pymupdf>=1.24` to `scripts/requirements-experiments.txt`. Run `--quick` first (about 2 minutes).
5. **Run.** `.venv-nlp/Scripts/python.exe -I scripts/experiment_mortality.py --run all`. Expected 30 to 90 minutes (the random-forest permutation test dominates); print progress per feature set.
6. **Load.** From `console/Babesiosis.Console`: `dotnet run -- --datasets-only`. SQL checks: `SELECT dataset_code, n_subjects FROM dbo.dataset WHERE dataset_code IN ('S-CB050','S-CB517')` gives 161 and 112; `SELECT experiment_code, n_tests FROM dbo.experiment WHERE experiment_code LIKE 'EXP03-%'` gives three rows; `SELECT COUNT(*) FROM dbo.association a JOIN dbo.experiment e ON e.experiment_id = a.experiment_id WHERE e.experiment_code = 'EXP03-SCB050-mortality'` equals `n_tests`; `dbo.experiment_result` has 7, 6 and 3 rows for the three runs (or 8 for S-CB050 if `A_full_cc` gets its own ranking; it does not by default).
7. **Verify.** Acceptance checks 1-9; open `/experiments/EXP03-SCB050-mortality` in the web app and read the interpretation as a veterinary reader would.
8. **Document.** Add rows for the two tidy scripts and the experiment script to `scripts/README.md`; add the three experiment codes to `docs/database.md` where experiments are listed; set EXP03 to done in `docs/ml-experiment-plan.html` and correct its data row to say that S-CB517 is a subset of S-CB050; update the `overlaps` field text only if the owner agrees (it is a curated record; see section 8).
9. **Optional.** A web view for method `mortality` (ranked-marker forest plot with rank intervals, AUC table) in `webapp/Babesiosis.Web/src/app/modules/experiments/views/`, only after everything above passes.

## 8. Open questions

1. **Cross-cohort transfer as requested is not possible.** The plan asked to train on one file and test on the other; the files share all 112 S-CB517 dogs. Default: temporal transfer cohort 1 to cohort 2 inside S-CB050 (T1) plus ranking concordance (T3), as specified. An external test needs a non-Onderstepoort cohort with survival and the same markers (none verified in `datasets.jsonl`).
2. **WBC in S-CB517.** In 24 infected dogs S-CB517 WBC is higher than S-CB050 WBC (for example Case35 16.10 against 9.04), while S-CB050 WBC equals the differential sum. Possibly the S-CB517 value is uncorrected for nucleated red cells. Default: keep each file's own value in its tidy file and run; note it; use S-CB050 WBC wherever the two are combined (EXP07).
3. **Cohort assignment by case number** (1-97 and 201-215 = cohort 1; 101-144 and 216-220 = cohort 2) is inferred, not stated. Default: use it; the S-CB517 match confirms the cohort-1 block.
4. **The 141st infected dog.** Not identifiable. Default: keep all rows.
5. **Censored cytokines.** Default: values as recorded, rank-based screen. A sensitivity with at-floor indicator variables was not specified, to keep the number of candidates down.
6. **Should `datasets.jsonl` be corrected** (S-CB517 `overlaps` says the match is unverified)? Default: do not edit curated records in this build; report the verified overlap in the run notes and to the owner.
