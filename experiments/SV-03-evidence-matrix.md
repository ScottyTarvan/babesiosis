# SV-03. Severity definition map and marker-evidence matrix

| | |
|---|---|
| Wave | 2 |
| Lane | Cross-study synthesis |
| Effort | Medium (after SV-G2) |
| Working folder | `/experiments/SV-03/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): "Literature inputs" only.

- **Question.** Which markers and host or parasite factors are linked to severity consistently, once definitions are aligned and each cohort is counted once?
- **Background.** According to PubMed, the meta-analyses in this field are of prevalence (for example [10.1002/vms3.1427](https://doi.org/10.1002/vms3.1427)); none of prognostic markers was found. The ten-article pilot has 6 outcome classes and 82 markers, 29 of them in 2 or more articles.
- **Depends on.** SV-G2.
- **Steps.**
  1. Definition map: a table of definition components by article, with species and setting. Report how many independent units use each component, and how often a tested marker is part of the definition.
  2. Evidence matrix: marker by outcome class by species, with the count of independent units by direction (higher, lower, no difference). Mark cells where the marker defines the outcome.
  3. Pool only where 3 or more independent units share species, outcome class and a usable summary. Everything else stays a direction table.
  4. Resolve, or state as unresolved, the conflicts that the syntheses name: IL-8, fibrinogen, aPTT, MDA, SOD and catalase, parasitaemia, platelets against death, lactate.
- **Confounders.** Stratify by species. Setting and definition are moderators. Abstract-only articles are a sensitivity set.
- **Main risk.** Selective reporting of significant markers. Report the share of "not significant" rows by article as a check.
- **Outputs.** `out/definition_map.csv`, `out/evidence_matrix.csv`, `out/pooled.csv`, `report.md`.
- **Do not.** Pool across species. Pool multivariable with univariable effects. Count CB510 and CB511 twice.
