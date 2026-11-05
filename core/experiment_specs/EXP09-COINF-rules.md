# EXP09 COINF rules: Co-infection association rules in DS05 and S-CB013

| Field | Value |
|---|---|
| Experiment code | `EXP09-COINF-rules`, run as two sub-runs: `EXP09-DS05-rules` (dataset `DS05`) and `EXP09-SCB013-rules` (dataset `S-CB013`) |
| Layer | 2 (pathogen-combination analysis over two tidy datasets) |
| Method token | `rules` (goes in `experiment.method` of both sub-runs) |
| Dataset(s) | `DS05` (exists), `S-CB013` (tidy file to be created). Each sub-run sets its own `experiment.dataset`; `EXP09-COINF-rules` is only the spec code |
| Readiness | tidy file needed (`S-CB013`); `DS05` needs two derived variables added by a small change to `scripts/tidy_ds05.py` |
| Python environment | `.venv` (Python 3.13, numpy 2.5.4). Nothing to install. `scipy` and `mlxtend` are NOT in `.venv` (checked), so Apriori, Fisher exact and permutation tests are numpy/stdlib implementations. The tidy scripts are stdlib only. `scipy` 1.17.1 exists in `.venv-nlp` and is used only for the acceptance cross-check of the Fisher implementation, never inside the script |
| Estimated build effort | medium (two tidy changes, one experiment script, two runs) |
| Suggested model for the building agent | sonnet: every step is specified; the only judgement call is the wording of the cleaning notes |
| Depends on | `data/tidy/DS05.json` (exists; regenerated after the edit in 2.2b). `EXP09-DS05-rules` must run before `EXP09-SCB013-rules` because the cross-dataset comparison reads `data/experiments/EXP09-DS05-rules.json` |

## 1. Question and hypotheses

Q1. Do particular pathogen combinations occur together more or less often than independence predicts (support, confidence, lift)?
Q2. DS05 only: do dogs co-infected with a second pathogen differ in admission haematology from dogs with a single pathogen?

Hypotheses (exploratory, directional; no source article states them formally):
- H1 (S-CB013): Babesia vogeli and Anaplasma platys co-occur more than expected (lift above 1). Motivation: article CB013 (Shapiro et al. 2017) reports 4 of 7 B. vogeli positive dogs also A. platys positive, against 26 of 96 dogs overall (about 1.9 of 7 expected).
- H2 (S-CB013): haemotropic mycoplasma status is unrelated to B. vogeli and A. platys status (lift near 1). CB013 reports no haematological association for haemoplasmas.
- H3 (DS05): co-infected dogs (B. rossi + Ehrlichia canis PCR, 3 dogs) have lower haematocrit and platelets than single-infected dogs. Not testable with useful power here.

Negative finding: every Fisher pair has BH-adjusted p at or above 0.05 and every lift interval includes 1. Report it as "no detectable departure from independence at these sample sizes", not as evidence of independence.

State plainly in the interpretation: DS05 has three co-infected dogs, so its rule table is a description, not inference. S-CB013 (96 dogs; 7 B. vogeli, 26 A. platys, 22 haemoplasma positive) is where inference is possible, and even there cells are small.

## 2. Data

### 2.1 Sources

| Source | Content | Licence / independent source |
|---|---|---|
| `data/tidy/DS05.json` (from `data/raw/DS05/BET Study Dataset.xlsx`) | 150 dogs, article CB126, B. rossi endemic South Africa. PCR variables (type `C`, levels `positive`/`negative`): `pcr_b_rossi` (149 positive, 1 negative), `pcr_b_vogeli` (1 positive), `pcr_e_canis` (3 positive), `pcr_t_equi` (0 positive). `subjects[].group_label`: `B. rossi only` 146, `B. rossi + E. canis` 3, `B. vogeli only` 1. All four PCR variables have `include_default = 0`, so EXP01 never used them | SRC-F |
| `data/raw/S-CB013/PMC5558717_supplementaryFiles.zip`, member `12917_2017_1169_MOESM4_ESM.xlsx` | Shapiro et al. 2017 (BMC Vet Res 13:238), Additional file 4. Sheets: `All data` (97 rows = header + 96 dogs, 21 columns), `Moree` (47 dogs incl. DOG Y51, DOG Y53), `Ti Tree` (51 dogs), `Y51Y53` (2 dogs). Free-ranging dogs, Ti Tree (Northern Territory, n=51) and Moree area (NSW, n=45) | article CC BY (presumed for the supplement); SRC-L; status_code 1 |
| `data/inspection/S-CB013.json` | first rows per sheet, to confirm headers | |
| `datasets.jsonl`, record `dataset_id = "S-CB013"` | fields `data_dictionary` ("Absent"), `missingness`, `groups_and_controls`, `overlaps`, `unverified_fields` say what is undocumented | |
| `articles/CB013_2017_vector-borne-zoonotic-diseases-north-west.md`, `data/markdown/CB013.md` (git-ignored, this machine only) | pathogens screened: A. platys, B. vogeli, M. haemocanis and Candidatus M. haematoparvum (the two mycoplasma qPCR targets, columns `Myco1` and `Myco2`; which column is which species is NOT stated in the workbook), Bartonella (never detected, no column). Anaemia = PCV < 0.30 L/L | |

