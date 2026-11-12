# SY11 search log

Run 2026-11-12. One row for each search. "Kept" = records used on the page.

| Date | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | `/core/search/clinical_treatment/combined_set.csv` | `syndromes` contains `sirs`, `mods` or `complicated babesiosis` | 34 | 7 (CB006, CB106, CB516, CB517, CB267, rescreen DOI 10.31016/1998-8435-2026-20-2-302-309; CB059 had no abstract) |
| 2026-11-12 | `/core/search/synthesis/SEV.md` | read whole (severity, MODS, prognosis) | 1 file | used to find CB399, CB372, CB338, CB516, CB006, CB106 |
| 2026-11-12 | local notes and texts `/core/articles/`, `/core/data/markdown/` | CB040, CB399, CB006, CB106, CB516, CB267, CB151, CB142 (grep for criteria, mortality, doses) | 8 | 8 |
| 2026-11-12 | PubMed | `babesiosis dog (SIRS OR "systemic inflammatory response" OR "multiple organ dysfunction")` | 17 | 7 (Welzl 2001, Matijatko 2009, Máthé 2006, Beletić 2021, Nel 2004, Jacobson 1994 read but not used, Kuleš 2016 read but not used) |
| 2026-11-12 | PubMed | `babesiosis dog (prognostic OR mortality OR "predictor of death" OR outcome) (lactate OR glucose OR cortisol OR score)` | 12 | 5 (Leisewitz 2019, Kandasamy 2021, Schoeman 2007, Nel 2004, Khan 2026) |
| 2026-11-12 | PubMed | `(babesiosis OR Babesia) dog (complicated OR "complications") (review OR treatment)` | 69 (60 screened by title) | 3 (Jacobson 2006, Keller 2004, Köster 2015 read; Köster not used: no supportive-care section) |
| 2026-11-12 | PubMed | `(babesiosis OR Babesia) dog (glucocorticoid OR prednisolone OR dexamethasone OR corticosteroid OR pentoxifylline OR "anti-inflammatory" OR antioxidant OR "vitamin C" OR "N-acetylcysteine" OR plasma OR immunomodulat*)` | 93 (60 screened by title) | 2 (Mundassery 2025, Khan 2026). No glucocorticoid, NSAID or pentoxifylline trial in dogs |
| 2026-11-12 | PubMed | `(babesiosis OR Babesia) dog (bacteremia OR bacteraemia OR "blood culture" OR antibiotic OR antimicrobial) (sepsis OR septic OR complicated)` | 46 (30 screened) | 1 (Böhm 2006 found here). No blood-culture study |
| 2026-11-12 | PubMed | `(babesiosis OR Babesia) dog (plasmapheresis OR "plasma exchange" OR "extracorporeal" OR hemoperfusion OR "fresh frozen plasma")` | 0 | 0 |
| 2026-11-12 | PubMed | `(dexamethasone OR corticosteroid OR pentoxifylline) cerebral malaria (trial OR randomized)` | 19 | 6 (Warrell 1982, Prasad 2000 Cochrane, Di Perri 1995, Das 2003, Hemmer 1997, Looareesuwan 1998); Hoffman 1988 read, covered by the Cochrane review |
| 2026-11-12 | Europe PMC | `(babesiosis OR babesia) AND dog AND (bacteraemia OR bacteremia OR "blood culture" OR "secondary bacterial")` | 414 (first 20 screened) | 0 |
| 2026-11-12 | Europe PMC | `(babesiosis) AND dog AND (glucocorticoid OR dexamethasone OR corticosteroid) AND (SIRS OR complicated OR "inflammatory response")` | 182 (first 20 screened) | 2 (Goggs 2026 sepsis consensus, Eisenecker 2026) |
| 2026-11-12 | Europe PMC | `(babesiosis) AND dog AND (plasmapheresis OR "plasma exchange" OR "blood purification")` | 48 (first 10 screened) | 0 new |
| 2026-11-12 | Europe PMC | `(babesiosis OR babesia) AND dog AND (APPLE OR "illness severity" OR "severity score" OR SOFA OR "scoring system")` | 254 (first 25 screened) | 0 new (Goggs 2026 again) |
| 2026-11-12 | Europe PMC | vitamin E / vitamin C; NSAID; pentoxifylline; fresh frozen plasma, each with `babesiosis AND dog` | 104, 114, 21, 59 (first 5 to 10 screened each) | 0 |
| 2026-11-12 | Crossref | DOI 10.31016/1998-8435-2026-20-2-302-309 (abstract) | 1 | 1 (Belomyttseva 2026) |
| 2026-11-12 | Hrčak | https://hrcak.srce.hr/62147 (Matijatko 2010 landing page and abstract) | 1 | 1 |
| 2026-11-12 | PMC full text | PMC6065580 (Köster 2015 review), PMC13490290 (Goggs 2026 consensus) | 2 | 1 (Goggs) |
| 2026-11-12 | AOSIS (JSAVA) | Welzl 2001 full text PDF | 1 | abstract only used: the PDF could not be turned into text in this run |

## Stop

The last six searches (Europe PMC rows) returned no new treatment and no new diagnostic criterion. Search stopped.

## Not reached

- Welzl 2001 full text: the PDF could not be converted, so its SIRS and organ criteria are not on the page; the criteria come from Leisewitz 2019 and Crnogaj 2017.
- Matijatko 2010 full text (Hrčak PDF): not read; abstract only.
- Jacobson and Swan 1995, "Supportive treatment of canine babesiosis" (JSAVA 66:95-105): abstract only; it gives no conclusion on glucocorticoids in the abstract, so it is not cited.
- The babesiosis study of the APPLE score that the 2026 sepsis consensus mentions was not identified.
