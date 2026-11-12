# SV-09 report: is there a second reproducible phenotype axis after anaemia and stage?

Run 2026-11-12. Method `axis_replication`. Experiments `SV-09-01-ds05-residual-axes` (role `descriptive`), `SV-09-02-axis-congruence` (`replication`), `SV-09-03-axis-outcome` (`descriptive`).

## 1. Question and hypothesis

After haematocrit and the stage of disease are removed, do *B. rossi* dogs still differ along a reproducible axis of admission blood values, and does it relate to death? Hypothesis: at least one stable residual axis exists in DS05, its pattern recurs in an independent file, and its score separates dogs that died beyond what band neutrophils alone show.

## 2. Inputs

| File | SHA-256 |
|---|---|
| `shared/tidy/DS05.features.json` (SRC-F) | `323238159fb21596dacc02464fe4ebdf7bd54282cd06fdce7535057f28e90a1e` |
| `shared/tidy/DS03.features.json` (natural dogs = SRC-A by SV-07) | `2862ac7e6e5fcec6200024543e4142fbe81eabd2eadef06d4f288bc982eda8a6` |
| `shared/tidy/S-CB017.features.json` (SRC-D) | `6ed00495a7296cb9e3a87e5132cfa0f7a6a798068e9c9e811c9efdcada088cac` |
| `shared/tidy/S-CB050.features.json` (SRC-A) | `fedde71e230325695e0866bd362d932a83904dc50de7883003dc6431cff9460f` |
| `SV-01/out/pseudo_stage.csv` | `bee82f3ee20bc3cc0b1295da1e8151a9355e081787df58f3c1658a50a5a2c24d` |
| `SV-01/out/time_anchored/pseudo_stage.csv` | `ebeb9cdbe4227c70b0449df8e34bed4fbe79c2635024ef485ebf928a28b4e835` |
| `shared/tidy/DS05.outcomes.json` (after the lock) | `4a86691b3b97aefe846803c6d5784d96b35bd75b4b33d1f74d519d3d8365eba0` |
| `shared/tidy/S-CB050.outcomes.json` (after the lock) | `d2657b5321d1dd8528d8e363a8bf621398df32b538301d68df81976562f2d813` |
| `shared/tidy/S-CB017.outcomes.json` (after the lock) | `11f98f2bae04842d46d493e00246d8dc275da2a7bcc307188f8002ead6f4f046` |

**Spec hash** (`spec.md`): `3f98321b72ecfae1a89a27c8e932118c3b9b4e841144ec8a343515f604118270`. `analyse.py` checks every hash at each run. Versions: Python 3.12.12, numpy 2.3.4, scipy 1.16.3. Seed 20261112. `analyse.py` version `e7f758a51299`.

DS05, S-CB050 and S-CB017 are on the "Already seen" list: everything with an outcome or habitus is exploratory.

## 3. What was done

1. **DS05 residual axes.** 140 *B. rossi* dogs with complete data (147 with a CBC; 4 without proteins, 1 globulin entry error set missing, 2 without illness duration). 12 variables (MCV, MCHC, RDW, ARC, nRBC, segmented and band neutrophils, lymphocytes, monocytes, platelets, albumin, globulin; log where skewed), each regressed on haematocrit, haematocrit² and log(illness days + 1). PCA of the residual correlations; Horn's parallel analysis (1,000); 2,000 bootstraps with Procrustes alignment; sensitivities S1 to S5.
2. **Congruence.** Blocks of variables shared with DS05: red cells in DS03 natural infection (MCHC, reticulocytes %, ARC; n 103), leukocytes and platelets in S-CB017 day 1 (*B. canis*; 5 variables; n 31), leukocytes in S-CB050 (WBC, segmented, band; n 141). Block PCA in both files under the same conditioning; Tucker phi with bootstrap intervals (both files resampled), a uniform-pattern baseline and an exact label permutation; replication rule R1 to R4 (spec).
3. **Outcome.** The rule chose an axis; its DS05 loadings on each file's shared variables were the weights. Cliff's delta, permutation p (S-CB050 stratified by cohort), bootstrap intervals, BH over 2 tests. Comparisons with band and segmented neutrophils alone, and the score after removing bands.

**Deviations from the package file and the spec:**

