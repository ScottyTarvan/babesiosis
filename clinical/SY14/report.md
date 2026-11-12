# SY14 report: haemoconcentration ("red biliary")

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY14.json` (validator `OK`, no warnings). Not viewed in a browser (instruction): `validated, not seen`. The page agent ran as a subagent and could not write this file; the coordinator saved its report text here unchanged.

## Definition
The working definition is confirmed in substance, with three changes:
- **No single threshold.** Three haematocrit cut-offs are used, each together with intravascular haemolysis: above 0.37 L/L (Defauw 2020, R2), above 0.47 L/L (Köster 2015 review, R1) and above 0.55 L/L (Leisewitz 2019, R3; also an experimental end point, R14). Only the 0.55 L/L group was linked to outcome, and that group had 4 dogs.
- **A "normal" haematocrit that is too high for the degree of haemolysis also counts** (R1).
- **Lung oedema.** The sources link the syndrome mainly to acute kidney injury and cerebral signs. A link to lung oedema rests on review statements only.

It is a rare *B. rossi* complication: 4 of 320 dogs (1.3%) and 3 of 35 dogs in recent Onderstepoort cohorts. Mortality was 3 of 4 dogs above 0.55 L/L (odds ratio 32.7). Referral data give more than 30%, and a practitioner survey gives usually more than 80%. Mechanism: the authors propose plasma leak through damaged vessel walls; the 320-dog cohort found it was not explained by dehydration.

## References: 20
- Level B (cohort or series in babesiosis): R2, R3, R10 (a survey of practices), R12, R13, R15, R18.
- Babesiosis trial on a different question, used for diagnosis only: R19.
- Level D: R8 and R9 (human malaria fluid studies), R20 (hydroxyethyl starch in ICU dogs).
- Level E (reviews, textbook): R1, R4, R5, R6, R7, R11, R16, R17.
- Experimental model: R14.
- Read in full: 12. Abstract only: R4, R6, R8, R9, R12, R13, R19, R20.

## Treatments: 4
| Treatment | Status | Level | Studies |
|---|---|---|---|
| Isotonic crystalloid in small titrated boluses | proposed | E | 0 |
| Hypertonic saline 7% | proposed | E | 0 |
| Large-volume fluid loading | harmful | D | 2 (human malaria) |
| Hydroxyethyl starch | harmful | D | 1 (ICU dogs) |

The drugs against the parasite are linked to TX00.

## Dose check
All dose rows come from R7, the emergency care chapter of Kirk & Bistner's handbook (2012), read in full:
- crystalloid: start with one quarter of a 90 mL/kg shock volume, then reassess;
- 7% sodium chloride: 4 mL/kg IV bolus;
- hydroxyethyl starch: 5 to 10 mL/kg over 10 to 15 minutes.

I re-read all three after writing the page; they match. I also re-read every threshold and odds ratio against its source. Two text fixes followed:
- The haematocrit fall after treatment (R19) is now given as a mean maximum fall of 0.046 L/L.
- Sodium was removed from the hypertonic saline monitoring line, because the source does not mention it.

No independent sub-agent checked the doses.

## Not found or not verified
- No fluid rate, end point or fluid type for these dogs in any source.
- No evidence on plasma, red cell transfusion or furosemide for this syndrome.
- No measurement of total protein or albumin in these dogs.
- No primary report in *B. canis*, *B. gibsoni* or *B. vogeli*.
- Jacobson 2006, Jacobson & Swan 1995 and Reyers 1998 were read from the abstract only.
- The 2024 AAHA fluid guideline was blocked (HTTP 403) and is not used. Its 15 to 20 mL/kg bolus appeared only in a search-engine snippet.

## Statements I am least sure of
- R7 recommends hydroxyethyl starch, but the page marks it harmful because of R20. The dose row is kept with a note.
- R7 prints the hypertonic saline concentration as 0.7% in one passage; 7% is taken from another passage of the same chapter.
- South African papers from before about 2006 call the parasite *B. canis*; the page assumes it was *B. rossi* from the location.
- R10 is a survey of practices, but its type is "case series" because the format has no survey value.

## Decisions for the coordinator or user
1. No `standard` treatment: accept, or mark crystalloid fluids standard?
2. CB371 and CB380 are the same paper (same DOI) in `core/`.
3. Add the AAHA 2024 guideline once someone can read its full text.
