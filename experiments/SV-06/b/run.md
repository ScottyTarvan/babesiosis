# SV-06b run

From `/experiments/SV-06/b/` in Git Bash, after `environment.md`. Inputs: `shared/tidy/DS07.features.json`, `shared/tidy/DS07.outcomes.json` (SV-G1) and `/core/data/raw/DS07/B_Proteins.txt` (read-only, master check).

```bash
env/py/Scripts/python.exe -I scripts/analyse.py       # out/ds07_candidates.csv, dog_values.csv, sensitivity_lopo.csv, results.json
env/py/Scripts/python.exe -I scripts/build_load.py    # out/master_check.csv, out/db/SV-06-02-ds07-candidate-tests.json
env/py/Scripts/python.exe -I scripts/write_db.py --dry-run
env/py/Scripts/python.exe -I scripts/write_db.py      # dbo.experiment + dbo.experiment_result for SV-06-02-ds07-candidate-tests, one transaction
env/py/Scripts/python.exe -I scripts/check_db.py      # the check query of run-instructions.md step 3
```

Seeds: 20261112 for every permutation run; 20261112 + protein index for each bootstrap. The connection string is read at run time from `/console/Babesiosis.Console/appsettings.Local.json`.

Rerun check: delete `out/` and run the first two commands again. Every file except the `run_utc` field of the load file must be byte-identical (checked 2026-11-12).
