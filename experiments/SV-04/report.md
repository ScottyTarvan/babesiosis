# SV-04 report: is the IL-8 conflict species, or sampling time and definition?

Run 2026-11-12. Experiments `SV-04-01-il8-direction` (primary) and `SV-04-02-response-size-balance`, method `cytokine_conflict`, role `descriptive` (the published group comparisons of CB050/CB517 and CB017 were already seen).

## 1. Question and hypothesis

IL-8 is reported to fall with severity in *B. rossi* and to rise in complicated *B. canis*. Hypotheses: sampling time relative to treatment or the severity definition is a sufficient explanation for this conflict; and severe disease is either a larger cytokine perturbation (size) or a shifted one (balance).

## 2. Inputs

| File | SHA-256 |
|---|---|
| `shared/tidy/S-CB050.features.json` | `fedde71e230325695e0866bd362d932a83904dc50de7883003dc6431cff9460f` |
| `shared/tidy/S-CB017.features.json` | `6ed00495a7296cb9e3a87e5132cfa0f7a6a798068e9c9e811c9efdcada088cac` |
| `shared/tidy/DS02.features.json` | `12475e823e588af20e8bec2df5164979c158bdbbb86ddfb96a32afe8aad83e2d` |
| `shared/tidy/S-CB050.outcomes.json` | `d2657b5321d1dd8528d8e363a8bf621398df32b538301d68df81976562f2d813` |
| `shared/tidy/S-CB017.outcomes.json` | `11f98f2bae04842d46d493e00246d8dc275da2a7bcc307188f8002ead6f4f046` |

- **spec.md SHA-256: `22c7da5db7ad2e3ee20189dddf790bb63ae12a5b670baf849c69f9de89914742`** (written before any outcomes file was opened; `exposure.md` has one line per outcomes file). The DS02 outcomes file was not opened.
- Python 3.12.12, numpy 2.3.4 (all statistics written in `scripts/analyse.py`, script version `9756f9a0ca42`). Seed 20261112; 2,000 bootstrap resamples of dogs (stratified by group), 10,000 permutations.
- Independent sources: SRC-A (S-CB050, *B. rossi*, Onderstepoort), SRC-D (S-CB017, *B. canis*, Zagreb), SRC-B (DS02, *B. rossi*, 5 experimental Beagles).

## 3. What was done

As in `spec.md`: S-CB050 cohort 1 (97 infected, 12 died, 85 survived; 15 controls; before treatment) and S-CB017 day 1 (31 infected, 18 complicated, 13 uncomplicated; 16 controls; 6 to 8 h after imidocarb). Six shared analytes: IL-2, IL-8, IL-10, IL-18, GM-CSF, MCP-1. Raw concentrations of the two files were never compared.

