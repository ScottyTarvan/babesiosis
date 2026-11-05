# EXP07 POOL mixed: Harmonised pooled haematology across six datasets

| Field | Value |
|---|---|
| Experiment code | `EXP07-POOL-haematology` |
| Layer | 2 pooled |
| Method token | `mixed` (goes in `experiment.method`) |
| Dataset(s) | `POOL01` (new pooled tidy dataset) built from `DS05`, `S-CB050`, `S-CB517`, `S-CB017`, `DS03`, `S-CB013`. `experiment.dataset` = `POOL01`, so associations can be stored |
| Readiness | harmonisation needed |
| Python environment | `.venv` (numpy 2.5.4) for `tidy_pool01.py` and `experiment_mixed.py`; numpy only, nothing to install. `statsmodels` is not installed anywhere; it is not needed for the default run (see step 4) |
| Estimated build effort | medium to large (one harmonisation script with unit checks, a numpy REML implementation with a simulation test; 5 to 8 hours, more if the upstream tidy files are missing) |
| Suggested model for the building agent | opus: unit harmonisation across five laboratories, animal overlap and a hand-written REML are easy to get wrong without noticing |
| Depends on | Tidy files `data/tidy/DS05.json` (exists), `S-CB050.json` and `S-CB517.json` (EXP03 spec), `S-CB017.json` and `DS03.json` (EXP05 spec), `S-CB013.json` (EXP09 spec). Experiment `EXP01-DS05-pairwise` (exists, `data/experiments/EXP01-DS05-pairwise.json`) |

## 1. Question and hypotheses

Questions:

1. Do the main haematological relationships found in DS05 by EXP01 hold in the other cohorts once units are harmonised and cohort differences are absorbed by a random intercept, and do they differ by *Babesia* species?
2. Does a minimal two-variable severity signal learned in one cohort with an outcome transfer to another, and how much discrimination is lost?

**Facts established while writing this spec (2026-11-05), which change the plan card.** The plan card says haematocrit, platelets, white cell count, band neutrophils and albumin appear in all six datasets. They do not:

| Canonical variable | DS05 | S-CB050 | S-CB517 | S-CB017 | DS03 | S-CB013 |
|---|---|---|---|---|---|---|
| haematocrit | yes | no | no | yes (`HMT`, %) | yes (`HCT (L/L)`) | yes (`PCV value`) |
| haemoglobin | yes | no | no | no | yes (`HGB (g/L)`) | no |
| rcc | yes | no | no | yes (`Eryt`) | no | no |
| mchc | yes (g/dL) | no | no | no | yes (`MCHC (g/L)`) | no |
| platelets | yes | no | no | yes (`Thromb`) | no | yes (`PLT count`) |
| wcc | yes | yes | yes (different definition, see 2.2) | yes (`Leuko`) | no | no |
| seg_neutrophils | yes | yes | yes (`NEUT`) | yes (`Seg. Neut`) | no | no |
| band_neutrophils | yes | yes | no | yes (`Neseg. Neut`) | no | no |
| lymphocytes, monocytes, eosinophils | yes | no | yes | yes | no | no |
| reticulocyte_pct, arc | yes | no | no | no | yes | no |
| albumin, total_protein | yes | no | no | no (reference ranges only) | no | no |
| age_months, weight_kg | yes | yes | no | no | yes | age coded, not used |
| sex | yes | yes | no | no | yes | yes (coded 1/2, see 8) |

And **S-CB517 is not a separate cohort**: its 112 dogs are S-CB050 cases 1-97 and 201-215 with identical cytokine and neutrophil values (verified in the EXP03 spec). In POOL01 they are one set of subjects. Albumin and total protein exist only in DS05; they stay in POOL01 for completeness but cannot enter any pooled model.

Named hypotheses:

- **H1.** The anaemia-inflammation axis in DS05 (haematocrit negatively related to white cell count, rho = -0.46, and to monocytes, rho = -0.45, EXP01) holds in *B. canis* (S-CB017) with the same sign. Motivation: EXP01; inflammation-associated anaemia is reported across *Babesia* species in the review.
- **H2.** The left-shift block (segmented with band neutrophils rho = 0.58, segmented with monocytes 0.54, bands with monocytes 0.50 in DS05) holds in S-CB050 and S-CB017.
- **H3.** The regenerative block (haematocrit and haemoglobin negatively related to reticulocyte %, rho about -0.53 and -0.58) holds in DS03, the other *B. rossi* cohort with reticulocyte data (article CB115).
- **H4.** A two-variable score from the shared leukocyte variables trained on death in S-CB050 discriminates complicated from uncomplicated *B. canis* in S-CB017 worse than it does internally (transfer loss above 0.1 AUC).

Negative finding: pooled slopes with BH-adjusted p above 0.05, or cohort-specific slopes of opposite sign with I-squared above 75%, mean the DS05 relationship does not generalise. A transfer AUC whose interval includes 0.5 means the severity signal does not travel.

## 2. Data

### 2.1 Sources

