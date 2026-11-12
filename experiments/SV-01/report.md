# SV-01 report: stage or trait? Disease-space maps of natural *B. rossi* infection

Run 2026-11-12. Experiments `SV-01-01-habitus-distance` (DS05, role `descriptive`) and `SV-01-02-ds03-geometry` (DS03, role `replication`), method `disease_space_map`.

## 1. Question and hypothesis

Is part of the variation in admission severity the stage a dog has reached on a common course of *B. rossi* infection? The hypothesis: dogs that are clinically worst lie off that course (far from it), not only later on it.

## 2. Inputs

| File | SHA-256 |
|---|---|
| `shared/tidy/DS02.features.json` (5 Beagles, SRC-B) | `12475e823e588af20e8bec2df5164979c158bdbbb86ddfb96a32afe8aad83e2d` |
| `shared/tidy/DS03.features.json` (SRC-E) | `2862ac7e6e5fcec6200024543e4142fbe81eabd2eadef06d4f288bc982eda8a6` |
| `shared/tidy/DS05.features.json` (SRC-F) | `323238159fb21596dacc02464fe4ebdf7bd54282cd06fdce7535057f28e90a1e` |
| `shared/tidy/DS05.outcomes.json` (opened after the spec lock) | `4a86691b3b97aefe846803c6d5784d96b35bd75b4b33d1f74d519d3d8365eba0` |
| `shared/dictionary.csv` (read, not used by the code) | `d2a3b07561815ae14b478b8796a999b481ad1db577eb9a063bfa25d7e6246c55` at the start; `17d1021960a6…` at the end |

`dictionary.csv` changed during the run because SV-G1 was still adding the rows of other datasets. The code never reads it; the rows for the variables SV-01 uses (`hct`, `arc`, `neut_band`, `illness_days`, `pcr_b_rossi`, `pcr_e_canis`, `setting`, `cohort` in DS02, DS03 and DS05) were checked at the end and are the same as at the start. The four files the code reads did not change.

**Spec hash** (`spec.md`): `7c272692530ce89c0857ec971fd9b75578e407e643ce1d85c50a1f7d67d6a98f`. `analyse.py` checks all five hashes (the four inputs and the spec) at every run and stops if one differs; none changed during the run. No other tidy file and no other outcomes file was opened (`exposure.md`). SV-G1's hand-over note was read before the spec was written; it says that the 5 DS03 experimental dogs are the DS02 Beagles, so they were not used.

Versions: Python 3.12.12, numpy 2.3.4, scipy 1.16.3 (numbers); matplotlib 3.10.7 (figures only). Seed 20261112.

**Everything on DS05 is exploratory**: DS05 is on the "Already seen" list of `rules.md` (habitus with haematocrit rho 0.54, illness duration screened).

## 3. What was done

As `spec.md`: a principal curve (cubic in arc length, Hastie-Stuetzle type) through the 22 pre-treatment Beagle samples in the plane haematocrit by log10 ARC (plane A), axes standardised by the Beagle points; pseudo-stage = position along the curve (0 to 1); distance = gap to the curve in units of the Beagles' own scatter (0.37 SD units). The same in the plane haematocrit by log10(band neutrophils + 0.05) (plane B, 32 Beagle samples, DS05 only). 147 DS05 *B. rossi* dogs (the *B. vogeli*-only dog and 2 dogs without a CBC drop out), 103 DS03 natural dogs (cohort 1: 85, cohort 2: 18), and DS03 healthy controls (14) and IMHA dogs (16) as reference. Partial Spearman by rank residuals; Freedman-Lane permutation (10,000); bootstrap of dogs (2,000); BH over H1 to H3 (family of 3); Wilson intervals for shares.

**Deviations from `spec.md`:**

- **D0 (fit did not converge).** The principal-curve iteration stopped at its limit of 100 iterations without meeting the 1e-4 criterion. The result of the 100th iteration is used, as the spec's stop rule says.
- **D1 (construction check added after the first run, and a time-anchored course as a sensitivity).** The spec's projection step re-ordered the Beagle samples: the high-dose day-4 "crash" samples (haematocrit 0.12 to 0.28, low ARC) were placed before day 1, so the curve is a U from anaemic and low-ARC to high-ARC and does not follow time. Its pseudo-stage agrees with the sampling day only at rho 0.19 over the 22 Beagle samples. I added this check (pseudo-stage should rise with day in the Beagles) after the first run; it was not in the spec. As a sensitivity I ran a **time-anchored course**: the same cubic fit with the curve parameter kept at the sampling day and no re-projection (rho with day 0.58). **The spec construction stays primary**, because the first run had already printed outcome-based numbers (the habitus table and the leave-one-out H1 values under the spec curve) before D1 was chosen. Both are reported in full.
- No other deviation. All tests in the spec were run.

