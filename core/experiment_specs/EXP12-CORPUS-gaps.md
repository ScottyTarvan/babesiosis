# EXP12 CORPUS gaps: Research-gap grid and trends over canine articles

| Field | Value |
|---|---|
| Experiment code | `EXP12-CORPUS-gaps` |
| Layer | 3 corpus |
| Method token | `gaps` (goes in `experiment.method`) |
| Dataset(s) | `null`. The run reads `articles.jsonl` only; no tidy dataset is involved, so `associations` and `cluster_assignments` are empty lists. |
| Readiness | ready |
| Python environment | `.venv` (numpy 2.5.4 is installed; scipy and statsmodels are NOT installed in `.venv`). The method is numpy-only: chi-square tail probabilities by the Wilson-Hilferty approximation, normal tails by `math.erfc`. Do not install scipy or statsmodels. |
| Estimated build effort | small (under 2 hours of agent work) |
| Suggested model for the building agent | haiku. The grids, residuals and Poisson/negative-binomial fits are mechanical once the normalisation rules below are implemented exactly. |
| Depends on | none. `articles.jsonl` must be current; `search-log.md` is cited in the interpretation. |

## 1. Question and hypotheses

Two questions, both restricted to canine articles (`id` starts with `CB`):

1. Which combinations of species group, primary category, evidence type, country group and publication period have no articles or far fewer than expected under independence? These are the candidate research gaps.
2. How has the share, and the absolute count, of each primary category changed over publication year?

Hypotheses (exploratory; the card names no literature hypothesis, so none is cited here):

- H1. Species group is not independent of primary category (permutation test on the species-by-category grid).
- H2. Species groups other than `B. canis` are under-represented in categories that need a clinical or pathology sample (`COA`, `REN`, `CAR`); direction: fewer articles than expected. Test by the residual flags, not by a separate model.
- H3. The share of `ERY` and `INF` articles has fallen over time relative to all canine articles (negative slope), while `OXO` has risen (positive slope). Direction is not known from the literature; the test reports the sign and interval.

A negative finding is: no grid rejects independence after permutation correction, or no cell has a residual below -2, or no category trend has a 95% interval excluding a rate ratio of 1.

## 2. Data

### 2.1 Sources

- `articles.jsonl`, one record per article (481 records; 444 canine). Fields used: `id`, `scope_label`, `include_type`, `species_short`, `species[]` (fallback only), `country`, `primary_category`, `evidence_type`, `first_pub_date`, `cohort_id`, `journal`, `pmcid`, `dataset_status_code`, `fulltext_checked`, `abstract_available`.
- `search-log.md` (repository root of `core/`): the search rounds, queries and screening counts. Cited in every gap claim.
- No other file is read. Do not read `index.md`, `research-map.md` or `data/syndromes/mentions.jsonl` for counts.

### 2.2 Tidy file required

Not applicable. The script reads `articles.jsonl` directly, as the corpus experiments do.

### 2.3 Variables and filters

Canine filter (mandatory): `id.startswith("CB")`. Do not count `HU` or `BG` records, even though they carry `primary_category` values in some cases. `scope_label` values present: `core canine evidence` 404, `canine review` 40, `human comparator` 27, `background` 10 (all 481 records). The canine set is `core canine evidence` plus `canine review` = 444 articles.

Default: reviews are included (they are canine articles and have an `evidence_type` of `review`). A sensitivity run with `--exclude-reviews` drops `include_type == "review"` (40 articles) and writes the same result kinds; its results are recorded in `run_notes` only, not as a second experiment file.

Grid variables and their groups (all 444 canine articles are assigned; no record is dropped for a missing value; `primary_category` is never null for CB records):

**Species group** from `species_short` (never null for CB records; 0 nulls counted):

| Group | Rule |
|---|---|
| `B. rossi` | `species_short` names B. rossi, or `B. canis rossi` (subspecies notation, mapped to B. rossi) |
| `B. canis` | names B. canis; `B. canis canis` is mapped to B. canis |
| `B. gibsoni` | names B. gibsoni |
| `B. vogeli` | names B. vogeli, or `B. canis vogeli` (mapped to B. vogeli) |
| `other/mixed` | everything else: names two or more groups (e.g. `B. canis, B. gibsoni`), or names no group (`Babesia sp.`, `Babesia spp.`, `mixed/unspecified`, `B. vulpes`, `B. microti`, `B. conradae`). |

