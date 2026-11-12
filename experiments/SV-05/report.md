# SV-05 report: age, sex and neuter status in *B. rossi*

Run 2026-11-12. Experiments `SV-05-01-age-death` and `SV-05-02-age-form` (method `age_sex_contrast`). Both are exploratory: S-CB050 and DS05 are on the "already seen" list of `rules.md`, and the S-CB050 age medians by outcome had been seen.

## 1. Question and hypothesis

Do age, sex and neuter status change how often *B. rossi* kills a dog, or the form the disease takes? Hypothesis: age changes the form of severe disease (anaemia-dominant in dogs under 12 months, inflammatory in adults) more than it changes the risk of death.

## 2. Inputs

| File | SHA-256 |
|---|---|
| `shared/tidy/S-CB050.features.json` | fedde71e230325695e0866bd362d932a83904dc50de7883003dc6431cff9460f |
| `shared/tidy/DS05.features.json` | 323238159fb21596dacc02464fe4ebdf7bd54282cd06fdce7535057f28e90a1e |
| `shared/tidy/DS03.features.json` | 2862ac7e6e5fcec6200024543e4142fbe81eabd2eadef06d4f288bc982eda8a6 |
| `shared/tidy/S-CB050.outcomes.json` (opened after the spec froze) | d2657b5321d1dd8528d8e363a8bf621398df32b538301d68df81976562f2d813 |
| `SV-04/out/perturbation.csv` (S-CB050 cohort 1 rows; its `severe` column was not used) | 88e1e3c48148d205870d3535545595ae3105c275c4781251a04d2d2db8cfde7b |

**Spec hash:** `spec.md` SHA-256 `dd68cbd66a738637cead48e9707a08a3c3fec84d5fd0286307d804b475e1782f` (`dd68cbd66a73`). The script stops if the spec or any input changes. Exposure log: `exposure.md`.

**Sources.** SV-07 found that the DS03 natural-infection dogs and controls are S-CB050 dogs (`SV-07/report.md`, section 4.3). This package therefore counts DS03 as SRC-A, never pools it with S-CB050 and never calls a DS03 result a replication. Independent sources: **SRC-A** (S-CB050, DS03) and **SRC-F** (DS05). `data.md` still lists DS03 as SRC-E. SV-07 is right on this point.

## 3. What was done

Young = under 12 months, adult = 12 months or more. Every effect is young minus adult, and odds ratios are young over adult. Seed 20261112, 10,000 permutations by dog and 2,000 stratified bootstrap resamples of dogs. Benjamini-Hochberg is applied inside each family.

- **Family A (risk, S-CB050, 3 tests):** A1 death by age group (Fisher exact test, conditional OR with exact interval); A2 the same stratified by sex (Mantel-Haenszel OR with Robins-Breslow-Greenland interval, p from permutation within sex); A3 age in months, died against survived.
- **Family B (form, 8 tests):** haematocrit (B1 DS05, B2 DS03 natural); band neutrophils (B3 DS05, B4 S-CB050); the SV-04 cytokine perturbation count (B5 S-CB050 cohort 1); shares in DS05 with severe anaemia, hct < 0.15 (B6), and with a left shift, bands > 0.5 x10^9/L (B7); days ill before presentation (B8 DS05).
- **Secondary contrasts (no claim):** the SV-04 balance index and z-score perturbation, WBC and segmented neutrophils (S-CB050), death by sex, haematocrit and bands by sex (DS05), and a description of the 7 neutered DS05 dogs.
- **Sensitivity analyses and checks:** S1 severe anaemia at hct < 0.20; S2 DS05 without the 3 *E. canis* co-infected dogs; S3 age as a continuous variable (Spearman); S4 DS05 inside each sex; C1 haematocrit of the healthy controls by age.

**Deviations from the spec**

- **D1. Decision rule for B5.** The perturbation count is a small integer, so its Hodges-Lehmann interval can sit at 0. For this reason the code also accepts a Cliff's-delta interval below 0 as an adult excess. I added this after the spec froze but before the first run. It did not fire (Cliff's delta interval -0.37 to +0.09) and it did not change the verdict.
- **D2. A fifth verdict, "Form and risk".** The code names the one combination that the spec left out: a form signal and a risk signal together. It did not occur.
- **D3. A descriptive age-band profile.** I added this for the figures: deaths, haematocrit, bands and days ill by age band (< 6, 6-11, 12-23, 24-47, 48-95, 96+ months). It has no test.
- **D4. DS03 counted as SRC-A, from SV-07.** The package file treats DS03 as a separate source. Step 2 is otherwise as planned.
- Not used: the optional SV-01 pseudo-stage.

