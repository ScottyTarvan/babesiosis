# TX00 search log

Run 2026-11-12. "Kept" = papers used on the page or read in full to decide.

| Date | Source | Query or file | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | local file | `core/search/clinical_treatment/combined_set.csv`, `syndromes` contains uncomplicated, chronic or relaps | 67 | 14 |
| 2026-11-12 | local file | same file, `include_type` trial, review, experimental or retrospective series, with a named antibabesial drug | 81 | 16 |
| 2026-11-12 | local texts | `core/data/markdown/` CB533, CB507, CB493, CB094, CB040, CB149, CB106, CB042, CB373, CB336 (grep mg/kg, drug names, relapse) | 10 | 9 |
| 2026-11-12 | local abstracts | CB371, CB422, CB361, CB442, CB067, CB382, CB389 | 7 | 5 |
| 2026-11-12 | PubMed | Babesia rossi AND (diminazene OR imidocarb OR "trypan blue") | 9 | 1 |
| 2026-11-12 | PubMed | "Antiprotozoal treatment of canine babesiosis"[Title] | 0 | 0 (found by the next search) |
| 2026-11-12 | PubMed | Babesia gibsoni atovaquone azithromycin dogs | 19 | 9 |
| 2026-11-12 | PubMed | diminazene dogs (toxicity OR neurological OR pharmacokinetics OR "Babesia canis") | 29 | 1 |
| 2026-11-12 | PubMed | imidocarb AND dog AND (adverse OR toxicity OR pharmacokinetics OR atropine OR resistance OR failure) | 28 | 4 |
| 2026-11-12 | PubMed | canine babesiosis South Africa treatment (Jacobson OR Leisewitz OR Lobetti OR Penzhorn) | 31 | 0 new |
| 2026-11-12 | PubMed citation lookup | Jacobson 1996 JSAVA 67:77; Jacobson 2006 Vet Parasitol 138:126; Neer 2002 JVIM 16:309; Miller 2005 JSAVA 76:146 | 4 | 2 |
| 2026-11-12 | PubMed metadata | tafenoquine, Malarone, artesunate, DEM, MCD, B. conradae, buparvaquone resistance, CYTb pyrosequencing | 9 | 7 |
| 2026-11-12 | web (OJVR) | Schoeman 2009 full text (open access) | 1 | 1 |
| 2026-11-12 | PubMed Central | Checa 2017, Lin & Huang 2010, Almendros 2020, Karasová 2022 full texts (read, not stored) | 4 | 4 |
| 2026-11-12 | PubMed Central | Iguchi 2014 (Malarone) | 1 | 0: bot check, abstract has no dose |
| 2026-11-12 | web | Imizol label, imidocarb 6.6 mg/kg, atropine | 10 | 1 (FDA FOI summary NADA 141-071) |
| 2026-11-12 | web | Berenil RTU diminazene South Africa package insert | 17 | 1 (MSD Animal Health South Africa product page) |
| 2026-11-12 | web | ACVIM ehrlichiosis consensus (Wiley full text) | 1 | 0: HTTP 403, dose not verified |
| 2026-11-12 | web | Shiranaga & Inokuma 2018, low-dose diminazene + clindamycin (JJVR 66:221) | 10 | 0: repository unavailable (503), DOI not in Crossref; regimen kept only from a review |
| 2026-11-12 | Crossref | DOIs of Torbica 2013, Schoeman 2009, Miller 2005, Collett 2000, JJVR 2018 | 5 | 4 confirmed |

## Saturation

The last four searches (South African authors, toxicity, imidocarb adverse effects, citation lookups) returned no new treatment and no new diagnostic criterion. Search stopped there.

## Left out on purpose

- Regional trials and case reports from the local set without PubMed or Crossref records, or without a stated dose (Indian, Russian and Ukrainian journals; homeopathy; plasmapheresis; N-acetylcysteine and other adjuncts that do not act on the parasite).
- Prevention and chemoprophylaxis (out of scope).
- Collett 2000 survey (trypan blue use in shocked dogs in 1993): confirmed but not needed once Schoeman 2009 was read.
- Ehrlichia canis treatment doses: the ACVIM consensus could not be read.

## Files read but not stored

Two PDFs (Schoeman 2009 and the FDA FOI summary) were fetched for reading by the web tool into its own cache outside the repository and deleted after reading.
