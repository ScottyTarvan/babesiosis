# SV-05 run

From `/experiments/SV-05/` in Git Bash, after `environment.md`.

```bash
rm -rf out
PY=env/py/Scripts/python.exe
$PY -I scripts/analyse.py      # checks the SHA-256 of spec.md, the 3 features files, S-CB050.outcomes.json and SV-04/out/perturbation.csv (the last two against exposure.md), then writes out/
$PY -I scripts/build_load.py   # out/db/<code>.json (2 load files); every number in the text comes from out/results.json
```

Seed 20261112, one generator, draws in the order of spec.md. Runtime about 10 s.

Database write (way B, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-05-01-age-death,SV-05-02-age-form --dry-run
dotnet run --no-build -- --datasets-only --only SV-05-01-age-death,SV-05-02-age-form
```

Check query: step 3 of `run-instructions.md`, with `WHERE e.experiment_code LIKE 'SV-05-%'`.

View (method `age_sex_contrast`): `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-age-sex-contrast-view.component.*`,
registered in `experiment-views.registry.ts`; build with `npx ng build` in `/webapp/Babesiosis.Web`.

Repeat check (done 2026-11-12): deleted `out/`, ran the two scripts; every file is byte-identical except `run_utc` in the two load files.

## Files in out/

| File | Holds |
|---|---|
| `age_contrasts.csv` | One row per test of families A and B: source, n, medians or shares, effect with 95% interval, Cliff's delta, p, BH q |
| `results.json` | Every number: families A and B, secondary contrasts, sensitivities S1-S4, check C1, the age-band profile and the decision rule |
| `db/` | The two load files |