Pathogens covered by the S-CB013 screen (confirmed from workbook headers and the article): Babesia vogeli, Anaplasma platys, haemotropic mycoplasma target 1 (`Myco1`), haemotropic mycoplasma target 2 (`Myco2`). There is no Ehrlichia, Hepatozoon or Theileria column.

Misnamed headers in `All data` (verified against `datasets.jsonl` and the inspection file): `Anaplasma platys alone` has 26 ones, equal to the number of non-blank `Anaplasma CT`, so it means "A. platys positive", not "alone"; `Babesia vogeli alone` has 7 ones = non-blank `Babesia CT`; `Haemoplasmas alone` has 22 ones; `Polymicrobial` has 8 ones (definition not given in the file).

Other individual-level datasets with more than one pathogen per dog (searched `datasets.jsonl` for `co-infect`, `Ehrlichia`, `Anaplasma`, `Hepatozoon`, `PCR`; status_code 1 only):
- `S-CB042` (SRC-K, 48 B. vulpes dogs, JVIM 2019, Barash et al.): about 29 dogs with M. haemocanis / Candidatus M. haematoparvum co-infection plus Ehrlichia IFA. Individual-level, no tidy file, raw `data/raw/S-CB042/PMC6766513_supplementaryFiles.zip`. Candidate for a later sub-run; NOT in scope here.
- `S-CB106` / `S-CB148` (9 dogs, PDF follow-up PCR table, longitudinal): too small; not a candidate.
- `DS01`, `DS02`, `DS04`, `DS08`, `S-CB017`, `S-CB050`, `S-CB071`, `S-CB091`, `S-CB137`, `S-CB147`, `S-CB517`, `S-CB005`: PCR or co-infection appears only as a confirmation or exclusion criterion (single-pathogen or experimental cohorts). Not candidates.

### 2.2 Tidy files required

#### 2.2a `S-CB013` (new): `scripts/tidy_s_cb013.py` -> `data/tidy/S-CB013.json`

Follow `scripts/tidy_ds05.py` for structure, output schema (README "Tidy dataset JSON"), `add_var` / `add_obs`, level counting and the dataset block. Copy `col_index`, `read_workbook` and `to_num` (tidy scripts are standalone). `read_workbook(path)` calls `zipfile.ZipFile(path)`, which accepts a file object, so read the member with `zipfile.ZipFile(SRC_ZIP).read(MEMBER)` and pass `io.BytesIO(data)`. Stdlib only. Docstring usage: `python -I scripts/tidy_s_cb013.py` from `core/`. The raw zip is never modified. Dataset block: `code` `S-CB013`; `article_code` `CB013`; `source_file` `data/raw/S-CB013/PMC5558717_supplementaryFiles.zip` (name the member in a note); `source_sha256` of the zip from `data/manifest.jsonl`; `independent_source` `SRC-L`; other fields from `datasets.jsonl` as `tidy_ds05.py` does; `script` `scripts/tidy_s_cb013.py`.

Subjects: one per row of `All data` (96). `code` = `Sample No` stripped (`DOG 1`, `N27`, `P12`, ...). Look columns up by header text in row 1, not by index (the other sheets have different headers). `DOG Y51` and `DOG Y53` exist only in `Moree`/`Y51Y53`; exclude and note.

