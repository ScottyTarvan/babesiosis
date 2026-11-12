# Rules and contracts for every agent

Read this file once before you start any package. The list of packages is in [index.md](index.md). The data facts are in [data.md](data.md).

## Rules

These rules come from `/CLAUDE.md` and from the limits of the data. They are not optional.

1. **No prediction, no subtypes.** Every dataset is small for its feature count. Do not fit or report a predictive model. Do not call a cluster or an axis a "subtype" or an "endotype". Unsupervised work is hypothesis-generating: report it with resampling stability and a stated detectable effect.
2. **Count independent evidence.** Articles: merge by `cohort_id` (`/core/cohorts.json`). Datasets: merge by `independent_source`. [data.md](data.md) lists the files that must never be pooled.
3. **Only `CB` articles are canine evidence.** `HU` articles are human comparators. `BG` articles are background.
4. **Categories are NLP labels with no human review.** Do not use `primary_category` as proof that a topic is or is not studied.
5. **About 230 of 481 article notes rest on the abstract only.** Check `source_format` in the front matter of `/core/data/markdown/<ID>.md` before you rely on a text.
6. **Species is aliased with source, country, assay and severity definition.** There is one dog-level source per species for each label. Analyse inside one species, or report within-study contrasts side by side. Never attribute a between-file difference to species.
7. **"Died" includes euthanasia for poor prognosis** in the Onderstepoort files. Say so in every result that uses it.
8. **`/core/` is read-only.** Write nothing under `/core/`. Files in `/core/data/raw/` are read-only by project rule.
9. **Full texts are copyrighted.** `/core/data/fulltext/` and `/core/data/markdown/` are git-ignored. Do not copy article text into outputs, except the short verbatim quotes that the extraction schema requires. Do not commit or publish them.
10. **Never read whole:** `/core/articles.jsonl` (1.4 MB; stream it), `/docs/pipeline-spec.md`.
11. **Tools and environments.** Each package chooses its own language and libraries (Python, R, .NET or others) and builds its own environment in `/experiments/<package>/env/`. Install what the analysis needs there, with pinned versions. The limits and the tools on the machine are in [run-instructions.md](run-instructions.md), section "Your freedom, and its limits". Do not install into, or change, the old environments `/core/.venv` and `/core/.venv-nlp`. The reader `shared/io/rawio.py` (last section of this file) is optional.
12. **Worktrees.** The old virtual environments, `/core/data/markdown/` and `/core/data/fulltext/` are git-ignored, so a new git worktree does not contain them. Use the absolute paths of the main checkout (`C:\Workspaces\Babesiosis\core\...`) for those. `/core/data/raw/` is tracked and is present in every worktree.
13. **Outside requests.** Do not put the user's name, email address or project details in a web or PubMed request. Cite every literature claim with a DOI link.
14. **Git.** Do not commit, switch branches, stash or reset unless the user tells you to. Other sessions share the checkout.
15. **Decisions that belong to the user.** Stop and ask before you: contact an author; add or change anything under `/core/`; edit `/docs/index.md` or the shared plan files in this folder (`index.md`, `rules.md`, `data.md`); or run a package before its dependencies (the wave table in [index.md](index.md)).
16. **Report faithfully.** A null result is a result. If a check fails, report the failure with the output.

## Workspace and ownership

The plan and the work are both in `/experiments/`.

```
/experiments/
  index.md  rules.md  data.md      the plan: shared documents
  SV-01-disease-space.md  ...      one description file for each package
  shared/                          owner: SV-G1 only
    io/rawio.py                    reader for xlsx and docx files (already present)
    tidy/<dataset>.features.json
    tidy/<dataset>.outcomes.json
    dictionary.csv
  SV-G1/ ... SV-10/ SV-INT/        one working folder for each package, created when the package starts
    spec.md                        frozen before any outcomes file is opened
    exposure.md                    one line for each outcomes file the package opened
    environment.md  run.md         how to build env/ and how to repeat the run (run-instructions.md, step 2)
    scripts/ or app/               the package's own code, in any language
    env/                           the package's own environment (git-ignored)
    out/
    report.md
```

**Paths.** A path that starts with `/` is from the repository root. A path that starts with `shared/` or `SV-` is relative to `/experiments/`. A path that starts with `out/` is relative to the working folder of the package.

**Ownership rule.** An agent writes only inside the working folder of its own package. Only SV-G1 writes in `shared/`. Only the coordinator edits `index.md` (the Status column), `rules.md`, `data.md` and the package description files. Two agents never write the same file. A package that fans out to sub-agents gives each sub-agent its own sub-folder or its own files.

## Tidy file contract (written by SV-G1, read by all)

`<dataset>.features.json`:

```json
{
  "dataset_id": "S-CB050",
  "independent_source": "SRC-A",
  "species": "B. rossi",
  "built_from": [{"file": "/core/data/raw/S-CB050/PMC7040022_supplementaryFiles.zip!Table_1.DOCX", "sha256": "..."}],
  "variables": [{"name": "wbc", "unit": "10^9/L", "original": "WBC (x10^9/L)", "floor": null, "ceiling": null}],
  "records": [{"dog_id": "S-CB050:d001", "group": "infected", "timepoint": "admission", "day": null,
               "values": {"wbc": 4.83}, "censored": {"il2": "floor"}}],
  "cleaning_notes": ["..."]
}
```

