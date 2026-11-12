# Run instructions: from a package file to the database, the web app and the ledger

Version 3, 2026-11-12. Read this file once before you run a package. The research rules, the outcome lock and the report template are in [rules.md](rules.md). This file tells you what a finished run is, how much freedom you have, and the three steps that come after the analysis: put the results in the database, show them in the web app, and record the run.

A run is finished only when all four are true:

1. `report.md` is written (the template is in [rules.md](rules.md)).
2. The results are in `dbo.experiment` and `dbo.experiment_result`.
3. The Experiments screen of the web app shows them with a visualisation.
4. The row in [ledger.md](ledger.md) says `Done`.

## Reading order

1. [index.md](index.md): find your package and its dependencies.
2. [rules.md](rules.md).
3. Your package file, and the parts of [data.md](data.md) that it names.
4. This file.
5. For step 5 only: `/webapp/.claude/agents/architecture/general.md`, `core.md` and `web-app.md` (6 KB together).

## Terms

- **Package**: one file `SV-xx-*.md`. It is the unit of work for an agent.
- **Experiment**: one question with one result and one visualisation. It is one row in `dbo.experiment`. A package has one experiment or more: the primary analysis is always an experiment of its own; a replication, or a part (SV-02a, SV-02b), is another.
- **Experiment code**: `<package>-<two digits>-<slug>`, for example `SV-01-01-habitus-distance`. Capitals for the package, lower case and hyphens for the slug, 60 characters at most. The code never changes after the first load.
- **Method**: the type of analysis, in lower case with underscores, 50 characters at most (`disease_space_map`, `evidence_matrix`). The web app chooses the view by the method. Experiments with the same method share one view.

A package with no statistical test (SV-G1, SV-G2, SV-06a, SV-07, SV-10) still records one experiment. Its results are the tables that describe the output: counts, coverage, the linkage table.

## Your freedom, and its limits

Each experiment is independent. Choose the tools that do the analysis best, and build what you need. Do not make a weaker analysis because a tool is not installed: install it.

**You can:**

- Use any language and any library: Python, R, .NET, Node, or a mix.
- Create your own environment and install packages into it.
- Write your own programs: scripts, console applications, a loader of your own.
- Run code for as long as the analysis needs. Run a command of more than about 2 minutes in the background.
- Make figures with a plotting library.
- Write your results to the database with your own code.

**You do not need:** the shared reader `shared/io/rawio.py`, the console loader in `/console/`, or the code of another package. Use them only if they save you time. The data contracts stay: if your package depends on the tidy files of SV-G1 or the output of another package, read those files; do not build your own copy.

**The limits:**

| Limit | Reason |
|---|---|
| Everything that you create is inside `/experiments/<package>/`. The web app view (step 5) is the one exception | Other agents work in the same checkout at the same time |
| The environment is in `/experiments/<package>/env/` (git-ignored). Do not install into, or change, `/core/.venv`, `/core/.venv-nlp`, the system Python, the system R library or the global npm and .NET tool folders | A change to a shared environment changes the results of other packages |
| Install packages only from the standard registries: PyPI, CRAN, Bioconductor, NuGet, npm, conda-forge. Pin every version | Reproducibility, and no code from unknown sources |
| A new runtime (for example Julia) goes in `env/` as a portable copy. If it has only a system installer, stop and ask | A system installer changes the machine for everyone |
| `/core/` is read-only | Rule 8 |
| In the database, write only the rows of your own experiment codes in `dbo.experiment` and `dbo.experiment_result`. No `CREATE`, `ALTER` or `DROP`. No other table | The database is shared and the web app reads it live |
| The research rules of [rules.md](rules.md) do not change: no predictive model, no "subtypes", the outcome lock, independent sources, no article text in outputs, no user details in an outside request | Freedom of tools is not freedom of method |

What is on the machine now (checked 2026-11-12; check again before you rely on it):

| Tool | Where |
|---|---|
| Python 3.13 and `uv` | On the path. `uv venv env/py --python 3.12` then `uv pip install --python env/py …` makes an environment in seconds. `uv` can also download another Python version |
| R 4.6.2 | `C:\Program Files\R\R-4.6.2\bin\Rscript.exe` (not on the path). Use a private library: `.libPaths("env/r-lib")`, or `renv` |
| .NET SDK 10 | `dotnet` on the path. Put a console project in `scripts/` or `app/` |
| Node and npm | On the path |
| `sqlcmd` | On the path |
| `pdftotext` | `/mingw64/bin/pdftotext` in Git Bash |
| The old environments | `/core/.venv-nlp` (numpy, scipy, scikit-learn, spaCy). Read-only: you can run it, you cannot add to it |