| Variable `code` | Raw column (`All data`) | type | domain | Coding / rule |
|---|---|---|---|---|
| `pcr_b_vogeli` | `Babesia CT` non-blank; cross-check `Babesia vogeli alone` | C | pathogen | `positive` if `Babesia CT` non-blank (7), else `negative`. Note the flag/Ct agreement |
| `pcr_a_platys` | `Anaplasma CT` non-blank; cross-check `Anaplasma platys alone` | C | pathogen | `positive` (26) / `negative` (70) |
| `pcr_myco1` | `Myco1` | C | pathogen | 1 `positive` (10), 0 `negative`. `description`: "haemotropic mycoplasma qPCR target 1 (M. haemocanis or Candidatus M. haematoparvum; assignment not stated in the file)" |
| `pcr_myco2` | `Myco2` | C | pathogen | same, 14 positive |
| `pcr_haemoplasma_any` | derived | C | pathogen | `positive` if `Myco1` or `Myco2` is 1 (expected 22, equal to `Haemoplasmas alone` and `Myco status`); `derived = true`, `derived_from = ["pcr_myco1","pcr_myco2"]` |
| `n_pathogens` | derived | N | pathogen | positives among `pcr_b_vogeli`, `pcr_a_platys`, `pcr_haemoplasma_any` (0-3); `derived = true` |
| `coinfected` | derived | C | pathogen | `yes` if `n_pathogens >= 2`, else `no`; `derived = true`. Note the `yes` count and whether it equals the file's `Polymicrobial` count (8); report any disagreement count |
| `polymicrobial_flag` | `Polymicrobial` | C | pathogen | `yes`/`no` as in the file; `include_default = 0`; "authors' flag, definition not given in the file" |
| `ct_babesia`, `ct_anaplasma` | `Babesia CT`, `Anaplasma CT` | N | pathogen | Ct, positives only (blank = negative, not missing); `include_default = 0` |
| `pcv` | `PCV value` | N | haematology | unit `L/L` (from the article, not the workbook); `ref_low` 0.30 with description "authors' anaemia threshold from control dogs, not a clinical reference interval" |
| `anaemia` | derived from `pcv` | C | haematology | `yes` if `pcv < 0.30`, else `no`; `derived = true`, `derived_from = ["pcv"]`. Cross-check against the file's `PCV` flag (13 ones); note mismatches |
| `plt_count` | `PLT count` | N | haematology | `x10^9/L` (presumed from the article note), range 4-434 |
| `thrombocytopenia_flag` | `PLT` | C | haematology | `yes`/`no` as in the file (18 yes); description states the file flags values up to 77 although the article says < 60 |
| `age_years` | `Age` | N | signalment | four coded values (0.5, 1.6, 3, 8.35); blank = missing (22); description: coded category values, not exact ages |
| `breed_code` | `Breed` | C | signalment | text `1`/`2`, coding undefined; 1 missing |
| `sex_code` | `Gender` | C | signalment | text `1`/`2`, coding undefined; complete |
| `entire_sterile_code` | `Entire/ster` | C | signalment | text `1`/`2`, coding undefined; 18 missing |
| `body_condition` | `BC` | O | signalment | score 2-4; 12 missing |
| `ticks_code` | `Ticks` | C | signalment | text `0`/`1`, coding assumed 0 = absent, 1 = present (state "assumed"); 68 missing |
| `site` | dog ID found in sheet `Ti Tree` or `Moree` | C | location | `Ti Tree (NT)` (expected 51) / `Moree (NSW)` (expected 45). Assert the two ID sets are disjoint and their union equals the 96 IDs, else stop with an error |
| `pcr_negative_control_flag` | `PCR negative 'control' dogs` | C | pathogen | `yes`/`no` as in the file (1 = `yes`, 46 dogs); `include_default = 0`; "coding unverified: looks inverted (1 seems to mean at least one pathogen positive)". Add a note comparing it with "any pathogen positive" computed from the presence variables |

`include_default = 1` for every variable above except those marked 0 and `pcr_negative_control_flag`. `time_point` is `''` throughout (one sample per dog). Observations: one per subject x variable with a value; blank cells are omitted, except that blank Ct means `negative` for the presence variables and no observation for the Ct variables.

`subjects[].group_label` = pathogen pattern from the three presence variables in the order B. vogeli, A. platys, haemoplasma, joined by ` + `: `none`, `B. vogeli only`, `A. platys only`, `haemoplasma only`, `B. vogeli + A. platys`, `B. vogeli + haemoplasma`, `A. platys + haemoplasma`, `B. vogeli + A. platys + haemoplasma`. `outcome_label` = null (no outcome in the file).