`<dataset>.outcomes.json` holds the severity labels and nothing else:

```json
{
  "dataset_id": "S-CB050",
  "outcomes": [{"name": "died", "definition": "death or euthanasia for poor prognosis before discharge", "includes_euthanasia": true}],
  "records": [{"dog_id": "S-CB050:d001", "values": {"died": 0}}]
}
```

- `group` in the features file is only `infected`, `control` or `comparator` (for example IMHA). It is not a severity label.
- `dog_id` must not reveal the label. In S-CB017 the label is in the original ID prefix (`B` = uncomplicated, `BK` = complicated). SV-G1 gives neutral IDs and keeps the original ID only in the outcomes file.
- Proxies that earlier work used as severity (DS05 habitus grade and the authors' derived classes) go in the outcomes file.
- Missing values are `null`. Values at an assay floor or ceiling keep the reported number and get an entry in `censored`.
- `dictionary.csv` columns: `harmonised_name, dataset_id, original_column, unit, conversion, note`.

## Outcome lock

The labelled files are too small to survive a second look. Each analysis package follows this order:

1. Write `spec.md` from the features files only: the primary analysis, the family of tests, the stability checks, and what result would count against the hypothesis.
2. Record the SHA-256 of `spec.md` in `report.md`.
3. Add a line to the package's own `exposure.md`: date, outcomes file, spec hash. SV-INT combines these files into one log.
4. Open the outcomes file and run the analysis as written.
5. Report every deviation from the spec, with the reason.

**Already seen before this plan** (treat as exploratory, not confirmatory):

- DS05: the old EXP01, EXP02 and EXP06 results. Habitus correlated with haematocrit (rho 0.54), red cell count, haemoglobin, monocytes (-0.42) and band neutrophils (-0.37). Illness duration had only weak associations (rho 0.23 to 0.26). Breed group related to weight and habitus (eta² 0.07). Age related to globulin.
- S-CB050: median age was 29 months in dogs that died and 20 months in survivors (a format probe on 2026-11-12). The published article reports band neutrophils, MPXI and cytokines by outcome.
- All published group comparisons in the linked articles (CB017, CB050, CB112, CB126, CB145, CB517).

Each package lists the primary analysis that the plan fixes now. The agent may sharpen it in `spec.md` before the outcome lock opens, and must not change it afterwards.

## Statistical conventions

- Prefer rank-based tests and exact or permutation p-values (10,000 permutations or exact enumeration). Fix and record every random seed.
- Report an effect size with a 95% interval for every test: Cliff's delta, Spearman rho, Hodges-Lehmann difference, or an odds ratio. Use 2,000 bootstrap resamples, resampling dogs, not rows.
- Control the false discovery rate (Benjamini-Hochberg) inside a family that the spec declares. State the family size.
- Repeated samples of one dog are not independent. Resample and permute by dog.
- State the detectable effect. Approximate values at 80% power and two-sided alpha 0.05: 15 vs 126 dogs, 0.76 SD; 12 vs 85, 0.86 SD; 18 vs 13, 1.05 SD; 14 vs 18, 1.0 SD; n = 148, |rho| 0.23; n = 103, |rho| 0.28.
- Write plot-ready CSV files for every figure, so that the numbers behind it can be checked. You can install a plotting library in your environment and make the figure too.

## Report template (`report.md` in each package)

1. Question and the hypothesis, in two sentences.
2. Inputs: files with SHA-256, and the spec hash.
3. What was done, including every deviation from the spec.
4. Results: the primary analysis first, with effect size, interval, n and independent sources.
5. Stability and sensitivity checks.
6. Confounders: what was handled, and what could not be handled.
7. What this does not show.
8. Verified in files, taken from documentation, or inferred.
9. Next step, and any decision the user must make.

## The reader for xlsx and docx files

This reader is optional: a package can use openpyxl, readxl or another library in its own environment. `shared/io/rawio.py` has three functions and uses only the standard library:

- `read_xlsx(src)` returns `{sheet name: list of rows}`. `src` is a path or bytes. Cells are text or `None`.
- `read_docx_tables(src)` returns a list of tables. Each table is a list of rows of cell text.
- `fnum(x)` returns a number from text with a decimal comma or a `<` or `>` sign, or `None`.

Import it with `sys.path.insert(0, r"C:\Workspaces\Babesiosis\experiments\shared\io")` and `from rawio import read_xlsx, read_docx_tables, fnum`.

Numeric cells come back as text and can carry floating-point noise (`0.1400000000000000`). Dates are stored as text in DS05. To read a file inside a zip, pass `zipfile.ZipFile(path).read(name)` to the reader as bytes. It was tested on 2026-11-12 on the DS05, DS02, DS04, DS07 and S-CB017 workbooks and on the S-CB050 table.
