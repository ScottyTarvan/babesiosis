# EXP08 SEV evidence: severity evidence matrix and meta-analysis

| Field | Value |
|---|---|
| Experiment code | `EXP08-SEV-evidence` |
| Layer | 2 pooled or evidence table |
| Method token | `evidence` (goes in `experiment.method`) |
| Dataset(s) | `null`: the input is the article-level extraction table `data/severity/associations.csv`, not a tidy per-dog dataset. `associations[]` and `cluster_assignments[]` are therefore written as empty lists (README: they need a dataset). |
| Readiness | ready (pilot table of 10 articles exists; the same script runs unchanged on the full table that EXP13 stage 1 produces) |
| Python environment | `.venv-nlp` (numpy 1.26.4, scipy 1.17.1 installed; scipy gives `stats.t.ppf`, `stats.norm.ppf`, `stats.binomtest`, `cluster.hierarchy`). `.venv` (numpy 2.5.4, networkx 3.7, no scipy) cannot run it. `.venv-nlp` has no `pip`; do not install anything. Add `scipy>=1.11` to `scripts/requirements-experiments.txt` with the comment `EXP08 needs .venv-nlp` if it is not there. No statsmodels (not installed in either environment): DerSimonian-Laird and Hartung-Knapp are implemented by hand (formulas in section 3). |
| Estimated build effort | medium (about 3 to 4 hours of agent work; the statistic-string parser for medians and IQRs is the fiddly part) |
| Suggested model for the building agent | opus: many small judgement rules (collapse order, effect orientation, parsing of free-text statistics) that must be implemented exactly and checked against the source rows |
| Depends on | `data/severity/associations.csv`, `data/severity/marker_map.csv`, `articles.jsonl`, `cohorts.json`. No other experiment. EXP13 stage 1 later replaces `associations.csv` with the full-corpus table; re-run this experiment then with the same command. |

## 1. Question and hypotheses

Questions:

1. Which markers are consistently associated with severity or death across independent study populations and *Babesia* species, which disagree, and which were tested only once?
2. Where several populations report a comparable effect size for the same marker and outcome class, what is the pooled effect, how heterogeneous is it, and what range would a new population be expected to show (prediction interval)?

Named hypotheses (directions relative to the worse outcome; they are checks on the evidence, not things to prove):

- H1: lower haematocrit/PCV goes with death. The `Haematocrit/PCV` x `mortality` cell is the only cell in the pilot with 4 independent study units (CB040, CB145/CB050 = CH03, CB238, CB263 = CH18 are candidates); expect a majority of `lower_in_severe` votes.
- H2: oxidative-stress markers (`Malondialdehyde / TBARS`, `Superoxide dismutase`, `Catalase`, `Glutathione / glutathione peroxidase`, `Total antioxidant capacity`) form one association-profile cluster (they come from the same two article groups in the pilot).
- H3: species changes the picture: *B. rossi* rows (127 of 275 pilot rows) show more significant associations with mortality than *B. canis* rows, because *B. rossi* populations are larger and more severe (CB040, n = 320).

Negative findings that count as results: no marker cell reaches three independent study units (expected in the pilot: only 2 cells do); pooled estimates whose prediction interval crosses zero; species-split votes that point in opposite directions. All three are reported, not hidden.

## 2. Data

### 2.1 Sources