- **D1 (stage covariate; decided before the lock, written into the spec).** The package file asks to regress out SV-01 pseudo-stage. SV-01 reports that score failed validation and is unstable, so it is not an established axis. Owner-reported illness duration was used instead; the two SV-01 constructions are sensitivities S2 and S3. Result: the axes do not depend on this choice (phi ≥ 0.93 against the primary in every variant).
- **D2 (sources; decided before the lock).** Following SV-07, DS03 natural dogs are S-CB050 dogs, so the DS03 and S-CB050 replications are one source (SRC-A), not two. The DS03 experimental Beagles (= DS02) were not used. Both are still independent of DS05 (SRC-F).
- **D3 (after the lock).** In step 3 the choice rule tied: axes 1 and 2 were both "congruent but not specific" in the S-CB050 block, and the code took axis 1 by order. Axis 2 — the one related to habitus — was scored post hoc as A4. In S-CB050 the two scores correlate at rho 0.99 (only bands and segmented cells are shared), so the choice does not matter there.
- No other deviation. All analyses in the spec were run.

## 4. Results

### SV-09-01: two stable residual axes in DS05 (descriptive)

| Axis | Eigenvalue (95% noise) | Residual variance | Bootstrap phi median (5th pct) | Habitus, partial rho (95% CI), p |
|---|---|---|---|---|
| 1 | 3.10 (1.64) | 26% | 0.99 (0.96) | -0.03 (-0.21 to +0.13), 0.70 |
| 2 | 1.92 (1.46) | 16% | 0.96 (0.88) | **-0.26 (-0.40 to -0.10), 0.003** |

n 140, 1 source. **Axis 1** moves leukocytes, regeneration (ARC, RDW, nRBC, MCV), platelets and globulin together (a general "marrow and inflammatory activity" direction). **Axis 2** sets the leukocytes (monocytes 0.57, lymphocytes 0.46, bands 0.45, segmented 0.34) and MCHC (0.66) against MCV (-0.47), ARC (-0.47) and RDW (-0.31): more inflammatory cells and less regeneration than the haematocrit predicts. Duller dogs score higher on axis 2. Detectable |rho| at n 140 is about 0.23, so the habitus link is near the edge, and DS05 monocytes and bands with habitus were seen before.

Sensitivity (phi with primary, axis 1 / axis 2): S1 haematocrit only 0.999 / 0.998; S2 SV-01 pseudo-stage 0.995 / 0.936; S3 time-anchored 0.999 / 0.999; S4 rank correlations 0.999 / 0.997; S5 no conditioning 0.985 / 0.995.

### SV-09-02: the axes are not shown to replicate (primary for the question)

| Block | Target (source) | n target | phi (95% CI) | Uniform baseline | Label-permutation p |
|---|---|---|---|---|---|
| Red cell | DS03 natural (SRC-A) | 103 | 0.993 (0.974 to 1.000) | 0.40 | 0.17 (minimum possible 1/6) |
| Leukocyte + platelet, comp. 1 | S-CB017 day 1 (SRC-D, *B. canis*) | 31 | 0.994 (0.855 to 0.998) | 0.98 | 0.075 (120 orderings) |
| Leukocyte + platelet, comp. 2 | S-CB017 day 1 | 31 | 0.769 (0.166 to 0.928) | 0.14 | 0.017 |
| Leukocyte | S-CB050 (SRC-A) | 141 | 0.999 (0.992 to 1.000) | 0.99 | 0.17 (minimum 1/6) |

**0 of 6 axis-by-block checks meet the replication rule; 4 are "congruent but not specific" and 2 (S-CB017) "not replicated".** The block patterns do recur, but:

- the S-CB050 block (WBC and two of its parts) loads uniformly in any file (uniform phi 0.99);
- the DS03 red-cell pattern (MCHC against reticulocytes and ARC) is not uniform but close to arithmetic (reticulocytes have low MCHC), and 3 variables cannot give p < 1/6;
- in the only block where specificity is testable (S-CB017, 5 variables, *B. canis*), component 1 is no more congruent than an all-equal pattern (0.994 vs 0.976; p 0.075); component 2 (platelets against leukocytes) is specific (p 0.017) but below the 0.85 threshold, with a wide interval;
- in the *B. rossi* blocks, only 2 step-1 variables are shared (MCHC and ARC; segmented and bands), so they **cannot tell axis 1 from axis 2**: both map onto each block (|phi| 0.93 to 1.00).

### SV-09-03: the score restates band neutrophils (descriptive)

