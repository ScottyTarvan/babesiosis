# SY09 Cardiac dysfunction: run report

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY09.json`. Validator: `OK`. View: validated, not seen (the coordinator views the page).

## Definition

Confirmed, with two changes (recorded in `definition_note`):

- ECG changes alone do not define the syndrome. Most are non-specific and did not match troponin or pathology (Lobetti 2002, Dvir 2004). Only ventricular premature complexes were linked to a high troponin.
- Clinical congestive heart failure in babesiosis is proposed in a review (Lobetti 2005) but no case series documents it. The page keeps heart failure in scope but says so.

## References: 17

| Level of the source | Count | References |
|---|---|---|
| Babesiosis, cohort or case-control (B) | 7 | Lobetti 2002, Dvir 2004, Lobetti 2012, Bartnicki 2017, Kızıltepe 2024, Gowtham 2024, Lobetti & Jacobson 2001 |
| Babesiosis, survey or necropsy series | 3 | Sharma 2025 (pooled with Ehrlichia), Huber 2026, Zygner 2021 |
| Babesiosis reviews (E) | 2 | Lobetti 2005, Köster 2015 |
| Other canine evidence (D) | 4 | Keene 2019 (ACVIM guideline), Diniz 2008, Hayes 2016, Spotswood 2006 (experimental anaemia) |
| Formulary (E) | 1 | MSD Veterinary Manual, antiarrhythmics |

Read in full: 7. Abstract only: 10. The South African troponin and ECG studies (Lobetti 2002, Dvir 2004) are behind paywalls; their numbers come from the PubMed abstracts. Lobetti 2002 and Dvir 2004 are from the same Onderstepoort group and years and may share dogs; they are counted as two studies, which may overstate independence.

## Treatments: 9

| Treatment | Status | Level | Dose source |
|---|---|---|---|
| Oxygen and strict cage rest | standard | E | none (no dose) |
| Lidocaine for ventricular arrhythmia | standard | E | MSD Veterinary Manual |
| Restricted, monitored IV fluids | proposed | E | none (no rate published) |
| Correction of potassium | proposed | E | none |
| Dopamine for systolic dysfunction | proposed | B | Gowtham 2024 (babesiosis series) |
| Dobutamine | proposed | D | ACVIM 2019 |
| Pimobendan | proposed | D | ACVIM 2019 |
| Furosemide | proposed | D | ACVIM 2019 |
| Hydroxyethyl starch | harmful | D | Gowtham 2024 (use); Hayes 2016 (harm) |

No cardiac treatment has been tested in dogs with babesiosis. Every dose except dopamine and HES is from a general canine source. All 9 dose rows were re-read against their sources, and an independent sub-agent checked them again with no view of the page: all matched. One wording fix followed (the lidocaine route no longer says "slowly", which the source does not state).

## What I could not find

- Any trial or comparison of a cardiac treatment in babesiosis.
- A fluid rate or transfusion rate for dogs with cardiac involvement (page question 5): no source.
- A dose for potassium or magnesium correction in this setting; no magnesium data in babesiosis.
- A validated troponin or NT-proBNP cut-off for prognosis.
- Any cardiac data for B. vogeli; B. gibsoni data are pooled with Ehrlichia.
- South African availability of any drug: no source, so the field is empty.

## Statements I am least sure of

- Gowtham 2024 mortality (74% with dysfunction against 31% without): the paper's text and table disagree on the number of deaths. The page says so.
- The dopamine level B: the series has more than 5 dogs, but gives no outcome by treatment. The level follows the rule, not the strength of the evidence; the summary says benefit is unknown.
- HES as `harmful`: the harm evidence is from critically ill dogs with other diseases (abstracts of two retrospective studies), not babesiosis.
- Species labels: the South African studies before 2006 report "B. canis" or "virulent babesiosis"; the page labels them B. rossi, as the reviews do.

## Decisions for the coordinator or the user

1. Whether to keep HES on the page at all (shown only as `harmful`, with the dose as reported in the babesiosis series).
2. Whether level D doses from mitral valve disease (pimobendan, furosemide, dobutamine) belong on a babesiosis page; they are labelled, but the heart disease differs.
3. Two local articles were dropped because they cannot be verified: CB284 (DOI does not resolve) and CB497 (no DOI or PMID). The review data may want to flag them.

## Files written

- `/webapp/Babesiosis.Web/public/assets/clinical/SY09.json`
- `/clinical/SY09/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md`
- My row in `/clinical/ledger.md`
