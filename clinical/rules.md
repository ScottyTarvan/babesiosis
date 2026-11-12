# Rules and run steps for every clinical page agent

Read this file once. The list of pages is in [index.md](index.md). The page file format is in [content-format.md](content-format.md). A path that starts with `/` is from the repository root; other paths are relative to `/clinical/`.

## The reader

The reader is a veterinarian in general or emergency practice in South Africa, with a sick dog on the table. Write as a clinical manual: short, direct, practical. The reader knows veterinary medicine; do not explain basic terms. The reader wants to know what to look for, what to measure, what to do, how sure the evidence is, and where to read more.

## Rules

1. **No fact from memory.** Every statement on the page has a reference that you read in this run. If you know something and cannot find a source, it does not go on the page.
2. **No invented reference.** Confirm each reference in PubMed, Crossref or Europe PMC in this run, and record the check (step 3). A reference that you cannot confirm is removed, with the statements that depend on it.
3. **Every dose has a source that states that dose.** Give the drug, dose, route, frequency and duration as the source gives them. If two sources differ, give both, each with its reference. Do not calculate a dose from another species. Do not convert a dose for one salt or formulation to another.
4. **Say what the evidence is.** Give each treatment an evidence level and a status (the tables below). Report negative results too: a treatment that was tested and did not help, or did harm, is on the page with that status.
5. **Say where the evidence comes from.** A treatment tested in dogs with babesiosis is not the same as a treatment taken from general canine critical care, or from human malaria. Level D marks the second kind. Much of supportive care is level D or E: say so plainly.
6. **Metric and SI units only.** Doses in mg/kg, µg/kg, mL/kg, mL/kg/h, IU/kg. Laboratory values in SI units as South African laboratories report them (creatinine µmol/L, glucose mmol/L, bilirubin µmol/L, proteins g/L, lactate mmol/L). Haematocrit as L/L with the percentage in brackets. Temperature in °C, pressure in mmHg, mass in kg. If a source uses other units, convert, and keep the source's value in the note of the evidence row.
7. **South Africa.** Give the generic drug name. Say that a product is available or registered in South Africa only if a source says so (a package insert, the IVS or MIMS index, a South African article); give that source. If you do not know, write nothing about availability.
8. **Only `CB` articles are canine evidence** in the local review. `HU` articles are human comparators: a treatment taken from them is level D. `BG` articles are background.
9. **Articles are not independent evidence.** Merge articles with the same `cohort_id` (`/core/cohorts.json`) before you count studies. The Onderstepoort *B. rossi* cohorts were published many times.
10. **Report by species.** Name the *Babesia* species for each finding. Do not carry a result from one species to another without saying so. "Died" often includes euthanasia: say so when you quote a mortality.
11. **Local labels are automatic.** The syndrome tags and the disorder terms were assigned by language models and NLP with no human review. About half of the article notes rest on the abstract only. Use them to find papers, not as proof.
12. **Copyright.** Write the page in your own words. No sentence copied from an article, on the page or in your working files, except a quote of at most 15 words in `evidence.csv` where the exact wording of a dose matters. Do not download or store full texts. Do not go around a paywall or a bot check: record "abstract only".
13. **Privacy.** Do not put the user's name, email address or project details in a web or PubMed request.
14. **`/core/` is read-only.** Never read whole: `/core/articles.jsonl` (stream it). Python, if you use the old environment: `/core/.venv/Scripts/python.exe -I`, read-only.
15. **Ownership.** Write only in `/clinical/<ID>/` and the one page file `/webapp/Babesiosis.Web/public/assets/clinical/<ID>.json`. Change no other file of the web app. Only the coordinator edits `index.md`, `rules.md`, `content-format.md`, the page description files and `/docs/`.
16. **Git.** Do not commit, switch branches, stash or reset. Other sessions share the checkout.
17. **Report faithfully.** "No evidence found" is a result: write it on the page. If the syndrome is not a distinct entity in the literature, say so and tell the coordinator.
18. **Not a prescription.** Do not write "you must". Write what the sources did and found, and what guidelines recommend. The screen carries a fixed notice that the manual is compiled by AI agents and is not peer reviewed.