## 4. Results

### Primary: risk of death (SV-05-01, S-CB050, SRC-A)

The data give no evidence that age changes the risk of death, but the data can detect only a large difference.

| Test | Young | Adult | Effect (95% CI) | p | q |
|---|---|---|---|---|---|
| A1 died by age group | 6 of 50 (12%) | 9 of 90 (10%) | OR 1.23 (0.34 to 4.15) | 0.778 | 0.785 |
| A2 the same, stratified by sex | females 3/21 vs 2/26; males 3/29 vs 7/64 | | MH OR 1.24 (0.41 to 3.77); females 1.97 (0.20 to 25.9), males 0.94 (0.15 to 4.54) | 0.785 | 0.785 |
| A3 age, died minus survived | median 29 months (15 died) | 20 months (125 survived) | HL -1 month (-8 to +17); Cliff's delta -0.04 (-0.39 to +0.31) | 0.780 | 0.785 |

With 15 deaths, a test at 80% power detects only an odds ratio of about 3.7 or more, or 0.28 or less. 0 of 3 tests pass q < 0.05. Death by sex (secondary): 10 of 93 males and 5 of 47 females died, OR 1.01 (0.29 to 4.02). Died includes euthanasia for poor prognosis.

### Form of disease (SV-05-02, DS05 SRC-F and SRC-A side by side)

| Test | Source | n young vs adult | Young vs adult | Effect, young minus adult (95% CI) | Cliff's delta | p | q |
|---|---|---|---|---|---|---|---|
| B1 haematocrit | DS05 | 55 vs 92 | median 0.17 vs 0.185 L/L | HL -0.02 (-0.04 to +0.01) | -0.12 (-0.32 to +0.08) | 0.222 | 0.267 |
| B2 haematocrit | DS03 (SRC-A) | 41 vs 60 | 0.14 vs 0.20 | HL -0.06 (-0.10 to -0.025) | -0.39 (-0.58 to -0.18) | < 0.001 | 0.007 |
| B6 severe anaemia (hct < 0.15) | DS05 | 23/55 vs 29/92 | 42% vs 32% | +0.10 (-0.05 to +0.26) | – | 0.217 | 0.267 |
| B3 band neutrophils | DS05 | 55 vs 92 | 0.23 vs 0.34 x10^9/L | HL -0.10 (-0.20 to +0.01) | -0.17 (-0.37 to +0.03) | 0.080 | 0.215 |
| B4 band neutrophils | S-CB050 | 50 vs 90 | 0.36 vs 0.34 | HL 0.00 (-0.11 to +0.13) | 0.00 (-0.19 to +0.19) | 0.967 | 0.967 |
| B5 SV-04 perturbation count | S-CB050 cohort 1 | 33 vs 63 | 1 vs 1 | HL 0 (-1 to 0) | -0.14 (-0.37 to +0.09) | 0.234 | 0.267 |
| B7 left shift (bands > 0.5) | DS05 | 15/55 vs 38/92 | 27% vs 41% | -0.14 (-0.28 to +0.02) | – | 0.110 | 0.221 |
| B8 days ill | DS05 | 55 vs 92 | median 3 vs 4 days | HL -1 (-1 to 0) | -0.23 (-0.41 to -0.03) | 0.023 | 0.090 |

**Verdict by the pre-stated rule: not supported.**

- **No anaemia-form signal.** In DS05, the only independent source, the haematocrit difference has an interval that includes 0. The lower haematocrit of young dogs is clear only in DS03 (Onderstepoort), and those are S-CB050 dogs.
- **No inflammatory-form signal.** Adults have no excess of bands or cytokine perturbation in S-CB050. DS05 points the hypothesised way: fewer bands and fewer left shifts in young dogs. Every interval includes 0.
- **No risk signal** (A1).
- **No result counts against the hypothesis.** Young dogs do not have a higher haematocrit or more bands in any source.

1 of 8 tests passes q < 0.05 (B2). The weak finding is about timing: young DS05 dogs presented about 1 day earlier (q 0.090).