Procedure: lowercase `species_short`; replace `canis canis`, `canis rossi` and `canis vogeli` with `canis`→ the mapped name (`canis canis`→`canis`, `canis rossi`→`rossi`, `canis vogeli`→`vogeli`); find the whole-word matches for `rossi`, `canis`, `gibsoni`, `vogeli`; if exactly one group matches, that group; otherwise `other/mixed`. Log the reason per raw value: `ok`, `mixed` (two or more groups matched) or `unspecified` (none matched).

**Country group** from the free-text `country` field (not normalised in the source; see Section 3, step 2 for the rule):

Levels in order: `India`, `South Africa`, `Poland`, `Croatia`, `Ukraine`, `Brazil`, `Serbia`, `Germany`, `Other`, `Unstated`.

**Evidence group** from `evidence_type` (free text, 30 distinct values):

Levels: `review`, `mechanistic`, `prognostic`, `associational`, `descriptive`, `other`. Rule in this order (first match wins, case-insensitive substring): contains `review` → `review`; `mechanistic` → `mechanistic`; `prognostic` → `prognostic`; `associational` → `associational`; `descriptive` → `descriptive`; else `other`. Under this rule `descriptive/associational` maps to `associational`, and `prognostic (associational)` maps to `prognostic`. Record every raw value in `normalisation_log`.

**Period** from `first_pub_date` (every CB record has one; years run 2006 to 2026; 2026 is partial, the window ends 2026-10-23):

Levels: `2006-2010`, `2011-2015`, `2016-2020`, `2021-2026`.

**Primary category** from `primary_category`, 11 levels: `ERY`, `INF`, `SEV`, `MET`, `REN`, `COA`, `OXO`, `CAR`, `END`, `NEU`, `PUL`. Use the codes as stored; their meanings are in `docs/ids-and-codes.md`.

Missing-data rule: none of the grid variables is missing for a CB record. If a future run finds a null, it is put in an explicit `Unstated` level for country, and the script stops with an error for any other variable.

Canine counts for these groups (computed 2026-11-05 from `articles.jsonl` with the rules above):

- Species group: other/mixed 146 (of which 115 `unspecified`, 31 `mixed`), B. canis 142, B. gibsoni 90, B. rossi 43, B. vogeli 23. Total 444.
- Country group: Other 110, Unstated 100, India 85, South Africa 36, Poland 29, Croatia 25, Ukraine 22, Brazil 17, Serbia 10, Germany 10. Total 444. (Raw `country` is null for 64 CB records and reads `not stated in abstract` (18), `not reported in abstract` (9), or an inferred phrase for the rest.)
- Evidence group: descriptive 241, associational 130, review 40, mechanistic 20, prognostic 13. Total 444.
- Period: 2006-2010 59, 2011-2015 85, 2016-2020 113, 2021-2026 187. Total 444.
- Primary category: ERY 96, INF 91, SEV 59, MET 50, REN 40, COA 40, OXO 21, CAR 18, END 14, NEU 8, PUL 7. Total 444.
- Zero cells in the observed grids: species by category 5 of 55; country by category 29 of 110; evidence by category 11 of 55.
- Cohort units: 38 distinct `cohort_id` values cover 101 articles; the other 343 canine articles have no `cohort_id`. Units = 38 + 343 = 381 cohort-or-article units. Cohort-adjusted (cohort-by-category) units total 415.

### 2.4 Cohort counting

Units are `cohort_id` when present, otherwise the article `id`. A unit is counted once per cell in which it appears (for example, a cohort with two articles, one `ERY` and one `INF`, counts once in `ERY` and once in `INF`). Report the cohort-adjusted count next to the article count everywhere a count appears.

Canine articles by `cohort_id`: 101 articles belong to a cohort; the reporting rule of CLAUDE.md applies: CB510 and CB511 are one study published twice and must count once in cohort units.

### 2.5 Trend series

Per primary category and per year (2006 to 2026, 21 years). Exposure (for the relative model) = all canine articles with that `first_pub_date` year. Counts are article counts; the cohort-adjusted series is a sensitivity output.

