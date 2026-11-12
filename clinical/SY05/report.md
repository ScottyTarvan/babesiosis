# SY05 report: Acute kidney injury

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY05.json`. The validator prints `OK` with no warnings. The page was **not viewed**: the preview server start (`babesiosis-web-mock`) was declined in this session, so the ledger says `validated, not seen`.

## Definition

I changed the working definition. Studies in babesiosis use IRIS AKI grading: creatinine, its rise over 48 h, and urine output. That includes non-azotaemic grade I injury, so "azotaemia persisting after rehydration" covers only the overt failure form. "Haemoglobinuric nephropathy" is not supported as the main cause. Infused haemoglobin did not cause significant nephropathy in dogs (Lobetti 1996), and fatal *B. canis* cases show hypoxic proximal tubular necrosis (Máthé 2007). Hypoxia and hypoperfusion are the favoured mechanisms. Glomerular and protein-losing disease stays in scope; it is reported mainly with *B. gibsoni* (6 dogs) and *B. vulpes* (one Spanish laboratory series).

## References: 28

| Level of the source | Count | References |
|---|---|---|
| B (cohort, case-control or series in babesiosis) | 13 | R2, R4, R5, R6, R7, R8, R9, R13, R15, R16, R17, R18, R19 |
| C (case reports in babesiosis) | 4 | R14, R24, R25, R28 |
| D (canine AKI guidance or studies, other causes; human data) | 6 | R1, R10, R11, R12, R23, R26 |
| E (review, lecture, experimental) | 5 | R20, R21, R3 (experimental), R22, R27 |

These are reference types. The levels given to treatments are on the page. 17 references were read in full or as the abstract in PubMed, and 2 by Crossref. 3 are guideline or lecture pages (URL), and 1 is a journal page. Every reference was matched by DOI, PMID or publisher page for title, first author and year (`references-check.csv`).

## Treatments: 11

| Treatment | Status | Level |
|---|---|---|
| IV isotonic crystalloid fluids | standard | D |
| Renal replacement therapy (haemodialysis, peritoneal dialysis) | proposed | C (2 single-dog reports in babesiosis) |
| Furosemide | proposed | D |
| Mannitol | proposed | E |
| Antiemetics and gastric protection | proposed | C |
| Amlodipine for hypertension | proposed | D |
| Antiproteinuric treatment (ARB or ACEI, kidney diet) | proposed | D (no dose: IRIS gives none) |
| Antithrombotic prophylaxis in protein-losing nephropathy | proposed | D |
| Immunosuppression for immune-complex glomerulonephritis | proposed | C (1 dog) |
| Dopamine | no_benefit | D |
| Fenoldopam | no_benefit | D |

None of these was tested for kidney injury in dogs with babesiosis.

## Dose check

A sub-agent with no view of the page re-read every dose and threshold in its source. All numbers matched. It found these points, and I corrected all of them on the page:

- No route is stated for the furosemide doses, the mannitol bolus or the acetylsalicylic acid dose. The page now says "route not stated".
- Furosemide doses were recorded for 20 of the 22 oliguric dogs. The page now gives the denominators (7 of 20, 11 of 20).
- Amlodipine: the discussion of Cole 2020 also gives a range of 0.1 to 1.2 mg/kg/day. This is now in the dose note.
- IRIS footnote ranges (clopidogrel 1 to 4 mg/kg, acetylsalicylic acid 1 to 5 mg/kg) differ from the main text (1.1 to 3 and 2 to 5 mg/kg). Both are now on the page.
- The dopamine "no change in outcome" statement refers to human studies. The wording is corrected.
- The hypertension figure (75%) means "at some point". The 24 h AKI count is out of the 13 dogs re-tested. Both are corrected.
- The Segev lecture's fluid formula reads "% Hydration". The page gives it as the fraction dehydrated.

## What could not be found or verified

- No source gives a dose change for diminazene or imidocarb in kidney injury, and no source proposed urine alkalinisation.
- The IRIS 2024 AKI consensus (R10) and the IRIS haemodialysis guideline (R23) were read as abstract only (subscription). The canine AKI doses therefore come from one open observational study (R11: doses as used, not tested) and one expert lecture on VIN (R21). The lecture is level E, and the VIN link may need a free login for some readers.
- Pomianowski 2008, peritoneal dialysis in *B. canis* acute renal failure: no text reachable, so it is not on the page.
- The *Babesia* species is not stated in the two dialysis case reports (R24, R25).
- No data on how often chronic kidney disease follows. One *B. gibsoni* case (R28) still had a creatinine of about 171 µmol/L at 30 days. I did not put this on the page: it is one dog, and that dog had no baseline.

## Statements I am least sure of

- Furosemide and mannitol doses: they come from non-babesiosis sources with no outcome data, and no route is stated.
- Fluids marked `standard` at level D: every babesiosis cohort gave fluids "as needed", but none evaluated them.
- Amlodipine: babesiosis dogs are usually hypotensive (R17). The entry rests entirely on AKI of other causes.

## Decisions for the user

- Whether to keep level E lecture doses (mannitol) on the page or drop doses that have no peer-reviewed source.
- A veterinarian should review the page before use (open decision in `index.md`).
- The page has not been seen in the browser. Someone should open `/clinical/SY05` once a server can be started.

## Files written

- `/webapp/Babesiosis.Web/public/assets/clinical/SY05.json`
- `/clinical/SY05/search-log.md`, `evidence.csv` (47 rows), `references-check.csv` (28 rows), `report.md`
- `/clinical/SY05/_refmap.csv` (citation key to R-number) and `_local_candidates.txt` (the local candidate list): working files
- My row in `/clinical/ledger.md`
