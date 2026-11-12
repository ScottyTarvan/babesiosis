# SV-06b environment

- Runtime: Python 3.12.12, managed by `uv` 0.10.4 (on the path).
- Libraries: `numpy` 2.3.4 (all numbers), `pyodbc` 5.2.0 (database writer only). Pinned in `requirements.txt` and `requirements.lock.txt`.
- Database driver: the system's "ODBC Driver 18 for SQL Server" (already installed; nothing was installed outside `env/`).

Build `env/` from nothing, from `/experiments/SV-06/b/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.lock.txt
```

Nothing failed to install.
