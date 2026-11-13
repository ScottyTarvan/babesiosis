# SV-META report: meta experiment — a final review of all experiments for research leads

Experiment `SV-META-01-research-leads` (method `meta_review`, role `descriptive`). Run 2026-11-12.

**Summary.** 0 of 29 candidates reached tier A, 0 tier B, 1 tier C and 6 tier D; 22 were rejected (X). No candidate reached tier A or B: the 23 experiments contain no new, non-circular severity finding that passes a statistical screen. The one tier C lead is a higher circulating monocyte count in more severe *B. rossi* disease. It agrees in
direction in 4 of 4 independent *B. rossi* sources (Stouffer Z 3.94, BH q 0.00016 over 8 themes, chosen after the results were seen), but
it rests mostly on DS05, the clinic file that first suggested it: without DS05 it does not survive the correction for themes. The tier D
leads are gaps: mechanisms with strong human evidence and a canine assay that no canine study has measured against severity. Everything
else that passed a statistical screen restates a known driver (band neutrophils, anaemia), is circular with its severity label, is the
published finding of the article that reported the same dogs, or did not survive its refutation attempt.

## 1. Question and hypothesis

Does any result of the 23 experiments, alone or in agreement across independent sources, point to a severity correlate, a mechanism not
established in canine babesiosis, or a human-disease parallel that the canine literature has not made? There is no hypothesis to confirm:
the experiment ranks candidates for further research, and its stated "against" outcome was "no candidate reaches tier A, B or C".

## 2. Inputs

- Every package folder (`SV-G1`, `SV-G2`, `SV-01`, `SV-02` a and b, `SV-03`, `SV-04`, `SV-05`, `SV-06` a and b, `SV-07`, `SV-08`,
  `SV-09`, `SV-10`, `SV-INT`): `report.md` and the `out/` files. The census cites file and line for every number.
- Tidy files (SV-G1) for the theme indicators that no package had printed: `S-CB017`, `S-CB517`, `S-CB516`, `DS05`, `DS02` features;
  outcomes files as listed in `exposure.md` (all already seen by earlier packages).
- Novelty: `/core/articles/*.md`, `/core/data/markdown/CB*.md` (read, never copied), `SV-G2/associations_v2.csv`, PubMed (no user
  details in any query). `HU` articles first for human comparators.
- **Spec** `spec.md` SHA-256 `9f41ddf629757e4f31569c305eb2a607cd84bf0eb91b1190adcfae96038f6238` (written before any result was scored;
  `themes.py` stops if it changes). Scripts (SHA-256, 12 characters): `census.py` 63cc704e0feb, `check_census.py` a7427d8f461a,
  `themes.py` beeaaae1f656, `screen.py` b4cdcc1abe98, `build_load.py` ff918784bffc, `candidates.json` 56b83af8ce0e.
- Python 3.12.12 (uv 0.10.4), numpy 2.3.4, scipy 1.16.3. Seed 20261112; 2,000 bootstrap resamples of dogs, 10,000 permutations, exact
  enumeration (10 allocations) for the 5 Beagles.

## 3. What was done

1. **Census** (`out/census.csv`, 495 rows): every row of the test and effect tables of every package, plus observations (linkage
   facts, genes missing from DS06, the SV-06a grid, SV-10 design numbers, SV-G1 and SV-G2 counts). `check_census.py` reopened each cited
   file and line (or JSON pointer) and found all 1,843 numbers.
2. **Screen** (columns of `census.csv`): interval and FDR in the result's own family, or BH over the 119 census rows with a p value
   when the result had no declared family; for the 5 Beagles, the same direction in all dogs. Independence, circularity, novelty and the
   detectable effect are given per row. 39 rows pass the statistical screen; every passing row is attached to a candidate.