## Evidence levels

| Level | Meaning |
|---|---|
| A | Controlled trial (randomised or not) in dogs with babesiosis |
| B | Cohort, case-control study or case series of 5 or more dogs with babesiosis, with an outcome |
| C | Case reports, or series of fewer than 5 dogs, with babesiosis |
| D | Extrapolated: evidence or a consensus guideline in dogs with the same syndrome from another cause, or in human malaria or babesiosis |
| E | Expert opinion, narrative review, textbook, formulary or product label, with no data for this use |

Give the highest level that applies, and the number of independent studies behind it.

## Treatment status

| Status | Meaning |
|---|---|
| `standard` | Accepted practice in the sources, whatever its evidence level |
| `proposed` | Suggested or used, with benefit reported but not established |
| `conflicting` | Studies disagree |
| `no_benefit` | Tested, with no benefit shown |
| `harmful` | Evidence of harm, or contraindicated in the sources |

## Sources

### Local sources (start here)

| Source | Use |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv` | 331 included papers with a syndrome, a treatment and an outcome. Filter the free-text `syndromes` column (values separated by `;`) for the tags in your page file. `source` = `main_review` rows have an `article_id`; `rescreen` rows are not in the review, were tagged from the abstract and have no note. Detail: `/core/search/clinical_treatment/README.md` |
| `/core/articles/<ID>_*.md` | The appraisal note of an article |
| `/core/data/markdown/<ID>.md` | The paper's own text (`source_format: abstract` in the front matter = abstract only). Copyrighted: read, do not copy |
| `/core/data/terms/term_display.csv`, `/core/data/terms/<ID>.json` | Which articles mention a disorder term (affirmed mentions) |
| `/core/search/synthesis/<CAT>.md` | The narrative synthesis of a pathophysiology category |
| `/core/articles.jsonl` | Bibliographic fields, species, `cohort_id`, `doi`, `pmid`. Stream it |
| SQL Server `dbo.search_articles`, `dbo.search_passages` | Semantic search over the articles and passages, if you have the `babesiosis-local-db` tools. Read only. See `/docs/database.md` |

"Treatment papers" in [index.md](index.md) = papers in `combined_set.csv` with the tag. "Term articles" = `CB` articles with an affirmed mention of the term.

### Web sources

The local review searched for pathophysiology, not for treatment, so it is incomplete for this task. Search further:

- PubMed and Europe PMC (the PubMed connector tools if your session has them, or the public APIs), for canine babesiosis with your syndrome and with each candidate treatment.
- Consensus statements and guidelines for the syndrome in dogs (for example ACVIM, IRIS, WSAVA, RECOVER, BSAVA). These are level D unless they address babesiosis.
- South African sources: the Journal of the South African Veterinary Association, the Onderstepoort Journal of Veterinary Research, University of Pretoria theses (UPSpace), package inserts.
- Formularies and textbooks, for a dose that no article states. Level E.
- Reference lists of the reviews that you find.

Nothing is downloaded. Read the page or the abstract, record what you read, and keep the link.

## What every page answers

1. What is the syndrome, and how is it defined in babesiosis? Is the working definition of your page file correct?
2. How common is it, in which *Babesia* species and settings, and when in the course of the disease?
3. What causes it (mechanism), in two or three sentences that help the clinician?
4. How is it recognised: clinical signs, tests, thresholds, grading? What must be ruled out?
5. What do you do first, in order, in a practice with basic equipment, and what needs referral?
6. Which treatments were proposed? For each: aim, dose, evidence level, status, cautions, monitoring.
7. What is the prognosis, and which findings change it?
8. What is not known?

Your page file adds questions that are specific to the syndrome.

## The steps of a run

### Step 1. Claim the page

Open [ledger.md](ledger.md). If a row with your ID has the status `Running` or `Done`, stop and tell the coordinator. If not, add your row with the status `Running`. Create `/clinical/<ID>/`.

### Step 2. Research

Work from the local sources, then the web. Keep these files in `/clinical/<ID>/`:

| File | Content |
|---|---|
| `search-log.md` | One row for each search: date, source (file, PubMed, web), the query, the number of hits, the number kept |
| `evidence.csv` | One row for each statement that goes on the page. Columns: `ref` (the reference key, `R1`), `section` (`description`, `diagnosis`, `treatment`, `prognosis`), `statement` (your words), `value` (dose or threshold, with units as on the page), `species`, `design`, `n_dogs`, `cohort_id` (if local), `read` (`full text` or `abstract`), `location` (section, table or page of the source), `note` (the source's own units; a quote of at most 15 words for a dose) |
| `references-check.csv` | One row for each reference: `ref`, `doi`, `pmid`, `checked_in` (`pubmed`, `crossref`, `europepmc`, `publisher`), `title_matches` (yes or no), `date_checked`, `article_id` (the local `CB` ID, if the paper is in the review) |

Stop the search when new searches return no new treatment and no new diagnostic criterion. Record that in `search-log.md`.

### Step 3. Check the references and the doses

- Look up every reference by DOI or PMID. The title, first author and year must match. Fill `references-check.csv`.
- For every dose and every threshold on the page, open the source again and compare the number, the unit, the route and the frequency. This second reading is not optional: a wrong dose is the worst error that this manual can make.
- If you can start a sub-agent, give it `evidence.csv` and the links, and let it check the doses with no view of your page.

### Step 4. Write the page file

Write `/webapp/Babesiosis.Web/public/assets/clinical/<ID>.json` in the format of [content-format.md](content-format.md). Then run:

```
python -I clinical/shared/validate.py webapp/Babesiosis.Web/public/assets/clinical/<ID>.json
```

It must end with `OK`. Correct every error. Read every warning and correct it or explain it in your report.

### Step 5. See the page

1. Start the web app with the entry `babesiosis-web-mock` in `/.claude/launch.json` (the Clinical screen reads static files and needs no API). If the port is in use, a server is already running: use it. Do not start the server with a shell command.
2. Open `/clinical/<ID>`. Confirm that every section shows, that each citation marker opens its reference, that each reference link opens the right paper, that the dose tables are complete, and that the browser console has no error. Check the light and the dark theme.

If the Clinical screen is not built, or you have no browser tools, write `validated, not seen` in the View column of the ledger.

### Step 6. Close the run

Write `/clinical/<ID>/report.md` (one page): the definition that you confirmed or changed; the number of references, by evidence level; the treatments, with status; what you could not find; the statements that you are least sure of; decisions for the user. Update your ledger row. Then give a final message with the same points and every file that you wrote.

## If something goes wrong

| Situation | Do this |
|---|---|
| A source is behind a paywall | Use the abstract, record `abstract` in `read`, and do not take a dose from a secondary citation without saying "as cited in" |
| Two sources give different doses | Put both on the page, each with its reference and context |
| No evidence in dogs with babesiosis | Say so on the page. Give the level D or E guidance with its label |
| The syndrome overlaps another page | Keep to the scope lines of your page file. Link to the other page by its ID |
| The syndrome is not a distinct entity in the literature | Write a short page that says so, with the evidence. Tell the coordinator |
| The validator fails on a rule that you think is wrong | Do not edit the validator. Report it |

## The ledger

[ledger.md](ledger.md) has one row for each page. Add your row before you start. Edit only your own row. Columns: `ID`, `Status` (`Running`, `Done`, `Blocked`), `Run (UTC)`, `References` (number), `Treatments` (number), `Validated` (date), `View` (`seen <date>`, or `validated, not seen`), `Report`, `Notes`.