| Analysis | n | Cliff's delta (95% CI) | p | BH q |
|---|---|---|---|---|
| S-CB050 died, axis score (segmented and bands) | 15 vs 126 | **+0.49 (+0.21 to +0.74)** | 0.002 | 0.003 |
| S-CB017 complicated, axis score (5 variables) | 18 vs 13 | +0.28 (-0.13 to +0.68) | 0.20 | 0.20 |
| S-CB050 died, band neutrophils alone | 15 vs 126 | +0.60 (+0.39 to +0.78) | < 0.001 | – |
| S-CB050 died, segmented neutrophils alone | 15 vs 126 | +0.31 (-0.05 to +0.64) | 0.046 | – |
| S-CB050 died, axis score after removing bands | 15 vs 126 | +0.15 (-0.17 to +0.45) | 0.34 | – |

2 tests, 1 with q < 0.05. **Negative for the hypothesis:** the score is weaker than band neutrophils alone, correlates 0.81 with bands, and adds nothing once bands are removed. This is the main risk the package file named: the result restates the published band-neutrophil finding (CB050). Died includes euthanasia for poor prognosis.

Sensitivities: A1 S-CB050 cohort 1 only +0.36 (+0.05 to +0.66), 12 vs 85; A2 with WBC +0.43 (+0.11 to +0.70); A3 S-CB017 without haematocrit conditioning +0.38 (-0.03 to +0.76); A4 (post hoc) axis-2 weights: S-CB050 +0.53 (+0.27 to +0.74), S-CB017 +0.04 (-0.34 to +0.45).

MCP-1 (SV-04 candidate) does not track the score: S-CB050 cohort 1 rho -0.10 (-0.30 to +0.12), n 97; S-CB017 day 1 +0.23 (-0.17 to +0.54), n 31.

## 5. Stability and sensitivity

- DS05 axes: bootstrap-stable (above) and insensitive to the stage covariate, to rank correlations, and even to removing all conditioning (S5 phi ≥ 0.985), so they are not by-products of the conditioning. The axis scores correlate with raw haematocrit and illness duration at |rho| ≤ 0.05.
- Repeat: deleting `out/` and re-running gave byte-identical `results.json` and CSV files.
- The bootstrap intervals for phi resample dogs in both files; the label permutation is exact.

## 6. Confounders

Handled: anaemia (haematocrit, quadratic) and owner-reported duration in DS05; haematocrit in DS03 and S-CB017; cohort in S-CB050 (stratified permutation, A1). Not handled: no haematocrit in S-CB050 (its score is not anaemia-adjusted); S-CB017 day 1 is 6 to 8 h after imidocarb; WBC is part of the S-CB017 label; species, source, country and assay are aliased between S-CB017 and the *B. rossi* files (one species per source); DS05 dogs come from a clinic, S-CB050/DS03 from a referral hospital; *E. canis* co-infection (3 DS05 dogs) was not excluded.

## 7. What this does not show

- It does not show that the DS05 axes are clinic-specific: the other files share 3 to 5 of the 12 variables, too few to test a 12-variable axis. The failure to replicate is mostly a limit of the files.
- It does not show that axis 2 (inflammation against regeneration at a given haematocrit) relates to death: no file with death has both its leukocyte and its regeneration sides.
- Axes are directions of variation in a continuum, not groups of dogs and not subtypes. No predictive score was made.

## 8. Verified, documented, inferred

- **Verified in files:** every number above (`out/results.json`, CSVs), input hashes, the database rows (check query in the final message).
- **Taken from documentation:** that DS03 natural dogs are S-CB050 dogs (SV-07, file-level probable); SV-01's failed validation of pseudo-stage; imidocarb timing in S-CB017 (SV-G1 note).
- **Inferred:** that the DS03 red-cell pattern is largely arithmetic (reticulocyte MCHC); that axis 2 is an inflammatory-against-regenerative balance (reading of the loadings).

## 9. Next step and decisions

- **The test that matters needs one file with both sides of axis 2 and a hard outcome**: a full CBC with ARC and RDW plus death. In the review's files only S-CB050 has death, and it has no red-cell data. SV-07 found that DS03 natural dogs are S-CB050 dogs in study-number order (dog-level pairs unverified). **Open question for the user/coordinator:** whether to use those probable DS03–S-CB050 pairs to join DS03 red-cell indices to S-CB050 death and leukocytes. That would allow an axis-2-like score (bands and segmented cells against ARC and MCHC at a given haematocrit) against death in about 100 dogs; it rests on an unverified link, so it should be a new, separately locked analysis, not a change to this one.
- For SV-INT: report SV-09 as "two stable residual axes in one clinic; not replicable with the shared variables; the outcome link restates band neutrophils".
