---
title: "Canine babesiosis pathophysiology review: article acquisition and processing pipeline"
doc_type: technical_specification
status: work_to_date
review_window: { start: 2006-10-23, end: 2026-10-23 }
search_runs:
  - { rounds: [r1, r2, r3], date: 2026-10-23, window: [2016-10-23, 2026-10-23] }
  - { rounds: [r4], date: 2026-10-27, window: [2006-10-23, 2016-10-22] }
counts_taken: 2026-11-04
counts_source: structured files in core/
companion: pipeline-spec.html
paths: relative to core/ unless stated
---

# Canine babesiosis pathophysiology review: article acquisition and processing pipeline

## Reading notes for agents

- **Paths:** all paths are relative to `core/` unless stated.
- **Counts:** taken on 2026-11-04 from the structured files. Where a count could not be checked, the text says so.
- **Source of truth:** structured files (`articles.jsonl`, `datasets.jsonl`, `cohorts.json`, `ids.json`). Do not count or filter from the rendered reports (`index.md`, `datasets.md`, `research-map.md`, `search-log.md`).
- **Stage IDs:** S1–S16 are in run order. Each stage is tagged `script` (deterministic Python), `agent` (LLM agents, not deterministic) or both.
- **ID prefixes:** `CB` = included canine article, `HU` = human comparator, `BG` = background paper. Cohort IDs are `CH01`–`CH38`.

## Contents