- `data/severity/associations.csv`: 275 rows (the plan card in `docs/ml-experiment-plan.html` says 290; the file has 275, re-count at run time), 10 articles: CB006 45, CB017 28, CB040 78, CB050 5, CB053 13, CB141 17, CB145 31, CB202 16, CB238 11, CB263 31. Columns (exact): `id, row, cohort, article_species, severity_key, outcome_class, complication, severity_label, marker_as_reported, marker_extracted, marker, marker_class, map_status, specimen, timepoint, species, species_confirmation, subgroup, n_total, n_severe, n_comparison, analysis, direction, significant, statistic, p_value, effect_type, effect_value, effect_ci, cutoff, sensitivity, specificity, adjusted_for, source_type, location, confidence, quote_check, numbers_missing, errors, note, quote`. Built by `scripts/check_associations.py` from `data/severity/extractions/<ID>.json`; field definitions in `data/severity/association_schema.json`.
- Distinct values in the pilot (use these spellings; the full table may add more, so code must not assume the list is closed):
  - `outcome_class`: `mortality` 149, `complicated` 41, `anaemia_grade` 29, `other` 24, `severity_grade` 17, `organ_dysfunction` 15 (schema also allows `specific_complication`, `treatment_intensity`, `parasitaemia_level`).
  - `analysis`: `group_comparison` 201, `correlation` 25, `univariable_regression` 17, `roc` 14, `descriptive_only` 11, `proportion_comparison` 7 (schema also allows `multivariable_regression`, `survival_analysis`).
  - `direction`: `higher_in_severe` 95, `lower_in_severe` 70, `positive_association` 41, `no_difference` 35, `negative_association` 17, `more_frequent_in_severe` 10, `not_stated` 3, `mixed` 3, `less_frequent_in_severe` 1.
  - `significant`: `yes` 130, `no` 116, `not_tested` 19, `unclear` 10.
  - `effect_type`: blank 214, `rho` 19, `OR` 17, `AUC` 14, `other` 5 (Kendall tau-b), `mean_difference` 5, `median_difference` 1 (schema also allows `HR`, `RR`, `r`).
  - `confidence`: `high` 231, `medium` 36, `low` 8.
  - `quote_check`: `exact` 275 (checker can also give `near`, `partial`, `not_found`).
  - `numbers_missing`: blank in all 275 rows. `errors`: blank in all rows. `map_status`: `canonical` 273, `pattern` 2.
  - `species`: `B. rossi` 127, `B. canis canis` 45, `B. canis` 45, `unspecified` 31, `mixed (B. vogeli, B. gibsoni)` 16, `Babesia spp. (unspecified)` 11.
  - `severity_key`: `S1` 207, `S2` 29, `S3` to `S9` 5 each (CB006 has nine definitions).
  - `cohort`: blank 175, `CH03` 36 (CB050 and CB145, same dogs), `CH18` 31, `CH12` 17, `CH08` 16.
  - `subgroup`: blank 265, `anaemic dogs` 10.
  - `timepoint`: 11 values, mostly admission (`admission, before any treatment`, `admission/pre-treatment`, `admission (before treatment)`, `admission (within 2 h of presentation)`, `admission/pre-treatment (T0)`, `presentation`, `admission`, `first B. canis PCR-positive sample, before imidocarb or other treatment`, `day 1 (admission, 6-8 h after imidocarb)`), plus `day 7 (6 days after imidocarb)` 10 and `history at presentation` 4.
  - `source_type`: `table` 161, `text` 113, `figure` 1 (schema also allows `abstract`).
  - `statistic` formats seen: `median 0.17 (IQR 0.15–0.24) vs 0.18 (0.17–0.23) U/mL, ...; Mann-Whitney U` (severe group first), `median 58,446.62 (IQR 38,885.96–74,709.27) vs ...` (thousands commas), `mean 5.83±3.56 vs 4.31±2.81 years`, `39.4 ± 0.2 vs 39.2 ± 0.1 °C; ... mean ± (SD or SE, not stated)`, `AUC 0.906 (SE 0.02)`, `Spearman rho −0.559` (Unicode minus U+2212), `OR for death 1.39 for every 1 °C decrease (n=320)`, `14/25 (56%) complicated vs 2/10 (20%) uncomplicated`. 144 rows mention median or IQR, 39 mention mean or SD.
  - `effect_ci` formats: `1.16-1.67`, `8.77- infinity`.
- Pilot density (for expectations): 82 distinct markers, 126 marker x outcome-class cells, 23 cells with 2 or more independent study units, 2 cells with 3 or more (`Haematocrit/PCV` x `mortality` 4, `Age` x `mortality` 3), 53 markers seen in only one study unit. No OR, AUC or rho cell has two study units, so in the pilot the meta-analysis will mostly be SMDs from medians and IQRs, and most `meta_analysis` entries will be `k < 2` (not pooled). That is the expected pilot result.
- `data/severity/marker_map.csv`: 399 rows, columns `alias, marker, marker_class, pattern, cui, source, note, articles`. `source` is `seed` (159 rows, the canonical markers, each with a `pattern`) or `scispacy` (240 alias rows, 162 with blank `marker`). `marker_class` values: `biochemistry`, `haematology`, `urine`, `endocrine`, `cardiac`, `acid-base and perfusion`, `endothelial`, `coagulation`, `cytokine`, `immunology`, `parasitology`, `clinical sign`, `acute phase protein`, `electrolyte`, `oxidative stress`, `clinical score`, `clinical history`, `signalment`, `imaging`, `omics`, `treatment`, blank.
- `articles.jsonl` (481 records): `id`, `scope_label` (`core canine evidence` 404, `canine review` 40, `human comparator` 27, `background` 10), `species_short`, `cohort_id`, `first_pub_date`, `primary_category`. Only `CB` IDs may contribute; drop any `HU`/`BG` row and any row whose article `scope_label` is not `core canine evidence`, and record the drop.
- `cohorts.json`: dict `CH01`... (38 cohorts; `certainty` `probable` 35, `confirmed` 3), each with `label`, `certainty`, `basis`, `members` (article IDs). `CH03` members: CB008, CB050, CB145, CB504, CB513, CB517.
- Licence: the extraction table is this project's own derived data (quotes are short verbatim excerpts). No dataset licences or independent-source letters apply; independence is decided by `cohort` (section 2.3).

### 2.2 Tidy file required

Not applicable. The input is already one flat table. The script does all normalisation in memory and records every rule in `run_notes`.

### 2.3 Variables and filters

Applied in this order; every dropped row goes into `run_notes.dropped` with `id`, `row`, `marker`, `reason`.

