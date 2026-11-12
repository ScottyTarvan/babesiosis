# SV-10 environment

Python 3.12.12 through `uv` (0.10.x), standard library only. No packages are installed, so `requirements.txt` is empty.

From `/experiments/SV-10/` in Git Bash:

```bash
uv venv env/py --python 3.12
```

The database write uses the console loader (way B), built with the .NET 10 SDK in `/console/Babesiosis.Console`.
