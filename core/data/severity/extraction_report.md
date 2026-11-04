# Marker-severity extraction report

Built by `scripts/check_associations.py` from `data/severity/extractions/`. Quote checks: exact = found verbatim after normalisation; near = >= 80% of 4-word shingles found; partial = >= 50%; not_found = unverified. Numbers not in text = values in the statistic fields that occur nowhere in the article text.

- Articles: 10
- Severity definitions: 21
- Associations: 275 (significant: 130, not significant: 116)
- Quotes: exact 275
- Rows with numbers not in text: 0
- Rows with schema errors: 0
- Markers: 82 distinct; unmapped rows: 0

## Per article

| ID | Species | Cohort | Definitions | Rows | Sig. yes / no | Quotes exact+near / total | Number misses | Errors |
|---|---|---|---|---|---|---|---|---|
| CB006 | B. canis canis |  | 9 | 45 | 26 / 18 | 45 / 45 | 0 | 0 |
| CB017 | B. canis |  | 1 | 28 | 7 / 11 | 28 / 28 | 0 | 0 |
| CB040 | B. rossi |  | 3 | 78 | 51 / 22 | 78 / 78 | 0 | 0 |
| CB050 | B. rossi | CH03 | 1 | 5 | 2 / 2 | 5 / 5 | 0 | 0 |
| CB053 | B. rossi |  | 1 | 13 | 5 / 7 | 13 / 13 | 0 | 0 |
| CB141 | B. canis | CH12 | 1 | 17 | 15 / 2 | 17 / 17 | 0 | 0 |
| CB145 | B. rossi | CH03 | 1 | 31 | 5 / 25 | 31 / 31 | 0 | 0 |
| CB202 | B. gibsoni, B. vogeli, mixed | CH08 | 1 | 16 | 9 / 5 | 16 / 16 | 0 | 0 |
| CB238 | mixed/unspecified |  | 2 | 11 | 4 / 3 | 11 / 11 | 0 | 0 |
| CB263 | mixed/unspecified | CH18 | 1 | 31 | 6 / 21 | 31 / 31 | 0 | 0 |

## Problems to check

```
CB006: 9 severity definitions, 45 associations; quotes exact 45
CB017: 1 severity definitions, 28 associations; quotes exact 28
CB040: 3 severity definitions, 78 associations; quotes exact 78
CB050: 1 severity definitions, 5 associations; quotes exact 5
CB053: 1 severity definitions, 13 associations; quotes exact 13
CB141: 1 severity definitions, 17 associations; quotes exact 17
CB145: 1 severity definitions, 31 associations; quotes exact 31
CB202: 1 severity definitions, 16 associations; quotes exact 16
CB238: 2 severity definitions, 11 associations; quotes exact 11
CB263: 1 severity definitions, 31 associations; quotes exact 31
```

## Marker mappings to check

Rows whose marker was not already a canonical name: mapped through an alias, a pattern (least reliable), or not at all. Fix wrong ones with a manual row in `marker_map.csv`.

| As reported | Extractor's marker | Mapped to | How | Rows |
|---|---|---|---|---|
| plasminogen activity (%) | Plasminogen | Fibrinolysis (plasminogen, antiplasmin) | pattern | 1 |
| alpha2-antiplasmin activity, α2-AP (%) | Alpha2-antiplasmin | Fibrinolysis (plasminogen, antiplasmin) | pattern | 1 |

## Severity definitions

