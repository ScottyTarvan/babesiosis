# SV-09. Phenotype axes replicated across sources

| | |
|---|---|
| Wave | 2 |
| Lane | Exploratory ML |
| Effort | Medium |
| Working folder | `/experiments/SV-09/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): `DS05`, `DS03`, `S-CB017`, `S-CB050`.

- **Question.** After the anaemia axis and the stage of disease are removed, is there a second reproducible axis, and does it relate to a real outcome?
- **Depends on.** SV-G1 and SV-01.
- **How it differs from the old EXP02.** Axes, not clusters. It conditions on the dominant axis and on pseudo-stage. It tests whether loadings recur in an independent file. It relates scores to a real label.
- **Steps.**
  1. DS05: principal components of the admission variables after regressing out haematocrit and pseudo-stage. Choose the number of components by parallel analysis.
  2. Replication of loadings by Tucker's congruence coefficient with bootstrap intervals: red cell block in DS03; leukocyte and platelet block in S-CB017; WBC, segmented and band neutrophils in S-CB050.
  3. Score the replicated axis in S-CB050 and S-CB017 and relate it to death and to the complicated label by permutation.
- **Confounders.** Compare the *B. rossi* files with each other first. Report S-CB017 (*B. canis*) separately as a transfer check. WBC is part of the S-CB017 label.
- **Main risk.** Only three leukocyte variables are shared with a hard outcome, so the result may restate the published band-neutrophil finding. Say so if it does.
- **Outputs.** `out/loadings.csv`, `out/congruence.csv`, `out/axis_outcome.csv`, `report.md`.