Notes to record in `dataset.notes`, one string each: 96 dogs in `All data`; `DOG Y51` / `DOG Y53` excluded (extra sheets only, origin unstated; Y51 is also B. vogeli positive and would make 8); the four misnamed headers and what they contain; blank Ct means negative; coded signalment with no dictionary; Myco1/Myco2 species assignment unstated; unresolved `N23A`/`N23B` question (independent animals 95 vs 96, from `unverified_fields`); the `PCR negative 'control' dogs` coding; the PLT flag cut-off discrepancy; every cross-check count above. Print counts, notes and the default test set at the end as `tidy_ds05.py` does.

#### 2.2b `DS05` (edit): add two derived variables to `scripts/tidy_ds05.py`

Without changing any existing variable or observation, add after the PCR variables are processed:
- `n_pathogens_pcr` (type `N`, domain `pathogen`, `derived = true`, `derived_from = ["pcr_b_rossi","pcr_b_vogeli","pcr_e_canis","pcr_t_equi"]`, `include_default = 0`): number of `positive` among the four. Description: "Count of positive PCR results among the four panel pathogens."
- `coinfected` (type `C`, domain `pathogen`, `derived = true`, same `derived_from`, `include_default = 0`): `yes` if `n_pathogens_pcr >= 2`, else `no`. Expected levels `yes` 3, `no` 147. Description: "single-infected comparison group is n_pathogens_pcr == 1".

Decision (added variable versus run-time): the DS05 co-infection variable is ADDED to the tidy file, because associations against it need `variable_b` to exist in the dataset. It has `include_default = 0`, so EXP01's test set and results do not change. Add one DS05 note: "EXP09 added n_pathogens_pcr and coinfected; EXP01 unaffected (include_default = 0)." Re-run the tidy script and reload.

### 2.3 Variables and filters

- Pathogen presence matrix: one row per dog, one 0/1 column per item. Default items: DS05 `pcr_b_rossi,pcr_b_vogeli,pcr_e_canis,pcr_t_equi`; S-CB013 `pcr_b_vogeli,pcr_a_platys,pcr_haemoplasma_any`. A dog with a missing item value is dropped from that run (expected: none). Items with zero positives (`pcr_t_equi`) or all positives are left out of itemsets and pair tests and listed in `run_notes.items_dropped`.
- S-CB013 sensitivity (in `run_notes.sensitivity`, no associations stored): replace `pcr_haemoplasma_any` by `pcr_myco1` and `pcr_myco2`; Fisher exact and BH over the 6 pairs.
- DS05 comparison responses: `domain = haematology`, `include_default = 1`, `derived = false` (expected 12: `haemoglobin`, `rcc`, `haematocrit`, `rdw`, `seg_neutrophils`, `band_neutrophils`, `lymphocytes`, `monocytes`, `eosinophils`, `platelets`, `nrbc_per_100_wbc`, `reticulocyte_pct`). Derived indices (`mcv`, `mch`, `mchc`, `wcc`, `arc`) are excluded unless `--include-derived`, in which case associations with their parents are marked trivial as in EXP01. Groups: `coinfected = yes` (3) versus `n_pathogens_pcr == 1` (147). A variable needs at least `min_group` (default 3) non-missing values in the co-infected group and `min_single` (default 10) in the single group, else it is skipped and listed.
- Not done: haematology comparison in S-CB013 (not requested; open question 2).

## 3. Method

numpy and stdlib only. Seed `20261105` (as EXP01): one `np.random.default_rng(seed)` per run, consumed in a fixed order (itemset bootstrap, rule bootstrap, then permutations and effect-size bootstraps in variable order) so the run reproduces exactly.

