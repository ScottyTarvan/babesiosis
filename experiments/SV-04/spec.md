# SV-04 spec: is the IL-8 conflict species, or sampling time and definition?

Written 2026-11-12 from the features files only (`shared/tidy/S-CB050.features.json`, `S-CB017.features.json`, `DS02.features.json`), before any `.outcomes.json` file was opened. The SHA-256 of this file is recorded in `report.md` and `exposure.md`.

## Status of the evidence

The published group comparisons of CB050 and CB017 are on the "Already seen" list of `rules.md`: the direction of the IL-8 difference in each article is known (lower in dogs that died in *B. rossi*; higher in complicated *B. canis*). The within-file contrasts of this package are therefore **descriptive re-analyses**, not confirmatory tests. Both experiment rows use the role `descriptive`. What is new is (a) the contrasts on the same 6 analytes with the same statistics, side by side, (b) the perturbation count and balance index, (c) the DS02 within-dog courses around treatment.

## Hypotheses

- H-time: the IL-8 conflict can be explained by sampling time relative to treatment (S-CB017 day 1 is 6 to 8 h after imidocarb; S-CB050 is before treatment).
- H-definition: the conflict can be explained by the severity definition (death in S-CB050; "complicated", partly defined by SIRS criteria that include WBC, in S-CB017).
- H-size vs H-balance: severe disease is a larger overall perturbation of the cytokine panel (size), or a shift in the balance between analytes (MCP-1 relative to IL-8) at a similar size.

Species, source, country, assay and definition are fully aliased. This package can show that timing or definition is a *sufficient* explanation, or that the data do not support it. It cannot show that species is the cause.

## Inputs and selection

- **S-CB050 (SRC-A, *B. rossi*).** `cohort = 1` (cytokines measured): 97 infected, 15 controls. All 6 analytes are present for all of them. Severe = `died = 1` (outcomes file; includes euthanasia for poor prognosis), non-severe = `died = 0`. Blood taken at presentation, before treatment.
- **S-CB017 (SRC-D, *B. canis*).** Infected records with `timepoint = day_1` (31 dogs) and controls (`single`, 16 dogs). Severe = `complicated = 1` (outcomes file), non-severe = `complicated = 0`. Blood taken 6 to 8 h after imidocarb. The day-7 records are used only in secondary check C2.
- **DS02 (SRC-B, *B. rossi*, 5 Beagles).** Cytokines exist on days -1, 0, 1, 2, 3, 4, 6, 8 (none on day 5, 7 or 4.1). Last pre-treatment sample = day 4; first post-treatment sample = day 6 (about 48 h after treatment in the high-dose dogs, about 36 h in the low-dose dogs). One high-dose dog has no sample after day 4 (death). DS02 has no severity label; `dose_group` is the design variable. No outcomes file of DS02 is opened.
- **Shared analytes (6):** `il2, il8, il10, il18, gmcsf, mcp1`. Raw concentrations of two files are never merged or compared (data.md).

## Floors (from the features files)

| File | Analyte | Floor | Samples at floor (controls + infected used) |
|---|---|---|---|
| S-CB050 | il2 | 3.4 | 30 / 112 |
| S-CB050 | il10 | 8.4 | 5 / 112 |
| S-CB050 | il18 | 5.7 | 4 / 112 |
| S-CB050 | gmcsf | 9.1 | 28 / 112 |
| S-CB050 | il8, mcp1 | none documented (IL-8 minimum 21.6 in 3 dogs may be an undocumented floor) | 0 |
| S-CB017 | il2 | 10 | 1 / 47 |
| S-CB017 | il8 | 10 | 1 / 47 |
| S-CB017 | il10 | 0.8 | 17 / 47 (all 16 controls) |
| S-CB017 | il18 | 2 | 12 / 47 |
| DS02 | all | 0 = below detection | il2 7, gmcsf 5, il18 2 samples over all days |

## Experiment 1 (primary): `SV-04-01-il8-direction`

**Step 1. Within-file contrasts.** In each natural-infection file, for each of the 6 analytes: Cliff's delta (severe minus non-severe; positive = higher in severe), 95% percentile bootstrap interval (2,000 resamples of dogs, stratified by severity group), two-sided permutation p (10,000 label permutations). Benjamini-Hochberg inside each file (family of 6; two families). Also the Hodges-Lehmann shift of log2 values with its bootstrap interval, and group medians.

**Primary quantity.** The sign and 95% interval of the IL-8 Cliff's delta in each file.

- *Conflict confirmed* if the two IL-8 intervals exclude 0 in opposite directions.
- *Partial conflict* if the signs differ and at least one interval includes 0.
- *No conflict* if the signs agree.

**Step 4. DS02 courses.** For each dog and each analyte (log2(x + 1), pg/mL, so that zeros stay finite):

- Pre-treatment course: log2 change from baseline (mean of days -1 and 0) to day 4.
- Pre-treatment day-to-day changes: the log2 changes between consecutive sampled days from day 0 to day 4.
- Post-treatment change: log2 change from day 4 to day 6, and from day 4 to day 8.

**Decision rule for IL-8 (stated in advance).** DS02 shows a post-treatment IL-8 change that could reverse a pre-treatment contrast only if all three hold:

