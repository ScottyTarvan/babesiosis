"""SV-01: disease-space maps of natural B. rossi infection.

Reads the tidy files of SV-G1 (DS02, DS03, DS05 features; DS05 outcomes after the spec lock),
fits the Beagle reference course, projects the natural dogs, runs the analyses fixed in
/experiments/SV-01/spec.md and writes everything to /experiments/SV-01/out/.

Run:  env/py/Scripts/python.exe -I scripts/analyse.py   (from /experiments/SV-01)
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy import stats

SEED = 20261112
N_PERM = 10_000
N_BOOT = 2_000
GRID = 2_000
BAND_PSEUDO = 0.05
WITHIN_BAND = 2.0
END_EDGE = 0.01

PKG = Path(__file__).resolve().parents[1]
EXP = PKG.parent
TIDY = EXP / "shared" / "tidy"
OUT = PKG / "out"

INPUTS = {
    "DS02.features.json": "12475e823e588af20e8bec2df5164979c158bdbbb86ddfb96a32afe8aad83e2d",
    "DS03.features.json": "2862ac7e6e5fcec6200024543e4142fbe81eabd2eadef06d4f288bc982eda8a6",
    "DS05.features.json": "323238159fb21596dacc02464fe4ebdf7bd54282cd06fdce7535057f28e90a1e",
    "DS05.outcomes.json": "4a86691b3b97aefe846803c6d5784d96b35bd75b4b33d1f74d519d3d8365eba0",
}
SPEC_SHA = "7c272692530ce89c0857ec971fd9b75578e407e643ce1d85c50a1f7d67d6a98f"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_inputs() -> dict:
    found = {}
    for name, expected in INPUTS.items():
        got = sha256(TIDY / name)
        if got != expected:
            sys.exit(f"STOP: input {name} changed during the run (sha256 {got}, expected {expected}).")
        found[name] = got
    spec = sha256(PKG / "spec.md")
    if spec != SPEC_SHA:
        sys.exit(f"STOP: spec.md changed after the lock (sha256 {spec}).")
    return found


def load(name: str) -> dict:
    return json.loads((TIDY / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- the principal curve

class Course:
    """Principal curve: cubic polynomial in normalised arc length, fitted to standardised points."""

    def __init__(self, x: np.ndarray, y: np.ndarray, day: np.ndarray, mode: str = "time"):
        """mode "principal": the spec algorithm (t re-estimated by projection until it converges).
        mode "time": t stays the sampling day (deviation D1 in report.md); no projection step."""
        self.mode = mode
        self.mx, self.sx = x.mean(), x.std(ddof=1)
        self.my, self.sy = y.mean(), y.std(ddof=1)
        P = np.column_stack([(x - self.mx) / self.sx, (y - self.my) / self.sy])
        t = (day - day.min()) / (day.max() - day.min())
        self.iterations = 0
        warnings.simplefilter("ignore", np.exceptions.RankWarning)
        for it in range(100 if mode == "principal" else 0):
            cx = np.polyfit(t, P[:, 0], 3)
            cy = np.polyfit(t, P[:, 1], 3)
            tg = np.linspace(t.min(), t.max(), GRID)
            G = np.column_stack([np.polyval(cx, tg), np.polyval(cy, tg)])
            seg = np.sqrt((np.diff(G, axis=0) ** 2).sum(axis=1))
            s = np.concatenate([[0.0], np.cumsum(seg)])
            s /= s[-1]
            idx = np.argmin(((P[:, None, :] - G[None, :, :]) ** 2).sum(axis=2), axis=1)
            t_new = s[idx]
            delta = np.abs(t_new - t).max()
            t = t_new
            self.iterations = it + 1
            if delta < 1e-4:
                break
        # final grid parameterised by arc length
        cx = np.polyfit(t, P[:, 0], 3)
        cy = np.polyfit(t, P[:, 1], 3)
        tg = np.linspace(t.min(), t.max(), GRID)
        G = np.column_stack([np.polyval(cx, tg), np.polyval(cy, tg)])
        seg = np.sqrt((np.diff(G, axis=0) ** 2).sum(axis=1))
        s = np.concatenate([[0.0], np.cumsum(seg)])
        s /= s[-1]
        # orientation: early end has the lower mean day among its nearest third of points
        idx = np.argmin(((P[:, None, :] - G[None, :, :]) ** 2).sum(axis=2), axis=1)
        stage = s[idx]
        lo = day[stage <= np.quantile(stage, 1 / 3)].mean()
        hi = day[stage >= np.quantile(stage, 2 / 3)].mean()
        if mode == "principal" and lo > hi:
            G = G[::-1]
            s = 1.0 - s[::-1]
        self.G, self.s = G, s
        d_fit = np.sqrt(((P - G[self._nearest(P)]) ** 2).sum(axis=1))
        self.spread = float(np.sqrt((d_fit ** 2).mean()))

    def _nearest(self, P: np.ndarray) -> np.ndarray:
        return np.argmin(((P[:, None, :] - self.G[None, :, :]) ** 2).sum(axis=2), axis=1)

    def project(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        P = np.column_stack([(x - self.mx) / self.sx, (y - self.my) / self.sy])
        idx = self._nearest(P)
        dist = np.sqrt(((P - self.G[idx]) ** 2).sum(axis=1)) / self.spread
        return self.s[idx], dist

    def curve_xy(self, every: int = 40) -> list[dict]:
        pts = []
        for i in list(range(0, GRID, every)) + [GRID - 1]:
            pts.append({"x": r6(self.G[i, 0] * self.sx + self.mx), "y": r6(self.G[i, 1] * self.sy + self.my),
                        "stage": r6(self.s[i])})
        return pts


# ---------------------------------------------------------------- statistics

def r6(v):
    if v is None:
        return None
    v = float(v)
    return None if not math.isfinite(v) else round(v, 6)


def ranks(v: np.ndarray) -> np.ndarray:
    return stats.rankdata(v, method="average")


def resid(y: np.ndarray, X: np.ndarray) -> np.ndarray:
    A = np.column_stack([np.ones(len(y)), X])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    return y - A @ beta


def corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    den = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else float("nan")


def partial_spearman(h, d, controls):
    C = np.column_stack([ranks(c) for c in controls])
    eh = resid(ranks(h), C)
    ed = resid(ranks(d), C)
    return corr(eh, ed), eh, ed


def partial_test(h, d, controls, rng):
    rho, eh, ed = partial_spearman(h, d, controls)
    perm = np.array([corr(rng.permutation(eh), ed) for _ in range(N_PERM)])
    p = (1 + (np.abs(perm) >= abs(rho) - 1e-12).sum()) / (N_PERM + 1)
    n = len(h)
    boot = []
    for _ in range(N_BOOT):
        i = rng.integers(0, n, n)
        r, *_ = partial_spearman(h[i], d[i], [c[i] for c in controls])
        if math.isfinite(r):
            boot.append(r)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"estimate": rho, "ci_low": float(lo), "ci_high": float(hi), "p": float(p), "n": n}


def spearman_test(a, b, rng):
    ra, rb = ranks(a), ranks(b)
    rho = corr(ra, rb)
    perm = np.array([corr(rng.permutation(ra), rb) for _ in range(N_PERM)])
    p = (1 + (np.abs(perm) >= abs(rho) - 1e-12).sum()) / (N_PERM + 1)
    n = len(a)
    boot = []
    for _ in range(N_BOOT):
        i = rng.integers(0, n, n)
        r = corr(ranks(a[i]), ranks(b[i]))
        if math.isfinite(r):
            boot.append(r)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return {"estimate": rho, "ci_low": float(lo), "ci_high": float(hi), "p": float(p), "n": n}


def bh(ps: list[float]) -> list[float]:
    m = len(ps)
    order = np.argsort(ps)
    q = np.empty(m)
    prev = 1.0
    for k in range(m - 1, -1, -1):
        i = order[k]
        prev = min(prev, ps[i] * m / (k + 1))
        q[i] = prev
    return q.tolist()


def wilson(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    z = 1.959963984540054
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (c - h, c + h)


def boot_median(v: np.ndarray, rng) -> tuple[float, float]:
    n = len(v)
    meds = [np.median(v[rng.integers(0, n, n)]) for _ in range(N_BOOT)]
    lo, hi = np.percentile(meds, [2.5, 97.5])
    return float(lo), float(hi)


# ---------------------------------------------------------------- data

def beagle_points(ds02: dict, plane: str, post: bool) -> list[dict]:
    pts = []
    for r in ds02["records"]:
        if bool(r["post_treatment"]) != post:
            continue
        v = r["values"]
        hct = v.get("hct")
        if plane == "A":
            yv = v.get("arc")
            y = math.log10(yv) if yv is not None and yv > 0 else None
        else:
            yv = v.get("neut_band")
            y = math.log10(yv + BAND_PSEUDO) if yv is not None else None
        if hct is None or y is None:
            continue
        pts.append({"dog_id": r["dog_id"], "timepoint": r["timepoint"], "day": float(r["day"]),
                    "dose": v.get("dose_group"), "hct": hct, "y": y, "post_treatment": post})
    return pts


def fit_course(pts: list[dict], mode: str = "time") -> Course:
    return Course(np.array([p["hct"] for p in pts]), np.array([p["y"] for p in pts]),
                  np.array([p["day"] for p in pts]), mode)


def natural_rows(ds: dict, plane: str, keep) -> list[dict]:
    rows = []
    for r in ds["records"]:
        if not keep(r):
            continue
        v = r["values"]
        hct = v.get("hct")
        if plane == "A":
            yv = v.get("arc")
            y = math.log10(yv) if yv is not None and yv > 0 else None
        else:
            yv = v.get("neut_band")
            y = math.log10(yv + BAND_PSEUDO) if yv is not None else None
        if hct is None or y is None:
            continue
        rows.append({"dog_id": r["dog_id"], "hct": hct, "y": y, "values": v})
    return rows


def ds05_keep(r):
    return r["group"] == "infected" and r["values"].get("pcr_b_rossi") == 1


# ---------------------------------------------------------------- main

def run(mode: str, out: Path) -> dict:
    hashes = check_inputs()
    out.mkdir(parents=True, exist_ok=True)
    ds02, ds03, ds05 = load("DS02.features.json"), load("DS03.features.json"), load("DS05.features.json")
    rng_master = np.random.default_rng(SEED)
    seeds = rng_master.integers(0, 2**31 - 1, 20).tolist()
    seed_iter = iter(seeds)

    def rng():
        return np.random.default_rng(next(seed_iter))

    res: dict = {"inputs_sha256": hashes, "spec_sha256": SPEC_SHA, "seed": SEED,
                 "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                              "scipy": __import__("scipy").__version__}}

    planes = {}
    for plane in ("A", "B"):
        pre = beagle_points(ds02, plane, post=False)
        post = beagle_points(ds02, plane, post=True)
        course = fit_course(pre, mode)
        post_course = fit_course(post, mode) if len(post) >= 5 else None
        planes[plane] = {"pre": pre, "post": post, "course": course, "post_course": post_course}
        bstage, bdist = course.project(np.array([p["hct"] for p in pre]), np.array([p["y"] for p in pre]))
        for p, s_, d_ in zip(pre, bstage, bdist):
            p["stage"], p["distance"] = float(s_), float(d_)
        if post_course is not None:
            ps, pd_ = course.project(np.array([p["hct"] for p in post]), np.array([p["y"] for p in post]))
            for p, s_, d_ in zip(post, ps, pd_):
                p["stage"], p["distance"] = float(s_), float(d_)
        bday = np.array([p["day"] for p in pre])
        res[f"course_{plane}_stage_vs_day"] = corr(ranks(bstage), ranks(bday))
        res[f"course_{plane}"] = {"n_points": len(pre), "n_dogs": len({p["dog_id"] for p in pre}),
                                  "iterations": course.iterations, "spread_sd_units": course.spread,
                                  "axis_mean": [course.mx, course.my], "axis_sd": [course.sx, course.sy],
                                  "n_post_points": len(post)}

    # ---- project the natural dogs
    out_rows = []      # pseudo_stage.csv
    map_rows = []      # map_points.csv
    projected = {}
    groups = {
        "DS05": (ds05, ds05_keep, "natural", True),
        "DS03_c1": (ds03, lambda r: r["values"].get("setting") == "natural" and r["values"].get("cohort") == 1, "natural", True),
        "DS03_c2": (ds03, lambda r: r["values"].get("setting") == "natural" and r["values"].get("cohort") == 2, "natural", True),
        "DS03_healthy": (ds03, lambda r: r["values"].get("setting") == "healthy", "healthy", False),
        "DS03_imha": (ds03, lambda r: r["values"].get("setting") == "imha", "imha", False),
    }
    for plane in ("A", "B"):
        course = planes[plane]["course"]
        for key, (ds, keep, setting, natural) in groups.items():
            if plane == "B" and not key.startswith("DS05"):
                continue
            rows = natural_rows(ds, plane, keep)
            st_, di_ = course.project(np.array([r["hct"] for r in rows]), np.array([r["y"] for r in rows]))
            for r, s_, d_ in zip(rows, st_, di_):
                r["stage"], r["distance"] = float(s_), float(d_)
                r["beyond_end"] = bool(s_ < END_EDGE or s_ > 1 - END_EDGE)
                if natural:
                    out_rows.append({"dog_id": r["dog_id"], "dataset_id": ds["dataset_id"], "pseudo_stage": r6(s_),
                                     "distance": r6(d_), "plane": "A_hct_logarc" if plane == "A" else "B_hct_logband"})
                map_rows.append({"plane": plane, "group": key, "setting": setting, "dog_id": r["dog_id"],
                                 "timepoint": "admission", "day": None, "hct": r6(r["hct"]), "y": r6(r["y"]),
                                 "pseudo_stage": r6(s_), "distance": r6(d_), "beyond_end": int(r["beyond_end"]),
                                 "post_treatment": None})
            projected[(plane, key)] = rows
        for which in ("pre", "post"):
            for p in planes[plane][which]:
                map_rows.append({"plane": plane, "group": "DS02_beagle", "setting": "experimental", "dog_id": p["dog_id"],
                                 "timepoint": p["timepoint"], "day": p["day"], "hct": r6(p["hct"]), "y": r6(p["y"]),
                                 "pseudo_stage": r6(p.get("stage")), "distance": r6(p.get("distance")),
                                 "beyond_end": None, "post_treatment": int(p["post_treatment"])})

    write_csv(out / "pseudo_stage.csv", out_rows, ["dog_id", "dataset_id", "pseudo_stage", "distance", "plane"])
    write_csv(out / "map_points.csv", map_rows, ["plane", "group", "setting", "dog_id", "timepoint", "day", "hct", "y",
                                                 "pseudo_stage", "distance", "beyond_end", "post_treatment"])
    curve_rows = []
    for plane in ("A", "B"):
        for arm in ("pre", "post"):
            c = planes[plane]["course"] if arm == "pre" else planes[plane]["post_course"]
            if c is None:
                continue
            for p in c.curve_xy(every=20):
                curve_rows.append({"plane": plane, "arm": arm, "hct": p["x"], "y": p["y"], "stage": p["stage"]})
    write_csv(out / "curves.csv", curve_rows, ["plane", "arm", "hct", "y", "stage"])

    # ---- validity check (features only)
    a05 = projected[("A", "DS05")]
    ill = [(r["stage"], r["values"].get("illness_days")) for r in a05 if r["values"].get("illness_days") is not None]
    v = spearman_test(np.array([s for s, _ in ill]), np.array([d for _, d in ill], dtype=float), rng())
    v["passed"] = bool(v["estimate"] > 0 and v["p"] < 0.05)
    res["validity"] = v

    # ---- outcome lock opens here: DS05 outcomes
    oc = load("DS05.outcomes.json")
    hab = {r["dog_id"]: r["values"].get("habitus_score") for r in oc["records"]}

    def with_hab(rows):
        return [r for r in rows if hab.get(r["dog_id"]) is not None]

    a = with_hab(a05)
    b = with_hab(projected[("B", "DS05")])
    H = lambda rows: np.array([hab[r["dog_id"]] for r in rows], dtype=float)
    S = lambda rows: np.array([r["stage"] for r in rows])
    D = lambda rows: np.array([r["distance"] for r in rows])

    h1 = partial_test(H(a), D(a), [S(a)], rng())
    h2 = spearman_test(H(a), S(a), rng())
    h3 = partial_test(H(b), D(b), [S(b)], rng())
    q = bh([h1["p"], h2["p"], h3["p"]])
    for t_, q_ in zip((h1, h2, h3), q):
        t_["q"] = q_
    res["H1"], res["H2"], res["H3"] = h1, h2, h3

    no_ec = [r for r in a if r["values"].get("pcr_e_canis") != 1]
    interior = [r for r in a if not r["beyond_end"]]
    s1 = partial_test(H(no_ec), D(no_ec), [S(no_ec)], rng())
    s2 = partial_test(H(interior), D(interior), [S(interior)], rng()) if len(interior) >= 10 else None
    hct_a = np.array([r["hct"] for r in a])
    arc_a = np.array([r["y"] for r in a])
    res["axes_vs_blood"] = {"stage_vs_hct": corr(ranks(S(a)), ranks(hct_a)), "distance_vs_hct": corr(ranks(D(a)), ranks(hct_a)),
                            "stage_vs_logarc": corr(ranks(S(a)), ranks(arc_a)), "distance_vs_logarc": corr(ranks(D(a)), ranks(arc_a)),
                            "habitus_vs_hct": corr(ranks(H(a)), ranks(hct_a)), "n": len(a)}
    s3 = partial_test(H(a), D(a), [S(a), hct_a], rng())
    res["S1"], res["S2"], res["S3"] = s1, s2, s3

    # descriptive: habitus by stage band and by distance tertile
    hab_tab = []
    for lvl in sorted(set(H(a).astype(int).tolist())):
        sel = [r for r in a if hab[r["dog_id"]] == lvl]
        hab_tab.append({"habitus": lvl, "n": len(sel), "median_stage": r6(np.median(S(sel))),
                        "median_distance": r6(np.median(D(sel))),
                        "median_hct": r6(np.median([r["hct"] for r in sel])),
                        "beyond_end": sum(r["beyond_end"] for r in sel)})
    res["habitus_table"] = hab_tab

    # ---- stability: leave one Beagle out
    loo = []
    full_stage, full_dist = S(a), D(a)
    pre_a = planes["A"]["pre"]
    for dog in sorted({p["dog_id"] for p in pre_a}):
        c = fit_course([p for p in pre_a if p["dog_id"] != dog], mode)
        st_, di_ = c.project(np.array([r["hct"] for r in a]), np.array([r["y"] for r in a]))
        rho_l, *_ = partial_spearman(H(a), di_, [st_])
        loo.append({"left_out": dog, "spread": r6(c.spread),
                    "median_abs_stage_change": r6(np.median(np.abs(st_ - full_stage))),
                    "spearman_stage_vs_full": r6(corr(ranks(st_), ranks(full_stage))),
                    "spearman_distance_vs_full": r6(corr(ranks(di_), ranks(full_dist))),
                    "share_beyond_end": r6(np.mean((st_ < END_EDGE) | (st_ > 1 - END_EDGE))),
                    "h1_partial_rho": r6(rho_l)})
    res["loo"] = loo
    write_csv(out / "stability_loo.csv", loo, list(loo[0].keys()))

    # ---- geometry: DS05 and the two DS03 cohorts (+ reference groups)
    geo = []
    for key in ("DS05", "DS03_c1", "DS03_c2", "DS03_healthy", "DS03_imha"):
        rows = projected[("A", key)]
        st_, di_ = S(rows), D(rows)
        n = len(rows)
        k_in = int((di_ <= WITHIN_BAND).sum())
        k_end = int(sum(r["beyond_end"] for r in rows))
        k_late = int((st_ > 1 - END_EDGE).sum())
        g = rng()
        hist, _ = np.histogram(st_, bins=10, range=(0, 1))
        geo.append({"group": key, "n": n,
                    "share_within_band": r6(k_in / n), "within_ci_low": r6(wilson(k_in, n)[0]), "within_ci_high": r6(wilson(k_in, n)[1]),
                    "share_beyond_end": r6(k_end / n), "beyond_ci_low": r6(wilson(k_end, n)[0]), "beyond_ci_high": r6(wilson(k_end, n)[1]),
                    "share_past_late_end": r6(k_late / n),
                    "median_stage": r6(np.median(st_)), "stage_q1": r6(np.percentile(st_, 25)), "stage_q3": r6(np.percentile(st_, 75)),
                    "median_stage_ci": [r6(x) for x in boot_median(st_, g)],
                    "median_distance": r6(np.median(di_)), "median_distance_ci": [r6(x) for x in boot_median(di_, g)],
                    "median_hct": r6(np.median([r["hct"] for r in rows])),
                    "stage_histogram": hist.tolist()})
    res["geometry"] = geo
    write_csv(out / "replication_geometry.csv",
              [{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in g_.items()} for g_ in geo], list(geo[0].keys()))

    # ---- Beagle course geometry summary (how far do the Beagles go?)
    pre = planes["A"]["pre"]
    res["beagle_hct_range"] = [min(p["hct"] for p in pre), max(p["hct"] for p in pre)]
    res["beagle_arc_range"] = [10 ** min(p["y"] for p in pre), 10 ** max(p["y"] for p in pre)]

    # ---- tables for the report and the view
    tests = [
        ("H1", "Habitus with distance given pseudo-stage, plane A (primary)", h1, "partial rho"),
        ("H2", "Habitus with pseudo-stage, plane A", h2, "rho"),
        ("H3", "Habitus with distance given pseudo-stage, plane B (bands)", h3, "partial rho"),
        ("S1", "H1 without the 3 E. canis co-infected dogs", s1, "partial rho"),
        ("S2", "H1, interior projections only", s2, "partial rho"),
        ("S3", "H1 also controlling haematocrit", s3, "partial rho"),
        ("V", "Validity: pseudo-stage with illness duration", v, "rho"),
    ]
    trows = []
    for code, label, t_, lab in tests:
        if t_ is None:
            trows.append({"code": code, "label": label, "statistic": lab, "estimate": None, "ci_low": None,
                          "ci_high": None, "n": 0, "p": None, "q": None})
            continue
        trows.append({"code": code, "label": label, "statistic": lab, "estimate": r6(t_["estimate"]),
                      "ci_low": r6(t_["ci_low"]), "ci_high": r6(t_["ci_high"]), "n": t_["n"], "p": r6(t_["p"]),
                      "q": r6(t_.get("q"))})
    res["tests"] = trows
    write_csv(out / "tests.csv", trows, list(trows[0].keys()))

    (out / "results.json").write_text(json.dumps(clean(res), indent=2, allow_nan=False), encoding="utf-8")
    # map of habitus for the DS05 points (view colours by it)
    hab_rows = [{"dog_id": r["dog_id"], "habitus_score": hab[r["dog_id"]]} for r in a]
    write_csv(out / "ds05_habitus_for_map.csv", hab_rows, ["dog_id", "habitus_score"])
    res["mode"] = mode
    return res


def main() -> None:
    # Primary: the construction frozen in spec.md. Deviation D1 (time-anchored course) is a labelled sensitivity.
    main_res = run("principal", OUT)
    dev_res = run("time", OUT / "time_anchored")
    keys = ("course_A_stage_vs_day", "course_B_stage_vs_day", "validity", "H1", "H2", "H3", "S1", "S2", "S3",
            "course_A", "course_B", "axes_vs_blood", "geometry", "loo", "habitus_table", "tests")
    main_res["time_anchored"] = {k: dev_res[k] for k in keys}
    (OUT / "results.json").write_text(json.dumps(clean(main_res), indent=2, allow_nan=False), encoding="utf-8")
    for name, r in (("AS SPECIFIED (primary)", main_res), ("TIME-ANCHORED (deviation D1)", dev_res)):
        print("=====", name)
        print(json.dumps(clean({k: r[k] for k in keys[:9]})))


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return r6(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})


if __name__ == "__main__":
    main()
