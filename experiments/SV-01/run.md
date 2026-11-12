# SV-01 run

From `/experiments/SV-01/` in Git Bash, after `environment.md`.

```bash
rm -rf out
PY=env/py/Scripts/python.exe
$PY -I scripts/analyse.py      # checks the SHA-256 of the 4 input files and of spec.md, then writes out/ (stops if one changed)
$PY -I scripts/build_load.py   # out/figure_map_A.svg, out/figure_map_B.svg, out/db/<code>.json (2 load files)
```

`analyse.py` runs both curve constructions: the spec construction into `out/` (primary) and the time-anchored course
(deviation D1) into `out/time_anchored/`. Seed 20261112. Runtime about 10 s.

Database write (way B of `/experiments/run-instructions.md`, the console loader), from `/console/Babesiosis.Console`:

```bash
dotnet run --no-build -- --datasets-only --only SV-01-01-habitus-distance,SV-01-02-ds03-geometry --dry-run
dotnet run --no-build -- --datasets-only --only SV-01-01-habitus-distance,SV-01-02-ds03-geometry
```

Check query: step 3 of `run-instructions.md`, with the two codes.

View: `/webapp/Babesiosis.Web/src/app/modules/experiments/views/experiment-disease-space-map-view.component.*`
(method `disease_space_map`); build with `npx ng build` in `/webapp/Babesiosis.Web`.

Repeat check (done 2026-11-12): delete `out/`, run the two scripts; every file is byte-identical except `run_utc` in the two load files.

## Files in out/

| File | Holds |
|---|---|
| `pseudo_stage.csv` | `dog_id, dataset_id, pseudo_stage, distance, plane` for the naturally infected dogs (DS05 147 in planes A and B; DS03 103 in plane A). Spec construction. Read by SV-05 and SV-09: see the caveat in `report.md` |
| `map_points.csv` | Every projected point (natural dogs, DS03 controls and IMHA, Beagle samples) with its plane coordinates |
| `curves.csv` | The reference course and the post-treatment arm, sampled along the curve |
| `tests.csv`, `stability_loo.csv`, `replication_geometry.csv` | The tables of `report.md` |
| `results.json` | Every number, including the time-anchored results under `time_anchored` |
| `ds05_habitus_for_map.csv` | Habitus grade of the DS05 dogs, for colouring the map (outcome data) |
| `time_anchored/` | The same files for deviation D1 |
| `db/` | The two load files |
