# SV-06a spec: human-to-dog mechanism transfer grid

Version 1, 2026-11-12. Frozen before any work on the grid. Part a opens no outcomes file (no dog-level labels are used), so the outcome lock has no file to guard; the hash is recorded anyway.

## Question

Which mechanisms linked to severity in falciparum or knowlesi malaria, human babesiosis and sepsis have not been measured against severity in dogs with babesiosis, have a canine assay, and could be tested now in a public file or stored samples?

## Experiment

One experiment: `SV-06-01-transfer-grid`, method `mechanism_transfer_grid`, role `descriptive`. No statistical test.

## Families and seed mechanisms

One sub-agent per family. Each family starts from the seed list below. A sub-agent may add at most 3 mechanisms of its own, and must say which are added.

| Family | Seeds |
|---|---|
| F1 Haemolysis and haem scavenging | cell-free haemoglobin; free haem and haemopexin depletion; haptoglobin depletion; haem oxygenase-1; nitric oxide scavenging and arginine / ADMA |
| F2 Endothelium, glycocalyx, angiopoietin | angiopoietin-2 and the Ang-2/Ang-1 ratio; glycocalyx shedding (syndecan-1, heparan sulfate, hyaluronan); soluble adhesion molecules (ICAM-1, VCAM-1, E-selectin); VEGF and soluble VEGFR-1 |
| F3 Neutrophils, NETs, histones | NETs (cell-free DNA, MPO-DNA, citrullinated histone H3); circulating extracellular histones (host and parasite); neutrophil granule proteins (MPO, elastase, lactoferrin, NGAL, S100A8/A9) |
| F4 VWF, ADAMTS13, thromboinflammation | VWF antigen and ultra-large multimers, ADAMTS13 activity and the VWF/ADAMTS13 ratio; platelet activation (soluble P-selectin, platelet factor 4); fibrinolytic shutdown (PAI-1, alpha-2-antiplasmin); protein C and thrombomodulin |
| F5 Iron and hepcidin | hepcidin; ferritin; serum iron and transferrin (iron restriction); lipocalin-2 iron sequestration (cross-reference F3) |
| F6 Endocrine and metabolic | adrenal (cortisol, cortisol:ACTH, adrenal androgens); thyroid (euthyroid sick); lactate and hypoglycaemia; kynurenine pathway; copeptin / vasopressin |
| F7 Immune regulation and tolerance | IL-10 and the IL-10/TNF balance; regulatory T cells and T-cell exhaustion (PD-1, PD-L1); monocyte deactivation (HLA-DR / DLA-DR); soluble TREM-1 and suPAR; soluble CD14 (presepsin) |

## What each mechanism row records

Fixed fields (the column list of `out/transfer_grid.csv`):

- `mechanism_id` (`F1-01` …), `family`, `mechanism`, `added_by_agent` (yes/no).
- **Human evidence**: `human_conditions` (malaria, babesiosis, sepsis), `hu_articles` (IDs of HU001–HU027 that bear on it), `human_key_dois` (up to 4 DOI links from a targeted PubMed search), `human_n_studies` (independent human cohorts linking it to severity or death that the agent found), `human_grade` (rule below), `human_direction` (what goes with severity).
- **Canine evidence**: `cb_note_hits` and `cb_text_hits` (article IDs from the local keyword search of `/core/articles/` CB notes and `/core/data/markdown/` CB texts; produced by `scripts/local_search.py`, not by the agent), `cb_confirmed` (CB articles the agent read and confirmed measure the mechanism in babesiosis), `canine_pubmed` (PubMed query string and the DOIs of any dog babesiosis study found), `canine_status` (rule below).
- **Assay**: `canine_assay` (rule below) with `assay_evidence` (DOI of a canine validation or canine use).
- **Test now**: `dog_genes` (canine gene symbols), `ds07_master` (master-protein accessions in DS07 `B_Proteins.txt`; from `scripts/reference_lookup.py`), `ds06_genes` (Ensembl IDs present in DS06 counts), `ds02_measured` (variable in DS02, if any), `testable_now` (rule below).
- `gap` (yes/no), `rank` (1–10 or empty), `notes`.

## Rules (fixed now)

- `human_grade`: **3** = 3 or more independent human cohorts, or a meta-analysis, link it to severity or death in at least one condition; **2** = 2 cohorts, or 1 cohort of 100 or more patients; **1** = one small cohort, or mechanistic or animal-model evidence only; **0** = none found.
- `canine_status`: **none** = no study of dogs with babesiosis measured it; **measured_no_severity** = measured in infected dogs (against controls or over time) but not against a severity or outcome contrast; **severity_tested** = at least one dog babesiosis study compared it by severity or outcome (give the count of independent units, using `/core/cohorts.json` where the article is in the review).
- `canine_assay`: **validated** = a published canine validation of an assay (or a canine-specific commercial kit with published canine use); **used_in_dogs** = measured in dogs with a cross-reactive or generic method (for example cfDNA fluorometry, colourimetric haem) without a formal validation; **none** = no canine measurement found.
- `testable_now`: **public_file** = the protein is a master protein in DS07, or the gene is in DS06, or the variable is in DS02; **stored_samples_only** = assay exists, no public file has it (archived serum such as DS07's would be needed); **no** = no assay and no file.
- `gap` = yes when `canine_status` is `none` or `measured_no_severity`, confirmed by a PubMed search (keyword counts alone are not enough).
- **Ranked list**: eligible rows have `gap` = yes, `human_grade` ≥ 2 and `canine_assay` ≠ none. Order by human grade (high first), then assay (validated before used_in_dogs), then `testable_now` (public_file, then stored_samples_only), then fewer canine studies (none before measured_no_severity), then `mechanism_id`. At most 10. If fewer than 10 are eligible, the list is shorter: that is a result.
- **What would count against the premise**: if most grade-3 human mechanisms already have canine severity data, the "unmeasured mechanism" line is weak. Report the share of grade ≥ 2 mechanisms that are gaps.

## Local search (deterministic)

`scripts/local_search.py` searches, for each mechanism, a fixed keyword list (word-boundary, case-insensitive regex) in (a) the 444 CB notes in `/core/articles/` and (b) the CB texts in `/core/data/markdown/`. It writes hit article IDs and counts. The keyword lists are in `scripts/mechanisms.json`, written before the search is run. A hit is a lead; the sub-agent confirms or rejects it.

## Hand-over to part b

`out/candidates_for_partb.json`: every mechanism with its dog gene symbols, DS07 master accessions and DS06 Ensembl IDs, the gap and rank fields. Part b's analysis family is fixed in the package file; this list does not change it. It tells part b which proteins of its family map to which mechanism, and which ranked gaps are or are not in DS07.

## Limits

- PubMed only, abstracts mostly; a gap means "not found in PubMed and the local corpus on 2026-11-12".
- No article text in outputs beyond short identifiers. No user details in queries.
- Agents' grades are judgements; the grid records the DOIs behind each.
