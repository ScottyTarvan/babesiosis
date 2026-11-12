# SV-META run

From `/experiments/SV-META/` in Git Bash, after `environment.md`. Inputs: the `out/` files of every other package, the SV-G1 tidy files,
`scripts/candidates.json` (candidate definitions, novelty, leads) and `refutation/K*.json` (the refutation attempts, written once by
sub-agents with a fresh context; `refutation/scripts/` holds their check scripts).

```bash
rm -rf out
env/py/Scripts/python.exe -I scripts/census.py        # out/census_raw.csv
env/py/Scripts/python.exe -I scripts/check_census.py  # stops if a number is not at its cited file and line
env/py/Scripts/python.exe -I scripts/themes.py        # out/themes.csv, out/theme_indicators.json (seed 20261112, about 15 s)
env/py/Scripts/python.exe -I scripts/screen.py        # out/census.csv, candidates.csv, refutation.csv, leads.csv, tiers.json
env/py/Scripts/python.exe -I scripts/build_load.py    # out/db/SV-META-01-research-leads.json
```

`themes.py` stops if `spec.md` changed after the lock. `screen.py` stops if a census row that passes the screen has no candidate, or if
there are more than 10 leads.

Database write (way B, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-META-01-research-leads --dry-run
dotnet run --no-build -- --datasets-only --only SV-META-01-research-leads
```

Check query: step 3 of `/experiments/run-instructions.md` with the code `SV-META-01-research-leads`.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-meta-review-view.component.*` (method `meta_review`).
