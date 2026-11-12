"""SV-06b analysis: candidate mechanism proteins in DS07, complicated vs uncomplicated B. rossi.

Follows /experiments/SV-06/b/spec.md. Reads the SV-G1 tidy files only. Writes out/ds07_candidates.csv,
out/dog_values.csv, out/sensitivity_lopo.csv, out/results.json.
Usage (from /experiments/SV-06/b): env/py/Scripts/python.exe -I scripts/analyse.py
"""
import csv, hashlib, json, math, os
import numpy as np

ROOT = r"C:\Workspaces\Babesiosis"
PKG = os.path.join(ROOT, "experiments", "SV-06", "b")
TIDY = os.path.join(ROOT, "experiments", "shared", "tidy")
OUT = os.path.join(PKG, "out")
SEED = 20261112
B_PERM = 10_000
B_BOOT = 2_000

# Fixed by spec.md section 2. (key, label, accession, mechanism, in_family, role, expected direction)
CANDIDATES = [
    ("hbb", "Haemoglobin beta", "P60524", "F1-01 cell-free haemoglobin", True, "mechanism", "higher"),
    ("hp", "Haptoglobin (group master A0A5F4DB38)", "A0A5F4DB38", "F1-03 haptoglobin depletion", True, "mechanism", "lower"),
    ("ltf", "Lactoferrin", "F1PR54", "F3-03 neutrophil granule proteins", True, "positive_control", "higher"),
    ("s100a8", "S100A8", "C0LQL0", "F3-03/F3-12 neutrophil granule proteins, calprotectin", True, "mechanism", "higher"),
    ("h4", "Histone H4", "L7N0L3", "F3-02 extracellular histones", True, "mechanism", "higher"),
    ("serpinf2", "Alpha-2-antiplasmin (SERPINF2)", "E2R4V3", "F4-03 fibrinolytic shutdown", True, "mechanism", "higher"),
    ("proc", "Protein C", "Q28278", "F4-04 anticoagulant consumption", True, "mechanism", "lower"),
    ("serpinc1", "Antithrombin (SERPINC1)", "E2RES2", "F4-04 anticoagulant consumption", True, "mechanism", "lower"),
    ("cfh", "Complement factor H", "A0A5F4BVG1", "F7-12 complement regulation", True, "mechanism", "none stated"),
    ("cd14", "CD14", "A0A1S7J0A8", "F7-05 monocyte activation", True, "positive_control", "higher"),
    ("hba", "Haemoglobin alpha (group master J9NXL3)", "J9NXL3", "F1-01 cell-free haemoglobin", False, "secondary", "higher"),
]
Z975, Z80, Z9975 = 1.959964, 0.841621, 2.807034


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def cliff(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    s = np.sign(x[:, None] - y[None, :])
    return float(s.mean())


def hl(x, y):
    return float(np.median(np.asarray(x, float)[:, None] - np.asarray(y, float)[None, :]))


def perm_test(values, labels, strata, rng, stratified=True):
    """Two-sided permutation p for Cliff's delta; labels permuted inside each stratum."""
    v = np.asarray(values, float); lab = np.asarray(labels, int); n = len(v)
    S = np.sign(v[:, None] - v[None, :])
    n1 = lab.sum(); n0 = n - n1
    obs = float((lab @ S @ (1 - lab)) / (n1 * n0))
    P = np.empty((B_PERM, n), dtype=float)
    if stratified:
        strata = np.asarray(strata)
        P[:] = lab
        for s in np.unique(strata):
            idx = np.where(strata == s)[0]
            block = np.tile(lab[idx], (B_PERM, 1))
            P[:, idx] = rng.permuted(block, axis=1)
    else:
        P[:] = rng.permuted(np.tile(lab, (B_PERM, 1)), axis=1)
    d = ((P @ S) * (1 - P)).sum(axis=1) / (n1 * n0)
    count = int((np.abs(d) >= abs(obs) - 1e-12).sum())
    return obs, (1 + count) / (1 + B_PERM)


def bootstrap(x, y, rng):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ds, hs = np.empty(B_BOOT), np.empty(B_BOOT)
    for b in range(B_BOOT):
        xb = x[rng.integers(0, len(x), len(x))]; yb = y[rng.integers(0, len(y), len(y))]
        ds[b] = cliff(xb, yb); hs[b] = hl(xb, yb)
    q = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]
    return q(ds), q(hs)