- Experiment 1: Cliff's delta (severe minus non-severe) per analyte per file, BH in each file (family of 6); DS02 courses with decision rules R1 to R3; checks C1 (IL-8 against WBC) and C2 (S-CB017 day 7); sensitivity S2 (floors at half the floor).
- Experiment 2: perturbation count (analytes outside the [min, max] range of the file's own controls) and balance index (within-file percentile of MCP-1 minus that of IL-8), each by severity, BH in each file (family of 2); sensitivities S1 (z-score version), S2, counts above and below the range.

**Deviations from the spec**

- **D1 (added after the outcome lock).** Infected dogs against healthy controls, 6 analytes, both files (`out/infected_vs_control.csv`). It uses no outcome. It was added because the primary result showed no severity conflict and the article notes place the *B. rossi* IL-8 fall between infected dogs and controls (CB517). Raw p only; not in a family. It runs last so that it does not change the random draws of the spec analyses.
- **D2 (minor).** The S2 repeats draw new bootstrap and permutation samples, so their intervals and p values differ from the primary ones by Monte Carlo error (for example S-CB050 T2 interval +0.02 to +0.60 primary, +0.01 to +0.59 at half floor). The point estimates are identical.
- No other deviation. DS02 has no cytokine sample on day 5; the spec already used day 4 to day 6.

## 4. Results

### Primary (experiment 1): IL-8 by severity inside each file

| File, time | n severe vs non-severe | IL-8 medians (pg/mL) | Cliff's delta (95% CI) | p | q |
|---|---|---|---|---|---|
| S-CB050, before treatment, died vs survived | 12 vs 85 | 1171.7 vs 1066.3 | +0.02 (-0.28 to +0.34) | 0.898 | 0.932 |
| S-CB017, 6-8 h after imidocarb, complicated vs uncomplicated | 18 vs 13 | 907.5 vs 600.7 | +0.15 (-0.29 to +0.56) | 0.518 | 0.622 |

**Verdict by the pre-stated rule: no conflict.** Both intervals include 0 and both estimates are positive. In the dog-level files, IL-8 does not differ by severity in either species. This is a negative result for the premise of the package.

**DS02 rule for a treatment-driven reversal: not met.** IL-8 log2 change from day 4 (last pre-treatment) to day 6 (first post-treatment): d001 (low) +1.80, d002 (high) -0.23, d004 (high) -2.33, d005 (low) +1.09. R1 (same direction in every dog) fails; R2 (median |change| 1.45 against a median day-to-day change before treatment of 1.11) holds; R3 (larger rise in the sicker high-dose dogs) fails: mean change high dose -1.28, low dose +1.45. Before treatment, IL-8 rose from baseline to day 4 in all three high-dose dogs (+1.65, +3.53 in the dog that died on day 4, +1.04 log2) and not in the low-dose dogs (+0.01, -0.46).

All six analytes:

| File, time | Analyte | n | Medians (pg/mL) | Cliff's delta (95% CI) | HL log2 shift (95% CI) | p | q |
|---|---|---|---|---|---|---|---|
| S-CB050 | IL-2 | 12 vs 85 | 40.8 vs 27.5 | +0.04 (-0.32 to +0.39) | +0.00 (-2.01 to +2.39) | 0.810 | 0.932 |
| S-CB050 | IL-8 | 12 vs 85 | 1171.7 vs 1066.3 | +0.02 (-0.28 to +0.34) | +0.11 (-1.11 to +1.05) | 0.898 | 0.932 |
| S-CB050 | IL-10 | 12 vs 85 | 849.2 vs 607.5 | +0.21 (-0.11 to +0.53) | +0.57 (-0.22 to +1.39) | 0.257 | 0.770 |
| S-CB050 | IL-18 | 12 vs 85 | 65.0 vs 52.3 | -0.05 (-0.46 to +0.36) | -0.24 (-1.90 to +2.04) | 0.773 | 0.932 |
| S-CB050 | GM-CSF | 12 vs 85 | 45.8 vs 29.2 | +0.02 (-0.37 to +0.38) | +0.00 (-1.12 to +2.00) | 0.932 | 0.932 |
| S-CB050 | MCP-1 | 12 vs 85 | 921.7 vs 527.6 | +0.47 (+0.22 to +0.70) | +0.74 (+0.31 to +1.24) | 0.009 | 0.052 |
| S-CB017 | IL-2 | 18 vs 13 | 131.4 vs 89.4 | +0.48 (+0.08 to +0.82) | +0.98 (+0.26 to +2.22) | 0.022 | 0.044 |
| S-CB017 | IL-8 | 18 vs 13 | 907.5 vs 600.7 | +0.15 (-0.29 to +0.56) | +0.35 (-0.61 to +1.09) | 0.518 | 0.622 |
| S-CB017 | IL-10 | 18 vs 13 | 592.2 vs 461.1 | +0.09 (-0.34 to +0.53) | +0.14 (-0.55 to +0.86) | 0.683 | 0.683 |
| S-CB017 | IL-18 | 18 vs 13 | 188.3 vs 144.9 | +0.21 (-0.23 to +0.60) | +0.75 (-0.59 to +2.37) | 0.339 | 0.508 |
| S-CB017 | GM-CSF | 18 vs 13 | 254.4 vs 143.0 | +0.73 (+0.44 to +0.97) | +0.83 (+0.37 to +1.51) | < 0.001 | < 0.001 |
| S-CB017 | MCP-1 | 18 vs 13 | 576.2 vs 224.4 | +0.81 (+0.56 to +0.97) | +1.31 (+0.79 to +1.89) | < 0.001 | < 0.001 |

3 of 12 tests pass q < 0.05 (IL-2, GM-CSF and MCP-1 in S-CB017). MCP-1 is the one analyte that is higher in severe dogs in both files (S-CB050 q 0.052).

**Deviation D1, infected minus healthy controls (no outcome used):** IL-8 -0.45 (-0.65 to -0.24) in S-CB050 (median 1066.3 vs 3316.7 pg/mL, 97 vs 15) and +0.87 (+0.68 to +1.00) in S-CB017 (856.3 vs 137.3, 31 vs 16). This is where the IL-8 directions differ. MCP-1 is higher in infected dogs in both files (+0.90 and +0.59); IL-10 too (+0.68 and +0.97).

### Experiment 2: size or balance?

| File | Test | Means severe vs non-severe | Cliff's delta (95% CI) | p | q |
|---|---|---|---|---|---|
| S-CB050 | T1 perturbation count | 1.42 vs 1.38 | +0.04 (-0.22 to +0.31) | 0.842 | 0.842 |
| S-CB050 | T2 balance index | 19.42 vs -2.74 | +0.32 (+0.02 to +0.60) | 0.070 | 0.139 |
| S-CB017 | T1 perturbation count | 4.11 vs 2.69 | +0.71 (+0.43 to +0.92) | < 0.001 | < 0.001 |
| S-CB017 | T2 balance index | 13.98 vs -19.35 | +0.44 (+0.07 to +0.78) | 0.038 | 0.038 |

**Verdict by the pre-stated rule: balance** (T2 interval excludes 0 with the same sign in both files; T1 does not exclude 0 in S-CB050). This is weak: in S-CB050 the interval only just excludes 0 and the permutation p is 0.070 (q 0.139). The shift is carried by MCP-1, which is higher in severe dogs in both files, not by IL-8. In *B. canis*, complicated dogs also have more analytes outside the healthy range (size); dogs that died of *B. rossi* do not. 2 of 4 tests pass q < 0.05.

## 5. Stability and sensitivity

- **S2, floors at half the floor:** every Cliff's delta, perturbation count, balance index and Hodges-Lehmann shift is unchanged (floor values are already the lowest, and the HL medians do not pass through them). Only the z-score version moves (S-CB050 +0.19 to +0.18; S-CB017 +0.76 to +0.75). BH q values move by Monte Carlo error only.
- **S1, z-score perturbation:** S-CB050 +0.19 (-0.09 to +0.43), S-CB017 +0.76 (+0.49 to +0.96): same reading as the count.
- **Above and below the range:** in S-CB017 the excess is above the range (+0.65, +0.36 to +0.89); below: +0.11 (+0.00 to +0.28). In S-CB050 neither differs (above +0.15, +0.00 to +0.31; below -0.08). In S-CB050 IL-8 is outside the control range (below it) in 42 of 85 survivors and 5 of 12 dogs that died; MCP-1 in 67 of 85 and 12 of 12.
- **C2, S-CB017 day 7:** IL-8 -0.15 (-0.59 to +0.29), median 1910.8 vs 2852.2 pg/mL (17 vs 13). The sign turns negative 6 days after treatment but the interval is wide on both days. MCP-1 stays higher in complicated dogs (+0.54, +0.17 to +0.86).
- **C1, IL-8 and WBC:** rho +0.30 (+0.09 to +0.49, n 97) in S-CB050 and +0.25 (-0.11 to +0.57, n 31) in S-CB017. WBC by label: +0.11 (-0.27 to +0.48) and +0.23 (-0.20 to +0.63). The definition is not needed to explain an IL-8 severity difference that the files do not show.
- **Repeat:** `out/` deleted and rebuilt; every file byte-identical (load files differ only in `run_utc`).

## 6. Confounders

- Handled: each contrast is inside one file (one assay run, one definition, one sampling time); dogs are the resampling unit; floors are flagged and tested at half the floor.
- Not handled: species, source, country, assay run, severity definition, sampling time and control selection are fully aliased between files. The infected-against-control IL-8 difference (D1) cannot be attributed to species. S-CB017 controls include 8 dogs whose ID prefix suggests prophylactic imidocarb (inferred). Supportive care in S-CB017 is not recorded. "Died" in S-CB050 includes euthanasia for poor prognosis. The S-CB017 "complicated" label uses SIRS, so a larger perturbation there is partly built into the label.

## 7. What this does not show

- It does not test the report that IL-8 falls with severity in *B. rossi*: that report comes from CB037 ([10.1111/pim.12630](https://doi.org/10.1111/pim.12630); 55 dogs in severity groups and 9 non-survivors; abstract only, no dog-level file, a separate cohort). In the only *B. rossi* dog-level file (S-CB050 = CB517 [10.1371/journal.pone.0150113](https://doi.org/10.1371/journal.pone.0150113) and CB050 [10.3389/fvets.2020.00072](https://doi.org/10.3389/fvets.2020.00072)), IL-8 is lower in infected dogs than in controls but not lower in dogs that died. The SV-G2 extraction of CB517 records the same (non-survivors 1171.7 vs survivors 1066.3 pg/mL, not significant).
- Smaller effects are not excluded: the detectable effect at 80% power is about 0.86 SD in S-CB050 and 1.05 SD in S-CB017.
- A 6 to 8 h effect of imidocarb cannot be seen: the first DS02 cytokine sample after treatment is 36 to 48 h later. DS02 has 4 dogs after treatment, no severity label, and the dose group is a design variable.
- The balance index is a rank difference of two analytes, not a validated measure of immune balance. No subtypes, no prediction.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files:** every number above (from the tidy files of SV-G1); the CB517 IL-8 values agree with the SV-G2 extraction (`/experiments/SV-G2/associations_v2.csv`); CB037 is abstract-only (`source_format: "abstract"`).
- **Taken from documentation:** sampling times (S-CB050 before treatment; S-CB017 6 to 8 h after imidocarb; DS02 treatment at about 96 h and 108 h) from the SV-G1 cleaning notes and `data.md`; the CB037 findings from its article note; the CB017 published results ([10.1371/journal.pone.0190474](https://doi.org/10.1371/journal.pone.0190474)).
- **Inferred:** that the DS02 day-4 sample was taken before treatment (SV-G1 note); the H/HI control subgroups of S-CB017.

## 9. Next step and decisions for the user

- The package premise ("IL-8 falls with severity in *B. rossi*") rests on CB037 alone. SV-03 (evidence matrix) should weigh CB037 against CB517 when it aligns definitions; the extraction has no CB037 row (abstract only). Whether to obtain the CB037 full text is a user decision.
- MCP-1 is the analyte that moves with severity in both files (in the same direction, with different definitions and sampling times). SV-03 and SV-09 may want it as a candidate; it is not a predictor.
- SV-05 step 3 depends on this package: the perturbation counts and balance indices per dog are in `out/perturbation.csv` (outcome-linked; read the caveats above).
