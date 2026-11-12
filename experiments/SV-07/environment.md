# SV-07 environment

- Runtime: Python 3.12.12, managed by `uv` 0.10.4 (on the path). Standard library only; the xlsx and docx reader is
  `/experiments/shared/io/rawio.py` (standard library). `requirements.txt` is empty on purpose.
- The database write uses the console loader in `/console/Babesiosis.Console` (way B); build it once with `dotnet build` for `--no-build`.

Build `env/` from nothing, from `/experiments/SV-07/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
```

Nothing was installed outside `env/`. Nothing failed to install.
