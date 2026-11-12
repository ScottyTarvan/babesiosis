# Extraction guide (round 4)

This guide is for the agents that extract the round-4 articles (CB320–CB540). Rounds 1–3 did not save their extraction instructions. This guide restates them from what those rounds produced: the records in `search/extraction_records.jsonl`, the notes in `articles/`, and the five check dimensions in `search/extraction_checks_r1.json` and `search/extraction_checks_r3.json`. The aim is for a round-4 record and note to look exactly like a round 1–3 one.

The one change: round 4 fetched the full texts **before** extraction. Where a full text exists, `data/markdown/<ID>.md` holds it, and its front matter shows the source (`source_format`: `jats_xml`, `pdf` or `abstract`).

## Inputs for one article

| Input | Path | Use |
|---|---|---|
| Packet | `search/packets/<ID>.json` | `record` (the search record: title, authors, journal, dates, DOI, PMID, abstract, MeSH, keywords); `screening` (the round-4 decision, categories and rationale); `fulltext_check` (Europe PMC data statements, supplements, repository links, where there is a PMCID); `replaces` and `duplicate_records` (see below) |
| Article text | `data/markdown/<ID>.md` | Full text where `source_format` is `jats_xml` or `pdf`; otherwise the abstract only. Check `quality_flags` (for example `garbled_text`, `no_sections_detected`) before you rely on it |
| Criteria | `search/r4/screening_criteria.md` | Eligibility, the window (2006-10-23 to 2016-10-22) and the category codes |
| Example records | `search/extraction_records.jsonl` | Rounds 1–3 records, for the style of every field. CB101 (experimental study, full text) and CB047 (case report, abstract only) are good models |

- **`replaces`**: when this is a `BG` ID, the article was a background paper and is now canine evidence. Read its old note `articles/<BG ID>_*.md` and `data/markdown/<BG ID>.md` as extra sources. Write a **new** CB note; do not edit the BG note. When `replaces` is `CB029`, the paper was retired earlier because it could not be found; this record confirms it.
- **`duplicate_records`**: other records of the same paper (a repository copy, a translated title, a reference-list entry). Use them for missing metadata or an abstract, and say so in `verification_notes`.

You may look a record up on the web: the DOI landing page, PubMed, Europe PMC, Crossref or OpenAlex. Do not create accounts, accept terms, or get past paywalls, bot checks or other access controls. If a page is blocked, record that and move on.

## Decision (`final_decision`)

| Value | When | Note written? |
|---|---|---|
| `include` | Eligible by the criteria, on the abstract and full text you could read. Records that screening marked `uncertain` are decided here | yes |
| `exclude_fulltext` | The full text or the full record shows that the article fails the criteria: no Babesia-specific host data, the wrong host, a treatment or prevalence study only, or an original publication outside the window (as with CB023) | no |
| `unverifiable` | You cannot confirm that the record exists as a published article, or no abstract or full text can be reached to judge it (as with CB016 and CB027) | no |

`decision_reason` gives the reason in one to three sentences. For `include`, say what the article contributes (as in CB101). For the other two, say what you checked and found.

## Record fields

Return one JSON object with exactly these 44 fields. Use `null` for a value that does not apply or that you cannot find; do not leave a field out.

