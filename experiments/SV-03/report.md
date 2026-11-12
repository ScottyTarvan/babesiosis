# SV-03 report: severity definition map and marker-evidence matrix

Experiments `SV-03-01-evidence-matrix` and `SV-03-02-definition-map` (method `evidence_matrix`, role `descriptive`). Run 2026-11-12.
Spec SHA-256 `25f2cc933b6d7bc93b26ac90a1f973dd6523bc9b37df5f9a6d017ec47718a884`.

## 1. Question and hypothesis

Which markers and host or parasite factors are linked to canine babesiosis severity consistently, once severity definitions are aligned and each cohort is counted once? Hypothesis: some markers agree in direction in 3 or more independent units of one species and one outcome class, enough to pool.

## 2. Inputs

| File | SHA-256 |
|---|---|
| `SV-G2/associations_v2.csv` (740 rows) | `ac19fa31070dc7c3542d48e1989c153ceb687fa892edac6411e1175fad4ce67d` |
| `SV-G2/definitions_v2.csv` (78 definitions) | `8815931ca4a9681dd5213b19ef929f9045d11db14d18b57e95a5a44012e8d1de` |
| `/core/cohorts.json` (through SV-G2's `independent_unit`) | `b2eb1cae1f9300a09ce37ae910ab3b454f2682d0445cbff91093674db75e51bc` |
| `spec.md` | `25f2cc933b6d7bc93b26ac90a1f973dd6523bc9b37df5f9a6d017ec47718a884` |

Also used: SV-07 report (link table, for the Onderstepoort sensitivity set), SV-04 report section 9 (IL-8, MCP-1), `/core/articles.jsonl` country field and two appraisal notes (CB518, CB040) to check species and a row. No dog-level outcomes file was opened (`exposure.md`); every input is a published group result, all on the "already seen" list, so both experiments are descriptive.

Scripts: `scripts/analyse.py` (`78c857654132`), `scripts/build_load.py` (`cbe0832df811`). Python 3.12.12, numpy 2.3.4, scipy 1.16.3. No random numbers.

## 3. What was done

- Every row was called H (significantly higher in the worse outcome, including positive correlation and more frequent), L (lower), N (not significant), U (unclear) or D (descriptive only). Rows were merged into one call per **independent unit** (cohort in `/core/cohorts.json`, else the article; CB510 and CB511 are inside CH23 and have no rows of their own) for each **cell** = canonical marker x outcome class x species group. Both H and L inside one unit = X. Multivariable rows kept apart.
- Cell "consistent": at least 2 tested units agree in one significant direction, at least 2/3 of tested units agree, no unit the other way.
- Circularity: a row is flagged when its marker belongs to a component of its own definition (fixed map in the spec), when the outcome class is defined by the marker, or when the marker is named in the definition text.
- Pooling rule: 3 or more units, one species, one outcome class, a usable summary (Hedges g with Wan et al. 2014 conversions, [10.1186/1471-2288-14-135](https://doi.org/10.1186/1471-2288-14-135); Fisher z; log OR). REML with Hartung-Knapp; DerSimonian-Laird beside it.
- Sensitivity sets: S1 all Onderstepoort *B. rossi* units counted once (CH03, CB040, CB035, CB053, CB112, CB125, CB342, CB376, CB418, CH29, CH31, CH04; SV-G2 section 6 and the SV-07 link table: DS04 = CB147 shares dogs with S-CB050, and DS07 = CB112 probably follows the DS04 numbering); S2 judgement-call definitions and machine translations removed; S3 strict unit rule; S4 circular units removed.

**Deviations from the spec**

- **D1 (added after the primary result).** The primary matrix had no cell with 3 tested units, so I added the same matrix with all outcome classes of one species merged (one call per unit across its definitions). It is an exploratory direction table: not pooled, and labelled post hoc in the payload and on the page.
- **D2.** The package's abstract-only sensitivity set is empty: SV-G2 extracted no abstract-only article. The CB037 IL-8 result that SV-04 asked about is therefore absent from the matrix.
- **D3.** Conflict counts in `conflicts.csv` count a unit once per call; a unit with several definitions can count under two calls (for example CB006 for MDA). The verdict rule was applied as written.
- `n_subjects` in the database is the sum over units of the largest n reported by the unit (3,636); dogs overlap between units, so it is an upper bound.

## 4. Results

### 4.1 Primary: the evidence matrix (SV-03-01) — negative

- 740 rows, 49 articles, **42 independent units**, 131 markers. Units by species: *B. rossi* 13, *B. canis* 16, *B. gibsoni* 4, *B. vogeli* 1, mixed/unspecified 8.
- **423 cells. 15 have 2 tested units; none has 3** (largest: 2). The evidence is spread over too many definitions: most markers were tested once, in one unit, against one definition.
- **Nothing was pooled.** 287 rows had a usable summary, but only 2 cells had 2 units with one (MDA against anaemia grade and against complicated, *B. canis*, CB006 and CH33) and none had 3.
- **Consistent cells (2 units each):** band neutrophils higher in non-survivors (*B. rossi*, CB040 and CH03); cortisol higher and thyroid hormones lower (*B. rossi*, outcome class "other", CB040 and CH09). Under S1 the band neutrophil cell is one unit (both Onderstepoort); under S2 cortisol and thyroid lose CH09 (experimental dose groups of CB105).
- **Opposite significant directions between units:** 2 cells. GGT against severity grade in *B. canis* (CB307 higher, CH12 lower). Haematocrit against death in *B. rossi* (CB040 higher, CH03 lower): a definition effect, since CB040's significant row is its haemoconcentration category (4 dogs, 3 died) and its low-haematocrit categories were not significant; CH03 (CB145) reports lower haematocrit in non-survivors. 7 further cells have both directions inside one unit (panels: proteome, acid-base, iron, echocardiography, immune complexes).

### 4.2 D1, exploratory: outcome classes merged within species

- 239 cells; 50 with 2 tested units, 22 with 3 or more.
- **Consistent, not circular, 3 or more agreeing units: 4, all *B. rossi*:** body temperature lower (3 of 4 units: CB040, CB342, CB518 lower; CH09 not significant), band neutrophils higher (3 of 3: CB040, CB418, CH03), cortisol higher (3 of 3: CB040, CB342, CH09), thyroid hormones lower (3 of 3: CB040, CB342, CH09).
- **With Onderstepoort counted once (S1), none keeps 3 agreeing units.** Band neutrophils collapse to 1 unit; cortisol, thyroid hormones and body temperature to 2. The body temperature cell also rests on CB518, whose species is only presumed (smear-only, *B. canis* suspected in the article, "B. rossi presumed in region" in the row).
- **Consistent but circular:** urea, creatinine, ALT, ALP, AST, bilirubin and haematocrit in *B. canis*, urea in *B. rossi*. The *B. canis* cells are multi-source (they survive S1), but each loses consistency when the units whose definition contains the marker are removed (S4).
- No marker is consistent in the same direction in two species groups outside circular cells.
- If merging outcome classes were allowed, 10 *B. canis* cells would have 3 or 4 units with usable summaries (urea, creatinine 4; albumin, total protein, red cell count, haematocrit, WBC, platelets, ALT, ALP 3). None in *B. rossi*.

### 4.3 Named conflicts (step 4)

| Conflict | Units tested | Calls (units) | Verdict |
|---|---|---|---|
| IL-8 | 2 | CH03 (CB517, *B. rossi*, death) N; CH23 (CB017, *B. canis*, complicated) N | No conflict in the extracted evidence |
| Fibrinogen | 2 | CB112 higher (complicated); CH03 N (death) | No conflict: inconsistent, not opposite |
| aPTT | 2 | CH18 higher (death, mixed species); CH03 N | No conflict |
| MDA | 3 | CB006 higher (3 definitions), CH08 higher; CH33 N | No conflict |
| SOD and catalase | 2 | CB006 lower; CH08 catalase lower, SOD N | No conflict |
| Parasitaemia | 4 | CH12 qPCR load higher (severity grade, *B. canis*); CH21 N (death, *B. canis*); CB045 N; CH09 unclear | No conflict |
| Platelets against death | 3 | CH21 lower (*B. canis*); CH03 N (*B. rossi*); CH18 unclear | No conflict |
| Lactate | 4 | CB040, CH21, CH18 higher in death; CB112 unclear | No conflict; the most uniform of the eight |
| MCP-1 (SV-04 candidate) | 2 | CH03 higher in death (*B. rossi*), CH23 higher in complicated (*B. canis*) | Agrees in 2 units, 2 species, 2 definitions |

No named conflict has two units with opposite significant directions in the extraction. The conflicts in the syntheses rest on three things the matrix does not contain: comparisons of infected dogs with healthy controls (IL-8 low in *B. rossi*, high in *B. canis*), articles that were not extracted (CB037, abstract only, is the only source of "IL-8 falls with severity in *B. rossi*"), and a significant result in one unit read against a non-significant one in another. On IL-8 this agrees with SV-04: CB517 (CH03) shows no IL-8 difference by death; CB037 stands alone.

### 4.4 Definition map (SV-03-02)

- 78 definitions in 42 units; median 1 component per definition.
- Components by units: death 20, other 15, renal 14, anaemia grade 13, hepatic or icterus 11, cerebral 7, pulmonary 6, collapse 6 (all *B. rossi*), rhabdomyolysis 4 (all *B. canis*), MODS 4, hypoglycaemia 4 (all *B. rossi*), SIRS 3.
- Outcome classes by units: mortality 16, severity grade 11, anaemia grade 10, complicated 9, specific complication 8, parasitaemia level 3, treatment intensity 3, other 2, organ dysfunction 1.
- **Marker in its own definition:** 38 of 504 tested rows (7.5%), in 7 of 31 units with tests. These rows are significant 79% of the time; other rows 47%.
- Euthanasia in mortality definitions: included 11, not stated 6, excluded 1. "Died" includes euthanasia for poor prognosis in the Onderstepoort files.

### 4.5 Selective reporting

50.4% of tested rows are not significant (median by article 53%, IQR 32% to 68%). 6 of 36 articles with tested rows report no non-significant row: CB035, CB071, CB220, CB286, CB307, CB425. Reporting looks balanced overall; those 6 articles are the ones to read with care.

## 5. Stability and sensitivity

| Set | Cells with 2 units | with 3 units | Consistent | Consistent, 3 agreeing, not circular |
|---|---|---|---|---|
| Primary | 15 | 0 | 3 | 0 |
| S1 Onderstepoort once | 9 | 0 | 2 | 0 |
| S2 judgement calls removed | 13 | 0 | 1 | 0 |
| S3 strict unit rule | 15 | 0 | 1 | 0 |
| S4 circular units removed | 15 | 0 | 3 | 0 |
| D1 classes merged | 50 | 22 | 15 | 4 |
| D1 + S1 | 40 | 13 | 11 | 0 |
| D1 + S4 | 42 | 14 | 7 | 4 |

Rerun: `out/` deleted and rebuilt from `run.md`; every file byte-identical except `run_utc` in the two load files.

## 6. Confounders

- **Handled:** cohorts counted once; species stratified; circular definitions flagged and removed in S4; Onderstepoort overlap in S1; judgement calls in S2.
- **Not handled:** species is aliased with source, country, setting, assay and definition (rule 6), so the species groups are never compared. Sample timing is "not stated" for most rows and could not be used as a moderator. Unit links beyond `/core/cohorts.json` are a judgement (S1 is a whole-hospital collapse, stricter than any confirmed link).

## 7. What this does not show

- It does not show that markers are unrelated to severity. An empty cell means one study, not no effect; the matrix measures how thin the replicated evidence is.
- Direction counts are not effect sizes. D1 mixes definitions and was added after the primary result.
- The calls inherit the SV-G2 extraction (language-model agents, 16-article owner check, blind second extraction agreement 0.99).
- The abstract-only literature (34 tier B articles, including CB037) is not in the matrix.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files:** every count and call (computed from the SV-G2 files by `analyse.py`); the CB040 haematocrit rows (row notes); CB518 species (row and appraisal note).
- **Taken from documentation:** cohort membership (`/core/cohorts.json`), the Onderstepoort membership of the S1 units (article country fields and appraisal notes; CB053 and CB125 are inferred from "veterinary academic hospital in South Africa" and the author group), and the dog overlaps (SV-07).
- **Inferred:** that the named conflicts in the syntheses come from infected-vs-control comparisons and unextracted articles.

## 9. Next step and decisions for the user

- **Most useful next data step:** extract the 34 abstract-only tier B articles (SV-G2 optional step), CB037 first, or obtain the CB037 full text (also asked by SV-04). It is the only source of the *B. rossi* IL-8-by-severity claim.
- **A harmonised-definition meta-analysis is possible only in *B. canis*:** 10 cells reach 3 to 4 units if complicated, severity grade and death are merged; that needs a user decision on whether merged definitions are acceptable.
- For *B. rossi*, every replicated signal (band neutrophils, cortisol, thyroid hormones, hypothermia) is from one hospital. Its replication needs a non-Onderstepoort *B. rossi* cohort: SV-10 territory.
- Candidates to carry forward (not predictors): lactate (higher with death in 3 units, 2 species groups and mixed), MCP-1 (higher in 2 units, 2 species), band neutrophils and the cortisol/thyroid pattern in *B. rossi*.
