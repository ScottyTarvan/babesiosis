# The page file

Each page of the Clinical screen is one JSON file: `/webapp/Babesiosis.Web/public/assets/clinical/<ID>.json`. The screen draws every page from this format, so all pages look the same. You write content; you do not write a component.

A complete file with every field is in `shared/example.json`. Check your file with `shared/validate.py` ([rules.md](rules.md), step 4). The rules for the content (sources, evidence levels, units) are in [rules.md](rules.md).

## Text rules

- Plain text, UTF-8. No HTML, no Markdown. One paragraph in each text field.
- British spelling (haemolytic, oedema, anaemia). Italic species names are not possible: write `B. rossi`.
- A citation is a marker in the text: `[R1]`. Two citations are two markers: `[R1][R2]`. The screen turns each marker into a link to the reference list.
- Fields named `refs` hold reference keys: `["R1", "R4"]`.
- Short sentences. The clinician reads on a phone or between patients.
- An empty optional text field is `""`. An empty optional list is `[]`.

## Fields

| Field | Required | Content |
|---|---|---|
| `schema_version` | Yes | `1` |
| `id` | Yes | The page ID. The same as the file name |
| `title` | Yes | The syndrome name, as in [index.md](index.md) unless the literature shows a better name |
| `updated` | Yes | `YYYY-MM-DD`, the date of the run |
| `definition` | Yes | One or two sentences, with a citation |
| `definition_note` | No | Whether the working definition was confirmed or changed |
| `key_points` | Yes | 3 to 6 sentences. What the clinician must remember |
| `description` | Yes | A list of `{heading, text}`. Use these headings where you have content: "What it is", "How common, and in which dogs", "When in the course of disease", "Mechanism". About 400 words in total |
| `species_notes` | No | A list of `{species, note}` for what differs between *Babesia* species |
| `diagnosis.criteria` | Yes | A list of `{criterion, threshold, basis, note, refs}`. `basis` says where the threshold comes from: `babesiosis` (used in dogs with babesiosis), `general canine` (a guideline for the syndrome from any cause), `human`, or `working` (no published threshold; say so in `note`) |
| `diagnosis.clinical_signs` | Yes | A list of `{sign, note, refs}` |
| `diagnosis.tests` | Yes | A list of `{test, finding, note, refs}`. Put the tests of a basic practice first |
| `diagnosis.differentials` | Yes | A list of `{condition, distinguish, refs}`. Include other complications of babesiosis that look the same, and co-infections |
| `diagnosis.grading` | No | A list of `{grade, criteria, refs}` if a grading scheme is in use |
| `approach` | Yes | The steps in order: `{step, action, detail, setting}`. `setting` is `practice` (a general practice can do it) or `referral`. 4 to 8 steps |
| `treatments` | Yes | See below. An empty list is allowed only if no treatment was proposed; say so in `evidence_gaps` |
| `prognosis` | Yes | `{text, indicators}`. `indicators` is a list of `{finding, meaning, refs}` |
| `related` | No | Links to other pages: `{id, why}` |
| `evidence_gaps` | Yes | A list of sentences: what is not known |
| `references` | Yes | See below |
| `search` | Yes | `{date, sources[], note}` |

## A treatment

| Field | Content |
|---|---|
| `name` | The treatment, by generic name or by kind ("Packed red cell transfusion") |
| `class` | `antibabesial` (TX00 only), `specific` (aimed at the mechanism of the syndrome), `supportive`, `adjunct` |
| `aim` | What it is meant to do, in one sentence |
| `status` | `standard`, `proposed`, `conflicting`, `no_benefit`, `harmful` |
| `evidence_level` | `A` to `E` |
| `independent_studies` | The number of independent studies behind the level (cohorts merged). `0` for level E |
| `evidence_summary` | What was done, in which species and how many dogs, and what happened. With citations. Say when the evidence is not from babesiosis |
| `doses` | A list. Empty for a treatment with no dose (for example oxygen by mask can have a flow rate; nursing has none) |
| `cautions` | Adverse effects, contraindications, interactions, with citations |
| `monitoring` | What to measure, and how often |
| `availability` | South African availability, only with a source. Otherwise `""` |
| `refs` | Every reference of this treatment |

Order the treatments as the clinician needs them: `standard` first, then `proposed` and `conflicting`, then `no_benefit` and `harmful`.

## A dose

| Field | Content |
|---|---|
| `drug` | Generic name, with the salt or formulation if the source gives it ("diminazene aceturate") |
| `dose` | Number and unit: `3.5 mg/kg`, `10 to 20 mL/kg`, `2 mL/kg/h`. A range as "x to y" |
| `route` | `IV`, `IM`, `SC`, `PO`, or in words |
| `frequency` | "once", "every 12 h", "repeat after 14 days" |
| `duration` | "single dose", "10 days", or `""` |
| `context` | The species, the kind of dog and the kind of source: "*B. gibsoni*, 12 dogs, trial" or "product label" |
| `note` | Anything that the clinician must know with this dose |
| `refs` | The source or sources that state this dose. Never empty |

One row for each distinct regimen. If sources disagree, give one row for each.

## A reference

| Field | Content |
|---|---|
| `ref` | `R1`, `R2`, …, in the order of first citation |
| `authors` | Up to three authors, then "et al." |
| `year`, `title`, `journal`, `volume_pages` | As in PubMed or Crossref |
| `doi` | The bare DOI (`10.1111/…`), or `""` |
| `pmid` | The PubMed ID, or `""` |
| `url` | Only if there is no DOI and no PMID (a guideline page, a thesis, a package insert). `https://` |
| `article_id` | The local ID (`CB050`) if the paper is in `/core/articles.jsonl`, or `""` |
| `type` | "trial", "cohort", "case series", "case report", "review", "guideline", "textbook", "label", "experimental" |
| `species` | The *Babesia* species, or `""` |
| `n_dogs` | A number, or `null` |
| `read` | `full text` or `abstract`: what you read |

The screen builds the link: `https://doi.org/<doi>`, or `https://pubmed.ncbi.nlm.nih.gov/<pmid>/`, or `url`. A reference needs at least one of the three.

## Size

A page that is read at the cage side must be short. Aim for 10 to 30 references, 4 to 12 treatments, and no text field above about 120 words. If the literature is larger, keep the strongest evidence and the most recent review, and say in `search.note` what was left out.
