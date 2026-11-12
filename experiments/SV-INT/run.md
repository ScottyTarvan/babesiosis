# SV-INT run

From `/experiments/SV-INT/` in Git Bash, after `environment.md`.

```bash
rm -rf out
env/py/Scripts/python.exe -I scripts/build.py
```

`build.py` checks every quoted number in `scripts/synthesis.json` against the cited report and stops if one is missing; checks that every
contributing experiment is `Done` in the ledger and that every Done experiment is used; writes `out/synthesis_table.csv`,
`out/decisions.csv`, `out/exposure_log.md` and `out/db/SV-INT-01-integration-report.json`. No random numbers. Under 1 s.

Database write (way B, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-INT-01-integration-report --dry-run
dotnet run --no-build -- --datasets-only --only SV-INT-01-integration-report
```

Check query: step 3 of `/experiments/run-instructions.md` with the code `SV-INT-01-integration-report`.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-integration-synthesis-view.component.*` (method `integration_synthesis`).
