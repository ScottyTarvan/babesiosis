# SV-03 run

From `/experiments/SV-03/` in Git Bash, after `environment.md`.

```bash
rm -rf out
PY=env/py/Scripts/python.exe
PYTHONIOENCODING=utf-8 $PY -I scripts/analyse.py      # reads SV-G2/associations_v2.csv and definitions_v2.csv; writes out/*.csv and out/results.json
PYTHONIOENCODING=utf-8 $PY -I scripts/build_load.py   # out/db/<code>.json (2 load files); every number in the text comes from out/
```

No random numbers (no seed needed). Runtime about 3 s.

Database write (way B of `/experiments/run-instructions.md`, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-03-01-evidence-matrix,SV-03-02-definition-map --dry-run
dotnet run --no-build -- --datasets-only --only SV-03-01-evidence-matrix,SV-03-02-definition-map
```

Check query: step 3 of `run-instructions.md`, with `WHERE e.experiment_code LIKE 'SV-03-%'`.

View (method `evidence_matrix`): `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-evidence-matrix-view.component.*`,
registered in `experiment-views.registry.ts`; build with `npx ng build` in `/webapp/Babesiosis.Web`.

Repeat check (done 2026-11-12): deleted `out/`, ran the two scripts; every file byte-identical except `run_utc` in the two load files.

## Files in out/

| File | Holds |
|---|---|
| `definition_map.csv` | One row per severity definition: unit, species, setting, outcome class, components, euthanasia, tested rows, markers in their own definition |
| `definition_components.csv`, `definition_outcome_classes.csv` | Independent units by component (or outcome class) and species group |
| `circularity.csv` | Tested rows whose marker is part of their own definition, by marker and reason |
| `evidence_matrix.csv` | Primary matrix: every marker x outcome class x species cell, unit counts by call, consistency, circularity, sensitivity sets S1-S4 |
| `evidence_matrix_collapsed.csv` | Deviation D1: outcome classes merged within species (cells with 2 or more tested units) |
| `unit_calls.csv` | One row per unit x marker x outcome class x species x analysis family: row calls and the unit call |
| `pooled.csv`, `pooled_points.csv` | Pooled estimates and their unit points (empty: no cell met the rule) |
| `pooling_near_misses.csv` | Cells with 2 units with a usable summary |
| `conflicts.csv`, `conflict_units.csv` | The named conflicts: verdicts and the unit calls behind them |
| `selective_reporting.csv` | Share of non-significant rows by article |
| `results.json` | Every number above, plus summaries and input hashes |
| `db/` | The two load files |
