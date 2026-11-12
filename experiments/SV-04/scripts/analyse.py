"""SV-04 analysis: IL-8 conflict between S-CB050 (B. rossi) and S-CB017 (B. canis), with DS02 courses.

Run from /experiments/SV-04/:  env/py/Scripts/python.exe -I scripts/analyse.py
Reads the tidy files of SV-G1 and spec.md, checks their SHA-256, writes out/.
"""
import csv
import hashlib
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
TIDY = os.path.join(os.path.dirname(PKG), "shared", "tidy")
OUT = os.path.join(PKG, "out")

EXPECTED = {
    "S-CB050.features.json": "fedde71e230325695e0866bd362d932a83904dc50de7883003dc6431cff9460f",
    "S-CB017.features.json": "6ed00495a7296cb9e3a87e5132cfa0f7a6a798068e9c9e811c9efdcada088cac",
    "DS02.features.json": "12475e823e588af20e8bec2df5164979c158bdbbb86ddfb96a32afe8aad83e2d",
}
SPEC_SHA = None  # read from exposure.md and compared with spec.md

ANALYTES = ["il2", "il8", "il10", "il18", "gmcsf", "mcp1"]
LABEL = {"il2": "IL-2", "il8": "IL-8", "il10": "IL-10", "il18": "IL-18", "gmcsf": "GM-CSF", "mcp1": "MCP-1"}
SEED = 20261112
N_BOOT = 2000
N_PERM = 10000
# analytes with < 20% floor values among the samples used (spec, sensitivity S1)
Z_ANALYTES = {"S-CB050": ["il8", "il10", "il18", "mcp1"], "S-CB017": ["il2", "il8", "gmcsf", "mcp1"]}

rng = np.random.default_rng(SEED)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def load(name):
    with open(os.path.join(TIDY, name), encoding="utf-8") as f:
        return json.load(f)


def check_inputs():
    hashes = {}
    for name, exp in EXPECTED.items():
        got = sha256(os.path.join(TIDY, name))
        if got != exp:
            sys.exit(f"Input changed: {name} {got} != {exp}")
        hashes[name] = got
    # outcomes files: their hashes are in exposure.md; spec hash too
    with open(os.path.join(PKG, "exposure.md"), encoding="utf-8") as f:
        rows = [l for l in f if l.startswith("| 2026")]
    spec = sha256(os.path.join(PKG, "spec.md"))
    for r in rows:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        fname = os.path.basename(cells[1])
        if sha256(os.path.join(TIDY, fname)) != cells[2]:
            sys.exit(f"Outcomes file changed since exposure: {fname}")
        if cells[3] != spec:
            sys.exit("spec.md changed after the outcome lock")
        hashes[fname] = cells[2]
    return hashes, spec


# ---------- statistics ----------

def avg_ranks(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x))
    xs = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1
        i = j + 1
    return ranks


def cliff(x, y):
    x = np.asarray(x, float)[:, None]
    y = np.asarray(y, float)[None, :]
    return float(((x > y).sum() - (x < y).sum()) / (x.size * y.size))


def hl_shift(x, y):
    d = np.asarray(x, float)[:, None] - np.asarray(y, float)[None, :]
    return float(np.median(d))


def boot_two(x, y, fn):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    out = np.empty(N_BOOT)
    for b in range(N_BOOT):
        xb = x[rng.integers(0, len(x), len(x))]
        yb = y[rng.integers(0, len(y), len(y))]
        out[b] = fn(xb, yb)
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(lo), float(hi)


def perm_cliff(x, y):
    """Two-sided permutation p for Cliff's delta (via rank sums; ties as 0.5)."""
    nx, ny = len(x), len(y)
    pooled = np.concatenate([np.asarray(x, float), np.asarray(y, float)])
    r = avg_ranks(pooled)
    n = nx + ny

    def d_from_ranksum(rs):
        u = rs - nx * (nx + 1) / 2.0
        return 2.0 * u / (nx * ny) - 1.0

    obs = d_from_ranksum(r[:nx].sum())
    keys = rng.random((N_PERM, n))
    idx = np.argsort(keys, axis=1)[:, :nx]
    d = d_from_ranksum(r[idx].sum(axis=1))
    p = (np.sum(np.abs(d) >= abs(obs) - 1e-12) + 1) / (N_PERM + 1)
    return float(p), float(obs)


