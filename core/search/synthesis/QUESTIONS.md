# Candidate research questions

Five research questions that link the pathophysiology priorities in the category syntheses (ERY, INF, END, COA, REN, PUL, NEU, CAR, MET, OXO, SEV; 2006–2026) to the verified datasets in [datasets.md](datasets.md), or that state which data are still needed. Links are relative to the review root.

**Ground rules for every question**

- These are questions, not findings. None of the analyses below has been run. No result, effect direction or "subtype" is promised.
- "Verified" means status 1 in [datasets.jsonl](datasets.jsonl), a public download that was checked. Request-only records (RQ-…) are unverified and may never be released.
- Every verified dataset is small for its number of features, so ordinary statistics come first. Machine learning is mentioned only where it is not ruled out, and then only as penalised regression with animal-level resampling.
- Novelty was checked against PubMed on 2026-10-23 with NCBI E-utilities (esearch, then efetch abstracts). Only abstracts were read, so full texts could still hold relevant analyses. On 2026-10-28 the labels were re-checked against the 2006–2026 included set, without a new PubMed search; where an included 2006–2016 paper covers part of a question, the label says so and cites it. PubMed hits that are now included articles carry their IDs.
- Cohort overlaps follow [cohorts.json](cohorts.json). Papers from the same cohort, or datasets from the same source (S-CB517 and S-CB050, SRC-A), are not independent replication.

---

## Q1. Haemolysis, free haem, endothelial activation and tubular injury in large-*Babesia* infection

**Hypothesis.** In dogs naturally infected with *B. rossi* or *B. canis*, plasma cell-free haemoglobin (CFH) at admission, and depletion of its scavengers haptoglobin and haemopexin, is associated with endothelial activation (angiopoietin-2, syndecan-1, VCAM-1) and with urinary tubular injury markers (uNGAL and KIM-1, each normalised to urine creatinine). The association is expected to hold after adjustment for haematocrit, parasitaemia, lactate and mean arterial pressure (MAP). Serum urea is not a renal outcome here, because the raised urea of babesiosis is mostly not renal (CB325).

There is a stated counter-hypothesis. In healthy dogs, experimental haemoglobinaemia alone did not cause nephropathy (Lobetti 1996, PMID 9284030). In the CH29 dogs, induced haemoglobinaemia did not reproduce the raised urea:creatinine ratio of babesiosis, and GFR was normal ([CB412](articles/CB412_2011_changes-serum-urea-creatinine-ratio-babesiosis.md)). Any CFH association may therefore depend on co-factors such as hypoxia, hypotension, inflammation or acidic, methaemoglobin-rich urine, rather than on a direct effect of CFH.

**Supporting canine papers**

- Tubular and glomerular injury before azotaemia:
  - *B. rossi*: urinary IgG, CRP and RBP rose while serum creatinine did not in [CB435](articles/CB435_2012_assessment-renal-dysfunction-using-urinary-markers.md) (2012, CH36), so older work already shows this signal; [CB053](articles/CB053_2020_evaluation-acute-kidney-injury-complicated-or.md) adds NGAL.
  - *B. canis*: [CB024](articles/CB024_2018_glomerular-tubular-kidney-damage-markers-babesiosis.md).
  - Clustering of renal azotaemia with ARDS, cerebral signs and death: [CB025](articles/CB025_2018_renal-azotemia-associated-clinical-laboratory-findings.md).
- Tissue: [CB341](articles/CB341_2007_histological-ultrastructural-studies-renal-lesions-babesia.md) (2007, 8 fatal *B. canis* cases): tubular necrosis and capillary endothelial damage, attributed to hypoxia; 7 dogs had imidocarb.
- Raised urea with creatinine and cystatin-C in range: [CB325](articles/CB325_2006_elevated-serum-urea-creatinine-ratio-babesiosis.md) and CB412 (CH29, one source).
- Endothelial activation:
  - [CB446](articles/CB446_2013_markers-coagulation-activation-endothelial-stimulation-inflammation.md) (2013, 12 *B. canis* dogs): soluble ICAM-1 raised, von Willebrand factor activity lowered.
  - [CB004](articles/CB004_2017_blood-markers-fibrinolysis-endothelial-activation-babesiosis.md): VCAM-1 separated complicated from uncomplicated cases.
  - [CB145](articles/CB145_2026_thromboinflammation-virulent-babesiosis.md): fibrin microthrombi in several organs of non-survivors.
- Hypotension: MAP below 80 mmHg in 7 of 48 dogs, with pressure inversely related to creatinine ([CB463](articles/CB463_2014_association-between-decreased-blood-pressure-azotaemia.md)); TNF-α tracked low pressure in [CB473](articles/CB473_2014_increased-concentration-serum-tnf-alpha-correlations.md) (one Warsaw group).
- Scavenger proteins point in different directions:
  - Haptoglobin was low in [CB058](articles/CB058_2020_serum-amyloid-haptoglobin-ceruloplasmin-albumin-levels.md) and rose then fell after treatment in [CB323](articles/CB323_2006_evidence-acute-phase-response-naturally-infected.md).
  - Haemopexin was higher in [CB117](articles/CB117_2023_proteomics-identification-overexpressed-serum-proteins-babesiacanis.md) (3 vs 3 dogs).
- Extravascular haemolysis at necropsy in 5 dogs ([CB522](articles/CB522_2016_septic-shock-similarities-differences-postmortem-findings.md)) means CFH may not track total red-cell loss.
- CFH was measured in the experimental model ([CB098](articles/CB098_2022_kinetics-inflammatory-response-during-experimental-babesia.md), [CB101](articles/CB101_2022_dataset-inflammatory-response-during-experimental-infection.md)), with a haemolytic transcriptional signature in [CB082](articles/CB082_2021_experimental-babesia-rossi-infection-induces-hemolytic.md) (all CH09).
- Proposed but untested mechanisms: [CB231](articles/CB231_2023_pathogenetic-relationship-between-kidney-pathologies-microcirculatory.md) and [CB157](articles/CB157_2017_over-20-years-research-babesiosis-faculty.md).

**Human comparators**

