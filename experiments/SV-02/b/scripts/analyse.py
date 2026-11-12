"""SV-02b: reaction norms in the DS02 Beagles (descriptive).

Run from /experiments/SV-02/b:  env/py/Scripts/python.exe -I scripts/analyse.py
Reads the SV-G1 tidy files for DS02, follows b/spec.md, writes out/.
"""
import csv
import hashlib
import json
import math
import os
import sys

import numpy as np
import scipy
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)
EXP = os.path.dirname(os.path.dirname(PART))
OUT = os.path.join(PART, "out")
FEAT = os.path.join(EXP, "shared", "tidy", "DS02.features.json")
OUTC = os.path.join(EXP, "shared", "tidy", "DS02.outcomes.json")
SPEC = os.path.join(PART, "spec.md")
SPEC_SHA = "0b44ffb3d1dab6e244c2d6f441a6bd747c890010d8d4009e92b6587bb2ac7724"
SEED = 20261112
OFFSET = 0.01
TARGETS = [1.0, 5.0]
MARGIN = {"hct_drop": 0.03, "lactate": 0.5, "habitus_loss": 1.0}
MEASURES = [
    ("hct_drop", "Haematocrit drop from baseline", "L/L"),
    ("lactate", "Venous lactate", "mmol/L"),
    ("habitus_loss", "Habitus loss (4 minus score)", "points"),
]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


if sha(SPEC) != SPEC_SHA:
    sys.exit("spec.md changed since it was frozen: stop")

feat = json.load(open(FEAT, encoding="utf-8"))
outc = json.load(open(OUTC, encoding="utf-8"))

# ---- outcomes: habitus by dog and timepoint, died by dog ----------------------------------------
habitus = {}
died = {}
for r in outc["records"]:
    v = r["values"]
    if "died" in v and r.get("timepoint") is None:
        died[r["dog_id"]] = v["died"]
    if "habitus_score" in v and v["habitus_score"] is not None:
        habitus[(r["dog_id"], r["timepoint"])] = v["habitus_score"]

# ---- features: per dog series -------------------------------------------------------------------
dogs = {}
for r in feat["records"]:
    if r["group"] != "infected":
        continue
    d = dogs.setdefault(r["dog_id"], {"dose": r["values"].get("dose_group"), "rows": []})
    d["rows"].append(r)

ORDER = {"day_4_1": 4.5}


def tkey(r):
    return ORDER.get(r["timepoint"], r["day"])


def baseline_hct(rows):
    vals = [r["values"].get("hct") for r in rows if r["day"] in (-1.0, 0.0) and r["values"].get("hct") is not None]
    return float(np.mean(vals)) if vals else None


def series(dog_id, offset=OFFSET, positive_only=False, lactate_var="lactate", hct_raw=False):
    """Pre-treatment points with a parasitaemia value: list of dicts with x and each measure."""
    rows = sorted(dogs[dog_id]["rows"], key=tkey)
    base = baseline_hct(rows)
    pts = []
    for r in rows:
        v = r["values"]
        p = v.get("parasitaemia_pct")
        if r["post_treatment"] or p is None:
            continue
        if positive_only and p <= 0:
            continue
        x = math.log10(p) if positive_only else math.log10(p + offset)
        hct = v.get("hct")
        hab = habitus.get((dog_id, r["timepoint"]))
        pts.append({
            "timepoint": r["timepoint"], "day": r["day"], "t": tkey(r), "parasitaemia_pct": p, "x": x,
            "hct_drop": (hct if hct_raw else (None if hct is None or base is None else base - hct)) if hct is not None else None,
            "lactate": v.get(lactate_var),
            "habitus_loss": None if hab is None else 4 - hab,
            "hct": hct, "habitus_score": hab,
        })
    return pts, base


def ols(xs, ys):
    n = len(xs)
    if n < 2 or len(set(xs)) < 2:
        return None
    x = np.array(xs); y = np.array(ys)
    xm, ym = x.mean(), y.mean()
    sxx = ((x - xm) ** 2).sum()
    b = ((x - xm) * (y - ym)).sum() / sxx
    a = ym - b * xm
    lo = hi = None
    if n >= 3:
        res = y - (a + b * x)
        s2 = (res ** 2).sum() / (n - 2)
        se = math.sqrt(s2 / sxx)
        tq = stats.t.ppf(0.975, n - 2)
        lo, hi = b - tq * se, b + tq * se
    ts = stats.theilslopes(y, x)[0] if n >= 2 else None
    return {"slope": float(b), "intercept": float(a), "ci_lo": None if lo is None else float(lo),
            "ci_hi": None if hi is None else float(hi), "theil_sen": None if ts is None else float(ts), "n_points": n}