- [0. Scope and status](#0-scope-and-status)
- [Pipeline overview](#pipeline-overview)
- [S1. Database search](#s1-database-search)
- [S2. Supplementary discovery](#s2-supplementary-discovery)
- [S3. Merge and deduplication](#s3-merge-and-deduplication)
- [S4. Title/abstract screening](#s4-titleabstract-screening)
- [S5. Stable IDs and extraction packets](#s5-stable-ids-and-extraction-packets)
- [S6. Full-text retrieval](#s6-full-text-retrieval)
- [S7. Markdown conversion](#s7-markdown-conversion)
- [S8. Translation](#s8-translation)
- [S9. Extraction, appraisal and retirement](#s9-extraction-appraisal-and-retirement)
- [S10. Cohort linkage](#s10-cohort-linkage)
- [S11. Dataset discovery, download and assessment](#s11-dataset-discovery-download-and-assessment)
- [S12. NLP concept extraction](#s12-nlp-concept-extraction)
- [S13. Article categorisation](#s13-article-categorisation)
- [S14. Marker–severity associations](#s14-markerseverity-associations)
- [S15. Synthesis and reports](#s15-synthesis-and-reports)
- [S16. Database load and semantic search](#s16-database-load-and-semantic-search)
- [Data products](#data-products)
- [Limitations and open items](#limitations-and-open-items)

---

## 0. Scope and status

The work is a **rapid scoping review** of the pathophysiology of canine babesiosis: the mechanisms that link *Babesia* infection to complications, severity and outcome in the dog. An article is eligible when it reports **host-side data in dogs infected with *Babesia***.

The review is not an exhaustive systematic review. Screening and extraction were done by LLM agents against written criteria, with a second-screener check. There was no duplicate human screening and no formal risk-of-bias assessment.

The window was searched in two parts: rounds 1–3 cover 2016-10-23 to 2026-10-23, and round 4 covers 2006-10-23 to 2016-10-22. All four rounds are complete: searched, screened, extracted, cohort-linked, mapped to datasets, run through the NLP and synthesised.

### Key figures

| Metric | Value |
|---|---:|
| Candidate records screened (4 rounds) | 3,028 |
| Passed to extraction | 540 |
| Canine articles included (CB) | 444 |
| Supporting papers | 37 (27 HU, 10 BG) |
| Full texts retrieved and converted (all 481 live articles) | 251 |
| Full texts retrieved for CB articles | 230 of 444 (52%) |
| Dataset records | 57 |
| Dataset files downloaded | 92 |
| Shared-cohort groups | 38 |
| Pathophysiology categories | 11 |

### Category codes

| Code | Category |
|---|---|
| `ERY` | Erythrocyte injury, haemolysis, anaemia, immune-mediated processes |
| `INF` | Inflammation, innate and adaptive immunity, immunopathology |
| `END` | Endothelium, microcirculation, perfusion, tissue hypoxia |
| `COA` | Coagulation, platelets, immunothrombosis, DIC |
| `REN` | Renal injury and renal function |
| `PUL` | Pulmonary injury and gas exchange |
| `CAR` | Cardiac injury and haemodynamics |
| `MET` | Hepatic, metabolic, endocrine and acid–base disturbances |
| `OXO` | Oxidative stress, host–parasite interaction, omics, virulence |
| `SEV` | Multisystem clinical phenotype, severity and outcome |
| `NEU` | Neurological and cerebral disease |

---

## Pipeline overview

Sixteen stages, in run order. Script stages are deterministic Python (standard library, except the PDF converter and the NLP). Agent stages were done by LLM agents run as orchestrated workflows, and they are not deterministic.

| Stage | Name | Type | Summary |
|---|---|---|---|
| S1 | Database search | script | PubMed, Europe PMC |
| S2 | Supplementary discovery | script | Citations, Crossref, OpenAlex |
| S3 | Merge and dedupe | script | DOI → PMID → title |
| S4 | Screening | agent | 3-tier agents, 40-record batches |
| S5 | IDs and packets | script | Append-only registry |
| S6 | Full-text retrieval | script | 3 tiers, type and title checks |
| S7 | Markdown conversion | script | JATS, PDF, abstract |
| S8 | Translation | agent + script | Number and length checks |
| S9 | Extraction | agent + script | 44-field record and note |
| S10 | Cohort linkage | agent | Same dogs, CH01–CH38 |
| S11 | Datasets | script + agent | Search, download, assess |
| S12 | NLP concepts | script | scispaCy and UMLS |
| S13 | Categorisation | script | Weighted concept scores |
| S14 | Severity associations | script + agent | Shortlist and pilot |
| S15 | Synthesis and reports | agent + script | Research map |
| S16 | Database load | script | SQL Server and embeddings |

### Record funnel (all rounds)

| Step | Records |
|---|---:|
| Candidates screened | 3,028 |
| Include or uncertain at screening | 560 |
| Passed to extraction (less duplicates) | 540 |
| Included as canine evidence (CB) | 444 |
| CB articles with full text retrieved | 230 |

Of the 540: 444 included, 2 merged as duplicates, 33 excluded on full text or record, 61 unresolved. Full text: 230 of the 444 CB articles (52%); 251 of all 481 live articles, including HU and BG.

---

## S1. Database search

**Type:** script

Documented queries against PubMed (E-utilities) and Europe PMC (REST). Full PubMed records, with abstracts, are fetched for every hit.

| Item | Value |
|---|---|
| Script | `scripts/search.py --start --end [--round rN]` |
| Outputs | `search/queries.jsonl`, `hits.jsonl` (4,159 query→PMID rows), `candidates.jsonl`; round 4 writes to `search/r4/` |
| Throttle | ≤ 3 requests/s to NCBI (no API key), with Europe PMC and OpenAlex rate limits respected |

### Queries

| ID | Source | Query (summary) | Hits r1–3 | Hits r4 |
|---|---|---|---:|---:|
| `PM1_broad` | PubMed | Babesia/babesiosis/piroplasm terms (MeSH and tiab) AND dog terms (MeSH and tiab) | 1,068 | 768 |
| `PM2_species` | PubMed | 17 named canine *Babesia* species and synonyms in tiab (*B. rossi*, *B. vogeli*, *B. gibsoni*, *B. vulpes*, *Theileria annae*, …) | 753 | 607 |
| `PM3_mechanism` | PubMed | PM1 AND about 70 mechanism, organ, omics and outcome terms | 699 | 481 |
| `PM4_review` | PubMed | PM1 AND (`Review[pt]` OR `review[ti]`) | 57 | 48 |
| `EP1_broad` | Europe PMC | TITLE_ABS/KW Babesia terms AND dog terms, `FIRST_PDATE` in window | 976 | 591 |
| `EP2_species` | Europe PMC | TITLE_ABS named species, `FIRST_PDATE` in window | 606 | 432 |
| `OA1`/`OA2` | OpenAlex | Relevance search `babesia dog`, `canine babesiosis` | HTTP 401 (key now required); replaced in S2 | — |

PM1 (exact string):

```text
(Babesia[MeSH Terms] OR Babesiosis[MeSH Terms] OR babesia*[tiab] OR babesiosis[tiab] OR babesioses[tiab]
 OR babesiose*[tiab] OR piroplasm*[tiab])
AND (Dogs[MeSH Terms] OR dog[tiab] OR dogs[tiab] OR canine[tiab] OR canines[tiab] OR canis[tiab]
 OR puppy[tiab] OR puppies[tiab])
```

### Date filter

- PubMed queries are run with a padded publication-date range (`datetype=pdat`, 2015/01/01–2027/12/31 for r1–3; 2005/01/01–2017/12/31 for r4), then filtered on the computed **first publication date**.
- **First publication date** by source:
  - PubMed: the earlier of the electronic (online) and issue dates.
  - Europe PMC: `FIRST_PDATE`.
  - Crossref: the earliest of published-online, print and issued.
  - OpenAlex: `publication_date`.
- Any difference between the online and issue dates is kept per article in `date_note`.

### Sources not searched

CAB Abstracts, Web of Science and Scopus (subscription only), Google Scholar (no API), Harvard Dataverse (HTTP 403). The OpenAlex relevance search was replaced by the keyless `title_and_abstract.search` filter.

---

## S2. Supplementary discovery

**Type:** script

Three routes for records that the curated indexes miss, mainly regional veterinary journals.

### S2.1 Citation searching

| Item | Value |
|---|---|
| Script | `scripts/citations.py` (Europe PMC references and citations API) |
| Seeds | r1–3: the seed review (BG001) and all 121 round-1 inclusions. r4: `--registry-seeds`, every non-retired article in `articles.jsonl` that has a PMID |
| Keep rule | Not seen before, first publication date in the window, and Babesia/babesiosis/piroplasm in the title (or the abstract, for records with a PMID). Reference-list entries with no PMID are kept when the title names Babesia and the year is in the window, then resolved by a Crossref title search |
| Yield | r1–3: 5,299 linked records → 181 kept. r4: 8,217 linked records → 211 kept |

### S2.2 Crossref

| Item | Value |
|---|---|
| Script | `scripts/crossref_search.py` |
| Queries | 8 `query.bibliographic` strings: `canine babesiosis`, `babesia dogs`, `Babesia canis`, `Babesia rossi`, `Babesia gibsoni`, `Babesia vogeli`, `Babesia vulpes`, `babesiosis dogs pathogenesis`; with `type:journal-article` and the window dates. Only the first 1,000 relevance-ranked rows per query are read |
| Keep rule | The **title** contains a Babesia term and a canine term (or a canine Babesia species), and the record is not in the earlier candidate sets. Records whose Crossref dates span more than a year get the flag `date_spread` (often retro-digitised archives with deposit dates) |
| Yield | r1–3: 88. r4: 40 |

### S2.3 OpenAlex

| Item | Value |
|---|---|
| Script | `scripts/openalex_search.py` |
| Filter | `title_and_abstract.search:(babesia OR babesiosis OR babesiose OR piroplasmosis) AND (dog OR dogs OR canine OR canis)` plus the window dates |
| Type/title rule | Type is `article` or `review` AND (title matches `babesi*\|piroplasm*` with a canine term in the title or abstract, OR a canine term in the title with `babesi*` in the abstract) |
| Yield | r1–3: 2,015 records, 1,042 new → 596 kept. r4: 1,166 records, 571 new → 293 kept |

Records dropped by the OpenAlex type rule:

| Reason | r1–3 | r4 |
|---|---:|---:|
| Dissertations | 153 | 124 |
| Conference papers and abstracts | 58 | 19 |
| Preprints | 21 | — |
| Books and book chapters | 25 | — |
| Datasets (screened separately for data, S11) | 15 | — |
| Babesia and canine terms not in the title | — | 105 |
| Other types | 31 | 30 |

---

## S3. Merge and deduplication

**Type:** script

| Item | Value |
|---|---|
| Script | `scripts/merge_candidates.py --round rN` (round 4); rounds 1–3 were deduplicated within `search.py` and each source script |
| Output | `search/r4/candidates_all.jsonl`, the screening input; records already screened in rounds 1–3 go to `*_prior_overlap.jsonl` |

Rules:

1. **Match key order:** DOI (lower-cased), then PMID, then normalised title (lower-case alphanumerics only).
2. **Precedence:** PubMed records win. Europe PMC and OpenAlex records that carry a PMID are fetched again from PubMed. In a merge, earlier files win; empty fields are filled from later files; `found_by[]` is merged.
3. **Near-duplicates:** titles among eligible records with a similarity ratio > 0.8 were checked by hand. 3 duplicates were merged in rounds 1–3 and 17 at round-4 screening (`duplicates.json`).
4. **Record key:** `PMID:…`, else `DOI:…`, else the source ID.
5. **Round 4 only:** 21 records already screened were left out. Records that already hold an article ID (background papers now inside the window, retired IDs) were kept and flagged `existing_id`.

| Round | Route | Records to screening |
|---|---|---:|
| r1 | PubMed + Europe PMC (plus 164 outside the window by first publication date, dropped) | 1,006 |
| r2 | Citation searching 181 + Crossref 88 | 269 |
| r3 | OpenAlex after the type/title rule | 596 |
| r4 | Databases 637 + citations 211 + Crossref 40 + OpenAlex 293, merged (24 found by two routes) | 1,157 |
| **Total** | | **3,028** |

---

## S4. Title/abstract screening

**Type:** agent

The same written criteria were used in every round; only the window changes. The criteria are restated in full in `search/r4/screening_criteria.md`.

### Process

1. **Batches:** 40 records per batch (`scripts/build_screen_batches.py`), with notes on existing IDs, date discrepancies and unresolved citation records.
2. **Tier 1, first screener** (Claude Sonnet): decides `include`, `exclude` or `uncertain` for each record.
3. **Tier 2, liberal rescue** (Claude Haiku): re-checks every exclusion. It is told to rescue any record that has host pathophysiological data.
4. **Tier 3, senior adjudication** (Claude Opus): decides the rescued and uncertain records. It may fetch a missing abstract from the DOI landing page.
5. **Assembly:** `scripts/assemble_screening.py` combines the tiers from the workflow journal. It checks every key against `batches.json` and writes `screening.jsonl` with `decision`, `exclude_reason`, `rationale` and `stage`.

### Eligibility

| Dimension | Rule |
|---|---|
| Host | Domestic dog. Wild *Canis lupus* (grey or Iberian wolf) counts as canine. Red fox, jackal and other non-*Canis* canids are excluded unless dog data are present. |
| Parasite | Any canine *Babesia*: *B. rossi*, *B. canis* (including the older three-subspecies names), *B. vogeli*, *B. gibsoni*, *B. vulpes* (*T. annae*, *B. microti*-like), *B. conradae*, *B. negevi*, and unspecified large or small *Babesia*. A species named without PCR is not a reason to exclude. |
| Co-infection | Eligible only when Babesia-specific host data can be separated out. |
| Include | Mechanism studies (inflammation, coagulation, endothelium, haemolysis, oxidative stress, organ injury, metabolic and endocrine, omics, histopathology); biomarker, severity, prognosis and outcome studies; **clinicopathological profiles** (haematology or biochemistry case series, labelled `descriptive`); experimental infections that report host responses; **case reports only with a distinct syndrome or mechanism** (for example Evans syndrome, ARDS, cerebral involvement, pancreatitis); reviews of pathophysiology or complications. |
| Overriding rule | A prevalence, diagnostic or treatment study that **also** reports host pathophysiological data for infected dogs is included. |
| Venue | Regional journals not indexed in MEDLINE are kept. A record is never excluded for its venue. |
| Window | By first publication date. `out_of_window` is used only when the record shows that the original publication is outside the window (for example a retro-digitised archive with a deposit date inside it). |
| Uncertain | Used when the abstract is missing or too short, or it does not say whether Babesia-specific host data are reported. |

### Exclusion codes

| Code | Use for | r1 | r2 | r3 | r4 |
|---|---|---:|---:|---:|---:|
| `prevalence_epidemiology` | Surveys, risk factors, distribution; no host data | 306 | 48 | 174 | 236 |
| `not_canine_babesia` | Other hosts or parasites; Babesia with no dog data | 214 | 143 | 36 | 327 |
| `vector_tick` | Tick and vector studies | 155 | 10 | 23 | 104 |
| `diagnostic_test` | Assay development or comparison; no host pathophysiology | 60 | 14 | 40 | 56 |
| `treatment_efficacy` | Endpoints are cure or clearance only | 50 | 11 | 55 | 29 |
| `other_out_of_scope` | Eligible topic, no usable content (for example a routine case report) | 35 | 7 | 75 | 66 |
| `not_peer_reviewed` | Theses, conference abstracts, preprints, chapters | 29 | 4 | 20 | 19 |
| `parasite_biology_only` | Parasite genetics, culture, antigens; no host data | 21 | 4 | 3 | 56 |
| `not_research` | Editorials, letters with no data, errata | 9 | 1 | 2 | 17 |
| `out_of_window` | Original publication outside the window (r4 only) | — | — | — | 9 |

### Screening results

| Round | Records | Include | Uncertain | Exclude |
|---|---:|---:|---:|---:|
| r1 | 1,006 | 121 | 6 | 879 |
| r2 | 269 | 22 | 5 | 242 |
| r3 | 596 | 146 | 22 | 428 |
| r4 | 1,157 | 180 | 58 | 919 |
| **Total** | **3,028** | **469** | **91** | **2,468** |

---

## S5. Stable IDs and extraction packets

**Type:** script

| Item | Value |
|---|---|
| Scripts | `scripts/assign_ids.py`; later `scripts/retire_ids.py` |
| Outputs | `ids.json` (584 entries, 103 retired); `search/packets/<ID>.json` (541) |

- **Format:** `<prefix><3 digits>`. `CB` = eligible canine article, `HU` = human comparator, `BG` = background (before 2006-10-23; `BG001` is the seed meta-analysis).
- **Assignment:** include or uncertain records get the next CB number in first-publication-date order.
- **Append-only registry:** IDs never change and are never reused. An ID excluded later is retired (`"retired": true` with `retired_reason`), which leaves a gap in the numbers.
- **Reclassification:** a BG paper that falls inside the extended window gets a new CB ID (`replaces`). The BG entry is kept, retired, under `RETIRED:<BG ID>` with `replaced_by`. Seven papers moved this way:

  | BG ID | New CB ID |
  |---|---|
  | BG004 | CB323 |
  | BG008 | CB446 |
  | BG010 | CB435 |
  | BG012 | CB438 |
  | BG013 | CB504 |
  | BG014 | CB517 |
  | BG015 | CB481 |

- **Packet contents:** the search record (title, authors, journal, dates, DOI, PMID, abstract, MeSH, keywords), the screening decision and rationale, the Europe PMC full-text check, and `replaces` and `duplicate_records`.

---

## S6. Full-text retrieval

**Type:** script

Tiered download of the article full text. In round 4 this ran *before* extraction, so the extraction agents could read the full text.

| Item | Value |
|---|---|
| Script | `scripts/fetch_fulltext.py [--all] [--ids …] [--retry-failed]` |
| Scope | Every article in `articles.jsonl`, plus assigned IDs not yet extracted. The default run tries open-access articles (OpenAlex `is_oa` or a PMCID); `--all` also tries closed articles |
| Outputs | `data/fulltext/<ID>/fulltext.xml` or `.pdf` (git-ignored, original bytes, never executed); `data/fulltext_status.jsonl`; `data/fulltext_log.jsonl` (1,029 attempts); `data/fulltext_missing.md`; `data/fulltext_openalex.json` (OA records for 442 DOIs) |

### Tiers

Tried in order until one gives a valid file. Article counts are for the 481 live articles.

| Tier | Source | Validity rule | Articles |
|---|---|---|---:|
| 1 | Europe PMC full-text XML (open-access subset) by PMCID; falls back to the Europe PMC PDF render for the same PMCID | XML must contain a `<body>`; front-matter-only records are rejected | 99 |
| 2 | PDF links from OpenAlex open-access locations, best location first | Must start with the `%PDF` header | 119 |
| 3a | Links recorded during the review (`fulltext_url`, then `source_links`) | As tier 2. Index and API links (PubMed, Crossref, OpenAlex, DOAJ) are skipped | 16 |
| 3b | Publisher landing pages (OpenAlex landing page, then doi.org): the `citation_pdf_url` meta tag, PDF-like links, or the OJS view→download pattern | The page's `citation_title` must match the article (some DOIs are registered to the wrong article). Site-wide links (policies, templates, forms) are ignored | 17 |
| — | No valid file | Abstract only (see S7) | 230 |

### Acceptance criteria

- **Type check:** a response is kept only if it really is the claimed type (a `%PDF` header, or JATS XML). An HTML page served as "PDF" is searched once more for the real PDF link.
- **Size caps:** 50 MB per file and 1 GB in total across `data/fulltext/`.
- **Title check after each run:**
  - Words compared: the article's title words with more than 3 letters, minus stop words such as *dogs*, *babesia* and *infected*.
  - Text searched: the JATS text, or the first three PDF pages (`pdftotext`).
  - Result: an overlap of ≥ 0.6 is `ok`, lower is `low`. Mostly non-Latin text is `unchecked`.
  - Files that fail are listed for checking by eye. They are not deleted.
- **Access rules:** no account creation, no paywall or bot-check bypass. A blocked page is recorded and skipped.
- **Re-runnable:** articles that already have a file are skipped. A file placed by hand in `data/fulltext/<ID>/` is recorded as `manual`.

---

## S7. Markdown conversion

**Type:** script

Every article gets exactly one sectioned Markdown file with YAML front matter. This is the text that extraction, translation and the NLP read.

| Item | Value |
|---|---|
| Scripts | `scripts/to_markdown.py` (full text; needs `.venv` with pymupdf 2.x); `scripts/abstracts_to_markdown.py [--fetch]` (abstract only; standard library) |
| Outputs | `data/markdown/<ID>.md` (git-ignored); `data/markdown_report.jsonl` and `.md` |

| Input | Method | Live articles |
|---|---|---:|
| JATS XML | Converted directly with ElementTree: sections, lists, tables as pipe tables (colspan and rowspan padded), figure and table captions, table footnotes | 99 |
| PDF | pymupdf4llm (layout mode, no page headers or footers, no OCR), then cleaned: running heads and page numbers removed, hyphenation and split paragraphs re-joined, emphasis markers dropped, `<sup>`/`<sub>` rewritten | 152 |
| Abstract | Title, the authors' abstract (structured abstracts split at their labels) and author keywords. Source order: search packet → background/comparator records → (with `--fetch`) PubMed or publisher meta tags, cached in `data/abstracts_fetched.json` (11). **The review's own paraphrased summaries are never used.** | 230 |

- **Headings:** known sections become `## Abstract`, `## Methods`, `## Results` and so on; all other headings become `###`.
- **Removed:** references and administrative back matter (acknowledgements, funding, conflicts, author contributions, data availability, supplementary-file lists, footnotes). The removed sections are named in the front matter. Abbreviation glossaries are kept.
- **Front matter fields:** identifiers, source file and SHA-256, converter, language guess, sections found and removed, word and table counts, the fetcher's title check, `text_coverage` and `quality_flags` (for example `garbled_text`, `no_sections_detected`, `language:cyrillic`).
- **Quality result (481 live):**

  | Quality | Articles |
  |---|---:|
  | `ok` | 207 |
  | `abstract_only` | 226 |
  | `review` (to check) | 44 |
  | `no_text` | 4 |

---

## S8. Translation

**Type:** agent + script

- **Which articles:** those whose Markdown has a `language:*` quality flag, or whose packet language is not English and whose body is mostly non-English.
- **Agent:** a translation agent (Sonnet) writes the English body to `data/markdown/translations/<ID>.body.md`. It keeps headings, tables, numbers and order.
- **Script:** `scripts/finish_translations.py` applies the same heading and reference rules, then checks that **numbers are kept** and that the **length ratio** is plausible. It writes `<ID>.en.md` with translation fields in the front matter. Re-converting an original marks its translation stale.
- **Result:** 30 live articles have an English translation (33 files in total). Every translation kept at least 98% of the source numbers.

  | Source language | Articles |
  |---|---:|
  | Portuguese | 8 |
  | Russian | 6 |
  | Ukrainian | 6 |
  | Turkish | 2 |
  | Romanian | 2 |
  | Polish | 1 |
  | French | 1 |
  | Serbian | 1 |
  | Not identified | 3 |

- **Downstream:** extraction and the NLP read `<ID>.en.md` where it exists.

---

## S9. Extraction, appraisal and retirement

**Type:** agent + script

Each article that passed screening goes through a three-step pipeline. Round 4 followed `search/r4/EXTRACTION_GUIDE.md`, which restates the rounds 1–3 practice field by field.

1. **Extract** (Sonnet): reads the packet and the Markdown (the full text where available). It writes the appraisal note `articles/<ID>_<year>_<slug>.md` and returns a **44-field record**, validated against a JSON schema.
2. **Check** (Haiku): checks the note against its source on five dimensions: numbers, design, identifiers, verbatim runs of ≤ 8 words, and causal language. It fixes the note in place and returns `{id, ok, fixes}`.
3. **Script check:** fields, ID and filename are valid, and a note exists if and only if `final_decision` is `include`.

### Decision values

| Value | When | Count |
|---|---|---:|
| `include` | Eligible on the abstract and the full text that could be read. Records screened `uncertain` are decided here | 444 |
| `exclude_fulltext` | The full text or full record shows the article fails the criteria (no Babesia-specific host data, wrong host, treatment or prevalence only, original publication outside the window) | 33 |
| `unverifiable` | The record cannot be confirmed as a published article, or no abstract or full text can be reached | 61 |
| duplicate | Merged into another included record (CB380 → CB371, CB488 → CB468) | 2 |

`scripts/retire_ids.py` then retires every `exclude_fulltext` and `unverifiable` ID in `ids.json` with the reason (cut to 300 characters).

### Record fields (groups)

| Group | Fields |
|---|---|
| Bibliographic | `title`, `authors[]`, `journal`, `volume_issue_pages`, `doi`, `pmid`, `pmcid`, `language`, `corrections` |
| Dates | `first_pub_date`, `online_date`, `issue_date`, `date_note` |
| Study | `species[]` `{name, status, method}` (status `confirmed` / `suspected` / `mixed` / `unspecified`), `host`, `country`, `design`, `sample_size`, `n_infected_dogs`, `n_controls` |
| Appraisal | `evidence_type` (descriptive, associational, prognostic, mechanistic (experimental), review), `one_sentence_finding`, agent `primary_category` and `secondary_tags` |
| Data leads | `data_availability_statement`, `dataset_leads[]`, `supplement_checked`, `repository_checked` |
| Cohort | `cohort_description`, `related_publications[]` (inputs to S10) |
| Provenance | `source_links[]`, `access_date`, `verification_notes` |

The **appraisal note** has a metadata table, then these sections:

- *Abstract-derived summary*
- *Critical interpretation* (evidence type, authors' conclusion, reviewer interpretation, key limitations)
- *Evidence basis*

Most notes are abstract-level appraisals, not risk-of-bias assessments.

### Included articles

| Type | r1–3 | r4 | Total |
|---|---:|---:|---:|
| Primary study | 213 | 125 | 338 |
| Case report | 45 | 21 | 66 |
| Review | 24 | 16 | 40 |
| **Total CB** | **282** | **162** | **444** |

### Supporting papers

- **HU (27):** human babesiosis, malaria and sepsis papers, chosen by the category agents for comparison. A second agent re-checked each against its PubMed XML.
- **BG (10):** older or foundational papers from before the window. They are not counted as canine evidence.

---

## S10. Cohort linkage

**Type:** agent

Identifies articles that report the same dogs, so a re-analysis is not counted as a replication.

- **Inputs:** `cohort_description` and `related_publications` from the extraction records.
- **Blocking:** code first groups candidates by institution, country and species, so each agent sees only plausible groups.
- **Agents:** Sonnet per group, then one Opus pass to reconcile.
- **Rules:** cohorts are never renumbered or deleted. A cohort is changed only with a stated basis.
- **Result:** `cohorts.json`, 38 groups (CH01–CH38), 3 `confirmed` by the authors and 35 `probable`. 101 CB articles belong to a cohort.

---

## S11. Dataset discovery, download and assessment

### S11.1 Discovery

**Type:** script

- **Repository searches** (`scripts/repo_search.py`, 16 queries, 906 hits): GEO DataSets, NCBI BioProject, Zenodo, Figshare (6 queries), Dryad, PRIDE, MetaboLights, BioStudies. Harvard Dataverse failed with HTTP 403.
- **Article-linked checks** (`scripts/fulltext_checks.py`): Europe PMC open-access XML parsed for data-availability statements, supplementary-material elements and repository links (154 checks in r1–3, 221 in r4). Extraction agents checked publisher pages for the other articles.
- **Matching:** hits are matched to articles by title, accession cross-references in the article, and data content (n, groups, variables).

### S11.2 Download

**Type:** script

| Item | Value |
|---|---|
| Script | `scripts/fetch_datasets.py <spec.json>` |
| Specs | `data/fetch_spec_repos.json` (repository deposits, 9 datasets) and `data/fetch_spec_supp.json` (article supplements, from the Europe PMC `supplementaryFiles` endpoint) |
| Outputs | `data/raw/<dataset_id>/` (unchanged bytes, read-only); `data/manifest.jsonl`; `data/fetch_log.jsonl` |

Download criteria:

- Only files listed in a spec (`dataset_id`, file URLs and names, expected size, source record, linked articles) are fetched.
- **≤ 50 MB per file and ≤ 250 MB in total** across `data/raw/` (files already there count). A file over the cap is skipped and logged, never truncated.
- Files already present with a manifest row are skipped.
- Every downloaded file gets a manifest row: `url`, `final_url`, `retrieved_utc`, `bytes`, `sha256`, `content_type`, `source_record`.
- Downloaded files are data only. They are parsed read-only and never executed.

**Result:** 92 files in 36 dataset folders, 41.0 MB in total. All 92 attempts in the log succeeded.

### S11.3 Inspection and assessment

**Type:** script + agent

- `scripts/inspect_files.py` writes structure summaries of xlsx, docx, csv, zip and gz files to `data/inspection/<ID>.json`: sheets, row and column counts, and a preview. `scripts/table_dump.py` is the read-only viewer the assessment agents used.
- Agents scored each dataset 1–5 on four dimensions:
  - **mechanistic relevance**
  - **phenotype richness**
  - **documentation**
  - **feasibility**

  They also recorded granularity, n, groups, time points, features, outcomes, missingness, suitable questions and limitations.
- `scripts/build_datasets.py` and `render_datasets.py` assign priority ranks and independent-source groups (`SRC-A` to `SRC-O`; records with the same letter share animals), then write `datasets.jsonl` and `datasets.md`.

### Status scale

| Code | Meaning | Dataset records | CB articles |
|---|---|---:|---:|
| 1 | Public download verified | 35 | 32 |
| 2 | Public record verified; file retrieval unverified | 12 | 1 |
| 3 | Request-only or controlled access | 10 | 10 |
| 4 | Not located after documented checks | — | 210 |
| 5 | Not assessed or access blocked (no full text) | — | 191 |

Of the 35 status-1 records, 21 hold dog-level or sample-level data from 15 independent sources. The other 14 hold summary statistics or protein lists only. Every verified dataset is small for its number of features, so `datasets.md` advises against predictive ML.

---

## S12. NLP concept extraction

**Type:** script

| Item | Value |
|---|---|
| Scripts | `scripts/extract_syndromes.py` (combined mentions); `scripts/extract_terms.py` (per-article term files, added 2026-10-30) |
| Runtime | Python 3.12 in `.venv-nlp`; scispaCy 0.6.2, spaCy 3.7; UMLS linker (~1.5 GB download), ~7 GB RAM |
| Input | `data/markdown/<ID>.en.md` where it exists, otherwise `<ID>.md`; split into blocks (prose, list items, table rows), each tagged with its section |

### Pipeline

1. `en_ner_bc5cdr_md` NER: DISEASE (and CHEMICAL) mentions.
2. `en_core_sci_md` NER: every biomedical concept (ENTITY), filling gaps between the step-1 entities.
3. AbbreviationDetector (Schwartz & Hearst), so "IMHA" links through its long form.
4. UMLS EntityLinker (char-3-gram TF-IDF with approximate nearest neighbours). The top concept is kept if its score is above the threshold, **0.85** (the scispaCy default is 0.7).
5. negspacy NegEx (the `en_clinical` termset plus post-negations such as "was absent" and "not detected") sets `negated`.

### Keep rules

- **`extract_syndromes`:**
  - Kept: DISEASE mentions (linked or not) and every UMLS-linked ENTITY mention.
  - `disorder` is true for UMLS Disorders-group semantic types.
  - Biomarker-type concepts are kept, because the mechanism categories are recognised from them.
  - CHEMICAL mentions (drugs) are dropped.
  - Negated mentions stay in the file but are left out of the summaries.
- **`extract_terms`:**
  - Kept: linked concepts in the Disorders group only.
  - Excluded: "Finding" (T033), which holds modifiers such as "Severe". Unlinked mentions are dropped.
  - Kept semantic types: T019, T020, T037, T046, T047, T048, T049, T050, T184, T190, T191.

### Outputs

| Output | Rows | Grain |
|---|---:|---|
| `data/syndromes/mentions.jsonl` | 239,733 | One per mention: section, sentence, mention, abbreviation, CUI, score, negation |
| `data/syndromes/article_concepts.csv` | 20,745 | Article × concept; `in_results_or_case` = studied, not only mentioned |
| `data/syndromes/concept_summary.csv` | 4,243 | One per CUI, article counts split by full text and abstract only |
| `data/terms/<ID>.json` | 481 files | Per-article terms: mentions, negated and affirmed counts, sections, surface forms, best score. 1,215 distinct concepts, 35,408 mentions, median 14 terms per article (run 2026-10-30) |

> **Checkout note.** The `data/syndromes/` folder is not in this checkout (`C:\Workspaces\Babesiosis\core`). Its row counts above are taken from `core/CLAUDE.md` (counted 2026-10-28) and were not re-counted. The `data/terms/` figures were counted on 2026-11-04.

---

## S13. Article categorisation

**Type:** script

The review's categories come from the NLP, with no human review (since 2026-10-28). The extraction agents' labels are kept for provenance and used only where the NLP finds no category.

| Item | Value |
|---|---|
| Scripts | `scripts/categorise_articles.py`, then `scripts/build_outputs.py` copies `nlp_primary`/`nlp_secondary` into `articles.jsonl`, `index.md` and the notes |
| Outputs | `data/syndromes/category_map.csv` (9,764 concepts; manual rows kept on regeneration), `article_categories.csv`, `category_comparison.md` |

### Algorithm

1. **Concept map:** name rules, first match wins (so "immune-mediated haemolytic anaemia" maps to ERY before INF). Routine panel analytes and method terms are excluded ("being measured is not a finding"). Cells, organisms and generic qualifiers are never mapped.
2. **Score per article and category:**

   ```text
   score(cat) = Σ over cat's concepts  idf(c) · ln(1 + Σ location weights of c's non-negated mentions)
   idf(c)     = ln((N + 1) / (df(c) + 1)) + 1
   ```

   Only mentions with a UMLS link score ≥ `MIN_LINK` = 0.9 count. A leukogram family (neutrophilia, lymphopenia, …) counts once per article.
3. **Two scores:**

   | Score | Section | Weight |
   |---|---|---:|
   | studied | title | 6 |
   | studied | abstract | 3 |
   | studied | results / case | 2 |
   | studied | conclusion | 2 |
   | studied | unlabelled | 1.5 |
   | studied | methods | 1 |
   | studied | other headings | 1 |
   | mentioned | introduction, discussion | 1 |

   For reviews, the introduction and discussion count as studied.
4. **Primary category:**
   - No mapped evidence → none.
   - SEV is assigned if SEV is the top category, or if ≥ 3 organ categories each reach `SEV_SPREAD` = 0.6 of the top organ score.
   - Otherwise the top category is the primary.
   - `confidence` is high when top/second ≥ `MARGIN` = 1.5.
5. **Secondary and mentioned:**
   - Secondary: categories ≥ `SECONDARY` = 0.35 of the top score.
   - Mentioned: other categories with studied + mentioned ≥ `MENTIONED_MIN` = 4.0.
6. **Study aim:** keyword rules on the title, then the abstract's objective sentence. The codes are PREV, DIAG, BIOM, CLIN, CASE, TRT, PREVN, EXP, MOL and REV.

### Parameters

| Constant | Value |
|---|---:|
| UMLS linker threshold (S12) | 0.85 |
| `MIN_LINK` | 0.9 |
| `MARGIN` | 1.5 |
| `SEV_SPREAD` | 0.6 |
| `SECONDARY` | 0.35 |
| `MENTIONED_MIN` | 4.0 |

### Result (444 CB articles, primary category)

| Category | Articles |
|---|---:|
| ERY | 96 |
| INF | 91 |
| SEV | 59 |
| MET | 50 |
| COA | 40 |
| REN | 40 |
| OXO | 21 |
| CAR | 18 |
| END | 14 |
| NEU | 8 |
| PUL | 7 |

- NLP category: 428 articles (284 high confidence, 144 low). Agent fallback (NLP found no category): 16.
- The NLP and the agents agree on the primary category for 238 of 444 articles (54%). Neither is a gold standard.
- Known mislinks exist (for example "MPO" linked to *Myeloperoxidase Deficiency*). Treat the categories as automatic labels.

---

## S14. Marker–severity associations

**Type:** script + agent. **Status:** pilot only.

Which markers were tested against clinical severity or outcome, and with what result.

### S14.1 Shortlist

**Type:** script

- `scripts/shortlist_severity.py` finds sentences in the article's own sections (title, abstract, results, case, conclusion) that name a severity or outcome. A sentence is "tested" when it also has an association or statistic (correlated, p <, odds ratio, ROC, …).
- Left out: human comparators, reviews and single-case reports.
- Rank score = 2 × tested sentences + other outcome sentences + aim bonus (BIOM 3, CLIN 1) + studied SEV score.
- Tiers:

  | Tier | Rule | Articles |
  |---|---|---:|
  | A | Full text with ≥ 2 tested sentences | 31 |
  | B | Full text with any outcome sentence, or abstract with a tested sentence | 120 |
  | C | The rest with any outcome sentence | 45 |
  | **Total** | | **196** |

- The shortlist also seeds the editable marker map, `data/severity/marker_map.csv`.

### S14.2 Extraction and checks

**Type:** agent + script

- An LLM extractor writes `data/severity/extractions/<ID>.json` (severity definitions and associations, with verbatim quotes) to `association_schema.json`.
- `scripts/check_associations.py` checks:
  - schema enums;
  - **quotes:** exact, near (≥ 80% of 4-word shingles), partial (≥ 50%), or not found;
  - **numbers:** every statistic must appear in the text;
  - marker normalisation through the map.
- **Status:** pilot of 10 articles (2026-10-26), 275 association rows, all with `quote_check` = exact. The full shortlist has not been extracted.

---

## S15. Synthesis and reports

**Type:** agent + script

- `scripts/synthesis_inputs.py` builds the inputs for each category: a one-line digest of each secondary-tagged article, and the primary notes condensed into parts of about 55,000 characters.
- One Sonnet agent per category rewrites `search/synthesis/<CAT>.md`. Opus agents write `CROSS.md` (cross-cutting themes) and `QUESTIONS.md` (five research questions). The agents read the notes, not the full texts. All were rewritten on 2026-10-28 from the NLP categories, for 2006–2026.
- `scripts/assemble_research_map.py` writes `research-map.md`. Its category table (articles, independent cohorts, species, evidence types, datasets) is computed from `articles.jsonl`.
- `scripts/build_search_log.py` writes `search-log.md`; `build_outputs.py` writes `articles.jsonl` and `index.md`.
- `scripts/validate.py` checks syntax, duplicate IDs, scope labels, links and anchors, category totals, dataset-status consistency, checksums and absolute paths.

Rebuild sequence:

```bash
python -I scripts/build_datasets.py && python -I scripts/render_datasets.py && python -I scripts/build_outputs.py \
 && python -I scripts/export_article_terms.py && python -I scripts/assemble_research_map.py \
 && python -I scripts/build_search_log.py && python -I scripts/validate.py
```

---

## S16. Database load and semantic search

**Type:** script

| Item | Value |
|---|---|
| Loader | `console/Babesiosis.Console` (.NET), `dotnet run -- --dry-run`, then `dotnet run` |
| Inputs | `articles.jsonl` and the `articles/*.md` notes. The database holds articles only: no datasets, NLP concepts or full texts |
| Schema | `dbo.category` (11 codes); `dbo.article` (note sections split into columns, JSON columns, `embedding VECTOR(1536)`); `dbo.article_category` (secondary and comparator tags) |

- **Embeddings:** Azure OpenAI `text-embedding-3-small`, 1,536 dimensions. The text embedded is title, one-sentence finding, summary, authors' conclusion, interpretation, limitations and relevance.
- **Change detection:** content hash = SHA-256(model + embedding text). Only new or changed articles are embedded again; a changed article that is not re-embedded has its stale vector cleared.
- **Search:** `EXEC dbo.search_articles @question, @top, @category_code, @from_year, @to_year, @max_distance`, by cosine distance. A distance under about 0.6 is usually on topic.
- The database is only as current as the last loader run. If it disagrees with `articles.jsonl`, the file is correct. *Row counts were not checked against the file for this document.*

---

## Data products

| File | Rows | Use |
|---|---:|---|
| `articles.jsonl` | 481 | Main article table: CB 444, HU 27, BG 10 |
| `articles/<ID>_*.md` | 481 | Appraisal note per article |
| `datasets.jsonl` | 57 | Main dataset table, with status, scores and limitations |
| `cohorts.json` | 38 | Shared-animal groups |
| `ids.json` | 584 | Source key → ID registry (103 retired) |
| `data/fulltext_status.jsonl` | 547 | Retrieval state (481 live and 66 retired IDs) |
| `data/markdown_report.jsonl` | 540 | Conversion front matter as a table |
| `data/manifest.jsonl` | 92 | Downloaded dataset files with SHA-256 |
| `data/terms/<ID>.json` | 481 | Per-article disorder terms |
| `data/severity/associations.csv` | 275 | Marker–severity rows (pilot, 10 articles) |
| `index.md`, `datasets.md`, `research-map.md`, `search-log.md` | — | Rendered reports. Do not count or filter from them |

---

## Limitations and open items

### Method limitations

- **Coverage:** no subscription indexes were searched. Regional literature is reached only through Crossref (capped at 1,000 rows per query) and OpenAlex, so further non-indexed papers almost certainly exist.
- **Language:** no language restriction in the search, but screening used English titles and abstracts. Records only on inaccessible platforms (for example eLIBRARY.ru) are unresolved, so Russian- and Chinese-language clinicopathology is likely under-represented.
- **Access:** 230 of the 481 articles have the abstract only. Most notes are abstract-level appraisals.
- **Automation:** screening, extraction and categories are LLM or NLP outputs. None was checked by a person.
- **Independence:** counts of articles are not counts of independent evidence. Use `cohort_id` and `independent_source`. Only 3 of the 38 cohorts are confirmed by the authors.
- **Reproducibility:** re-running the searches returns newer records, and the agent steps are not deterministic. The structured inputs and outputs of every agent step are kept in `search/`.
- **Theses** (153 in r3, 124 in r4) and conference abstracts were excluded as not peer-reviewed, although some underlie included papers and datasets.

### Open items

| Item | State |
|---|---|
| Severity association extraction for the 196-article shortlist | Pilot only (10 articles) |
| `data/syndromes/` outputs (mentions, concepts, category map) | Missing from this checkout; `articles.jsonl` categories were built from them on 2026-10-28 |
| 61 unresolved records (23 from r1–3, 38 from r4) | Listed in `search-log.md`; not counted |
| Database row counts against `articles.jsonl` | Not checked for this document |
| Status 2 and 3 datasets (22 records) | File retrieval unverified or request-only; not pursued |

---

## Sources

`core/CLAUDE.md`, `core/scripts/README.md`, `core/search-log.md`, `core/search/r4/screening_criteria.md`, `core/search/r4/EXTRACTION_GUIDE.md`, `core/search/r4/PIPELINE.md`, script docstrings and constants, and the structured files (re-counted 2026-11-04). The counts reflect the files at that date.
