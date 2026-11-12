# SV-G1 environment

| Runtime | Version | Where |
|---|---|---|
| Python | 3.12.12 (made by `uv`) | `env/py/` (git-ignored) |
| Python packages | none: standard library only | `requirements.txt` is empty on purpose |
| pdftotext | Poppler, shipped with Git for Windows | `/mingw64/bin/pdftotext` (Git Bash), used for the S-CB517 and S-CB516 PDFs |
| .NET SDK | 10 (machine) | only to run the console loader in `/console/Babesiosis.Console` |
| Node / npm | machine | only for `npx ng build` of the web app |

Build `env/` from nothing (Git Bash, from `/experiments/SV-G1/`):

```bash
uv venv env/py --python 3.12
```

Nothing is installed into it. The reader `shared/io/rawio.py` (standard library) does the xlsx and docx reading.
The old environments `/core/.venv` and `/core/.venv-nlp` are not used.