1. Load `data/tidy/<dataset>.json`. Build a subject x item 0/1 matrix `X` (positive = 1). `n_transactions` = dogs used.
2. Frequent itemsets by Apriori, levelwise: L1 = items with count >= `min_count` (default 2); join (k-1)-itemsets sharing k-2 items; prune a candidate if any (k-1)-subset is infrequent; count with `X[:, idx].all(axis=1).sum()`. For each itemset store `count`, `support = count/n` and a Wilson 95% interval. With at most 4 items this is trivial, but implement it generally. Do not add `mlxtend`.
3. Rules from every frequent itemset of size >= 2: every split into non-empty antecedent A and consequent C. `support = count(A+C)/n`; `confidence = count(A+C)/count(A)`; `lift = confidence / (count(C)/n)`; `leverage = support - (count(A)/n)(count(C)/n)`; `conviction = (1 - count(C)/n) / (1 - confidence)`, null when confidence = 1. Keep rules with `confidence >= min_confidence` (default 0.0 = keep all). Percentile bootstrap 95% intervals for lift and confidence from `bootstrap = 2000` resamples of dogs; resamples where count(A) or count(C) is 0 are skipped and counted in `run_notes.notes`. Sort by lift descending, then support.
4. Fisher exact test for every pair of retained items. Table `[[a, b], [c, d]]`, a = both positive. Two-sided p = sum of hypergeometric probabilities of all tables with the same margins whose probability is <= observed probability x (1 + 1e-7), using `math.lgamma`. Estimate = odds ratio `a*d/(b*c)`; if any cell is 0 add 0.5 to all four cells (Haldane-Anscombe) and set `zero_cell_corrected = true`. Interval: Woolf, `exp(log OR +- 1.96*sqrt(1/a + 1/b + 1/c + 1/d))` on the same (corrected) cells. A pair with an item margin of 0 or n is degenerate: skip and record in `pair_tests.skipped`.
5. DS05 only, co-infection comparison. For each response variable: Mann-Whitney U (co-infected vs single) with average ranks (copy `rankdata` from `scripts/experiment_pairwise.py`, keep the script standalone); permutation p from `permutations = 10000` random relabellings of the pooled complete values keeping group sizes: `p = (count(|U - n1*n2/2| >= |U_obs - n1*n2/2| - 1e-12) + 1) / (permutations + 1)`. Effect size = rank-biserial `r = 2U/(n1*n2) - 1` (positive = higher in the co-infected group) with a percentile bootstrap 95% interval (`bootstrap` resamples within each group). With 3 co-infected dogs the interval is very wide; say so. Also store the two medians and the Hodges-Lehmann shift (median of all pairwise differences co - single).
6. Multiple testing: Benjamini-Hochberg (`bh_adjust` copied from `experiment_pairwise.py`) across ALL stored associations of the run as one family (DS05: valid Fisher pairs + haematology comparisons; S-CB013: Fisher pairs). `significant = p_adjusted < alpha` (0.05). Itemsets and rules have no p values; they carry bootstrap intervals and are descriptive.
7. Stored associations. Fisher: `variable_a`/`variable_b` = the two pathogen variable codes in alphabetical order, `test = "fisher_exact"`, `estimate` = odds ratio, `estimate_label = "odds_ratio"`, `n` = dogs used, `direction` = `positive` if OR > 1 else `negative`, `trivial = false`. Comparison: `variable_a` = haematology variable code, `variable_b` = `coinfected`, `test = "mann_whitney_permutation"`, `estimate` = rank-biserial r, `estimate_label = "rank_biserial"`, `n` = non-missing values used, `direction` = `higher in co-infected` / `lower in co-infected`.
8. S-CB013 only: read `data/experiments/EXP09-DS05-rules.json` (error if missing) and build the "Comparison with DS05" interpretation section (4.1).
9. Interpretation text is generated from the computed numbers by a function in the script (as `experiment_pairwise.py` does), in plain language for a veterinary reader.

## 4. Outputs

### 4.1 Experiment JSON

Files: `data/experiments/EXP09-DS05-rules.json`, `data/experiments/EXP09-SCB013-rules.json`. Top-level keys as in the README.

`experiment` block:

| Field | Value |
|---|---|
| `code` | `EXP09-DS05-rules` / `EXP09-SCB013-rules` |
| `name` | `Pathogen co-infection rules, BET cohort (DS05)` / `Pathogen co-infection rules, free-ranging dogs in Australia (S-CB013)` |
| `description` | one sentence: itemsets, association rules and Fisher tests over PCR presence; DS05 adds a haematology comparison; descriptive for DS05 (3 co-infected dogs), inferential but small for S-CB013 |
| `method` | `rules` |
| `dataset` | `DS05` / `S-CB013` |
| `parameters` | `{"items": [...], "min_count": 2, "min_confidence": 0.0, "bootstrap": 2000, "permutations": 10000, "seed": 20261105, "alpha": 0.05, "min_group": 3, "min_single": 10, "include_derived": false, "adjustment": "benjamini_hochberg", "fisher_zero_cell_correction": "haldane_anscombe", "comparison_groups": {"co_infected": "coinfected == yes", "single": "n_pathogens_pcr == 1"}}` (`permutations`, `min_group`, `min_single`, `include_derived`, `comparison_groups` only in the DS05 run) |
| `script`, `script_version`, `run_utc` | `scripts/experiment_rules.py`; first 12 hex characters of the script's SHA-256; UTC ISO time |
| `n_subjects` | dogs used (150 / 96) |
| `n_variables` | items used + (DS05) haematology variables compared |
| `n_tests` | number of stored associations |
| `summary` | one paragraph: dogs per item, number co-infected, strongest rule by lift with its interval, Fisher pairs and how many are BH-significant, and for DS05 the haematology variables compared and significant |

