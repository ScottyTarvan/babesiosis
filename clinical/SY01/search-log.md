# SY01 search log

Run 2026-11-12. Hits = records returned; kept = records used on the page.

| Date | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | `/core/search/clinical_treatment/combined_set.csv` | `syndromes` contains "haemolytic anaemia" | 221 | 52 screened by treatment keyword (transfusion, oxyglobin, iron, haematinic, fluids); 8 used (CB040, CB094, CB102, CB143, CB221, CB315, CB368, CB418) |
| 2026-11-12 | `/core/search/synthesis/ERY.md` | read whole | 1 | pointers only (CB129, CB538, CB238, CB516) |
| 2026-11-12 | `/core/data/markdown/CB*.md` | grep "transfus", "mL/kg", "severe anaemia" with thresholds, "haemoglobinuri", "iron", "haematinic", "DEA 1" | 81 files mention transfusion | CB040, CB119, CB129, CB315, CB418, CB493, CB094, CB102, CB221 read in the relevant sections |
| 2026-11-12 | `/core/articles/*.md` notes | CB368, CB418, CB371, CB129, CB538, CB516, CB238 | 7 | 6 (CB371 abstract only locally; CB516 not used: note gives no haematocrit result) |
| 2026-11-12 | PubMed | (babesiosis OR babesia) AND dog AND (transfusion OR anaemia OR anemia OR haematocrit) | 327 (60 reviewed) | Jacobson & Swan 1995, Irwin 2010 (not used) |
| 2026-11-12 | PubMed | (Jacobson LS OR Leisewitz AL OR Schoeman JP OR Lobetti RG OR Reyers F)[Author] AND babesiosis | 79 | Jacobson 2006, Böhm 2006; Koma 2005, Spotswood 2005/2006 read, not used |
| 2026-11-12 | PubMed | Association of Veterinary Hematology and Transfusion Medicine consensus statement | 10 | TRACS parts 1-3 found; paywalled (Europe PMC: not open access); not cited |
| 2026-11-12 | PubMed | dog/canine packed red blood cell transfusion review, free full text | 2 | 0 (Klein 2017 kept later for iron caution) |
| 2026-11-12 | PubMed | dogs transfusion volume formula PCV increase mL/kg | 0 | 0 |
| 2026-11-12 | PubMed | babesiosis dog (fluid therapy OR crystalloid OR blood volume OR hypervolaemia OR pulmonary oedema) anaemia | 5 | 0 new (normovolaemic anaemia models read, not used) |
| 2026-11-12 | PubMed citation lookup | Nel 2004 JVIM 18:471; Keller 2004 JVIM 18:265; Collett 2000 JSAVA 71; Reyers 1998 ATMP 92:503 | 4 | 4 |
| 2026-11-12 | Web search | Merck Veterinary Manual blood transfusion dogs packed red cells mL/kg crossmatch DEA 1 | 10 | Merck Vet Manual "Blood transfusions in animals"; Herter 2022 (via PMC link) |
| 2026-11-12 | Web search | "Supportive treatment of canine babesiosis" Jacobson Swan 1995 pdf | 10 | 0 full text found; Collett 2000 survey page (JSAVA) read |
| 2026-11-12 | Web (Wiley) | TRACS part 2 full text | 1 | 403, not read |
| 2026-11-12 | Europe PMC REST | verification of 19 PMIDs; abstract of Bumby 2024 | 19 | 19 confirmed |
| 2026-11-12 | Crossref REST | verification of 6 DOIs without PMID or for title check | 6 | 6 confirmed |

## Saturation

The last searches (fluid therapy, volume formula, free-text transfusion reviews) returned no new treatment and no new diagnostic criterion. The candidate list of the page file (packed cells, whole blood, HBOC, oxygen, fluids, haematinics) was covered; compatibility testing and donor screening were added. No further babesiosis-specific treatment for the anaemia was found.

## Not used

- Rescreen-only transfusion case reports (India, Brazil, Nigeria) and Ukrainian reports on cryopreserved red cells: single cases or abstracts with no dose per kg or outcome beyond the cited studies.
- AVHTM TRACS 2021 (Davidow et al., Odunayo et al.): abstract only, no specific recommendation readable; guidance cited from the Merck Veterinary Manual instead.
- Human malaria transfusion thresholds (WHO): not searched in this run; recorded as a gap.
