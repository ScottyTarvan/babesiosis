# SY13 search log

Run 2026-11-12. One row for each search. "Kept" = sources used on the page.

| Date | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | `/core/search/clinical_treatment/combined_set.csv` | `syndromes` or text containing gastro, melaena, vomit, diarrh | 8 rows (all `rescreen`, case reports or small series; none tests a gut treatment) | 0 |
| 2026-11-12 | `/core/data/terms/CB*.json` | affirmed mentions of Vomiting, Diarrhea, Melena, Gastroenteritis, Hematochezia | 69 CB articles | 13 (frequency series, reviews, necropsy) |
| 2026-11-12 | `/core/data/markdown/CB*.md` | haemorrhagic diarrhoea/gastroenteritis/enteritis, melaena, haematochezia, haematemesis, gastrointestinal bleeding, "gut form" | 24 files | CB493, CB106, CB120, CB310, CB304, CB325 (others: single cases or passing mentions) |
| 2026-11-12 | `/core/data/markdown/CB*.md` | parvovirus | 17 files | 0 (CB268 dropped: DOI does not resolve; CB222 compares acute phase proteins only) |
| 2026-11-12 | Local full texts | vomit, diarrh, melena in CB508, CB106, CB134, CB126, CB294, CB080, CB224 | 7 | 6 (CB294 not used: species unspecified) |
| 2026-11-12 | PubMed | (babesiosis OR Babesia) AND dog AND (parvovirus OR gastroenteritis OR melena OR haematochezia OR hemorrhagic diarrhea) | 12 | 0 (surveillance, wildlife, Rangelia) |
| 2026-11-12 | PubMed | Babesia/babesiosis [tiab] AND parvovirus/parvoviral [tiab] AND dog | 16 | 0 (no clinical co-infection report) |
| 2026-11-12 | PubMed | Babesia rossi AND (vomiting OR diarrhoea OR gastrointestinal) AND dogs | 1 | 1 (Keller 2004) |
| 2026-11-12 | PubMed | (babesiosis OR Babesia) AND dogs AND (maropitant OR ondansetron OR metoclopramide OR antiemetic OR omeprazole OR pantoprazole OR sucralfate) | 0 | 0 |
| 2026-11-12 | PubMed | imidocarb dog atropine adverse effects cholinergic | 0 | 0 |
| 2026-11-12 | PubMed | Jacobson LS [au] AND babesiosis AND complicated | 17 | 1 (Jacobson 2006) |
| 2026-11-12 | PubMed | ACVIM gastroprotectant consensus (by citation: J Vet Intern Med 2018;32:1823) | 1 | 1 (Marks 2018, PMC full text) |
| 2026-11-12 | PubMed | acute hemorrhagic diarrhea syndrome antibiotic randomized OR ENOVAT canine acute diarrhoea | 3 | 2 (Scahill 2024; Unterer 2011 by citation). ENOVAT guideline itself paywalled, not cited |
| 2026-11-12 | PubMed | Mohr AJ [au] parvoviral enteritis enteral nutrition | 1 | 1 |
| 2026-11-12 | PubMed | canine parvovirus enteritis review Mylonakis | 1 | 1 (PMC full text) |
| 2026-11-12 | Web | parvovirus babesiosis concurrent infection dog puppy case report South Africa | 10 | 0 (no parvovirus plus Babesia report) |
| 2026-11-12 | Web | imidocarb package insert atropine dose | 10 | 1 (Clinician's Brief summary) |
| 2026-11-12 | Web | Cerenia maropitant injectable label | 10 | 1 (UK VMD product information; US FDA FOI summary read to confirm dose, not cited) |
| 2026-11-12 | Crossref API | every DOI on the page | 23 | 21 confirmed, 2 cited by URL (no DOI) |

## Stop rule

Searches for each candidate treatment with babesiosis returned no paper that tested a gut treatment. The last four searches (PubMed treatment terms, PubMed co-infection, two web searches) returned no new treatment and no new diagnostic criterion. Search stopped there.

## Not reached

- ENOVAT guideline (Jessen et al. 2024, Vet J 307:106208): paywalled; only the abstract was read, which gives no recommendations in detail. Not cited.
- ACVIM consensus boxes: the PMC full text had the consensus-opinion boxes stripped; the body text was read.
- PMC web pages are behind a bot check; the PubMed connector full-text tool was used instead.
- CB268 (Indian kennel outbreak, puppies with haemorrhagic enteritis negative for enteric viruses): DOI 404 at Crossref and doi.org; publisher page needs login. Dropped.