`cluster_assignments`: `[]` in both runs.

`associations[]` per steps 6-7. Illustrative Fisher row (the script computes the real numbers): `{"variable_a": "pcr_a_platys", "variable_b": "pcr_b_vogeli", "test": "fisher_exact", "estimate": 4.06, "estimate_label": "odds_ratio", "n": 96, "p_value": 0.06, "p_adjusted": 0.18, "significant": false, "trivial": false, "direction": "positive", "detail": {"table": [[4,22],[3,67]], "ci_low": 0.8, "ci_high": 20.5, "zero_cell_corrected": false}}`. Illustrative comparison row: `{"variable_a": "haematocrit", "variable_b": "coinfected", "test": "mann_whitney_permutation", "estimate": -0.45, "estimate_label": "rank_biserial", "n": 150, "p_value": 0.4, "p_adjusted": 0.9, "significant": false, "trivial": false, "direction": "lower in co-infected", "detail": {"n_co": 3, "n_single": 147, "median_co": 0.15, "median_single": 0.2, "hl_shift": -0.04, "ci_low": -0.95, "ci_high": 0.7, "u": 130.0}}`.

`results[]`:

| kind | `title` | `sort_order` | payload |
|---|---|---|---|
| `interpretation` | `Explanation and interpretation` | 0 | `{"sections": [{"heading": str, "paragraphs": [str]}]}`; headings `Question`, `What was done`, `Main findings`, `Limits`; the S-CB013 run adds `Comparison with DS05` last |
| `itemsets` | `Frequent pathogen combinations` | 1 | `{"items": [codes], "labels": {code: display name}, "n_transactions": int, "min_count": int, "itemsets": [{"items": [codes], "count": int, "support": float, "support_ci": [lo, hi]}]}` |
| `rules` | `Association rules` | 2 | `{"min_confidence": float, "bootstrap": int, "rules": [{"antecedent": [codes], "consequent": [codes], "count": int, "support": float, "confidence": float, "lift": float, "leverage": float, "conviction": float or null, "lift_ci": [lo, hi], "confidence_ci": [lo, hi]}]}` |
| `pair_tests` | `Pairwise co-occurrence tests (Fisher exact)` | 3 | `{"pairs": [{"variable_a", "variable_b", "table": [[a,b],[c,d]], "odds_ratio", "ci_low", "ci_high", "zero_cell_corrected": bool, "p_value", "p_adjusted", "significant"}], "skipped": [{"variable_a", "variable_b", "reason"}]}` |
| `coinfection_comparison` (DS05 only) | `Haematology: co-infected versus single-infected dogs` | 4 | `{"definition": str, "groups": {"co_infected": {"n": 3, "subjects": [codes], "group_labels": {label: n}}, "single": {"n": 147}}, "rows": [{"variable", "name", "unit", "n_co", "n_single", "median_co", "median_single", "hl_shift", "rank_biserial", "ci_low", "ci_high", "p_value", "p_adjusted", "significant"}], "co_infected_dogs": [{"subject": code, "values": {variable: value}}], "skipped": [{"variable", "reason"}]}` |
| `run_notes` | `Items, exclusions and sensitivity` | 5 in DS05, 4 in S-CB013 | `{"items_used": [codes], "items_dropped": [{"code", "reason"}], "counts_per_item": {code: n_positive}, "n_dropped_missing": int, "sensitivity": {...} (S-CB013: myco1/myco2 pair tests), "cross_checks": {...}, "notes": [str]}` |

