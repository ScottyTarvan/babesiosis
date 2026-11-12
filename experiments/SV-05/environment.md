# SV-05 environment

- Runtime: Python 3.12.12, downloaded and managed by `uv` (on the path). No R, .NET or Node code in this package.
- Direct dependencies (pinned): `requirements.txt` (numpy 2.3.4, scipy 1.16.3). Full resolved set: `requirements.lock.txt`.
- scipy gives Fisher's exact test, the conditional odds ratio with its exact interval and Spearman's rho. Hodges-Lehmann,
  Cliff's delta, bootstrap, permutation tests, the Newcombe interval, Mantel-Haenszel (Robins-Breslow-Greenland interval) and
  Benjamini-Hochberg are written in `scripts/analyse.py` with numpy.
- The database write uses the console loader in `/console/Babesiosis.Console` (way B); it must have been built once (`dotnet build`).

Build `env/` from nothing, from `/experiments/SV-05/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.lock.txt
```

Nothing was installed outside `env/`. Nothing failed to install.