## 3. Method

Parameters with defaults (all recorded in `experiment.parameters`):

`seed` 20261105 · `permutations` 5000 · `residual_cut` -2.0 · `min_expected` 1.0 · `min_total_for_trend` 20 · `year_reference` 2016 · `alpha` 0.05 · `nb_dispersion_cut` 1.5 · `exclude_reviews` false · `cohort_key` `cohort_id` · `canine_prefix` `CB` · `articles_path` `articles.jsonl`.

1. **Load and filter.** Read `articles.jsonl` line by line (`json.loads` per line, with `encoding="utf-8"`). Keep records whose `id` starts with `CB`. If `exclude_reviews` is set, drop `include_type == "review"`. Assert that exactly 444 records remain (or 404 with `exclude_reviews`); stop with an error otherwise.

2. **Normalise.** Apply the species, country, evidence and period rules in Section 2.3. Country rule: (a) if the value contains one of the listed country keywords (case-insensitive substring), take the keyword whose first occurrence is earliest in the string, so `South Africa; Onderstepoort ...` is `South Africa`, and `Ukraine (inferred from publisher; not stated in abstract)` is `Ukraine`; (b) otherwise, if the value is null or contains `not stated` or `not reported` or `not specified`, the level is `Unstated`; (c) otherwise `Other`. Write one `normalisation_log` entry per raw value of `species_short`, `country` and `evidence_type`, with its group and count.

3. **Observed grids.** Four grids, each a contingency table of article counts (the row variable by the column variable):
   - `species_by_category` (5 by 11)
   - `species_by_evidence` (5 by 6)
   - `country_by_category` (10 by 11)
   - `period_by_category` (4 by 11)

   The primary category is always a column. Each grid sums to 444.

4. **Expected and residuals.** For each grid: row totals `R_i`, column totals `C_j`, grand total `N`; expected `E_ij = R_i * C_j / N`; Pearson residual `r_ij = (O_ij - E_ij) / sqrt(E_ij)`. Chi-square `X2 = sum((O-E)^2/E)` with df `(rows-1)(cols-1)`. Cramer's V = sqrt(X2 / (N * min(rows-1, cols-1))). Store observed, expected and residual matrices.

5. **Gap flags.** A cell is a `gap` when `r_ij < residual_cut` (default -2.0). A cell with `E_ij < min_expected` is also flagged `low_expected` and is reported, but a gap flag on such a cell is read with caution. Every cell with `O_ij = 0` is listed in `gap_cells` as `zero`, whatever its residual. Write `gap_cells` as one row per flagged or zero cell, with grid id, row, column, observed, expected, residual, flag.

6. **Permutation test for each grid.** Permute the row-variable label across the 444 articles `permutations` times (seed `seed`, one `numpy.random.default_rng(seed)` generator for the whole run, consumed in grid order). For each permutation, recompute X2 for the permuted table. `p_permutation = (1 + #{X2_perm >= X2_obs}) / (1 + permutations)`. Report this beside the Wilson-Hilferty chi-square p value (approximation: `z = ((X2/df)^(1/3) - (1 - 2/(9df))) / sqrt(2/(9df))`, p = normal upper tail by `math.erfc`).

7. **Cohort-adjusted counts.** For each grid, a unit `u` (Section 2.4) is counted once per cell in which it appears. Store `articles` and `units` per row and per column and per cell, for all four grids.

