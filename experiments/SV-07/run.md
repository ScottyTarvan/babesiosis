# SV-07 run

From `/experiments/SV-07/` in Git Bash, after `environment.md`.

```bash
rm -rf out
PY=env/py/Scripts/python.exe
$PY -I scripts/analyse.py      # reads the raw files and shared/tidy/DS05.features.json, writes out/*.csv and out/results.json
$PY -I scripts/build_load.py   # out/author_query_draft.md and out/db/SV-07-01-linkage-audit.json
```

Runtime about 30 s (the 10! enumeration of step 1 takes most of it). No random numbers.

Database write (way B, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-07-01-linkage-audit --dry-run
dotnet run --no-build -- --datasets-only --only SV-07-01-linkage-audit
```

Check query: step 3 of `/experiments/run-instructions.md`, with the code `SV-07-01-linkage-audit`.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-linkage-audit-view.component.*` (method `linkage_audit`).

Repeat check (done 2026-11-12): delete `out/`, run the two scripts twice; every CSV, `results.json` and the query draft are
byte-identical; the load file differs only in `run_utc`.

## Files in out/

| File | Holds |
|---|---|
| `linkage.csv` | Every link: `dataset_a, id_a, dataset_b, id_b, basis, fields_matched, certainty` |
| `ds04_vs_scb050.csv` | Steps 1b and 2: each DS04 haematology row against all S-CB050 rows |
| `ds04_icterus_join.csv` | Step 1c: icterus wording against bilirubin |
| `ds04_vs_ds03.csv` | Added check D3: DS04 rows against DS03 on haematocrit and reticulocyte % |
| `ds03_vs_scb050_candidates.csv`, `ds03_unique_pairs.csv` | Step 3: every age-weight-sex twin pair, with share counts |
| `ds03_summary.csv`, `ds03_match_rates.csv`, `ds03_order_check.csv` | Step 3 summaries, chance baseline, study-number order (D2) |
| `ds06_series.csv`, `ds06_assignment_scores.csv` | Step 4 |
| `ds07_numbering_chance.csv`, `ds07_ds04_consistency.csv` | Step 5 |
| `results.json` | Every number above plus input hashes |
| `author_query_draft.md` | The draft query (not sent) |
| `db/` | The load file |
