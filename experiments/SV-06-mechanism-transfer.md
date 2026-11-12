# SV-06. Human-to-dog mechanism transfer

| | |
|---|---|
| Wave | a: 0. b: 1 |
| Lane | Literature-based discovery |
| Effort | Medium |
| Working folder | `/experiments/SV-06/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): `DS07` and "Literature inputs".

- **Question.** Which mechanisms linked to severity in malaria, human babesiosis and sepsis have not been measured in dogs with babesiosis? Do any already show in the public proteome?
- **SV-06a, transfer grid.** Depends on nothing. **Parallel:** one sub-agent per family: (1) haemolysis and haem scavenging; (2) endothelium, glycocalyx, angiopoietin; (3) neutrophils, NETs, histones; (4) VWF, ADAMTS13, thromboinflammation; (5) iron and hepcidin; (6) endocrine and metabolic; (7) immune regulation and tolerance.
  - For each mechanism record: the human evidence (HU articles first, then a targeted PubMed search, with DOI links); the canine evidence (search the notes in `/core/articles/` and the texts in `/core/data/markdown/`, then PubMed); whether a canine assay exists; whether a public dataset or stored sample could test it now.
  - Starting counts from a keyword probe of the 444 CB titles and findings (all-text mentions in brackets): angiopoietin 0 (0); glycocalyx or syndecan 0 (0); NETs or cell-free DNA 0 (5); haem oxygenase 0 (0); cell-free haemoglobin 0 (6, Beagles only); haemopexin 1 (CB117, 3 against 3 dogs); VWF or ADAMTS13 1 (CB446); hepcidin or ferritin 1; microbiome 0. A keyword count is a lead, not a finding: confirm each gap in PubMed before it is called a gap.
  - Output: `out/transfer_grid.csv` and a ranked list of at most 10 mechanisms that have strong human evidence, no canine severity data and an available assay.
- **SV-06b, candidate tests in DS07.** Depends on SV-G1. The family is fixed now (found in `B_Proteins.txt` on 2026-11-12): haemoglobin alpha and beta subunits, haptoglobin, lactoferrin, S100A8, histone H4, alpha-2-antiplasmin (SERPINF2), protein C, antithrombin (SERPINC1), complement factor H, CD14. Reasons: haemolysis and scavenging; neutrophil granule proteins were linked to every severe malaria phenotype ([10.1126/scitranslmed.aar3619](https://doi.org/10.1126/scitranslmed.aar3619)); fibrinolytic shutdown with raised alpha-2-antiplasmin activity in *B. rossi* ([10.3389/fvets.2026.1712262](https://doi.org/10.3389/fvets.2026.1712262)); factor H and parasite multiplication ([10.1038/s41564-019-0474-x](https://doi.org/10.1038/s41564-019-0474-x)). Lactoferrin and CD14 were already reported by the source article (CB112): they are positive controls for the pipeline, not discoveries. Haemopexin, VWF, ADAMTS13, angiopoietin-2 and MPO are not in the file.
  - **First step.** The candidates were found by name in the whole table. Confirm that each one is a master protein and note its coverage before the outcome lock opens. Drop a candidate that fails, and say so.
  - **Primary analysis.** Complicated against uncomplicated for each candidate: a plex-stratified rank test (permute labels inside each plex), effect size with interval, false discovery control across the family. Analyse a protein only if it is present in 60% or more of each group; otherwise compare presence with an exact test.
  - **Confounders.** The label is defined partly by haematocrit, urea, creatinine, bilirubin, glucose and lactate. Proteins that follow anaemia or renal injury partly restate the label: say so for the haemoglobin subunits in particular. Age, sex and treatment are not in the file.
  - **Main risk.** 14 against 18 dogs detects about 1.0 SD, or about 1.4 SD after correction for 11 to 12 tests.
- **Outputs.** `out/transfer_grid.csv`, `out/ds07_candidates.csv`, `report.md`.
- **Do not.** Run an untargeted screen of the proteome and report the top hits.
