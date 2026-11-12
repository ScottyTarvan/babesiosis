"""K04 refutation checks: DS07 S100A8 and lactoferrin vs complicated, with confounder adjustment.

Reads /experiments/shared/tidy/DS07.features.json and DS07.outcomes.json. Prints JSON to stdout.
Rank-based: plex-centred values (median per plex subtracted, as a batch guard), Spearman partial correlation
with the complicated label after regressing ranks of covariates, bootstrap by dog (seed 20261112).
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
TIDY = ROOT / "experiments" / "shared" / "tidy"
SEED = 20261112
NBOOT = 2000

feat = json.loads((TIDY / "DS07.features.json").read_text(encoding="utf-8"))
outc = json.loads((TIDY / "DS07.outcomes.json").read_text(encoding="utf-8"))
label = {r["dog_id"]: r["values"].get("complicated") for r in outc["records"]}

VARS = {"s100a8": "p_c0lql0", "ltf": "p_f1pr54", "hbb": "p_p60524", "crp": "p_t2ken6", "saa": "p_a0a5f4d168"}

rows = []
for r in feat["records"]:
    v = r["values"]
    row = {"dog": r["dog_id"], "plex": v.get("plex"), "y": label.get(r["dog_id"])}
    for k, col in VARS.items():
        x = v.get(col)
        row[k] = float(x) if x is not None else None
    rows.append(row)

# plex-centre each variable over all dogs (controls included) with a value
for k in VARS:
    by = {}
    for row in rows:
        if row[k] is not None:
            by.setdefault(row["plex"], []).append(row[k])
    med = {p: float(np.median(xs)) for p, xs in by.items()}
    for row in rows:
        row[k + "_c"] = None if row[k] is None else row[k] - med[row["plex"]]

inf = [r for r in rows if r["y"] in (0, 1)]


def resid(y, X):
    X1 = np.column_stack([np.ones(len(y))] + [stats.rankdata(c) for c in X])
    b, *_ = np.linalg.lstsq(X1, stats.rankdata(y), rcond=None)
    return stats.rankdata(y) - X1 @ b


def partial(sub, target, covs):
    y = np.array([r["y"] for r in sub], float)
    x = np.array([r[target] for r in sub], float)
    if not covs:
        return float(stats.spearmanr(x, y)[0])
    X = [np.array([r[c] for r in sub], float) for c in covs]
    return float(np.corrcoef(resid(x, X), resid(y, X))[0, 1])


def run(target, covs):
    need = [target] + covs
    sub = [r for r in inf if all(r[n] is not None for n in need)]
    est = partial(sub, target, covs)
    rng = np.random.default_rng(SEED)
    bs = []
    n = len(sub)
    for _ in range(NBOOT):
        s = [sub[i] for i in rng.integers(0, n, n)]
        if len({r["y"] for r in s}) < 2:
            continue
        val = partial(s, target, covs)
        if np.isfinite(val):
            bs.append(val)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"target": target, "covariates": covs, "n": n,
            "n_comp": sum(r["y"] == 1 for r in sub), "rho": round(est, 3),
            "ci95": [round(float(lo), 3), round(float(hi), 3)]}


out = {"tests": []}
for t in ("s100a8_c", "ltf_c"):
    for covs in ([], ["hbb_c"], ["crp_c"], ["saa_c"], ["hbb_c", "crp_c"]):
        out["tests"].append(run(t, covs))
out["tests"].append(run("s100a8_c", ["ltf_c"]))

# S100A8 and LTF correlation among infected dogs; S100A8 detection by group
both = [r for r in inf if r["s100a8_c"] is not None and r["ltf_c"] is not None]
rho, p = stats.spearmanr([r["s100a8_c"] for r in both], [r["ltf_c"] for r in both])
out["s100a8_vs_ltf_infected"] = {"n": len(both), "rho": round(float(rho), 3), "p": round(float(p), 4)}
det = {}
for g, nm in ((1, "complicated"), (0, "uncomplicated")):
    grp = [r for r in inf if r["y"] == g]
    det[nm] = [sum(r["s100a8"] is not None for r in grp), len(grp)]
ctrl = [r for r in rows if r["y"] is None]
det["control"] = [sum(r["s100a8"] is not None for r in ctrl), len(ctrl)]
out["s100a8_detected_of_n"] = det
tab = [[det["complicated"][0], det["complicated"][1] - det["complicated"][0]],
       [det["uncomplicated"][0], det["uncomplicated"][1] - det["uncomplicated"][0]]]
out["s100a8_detection_fisher_p"] = round(float(stats.fisher_exact(tab)[1]), 4)
json.dump(out, sys.stdout, indent=1)
