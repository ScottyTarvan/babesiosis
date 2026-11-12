# SY08 search log

Run 2026-11-12. Agent: SY08 page session. Hits = records returned; kept = records used on the page.

| # | Date | Source | Query or file | Hits | Kept |
|---|---|---|---|---|---|
| 1 | 2026-11-12 | file | `/core/search/clinical_treatment/combined_set.csv`, `syndromes` matching ards, pulmonary, respiratory, haemoptysis, lung | 20 | 6 (CB102, CB111, CB356, CB080, CB079, CB493 via review tag) |
| 2 | 2026-11-12 | file | `/core/search/synthesis/PUL.md` | 1 | used to find CB447, CB040-linked papers |
| 3 | 2026-11-12 | file | `/core/data/markdown/` CB102, CB111, CB356, CB080, CB493, CB040, CB098, CB260 (full text); CB447, CB079, CB389, CB371, CB332 (abstract) | 13 | 8 |
| 4 | 2026-11-12 | file | `/core/data/terms/*.json` for Pulmonary Edema, ARDS, Acute Lung Injury, Non-cardiogenic pulmonary edema, TRALI, Neurogenic pulmonary edema | 55 CB articles | 0 new (titles screened; CB256, CB028, CB098, CB134, CB507, CB418 grepped; only CB098 added a criterion) |
| 5 | 2026-11-12 | PubMed | `babesiosis AND dog AND (lung OR pulmonary OR respiratory OR ARDS)` | 34 | 7 (Daste 2013, Welzl 2001, Leisewitz 2001, Máthé 2006, Möhr 2000, Collett 2000, Sweers 2008) |
| 6 | 2026-11-12 | PubMed | citation lookup Welzl 2001, Leisewitz 2001, Wilkins 2007, Máthé 2006 | 4 | 3 (Wilkins 2007 not found in PubMed) |
| 7 | 2026-11-12 | PubMed | `Leisewitz[Author] AND Babesia rossi AND (clinical and pathological OR 320 cases OR outcome)` | 13 | 1 (CB040) |
| 8 | 2026-11-12 | Crossref | Jacobson Swan 1995 supportive treatment; Wilkins 2007 VetALI/VetARDS | 6 | Wilkins DOI found; full text blocked (publisher 403) |
| 9 | 2026-11-12 | web | VetARDS consensus criteria (search engine) | 10 | 0 (pointed to Wiley and repositories, all blocked) |
| 10 | 2026-11-12 | Europe PMC | `(VetARDS OR VetALI) AND (dog OR dogs) AND OPEN_ACCESS:Y` | 16 | 1 (ARDSVet 2025, full text) |
| 11 | 2026-11-12 | PubMed | `babesiosis AND dog AND (fluid therapy OR furosemide OR oxygen therapy OR mechanical ventilation OR pulmonary edema)` | 14 | 3 (Jacobson 2006, Leisewitz 1996, Jacobson & Swan 1995) |
| 12 | 2026-11-12 | PubMed | `(dogs OR canine) AND "high-flow nasal" AND (hypoxemia OR respiratory failure)` | 14 | 3 (Frischer 2022, Jagodich 2020, Whitney & Keir 2023 full text) |
| 13 | 2026-11-12 | PubMed | transfusion reaction consensus; fluid overload critically ill dogs; noncardiogenic oedema furosemide; ARDS dogs retrospective; ventilation outcome; AAHA fluid guidelines | 21 | 4 (Cavanagh 2016, Boiron 2019, Balakrishnan 2017, Bruchim 2014) |
| 14 | 2026-11-12 | web | TRACS TRALI/TACO definitions (unimi repository PDFs) | 3 | 0 (403, not read; left out) |
| 15 | 2026-11-12 | web | AAHA 2024 fluid guidelines (aaha.org, Allen Press) | 2 | 0 (403, not read; left out) |
| 16 | 2026-11-12 | web | sedation dose for dyspnoeic dogs (butorphanol) | 10 | 0 (Can Vet J review full text not reachable; dose not taken from a search snippet) |
| 17 | 2026-11-12 | PubMed / Crossref | esummary of all 25 references; Crossref for CB079 and CB111 | 25 | 25 verified |

## Stop decision

Searches 11 to 16 returned no new treatment and no new diagnostic criterion for lung injury in babesiosis. The candidate list in the page file (oxygen, ventilation, furosemide, fluid restriction, colloids or plasma, glucocorticoids, bronchodilators, sedation) was searched; no evidence was found for colloids, plasma (for this syndrome), bronchodilators, or for sedation of the awake dog. Search stopped.

## Not reachable

- Wilkins et al. 2007 (VetALI/VetARDS), Wiley: 403. Replaced by the 2025 ARDSVet definitions (open access).
- TRACS parts 1 to 3 (transfusion reactions): abstracts read in PubMed; full text 403. Not cited.
- 2024 AAHA fluid therapy guidelines: 403. Not cited.
- Thomovsky & Ilie 2024, Can Vet J (triage, sedation doses): full text not served by the PubMed tool, PMC bot check. Not cited.