3. **Themes** (`out/themes.csv`): 15 themes, one indicator per independent source (counted after SV-07), oriented so that positive means
   more of the mechanism in the more severe dogs. 39 indicator rows (including the T02s sensitivity rows): 17 computed here from the tidy files, the rest read from package output files or computed from per-dog values in them.
   Stouffer, Fisher, sign test and leave-one-source-out per theme; BH over the 8 themes that have a *B. rossi* combined row; *B. canis*
   kept apart and added only as a transfer check.
4. **Human parallels and novelty**: CB notes and full texts searched by keyword; SV-G2 rows; PubMed.
5. **Refutation**: one separate attempt per surviving candidate and gap lead by a Claude sub-agent with a fresh context and only the
   evidence pointers (`refutation/BRIEF.md`; results `refutation/K*.json`, scripts `refutation/scripts/`). Candidates that were X at the
   screen carry the screen reason as their refutation row (`out/refutation.csv`).
6. **Tiers** by the rules of `spec.md` section 8 (a refutation can only lower a tier), and **leads** (`out/leads.csv`).

**Deviations from the spec**

- **D1 (DS02 baseline).** For DS02 cell-free haemoglobin there is no day −1 or day 0 value in some dogs; the earliest pre-treatment value
  was used as baseline (noted in the indicator row). It does not change the reading: the K03 refutation showed this indicator is a
  parasite-load effect anyway.
- **D2 (refutation sub-agents opened outcomes files).** The K01, K03 and K04 sub-agents opened `DS07.outcomes.json` and (K03)
  `DS02.outcomes.json`, which the package scripts did not open. Both were already seen; recorded in `exposure.md`.
- **D3 (wording of K01).** The K01 refutation found that the evidence supports a circulating monocyte count, not "monocyte activation"
  (CB504 and a Malawian malaria study point the other way for activation markers). The candidate and lead were reworded; the tier was
  not changed by the rewording.
- **D4 (family q computed here).** SV-09-01 prints p but no q for its declared family of 2; `screen.py` computes BH inside that family.
- No other deviation. The spec's tier definitions were applied as written.

## 4. Results

### 4.1 Tier counts

| Tier | Meaning | n | Candidates |
|---|---|---|---|
| A | significant finding | 0 | none |
| B | signal | 0 | none |
| C | convergent lead | 1 | K01 Higher circulating monocyte count in more severe disease (with CD14 and CCL2 as supporting markers) |
| D | gap lead | 6 | K03 Intravascular haemolysis per unit of anaemia (cell-free haemoglobin, haem scavenging); K04 Neutrophil degranulation and extracellular traps (NETs, histones, released MPO and elastase, calprotectin); K05 Angiopoietin-2 and the Ang-2/Ang-1 ratio; K06 VWF, ultra-large multimers and ADAMTS13; K08 Ferritin (hyperferritinaemia); K09 Kynurenine pathway (kynurenine:tryptophan) |
| X | rejected | 22 | K02 Inflammation against regeneration at a given haematocrit (SV-09 residual axis 2) tracks dullness; K07 VEGF and soluble VEGFR-1 (sFlt-1); X01 Neutrophil activation and left shift (band neutrophils, lactoferrin); X02 CCL2 (MCP-1) higher in severe disease in each file; X03 GM-CSF and IL-2 higher in complicated B. canis; X04 Type 1 interferon transcript response in the Beagles; X05 Anaemia (haematocrit); X06 Anti-inflammatory IL-10; X07 Coagulation and platelet consumption; X08 Host age; X09 Acute phase response (CRP); X10 Size of the cytokine response (perturbation count); X11 SV-09 leukocyte axis score with death; X12 Distance from the Beagle course (SV-01); X13 Antibody level against load (CB141, B. canis); X14 Endocrine stress response (cortisol up, thyroid down), body temperature; X15 Lactate; X16 Young dogs present earlier (DS05); X17 MCP-1 minus IL-8 balance index; X18 Parasite load; X19 Infected against healthy controls (IL-8 direction, MCP-1, IL-10, CD14, antithrombin); X20 Lower haematocrit in young infected Onderstepoort dogs (DS03) |


