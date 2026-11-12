# SV-04 run

From `/experiments/SV-04/` in Git Bash, after `environment.md`.

```bash
rm -rf out
PY=env/py/Scripts/python.exe
$PY -I scripts/analyse.py      # checks the SHA-256 of the 3 features files, of the 2 outcomes files (against exposure.md) and of spec.md, then writes out/
$PY -I scripts/build_load.py   # out/db/<code>.json (2 load files); every number in the text comes from out/results.json
```

Seed 20261112, one generator, fixed order of draws (spec analyses first, deviation D1 last). Runtime about 5 s.

Database write (way B of `/experiments/run-instructions.md`, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-04-01-il8-direction,SV-04-02-response-size-balance --dry-run
dotnet run --no-build -- --datasets-only --only SV-04-01-il8-direction,SV-04-02-response-size-balance
```

Check query: step 3 of `run-instructions.md`, with `WHERE e.experiment_code LIKE 'SV-04-%'`.

View (method `cytokine_conflict`): `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-cytokine-conflict-view.component.*`,
registered in `experiment-views.registry.ts`; build with `npx ng build` in `/webapp/Babesiosis.Web`.

Repeat check (done 2026-11-12): deleted `out/`, ran the two scripts; every file is byte-identical except `run_utc` in the two load files.

## Files in out/

| File | Holds |
|---|---|
| `contrasts.csv` | Severe vs non-severe, 6 analytes: S-CB050 and S-CB017 day 1 (primary, floors as reported), S-CB017 day 7 (check C2), and both files with floors at half the floor (S2) |
| `infected_vs_control.csv` | Infected vs healthy controls, 6 analytes, both files (deviation D1; no outcome used) |
| `perturbation.csv` | One row per infected dog: severe flag, perturbation count (above, below), z-score version, IL-8 and MCP-1 percentiles, balance index |
| `ds02_courses.csv` | One row per Beagle and analyte: baseline, day 4, 6, 8 (log2(x + 1)), changes, day-to-day change before treatment |
| `ds02_series.csv` | The DS02 series behind the figure |
| `results.json` | Every number, including checks C1 and C2, sensitivities S1 and S2, and the decision rules |
| `db/` | The two load files |