In a git worktree, `env/` is in the worktree. `/core/data/markdown/`, `/core/data/fulltext/` and the old environments are only in the main checkout (rule 12).

## The steps

### Step 1. Claim the run in the ledger

Open [ledger.md](ledger.md). If a row with your code has the status `Running` or `Done`, stop and tell the coordinator. If not, add one row for each experiment that you plan, with the status `Running`. The ledger rules are at the end of this file.

### Step 2. Build the environment and do the package

Follow the package file and [rules.md](rules.md): `spec.md`, the outcome lock, your code, `out/`, `report.md`.

Your working folder must let another agent repeat the run with no help from you:

```
/experiments/<package>/
  spec.md  exposure.md  report.md
  environment.md      runtimes with versions, and the exact commands that build env/ from nothing
  run.md              the exact commands, in order, that go from the inputs to out/ and to the database
  requirements.txt | renv.lock | *.csproj | package-lock.json     the pinned versions
  scripts/ or app/    your code
  env/                the environment (git-ignored; never the only copy of anything)
  out/                results
```

- Fix and record every random seed. Record the versions of the libraries that produce a number in `report.md`.
- Before you close the run, delete `out/` and run the commands of `run.md` again. The numbers must be the same.
- Do not put a password, a key or a connection string in a file.

### Step 3. Put the results in the database

Skip this step if you work in a git worktree (see below).

The database is the SQL Server database `babesiosis-db`. You choose how you write to it. Two ways are given below. With each way, the rows must have the content that "What the rows must hold" describes, and the write must be a command in `run.md`.

**Way A: your own writer.** Write a program in your package that reads `out/` and writes the rows. Get the connection string at run time from `ConnectionStrings:Babesiosis` in `/console/Babesiosis.Console/appsettings.Local.json` (git-ignored). Do not copy it. The writer must:

1. Do all of its work for one experiment in one transaction.
2. Find the experiment row by `experiment_code`. Update it if it is there; insert it if not.
3. Delete the `dbo.experiment_result` rows of that `experiment_id`, then insert the new rows.
4. Touch no row of another code.

A second run of the writer must give the same rows as the first. Do not type results into SQL by hand or through an MCP query: a program must write them from the files in `out/`.

**Way B: the console loader.** Write one file `/experiments/<package>/out/db/<code>.json` and let the loader in `/console/Babesiosis.Console` do the write. This way needs no database code.

```json
{
  "experiment": {
    "code": "SV-01-01-habitus-distance",
    "name": "Habitus grade against distance from the Beagle course (DS05)",
    "description": "The question and the hypothesis, in two sentences.",
    "method": "disease_space_map",
    "dataset": null,
    "parameters": {"package": "SV-01", "role": "primary", "datasets": ["DS02", "DS05"],
                   "independent_sources": ["SRC-A", "SRC-F"], "spec_sha256": "…", "seed": 20261112},
    "script": "/experiments/SV-01/scripts/analyse.R",
    "script_version": "first 12 characters of the SHA-256 of the analysis script",
    "run_utc": "2026-11-13T09:30:00Z",
    "n_subjects": 148, "n_variables": 4, "n_tests": 1,
    "summary": "One or two sentences: the primary result with its effect size, interval and n."
  },
  "associations": [],
  "cluster_assignments": [],
  "results": [
    {"kind": "primary_result", "title": "Primary analysis", "sort_order": 1, "payload": {}},
    {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": {"sections": []}}
  ]
}
```

```
dotnet run --no-build -- --datasets-only --only <code> --dry-run
dotnet run --no-build -- --datasets-only --only <code>
```

The loader checks every load file of every package before it applies `--only`. An error line that names the file of another package is not yours: report it and continue. The three arrays must be present, and the file name must be `<code>.json`. The line "Folder … tidy not found" is a warning; ignore it.

**What the rows must hold** (both ways). The column types are in `/console/Babesiosis.Console/Database/schema.sql`; grep for `CREATE TABLE dbo.experiment`.

`dbo.experiment`, one row:

