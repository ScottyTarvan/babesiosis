# SV-01 environment

- Runtime: Python 3.12.12, downloaded and managed by `uv` 0.10.4 (on the path). No R, .NET or Node code in this package.
- Direct dependencies (pinned): `requirements.txt` (numpy 2.3.4, scipy 1.16.3, matplotlib 3.10.7).
- Full resolved set: `requirements.lock.txt`.
- The database write uses the console loader in `/console/Babesiosis.Console` (way B); it must be built once (`dotnet build`) for `--no-build` to work.

Build `env/` from nothing, from `/experiments/SV-01/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.lock.txt
```

Nothing was installed outside `env/`. Nothing failed to install.