- **Mechanistically plausible (REN):** CFH and lipid peroxidation are linked to AKI in falciparum malaria ([HU002](articles/HU002_2017_cell-free-hemoglobin-mediated-oxidative-stress.md)).
- **Speculative (ERY):** haem–haemopexin dysregulation predicts death in malaria ([HU003](articles/HU003_2015_dysregulation-haem-haemopexin-axis-associated-severe.md)).
- **Endothelial markers:**
  - Haemolysis-linked endothelial activation and angiopoietin-2 (Ang-2) as AKI risk factors in *P. knowlesi* malaria: [HU010](articles/HU010_2018_intravascular-haemolysis-severe-plasmodium-knowlesi-malaria.md).
  - Glycocalyx shedding: [HU011](articles/HU011_2019_glycocalyx-breakdown-associated-severe-disease-fatal.md) (speculative).
  - Ang-2 and severe AKI in sepsis: [HU012](articles/HU012_2021_angiopoietin-2-outperforms-other-endothelial-biomarkers.md) (mechanistically plausible).
- **Directly demonstrated in both hosts, malaria in humans:** uNGAL and KIM-1 before a creatinine rise ([HU013](articles/HU013_2016_neutrophil-gelatinase-associated-lipocalin-ngal-predicts.md)).
- No human *babesiosis* study measured CFH or tubular markers.

**Datasets and variables**

