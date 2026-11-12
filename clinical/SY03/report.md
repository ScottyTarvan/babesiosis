# SY03 report: thrombocytopenia, coagulopathy and DIC

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY03.json` (validator: OK, no warnings). Not viewed in a browser (instruction for this run): `validated, not seen`.

## Definition

**Changed.** The working definition put thrombocytopenia and DIC on one bleeding spectrum. The literature separates them:

- Thrombocytopenia is present in almost every dog (84-100%) and seldom bleeds. In German *B. canis*, 2 of 39 dogs below 40 x10^9/L bled. None of 19 uncomplicated *B. rossi* dogs with a median count of 20 x10^9/L bled.
- Consumptive coagulopathy (long PT and aPTT, low factors, antithrombin and protein C, high D-dimer, reduced fibrinolysis, organ microthrombi) marks severe and fatal *B. rossi* disease. Its main lesion is microthrombosis, not haemorrhage.
- No babesiosis study used a validated DIC score. "DIC" was inferred from marker panels (TAT and antithrombin; or fibrin monomer, FDP and D-dimer).

## Page questions

1. **Bleeding at which counts:** rare even below 20-40 x10^9/L (CB106, CB439). Petechiae in 14% of one untyped Ukrainian series.
2. **DIC criteria used:** marker panels only (CB374, CB199, CB217, CB145, CB438). The general canine score (Wiinberg 2010) is given, labelled `general canine`.
3. **Hyper- or hypocoagulable:**
   - *B. rossi*: normocoagulable TEG, because high fibrinogen offsets the low platelet count. Initiation is slow and lysis reduced. Non-survivors have consumed factors.
   - *B. canis*: procoagulant (high TAT, low antithrombin); aPTT is often long.
   - *B. gibsoni*: aPTT long, PT normal.
   - Untyped Ukrainian dogs: low fibrinogen.
4. **Prediction:**
   - The platelet count does not predict death in *B. rossi*. PT, antithrombin and factors VII and X do.
   - In *B. canis*, platelets below 27.5 x10^9/L were associated with death (15 dogs; limited value).
5. **Recovery:**
   - *B. rossi*: the count rises within 24-48 h of treatment and the median is normal by day 6.
   - *B. canis*: normal in 21 of 23 dogs by about day 17.
   - A count that stays low was not studied. *E. canis* co-infection was found in only 2% of Eastern Cape *B. rossi* dogs, and the blood count did not predict it.

## References

29 in total, all confirmed: 22 in PubMed, 7 in Crossref only. 23 are local `CB` articles and 6 are non-babesiosis sources. 13 were read in full text and 16 as abstracts.

| Evidence kind | Refs |
|---|---|
| Trials in dogs with babesiosis (level A) | 3 (CB247, CB213, CB217; CB213 and CB217 are one Ukrainian programme) |
| Cohorts or series of 5 or more dogs with babesiosis (B) | 13 |
| Case reports (C) | 2 |
| Non-babesiosis canine evidence or guideline (D) | 6 |
| Reviews (E) | 2 (CB533, CB041) |

## Treatments (7)

| Treatment | Status | Level | Dose source |
|---|---|---|---|
| Fresh frozen plasma | standard | C | 10 mL/kg, Langhorn 2019 (not babesiosis) |
| Fresh whole blood or platelet products | proposed | C | whole blood 20 mL/kg, Ryu 2024 (not babesiosis) |
| Glucocorticoids for secondary immune thrombocytopenia | proposed | A (1 small trial) | prednisone 2 mg/kg/day for 10 days or less (CB533); prednisolone taper (CB247) |
| Dextran or plasma substitute with dipyridamole | proposed | A (1 programme) | CB213, CB217 |
| Romiplostim | proposed | C | 5-10 µg/kg SC, Ryu 2024 |
| Vincristine | proposed | D | 0.02 mg/kg IV once, Rozanski 2002 (primary ITP) |
| Heparin (UFH or LMWH) | proposed | E | no dose: the CURATIVE Domain 3 full text was not reachable |

- **Antibabesial drugs:** these are in TX00. The page links there.
- **Tranexamic acid, aspirin and clopidogrel:** no source in babesiosis was found. They are reported in `evidence_gaps`, not as treatment rows.

## Dose check

An independent sub-agent re-read every dose and threshold row (17 rows) against its source without seeing the page. It found 14 matches, 1 mismatch and 2 partial matches. All were corrected:

- **Whole blood:** the frequency was given as "once". It is now "median 2.5 transfusions", and the route is now "not stated".
- **Plasma:** only 3 of the 4 dogs got plasma, and the route is not stated.
- ***B. rossi* day-6 platelet count:** it rests on the 46 dogs still sampled, not on all 86.

Other caveats were added to the page: the romiplostim responder denominator, the non-randomised vincristine study, and the condition for prednisone.

## Least sure

- **Glucocorticoids labelled level A:** the rule gives level A to any controlled trial in babesiosis. CB247 is small (6 dogs per arm) and unblinded, and it measured IMHA, not thrombocytopenia. Platelets recovered in all arms.
- **Dextran with dipyridamole labelled level A:** the trial had untyped parasites, no stated allocation, laboratory outcomes only and regional products.
- **CB199/CB213 low fibrinogen:** non-standard assays and untyped species.
- **CB254 "pancytopenia and DIC":** the criteria are not in the abstract.

## For the coordinator or user

1. **Heparin has no dose.** The canine protocols (CURATIVE Domain 3, doi 10.1111/vec.12795) are paywalled. University-hosted copies exist but were not used (rule 12). If the coordinator has legitimate access, a dose row could be added.
2. **Level A labels.** Decide whether these two labels should stand or whether the rules should allow a downgrade for very small or surrogate-outcome trials.
3. **SY02 overlap.** CB247 is also SY02 evidence (IMHA). The glucocorticoid row here is limited to thrombocytopenia.
