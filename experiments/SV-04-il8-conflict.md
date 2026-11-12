# SV-04. Is the IL-8 conflict species, or sampling time and definition?

| | |
|---|---|
| Wave | 1 |
| Lane | Cross-dataset |
| Effort | Small to medium |
| Working folder | `/experiments/SV-04/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): `S-CB050`, `S-CB017`, `DS02`.

- **Question.** IL-8 falls with severity in *B. rossi* (CB517, CB050, [10.1111/pim.12630](https://doi.org/10.1111/pim.12630)) and rises in complicated *B. canis* (CB017). Can sampling time, treatment or the severity definition explain the difference? Is severity the size of the response or its balance?
- **Depends on.** SV-G1.
- **Inputs.** Tidy S-CB050 (cohort 1), S-CB017 (day 1), DS02. Shared analytes: IL-2, IL-8, IL-10, IL-18, GM-CSF, MCP-1.
- **Steps.**
  1. Inside each natural-infection file, compare each shared analyte between severe and non-severe dogs (Cliff's delta with bootstrap interval; family of 6).
  2. Perturbation score for each infected dog: the number of the 6 analytes outside the range of that file's own healthy controls. Use this count, not z-scores, because several analytes sit at the assay floor in controls. Give a z-score version as a sensitivity analysis for analytes with fewer than 20% floor values.
  3. Balance index: the within-file percentile of MCP-1 minus the within-file percentile of IL-8, among infected dogs.
  4. DS02: for each analyte, the course before treatment and the change after treatment in each dog. State whether a sample taken shortly after treatment would be expected to differ in direction from one taken before.
- **Primary analysis.** The sign and interval of the IL-8 contrast in each file, and whether DS02 shows a post-treatment change in IL-8 large enough to reverse it.
- **Confounders.** Species, source, country, definition and sampling time are fully aliased. The package can say that timing or definition is a sufficient explanation. It cannot say that species is the cause. WBC is a SIRS criterion, so the S-CB017 label is partly defined by inflammation.
- **Stability.** Bootstrap by dog. Repeat with floor values set to half the floor and with rank-only statistics.
- **Main risk.** Floor values. DS02 has daily samples, so it cannot show a 6 to 8 h effect directly.
- **Outputs.** `out/contrasts.csv`, `out/perturbation.csv`, `out/ds02_courses.csv`, `report.md`.
- **Do not.** Merge raw concentrations from two files. Use S-CB517 as a second cohort.