8. **Trends.** For each primary category with at least `min_total_for_trend` canine articles (ERY, INF, SEV, MET, REN, COA, OXO are eligible; CAR 18, END 14, NEU 8 and PUL 7 are reported as descriptive counts only, with `estimable = false` and no fit):
   - Poisson log-linear model, year as continuous covariate centred at `year_reference` (2016): `log E[y_t] = b0 + b1 * (year - 2016)`, with offset `log(N_t)` where `N_t` is all canine articles in year t (relative-share trend, primary). Fit by iteratively reweighted least squares in numpy: `beta <- beta + (X'WX)^-1 X'(y - mu)/...`, with `W = diag(mu)`, starting from `b0 = log(mean(y)+0.5)`, `b1 = 0`; iterate to `|delta beta| < 1e-10` or 100 iterations.
   - Rate ratio per year `RR = exp(b1)`; 95% Wald interval `exp(b1 +- 1.96 * se(b1))`, `se` from `sqrt(diag((X'WX)^-1))` at convergence.
   - Absolute-count model: the same Poisson fit without the offset (secondary; growth in absolute count).
   - Dispersion `phi = sum((y - mu)^2 / mu) / (n - p)`. If `phi > nb_dispersion_cut` (default 1.5), also fit a negative-binomial model with NB2 variance `mu + alpha mu^2`; estimate `alpha` by the method of moments, `alpha = max(0, sum(((y-mu)^2 - mu)/mu^2) / (n - p))`, refit with IRLS weights `mu/(1 + alpha mu)`, and iterate `alpha` twice. Report both models' RR, interval, and `phi`.
   - Permutation p for the relative-share slope (distribution-free check): among all canine articles, permute the indicator `is_category` within year strata, `permutations` times, and recompute the Spearman-type statistic (Pearson correlation of ranked `year` and ranked indicator). p = `(1 + #{|stat_perm| >= |stat_obs|}) / (1 + permutations)`.
   - Wald p for `b1` from `z = b1 / se`, two-sided normal p by `math.erfc`.
   - Benjamini-Hochberg across all p values of the run: the four grid permutation p values and the Wald p values of the trend models (relative and absolute). Write the adjusted value beside each.

9. **Outputs.** Write the JSON described in Section 4.1. `n_tests` = number of grid tests + number of trend p values (4 + 7 eligible categories x 2 models = 18 at the defaults; the builder confirms the count and writes it).

Numpy-only functions the builder writes: `chi2_stat`, `wilson_hilferty_sf`, `normal_sf`, `poisson_irls`, `nb_irls`, `bh_adjust` (same as in `scripts/experiment_pairwise.py`), `rank`, `permute_counts`. Do not add scipy or statsmodels.

## 4. Outputs

### 4.1 Experiment JSON

File: `data/experiments/EXP12-CORPUS-gaps.json`.

`experiment` block:

- `code`: `EXP12-CORPUS-gaps`
- `name`: `Research-gap grid and trends, canine articles`
- `description`: one plain sentence: species, category, evidence type, country and period grids over the canine articles, with residual gap flags, cohort-adjusted counts and category trends by year.
- `method`: `gaps`
- `dataset`: `null`
- `parameters`: every setting in Section 3 with its default, plus `exclude_reviews`, `articles_path`, `canine_prefix`. Include the guardrail string: `"search_caveat": "absence in this index reflects the search strategy; see search-log.md"`.
- `script`: `scripts/experiment_gaps.py`
- `script_version`: first 12 characters of the SHA-256 of the script file.
- `run_utc`: ISO 8601 UTC.
- `n_subjects`: 444 (canine articles; "subjects" here means articles).
- `n_variables`: 5 (species group, country group, evidence group, period, primary category).
- `n_tests`: as in step 9.
- `summary`: one plain paragraph with N, the number of gap cells per grid, and the number of categories with a trend whose interval excludes 1.

`associations`: `[]`. `cluster_assignments`: `[]`.

`results[]` (kinds, sort order, payload):

1. `interpretation` (sort 0): `{"sections": [{"heading": str, "paragraphs": [str]}]}`. Headings: Question; What was done; Main findings; Gaps and what they mean; Trends; Limits. Section 6 lists the required content.

2. `grids` (sort 1): `{"grids": [{"id": "species_by_category", "row_var": "species_group", "col_var": "primary_category", "rows": [str], "cols": [str], "observed": [[int]], "expected": [[float]], "residual": [[float]], "n": 444, "chi2": float, "df": int, "p_wilson_hilferty": float, "p_permutation": float, "cramers_v": float}]}`. Four grids: `species_by_category`, `species_by_evidence`, `country_by_category`, `period_by_category`. Round expected and residuals to 3 decimals.

3. `gap_cells` (sort 2): `{"cells": [{"grid": str, "row": str, "col": str, "observed": int, "expected": float, "residual": float, "flag": "gap" | "zero" | "low_expected"}], "residual_cut": -2.0, "min_expected": 1.0}`. A cell can have two flags; list it once with `flag` joined by `+` (for example `zero+low_expected`).