Interpretation content. `Question`: Q1 (and Q2 for DS05). `What was done`: Apriori, Fisher exact with BH, and (DS05) the permutation Mann-Whitney comparison, with the parameter values. `Main findings`: numbers for dogs per pathogen, co-infected count, top rule with lift and interval, Fisher pairs with OR, interval and adjusted p. `Limits`: three co-infected dogs in DS05, so descriptive; 7 B. vogeli positives in S-CB013 and wide intervals; no outcome; site confounds pathogen mix; PCR positivity is not disease; mostly healthy dogs in S-CB013; no causal claim. `Comparison with DS05` (S-CB013 run): for the pathogen both datasets share, Babesia (B. rossi in DS05, B. vogeli in S-CB013), give the fraction of Babesia-positive dogs that carry a second panel pathogen (DS05 3 of 150, 2.0%; S-CB013 4 of 7 B. vogeli dogs carry A. platys, plus any with haemoplasma, from the run); the different second pathogens (E. canis vs A. platys / haemoplasma); the different populations (hospital admissions of sick B. rossi dogs in South Africa vs mostly healthy free-ranging dogs in Australia); and that the two datasets share no pathogen pair, so the comparison is qualitative and the data must not be pooled. Read the DS05 numbers from `EXP09-DS05-rules.json`; do not hard-code them.

### 4.2 Other artefacts

- `data/tidy/S-CB013.json` (new); `data/tidy/DS05.json` (regenerated, 2 added variables).
- `scripts/tidy_s_cb013.py`, `scripts/experiment_rules.py`.
- No CSV and nothing else outside `data/experiments/` and `data/tidy/`.

## 5. Acceptance checks

1. `data/tidy/S-CB013.json`: `n_subjects` 96; `pcr_b_vogeli` `positive` 7 / `negative` 89; `pcr_a_platys` 26 / 70; `pcr_haemoplasma_any` 22 / 74; `site` 51 + 45; `anaemia = yes` for 13 dogs (matches the file's PCV flag; record any mismatch); B. vogeli and A. platys both positive in 4 dogs (the article's "four of 7"); `coinfected` count compared with `Polymicrobial` = 8 and recorded.
2. `data/tidy/DS05.json` after regeneration: `coinfected` `yes` 3 / `no` 147; the three `yes` subjects are exactly those with `group_label = "B. rossi + E. canis"`; variable count up by exactly 2; every other variable and observation unchanged (diff the old and new files ignoring `extracted_utc` and the two new variables). Re-run the EXP01 command and confirm `n_variables` 39, `n_tests` 740 and identical associations (only `run_utc` may differ).
3. Reproducibility: run each sub-run twice; outputs identical except `run_utc`.
4. Fisher check: for every 2 x 2 table in `pair_tests`, `p_value` and odds ratio agree to 1e-9 with `scipy.stats.fisher_exact(table)` run once in `.venv-nlp` from a scratchpad script (uncorrected tables only; not part of the repository).
5. Apriori check: for S-CB013 `count({pcr_b_vogeli, pcr_a_platys})` = 4; every itemset count equals a brute-force count from the matrix; every rule satisfies `confidence * count(A) = count(A+C)` and `lift = confidence / support(C)`.
6. Permutation behaviour (DS05): shuffle the `coinfected` labels 200 times (quick separate check, not saved) and run the comparison; the share of runs with any BH-significant haematology variable is about alpha (0.05) or less, allowing Monte-Carlo noise.
7. Load: `Babesiosis.Console --datasets-only` completes. SQL: `SELECT e.experiment_code, COUNT(*) AS n FROM dbo.association AS x JOIN dbo.experiment AS e ON e.experiment_id = x.experiment_id WHERE e.experiment_code LIKE 'EXP09-%' GROUP BY e.experiment_code` returns the stored association counts; `dbo.experiment_result` has the kinds in 4.1 for each code.
8. The DS05 `Limits` section says there are three co-infected dogs and the result is descriptive. The S-CB013 interpretation has the `Comparison with DS05` section. No sentence says "significant" without the adjusted p, and none says "cause".

## 6. Caveats and reporting language

- DS05: three co-infected dogs (B. rossi + E. canis PCR). The rule table and comparison describe those dogs. Keep the effect-size interval next to every p value. Do not rank haematology findings from this comparison.
- S-CB013: 96 dogs, 7 B. vogeli positive, 4 of them also A. platys positive. Two sites with different sampling dates (NT Nov 2010, NSW Feb 2013) confound pathogen mix with site. Mostly clinically healthy free-ranging dogs, so PCR positivity is not disease. Signalment codes undefined. Mycoplasma target species unstated. `DOG Y51` / `DOG Y53` excluded.
- Independence: DS05 is SRC-F, S-CB013 is SRC-L. Neither replicates the other (no shared pathogen pair).
- Species is a variable: B. rossi (DS05) and B. vogeli (S-CB013) differ in virulence; never pool.
- Wording: co-occurrence and association, not interaction or synergy; "no detectable departure from independence", not "independent"; lift above 1 is not a biological cause.
- S-CB013 anaemia uses the authors' threshold (PCV < 0.30 L/L), not a reference interval.