def interp(pts, m, target_x):
    """Interpolate measure m at target_x between consecutive (time-ordered) points that bracket it."""
    q = [p for p in pts if p[m] is not None]
    for a, b in zip(q, q[1:]):
        if a["x"] == target_x:
            return a[m]
        if (a["x"] - target_x) * (b["x"] - target_x) < 0 or b["x"] == target_x:
            if b["x"] == a["x"]:
                return b[m]
            f = (target_x - a["x"]) / (b["x"] - a["x"])
            return a[m] + f * (b[m] - a[m])
    if len(q) == 1 and q[0]["x"] == target_x:
        return q[0][m]
    return None


def analyse(offset=OFFSET, positive_only=False, lactate_var="lactate", hct_raw=False, drop=()):
    per = []
    pooled = {}
    allpts = {}
    for dog_id in sorted(dogs):
        if dog_id in drop:
            continue
        pts, base = series(dog_id, offset, positive_only, lactate_var, hct_raw)
        allpts[dog_id] = pts
        for m, _, _ in MEASURES:
            q = [p for p in pts if p[m] is not None]
            fit = ols([p["x"] for p in q], [p[m] for p in q])
            peak = max(q, key=lambda p: p["x"]) if q else None
            row = {"dog_id": dog_id, "dose_group": dogs[dog_id]["dose"], "died": died.get(dog_id), "measure": m,
                   "n_points": len(q), "baseline_hct": base,
                   "slope": None, "ci_lo": None, "ci_hi": None, "theil_sen": None, "intercept": None,
                   "peak_parasitaemia_pct": None if peak is None else peak["parasitaemia_pct"],
                   "peak_timepoint": None if peak is None else peak["timepoint"],
                   "damage_at_peak": None if peak is None else peak[m]}
            if fit:
                row.update({k: fit[k] for k in ("slope", "ci_lo", "ci_hi", "theil_sen", "intercept")})
            for tg in TARGETS:
                tx = math.log10(tg) if positive_only else math.log10(tg + offset)
                row[f"damage_at_{tg:g}pct"] = interp(pts, m, tx)
            per.append(row)
    for m, _, _ in MEASURES:
        xs, ys, who = [], [], []
        for dog_id, pts in allpts.items():
            for p in pts:
                if p[m] is not None:
                    xs.append(p["x"]); ys.append(p[m]); who.append(dog_id)
        fit = ols(xs, ys)
        resid = {}
        if fit:
            for x, y, w in zip(xs, ys, who):
                resid.setdefault(w, []).append(y - (fit["intercept"] + fit["slope"] * x))
        pooled[m] = {"slope": fit and fit["slope"], "intercept": fit and fit["intercept"], "n_points": len(xs),
                     "mean_residual": {w: float(np.mean(v)) for w, v in resid.items()}}
    return per, pooled, allpts


def read_rule(per, pooled, m):
    rows = [r for r in per if r["measure"] == m]
    slopes = [r["slope"] for r in rows if r["slope"] is not None]
    signs = {1 if s > 0 else (-1 if s < 0 else 0) for s in slopes}
    same_sign = len(signs) == 1 and 0 not in signs and len(slopes) >= 2
    mg = MARGIN[m]
    crit = {"same_sign": same_sign, "n_slopes": len(slopes)}
    for tg in TARGETS:
        k = f"damage_at_{tg:g}pct"
        lo = [r[k] for r in rows if r["dose_group"] == "low" and r[k] is not None]
        hi = [r[k] for r in rows if r["dose_group"] == "high" and r[k] is not None]
        if lo and hi:
            inside = all(min(hi) - mg <= v <= max(hi) + mg for v in lo)
            separate = min(lo) > max(hi) + mg or max(lo) < min(hi) - mg
        else:
            inside = separate = None
        crit[f"low_inside_high_{tg:g}pct"] = inside
        crit[f"separate_{tg:g}pct"] = separate
        crit[f"n_low_{tg:g}pct"] = len(lo)
        crit[f"n_high_{tg:g}pct"] = len(hi)
    mr = pooled[m]["mean_residual"]
    absr = sorted(((abs(v), w) for w, v in mr.items()), reverse=True)
    outlier = None
    if len(absr) >= 2 and absr[0][0] > 2 * absr[1][0]:
        outlier = absr[0][1]
    crit["residual_outlier_dog"] = outlier
    different = bool(crit["separate_1pct"]) or bool(crit["separate_5pct"]) or outlier is not None
    shared = same_sign and crit["low_inside_high_5pct"] is True
    # Precedence (not stated in the spec; recorded as clarification C1): a "different" criterion wins.
    label = "different norms" if different else ("one shared norm" if shared else "cannot tell")
    crit["reading"] = label
    return crit