4. `cohort_adjusted_counts` (sort 3): `{"grids": [{"id": str, "rows": [str], "cols": [str], "articles": [[int]], "units": [[int]]}], "note": "units = distinct cohort_id (or article id) per cell"}`. Expect the primary-category totals of units: ERY 92, INF 81, SEV 59, MET 46, REN 37, COA 36, OXO 21, CAR 17, END 13, PUL 7, NEU 6 (total 415 across categories).

5. `trends` (sort 4): `{"model": "poisson_offset_primary", "reference_year": 2016, "years": [int], "series": [{"category": str, "estimable": bool, "counts": [int], "exposure": [int], "rate_ratio_per_year": float, "ci_low": float, "ci_high": float, "p_wald": float, "p_bh": float, "p_permutation": float, "phi": float, "nb_fitted": bool, "nb_alpha": float|null, "nb_rate_ratio_per_year": float|null, "absolute_rate_ratio_per_year": float|null, "absolute_ci": [float, float]|null, "cohort_units": [int]}]}`. Non-estimable categories (CAR, END, NEU, PUL) carry `counts` and `exposure` only, with the numeric fit fields `null`.

6. `normalisation_log` (sort 5): `{"species": [{"raw": str, "group": str, "reason": "ok"|"mixed"|"unspecified", "n": int}], "country": [{"raw": str, "group": str, "n": int}], "evidence": [{"raw": str, "group": str, "n": int}], "period": [{"year": int, "period": str, "n": int}]}`. Country has about 180 raw values, so this payload is the largest and must stay below 2 MB.

7. `run_notes` (sort 6): `{"included": int, "excluded": {"HU": int, "BG": int}, "reviews_included": bool, "species_groups": [...], "country_levels": [...], "min_expected": float, "residual_cut": float, "dropped": [], "skipped": [], "packages": ["numpy"], "not_used": ["scipy", "statsmodels"], "design_field_used": false}`. `design` is free text with 410 distinct values in 444 canine records and is not a grid variable; say so.

### 4.2 Other artefacts

None. The experiment writes only `data/experiments/EXP12-CORPUS-gaps.json`. Figures (heatmaps, trend chart) are rendered by the web app from the payloads; the builder does not create image files.

## 5. Acceptance checks

1. `articles.jsonl` read; canine count is 444 (404 with `--exclude-reviews`). HU and BG counts recorded (27 and 10) and not used.
2. Every grid's observed matrix sums to 444; every expected matrix sums to 444 (within 1e-6); chi-square and df recomputed independently match the stored values.
3. Species-by-category observed zeros: exactly 5 cells (the 5 zero cells computed in Section 2.3). Country-by-category zeros: 29. Evidence-by-category zeros: 11. The gap list includes every zero cell.
4. Species group totals match 146 / 142 / 90 / 43 / 23 (other/mixed / B. canis / B. gibsoni / B. rossi / B. vogeli).
5. Permutation: with a shuffled label (set `--shuffle-check`, not in the default run) the fraction of grids with `p_permutation < 0.05` is about 0.05. Run this once and record it in `run_notes`.
6. Reproduction: two runs with the same seed produce byte-identical `grids`, `gap_cells`, `trends` and `normalisation_log` payloads (only `run_utc` and `script_version` may differ if the script changed).
7. Load: the console reads the file (Section 7 step 5). `experiment.dataset` is null and the loader accepts it.
8. Interpretation reads correctly for a veterinary reader: it says which cells are gaps in the index, not in the literature, and cites `search-log.md`.

## 6. Caveats and reporting language

