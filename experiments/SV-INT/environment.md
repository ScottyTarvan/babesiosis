# SV-INT environment

Python 3.12.12, standard library only, in a uv environment. No packages, so no `requirements.txt` pins are needed.

```bash
cd /c/Workspaces/Babesiosis/experiments/SV-INT
uv venv env/py --python 3.12
```

Tested with uv 0.10.4. The web view needs the existing Angular project (`npx ng build` in `/webapp/Babesiosis.Web`); nothing was installed into it.
