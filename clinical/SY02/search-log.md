# SY02 search log

Run 2026-11-12. "Kept" = cited on the page.

| Date | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | `core/search/clinical_treatment/combined_set.csv` | `syndromes` contains `imha` or `evans` | 27 | 6 (CB247, CB153, CB264, CB047, CB094, and CB106 found later) |
| 2026-11-12 | `core/data/terms/*.json` | CUI C0002880 (Autoimmune hemolytic anemia), affirmed | 36 articles | used to find papers; 4 kept (CB094, CB153, CB247, CB248) |
| 2026-11-12 | `core/data/markdown/CB*.md` | grep `Coombs|antiglobulin` | 19 articles | 6 kept (CB106, CB148, CB247, CB248, CB107 used to trace sources only, CB259 read not kept) |
| 2026-11-12 | `core/data/markdown/CB*.md` | grep `in-saline|autoagglutinat|ISA positive` | 13 articles | 2 kept (CB040, CB053) |
| 2026-11-12 | local notes / full texts | CB040, CB053, CB094, CB106, CB148, CB153, CB247, CB248, CB250, CB264, CB047, CB493, CB336, CB008 | 14 read | 11 kept; CB250 (no DOI/PMID), CB493, CB336, CB008 (abstract only; no dose) not kept |
| 2026-11-12 | PubMed | ACVIM consensus immune-mediated hemolytic anemia dogs | 4 | 3 (Garden 2019, Swann 2019, Idalan 2021) |
| 2026-11-12 | PubMed | Babesia AND dog AND (Coombs OR antiglobulin OR "saline agglutination" OR spherocytes) | 9 | 2 (Farwell 1982, Eisenecker 2026 = CB148) |
| 2026-11-12 | PubMed | Babesia rossi AND (immune-mediated OR agglutination OR Coombs OR glucocorticoid ...) | 10 | 1 (Seejarim 2023 = CB115); Reyers 1998 checked, figure only via CB040 |
| 2026-11-12 | PubMed | Babesia gibsoni dogs (prednisolone OR glucocorticoid OR splenectomy OR immunosuppressive) relapse | 3 | 0 |
| 2026-11-12 | PubMed | Carli Solano-Gallego erythrocyte binding IgM IgG flow cytometry | 1 | 1 |
| 2026-11-12 | PubMed | warm autoimmune hemolytic anemia after Babesia microti asplenic | 1 | 1 (Woolley 2017, human comparator) |
| 2026-11-12 | PubMed | CURATIVE defining antithrombotic protocols dogs cats | 3 | 0 (Wiley full text returned 403; doses taken from ACVIM treatment statement instead) |
| 2026-11-12 | Europe PMC full text | PMC6524099 (ACVIM treatment), PMC6430921 (ACVIM diagnosis) | 2 | 2 |
| 2026-11-12 | Crossref | DOIs of CB247, CB248, CB264, CB047 | 4 | 4 |

## Stopping point

After the ACVIM statements and the species searches, new searches gave no new treatment and no new diagnostic criterion for babesiosis-associated IMHA. The only babesiosis treatment study is CB247 (with CB248, same cohort CH17). Everything else on immunosuppressants, IVIG and antithrombotics is general canine IMHA guidance (level D).

## Not reached or left out

- CURATIVE domain 3 (doi 10.1111/vec.12795): publisher blocked (403); not cited.
- CB008 (B. rossi, prednisolone for secondary IMHA in the accepted manuscript): only the abstract is local; not cited.
- CB250, CB262, CB252, CB272, CB283, CB096, CB216 case reports: no DOI/PMID, abstract only, or outside scope (immune thrombocytopenia, vasculitis); not cited.
- CB198 rescreen paper (secondary IMHA, Chennai, 13 B. gibsoni dogs): not opened; abstract tag only.
