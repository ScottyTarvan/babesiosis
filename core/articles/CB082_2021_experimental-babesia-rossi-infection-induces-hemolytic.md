# Experimental Babesia rossi infection induces hemolytic, metabolic, and viral response pathways in the canine host.

[Back to article index](../index.md)

| Field | Value |
|---|---|
| ID | CB082 |
| Scope label | core canine evidence |
| Authors | Smith RL, Goddard A, Boddapati A, Brooks S, Schoeman JP, Lack J, Leisewitz A, Ackerman H |
| Journal | BMC genomics, 22(1):619 |
| First publication date | 2021-08-16 (online and issue) |
| Date notes | none recorded (a preprint record, PPR292493, also exists in Europe PMC) |
| DOI | [10.1186/s12864-021-07889-4](https://doi.org/10.1186/s12864-021-07889-4) |
| PMID / PMCID | [PMID 34399690](https://pubmed.ncbi.nlm.nih.gov/34399690/) / [PMC8369750](https://pmc.ncbi.nlm.nih.gov/articles/PMC8369750/) |
| Corrections / retractions | none indicated in PubMed record |
| Babesia species | B. rossi (confirmed; inoculum from naturally infected dogs, mono-infection confirmed by PCR and reverse line blot per full text) |
| Host | experimental purpose-bred male Beagles |
| Country / setting | South Africa; Onderstepoort Veterinary Animal Research Unit |
| Study design | experimental infection, longitudinal clinical and whole-blood RNA-seq time course (two inoculum doses) |
| Sample size | 5 infected dogs (2 low-dose, 3 high-dose); 8 days follow-up |
| Cohort identifier | CH09 — Onderstepoort experimental B. rossi Beagle infection (6 male Beagles: 1 donor, 3 high-dose, 2 low-dose) (see [research map](../research-map.md#cohorts)) |
| Primary category | INF — inflammation/immunity/acute phase/immunopathology (NLP, high confidence; agent label was OXO) |
| Secondary tags | none (NLP) |
| Dataset status | verified download — [DS06](../datasets.md#ds06); verified download — [S-CB082](../datasets.md#s-cb082) |

## Abstract-derived summary

Natural B. rossi cases cannot reveal infection onset or inoculum size, so the authors infected five dogs under controlled conditions: two received about 10^4 parasites and three about 10^8. Dogs were followed for eight days, with diminazene given on day 4. Clinical and laboratory variables were recorded daily, and whole-blood mRNA was sequenced at days 0, 1, 3, 4, 6 and 8. The model reproduced anaemia, acidosis, inflammation and behavioural change, with onset and severity scaling with dose. Differential expression, clustering and enrichment analyses pointed to genes tied to haemolysis, metabolic shifts, and innate, adaptive and antiviral-type immune responses. The authors present this as a large-animal model of severe haemoprotozoal disease for studying host-parasite biology and testing anti-disease therapies.

## Critical interpretation

- **Evidence type:** mechanistic (experimental)
- **Authors' conclusion:** The work characterises clinical and transcriptomic progression of B. rossi infection and establishes a large mammalian model of severe haemoprotozoal disease.
- **Reviewer interpretation:** Provides time-resolved host transcriptome data with a known inoculum, linking haemolysis, metabolic change and interferon/antiviral-type responses to dose-dependent severity. Enrichment results are hypothesis-generating; whole-blood expression conflates per-cell regulation with changes in cell composition (erythroid, reticulocyte, leukocyte), and does not itself demonstrate causal mechanisms.
- **Key limitations (from available information):** very small groups (n=2 and n=3); no uninfected parallel controls (day 0 baseline only); one high-dose dog died on day 4; diminazene and transfusion from day 4 confound later time points; acute course may resemble transfusion-associated rather than tick-borne infection; one text inconsistency in inoculum (10^8 vs 10^9).

_Abstract-level appraisal; not a formal risk-of-bias assessment._

## Evidence basis

- **Abstract:** PubMed record ([PMID 34399690](https://pubmed.ncbi.nlm.nih.gov/34399690/)), accessed 2026-10-23
- **Full text:** checked ([Europe PMC XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8369750/fullTextXML); first ~100,000 of ~192,000 characters read)
- **Supplementary material:** checked; Additional file 1 (MultiQC mapping summary), Additional file 2 (genes differentially expressed on every day, with cluster assignments), Additional file 3 (erythroblast transcript vs reticulocyte count correlations), Additional file 4 (top GO/Reactome pathways per day and cohort); summary-level, not per-dog data
- **Repository records:** GEO [GSE167201](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE167201); code at GitHub rlsmith1/Babesia_RNAseq
- **Information beyond the abstract:**
  - Six purpose-bred male Beagles (five infected, one splenectomised donor); University of Pretoria ethics approval V003-18 (full text).
  - Cryopreserved inoculum from natural cases, passaged through the donor dog (full text).
  - 13-analyte Luminex cytokine panel; Illumina NovaSeq 100 bp paired-end RNA-seq (full text).
  - 1,614 (low) and 2,455 (high) unique DEGs; one high-dose death day 4 (full text).
  - Experimental dates and overlap with earlier publications not reported (full text).
