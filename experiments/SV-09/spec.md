# SV-09 spec: is there a second reproducible phenotype axis after anaemia and stage?

Written 2026-11-12 from the features files only (`shared/tidy/DS05.features.json`, `DS03.features.json`, `S-CB017.features.json`, `S-CB050.features.json`) and SV-01 `out/pseudo_stage.csv` (built from features only). No `.outcomes.json` file was opened before this file was frozen. Its SHA-256 is recorded in `report.md` and `exposure.md`.

## Status of the evidence and what changed since the package file

- DS05, S-CB050 and S-CB017 are on the "Already seen" list of `rules.md` (DS05 habitus screens; published group comparisons of CB050 and CB017, including band neutrophils by death). Every experiment of this package has the role `descriptive`, except the congruence experiment, which compares correlation structure only and has the role `replication`.
- **Stage.** The package file asks to regress out "pseudo-stage" from SV-01. SV-01 reports that its pseudo-stage failed validation (no construction passes both its construction and validity checks) and is unstable (dropping one Beagle reverses the order of DS05 dogs in 2 of 5 refits). It is therefore **not used as the primary stage covariate** (deviation D1, decided before any outcome file). Substitute: owner-reported **illness duration** (`illness_days`, log(days + 1)), the only direct time measure in DS05. SV-01 pseudo-stage (spec construction and time-anchored) enter as sensitivities S2 and S3.
- **Sources (SV-07, section 4.3 and link table).** DS03 natural dogs are S-CB050 dogs (SRC-A, file-level probable). So the two *B. rossi* replications (DS03 red-cell block, S-CB050 leukocyte block) are **one source**, not two. Both are still independent of DS05 (SRC-F). The 5 DS03 experimental dogs are the DS02 Beagles and are not used. S-CB017 (SRC-D, *B. canis*) is a transfer check, reported separately.

## Step 1. DS05 residual axes (experiment `SV-09-01-ds05-residual-axes`)

- **Dogs.** DS05 records with `pcr_b_rossi = 1` and a CBC (147). Complete cases on the variables and covariates below.
- **Variables (12).** `mcv, mchc, rdw, arc, nrbc_per100wbc, neut_seg, neut_band, lymph, mono, plt, albumin, globulin`.
  Left out, with the reason: `hb`, `rbc` (near-collinear with haematocrit, the conditioning variable); `mch` (function of MCV and MCHC); `retic_pct` (function of ARC and red cell count); `wbc` (sum of the differential); `tsp` (albumin + globulin); `eos` (zero in 84 of 147); `baso`, `other_cells` (mostly zero); vital signs (handling and missingness).
- **Transforms.** log(x + 0.05) for `arc`, `neut_seg`, `neut_band`, `lymph`, `mono`, `plt`; log(x + 1) for `nrbc_per100wbc`; others untransformed. Known entry error: the dog with globulin 1 g/L (BET021 in the file, `rules`/data.md) is set to missing for `globulin` and `albumin`.
- **Conditioning (primary).** Each transformed variable is regressed (OLS) on haematocrit, haematocrit², and log(illness_days + 1); the residuals are standardised. Principal components of the correlation matrix of the residuals.
- **Number of components.** Horn's parallel analysis: 1,000 data sets with each residual column permuted independently; retain component *k* if its eigenvalue exceeds the 95th percentile of the *k*-th permuted eigenvalue.
- **Stability.** 2,000 bootstrap resamples of dogs: re-residualise, re-run the PCA, align the first *m* bootstrap components to the full-sample ones by orthogonal Procrustes rotation (*m* = number retained, at least 2), and compute Tucker's congruence (phi) per component. A component is **stable** if the median phi ≥ 0.85 and the 5th percentile ≥ 0.70.
- **Loadings** are structure coefficients (correlation of each residual with the component score). Sign: the largest absolute loading is positive.
- **Sensitivities** (phi of each retained component against the primary): S1 haematocrit only (no illness duration); S2 haematocrit + SV-01 pseudo-stage (spec construction, plane A); S3 haematocrit + SV-01 time-anchored pseudo-stage (plane A); S4 Spearman (rank) correlation matrix instead of Pearson; S5 no conditioning at all (to show what conditioning removed).
- **Habitus (secondary, descriptive, DS05 outcomes file).** Spearman rho of each retained component score with habitus grade, partial on the same covariates (rank residuals), permutation p (10,000), bootstrap interval. Not in a BH family; reported as already-seen data.

## Step 2. Replication of loadings (experiment `SV-09-02-axis-congruence`)

Three blocks, each the variables shared between DS05 and one target file:

