# SV-05 spec: age, sex and neuter status in *B. rossi*

Frozen 2026-11-12, written from the features files only (S-CB050, DS05, DS03) and the header of `SV-04/out/perturbation.csv`. No outcome file was opened before this file was frozen. Its SHA-256 is recorded in `report.md` and `exposure.md`.

## Hypothesis

Age changes the form of severe disease (anaemia-dominant in young dogs, inflammatory in adults) more than it changes overall risk of death.

## Fixed definitions

- **Age group.** Young = `age_months` < 12; adult = `age_months` >= 12. Dogs with no age are left out of every age contrast and counted.
- **Contrast direction.** Every difference is young minus adult. Odds ratios are odds of the event in young dogs over odds in adults.
- **Dogs.** Infected dogs at admission, natural infection only.
  - S-CB050: 141 infected (cohort 1 and 2). Step 3 uses cohort 1 only (the 97 dogs in `perturbation.csv`, rows `file = S-CB050`).
  - DS05: dogs with `pcr_b_rossi = 1` (149; the one *B. vogeli*-only dog is excluded). The 3 *B. rossi* + *E. canis* dogs stay in (sensitivity S2 removes them).
  - DS03: `setting = natural`, cohorts 1 and 2 (103). Experimental, healthy and IMHA dogs are out of the contrasts.
- **Source.** SV-07 found that the DS03 natural dogs are S-CB050 dogs (file level, probable). So DS03 is counted as **SRC-A**, not as an independent source. The independent sources in this package are SRC-A (S-CB050, DS03) and SRC-F (DS05). DS03 and S-CB050 are never pooled, and a DS03 result is never called a replication of an S-CB050 result.
- **Severe anaemia (DS05).** `hct` < 0.15 L/L. Sensitivity S1: `hct` < 0.20 L/L.
- **Left shift (DS05).** `neut_band` > 0.5 x10^9/L, computed from the features file (the threshold of the authors' class; the class itself, in the outcomes file, is not opened).
- **Death (S-CB050).** `died` from `S-CB050.outcomes.json`. Includes euthanasia for poor prognosis.

## Tests

Seed 20261112, one numpy generator, draws in the order below. Permutation tests: 10,000 permutations of the age-group label (within sex strata where stated), two-sided, p = (k + 1) / (B + 1). Bootstrap: 2,000 resamples of dogs within each age group (stratified), percentile 95% interval. Hodges-Lehmann (HL) difference = median of all young-minus-adult pairwise differences. Cliff's delta is given with every HL test.

### Family A: risk (S-CB050, 3 tests, BH inside the family)

- **A1 (primary of the package).** Death by age group, 141 infected minus missing age. Fisher exact test (two-sided); conditional maximum-likelihood odds ratio with exact (Cornfield-type conditional) 95% interval.
- **A2.** Death by age group stratified by sex. Odds ratio and Fisher p in each sex; Mantel-Haenszel pooled OR with the Robins-Breslow-Greenland interval; p from 10,000 permutations of age group within sex (statistic: deaths among young dogs summed over strata, which is the conditional exact test statistic).
- **A3 (secondary).** Age in months by outcome (died minus survived): Cliff's delta with bootstrap interval, HL difference, permutation p of the Mann-Whitney U.

### Family B: form (8 tests, BH inside the family)

| Test | Source | Measure | Statistic |
|---|---|---|---|
| B1 | DS05 | haematocrit | HL, Cliff's delta, permutation p |
| B2 | DS03 natural | haematocrit | same |
| B3 | DS05 | band neutrophils | same |
| B4 | S-CB050 (all 141) | band neutrophils | same |
| B5 | S-CB050 cohort 1 | SV-04 perturbation count | same |
| B6 | DS05 | share with severe anaemia | difference in proportions (Newcombe hybrid score interval), OR, Fisher p |
| B7 | DS05 | share with left shift | same |
| B8 | DS05 | illness duration (days) | HL, Cliff's delta, permutation p |

### Secondary, not in a family (reported with intervals, no claim)

- S-CB050 cohort 1: SV-04 balance index (MCP-1 minus IL-8 percentile) and z-score perturbation (`z_mean_abs`) by age group.
- S-CB050: WBC and segmented neutrophils by age group.
- Sex: death by sex in S-CB050 (Fisher, OR), and haematocrit and bands by sex in DS05 (HL). Sex differs between cases and controls in SRC-A; no control is used here.
- Neuter status (DS05, 7 neutered dogs, all adults): medians of haematocrit, bands and illness duration against intact adults. Described, not tested.

### Sensitivity and checks

- **S1.** Severe anaemia at `hct` < 0.20.
- **S2.** DS05 without the 3 *E. canis* co-infected dogs (B1, B3, B6, B7, B8).
- **S3.** Age as a continuous variable: Spearman rho (bootstrap interval) of age with haematocrit (DS05, DS03), bands (DS05, S-CB050), perturbation (S-CB050 cohort 1), illness duration (DS05).
- **S4.** B1 and B3 within each sex.
- **C1.** Haematocrit by age group in DS03 healthy controls (the S-CB050 controls; few young dogs expected). Described: tells whether a lower haematocrit in young infected dogs could be the normal age difference.
- **Detectable effect.** For each contrast, the standardised difference detectable at 80% power and alpha 0.05 (normal approximation) and, for A1, the smallest detectable odds ratio given the observed death rate.

## Decision rule (stated before the outcome is opened)

- **Anaemia-form signal:** B1 HL < 0 with its interval excluding 0, and B2 with the same sign. (B2 is the same source, so it confirms the measure, not the finding.)
- **Inflammatory-form signal:** an adult excess (HL > 0 with young minus adult < 0, interval excluding 0) in at least one of B3, B4 or B5, with the same sign in the other source where it exists (B3 against B4).
- **Risk signal:** A1 odds ratio interval excludes 1.
- **Verdict.**
  - "Supported": both form signals and no risk signal.
  - "Partly supported": one form signal and no risk signal.
  - "Risk, not form": a risk signal and no form signal.
  - "Not supported": no form signal (whatever the risk result); a null risk result is not evidence of no risk difference, because only an odds ratio near 3 or more is detectable.
  - **Against the hypothesis:** young dogs with a higher haematocrit (B1 interval above 0), or young dogs with more bands (B3 or B4 interval above 0).
- Step 1 is exploratory: the S-CB050 age medians by outcome were seen before this plan.

## Outputs

- `out/age_contrasts.csv`: one row per contrast (family, test, source, n young, n adult, medians or shares, effect, interval, p, q).
- `out/results.json`: every number, the checks and the verdict.
- `out/db/<code>.json`: load files for the two experiments `SV-05-01-age-death` (family A) and `SV-05-02-age-form` (family B and the secondary analyses).
