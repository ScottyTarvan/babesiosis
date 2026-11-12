# SV-05. Age, sex and neuter status in *B. rossi*

| | |
|---|---|
| Wave | 1 |
| Lane | Within-dataset statistics with cross-source replication |
| Effort | Small |
| Working folder | `/experiments/SV-05/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): `S-CB050`, `DS05`, `DS03`.

- **Hypothesis.** Age changes the form of severe disease (anaemia-dominant in young dogs, inflammatory in adults) more than it changes overall risk.
- **Background.** Young *B. canis* dogs had higher parasitaemia and worse anaemia (CB123, [10.1016/j.vetpar.2024.110197](https://doi.org/10.1016/j.vetpar.2024.110197)). Gonadectomy lowered the risk of severe disease, RR 0.72 (CB125, [10.1016/j.prevetmed.2024.106293](https://doi.org/10.1016/j.prevetmed.2024.106293)). Toy breeds had lower odds of diagnosis ([10.1111/j.1939-1676.2011.00779.x](https://doi.org/10.1111/j.1939-1676.2011.00779.x)).
- **Depends on.** SV-G1. Step 3 also reads `SV-04/out/perturbation.csv` and waits for it; the other steps do not. Optional input: pseudo-stage from SV-01.
- **Primary contrast, fixed now.** Dogs under 12 months against dogs of 12 months or more.
- **Steps.**
  1. S-CB050: death by age group (Fisher exact test, odds ratio with exact interval; then stratified by sex). Secondary: age in months by outcome (rank test).
  2. DS05 and DS03 natural, separately: haematocrit by age group (Hodges-Lehmann difference with bootstrap interval). DS05 and S-CB050: band neutrophils by age group.
  3. Form: in S-CB050 cohort 1, the SV-04 perturbation score by age group. In DS05, the share of dogs with severe anaemia and the share with a left shift, by age group.
  4. DS05: illness duration by age group, to check whether young dogs present earlier.
  5. Show the same contrast from each source side by side. Do not pool DS03 with S-CB050.
- **Confounders.** Species and country are fixed. Age stands in for prior exposure, breed and size, which are not measured. Sex differs between cases and controls in SRC-A. Only 7 DS05 dogs are neutered: describe them, do not test.
- **Main risk.** 15 deaths: only an odds ratio near 3 or more is detectable. The age medians by outcome in S-CB050 have been seen (see "Outcome lock" in [rules.md](rules.md)), so step 1 is exploratory.
- **Outputs.** `out/age_contrasts.csv`, `report.md`.
