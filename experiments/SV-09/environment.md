# SV-09 environment

- Runtime: Python 3.12.12, managed by `uv` (on the path). No R, .NET or Node code in this package.
- Pinned dependencies: `requirements.txt` = `requirements.lock.txt` (numpy 2.3.4, scipy 1.16.3). scipy is used only for `rankdata`.
- All statistics (residualising, PCA, Horn's parallel analysis, Tucker's phi, orthogonal Procrustes, Cliff's delta, permutation, bootstrap, BH) are written in `scripts/analyse.py`.
- Database write: the console loader in `/console/Babesiosis.Console` (way B); it must have been built once (`dotnet build`).

Build `env/` from nothing, from `/experiments/SV-09/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.lock.txt
```

Nothing was installed outside `env/`. Nothing failed to install.
