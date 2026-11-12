# SV-01 spec: stage or trait? Disease-space maps of natural *B. rossi* infection

Written 2026-11-12 from the features files only (`shared/tidy/DS02.features.json`, `DS03.features.json`, `DS05.features.json`) and `shared/dictionary.csv`, before any `.outcomes.json` file was opened. The SHA-256 of this file is recorded in `report.md` and `exposure.md`.

## Status of the evidence

DS05 is on the "Already seen" list of `rules.md`: habitus was already correlated with haematocrit (rho 0.54), red cell count, haemoglobin, monocytes and band neutrophils, and illness duration was already screened (weak, rho 0.23 to 0.26). So **every DS05 result of this package is exploratory**, including the primary analysis. The DS05 experiment row uses the role `descriptive`. DS03 has no outcome; its replication is geometric and descriptive.

## Hypothesis

Part of the variation in admission severity is the stage a dog has reached on a common course (pseudo-stage). Dogs that are clinically worst lie off that course (large distance), not only later on it.

## Inputs and selection

- **Reference course (DS02, 5 Beagles, SRC-B).** Records with `post_treatment = false` and both `hct` and `arc` present (ARC exists from day 1; the high-dose day-4.1 samples have no haematocrit and drop out). Expected about 22 points.
- **Post-treatment arm.** DS02 records with `post_treatment = true` and both values. Fitted the same way, drawn separately, never used for pseudo-stage.
- **DS05 (SRC-F).** Dogs with `pcr_b_rossi = 1` (the one *B. vogeli*-only dog is excluded) and non-missing `hct` and `arc`. The 3 dogs co-infected with *E. canis* stay in (sensitivity S1 removes them).
- **DS03 (SRC-E).** `setting = natural`, reported by `cohort` (1 and 2) separately. `healthy` controls and the `imha` comparators are projected and drawn as reference only. The `experimental` records are the DS02 Beagles (`same_dog_as`) and are not used.

## Planes and transforms

- **Plane A (primary):** x = `hct` (L/L), y = log10(`arc`, 10^9/L).
- **Plane B (secondary, DS05 and DS02 only):** x = `hct`, y = log10(`neut_band` + 0.05), 10^9/L. The pseudo-count 0.05 is fixed here because many band counts are 0. Plane B uses every pre-treatment Beagle record with both values (days -1 to 4).
- Each axis is standardised by the mean and SD of the pre-treatment Beagle points of that plane. Distances are Euclidean in this standardised plane.

## The reference course

- A principal curve (Hastie and Stuetzle type) through the pre-treatment Beagle points: each coordinate is a cubic polynomial in a latent parameter t; start with t = day (rescaled to 0 to 1); then alternate (a) fit both polynomials, (b) project every point to the nearest point on the curve, sampled at 2,000 points over the observed t range, and reset t to normalised arc length. Stop when the largest change in t is below 1e-4 or after 100 iterations.
- **Pseudo-stage** = normalised arc length of the projection, 0 at the early end and 1 at the late end. The early end is the end whose nearest Beagle points have the lower mean day.
- **Spread** s = root mean square of the orthogonal distances of the Beagle pre-treatment points to the curve.
- **Distance** of a dog = Euclidean distance to its projection, divided by s.
- **Beyond-end flag**: projection falls on the first or last 1% of the curve (pseudo-stage < 0.01 or > 0.99). Such a dog lies past the range of the Beagle course; its distance mixes "later than the reference" with "off the course".
- **Within the Beagle band**: distance <= 2.
- The curve never uses habitus or any outcome.

## Validity check (stated in advance, gate)

In DS05, Spearman rho of plane-A pseudo-stage with `illness_days` (owner-reported; nulls dropped). **Pass** if rho > 0 and the two-sided permutation p < 0.05. If it fails, the report says that the stage score is not validated and every DS05 result is reported as descriptive only. (Illness duration was screened before against other variables; this is a fresh variable pair but the file is already seen.)

## Primary analysis

In DS05, plane A: partial Spearman correlation of `habitus_score` (outcomes file) with distance, controlling pseudo-stage.

- Method: rank all three variables (average ranks for ties); regress the habitus ranks and the distance ranks each on the pseudo-stage ranks (linear, with intercept); the partial rho is the Pearson correlation of the two residual vectors.
- p: permutation of the habitus residuals (Freedman and Lane), 10,000 permutations, two-sided.
- 95% interval: percentile bootstrap, 2,000 resamples of dogs. The curve is fixed (the Beagles are not resampled in this bootstrap).
- Direction: the DS05 features cleaning notes say a "COLLAPSED" habitus is coded 0 in `habitus_score`, so a lower score is taken as worse. The hypothesis then predicts a **negative** partial rho (further off the course, worse habitus). If the outcomes file defines the scale the other way, the sign of the prediction is reversed and the report says so; the test is unchanged.
- Detectable effect at n about 146: |rho| about 0.23 (80% power, alpha 0.05).

## Family of tests (Benjamini-Hochberg, family size 3)

1. H1 (primary): habitus with distance given pseudo-stage, plane A.
2. H2: Spearman rho of habitus with plane-A pseudo-stage ("is severe partly late?"). The hypothesis predicts lower habitus at higher pseudo-stage (negative rho).
3. H3: habitus with distance given pseudo-stage, plane B.

All three are DS05 and exploratory. q values are reported beside the raw p values. The validity check is a gate and is not in the family.

## Sensitivity checks (raw p only, not in the family)

- S1: H1 without the 3 *E. canis* co-infected dogs.
- S2: H1 among dogs whose projection is interior (not beyond-end).
- S3: H1 controlling haematocrit as well as pseudo-stage (ranks; both regressed out). This asks whether distance carries anything beyond anaemia, which is already known to track habitus.

## Stability

- Leave each Beagle out (5 fits): refit the curve and spread; for DS05 report the median absolute change in pseudo-stage, the Spearman rho of LOO pseudo-stage with full pseudo-stage, and the H1 partial rho under each fit.
- Bootstrap of natural dogs: the intervals above.
- Seed 20261112 for every random step (one numpy Generator per analysis, seeded from this value).

## Replication (DS03, geometry only)

For DS03 cohort 1 and cohort 2 separately, and for DS05 beside them: n, the share within the Beagle band (distance <= 2), the share beyond the end, the median and IQR of pseudo-stage, a histogram of pseudo-stage (10 bins), and the median distance. 95% intervals for the shares (Wilson) and for the medians (bootstrap of dogs, 2,000). No test between DS03 and DS05 (different sources, clinic against referral hospital); they are shown side by side.

## What counts against the hypothesis

- The "off course" part: the H1 partial rho is near 0 with an interval that excludes |rho| >= 0.23, or it has the wrong sign; or it vanishes once haematocrit is controlled (S3), so that distance only restates anaemia.
- The "stage" part: H2 near 0 or positive.
- The geometry: most natural dogs are beyond the end of the Beagle course, so that pseudo-stage is not informative for them. This would make the stage score unusable in cross-section, whatever H1 shows.
- A failed validity check makes the stage score unvalidated.

## Outputs

- `out/pseudo_stage.csv`: exactly `dog_id, dataset_id, pseudo_stage, distance, plane` (plane `A_hct_logarc` or `B_hct_logband`), one row per dog per plane, naturally infected dogs only (DS05 *B. rossi* dogs and DS03 natural dogs). DS03 controls and IMHA dogs go only in the map CSV.
- Map coordinates as CSV (Beagle points, curves, natural dogs), result tables as CSV, and the database load files.

## Do not

Use habitus to build the curve. Call off-course dogs a subtype. Fit a predictive model.