per, pooled, allpts = analyse()
readings = {m: read_rule(per, pooled, m) for m, _, _ in MEASURES}

# ---- sensitivity ---------------------------------------------------------------------------------
sens_defs = [
    ("offset_0.001", dict(offset=0.001)),
    ("offset_0.1", dict(offset=0.1)),
    ("positive_load_only", dict(positive_only=True)),
    ("clinical_lactate", dict(lactate_var="lactate_clinical")),
    ("hct_raw_value", dict(hct_raw=True)),
    ("without_dog_that_died", dict(drop=tuple(d for d, v in died.items() if v == 1))),
]
sens = []
for name, kw in sens_defs:
    p2, pool2, _ = analyse(**kw)
    for m, _, _ in MEASURES:
        if name == "clinical_lactate" and m != "lactate":
            continue
        if name == "hct_raw_value" and m != "hct_drop":
            continue
        rd = read_rule(p2, pool2, m)
        for r in p2:
            if r["measure"] != m:
                continue
            sens.append({"check": name, "measure": m, "dog_id": r["dog_id"], "dose_group": r["dose_group"],
                         "n_points": r["n_points"], "slope": r["slope"], "theil_sen": r["theil_sen"],
                         "damage_at_1pct": r["damage_at_1pct"], "damage_at_5pct": r["damage_at_5pct"],
                         "reading": rd["reading"]})

# ---- write ---------------------------------------------------------------------------------------
os.makedirs(OUT, exist_ok=True)


def rnd(v, d=4):
    return None if v is None else (round(v, d) if isinstance(v, float) else v)


def wcsv(name, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if v is None else rnd(v)) for k, v in r.items()})


wcsv("reaction_norms.csv", per)
pts_rows = []
for dog_id, pts in allpts.items():
    for p in pts:
        pts_rows.append({"dog_id": dog_id, "dose_group": dogs[dog_id]["dose"], "died": died.get(dog_id),
                         "timepoint": p["timepoint"], "day": p["day"], "parasitaemia_pct": p["parasitaemia_pct"],
                         "log10_load": p["x"], "hct": p["hct"], "hct_drop": p["hct_drop"], "lactate": p["lactate"],
                         "habitus_score": p["habitus_score"], "habitus_loss": p["habitus_loss"]})
wcsv("points.csv", pts_rows)
wcsv("sensitivity.csv", sens)
pool_rows = [{"measure": m, "slope": pooled[m]["slope"], "intercept": pooled[m]["intercept"], "n_points": pooled[m]["n_points"],
              **{f"mean_residual_{w}": v for w, v in sorted(pooled[m]["mean_residual"].items())}} for m, _, _ in MEASURES]
wcsv("pooled_lines.csv", pool_rows)
wcsv("readings.csv", [{"measure": m, **readings[m]} for m, _, _ in MEASURES])


def clean(o):
    if isinstance(o, float):
        return None if (math.isnan(o) or math.isinf(o)) else round(o, 6)
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    return o


results = {
    "code": "SV-02-02-beagle-reaction-norms",
    "seed": SEED, "offset": OFFSET, "targets_pct": TARGETS, "margins": MARGIN,
    "measures": [{"key": m, "label": l, "unit": u} for m, l, u in MEASURES],
    "inputs": {"experiments/shared/tidy/DS02.features.json": sha(FEAT),
               "experiments/shared/tidy/DS02.outcomes.json": sha(OUTC),
               "experiments/SV-02/b/spec.md": SPEC_SHA},
    "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__},
    "n_dogs": len(dogs), "dose_groups": {d: v["dose"] for d, v in sorted(dogs.items())}, "died": died,
    "per_dog": per, "pooled": pooled, "readings": readings, "points": pts_rows, "sensitivity": sens,
}
json.dump(clean(results), open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"), indent=1, allow_nan=False)
for m, _, _ in MEASURES:
    print(m, readings[m])
for r in per:
    print(r["dog_id"], r["dose_group"], r["measure"], r["n_points"], rnd(r["slope"], 3), rnd(r["ci_lo"], 2), rnd(r["ci_hi"], 2),
          rnd(r["theil_sen"], 3), "@1%", rnd(r["damage_at_1pct"], 3), "@5%", rnd(r["damage_at_5pct"], 3),
          "peak", r["peak_parasitaemia_pct"], rnd(r["damage_at_peak"], 3))