## 4. Results

### Primary analysis (SV-01-01, DS05, spec construction)

Habitus grade with distance from the Beagle course, controlling pseudo-stage (H1): **partial rho -0.24 (95% CI -0.39 to -0.07), permutation p 0.005, BH q 0.007, n 147 dogs**, independent sources 2 (SRC-B for the course, SRC-F for the dogs). Direction as predicted (higher habitus is brighter; duller dogs lie further from the course). Detectable effect at n 147: |rho| about 0.23, so this is at the edge of what the file can detect.

But the stage score is **not validated**:

| Check | Spec construction | Time-anchored (D1) |
|---|---|---|
| Construction: Beagle pseudo-stage with sampling day (added, D1) | rho 0.19, **failed** | rho 0.58, passed |
| Validity (stated in advance): DS05 pseudo-stage with illness duration, n 145 | rho +0.18 (0.02 to 0.34), p 0.03, passed | rho -0.21 (-0.36 to -0.06), p 0.010, **failed** (wrong sign) |

The spec construction passes the validity check only because its "stage" axis is not a time axis: in DS05 it tracks ARC (rho 0.61) and haematocrit (0.33), not the Beagles' days. No construction passes both checks. By the rule in the package file, every DS05 result is descriptive.

### All tests

| Test | Spec construction | Time-anchored (D1) |
|---|---|---|
| H1 habitus ~ distance given stage, plane A | -0.24 (-0.39 to -0.07), p 0.005, q 0.007 | -0.54 (-0.67 to -0.40), p < 0.001 |
| H2 habitus ~ stage, plane A | +0.29 (0.13 to 0.42), p < 0.001, q 0.002 | -0.28 (-0.43 to -0.11), p < 0.001 |
| H3 habitus ~ distance given stage, plane B (bands) | -0.12 (-0.28 to 0.06), p 0.15, q 0.15 | -0.47 (-0.59 to -0.34), p < 0.001 |
| S1 H1 without 3 *E. canis* co-infections (n 144) | -0.26 (-0.43 to -0.09), p 0.002 | -0.55 (-0.68 to -0.41) |
| S2 H1, interior projections only (n 57 / 56) | -0.15 (-0.43 to 0.11), p 0.28 | -0.51 (-0.72 to -0.25) |
| S3 H1 also controlling haematocrit | **+0.08 (-0.08 to 0.24), p 0.34** | -0.29 (-0.44 to -0.10), p < 0.001 |

7 tests per construction; under the spec construction 4 had p < 0.05 (V, H1, H2, S1); 2 of the 3 family tests pass BH at 0.05 (H1, H2).

**Distance restates anaemia.** Under the spec construction distance correlates with haematocrit at rho -0.45 and H1 disappears once haematocrit is controlled (S3). Under the time-anchored course distance is almost haematocrit (rho -0.90); a partial rho of -0.29 remains after controlling haematocrit, which may be the ARC component of distance, but that construction failed the validity check. Habitus with haematocrit alone: rho 0.53 (already seen).

**H2 has opposite signs** in the two constructions, because "stage" means different things in each. It cannot be read as "severe dogs are later".

### Geometry: where natural dogs lie (SV-01-02 replication, and DS05)

The 5 Beagles before treatment span haematocrit 0.12 to 0.42 (only one sample below 0.27) and ARC 26 to 240 x10^9/L. The median natural dog has haematocrit 0.18 (DS05, DS03 cohort 1) or 0.135 (cohort 2).

