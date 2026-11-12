# SV-G2 environment

| Runtime | Version | Used for |
|---|---|---|
| Python (CPython, via `uv`) | 3.13.14 | Every script in `scripts/`. Standard library only: no third-party package |
| uv | 0.10.4 | Builds `env/py` |
| .NET SDK 10 | (machine) | The console loader `/console/Babesiosis.Console` (Way B of run-instructions.md, step 3) |
| Node / Angular CLI | (machine) | `npx ng build` for the web app view |

Build `env/` from nothing (from `/experiments/SV-G2/`):

```
uv venv env/py --python 3.13
```

No packages are installed (`requirements.txt` is empty on purpose). Any Python 3.12+ runs the scripts as `python -I scripts/<name>.py`; `env/py/Scripts/python.exe -I scripts/<name>.py` is the pinned interpreter.

Extraction itself was done by Claude sub-agents (model `claude-opus-5-5`) following `EXTRACTION_GUIDE_v2.md`; that step cannot be re-run deterministically. Everything after the extraction files (checker, agreement, tables, load file) is deterministic.