| Dataset | Tidy file | Raw file (read-only) | Species, setting | Licence | Source letter |
|---|---|---|---|---|---|
| DS05 | `data/tidy/DS05.json` (exists) | `data/raw/DS05/BET Study Dataset.xlsx` | *B. rossi* (149) and *B. vogeli* (1), Mdantsane, Eastern Cape, South Africa, 2021 | CC BY 4.0 | SRC-F |
| S-CB050 | `data/tidy/S-CB050.json` (EXP03) | `data/raw/S-CB050/PMC7040022_supplementaryFiles.zip`, `Table_1.DOCX` | *B. rossi*, Onderstepoort, 2011-2014 | CC BY | SRC-A |
| S-CB517 | `data/tidy/S-CB517.json` (EXP03) | `data/raw/S-CB517/PMC4783066_supplementaryFiles.zip`, `pone.0150113.s001.pdf` | same dogs as S-CB050 cohort 1 | article licence | SRC-A |
| S-CB017 | `data/tidy/S-CB017.json` (EXP05) | `data/raw/S-CB017/PMC5756041_supplementaryFiles.zip`, `pone.0190474.s001.xlsx`, sheet `HEMATOLOGY` (header row 2, `Sample ID`, `Leuko `, `Lymph`, `Neseg. Neut`, `Seg. Neut`, `Mono`, `Eos`, `Thromb `, `HMT `, `Eryt `, ...; text rows `Diseased` / `day 1` at row 19 and `day 7` at row 51) | *B. canis*, Zagreb, Croatia | CC BY | SRC-D |
| DS03 | `data/tidy/DS03.json` (EXP05) | `data/raw/DS03/Babesia Retics_Natural inf and cont_dissertation.xlsx`, `Sheet1` (header row 1: `No`, `Study no`, `Age (months)`, `Weight (kg)`, `Gender`, `HGB (g/L)`, `HCT (L/L)`, `MCHC (g/L)`, `CHCM (g/L)`, `Ret% (%)`, `ARC (x10^9/L)`, `MCVr (fL)`, `CHCMr (g/L)`, `CHr (pg/cell)`, `CHDWr (pg/cell)`, `RDWr (%)`, `CHDelta (pg)`; section rows `Study cohort 1: Naturally infected Babesia dogs` (row 2, 85 `BC` dogs), `Study cohort 2: Naturally infected Babesia dogs` (row 88, 18 `BLSC` dogs), `Control dogs` (row 107, 14 `CON` dogs)) | *B. rossi*, University of Pretoria | CC BY 4.0 | SRC-E |
| S-CB013 | `data/tidy/S-CB013.json` (EXP09) | `data/raw/S-CB013/PMC5558717_supplementaryFiles.zip`, `12917_2017_1169_MOESM4_ESM.xlsx`, sheet `All data` (`Sample No`, `PLT count`, `PCV value`, `Babesia CT`, `Babesia vogeli alone`, `Gender`, ...) | *B. vogeli* PCR-positive in 7 of 96 community dogs, Australia | CC BY | SRC-L |

Also read: `data/inspection/<id>.json` for the six datasets, their `datasets.jsonl` records (`species`, `design`, `features`, `missingness`, `overlaps`), the variable list of `data/tidy/DS05.json` (codes, units, reference ranges), and `data/experiments/EXP01-DS05-pairwise.json` (`associations` rows with `significant` true and `trivial` false).

### 2.2 Tidy file required: POOL01

`scripts/tidy_pool01.py` writes `data/tidy/POOL01.json`. It follows the layout of `scripts/tidy_ds05.py` (same `add_var`, `add_obs`, notes, `levels`, printed summary), but reads tidy JSON files, not raw files.

**Inputs that must exist first** (the script stops with a clear message naming the missing file and the spec that creates it): `data/tidy/DS05.json`; `data/tidy/S-CB050.json` and `data/tidy/S-CB517.json` (`EXP03-SRCA-mortality.md`, scripts `tidy_s_cb050.py`, `tidy_s_cb517.py`); `data/tidy/S-CB017.json` and `data/tidy/DS03.json` (`EXP05-LONG-trajectories.md`); `data/tidy/S-CB013.json` (`EXP09-COINF-rules.md`). Flag `--allow-missing` builds POOL01 from the files present and lists the absent ones in the notes (for development only; the experiment run requires all six).

**Variable lookup.** Each source variable is found first by the expected tidy `code` in the table below, then by `source_name` (the raw header, compared after stripping and lower-casing). If neither matches, stop with an error that lists the source file's codes. Record the matched source code in the variable `description`.

**Subjects included.**

| Source | Subjects in POOL01 | Time point taken | Excluded |
|---|---|---|---|
| DS05 | all 150 | `''` | none |
| S-CB050 | all 161 | `''` | none |
| S-CB517 | no subjects of its own; its `lymphocytes`, `monocytes`, `eosinophils` are attached to the linked S-CB050 subject (`s_cb050_case`, or Case*n* -> `Case`*n*, Control*n* -> `Case`(200+*n*)) | `''` | its `wcc` and `seg_neutrophils` (S-CB050 values used), SAA, CRP, cytokines |
| S-CB017 | the 47 dogs at their first sample: infected dogs at day 1 (`D01` if the tidy file uses that label, else the earliest time point), healthy dogs at their single sample | first | day-7 samples (30 dogs), noted |
| DS03 | the 117 single-visit dogs with `group_label` `natural cohort 1` (85 `BC`), `natural cohort 2` (18 `BLSC`) or `control` (14 `CON`) | `''` | 16 `IMHA` dogs (different disease) and the 5 experimental dogs (`experimental low dose` / `experimental high dose`, EXP1-EXP5): these are the SRC-B beagles (DS02 dogs 2-6, verified by the EXP05 spec writer by matching haemoglobin), so they must never enter an independent pool |
| S-CB013 | all 96 | `''` | none |