1. **Scope.** Keep rows whose `id` starts with `CB` and whose article `scope_label` is `core canine evidence`.
2. **Quote check.** Keep `quote_check` in `--quote-ok` (default `exact,near`). `partial` and `not_found` rows are dropped as unverified.
3. **Errors.** Drop rows with a non-blank `errors`.
4. **Canonical marker.** `marker` is already the canonical name when `map_status` is `canonical` or `pattern`. Re-check every `marker` against the canonical set (`marker_map.csv` rows with `source = seed`, or `source = manual` with a non-blank `pattern`); if a `marker` is not canonical, look up `marker_as_reported` then `marker` (lowercased) in the `alias` column and take that row's `marker`; if still unmapped or the mapped `marker` is `-`, drop with reason `unmapped marker`. Take `marker_class` from the canonical row, not from the CSV.
5. **Marker part of the definition.** If `note` contains `part of the severity definition` (1 pilot row), drop it from the matrix and pooling by default (`--keep-definitional` keeps it, flagged).
6. **Usable result.** Rows with `analysis = descriptive_only` or `significant` in `not_tested, unclear` stay in the evidence matrix as `untested` but give no vote and no pooled estimate.
7. **Confidence tiers.** `confidence = high` rows feed the pooled estimates. `medium` rows feed the matrix and the vote counts, flagged. `low` rows (8) are shown only in a separate `low_confidence` list inside `evidence_matrix`; they never vote or pool. Rows with non-blank `numbers_missing` behave like `medium` for voting and are excluded from pooling. Rows with `source_type = abstract` (none in the pilot; produced by EXP13 stage 1) vote with weight multiplied by `--abstract-weight` (default 0.5) and never pool.
8. **Species group.** Map `species` (lowercased) by first match:
   - contains `rossi` -> `B. rossi`
   - contains `canis` and not `vogeli` -> `B. canis` (covers `B. canis`, `B. canis canis`)
   - contains `gibsoni` or `vogeli` -> `B. gibsoni / B. vogeli` (covers `mixed (B. vogeli, B. gibsoni)`)
   - otherwise -> `unspecified` (covers `unspecified`, `Babesia spp. (unspecified)`, `mixed`)
   The mapping and its counts go into `run_notes.species_groups`.
9. **Outcome cell.** The outcome column is `outcome_class`; for `specific_complication` it is `specific_complication: <complication>` (lowercased complication).
10. **Timepoint class.** `admission` when `timepoint` matches `--admission-regex` (default `admission|presentation|pre-?treatment|before (any )?treatment|\bT0\b|first .*sample|history at presentation|^$`, case-insensitive; blank counts as admission), else `later`. `later` rows (10 in the pilot, all `day 7 (6 days after imidocarb)`) are kept only when a cell has no admission row for that study unit.

**Study unit and collapse.** The study unit is `cohort` when non-blank, else the article `id` (so CB050 and CB145 are one unit, `CH03`). Collapse to one row per study unit x canonical marker x outcome cell x species group, choosing by this priority (first rule that separates the candidates wins):