- R1. All dogs with a day-6 sample (expected 4) change in the same direction from day 4 to day 6.
- R2. The median |log2 change| day 4 to day 6 is larger than the median |log2 day-to-day change| before treatment in the same dogs (treatment change stands out from daily fluctuation).
- R3. The change differs by disease intensity in the direction needed for reversal: IL-8 rises more (or falls less) after treatment in the high-dose dogs than in the low-dose dogs. (A uniform shift in all dogs cannot reverse a within-file contrast; a reversal needs the sicker dogs to change more upward.)

If R1 to R3 all hold, the report says that timing is a sufficient explanation as far as daily data can show. If not, it says that DS02 gives no support for a treatment-driven reversal, and that a 6 to 8 h effect cannot be seen in daily samples (main risk). With 4 dogs, no test is done in DS02; this is descriptive.

The same summaries are reported for the other 5 analytes, with the same rule, as context (not part of the decision).

**Secondary checks (descriptive, raw p only, not in a family).**

- C1 (definition). Spearman rho of IL-8 with WBC among infected dogs in each file (features only), with a bootstrap interval; and Cliff's delta of WBC between severe and non-severe in each file. If IL-8 tracks WBC in S-CB017 and the complicated group has the higher WBC, the "complicated" label (SIRS includes WBC) is partly selecting on an inflammation marker that moves with IL-8: the definition is then a sufficient explanation for at least part of the S-CB017 direction.
- C2 (time inside S-CB017). The 6 contrasts repeated on the S-CB017 day-7 records (6 days after imidocarb), same statistics. If the IL-8 sign holds at day 7, the S-CB017 direction is not only an early post-dose effect.

## Experiment 2: `SV-04-02-response-size-balance`

**Step 2. Perturbation score.** For each infected dog: the number of the 6 analytes outside the range [min, max] of that file's own healthy controls (S-CB050 cohort-1 controls, n 15; S-CB017 controls, n 16). Also the counts above the maximum and below the minimum, separately. Values equal to the control min or max are inside.

**Step 3. Balance index.** Among infected dogs in each file: percentile rank of MCP-1 minus percentile rank of IL-8 (percentile = 100 x (average rank - 0.5) / n). Range about -100 to +100; positive = MCP-1 high relative to IL-8.

**Tests (BH inside each file, family of 2).** Cliff's delta (severe minus non-severe) for the perturbation count (T1) and for the balance index (T2), with bootstrap interval and permutation p as in experiment 1.

**What counts for each hypothesis.**

- *Size*: T1 positive with an interval that excludes 0 in both files.
- *Balance*: T2 differs from 0 with the same sign in both files, while T1 does not exclude 0 in at least one file.
- *Neither*: no interval excludes 0 in both files. *Mixed*: anything else, reported as such.

**Sensitivity (not in the families).**

- S1, z-score version of the perturbation: for analytes with fewer than 20% floor values among the samples used in that file (S-CB050: il8, il10, il18, mcp1; S-CB017: il2, il8, gmcsf, mcp1), z = (log2 x - mean of control log2) / SD of control log2; score = mean |z| over those analytes; Cliff's delta severe vs non-severe.
- S2, floors at half the floor: every value flagged `floor` is replaced by half the floor; all statistics of both experiments are repeated. Rank-based statistics (Cliff's delta, perturbation count, balance index) are expected not to change, because a floor value is already the lowest; the Hodges-Lehmann log2 shift and the z-scores can change. The report states which changed.
- S3, rank-only: Cliff's delta is the rank statistic of record. The Hodges-Lehmann shift is the non-rank companion.

## Stability

- Bootstrap by dog (2,000), stratified by severity group, inside each file. Permutation p by dog (10,000). Each dog has one record in each analysis set, so rows are dogs.
- Seed 20261112 for every random step, with a fixed order of draws (file, then analyte, in the order above).

## Detectable effect (80% power, two-sided 0.05)

- S-CB050: 12 died vs 85 survived (expected): about 0.86 SD.
- S-CB017: 18 complicated vs 13 uncomplicated: about 1.05 SD.

## What would count against the hypotheses

- Against H-time: R1, R2 or R3 fails in DS02; or C2 shows the S-CB017 IL-8 direction persists at day 7.
- Against H-definition: C1 shows no IL-8 to WBC association in S-CB017, or no WBC difference by label.
- Against H-size: T1 does not exclude 0 in either file, or has opposite signs.

## Outputs

- `out/contrasts.csv`: file, timepoint, analyte, n severe, n non-severe, medians, Cliff's delta and interval, HL log2 shift and interval, p, q, floor handling.
- `out/perturbation.csv`: one row per infected dog: file, dog_id, severe flag, perturbation count, above, below, z-score version, MCP-1 and IL-8 percentiles, balance index.
- `out/ds02_courses.csv`: one row per dog and analyte: dose group, baseline, day 4, day 6, day 8, the log2 changes, median |day-to-day change|.
- `out/ds02_series.csv`: the raw DS02 series (log2(x + 1)) for the figure.
- `out/results.json`: every number in the report.
- `out/db/<code>.json`: two load files (way B, the console loader).
