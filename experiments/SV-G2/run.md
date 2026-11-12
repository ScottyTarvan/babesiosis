# SV-G2 run

All commands from `/experiments/SV-G2/` unless stated. Python: `env/py/Scripts/python.exe` (or any Python 3.12+), always with `-I`. Standard library only.

## 1. Schema and batches (done once, 2026-11-12)

```
python -I scripts/make_schema_v2.py          # -> association_schema_v2.json
```

`batches/batches.json` holds the batch lists (B00 = the 10 pilot articles, B01-B11), the blind second sample (24 articles, `random.seed(20261112)`, `random.sample(sorted(scope_ids), 24)`) and its split into S1-S3.

## 2. Extraction (sub-agents; not deterministic)

One Claude sub-agent per batch, following `EXTRACTION_GUIDE_v2.md`, wrote `batches/<batch>/<ID>.json` (B00 was split into B00a and B00b) and proposals in `marker_map_additions/<batch>.csv`. The blind second agents wrote `second/S1..S3/<ID>.json`. After the owner's spot checks (`owner_spot_checks.csv`) the files were copied:

```
cp batches/B*/*.json extractions/
cp second/S*/*.json second/
```

Owner-merged marker names are in `marker_map_v2_additions.csv`. Differences found by the agreement check were resolved in `extractions/` and logged in `agreement_resolutions.csv`.

## 3. Deterministic part (inputs -> out/)

```
rm -rf out
python -I scripts/check_associations.py --quiet                     # associations_v2.csv, definitions_v2.csv, out/check_report.md, out/unmapped_markers.csv
python -I scripts/check_associations.py --dir second --no-write --quiet
python -I scripts/agreement.py --name second                        # out/agreement_second*.{json,csv}
python -I scripts/agreement.py --name pilot --other ../../core/data/severity/extractions
python -I scripts/build_results.py --run-utc <UTC time of the run>   # out/tables/*.csv, out/db/SV-G2-01-literature-extraction.json
```

The pilot comparison is limited to the 10 calibration articles (the only ones in both folders).

## 4. Database (console loader, Way B)

From `/console/Babesiosis.Console`:

```
dotnet build
dotnet run --no-build -- --datasets-only --only SV-G2-01-literature-extraction --dry-run
dotnet run --no-build -- --datasets-only --only SV-G2-01-literature-extraction
```

## 5. Web app

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-literature-extraction-view.component.*` (method `literature_extraction`). Check with `npx ng build` in `/webapp/Babesiosis.Web`, then open `/experiments/SV-G2-01-literature-extraction` with the `babesiosis-api` and `babesiosis-web` entries of `/.claude/launch.json`.