| ID | Key | Class | Label | Definition |
|---|---|---|---|---|
| CB006 | S1 | organ_dysfunction | one complication vs uncomplicated | Complicated babesiosis split into dogs with a single organ dysfunction and MODS, using Table 1 criteria (renal: creatinine >180 μmol/L; respiratory: dyspnoea/nasal discharge or radiographic pulmonary oedema; hepatic: ALT >176 U/L, AP >360 U/L and bilirubin >100 μmol/L; muscular: CPK >600 U/L; CNS: modified Glasgow coma scale <9). Uncomplicated = none of the listed complications. Pancreatitis and secondary infection were noted as additional, not main, complications. |
| CB006 | S2 | organ_dysfunction | MODS vs uncomplicated | MODS = two or more organ dysfunctions by Table 1 criteria; uncomplicated = no listed complication. Of the 5 MODS dogs, 4 died. |
| CB006 | S3 | organ_dysfunction | MODS vs one complication | MODS (two or more organ dysfunctions) vs single organ dysfunction, within complicated babesiosis, by Table 1 criteria. |
| CB006 | S4 | mortality | lethal outcome (died vs survived) | Death despite treatment; follow-up horizon not stated. All 4 deaths were dogs with MODS (mortality 10%). Analysed as Kendall tau-b correlation of each marker with outcome. |
| CB006 | S5 | anaemia_grade | anaemic vs non-anaemic | Anaemia by HCT: non-anaemic HCT >37%; anaemic HCT <=37% (mild 30–37%, moderate 18–29%, severe <18%). |
| CB006 | S6 | anaemia_grade | moderately anaemic vs mildly anaemic | Moderate anaemia HCT 18–29% vs mild anaemia HCT 30–37%. The single severely anaemic dog was not analysed. |
| CB006 | S7 | anaemia_grade | mildly anaemic vs non-anaemic | Mild anaemia HCT 30–37% vs non-anaemic HCT >37% (pairwise comparison in Table 5). |
| CB006 | S8 | anaemia_grade | moderately anaemic vs non-anaemic | Moderate anaemia HCT 18–29% vs non-anaemic HCT >37% (pairwise comparison in Table 5). |
| CB006 | S9 | anaemia_grade | haematocrit (continuous degree of anaemia) | Spearman correlation of each marker with admission HCT (%) in the 40 infected dogs; lower HCT = more severe anaemia. |
| CB017 | S1 | complicated | complicated vs uncomplicated | Infected dogs classified on clinical manifestations and laboratory data into complicated and uncomplicated babesiosis; complicated form based on WHO classification for malaria, main complications SIRS (>=2 of 4 criteria: temperature, heart rate, respiratory rate, WBC/band neutrophils) and MODS (>=2 of renal, hepatic, respiratory, muscular dysfunction). 66% of complicated cases were MODS positive and all were SIRS positive. Day 7 comparison: 17 complicated (one died) vs 13 uncomplicated. |
| CB040 | S1 | mortality | died vs survived | Short-term outcome: survival to discharge vs death or euthanasia due to poor prognosis. 34 of 320 dogs died; all deaths within 24 h of admission. |
| CB040 | S2 | other | collapsed vs able to stand (non-collapsed) | Collapse at presentation, defined as unable to stand unaided, as a marker of clinical severity at admission. |
| CB040 | S3 | anaemia_grade | degree of anaemia (haematocrit) | Severity of anaemia measured by admission haematocrit, used as a continuous measure for correlations and the ISA comparison. The authors also grade anaemia as severe (Hct <0.15 L/L), moderate (0.15-0.24), mild (0.25-0.36). |
| CB050 | S1 | mortality | non-survivors vs survivors | Short-term outcome: survival until discharge from hospital vs death or euthanasia due to poor prognosis during hospitalisation. Dogs euthanised for other reasons were excluded (cohort 1 criterion). Both cohorts pooled. |
| CB053 | S1 | complicated | complicated vs uncomplicated babesiosis | Complicated when at least one complication was diagnosed at presentation or during hospitalisation: collapse (unable to walk unaided), hypotension (MAP < 80 mmHg), severe anaemia (HCT < 0.15), haemoconcentration (HCT > 0.37 with intravascular haemolysis), secondary IMHA (positive in-saline agglutination), AKI (IRIS grading, incl. grade I = sCr rise >= 26.4 µmol/L within 48 h), hypoglycaemia (< 3.3 mmol/L), jaundice (total bilirubin > 50 µmol/L), cerebral babesiosis, ARDS. Based on Jacobson and Clark 1994, Jacobson 2006, WHO 2014. |
| CB141 | S1 | severity_grade | hematological score (HES) | Haematological score: sum of the grades of anaemia (HCT mild 0.31–0.43, moderate 0.20–0.30, marked < 0.20 l/l), thrombocytopenia (91–149, 40–90, < 40 G/l) and leukopenia (4.0–5.9, 2.0–3.9, < 2.0 G/l) scored 0/+1/+2/+3, plus leukocytosis > 12.0 G/l (+1) and pancytopenia (+3); range 0–11. Higher = more severe haematological abnormality. Used as a continuous severity measure (Spearman) and compared between groups (Mann-Whitney, Kruskal-Wallis). |
| CB145 | S1 | mortality | non-survivors vs survivors | Short-term outcome: survival until hospital discharge vs death or euthanasia due to poor prognosis. Dogs euthanised for other reasons were excluded. Median time to death 24 (24-48) h. |
| CB202 | S1 | mortality | non-survivors vs survivors | Infected dogs followed up during the treatment period for survival; died vs survived. No fixed follow-up horizon stated. |
| CB238 | S1 | mortality | dead vs survived (mortalities vs survival) | Death vs survival among anaemic dogs with babesiosis; horizon not stated. Parameters measured at presentation. |
| CB238 | S2 | anaemia_grade | anemic vs non-anemic | Anaemia (PCV <36%; mild 30-36%, moderate 20-29%, severe <20%) vs no anaemia among 103 dogs with babesiosis. |
| CB263 | S1 | mortality | non survivors vs survivors | Dogs split into survivors and non-survivors based on the treatment response; follow-up horizon not stated. All dogs met SIRS, severe sepsis or septic shock criteria; dogs with pre-existing cardiac disease, diabetes, ARDS, creatinine above 7 mg/dL or chronic renal disease were excluded. |

