# SV-06b spec: candidate mechanism tests in the DS07 serum proteome

Frozen 2026-11-12 before `shared/tidy/DS07.outcomes.json` was opened. Written from `shared/tidy/DS07.features.json`, `/core/data/raw/DS07/B_Proteins.txt` and `B_ProteinGroups.txt` (no labels), the package file `/experiments/SV-06-mechanism-transfer.md`, and part a's hand-over `a/out/candidates_for_partb.json`.

Experiment code: `SV-06-02-ds07-candidate-tests`. Method: `proteome_candidate_test`. Role: `primary`. Dataset DS07, independent source SRC-C, *B. rossi*, one source. Seed 20261112.

## 1. Question and hypothesis

Do the serum proteins of mechanisms linked to severity in human disease (haemolysis and haem scavenging, neutrophil granule proteins and histones, fibrinolysis and anticoagulant consumption, complement regulation) differ between complicated and uncomplicated *B. rossi* babesiosis in DS07? Hypothesis: at least one mechanism candidate (not a positive control) differs at q < 0.05.

## 2. Candidate list (fixed by the package file; master check done before the lock)

The family of 11 named proteins is fixed by the package file. Part a mapped it to accessions. The master check was run on `B_Proteins.txt` (column `Master`) and, for candidate-only rows, by finding the master protein whose 66 grouped abundances are identical (same protein group, same quantity). No label was used.

| # | Candidate | Mechanism (part a) | DS07 quantity used | Master check | Coverage % | Unique peptides | Infected dogs with a value (no label) | In family |
|---|---|---|---|---|---|---|---|---|
| 1 | Haemoglobin beta | F1-01 cell-free Hb | P60524 (HBB) | master | 45 | 6 | 32/32 | yes |
| 2 | Haemoglobin alpha | F1-01 | P60529 is a candidate only; its group master is J9NXL3 (LOC100855558, "Uncharacterized protein") | **fails** | 31 (P60529) | 2 | 32/32 (J9NXL3) | **no**: secondary, descriptive |
| 3 | Haptoglobin | F1-03 | P19006 and G1K2D9 are candidates only; the group master A0A5F4DB38 has the same gene symbol (LOC479668, the gene of G1K2D9 "Haptoglobin") and identical abundances | passes through the gene symbol of the group master | 16 | 6 | 32/32 | yes (quantity of the haptoglobin protein group) |
| 4 | Lactoferrin | F3-03, positive control | F1PR54 (LTF) | master | 6 | 3 | 31/32 | yes |
| 5 | S100A8 | F3-03, F3-12 | C0LQL0 (S100A8) | master | 9 | 1 | 26/32 | yes |
| 6 | Histone H4 | F3-02 | L7N0L3 (H4C7) | master | 11 | 1 | 6/32 | yes |
| 7 | Alpha-2-antiplasmin | F4-03 | E2R4V3 (SERPINF2) | master | 26 | 8 | 32/32 | yes |
| 8 | Protein C | F4-04 | Q28278 (PROC) | master | 4 | 2 | 16/32 | yes |
| 9 | Antithrombin | F4-04 | E2RES2 (SERPINC1) | master | 18 | 7 | 32/32 | yes |
| 10 | Complement factor H | F7-12 | A0A5F4BVG1 (CFH) | master | 15 | 13 | 32/32 | yes |
| 11 | CD14 | F7-05, positive control | A0A1S7J0A8 (GN 607076) | master | 11 | 4 | 32/32 | yes |

**Family for false discovery control: 10 proteins** (all but haemoglobin alpha). Haemoglobin alpha fails the master check (its group master has no stated identity) and is dropped from the family, as the package file says; it is reported once as a secondary, descriptive result through J9NXL3, outside the family.

Quality flags carried into the report: S100A8 and histone H4 rest on 1 unique peptide (H4: 2 PSMs); protein C on 2 peptides and 5 PSMs. CB112 reported only proteins with 2 or more unique peptides, so S100A8 and H4 were outside its list.

## 3. Missing values are plex-level, not dog-level

In every candidate, a value is missing for all dogs of a plex or for none (checked without labels: H4 is observed only in plexes B1 and B9; protein C only in B2, B5, B6, B7, B10; S100A8 is missing in B1 and B9; lactoferrin in B11). A presence test therefore tests how the groups were placed in plexes, not biology.

