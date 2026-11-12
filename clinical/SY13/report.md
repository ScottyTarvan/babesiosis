# SY13 report: haemorrhagic gastroenteritis and gut signs

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY13.json` (validator: `OK`, no warnings). Not viewed in a browser (instruction): `validated, not seen`. The page agent ran as a subagent and could not write this file; the coordinator saved its report text here.

## Definition: changed. This is not a distinct syndrome

No paper defines haemorrhagic gastroenteritis as a complication of babesiosis, and none gives a threshold or a grading. The old "gut form" (vomiting, diarrhoea, melaena, haematemesis, abdominal effusion) is now described as acute pancreatitis (Köster 2015 review, CB493). The page treats gut signs as non-specific findings of the disease and is built around finding their cause. This is a rule-17 case: the user decides whether the page stays.

## References: 23

| Level | References |
|---|---|
| B (babesiosis series of 5 dogs or more) | R2, R3, R4, R5, R6, R10, R11, R12, R14, R15 |
| C (case report) | R13 |
| D (same signs from another cause) | R7, R8, R17, R20, R21 |
| E (review, label, drug summary) | R1, R9, R16, R18, R19, R22, R23 |

- 21 references were confirmed in Crossref and/or PubMed. Two have no DOI and are cited by URL after they were opened: the UK product information for Cerenia (maropitant) and a Clinician's Brief drug summary.
- CB268 was dropped. It is an Indian outbreak in puppies with haemorrhagic enteritis that tested negative for enteric viruses. Its DOI returns 404 at Crossref and doi.org, and the publisher page needs a login.

## Treatments: 9

No gut treatment was tested in dogs with babesiosis.

| Treatment | Status | Level |
|---|---|---|
| IV fluids and electrolytes | standard | D (doses from a parvovirus review) |
| Maropitant | standard | D (UK label dose; used in a B. canis series but not evaluated) |
| Transfusion for gut blood loss | standard | D (links to SY01 and SY03) |
| Omeprazole or esomeprazole | proposed | D (doses from a B. canis series; ACVIM consensus for when to use them) |
| Early enteral nutrition | proposed | D (parvovirus trial; no dose) |
| Sucralfate | proposed | D (no dose found) |
| Splitting oral doxycycline when the dog vomits | proposed | E |
| Atropine for imidocarb's cholinergic signs | proposed | E |
| Antibiotics for bloody diarrhoea without sepsis | no_benefit | D (one randomised trial and one meta-analysis, not in babesiosis) |

All 15 dose rows were re-read against their sources in this run, without a sub-agent, and all match.

## Answers to the page questions

1. **Distinct syndrome:** no.
2. **How often:**
   - *B. rossi*: vomiting in 17 of 87 dogs at Onderstepoort, and the main complaint in 6 of 146 in the Eastern Cape.
   - *B. canis*: vomiting in 9% (Germany).
   - *B. gibsoni*: vomiting in 24% (Hong Kong), gut signs in 29% (Korea), melaena in 30% of 23 dogs (India).
3. **Cause:** none proven. The candidates in the sources are pancreatitis; gut-lining petechiae, found in 4 of 6 fatal *B. canis* cases with no thrombi; uraemia; imidocarb's cholinergic effect (2 dogs vomiting and 2 with bloody diarrhoea out of 49); and *E. canis* co-infection (melaena in 43% of *E. canis* dogs in an Indian series).
4. **Parvovirus:** no report of the two infections together and no study that tells them apart. Leukopenia occurs in both, so it does not separate them. The faecal antigen test has a sensitivity of 16% to 80%, so a negative test does not rule parvovirus out.
5. **Treatment tested in babesiosis:** none.

## Not found or not verified

- **Atropine before imidocarb:** the two sources differ fivefold. One review gives 0.05 mg/kg with no route; the drug summary gives 0.01 mg/kg IV. Neither cites a trial. Both rows are on the page.
- **Missing doses:** no source read gave a dose for sucralfate, metoclopramide or ondansetron.
- **Paywalled:** the ENOVAT antimicrobial guideline, so its meta-analysis abstract is used instead.
- **Abstract only:** Keller 2004, Jacobson 2006, Unterer 2011, Scahill 2024 and Mohr 2003.
- **Gut pathology in B. rossi:** none described.
- **South African availability:** blank for every treatment; no South African source was found.
- **Fluid doses:** the fluid, potassium and dextrose doses come from parvovirus care in puppies, not from babesiosis.

## Statements I am least sure of

- The atropine doses and the parvovirus-derived fluid doses (above).
- CB304's babesiosis denominator is unclear, so only its *E. canis* figure is used.
- The Clinician's Brief page is dated October 2026, so its year is given as 2026.
- The five abstract-only references.

## Decisions for the coordinator or user

1. **The page itself:** keep SY13 as a short "gut signs" page, or fold it into SY12 (pancreatitis).
2. **Atropine row:** whether to align it with TX00 (imidocarb).

## Files written

- `/webapp/Babesiosis.Web/public/assets/clinical/SY13.json`
- `/clinical/SY13/search-log.md`, `evidence.csv`, `references-check.csv`
- `/clinical/ledger.md` (SY13 row only)
- `/clinical/SY13/report.md` (saved by the coordinator)
