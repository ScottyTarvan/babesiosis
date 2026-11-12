# SV-02b run

From `/experiments/SV-02/b/` in Git Bash, after `environment.md`.

```bash
rm -rf out ../out/db/SV-02-02-beagle-reaction-norms.json
PY=env/py/Scripts/python.exe
$PY -I scripts/analyse.py      # checks the SHA-256 of spec.md, reads the DS02 tidy files, writes out/
$PY -I scripts/build_load.py   # writes /experiments/SV-02/out/db/SV-02-02-beagle-reaction-norms.json
```

`analyse.py` stops if `spec.md` changed. Nothing is random; seed 20261112 recorded. Runtime about 1 s.

Database write (way B), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-02-02-beagle-reaction-norms --dry-run
dotnet run --no-build -- --datasets-only --only SV-02-02-beagle-reaction-norms
```

Check query: step 3 of `/experiments/run-instructions.md`, with the code `SV-02-02-beagle-reaction-norms`.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-reaction-norm-view.component.*`
(method `reaction_norm`); build with `npx ng build` in `/webapp/Babesiosis.Web`.

## Files in out/

| File | Holds |
|---|---|
| `reaction_norms.csv` | Per dog and measure: n points, OLS slope with 95% t interval, Theil-Sen slope, damage at 1% and 5% parasitaemia, peak load and damage at peak |
| `points.csv` | The 22 pre-treatment dog-days used (plot-ready): load, log load, haematocrit, lactate, habitus |
| `pooled_lines.csv` | The pooled descriptive line per measure and each dog's mean residual from it |
| `readings.csv` | The spec's reading rule, criterion by criterion, per measure |
| `sensitivity.csv` | Per-dog slopes and readings under each sensitivity check |
| `results.json` | Every number, the input hashes and the library versions |
