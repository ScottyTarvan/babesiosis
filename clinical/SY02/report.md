# SY02 report: secondary immune-mediated haemolytic anaemia

Run 2026-11-12. Page: `/webapp/Babesiosis.Web/public/assets/clinical/SY02.json` (validator: `OK`, no warnings). Not viewed in a browser (instruction for this run): `validated, not seen`.

## Definition

**Changed.** The working definition required antibody-mediated haemolysis that goes on despite antibabesial treatment. The sources do not use that condition:

- The ACVIM diagnosis consensus (R1) defines IMHA as anaemia + at least 2 markers of immune destruction (marked spherocytosis, saline agglutination, DAT, flow cytometry), or agglutination that persists after washing, + at least 1 sign of haemolysis. "Secondary" = attributable to an underlying disease such as Babesia.
- Onderstepoort *B. rossi* studies define secondary IMHA by a positive in-saline agglutination test at admission (R2, R3).
- Haemolysis that recurs after the parasite is cleared is reported only in single *B. canis* dogs (R5, R6) and in asplenic people with *B. microti* (R12).
- A positive Coombs test alone does not define it: it is common in uncomplicated infection and clears with antibabesial treatment (R7, R8).
- Evans syndrome: case reports only (R9).

The page uses the ACVIM definition, notes the babesiosis-study definition, and treats "persists after clearance" as a subset with a `working` threshold.

## References by evidence level (17)

| Level | Refs | Notes |
|---|---|---|
| A | 1 (R15) | Small randomised trial, *B. gibsoni*, 18 dogs (6 per group), cohort CH17 (R4 is the same cohort) |
| B | 9 (R2, R3, R4, R5, R7, R8, R10, R13, R17) | Cohorts and case series in babesiosis (R7 is from 1982) |
| C | 2 (R6, R9) | Case reports |
| D | 4 (R1, R11, R12, R16) | ACVIM consensus statements; DAT method study; human *B. microti* cohort |
| E | 1 (R14) | Narrative review (*B. gibsoni*) |

Read: 10 full text (R1, R2, R3, R4, R5, R8, R9, R11, R14, R15), 7 abstract only (R6, R7, R10, R12, R13, R16, R17).

## Treatments (7)

| Treatment | Status | Level | Note |
|---|---|---|---|
| Red cell transfusion | standard | B | Volumes on SY01 |
| Prednisolone / dexamethasone | proposed | A (1 study) | All 3 trial arms improved; benefit over antimicrobials alone not shown |
| Azathioprine as second drug | proposed | A (1 study) | Liver enzymes rose in the azathioprine arm |
| Ciclosporin or mycophenolate | proposed | D | ACVIM doses only |
| Antithrombotic prophylaxis | proposed | D | Not if platelets < 30 × 10^9/L, which is common in babesiosis |
| Human IVIG | proposed | D | Salvage only |
| Splenectomy | harmful | D | ACVIM: only after vector-borne infection excluded |

Every dose is from R11 (ACVIM treatment), R14, R15, R10 or R5. All 16 dose rows and the thresholds were re-read against the source; an independent sub-agent re-checked them with no view of the page: all 16 claims matched (dose, unit, route, frequency, duration, counts). Its notes: the CB247 discussion swaps the clindamycin and metronidazole doses in one passage (methods and abstract agree with the page); the R10 confidence interval looks like a typo and is not quoted; CB148 says 26% in results and 25% in discussion (page gives 6 of 23).

## What could not be found

- No study compares immunosuppression with none for survival, in any species.
- No *B. rossi* study reports outcome by glucocorticoid use; CB008 (accepted manuscript says prednisolone was given for secondary IMHA) is local as abstract only and was not cited.
- No evidence on whether immunosuppression delays clearance, causes relapse or a carrier state.
- No primary source for the 88% Coombs-positive figure in *B. rossi*: given "as cited in" R3 (Reyers 1998 abstract does not state it).
- CURATIVE antithrombotic dosing paper: publisher returned 403; the ACVIM treatment statement restates the starting doses and was used instead.
- No South African availability source: `availability` left empty.

## Statements I am least sure of

- Level A for glucocorticoids and azathioprine rests on one small, single-centre trial in a low-impact journal with haematology end points at day 21; its text has duplicated and inconsistent passages (e.g. table numbering). Rated A by design only.
- R10 (*B. gibsoni* worse than primary IMHA) is from the abstract; the HR confidence interval as printed (1.2–2.9 for HR 2.6) is odd.
- "Harmful" for splenectomy rests on guideline advice and indirect evidence (R11, R14, R12), not on a study of splenectomy in babesiosis.

## Decisions for the coordinator

1. Accept the changed definition (ACVIM criteria, not "persists despite treatment").
2. Whether level A should stand for the CB247 trial, or be shown as B given its size and quality. The rules give A for any controlled trial in dogs with babesiosis.
3. The page links to SY01 for transfusion volumes and to SY03 for Evans syndrome / immune thrombocytopenia.

## Files written

- `/webapp/Babesiosis.Web/public/assets/clinical/SY02.json`
- `/clinical/SY02/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md`
- `/clinical/ledger.md` (SY02 row only)