| Group (spec construction) | n | Within 2 spread units (95% CI) | On an end of the course (95% CI) | Median pseudo-stage (IQR) | Median haematocrit |
|---|---|---|---|---|---|
| DS03 natural, cohort 1 | 85 | 20% (13 to 30) | 61% (51 to 71) | 0.46 (0.00 to 1.00) | 0.18 |
| DS03 natural, cohort 2 | 18 | 17% (6 to 39) | 83% (61 to 94) | 0.20 (0.00 to 1.00) | 0.135 |
| DS05 natural | 147 | 24% (18 to 32) | 61% (53 to 69) | 0.48 (0.00 to 1.00) | 0.18 |
| DS03 healthy controls | 14 | 14% (4 to 40) | 0% (0 to 22) | 0.68 | 0.52 |
| DS03 IMHA | 16 | 6% (1 to 28) | 88% (64 to 97) | 1.00 | 0.15 |

Time-anchored course: within the band 41% (cohort 1), 17% (cohort 2), 40% (DS05); past its late end 55%, 44% and 54%.

The geometry replicates across the clinic (DS05) and the referral hospital (DS03 cohort 1): about 6 in 10 naturally infected dogs project onto an end of the Beagle course and about 1 in 4 to 1 in 5 lie near it. Pseudo-stage piles up at the two ends (histogram in the view). No test between DS03 and DS05 (different sources and settings).

## 5. Stability

Leave one Beagle out (5 refits), DS05 dogs:

| Left out | Spec: stage rank agreement with full fit | Spec: H1 partial rho | Time-anchored: stage rank agreement | Time-anchored: H1 |
|---|---|---|---|---|
| DS02:d001 | +0.92 | -0.30 | +0.84 | -0.51 |
| DS02:d002 | **-0.74** | -0.26 | -0.24 | -0.58 |
| DS02:d003 (died day 4) | +0.73 | -0.48 | -0.39 | -0.56 |
| DS02:d004 | +0.58 | -0.07 | +0.47 | -0.53 |
| DS02:d005 | **-0.65** | -0.14 | +0.84 | -0.54 |

Pseudo-stage is **not stable**: dropping one Beagle reverses the order of the DS05 dogs in 2 of 5 spec refits and 2 of 5 time-anchored refits. Distance is more stable (rank agreement 0.63 to 0.99 spec; 0.97 to 1.00 time-anchored). The spec H1 ranges from -0.07 to -0.48. The bootstrap intervals above resample the natural dogs with the curve fixed; they do not include this curve uncertainty.

## 6. Confounders

Handled: *E. canis* co-infection (S1, no change); anaemia (S3: it explains the spec-construction H1). Not handled: prior treatment (unknown); the route of infection (the Beagle course follows intravenous inoculation and may be faster than tick-borne disease); dose (2 low, 3 high dose Beagles in one course); time from onset (only owner-reported, in DS05); clinic against referral hospital (shown side by side, not tested). DS03 may share dogs with S-CB050 or S-CB517 (unverified); this does not affect SV-01, which uses neither.

## 7. What this does not show

- It does not show that severe dogs are "late" or "off course". The stage score failed validation, is unstable to one Beagle, and most natural dogs lie past the range of the 5-dog pre-treatment course, so the course cannot place them. This is the "main risk" the package file named: in cross-section, stage and course are not separable with this reference.
- The H1 association is mostly anaemia, already known to track habitus in DS05. Off-course dogs are not a subtype. No predictive score was made.
- Habitus is a proxy; DS05 has no hard outcome. One species, one country.

## 8. Verified, documented, inferred

- **Verified in files:** all numbers above (from `out/`); input hashes; that the DS03 experimental dogs are the DS02 Beagles (SV-G1 tidy file, field `same_dog_as`); the habitus coding (higher is brighter; outcomes file definition).
- **Taken from documentation:** treatment timing and the post-treatment flag (SV-G1, from the dataset record); dose groups.
- **Inferred:** that the spec curve's failure comes from the loop shape of the Beagle course (the crash samples lie near the day-1 samples in this plane); that the residual time-anchored S3 association is the ARC part of distance.

## 9. Next step and decisions

- **For SV-05 and SV-09 (readers of `out/pseudo_stage.csv`):** the file has the columns the package file names and uses the spec construction. Its `pseudo_stage` is **not validated and not stable**; `distance` is more stable but is mostly anaemia. Use them, if at all, as descriptive covariates, and say so. The time-anchored values are in `out/time_anchored/pseudo_stage.csv` with the same columns.
- A usable stage score needs a reference course that covers the anaemia range of natural cases (longer or tick-borne experimental infections, or natural cases sampled serially from known onset). This is a data need, not an analysis that can be done now.
- No user decision is needed for this package.