| Column | Content |
|---|---|
| `experiment_code` | The code. 60 characters at most |
| `name` | A title that a reader understands with no other context. 200 at most |
| `description` | The question and the hypothesis, in two sentences |
| `method` | The method. 50 at most |
| `dataset_id` | `NULL`. `dbo.dataset` is empty. Name the datasets in `parameters` |
| `parameters` | A JSON object with at least `package`, `role` (`primary`, `replication`, `sensitivity` or `descriptive`), `datasets`, `independent_sources`, `spec_sha256` and the seeds. Use `descriptive` for work on files in the "Already seen" list of [rules.md](rules.md) |
| `script`, `script_version` | The path of the main analysis program, and the first 12 characters of its SHA-256 |
| `run_at` | The UTC time of the run |
| `n_subjects`, `n_variables`, `n_tests` | Dogs (not rows), variables and tests in the analysis |
| `summary` | One or two sentences: the primary result with its effect size, interval and n; then the number of tests and the number that passed |

`dbo.experiment_result`, one row for each thing that the view shows:

- `result_kind`: lower case with underscores, 40 characters at most, used once in an experiment. `title`: 200 at most. `sort_order`: the order on the page.
- `payload`: valid JSON, an object or an array. No `NaN` and no `Infinity`: use `null`. (Python: `json.dumps(..., allow_nan=False)`. R: `jsonlite::toJSON(..., na = "null", auto_unbox = TRUE, digits = NA)`.)
- **One row has the kind `interpretation`.** The page shows it as text below the visualisation. Its payload is `{"sections": [{"heading": "…", "paragraphs": ["…"]}]}`. Use these headings: `Question`, `What was done`, `Result`, `What this does not show`. Your code must fill the numbers in this text from its own variables, so that the text and the other payloads agree.
- **A payload holds what the view draws, not the raw data.** Give plot-ready points, the table rows, the effect size with its interval, and n. A figure that your code made (SVG or PNG) can be a payload too: `{"mime": "image/svg+xml", "base64": "…", "alt": "…", "caption": "…"}`. Keep all payloads of one experiment below 1 MB together: the page gets them in one request.
- **No article text** in a payload (rule 9).
- **A null result is stored as fully as a positive result.**

Do not write to `dbo.association` or `dbo.cluster_assignment`: they need dataset rows that do not exist. The page header then shows Subjects, Variables and Tests only, so give the number of tests that passed in `summary`.

**Check the write.** Run this with your own code, with `sqlcmd`, or with the `babesiosis-local-db` MCP server, and copy the answer into your final message:

```sql
SELECT e.experiment_code, e.method, e.run_at, COUNT(r.result_id) AS results,
       SUM(CASE WHEN r.result_kind = 'interpretation' THEN 1 ELSE 0 END) AS interpretation
FROM dbo.experiment AS e LEFT JOIN dbo.experiment_result AS r ON r.experiment_id = e.experiment_id
WHERE e.experiment_code = '<code>'
GROUP BY e.experiment_code, e.method, e.run_at;
```

### Step 4. Make the visualisation

The web app has a menu item "Experiments" (`/experiments`). Its left rail lists every row of `dbo.experiment`, grouped by package, so your experiment gets its link on the rail when step 3 is done: the package is read from the code (`SV-01-02-…` goes under `SV-01`), and the link shows the `name`, the method label and the code. A click opens `/experiments/<code>`: the header (name, summary, description), then your view, then the `interpretation` text, then the parameters.

You add the view. The screen is `/webapp/Babesiosis.Web/src/app/modules/experiments/`. The API sends every result of an experiment as JSON text, so a new method needs no change to the API, the functions or the database. A method with no view shows a notice and the raw JSON; that is not a finished run.

The web app is shared, so this step has less freedom than the analysis. You design the view and its components; you keep to the files below.

**If a view for your method exists, use it.** Make your payloads match the result kinds of its entry in `experiment-views.registry.ts` and go to "Check".

**If not, add a view.** Use an existing view in `views/` as the pattern.

Files that you own (create them):

- `views/experiment-<method with hyphens>-view.component.ts`, `.html` and `.scss`. A standalone component with one required input, `detail` (`ExperimentDetailViewModel`). Read each payload with `parsePayload`. Put the TypeScript interfaces of your payloads in this component file.
- More components, if the view needs them: put them in a folder `views/<method with hyphens>/` and import them from your view component.

The one shared file (other agents edit it at the same time):

- `experiment-views.registry.ts`: one import line, and one entry in `EXPERIMENT_VIEWS` with `method`, `label`, `component` and `kinds` (the result kinds that your view draws; a kind that is not listed is shown a second time as raw JSON).

Read the registry again immediately before you edit it, add only your two lines at the end of their lists, and do not reformat or reorder the lines of other agents. Change no other file of the web app, and add no npm package to it: ask first. The page component, the rail, the menu and the routes belong to the coordinator.

