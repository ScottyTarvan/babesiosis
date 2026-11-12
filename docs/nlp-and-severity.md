# NLP concepts, categories and marker-severity associations

Paths are relative to `core/`. Counts as of 2026-10-28.

## NLP concepts (`data/syndromes/`)

From a scispaCy run (UMLS linker, threshold 0.85, NegEx); settings in `run.json`. This folder is not in every checkout.

**Do not load `mentions.jsonl` whole** (140 MB). Stream it, or grep it for an `id` or `cui`.

| File | Rows | What it holds |
|---|---|---|
| `mentions.jsonl` | 239,733 | One row per mention: `id`, `document`, `section`, `block`, `sentence`, `mention`, `abbreviation_of`, `label`, `disorder`, `negated`, `cui`, `concept`, `score`, `semantic_types[]` |
| `article_concepts.csv` | 20,745 | Article × concept: `id`, `cui`, `concept`, `semantic_types`, `mentions`, `in_results_or_case`, `sections`, `mention_texts` |
| `concept_summary.csv` | 4,243 | Per concept: `cui`, `concept`, `articles`, `articles_full_text`, `articles_abstract_only`, `articles_in_results_or_case`, `mentions` |
| `category_map.csv` | 9,764 | Concept → category (`-` = not mapped). Edit by hand; manual rows are kept on rescoring |
| `article_categories.csv` | 481 | Per article: `aim`, `nlp_primary`, `nlp_secondary`, `nlp_mentioned`, `confidence`, `agent_primary`, `agent_secondary`, `agree_primary`, `primary_evidence`, `score_<CAT>` (studied), `mscore_<CAT>` (mentioned only) |
| `category_comparison.md` | – | Agreement of the NLP categories with the agents' categories |
| `article_terms.csv`, `.jsonl` | 481 | Per article: categories, summary, one-sentence finding and every term with its mention count, category and studied or mentioned status |
| `review/` | – | **Retired** (2026-10-28). Not used by any step |

<a id="categories"></a>
## Categories

**Categories come from the NLP, with no human review.** `build_outputs.py` copies `nlp_primary` and `nlp_secondary` from `article_categories.csv` into `articles.jsonl` (`primary_category`, `secondary_tags`), `index.md` and the notes. The scoring algorithm is in [pipeline-spec.md](pipeline-spec.md), stage S13.

- Of the 444 `CB` articles, 428 have an NLP category (`category_confidence` high 284, low 144). For the other 16 the extraction agents' label is used, and `category_source` says so.
- Primary categories: ERY 96, INF 91, SEV 59, MET 50, COA 40, REN 40, OXO 21, CAR 18, END 14, NEU 8, PUL 7.
- The agents' labels are kept in `agent_primary_category` and `agent_secondary_tags`. They agree with the NLP on 238 of 444 articles (54%).
- The NLP has known mislinks (for example "MPO" linked to *Myeloperoxidase Deficiency*). Treat the categories as automatic labels.

Category code definitions are in [ids-and-codes.md](ids-and-codes.md#category-codes).

## Per-article terms and the dashboard display map (`data/terms/`)

- `<ID>.json` (481 files, written by `extract_terms.py`): one entry per UMLS Disorders-group concept (T033 "Finding" excluded) with `mentions`, `mentions_affirmed`, `mentions_negated`, mentions per `sections`, surface `forms` and `best_score`. `source_format` says whether the terms come from the abstract (`abstract`) or the full text (`jats_xml`, `pdf`).
- `term_display.csv`: the curated display layer for the dashboard card "Clinical syndromes and signs". Columns: `cui`, `concept`, `articles` (CB articles with an affirmed mention), `action` (`show` / `hide`), `display_name` (CUIs with the same name are counted as one term; blank = `concept`), `note`. `build_term_display.py` refreshes `concept` and `articles`; edit the other columns by hand.

The console loader (`TermLoader`) reads both into `dbo.term` and `dbo.article_term`. A term is **studied** in an article when it has an affirmed mention in `title`, `results`, `case` or `conclusion`, or in `abstract` when the article is abstract-only. Otherwise it is mentioned only. Terms with only negated mentions are not loaded. The linking is automatic and not reviewed by a person.

## Marker-severity associations (`data/severity/`)

Which markers were tested against clinical severity or outcome, and with what result. Pilot of 10 articles (2026-10-26); the full shortlist is not extracted.

| File | What it holds |
|---|---|
| `shortlist.csv` | Candidate articles: `tier` (A–C), `rank_score`, `tested_sentences`, `outcome_sentences`, `source_format`, `aim`, `species`, `cohort`, `marker_hints` |
| `candidate_sentences.jsonl` | Severity or outcome sentences per article: `id`, `section`, `tested`, `sentence`, `marker_hints[]` |
| `marker_map.csv` | Alias → canonical `marker` and `marker_class`. Rows with a `pattern` define the canonical markers. Edit by hand |
| `association_schema.json`, `EXTRACTION_GUIDE.md` | The row definition and the extraction instructions |
| `extractions/<ID>.json` | Per-article extraction: `severity_definitions[]` and `associations[]` with verbatim quotes |
| `associations.csv` | One row per marker × severity definition × subgroup × analysis: `outcome_class`, `marker`, `direction`, `significant`, statistics, and checks (`quote_check`, `numbers_missing`, `errors`, `map_status`) |
| `extraction_report.md` | Check results, marker mappings to check, severity definitions, evidence preview |

Use only rows with `quote_check` = `exact` or `near`. Count articles, not rows, and merge linked cohorts (`cohort`) before you count independent evidence.
