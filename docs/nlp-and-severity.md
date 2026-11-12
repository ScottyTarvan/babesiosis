# NLP concepts, categories and marker-severity associations

Paths are relative to `core/`. Counts were taken on 2026-10-28; re-count before you quote them as current.

## NLP concepts and categories (`data/syndromes/`)

These files come from a scispaCy run (UMLS linker, threshold 0.85, NegEx). `run.json` has the run settings and per-document mention counts. Only disease mentions and Disorders-group UMLS concepts are kept.

**Do not load `mentions.jsonl` whole** (140 MB). Stream it, or grep it for an `id` or `cui`.

| File | Format | Rows | What it holds |
|---|---|---|---|
| `mentions.jsonl` | JSONL | 239,733 | One row per mention: `id`, `document`, `section`, `block`, `sentence`, `mention`, `abbreviation_of`, `label`, `disorder`, `negated`, `cui`, `concept`, `score`, `semantic_types[]` |
| `article_concepts.csv` | CSV | 20,745 | One row per article × concept: `id`, `cui`, `concept`, `semantic_types`, `mentions`, `in_results_or_case`, `sections`, `mention_texts` |
| `concept_summary.csv` | CSV | 4,243 | One row per concept: `cui`, `concept`, `articles`, `articles_full_text`, `articles_abstract_only`, `articles_in_results_or_case`, `mentions` |
| `category_map.csv` | CSV | 9,764 | Concept → category (`-` means not mapped). Can be edited by hand; manual rows are kept on rescoring. |
| `article_categories.csv` | CSV | 481 | Per article: `aim`, `nlp_primary`, `nlp_secondary`, `nlp_mentioned`, `confidence`, `agent_primary`, `agent_secondary`, `agree_primary`, `primary_evidence`, `score_<CAT>` (studied) and `mscore_<CAT>` (mentioned only) |
| `category_comparison.md` | Markdown | – | How well the NLP categories agree with the agents' categories |
| `article_terms.csv`, `article_terms.jsonl` | CSV, JSONL | 481 | Per article: categories, summary (from the note), one-sentence finding and every extracted term, with its mention count, mapped category (`-` = none), and whether it was studied or only mentioned. Written by `export_article_terms.py` |
| `review/` | – | – | **Retired.** The human category review (queue, review page and 6 decisions from 2026-10-26) was dropped on 2026-10-28. The files are kept for the record and are not used by any step. The study-aim definitions are in `categorise_articles.py` (`AIMS`) |

<a id="categories"></a>
### Categories

**Categories come from the NLP, with no human review** (since 2026-10-28, for every round). `build_outputs.py` copies `nlp_primary` and `nlp_secondary` from `article_categories.csv` into `articles.jsonl` (`primary_category`, `secondary_tags`), `index.md` and the notes. Where the NLP finds no category (16 of 444 `CB` articles: 4 from rounds 1–3 and 12 from round 4), the extraction agents' label is used and `category_source` says so. Of the 428 NLP rows, 284 have `category_confidence` high and 144 low. The primary categories of the 444 CB articles are ERY 96, INF 91, SEV 59, MET 50, COA 40, REN 40, OXO 21, CAR 18, END 14, NEU 8 and PUL 7. The agents' labels are kept in `agent_primary_category` and `agent_secondary_tags`. They agree with the NLP on 238 of 444 articles (54%). Neither is checked by a person, and the NLP has known mislinks (for example "MPO" linked to *Myeloperoxidase Deficiency*), so treat the categories as automatic labels. `research-map.md` and `search/synthesis/` were rewritten on 2026-10-28 from the NLP categories, for 2006–2026.

Category code definitions are in [ids-and-codes.md](ids-and-codes.md#category-codes).

## Per-article terms and the dashboard display map (`data/terms/`)

`extract_terms.py` writes `data/terms/<ID>.json` for every article (481 files, run 2026-10-30): one entry per UMLS Disorders-group concept (T033 "Finding" excluded) with `mentions`, `mentions_affirmed`, `mentions_negated`, mentions per `sections`, surface `forms` and `best_score`. The file's `source_format` says whether the terms come from the abstract alone (`abstract`) or the full text (`jats_xml`, `pdf`).

`term_display.csv` is the curated display layer for the Literature Review dashboard's "Clinical syndromes and signs" card. Columns: `cui`, `concept`, `articles` (CB articles with an affirmed mention), `action` (`show` / `hide`), `display_name` (several CUIs with the same name are counted as one term; blank = `concept`) and `note` (why). `build_term_display.py` creates it and refreshes `concept` and `articles` on a re-run; `action`, `display_name` and `note` are kept, so edit them by hand. The seed (2026-11-04) hides 13 generic or mislinked concepts (Babesiosis, Disease, Communicable Diseases, Infection by Babesia canis, Parasitic Diseases, Tick-Borne Diseases, Pathogenesis, Complication, Signs and Symptoms, disease transmission, Tissue damage, Malaria, Infections of musculoskeletal system), merges Anemia and Anemia, Hemolytic as "Anaemia (incl. haemolytic)", and relabels Mental Depression as "Depression (clinical sign)". Kidney Failure, Acute and Azotemia stay separate.

The console loader (`console/Babesiosis.Console`, `TermLoader`) reads both into `dbo.term` and `dbo.article_term`. A term is **studied** in an article when it has an affirmed mention in `title`, `results`, `case` or `conclusion`, or in `abstract` when the article is abstract-only; otherwise it is mentioned only. Terms with only negated mentions are not loaded. Linking is automatic (scispaCy, threshold 0.85) and not reviewed by a person: the map removes the known problems, not all of them.

## Marker-severity associations (`data/severity/`)

Which markers and parameters were tested against clinical severity or outcome, and with what result. Built in a pilot on 2026-10-26 (10 articles). Not yet extracted for the whole shortlist.

| File | Format | What it holds |
|---|---|---|
| `shortlist.csv` | CSV | Candidate articles: `tier` (A–C), `rank_score`, `tested_sentences`, `outcome_sentences`, `source_format`, `aim`, `species`, `cohort`, `marker_hints` |
| `candidate_sentences.jsonl` | JSONL | Severity or outcome sentences per article: `id`, `section`, `tested`, `sentence`, `marker_hints[]` |
| `marker_map.csv` | CSV | Alias → canonical `marker` and `marker_class`. Rows with a `pattern` define the canonical markers. Edit by hand; manual and extracted rows are kept when the map is regenerated. |
| `association_schema.json`, `EXTRACTION_GUIDE.md` | JSON Schema, Markdown | The row definition and the extraction instructions |
| `extractions/<ID>.json` | JSON | Per-article extraction: `severity_definitions[]` and `associations[]` with verbatim quotes |
| `associations.csv` | CSV | One row per marker × severity definition × subgroup × analysis, with `outcome_class`, normalised `marker`, `direction`, `significant`, statistics, and checks (`quote_check`, `numbers_missing`, `errors`, `map_status`) |
| `extraction_report.md` | Markdown | Check results, marker mappings to check, severity definitions and an evidence preview (marker × outcome class) |

Use only rows with `quote_check` = `exact` or `near` as verified. Count articles, not rows, and merge linked cohorts (`cohort`) before you count independent evidence.
