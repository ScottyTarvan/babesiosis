# SV-03 environment

- Runtime: Python 3.12.12, downloaded and managed by `uv` 0.10.4 (on the path). No R, .NET or Node code in this package
  (the database write uses the shared console loader, way B).
- Libraries (pinned in `requirements.txt`): numpy 2.3.4, scipy 1.16.3.

Build from nothing, in Git Bash from `/experiments/SV-03/`:

```bash
uv venv env/py --python 3.12
uv pip install --python env/py -r requirements.txt
env/py/Scripts/python -I -c "import numpy, scipy; print(numpy.__version__, scipy.__version__)"
```

`env/` is git-ignored and holds nothing that is not rebuilt by these commands.
