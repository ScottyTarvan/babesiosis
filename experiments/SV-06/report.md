# SV-06 report: human-to-dog mechanism transfer

Package file: [/experiments/SV-06-mechanism-transfer.md](../SV-06-mechanism-transfer.md). The package has two parts, each with its own section below. Each part keeps its own spec, scripts, environment and outputs in its sub-folder (`a/`, `b/`).

| Part | Experiment code | Method | Status | Section |
|---|---|---|---|---|
| a, transfer grid | `SV-06-01-transfer-grid` | `mechanism_transfer_grid` | Done 2026-11-12 | [Part a](#part-a-sv-06a-human-to-dog-transfer-grid) |
| b, candidate tests in DS07 | `SV-06-02-ds07-candidate-tests` | `proteome_candidate_test` | Done 2026-11-12 | [Part b](#part-b-sv-06b-candidate-tests-in-ds07) |

---

## Part a (SV-06a): human-to-dog transfer grid

Experiment `SV-06-01-transfer-grid` (method `mechanism_transfer_grid`, role `descriptive`). Run 2026-11-12. Spec: [a/spec.md](a/spec.md), SHA-256 `93fc808887e8b5b42ee269ec3851d148553502a6446e2417daad4b860d76b6b2`. No outcomes file was opened ([a/exposure.md](a/exposure.md)); no statistical test.

**For part b:** the machine-readable list is [`a/out/candidates_for_partb.json`](a/out/candidates_for_partb.json). It holds every mechanism with its dog gene symbols, DS07 accessions (status `master` or `master_candidate`), DS06 Ensembl IDs, DS02 variables, gap and rank, plus `partb_family_map`, which maps each protein of part b's fixed family to the grid mechanisms. Section a.9 lists what part b needs to know.

### a.1 Question and hypothesis

Which mechanisms linked to severity in malaria, human babesiosis and sepsis have not been measured against severity in dogs with babesiosis, have a canine assay, and could be tested now? Premise: most mechanisms with good human evidence (grade 2 or 3) are unmeasured in dogs; the premise is weak if most of them already have canine severity data.

### a.2 Inputs

| Input | SHA-256 (first 12) |
|---|---|
| `a/spec.md` | `93fc808887e8` |
| `a/scripts/mechanisms.json` (29 seeds, keyword lists, gene symbols) | `7bced0d0f9b8` |
| `a/families/F1.json` … `F7.json` (sub-agent rows) | F1 `f3ded0f8f6fc`, F2 `d35507ea65ae`, F3 `9fc7792af70e`, F4 `14fa9a3d2bc4`, F5 `f20cacb9be77`, F6 `142913bc3c97`, F7 `91908069612e` |
| `a/families/BRIEF.md` (the sub-agent brief) | `63ec4bdb8cf5` |
| `/core/articles/CB*.md` (444 notes), `/core/data/markdown/CB*.md` (503 texts, 234 not abstract-only), `/core/articles/HU0*.md` (27) | read, not hashed |
| `/core/data/raw/DS07/B_Proteins.txt` (protein list only; no abundance used) | `2fc5d617dea4` |
| `/core/data/raw/DS06/GSE167201_raw_counts.txt.gz` (gene IDs only) | `b2575d138ca0` |
| `/experiments/shared/tidy/DS02.features.json` (variable names only) | `12475e823e58` |
| PubMed (MCP search server), searched 2026-11-12 | queries in `a/out/transfer_grid.csv` |

Also used: `/experiments/SV-G2/associations_v2.csv`, `/experiments/SV-03/report.md` §4 and the SV-07 link table (DS07 = the CB112 proteome; the B. rossi endocrine units are all Onderstepoort).

Scripts: `a/scripts/local_search.py` (`0e3b9b7462ad`), `a/scripts/assemble.py` (`36aa3b8d9577`), `a/scripts/write_db.py` (`0b1724a00525`). Python 3.12.12 (uv 0.10.4), standard library; pyodbc 5.2.0 for the writer only. No random numbers.

### a.3 What was done

1. **Seed list and local search (scripted).** 29 seed mechanisms in 7 families, with keyword regexes and canine gene symbols, were fixed in the spec and in `mechanisms.json` before the search. `local_search.py` counts keyword hits in the CB notes and texts and looks up each mechanism's proteins in DS07 (master proteins and master-protein candidates, by `GN=` symbol or description prefix) and its genes in DS06.
2. **Seven sub-agents, one per family** (Claude, general-purpose), each with `families/BRIEF.md` and the spec. Each one:
   - graded the human evidence (HU notes first, then 3 to 6 targeted PubMed queries per mechanism);
   - read the local hits, confirming or rejecting each CB article as a real measurement in dogs with babesiosis, with or without a severity contrast;
   - searched PubMed for dog babesiosis studies and for canine assays;
   - wrote one JSON file. Agents could add up to 3 mechanisms each; 8 were added.
3. **Assembly (scripted).** `assemble.py` merges the family files and recomputes three things from the spec's rules rather than taking the agents' values: `gap` (canine status `none` or `measured_no_severity`, with a PubMed query recorded), `testable_now` (from the lookups) and the rank. It also writes the hand-over file and the database load file. Two agents' `testable_now` values differed from the rule; the rule was used, and the differences are logged by the script:
   - F1-03 haptoglobin is only a DS07 master-protein *candidate*;
   - F1-11 ADMA has DDAH genes in DS06.
4. `write_db.py` writes the experiment row and 5 result rows in one transaction (way A).
5. Re-run check: `out/` was deleted and rebuilt. All six output files were byte-identical.

**Deviations from the spec**

- **D1. Lookup aliases.** After the keyword lists were frozen but before the grid was assembled, I added `ds07_desc` (protein-name prefixes) to `mechanisms.json`. Many DS07 proteins have no usable `GN=` symbol (CD14 is `GN=607076`, haptoglobin `GN=LOC479668`). This changes the DS07 lookup only, not the keyword search.
- **D2 (post hoc, added after the primary ranking was seen). Sensitivity ranking that does not count DS06.** The spec counts any DS06 gene as `public_file`. DS06 holds 12,362 genes, so almost every mechanism qualifies, and the test-now tie-break says little. I therefore also ranked with DS06 not counted. The primary ranking is unchanged, and the sensitivity ranking is labelled post hoc in the payload and on the page.
- **D3. Extra column.** I added the column `severity_contrast_testable_now`. It is `yes` only when the protein is a DS07 master protein: DS07 is the only public file with a severity label and circulating protein.
- **D4. Agent-added rows that overlap seeds.** F7-11 (soluble TREM-1) was split out of seed F7-04 (sTREM-1 and suPAR), because only suPAR has canine severity data (CB004). F3-11 and F3-12 split released MPO/elastase and calprotectin out of seed F3-03, which counts as "tested" only through MPXI (cellular granule content) and NGAL (largely renal). Some evidence is therefore counted under two rows. The seeds are kept as written.
- **D5. Missed local hits.** The keyword search missed CB073 (iron, a real severity contrast) and CB412 (serum haemoglobin). The agents found and added both. Keyword counts in the grid are leads only, as the spec says.
- `n_subjects` is 0: no dog-level data were used.

### a.4 Results

**Primary: the grid** ([`a/out/transfer_grid.csv`](a/out/transfer_grid.csv), 37 rows)

- **37 mechanisms**: 29 seeds plus 8 added by agents.
- **21 are gaps.** 12 were never measured in dogs with babesiosis. 9 were measured only against healthy controls or over time.
- **16 already have canine severity or outcome data.**
- **Premise holds, moderately.** 21 of 36 mechanisms with human grade 2 or 3 are gaps (58%).
- **Negative part.** 10 of the 26 grade-3 mechanisms already have canine severity data. The well-studied lines are:
  - lactate and hypoglycaemia: 8 units;
  - cortisol: 5 units;
  - thyroid: 5 units;
  - IL-10/TNF: 5 units;
  - protein C, antithrombin and thrombomodulin: 4 units;
  - iron and transferrin: 4 units;
  - fibrinolysis: 2 units.
  These lines are not "unmeasured mechanisms", and the transfer premise does not apply to them.
- Every gap with human grade 2 or more has some canine assay, so all 21 gaps meet the ranking rule. The rank therefore comes from the tie-breaks.

| Family | Mechanisms | Never measured | Measured, no severity | Severity tested | Gaps | In top 10 |
|---|---|---|---|---|---|---|
| F1 Haemolysis and haem scavenging | 7 | 2 | 3 | 2 | 5 | 1 |
| F2 Endothelium, glycocalyx, angiopoietin | 4 | 3 | 0 | 1 | 3 | 2 |
| F3 Neutrophils, NETs, histones | 6 | 4 | 0 | 2 | 4 | 4 |
| F4 VWF, ADAMTS13, thromboinflammation | 5 | 0 | 2 | 3 | 2 | 1 |
| F5 Iron and hepcidin | 3 | 0 | 1 | 2 | 1 | 1 |
| F6 Endocrine and metabolic | 5 | 1 | 1 | 3 | 2 | 1 |
| F7 Immune regulation and tolerance | 7 | 2 | 2 | 3 | 4 | 0 |

**Ranked gaps** ([`a/out/ranked_gaps.csv`](a/out/ranked_gaps.csv)). The rule, fixed in the spec: a gap, human grade 2 or more and a canine assay, ordered by human grade, then assay, then test-now, then fewer canine studies.

| Rank | Mechanism | Human grade (cohorts) | Dogs with babesiosis | Canine assay | Testable now | Key human DOI | Canine assay DOI |
|---|---|---|---|---|---|---|---|
| 1 | Angiopoietin-2, Ang-2/Ang-1 | 3 (6) | never measured | validated | DS06 RNA only | [10.1186/s12936-016-1624-8](https://doi.org/10.1186/s12936-016-1624-8) | [10.2460/ajvr.79.8.803](https://doi.org/10.2460/ajvr.79.8.803) |
| 2 | VEGF and soluble VEGFR-1 | 3 (4) | never measured | validated (VEGF only) | DS06 RNA only | [10.1016/j.medcli.2024.03.027](https://doi.org/10.1016/j.medcli.2024.03.027) | [10.1892/0891-6640(2006)20[144:eavegf]2.0.co;2](https://doi.org/10.1892/0891-6640(2006)20[144:eavegf]2.0.co;2) |
| 3 | NETs (cfDNA, MPO-DNA, H3Cit) | 3 (6) | never measured | validated | DS06 RNA only (PADI4) | [10.1093/infdis/jiy661](https://doi.org/10.1093/infdis/jiy661) | [10.1111/vec.12592](https://doi.org/10.1111/vec.12592) |
| 4 | Circulating histones | 3 (5) | never measured | validated | **DS07 master** L7N0L3 histone H4 (11%) | [10.1182/bloodadvances.2019001258](https://doi.org/10.1182/bloodadvances.2019001258) (HU021) | [10.1007/s12192-017-0817-6](https://doi.org/10.1007/s12192-017-0817-6) |
| 5 | Calprotectin (S100A8/A9), S100A12 | 3 (5) | never measured | validated | **DS07 master** C0LQL0 S100A8 (9%) | [10.3389/fcimb.2026.1934020](https://doi.org/10.3389/fcimb.2026.1934020) | [10.2460/ajvr.69.7.845](https://doi.org/10.2460/ajvr.69.7.845) |
| 6 | VWF, ultra-large multimers, ADAMTS13 | 3 (4) | measured vs controls (CB446, lower) | validated | DS06 RNA only | [10.1371/journal.ppat.1000349](https://doi.org/10.1371/journal.ppat.1000349) (HU009) | [10.1177/1040638714523609](https://doi.org/10.1177/1040638714523609) |
| 7 | Ferritin | 3 (4) | measured, no difference 7 vs 7 (CB242) | validated | DS06 RNA only | [10.1186/s12879-026-13418-z](https://doi.org/10.1186/s12879-026-13418-z) | [10.1016/j.rvsc.2016.09.003](https://doi.org/10.1016/j.rvsc.2016.09.003) |
| 8 | Kynurenine pathway | 3 (4) | measured vs controls (CB091, B. canis) | validated | DS06 RNA only | [10.1086/650996](https://doi.org/10.1086/650996) | [10.1177/10406387261447261](https://doi.org/10.1177/10406387261447261) |
| 9 | Released plasma MPO and elastase | 3 (4) | never measured | validated | stored samples only | [10.1128/mBio.01300-15](https://doi.org/10.1128/mBio.01300-15) (HU005) | [10.2460/ajvr.68.6.584](https://doi.org/10.2460/ajvr.68.6.584) |
| 10 | Haem oxygenase-1 | 3 (4) | never measured | used in dogs | DS06 RNA only | [10.1371/journal.ppat.1002579](https://doi.org/10.1371/journal.ppat.1002579) | [10.1016/j.imbio.2016.12.006](https://doi.org/10.1016/j.imbio.2016.12.006) |

The following gaps meet the rule but fall below the cut of 10, in rank order:

- glycocalyx shedding;
- Tregs and PD-1/PD-L1;
- soluble TREM-1;
- cell-free haemoglobin;
- monocyte DLA-DR;
- copeptin;
- soluble EPCR;
- haptoglobin;
- ADMA;
- haem and haemopexin;
- complement factor H.

**Testable now.** Only 2 of the top 10 can be tested in a public file with a severity label: circulating histone H4 and S100A8, both in DS07. The other 8 need stored plasma or serum and a canine assay. "DS06 RNA only" is blood gene expression in 5 experimental Beagles. It is not circulating protein and has no severity contrast.

### a.5 Stability and sensitivity

- **D2, DS06 not counted (post hoc).** The top 10 gains cell-free haemoglobin (DS02 `cfhb` and DS07 HBB) and loses haem oxygenase-1. In this ranking histones and calprotectin move to ranks 1 and 2.
- **Ranking order.** 16 of the 21 gaps are grade 3 and 5 are grade 2, so after the human grade, assay type and test-now decide most positions. The ranks inside the top 10 are not a measure of importance. Membership of the top 10 is the more robust result: 9 of the 10 are in the top 10 under both rankings, and the 9 grade-3 gaps with a validated assay are all inside it.
- **Agent judgement.** The grades are single-agent judgements; no second agent or person checked them. Spot check: three DOIs from 2026 cited by the agents (`fcimb.2026.1934020`, `10406387261447261`, `s12879-026-13418-z`) resolve in PubMed.

### a.6 Confounders and limits that were handled, and those that were not

- **Handled:**
  - Independent units were counted with `/core/cohorts.json`.
  - The Onderstepoort endocrine units may share dogs (F6 note), so their 5 units may be fewer. This does not change their status, `severity_tested`.
  - DS07 = CB112, so DS07 proteins that CB112 already reported (CD14, transferrin, protein C, lactoferrin) are `severity_tested`, not discoveries.
- **Not handled:**
  - Human severity evidence comes from different organisms (P. falciparum, P. knowlesi, B. microti, bacterial sepsis). Cytoadherence-driven mechanisms (VWF, angiopoietin) may not transfer to Babesia.
  - Human severity definitions differ from the canine ones.

### a.7 What this does not show

- That any gap mechanism matters in dogs. The grid says what to measure, not what will be found.
- That a gap is a true gap. One database (PubMed) was searched, mostly through abstracts, on 2026-11-12. About half the CB texts are abstract only. Non-indexed journals were missed: hepcidin's only canine severity study, CB202, is not in PubMed.
- A ranking by importance. The tie-breaks are about practicality.
- Any dog-level result. No test was run.

### a.8 Verified in files, taken from documentation, or inferred

- **Verified in files:**
  - the keyword hits;
  - DS07 master or candidate status and coverage for every listed protein;
  - DS06 gene presence;
  - DS02 variable names;
  - the database rows (check query in a.10).
- **Taken from the literature by agents:**
  - human grades, cohort counts and directions;
  - canine study contents (from notes and texts, often abstracts);
  - assay availability.
  Every one of these has a DOI in the grid.
- **Inferred:** that the PubMed gaps are true gaps, and the grade boundaries.

### a.9 Next step, and decisions for the user

- **For part b:**
  - Histone H4 (L7N0L3 is a master protein; three more H4 entries are candidates) and S100A8 (C0LQL0 master) are the two ranked gaps in DS07. Both are already in part b's fixed family.
  - Haptoglobin and haemoglobin alpha are only master-protein *candidates* in `B_Proteins.txt`, not master proteins.
  - Complement factor H is `GN=CFH`, described as "Uncharacterized protein": match it on the gene symbol (A0A5F4BVG1 is the master, with candidates beside it).
  - CD14 is `GN=607076` (A0A1S7J0A8).
  - Lactoferrin, CD14, transferrin and protein C were already reported by CB112, which is the same data.
- **Stored-sample candidates.** For a new or archived-sample study, the strongest set is: angiopoietin-2, NET markers (cfDNA or nucleosomes; canine nucleosome ELISAs are affected by haemolysis and icterus), VWF:ADAMTS13, ferritin, kynurenine:tryptophan, and plasma MPO and elastase. All of them have canine assays. SV-10 (minimum dataset) may want this list.
- **Open question for the user:** should the grades get a second, independent review (a person or a blind second agent) before SV-INT relies on the ranking?

### a.10 Database and view

- **Database:** `dbo.experiment` and `dbo.experiment_result`, 5 results: `primary_result`, `family_summary`, `transfer_grid`, `partb_handover`, `interpretation`. Written by `a/scripts/write_db.py`; a second run gives the same rows.

  | experiment_code | method | run_at | results | interpretation |
  |---|---|---|---|---|
  | SV-06-01-transfer-grid | mechanism_transfer_grid | 2026-11-12 15:37:37 | 5 | 1 |

- **View:** `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-mechanism-transfer-grid-view.component.{ts,html,scss}`, one import and one entry in `experiment-views.registry.ts`.
  - `npx ng build` is clean.
  - The page was seen at `http://127.0.0.1:4400/experiments/SV-06-01-transfer-grid` on 2026-11-12: no raw JSON card and no console error.

---

## Part b (SV-06b): candidate tests in DS07

*Part b section, written by the SV-06b session on 2026-11-12. Part a's text above is unchanged.*

Experiment `SV-06-02-ds07-candidate-tests` (method `proteome_candidate_test`, role `primary`). Run 2026-11-12. Spec: [b/spec.md](b/spec.md), SHA-256 `a23e9c00852211c91cf0b3789b50d1f1fb870579180ab955acb3f71bab6ab8e1`. Exposure: [b/exposure.md](b/exposure.md) (one line: `DS07.outcomes.json`, opened after the spec was frozen). Environment and commands: [b/environment.md](b/environment.md), [b/run.md](b/run.md).

### b.1 Question and hypothesis

Do the serum proteins of mechanisms linked to severity in human disease (haemolysis and haem scavenging, neutrophil granule proteins and histones, fibrinolysis and anticoagulant consumption, complement regulation) differ between complicated and uncomplicated *B. rossi* babesiosis in DS07? Hypothesis: at least one mechanism candidate (not a positive control) differs at q < 0.05.

### b.2 Inputs

| File | SHA-256 |
|---|---|
| `shared/tidy/DS07.features.json` (SV-G1; built from `B_Proteins.txt` and `sample_list.xlsx`) | in `b/out/results.json` (`inputs`) |
| `shared/tidy/DS07.outcomes.json` | `596e092a2b3df0f95057347467d9d48295703a77b0fef62df2391e6db5eb5962` |
| `/core/data/raw/DS07/B_Proteins.txt` (master check only) | `2fc5d617dea4386d764336e4bed17405e56b5fbb542a0a0f79808c1afbbec120` |
| `a/out/candidates_for_partb.json` (part a hand-over: accessions of the fixed family) | – |
| `b/spec.md` | `a23e9c00852211c91cf0b3789b50d1f1fb870579180ab955acb3f71bab6ab8e1` |
| `b/scripts/analyse.py` (script version) | `01362624de84…` |

DS07: SRC-C, *B. rossi*, archived serum. 14 complicated, 18 uncomplicated, 20 controls, 11 TMT plexes (1 to 2 complicated dogs per plex; plex B11 has none). One species, one source.

### b.3 What was done

1. **Master check before the lock** (`b/out/master_check.csv`). Each named accession was looked up in the `Master` column of `B_Proteins.txt`. For a candidate-only row, the script found the master protein with identical grouped abundances in all 66 cells, which is the same protein group and the same quantity.
   - Master proteins: haemoglobin beta P60524, lactoferrin F1PR54, S100A8 C0LQL0, histone H4 L7N0L3, alpha-2-antiplasmin E2R4V3, protein C Q28278, antithrombin E2RES2, factor H A0A5F4BVG1, CD14 A0A1S7J0A8.
   - **Haptoglobin**: P19006 and G1K2D9 are candidates only. Their group master A0A5F4DB38 ("Peptidase S1 domain-containing protein") has the haptoglobin gene symbol LOC479668, so haptoglobin is kept, quantified through that group.
   - **Haemoglobin alpha fails**: P60529 is a candidate only, and its group master J9NXL3 (LOC100855558, "Uncharacterized protein") has no stated identity. As the package file says, it is dropped from the family. It is reported once as a secondary result outside the family.
   - The family therefore has **10 proteins**.
2. **Missing values are plex-level** (checked without labels). A protein that is missing is missing for every dog of a plex. The package file's presence test would therefore test how the groups were placed in plexes, not biology. The spec sharpened the rule before the lock: a protein seen in less than 60% of a group is tested on the observed dogs only and flagged as low coverage, and its Fisher presence p is reported as a plex-allocation check. A protein with fewer than 3 observed dogs in a group is not tested but still counts in the family size.
3. **Primary test** for each protein:
   - Statistic: Cliff's delta, complicated against uncomplicated, on the tidy log2 ratio to the plex standard.
   - p-value: two-sided permutation with labels permuted inside each plex (10,000 permutations, seed 20261112).
   - Intervals: 95% bootstrap intervals for delta and for the Hodges-Lehmann shift (2,000 resamples of dogs within each group, seed 20261112 + protein index).
   - Correction: Benjamini-Hochberg over 10 proteins.
4. **Checks**: S1 unstratified permutation; S2 leave one plex out; S3 infected against controls (plex-stratified, not corrected); S4 haemoglobin alpha through J9NXL3; S5 Spearman rho of each candidate with haemoglobin beta among infected dogs; S6 rerun from an empty `out/`.

**Deviations from the spec:** none after the lock. Two notes:

- The spec gives "about 1.4 SD" as the detectable effect after correction, a figure taken from the package file. The script computes 1.3 SD for 14 against 18 dogs at alpha 0.005. The report uses 1.3.
- The two rule changes against the package file were both made in the spec before the lock: haptoglobin is kept through its group master, and the presence test was replaced. Both are listed in b.9 for the user.

### b.4 Results

**Primary.** The hypothesis is **not supported**. None of the 10 family proteins differs at q < 0.05 (9 tested; 2 with uncorrected p < 0.05).

| Protein | Role | n compl. / uncompl. | Median log2 ratio, compl. / uncompl. / controls | Cliff's delta (95% CI) | HL shift, log2 (95% CI) | p (plex-stratified) | BH q |
|---|---|---|---|---|---|---|---|
| Haemoglobin beta | mechanism | 14 / 18 | 0.35 / −1.26 / −1.31 | **+0.48 (+0.09 to +0.82)** | +1.17 (+0.08 to +2.42) | 0.019 | 0.133 |
| Haptoglobin (group A0A5F4DB38) | mechanism | 14 / 18 | −0.22 / −0.29 / −0.40 | +0.08 (−0.34 to +0.47) | +0.09 (−0.50 to +0.86) | 0.714 | 0.892 |
| Lactoferrin | positive control | 14 / 17 | 0.29 / −0.35 / −0.45 | +0.42 (+0.01 to +0.81) | +0.51 (+0.02 to +0.85) | 0.027 | 0.133 |
| S100A8 | mechanism | 10 / 16 | 0.47 / −0.27 / −0.14 | +0.43 (−0.10 to +0.93) | +0.65 (−0.09 to +1.07) | 0.118 | 0.294 |
| Histone H4 | mechanism | 4 / 2 (plexes B1, B9) | – | not tested | – | – | – |
| Alpha-2-antiplasmin | mechanism | 14 / 18 | 0.03 / 0.05 / −0.06 | +0.10 (−0.33 to +0.48) | +0.03 (−0.12 to +0.28) | 0.569 | 0.892 |
| Protein C | mechanism, low coverage | 7 / 9 (5 plexes) | 0.36 / 0.18 / 0.09 | +0.02 (−0.56 to +0.68) | +0.03 (−0.43 to +0.40) | 1.000 | 1.000 |
| Antithrombin | mechanism | 14 / 18 | −0.17 / −0.17 / 0.09 | −0.08 (−0.46 to +0.34) | −0.03 (−0.18 to +0.09) | 0.714 | 0.892 |
| Complement factor H | mechanism | 14 / 18 | −0.04 / 0.03 / 0.04 | −0.12 (−0.52 to +0.29) | −0.03 (−0.12 to +0.07) | 0.614 | 0.892 |
| CD14 | positive control | 14 / 18 | 0.42 / 0.23 / −0.25 | +0.42 (+0.05 to +0.74) | +0.18 (+0.01 to +0.35) | 0.073 | 0.242 |

- **Positive controls pass.** Lactoferrin and CD14 are both higher in complicated dogs, which is the direction CB112 reported for the same data. The value pipeline (plex mapping, ratio construction) agrees with the source article. Neither control survives the family correction.
- **Haemoglobin beta.** This is the strongest mechanism signal, but it is nominal only. Complicated dogs have a median log2 ratio 1.6 units above uncomplicated dogs, and uncomplicated dogs sit at the control level (−1.26 against −1.31). Its interval excludes zero, but q is 0.133. It partly restates the label: the complicated definition includes haematocrit < 0.15 and bilirubin > 30 µmol/L.
- **Not supported:** haptoglobin depletion, fibrinolytic shutdown (by amount of alpha-2-antiplasmin), anticoagulant consumption (protein C, antithrombin) and complement factor H. For these the delta is within ±0.12 and every interval includes zero.
- **Histone H4 could not be tested.** It is quantified in 2 of 11 plexes only, from 1 peptide.

**Secondary (S4, outside the family).** Haemoglobin alpha through J9NXL3 gives delta +0.47 (+0.09 to +0.81), HL +1.48 log2, uncorrected p 0.028. It follows haemoglobin beta (rho 0.95).

### b.5 Stability and sensitivity

| Protein | S1 unstratified delta, p | S2 leave one plex out, delta range | S3 infected vs controls, delta, p | S5 rho with Hb beta (n) |
|---|---|---|---|---|
| Haemoglobin beta | +0.48, 0.022 | +0.41 to +0.54 | +0.23, 0.052 | – |
| Haptoglobin | +0.08, 0.708 | +0.00 to +0.14 | +0.16, 0.329 | +0.58 (32) |
| Lactoferrin | +0.42, 0.052 | +0.33 to +0.52 | +0.44, 0.008 | +0.54 (31) |
| S100A8 | +0.43, 0.081 | +0.27 to +0.59 | +0.01, 0.978 | +0.40 (26) |
| Alpha-2-antiplasmin | +0.10, 0.656 | −0.04 to +0.22 | +0.22, 0.140 | −0.24 (32) |
| Protein C | +0.02, 1.000 | −0.22 to +0.19 | +0.10, 0.619 | +0.51 (16) |
| Antithrombin | −0.08, 0.728 | −0.18 to +0.02 | −0.67, < 0.001 | −0.12 (32) |
| Complement factor H | −0.12, 0.584 | −0.25 to +0.02 | −0.17, 0.287 | −0.03 (32) |
| CD14 | +0.42, 0.043 | +0.31 to +0.53 | +0.83, < 0.001 | +0.46 (32) |

- Leaving one plex out never changes the sign for haemoglobin beta, lactoferrin, S100A8 or CD14. Stratifying by plex changes little: the layout is balanced, with 1 or 2 complicated dogs in every plex except B11.
- **Antithrombin** is much lower in infected dogs than in controls (delta −0.67, p < 0.001), but it does not differ by complicated status. Anticoagulant consumption, as far as it shows in amount, goes with infection, not with complicated disease.
- **CD14 and lactoferrin** are higher in infected dogs than in controls, and higher again in complicated dogs.
- **Haptoglobin** moves *with* haemoglobin beta among infected dogs (rho +0.58), not against it. The proteome measures total protein, including haptoglobin–haemoglobin complexes. This file therefore does not show haptoglobin depletion.
- Lactoferrin, CD14 and protein C also correlate with haemoglobin beta (rho 0.46 to 0.54). Part of the positive-control signal may share a source with the haemoglobin signal, for example sample haemolysis or overall disease intensity. The file cannot separate these.
- **Presence checks** (plex allocation only): histone H4, Fisher p 0.36; protein C, p 1.0.
- **Repeat (S6).** `out/` was deleted and the run repeated. Every output file was byte-identical, except the `run_utc` field of the load file. The database writer was run twice and gave the same rows.

### b.6 Confounders

- **Handled:** plex, by within-plex permutation. Repeated samples do not arise (one sample per dog).
- **Not handled:** no age, sex, breed, treatment, time from onset or sample haemolysis index is in the files. The complicated label is defined partly by haematocrit, urea, creatinine, bilirubin, glucose, lactate and band neutrophils. A haemoglobin difference may come from in-vivo haemolysis, from anaemia severity, or from haemolysis of the stored sample, and these cannot be told apart. The pooled standard of each plex contains serum of all dogs, so the ratios are slightly self-referential.
- **Linkage:** DS07 may share dogs with DS04, and through DS04 with 3 S-CB050 dogs (SV-07 section 9 and its link table: unverified, "DS07 cannot take death from another file yet"). This does not change a within-DS07 test. It does mean that a later "replication" in DS04 or S-CB050 might not be independent.

### b.7 What this does not show

- A null here is "not shown", not "absent". With 14 against 18 dogs the test detects about 1.0 SD at alpha 0.05, and about 1.3 SD after correction. The low-coverage proteins detect less (protein C, 7 against 9: 1.4 SD).
- Serum proteomics gives total protein amounts, not activity. An unchanged amount of alpha-2-antiplasmin or protein C does not test fibrinolytic shutdown or protein C activation. Total haptoglobin is not free haptoglobin.
- One proteome, one source, no replication. Lactoferrin and CD14 are already-seen results (CB112). They confirm the pipeline, not a mechanism.
- This is not a screen: no protein outside the fixed family was looked at.

### b.8 Verified in files, taken from documentation, or inferred

- **Verified in files:** the master status, coverage and peptide counts; the identical-abundance group matches; the plex-level missingness; every number above (`b/out/ds07_candidates.csv`, `sensitivity_lopo.csv`, `dog_values.csv`, `results.json`).
- **From documentation:** the definition of "complicated" (CB112, via the SV-G1 outcomes file); CB112's report that CD14 and lactoferrin are higher in complicated dogs (article note `/core/articles/CB112_*.md`); the plex mapping B_k = F_k (SV-G1 cleaning note).
- **Inferred:** that A0A5F4DB38 is haptoglobin (shared gene symbol LOC479668 and identical quantities, but a different UniProt description); that the haemoglobin signal reflects haemolysis of some kind.

### b.9 Next step, and decisions for the user

- **Haemoglobin beta** (and alpha) is the only mechanism protein with an interval that excludes zero, and it partly restates the label. In a stored-sample or prospective study it should be measured together with a sample haemolysis index and haematocrit (cell-free haemoglobin by spectrophotometry, with haptoglobin and haemopexin), so that "more haemolysis per unit of anaemia" can be told apart from "more anaemia". This fits SV-10's minimum dataset.
- **Histone H4, S100A8 and the coagulation proteins** need targeted assays, not shotgun serum proteomics: nucleosome or cfDNA ELISA, calprotectin, and protein C and antithrombin *activity*. Part a's stored-sample list (a.9) stands.
- **Open questions for the user:**
  1. Accept haptoglobin through its group master A0A5F4DB38? The alternative is to drop it, as was done for haemoglobin alpha. If it is dropped the family becomes 9, and no conclusion changes: haptoglobin q 0.89.
  2. Accept the replacement of the package file's presence test by low-coverage rank tests, because DS07 missingness is plex-level?

### b.10 Database and view

- **Database:** `dbo.experiment` and `dbo.experiment_result`, 8 results: `primary_result`, `candidate_tests`, `dog_values`, `sensitivity`, `secondary`, `master_check`, `plex_layout`, `interpretation`. Written by `b/scripts/write_db.py`; a second run gives the same rows.

  | experiment_code | method | run_at | results | interpretation |
  |---|---|---|---|---|
  | SV-06-02-ds07-candidate-tests | proteome_candidate_test | 2026-11-12 15:52:40 | 8 | 1 |

- **View:** `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-proteome-candidate-test-view.component.{ts,html,scss}`, plus one import and one entry in `experiment-views.registry.ts`.
  - The view shows the primary result card, a forest plot of Cliff's delta, values by dog for each protein, the sensitivity table, the secondary result, the master check and the plex layout.
  - `npx ng build` is clean.
  - The page was seen at `http://127.0.0.1:4400/experiments/SV-06-02-ds07-candidate-tests` on 2026-11-12, in the light and the dark theme: no raw JSON card and no console error.

### Software

Python 3.12.12 (uv 0.10.4), numpy 2.3.4, pyodbc 5.2.0.
