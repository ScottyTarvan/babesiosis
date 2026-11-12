# SY08 report: acute lung injury, ARDS and pulmonary oedema

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY08.json`. The validator prints `OK`, with 3 warnings that are explained below. The page was **not seen**, because starting the preview server was declined.

## Definition

The working definition is confirmed, with three corrections:

1. Frothy or blood-tinged airway fluid is a late, often terminal sign. It is not present in every case (CB111, CB040).
2. Hypoxaemia is not universal. Most fast-breathing dogs with severe *B. rossi* have low PaCO2 without hypoxaemia (Leisewitz 2001). Only 18 of 98 dogs had a PaO2 below 60 mmHg at admission (CB040).
3. The 2025 ARDSVet consensus replaces VetALI and VetARDS and drops the term "acute lung injury". The page uses its criteria. The babesiosis papers used a PaO2 below 60 mmHg, or the older criteria.

The syndrome is a real entity in the literature. It is best documented as a necropsy lesion in fatal *B. rossi* (CB111, CB040).

## References: 25, all verified

All were checked in PubMed, and 2 also in Crossref. Title, first author and year match for each.

| Level | References | Notes |
|---|---|---|
| A | 0 | |
| B (babesiosis series of 5 or more dogs, with an outcome) | 10 | CB040, CB111, CB356, CB080, Leisewitz 2001, Leisewitz 1996, Welzl 2001, Máthé 2006, Möhr 2000, CB098 (experimental) |
| C (babesiosis case reports) | 3 | CB102, CB447, CB079 |
| D (general canine) | 8 | ARDSVet 2025, Frischer 2022, Jagodich 2020, Bruchim 2014, Boiron 2019, Balakrishnan 2017, Cavanagh 2016, Whitney & Keir 2023 (review) |
| E (review or survey) | 4 | Köster 2015, Jacobson 2006, Jacobson & Swan 1995, Collett 2000 |

Full text was read for 9 references; the other 16 are abstract only.

## Treatments: 9

| Treatment | Status | Level | Doses on page |
|---|---|---|---|
| Oxygen supplementation | standard | C | Flows and FiO2 by method, from a review table (R18) |
| Red cell or whole blood transfusion for severe anaemia | standard | B | None; doses are on SY01 |
| Conservative fluids | proposed | D | None, because no source states a rate |
| High-flow nasal oxygen | proposed | D | More than 1 L/kg/min (ARDSVet), 1 to 2 L/kg/min (review) |
| Mechanical ventilation, lung-protective settings | proposed | C | Tidal volume about 9.6 mL/kg, PEEP 5 to 24 cmH2O (CB102) |
| Sedation infusions during ventilation | proposed | C | Fentanyl, midazolam, dexmedetomidine, propofol, ketamine (CB102) |
| Neuromuscular blockade (atracurium) | proposed | C | 0.3 mg/kg IV, then 6 to 9 µg/kg/min (CB102) |
| Furosemide | proposed | C | None, because no source gives a dose for this syndrome. SY09 has the cardiogenic doses |
| Glucocorticoids (dexamethasone) | proposed | C | 0.1 mg/kg IV once (CB102) |

### Dose check

Each dose was read a second time against its source. An independent sub-agent also checked all 13 dose and threshold groups and confirmed every one, with one exception. It reported that the 14 mL/kg transfusion in CB102 was missing. I re-checked: the dose is stated at line 48 of CB102's text, so the total of about 42 mL/kg stands. That total is the sum of three stated doses; the source does not state it. The "about 9.6 mL/kg" tidal volume is stated in the CB102 discussion.

### Validator warnings

There are 3 warnings, all about doses with no per-kg unit:

- Mask and flow-by oxygen are given in L/min because the source states them that way.
- PEEP is a pressure, so it has no per-kg form.

## What could not be found or read

- **No evidence for or against:** colloids, plasma (for this syndrome), bronchodilators, or furosemide for permeability oedema in babesiosis.
- **No sedation dose for the awake, distressed dog.** The one review that gives one (Can Vet J 2024) could not be read, so no dose is on the page.
- **Wilkins 2007 VetALI/VetARDS:** blocked by the publisher (403). It was replaced by ARDSVet 2025.
- **TRACS transfusion-reaction consensus:** only the abstracts could be read. It is not cited, so the TRALI and TACO definitions are not on the page.
- **2024 AAHA fluid guidelines:** blocked (403) and not cited.
- **No ARDSVet-defined incidence study** exists for any *Babesia* species.

## Statements I am least sure of

- **Leisewitz 1996.** The species is named *B. canis* in the source. The page calls it "described as *B. canis*" and does not relabel it *B. rossi*.
- **Level B for transfusion.** This rests on 6 dogs and a blood-gas outcome, from the abstract only.
- **Möhr 2000 and Collett 2000.** These are treated as South African babesiosis without a named species.
- **Hypoxaemia at admission is "often survived" (CB040).** This comes from 18 dogs, and the authors say the numbers are too small for statistics.
- **The SpO2:FiO2 thresholds.** They are general canine and partly taken from human data, not validated in anaemic dogs. The page says so.

## Decisions for the user or coordinator

1. **Fluid rate.** Should SY08 give a fluid rate for at-risk dogs? No source found states one. SY10 and SY05 may hold the relevant resuscitation guidance.
2. **Furosemide dose.** Could SY09 carry the furosemide dose for suspected fluid overload, with this page linking to it?
3. **Altitude.** The ARDSVet altitude correction (above 1,000 m) may matter for inland practices. No source was found that gives the altitude of South African practices, so the page states only the rule.
4. **Seeing the page.** It still needs to be opened at `/clinical/SY08` (light and dark theme) once a preview server can run.

## Files written

- `clinical/SY08/search-log.md`
- `clinical/SY08/evidence.csv` (44 rows)
- `clinical/SY08/references-check.csv` (25 rows)
- `clinical/SY08/report.md`
- `webapp/Babesiosis.Web/public/assets/clinical/SY08.json`
- The SY08 row of `clinical/ledger.md`