### 4.2 Agreement between independent sources (primary new calculation)

*B. rossi* combined rows (themes chosen after the results were seen; BH over 8 themes):

| Theme | Sources in expected direction | Stouffer Z | p (one-sided) | BH q | Leave-one-source-out max p | Reading |
|---|---|---|---|---|---|---|
| T01 Neutrophil activation, left shift | 3 of 3 (A, B, F) | 5.23 | < 1e-6 | < 1e-5 | 0.0001 | Known driver: band neutrophils are a published severity finding (CB050, CB040) |
| T02 Circulating monocyte count (CD14, CCL2) | 4 of 4 (A, B, C, F) | 3.94 | 4e-05 | 0.00016 | 0.0105 | **Tier C**, weakened (section 5) |
| T04 Haemolysis, cell-free haemoglobin | 2 of 2 (B, C) | 2.56 | 0.0052 | 0.010 | 0.10 | Fails leave-one-source-out; gap lead D |
| T05 Coagulation, platelet consumption | 1 of 3 | −0.46 | 0.68 | 0.68 | 0.79 | Null |
| T07 Anaemia | 2 of 2 (B, F) | 3.66 | 0.0001 | 0.0003 | 0.10 | Known driver |
| T10 Host age (two-sided) | 0 of 2 | −0.48 | 0.63 | 0.68 | 0.78 | Null |
| T11 IL-10 | 2 of 2 (A, B) | 1.40 | 0.081 | 0.13 | 0.20 | Not significant |
| T13 CRP | 1 of 2 | −0.41 | 0.66 | 0.68 | 0.90 | Null |

Transfer checks with *B. canis* (SRC-D, SRC-O): T02 5 of 5 (Z 4.06); T11 3 of 3 (Z 1.38, p 0.084); T05 1 of 4; T10 0 of 3. With
CCL2 (MCP-1) in place of the monocyte count (T02s) the *B. rossi* Z is 4.80. Themes with a single dog-level source (T03 type 1
interferon, T08 SV-09 axis 2, T09 load, T12 lactate, T14 cytokine response size) and the literature-only theme (T06 cortisol and thyroid)
have no combined test. The sign test cannot pass with 2 to 4 sources (minimum one-sided p 0.0625 at 4 of 4).

### 4.3 Single results that pass the statistical screen

39 of 495 census rows pass. None becomes tier A or B:

- S-CB017 (*B. canis*) MCP-1, GM-CSF and IL-2 by complicated status: the published findings of CB017 (X02, X03).
- S-CB050 band neutrophils and the SV-09 leukocyte score with death: a known driver (X01, X11).
- SV-01 distance from the Beagle course: restates anaemia; the stage score failed validation (X12).
- SV-04 and SV-06b infected-versus-control contrasts: infection response, not severity, already reported (X19).
- SV-05 B2 lower haematocrit in young Onderstepoort dogs: partly physiological, not in the independent source (X20).
- SV-04-02 perturbation count and balance in *B. canis*: the label contains SIRS; carried by MCP-1 (X10, X17).
- SV-08 within-dog rise of the interferon and neutrophil-granule transcript scores in 5 of 5 Beagles: a response to infection with no
  severity gradient; interferon genes already reported for these dogs (CB082) (X04; the granule score supports gap lead K04).
- SV-09-01 residual axis 2 with habitus: provisional tier B, **refuted** (section 5).

### 4.4 Research leads (`out/leads.csv`)

