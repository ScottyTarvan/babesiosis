# SY11 report: SIRS and multiple organ dysfunction

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY11.json`. Validator: `OK`, no warnings. View: **validated, not seen** (the request to start the `babesiosis-web-mock` preview server was declined, so no alternative port was tried).

## Definition

**Changed.** The working definition ("SIRS with dysfunction of two or more organs; the umbrella for complicated babesiosis") mixed two things together:

- *Complicated babesiosis* = signs not explained by haemolytic anaemia alone. It starts at **one** organ complication (Jacobson 2006; Crnogaj 2017, Zagreb criteria).
- *SIRS* (2 of 4 criteria) is met by most dogs: 61% to 87% of *B. rossi* dogs and 37% to 68% of *B. canis* dogs. It did **not** predict death in *B. rossi* (Welzl 2001; Leisewitz 2019).
- *MODS* (2 or more organs) is the severe end, and organ count tracks death in *B. canis* (Matijatko 2010; Máthé 2006).

The 2026 canine sepsis consensus (Goggs et al.) also makes organ dysfunction, not SIRS, central to the definition. The page follows that.

## References: 28

| Level of the source | n | Which |
|---|---|---|
| Trials in dogs with babesiosis (A) | 2 | N-acetylcysteine in *B. gibsoni* (Khan 2026, Mundassery 2025) |
| Cohorts or series of 5 or more dogs with babesiosis (B) | 16 | Onderstepoort *B. rossi*: Welzl, Leisewitz, Nel, Keller, Böhm, Schoeman, Goddard. *B. canis*: Matijatko 2010, Matijatko 2009, Crnogaj, Beletić, Weingart, Máthé, Eisenecker, Eichenberger. *B. gibsoni*: Kandasamy |
| Case reports or uncontrolled reports (C) | 2 | Plasmapheresis: Belomyttseva 2026, Belova 2025 |
| Human malaria or canine consensus (D) | 7 | Warrell 1982, Prasad (Cochrane), Di Perri, Das, Hemmer, Looareesuwan; Goggs 2026 consensus |
| Narrative review (E) | 1 | Jacobson 2006 |

**Cohort overlap.** The Onderstepoort *B. rossi* cohorts may share dogs. Leisewitz 2019 pools three databases from 2006 to 2016, and Nel 2004 and Keller 2004 were probably recruited in the same period. These were not merged because no shared `cohort_id` is recorded. The page says they may overlap.

**Reference checks.** Every reference was checked in PubMed (or in Crossref, or on the Hrčak publisher page for Matijatko 2010), and title, first author and year match.

## Treatments: 6

| Treatment | Status | Level | Doses |
|---|---|---|---|
| Supportive intensive care, organ by organ | standard | B (2) | none here: they are on the organ pages |
| Antibiotics for suspected secondary bacterial infection | proposed | C (1) | amoxicillin-clavulanic acid 22 mg/kg IV every 8 h, with or without enrofloxacin 10 mg/kg IV every 12 h (Crnogaj 2017) |
| Plasmapheresis | proposed | C (2) | none |
| N-acetylcysteine | proposed | A (2) | 70 mg/kg PO once daily for 14 days (Khan 2026); 70 mg/kg PO for 5 days, frequency not stated (Mundassery 2025) |
| Pentoxifylline | conflicting | D (4) | none: human data only, no dose transferred |
| Glucocorticoids against the inflammatory response | harmful | D (2) | none |

**Dose check.** I re-read each of the three doses against its source text: `/core/data/markdown/CB006.md` (Methods) and the abstracts of CB151 and CB142. They match on number, unit, route and frequency. No sub-agent was used for this check.

## Not found

- No trial in dogs of any treatment aimed at the inflammatory response.
- No study in dogs with babesiosis of NSAIDs, vitamins C or E, pentoxifylline, fresh frozen plasma or blood cultures.
- No canine sepsis treatment guideline. The 2026 consensus covers definition and criteria only.
- No canine babesiosis study of the APPLE score. The consensus mentions one, but I did not identify it.

## Statements I am least sure of

- **Welzl 2001 and Matijatko 2010 were read as abstracts only.** Their SIRS and organ criteria are not on the page. The listed criteria come from Leisewitz 2019 (SIRS) and Crnogaj 2017 (organs).
- **Band neutrophil odds ratio.** Leisewitz 2019 gives 5.9 in its text and 4.9 in Table 1. The page uses the table value.
- **Enrofloxacin 10 mg/kg IV every 12 h** is given as the source states it, with a note to check a formulary.
- **Antibiotics, level C.** This rests on a single study that reports use, not effect.
- **Plasmapheresis.** The 2026 abstract gives no number of dogs and no design, so level C is a conservative choice.
- **Glucocorticoids marked `harmful`.** This rests on human cerebral malaria trials (level D), not on dogs.

## Decisions for the coordinator

- The definition was changed (see above). `index.md` still carries the old working definition.
- Should the glucocorticoid status be `harmful` (level D) or `no_benefit`? The human evidence shows harm in one trial and no benefit in the Cochrane review.
- The page has not been seen in the browser. Someone should open `/clinical/SY11` once the mock server can run.

## Files written

- `/clinical/SY11/search-log.md`
- `/clinical/SY11/evidence.csv`
- `/clinical/SY11/references-check.csv`
- `/clinical/SY11/report.md`
- `/webapp/Babesiosis.Web/public/assets/clinical/SY11.json`
- the SY11 row of `/clinical/ledger.md`
