# SV-09 run

From `/experiments/SV-09/` in Git Bash, after `environment.md`.

```bash
rm -rf out
PY=env/py/Scripts/python.exe
$PY -I scripts/analyse.py      # checks the SHA-256 of the 4 features files, the 2 SV-01 pseudo-stage files, spec.md and the 3 outcomes files (against exposure.md); writes out/
$PY -I scripts/build_load.py   # out/db/<code>.json (3 load files); every number in the text comes from out/results.json
```

Seed 20261112, one generator, fixed order of draws (step 1, 2, 3, then A4). Runtime about 10 s.

Database write (way B), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-09-01-ds05-residual-axes,SV-09-02-axis-congruence,SV-09-03-axis-outcome --dry-run
dotnet run --no-build -- --datasets-only --only SV-09-01-ds05-residual-axes,SV-09-02-axis-congruence,SV-09-03-axis-outcome
```

Check query: step 3 of `run-instructions.md`, with `WHERE e.experiment_code LIKE 'SV-09-%'`.

View (method `axis_replication`): `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-axis-replication-view.component.*`, registered in `experiment-views.registry.ts`.

Repeat check (done 2026-11-12): deleted `out/`, ran both scripts; `results.json` and every CSV byte-identical; load files differ only in `run_utc`.

## Files in out/

| File | Holds |
|---|---|
| `loadings.csv` | DS05 residual-axis loadings (block `ds05_main`) and block component loadings in DS05 and each target |
| `congruence.csv` | Tucker phi per block and component, bootstrap interval, uniform baseline, label-permutation p |
| `axis_outcome.csv` | Axis score against death (S-CB050) and complicated (S-CB017), comparisons and sensitivities A1 to A4 |
| `axis_scores_by_label.csv` | Score and label per dog (behind the strip plots) |
| `ds05_scree.csv`, `ds05_scores.csv` | Eigenvalues with parallel-analysis thresholds; DS05 axis scores per dog |
| `results.json` | Every number |
| `db/` | The three load files |
