# ID schemes and codes

Paths are relative to `core/`. Counts as of 2026-10-28.

## Article IDs

The format of an article ID is `<prefix><3 digits>`. The ID is also the start of the file name in `articles/`, for example `CB050_2020_<slug>.md`.

| Prefix | `scope_label` | Count | Meaning |
|---|---|---|---|
| `CB` | `core canine evidence` (404), `canine review` (40) | 444 | Eligible canine articles. These are the review's evidence. |
| `HU` | `human comparator` | 27 | Human babesiosis, malaria and sepsis papers, for comparison only. |
| `BG` | `background` | 10 | Older or foundational papers (before 2006-10-23). `BG001` is the seed meta-analysis. |

- IDs are append-only and stable. `ids.json` maps each source key (`PMID:…` or `DOI:…`) to its ID. It has 584 entries, and 103 of them are retired (`"retired": true`, with a `retired_reason`). Retired IDs leave gaps in the numbers (for example, `CB003` is retired). A missing number is not an error.
- Round 4 added CB320–CB540 (221 IDs: 162 included, 57 retired, 2 retired as duplicates: CB380 → CB371, CB488 → CB468).
- A replaced ID has `replaced_by`, and the new entry has `replaces`. Seven `BG` papers inside the window became `CB` articles (BG004, BG008, BG010, BG012, BG013, BG014, BG015 → CB323, CB446, CB435, CB438, CB504, CB517, CB481), under `RETIRED:<BG ID>` keys. `CB029` → CB409.
- CB510 and CB511 are the same study, published twice (cohort CH23). Count them once.
- Do not count `HU` and `BG` articles as canine evidence.

## Other IDs

| ID | Format | Meaning |
|---|---|---|
| Category code | `ERY` `INF` `END` `COA` `REN` `PUL` `NEU` `CAR` `MET` `OXO` `SEV` | The 11 pathophysiology categories. See [Category codes](#category-codes). |
| Cohort | `CH01`–`CH38` | A group of articles that report the same animals. Defined in `cohorts.json`. |
| Dataset | `DS01`–`DS09` | A repository deposit (Mendeley, Figshare, PRIDE and others). Can link to more than one article. |
| | `S-CB###` | Supplementary files of article `CB###`. |
| | `P-<accession>` | A PRIDE or ENA project record, for example `P-PXD005117`. |
| | `R-<accession>` | A BioProject or SRA record. Mostly parasite-side data, with the record verified but no file retrieved. |
| | `RQ-CB###` | Article `CB###` says its data are available on request. Not pursued. |
| Independent source | `SRC-A`–`SRC-O` | Dataset records with the same letter share animals. Use this to count independent sources. |
| Study aim | `PREV` `DIAG` `BIOM` `CLIN` `CASE` `TRT` `PREVN` `EXP` `MOL` `REV` | A rule-based study aim, assigned by `categorise_articles.py` (`AIMS`, `AIM_RULES`). |

## Category codes

| Code | Category |
|---|---|
| ERY | Erythrocyte injury, haemolysis, anaemia and immune-mediated processes |
| INF | Inflammation, innate/adaptive immunity and immunopathology |
| END | Endothelium, microcirculation, perfusion and tissue hypoxia |
| COA | Coagulation, platelets, immunothrombosis and DIC |
| REN | Renal injury and renal function |
| PUL | Pulmonary injury and gas exchange |
| NEU | Neurological and cerebral disease |
| CAR | Cardiac injury and haemodynamics |
| MET | Hepatic, metabolic, endocrine and acid-base disturbances |
| OXO | Oxidative stress, host-parasite interaction, omics and virulence |
| SEV | Multisystem clinical phenotype, severity and outcome |

How the categories are assigned (NLP, no human review), and the distribution, is in [nlp-and-severity.md](nlp-and-severity.md#categories).

## Dataset status codes

`status_code` in `datasets.jsonl` and `dataset_status_code` in `articles.jsonl` use the same scale:

| Code | Meaning | Where it appears |
|---|---|---|
| 1 | Public download verified | `datasets.jsonl` (35 records) and articles |
| 2 | Public record verified; file retrieval unverified | `datasets.jsonl` (12 records) and articles |
| 3 | Request-only or controlled access | `datasets.jsonl` (10 records) and articles |
| 4 | Not located after documented checks | Articles only (210 CB articles) |
| 5 | Not assessed or access blocked (no full text) | Articles only (191 CB articles; 192 with BG001) |

Of the 35 records with status 1, 21 have individual dog-level or sample-level data (15 independent sources). The other 14 hold only summary statistics or protein lists. Use `granularity` to tell them apart.
