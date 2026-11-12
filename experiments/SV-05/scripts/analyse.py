"""SV-05: age, sex and neuter status in B. rossi (spec.md, frozen 2026-11-12).

Run from /experiments/SV-05/:  env/py/Scripts/python.exe -I scripts/analyse.py
Writes out/age_contrasts.csv and out/results.json. Seed 20261112, one generator, draws in spec order.
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
from scipy.stats.contingency import odds_ratio

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
EXP = os.path.dirname(PKG)
TIDY = os.path.join(EXP, "shared", "tidy")
OUT = os.path.join(PKG, "out")
SEED = 20261112
B_PERM = 10000
B_BOOT = 2000
YOUNG_CUT = 12.0

INPUTS = {
    "shared/tidy/S-CB050.features.json": "fedde71e230325695e0866bd362d932a83904dc50de7883003dc6431cff9460f",
    "shared/tidy/DS05.features.json": "323238159fb21596dacc02464fe4ebdf7bd54282cd06fdce7535057f28e90a1e",
    "shared/tidy/DS03.features.json": "2862ac7e6e5fcec6200024543e4142fbe81eabd2eadef06d4f288bc982eda8a6",
    "shared/tidy/S-CB050.outcomes.json": "d2657b5321d1dd8528d8e363a8bf621398df32b538301d68df81976562f2d813",
    "SV-04/out/perturbation.csv": "88e1e3c48148d205870d3535545595ae3105c275c4781251a04d2d2db8cfde7b",
}
SPEC_SHA = "dd68cbd66a738637cead48e9707a08a3c3fec84d5fd0286307d804b475e1782f"


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_inputs():
    if sha(os.path.join(PKG, "spec.md")) != SPEC_SHA:
        sys.exit("spec.md changed after it was frozen")
    with open(os.path.join(PKG, "exposure.md"), encoding="utf-8") as f:
        exposure = f.read()
    for rel, h in INPUTS.items():
        got = sha(os.path.join(EXP, rel))
        if got != h:
            sys.exit(f"input changed: {rel} {got}")
    for rel in ("S-CB050.outcomes.json", "perturbation.csv"):
        if INPUTS[[k for k in INPUTS if k.endswith(rel)][0]] not in exposure:
            sys.exit(f"{rel} is not in exposure.md")


def load(name):
    with open(os.path.join(TIDY, name), encoding="utf-8") as f:
        return json.load(f)


rng = np.random.default_rng(SEED)


# ---------- statistics ----------
def r6(x):
    if x is None:
        return None
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        return None
    return round(x, 6)


def cliff(a, b):
    a = np.asarray(a, float)[:, None]
    b = np.asarray(b, float)[None, :]
    return float((np.sign(a - b)).mean())


def hl(a, b):
    return float(np.median((np.asarray(a, float)[:, None] - np.asarray(b, float)[None, :]).ravel()))


def boot_two(a, b, fn):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    vals = np.empty(B_BOOT)
    for i in range(B_BOOT):
        vals[i] = fn(a[rng.integers(0, len(a), len(a))], b[rng.integers(0, len(b), len(b))])
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def perm_two(a, b):
    """Two-sided permutation p of the Mann-Whitney U (|Cliff's delta|), by dog."""
    x = np.concatenate([a, b]).astype(float)
    na = len(a)
    obs = abs(cliff(a, b))
    k = 0
    for _ in range(B_PERM):
        p = rng.permutation(x)
        if abs(cliff(p[:na], p[na:])) >= obs - 1e-12:
            k += 1
    return (k + 1) / (B_PERM + 1)


def detectable_sd(n1, n2):
    return 2.8016 * math.sqrt(1 / n1 + 1 / n2)


def rank_contrast(young, adult):
    """HL (young - adult) with bootstrap CI, Cliff's delta with CI, permutation p."""
    young = [float(v) for v in young]
    adult = [float(v) for v in adult]
    est = hl(young, adult)
    hlo, hhi = boot_two(young, adult, hl)
    cd = cliff(young, adult)
    clo, chi = boot_two(young, adult, cliff)
    p = perm_two(np.array(young), np.array(adult))
    return {"n_young": len(young), "n_adult": len(adult),
            "median_young": r6(np.median(young)), "median_adult": r6(np.median(adult)),
            "iqr_young": [r6(np.percentile(young, 25)), r6(np.percentile(young, 75))],
            "iqr_adult": [r6(np.percentile(adult, 25)), r6(np.percentile(adult, 75))],
            "hl": r6(est), "hl_low": r6(hlo), "hl_high": r6(hhi),
            "cliff": r6(cd), "cliff_low": r6(clo), "cliff_high": r6(chi),
            "p": r6(p), "detectable_sd": r6(detectable_sd(len(young), len(adult)))}


def wilson(x, n, z=1.959964):
    if n == 0:
        return (None, None)
    p = x / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def newcombe(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1)
    l2, u2 = wilson(x2, n2)
    d = p1 - p2
    return d, d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def table_or(a, b, c, d):
    """2x2 [[a, b], [c, d]]: rows young/adult, columns event/no event."""
    t = np.array([[a, b], [c, d]])
    res = odds_ratio(t, kind="conditional")
    ci = res.confidence_interval(0.95)
    p = stats.fisher_exact(t, alternative="two-sided").pvalue
    return {"table": [[int(a), int(b)], [int(c), int(d)]], "or": r6(res.statistic),
            "or_low": r6(ci.low), "or_high": r6(ci.high), "p": r6(p)}


def share_contrast(ev_y, n_y, ev_a, n_a):
    d, lo, hi = newcombe(ev_y, n_y, ev_a, n_a)
    o = table_or(ev_y, n_y - ev_y, ev_a, n_a - ev_a)
    o.update({"n_young": n_y, "n_adult": n_a, "events_young": ev_y, "events_adult": ev_a,
              "share_young": r6(ev_y / n_y), "share_adult": r6(ev_a / n_a),
              "diff": r6(d), "diff_low": r6(lo), "diff_high": r6(hi)})
    return o


def mh(strata):
    """Mantel-Haenszel OR with the Robins-Breslow-Greenland interval. strata: list of (a, b, c, d)."""
    R = S = PR = PSQS = QS = 0.0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n == 0:
            continue
        r, s = a * d / n, b * c / n
        P, Q = (a + d) / n, (b + c) / n
        R += r
        S += s
        PR += P * r
        PSQS += P * s + Q * r
        QS += Q * s
    est = R / S
    var = PR / (2 * R * R) + PSQS / (2 * R * S) + QS / (2 * S * S)
    se = math.sqrt(var)
    return est, math.exp(math.log(est) - 1.959964 * se), math.exp(math.log(est) + 1.959964 * se)


def strat_perm(young, died, stratum):
    """Two-sided p: permute age group within strata; statistic = deaths among young dogs."""
    young = np.asarray(young, bool)
    died = np.asarray(died, int)
    stratum = np.asarray(stratum)
    obs = int(died[young].sum())
    groups = [np.where(stratum == s)[0] for s in np.unique(stratum)]
    sims = np.empty(B_PERM)
    for i in range(B_PERM):
        y = young.copy()
        for g in groups:
            y[g] = rng.permutation(young[g])
        sims[i] = died[y].sum()
    centre = sims.mean()
    k = int((np.abs(sims - centre) >= abs(obs - centre) - 1e-9).sum())
    return obs, float(centre), (k + 1) / (B_PERM + 1)


def spearman_boot(x, y):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    rho = stats.spearmanr(x, y).statistic
    vals = np.empty(B_BOOT)
    for i in range(B_BOOT):
        idx = rng.integers(0, len(x), len(x))
        vals[i] = stats.spearmanr(x[idx], y[idx]).statistic
    vals = vals[~np.isnan(vals)]
    return {"n": len(x), "rho": r6(rho), "rho_low": r6(np.percentile(vals, 2.5)),
            "rho_high": r6(np.percentile(vals, 97.5))}


def bh(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    q = [0.0] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        prev = min(prev, ps[i] * m / rank)
        q[i] = prev
    return q


def detectable_or(p0, n1, n0):
    """Smallest OR > 1 detectable at 80% power, two-sided 0.05 (two-proportion z-test), p0 = adult death rate."""
    z_a, z_b = 1.959964, 0.841621
    for orv in np.arange(1.01, 30, 0.01):
        odds = orv * p0 / (1 - p0)
        p1 = odds / (1 + odds)
        pbar = (n1 * p1 + n0 * p0) / (n1 + n0)
        num = abs(p1 - p0) - z_a * math.sqrt(pbar * (1 - pbar) * (1 / n1 + 1 / n0))
        den = math.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
        if stats.norm.cdf(num / den) >= 0.8:
            return float(round(orv, 2))
    return None


# ---------- data ----------
def main():
    check_inputs()
    os.makedirs(OUT, exist_ok=True)

    sc = load("S-CB050.features.json")
    so = load("S-CB050.outcomes.json")
    ds05 = load("DS05.features.json")
    ds03 = load("DS03.features.json")
    died = {r["dog_id"]: r["values"]["died"] for r in so["records"]}

    sc_inf = [r for r in sc["records"] if r["group"] == "infected"]
    sc_age_missing = sum(1 for r in sc_inf if r["values"].get("age_months") is None)
    sc_inf = [r for r in sc_inf if r["values"].get("age_months") is not None]
    d05_all = [r for r in ds05["records"] if r["group"] == "infected" and r["values"].get("pcr_b_rossi") == 1]
    d05_age_missing = sum(1 for r in d05_all if r["values"].get("age_months") is None)
    d05 = [r for r in d05_all if r["values"].get("age_months") is not None]
    d03_all = [r for r in ds03["records"] if r["group"] == "infected" and r["values"].get("setting") == "natural"]
    d03_age_missing = sum(1 for r in d03_all if r["values"].get("age_months") is None)
    d03 = [r for r in d03_all if r["values"].get("age_months") is not None]
    d03_ctrl = [r for r in ds03["records"] if r["values"].get("setting") == "healthy"]

    def young(r):
        return r["values"]["age_months"] < YOUNG_CUT

    def split(recs, var, extra=None):
        y, a = [], []
        for r in recs:
            v = r["values"].get(var)
            if v is None or (extra and not extra(r)):
                continue
            (y if young(r) else a).append(float(v))
        return y, a

    pert = {}
    with open(os.path.join(EXP, "SV-04", "out", "perturbation.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["file"] == "S-CB050":
                pert[row["dog_id"]] = row   # column `severe` is not used
    sc_age = {r["dog_id"]: r["values"]["age_months"] for r in sc_inf}
    pert_missing_age = sum(1 for k in pert if k not in sc_age)

    def pert_split(col):
        y, a = [], []
        for k, row in pert.items():
            if k not in sc_age or row[col] in ("", None):
                continue
            (y if sc_age[k] < YOUNG_CUT else a).append(float(row[col]))
        return y, a

    R = {"seed": SEED, "b_perm": B_PERM, "b_boot": B_BOOT, "young_cut_months": YOUNG_CUT,
         "spec_sha256": SPEC_SHA, "inputs": INPUTS,
         "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__},
         "dogs": {"S-CB050": {"infected": len(sc_inf) + sc_age_missing, "age_missing": sc_age_missing,
                              "young": sum(young(r) for r in sc_inf), "adult": sum(not young(r) for r in sc_inf),
                              "cohort1_in_perturbation": len(pert), "cohort1_age_missing": pert_missing_age},
                  "DS05": {"b_rossi": len(d05_all), "age_missing": d05_age_missing,
                           "young": sum(young(r) for r in d05), "adult": sum(not young(r) for r in d05)},
                  "DS03": {"natural": len(d03_all), "age_missing": d03_age_missing,
                           "young": sum(young(r) for r in d03), "adult": sum(not young(r) for r in d03)}}}

    # ---------- family A: risk ----------
    a_cells = {"yd": 0, "ys": 0, "ad": 0, "as": 0}
    strata = {}
    yv, dv, sv, ages_died, ages_surv = [], [], [], [], []
    for r in sc_inf:
        dd = died[r["dog_id"]]
        y = young(r)
        a_cells[("y" if y else "a") + ("d" if dd == 1 else "s")] += 1
        sex = r["values"]["sex"]
        s = strata.setdefault(sex, [0, 0, 0, 0])
        s[(0 if y else 2) + (0 if dd == 1 else 1)] += 1
        yv.append(y)
        dv.append(dd)
        sv.append(sex)
        (ages_died if dd == 1 else ages_surv).append(r["values"]["age_months"])
    A1 = table_or(a_cells["yd"], a_cells["ys"], a_cells["ad"], a_cells["as"])
    n_y = a_cells["yd"] + a_cells["ys"]
    n_a = a_cells["ad"] + a_cells["as"]
    A1.update({"n_young": n_y, "n_adult": n_a, "deaths_young": a_cells["yd"], "deaths_adult": a_cells["ad"],
               "share_young": r6(a_cells["yd"] / n_y), "share_adult": r6(a_cells["ad"] / n_a),
               "detectable_or_above_1": detectable_or(a_cells["ad"] / n_a, n_y, n_a)})
    # smallest detectable OR below 1 (protective young): by symmetry swap groups
    A1["detectable_or_below_1"] = r6(1 / detectable_or(a_cells["yd"] / n_y, n_a, n_y))
    A2 = {"by_sex": {}}
    for sex in sorted(strata):
        a, b, c, d = strata[sex]
        A2["by_sex"][sex] = table_or(a, b, c, d)
        A2["by_sex"][sex].update({"n_young": a + b, "n_adult": c + d, "deaths_young": a, "deaths_adult": c})
    est, lo, hi = mh([tuple(strata[s]) for s in sorted(strata)])
    obs, centre, p = strat_perm(yv, dv, sv)
    A2.update({"mh_or": r6(est), "mh_low": r6(lo), "mh_high": r6(hi), "deaths_young_obs": obs,
               "deaths_young_expected": r6(centre), "p": r6(p)})
    A3 = rank_contrast(ages_died, ages_surv)  # here "young" = died, "adult" = survived
    A3 = {"n_died": A3["n_young"], "n_survived": A3["n_adult"], "median_died": A3["median_young"],
          "median_survived": A3["median_adult"], "iqr_died": A3["iqr_young"], "iqr_survived": A3["iqr_adult"],
          "hl_months": A3["hl"], "hl_low": A3["hl_low"], "hl_high": A3["hl_high"], "cliff": A3["cliff"],
          "cliff_low": A3["cliff_low"], "cliff_high": A3["cliff_high"], "p": A3["p"],
          "detectable_sd": A3["detectable_sd"]}
    qa = bh([A1["p"], A2["p"], A3["p"]])
    A1["q"], A2["q"], A3["q"] = r6(qa[0]), r6(qa[1]), r6(qa[2])
    R["family_A"] = {"A1": A1, "A2": A2, "A3": A3, "size": 3}

    # ---------- family B: form ----------
    B = {}
    B["B1"] = rank_contrast(*split(d05, "hct"))
    B["B2"] = rank_contrast(*split(d03, "hct"))
    B["B3"] = rank_contrast(*split(d05, "neut_band"))
    B["B4"] = rank_contrast(*split(sc_inf, "neut_band"))
    B["B5"] = rank_contrast(*pert_split("perturbation"))

    def share(recs, var, pred, extra=None):
        y, a = split(recs, var, extra)
        return share_contrast(sum(pred(v) for v in y), len(y), sum(pred(v) for v in a), len(a))

    B["B6"] = share(d05, "hct", lambda v: v < 0.15)
    B["B7"] = share(d05, "neut_band", lambda v: v > 0.5)
    B["B8"] = rank_contrast(*split(d05, "illness_days"))
    keys = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
    qb = bh([B[k]["p"] for k in keys])
    for k, q in zip(keys, qb):
        B[k]["q"] = r6(q)
    B["size"] = 8
    R["family_B"] = B

    # ---------- secondary ----------
    S = {}
    S["balance"] = rank_contrast(*pert_split("balance"))
    S["z_mean_abs"] = rank_contrast(*pert_split("z_mean_abs"))
    S["wbc"] = rank_contrast(*split(sc_inf, "wbc"))
    S["neut_seg"] = rank_contrast(*split(sc_inf, "neut_seg"))
    sex_tab = {"male": [0, 0], "female": [0, 0]}
    for r in sc_inf:
        sex_tab[r["values"]["sex"]][0 if died[r["dog_id"]] == 1 else 1] += 1
    S["death_by_sex"] = table_or(sex_tab["male"][0], sex_tab["male"][1], sex_tab["female"][0], sex_tab["female"][1])
    S["death_by_sex"].update({"rows": "male, female", "n_male": sum(sex_tab["male"]), "n_female": sum(sex_tab["female"]),
                              "deaths_male": sex_tab["male"][0], "deaths_female": sex_tab["female"][0]})

    def sex_split(recs, var):
        m = [float(r["values"][var]) for r in recs if r["values"].get(var) is not None and r["values"].get("sex") == "male"]
        f = [float(r["values"][var]) for r in recs if r["values"].get(var) is not None and r["values"].get("sex") == "female"]
        return m, f

    S["ds05_hct_by_sex"] = rank_contrast(*sex_split(d05, "hct"))       # male minus female
    S["ds05_band_by_sex"] = rank_contrast(*sex_split(d05, "neut_band"))
    # neuter description: DS05 neutered vs intact adults
    neut = [r for r in d05 if r["values"].get("neuter") == "neutered"]
    intact_ad = [r for r in d05 if r["values"].get("neuter") == "intact" and not young(r)]

    def desc(recs, var):
        v = [float(r["values"][var]) for r in recs if r["values"].get(var) is not None]
        if not v:
            return {"n": 0, "median": None, "min": None, "max": None}
        return {"n": len(v), "median": r6(np.median(v)), "min": r6(min(v)), "max": r6(max(v))}

    S["neuter"] = {"n_neutered": len(neut), "n_neutered_young": sum(young(r) for r in neut),
                   "sex_neutered": {s: sum(1 for r in neut if r["values"]["sex"] == s) for s in ("male", "female")},
                   "vars": {v: {"neutered": desc(neut, v), "intact_adult": desc(intact_ad, v)}
                            for v in ("age_months", "hct", "neut_band", "illness_days", "weight_kg")}}
    R["secondary"] = S

    # ---------- sensitivity and checks ----------
    T = {}
    T["S1_severe_anaemia_020"] = share(d05, "hct", lambda v: v < 0.20)
    no_ec = lambda r: r["values"].get("pcr_e_canis") != 1  # noqa: E731
    T["S2"] = {"n_excluded": sum(1 for r in d05 if not no_ec(r)),
               "B1": rank_contrast(*split(d05, "hct", no_ec)),
               "B3": rank_contrast(*split(d05, "neut_band", no_ec)),
               "B6": share(d05, "hct", lambda v: v < 0.15, no_ec),
               "B7": share(d05, "neut_band", lambda v: v > 0.5, no_ec),
               "B8": rank_contrast(*split(d05, "illness_days", no_ec))}

    def age_pairs(recs, var):
        p = [(r["values"]["age_months"], r["values"][var]) for r in recs if r["values"].get(var) is not None]
        return [x for x, _ in p], [y for _, y in p]

    pa = [(sc_age[k], float(row["perturbation"])) for k, row in pert.items() if k in sc_age]
    T["S3"] = {"DS05_hct": spearman_boot(*age_pairs(d05, "hct")),
               "DS03_hct": spearman_boot(*age_pairs(d03, "hct")),
               "DS05_band": spearman_boot(*age_pairs(d05, "neut_band")),
               "S-CB050_band": spearman_boot(*age_pairs(sc_inf, "neut_band")),
               "S-CB050_perturbation": spearman_boot([x for x, _ in pa], [y for _, y in pa]),
               "DS05_illness_days": spearman_boot(*age_pairs(d05, "illness_days"))}
    T["S4"] = {}
    for sex in ("male", "female"):
        f = (lambda s: (lambda r: r["values"].get("sex") == s))(sex)
        T["S4"][sex] = {"B1": rank_contrast(*split(d05, "hct", f)), "B3": rank_contrast(*split(d05, "neut_band", f))}
    cy, ca = split([r for r in d03_ctrl if r["values"].get("age_months") is not None], "hct")
    T["C1"] = {"n_young": len(cy), "n_adult": len(ca),
               "young": [r6(v) for v in sorted(cy)],
               "median_adult": r6(np.median(ca)) if ca else None,
               "range_adult": [r6(min(ca)), r6(max(ca))] if ca else None,
               "ages_controls": sorted(r["values"]["age_months"] for r in d03_ctrl if r["values"].get("age_months") is not None)}
    R["sensitivity"] = T

    # ---------- descriptive age-band profile (figure only, no test) ----------
    bands = [(0, 6, "< 6"), (6, 12, "6-11"), (12, 24, "12-23"), (24, 48, "24-47"), (48, 96, "48-95"), (96, 1e9, "96+")]

    def band_rows(recs, var):
        out = []
        for lo, hi, lab in bands:
            v = [float(r["values"][var]) for r in recs
                 if lo <= r["values"]["age_months"] < hi and r["values"].get(var) is not None]
            out.append({"band": lab, "n": len(v), "median": r6(np.median(v)) if v else None,
                        "q1": r6(np.percentile(v, 25)) if v else None, "q3": r6(np.percentile(v, 75)) if v else None})
        return out

    death_bands = []
    for lo, hi, lab in bands:
        g = [r for r in sc_inf if lo <= r["values"]["age_months"] < hi]
        dd = sum(died[r["dog_id"]] == 1 for r in g)
        death_bands.append({"band": lab, "n": len(g), "died": int(dd), "share": r6(dd / len(g)) if g else None})
    R["profile"] = {"bands": [b[2] for b in bands], "death_S-CB050": death_bands,
                    "hct_DS05": band_rows(d05, "hct"), "hct_DS03": band_rows(d03, "hct"),
                    "band_DS05": band_rows(d05, "neut_band"), "band_S-CB050": band_rows(sc_inf, "neut_band"),
                    "illness_DS05": band_rows(d05, "illness_days")}

    # ---------- decision rule ----------
    def excl0(c, lo="hl_low", hi="hl_high"):
        return c[lo] is not None and c[hi] is not None and (c[lo] > 0 or c[hi] < 0)

    anaemia = B["B1"]["hl_high"] < 0 and B["B2"]["hl"] < 0
    infl_parts = []
    if B["B3"]["hl_high"] < 0 and B["B4"]["hl"] < 0:
        infl_parts.append("B3")
    if B["B4"]["hl_high"] < 0 and B["B3"]["hl"] < 0:
        infl_parts.append("B4")
    if B["B5"]["hl_high"] < 0:
        infl_parts.append("B5")
    # rank tests on counts can give HL = 0 with an interval of [0, 0]; use Cliff's delta interval for B5 as well
    if "B5" not in infl_parts and B["B5"]["cliff_high"] < 0:
        infl_parts.append("B5 (Cliff)")
    inflammatory = bool(infl_parts)
    risk = A1["or_low"] > 1 or A1["or_high"] < 1
    against = []
    if B["B1"]["hl_low"] > 0:
        against.append("B1: young dogs have a higher haematocrit")
    if B["B3"]["hl_low"] > 0:
        against.append("B3: young dogs have more bands")
    if B["B4"]["hl_low"] > 0:
        against.append("B4: young dogs have more bands")
    if anaemia and inflammatory and not risk:
        verdict = "Supported"
    elif (anaemia or inflammatory) and not risk:
        verdict = "Partly supported"
    elif risk and not (anaemia or inflammatory):
        verdict = "Risk, not form"
    elif not (anaemia or inflammatory):
        verdict = "Not supported"
    else:
        verdict = "Form and risk"  # not named in the spec: both a form and a risk signal
    R["decision"] = {"anaemia_form_signal": anaemia, "inflammatory_form_signal": inflammatory,
                     "inflammatory_parts": infl_parts, "risk_signal": risk, "against": against,
                     "verdict": verdict}

    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(R, f, indent=1, allow_nan=False)

    # ---------- age_contrasts.csv ----------
    rows = []
    src = {"S-CB050": "SRC-A", "DS03": "SRC-A (same dogs as S-CB050, SV-07)", "DS05": "SRC-F"}
    rows.append(["A", "A1", "S-CB050", src["S-CB050"], "died (incl. euthanasia)", n_y, n_a,
                 A1["share_young"], A1["share_adult"], "odds_ratio", A1["or"], A1["or_low"], A1["or_high"],
                 None, None, None, A1["p"], A1["q"]])
    rows.append(["A", "A2", "S-CB050", src["S-CB050"], "died, stratified by sex (MH)", n_y, n_a, None, None,
                 "odds_ratio_mh", A2["mh_or"], A2["mh_low"], A2["mh_high"], None, None, None, A2["p"], A2["q"]])
    rows.append(["A", "A3", "S-CB050", src["S-CB050"], "age months, died minus survived", A3["n_died"],
                 A3["n_survived"], A3["median_died"], A3["median_survived"], "hl_months", A3["hl_months"],
                 A3["hl_low"], A3["hl_high"], A3["cliff"], A3["cliff_low"], A3["cliff_high"], A3["p"], A3["q"]])
    meta = {"B1": ("DS05", "haematocrit L/L"), "B2": ("DS03", "haematocrit L/L"),
            "B3": ("DS05", "band neutrophils 10^9/L"), "B4": ("S-CB050", "band neutrophils 10^9/L"),
            "B5": ("S-CB050", "SV-04 perturbation count (cohort 1)"), "B6": ("DS05", "severe anaemia hct < 0.15"),
            "B7": ("DS05", "left shift bands > 0.5"), "B8": ("DS05", "illness duration days")}
    for k in keys:
        c = B[k]
        ds, m = meta[k]
        if "diff" in c:
            rows.append(["B", k, ds, src[ds], m, c["n_young"], c["n_adult"], c["share_young"], c["share_adult"],
                         "difference_in_share", c["diff"], c["diff_low"], c["diff_high"], None, None, None,
                         c["p"], c["q"]])
        else:
            rows.append(["B", k, ds, src[ds], m, c["n_young"], c["n_adult"], c["median_young"], c["median_adult"],
                         "hl", c["hl"], c["hl_low"], c["hl_high"], c["cliff"], c["cliff_low"], c["cliff_high"],
                         c["p"], c["q"]])
    with open(os.path.join(OUT, "age_contrasts.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["family", "test", "dataset", "source", "measure", "n_young", "n_adult", "young_value",
                    "adult_value", "effect", "estimate", "ci_low", "ci_high", "cliff_delta", "cliff_low",
                    "cliff_high", "p", "q"])
        for row in rows:
            w.writerow(["" if v is None else v for v in row])
    print(json.dumps(R["decision"]), "A1", A1["or"], A1["or_low"], A1["or_high"], A1["p"])


if __name__ == "__main__":
    main()
