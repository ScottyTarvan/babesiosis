# SV-G1 run

From `/experiments/SV-G1/` in Git Bash, after `environment.md`. Every script is deterministic (no random numbers;
the neutral dog IDs come from a salted SHA-256 order, salt `SV-G1-2026-11-12` in `scripts/tidylib.py`).

```bash
rm -rf out ../shared/dictionary.csv
for d in DS02 DS03 DS05 S-CB050 S-CB517 S-CB017 S-CB516 DS07 DS04; do rm -f ../shared/tidy/$d.features.json ../shared/tidy/$d.outcomes.json; done
PY=env/py/Scripts/python.exe
$PY -I scripts/tidy_ds02.py      # DS02 first: DS03 links its experimental dogs to the DS02 tidy file
$PY -I scripts/tidy_ds03.py
$PY -I scripts/tidy_ds05.py
$PY -I scripts/tidy_scb050.py    # S-CB050 before S-CB517: S-CB517 compares its cytokines with the S-CB050 tidy file
$PY -I scripts/tidy_scb517.py
$PY -I scripts/tidy_scb017.py
$PY -I scripts/tidy_scb516.py
$PY -I scripts/tidy_ds07.py
$PY -I scripts/tidy_ds04.py
$PY -I scripts/summarise.py      # shared/dictionary.csv, out/coverage.csv, out/datasets.csv, out/summary.json, out/db/<code>.json
```

Each tidy script prints its counts and the checks that failed. `summarise.py` stops if a tidy file is missing.

Database write (way B of `run-instructions.md`, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-G1-01-data-layer-coverage --dry-run
dotnet run --no-build -- --datasets-only --only SV-G1-01-data-layer-coverage
```

The check query of `run-instructions.md` step 3 confirms the write. The view is
`/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-data-layer-coverage-view.component.*`
(method `data_layer_coverage`); build it with `npx ng build` in `/webapp/Babesiosis.Web`.

Repeat check: delete `out/` and the tidy files, run the commands above, and compare (`run_utc` and `script_version` aside, the
load file and every tidy file must be byte-identical).
