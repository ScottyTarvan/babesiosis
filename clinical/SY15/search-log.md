# SY15 search log

Run date: 2026-11-12. Agent: SY15 page agent.

| Date | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | `/core/search/clinical_treatment/combined_set.csv` | grep `rhabdomyolysis`, `myoglobin`, `muscle`, `creatine kinase` (all columns) | 0 | 0 |
| 2026-11-12 | `/core/data/terms/term_display.csv` | concepts Rhabdomyolysis, myopathy, myositis | Rhabdomyolysis 15 articles; Myositis (inclusion body) 14 (false NLP matches, not used) | – |
| 2026-11-12 | `/core/data/terms/*.json` | files with CUI C0035410 (Rhabdomyolysis) | 15 CB + HU002 | Most mentions are lists of complications in introductions. Used CB093, CB493 |
| 2026-11-12 | `/core/data/markdown/*.md` | grep `rhabdomyoly`, `myoglobin`, `creatine kinase`, `creatine phosphokinase`, `CPK`, `CK` | 27 files | CB004, CB006, CB394 (CPK >600 U/L criterion and counts), CB141 (CK table), CB093, CB493. CB017 uses the same criterion but gives no count; CB148 gives no CK numbers; CB242, CB259, CB318, CB325 are secondary statements |
| 2026-11-12 | `/core/cohorts.json` | cohorts of kept articles | – | CB394 = CH33; CB141 = CH12; CB093 = CH27; CB004 and CB006 have no cohort (both Zagreb 2017, possible overlap, noted) |
| 2026-11-12 | PubMed | `(rhabdomyolysis OR myoglobinuria OR "creatine kinase" OR myopathy OR myositis) AND babesi* AND (dog OR dogs OR canine)` | 5 | 3 (Jacobson & Lobetti 1996, Jacobson 2006, Furlanello 2005) |
| 2026-11-12 | PubMed | `Jacobson LS[Author] AND Lobetti RG[Author] AND rhabdomyolysis` | 1 | 1 (same) |
| 2026-11-12 | PubMed | `Welzl C[Author] AND babesiosis` | 1 | 1 (Welzl 2001; full text PDF read from the open-access journal site) |
| 2026-11-12 | PubMed | `rhabdomyolysis[Title] AND (dog[Title] OR dogs[Title] OR canine[Title])` | 20 | 7 (Smith 2020, Frye 2018, Devall 2018, Santifort 2023, Chen 2018, Murray 2003, Haburjak 2002) |
| 2026-11-12 | PubMed | `(myoglobinuria OR myoglobin) AND (dog OR dogs OR canine) AND (urine OR urinalysis OR hemoglobinuria)` | 30 | 0 new |
| 2026-11-12 | PubMed | `(rhabdomyolysis OR myoglobinuria OR "pigment nephropathy" OR "exertional myopathy") AND (dogs OR canine OR "small animal") AND (review OR treatment OR management)` | 66 (first 40 screened) | 0 new (no canine review of rhabdomyolysis treatment) |
| 2026-11-12 | PubMed | `rhabdomyolysis acute kidney injury prevention guideline bicarbonate mannitol` | 2 | 1 (Michelsen 2019 DASAIM/DSIT guideline) |
| 2026-11-12 | PubMed | `Beyond muscle destruction: a systematic review of rhabdomyolysis for clinical practice` | 1 | 1 (Chavez 2016, PMC full text) |
| 2026-11-12 | PubMed | `hyperkalemia dogs treatment calcium gluconate insulin dextrose review` | 0 | 0 (hyperkalaemia treatment left to SY05) |
| 2026-11-12 | PubMed | `2022 WSAVA guidelines for the recognition, assessment and treatment of pain` | 1 (wrong paper) | 0 |
| 2026-11-12 | Europe PMC | `(rhabdomyolysis OR myoglobinuria) AND babesi* AND (dog OR canine)` | 101 (first 49 screened) | 0 new (no further babesiosis muscle case) |
| 2026-11-12 | Europe PMC | DOI and title search for the WSAVA 2022 pain guideline | 0 | 0 |
| 2026-11-12 | Crossref | WSAVA pain guideline bibliographic search | 3 | Confirms Monteiro et al. 2023, JSAP 64:177-254 (full text 403 at Wiley) |
| 2026-11-12 | Web | WSAVA pain guideline PDF and protocol sheets | 10 | 1 (WSAVA Emergency and critical care protocol sheet, read in full) |
| 2026-11-12 | Web | eClinpath (Cornell) urinalysis, chemical constituents | 1 page | 1 (haemoglobin vs myoglobin) |
| 2026-11-12 | Web | Wiley page of Jacobson & Lobetti 1996 | 403 | Abstract only |

## Stop rule

The searches on canine rhabdomyolysis, myoglobinuria and treatment returned no further treatment and no further diagnostic criterion after the human guideline (Michelsen 2019) and review (Chavez 2016) were added. The Europe PMC search returned no further babesiosis case. Search stopped.

## Not reached

- Full text of Jacobson & Lobetti 1996 (paywall): CK and myoglobin values and the treatment of the two dogs are unknown.
- Full text of the WSAVA 2022 pain guideline (Wiley 403; no English PDF found on wsava.org): no opioid dose could be verified, so the analgesia row has no dose.
- Full text of Jacobson 2006 (Elsevier): abstract only.
