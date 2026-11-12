# SV-04 environment

- Runtime: Python 3.12.12, downloaded and managed by `uv` (on the path). No R, .NET or Node code in this package.
- Direct dependency (pinned): `requirements.txt` (numpy 2.3.4). Full resolved set: `requirements.lock.txt` (the same single package).
- All statistics (Cliff's delta, bootstrap, permutation, Spearman, Benjamini-Hochberg, Hodges-Lehmann) are written in `scripts/analyse.py` with numpy only.
- The database write uses the console loader in `/console/Babesiosis.Console` (way B); it must have been built once (`dotnet build`) for `--no-build` to work.

Build `env/` from nothing, from `/experiments/SV-04/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.lock.txt
```

Nothing was installed outside `env/`. Nothing failed to install.
