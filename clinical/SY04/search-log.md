# SY04 search log

| Date | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | `/core/search/clinical_treatment/combined_set.csv` | `syndromes` contains non-regenerative, pancytopenia, haemophag | 24 rows | 9 (CB129, CB251, CB214, CB132, CB106, CB099, CB351, the filgrastim and NAC rescreen rows) |
| 2026-11-12 | `/core/data/terms/*.json` (CB only) | CUIs for pancytopenia, erythrophagocytosis, bone marrow suppression, aplastic anaemia, haemophagocytic lymphohistiocytosis, bone marrow diseases | 53 articles | 6 |
| 2026-11-12 | `/core/articles.jsonl` (streamed) | title or finding matches reticulocyt, regenerat, marrow, pancytopen, haemophag, erythropoie, darbepoetin, colony | 34 | 9 (CB115, CB418, CB538, CB540, CB297, CB337, CB141, CB148; CB306 read, not cited) |
| 2026-11-12 | PubMed | (babesia OR babesiosis) AND dog AND (pancytopenia OR "bone marrow" OR nonregenerative OR "non-regenerative" OR hemophagocytic OR aplastic) | 46 | 3 new (Cloete 2024, Rosa 2014, Yadav 2025); De Tommasi 2014 read, not cited (no B. vogeli-only data) |
| 2026-11-12 | PubMed | (filgrastim OR "granulocyte colony-stimulating factor") AND dogs AND (ehrlichia OR ehrlichiosis OR pancytopenia OR neutropenia) | 54 | 0 (no babesiosis study other than Pothiappan 2020) |
| 2026-11-12 | PubMed | Neer ehrlichial consensus; Weiss hemophagocytic dogs; Mylonakis chronic ehrlichiosis 2004 | 5 | 2 (Weiss 2007, Mylonakis 2004). ACVIM consensus found; full text HTTP 403; not cited |
| 2026-11-12 | Web | ACVIM ehrlichial consensus doxycycline dose | 10 | 1 (Fourie 2015, JSAVA) |
| 2026-11-12 | Crossref and publisher PDF | 10.30954/2277-940x.02.2020.6 (filgrastim) | 1 | 1 (read; the temporary copy was deleted) |
| 2026-11-12 | PubMed | (babesia OR babesiosis) AND dog AND (erythropoietin OR darbepoetin OR filgrastim OR colony-stimulating OR acetylcysteine OR "bone marrow aspirate" OR myelofibrosis) | 8 | 2 new (Khan 2026, Mundassery 2025); the rest already found or out of scope |

**Stop.** The last search found no new treatment and no new diagnostic criterion, only two more trials of a treatment already found (N-acetylcysteine). No source was found for antibiotic cover in neutropenic dogs with babesiosis, or for an immunosuppressive dose for haemophagocytic syndrome in babesiosis.
