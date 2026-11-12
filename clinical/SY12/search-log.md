# SY12 search log

All searches on 2026-11-12.

| # | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 1 | `/core/search/clinical_treatment/combined_set.csv` | `syndromes` contains "pancrea" | 7 rows (6 tagged pancreatitis + CB061) | 0 as treatment evidence (no row tests a pancreatitis treatment); CB061 kept as prognosis; rescreen PMID 31477120 kept as a caution |
| 2 | `/core/data/terms/*.json` | CUI C0030305 (Pancreatitis) or C0001339 (Pancreatitis, Acute) | 41 CB articles | 7 (CB508, CB045, CB106, CB006, CB061, CB119; CB493 read, not cited) |
| 3 | `/core/articles/*.md` | grep "pancrea" | 16 notes | same set as row 2; reviews (CB371, CB389, CB493, CB507, CB533, CB259) give no new data |
| 4 | `/core/data/markdown/` | grep "pancrea" in 20 key texts | 20 | full texts read: CB508, CB045, CB106, CB006, CB119, CB493; abstract: CB061 |
| 5 | PubMed | `(babesiosis OR babesia) AND pancrea* AND (dog OR dogs OR canine)` | 11 | 6 (Möhr 2000, Máthé 2006, Jacobson 2006, Köster 2015, Masuda 2019, Choi 2019); 2 not relevant (Rangelia, felid CDV), 1 case report not used (Piane 2016) |
| 6 | PubMed | `acute pancreatitis[Title] AND dog AND (treatment OR management OR consensus OR review)`, 2015 on | 275 (first 40 screened) | 1 (Angst 2026 TAP pilot) |
| 7 | PubMed | `pancreatitis[Title] AND dog[Title] AND (consensus OR fuzapladib OR maropitant OR enteral OR antimicrobial OR fluid OR management OR treatment)[Title]` | 51 (first 21 screened) | 6 (Lim 2024, Cridge 2024 nutrition, Steiner 2023 fuzapladib, Okanishi 2019, Harris 2017, Mansfield 2011); Mansfield & Beths 2015 abstract read, not cited |
| 8 | PubMed | `Cridge H[Author] AND pancreatitis` | 31 (30 screened) | 1 (Cridge 2021 diagnosis review) |
| 9 | PubMed | `(pancreatic lipase OR cPLI OR Spec cPL OR DGGR) AND (hemolysis OR haemolysis OR interference) AND dogs` | 8 | 3 (Steiner 2017, Goodband 2018, Lim 2020) |
| 10 | PubMed citation lookup | Mansfield 2011 JVIM 25:419; Marks 2018 JVIM 32:1823 | 2 | 2 |
| 11 | PubMed | `metoclopramide AND dogs AND (constant rate infusion OR mg/kg/day) AND ... AND free full text` | 2 | 0 (no dose source for pancreatitis) |
| 12 | Web | "Management of acute-onset pancreatitis in dogs: a Narrative Review" JAVMA 2024 | 10 | 0 extra; JAVMA full text and RVC repository copy returned HTTP 403 (abstract used) |
| 13 | Web | Vet Times 2026 "Acute pancreatitis problems in dogs: what's new, part two" | 1 | 0 (no doses stated) |
| 14 | Web | Cerenia maropitant injectable dose package insert | 10 | 1 (UK VMD SPC; EMA PDF returned HTTP 429) |
| 15 | Publisher | JSAVA (AOSIS) Möhr 2000 article page and open PDF | 1 | 1 (full text read) |
| 16 | PMC | Full texts: PMC10658511 (fuzapladib), PMC8692219 (diagnosis review), PMC6271318 (gastroprotectant consensus; consensus boxes read on the PMC web page), PMC13700751 (TAP pilot) | 4 | 4 |

## Stop rule

Searches 7 to 14 gave no new treatment and no new diagnostic criterion beyond those on the page. No study of any pancreatitis treatment in dogs with babesiosis was found in the local review, in PubMed (search 5) or in the reviews read. Search stopped.

## Not reached

- Lim et al. 2024 JAVMA review: abstract only (HTTP 403).
- Mansfield & Beths 2015 JSAP critical appraisal: abstract only; a third-party PDF copy was not used.
- BSAVA formulary: not accessible; no metoclopramide or buprenorphine dose taken.
- Low-quality B. gibsoni series with amylase/lipase only (CB260 India, CB224 Korea): read, left out.
