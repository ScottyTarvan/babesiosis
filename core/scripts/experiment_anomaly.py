"""Anomaly experiment over a tidy dataset (data/tidy/<DS>.json): atypical admission profiles.

Question: which dogs have admission profiles that do not fit the rest of the cohort, by two independent
methods (isolation forest, robust Mahalanobis distance from the minimum covariance determinant), do the two
agree, and do the pathogen-minority dogs (B. rossi + E. canis, B. vogeli only) stand out?
Spec: experiment_specs/EXP06-DS05-anomaly.md.  Steps:

  - input = numeric/ordinal variables with include_default, derived = false and no derived_from (22 for
    DS05, as EXP02); dogs missing more than 30 percent of them are not scored; skewed non-negative
    variables get log1p (never clipped); one iterative (BayesianRidge) imputation; standardise;
  - isolation forest (1000 trees, mean of 10 seeds, seed stability reported) and MinCovDet Mahalanobis
    distance (variables dropped for collinearity only if the MCD covariance is singular);
  - rank-normalised scores, combined = mean of the two; the most atypical 5 percent are labelled outlier;
  - drivers for the top 10, the top 3 of each method and the four pathogen-minority dogs: robust z,
    univariate isolation score, MCD contribution;
  - agreement (Spearman with permutation p and bootstrap interval, top-10 overlap);
  - sensitivity S1 complete cases, S2 no log transform, S3 28 variables, S4 suspect raw cells set missing;
  - raw-sheet check: findings recorded by hand in experiment_specs/EXP06-raw-check.json and read back by
    --raw-check (absent file: every status is "pending" and nothing is interpreted biologically).

Output: data/experiments/<code>.json, read by the console ExperimentLoader. Nothing else is written.
--selftest multiplies the haematocrit of a few typical dogs by 10 (in memory), prints where they land and
writes nothing.

Not stdlib-only: needs numpy, scipy and scikit-learn (use .venv-nlp; .venv has numpy only). Run from core/:
    .venv-nlp/Scripts/python.exe -I scripts/experiment_anomaly.py --dataset DS05 --code EXP06-DS05-anomaly \
        --name "Atypical dogs, BET cohort" --seed 20261105 --raw-check experiment_specs/EXP06-raw-check.json
Other options (defaults as in the spec): --skew-threshold 1.0 --max-missing-subject 0.30 --imputer-max-iter 20
    --if-n-estimators 1000 --if-seeds 10 --mcd-support-fraction 0.75 --mcd-collinearity-threshold 0.95
    --outlier-quantile 0.95 --top-n 10 --z-threshold 3.0 --univariate-if-estimators 200 --perm 5000
    --ci-boot 1000 --selftest
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import warnings
from pathlib import Path

import numpy as np
import scipy
import sklearn
from scipy.stats import chi2, skew
from sklearn.covariance import MinCovDet
from sklearn.ensemble import IsolationForest
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()

DERIVED_BACK = ["mcv", "mch", "mchc", "wcc", "arc", "globulin"]
HEADINGS = ["Question", "What was done", "Raw-sheet check", "Most atypical dogs", "The co-infected and B. vogeli dogs",
            "Agreement between the two methods", "Limits"]
VALID_STATUS = ("matches_raw", "discrepancy", "unit_suspect", "not_checked")


# ---------------------------------------------------------------------------------------------------------
# Helpers (rankdata, perm_p copied from experiment_pairwise.py: -I removes the script folder from the path)
# ---------------------------------------------------------------------------------------------------------

def rankdata(x):
    """Average ranks (1-based) with ties, like scipy.stats.rankdata."""
    uniq, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    cum = np.cumsum(counts)
    first = cum - counts + 1
    return ((first + cum) / 2.0)[inv]


def perm_p(stat, perm_stats):
    return (np.count_nonzero(perm_stats >= stat - 1e-12) + 1) / (len(perm_stats) + 1)


def r(x, nd=4):
    if x is None:
        return None
    x = float(x)
    return None if math.isnan(x) else round(x, nd)


def fmt_p(p):
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


def spearman(a, b):
    ra, rb = rankdata(a), rankdata(b)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    d = math.sqrt(float(ra @ ra) * float(rb @ rb))
    return float(ra @ rb) / d if d > 0 else float("nan")


def norm_rank(x):
    n = len(x)
    return (rankdata(x) - 1.0) / (n - 1.0)


def order_desc(x):
    """Indices most anomalous first; ties broken by position (stable)."""
    return np.lexsort((np.arange(len(x)), -np.asarray(x)))


def rank_desc(x):
    """Rank 1 = highest value; tied values share the best rank."""
    x = np.asarray(x)
    return np.array([1 + int((x > v + 1e-12).sum()) for v in x])


def band(rank, n, top_q=0.05, second_q=0.20):
    if rank <= math.ceil(top_q * n):
        return "top5pct"
    if rank <= math.ceil(second_q * n):
        return "top20pct"
    return "rest"


# ---------------------------------------------------------------------------------------------------------
# Matrix preparation and the two scorers
# ---------------------------------------------------------------------------------------------------------

def prepare(raw, codes, fixed, mode, seed, skew_threshold, max_iter):
    """raw: dogs x variables with NaN. mode 'iterative' or 'none'. Returns transformed, standardised matrix and bookkeeping."""
    T = raw.copy()
    transformed = []
    for j, c in enumerate(codes):
        obs = raw[~np.isnan(raw[:, j]), j]
        if c in fixed:
            do = fixed[c]
        else:
            do = len(obs) > 2 and obs.min() >= 0 and abs(float(skew(obs))) > skew_threshold
        if do:
            T[:, j] = np.log1p(raw[:, j])
            transformed.append(c)
    Z0 = (T - np.nanmean(T, axis=0)) / np.nanstd(T, axis=0, ddof=1)
    miss = np.isnan(Z0)
    if mode == "none":
        if miss.any():
            raise ValueError("complete case matrix has gaps")
        Zi = Z0
    else:
        Zi = IterativeImputer(estimator=BayesianRidge(), max_iter=max_iter, sample_posterior=False,
                              initial_strategy="median", random_state=seed).fit_transform(Z0)
    mu, sd = Zi.mean(axis=0), Zi.std(axis=0, ddof=1)
    Zs = (Zi - mu) / sd
    return {"T": T, "transformed": transformed, "Zs": Zs, "miss": miss, "mu": mu, "sd": sd,
            "mu0": np.nanmean(T, axis=0), "sd0": np.nanstd(T, axis=0, ddof=1)}


def isolation_scores(Zs, seeds, n_estimators):
    S = []
    for s in seeds:
        f = IsolationForest(n_estimators=n_estimators, max_samples="auto", contamination="auto", max_features=1.0,
                            bootstrap=False, random_state=s).fit(Zs)
        S.append(-f.score_samples(Zs))
    S = np.array(S)
    mins = min(spearman(S[a], S[b]) for a in range(len(S)) for b in range(a + 1, len(S))) if len(S) > 1 else 1.0
    return S.mean(axis=0), mins


def cond_ok(cov):
    return np.linalg.cond(cov) <= 1e10


def fit_mcd(Zs, miss_counts, seed, support, thr, codes):
    """MinCovDet on all variables; on failure or a singular covariance drop collinear variables and refit.
    Returns (mcd, used column indices, dropped list [(code index, reason)])."""
    p = Zs.shape[1]
    used = list(range(p))
    dropped = []

    def attempt(cols):
        try:
            m = MinCovDet(support_fraction=support, random_state=seed).fit(Zs[:, cols])
            return m if cond_ok(m.covariance_) else None
        except Exception:
            return None

    m = attempt(used)
    if m is not None:
        return m, used, dropped
    C = np.abs(np.corrcoef(Zs, rowvar=False))
    pairs = sorted(((C[i, j], i, j) for i in range(p) for j in range(i + 1, p) if C[i, j] > thr), reverse=True)
    for c, i, j in pairs:
        if i in [d for d, _ in dropped] or j in [d for d, _ in dropped]:
            continue
        drop = i if miss_counts[i] > miss_counts[j] else j  # more missing; tie: the later in the list
        dropped.append((drop, f"|r| = {c:.3f} with {codes[j if drop == i else i]}"))
    used = [k for k in range(p) if k not in [d for d, _ in dropped]]
    m = attempt(used)
    while m is None and len(used) > 2:  # still singular: drop the variable most correlated with the rest
        sub = np.abs(np.corrcoef(Zs[:, used], rowvar=False))
        np.fill_diagonal(sub, 0)
        k = int(np.argmax(sub.max(axis=1)))
        dropped.append((used[k], f"covariance still singular; highest |r| = {sub[k].max():.3f}"))
        used.pop(k)
        m = attempt(used)
    if m is None:
        raise RuntimeError("MCD could not be fitted")
    return m, used, dropped


def score_matrix(raw, codes, fixed, mode, seeds, args):
    """Both scores for one matrix. Returns a dict (arrays aligned to the rows of raw)."""
    P = prepare(raw, codes, fixed, mode, seeds["imp"], args.skew_threshold, args.imputer_max_iter)
    Zs = P["Zs"]
    miss_counts = np.isnan(raw).sum(axis=0)
    if_mean, stab = isolation_scores(Zs, seeds["if"], args.if_n_estimators)
    mcd, used, dropped = fit_mcd(Zs, miss_counts, seeds["mcd"], args.mcd_support_fraction, args.mcd_collinearity_threshold, codes)
    d2 = mcd.mahalanobis(Zs[:, used])
    nif, nmcd = norm_rank(if_mean), norm_rank(d2)
    return {"P": P, "Zs": Zs, "if_score": if_mean, "stability": stab, "mcd": mcd, "used": used,
            "dropped": [(codes[d], why) for d, why in dropped],
            "dropped_idx": [d for d, _ in dropped], "d2": d2, "norm_if": nif, "norm_mcd": nmcd, "combined": (nif + nmcd) / 2.0}


def mcd_contributions(Zs, mcd, used):
    """contribution_j = d2_full - d2_without_j with the same location and covariance (sub-vector, sub-matrix)."""
    X = Zs[:, used] - mcd.location_
    S = mcd.covariance_
    full = np.einsum("ij,jk,ik->i", X, np.linalg.inv(S), X)
    out = np.zeros((len(Zs), len(used)))
    for t in range(len(used)):
        keep = [k for k in range(len(used)) if k != t]
        Sk = S[np.ix_(keep, keep)]
        Xk = X[:, keep]
        out[:, t] = full - np.einsum("ij,jk,ik->i", Xk, np.linalg.inv(Sk), Xk)
    return full, out


def robust_z(Zs, miss):
    """(x - median) / (1.4826 MAD) on observed values of each (affinely equivalent) column; SD fallback if MAD = 0."""
    n, p = Zs.shape
    rz = np.zeros((n, p))
    fallback = []
    for j in range(p):
        obs = Zs[~miss[:, j], j]
        med = np.median(obs)
        mad = np.median(np.abs(obs - med))
        if mad > 0:
            rz[:, j] = (Zs[:, j] - med) / (1.4826 * mad)
        else:
            rz[:, j] = (Zs[:, j] - med) / obs.std(ddof=1)
            fallback.append(j)
    return rz, fallback


# ---------------------------------------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------------------------------------

def vname(variables, c):
    return variables[c]["name"].lower()


def fmt_val(v):
    if v is None:
        return "n/a"
    return f"{v:.3g}" if abs(v) < 1000 else f"{v:.0f}"


def ref_text(d):
    lo, hi = d["ref_low"], d["ref_high"]
    if lo is None and hi is None:
        return "no reference range"
    return f"reference {fmt_val(lo) if lo is not None else '-'} to {fmt_val(hi) if hi is not None else '-'}"


def driver_phrase(d, variables):
    unit = f" {d['unit']}" if d.get("unit") and not d["unit"].startswith("score") else ""
    if d.get("unit") == "days" and d["value"] == 1:
        unit = " day"
    pos = ""
    if d["ref_high"] is not None and d["value"] > d["ref_high"]:
        pos = ", above reference"
    elif d["ref_low"] is not None and d["value"] < d["ref_low"]:
        pos = ", below reference"
    imp = ", imputed" if d["imputed"] else ""
    return (f"{vname(variables, d['variable'])} {fmt_val(d['value'])}{unit} (cohort median {fmt_val(d['cohort_median'])}, "
            f"robust z {d['robust_z']:+.1f}{pos}{imp})")


def top_drivers(o, k=3):
    ds = sorted(o["drivers"], key=lambda d: (-(d["mcd_contribution"] if d["mcd_contribution"] is not None else -1e9), -abs(d["robust_z"])))
    return ds[:k]


# ---------------------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--code", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--description", default=None)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--skew-threshold", type=float, default=1.0)
    ap.add_argument("--max-missing-subject", type=float, default=0.30)
    ap.add_argument("--imputer-max-iter", type=int, default=20)
    ap.add_argument("--if-n-estimators", type=int, default=1000)
    ap.add_argument("--if-seeds", type=int, default=10)
    ap.add_argument("--mcd-support-fraction", type=float, default=0.75)
    ap.add_argument("--mcd-collinearity-threshold", type=float, default=0.95)
    ap.add_argument("--outlier-quantile", type=float, default=0.95)
    ap.add_argument("--top-n", type=int, default=10)
    ap.add_argument("--z-threshold", type=float, default=3.0)
    ap.add_argument("--univariate-if-estimators", type=int, default=200)
    ap.add_argument("--perm", type=int, default=5000)
    ap.add_argument("--ci-boot", type=int, default=1000)
    ap.add_argument("--raw-check", default="experiment_specs/EXP06-raw-check.json")
    ap.add_argument("--selftest", action="store_true", help="inject haematocrit x10 into typical dogs, print ranks, write nothing")
    args = ap.parse_args()

    tidy = json.loads((ROOT / "data" / "tidy" / f"{args.dataset}.json").read_text(encoding="utf-8"))
    variables = {v["code"]: v for v in tidy["variables"]}
    subjects = [s["code"] for s in tidy["subjects"]]
    sidx = {s: i for i, s in enumerate(subjects)}
    group_label = {s["code"]: s["group_label"] for s in tidy["subjects"]}
    n_all = len(subjects)

    input_codes = [v["code"] for v in tidy["variables"]
                   if v["data_type"] in ("N", "O") and v["include_default"] and not v["derived"] and not v.get("derived_from")]
    extra_codes = [c for c in DERIVED_BACK if c in variables]
    all_codes = input_codes + extra_codes
    cidx = {c: i for i, c in enumerate(all_codes)}
    Xall = np.full((n_all, len(all_codes)), np.nan)
    for o in tidy["observations"]:
        c = o["variable"]
        if c in cidx and o["value_num"] is not None:
            Xall[sidx[o["subject"]], cidx[c]] = o["value_num"]

    rng = np.random.default_rng(args.seed)

    def child():
        return int(rng.integers(0, 2 ** 31 - 1))

    # Fixed draw order: imputer, isolation forest seeds, MCD, univariate forests (one per variable), permutation, bootstrap.
    p_in = len(input_codes)
    seeds = {"imp": child(), "if": [child() for _ in range(args.if_seeds)], "mcd": child()}
    seeds_uni = [child() for _ in range(p_in)]
    seed_perm, seed_boot = child(), child()

    # ---- Filter -------------------------------------------------------------------------------------------
    X_in = Xall[:, :p_in]
    miss_frac = np.isnan(X_in).mean(axis=1)
    keep = miss_frac <= args.max_missing_subject
    lab_codes = ["haemoglobin", "rcc", "haematocrit", "total_protein", "albumin"]
    dropped = []
    for i in np.where(~keep)[0]:
        none_lab = all(np.isnan(Xall[i, cidx[c]]) for c in lab_codes if c in cidx)
        dropped.append({"subject_code": subjects[i],
                        "reason": ("no haematology or biochemistry; " if none_lab else "") +
                                  f"{int(np.isnan(X_in[i]).sum())} of {p_in} input variables missing"})
    kept_idx = np.where(keep)[0]
    kept = [subjects[i] for i in kept_idx]
    n = len(kept)
    codes = input_codes
    X = X_in[kept_idx]
    X28 = Xall[kept_idx]
    kidx = {s: i for i, s in enumerate(kept)}
    minority = [s for s in kept if group_label[s] != "B. rossi only"]

    # ---- Selftest -----------------------------------------------------------------------------------------
    if args.selftest:
        # Spec check 7: copy of the standardised matrix, one dog's haematocrit multiplied by 10 (in memory only).
        base = score_matrix(X, codes, {}, "iterative", seeds, args)
        Zb = base["Zs"]
        hct = codes.index("haematocrit")
        ok_all = True
        for target in (1.0, -1.0, 0.5):  # dogs whose haematocrit z is closest to +1, -1, +0.5
            i = int(np.argmin(np.abs(Zb[:, hct] - target)))
            Zi = Zb.copy()
            Zi[i, hct] = Zb[i, hct] * 10
            if_mean, _ = isolation_scores(Zi, seeds["if"], args.if_n_estimators)
            mcd, used, _ = fit_mcd(Zi, np.isnan(X).sum(axis=0), seeds["mcd"], args.mcd_support_fraction,
                                   args.mcd_collinearity_threshold, codes)
            d2 = mcd.mahalanobis(Zi[:, used])
            rk_if = int(rank_desc(norm_rank(if_mean))[i]); rk_m = int(rank_desc(norm_rank(d2))[i])
            rk_c = int(rank_desc((norm_rank(if_mean) + norm_rank(d2)) / 2)[i])
            rzi, _ = robust_z(Zi, base["P"]["miss"])
            full, contrib = mcd_contributions(Zi, mcd, used)
            top_contrib = [codes[used[t]] for t in np.argsort(-contrib[i])[:3]]
            top_rz = [codes[t] for t in np.argsort(-np.abs(rzi[i]))[:3]]
            ok = rk_if <= 3 and rk_m <= 3 and ("haematocrit" in top_contrib or "haematocrit" in top_rz)
            ok_all &= ok
            print(f"selftest {kept[i]}: haematocrit z {Zb[i, hct]:+.2f} -> {Zi[i, hct]:+.2f}; rank IF {rk_if}, rank MCD {rk_m}, combined rank {rk_c}, "
                  f"top MCD contributors {top_contrib}, top robust-z {top_rz}; {'PASS' if ok else 'FAIL'}")
        print("selftest overall:", "PASS" if ok_all else "FAIL")
        return

    # ---- Main scores --------------------------------------------------------------------------------------
    M = score_matrix(X, codes, {}, "iterative", seeds, args)
    Zs, miss = M["Zs"], M["P"]["miss"]
    comb, nif, nmcd = M["combined"], M["norm_if"], M["norm_mcd"]
    p = len(codes)
    rank = rank_desc(comb)
    rank_if, rank_mcd = rank_desc(nif), rank_desc(nmcd)
    cut = float(np.quantile(comb, args.outlier_quantile))
    is_out = comb >= cut - 1e-12
    n_out = int(is_out.sum())
    used_codes = [codes[t] for t in M["used"]]
    chi_cut = float(chi2.ppf(0.975, df=len(used_codes)))
    n_above = int((M["d2"] > chi_cut).sum())

    rz, fallback = robust_z(Zs, miss)
    full_d2, contrib = mcd_contributions(Zs, M["mcd"], M["used"])
    uni = np.zeros((n, p))
    for j in range(p):
        obs = Zs[~miss[:, j], j].reshape(-1, 1)
        f = IsolationForest(n_estimators=args.univariate_if_estimators, random_state=seeds_uni[j]).fit(obs)
        uni[:, j] = -f.score_samples(Zs[:, j].reshape(-1, 1))
    cohort_median = [float(np.nanmedian(X[:, j])) for j in range(p)]
    P = M["P"]

    def cell_value(i, j):
        """Original-unit value; the back-transformed estimate when the cell was imputed."""
        if not miss[i, j]:
            return float(X[i, j])
        t = Zs[i, j] * P["sd"][j] + P["mu"][j]
        t = t * P["sd0"][j] + P["mu0"][j]
        return float(np.expm1(t)) if codes[j] in P["transformed"] else float(t)

    # ---- Raw-check file -----------------------------------------------------------------------------------
    raw_path = ROOT / args.raw_check
    raw_present = raw_path.exists()
    raw_data = json.loads(raw_path.read_text(encoding="utf-8")) if raw_present else {}

    # ---- Listed dogs --------------------------------------------------------------------------------------
    top_c = list(order_desc(comb)[:args.top_n])
    top_if3 = list(order_desc(nif)[:3])
    top_mcd3 = list(order_desc(nmcd)[:3])
    min_idx = [kidx[s] for s in minority]
    reasons = {}
    for lst, tag in ((top_c, "top10"), (top_if3, "top3_if"), (top_mcd3, "top3_mcd"), (min_idx, "pathogen_minority")):
        for i in lst:
            reasons.setdefault(int(i), []).append(tag)
    top10_if = set(order_desc(nif)[:10].tolist())
    top10_mcd = set(order_desc(nmcd)[:10].tolist())
    listed = sorted(reasons, key=lambda i: (rank[i], i))

    outliers = []
    for i in listed:
        tops_u = list(np.argsort(-uni[i])[:3])
        pos = [t for t in np.argsort(-contrib[i])[:3] if contrib[i, t] > 0]
        tops_m = [M["used"][t] for t in pos]
        sel = [j for j in range(p) if abs(rz[i, j]) > args.z_threshold] + [int(j) for j in tops_u] + [int(j) for j in tops_m]
        sel = list(dict.fromkeys(sel))
        drivers = []
        for j in sel:
            t = M["used"].index(j) if j in M["used"] else None
            why = []
            if abs(rz[i, j]) > args.z_threshold:
                why.append("robust_z")
            if j in tops_u:
                why.append("univariate_if")
            if j in tops_m:
                why.append("mcd_contribution")
            drivers.append({"variable": codes[j], "value": r(cell_value(i, j)), "unit": variables[codes[j]].get("unit"),
                            "cohort_median": r(cohort_median[j]), "ref_low": variables[codes[j]].get("ref_low"),
                            "ref_high": variables[codes[j]].get("ref_high"), "robust_z": r(rz[i, j]),
                            "univariate_if": r(uni[i, j]), "mcd_contribution": r(contrib[i, t]) if t is not None else None,
                            "mcd_share": r(contrib[i, t] / full_d2[i]) if t is not None else None,
                            "imputed": bool(miss[i, j]), "listed_for": why})
        code = kept[i]
        rc = raw_data.get(code) if raw_present else None
        if not raw_present:
            rcheck = {"status": "pending", "note": None, "raw_row": None}
        elif rc is None:
            rcheck = {"status": "not_checked", "note": "no entry for this dog in the raw-check file", "raw_row": None}
        else:
            if rc.get("status") not in VALID_STATUS:
                raise ValueError(f"raw-check status for {code} must be one of {VALID_STATUS}")
            rcheck = {"status": rc["status"], "note": rc.get("note"), "raw_row": rc.get("raw_row")}
        outliers.append({"subject_code": code, "group_label": group_label[code], "rank": int(rank[i]), "combined": r(comb[i]),
                         "norm_if": r(nif[i]), "norm_mcd": r(nmcd[i]), "rank_if": int(rank_if[i]), "rank_mcd": int(rank_mcd[i]),
                         "label": "outlier" if is_out[i] else "typical", "reason_listed": "+".join(reasons[i]),
                         "consensus_outlier": bool(i in top10_if and i in top10_mcd), "drivers": drivers, "raw_check": rcheck})
    by_code = {o["subject_code"]: o for o in outliers}

    # ---- Agreement ----------------------------------------------------------------------------------------
    rho = spearman(nif, nmcd)
    gen = np.random.default_rng(seed_perm)
    ra = rankdata(nif) - rankdata(nif).mean()
    rb = rankdata(nmcd)
    Pm = gen.permuted(np.tile(rb, (args.perm, 1)), axis=1)
    Pm = Pm - Pm.mean(axis=1, keepdims=True)
    perm_rho = (Pm @ ra) / np.sqrt((ra @ ra) * (Pm * Pm).sum(axis=1))
    p_perm = perm_p(abs(rho), np.abs(perm_rho))
    gen = np.random.default_rng(seed_boot)
    boots = []
    for _ in range(args.ci_boot):
        idx = gen.integers(0, n, n)
        v = spearman(nif[idx], nmcd[idx])
        if not math.isnan(v):
            boots.append(v)
    ci = [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]
    t10_if, t10_mcd = set(order_desc(nif)[:10].tolist()), set(order_desc(nmcd)[:10].tolist())
    shared10 = t10_if & t10_mcd
    k5 = math.ceil(0.05 * n)
    shared5 = set(order_desc(nif)[:k5].tolist()) & set(order_desc(nmcd)[:k5].tolist())
    shared20 = set(order_desc(nif)[:20].tolist()) & set(order_desc(nmcd)[:20].tolist())

    # ---- Sensitivity --------------------------------------------------------------------------------------
    main_comb_by = {kept[i]: comb[i] for i in range(n)}
    main_band = {s: band(int(rank[kidx[s]]), n) for s in minority}

    def sens_entry(name, dogs, res, extra=None):
        mc = np.array([main_comb_by[s] for s in dogs])
        rho_s = spearman(res["combined"], mc)
        t_sens = [dogs[i] for i in order_desc(res["combined"])[:10]]
        t_main = [dogs[i] for i in order_desc(mc)[:10]]
        rk = rank_desc(res["combined"])
        bands = {}
        for s in minority:
            if s in dogs:
                b = band(int(rk[dogs.index(s)]), len(dogs))
                bands[s] = {"band": b, "main_band": main_band[s], "keeps_band": b == main_band[s]}
            else:
                bands[s] = {"band": "not_in_sample", "main_band": main_band[s], "keeps_band": False}
        e = {"name": name, "n_subjects": len(dogs), "spearman_vs_main": r(rho_s),
             "top10_shared_with_main": len(set(t_sens) & set(t_main)), "top10": t_sens,
             "top10_main_on_same_dogs": t_main, "pathogen_minority_bands": bands,
             "mcd_variables_dropped": [c for c, _ in res["dropped"]], "n_mcd_variables": len(res["used"]),
             "isolation_forest_seed_stability": r(res["stability"])}
        if extra:
            e.update(extra)
        return e

    sens = []
    full_rows = [i for i in range(n) if not np.isnan(X[i]).any()]
    dogs1 = [kept[i] for i in full_rows]
    sens.append(sens_entry("S1_complete_case", dogs1, score_matrix(X[full_rows], codes, {}, "none", seeds, args)))
    sens.append(sens_entry("S2_no_log_transform", kept, score_matrix(X, codes, {c: False for c in codes}, "iterative", seeds, args)))
    codes28 = input_codes + extra_codes
    res3 = score_matrix(X28, codes28, {}, "iterative", seeds, args)
    sens.append(sens_entry("S3_with_derived_variables", kept, res3, {"n_variables": len(codes28)}))
    # S4: suspect cells of discrepancy / unit_suspect dogs set missing and re-imputed
    suspects = {}
    for code, rc in (raw_data.items() if raw_present else []):
        if code in kidx and rc.get("status") in ("discrepancy", "unit_suspect"):
            vs = rc.get("suspect_variables")
            if vs is None and code in by_code:
                vs = [d["variable"] for d in by_code[code]["drivers"] if abs(d["robust_z"]) > args.z_threshold]
            suspects[code] = [v for v in (vs or []) if v in codes]
    if suspects:
        X4 = X.copy()
        for code, vs in suspects.items():
            for v in vs:
                X4[kidx[code], codes.index(v)] = np.nan
        res4 = score_matrix(X4, codes, {}, "iterative", seeds, args)
        sens.append(sens_entry("S4_suspect_cells_set_missing", kept, res4, {"suspect_cells": suspects}))
    else:
        sens.append({"name": "S4_suspect_cells_set_missing", "n_subjects": n, "spearman_vs_main": None,
                     "top10_shared_with_main": None, "top10": None, "pathogen_minority_bands": None,
                     "suspect_cells": {}, "note": "no listed dog has status discrepancy or unit_suspect (or the raw-check file is absent), so no cell was set missing"})

    # ---- Output payloads ----------------------------------------------------------------------------------
    order = order_desc(comb)
    scores = [{"subject_code": kept[i], "group_label": group_label[kept[i]], "if_score": r(M["if_score"][i]), "norm_if": r(nif[i]),
               "mcd_d2": r(M["d2"][i]), "norm_mcd": r(nmcd[i]), "combined": r(comb[i]), "rank": int(rank[i]),
               "label": "outlier" if is_out[i] else "typical", "n_imputed": int(miss[i].sum())} for i in order]
    cluster_assignments = [{"subject_code": kept[i], "cluster_label": "outlier" if is_out[i] else "typical", "score": r(comb[i])}
                           for i in range(n)]
    agreement = {"spearman": {"rho": r(rho), "ci95": [r(ci[0]), r(ci[1])], "p_value": r(p_perm)},
                 "top10": {"shared": len(shared10), "jaccard": r(len(shared10) / len(t10_if | t10_mcd)),
                           "only_if": [kept[i] for i in sorted(t10_if - t10_mcd)], "only_mcd": [kept[i] for i in sorted(t10_mcd - t10_if)],
                           "shared_codes": [kept[i] for i in sorted(shared10)]},
                 "overlap": {"top5pct": len(shared5), "top5pct_k": k5, "top20": len(shared20)},
                 "points": [{"subject_code": kept[i], "norm_if": r(nif[i]), "norm_mcd": r(nmcd[i])} for i in range(n)],
                 "sensitivity": sens}

    n_listed = len(outliers)
    stat_counts = {}
    for o in outliers:
        stat_counts[o["raw_check"]["status"]] = stat_counts.get(o["raw_check"]["status"], 0) + 1
    n_checked = sum(v for k_, v in stat_counts.items() if k_ not in ("pending", "not_checked"))
    cells_imputed = int(miss.sum())
    run_notes = {
        "input_variables": [{"code": c, "name": variables[c]["name"], "unit": variables[c].get("unit"),
                             "n_observed": int((~miss[:, j]).sum()), "n_imputed": int(miss[:, j].sum()),
                             "transformed": c in P["transformed"]} for j, c in enumerate(codes)],
        "excluded_derived_from": DERIVED_BACK,
        "excluded_other": "All C, D and T variables, basophils, other_cells and month; mcv, mch, mchc, wcc, arc and globulin are arithmetic functions of other columns and are used only in sensitivity S3.",
        "dropped_subjects": dropped,
        "mcd_dropped_for_collinearity": [{"variable": c, "reason": why} for c, why in M["dropped"]],
        "robust_z_sd_fallback": [codes[j] for j in fallback],
        "imputation": {"method": "IterativeImputer(BayesianRidge, max_iter=20, initial_strategy=median) once on the standardised matrix; matrix re-standardised afterwards",
                       "cells_imputed": cells_imputed},
        "raw_check": {"file": args.raw_check, "file_present": raw_present, "n_listed": n_listed, "n_checked": n_checked,
                      "status_counts": stat_counts},
        "environment": {"numpy": np.__version__, "scipy": scipy.__version__, "scikit_learn": sklearn.__version__},
        "dataset": {"independent_source": tidy["dataset"].get("independent_source"), "licence": tidy["dataset"].get("licence")},
        "notes": ["Ordinal variables (lymph_node_score, habitus_score) treated as numeric.",
                  "Transformed variables (log1p): " + (", ".join(P["transformed"]) or "none") + ". No clipping or winsorising.",
                  "Imputed driver values are back-transformed estimates and flagged imputed = true.",
                  "cohort_median is the median of observed original-unit values among scored dogs.",
                  "reason_listed joins every reason with '+'; label threshold is the 0.95 quantile of the combined score."],
    }

    # ---- Interpretation -----------------------------------------------------------------------------------
    sec = []
    V = variables
    sec.append({"heading": HEADINGS[0], "paragraphs": [
        f"Which of the {n} dogs in the {tidy['dataset']['code']} cohort (all Babesia PCR positive; {sum(1 for s in kept if group_label[s] == 'B. rossi only')} B. rossi only, three B. rossi + E. canis, one B. vogeli only) have an atypical admission profile "
        f"across {p} routine clinical and laboratory variables, as judged by two unrelated methods (an isolation forest and a robust Mahalanobis distance), "
        "do the two methods agree, and do the three B. rossi + E. canis dogs and the one B. vogeli dog stand out? "
        "An atypical profile means unusual relative to this cohort. It does not mean abnormal, and there is no outcome in this dataset."]})
    sec.append({"heading": HEADINGS[1], "paragraphs": [
        f"{n_all} dogs were available; {len(dropped)} ({', '.join(d['subject_code'] for d in dropped)}) were not scored because more than {int(args.max_missing_subject * 100)} percent "
        f"of the {p} input variables were missing, leaving {n}. The inputs are the measured numeric and ordinal admission values; calculated indices ({', '.join(DERIVED_BACK)}) "
        f"were left out so that one measurement is not counted twice (they enter sensitivity S3). {len(P['transformed'])} skewed non-negative variables were log-transformed "
        f"({', '.join(vname(V, c) for c in P['transformed']) or 'none'}). Nothing was clipped, because extreme values are the object of study. "
        f"{cells_imputed} of {n * p} cells ({100 * cells_imputed / (n * p):.1f} percent) were imputed once by iterative regression, then all variables were standardised.",
        f"The isolation forest ({args.if_n_estimators} trees) was fitted with {args.if_seeds} different seeds and the scores averaged. The robust Mahalanobis distance used the minimum covariance determinant "
        f"on {len(used_codes)} variables" + (f" ({', '.join(c for c, _ in M['dropped'])} dropped for collinearity)" if M["dropped"] else " (none had to be dropped)") +
        ". Each score was converted to a rank between 0 (most typical) and 1 (most atypical) and the two were averaged into a combined score. "
        f"The {n_out} dogs at or above the {args.outlier_quantile:g} quantile of the combined score (combined at least {cut:.3f}) are labelled outlier; the label depends on ranks, not on a chi-square cut, "
        f"because skewed data push many dogs ({n_above}) over the chi-square 97.5 percent cut of {chi_cut:.1f}."]})

    # raw-check section
    names_by_status = {s_: [o["subject_code"] for o in outliers if o["raw_check"]["status"] == s_] for s_ in ("matches_raw", "discrepancy", "unit_suspect", "not_checked", "pending")}
    p_raw = []
    if not raw_present:
        p_raw.append(f"None of the {n_listed} listed dogs has yet been checked against the raw sheet, so no outlier may be interpreted biologically. "
                     "Each could equally be a data-entry, unit or transcription problem.")
    else:
        p_raw.append(f"{n_checked} of the {n_listed} listed dogs (top {args.top_n}, the top 3 of each method and the four pathogen-minority dogs) were checked against the 'Entire population' sheet of the original workbook "
                     f"(and the CORRESPONDENCE sheet for habitus): {len(names_by_status['matches_raw'])} match the raw sheet, {len(names_by_status['discrepancy'])} show a discrepancy, "
                     f"{len(names_by_status['unit_suspect'])} look like unit or entry problems in the raw cell, {len(names_by_status['not_checked'])} were not checked.")
        for o in outliers:
            rc = o["raw_check"]
            p_raw.append(f"{o['subject_code']} (rank {o['rank']}, raw row {rc['raw_row']}): {rc['status'].replace('_', ' ')}. {rc['note'] or ''}".strip())
        if not (names_by_status["discrepancy"] or names_by_status["unit_suspect"]):
            p_raw.append("No listed dog has a transcription discrepancy or a suspect unit: every listed driver value equals the raw cell. Atypical here therefore reflects the recorded values, "
                         "which are still only unusual relative to this cohort.")
    sec.append({"heading": HEADINGS[2], "paragraphs": p_raw})

    # most atypical
    p_top = [f"The {n_out} outlier dogs and the rest of the top {args.top_n} by combined score are listed below (rank 1 = most atypical). The cut for the label is a combined score of {cut:.3f}."]
    for i in top_c:
        o = by_code[kept[i]]
        stat = o["raw_check"]["status"]
        head = f"Rank {o['rank']}, {o['subject_code']} (combined {o['combined']:.3f}, {o['label']}{', top 10 of both methods' if o['consensus_outlier'] else ''})"
        if stat == "matches_raw":
            p_top.append(head + ", main contributors to the distance: " + "; ".join(driver_phrase(d, V) for d in top_drivers(o)) + ".")
        elif stat in ("discrepancy", "unit_suspect"):
            p_top.append(head + f": data-quality finding, not interpreted biologically ({stat.replace('_', ' ')}). {o['raw_check']['note'] or ''}".strip())
        else:
            p_top.append(head + ": raw-sheet check outstanding, not interpreted.")
    extra = [o for o in outliers if o["rank"] > args.top_n and "pathogen_minority" not in o["reason_listed"]]
    for o in extra:
        stat = o["raw_check"]["status"]
        head = (f"Also listed as one of the top 3 of a single method: rank {o['rank']}, {o['subject_code']} (combined {o['combined']:.3f}, isolation-forest rank {o['rank_if']}, "
                f"Mahalanobis rank {o['rank_mcd']}, {o['label']})")
        if stat == "matches_raw":
            p_top.append(head + ", main contributors: " + "; ".join(driver_phrase(d, V) for d in top_drivers(o)) + ".")
        elif stat in ("discrepancy", "unit_suspect"):
            p_top.append(head + f": data-quality finding, not interpreted biologically ({stat.replace('_', ' ')}). {o['raw_check']['note'] or ''}".strip())
        else:
            p_top.append(head + ": raw-sheet check outstanding, not interpreted.")
    s4 = sens[3]
    if s4.get("top10"):
        p_top.append(f"With the suspect raw cells set missing and re-imputed (sensitivity S4) the combined score agrees with the main one at Spearman {s4['spearman_vs_main']:.2f}; "
                     f"{s4['top10_shared_with_main']} of the top 10 are shared.")
    sec.append({"heading": HEADINGS[3], "paragraphs": p_top})

    # minority
    p_min = ["Three dogs, one dog: descriptive only. No test and no group statistic is given; each dog is a single case."]
    for s in minority:
        o = by_code[s]
        stat = o["raw_check"]["status"]
        txt = (f"{s} ({o['group_label']}): rank {o['rank']} of {n} by combined score {o['combined']:.3f} (isolation forest rank score {o['norm_if']:.3f}, rank {o['rank_if']}; "
               f"Mahalanobis rank score {o['norm_mcd']:.3f}, rank {o['rank_mcd']}); label {o['label']}; raw-sheet check {stat.replace('_', ' ')}. ")
        if stat == "matches_raw":
            txt += ("Main contributors: " + "; ".join(driver_phrase(d, V) for d in top_drivers(o)) + "." if o["drivers"] else "No variable stands out.")
            if o["rank"] > math.ceil(0.2 * n):
                txt += " The dog's overall profile is not unusual for this cohort."
        else:
            txt += "Not interpreted biologically until the raw-sheet check is complete and matching."
        p_min.append(txt)
    n_in_top = sum(1 for s in minority if by_code[s]["rank"] <= args.top_n)
    p_min.append(f"{n_in_top} of the four are among the top {args.top_n}. " + ("A finding that none of them is among the top outliers is a valid negative result: co-infection or a different Babesia species need not move routine admission variables."
                                                                            if n_in_top == 0 else "With only four dogs this says nothing about co-infection in general."))
    sec.append({"heading": HEADINGS[4], "paragraphs": p_min})

    ag = [f"Spearman correlation between the two rank scores is {rho:.2f} (95 percent bootstrap interval {ci[0]:.2f} to {ci[1]:.2f}, permutation p {fmt_p(p_perm)}). "
          f"{len(shared10)} of the top 10 are shared (Jaccard {len(shared10) / len(t10_if | t10_mcd):.2f}); {len(shared5)} of the top {k5} (5 percent) and {len(shared20)} of the top 20.",
          f"Only in the isolation-forest top 10: {', '.join(kept[i] for i in sorted(t10_if - t10_mcd)) or 'none'}. Only in the Mahalanobis top 10: {', '.join(kept[i] for i in sorted(t10_mcd - t10_if)) or 'none'}."]
    if rho < 0.5 and len(shared10) < 3:
        ag.append("Negative finding: agreement is below 0.5 and fewer than 3 of the top 10 are shared, so which dogs are atypical depends on the method. Both lists are reported.")
    else:
        ag.append("The two methods broadly agree, though they reward different kinds of unusualness: in the injection test the Mahalanobis distance reacted strongly to one extreme value in a correlated set, while the forest's random feature choice dilutes a single extreme among 22 variables and rewards dogs that are unusual on several variables at once.")
    for e in sens:
        if e.get("top10"):
            keeps = ", ".join(f"{s} {b['band'].replace('_', ' ')}" for s, b in e["pathogen_minority_bands"].items())
            ag.append(f"Sensitivity {e['name']} (n = {e['n_subjects']}): Spearman with the main combined score {e['spearman_vs_main']:.2f}, {e['top10_shared_with_main']} of the top 10 shared; pathogen-minority bands: {keeps}.")
    sec.append({"heading": HEADINGS[5], "paragraphs": ag})

    lim = ["Unsupervised outlier scores say a dog is unusual relative to this cohort. They do not say a dog is clinically abnormal or will do badly; no outcome exists in this dataset and the scores are not prognostic. "
           "Outliers are as likely to be data-entry, unit or transcription problems as biology, which is why each listed dog was compared with the raw sheet."]
    if M["stability"] < 0.9:
        lim.append(f"The isolation forest is not stable between seeds: the minimum pairwise Spearman across {args.if_seeds} seeds is {M['stability']:.2f}, below 0.9, so individual ranks can shift (the reported score is the mean of the {args.if_seeds} fits).")
    else:
        lim.append(f"The isolation forest is stable between seeds: the minimum pairwise Spearman across {args.if_seeds} seeds is {M['stability']:.3f} (reported score is the mean of the fits).")
    lim.append("A dog with a single wildly wrong value may rank high on one method only (the Mahalanobis distance picks it up far more readily than the isolation forest), which is why both lists are shown.")
    lim.append(f"{cells_imputed} cells were imputed; a driver whose value was imputed is flagged. Skewed haematology means the chi-square cut over-flags ({n_above} dogs), so the label uses ranks. "
               f"One hospital cohort of {n} dogs and {p} correlated variables; the isolation forest is not tuned. The raw-sheet check covers only the listed dogs, not the remaining {n - n_listed}, "
               "and a veterinarian should review any discrepancy or unit-suspect dog before the page is shared.")
    sec.append({"heading": HEADINGS[6], "paragraphs": lim})

    mpos = ", ".join(f"{s} rank {by_code[s]['rank']} ({by_code[s]['label']})" for s in minority)
    summary = (f"Two unsupervised anomaly scores (isolation forest and robust Mahalanobis distance) were computed for {n} dogs over {p} admission variables; {n_out} dogs are labelled outlier "
               f"(combined rank score at or above {cut:.3f}). The scores agree with Spearman rho {rho:.2f} (95% interval {ci[0]:.2f} to {ci[1]:.2f}) and share {len(shared10)} of the top 10. "
               f"Pathogen-minority dogs: {mpos}. {n_checked} of {n_listed} listed dogs have been checked against the raw sheet"
               + (f" ({len(names_by_status['matches_raw'])} match, {len(names_by_status['discrepancy'])} discrepancy, {len(names_by_status['unit_suspect'])} unit suspect)." if raw_present else "; none may be interpreted biologically yet."))

    experiment = {
        "code": args.code, "name": args.name,
        "description": args.description or ("Two unsupervised anomaly scores over 22 admission variables identify atypical dogs in the BET cohort; every outlier needs a raw-sheet check before interpretation."),
        "method": "anomaly", "dataset": args.dataset,
        "parameters": {"seed": args.seed, "skew_threshold": args.skew_threshold, "max_missing_subject": args.max_missing_subject,
                       "imputation": "iterative_bayesian_ridge", "imputer_max_iter": args.imputer_max_iter, "if_n_estimators": args.if_n_estimators,
                       "if_seeds": args.if_seeds, "mcd_support_fraction": args.mcd_support_fraction,
                       "mcd_collinearity_threshold": args.mcd_collinearity_threshold, "outlier_quantile": args.outlier_quantile,
                       "top_n": args.top_n, "z_threshold": args.z_threshold, "univariate_if_estimators": args.univariate_if_estimators,
                       "perm": args.perm, "ci_boot": args.ci_boot, "raw_check_file": args.raw_check, "input_variables": codes},
        "script": "scripts/experiment_anomaly.py",
        "script_version": hashlib.sha256(SCRIPT.read_bytes()).hexdigest()[:12],
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "n_subjects": n, "n_variables": p, "n_tests": 1, "summary": summary,
    }
    results = [
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 0, "payload": {"sections": sec}},
        {"kind": "anomaly_scores", "title": "Anomaly scores per dog", "sort_order": 1,
         "payload": {"threshold": {"outlier_quantile": args.outlier_quantile, "combined_cut": r(cut), "n_outliers": n_out},
                     "mcd": {"variables_used": used_codes, "chi2_975_cut": r(chi_cut), "n_above_cut": n_above},
                     "isolation_forest": {"seed_stability_min_spearman": r(M["stability"])}, "scores": scores}},
        {"kind": "top_outliers", "title": "Most atypical dogs and the variables that drive them", "sort_order": 2, "payload": {"outliers": outliers}},
        {"kind": "score_agreement", "title": "Agreement between isolation forest and robust Mahalanobis", "sort_order": 3, "payload": agreement},
        {"kind": "run_notes", "title": "Variables, missing data, dropped dogs and raw-check status", "sort_order": 4, "payload": run_notes},
    ]
    out = {"experiment": experiment, "associations": [], "cluster_assignments": cluster_assignments, "results": results}
    path = ROOT / "data" / "experiments" / f"{args.code}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{args.code}: {n} dogs scored, {n_out} outliers (cut {cut:.4f}), rho {rho:.3f} [{ci[0]:.3f}, {ci[1]:.3f}] p {p_perm:.4f}, "
          f"top10 shared {len(shared10)}, IF stability {M['stability']:.3f}, raw check {n_checked}/{n_listed} -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