def fisher_two_sided(a, b, c, d):
    """Fisher exact p for [[a,b],[c,d]] (two-sided, sum of tables with p <= observed)."""
    r1, r2, c1 = a + b, c + d, a + c
    n = r1 + r2
    def pmf(k):
        return math.comb(r1, k) * math.comb(r2, c1 - k) / math.comb(n, c1)
    lo, hi = max(0, c1 - r2), min(r1, c1)
    p0 = pmf(a)
    return float(min(1.0, sum(pmf(k) for k in range(lo, hi + 1) if pmf(k) <= p0 * (1 + 1e-9))))


def spearman(x, y):
    def rank(a):
        a = np.asarray(a, float); o = a.argsort(); r = np.empty(len(a)); r[o] = np.arange(len(a))
        for val in np.unique(a):  # average ties
            m = a == val
            r[m] = r[m].mean()
        return r
    rx, ry = rank(x), rank(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def bh(ps):
    idx = [i for i, p in enumerate(ps) if p is not None]
    m = len(ps)  # untested proteins count in the family size (spec section 3)
    q = [None] * len(ps)
    order = sorted(idx, key=lambda i: ps[i])
    prev = 1.0
    for rank in range(len(order), 0, -1):
        i = order[rank - 1]
        prev = min(prev, ps[i] * m / rank)
        q[i] = prev
    return q


def detectable(n1, n0, z):
    return (z + Z80) * math.sqrt(1 / n1 + 1 / n0)


def main():
    os.makedirs(OUT, exist_ok=True)
    fpath, opath = os.path.join(TIDY, "DS07.features.json"), os.path.join(TIDY, "DS07.outcomes.json")
    feat = json.load(open(fpath, encoding="utf-8")); outc = json.load(open(opath, encoding="utf-8"))
    lab = {r["dog_id"]: r["values"]["complicated"] for r in outc["records"]}
    dogs = feat["records"]
    for r in dogs:
        r["label"] = lab.get(r["dog_id"]) if r["group"] == "infected" else None
    infected = [r for r in dogs if r["group"] == "infected"]
    assert len(infected) == 32 and all(r["label"] in (0, 1) for r in infected)
    n_comp = sum(r["label"] for r in infected); n_unc = 32 - n_comp
    assert (n_comp, n_unc) == (14, 18)
    plex_layout = {}
    for r in dogs:
        p = r["values"]["plex"]
        k = "control" if r["group"] == "control" else ("complicated" if r["label"] == 1 else "uncomplicated")
        plex_layout.setdefault(p, {"complicated": 0, "uncomplicated": 0, "control": 0})[k] += 1

    rows, dog_rows, lopo_rows = [], [], []
    hbb_var = "p_p60524"
    for i, (key, name, acc, mech, fam, role, expect) in enumerate(CANDIDATES):
        var = "p_" + acc.lower()
        obs = [r for r in infected if r["values"].get(var) is not None]
        comp = [r["values"][var] for r in obs if r["label"] == 1]
        unc = [r["values"][var] for r in obs if r["label"] == 0]
        ctrl_obs = [r for r in dogs if r["group"] == "control" and r["values"].get(var) is not None]
        for r in dogs:
            v = r["values"].get(var)
            g = "control" if r["group"] == "control" else ("complicated" if r["label"] == 1 else "uncomplicated")
            dog_rows.append({"protein": key, "dog_id": r["dog_id"], "plex": r["values"]["plex"], "group": g,
                             "value": None if v is None else round(v, 6)})
        frac_c, frac_u = len(comp) / n_comp, len(unc) / n_unc
        full = frac_c >= 0.6 and frac_u >= 0.6
        presence_p = None
        if not full:
            presence_p = fisher_two_sided(len(comp), n_comp - len(comp), len(unc), n_unc - len(unc))
        rec = {"key": key, "protein": name, "accession": acc, "mechanism": mech, "in_family": fam, "role": role,
               "expected_direction": expect, "n_comp": len(comp), "n_unc": len(unc), "n_ctrl": len(ctrl_obs),
               "frac_comp": round(frac_c, 3), "frac_unc": round(frac_u, 3),
               "coverage_rule": "full" if full else "low coverage", "presence_fisher_p": presence_p,
               "plexes_observed": sorted({r["values"]["plex"] for r in obs})}
        if len(comp) >= 3 and len(unc) >= 3:
            vals = [r["values"][var] for r in obs]; labs = [r["label"] for r in obs]; strata = [r["values"]["plex"] for r in obs]
            d, p = perm_test(vals, labs, strata, np.random.Generator(np.random.PCG64(SEED)))
            d_u, p_u = perm_test(vals, labs, strata, np.random.Generator(np.random.PCG64(SEED)), stratified=False)
            ci_d, ci_h = bootstrap(comp, unc, np.random.Generator(np.random.PCG64(SEED + i)))
            lo = []
            for pl in sorted({s for s in strata}):
                c2 = [r["values"][var] for r in obs if r["label"] == 1 and r["values"]["plex"] != pl]
                u2 = [r["values"][var] for r in obs if r["label"] == 0 and r["values"]["plex"] != pl]
                if c2 and u2:
                    dd = cliff(c2, u2); lo.append(dd)
                    lopo_rows.append({"protein": key, "plex_left_out": pl, "delta": round(dd, 4)})
            # infected vs control, plex-stratified (S3)
            allobs = obs + ctrl_obs
            v2 = [r["values"][var] for r in allobs]; l2 = [1 if r["group"] == "infected" else 0 for r in allobs]
            s2 = [r["values"]["plex"] for r in allobs]
            d_ic, p_ic = perm_test(v2, l2, s2, np.random.Generator(np.random.PCG64(SEED))) if ctrl_obs else (None, None)
            # S5: rho with haemoglobin beta among infected
            both = [r for r in obs if r["values"].get(hbb_var) is not None]
            rho = spearman([r["values"][var] for r in both], [r["values"][hbb_var] for r in both]) if key != "hbb" else 1.0
            sdp = float(np.std(vals, ddof=1))
            rec.update({"tested": True, "delta": round(d, 4), "delta_lo": round(ci_d[0], 4), "delta_hi": round(ci_d[1], 4),
                        "hl_log2": round(hl(comp, unc), 4), "hl_lo": round(ci_h[0], 4), "hl_hi": round(ci_h[1], 4),
                        "p_stratified": round(p, 5), "p_unstratified": round(p_u, 5), "delta_unstratified": round(d_u, 4),
                        "median_comp": round(float(np.median(comp)), 4), "median_unc": round(float(np.median(unc)), 4),
                        "median_ctrl": round(float(np.median([r["values"][var] for r in ctrl_obs])), 4) if ctrl_obs else None,
                        "sd_infected": round(sdp, 4), "hl_sd_units": round(hl(comp, unc) / sdp, 3) if sdp > 0 else None,
                        "lopo_min": round(min(lo), 4), "lopo_max": round(max(lo), 4),
                        "lopo_sign_change": bool(min(lo) < 0 < max(lo)),
                        "delta_infected_vs_control": None if d_ic is None else round(d_ic, 4),
                        "p_infected_vs_control": None if p_ic is None else round(p_ic, 5),
                        "rho_with_hbb": round(rho, 3), "n_rho": len(both),
                        "detectable_sd_a05": round(detectable(len(comp), len(unc), Z975), 2),
                        "detectable_sd_a005": round(detectable(len(comp), len(unc), Z9975), 2)})
        else:
            rec.update({"tested": False})
        rows.append(rec)

    fam = [r for r in rows if r["in_family"]]
    qs = bh([r.get("p_stratified") if r["tested"] else None for r in fam])
    for r, q in zip(fam, qs):
        r["q_bh"] = None if q is None else round(q, 5)
    for r in rows:
        r.setdefault("q_bh", None)
    pc = [r for r in rows if r["role"] == "positive_control"]
    pipeline_ok = all(r["tested"] and r["delta"] > 0 for r in pc)
    mech = [r for r in fam if r["role"] == "mechanism"]
    mech_hits = [r["key"] for r in mech if r["q_bh"] is not None and r["q_bh"] < 0.05]
    family_hits = [r["key"] for r in fam if r["q_bh"] is not None and r["q_bh"] < 0.05]

    cols = ["key", "protein", "accession", "mechanism", "role", "in_family", "expected_direction", "coverage_rule",
            "n_comp", "n_unc", "n_ctrl", "frac_comp", "frac_unc", "plexes_observed", "tested", "median_comp", "median_unc",
            "median_ctrl", "delta", "delta_lo", "delta_hi", "hl_log2", "hl_lo", "hl_hi", "hl_sd_units", "p_stratified",
            "q_bh", "p_unstratified", "delta_unstratified", "lopo_min", "lopo_max", "lopo_sign_change",
            "delta_infected_vs_control", "p_infected_vs_control", "rho_with_hbb", "n_rho", "presence_fisher_p",
            "detectable_sd_a05", "detectable_sd_a005"]
    with open(os.path.join(OUT, "ds07_candidates.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for r in rows:
            w.writerow({k: (";".join(r[k]) if isinstance(r.get(k), list) else r.get(k)) for k in cols})
    with open(os.path.join(OUT, "dog_values.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["protein", "dog_id", "plex", "group", "value"]); w.writeheader(); w.writerows(dog_rows)
    with open(os.path.join(OUT, "sensitivity_lopo.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["protein", "plex_left_out", "delta"]); w.writeheader(); w.writerows(lopo_rows)

    res = {"spec_sha256": sha(os.path.join(PKG, "spec.md")), "script_sha256": sha(__file__),
           "inputs": {"DS07.features.json": sha(fpath), "DS07.outcomes.json": sha(opath)},
           "seed": SEED, "n_perm": B_PERM, "n_boot": B_BOOT, "numpy": np.__version__,
           "n_comp": n_comp, "n_unc": n_unc, "n_ctrl": sum(1 for r in dogs if r["group"] == "control"),
           "family_size": len(fam), "n_tested": sum(1 for r in fam if r["tested"]),
           "plex_layout": dict(sorted(plex_layout.items(), key=lambda kv: int(kv[0][1:]))),
           "positive_controls_consistent": pipeline_ok, "mechanism_hits_q05": mech_hits, "family_hits_q05": family_hits,
           "candidates": rows, "dog_values": dog_rows, "lopo": lopo_rows}
    json.dump(res, open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"), indent=1, allow_nan=False)
    for r in rows:
        if r["tested"]:
            print(f"{r['key']:9s} n {r['n_comp']}/{r['n_unc']} d {r['delta']:+.3f} ({r['delta_lo']:+.2f},{r['delta_hi']:+.2f}) "
                  f"HL {r['hl_log2']:+.3f} p {r['p_stratified']:.4f} q {r['q_bh']} pu {r['p_unstratified']:.4f} "
                  f"lopo {r['lopo_min']:+.2f}..{r['lopo_max']:+.2f} IvC {r['delta_infected_vs_control']} rhoHBB {r['rho_with_hbb']} {r['coverage_rule']}")
        else:
            print(r["key"], "untested", r["n_comp"], r["n_unc"])
    print("positive controls consistent:", pipeline_ok, "mechanism hits:", mech_hits, "family hits:", family_hits)


if __name__ == "__main__":
    main()
