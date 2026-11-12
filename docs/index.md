# Documentation index

Read the one file that matches the task. For a file marked **large**, grep for a heading or an ID; do not read it whole. A path with no prefix is relative to `core/`. A path that starts with `/` is from the repository root.

## Review data

| File | Size | Read when you need |
|---|---|---|
| [data-guide.md](data-guide.md) | 3 KB | **Start here.** Which file or table answers a question about articles, datasets, terms or the search |
| [ids-and-codes.md](ids-and-codes.md) | 4 KB | ID schemes (`CB`, `HU`, `BG`, `CH`, `DS`, `SRC`), retired IDs, the 11 category codes, dataset status codes 1–5 |
| [core-tables.md](core-tables.md) | 3 KB | The field lists of `articles.jsonl` and `datasets.jsonl`; the root output files |
| [data-files.md](data-files.md) | 3 KB | `data/`: raw downloads, manifest, full texts, Markdown conversion and quality flags |
| [nlp-and-severity.md](nlp-and-severity.md) | 5 KB | `data/syndromes/`, `data/terms/`, how categories are assigned, `data/severity/` |
| [search-provenance.md](search-provenance.md) | 4 KB | `search/` working files: queries, candidates, screening, extraction, synthesis, round 4 |
| [database.md](database.md) | 3 KB | SQL Server tables, the console loader, `dbo.search_articles`, `dbo.search_passages` |

## Pipeline

| File | Size | Read when you need |
|---|---|---|
| [pipeline-spec.md](pipeline-spec.md) | 37 KB, **large** | The method of each stage S1–S16, with criteria and counts. Grep for the stage heading (`## S4.`). The scripts it names are deleted (see below) |
| `search/r4/screening_criteria.md` | 6 KB | The title and abstract eligibility criteria (all rounds) |
| `search/r4/EXTRACTION_GUIDE.md` | 12 KB | The extraction rules, field by field |
| `search/clinical_treatment/README.md` | 7 KB | The clinical syndrome plus treatment set and its re-screen |
| `data/severity/EXTRACTION_GUIDE.md` | 5 KB | Rules for the marker against severity extraction |

## Experiments

| File | Size | Read when you need |
|---|---|---|
| `/experiments/index.md` | 7 KB | **Start here for research work.** The experiments on why some dogs develop severe disease: 14 packages for parallel agents, one file each; the Status column says what was run. `SV-META` is the meta experiment, the final review of all results for research leads. Read the index, then `/experiments/rules.md`, then only your package file. Experiment scripts and outputs go in `/experiments/` too |
| `/experiments/run-instructions.md` | 20 KB | How an agent runs a package to the end: its own environment and tools (Python, R, .NET) and their limits, the rows for `dbo.experiment` and `dbo.experiment_result`, the view on the Experiments screen, and the ledger |
| `/experiments/ledger.md` | small | Which experiments were run, and whether each is in the database and visible in the web app |

## Clinical manual

| File | Size | Read when you need |
|---|---|---|
| `/clinical/index.md` | 6 KB | **Start here for the clinical manual.** The 16 clinical syndromes (`SY01`–`SY16`) and the antibabesial treatment section (`TX00`): one page file each for a research agent, with working definitions and scope. All 17 pages were written on 2026-11-12 (AI-compiled, not reviewed by a veterinarian; not committed); the Status column and `/clinical/ledger.md` say what is done, and each page has a report in `/clinical/<ID>/report.md` |
| `/clinical/rules.md` | 12 KB | The rules for every page agent (sources, evidence levels A–E, metric and SI units, reference checks), the steps of a run and the ledger |
| `/clinical/content-format.md` | 6 KB | The JSON page file that an agent writes to `/webapp/Babesiosis.Web/public/assets/clinical/`; `shared/validate.py` checks it |
| `/clinical/CL-00-shell.md` | 5 KB | The specification of the "Clinical" screen of the web app (menu item, side rail, page sections) and what was built on 2026-11-12 |

## Web app

| File | Read when you need |
|---|---|
| `/webapp/.claude/agents/agents.md` | The index of the web app's architecture and agent guides |
| `/webapp/Babesiosis.Web/README.md` | The Angular app |
| [ai-agent.md](ai-agent.md) | The AI agent of the web app: the three sources it reads (articles, experiments, clinical manual), its tools, its rules, and how to add a source |
| `/.claude/launch.json` | The local run entries (API on 6060, web on 4400) |

## Deleted on 2026-11-12

`core/` holds data only. The pipeline scripts (`scripts/`), the experiment specs, tidy files and results (`experiment_specs/`, `data/tidy/`, `data/experiments/`), `data/inspection/`, the rendered reports (`index.md`, `datasets.md`, `research-map.md`, `search-log.md`) and the fetch logs were deleted. A script name in these docs says how a file was made; the script is not in the working tree. To read one: `git show 8d4c6d9:core/scripts/<name>.py`.
