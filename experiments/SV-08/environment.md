# SV-08 environment

- Runtime: Python 3.12.12, managed by `uv` 0.10.4 (on the path). Libraries (pinned in `requirements.txt`): numpy 2.3.4, scipy 1.16.3.
- `curl` (Git for Windows) for the Ensembl REST GET calls in `scripts/fetch_annotation.py` (Python's urllib timed out on these calls
  on this machine; curl did not).
- The database write uses the console loader in `/console/Babesiosis.Console` (way B); build it once with `dotnet build` for `--no-build`.

Build `env/` from nothing, from `/experiments/SV-08/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.txt
```

## Public reference data (in `ref/`, fetched once)

| File | Source | Version |
|---|---|---|
| `ref/unsymbolled_lookup.json` | Ensembl REST `POST /lookup/id` (https://rest.ensembl.org) for the 1,922 DS06 rows that carry no symbol | Ensembl release 116 (REST `info/data`), dog Boxer annotation `canis_lupus_familiarisboxer`, assembly Dog10K_Boxer_Tasha; fetched 2026-11-12 |
| `ref/symbol_xrefs.json` | Ensembl REST `GET /xrefs/symbol/canis_lupus_familiarisboxer/<symbol>?object_type=gene` for the 25 set genes | Same release; fetched 2026-11-12 |
| `ref/ensembl_release.json` | Ensembl REST `GET /info/data` | Records the release and fetch time |

Why this annotation: DS06 gene IDs are CanFam3.1 Ensembl IDs (`ENSCAFG…`). The Ensembl archive that held CanFam3.1 BioMart
(release 103, `feb2021.archive.ensembl.org`) now redirects to the archive help page, and the Boxer annotation keeps the CanFam3.1
stable gene IDs that are still current. 854 of the 1,922 unnamed IDs are not found in release 116 (retired); a set gene hidden among
them cannot be ruled out (reported in `report.md`).

Requests sent only Ensembl gene IDs and gene symbols, with the User-Agent `generic-client`. No user or project detail.

Tried and failed: the BioMart archive query (redirect, 0 bytes); Ensembl REST `homology/symbol` with the Boxer genome (no Compara
GenomeDB for it). Nothing was installed outside `env/`.