| Rank | Tier | Kind | Hypothesis | Human counterpart (DOI) | Cheapest next study | New dogs (SV-10) |
|---|---|---|---|---|---|---|
| 1 | C | severity; human parallel | In B. rossi babesiosis, a higher circulating monocyte count at admission goes with more severe disease, beyond anaemia and total leukocytes. | [10.1186/s12879-018-3593-8](https://doi.org/10.1186/s12879-018-3593-8), [10.1371/journal.pone.0191486](https://doi.org/10.1371/journal.pone.0191486), [10.1186/cc5783](https://doi.org/10.1186/cc5783), [10.1111/pim.12319](https://doi.org/10.1111/pim.12319) | Monocyte count and monocyte fraction against death in the probable DS03-S-CB050 join is not possible (DS03 has no leukocytes); cheapest: ask the CB040 authors (320 B. rossi dogs, SV-02c request) for dog-level monocyte counts and outcome | SV-10-03 prospective B. rossi cohort with at least 200 dogs outside Onderstepoort: admission CBC with differential, outcome components stored separately |
| 2 | D | mechanism; human parallel | Neutrophil degranulation and extracellular trap release (cfDNA, nucleosomes, histones, released MPO and elastase, calprotectin) are greater in severe B. rossi babesiosis, beyond neutrophil number. | [10.1128/mBio.01300-15](https://doi.org/10.1128/mBio.01300-15), [10.1182/bloodadvances.2019001258](https://doi.org/10.1182/bloodadvances.2019001258), [10.1126/scitranslmed.aar3619](https://doi.org/10.1126/scitranslmed.aar3619), [10.1093/ajrcmb/aanag021](https://doi.org/10.1093/ajrcmb/aanag021), [10.1164/rccm.201811-2111OC](https://doi.org/10.1164/rccm.201811-2111OC) | Re-quantify DS06 from SRA PRJNA703846 without the CPM filter to recover MPO and ELANE (a coordinator decision, large download); no severity contrast in those 5 dogs | SV-10-03 cohort: citrate plasma (not serum) for cfDNA by fluorometry and calprotectin; nucleosome ELISA only with a haemolysis and icterus check |
| 3 | D | mechanism; human parallel | More intravascular haemolysis per unit of anaemia (cell-free haemoglobin and haem load relative to haematocrit and scavenger capacity) goes with severe and fatal B. rossi disease, as in severe falciparum and knowlesi malaria and sepsis. | [10.1186/s12879-017-2373-1](https://doi.org/10.1186/s12879-017-2373-1), [10.1186/s12936-015-1028-1](https://doi.org/10.1186/s12936-015-1028-1), [10.1038/s41426-018-0105-2](https://doi.org/10.1038/s41426-018-0105-2), [10.1097/CCM.0b013e3182741a54](https://doi.org/10.1097/CCM.0b013e3182741a54) | None adequate: DS07 lacks haematocrit, bilirubin and a haemolysis index. Cheapest is stored pre-treatment plasma (CB145 / Onderstepoort biobank, SV-02c-type request) | SV-10-03 cohort: plasma cfHb by spectrophotometry with haematocrit, haptoglobin, haemopexin and a haemolysis index at admission |
| 4 | D | mechanism; human parallel | Endothelial activation measured as plasma angiopoietin-2 is higher in dogs with severe or fatal B. rossi babesiosis. | [10.1186/s12936-016-1624-8](https://doi.org/10.1186/s12936-016-1624-8), [10.1186/1475-2875-10-383](https://doi.org/10.1186/1475-2875-10-383), [10.1097/CCM.0000000000004469](https://doi.org/10.1097/CCM.0000000000004469), [10.1111/jvim.15369](https://doi.org/10.1111/jvim.15369) | None in the public files. Stored pre-treatment plasma with outcome (Onderstepoort biobank; contacting the authors is a user decision) | SV-10-03 cohort: plasma Ang-2 at admission with creatinine and a haemolysis index |
| 5 | D | mechanism; human parallel | VWF release and ADAMTS13 consumption (a higher VWF:ADAMTS13 ratio) go with severe B. rossi babesiosis and its microthrombi. | [10.1371/journal.ppat.1000349](https://doi.org/10.1371/journal.ppat.1000349), [10.1186/s12936-019-3040-3](https://doi.org/10.1186/s12936-019-3040-3), [10.1097/CCM.0000000000004469](https://doi.org/10.1097/CCM.0000000000004469) | None public. CB145 cohort plasma (thromboinflammation study, raw data on request) is the natural place to add VWF and ADAMTS13 | SV-10-03 cohort: citrate plasma for VWF antigen, VWF:collagen binding and ADAMTS13 activity |
| 6 | D | mechanism; human parallel | Hyperferritinaemia (macrophage activation and iron sequestration) at admission goes with severe or fatal B. rossi babesiosis. | [10.1186/s12879-026-13418-z](https://doi.org/10.1186/s12879-026-13418-z), [10.3389/fnut.2026.1858343](https://doi.org/10.3389/fnut.2026.1858343), [10.1159/000552315](https://doi.org/10.1159/000552315), [10.1017/S0007114522000757](https://doi.org/10.1017/S0007114522000757) | None public; stored serum with outcome (same biobank question as the other plasma leads) | SV-10-03 cohort: serum ferritin with CRP, serum iron and transferrin at admission |
| 7 | D | mechanism; human parallel | Higher kynurenine:tryptophan (IDO activity) at admission goes with severe or fatal canine babesiosis. | [10.1086/650996](https://doi.org/10.1086/650996), [10.1371/journal.pone.0087538](https://doi.org/10.1371/journal.pone.0087538), [10.1186/s12936-017-1954-1](https://doi.org/10.1186/s12936-017-1954-1) | None public with a severity label; the CB091 supplement has dog-level values but no severity label (ask the authors for complicated status: a user decision) | SV-10-03 cohort: plasma tryptophan and kynurenine by LC-MS/MS with creatinine and CRP |

The full cards (evidence, what would refute each lead, the measurement to add to the SV-10-03 minimum dataset) are in `out/leads.csv` and on the page. Order: tier C first; tier D by SV-06a rank, with the two leads that a public file has already touched (K04 S100A8 and K03 haemoglobin beta in DS07) moved up, as the spec says.


## 5. Stability, sensitivity and the refutation attempts

One separate sub-agent attempt per candidate that survived the screen (K01 to K09); the attempts and results are in `out/refutation.csv`.

| Candidate | Provisional | Verdict | Final tier | Main reason |
|---|---|---|---|---|
| K01 Higher circulating monocyte count in more severe disease (with CD14 and CCL2 as supporting markers) | C | survives_weakened | C | No single check rejects the lead. The DS05 monocyte-dullness association survives adjustment for haematocrit, total and differential leukocytes and illness days (partial rho about +0.28), and the post hoc marker choice was conservative. But the cross-source support outside the source that suggested it is weak: without SRC-F, Z 2.31, Bonferroni over 8 themes 0.084. In the two hard-outcome sources the monocyte difference is no larger than the WBC difference, and half of the DS07 CD14 signal goes with haemoglobin beta. Monocyte count does not track MCP-1, the CCL2 form is already published (CB107, CB517, CB037, CB017), and the only direct activation marker in B. rossi (CB504) points the other way in non-survivors. |
| K02 Inflammation against regeneration at a given haematocrit (SV-09 residual axis 2) tracks dullness | B | refuted | X | The axis-2 association with habitus does not survive control for band neutrophils and monocytes (rho -0.10, -0.27 to +0.07), so it restates leukocytes already known to track dullness, a known driver under the spec. The named mechanism is also absent: at a given haematocrit the leukocyte and regeneration sides are uncorrelated (rho -0.002) and leukocytes do not go with lower ARC. What remains is a weak, uncorrected ARC-brighter link (rho +0.18, p 0.03) in one already-seen clinic file, which could be re-entered as a separate gap/test lead (the DS03-S-CB050 join) but not as K02. |
| K03 Intravascular haemolysis per unit of anaemia (cell-free haemoglobin, haem scavenging) | D | survives_weakened | D | The gap stands: no CB article relates measured cell-free haemoglobin or haem load to outcome in natural canine babesiosis, the human evidence (falciparum, knowlesi, sepsis) agrees, and canine assays exist. The programme's 'weak convergent support' does not hold. DS02 is a pure parasite-load effect that CB082 already reports. DS07 haemoglobin beta partly restates the label, cannot be put per unit of anaemia, moves with another red-cell protein (sample haemolysis not excluded), drops below significance when adjusted for lactoferrin or CD14 or when the top 3 dogs are removed, and has q 0.133. So T04 should be cited as a literature gap, not as a data signal. |
| K04 Neutrophil degranulation and extracellular traps (NETs, histones, released MPO and elastase, calprotectin) | D | survives_weakened | D | The gap is real: no study has measured NETs, cfDNA, nucleosomes, circulating histones, calprotectin or released MPO/elastase against severity or outcome in canine babesiosis, and CB107 states NETosis is unstudied. The canine support is weak and confounded: no signal passes correction (S100A8 q 0.29, H4 untestable), half the lactoferrin and a third of the S100A8 effect go with serum haemoglobin, the DS07 label contains band neutrophils, and SV-08 shows a response to infection with no severity gradient that tracks band counts. It remains a literature-driven gap lead, not a data-supported finding, and the human evidence itself is mixed. |
| K05 Angiopoietin-2 and the Ang-2/Ang-1 ratio | D | survives_weakened | D | No canine babesiosis study has measured angiopoietin-2, the human severity evidence is strong (systematic review of 11 falciparum studies, sepsis meta-analysis of 33 studies) and a validated canine Ang-2 ELISA exists with prognostic data in canine sepsis. The candidate is weakened only because Ang-1 could not be measured with the validated kit, so the Ang-2/Ang-1 ratio is not assayable in dogs; the lead should be restricted to Ang-2 and adjusted for haemolysis and creatinine. |
| K06 VWF, ultra-large multimers and ADAMTS13 | D | survives_weakened | D | No canine babesiosis study has measured VWF or ADAMTS13 against severity or outcome, and CB145, the obvious threat, measured factor activities but not VWF or ADAMTS13. Validated canine assays exist for both. The lead is weakened because the human VWF/ADAMTS13 ratio evidence rests largely on one small cohort and because the single canine measurement (CB446) found vWF activity lower, not higher, than in controls, so the direction of transfer cannot be assumed. |
| K07 VEGF and soluble VEGFR-1 (sFlt-1) | D | refuted | X | The gap itself is real: no canine babesiosis study has measured VEGF or sFlt-1, and CB122 only names VEGF as an enriched pathway. But the tier D rule fails on the other two conditions at once. The human severity evidence is grade 2 at best and inconsistent in direction for VEGF (protective in cerebral malaria, raised in uncomplicated malaria, low with immunosuppression in human babesiosis), while the stronger sepsis sFlt-1 evidence rests on one cohort; and no canine sFlt-1 assay exists, so the half with the better human case cannot be measured in dogs at all. |
| K08 Ferritin (hyperferritinaemia) | D | survives_weakened | D | Ferritin has never been measured against severity or outcome in canine babesiosis: the only measurement (CB242, 7 vs 7, infected versus healthy, no difference) has no severity contrast and no power, and CB132 is a single severe case with hyperferritinaemia. The human sepsis evidence is strong across three cohorts, and canine ferritin assays are in use. The lead is weakened because the malaria evidence is an infection contrast rather than a severity one, because no formal canine assay validation was found, and because ferritin in a haemolytic disease is heavily confounded by haemolysis and the acute-phase response. |
| K09 Kynurenine pathway (kynurenine:tryptophan) | D | survives_weakened | D | No canine babesiosis study has measured the kynurenine pathway against severity or outcome; CB091 is an infected-versus-healthy contrast, which my re-analysis of its supplement confirms is large (Kyn/Trp delta +0.86, p 3.8e-04). The human sepsis and critical-illness evidence is strong across several cohorts and a validated canine plasma LC-MS/MS assay exists, so tier D holds. It is weakened because the nearest severity proxy that can be computed now, the CB071 renal-function groups, shows no urinary kynurenine or tryptophan difference, because the malaria evidence is mostly CSF and cerebral, and because kynurenine is confounded by azotaemia and by inflammatory intensity. |

The screen-rejected candidates (X01 to X20) carry their screen reason as their refutation row. Sensitivity inside the themes: T02 with CCL2 in place of the monocyte count gives Z 4.80 (count was the conservative choice); without DS05 (the source that suggested the monocyte lead) T02 gives Z 2.31, p 0.0105, Bonferroni over 8 themes 0.084 (K01).

- Rerun: `out/` deleted and rebuilt with the commands in `run.md`; every CSV and JSON file came back byte-identical; the load file differs only in `run_utc`.

## 6. Confounders

- **Handled.** Sources counted after SV-07 (no dog counted twice in any theme; K01 checked); circular indicators removed from combined
  tests; known drivers flagged; species kept apart (rule 6) and only combined as a transfer check; DS05 monocyte association adjusted for
  haematocrit, total and differential leukocytes and illness days (K01); DS07 CD14, S100A8 and haemoglobin beta adjusted for each other
  and for acute-phase proteins (K01, K03, K04).
- **Not handled.** All dog-level *B. rossi* outcome data come from Onderstepoort (SRC-A, SRC-C) or are proxies (DS05 habitus) or a
  design contrast (5 Beagles by dose, with dose aliased with dog). Sample haemolysis in DS07 cannot be separated from in-vivo haemolysis.
  Treatment, time from onset and breed are not in most files. Died includes euthanasia for poor prognosis in the Onderstepoort files.

## 7. What this does not show

- No lead is a confirmed finding or a predictor. Every labelled file was already seen, the themes were chosen after the results, and the
  tier C lead rests mainly on the file that suggested it. A candidate is a thing to measure.
- Tier D leads say what to measure, not what will be found. Their human grades come from SV-06a (one agent's judgement, not reviewed
  by a person); the refutation sub-agents checked the gap, a human DOI and the canine assay for each.
- A rejected candidate (X) is not shown to be unimportant: most nulls come from small files (detectable effects about 0.76 to 1.3 SD).
- No clustering into groups of dogs and no predictive score. Between-file differences are not species effects.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files:** every census number (checked at its file and line); every theme indicator (read from a package file with its
  line, or computed here from the tidy files); the refutation checks (the sub-agents' scripts are in `refutation/scripts/`).
- **Taken from documentation:** package results as printed by each package; article contents from CB notes and texts; human evidence
  from PubMed records and the HU notes (DOIs in `out/leads.csv` and `refutation/K*.json`); SV-06a grades.
- **Inferred:** novelty (one database plus the local corpus; a parallel is "new" only if none was found); the tier boundaries (spec);
  that the DS07 red-cell protein signal may be sample haemolysis.

## 9. Next step and decisions for the user

1. **Cheapest test of the tier C lead:** dog-level monocyte counts and outcome from a non-Onderstepoort or larger *B. rossi* cohort. The
   SV-02c author request (already a user decision) could add "admission differential with absolute monocyte count" to its list (CB040,
   320 dogs). Decision: whether to extend SV-02c.
2. **Stored plasma:** most leads (cell-free haemoglobin with a haemolysis index, NETs/cfDNA, calprotectin, angiopoietin-2, VWF:ADAMTS13,
   sFlt-1, ferritin, kynurenine:tryptophan) need archived pre-treatment plasma with outcome. Decision: whether to ask the Onderstepoort
   group about a biobank (CB145 cohort) — contacting an author is a user decision.
3. **DS06 re-quantification** from SRA PRJNA703846 to recover MPO and ELANE (already raised by SV-08; large download).
4. **SV-10-03 minimum dataset:** add the measurements listed per lead (`out/leads.csv`, column `minimum_dataset_addition`).
5. Not a lead but worth noting: the K02 refutation left a weak, uncorrected signal that a higher reticulocyte count at a given
   haematocrit goes with a brighter dog in DS05 (rho +0.18, p 0.03). It could be tested in the DS03–S-CB050 join (SV-05/SV-09 decision 9).

### 4.5 Evidence map (second run, 2026-11-13)

The page draws the 29 candidates on an evidence map. It is a map of evidence, not a score: no probability, no ranking value. Every
position and colour is written by `scripts/build_load.py` to `out/evidence_map.csv` and to the payload `evidence_map`, by these rules:

- **Horizontal: canine evidence.** A candidate that was tier D before refutation (a gap lead) is at **0**: no canine data against
  severity (this includes K03 and K04, whose weak DS07 and Beagle data the refutation set aside). A theme-level candidate
  (`x_from_theme` in `candidates.json`: K01, K02, X01, X04 to X10, X15, X18) is at the number of non-circular indicators of its theme,
  any species, whose oriented effect is above zero (`out/themes.csv`). Any other candidate is at the number of distinct independent
  sources among its census rows that pass the statistical screen (`out/census.csv`).
- **Vertical: human evidence.** The number of verified human records whose direction agrees, from the `human_counterpart` list of the
  candidate's refutation file (`refutation/K*.json`). Records on dogs with another disease, and records the refutation marked as not
  verified, are not counted. A dashed ring marks a candidate with at least one disagreeing human record. Candidates rejected at the screen
  had no refutation attempt and sit in a "not assessed" band below zero.
- **Colour: final tier.** Leads (the 7 of `out/leads.csv`) are large and labelled with rank and short name; rejected candidates (X)
  are hidden at the start and dimmed when shown.
- **Overlap.** Marks with the same position get slots (leads first, by rank, then by id); the page spreads them by a fixed step.
- **Labels.** The short labels and the short card items are editorial text in `scripts/candidates.json` (`short_label`, `short_name`,
  `refuted_short`, `existing_short`, `new_short`, `md_short`, `canine_line`); the chip label of a human record is the first disease
  keyword found in its claim text (rule in `build_load.py`).

Positions (x, y): K01 Monocytes (5, 4, mixed); K04 NETs and degranulation (0, 4, mixed); K03 cell-free haemoglobin (0, 4); K05
angiopoietin-2 (0, 4); K06 VWF and ADAMTS13 (0, 3); K08 ferritin (0, 4); K09 kynurenine (0, 5). Refuted: K02 (1, 5), K07 (0, 1, mixed).

## Software and outputs

Python 3.12.12 (uv 0.10.4), numpy 2.3.4, scipy 1.16.3; Claude sub-agents for the refutation attempts; .NET console loader (way B);
Angular view `experiment-meta-review-view.component.*` with `views/meta-review/meta-evidence-map.component.*` and
`views/meta-review/meta-lead-card.component.*`. Outputs: `out/census.csv`, `out/themes.csv`, `out/leads.csv`, `out/refutation.csv`,
`out/candidates.csv`, `out/evidence_map.csv`, `out/theme_indicators.json`, `out/tiers.json`, `out/db/SV-META-01-research-leads.json`
(8 results: `primary_result`, `evidence_map`, `leads`, `themes`, `candidates`, `refutation`, `census`, `interpretation`).

**Second run, 2026-11-13 (presentation only).** On user feedback that the page was text-heavy, the view was redesigned: a one-line
headline with tier tiles, the evidence map (section 4.5), one tab per lead with only the selected lead's card (a forest plot of the
theme indicators, or a "no canine data" note for a gap lead; human records as chips; long text behind a closed Details), and the
supporting tables in closed sections. `build_load.py` gained the evidence map, the compact lead fields, a shorter summary and a shorter
interpretation. No analysis changed: every tier, effect and lead is the same, and `out/` rebuilt from empty gives the same CSV files
as the first run (the load file differs only in `run_utc` and the new payload fields).