Expected total: 150 + 161 + 47 + 117 + 96 = 571 subjects.

**Subject code**: `<source dataset code>:<source subject code>`, for example `DS05:BET001`, `S-CB050:Case12`, `S-CB017:BK3`, `DS03:BC02`, `S-CB013:DOG 1` (kept verbatim; at most 60 characters).

**group_label**: `<source> | <species> | <status>`, where species is `B. rossi`, `B. canis`, `B. vogeli` or `none detected`, and status is `infected`, `healthy control` or `community dog`. Rules: DS05 `B. vogeli only` -> `B. vogeli`, other DS05 groups -> `B. rossi`, all `infected`; S-CB050 `B. rossi infected` -> `B. rossi | infected`, `Healthy control` -> `none detected | healthy control`; S-CB017 `B. canis infected` -> `B. canis | infected`, `healthy` -> `none detected | healthy control`; DS03 `natural cohort 1`, `natural cohort 2` -> `B. rossi | infected`, `control` -> `none detected | healthy control`; S-CB013 `Babesia vogeli alone` = 1 or a non-blank `Babesia CT` -> `B. vogeli | community dog`, else `none detected | community dog`.

**outcome_label**: S-CB050 `Survived` / `Died` (infected only); S-CB017 `complicated` (ID prefix `BK`) / `uncomplicated` (prefix `B` not `BK`), taken from the source `outcome_label` when it holds these words; null for all others. The unlabelled `Dead` column of S-CB017 is not used (it contradicts the article's single death).

**Canonical variables** (POOL01 `code`, unit after conversion, `data_type` N unless stated). Conversions are applied by the script and written into each variable `description` as "source: code, unit, conversion".

| `code` | name | unit | Sources and conversion | `include_default` |
|---|---|---|---|---|
| `haematocrit` | Haematocrit / PCV | L/L | DS05 `haematocrit` L/L x1; S-CB017 `haematocrit` x1 (the EXP05 tidy script already stores raw `HMT ` % / 100 as L/L; check the variable `unit` is `L/L`, else divide by 100); DS03 `haematocrit` (`HCT (L/L)`) x1; S-CB013 `PCV value` L/L x1 (centrifuged PCV, not analyser HCT: method note) | true |
| `haemoglobin` | Haemoglobin | g/L | DS05 g/L x1; DS03 `HGB (g/L)` x1 | true |
| `rcc` | Red cell count | x10^12/L | DS05 x1; S-CB017 `Eryt ` x1 (BK9 day-1 value 35 is already missing in the S-CB017 tidy file); values above 15 set missing as a guard | true |
| `mchc` | Mean cell haemoglobin concentration | g/L | DS05 g/dL **x10**; DS03 `MCHC (g/L)` x1; values above 450 g/L set missing (DS03 artefacts) | true |
| `platelets` | Platelet count | x10^9/L | DS05 x1; S-CB017 `Thromb ` x1; S-CB013 `PLT count` x1 (unit presumed, see 8) | true |
| `wcc` | White cell count | x10^9/L | DS05 x1; S-CB050 x1 (differential total); S-CB017 `Leuko ` x1 | true |
| `seg_neutrophils` | Segmented neutrophils | x10^9/L | DS05, S-CB050, S-CB017 `Seg. Neut` x1 | true |
| `band_neutrophils` | Band neutrophils | x10^9/L | DS05, S-CB050, S-CB017 `Neseg. Neut` x1 | true |
| `lymphocytes` | Lymphocytes | x10^9/L | DS05; S-CB517 via link; S-CB017 `Lymph` x1 | true |
| `monocytes` | Monocytes | x10^9/L | as lymphocytes (`Mono`) | true |
| `eosinophils` | Eosinophils | x10^9/L | as lymphocytes (`Eos`) | true |
| `reticulocyte_pct` | Reticulocytes | % | DS05 x1; DS03 `Ret% (%)` x1 | true |
| `arc` | Absolute reticulocyte count | x10^9/L | DS05 x1; DS03 `ARC (x10^9/L)` x1 | true |
| `albumin` | Albumin | g/L | DS05 only | false (single source) |
| `total_protein` | Total serum protein | g/L | DS05 only | false (single source) |
| `age_months` | Age | months | DS05, S-CB050, DS03 x1 (S-CB013 `Age` is coded 0.5/1.6/3/8.35 and not used) | true |
| `weight_kg` | Body weight | kg | DS05, S-CB050, DS03 x1 | true |
| `sex` | Sex (C) | null | DS05 `sex`, S-CB050 `sex`, DS03 `sex` (`Gender`); S-CB013 not used (1/2 coding undocumented) | true |
| `source_dataset` | Source dataset (C) | null | the source code | false |
| `source_subcohort` | Sub-cohort (C) | null | S-CB050 `cohort`; DS03 `cohort 1` / `cohort 2` / `control`; S-CB013 `Ti Tree` / `Moree` if the S-CB013 tidy file carries the site, else null; others = source code | false |
| `independent_source` | Independent source letter (C) | null | SRC-F, SRC-A, SRC-D, SRC-E, SRC-L | false |
| `species` | Babesia species (C) | null | from the group rule | false |
| `infection_status` | Infection status (C) | null | `infected` / `healthy control` / `community dog` | false |
| `outcome_death` | Died (C) | null | S-CB050 infected: `Died` / `Survived` | false |
| `outcome_complicated` | Complicated babesiosis (C) | null | S-CB017 infected: `complicated` / `uncomplicated` | false |

Not pooled and recorded as such in the notes: DS05 `rdw` (DS03 `RDWr` is reticulocyte RDW, a different measurement), DS03 reticulocyte indices (`CHr`, `MCVr`, ...), S-CB050 `mpxi` and cytokines, S-CB517 SAA, CRP, S-CB017 percentages and `n:l`.

`ref_low` / `ref_high`: null for every POOL01 variable (each laboratory has its own ranges). The description lists the source range where the source tidy file gives one (DS05 for most).

**Unit sanity check (the script stops if it fails).** After conversion, the median per source must fall in: haematocrit 0.05-0.70, haemoglobin 20-200, rcc 0.5-10, mchc 250-400, platelets 5-600, wcc 1-60, seg_neutrophils 0.5-50, band_neutrophils 0-10, lymphocytes 0.1-10, monocytes 0-5, eosinophils 0-3, reticulocyte_pct 0-30, arc 0-800, age_months 1-200, weight_kg 1-80. Print the per-source medians.

**Dataset block**: `code` `POOL01`; `title` "Harmonised admission haematology pooled from DS05, S-CB050 (+ S-CB517), S-CB017, DS03 and S-CB013"; `article_code` null; `repository` "derived (tidy_pool01.py)"; `source_record` null; `licence` "CC BY (all inputs CC BY or article licence; attribution to each source article)"; `independent_source` **`POOL`** (the database column is `VARCHAR(10)` and the loader reads a string, so the README's list form cannot be loaded; the letter list `SRC-A, SRC-D, SRC-E, SRC-F, SRC-L` goes in `notes` and in the `independent_source` variable); `species` "Dog; B. rossi, B. canis, B. vogeli and uninfected controls"; `design` "Cross-sectional admission samples pooled across five independent sources"; `source_file` the semicolon-joined input tidy paths; `source_sha256` null (input file hashes listed in notes); `n_subjects` 571; `script` `scripts/tidy_pool01.py`.

**Cleaning notes** (one string each): inputs and their SHA-256; subjects per source and exclusions (S-CB017 day 7, DS03 IMHA and experimental); "S-CB517 merged into S-CB050 subjects; 112 linked"; every unit conversion; every implausible value set missing (with subject code); the variables not pooled and why; "S-CB050 WBC used; S-CB517 WBC differs in 24 dogs"; "source letters SRC-A, SRC-D, SRC-E, SRC-F, SRC-L; DS03 and S-CB050 are both University of Pretoria B. rossi studies and may share dogs (not verifiable)".

### 2.3 Variables and filters

- **Pairs re-tested** (rule, computed by the script): every EXP01 association with `significant` true and `trivial` false whose two variables are both POOL01 canonical numeric variables and are measured together in at least 2 sources with at least 15 analysed dogs each; ordered by |EXP01 estimate|, keep the top `--max-pairs` (default 20). With the coverage above, the expected candidates include `haemoglobin`-`haematocrit` (DS05, DS03; kept as a positive control), `seg_neutrophils`-`band_neutrophils` (DS05, S-CB050, S-CB017), `seg_neutrophils`-`monocytes`, `band_neutrophils`-`monocytes`, `seg_neutrophils`-`lymphocytes`, `lymphocytes`-`monocytes`, `band_neutrophils`-`lymphocytes` (DS05, S-CB050 cohort 1, S-CB017), `haematocrit`-`wcc`, `haematocrit`-`monocytes`, `haematocrit`-`lymphocytes`, `rcc`-`wcc` (DS05, S-CB017), `haematocrit`-`reticulocyte_pct`, `haemoglobin`-`reticulocyte_pct`, `mchc`-`reticulocyte_pct`, `mchc`-`arc` (DS05, DS03), `wcc`-`platelets` (DS05, S-CB017), `age_months`-`weight_kg` (DS05, S-CB050, DS03). Pairs with albumin, total protein, rdw, mcv or globulin drop out by the rule; list them in `run_notes`.
- **Population (default)**: infected dogs only (`infection_status` = `infected`), because EXP01 was run on infected dogs. Species strata with fewer than 5 dogs in a source are dropped from the models (the single DS05 *B. vogeli* dog; S-CB013's 7 PCR-positive community dogs are below `--min-cohort-n` 15 and drop out). Sensitivity (`--include-controls`): all dogs, with `infection_status` as an extra fixed effect.
- **Missing data**: complete cases per pair; no imputation.
- **Transforms**: `log10(x + c)` for `wcc`, `seg_neutrophils`, `band_neutrophils`, `lymphocytes`, `monocytes`, `eosinophils`, `platelets`, `reticulocyte_pct`, `arc` (c = 0 if the variable minimum in the analysed rows is above 0, else half the smallest positive value; recorded). Others untransformed.
- **Scaling**: each transformed variable is divided by its pooled within-source SD (square root of the dof-weighted mean of within-source variances, over the analysed rows of that pair), after subtracting the grand mean. Slopes are then in within-cohort SD units and comparable to a correlation.

## 3. Method

Seed: `--seed` default `20261105`; `numpy.random.default_rng(seed)` for permutations, `default_rng(seed + 1)` for bootstrap, `default_rng(seed + 2)` for the transfer CV.

1. **Pooled descriptives.** For every canonical numeric variable and every source x species x infection status cell with at least 3 dogs: n, median, quartiles, min, max, on the converted scale, with the unit and the conversion text. No tests.

2. **Linear mixed model, random intercept (main model).** For each pair (x = EXP01 `variable_a`, y = `variable_b`): `y_ij = b0 + b1 x_ij + sum_s g_s species_s + u_j + e_ij`, with `u_j ~ N(0, s_u^2)` for source `j` and `e_ij ~ N(0, s_e^2)`. Species dummies only for species present in the pair's data (reference `B. rossi`). Fit by **restricted maximum likelihood in numpy**: with `lambda = s_u^2 / s_e^2` and `H_j = I + lambda J` (J all-ones, size n_j), use `H_j^-1 = I - (lambda / (1 + n_j lambda)) J` and `log|H_j| = log(1 + n_j lambda)`. For a given lambda, the GLS estimate is `b = (X' H^-1 X)^-1 X' H^-1 y`, residual `r = y - X b`, and `s_e^2 = r' H^-1 r / (n - p)`. The profiled REML criterion to minimise is `(n - p) log s_e^2 + sum_j log(1 + n_j lambda) + log|X' H^-1 X|`. Minimise over `t = log(lambda)` in [-12, 6] with a 61-point grid then golden-section refinement (tolerance 1e-6); if the minimum is at the lower bound, report `s_u^2 = 0` (boundary). Report `b1`, its model-based SE from `s_e^2 (X' H^-1 X)^-1`, `s_u^2`, `s_e^2`, ICC = `s_u^2 / (s_u^2 + s_e^2)`.
   - When the species of the pair's data is confounded with a single source (S-CB017 is the only *B. canis* source), the species fixed effect and that source's random intercept are not separately identifiable: report `g_s` but flag `species_identifiable: false`; the slope `b1` is still estimable.
   - **Inference for b1**: p value by permuting x within source (preserves cohort structure), `--permutations` default 2000, statistic |b1|; 95% interval by bootstrap of dogs resampled within source, `--bootstrap` default 2000, percentile method. The model-based SE is reported alongside.
   - BH across all pairs of the main model (one family). `significant` = BH p < 0.05.

3. **Heterogeneity and species slopes.** Per source, OLS slope of y on x (same scaling) with 95% interval (t-based) and the Spearman rho; Cochran Q = sum w_j (b_j - b_fe)^2 with w_j = 1/SE_j^2, df = k - 1, I^2 = max(0, (Q - df) / Q). Species-specific slopes: refit step 2 with an `x * species` interaction; report the interaction coefficient and its permutation p (permute x within source; 1000 permutations). `direction_agrees_with_exp01`: sign of b1 equals sign of the EXP01 rho.

4. **When statsmodels is justified.** The random-intercept model above is exact in numpy and is the default. A random slope per source (`(1 + x | source)`) needs `statsmodels.MixedLM`, but with 2 to 4 sources per pair the slope variance cannot be estimated reliably; the per-source slopes and I^2 in step 3 answer the same question more honestly. Only if the owner asks for random slopes: install statsmodels into `.venv`, add it to `scripts/requirements-experiments.txt`, run with `--random-slopes` on pairs with at least 4 sources, and report it as a sensitivity. Also use statsmodels to cross-check step 2 once, if it is installed (acceptance check 3).

5. **Sensitivities** (each reported in `mixed_effects` under `sensitivity`): (a) source sub-cohorts as clusters instead of sources (`source_subcohort`); (b) `--include-controls`; (c) source as a fixed effect (OLS with source dummies; equals the within-source slope).

6. **Minimal severity score and transfer.** Cohorts with an outcome: S-CB050 (death, 141 infected dogs, 15 events) and S-CB017 (complicated, 31 infected dogs, 18 events). Candidate predictors: the canonical variables measured in both cohorts in at least 80% of infected dogs: `wcc`, `seg_neutrophils`, `band_neutrophils` (lymphocytes, monocytes and eosinophils exist for only 97 of 141 S-CB050 dogs and are excluded by the 80% rule; record this). Procedure for a training cohort T and test cohort V:
   - Transform as in 2.3, standardise with T's mean and SD.
   - Select the 2 candidates with the largest |AUC - 0.5| (Mann-Whitney AUC against T's outcome).
   - Fit logistic regression with a ridge penalty (lambda = 1 on standardised coefficients, intercept unpenalised) by Newton-Raphson in numpy (at most 100 iterations, tolerance 1e-8).
   - **Internal AUC**: the whole procedure (including selection) in stratified 5-fold CV repeated 20 times in T; AUC of the repeat-averaged out-of-fold probability, interval by 2000 stratified bootstrap resamples.
   - **External AUC**: refit on all of T, score V standardised with T's parameters ("frozen"); interval by 2000 stratified bootstrap resamples of V. Also `external_auc_restandardised`: V standardised with its own mean and SD (removes laboratory calibration shifts; ranking within V is unchanged for a monotone score, so this mainly checks sign stability and is expected to equal the frozen AUC when both selected variables keep their sign).
   - **Transfer loss** = internal AUC - external AUC.
   - Analyses: **A** S-CB050 (death) -> S-CB017 (complicated); **B** S-CB017 (complicated) -> S-CB050 (death); **C** S-CB050 cohort 1 -> S-CB050 cohort 2 (same label, same species and hospital; 3 test deaths; reference for how much loss comes from label and species in A and B). `--min-train-events` default 8; analyses below it are recorded as skipped.
   - The score is a minimal two-variable severity signal for a transfer experiment, not a clinical score.

## 4. Outputs

### 4.1 Experiment JSON

`data/experiments/EXP07-POOL-haematology.json`.

`experiment` block:

- `code` `EXP07-POOL-haematology`; `name` "Harmonised pooled haematology: cohort-adjusted relationships and severity transfer"; `description` one paragraph naming the six datasets, the REML random-intercept model, the permutation and bootstrap inference and the transfer analyses.
- `method` `mixed`; `dataset` `POOL01`.
- `parameters`: `{"seed": 20261105, "permutations": 2000, "interaction_permutations": 1000, "bootstrap": 2000, "max_pairs": 20, "min_cohort_n": 15, "min_sources": 2, "min_species_n": 5, "population": "infected", "include_controls": false, "transform": "log10(x + c) for counts", "scaling": "pooled within-source SD", "reml_log_lambda_bounds": [-12, 6], "alpha": 0.05, "adjustment": "benjamini_hochberg", "transfer_candidates": ["wcc", "seg_neutrophils", "band_neutrophils"], "transfer_min_coverage": 0.8, "transfer_n_markers": 2, "transfer_ridge_lambda": 1.0, "transfer_cv_folds": 5, "transfer_cv_repeats": 20, "min_train_events": 8, "random_slopes": false}`
- `script` `scripts/experiment_mixed.py`; `script_version` (12-character SHA-256 prefix); `run_utc`.
- `n_subjects`: distinct POOL01 subjects used in at least one main model; `n_variables`: distinct variables in the tested pairs; `n_tests`: number of main-model pairs (= association rows).
- `summary`: pairs tested, how many keep the EXP01 sign and are BH-significant, how many show I^2 above 75%, and the three transfer AUCs with losses.

`associations`: one row per main-model pair. `variable_a` = x, `variable_b` = y (POOL01 codes), `test` `lmm_reml_random_intercept`, `estimate` = b1, `estimate_label` `beta_sd` (slope in within-source SD units), `n` = dogs, `p_value` (permutation), `p_adjusted` (BH), `significant`, `trivial` = false, except true for `haemoglobin`-`haematocrit` (positive control, near-definitional), `direction` `positive` / `negative`, `detail` `{"ci_low", "ci_high", "se_model", "sources": [...], "n_by_source": {...}, "sigma_u2", "sigma_e2", "icc", "boundary": false, "i2", "exp01_rho", "direction_agrees_with_exp01"}`.

`cluster_assignments`: `[]`.

`results`:

| kind | title | sort_order | payload |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | `{"sections": [...]}` |
| `pooled_descriptives` | Per-cohort medians after unit harmonisation | 1 | see below |
| `mixed_effects` | Cohort-adjusted re-test of EXP01 relationships | 2 | see below |
| `transfer` | Two-variable severity signal: transfer between cohorts | 3 | see below |
| `run_notes` | Pairs, exclusions, conversions and choices | 4 | see below |

`pooled_descriptives` payload:

```json
{"variables": [
  {"code": "haematocrit", "unit": "L/L",
   "conversions": {"S-CB017": "HMT % / 100", "S-CB013": "PCV value, L/L, centrifuged PCV"},
   "cells": [{"source": "DS05", "species": "B. rossi", "status": "infected", "n": 148, "median": 0.21, "q1": 0.14, "q3": 0.30, "min": 0.05, "max": 0.55},
             {"source": "S-CB017", "species": "B. canis", "status": "infected", "n": 31, "median": 0.38, "q1": 0.33, "q3": 0.43, "min": 0.2, "max": 0.5}]}
 ]}
```

`mixed_effects` payload:

```json
{"pairs": [
  {"x": "haematocrit", "y": "wcc", "exp01_rho": -0.462, "sources": ["DS05", "S-CB017"], "n": 177,
   "beta": -0.41, "ci": [-0.55, -0.27], "se_model": 0.07, "p_perm": 0.0005, "p_adjusted": 0.002,
   "sigma_u2": 0.02, "sigma_e2": 0.83, "icc": 0.02, "boundary": false,
   "species": {"B. canis": {"gamma": 0.1, "identifiable": false}},
   "species_slope_interaction": {"B. canis": {"beta": 0.05, "p_perm": 0.6}},
   "per_source": [{"source": "DS05", "n": 148, "slope": -0.45, "ci": [-0.6, -0.3], "spearman": -0.46}],
   "heterogeneity": {"Q": 0.4, "df": 1, "I2": 0.0},
   "direction_agrees_with_exp01": true,
   "sensitivity": {"subcohort_clusters": {"beta": -0.41, "ci": [-0.56, -0.26]}, "include_controls": null, "source_fixed": {"beta": -0.42}}}
 ],
 "dropped_pairs": [{"x": "haematocrit", "y": "albumin", "reason": "albumin in one source only"}]}
```

`transfer` payload:

```json
{"analyses": [
  {"id": "A", "train": "S-CB050", "train_label": "died vs survived (B. rossi)", "test": "S-CB017", "test_label": "complicated vs uncomplicated (B. canis)",
   "label_mismatch": true, "species_mismatch": true,
   "candidates": ["wcc", "seg_neutrophils", "band_neutrophils"], "selected": ["band_neutrophils", "wcc"],
   "coefficients": {"intercept": -2.3, "band_neutrophils": 0.6, "wcc": 0.2},
   "n_train": 141, "events_train": 15, "n_test": 31, "events_test": 18, "epv_train": 7.5,
   "internal_auc": 0.66, "internal_auc_ci": [0.5, 0.8], "external_auc": 0.58, "external_auc_ci": [0.37, 0.78],
   "external_auc_restandardised": 0.58, "transfer_loss": 0.08},
  {"id": "C", "train": "S-CB050 cohort 1", "test": "S-CB050 cohort 2", "status": "done"}
 ],
 "excluded_candidates": [{"code": "lymphocytes", "reason": "measured in 97 of 141 S-CB050 infected dogs (< 80%)"}]}
```

`run_notes` payload: `{"inputs": [{"file": "data/tidy/DS05.json", "sha256": "..."}], "pairs_candidate": [...], "pairs_tested": [...], "pairs_dropped": [...], "population_counts": {"DS05": 149, "S-CB050": 141, "S-CB017": 31, "DS03": 103, "S-CB013": 7}, "dropped_strata": [...], "transforms": {"wcc": {"c": 0}}, "reml_boundary_fits": [...], "skipped_transfer": [...], "warnings": []}`.

Interpretation sections (headings): "The question"; "What was pooled and how units were aligned" (the coverage table in words: no variable is in all six datasets); "Which DS05 relationships hold elsewhere" (numbers: beta, interval, BH p, I^2, sources); "Does it differ by species"; "Does a severity signal travel" (internal and external AUC, loss, label and species mismatch); "How far this goes" (section 6).

### 4.2 Other artefacts

`data/tidy/POOL01.json` (section 2.2). Nothing else.

## 5. Acceptance checks

1. **POOL01 counts**: 571 subjects (150 DS05, 161 S-CB050, 47 S-CB017, 117 DS03, 96 S-CB013); 112 S-CB050 subjects carry `lymphocytes` (from S-CB517); no subject code repeats; `outcome_death` has 15 `Died`, `outcome_complicated` 18 `complicated`.
2. **Units**: the per-source medians print inside the ranges of 2.2; S-CB017 healthy-dog haematocrit median near 0.52 (raw HMT 51-55), DS03 control HCT median near 0.52 (dataset record), DS05 `mchc` median in g/L between 300 and 380.
3. **REML correctness**: (a) a simulation test inside the script (`--selftest`): 4 clusters of 40, true b1 = -0.4, s_u^2 = 0.5, s_e^2 = 1, 200 replicates; mean b1 within 0.03 of -0.4 and mean s_u^2 within 30% of 0.5; (b) with one source only, b1 equals the OLS slope to 1e-8; (c) if statsmodels happens to be available, `MixedLM(..., groups=source).fit(reml=True)` gives the same b1 to 1e-4.
4. **DS05 anchor**: for every pair, the DS05 per-source slope has the sign of the EXP01 rho, and the DS05 per-source Spearman equals the EXP01 estimate to 2 decimals for dogs in both analyses (the DS05 *B. vogeli* dog is excluded here, so small differences are expected).
5. **Null**: `--shuffle-within-source --seed 1..20` (permutes y within source before fitting) gives a BH-significant pair in no more than 1 of 20 seeds, apart from the positive control.
6. **Positive control**: `haemoglobin`-`haematocrit` has beta above 0.9 in DS05 and DS03.
7. **Reproducibility**: same seed, identical `associations` and `results` (ignore `run_utc`).
8. **Load**: `Babesiosis.Console --datasets-only` loads POOL01 then the experiment; SQL checks in section 7.
9. **Wording**: no "subtype", no "prognostic", no "clinically usable" in the JSON; species named in every transfer sentence.

## 6. Caveats and reporting language

- **Coverage.** No variable is shared by all six datasets; most pairs rest on two sources, so "holds across cohorts" usually means "holds in one other cohort". Albumin and total protein could not be pooled at all.
- **Species.** *B. rossi* (DS05, S-CB050, DS03), *B. canis* (S-CB017) and *B. vogeli* (S-CB013, 7 dogs). Species is confounded with source for *B. canis*; a species difference cannot be told apart from a hospital, laboratory, country or case-mix difference.
- **Laboratories and methods.** Five laboratories with different analysers; PCV (S-CB013) is not analyser haematocrit; S-CB050 WBC is a differential total; band counts depend on the smear reader. The random intercept absorbs level shifts, not differences in scale or definition.
- **Shared animals.** S-CB050 and S-CB517 are the same dogs (merged; SRC-A). DS03 (SRC-E) and S-CB050 (SRC-A) are both University of Pretoria *B. rossi* studies; overlap of dogs cannot be checked from the files. Count replication by source letter, and treat DS03 and S-CB050 agreement as weaker than agreement with S-CB017.
- **Few clusters.** 2 to 4 sources per pair: the between-source variance is poorly estimated and often at the boundary; the slope inference uses within-source permutation and bootstrap for that reason.
- **Different outcomes.** Death (S-CB050, includes euthanasia) and complicated disease (S-CB017, WHO-style criteria) are different labels in different species; transfer loss mixes label, species and laboratory effects. 15 and 18 events; the two-variable score is a transfer experiment, not a severity score for use.
- **Timing.** S-CB017 day-1 samples were taken after imidocarb treatment (6-8 h for cytokines per the article; haematology timing not stated); the other cohorts are admission samples.
- Wording: "relationship holds / does not hold in cohort X", "cohort-adjusted slope"; never "validated", "prognostic" or "subtype".

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md`, this spec, `scripts/tidy_ds05.py`, `scripts/experiment_pairwise.py`, the specs EXP03, EXP05, EXP09 (sections 2.2), `data/tidy/DS05.json` variable list, `data/experiments/EXP01-DS05-pairwise.json` associations. Done when you have the source code for every canonical variable in each input tidy file.
2. **Upstream tidy files.** Check that `data/tidy/S-CB050.json`, `S-CB517.json`, `S-CB017.json`, `DS03.json`, `S-CB013.json` exist; if not, build them from their specs first (EXP03: `tidy_s_cb050.py`, `tidy_s_cb517.py`; EXP05: `tidy_s_cb017.py`, `tidy_ds03.py`; EXP09: `tidy_s_cb013.py`). The EXP05 DS03.json holds all 138 DS03 dogs; POOL01 filters on `group_label` (2.2).
3. **Tidy POOL01.** Write and run `.venv/Scripts/python.exe -I scripts/tidy_pool01.py`. Done when acceptance checks 1-2 pass.
4. **Script.** Write `scripts/experiment_mixed.py` (numpy only; docstring with inputs, outputs, environment and the command): `.venv/Scripts/python.exe -I scripts/experiment_mixed.py [--seed 20261105] [--permutations 2000] [--bootstrap 2000] [--max-pairs 20] [--include-controls] [--selftest] [--shuffle-within-source] [--random-slopes]`. Copy `rankdata`, `bh_adjust`, `perm_p` from `experiment_pairwise.py`. Run `--selftest` first.
5. **Run.** `.venv/Scripts/python.exe -I scripts/experiment_mixed.py`. Expected 5 to 15 minutes (20 pairs x 2000 permutations x 1-D REML).
6. **Load.** From `console/Babesiosis.Console`: `dotnet run -- --datasets-only`. SQL: `SELECT n_subjects, independent_source FROM dbo.dataset WHERE dataset_code = 'POOL01'` (571, `POOL`); `SELECT COUNT(*) FROM dbo.association a JOIN dbo.experiment e ON e.experiment_id = a.experiment_id WHERE e.experiment_code = 'EXP07-POOL-haematology'` equals `n_tests`; `SELECT kind FROM dbo.experiment_result r JOIN dbo.experiment e ON e.experiment_id = r.experiment_id WHERE e.experiment_code = 'EXP07-POOL-haematology'` gives the five kinds.
7. **Verify.** Acceptance checks 1-9.
8. **Document.** `scripts/README.md` rows for `tidy_pool01.py` and `experiment_mixed.py`; `docs/database.md` (POOL01 and the experiment); correct the EXP07 card and the data table in `docs/ml-experiment-plan.html` (coverage table; S-CB517 is part of S-CB050); note in `experiment_specs/README.md` that a pooled dataset's `independent_source` is `POOL` with the letters in `notes`.
9. **Optional.** A web view for method `mixed` (forest plot of per-source and pooled slopes per pair) only after everything above passes.

## 8. Open questions

1. **README conflict on `independent_source`.** The README says a pooled dataset sets it to the list of SRC letters, but `dbo.dataset.independent_source` is `VARCHAR(10)` and the loader reads a string. Default: `POOL`, letters in notes and in the `independent_source` variable.
2. **S-CB017 HMT unit.** Settled: the EXP05 spec stores it in L/L (raw % / 100). Default: use as is after checking `unit`.
3. **S-CB013 `PLT count` unit and `Gender` coding.** Unit presumed x10^9/L (range 4-434); gender 1/2 undocumented. Default: platelets used as x10^9/L; S-CB013 sex not pooled.
4. **DS03 tidy scope.** Settled: the EXP05 spec tidies all 138 DS03 dogs. POOL01 takes the 117 natural-infection and control dogs and excludes the IMHA dogs and the 5 experimental dogs, which are SRC-B beagles (DS02).
5. **Which WBC for S-CB050 dogs.** Default: the S-CB050 value (differential total); see EXP03 section 8.
6. **Transfer candidates are only three leukocyte variables.** Haematocrit and platelets, the markers most often reported for severity, are absent from S-CB050. Default: run as specified and say so; no imputation across cohorts.
7. **Include S-CB013 at all?** It adds 7 *B. vogeli* dogs and mostly uninfected community dogs. Default: include in POOL01 and in descriptives and the `--include-controls` sensitivity; it drops out of the infected-only models by the minimum-n rule.