| Field | Type | Content (rounds 1–3 style) |
|---|---|---|
| `id` | string | The packet ID |
| `final_decision` | string | `include`, `exclude_fulltext` or `unverifiable` |
| `decision_reason` | string | See above |
| `scope_label` | string | `core canine evidence`, or `canine review` for a review |
| `include_type` | string or null | `primary`, `case_report` or `review`; null unless included |
| `title` | string | The title as published (packet title; fix only clear errors, and say so in `verification_notes`) |
| `authors` | list of strings | `Surname Initials`, for example `Atkinson BK` |
| `journal` | string | Full journal name |
| `volume_issue_pages` | string or null | For example `45:108475` or `54(3):281-9` |
| `first_pub_date` | string | `YYYY-MM-DD`, `YYYY-MM` or `YYYY`: the earlier of the online and issue dates. Keep the packet value unless a source shows it is wrong |
| `online_date`, `issue_date` | string or null | As found |
| `date_note` | string | For example `online 2022-07-19; issue 2022-12 (month precision)`; note any discrepancy between sources |
| `doi`, `pmid`, `pmcid` | string or null | `doi` lower-case, without `https://doi.org/` |
| `language` | string | The language of the article, as in the packet (`eng`, `en`, `pt` and so on) |
| `corrections` | string | For example `none indicated in PubMed record`, or `not checked (not in PubMed)` |
| `species` | list | `{name, status, method}`. `status` is `confirmed`, `suspected`, `mixed` or `unspecified`. `method` says how the species was identified (for example "PCR-RLB", "blood smear only"). Older papers that say only "*B. canis*" with no molecular method are `suspected` or `unspecified` |
| `species_short` | string | For example `B. rossi`, `B. canis`, `Babesia sp.` |
| `host` | string | For example `client-owned dogs, natural infection` |
| `country` | string | Country and, where given, the setting |
| `design` | string | For example `case-control biomarker study of natural infection` |
| `sample_size` | string | Free text with the groups, for example `30 infected, 10 healthy controls` |
| `n_infected_dogs`, `n_controls` | integer or null | Numbers as reported; null when not reported |
| `primary_category` | string | One code: ERY, INF, END, COA, REN, PUL, NEU, CAR, MET, OXO or SEV (definitions in `/docs/ids-and-codes.md`) |
| `secondary_tags` | list of strings | Further codes |
| `evidence_type` | string | `descriptive`, `associational`, `prognostic`, `mechanistic (experimental)` or `review`. Add a short qualifier in brackets only where it is needed, for example `descriptive (single case report)` |
| `one_sentence_finding` | string | The main finding in one sentence, with no causal claim |
| `abstract_source` | string | Where the abstract came from, for example `PubMed record PMID 17116368 (packet)` |
| `abstract_available` | boolean | |
| `fulltext_checked` | boolean | True if you read the full text (`data/markdown` with `source_format` other than `abstract`, or a page you reached) |
| `fulltext_url` | string or null | The URL of the full text you read |
| `supplement_checked`, `repository_checked` | boolean | Whether you looked |
| `data_availability_statement` | string or null | Quoted or summarised from the article |
| `dataset_leads` | list | `{kind, description, url, accession, likely_granularity}`. `kind` is `none`, `supplement`, `sequence_accession`, `request_only` or `repository`. `likely_granularity` is `individual dog/sample-level`, `aggregate`, `sequence` or `unknown`. With no lead, give one `none` entry that says what was checked |
| `cohort_description` | string | Institution, place, recruitment period and n, and any statement that the dogs overlap with another paper, with that paper's details. This feeds the cohort linkage, so be specific |
| `related_publications` | list of strings | Companion or overlapping papers: `Author et al. Title. Journal Year;vol:pages. PMID … doi …` |
| `source_links` | list of strings | Every page you used |
| `verification_notes` | string | What you checked, what did not match, and what you could not reach |
| `note_written` | boolean | True for `include` only |
| `keywords` | list of strings | From the packet record (`keywords`), or `[]` |

## Note (`articles/<filename>`, `include` only)

Write the note to `articles/` with the `filename` from the packet. Use the layout of the rounds 1–3 notes (see `articles/CB101_*.md` and `articles/CB047_*.md`):