What the view must do:

- Show the primary result first: the effect size, its 95% interval, n, and the number of independent sources.
- Draw with the `fs-*` components (`fs-card`, `fs-chart`, the data grid) and the theme colour tokens, as the pairwise view does. A figure that your code made can be shown as an image from its payload, with its `alt` text and caption; give the numbers behind it in a table or a second payload. The view must be readable in the light and the dark theme.
- Give each chart a subtitle or footnote that names the datasets, n, and the caveat that applies: "exploratory" for an already-seen file, "died includes euthanasia" for the Onderstepoort files, "one species per source" for a contrast between files.
- Show a plain message when a payload is missing. Do not fail.
- Do not use the words "subtype" or "endotype". Do not show a predictive score.

**Check.**

1. Run `npx ng build` in `/webapp/Babesiosis.Web`. It must end with no error.
2. Start the API and the web app with the entries in `/.claude/launch.json` (`babesiosis-api`, then `babesiosis-web` or `babesiosis-web-4401`). If a port is in use, a server is already running: use it. Do not start these two servers with shell commands.
3. Open `/experiments/<code>`. Confirm that the visualisation shows the numbers of `report.md`, that the interpretation text is below it, that no raw JSON card remains, and that the browser console has no error.

If you have no browser tools, do item 1 only and write `built, not seen` in the View column of the ledger. The coordinator does items 2 and 3.

### Step 5. Close the run

Update your rows in [ledger.md](ledger.md). Then give a final message with:

- each experiment code and its ledger status;
- the primary result in one sentence, or the reason for `Failed` or `Blocked`;
- the languages and main libraries that you used, and anything that you installed;
- the answer of the check query;
- every file that you changed outside your working folder;
- every deviation from `spec.md`;
- each decision that the user must make.

## If something goes wrong

| Situation | Do this |
|---|---|
| A dependency is not `Done` in [index.md](index.md) | Do not start. Rule 15 of [rules.md](rules.md) |
| A package will not install | Try another version, another registry in the list, or another library that does the same analysis. Record what you tried in `environment.md` |
| The tool that you need has only a system installer | Stop and ask |
| The analysis cannot be done as the spec says | Report the deviation. Store the result that you have, with the deviation in the `interpretation` text |
| The analysis cannot be done at all | Store nothing. Ledger status `Blocked`, with the reason and what is needed |
| Your writer fails in the middle | The transaction rolls back. Correct the code and run it again. Do not repair rows by hand |
| `ng build` fails in a file that is not yours | Do not repair it. Report the file and the error |
| You must run an experiment again | Keep the code. Write again. Add the new date and the reason to the Notes of the ledger row |

## If you work in a git worktree

The ledger of your branch is not the ledger of the other agents, and the coordinator must be able to repeat your database write from the merged files. Do steps 2 and 4 (to `ng build`), and make the writer or the load file of step 3 ready. Do not write to the database, and do not edit the ledger. Put your ledger rows and the write command in your final message. The coordinator merges the branch, builds `env/` from `environment.md`, runs the write, checks the page and writes the rows.

## The ledger

[ledger.md](ledger.md) has one row for each experiment code. It records runs; the plan and the package status stay in [index.md](index.md), which only the coordinator edits.

| Column | Holds |
|---|---|
| Code | The experiment code |
| Package | `SV-01` |
| Method | The `method` of the experiment row |
| Status | `Running`, `Done`, `Failed` or `Blocked` |
| Run (UTC) | The `run_at` of the last run, as a date |
| Spec hash | The first 12 characters of the SHA-256 of `spec.md`; `–` if the package has no outcome lock |
| Database | `written <date>`, or `no` |
| View | `seen <date>`, `built, not seen`, or `no` |
| Report | The path of `report.md` |
| Notes | The stack (`R 4.6 + lme4`); the primary result in one clause; the reason for a failure; the date and reason of each run after the first |

Rules:

- Add your row before you start (step 1) and update it when you stop (step 5). Do not leave a row at `Running` when you end your session: use `Blocked` or `Failed` with the reason.
- `Done` means that the four conditions at the top of this file are true. If the view is `built, not seen`, the status stays `Running` until the coordinator has seen the page.
- Edit only your own rows. Read the file again immediately before each edit, and change one row in one edit.
- Do not delete a row. A code that is no longer wanted gets the note `withdrawn <date>`, and the coordinator removes it from the database.
- The ledger and the database must agree. If they do not, the commands in `run.md` decide: run the write again and correct the ledger.
