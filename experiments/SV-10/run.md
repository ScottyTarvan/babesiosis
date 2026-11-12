# SV-10 run

From `/experiments/SV-10/` in Git Bash, after `environment.md`.

```bash
rm -rf out
PY=env/py/Scripts/python.exe
$PY -I scripts/power.py        # out/power.csv, out/power.json (every sample-size scenario and the SV-05 formula check)
$PY -I scripts/build_load.py   # out/memo_*.md (memos/ with the tables filled) and out/db/<code>.json
```

Runtime under 1 s. No random numbers. The hand-written memos are in `memos/`; the sub-agents' research notes and PubMed search log
are in `research/`. Neither is under `out/`, so `rm -rf out` loses nothing.

Database write (way B, the console loader), from `/console/Babesiosis.Console`:

```bash
for c in SV-10-01-parasite-genotype SV-10-02-host-genetics SV-10-03-minimum-dataset; do
  dotnet run --no-build -- --datasets-only --only $c --dry-run
  dotnet run --no-build -- --datasets-only --only $c
done
```

Check query: step 3 of `/experiments/run-instructions.md`, with each code.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-study-design-view.component.*` (method `study_design`).
