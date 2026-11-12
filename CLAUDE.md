# Canine babesiosis review

Rapid scoping review of canine babesiosis pathophysiology (window 2006-10-23 to 2026-10-23, complete), with a loader and a web app over its outputs.

**Documentation is in [docs/](docs/index.md). Read `docs/index.md` first, then only the one file the task needs.**

## Layout

| Folder | Holds |
|---|---|
| `core/` | The review data: `articles.jsonl` (481 articles), `datasets.jsonl` (57 records), `cohorts.json`, `ids.json`, `articles/` (one note per article), `search/` (search record), `data/` (downloads, full texts, terms, severity). No scripts, experiments or rendered reports |
| `console/Babesiosis.Console` | Loader: `core/` files → SQL Server |
| `webapp/` | Angular + Azure Functions app over the database. Agent guides: `webapp/.claude/agents/agents.md` |
| `docs/` | All project documentation |
| `clinical/` | Clinical manual for veterinarians: one page per clinical syndrome and its treatments, researched by agents and shown on the web app's Clinical screen. Start at `clinical/index.md` |
| `experiments/` | Research experiments on disease severity: one file per experiment, with their scripts and outputs. Start at `experiments/index.md` |

In `docs/` and `core/`, a path with no prefix is relative to `core/`. A path that starts with `/` is from the repository root.

## Rules

- **Whole-set questions: use the structured files** (`core/articles.jsonl`, `core/datasets.jsonl`, `core/cohorts.json`). Join on the article `id`.
- **Never read these whole**: `core/articles.jsonl` (1.4 MB), `docs/pipeline-spec.md` (37 KB), and `core/data/syndromes/mentions.jsonl` (140 MB; the `syndromes/` folder is not in every checkout). Stream them, or grep for an ID or a heading.
- **Only `CB` articles are canine evidence** (444). `HU` (27) are human comparators and `BG` (10) are background.
- **Articles are not independent evidence.** Count with `cohort_id` (articles) and `independent_source` (datasets).
- **Free-text fields are not normalised** (`language`, `country`, `evidence_type`). Match on keywords.
- **Categories are assigned by NLP, with no human review.**
- **Every dataset is small for its feature count.** No predictive ML. Do not call clusters "subtypes".
- **Full texts are copyrighted.** `core/data/fulltext/` and `core/data/markdown/` are git-ignored. Do not commit or publish them.
- **`core/` holds data only.** Put new scripts and experiment work outside `core/`, and write a row in `docs/index.md` for them. The old pipeline scripts and experiments were deleted on 2026-11-12 (`docs/index.md` says how to read one from git); the dataset tables in the database are empty (`dbo.experiment` and `dbo.experiment_result` hold the runs of `/experiments/`). Files in `core/data/raw/` are read-only.
- **Python**: run as `python -I` with an environment in `core/`. `.venv` has numpy; `.venv-nlp` has numpy, scipy, scikit-learn and spaCy. Do not install packages into these two.
- **Experiments are free to choose tools.** A package in `experiments/` builds its own environment in `experiments/<package>/env/` (Python, R, .NET; any library) and writes its own results to the database. The limits are in `experiments/run-instructions.md`.
- **Counts in `docs/` have a date.** Re-count before you quote one as current.
- **Run the apps with the entries in `.claude/launch.json`**, not with shell commands.

## When you change documentation

- Put new documents in `docs/` and add a row to `docs/index.md`. Write each fact in one document and link to it from the others.
- Delete a plan when its work is done. Git keeps the history.
- Keep this file short: it is loaded in every session. Detail belongs in `docs/`.
- A `README.md` stays beside the files it describes.
