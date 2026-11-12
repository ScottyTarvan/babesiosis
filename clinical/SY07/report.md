# SY07 report: cerebral babesiosis

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY07.json`. Validator: `OK`, no warnings. View: not seen. Starting the `babesiosis-web-mock` preview was declined, so the page was not opened in the browser.

## Definition

I confirmed the working definition and narrowed it. The Onderstepoort *B. rossi* cohort (Leisewitz 2019, R1) defines the syndrome as acute cerebral signs (stupor, semi-coma, coma, seizures or marked behaviour change) with a positive smear and a **normal or raised blood glucose**. In pathology the hallmark is microvascular brain injury with haemorrhage (R1, R2). The Indian *B. gibsoni* cohort (CH16, R4/R11) uses a different, unvalidated definition: signs plus parasites in red cells of cerebrospinal fluid. Isolated cerebellar ataxia is reported separately (R5) and is not the same entity.

## References: 28

All 28 were confirmed in PubMed, Crossref or Europe PMC (`references-check.csv`). One reference was removed: CB279 (Sivajothi 2025). Its DOI returns 404, and Crossref and Europe PMC do not have it.

| Level of the source | Count | References |
|---|---|---|
| Trials and consensus statements in dogs, other causes (level D for this page) | 7 | R7, R8, R22, R24, R26, R27, R19 |
| Cohorts or series of 5 or more dogs with babesiosis (B) | 11 (10 independent) | R1, R2, R3, R4 and R11 (one cohort, CH16), R10, R13, R14, R15, R16, R21 |
| Case reports (C) | 5 | R5, R9, R17, R18, and R25 (R25 is not babesiosis) |
| Reviews, surveys, pharmacokinetics, imaging (E or context) | 5 | R6, R12, R20, R23, R28 |

## Treatments: 8

| Treatment | Status | Level | Note |
|---|---|---|---|
| IV dextrose for hypoglycaemia | standard | D | Dose from one non-babesiosis case report (R25) |
| Benzodiazepines (midazolam, diazepam) | standard | D | ACVIM consensus, two trials in epilepsy |
| Phenobarbital | standard | D | IVETF doses |
| Levetiracetam | standard | D | One RCT (19 dogs); reduce the dose in kidney injury |
| Mannitol | proposed | C | Used in one fatal *B. canis* dog. Dose from dogs with intracranial hypertension of other causes |
| Hypertonic saline | proposed | D | No babesiosis use found |
| Glucocorticoids | proposed | C | Two case-level reports and a 1993 survey. **No dose given**: no source read gave one for this use |
| Oxygen and nursing | proposed | E | No study |

No treatment aimed at the brain lesion has been tested in any *Babesia* species. Antibabesial drugs are linked to TX00. Only the diminazene points specific to this syndrome are on this page: the toxicity mimic, and the advice not to repeat diminazene within 21 days after 4.2 mg/kg.

## Doses

There are 14 dose rows. I re-read every one in the PMC full text: R22, R24, R26, R8 and R25. The exception is levetiracetam 30 or 60 mg/kg IV, which was read in the R27 abstract only. A subagent first collected the doses. I then checked each number, unit, route and frequency against the source text myself; the quotes are in `evidence.csv`.

## What I could not find or read

- No *B. rossi* study of clinical signs, imaging or CSF in living dogs.
- No dextrose dose from any babesiosis source.
- No glucocorticoid dose for this use.
- These sources could not be read:
  - Lewis 2022, a UP MMedVet dissertation on *B. rossi* cerebral histopathology. It has no abstract, and the 33 MB PDF was not downloaded.
  - Naudé 1970 (experimental diamidine poisoning), van Heerden 1981 and the 1947 to 1978 reports. None has an abstract online.
  - Schoeman 2009 (OJVR): the PDF could not be parsed.
  - Welzl 2001: abstract only.
- Several key South African papers were read as abstract only: Keller 2004, Jacobson 2006 and Welzl 2001.

## The statements I am least sure of

- R2 (Leisewitz 2014, a conference abstract): the extracted text lost the italic species name. The authors are from Onderstepoort, but the page does not say *B. rossi* for these 50 brains.
- R5 (Jacobson 1994): the abstract says *B. canis*. That was the name for the South African parasite at the time, but I did not relabel it.
- The *B. gibsoni* frequency (8.1%) comes from dogs selected for signs. It is not a prevalence.
- The differentials "hepatic or uraemic encephalopathy" are a working point. No study compared them with cerebral cases.

## Decisions for the user or coordinator

- Do you want the Lewis 2022 dissertation read? It is open access, but reading it needs a 33 MB download, which the rules forbid.
- The dextrose dose rests on one case report. The SY16 page may have a better source; the two pages should agree.
- Rabies: the page says to consider it, from one Croatian case report. A South African source on rabies risk in dogs would strengthen this point.