```markdown
# <Title>

[Back to article index](../index.md)

| Field | Value |
|---|---|
| ID | <ID> |
| Scope label | <scope_label> |
| Authors | <authors, comma-separated> |
| Journal | <journal>, <volume_issue_pages> |
| First publication date | <first_pub_date> (<online or issue>) |
| Date notes | <date_note> |
| DOI | [<doi>](https://doi.org/<doi>) |
| PMID / PMCID | [PMID <pmid>](https://pubmed.ncbi.nlm.nih.gov/<pmid>/) / [<pmcid>](https://pmc.ncbi.nlm.nih.gov/articles/<pmcid>/) |
| Corrections / retractions | <corrections> |
| Babesia species | <species with status and method> |
| Host | <host> |
| Country / setting | <country> |
| Study design | <design> |
| Sample size | <sample_size> |
| Cohort identifier | pending |
| Primary category | <code> — <short name> |
| Secondary tags | <codes> |
| Dataset status | pending |

## Abstract-derived summary

<100–150 words>

## Critical interpretation

- **Evidence type:** <evidence_type>
- **Authors' conclusion:** <one or two sentences>
- **Reviewer interpretation:** <two to four sentences>
- **Key limitations (from available information):** <semicolon-separated list>

_Abstract-level appraisal; not a formal risk-of-bias assessment._

## Evidence basis

- **Abstract:** [<source>](<url>), accessed <today's date>
- **Full text:** checked ([<source>](<url>)) | not accessible (<why>)
- **Supplementary material:** <what is listed, or "none listed">
- **Repository records:** <what was found, or "none found in article">
- **Information beyond the abstract:**
  - <one bullet per fact, each ending in "(full text)" or naming its source>
```

- Leave the **Cohort identifier** and **Dataset status** rows as `pending`. `build_outputs.py` fills them.
- Where an ID or link is missing, write `not available` in that cell instead of an empty link.
- Keep the italic appraisal line exactly as shown, even when you read the full text, so the notes stay comparable across rounds.
- Write the note in English, whatever the article's language.

## Clarifications from the pilot (2026-10-28)

The 10-article pilot (CB323, CB325, CB327, CB332, CB342, CB438, CB440, CB443, CB448, CB517) was compared with the rounds 1–3 records. These rules make round 4 match them:

- **Dates at their real precision.** A `YYYY-01-01` that is only a year (PubMed year-only issue, OpenAlex or Crossref placeholder) is written `YYYY`; a month-only date is `YYYY-MM`, not `YYYY-MM-01`. Rounds 1–3 did this for 25 records. Where the issue date has only year or month precision and a dated online publication exists, `first_pub_date` is the online date. Say what you did in `date_note`.
- **`fulltext_url`** is the URL the full text was retrieved from. The extract agent is given it (from `data/fulltext_status.jsonl`, `source_url`). Never give a local path (`data/markdown/...`) or an OpenAlex work page. Use `null` when only the abstract was read.
- **Keep the short fields short**, as in rounds 1–3 (`host` about 30 characters, `sample_size` about 45, `design` about 70). For example, `host` is `client-owned dogs, natural infection` only when a source says client-owned; otherwise `dogs, natural infection`. Put caveats ("not stated in the abstract", "derived") in `verification_notes`, not in these fields. When the numbers are not reported, `sample_size` is `not reported in abstract`.
- **A replaced BG note is not a source of facts.** Take facts from the packet and the Markdown texts; where the old note says more than they do, leave it out.

## Rules (the five check dimensions)

The checker tests every note and record against these rules:

- **(a) Numbers, species, design and sample size** match the sources. Give no number that is not in the abstract or the full text you read. Mark anything beyond the abstract "(full text)".
- **(b) The summary** is 100–150 words, paraphrased, with no run of more than 8 words copied from the source. It summarises the abstract. Put full-text detail in *Information beyond the abstract*.
- **(c) Title, DOI, PMID or PMCID, and dates** match the packet, or the difference is explained in `verification_notes` and *Date notes*.
- **(d) The note is complete:** no placeholders other than the two `pending` rows, and the back link to the index is present.
- **(e) No causal claims** beyond what the design supports. Use "was associated with", not "caused", unless the study was experimental and showed it.
