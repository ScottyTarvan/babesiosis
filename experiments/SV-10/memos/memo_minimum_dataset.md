# Memo 3. A prospective minimum dataset for canine babesiosis severity

SV-10, design memo, draft 2026-11-12. Not sent to anyone. Sample sizes come from `scripts/power.py` (`out/power.csv`, memo `minimum_dataset`).

## 1. Why a new dataset

The finished packages ran into the same walls. Each wall is a variable that no public file records, or records in only one file:

| Package | What it could not answer | The item that would have answered it |
|---|---|---|
| SV-02a | Load against outcome at dog level: no species x outcome cell of published contrasts reaches 3 independent units; no *B. rossi* unit reports load against a clinical outcome | Quantified load (smear and qPCR) and outcome for each dog |
| SV-02b | Tolerance (damage per parasite) in natural infection: only 5 experimental Beagles | Load, damage markers and antibody status in the same dog before treatment |
| SV-01 | Stage of disease: the pseudo-stage failed validation; natural dogs lie past the 5-dog Beagle course | Days sick, and a second sample at a fixed time after the first |
| SV-03 | 0 of 423 marker x outcome x species cells reach 3 independent units; 78 severity definitions in 42 units; the marker is in its own definition in 38 of 504 tested rows. Every replicated *B. rossi* signal is from one hospital | One outcome set stored as components; a *B. rossi* site outside Onderstepoort |
| SV-04 | IL-8 by severity: the two dog-level files differ in sampling time (before treatment vs 6 to 8 h after imidocarb) and in definition | Sample before the first antibabesial dose, with the times recorded |
| SV-05 | Age against death: with 15 deaths only OR of about 3.7 or more is detectable; neuter status not recorded in S-CB050 | Enough deaths, and neuter status with age at neutering |
| SV-07 | Dogs re-used across files under new numbers (DS03 natural cohorts are S-CB050 dogs) | One permanent dog ID and a register of every sub-study that uses the dog |

## 2. Design

A prospective, multi-centre cohort of client-owned dogs with acute babesiosis confirmed by PCR, enrolled at presentation and followed to day 28.

- **Sites.** At least three. One may be Onderstepoort, but at least two *B. rossi* sites must be outside it (SV-03). A *B. canis* site in Europe can use the same protocol; species stays a site-level variable and is never compared across sites as a species effect (rule 6).
- **Eligibility.** Smear or PCR positive, species confirmed by PCR, no antibabesial drug in the previous 28 days, owner consent. Co-infections (*Ehrlichia canis*, *Hepatozoon*) tested by PCR and kept, not excluded.
- **Consecutive enrolment.** All eligible dogs, mild ones included. A referral-only cohort over-samples severe cases; record whether the dog was referred.
- **Timing.** Sample 1 before the first antibabesial dose. Sample 2 at 24 h (± 2 h) after it. Sample 3 at day 3 if still hospitalised. Day 28 follow-up by visit or telephone.

## 3. The minimum dataset

### 3.1 Outcome set (built from the SV-03 definition map)

Record every component as a measured value or a yes/no with its time. Do not record only a composite. This lets any published definition be rebuilt, and lets a marker be removed from the definition when it is the marker under study (the SV-03 circularity problem).

| Component | SV-03 units using it | What to record |
|---|---|---|
| Death | 20 | Date and time; **spontaneous death and euthanasia as separate fields**, with the reason for euthanasia (poor prognosis, cost, other). The Onderstepoort files merge them; the new file must not |
| Renal | 14 | Creatinine and urea at each sample; urine output; anuria or oliguria |
| Anaemia grade | 13 | Haematocrit at each sample; transfusion (yes/no, volume, time) |
| Hepatic or icterus | 11 | Total bilirubin; icterus score |
| Cerebral | 7 | Modified Glasgow coma scale |
| Collapse | 6 | Collapse at presentation (yes/no) |
| Pulmonary | 6 | Respiratory rate; SpO2 or PaO2; thoracic imaging if done |
| Hypoglycaemia | 4 | Glucose at each sample |
| Rhabdomyolysis, MODS, SIRS | 4, 4, 3 | Creatine kinase; temperature, heart rate, respiratory rate, WBC (SIRS criteria) |
| Haemoconcentration | 3 | Haematocrit with total protein |
| Hyperlactataemia, shock | 1, 2 | Lactate; systolic blood pressure |

**Primary outcome (pre-registered):** death or euthanasia for poor prognosis by day 7. **Secondary:** the count of organ complications on fixed thresholds (written into the protocol before enrolment), and death by day 28. Treatment intensity (transfusion, days in hospital) is recorded but is not an outcome, because cost and owner choice drive it.

### 3.2 Exposures and covariates