def spearman(x, y):
    rx, ry = avg_ranks(x), avg_ranks(y)
    rx -= rx.mean()
    ry -= ry.mean()
    den = math.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / den) if den > 0 else None


def spearman_full(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    rho = spearman(x, y)
    bs = []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(x), len(x))
        v = spearman(x[i], y[i])
        if v is not None:
            bs.append(v)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    perm = np.array([spearman(x, rng.permutation(y)) for _ in range(N_PERM)])
    p = (np.sum(np.abs(perm) >= abs(rho) - 1e-12) + 1) / (N_PERM + 1)
    return {"rho": rho, "lo": float(lo), "hi": float(hi), "p": float(p), "n": len(x)}


def bh(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    order = np.argsort(ps)
    q = np.empty(m)
    prev = 1.0
    for k in range(m - 1, -1, -1):
        i = order[k]
        prev = min(prev, ps[i] * m / (k + 1))
        q[i] = prev
    return [float(v) for v in q]


def contrast(sev, non, name, logvals=True):
    """sev, non: arrays of values (>0). Returns dict."""
    d = cliff(sev, non)
    dlo, dhi = boot_two(sev, non, cliff)
    p, _ = perm_cliff(sev, non)
    res = {"analyte": name, "n_severe": len(sev), "n_nonsevere": len(non),
           "median_severe": float(np.median(sev)), "median_nonsevere": float(np.median(non)),
           "cliff_delta": d, "cliff_lo": dlo, "cliff_hi": dhi, "p": p}
    if logvals:
        ls, ln = np.log2(sev), np.log2(non)
        res["hl_log2"] = hl_shift(ls, ln)
        res["hl_lo"], res["hl_hi"] = boot_two(ls, ln, hl_shift)
    return res


# ---------- data ----------

def value(rec, a, half_floor, floors):
    v = rec["values"].get(a)
    if v is None:
        return None
    if half_floor and rec["censored"].get(a) == "floor":
        return floors[a] / 2.0
    return float(v)


def file_sets(half_floor):
    """Return {file: {'infected': [(dog, sev, rec)], 'control': [rec], 'floors': {}}}."""
    sets = {}
    f050 = load("S-CB050.features.json")
    o050 = {r["dog_id"]: r["values"]["died"] for r in load("S-CB050.outcomes.json")["records"]}
    f017 = load("S-CB017.features.json")
    o017 = {r["dog_id"]: r["values"]["complicated"] for r in load("S-CB017.outcomes.json")["records"]}
    for fid, feat, outc, sel_inf, sel_ctl in [
        ("S-CB050", f050, o050, lambda r: r["values"].get("cohort") == 1 and r["group"] == "infected",
         lambda r: r["values"].get("cohort") == 1 and r["group"] == "control"),
        ("S-CB017", f017, o017, lambda r: r["group"] == "infected" and r["timepoint"] == "day_1",
         lambda r: r["group"] == "control"),
        ("S-CB017 day 7", f017, o017, lambda r: r["group"] == "infected" and r["timepoint"] == "day_7",
         lambda r: r["group"] == "control"),
    ]:
        floors = {v["name"]: v.get("floor") for v in feat["variables"]}
        inf = [(r["dog_id"], outc[r["dog_id"]], r) for r in feat["records"] if sel_inf(r)]
        ctl = [r for r in feat["records"] if sel_ctl(r)]
        sets[fid] = {"infected": inf, "control": ctl, "floors": floors, "half": half_floor}
    return sets


def analyte_vals(s, a):
    sev, non = [], []
    for dog, lab, r in s["infected"]:
        v = value(r, a, s["half"], s["floors"])
        if v is None or lab is None:
            continue
        (sev if lab == 1 else non).append(v)
    return np.array(sev), np.array(non)


def run_contrasts(sets, files):
    rows = []
    for fid in files:
        s = sets[fid]
        fam = []
        for a in ANALYTES:
            sev, non = analyte_vals(s, a)
            c = contrast(sev, non, a)
            c["file"] = fid
            fam.append(c)
        for c, q in zip(fam, bh([c["p"] for c in fam])):
            c["q"] = q
        rows += fam
    return rows


def perturbation(sets, fid):
    s = sets[fid]
    rngs = {}
    zpar = {}
    for a in ANALYTES:
        cv = np.array([value(r, a, s["half"], s["floors"]) for r in s["control"]], float)
        rngs[a] = (float(cv.min()), float(cv.max()))
        lc = np.log2(cv)
        zpar[a] = (float(lc.mean()), float(lc.std(ddof=1)))
    rows = []
    for dog, lab, r in s["infected"]:
        vals = {a: value(r, a, s["half"], s["floors"]) for a in ANALYTES}
        above = sum(1 for a in ANALYTES if vals[a] is not None and vals[a] > rngs[a][1])
        below = sum(1 for a in ANALYTES if vals[a] is not None and vals[a] < rngs[a][0])
        zs = [abs((math.log2(vals[a]) - zpar[a][0]) / zpar[a][1]) for a in Z_ANALYTES[fid] if vals[a] is not None]
        rows.append({"file": fid, "dog_id": dog, "severe": lab, "perturbation": above + below,
                     "above": above, "below": below, "z_mean_abs": float(np.mean(zs)),
                     "il8": vals["il8"], "mcp1": vals["mcp1"]})
    n = len(rows)
    pm = avg_ranks([r["mcp1"] for r in rows])
    p8 = avg_ranks([r["il8"] for r in rows])
    for r, a, b in zip(rows, pm, p8):
        r["pct_mcp1"] = 100.0 * (a - 0.5) / n
        r["pct_il8"] = 100.0 * (b - 0.5) / n
        r["balance"] = r["pct_mcp1"] - r["pct_il8"]
    return rows, rngs, zpar


def group_test(rows, key, logvals=False):
    sev = np.array([r[key] for r in rows if r["severe"] == 1], float)
    non = np.array([r[key] for r in rows if r["severe"] == 0], float)
    c = contrast(sev, non, key, logvals=logvals)
    c["mean_severe"] = float(sev.mean())
    c["mean_nonsevere"] = float(non.mean())
    return c


# ---------- DS02 ----------

def ds02():
    feat = load("DS02.features.json")
    dogs = {}
    for r in feat["records"]:
        if r["timepoint"] == "day_4_1":
            continue
        dogs.setdefault(r["dog_id"], {"dose": r["values"].get("dose_group"), "days": {}})
        dogs[r["dog_id"]]["days"][r["day"]] = r["values"]
    series, courses = [], []
    for dog in sorted(dogs):
        info = dogs[dog]
        for a in ANALYTES:
            pts = {}
            for day, v in sorted(info["days"].items()):
                x = v.get(a)
                if x is not None:
                    pts[day] = math.log2(x + 1.0)
                    series.append({"dog_id": dog, "dose_group": info["dose"], "analyte": a, "day": day,
                                   "value": x, "log2_value_plus1": pts[day], "post_treatment": day > 4})
            base = np.mean([pts[d] for d in (-1.0, 0.0) if d in pts])
            pre_days = [d for d in sorted(pts) if 0.0 <= d <= 4.0]
            dd = [abs(pts[b] - pts[a_]) for a_, b in zip(pre_days, pre_days[1:])]
            courses.append({
                "dog_id": dog, "dose_group": info["dose"], "analyte": a,
                "baseline_log2": float(base), "day4_log2": pts.get(4.0), "day6_log2": pts.get(6.0),
                "day8_log2": pts.get(8.0),
                "pre_change_log2": (pts[4.0] - base) if 4.0 in pts else None,
                "post_change_d4_d6": (pts[6.0] - pts[4.0]) if 6.0 in pts and 4.0 in pts else None,
                "post_change_d4_d8": (pts[8.0] - pts[4.0]) if 8.0 in pts and 4.0 in pts else None,
                "median_abs_daily_pre": float(np.median(dd)) if dd else None,
                "max_abs_daily_pre": float(np.max(dd)) if dd else None,
            })
    decisions = {}
    for a in ANALYTES:
        cs = [c for c in courses if c["analyte"] == a and c["post_change_d4_d6"] is not None]
        ch = [c["post_change_d4_d6"] for c in cs]
        same_dir = all(v > 0 for v in ch) or all(v < 0 for v in ch)
        med_post = float(np.median(np.abs(ch)))
        med_daily = float(np.median([c["median_abs_daily_pre"] for c in cs]))
        hi = [c["post_change_d4_d6"] for c in cs if c["dose_group"] == "high"]
        lo = [c["post_change_d4_d6"] for c in cs if c["dose_group"] == "low"]
        r3 = (min(hi) > max(lo)) if hi and lo else False
        decisions[a] = {"n_dogs": len(cs), "changes": {c["dog_id"]: c["post_change_d4_d6"] for c in cs},
                        "R1_same_direction": same_dir, "median_abs_post": med_post,
                        "median_abs_daily_pre": med_daily, "R2_exceeds_daily": med_post > med_daily,
                        "mean_change_high": float(np.mean(hi)) if hi else None,
                        "mean_change_low": float(np.mean(lo)) if lo else None,
                        "R3_high_more_upward": r3,
                        "all_rules": bool(same_dir and med_post > med_daily and r3)}
    return series, courses, decisions


# ---------- C1 ----------

def c1(sets, fid):
    s = sets[fid]
    x, y, wsev, wnon = [], [], [], []
    for dog, lab, r in s["infected"]:
        w, i8 = r["values"].get("wbc"), r["values"].get("il8")
        if w is not None and i8 is not None:
            x.append(i8)
            y.append(w)
        if w is not None and lab is not None:
            (wsev if lab == 1 else wnon).append(w)
    rho = spearman_full(x, y)
    wc = contrast(np.array(wsev), np.array(wnon), "wbc", logvals=False)
    return {"il8_wbc": rho, "wbc_contrast": wc}


def c3(sets, fid):
    """Deviation D1 (added after the lock, features only): infected vs healthy controls, each analyte."""
    s = sets[fid]
    out = []
    for a in ANALYTES:
        inf = np.array([value(r, a, s["half"], s["floors"]) for _, _, r in s["infected"]
                        if r["values"].get(a) is not None], float)
        ctl = np.array([value(r, a, s["half"], s["floors"]) for r in s["control"]
                        if r["values"].get(a) is not None], float)
        c = contrast(inf, ctl, a)
        c["file"] = fid
        c["n_infected"], c["n_control"] = len(inf), len(ctl)
        out.append(c)
    return out


def write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()})


