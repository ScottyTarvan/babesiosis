# SV-META environment

- Runtime: Python 3.12.12, downloaded and managed by `uv` 0.10.4 (on the path). No R, .NET or Node code in this package; the database
  write uses the console loader in `/console/Babesiosis.Console` (way B), which must have been built once (`dotnet build`).
- Direct dependencies (pinned): `requirements.txt` (numpy 2.3.4, scipy 1.16.3). Resolved set: `requirements.lock.txt` (the same two).
- `census.py`, `check_census.py`, `screen.py` and `build_load.py` use the standard library plus scipy (normal and chi-square
  quantiles); `themes.py` uses numpy and scipy (bootstrap, permutation, Spearman, Stouffer, Fisher, binomial sign test).
- The refutation sub-agents used the same environment for their checks (`refutation/scripts/*.py`).

Build `env/` from nothing, from `/experiments/SV-META/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.lock.txt
```

Nothing was installed outside `env/`. Nothing failed to install.
