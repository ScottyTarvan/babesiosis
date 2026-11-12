# SV-06a environment

- Runtime: Python 3.12.12, downloaded and managed by `uv` 0.10.4 (on the path).
- Libraries: standard library for the search and the assembly; `pyodbc` 5.2.0 for the database writer only (`requirements.txt`, `requirements.lock.txt`).
- Database driver: the system's "ODBC Driver 18 for SQL Server" (already installed; nothing installed outside `env/`).
- Literature: the PubMed MCP server available to Claude sessions (search and metadata tools), used by the seven family sub-agents. It is not part of `env/`; the PubMed queries are recorded in `out/transfer_grid.csv` (column `canine_pubmed_queries`) and in `families/F*.json`.

Build `env/` from nothing, from `/experiments/SV-06/a/` in Git Bash:

```bash
rm -rf env
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.lock.txt
```

Nothing failed to install.