## Evidence preview

Articles per marker and outcome class: significant with higher values in (or positively associated with) the worse outcome, significant lower, and not significant. Articles, not rows; linked cohorts are not merged here.

| Class | Marker | Outcome | Higher | Lower | Not significant |
|---|---|---|---|---|---|
| acid-base and perfusion | Acid-base (pH, bicarbonate, base excess, anion gap) | mortality |  | CB040 | CB040 |
| acid-base and perfusion | Acid-base (pH, bicarbonate, base excess, anion gap) | other | CB040 | CB040 |  |
| acid-base and perfusion | Blood gases and oxygenation | mortality |  |  | CB040 |
| acid-base and perfusion | Blood gases and oxygenation | other |  | CB040 | CB040 |
| acid-base and perfusion | Lactate | mortality | CB040, CB263 |  |  |
| acid-base and perfusion | Lactate | other | CB040 |  |  |
| acute phase protein | C-reactive protein | mortality | CB202 |  | CB145 |
| acute phase protein | C-reactive protein | severity_grade | CB141 |  |  |
| acute phase protein | Hepcidin | mortality | CB202 |  |  |
| acute phase protein | Serum amyloid A | mortality |  |  | CB145, CB202 |
| biochemistry | ALP | mortality |  |  | CB040, CB263 |
| biochemistry | ALP | severity_grade | CB141 |  |  |
| biochemistry | ALT | mortality |  |  | CB040, CB263 |
| biochemistry | ALT | severity_grade | CB141 |  |  |
| biochemistry | AST | severity_grade | CB141 |  |  |
| biochemistry | Albumin | mortality |  |  |  |
| biochemistry | Albumin | other |  | CB040 |  |
| biochemistry | Bilirubin | anaemia_grade |  |  |  |
| biochemistry | Bilirubin | mortality | CB040 |  | CB263 |
| biochemistry | Bilirubin | other | CB040 |  |  |
| biochemistry | Bilirubin | severity_grade | CB141 |  |  |
| biochemistry | Copper | mortality |  |  | CB202 |
| biochemistry | Creatine kinase | severity_grade | CB141 |  |  |
| biochemistry | Creatinine | complicated |  |  | CB053 |
| biochemistry | Creatinine | mortality | CB040 |  |  |
| biochemistry | Creatinine | other | CB040 |  |  |
| biochemistry | GGT | severity_grade |  | CB141 |  |
| biochemistry | Globulins | mortality |  |  | CB040 |
| biochemistry | Globulins | other |  |  | CB040 |
| biochemistry | Globulins | severity_grade |  | CB141 |  |
| biochemistry | Glucose | mortality |  | CB040 | CB040 |
| biochemistry | Glucose | other |  |  | CB040 |
| biochemistry | Iron and iron indices | mortality | CB202 | CB202 |  |
| biochemistry | Iron and iron indices | severity_grade |  | CB141 |  |
| biochemistry | Plasma NGAL | complicated |  |  | CB053 |
| biochemistry | SDMA | complicated | CB053 |  |  |
| biochemistry | Selenium | mortality |  |  | CB202 |
| biochemistry | Total protein | mortality |  |  | CB263 |
| biochemistry | Total protein | severity_grade |  | CB141 |  |
| biochemistry | Urea | complicated | CB053 |  |  |
| biochemistry | Urea | mortality | CB040 |  | CB040 |
| biochemistry | Urea | other | CB040 |  |  |
| biochemistry | Zinc | mortality |  | CB202 |  |
| cardiac | Echocardiographic findings | mortality | CB263 | CB263 | CB263 |
| clinical history | Travel / import history | severity_grade | CB141 |  | CB141 |
| clinical score | Clinical severity score | mortality |  |  | CB040 |
| clinical score | Clinical severity score | other | CB040 |  |  |
| clinical sign | Body temperature | mortality |  | CB040 | CB238 |
| clinical sign | Body temperature | other |  | CB040 |  |
| clinical sign | Heart rate | mortality | CB238 |  |  |
| clinical sign | Mentation / neurological signs | mortality | CB040 |  |  |
| coagulation | Antithrombin | mortality |  | CB145 |  |
| coagulation | Coagulation factor activity | mortality |  | CB145 | CB145 |
| coagulation | D-dimer | mortality |  |  | CB145 |
| coagulation | Fibrinogen | mortality |  |  | CB145 |
| coagulation | Fibrinolysis (plasminogen, antiplasmin) | mortality |  |  | CB145 |
| coagulation | Prothrombin time | mortality | CB145, CB263 |  |  |
| coagulation | Viscoelastic testing (TEG/ROTEM) | mortality |  |  | CB145 |
| coagulation | aPTT | mortality | CB263 |  | CB145 |
| cytokine | Cytokine linear combination | complicated |  |  |  |
| cytokine | GM-CSF | complicated | CB017 |  | CB017 |
| cytokine | IL-10 | complicated |  |  | CB017 |
| cytokine | IL-18 | complicated |  |  | CB017 |
| cytokine | IL-2 | complicated | CB017 |  | CB017 |
| cytokine | IL-8 (CXCL8) | complicated |  |  | CB017 |
| cytokine | KC-like (CXCL1) | complicated | CB017 |  |  |
| cytokine | MCP-1 (CCL2) | complicated | CB017 |  |  |
| cytokine | Other cytokines and chemokines | complicated | CB017 |  | CB017 |
| electrolyte | Chloride | mortality |  | CB040 |  |
| electrolyte | Ionised calcium | mortality |  | CB040 |  |
| electrolyte | Ionised calcium | other |  | CB040 |  |
| electrolyte | Phosphate | mortality | CB040 |  |  |
| electrolyte | Phosphate | other | CB040 |  |  |
| electrolyte | Potassium | mortality |  |  | CB040 |
| electrolyte | Potassium | other |  |  | CB040 |
| electrolyte | Sodium | mortality |  |  | CB040 |
| electrolyte | Sodium | other |  |  | CB040 |
| endocrine | Cortisol | mortality | CB040 |  |  |
| endocrine | Cortisol | other | CB040 |  |  |
| endocrine | Thyroid hormones | mortality |  | CB040 |  |
| endocrine | Thyroid hormones | other |  | CB040 |  |
| haematology | Autoagglutination | anaemia_grade |  |  | CB040 |
| haematology | Autoagglutination | mortality |  |  | CB040 |
| haematology | Band neutrophils | mortality | CB040, CB050 |  |  |
| haematology | Haematocrit/PCV | complicated |  |  |  |
| haematology | Haematocrit/PCV | mortality | CB040 | CB145, CB238 | CB040, CB263 |
| haematology | Haematocrit/PCV | other |  | CB040 |  |
| haematology | Haemoglobin | mortality |  | CB238 | CB263 |
| haematology | Mean platelet volume and platelet indices | mortality |  |  | CB145 |
| haematology | Myeloperoxidase / MPXI | mortality |  |  | CB050 |
| haematology | Neutrophil count | mortality | CB050 |  |  |
| haematology | Platelet count | mortality |  |  | CB145 |
| haematology | Red blood cell count | mortality |  | CB238 | CB263 |
| haematology | Red cell indices | mortality | CB202 |  |  |
| haematology | Reticulocytes | anaemia_grade | CB040 |  |  |
| haematology | White blood cell count | anaemia_grade | CB040 |  |  |
| haematology | White blood cell count | mortality | CB040 |  |  |
| haematology | White blood cell count | other | CB040 |  |  |
| immunology | Antibody titre / serostatus | severity_grade |  | CB141 |  |
| oxidative stress | Catalase | anaemia_grade |  | CB006 | CB006 |
| oxidative stress | Catalase | mortality |  | CB006, CB202 |  |
| oxidative stress | Catalase | organ_dysfunction |  | CB006 | CB006 |
| oxidative stress | Glutathione / glutathione peroxidase | anaemia_grade |  | CB006 | CB006 |
| oxidative stress | Glutathione / glutathione peroxidase | mortality |  | CB006 | CB202 |
| oxidative stress | Glutathione / glutathione peroxidase | organ_dysfunction |  | CB006 | CB006 |
| oxidative stress | Malondialdehyde / TBARS | anaemia_grade | CB006 |  | CB006 |
| oxidative stress | Malondialdehyde / TBARS | mortality | CB006, CB202 |  |  |
| oxidative stress | Malondialdehyde / TBARS | organ_dysfunction | CB006 |  | CB006 |
| oxidative stress | Superoxide dismutase | anaemia_grade |  | CB006 |  |
| oxidative stress | Superoxide dismutase | mortality |  | CB006 | CB202 |
| oxidative stress | Superoxide dismutase | organ_dysfunction |  | CB006 | CB006 |
| oxidative stress | Total antioxidant capacity | anaemia_grade |  |  | CB006 |
| oxidative stress | Total antioxidant capacity | mortality | CB006 |  |  |
| oxidative stress | Total antioxidant capacity | organ_dysfunction |  |  | CB006 |
| parasitology | Parasite DNA load (qPCR) | severity_grade | CB141 |  |  |
| parasitology | Parasite species or genotype | mortality |  |  |  |
| signalment | Age | complicated |  |  |  |
| signalment | Age | mortality |  |  | CB040, CB050, CB145 |
| signalment | Body weight / body condition | mortality |  |  | CB040, CB145 |
| signalment | Breed | mortality |  |  | CB238 |
| signalment | Sex / neuter status | complicated |  |  |  |
| signalment | Sex / neuter status | mortality |  |  | CB238 |
| urine | Urinary kidney injury biomarkers | complicated | CB053 |  | CB053 |
| urine | Urine osmolality | complicated |  |  | CB053 |
| urine | Urine protein:creatinine ratio | complicated | CB053 |  |  |
| urine | Urine specific gravity | complicated |  |  | CB053 |
