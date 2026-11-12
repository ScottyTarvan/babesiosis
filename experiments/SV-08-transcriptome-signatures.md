# SV-08. Human severity signatures in the Beagle transcriptome

| | |
|---|---|
| Wave | 1 |
| Lane | Exploratory ML and omics |
| Effort | Medium |
| Working folder | `/experiments/SV-08/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): `DS06`, `DS02`.

- **Question.** Do the blood signatures of severe malaria appear in the Beagles before clinical deterioration, and earlier at the high dose?
- **Depends on.** SV-G1 (DS02 tidy file). This package tidies DS06 itself.
- **Gene sets, fixed now** (map to dog gene symbols; report every gene that does not map):
  - Neutrophil granule: MPO, ELANE, CTSG, LTF, LCN2, MMP8, MMP9, CAMP, OLFM4, CEACAM8, ARG1.
  - Type 1 interferon: IFI44, IFI44L, IFIT1, IFIT3, ISG15, MX1, MX2, OAS1, OAS2, RSAD2, CXCL10.
  - Composition control (erythroid): ALAS2, HBB, SLC4A1.
- **Steps.** Rank genes inside each sample; score each set by its mean rank; plot score against day and against parasitaemia for each dog. Report the erythroid score beside the others, because the day 3 and day 4 libraries shift to reticulocyte transcripts.
- **Primary analysis.** The within-dog change in each score from day 0 to the last sample before treatment, with the 5 dogs shown one by one. No test across dogs beyond a sign count.
- **Confounders.** Dose is aliased with dog. Days 6 and 8 follow treatment. The DS06 to DS02 dog mapping is unverified (SV-07 step 4).
- **Main risk.** Five dogs show a pattern, never a rate. The human signatures may not transfer.
- **Outputs.** `out/set_scores.csv`, `out/unmapped_genes.csv`, `report.md`.
- **Do not.** Train a classifier. Run a genome-wide differential expression screen and report top genes.