## 7. Build plan for the agent

Run all commands from `core/` (`C:\Workspaces\Babesiosis\core`). Open files with `encoding="utf-8"` (Windows defaults to cp1252).

1. Read: `experiment_specs/README.md`, `TEMPLATE.md`, this spec, `scripts/tidy_ds05.py`, `scripts/experiment_pairwise.py` (`rankdata`, `bh_adjust`, `perm_p`, `r`, and the JSON assembly in `main()`), `data/inspection/S-CB013.json`, the `S-CB013` record in `datasets.jsonl`, `articles/CB013_2017_vector-borne-zoonotic-diseases-north-west.md`. Done when the 2.2a variable table is clear.
2. Tidy DS05: edit `scripts/tidy_ds05.py` per 2.2b; run `python -I scripts/tidy_ds05.py`. Done when acceptance check 2 (tidy part) passes.
3. Tidy S-CB013: write `scripts/tidy_s_cb013.py` per 2.2a; run `python -I scripts/tidy_s_cb013.py`. Done when acceptance check 1 passes and every cross-check count is in `dataset.notes`.
4. Script: write `scripts/experiment_rules.py` with a module docstring (inputs, outputs, run command, dependency numpy) in the style of `experiment_pairwise.py`. Options: `--dataset`, `--code`, `--name`, `[--items a,b,c] [--min-count 2] [--min-confidence 0.0] [--bootstrap 2000] [--permutations 10000] [--seed 20261105] [--alpha 0.05] [--min-group 3] [--min-single 10] [--include-derived]`. The co-infection comparison runs only when the dataset has `coinfected` and `n_pathogens_pcr` and the code starts with `EXP09-DS05`; the DS05 cross-read happens only for `--dataset S-CB013`. Done when it runs on both datasets.
5. Run (DS05 first; each under a minute):
   `.venv/Scripts/python.exe -I scripts/experiment_rules.py --dataset DS05 --code EXP09-DS05-rules --name "Pathogen co-infection rules, BET cohort (DS05)"`
   `.venv/Scripts/python.exe -I scripts/experiment_rules.py --dataset S-CB013 --code EXP09-SCB013-rules --name "Pathogen co-infection rules, free-ranging dogs in Australia (S-CB013)"`
6. Load: run `Babesiosis.Console --datasets-only` (tidy datasets load before experiments; `appsettings.json` `ReviewRoot` must point at `core/`). Run the SQL check in acceptance check 7.
7. Verify: acceptance checks 1 to 8; fix and re-run until all pass.
8. Document: add `tidy_s_cb013.py` and `experiment_rules.py` rows to `scripts/README.md`; add the EXP09 codes and result kinds `itemsets`, `rules`, `pair_tests`, `coinfection_comparison` to the `dbo.experiment_result` line of `docs/database.md`; add `S-CB013` to any tidy-dataset list in `docs/data-files.md`; set the EXP09 Readiness cell in `experiment_specs/README.md` to "built"; update `docs/ml-experiment-plan.html` status if the page is kept.
9. Optional, only after 1-8 pass: a dedicated web view for method `rules` (rules table with lift bars) in `webapp/Babesiosis.Web/src/app/modules/experiments/views/`. Without it the app shows the interpretation plus formatted JSON.

## 8. Open questions

1. Item set for S-CB013. Default: three items (B. vogeli, A. platys, any haemoplasma) in the main run; the two mycoplasma targets only as the sensitivity run.
2. A haematology comparison in S-CB013 (PCV and platelets, co-infected vs single-infected) was not requested. Default: not done; it could be added as an inferential companion to DS05.
3. `S-CB042` (B. vulpes, mycoplasma and Ehrlichia co-infection, 48 dogs, SRC-K) is a third candidate. Default: out of scope; mention in `run_notes.notes` only.
4. The DS05 single-infected group includes the one B. vogeli-only dog (`n_pathogens_pcr == 1`, 147 dogs). Default: keep.
5. Whether the file's `Polymicrobial` (8) equals the derived `coinfected` count is unknown until the tidy script runs. Default: use the derived variable and report any disagreement in the notes.