**Neuter status.** DS05 has 7 neutered dogs (5 female, 2 male), all adults: median age 48 months, haematocrit 0.24 (0.10 to 0.45), bands 0.27 x10^9/L and 2 days ill. Intact adults: 24 months, 0.18, 0.40 and 4 days. These numbers are described, not tested. S-CB050 does not record neuter status, so the RR of 0.72 for gonadectomy reported in CB125 ([10.1016/j.prevetmed.2024.106293](https://doi.org/10.1016/j.prevetmed.2024.106293)) cannot be examined here.

## 5. Stability and sensitivity

- **S1, severe anaemia at hct < 0.20:** 58% vs 52%, a difference of +0.06 (-0.10 to +0.22). Same reading.
- **S2, without the 3 *E. canis* co-infected dogs:** haematocrit -0.02 (-0.04 to +0.01); bands -0.11 (-0.22 to 0.00, p 0.056); left shift -0.15 (-0.29 to +0.01); days ill -1 (-1 to 0), Cliff's delta -0.27, p 0.007. Same reading. The bands interval now reaches 0.
- **S3, age continuous (Spearman rho with age):**

  | Measure | Source | rho (95% CI) |
  |---|---|---|
  | Haematocrit | DS05 | +0.15 (-0.02 to +0.31) |
  | Haematocrit | DS03 | +0.37 (+0.18 to +0.53) |
  | Bands | DS05 | +0.11 (-0.07 to +0.27) |
  | Bands | S-CB050 | +0.02 (-0.15 to +0.19) |
  | Perturbation count | S-CB050 | +0.17 (-0.03 to +0.36) |
  | Days ill | DS05 | +0.19 (+0.04 to +0.34) |

  The continuous analysis agrees with the age-group contrasts.
- **S4, DS05 inside each sex:**
  - Males: haematocrit -0.03 (-0.07 to 0.00, p 0.069), bands -0.11 (-0.27 to +0.03).
  - Females: haematocrit 0.00 (-0.03 to +0.05), bands -0.055 (-0.23 to +0.13).
  - The DS05 trends in age are carried mainly by the males.
- **C1, healthy controls:** the 2 control dogs under 12 months have a haematocrit of 0.38 and 0.39 L/L. All 12 adult controls are at 0.45 to 0.59 (median 0.545). So at least part of the lower haematocrit of young infected Onderstepoort dogs is the normal age difference, not a different form of disease.
- **Detectable effects:** about 0.48 SD for the DS05 contrasts (55 vs 92), 0.49 SD for S-CB050 bands, 0.57 SD for DS03 and 0.60 SD for the perturbation count.
- **Repeat:** I deleted `out/` and ran the scripts again. Every file was byte-identical except `run_utc`.

## 6. Confounders

- **Handled:**
  - Species is fixed (*B. rossi*).
  - Sources are analysed separately.
  - DS03 is not counted as an independent source (SV-07).
  - The analyses were stratified by sex (A2, S4).
  - Co-infection was checked (S2).
  - The normal age difference in haematocrit was checked against the healthy controls (C1, only 2 young dogs).
- **Not handled:**
  - Age stands in for prior exposure, breed and body size, which are not recorded in S-CB050. Breed is in DS05 but was not used.
  - Sex differs between cases and controls in SRC-A.
  - Euthanasia for poor prognosis is part of "died" and can depend on owner and cost.
  - DS05 has no outcome label. So "form" is read across all infected dogs, not inside the severe dogs.
  - Source, region, year and case mix differ between DS05 and SRC-A, so a difference between sources cannot be attributed to age.

## 7. What this does not show

- It does not show that age has no effect on risk. An odds ratio below about 3.7 could be missed.
- It does not show that age does not change the form of disease. Differences below about 0.5 SD could be missed, and DS05 leans the hypothesised way for bands and left shift.
- It does not test neuter status (7 dogs) or breed.
- It does not use a severity label to define "form". DS05 and DS03 have none.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files:** every count, median, effect, interval and p value above (`out/results.json`, `out/age_contrasts.csv`).
- **Taken from documentation:** that DS03 natural dogs are S-CB050 dogs (SV-07, file level "probable"); the perturbation score and its caveats (SV-04); the literature background in the package file.
- **Inferred:** that the lower haematocrit in young Onderstepoort dogs is partly physiological (2 young controls only).

## 9. Next step and decisions for the user

1. **DS03 haematocrit could be linked to S-CB050 death.** If the SV-07 twin links between DS03 and S-CB050 were accepted at dog level, the DS03 haematocrit could be joined to S-CB050 death. That would give the only haematocrit-by-outcome contrast in *B. rossi* at Onderstepoort. It needs a new spec and acceptance of links that SV-07 marks "unverified" at dog level. This is a user decision.
2. **Correct `data.md`.** The coordinator should record in `data.md` that DS03 natural dogs are SRC-A (as SV-07 proposes).
3. **Earlier presentation of young dogs is the one lead.** It is weak (q 0.09, DS05 only). It needs a second source with illness duration, and none is public.

## Software

Python 3.12.12 (uv), numpy 2.3.4, scipy 1.16.3; .NET console loader (way B); Angular view `experiment-age-sex-contrast-view.component.*`.