| Block | Target | Target dogs | Variables | Conditioning in both files |
|---|---|---|---|---|
| Red cell | DS03 natural infection, cohorts 1 and 2 (SRC-A by SV-07) | 103 | `mchc, retic_pct, arc` (log for retic, ARC) | haematocrit, haematocrit² |
| Leukocyte and platelet | S-CB017 day 1 (*B. canis*, SRC-D) | 31 | `neut_seg, neut_band, lymph, mono, plt` (log) | haematocrit, haematocrit² |
| Leukocyte | S-CB050 infected, both cohorts (SRC-A) | 141 | `wbc, neut_seg, neut_band` (log) | none (no haematocrit in the file) |

For DS05 the same conditioning is applied as in the target (illness duration is not in the targets), so like is compared with like.

- **Block pattern.** In each file, PCA of the block's residual correlation matrix; loadings as above. Compare DS05 with the target by Tucker's phi per component, for component 1 and, in blocks of 5 variables, component 2 (after orthogonal Procrustes rotation of the target's first two components to DS05). Interval: 2,000 bootstrap resamples of dogs in both files at once (percentile 95%).
- **Specificity (label permutation).** A phi near 1 is trivial when every loading has the same sign. Two baselines: (a) phi of the target pattern with a uniform vector (all loadings equal); (b) exact label permutation: phi between DS05 and target after every permutation of the target's variable labels (3! = 6 for 3 variables, 5! = 120 for 5); p = share of permutations with |phi| ≥ observed. The smallest possible p is 1/6 for the 3-variable blocks, so specificity is **not testable** there; this is stated in the result.
- **Link to the DS05 residual axes.** For each retained DS05 component (step 1), phi between its loadings restricted to the block variables that are in the step-1 set and the DS05 block component 1. This says which DS05 axis a block carries.
- **Replication rule (stated in advance).** A DS05 residual axis is **replicated in a block** if all hold: (R1) it is retained and stable in step 1; (R2) it maps onto the block (|phi| ≥ 0.85 with DS05 block component 1); (R3) DS05 versus target phi ≥ 0.85 with bootstrap lower bound ≥ 0.70; (R4) where testable (≥ 4 variables), label-permutation p ≤ 0.05 and phi above the uniform baseline. Where R4 is not testable, the result is "congruent but not specific".

## Step 3. Axis score against a real label (experiment `SV-09-03-axis-outcome`)

- **Axis chosen.** The DS05 residual axis with the strongest replication in a leukocyte block (S-CB050 first, then S-CB017). If no axis meets the replication rule, the DS05 retained component with the largest summed absolute loading on `neut_seg, neut_band` is used and the result is labelled "not replicated".
- **Score.** Weights = DS05 loadings of that axis restricted to the target's shared variables, scaled to unit length. Target score = weights · within-file standardised (and, in S-CB017, haematocrit-residualised) variables. For S-CB050, `wbc` has no DS05 step-1 loading, so the S-CB050 score uses `neut_seg, neut_band` only, with `wbc` added as sensitivity A2 (weight from the DS05 block loading).
- **Outcomes (BH family of 2).** S-CB050: `died` (includes euthanasia for poor prognosis), all 141 infected dogs; Cliff's delta (died minus survived), permutation p stratified by cohort (10,000), bootstrap interval (2,000, stratified by group). S-CB017: `complicated`, day-1 records; same statistics, unstratified.
- **Does it restate the band-neutrophil finding? (main risk).** In S-CB050: Cliff's delta of log band neutrophils alone; and of the axis score after regressing out log band neutrophils. The axis "adds nothing beyond bands" if the residual delta interval includes 0 or |delta axis| ≤ |delta bands|.
- **Other checks (not in the family).** A1 S-CB050 cohort 1 only (cytokine cohort); A2 with `wbc`; A3 S-CB017 without haematocrit conditioning; MCP-1 (SV-04 candidate): Spearman rho of the score with log MCP-1 among infected dogs in S-CB050 cohort 1 and S-CB017 day 1 (descriptive, no outcome).
- **Circularity.** WBC (and, through it, the differential) is part of the S-CB017 "complicated" definition; any S-CB017 association is partly by construction.
- **Detectable effect** (80% power, alpha 0.05): S-CB050 15 vs 126 dogs about 0.76 SD; S-CB017 18 vs 13 about 1.05 SD.

## What counts against the hypothesis

- Parallel analysis retains no component, or no retained component is stable (no second axis in DS05 beyond noise).
- No block meets R3 (the DS05 pattern does not recur), or the only congruent blocks are not specific (all-same-sign patterns that any leukocyte data would give).
- The score's delta interval includes 0 in S-CB050, or the axis adds nothing beyond band neutrophils (then the result restates the published finding).

## Statistics and seeds

Seed 20261112, one numpy generator, fixed order of draws (step 1, then 2, then 3). Permutations 10,000; bootstrap 2,000; parallel analysis 1,000. Resampling is by dog (one record per dog in every file used). No predictive model; no axis is called a subtype.