1. timepoint class `admission` before `later`;
2. blank `subgroup` before a subgroup;
3. `analysis` in this order: `group_comparison`, `proportion_comparison`, `univariable_regression`, `roc`, `correlation`, `survival_analysis`, `multivariable_regression`, `descriptive_only` (the univariable between-group test is the most comparable across articles);
4. `significant` in `yes, no` before `not_tested, unclear`;
5. `confidence` high, medium, low;
6. lowest `severity_key` number (the article's primary definition);
7. largest `n_total`;
8. earliest article `first_pub_date`, then `id`, then `row`.

The kept row is the "representative" row of the cell. Rows not kept are listed in `run_notes.collapsed` with the key of the row that replaced them. For pooling, a separate selection is made per effect family (section 3 step 3) with the same priority but restricted to rows that yield that family, so a cell can contribute an SMD from its group comparison and an AUC from its ROC row.

## 3. Method

All randomness uses `numpy.random.default_rng(seed)` with `seed` from parameters (default `20261105`). The run is deterministic apart from the bootstrap in step 7, which is seeded.

1. **Load and filter** as in section 2.3. Store counts at each filter step in `run_notes.filter_counts`.

2. **Evidence matrix.** For each marker x outcome cell, from the representative rows (all study units and all species groups together; species splits in step 8):
   - `sign` of each representative row: `+1` if `direction` in `higher_in_severe, more_frequent_in_severe, positive_association`; `-1` if in `lower_in_severe, less_frequent_in_severe, negative_association`; `0` if `no_difference`; `null` for `mixed, not_stated`.
   - `status` per row: `sig_worse_high` (sign +1, significant yes), `sig_worse_low` (sign -1, significant yes), `ns` (significant no), `untested` (not_tested, unclear, descriptive_only), `unclear_direction` (significant yes, sign null).
   - cell summary: counts of each status in study units, `k_units`, `articles`, `species_groups`, `consensus` = `consistent_high` if all tested units are `sig_worse_high` or `ns` with at least one `sig_worse_high` and none `sig_worse_low`; `consistent_low` symmetrically; `conflicting` if both `sig_worse_high` and `sig_worse_low` occur; `null_only` if all tested are `ns`; `untested_only` otherwise.
   - Matrix ordering: rows by `marker_class` then marker; columns in the order `mortality, complicated, organ_dysfunction, specific_complication: *, severity_grade, anaemia_grade, parasitaemia_level, treatment_intensity, other`.

3. **Effect sizes per comparable family.** One estimate per study unit per marker x outcome cell per family, from `confidence = high` rows only, with `numbers_missing` blank and `source_type` not `abstract`. Parse numbers after replacing U+2212 with `-`, en and em dashes between numbers with `-`, removing thousands commas (a comma followed by exactly three digits), and decimal commas (`0,05` -> `0.05`). All estimates are oriented so that a positive value means "higher marker value, or presence of the finding, goes with the worse outcome".
   - **`log_or`** (`effect_type = OR`, `analysis` in `univariable_regression, proportion_comparison`): `y = ln(OR)`, `se = (ln(hi) - ln(lo)) / (2 * 1.959964)` from `effect_ci` (two numbers split on `-`, `to`, `,` or `;`). Skip with reason when the CI is missing, unparsable or open (`infinity`). Orientation: if `statistic` or `note` contains `decrease`, `lower`, `per 1 .* less` or `reference: .*higher`, multiply `y` by -1 and record it. ORs are comparable only on the same scale: build `scale_key` from `statistic` (the text after `for every`/`per` up to the next `(` or `;`, lowercased, digits kept, e.g. `1 °c decrease` -> `1 °c`); for continuous markers pool only estimates with identical `scale_key`; for `proportion_comparison` and categorical markers (`marker_class` in `clinical sign, signalment, clinical history, treatment`) `scale_key = binary`. Multivariable ORs (`analysis = multivariable_regression`) form a separate family `log_or_adjusted`, pooled only if `--pool-adjusted` (default off; listed otherwise).
   - **`smd`** (Hedges' g) from `group_comparison` rows whose `statistic` gives both groups:
     - medians and IQR (`median m1 (IQR a1-b1) vs m2 (a2-b2)`), with `n_severe` = n1 and `n_comparison` = n2: estimate mean and SD by Wan et al. (2014) scenario 3: `mean = (a + m + b) / 3`, `sd = (b - a) / (2 * norm.ppf((0.75 n - 0.125) / (n + 0.25)))`.
     - medians and range (`range lo-hi`): Wan scenario 1 (`mean = (lo + 2m + hi) / 4`, `sd = (hi - lo) / (2 * norm.ppf((n - 0.375) / (n + 0.25)))`) only with `--allow-range` (default off).
     - means with SD (`mean x ± s`, or `x±s` where the row or `note` says SD): used directly. When the text says SD or SE is not stated (`SD or SE, not stated` occurs in the pilot), skip with reason `sd_or_se_unstated` unless `--assume-sd` (default off).
     - Group order: the first group in `statistic` is the severe group if the text after the numbers names the severe group first (match the `severity_label` words, e.g. `non-survivors`, `complicated`, `one complication`), which is the guide's convention. Then `d = (mean1 - mean2) / s_pooled`, `s_pooled = sqrt(((n1-1) sd1^2 + (n2-1) sd2^2) / (n1 + n2 - 2))`, `J = 1 - 3 / (4 (n1 + n2) - 9)`, `g = J d`, `var = (n1 + n2) / (n1 n2) + g^2 / (2 (n1 + n2))`.
     - **Sign check.** If the row's `significant = yes` and `sign(g)` disagrees with the row's `sign`, drop the estimate with reason `sign_conflict` (usually a reversed group order) and list it for review. Skip when `n_severe` or `n_comparison` is blank or either is below 2.
   - **`logit_auc`** (`effect_type = AUC`, `analysis = roc`): `y = logit(AUC)`; SE from `statistic` (`SE x`) when given, else Hanley-McNeil (1982) from `n_severe` (positives) and `n_comparison`: `Q1 = A/(2-A)`, `Q2 = 2A^2/(1+A)`, `se_A = sqrt((A(1-A) + (n1-1)(Q1-A^2) + (n2-1)(Q2-A^2)) / (n1 n2))`; then `se = se_A / (A (1 - A))`. AUC is not oriented (already relative to the worse outcome). Back-transform pooled values with the inverse logit.
   - **`fisher_z`** (`effect_type` in `r, rho`, `analysis = correlation`): `y = atanh(r)`, `se = 1 / sqrt(n_total - 3)`. Pearson and Spearman are pooled together and flagged; Kendall tau (`effect_type = other`) is not pooled.
   - Medians, IQRs, and all derived means and SDs are stored per estimate (`inputs`) so a reader can check the conversion.

4. **Random-effects meta-analysis** per marker x outcome cell x family, when `k` (study units with an estimate) is at least `--min-k-pool` (default 2):
   - Fixed weights `w_i = 1 / v_i`; `Q = sum w_i (y_i - y_FE)^2`; DerSimonian-Laird `tau2 = max(0, (Q - (k-1)) / (sum w_i - sum w_i^2 / sum w_i))`; random weights `w*_i = 1 / (v_i + tau2)`; `mu = sum w*_i y_i / sum w*_i`; `se_DL = sqrt(1 / sum w*_i)`.
   - CI: for `k >= --hk-min-k` (default 3) use Hartung-Knapp-Sidik-Jonkman: `q = sum w*_i (y_i - mu)^2 / (k - 1)`, `se_HK = sqrt(q / sum w*_i)`, CI `mu ± t_{k-1, 0.975} se_HK` (no truncation of `q`; record `q`). For `k = 2` use the DL normal CI `mu ± 1.959964 se_DL` and flag `ci_method = "DL_normal_k2"`.
   - `I2 = max(0, (Q - (k-1)) / Q)` (0 when `Q = 0`), `Q` and its chi-square p value (`scipy.stats.chi2.sf`).
   - Prediction interval (Higgins, Thompson and Spiegelhalter 2009) for `k >= 3`: `mu ± t_{k-2, 0.975} sqrt(tau2 + se_DL^2)`; null for `k < 3`.
   - Report on the analysis scale and back-transformed (`OR`, `AUC`, `r`; SMD stays as g).
   - `confidence = medium` rows are not pooled; a sensitivity pool including them is reported as `sensitivity_with_medium` when it changes `k`.
   - Studies with `k = 1` are listed with their single estimate and CI but `pooled = null`.
   - Multiple testing: the p values of the pooled estimates (`2 * t.sf(|mu / se|, k-1)` for HK, normal for k = 2) are BH-adjusted across all pooled analyses in the run (family = every pooled marker x outcome x family in the overall analysis; the species-split pools form their own family).

5. **Vote counting weighted by sample size.** Per marker x outcome cell, from representative rows that are tested (`significant` yes or no, sign not null):
   - `w = n_total` (blank `n_total` -> `n_severe + n_comparison`; if still blank, `w` = median `n_total` of that outcome class, flagged `n_imputed`); multiply by `--abstract-weight` for abstract rows and by 0.5 for `medium` confidence rows (`--medium-weight`, default 0.5).
   - `score = sum(w * s) / sum(w)` where `s = +1` for `sig_worse_high`, `-1` for `sig_worse_low`, `0` for `ns`. Also unweighted counts.
   - Sign test across significant votes only: `scipy.stats.binomtest(n_high, n_high + n_low, 0.5)`, two-sided; BH across all cells with at least 2 significant votes. Labelled exploratory: vote counting ignores effect size and power.

6. **Marker clusters on association profiles.** Markers with at least `--cluster-min-cells` (default 2) tested cells. Each marker's profile is the set of features `"<outcome cell>|<species group>|<status>"` with status in `high` (score > 0.33), `low` (score < -0.33), `null` (otherwise, tested). Distance = Jaccard distance between feature sets (`--cluster-distance jaccard`; alternative `correlation`: Pearson correlation distance on the signed score vector over cells tested by both markers, set to 1 when fewer than 2 shared cells). Average linkage (`scipy.cluster.hierarchy.linkage(method="average")` on the condensed matrix), cut at `--cluster-cut` (default 0.7). Clusters of size 1 are reported as singletons.
   - Stability (step 7).

7. **Cluster stability.** `--bootstrap` (default 200) resamples of study units with replacement (seeded), recompute profiles and clusters; for every pair of markers in the same cluster in the full data, the fraction of resamples where they are still together. Report each cluster's mean co-clustering rate. Clusters below 0.5 are labelled unstable.

8. **Species split.** Repeat steps 2 to 7 inside each species group with at least one row. BH families for the species-split pools are per species group. Add a comparison table: for every marker x outcome cell tested in 2 or more species groups, the per-species `score` and pooled estimates side by side, and `species_disagree = true` when one species has `score > 0.33` and another `< -0.33`.

9. **Single-study markers.** Every canonical marker whose tested rows come from exactly one study unit (after collapse, over all outcome cells and species) is listed with that unit, the outcome cells, the species, `n_total`, the result, and the row's quote location. These are explicit evidence gaps. A second list: marker x outcome cells with exactly one study unit, for markers that have more than one unit elsewhere.

10. **Interpretation and run notes** (section 4.1).

No predictive modelling; no permutation test is needed because no p value here comes from a distributional assumption on per-dog data.

## 4. Outputs

### 4.1 Experiment JSON

`data/experiments/EXP08-SEV-evidence.json`.

`experiment`:

- `code` `EXP08-SEV-evidence`; `name` `Severity evidence matrix and meta-analysis`; `description` one sentence naming the table and the number of articles; `method` `evidence`; `dataset` `null`.
- `parameters` (all defaults):

```json
{
  "seed": 20261105,
  "input": "data/severity/associations.csv",
  "n_articles_in_input": 10,
  "quote_ok": ["exact", "near"],
  "pool_confidence": ["high"],
  "vote_confidence": ["high", "medium"],
  "medium_weight": 0.5,
  "abstract_weight": 0.5,
  "keep_definitional": false,
  "admission_regex": "admission|presentation|pre-?treatment|before (any )?treatment|\\bT0\\b|first .*sample|history at presentation|^$",
  "study_unit": "cohort_else_article",
  "analysis_priority": ["group_comparison", "proportion_comparison", "univariable_regression", "roc", "correlation", "survival_analysis", "multivariable_regression", "descriptive_only"],
  "families": ["log_or", "smd", "logit_auc", "fisher_z"],
  "pool_adjusted": false,
  "smd_method": "wan2014_iqr",
  "allow_range": false,
  "assume_sd": false,
  "min_k_pool": 2,
  "hk_min_k": 3,
  "pi_min_k": 3,
  "ci_level": 0.95,
  "adjustment": "benjamini_hochberg",
  "alpha": 0.05,
  "vote_threshold": 0.33,
  "cluster_min_cells": 2,
  "cluster_distance": "jaccard",
  "cluster_linkage": "average",
  "cluster_cut": 0.7,
  "bootstrap": 200
}
```

- `script` `scripts/experiment_evidence.py`; `script_version` first 12 hex characters of the SHA-256 of the script (as in EXP01); `run_utc`.
- `n_subjects` = number of independent study units contributing at least one kept row (pilot: 9, because CB050 and CB145 are both CH03); `n_variables` = number of canonical markers in the matrix; `n_tests` = number of pooled analyses plus number of vote sign tests (overall, not species-split).
- `summary`: one paragraph with articles, study units, rows kept, markers, cells, cells with 3 or more units, number pooled, number of single-study markers.

`associations`: `[]`. `cluster_assignments`: `[]` (no dataset; marker clusters are in `results`).

`results[]`:

| kind | title | sort_order | payload |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | `{"sections": [{"heading", "paragraphs": [..]}]}` |
| `evidence_matrix` | Marker by outcome-class evidence matrix | 1 | see below |
| `vote_counts` | Vote counts weighted by sample size | 2 | see below |
| `meta_analysis` | Random-effects meta-analysis per marker | 3 | see below |
| `marker_clusters` | Markers with similar association profiles | 4 | see below |
| `single_study_markers` | Markers tested in only one study population (evidence gaps) | 5 | see below |
| `species_split` | Results split by Babesia species | 6 | see below |
| `run_notes` | Rows included, collapsed, dropped and skipped | 7 | see below |

Payload schemas (small examples; real values come from the run):

- `evidence_matrix`:
  ```json
  {"markers": [{"marker": "Haematocrit/PCV", "marker_class": "haematology"}],
   "outcomes": ["mortality", "complicated"],
   "cells": [{"marker": "Haematocrit/PCV", "outcome": "mortality", "k_units": 4,
              "sig_worse_high": 0, "sig_worse_low": 2, "ns": 1, "untested": 1, "unclear_direction": 0,
              "consensus": "consistent_low", "species_groups": ["B. rossi", "unspecified"],
              "units": [{"unit": "CH03", "articles": ["CB145"], "row": 12, "status": "ns", "n_total": 87,
                         "analysis": "group_comparison", "confidence": "high", "species_group": "B. rossi"}]}],
   "low_confidence": [{"id": "CB040", "row": 51, "marker": "...", "outcome": "...", "reason": "confidence low"}]}
  ```
- `vote_counts`: `{"cells": [{"marker", "outcome", "n_votes", "n_high", "n_low", "n_ns", "weight_sum", "score", "score_unweighted", "sign_test_p", "p_adjusted", "n_imputed": 0}]}`, sorted by `|score|` then `weight_sum` descending.
- `meta_analysis`: `{"analyses": [{"marker", "outcome", "family": "smd", "k": 3, "units": ["CH03", "CB040", "CH18"], "articles": ["CB145", "CB040", "CB263"], "estimates": [{"unit", "article", "row", "y", "se", "inputs": {"m1": 4.3, "q1_1": 1.7, "q3_1": 10.8, "n1": 40, "m2": 2.2, "...": "..."}}], "pooled": -0.62, "ci_low": -1.10, "ci_high": -0.14, "ci_method": "HKSJ", "q_hk": 1.4, "tau2": 0.05, "i2": 0.31, "q": 2.9, "q_p": 0.23, "pi_low": -2.9, "pi_high": 1.7, "p": 0.03, "p_adjusted": 0.21, "scale": "g", "pooled_back": null, "sensitivity_with_medium": null}], "not_pooled": [{"marker", "outcome", "family", "k": 1, "estimate", "reason": "k < 2"}], "skipped_estimates": [{"id", "row", "family", "reason": "sd_or_se_unstated"}]}`. One entry per marker x outcome x family. This list carries the forest-plot data (per-unit `y`, `se` plus pooled and PI).
- `marker_clusters`: `{"distance": "jaccard", "cut": 0.7, "clusters": [{"label": "C1", "markers": [...], "stability": 0.82, "stable": true, "shared_features": ["mortality|B. rossi|high"]}], "singletons": [...], "merges": [[i, j, height, size]], "markers_excluded": [{"marker", "reason": "fewer than 2 tested cells"}]}`.
- `single_study_markers`: `{"markers": [{"marker", "marker_class", "unit", "articles", "outcomes", "species_groups", "n_total", "results": [{"outcome", "status", "location"}]}], "single_unit_cells": [{"marker", "outcome", "unit", "article", "status"}]}`.
- `species_split`: `{"groups": {"B. rossi": {"n_units", "n_rows", "evidence_matrix": {...same shape, cells only}, "vote_counts": {...}, "meta_analysis": {...}, "marker_clusters": {...}}, "B. canis": {...}}, "comparison": [{"marker", "outcome", "scores": {"B. rossi": -0.8, "B. canis": 0.0}, "species_disagree": false}]}`.
- `run_notes`: `{"filter_counts": {"input": 275, "scope": 275, "quote_ok": 275, "errors": 275, "mapped": 275, "definitional": 274, "kept": 266}, "dropped": [{"id", "row", "marker", "reason"}], "collapsed": [{"id", "row", "kept_id", "kept_row", "reason": "later timepoint"}], "species_groups": {"B. canis canis": "B. canis"}, "orientation_flips": [{"id", "row", "reason"}], "sign_conflicts": [...], "pilot": true, "n_articles": 10, "cohort_merges": {"CH03": ["CB050", "CB145"]}}`. `pilot` = true when fewer than 50 articles are in the input.

Interpretation sections (headings in this order; plain language for a veterinary reader, numbers included):

1. `Question` — what was asked, in two sentences.
2. `What was done` — the table, the filters, the collapse to study populations, the meta-analysis methods and why vote counting is used where effect sizes are not comparable.
3. `Main findings` — cells with consistent results across 2 or more populations, pooled estimates with CI and prediction interval, H1 and H3 outcomes.
4. `Where the evidence disagrees` — conflicting cells and species disagreements.
5. `Markers that behave alike` — clusters and their stability, H2.
6. `Single-study markers` — the count, the classes they come from, and that these are gaps in the extracted evidence.
7. `Limits` — section 6 text, including the pilot status.

### 4.2 Other artefacts

None. Forest plots and the heatmap are drawn from the `meta_analysis` and `evidence_matrix` payloads by the web app's JSON view (or a later dedicated view). Nothing is written outside `data/experiments/`.

## 5. Acceptance checks

1. `.venv-nlp/Scripts/python.exe -I scripts/experiment_evidence.py --help` lists every parameter in 4.1.
2. The JSON has the four top-level keys; `associations` and `cluster_assignments` are empty lists; `results` has the eight kinds above, one `interpretation` and one `run_notes`.
3. Counts: `run_notes.filter_counts.input` equals the row count of `associations.csv` (275 for the pilot); kept + dropped = input; `n_subjects` = 9 for the pilot (10 articles, CB050 and CB145 merge into CH03). Re-run the count with `python -I` and compare.
4. Reproducibility: run twice with the default seed; the two files are identical except `run_utc` (compare with a small `python -I` script that removes `run_utc` and diffs the JSON).
5. Meta-analysis unit test inside the script (`--self-test`): DL and HKSJ on the textbook example of 3 studies `y = [0.1, 0.3, 0.5]`, `v = [0.04, 0.02, 0.05]` give `tau2 = 0` and the fixed-effect estimate; a second set with heterogeneity `y = [-0.5, 0.2, 0.9]`, `v = [0.02, 0.02, 0.02]` gives `tau2 = 0.47` (Q = 49, check by hand in the docstring) and `I2` about 0.96. Wan conversion: median 10, IQR 6 to 14, n = 40 gives mean 10.0 and sd about 6.15 (`8 / (2 * 0.6503)`). Hanley-McNeil: AUC 0.8, n1 = n2 = 20 gives se about 0.071.
6. Sign check: no pooled SMD estimate disagrees in sign with a significant row's `direction`; the `sign_conflicts` list is printed and each one inspected by reading the quote.
7. Spot check against the source: for 5 random kept rows (seeded), print `id`, `row`, `quote` and the derived status or estimate, and confirm by eye. For `Haematocrit/PCV` x `mortality`, list the units and confirm that CB050 and CB145 do not both count.
8. Load: the console loads the file; `dbo.experiment` has one row for `EXP08-SEV-evidence` with `method = 'evidence'` and `dbo.experiment_result` has 8 rows for it.
9. The interpretation names the pilot status and says that most cells have one population.

## 6. Caveats and reporting language

- **Pilot.** The current table covers 10 of the 404 core canine articles, chosen from the top of `data/severity/shortlist.csv`. Results describe these 10 articles only and say so in the first paragraph of `Main findings`. Scaling: when EXP13 stage 1 extends the extraction to every canine article, `scripts/check_associations.py` rewrites `associations.csv` with the same columns; re-running this experiment with the same command needs no code change. Only `n_articles_in_input` and `run_notes.pilot` change, and more cells reach `k >= 3`. Nothing in the script may hard-code pilot article IDs, marker names or counts.
- **Non-independence.** Articles sharing a `cohort` are one population; 35 of the 38 cohorts in `cohorts.json` are `probable`, not confirmed, so the merge can be wrong in both directions. Multiple outcome definitions and markers from one article are correlated; the per-cell collapse keeps one row per population but does not model the correlation across cells.
- **Comparability.** SMDs from medians and IQRs assume roughly normal data (Wan et al. warn about skew); ORs per unit are pooled only on the same scale; outcome classes group different definitions (for example `complicated` in CB017 and CB053 are defined differently). State this next to every pooled estimate.
- **Extraction confidence.** All rows came from one LLM extraction with automatic quote and number checks; there was no double human extraction. `medium` and `low` rows are shown separately.
- **Species.** Never pooled silently; the overall analysis is shown next to the species split, and `unspecified` is a group, not a species.
- **Vote counting** ignores effect size and statistical power; a `ns` vote from a small study is weak evidence of no effect. Say "was not significantly associated in", never "is not associated with".
- **Wording.** Clusters are "markers with similar reported association profiles", not biological pathways. Pooled estimates are summaries of reported associations, not prognostic scores, and nothing here is clinically usable as a cut-off. Single-study markers are gaps in the extracted evidence, not necessarily gaps in the literature.

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md`, `TEMPLATE.md`, `core/CLAUDE.md`, this spec, `scripts/experiment_pairwise.py` (docstring, `bh_adjust`, argparse, output assembly, `script_version` hash, `interpretation()`), `scripts/check_associations.py` (docstring and `load_map`, `map_marker` for the alias lookup), `data/severity/association_schema.json`, `data/severity/EXTRACTION_GUIDE.md`, and 10 rows of `data/severity/associations.csv` with `python -I`. Done: you can state the study unit of each of the 10 pilot articles.
2. **Tidy.** Not applicable.
3. **Script.** Write `scripts/experiment_evidence.py` (stdlib `csv`, `json`, numpy, scipy) with a module docstring giving inputs, outputs, the run command, the dependency on `.venv-nlp`, and the formulas named in section 3. One argparse option per parameter in 4.1 (`--seed`, `--quote-ok`, `--medium-weight`, `--abstract-weight`, `--keep-definitional`, `--admission-regex`, `--pool-adjusted`, `--allow-range`, `--assume-sd`, `--min-k-pool`, `--hk-min-k`, `--alpha`, `--vote-threshold`, `--cluster-min-cells`, `--cluster-distance`, `--cluster-cut`, `--bootstrap`, `--input`), plus `--code`, `--name`, `--self-test`. Copy `bh_adjust` and `r()` from `experiment_pairwise.py`; do not import it. Add `scipy>=1.11` to `scripts/requirements-experiments.txt` if missing. Done: `--help` lists every option and `--self-test` passes.
4. **Run.** From `core/`:
   `.venv-nlp/Scripts/python.exe -I scripts/experiment_evidence.py --code EXP08-SEV-evidence --name "Severity evidence matrix and meta-analysis" --seed 20261105`
   Expected runtime under 30 seconds (200 bootstraps on about 80 markers). Done: `data/experiments/EXP08-SEV-evidence.json` exists and the printed summary matches section 5 check 3.
5. **Load.** Run `Babesiosis.Console --datasets-only` (`console/Babesiosis.Console`, `appsettings.json` `ReviewRoot` pointing at `core/`). Check through the `babesiosis-local-db` MCP (read `docs/database.md` first): `SELECT e.experiment_code, e.method, COUNT(r.experiment_result_id) FROM dbo.experiment e LEFT JOIN dbo.experiment_result r ON r.experiment_id = e.experiment_id WHERE e.experiment_code = 'EXP08-SEV-evidence' GROUP BY e.experiment_code, e.method;` returns `evidence` and 8 (adjust the result table key column name to `docs/database.md` if it differs). Done: the row arrives and the web page `/experiments/EXP08-SEV-evidence` shows the interpretation and the JSON results.
6. **Verify.** Run every check in section 5; fix and re-run until all pass.
7. **Document.** Add `experiment_evidence.py` to the script table in `scripts/README.md`; add `evidence` to the `result_kind` list in `docs/database.md` if experiment kinds are listed there; mark EXP08 as run in `docs/ml-experiment-plan.html` if the page tracks status.
8. **Optional.** A web view under `webapp/Babesiosis.Web/src/app/modules/experiments/views/` for `method = 'evidence'`: heatmap of `evidence_matrix` (rows markers, columns outcomes, colour = vote score, cell text = units) and forest plots for `meta_analysis` entries with `k >= 3`. Only after tasks 1 to 7 pass.

## 8. Open questions

1. Should `medium` confidence rows ever enter the pooled estimates? Default: no; they appear in `sensitivity_with_medium` only.
2. Should `anaemia_grade` cells with `Haematocrit/PCV` (marker defines the outcome) be dropped even when the note does not say so? Default: drop only rows whose `note` says `part of the severity definition`, and list any `Haematocrit/PCV` x `anaemia_grade` cell in `run_notes` for review.
3. Should multivariable ORs be pooled with univariable ORs? Default: no (separate family, off).
4. Is `probable` cohort membership enough to merge study units? Default: yes for all 38 cohorts; add `--confirmed-cohorts-only` only if a reviewer asks.
5. Should Pearson r and Spearman rho pool together? Default: yes, flagged; Kendall tau is listed but not pooled.
6. Cluster cut 0.7 is a judgement call on a small pilot. Default: 0.7, with the dendrogram merges stored so a reader can see other cuts.
7. The plan card says 290 rows; the file has 275. Default: trust the file and re-count at run time.
