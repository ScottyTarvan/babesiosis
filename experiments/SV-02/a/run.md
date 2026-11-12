# SV-02a run

From `/experiments/SV-02/a/` in Git Bash, after `environment.md`.

```bash
rm -rf out ../out/db/SV-02-01-load-by-outcome.json
PY=env/py/Scripts/python.exe
$PY -I scripts/analyse.py      # checks the SHA-256 of spec.md, reads SV-G2 rows and the appraisal notes, writes out/
$PY -I scripts/build_load.py   # writes /experiments/SV-02/out/db/SV-02-01-load-by-outcome.json
```

`analyse.py` stops if `spec.md` changed, or if the keyword screen of `/core/articles/CB*.md` finds a note that `curated_note_hits.csv`
has no decision for (or the reverse). No random step; seed 20261112 recorded. Runtime about 2 s.

Database write (way B), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-02-01-load-by-outcome --dry-run
dotnet run --no-build -- --datasets-only --only SV-02-01-load-by-outcome
```

Check query: step 3 of `/experiments/run-instructions.md`, with the code `SV-02-01-load-by-outcome`.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-load-outcome-synthesis-view.component.*`
(method `load_outcome_synthesis`); build with `npx ng build` in `/webapp/Babesiosis.Web`.

## Files in out/

| File | Holds |
|---|---|
| `load_by_outcome.csv` | Every load row compared with a severity or outcome definition (6 units): direction, significance, load method, sample timing, effect and interval where computable, detectable effect |
| `cells.csv` | The pooling cells (species group × outcome class) and why none was pooled |
| `moderators.csv` | Load method and sample timing by unit |
| `sensitivity.csv` | Equal-split group sizes (CB220) and the excluded experimental dose contrast (CB105) |
| `damage_by_load_group.csv` | The inverse question: markers in groups defined by load (CH09, CB187, CB241) |
| `low_load_list.csv` | Severe disease at low load, protection at unchanged load |
| `excluded_load_rows.csv` | Load rows outside the primary set, with the reason |
| `results.json` | Every number, the input hashes and the library versions |