**Rule (sharpens the package file's presence rule).**

- A protein observed in 60% or more of each group: plex-stratified rank test (section 4) on all observed infected dogs.
- A protein observed in less than 60% of a group: the presence comparison (Fisher exact test, two-sided) is reported, labelled as a plex-allocation check, and is **not** counted in the family. The protein's family test is the plex-stratified rank test on the observed dogs only, if each group has at least 3 observed dogs; it is flagged "low coverage" with its detectable effect. With fewer than 3 in a group the protein gets no test and counts as untested (the family size stays 10 for BH; an untested protein gets q = null).

## 4. Primary analysis

For each family protein, complicated against uncomplicated, infected dogs only (controls not used in the primary test):

- Value: the tidy log2 ratio to the plex standard.
- Effect size: Cliff's delta (P(complicated > uncomplicated) − P(complicated < uncomplicated)) over all observed pairs; and the Hodges-Lehmann shift (median of pairwise differences, complicated minus uncomplicated, log2 units).
- p-value: permutation of the labels **inside each plex** (the number of complicated dogs in each plex is kept), 10,000 permutations, two-sided on |delta|, p = (1 + count) / (1 + 10,000). One random generator (numpy PCG64, seed 20261112) re-created for each protein, so each protein's p does not depend on the order of the family.
- 95% interval: 2,000 bootstrap resamples of dogs, stratified by label (resample complicated and uncomplicated dogs separately, with replacement), percentile interval, for delta and for the HL shift. Seed 20261112 + protein index.
- False discovery: Benjamini-Hochberg over the 10 family proteins (untested proteins count in the family size).
- Detectable effect: 14 vs 18 dogs, about 1.0 SD at alpha 0.05, about 1.4 SD at alpha 0.005 (the first BH step for 10 tests). Reported per protein from the observed n.

Expected directions, for interpretation only (the tests are two-sided): haemoglobin beta higher and haptoglobin lower in complicated (haemolysis, scavenger consumption); lactoferrin, S100A8, histone H4 higher (neutrophil activation; LTF higher is the CB112 finding); alpha-2-antiplasmin higher (fibrinolytic shutdown); protein C and antithrombin lower (consumption); CD14 higher (CB112); factor H no stated direction.

## 5. Positive controls

Lactoferrin and CD14 were reported higher in complicated dogs by CB112 (same data; already seen). The pipeline is **consistent** with the source article if both have delta > 0. If either is ≤ 0, the report flags the pipeline (plex mapping, value construction) before any other result is read. Their q-values count in the family but they are not discoveries.

## 6. What counts against the hypothesis

- Against: no mechanism candidate (rows 1, 3, 5, 6, 7, 8, 9, 10) reaches q < 0.05. Because the study detects only about 1.4 SD after correction, this is "not shown", not "absent": the report states the detectable effect next to each null.
- For (weakly): one or more mechanism candidates with q < 0.05. For the haemoglobin and haptoglobin group, a positive result partly restates the label (the complicated definition includes anaemia and laboratory thresholds); it is not evidence of a mechanism beyond haemolysis.

## 7. Stability and sensitivity checks (not in the family)

- S1. Unstratified permutation (labels permuted across all infected dogs), same statistic.
- S2. Leave-one-plex-out: delta recomputed with each plex removed; report the range and whether the sign changes.
- S3. Infected against controls, plex-stratified permutation (context: whether the protein moves with infection at all). Reported, not corrected; the 20 controls are not part of the hypothesis.
- S4. Haemoglobin alpha through J9NXL3: same test as the family, outside the family.
- S5. Tracking of free haemoglobin: Spearman rho of each candidate with haemoglobin beta among the 32 infected dogs (no labels), to say which candidates move with haemolysis.
- S6. Repeat run: delete `out/` and run again; the numbers must be the same.

## 8. Confounders that cannot be handled

The label is defined partly by haematocrit, urea, creatinine, bilirubin, glucose and lactate (CB112). No covariates are in the files (no age, sex, treatment, time from onset, haemolysis index of the sample). The pooled standard of each plex contains serum of all dogs. DS07 may share dogs with DS04 (and through it, 3 S-CB050 dogs) by case number (SV-07, unverified); this does not change a within-DS07 test. DS07 is the only proteome: no replication.

## 9. Not done

No untargeted screen of the proteome and no ranking of other proteins (package file, "Do not"). No predictive model. No pooling with another file.