- **Absence in this index is absence in the search strategy, not necessarily in the literature.** Every gap claim in the interpretation states this and points to `search-log.md` (search rounds, queries, screening counts, 61 unresolved records). Use the phrase "no article in this index", never "no research has been done".
- Articles are not independent evidence: cohort-adjusted counts are shown beside every count, and CB510 and CB511 count once.
- Most notes appraise the abstract only (`abstract_available` true for all 444; `fulltext_checked` true for 179). Category and species labels are NLP or agent assignments, not human-reviewed (`category_source`, `category_confidence`).
- Species and country are free text or derived strings. The rules are in `normalisation_log`; read the log before quoting a species or country count. `species_short` `mixed/unspecified` and `Babesia sp.` are both `other/mixed`, which hides 115 species-unspecified articles inside one level; say so.
- Country is the author's study location as stated in the abstract, not a claim about where the dogs lived; 100 of 444 are `Unstated`.
- Trends: 2026 is a partial year (window ends 2026-10-23); relative-share trends are the primary model because total canine output grew. Categories with fewer than 20 articles are not fitted (CAR 18, END 14, NEU 8, PUL 7). A rate ratio interval that includes 1 is "no detectable change in this index", not "stable literature".
- Pearson residuals below -2 are a screening rule, not a significance test; the permutation p value is the formal test of the whole grid.
- Do not describe any category as "neglected" or "fading" in the literature; the grids describe this index only.

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md` (conventions), this file, `core/CLAUDE.md` (querying rules), `docs/core-tables.md` (articles.jsonl field list), `search-log.md` (the review window and run section, for the caveat text). Do not read `index.md`, `research-map.md` or `data/syndromes/mentions.jsonl`.

2. **Tidy.** Not applicable. No tidy file is written.

3. **Script.** Create `scripts/experiment_gaps.py` in `core/`. Module docstring with: inputs (`articles.jsonl`), outputs (`data/experiments/EXP12-CORPUS-gaps.json`), the exact run command below, and the statement "numpy only; no scipy or statsmodels". Implement the functions listed in Section 3. Do not add anything to `scripts/requirements-experiments.txt` (numpy is already listed). Confirm numpy first:
   `.venv/Scripts/python.exe -I -c "import numpy; print(numpy.__version__)"`

4. **Run.** From `core/`:
   `.venv/Scripts/python.exe -I scripts/experiment_gaps.py --code EXP12-CORPUS-gaps --seed 20261105 --permutations 5000`
   Expected runtime: under 1 minute (grid permutations are 4 x 5000 chi-square recomputations on 444 rows; the trend permutations are 7 x 5000 Spearman statistics).
   Sensitivity run (optional, writes the same file name, so run it first to a copy or note its result in `run_notes` only): add `--exclude-reviews` and record the key counts (404 articles; gap-cell count) in `run_notes`. Re-run the default afterwards so the committed file is the default run.

5. **Load.** From the repository root, run the console once to load datasets and experiments:
   `dotnet run --project console/Babesiosis.Console -- --datasets-only`
   Check `ReviewRoot` in `appsettings.json` points at `core/`. Then SQL check via the `babesiosis-local-db` MCP:
   `SELECT experiment_code, method, dataset_code FROM dbo.experiment WHERE experiment_code = 'EXP12-CORPUS-gaps';` and `SELECT kind, sort_order FROM dbo.experiment_result WHERE experiment_code = 'EXP12-CORPUS-gaps' ORDER BY sort_order;` (expect 7 rows: interpretation, grids, gap_cells, cohort_adjusted_counts, trends, normalisation_log, run_notes, with sort orders 0 to 6). Check the column names against `docs/database.md` before running.

6. **Verify.** Run the Section 5 checks. The reproduction check (5.6) is a second run with the same seed, compared with `fc` or a Python comparison of the payloads.

7. **Document.** Add a row for `scripts/experiment_gaps.py` to `scripts/README.md` and a row for `EXP12-CORPUS-gaps` to the experiment table in `docs/database.md`. Update the EXP12 status on the `docs/ml-experiment-plan.html` card if that page is kept.

8. **Optional.** A heatmap view for the four grids in `webapp/Babesiosis.Web/src/app/modules/experiments/views/`, only after steps 1 to 7 pass. The experiment is complete without it.

## 8. Open questions

1. Reviews (`include_type` = review, 40 articles): included by default. Default if nobody answers: included, with the `--exclude-reviews` sensitivity recorded in `run_notes`.
2. Country mapping: the keyword list covers only the eight countries with 10 or more articles plus `Other`. Default: keep it; a fuller ISO mapping would need a human decision on multi-country strings.
3. Species mapping of subspecies notation (`B. canis rossi` to B. rossi, `B. canis vogeli` to B. vogeli). Default: as in Section 2.3, recorded per raw value so a reviewer can change it.
4. Whether `Babesia sp.` and `mixed/unspecified` should be a separate level from `other/mixed`. Default: no, reported as a sub-count in `normalisation_log`.