- **Verified, for hypothesis generation only:** [DS01](datasets.md#ds01), or [DS02](datasets.md#ds02) but not both (they hold the same 5 infected Beagles, CH09).
  - Per-dog CFH: sparse, 23 values over days 1–8, units not stated.
  - Haematocrit and haemoglobin, parasitaemia, venous lactate, MAP, CRP and albumin (DS02), and 13 cytokines.
  - No renal or endothelial markers.
- [S-CB516](datasets.md#s-cb516) (verified) has per-dog pigmenturia and outcome for 15 *B. canis* dogs but no laboratory values. The 2006–2016 renal and endothelial papers have no listed dataset.
- **Still needed:** a prospective natural-infection cohort in which all of the following are measured in the same admission sample:
  - CFH, from a standardised, haemolysis-controlled draw.
  - Haptoglobin, haemopexin and free haem.
  - Ang-2, syndecan-1 and VCAM-1.
  - Urinary NGAL, KIM-1, uCr, UPC and dipstick haem, plus serum creatinine and SDMA.
  - Parasitaemia by qPCR, lactate and MAP.
  - Ideally repeated at 24 h and 72 h.
- Neither data source has been obtained: RQ-CB145 is request-only, and CB053 has no dataset.

**Feasible analysis**

- *DS01/DS02:* dog-level trajectory plots of CFH against haematocrit, lactate, MAP and parasitaemia. Within-dog rank correlations with permutation p-values. No inference beyond temporal ordering in 5 dogs.
- *New cohort:*
  - Pre-specified linear regression of log(uNGAL/uCr), with a continuous outcome to avoid relying on few deaths. Log CFH is the exposure, adjusted for haematocrit, log parasitaemia, lactate and MAP, with restricted cubic splines where needed. Fit species-stratified models, then test a species interaction.
  - Repeated samples: a linear mixed model with a random intercept per dog.
  - A mediation-style decomposition (CFH to Ang-2 to uNGAL) only as description, because exposure ordering in cross-sectional samples is uncertain.
  - Ordinary statistics are preferable to ML. The question is about one pre-specified pathway, not prediction.
- *Sample size:* with roughly 10–12% mortality in *B. rossi*, about 100 dogs give only 10–12 deaths. Death can therefore carry at most one or two predictors (Firth logistic), and the continuous injury outcome should be primary.

**Principal confounders**

- In vitro haemolysis during sampling, which falsely raises CFH.
- Haemoglobinuria and urine concentration affecting urinary marker assays.
- Transfusion of stored red cells before sampling (storage-lesion CFH).
- Diminazene or imidocarb (CB341), fluids, and time since onset.
- Hypotension and hypoxia as shared causes (CB463, CB341).
- *E. canis* co-infection.
- Species: *B. rossi* is mainly from South African referral hospitals, *B. canis* from European clinics.
- Referral selection.

**Validation required**

- An independent second centre, and *B. canis* replication under the same pre-analytical protocol.
- Prospective sampling before treatment.
- Marker–histology concordance in fatal cases: kidney tissue from the CH04 tissue bank, if it exists, with electron microscopy as in CB341.

**Prior-work search (PubMed)**

1. `(babesia OR babesiosis) AND (dog OR dogs OR canine) AND (haptoglobin OR hemopexin OR haemopexin OR "free hemoglobin" OR "cell-free hemoglobin" OR heme OR haem)`, 6 hits:
   - Haptoglobin as an acute-phase protein in *B. canis*: low in Ulutas 2005 (PMID 15902667); rose after treatment in Matijatko 2007 (PMID 17116368, = CB323).
   - Haemopexin higher in 3 infected dogs (Ritchoo 2023, PMID 38023278, = CB117).
   - Carboxyhaemoglobin from haem catabolism (Taylor 1991, PMID 1770488).
   - Globin electrophoresis (PMID 8691410).
   - A porcine case (PMID 33490140).
2. `… AND (NGAL OR lipocalin OR KIM-1 OR "acute kidney injury") AND (hemolysis OR haemolysis OR hemoglobinuria OR haemoglobinuria OR endothelial OR angiopoietin OR syndecan)`, 1 hit: Defauw 2018 (PMID 30197009, = CB025). Haemoglobinuria was noted as a confounder of urine specific gravity; NGAL was not measured.
3. `… AND (angiopoietin OR syndecan OR glycocalyx OR "von Willebrand")`, 3 hits:
   - Barić Rafaj 2013 (PMID 23875771, = CB446): sICAM-1 up, vWF activity down.
   - A *Rangelia* report and a case report.
   - No Ang-2 or glycocalyx data in dogs.
4. `… AND (kidney OR renal OR urinary OR azotemia OR azotaemia) AND (hemoglobin* OR haemoglobin* OR hemolysis OR haemolysis OR pigment)`, 17 hits. The relevant ones are:
   - Lobetti 1996 (PMID 9284030): experimental haemoglobinaemia did not cause significant nephropathy.
   - Lobetti 1996 (PMID 8765069): methaemoglobinuria with aciduria.
   - Defauw 2012 (PMID 22884913, = CB435) and Kuleš 2018 (PMID 30057291): urinary markers, without haem measures.
5. Re-check (2026-10-28): CB412, CB325 and CB341 add renal work without CFH or scavengers.

**Result.** No canine study was found that measured CFH or haem scavengers together with endothelial or tubular injury markers in the same dogs. **Novelty: potential gap in the literature searched, with partial prior work** (CB412 on haemoglobin load; CB435 and CB341 on tubular injury without haem measures). The negative haemoglobinaemia studies make a simple "CFH causes AKI" model unlikely in dogs.

---

## Q2. Coupling of inflammation and coagulation, and death, in *B. rossi*

**Hypothesis.** In naturally infected *B. rossi* dogs, admission chemokine and cytokine concentrations (MCP-1, IL-6) and neutrophil activation (MPXI) correlate with coagulation-factor consumption (prolonged PT and aPTT, low factor activities, D-dimer). The two axes are expected to carry largely overlapping rather than additive information about death, consistent with one thromboinflammatory process. The opposite result, additive information, would also be informative. CRP and SAA are not expected to carry this information, because they did not separate outcome in two sources (CB376, CB517).

**Supporting canine papers**

- CH03 (Onderstepoort, Oct 2011–Apr 2013), one source in six papers:
  - Cytokines: [CB517](articles/CB517_2016_excessive-pro-inflammatory-serum-cytokine-concentrations.md) (2016): IL-6 and MCP-1 higher in the 12 non-survivors; CRP and SAA did not separate outcome. [CB050](articles/CB050_2020_neutrophil-myeloperoxidase-index-babesiosis-caused-babesia.md): MPXI above controls in non-survivors.
  - Coagulation and death: [CB145](articles/CB145_2026_thromboinflammation-virulent-babesiosis.md) found prolonged PT/aPTT, low factor activities, fibrinolytic shutdown and fibrin microthrombi in non-survivors. It reports the same 97 dogs as CB517.
  - Cellular coupling: in [CB504](articles/CB504_2015_platelet-activation-platelet-leukocyte-interaction-naturally.md) (36 dogs, 7 died), platelet-monocyte aggregates were above controls in survivors but not in non-survivors.
  - No platelet index differed by outcome in [CB513](articles/CB513_2015_platelet-indices-babesia-rossi-infection.md). Lymphocyte data for the 2014 cohort: [CB008](articles/CB008_2017_flow-cytometric-assessment-lymphocyte-immunophenotypes-naturally.md).
- Other *B. rossi* sources (overlap with CH03 not stated):
  - [CB438](articles/CB438_2012_mortality-virulent-babesiosis-associated-consumptive-coagulopathy.md) (2012; 72 dogs, 13 died): lower factor and protein C activity, longer PT and aPTT and higher D-dimer in non-survivors. Older work thus already ties consumption to death.
  - Admission CRP did not separate outcome ([CB376](articles/CB376_2009_c-reactive-protein-babesiosis-caused-babesia.md), 2009). [CB037](articles/CB037_2019_disease-severity-blood-cytokine-concentrations-natural.md): IL-6, MCP-1 and TNF-α higher in the 9 dogs that died.
  - TEG: [CB439](articles/CB439_2012_hemostatic-abnormalities-uncomplicated-babesiosis-babesia-rossi.md) (CH36, uncomplicated dogs) and [CB034](articles/CB034_2019_thromboelastographic-platelet-mapping-complicated-babesia-rossi.md) (preserved platelet function). Intra-alveolar fibrin: [CB111](articles/CB111_2023_lung-pathology-natural-babesia-rossi-infection.md).
- Experimental *B. canis*: dose shifted the timing of the CRP, fibrinogen and platelet curves together ([CB370](articles/CB370_2009_systemic-inflammatory-responses-experimentally-infected-babesia.md), 2009), with no outcome.
- *B. canis* counterparts (Zagreb): TAT up and antithrombin III down in [CB374](articles/CB374_2009_alterations-some-blood-coagulation-parameters-naturally.md) (2009) and [CB011](articles/CB011_2017_alteration-haemostatic-parameters-uncomplicated-babesiosis.md); endothelial markers in [CB004](articles/CB004_2017_blood-markers-fibrinolysis-endothelial-activation-babesiosis.md) and [CB446](articles/CB446_2013_markers-coagulation-activation-endothelial-stimulation-inflammation.md); MCP-1, KC-like and IL-8 in complicated disease in [CB017](articles/CB017_2018_mcp-1-kc-like-il-8.md) and [CB510](articles/CB510_2015_serum-levels-chemokines-keratinocyte-chemoattractant-interleukin.md) (CH23, one source).

**Human comparators**

- Admission IL-8 and TNF predict death in cerebral malaria: [HU004](articles/HU004_2023_elevated-plasma-interleukin-8-risk-factor.md). INF cytokine–severity link rated directly demonstrated in both hosts.
- Neutrophil activation:
  - [HU005](articles/HU005_2016_activated-neutrophils-are-associated-pediatric-cerebral.md) and [HU006](articles/HU006_2026_whole-blood-transcriptomics-reveals-sepsis-mortality.md): mechanistically plausible.
- NET-forming capacity predicts DIC and death in sepsis: [HU008](articles/HU008_2019_novel-assay-neutrophil-extracellular-trap-formation.md). Speculative.
- Ultra-large VWF in severe malaria: [HU009](articles/HU009_2009_severe-plasmodium-falciparum-malaria-associated-circulating.md).
- DIC in severe human babesiosis: [HU007](articles/HU007_2001_severe-babesiosis-long-island-review-34.md). COA rated mechanistically plausible.

**Datasets and variables**

- **Verified:** [S-CB050](datasets.md#s-cb050) (SRC-A).
  - 161 dogs: 141 infected, of whom 15 died, plus 20 controls.
  - Per dog: WBC, segmented and band neutrophils, MPXI, IL-2, IL-6, IL-8, IL-10, IL-18, GM-CSF, MCP-1, age, weight, sex and survival.
  - Cytokines are available only in cohort 1 (the CH03 period), with 12 deaths.
  - No coagulation variables.
- **Verified:** [S-CB517](datasets.md#s-cb517) (SRC-A, the same cohort-1 dogs).
  - 97 infected dogs (12 died) and 15 controls, one admission sample each.
  - Adds SAA, CRP and the full leukocyte differential to the same 7 cytokines; no age, sex, days sick or coagulation. Join it to S-CB050; never pool the two.
- **Request-only, unverified:** [RQ-CB145](datasets.md#rq-cb145).
  - Likely per-dog TEG, PT, aPTT, factor activities, fibrinogen, D-dimer and α2-antiplasmin, plus CRP and SAA, for 97 dogs from the same hospital and period.
  - Because CB145 and CB517 report the same 97 dogs, linkage with S-CB517 and S-CB050 by case number is plausible but unconfirmed.
- CB438, CB504 and CB374 have no listed dataset. [S-CB476](datasets.md#s-cb476) is a protein list from pooled *B. canis canis* sera, with no per-dog values.
- **If linkage fails:** a new prospective cohort with cytokines, MPXI, a coagulation panel and, ideally, a NET marker (cfDNA or citrullinated H3, with validation in dogs), all in the same pre-treatment sample.

**Feasible analysis**

- Pre-specify two scores before looking at outcome:
  - An inflammation score: mean of standardised log MCP-1 and log IL-6.
  - A coagulation score: for example, standardised aPTT and a mean factor activity.
- Estimate their Spearman correlation with a bootstrap CI.
- Fit Firth-penalised logistic models for death with each score alone, then both together, and report the bootstrap optimism-corrected change in AUC with its CI.
- A comparison score of log CRP and log SAA (S-CB517) tests whether any coupling is specific to cytokines.
- Univariable contrasts: exact Mann–Whitney tests with Holm correction. Treat cytokines at their floor or ceiling as censored (rank methods or Tobit).
- Add cohort as a stratum. Never impute cohort-2 cytokines, which are structurally missing.
- With about 12 deaths, nothing beyond 2 predictors per model is defensible. The deliverable is effect sizes and CIs for planning, not a prognostic tool. ML is not appropriate.
- There is one row per dog, so no repeated-measures issue arises at admission.

**Principal confounders**

- The "died" label includes euthanasia for poor prognosis.
- Sampling relative to diminazene and transfusion: transfusion dilutes factors and adds donor plasma.
- Haemolysed and icteric plasma can interfere with optical coagulometry.
- Time since onset.
- *E. canis* co-infection.
- Referral selection.
- Prior publication of the same dogs (CH03; possibly CB438).

**Validation required**

- An independent *B. rossi* cohort from another centre or period.
- *B. canis* replication with harmonised assays, for example through the Zagreb group (CB004, CB011, CB374).
- Prospective serial sampling at 0, 24 and 48 h, to test whether the inflammatory change precedes or follows coagulation consumption.

**Prior-work search (PubMed)**

1. `(babesia OR babesiosis) AND (dog OR dogs OR canine) AND (cytokine* OR chemokine* OR MCP-1 OR interleukin* OR myeloperoxidase OR neutrophil*) AND (coagulation OR thromboelastograph* OR fibrin* OR D-dimer OR DIC OR thrombo*)`, 21 hits. None measured cytokines, MPO or NETs together with coagulation assays in the same dogs. Furlanello 2005 (PMID 16112810) had coagulation tests and lymphocyte morphology only.
2. `(babesia rossi OR babesiosis) AND (dog OR dogs OR canine) AND (thromboinflammation OR hemostasis OR haemostasis OR "factor activity" OR thromboelastography OR antithrombin OR fibrinolysis)`, 14 hits, including:
   - Goddard 2026 (PMID 41908963, = CB145): coagulation with CRP and SAA, 97 dogs.
   - Goddard 2013 (PMID 23098634, = CB438): factor activities, PT/aPTT and D-dimer associated with death, 72 dogs.
   - Goddard 2015 (PMID 26088270, = CB504): platelet–leukocyte aggregates and CD62P in 36 dogs, with 7 deaths. This is a cellular measure of the same coupling.
   - Kuleš 2017 (PMID 28363279, = CB004): endothelial plus fibrinolytic markers in *B. canis*.
   - Liebenberg 2013 (= CB439) and van Rooyen 2019: TEG.
3. The IL-8 search for Q3 also retrieved Goddard 2016 (PMID 26953797, = CB517). It is the cytokine paper for the CH03 cohort, and it reported IL-6 and MCP-1 higher in non-survivors in samples taken before treatment.
4. Re-check (2026-10-28): CB370, CB374, CB376 and CB513 add single-axis or experimental work.

**Result.** Each axis has been related to death separately in this population (CB438, CB517, CB145), the cellular coupling has been examined (CB504), and both axes were followed together in experimental *B. canis* without outcome (CB370). No study was found that analysed soluble cytokines or neutrophil activation jointly with coagulation-factor consumption in the same dogs. **Novelty: potential gap in the literature searched, with partial prior work.** Because the originating group may already hold both data types for the same 97 dogs, the gap may be in publication rather than in data.

---

## Q3. Does the IL-8 (CXCL8) response really differ between *B. rossi* and *B. canis*?

**Hypothesis.** The published direction of circulating IL-8 differs by species: low relative to controls and lower with severity in *B. rossi*, but rising over time, inversely related to haematocrit and higher in complicated disease in *B. canis*. The question is whether this divergence persists after accounting for three things:

- neutrophil count, or the granulocyte:lymphocyte ratio, which tracked IL-8 in *B. canis* (CB510);
- sampling time relative to treatment;
- day of infection.

If it persists it is a candidate species difference. If it disappears it is a design artefact. In experimental *B. rossi*, the within-dog prediction is that IL-8 falls below each dog's own pre-infection baseline as parasitaemia rises.

**Supporting canine papers**

- *B. rossi*:
  - IL-8 lower than in controls, before treatment: [CB517](articles/CB517_2016_excessive-pro-inflammatory-serum-cytokine-concentrations.md) (2016, CH03), with only weak correlations with leukocyte counts (per the S-CB517 record).
  - IL-8 fell with severity: [CB037](articles/CB037_2019_disease-severity-blood-cytokine-concentrations-natural.md).
  - IL-8 correlated inversely with MPXI: [CB050](articles/CB050_2020_neutrophil-myeloperoxidase-index-babesiosis-caused-babesia.md) (CH03, same source as CB517).
  - IL-8 differed by inoculum dose: [CB098](articles/CB098_2022_kinetics-inflammatory-response-during-experimental-babesia.md) and [CB101](articles/CB101_2022_dataset-inflammatory-response-during-experimental-infection.md).
- *B. canis*, one cohort (CH23):
  - KC-like higher in complicated disease, IL-8 rising and inversely correlated with haematocrit (rs about −0.60) ([CB017](articles/CB017_2018_mcp-1-kc-like-il-8.md)).
  - KC-like and IL-8 higher in complicated disease, IL-8 correlated with the granulocyte:lymphocyte ratio ([CB510](articles/CB510_2015_serum-levels-chemokines-keratinocyte-chemoattractant-interleukin.md), 2015, = [CB511](articles/CB511_2015_razine-kemokina-kc-i-il-8.md); abstract only, n not stated). It probably used the same stored sera as CB017, so it is not replication.
- Leukogram conflict: leukopenic SIRS in *B. canis* ([CB073](articles/CB073_2021_systemic-inflammatory-response-syndrome-naturally-infected.md)), but leukocytosis in complicated disease in [CB355](articles/CB355_2008_case-controlled-retrospective-study-causes-implications.md) (2008, species unstated) and CB510.
- Review hypothesis of cytokine-driven anaemia: [CB107](articles/CB107_2023_pathogenesis-anemia-babesiosis-possible-contribution-pro.md).

**Human comparators**

- Admission IL-8 is an independent mortality risk factor in paediatric cerebral malaria: [HU004](articles/HU004_2023_elevated-plasma-interleukin-8-risk-factor.md). This is the opposite direction to *B. rossi*. The INF connection is rated directly demonstrated in both hosts for cytokines in general, but the IL-8 direction itself is contradictory.
- Neutrophil activation: [HU005](articles/HU005_2016_activated-neutrophils-are-associated-pediatric-cerebral.md) and [HU006](articles/HU006_2026_whole-blood-transcriptomics-reveals-sepsis-mortality.md).
- IL-8 as a driver of NET formation in sepsis: [HU008](articles/HU008_2019_novel-assay-neutrophil-extracellular-trap-formation.md).

**Datasets and variables (all verified)**

- [DS01](datasets.md#ds01) (or DS02, not both): experimental *B. rossi*, 5 dogs.
  - IL-8, KC-like and 11 other cytokines on days −1, 0, 1, 2, 3, 4, 6 and 8.
  - Neutrophils, bands, parasitaemia and haematocrit, daily.
- [S-CB050](datasets.md#s-cb050) or [S-CB517](datasets.md#s-cb517), never as two cohorts (SRC-A): natural *B. rossi*, CH03 cohort 1.
  - S-CB050: about 112 dogs with cytokines, IL-8 with segmented and band neutrophils, MPXI, survival, and controls.
  - S-CB517: the same dogs with lymphocyte counts, so the CB510 ratio can be computed; 17 rows with differentials far below WBC need checking first.
- [S-CB017](datasets.md#s-cb017): natural *B. canis*.
  - 31 infected dogs (18 complicated, 13 uncomplicated) on days 1 and 7, plus 16 controls.
  - IL-8, KC-like, MCP-1 and 6 other cytokines, with 16 haematology variables.
  - The day-1 sample was drawn 6–8 h after imidocarb.
- CB510 has no dataset. RQ-CB536 (request-only, 58 Polish *B. canis* dogs from a *Dirofilaria repens* study) is not expected to help.
- **Still needed:** a head-to-head study of both species with one laboratory, one assay lot and samples taken before treatment. Split serum and plasma aliquots would test effects of sample type.

**Feasible analysis**

- Do not pool raw concentrations across datasets, because platform, laboratory, sample type and timing differ.
- Within each dataset:
  - Estimate the infected-versus-control ratio of geometric means, or a Hodges–Lehmann shift on the log scale, with exact CIs.
  - Do the same for severity contrasts: died versus survived in S-CB050 or S-CB517, complicated versus uncomplicated in S-CB017.
  - Then fit log IL-8 ~ group + log neutrophil count (and, separately, the granulocyte:lymphocyte ratio) to see whether the contrast survives adjustment.
- S-CB017 has repeated measures (days 1 and 7). Use a linear mixed model with a random intercept per dog.
- DS01: within-dog change from baseline (mean of days −1 and 0), plotted per dog, with permutation tests. Run a sensitivity analysis that excludes the dog-5 saturated values and the dog-6 terminal sample. With 5 dogs, report effect sizes and ranges rather than p-values.
- Display the species contrast side by side. A formal heterogeneity estimate is descriptive only.
- Ordinary statistics only. ML has no role.

**Principal confounders**

- Treatment: S-CB017 day 1 is after imidocarb; *B. rossi* samples were taken before treatment (CB517) or at an unstated time (S-CB050).
- Time since onset; S-CB517 has no days-sick column.
- Neutrophil count and left shift.
- Assay floors and ceilings, with censored values recorded as 0 or as the minimum detectable value.
- Control groups differ: 8 of the S-CB017 controls received prophylactic imidocarb.
- Severity definitions differ: WHO-malaria criteria versus death.
- Geography and breed.
- Co-infection.

**Validation required**

- A prospective two-species study with a single laboratory and samples taken before treatment.
- Spike-recovery of IL-8 in haemolysed and non-haemolysed canine samples.
- Independent replication outside Onderstepoort and Zagreb.

**Prior-work search (PubMed)**

`(babesia OR babesiosis) AND (dog OR dogs OR canine) AND ("interleukin-8" OR IL-8 OR CXCL8 OR KC-like OR "keratinocyte chemoattractant")`, 6 hits:

- Zygner 2023 (review, = CB107).
- Atkinson 2022 (PMID 35606218, = CB098).
- Celliers 2020 (PMID 32133380, = CB050).
- Leisewitz 2019 (PMID 31063593, = CB037).
- Galán 2018 (PMID 29304171, = CB017).
- Goddard 2016 (PMID 26953797, = CB517): IL-8 "significantly decreased" in infected dogs compared with controls, in samples taken before treatment.

None compares IL-8 across species within one study. Galán 2018 contrasts its pattern with *B. rossi* only across studies. Re-check (2026-10-28): CB510 and CB511 are not in PubMed, so the first search missed them; they cover one species.

**Result. Novelty: potential gap in the literature searched, with partial prior work** (IL-8 against leukocytes within each species: CB510, CB517). This is a reanalysis question with existing verified data. It can test whether the conflict is explained by measured design factors. It cannot show a true species difference without the head-to-head study.

---

## Q4. Why is erythropoiesis inadequate in *B. rossi*: marrow lag, suppression or iron restriction?

**Hypothesis.** In natural *B. rossi* infection, the absolute reticulocyte count (ARC) for a given haematocrit is lower than in IMHA. The question is whether this shortfall persists after adjustment for owner-reported duration of illness, that is, whether it is more than a marrow-lag effect in dogs that present early. If reticulocyte haemoglobin content (CHr) is reduced relative to controls, that would point to iron-restricted erythropoiesis.

**Supporting canine papers**

- *B. rossi*, Onderstepoort (separate cohorts from one group):
  - Serial haematology in 86 uncomplicated dogs: red-cell response weaker than the haemolysis predicts ([CB418](articles/CB418_2011_serial-haematology-results-transfused-non-transfused.md), 2011), the earliest report of the core finding.
  - ARC above controls but below IMHA, and ARC fell about 48 h after experimental parasitaemia: [CB115](articles/CB115_2023_regenerative-response-naturally-experimentally-infected-babesia.md).
  - Dyserythropoiesis and increased marrow iron in fatal cases: [CB129](articles/CB129_2024_cytological-histopathological-bone-marrow-findings-natural.md) (CH04).
  - The source study for DS05: [CB126](articles/CB126_2024_prevalence-co-infections-ehrlichia-spp-or.md).
- Suppression: serum from *B. gibsoni*-infected dogs slowed reticulocyte maturation in vitro ([CB337](articles/CB337_2007_suppressive-effect-culture-supernatant-erythrocytes-serum.md), 2007; 3 infected donors).
- Analyser artefact: abnormal reticulocyte profiles in 20 of 92 large-form dogs ([CB538](articles/CB538_2016_spurious-reticulocyte-profiles-large-form-babesiosis.md), [CB540](articles/CB540_2016_spurious-reticulocyte-profiles-babesiosis.md), 2016).
- *B. canis*: non-regenerative at admission, reticulocytosis by day 14, which favours timing ([CB251](articles/CB251_2024_reticulocyte-response-paired-blood-samples-babesia.md)).
- Iron findings conflict:
  - Low transferrin saturation in *B. canis*: [CB177](articles/CB177_2018_changes-erythrocytopoesis-indices-babesiosis.md).
  - High iron in *B. gibsoni*: [CB214](articles/CB214_2022_comparative-evaluation-darbepoetin-therapy-non-regenerative.md).
- Hepcidin and low haemoglobin density (CH08): [CB202](articles/CB202_2020_serum-hepcidin-clinical-prognostic-marker-discriminate.md) and [CB286](articles/CB286_2025_low-haemoglobin-density-anaemic-indicator-babesiosis.md).
- EPO, low in about 9% of infected dogs: [CB297](articles/CB297_2026_serum-erythropoietin-levels-babesia-affected.md).

**Human comparators.** None of the 27 HU notes addresses erythropoiesis or iron restriction directly, and none should be cited as support.

- [HU001](articles/HU001_2017_post-babesiosis-warm-autoimmune-hemolytic-anemia.md) (post-babesiosis warm AIHA, mechanistically plausible) concerns immune destruction, not marrow response.
- [HU003](articles/HU003_2015_dysregulation-haem-haemopexin-axis-associated-severe.md) concerns haem handling.

The human analogue (malarial dyserythropoiesis) is outside the comparator set and would need its own search.

**Datasets and variables**

- [DS03](datasets.md#ds03) (verified, SRC-E):
  - 103 natural *B. rossi* dogs, 14 controls, and 16 IMHA dogs in the files; the abstract reports 10, a discrepancy to resolve first.
  - 5 experimental dogs sampled on days 1–6.
  - 12 ADVIA indices, including HCT, ARC, Ret%, CHr, CHDWr and MCVr, plus age, weight and sex.
  - No parasitaemia, platelets, outcome or treatment data.
- [DS05](datasets.md#ds05) (verified, independent source SRC-F, Eastern Cape):
  - 150 dogs: 149 *B. rossi*, 1 *B. vogeli*, and 3 *E. canis* co-infections.
  - Haematocrit, ARC, Ret%, owner-reported duration of illness, habitus, albumin and globulin.
  - No CHr and no analyser metadata.
- No 2006–2016 paper on this axis (CB418, CB337, CB538, CB540) has a listed dataset.
- **Still needed:**
  - Manual new-methylene-blue reticulocyte counts alongside automated counts.
  - qPCR parasitaemia.
  - Hepcidin, ferritin, serum iron and TIBC, and EPO.
  - Serial samples at days 0, 3, 7 and 14.

**Feasible analysis**

- DS03:
  - Linear regression of log ARC on haematocrit (spline) × group (*B. rossi* versus IMHA), plus age, with robust SEs. The group term and interaction describe the shortfall in regeneration.
  - CHr: Kruskal–Wallis or exact pairwise tests across controls, *B. rossi* and IMHA, then CHr ~ haematocrit by group.
  - The 12 indices are collinear and partly derived from one another, so do not rank feature importance.
  - Experimental dogs: within-dog trajectories, described only.
- DS05:
  - log ARC ~ haematocrit + duration of illness (spline or categories such as 0–2, 3–4 and ≥5 days) + age.
  - Test whether the ARC–haematocrit slope rises with duration.
  - The 3 co-infections allow only exact tests.
- Replication: compare the DS03 ARC–haematocrit slope for *B. rossi* with the DS05 slope as an out-of-sample check from an independent source, acknowledging that the analysers differ.
- Ordinary regression only. ML is not warranted with about 12 correlated variables and no outcome.

**Principal confounders**

- Automated pseudoreticulocytosis: parasitised erythrocytes counted as reticulocytes (CB538, CB540). This bias scales with parasitaemia, which neither dataset records, and the extent on the ADVIA is unverified.
- Time since onset, owner-reported and imprecise.
- Prior transfusion or treatment (CB418 compares transfused and non-transfused dogs).
- IMHA comparators may be on immunosuppressants.
- *E. canis* marrow suppression.
- Analyser differences between DS03 and DS05.
- Referral selection.
- Possible overlap of DS03 dogs with other Onderstepoort cohorts (unverifiable).

**Validation required**

- A prospective paired-sample study with manual reticulocyte counts and iron, hepcidin and EPO panels.
- *B. canis* and *B. gibsoni* comparison under the same protocol.
- Marrow cytology in a subset of surviving dogs, where ethical.

**Prior-work search (PubMed)**

`(babesia OR babesiosis) AND (dog OR dogs OR canine) AND (reticulocyte* OR erythropoie* OR hepcidin OR "reticulocyte hemoglobin" OR CHr OR ferritin OR iron)`, 31 hits. Relevant:

- Seejarim 2023 (PMID 37638541, = CB115): ARC in *B. rossi* lower than IMHA, an inadequate response. CHr was not reported in the abstract.
- Bumby 2024 (PMID 39995030, = CB129): marrow findings in 6 dogs.
- Piane 2016 (PMIDs 27701759 and 27755775, = CB538 and CB540): spurious reticulocyte profiles in 20 of 92 large-*Babesia* dogs on Sysmex analysers. In one dog the automated ARC was 60 versus 3.6 ×10⁹/L by manual count.
- Hossain 2003 and 2007 (PMIDs 14709814 and 17519571; 2007 = CB337): serum from *B. gibsoni*-infected dogs inhibits reticulocyte maturation in vitro.
- No study was found that adjusted reticulocyte response for illness duration, or that evaluated CHr in *B. rossi*.

Re-check (2026-10-28): CB418 adds serial data, without duration adjustment or CHr.

**Result.** The core descriptive finding (inadequate regeneration) is **already published**, first in serial form (CB418, 2011) and then against IMHA (CB115). Adjustment for illness duration, CHr-based assessment of iron restriction, and replication in an independent cohort are a **potential gap in the literature searched**. The pseudoreticulocytosis artefact (CB538, CB540) must be addressed before any conclusion is drawn.

---

## Q5. Does antibabesial treatment trigger an inflammatory surge, and does it precede organ deterioration?

**Hypothesis.** In natural large-*Babesia* infection, diminazene or imidocarb is followed within 6–24 h by a transient rise in pro-inflammatory cytokines and a fall in haematocrit. The size of that rise is expected to be associated with new respiratory or renal dysfunction within the next 48 h, independently of severity before treatment.

**Supporting canine papers**

- Experimental *B. rossi*: [CB098](articles/CB098_2022_kinetics-inflammatory-response-during-experimental-babesia.md) and [CB101](articles/CB101_2022_dataset-inflammatory-response-during-experimental-infection.md) report that "Treatment enhances the inflammatory response in the immediate post-treatment period".
- *B. canis*: day-1 samples were drawn 6–8 h after imidocarb, with no pre-treatment comparison ([CB017](articles/CB017_2018_mcp-1-kc-like-il-8.md)).
- Older post-treatment series in natural *B. canis*, none reporting a 6–24 h sample with an organ outcome: haptoglobin rose then fell ([CB323](articles/CB323_2006_evidence-acute-phase-response-naturally-infected.md), 2006); CRP fell by day 7 ([CB481](articles/CB481_2014_relationship-between-paraoxonase-1-activity-high.md)); lymphocyte subsets rose ([CB490](articles/CB490_2015_changes-selected-subpopulations-lymphocytes-infected-babesia.md)). PGE2 stayed high after therapy in MODS but not in SIRS ([CB470](articles/CB470_2014_serum-concentrations-eicosanoids-lipids-naturally-infected.md), abstract only), the only older link between post-treatment inflammation and organ dysfunction.
- Drug and transfusion effects: 7 of 8 fatal *B. canis* dogs with tubular necrosis had imidocarb ([CB341](articles/CB341_2007_histological-ultrastructural-studies-renal-lesions-babesia.md)). Central venous oxygen tension stayed low for 72 h after Oxyglobin or red-cell transfusion in 12 *B. rossi* dogs ([CB368](articles/CB368_2009_prospective-randomized-comparison-oxyglobin-hb-200.md)).
- ARDS onset about 14 h after admission, after a large transfusion: [CB102](articles/CB102_2022_successful-treatment-suspect-babesia-induced-ards.md).
- Lung lesions in fatal *B. rossi*: [CB111](articles/CB111_2023_lung-pathology-natural-babesia-rossi-infection.md).
- Multi-organ congestion and oedema in 6 fatal *B. canis* dogs, read as circulatory failure that fluid therapy could also produce: [CB080](articles/CB080_2021_disorders-blood-circulation-probable-cause-death.md).
- Renal azotaemia clustering with ARDS: [CB025](articles/CB025_2018_renal-azotemia-associated-clinical-laboratory-findings.md).
- Evidence against renal worsening: tubular markers fell within 24 h of treatment in [CB053](articles/CB053_2020_evaluation-acute-kidney-injury-complicated-or.md) (n=11).

**Human comparators**

- In human babesiosis, 6 of 8 ARDS cases began after antibabesial therapy started: [HU016](articles/HU016_2018_babesiosis-cause-acute-respiratory-distress-syndrome.md). The authors acknowledge confounding.
- AKI and intubation are associated with death: [HU015](articles/HU015_2025_pulmonary-manifestations-babesiosis-predictors-mortality-quaternary.md).
- Endothelial activation in malaria lung: [HU017](articles/HU017_2019_release-endothelial-activation-markers-lungs-patients.md).
- The PUL connection on post-treatment injury is rated **speculative**.

**Datasets and variables**

- **Verified:** [DS01](datasets.md#ds01) (or DS02, not both).
  - 5 experimental dogs, treated at 96 h (high dose) or 108 h (low dose).
  - Cytokines on days 4, 6 and 8, so there is no sample between treatment and about 48 h afterwards.
  - CRP on day 5, daily haematocrit, lactate and MAP.
  - There is no untreated infected control, so treatment cannot be separated from the natural course.
- [S-CB017](datasets.md#s-cb017) has samples only after treatment and cannot answer the question.
- [S-CB476](datasets.md#s-cb476) (pooled sera at admission, day 1 and day 6, protein lists only) and [S-CB106](datasets.md#s-cb106) (PCR after imidocarb, 9 dogs) cannot test a surge. S-CB517, S-CB050 and S-CB516 are single admission records.
- **Still needed:** a prospective natural-infection cohort (*B. rossi* and *B. canis*) with:
  - at least 2 samples before treatment;
  - samples 6, 12, 24 and 48 h after treatment;
  - cytokines, CRP, haptoglobin, haematocrit and CFH;
  - SpO₂ or PaO₂/FiO₂;
  - creatinine and uNGAL;
  - recorded fluid balance and the timing and volume of transfusion;
  - drug, dose and time of administration.

**Feasible analysis**

- Interrupted time series within each dog: a linear mixed model of log cytokine with a random intercept (and, if supported, a random slope) per dog. It estimates the pre-treatment trend and the post-treatment level and slope change, so that the post-treatment value is not attributed to treatment when it continues an existing trend.
- New organ dysfunction within 48 h will be a rare event. Use Firth logistic regression with one exposure (change from pre-treatment to peak), adjusted for one pre-treatment severity measure, or exact tests.
- Use a landmark at the time of treatment to avoid immortal-time bias.
- DS01: per-dog plots only. No inference about treatment effects is possible.
- Ordinary statistics only.

**Principal confounders**

- Confounding by time: disease would progress without treatment.
- Severity at the time of treatment, which also determines when treatment is given.
- Transfusion and fluids given at the same time (TRALI/TACO).
- Drug and dose, including possible imidocarb nephrotoxicity (CB341).
- Species.
- Time since onset.
- Co-infection.
- An untreated control is unethical. Designs must rely on within-dog pre-treatment trends, or on comparing drugs or timings that vary for clinical reasons.

**Validation required**

- A multicentre prospective cohort.
- Replication in a second species.
- A pre-registered analysis plan, to avoid choosing the time window after seeing the data.

**Prior-work search (PubMed)**

1. `(babesia OR babesiosis) AND (dog OR dogs OR canine) AND (diminazene OR imidocarb OR antibabesial OR treatment) AND (cytokine* OR inflammat* OR "C-reactive protein") AND (kinetic* OR serial OR longitudinal OR "after treatment" OR post-treatment OR follow-up)`, 11 hits:
   - Atkinson 2022 (PMID 35606218, = CB098): the treatment-enhanced response in the experiment.
   - Defauw 2020 (PMID 32107174, = CB053): renal markers did not deteriorate.
   - Rossi 2014 (PMID 25104322, = CB481): CRP fell by day 7.
   - Matijatko 2007 (PMID 17116368, = CB323).
   - van Zyl 2023 (PMID 36535203): endocrine.
   - A *B. gibsoni* NAC trial (PMID 40828450).
   - No study of natural infection sampled cytokines between 0 and 24 h after treatment.
2. `(babesia OR babesiosis) AND (dog OR dogs OR canine) AND (Herxheimer OR "treatment-induced" OR "after diminazene" OR "pulmonary oedema" OR "pulmonary edema" OR ARDS OR "acute respiratory distress")`, 30 hits, screened by title, plus abstracts for 3:
   - Jacobson 1996 (PMID 8765067): haematocrit fell in all 19 dogs after diminazene or trypan blue, with the largest mean fall of 0.046 L/L at 6–12 h.
   - Joubert 2003 (PMID 15029949): no blood-pressure change after diminazene in healthy dogs.
   - The ARDS case reports (PMIDs 35957771 and 24238090) do not establish timing relative to treatment.
3. Re-check (2026-10-28): CB323, CB470 and CB490 add post-treatment samples, none reported at 6–24 h.

**Result.** Treatment-associated inflammation has been shown in 5 experimental dogs, and a fall in haematocrit after treatment in one 1996 study. Post-treatment marker change in natural infection is reported (CB323, CB470), but not at 6–24 h. The early window and its relation to new organ deterioration have not been studied in the records found. **Novelty: potential gap in the literature searched, with partial prior work.**

---

## Summary table

| Q | Axis | Verified data usable now | Main data still needed | Novelty label |
|---|---|---|---|---|
| Q1 | ERY–END–REN (haemolysis, haem, endothelium, AKI) | DS01/DS02 (5 dogs, CFH; hypothesis generation) | Natural cohort with CFH, scavengers, Ang-2, uNGAL/KIM-1 | Potential gap, partial prior work (CB412, CB435, CB341) |
| Q2 | INF–COA (thromboinflammation, death) | S-CB050 joined to S-CB517 (same CH03 dogs; cytokines, MPXI, SAA, CRP, survival) | RQ-CB145 coagulation data, linked by case number | Potential gap, partial prior work (CB438, CB504, CB517, CB370) |
| Q3 | INF, species differences | DS01, S-CB050 or S-CB517, S-CB017 | Head-to-head two-species study with one assay | Potential gap, partial prior work (CB510, CB517) |
| Q4 | ERY (marrow response, iron) | DS03, DS05 (independent sources) | Manual reticulocyte counts, iron, hepcidin, EPO, serial samples | Core finding published (CB418, CB115); extensions are a potential gap |
| Q5 | INF–PUL–REN (treatment response) | DS01 (5 dogs, descriptive only) | Dense sampling before and after treatment in natural infection | Potential gap, partial prior work (CB323, CB470) |