def rnd(o):
    if isinstance(o, float):
        if math.isnan(o) or math.isinf(o):
            return None
        return round(o, 6)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [rnd(v) for v in o]
    if isinstance(o, (np.floating,)):
        return rnd(float(o))
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def main():
    hashes, spec = check_inputs()
    os.makedirs(OUT, exist_ok=True)
    results = {"seed": SEED, "n_boot": N_BOOT, "n_perm": N_PERM, "inputs_sha256": hashes, "spec_sha256": spec,
               "numpy": np.__version__}

    # Experiment 1, step 1 (primary) and C2
    sets = file_sets(half_floor=False)
    con = run_contrasts(sets, ["S-CB050", "S-CB017"])
    for c in con:
        c["timepoint"] = "admission (before treatment)" if c["file"] == "S-CB050" else "day 1 (6-8 h after imidocarb)"
        c["floor_handling"] = "as reported"
    con_d7 = run_contrasts(sets, ["S-CB017 day 7"])
    for c in con_d7:
        c["timepoint"] = "day 7 (6 days after imidocarb)"
        c["floor_handling"] = "as reported"
    # S2: half floor
    sets_h = file_sets(half_floor=True)
    con_h = run_contrasts(sets_h, ["S-CB050", "S-CB017"])
    for c in con_h:
        c["timepoint"] = "as primary"
        c["floor_handling"] = "half floor"

    il8 = {c["file"]: c for c in con if c["analyte"] == "il8"}
    a, b = il8["S-CB050"], il8["S-CB017"]
    excl = lambda c: c["cliff_lo"] > 0 or c["cliff_hi"] < 0
    if (a["cliff_delta"] > 0) == (b["cliff_delta"] > 0):
        verdict = "no conflict"
    elif excl(a) and excl(b):
        verdict = "conflict confirmed"
    else:
        verdict = "partial conflict"

    series, courses, decisions = ds02()
    c1res = {f: c1(sets, f) for f in ["S-CB050", "S-CB017"]}

    results["experiment1"] = {"contrasts": con, "contrasts_day7": con_d7, "contrasts_half_floor": con_h,
                              "il8_verdict": verdict, "ds02_decisions": decisions, "c1": c1res,
                              }

    # Experiment 2
    pert_rows, e2 = [], {}
    for fid in ["S-CB050", "S-CB017"]:
        rows, rngs, zpar = perturbation(sets, fid)
        rows_h, _, _ = perturbation(sets_h, fid)
        t1 = group_test(rows, "perturbation")
        t2 = group_test(rows, "balance")
        s1 = group_test(rows, "z_mean_abs")
        s1h = group_test(rows_h, "z_mean_abs")
        t1h = group_test(rows_h, "perturbation")
        t2h = group_test(rows_h, "balance")
        q = bh([t1["p"], t2["p"]])
        t1["q"], t2["q"] = q
        above = group_test(rows, "above")
        below = group_test(rows, "below")
        dist = {}
        for lab in (0, 1):
            cnt = [0] * 7
            for r in rows:
                if r["severe"] == lab:
                    cnt[r["perturbation"]] += 1
            dist["severe" if lab else "nonsevere"] = cnt
        e2[fid] = {"T1_perturbation": t1, "T2_balance": t2, "S1_z": s1, "S2_half_floor": {
            "T1": t1h, "T2": t2h, "S1_z": s1h}, "above": above, "below": below,
            "control_ranges": rngs, "control_log2_mean_sd": zpar, "distribution": dist,
            "outside_by_analyte": {
                lab: {a_: sum(1 for r in rows if r["severe"] == (1 if lab == "severe" else 0)
                              and (lambda v: v is not None and (v < rngs[a_][0] or v > rngs[a_][1]))(
                    next(rr for d, l, rr in sets[fid]["infected"] if d == r["dog_id"])["values"].get(a_)))
                      for a_ in ANALYTES}
                for lab in ("severe", "nonsevere")}}
        pert_rows += rows

    def ok(c):
        return c["cliff_lo"] > 0 or c["cliff_hi"] < 0
    t1s = [e2[f]["T1_perturbation"] for f in e2]
    t2s = [e2[f]["T2_balance"] for f in e2]
    if all(c["cliff_lo"] > 0 for c in t1s):
        e2v = "size"
    elif all(ok(c) for c in t2s) and len({c["cliff_delta"] > 0 for c in t2s}) == 1 and not all(ok(c) for c in t1s):
        e2v = "balance"
    elif not any(all(ok(c) for c in pair) for pair in (t1s, t2s)) and not any(ok(c) for c in t1s + t2s):
        e2v = "neither"
    else:
        e2v = "mixed"
    results["experiment2"] = {"by_file": e2, "verdict": e2v}

    # Deviation D1 (after the lock; features only). Run last so that it does not change the random draws of the spec analyses.
    c3res = {f: c3(sets, f) for f in ["S-CB050", "S-CB017"]}
    results["experiment1"]["c3_infected_vs_control"] = c3res

    # outputs
    cols = ["file", "timepoint", "analyte", "n_severe", "n_nonsevere", "median_severe", "median_nonsevere",
            "cliff_delta", "cliff_lo", "cliff_hi", "hl_log2", "hl_lo", "hl_hi", "p", "q", "floor_handling"]
    write_csv(os.path.join(OUT, "contrasts.csv"), con + con_d7 + con_h, cols)
    c3rows = [dict(c, median_infected=c["median_severe"], median_control=c["median_nonsevere"])
              for f in c3res for c in c3res[f]]
    write_csv(os.path.join(OUT, "infected_vs_control.csv"), c3rows,
              ["file", "analyte", "n_infected", "n_control", "median_infected", "median_control", "cliff_delta",
               "cliff_lo", "cliff_hi", "hl_log2", "hl_lo", "hl_hi", "p"])
    write_csv(os.path.join(OUT, "perturbation.csv"), pert_rows,
              ["file", "dog_id", "severe", "perturbation", "above", "below", "z_mean_abs", "il8", "mcp1",
               "pct_il8", "pct_mcp1", "balance"])
    write_csv(os.path.join(OUT, "ds02_courses.csv"), courses,
              ["dog_id", "dose_group", "analyte", "baseline_log2", "day4_log2", "day6_log2", "day8_log2",
               "pre_change_log2", "post_change_d4_d6", "post_change_d4_d8", "median_abs_daily_pre",
               "max_abs_daily_pre"])
    write_csv(os.path.join(OUT, "ds02_series.csv"), series,
              ["dog_id", "dose_group", "analyte", "day", "value", "log2_value_plus1", "post_treatment"])
    results["perturbation_rows"] = pert_rows
    results["ds02_courses"] = courses
    results["ds02_series"] = series
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
        json.dump(rnd(results), f, indent=1, allow_nan=False)
    print("IL-8 verdict:", verdict)
    for c in con + con_d7:
        print(f"{c['file']:14s} {c['analyte']:6s} n {c['n_severe']}/{c['n_nonsevere']} d {c['cliff_delta']:+.2f} "
              f"({c['cliff_lo']:+.2f} to {c['cliff_hi']:+.2f}) p {c['p']:.4f} q {c.get('q', 0):.3f} "
              f"med {c['median_severe']:.1f}/{c['median_nonsevere']:.1f}")
    for a_, d in decisions.items():
        print("DS02", a_, {k: d[k] for k in d if k != "changes"})
        print("     ", {k: round(v, 2) for k, v in d["changes"].items()})
    for f, r in c1res.items():
        print("C1", f, rnd(r["il8_wbc"]), "WBC d", round(r["wbc_contrast"]["cliff_delta"], 2),
              round(r["wbc_contrast"]["cliff_lo"], 2), round(r["wbc_contrast"]["cliff_hi"], 2))
    for f, e in e2.items():
        for k in ["T1_perturbation", "T2_balance", "S1_z", "above", "below"]:
            c = e[k]
            print("E2", f, k, f"d {c['cliff_delta']:+.2f} ({c['cliff_lo']:+.2f} to {c['cliff_hi']:+.2f}) p {c['p']:.4f}"
                  f" mean {c['mean_severe']:.2f}/{c['mean_nonsevere']:.2f}")
        print("   dist", e["distribution"], e["outside_by_analyte"])
    print("E2 verdict:", e2v)
    for f, rows in c3res.items():
        for c in rows:
            print("C3", f, c["analyte"], f"d {c['cliff_delta']:+.2f} ({c['cliff_lo']:+.2f} to {c['cliff_hi']:+.2f}) p {c['p']:.4f}"
                  f" med inf {c['median_severe']:.1f} ctl {c['median_nonsevere']:.1f}")


if __name__ == "__main__":
    main()
