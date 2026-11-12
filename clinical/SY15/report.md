# SY15 Rhabdomyolysis: run report

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY15.json`. The validator printed `OK` with no warnings. The page was not viewed in a browser, as instructed (View: `validated, not seen`).

## Definition

The working definition (muscle pain, tremors, raised CK and myoglobinuria) is **confirmed for clinical rhabdomyolysis**, but it rests on two *B. rossi* dogs (Jacobson & Lobetti 1996). The definition was **changed** to separate two levels:

- Clinical rhabdomyolysis: muscle pain or tremors, pigmenturia, high myoglobin and muscle enzymes. This is rare. Only 2 dogs are published, both *B. rossi* from South Africa.
- Biochemical muscle damage: CK above 300 U/L (Onderstepoort, *B. rossi*, 20 of 56 complicated cases) or above 600 U/L (Zagreb, *B. canis*, 7 of 11 complicated cases in each of two studies). This is common and did not affect survival.

Tremor alone is not specific, because it also occurs in cerebral babesiosis (SY07). **For the coordinator:** rhabdomyolysis is not a distinct entity with its own treatment literature in babesiosis. The page is short and says so.

## Answers to the page questions

1. **Published cases:** 2 clinical cases, *B. rossi* (1996). Biochemical muscle damage is reported in *B. rossi* (Welzl 2001) and *B. canis* (Zagreb 2010 and 2017, Germany 2025, Italy 2005). Polish authors state that no clinical case is described with *B. canis*. No report was found for *B. gibsoni* or *B. vogeli*.
2. **Signs and CK values:** muscle pain, tremors and caramel-coloured urine. The CK values of the clinical cases could not be read (abstract only). Cut-offs used: 300 U/L and 600 U/L. In German *B. canis* dogs the maximum CK was 5214 U/L.
3. **Myoglobin or haemoglobin:** red plasma means haemoglobinaemia. A marked rise in CK means muscle. The dipstick is positive for both pigments. Both pigments can be present at the same time (eClinpath; Chavez 2016).
4. **Other complications:** in Welzl 2001, muscle damage occurred mostly with other organs (18 of 20 dogs). The clinical cases had acute renal failure, or neurological signs with pulmonary oedema.
5. **Treatment and outcome:** the treatment of the 1996 cases is not in the abstract. One dog died; the outcome of the other is not stated.

## References: 21

| Evidence type | Refs | Count |
|---|---|---|
| Babesiosis cohort (level B data) | R2, R3, R4, R12, R13, R15 | 6 (R3 and R4 may overlap: Zagreb 2017, no cohort_id) |
| Babesiosis case series or case report (C) | R1, R14 | 2 |
| Babesiosis reviews (E) | R10, R11 | 2 |
| Canine, other cause of rhabdomyolysis (D) | R7, R16, R17, R18, R19, R20, R21 | 7 |
| Human rhabdomyolysis (D, see decision 1) | R6, R8 | 2 |
| Textbook or guideline sheet (E) | R5, R9 | 2 |

Read in full: 11 (R2 to R7, R9, R11, R12, R13, R15). Read as abstract only: 10. R5 (eClinpath) and R9 (WSAVA sheet) are web pages with no DOI or PMID. They were opened and read in this run and are linked by URL.

## Treatments: 7

| Treatment | Status | Level | Dose rows |
|---|---|---|---|
| Isotonic crystalloid fluid therapy | standard | D | 2 (lactated Ringer's 10 mL/kg IV bolus, then 5 mL/kg/h: Smith 2020, one dog, not babesiosis) |
| Analgesia with opioids | standard | E | none (no dose could be verified; see below) |
| Electrolyte monitoring and correction | proposed | D | none (hyperkalaemia treatment left to SY05) |
| Renal replacement therapy | proposed | D | none (referral) |
| Urine alkalinisation with sodium bicarbonate | no_benefit | D | none |
| Mannitol or loop diuretics | no_benefit | D | none |
| Fenoldopam | harmful | D | none (the tested dose of 0.1 to 1.0 µg/kg/min is given in the summary only) |

"Rest and nursing" is not a treatment row. No source was found for it, and this is listed under evidence gaps.

## Dose and threshold check

I re-read every number against its source in this run. No sub-agent was used: the page has only 2 dose rows.

- Lactated Ringer's 10 mL/kg bolus, then 5 mL/kg/h: checked against the full text of Smith & Wurlod 2020 (PMC7008280). They match. The dog was discharged on day 5.
- Fenoldopam 0.1 to 1.0 µg/kg/min IV in 10 dogs: checked against the Murray 2003 abstract. It matches.
- The thresholds were checked against their sources:
  - CK 300 U/L and creatinine 150 µmol/L: Welzl Table 1.
  - CK 600 U/L: CB004, CB006 and CB394.
  - CK 200 U/L, 107 of 236 dogs and a maximum of 5214 U/L: CB141 Table 2.
  - Sled-dog CK and potassium: Frye abstract.
  - CK 32 856 U/L: Santifort abstract.
  - CK 5 times the upper limit, and AKI in 10 to 55%: Chavez.
  - Correlation R = 0.91: Devall abstract.
- Two discrepancies in the sources are recorded in `evidence.csv`:
  - Welzl gives the CK unit as µmol/l in the text but as U/l in Table 1. The page uses U/L.
  - CB141 gives 107 dogs as 31.3%, a percentage of all 342 dogs, although only 236 dogs were tested. The page gives the count.

## What I could not find or verify

- The full text of Jacobson & Lobetti 1996 (paywall). The CK and myoglobin values and the treatment of the only two clinical cases are not known.
- An opioid dose. The English full text of the WSAVA 2022 pain guideline could not be reached (Wiley 403), so the analgesia row has the guideline's method (titrate a short-acting opioid) but no dose.
- A canine hyperkalaemia treatment dose. No source was found in one PubMed search; the page refers to SY05.
- Any study of rest, nursing or muscle relaxants in this syndrome.
- Any report in *B. gibsoni* or *B. vogeli*.

## Statements I am least sure of

- "7 of 11 in each of two Zagreb studies" (CB004 and CB006). These may be overlapping dogs from the same clinic in 2017. The page does not count them as independent.
- In Welzl 2001 the parasite is named *B. canis*. I report it as *B. rossi*, on the basis that it was the South African parasite at Onderstepoort, and the page says so.
- The fluid regimen comes from one dog with amphetamine toxicosis. It is level D and is labelled as such.

## Decisions for the coordinator or user

1. **Evidence level of human non-malarial data.** The rules give level D for human malaria or babesiosis, not for human rhabdomyolysis from other causes. I rated the human guideline and review (R6, R8) as level D, as the nearest fit, and said plainly in each summary that they are human data. Should they be level E instead?
2. **Syndrome status.** Clinical rhabdomyolysis rests on 2 cases. The coordinator may want to keep SY15 as a short page or merge it into SY11 as one organ of multiple organ dysfunction.
3. **No browser check.** The page was not viewed, as instructed.

## Files written

- `/webapp/Babesiosis.Web/public/assets/clinical/SY15.json`
- `/clinical/SY15/search-log.md`
- `/clinical/SY15/evidence.csv`
- `/clinical/SY15/references-check.csv`
- `/clinical/SY15/report.md`
- `/clinical/ledger.md` (row SY15 only)
