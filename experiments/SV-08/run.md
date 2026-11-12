# SV-08 run

From `/experiments/SV-08/` in Git Bash, after `environment.md`.

```bash
PY=env/py/Scripts/python.exe
# Once only (network): public Ensembl annotation into ref/. Skip if ref/ is present; the analysis checks the hashes of ref/ files.
# $PY -I scripts/fetch_annotation.py
rm -rf out
$PY -I scripts/analyse.py      # DS06 counts + shared/tidy/DS02.* + ref/ -> out/*.csv, out/results.json (about 10 s)
$PY -I scripts/build_load.py   # out/db/SV-08-01-transcriptome-signatures.json
```

Seed 20261112 (numpy `default_rng`), 2,000 random gene sets per dog and set. `analyse.py` stops if `spec.md` changed.

Database write (way B, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-08-01-transcriptome-signatures --dry-run
dotnet run --no-build -- --datasets-only --only SV-08-01-transcriptome-signatures
```

Check query: step 3 of `/experiments/run-instructions.md`, with the code `SV-08-01-transcriptome-signatures`.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-transcriptome-signature-view.component.*`
(method `transcriptome_signature`).

Repeat check (done 2026-11-12): `out/` deleted and rebuilt with the commands above; every CSV and `results.json` came back
byte-identical; the load file differs only in `run_utc`.

## Files in out/

| File | Holds |
|---|---|
| `set_scores.csv` | Every sample x set: score, change from D0, background percentile and range, S2 and S3 scores, library size, DS02 parasitaemia under both mappings |
| `unmapped_genes.csv` | Every fixed set gene that does not map, with the reason |
| `gene_map.csv` | All 25 genes: DS06 row and how it was mapped |
| `primary_deltas.csv` | Primary per-dog change with the background, and S1 to S4 |
| `sign_counts.csv` | Per set: dogs with a rise, sign-test p, dogs beyond background, sensitivity counts |
| `timing.csv` | First risen day, deterioration day, both mappings |
| `habitus.csv` | DS02 habitus by dog and day (outcomes file) |
| `construct_checks.csv` | Within-dog rho of scores with IP-10, band neutrophils and reticulocyte % |
| `library_sizes.csv` | Library size and ALAS2 percentile per sample |
| `results.json` | Input hashes, versions, sign counts, verdicts |
| `db/` | The load file |