| Item | How | Why |
|---|---|---|
| Parasite load, capillary | Ear-tip smear; parasitised red cells per 1,000 counted by one trained reader per site; 10% double-read blind | SV-02a: no dog-level load and outcome in *B. rossi* |
| Parasite load, qPCR | EDTA blood, species-specific qPCR with a standard curve, copies per µL, one central laboratory | Smear load is coarse at low parasitaemia and differs between capillary and venous blood |
| Days sick | Owner-reported date of the first sign (lethargy, anorexia, red urine), with the owner's certainty (sure / within 1 day / unsure); known tick exposure date | SV-01: no time axis in natural cases. Illness duration exists only in DS05, which has no outcome |
| Antibody status | IFAT titre at sample 1 and at day 14 to 28 | CB141: antibody correlated with less severe disease (rho -0.65) in the cohort where load did (rho 0.35); the strongest lead for a tolerance modifier |
| Signalment | Breed (FCI name or "mixed"), date of birth, sex, **neuter status and age at neutering**, weight, body condition score | SV-05 could not test neuter status; CB125 reports RR 0.72 for gonadectomy ([10.1016/j.prevetmed.2024.106293](https://doi.org/10.1016/j.prevetmed.2024.106293)) |
| History | Earlier babesiosis episodes, tick prophylaxis, vaccination, drugs in the previous 14 days | Earlier exposure changes immunity |
| Treatment | Drug, dose and time of each antibabesial dose; fluids; transfusion | Sample timing relative to treatment (SV-04) |

### 3.3 Samples and storage

| Sample | Volume | Use |
|---|---|---|
| EDTA whole blood | 2 mL; CBC, smear, then 0.5 mL frozen at -80 °C | qPCR; parasite genotyping and genome sequencing (memo 1) |
| Buffy coat or EDTA pellet | from the same tube | Host DNA for DEA 1, haptoglobin, DLA and SNP array (memo 2) |
| Citrate plasma | 8 aliquots of 0.25 mL, double-spun, at -80 °C within 2 h | Coagulation, VWF, ADAMTS13, fibrinolysis |
| Serum and heparin plasma | 8 aliquots each, at -80 °C within 2 h | Cytokines (MCP-1, IL-8: SV-04), cortisol and thyroid hormones (SV-03), haptoglobin, haemopexin, cell-free haemoglobin, hepcidin, ferritin, angiopoietin-2, syndecan-1, cell-free DNA and nucleosomes |
| RNA tube (optional) | 2.5 mL at sample 1 | Host transcriptome against the Beagle signatures (SV-08) |

Freeze-thaw cycles and time to freezer are logged per aliquot. Haemolysed samples are flagged, not discarded, because haemolysis is part of the disease.

**Stored-plasma panel.** SV-06a (human-to-dog mechanism transfer) was still running when this memo was written, so its ranked list could not be used. The panel above covers its seven mechanism families (haemolysis and haem scavenging; endothelium and glycocalyx; neutrophils and NETs; VWF and thromboinflammation; iron and hepcidin; endocrine and metabolic; immune regulation). The aliquot count (8 per matrix) leaves room for the top-ranked assays when SV-06a reports. This is an open question for the coordinator.

### 3.4 Identity and linkage

- One permanent study ID per dog, never re-used or re-numbered, and one per episode for re-infections.
- A register of every sub-study that uses a dog's data or samples. SV-07 found that DS03's natural cohorts are S-CB050 dogs under new numbers; this must not happen again.
- Release a de-identified dog-level file with a data dictionary at publication.

## 4. Sample size

Normal approximations, two-sided alpha 0.05, power 0.8, death 11% (S-CB050: 15 of 140; died includes euthanasia for poor prognosis). Formula check: the cohort formula gives a detectable OR of 3.66 for the S-CB050 age contrast, which matches SV-05's "about 3.7".

SAMPLE_SIZE_TABLE

**Recommendation.** Enrol **610 *B. rossi* dogs** (about 67 deaths) over at least three sites, with at least 200 outside Onderstepoort. This detects an OR of 1.5 per SD for a continuous exposure such as log load, an OR of about 2 for a binary host factor such as age (559 needed), and replicates an Onderstepoort marker difference of 0.5 SD at the non-Onderstepoort sites only if they reach about 340 dogs together; with 200 dogs they can replicate only about 0.65 SD. A load x antibody interaction of the same size as the main effect needs about four times the main-effect n, so the tolerance question is a secondary, hypothesis-generating analysis even at 610. S-CB050 cohort 1 enrolled 97 dogs in 18 months at one hospital, so 610 dogs is about three years at three sites of that size.

The same cohort supplies the nested case-control sets of memo 1 (parasite genotype) and memo 2 (host genetics): with a severe outcome set of about 30%, 610 dogs give about 183 severe and 427 mild dogs. Memo 1's primary BrEMA1 contrast needs about 229 enrolled dogs and its death contrast about 545, so both fit; a within-breed host GWAS does not (memo 2) and needs a breed-focused extension.

## 5. What this design cannot do

- It cannot estimate treatment effects: treatment is not randomised.
- It does not support prediction; the analyses are associations with effect sizes and intervals, pre-registered, with no risk score.
- It does not compare species, unless one site enrols two species under the same protocol.
- Days sick is owner-reported and will be noisy; it is a covariate, not a stage.

## 6. Open questions

1. Which mechanisms to assay first from stored plasma: waits for SV-06a's ranked list.
2. Whether the severe outcome set is about 30% of enrolled dogs: to be checked in the first 100 dogs; the sample sizes of memos 1 and 2 scale with it.
3. Whether the composite thresholds should follow one published definition (for example the Onderstepoort complication criteria) or a new consensus; a user decision before enrolment.
