# SY12 Acute pancreatitis: run report

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY12.json` (validator: `OK`, no warnings). The page was not viewed in a browser, as the coordinator instructed. The page agent ran as a subagent and could not write this file; the coordinator saved its report text here unchanged.

## Definition

**Changed.** The working definition accepted raised pancreatic lipase OR imaging. In babesiosis a raised lipase alone is not enough. In B. rossi, 28% of 87 dogs had Spec cPL above 400 µg/L at admission, most of them with no gastrointestinal signs, and cPL did not differ between dogs with and without signs (Köster 2015). The page now uses the clinical reference standard of the general canine literature: compatible signs plus increased pancreas-specific lipase plus compatible imaging (Cridge 2021). Only histology confirms the diagnosis (Möhr 2000).

Pancreatitis is a distinct, documented complication of B. rossi (Möhr 2000, 4 histological cases) and is reported in B. canis. It is rare or low in B. gibsoni, and no reports were found for B. vogeli.

## References: 23

| Level / kind | n | References |
|---|---|---|
| Babesiosis, cohort or case series (B) | 7 | Möhr 2000, Köster 2015, Máthé 2006, Weingart 2023, Crnogaj 2017, Strobl 2020, Masuda 2019 |
| Babesiosis, case report (C) | 1 | Choi 2019 (atovaquone-proguanil) |
| Babesiosis reviews | 2 | Jacobson 2006, Leisewitz 2023 |
| General canine pancreatitis, trials and cohorts (D) | 5 | Steiner 2023 (fuzapladib RCT), Angst 2026 (TAP pilot), Mansfield 2011, Harris 2017, Okanishi 2019 |
| General canine guideline (D) | 1 | Marks 2018 ACVIM gastroprotectants |
| General canine reviews (E) | 3 | Cridge 2021, Lim 2024, Cridge 2024 |
| Assay studies | 3 | Steiner 2017, Goodband 2018, Lim 2020 |
| Label (E) | 1 | Cerenia SPC (UK VMD) |

All 23 were checked in PubMed (22) or on the publisher's site (the SPC). Title, first author and year match. None was removed.

## Treatments: 11

No treatment of pancreatitis has been tested in dogs with babesiosis. Every treatment is level D or E.

| Treatment | Status | Level |
|---|---|---|
| IV fluid therapy (no dose; links SY10, SY08, SY05) | standard | E |
| Opioid analgesia, methadone | standard | D |
| Maropitant | standard | D (dose from label) |
| Early enteral feeding, low-fat diet | standard | D |
| Ondansetron | proposed | D |
| Fuzapladib | proposed | D |
| Prednisolone | proposed | D |
| Liposomal bupivacaine TAP block | proposed | D |
| Antibiotics, only for shown infection | proposed | E |
| Acid suppressants, only for ulceration or bleeding | proposed | D |
| NSAIDs | harmful (avoid) | E |

There are 8 dose rows. An independent sub-agent re-read every dose against its source with no view of the page: all 9 checked items matched. It suggested two wording fixes, and both were applied: the prednisolone mortality is at "1 month after discharge", and the amylase cut-off of 3500 U/L appears in the abstract and results while 3600 U/L is in the methods.

## What could not be found

- Any study of any pancreatitis treatment in dogs with babesiosis.
- Systematic abdominal ultrasound or histology in a babesiosis cohort; validation of Spec cPL against histology in babesiosis.
- A readable source with a metoclopramide or buprenorphine dose. The JAVMA 2024 review returned HTTP 403, and the BSAVA formulary could not be reached. Metoclopramide is therefore left off the page and recorded as a gap.
- The full text of the 2024 Lim management review: its abstract only was used for statements on fluids, antibiotics, NSAIDs, PPIs, plasma and fuzapladib licensing.
- South African availability of any drug: no source, so every availability field is empty.

## Least-sure statements

- B. canis frequency: Máthé 2006 (33% of complicated cases) and Strobl 2020 (40% mortality with pancreatitis) were read as abstracts only, and the diagnostic method is not given.
- Prognosis: whether pancreatitis worsens the outcome on its own. The sources disagree in kind: Jacobson 2006 and Strobl 2020 found high mortality, while Köster 2015 found no association of cPL with death. The page presents both.
- The prednisolone dose route is not stated in the Okanishi abstract. The page says so.
- Level "D" for maropitant and opioids rests on use in pancreatitis trials (standard care), not on a test of the drugs themselves.

## Decisions for the coordinator or the user

1. **Two statuses do not fit the scale.** Antibiotics and acid suppressants are listed as `proposed` with names that limit them to a shown infection or bleeding. The status scale has no "not routinely indicated" value. A `no_benefit` status would wrongly imply that they were tested.
2. **The TAP block** is a referral technique with pilot data only, and the product may not be available in South Africa. Keep it or drop it.
3. **Atovaquone-proguanil-induced pancreatitis** (one case report, suspected B. gibsoni) is a differential and a species note on this page. TX00 may want a cross-reference.

## Files written

- `/webapp/Babesiosis.Web/public/assets/clinical/SY12.json`
- `/clinical/SY12/search-log.md`
- `/clinical/SY12/evidence.csv`
- `/clinical/SY12/references-check.csv`
- `/clinical/ledger.md` (SY12 row only)
- `/clinical/SY12/report.md` (saved by the coordinator)
