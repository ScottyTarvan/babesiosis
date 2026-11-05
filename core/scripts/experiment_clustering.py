"""Clustering experiment over a tidy dataset (data/tidy/<DS>.json): admission phenotype structure.

Question: do the dogs fall into recognisable phenotype groups, or form one continuum, and which axes
carry the variance?  Steps (spec: experiment_specs/EXP02-DS05-clustering.md):

  - input = numeric/ordinal variables with include_default, derived = false and no derived_from
    (arithmetic functions of other columns are left out); dogs or variables with more than 30 percent
    missing are dropped; skewed non-negative variables get log1p; standardise, iterative imputation
    (BayesianRidge) once, re-standardise, clip at +/-4 for clustering;
  - PCA with parallel analysis (axes kept), varimax factor analysis beside it;
  - k chosen by the highest Ward mean silhouette among admissible k (smallest cluster >= 8 dogs),
    Gaussian mixture BIC reported beside it, parametric-null silhouette test;
  - stability: bootstrap Jaccard (Hennig), 80 percent subsample consensus, Jaccard for every admissible k;
  - cluster profiles in original units, cross-tabulation against the authors' derived classes, PCR and
    group (chi-square, Cramer's V with bootstrap interval, permutation p, Benjamini-Hochberg);
  - five sensitivity analyses (complete case, median imputation, fewer clinical variables, derived
    variables added back, no log transform);
  - figure coordinates: UMAP if umap-learn is installed, otherwise the first two principal components.

Output: data/experiments/<code>.json, read by the console ExperimentLoader. Nothing else is written.
Add --selftest to run the permutation sanity check (shuffled anaemia_class, 100 times) instead of
writing the file.

Not stdlib-only: needs numpy, scipy and scikit-learn (use .venv-nlp; .venv has numpy only); umap-learn
is optional. Run from core/:
    .venv-nlp/Scripts/python.exe -I scripts/experiment_clustering.py --dataset DS05 --code EXP02-DS05-clustering \
        --name "Admission phenotype structure, BET cohort" [--seed 20261105] [--n-boot 200] [--n-consensus 200] \
        [--null-sims 200] [--pa-permutations 500] [--perm 5000] [--ci-boot 1000] [--k-min 2] [--k-max 8] \
        [--min-cluster-size 8] [--min-level 5] [--skew-threshold 1.0] [--clip-z 4.0] [--selftest]
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
from scipy.cluster.hierarchy import cut_tree, linkage
from scipy.spatial.distance import pdist, squareform
from scipy.stats import skew
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import FactorAnalysis, PCA
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge
from sklearn.metrics import adjusted_rand_score, silhouette_samples
from sklearn.mixture import GaussianMixture

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()

DERIVED_BACK = ["mcv", "mch", "mchc", "wcc", "arc", "globulin"]
HELD_OUT = ["anaemia_class", "left_shift", "habitus_class", "illness_class", "arc_class", "pcr_e_canis", "group_label"]
DESCRIPTIVE = {"pcr_e_canis", "group_label"}
NOT_TABULATED = ["pcr_b_rossi", "pcr_b_vogeli", "pcr_t_equi"]
AXIS_GROUPS = [("red-cell (anaemia) variables", ["haemoglobin", "haematocrit", "rcc", "reticulocyte_pct"]),
               ("inflammatory / left-shift variables", ["band_neutrophils", "seg_neutrophils", "monocytes", "lymphocytes", "platelets"]),
               ("protein variables", ["total_protein", "albumin"])]


# ---------------------------------------------------------------------------------------------------------
# Helpers (bh_adjust, perm_p, chi-square copied from experiment_pairwise.py: -I removes the script folder)
# ---------------------------------------------------------------------------------------------------------

def bh_adjust(p):
    p = np.asarray(p, dtype=float)
    m = len(p)
    if m == 0:
        return p
    order = np.argsort(p)
    ranked = p[order] * m / np.arange(1, m + 1)
    adj = np.minimum.accumulate(ranked[::-1])[::-1]
    out = np.empty(m)
    out[order] = np.minimum(adj, 1.0)
    return out


def perm_p(stat, perm_stats):
    return (np.count_nonzero(perm_stats >= stat - 1e-12) + 1) / (len(perm_stats) + 1)


def r(x, nd=4):
    if x is None:
        return None
    x = float(x)
    return None if math.isnan(x) else round(x, nd)


def fmt_p(p):
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


def chi_square(a, b, B, rng, ci_boot=0):
    """Chi-square and Cramer's V of cluster a against class b; permutation p by shuffling b (as EXP01)."""
    la, ca = np.unique(a, return_inverse=True)
    lb, cb = np.unique(b, return_inverse=True)
    ka, kb = len(la), len(lb)
    n = len(a)
    if ka < 2 or kb < 2:
        return None
    A = np.zeros((n, ka))
    A[np.arange(n), ca] = 1.0
    Bm = np.zeros((n, kb))
    Bm[np.arange(n), cb] = 1.0
    O = A.T @ Bm
    E = np.outer(O.sum(axis=1), O.sum(axis=0)) / n
    chi2 = float(((O - E) ** 2 / E).sum())
    V = math.sqrt(chi2 / (n * (min(ka, kb) - 1)))
    P = rng.permuted(np.tile(cb, (B, 1)), axis=1)
    Bp = (P[:, :, None] == np.arange(kb)[None, None, :]).astype(float)
    Op = np.einsum("nk,bnl->bkl", A, Bp)
    chi2_perm = ((Op - E) ** 2 / E).sum(axis=(1, 2))
    p = perm_p(chi2, chi2_perm)
    ci = [None, None]
    if ci_boot:
        vs = []
        for _ in range(ci_boot):
            idx = rng.integers(0, n, n)
            Ob = np.zeros((ka, kb))
            np.add.at(Ob, (ca[idx], cb[idx]), 1.0)
            Ob = Ob[Ob.sum(axis=1) > 0][:, Ob.sum(axis=0) > 0]
            if min(Ob.shape) < 2:
                continue
            Eb = np.outer(Ob.sum(axis=1), Ob.sum(axis=0)) / n
            vs.append(math.sqrt(((Ob - Eb) ** 2 / Eb).sum() / (n * (min(Ob.shape) - 1))))
        if vs:
            ci = [float(np.percentile(vs, 2.5)), float(np.percentile(vs, 97.5))]
    table = {str(la[x]): {str(lb[y]): int(O[x, y]) for y in range(kb)} for x in range(ka)}
    return {"chi2": chi2, "v": V, "p": p, "ci": ci, "table": table, "n": n}


# ---------------------------------------------------------------------------------------------------------
# Matrix preparation
# ---------------------------------------------------------------------------------------------------------

def standardise(M):
    return (M - np.nanmean(M, axis=0)) / np.nanstd(M, axis=0, ddof=1)


def build_matrix(raw, codes, fixed, mode, seed, skew_threshold, clip_z, max_iter=20):
    """raw: dogs x variables with NaN. fixed: {code: bool} forced transform decisions; others by the skew rule."""
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
    Z0 = standardise(T)
    miss = np.isnan(Z0)
    if mode == "none":
        if miss.any():
            raise ValueError("complete case matrix has gaps")
        Zs = Z0
    else:
        if mode == "median":
            Zi = np.where(miss, np.nanmedian(Z0, axis=0), Z0)
        else:
            Zi = IterativeImputer(estimator=BayesianRidge(), max_iter=max_iter, sample_posterior=False,
                                  initial_strategy="median", random_state=seed).fit_transform(Z0)
        Zs = (Zi - Zi.mean(axis=0)) / Zi.std(axis=0, ddof=1)
    Zc = np.clip(Zs, -clip_z, clip_z)
    return {"T": T, "transformed": transformed, "Zs": Zs, "Zc": Zc, "miss": miss,
            "clipped": (np.abs(Zs) > clip_z).sum(axis=0)}


def fit_pca(Zs):
    pca = PCA(svd_solver="full").fit(Zs)
    comp = pca.components_.copy()
    for i in range(comp.shape[0]):  # sign: largest absolute loading positive
        if comp[i, np.argmax(np.abs(comp[i]))] < 0:
            comp[i] = -comp[i]
    return comp, pca.explained_variance_, pca.explained_variance_ratio_, Zs @ comp.T


def parallel_analysis(Zs, B, gen):
    n, p = Zs.shape
    eig = np.empty((B, p))
    for b in range(B):
        P = np.column_stack([gen.permutation(Zs[:, j]) for j in range(p)])
        eig[b] = np.sort(np.linalg.eigvalsh(np.cov(P, rowvar=False)))[::-1]
    return np.percentile(eig, 95, axis=0)


# ---------------------------------------------------------------------------------------------------------
# Ward search, silhouette, stability
# ---------------------------------------------------------------------------------------------------------

def silhouette_D(D, labels):
    ks = np.unique(labels)
    if len(ks) < 2:
        return np.zeros(len(labels))
    n = len(labels)
    mean_d = np.zeros((n, len(ks)))
    sizes = np.array([(labels == k).sum() for k in ks])
    for t, k in enumerate(ks):
        mean_d[:, t] = D[:, labels == k].sum(axis=1)
    own = np.searchsorted(ks, labels)
    a = mean_d[np.arange(n), own] / np.maximum(sizes[own] - 1, 1)
    other = mean_d / sizes[None, :]
    other[np.arange(n), own] = np.inf
    b = other.min(axis=1)
    s = (b - a) / np.maximum(np.maximum(a, b), 1e-12)
    s[sizes[own] == 1] = 0.0
    return s


def ward_search(Zc, ks, min_size):
    D = squareform(pdist(Zc))
    L = linkage(Zc, "ward")
    cuts = cut_tree(L, n_clusters=list(ks))
    out = {}
    for t, k in enumerate(ks):
        lab = cuts[:, t]
        sizes = np.bincount(lab, minlength=k)
        s = silhouette_D(D, lab)
        out[k] = {"labels": lab, "sil_samples": s, "sil": float(s.mean()), "min_size": int(sizes.min()),
                  "admissible": bool(sizes.min() >= min_size)}
    adm = [k for k in ks if out[k]["admissible"]]
    best = max(adm, key=lambda k: (out[k]["sil"], -k)) if adm else None
    return out, best


def jaccard_bootstrap(Zc, ks, orig, n_boot, gen):
    """orig: {k: labels}. Returns {k: array (n_boot, k)} of per-cluster best Jaccard."""
    n = len(Zc)
    res = {k: np.zeros((n_boot, k)) for k in ks}
    for b in range(n_boot):
        idx = gen.integers(0, n, n)
        ins = np.zeros(n, bool)
        ins[idx] = True
        cuts = cut_tree(linkage(Zc[idx], "ward"), n_clusters=list(ks))
        for t, k in enumerate(ks):
            lb = cuts[:, t]
            Bm = np.zeros((k, n))
            for j in range(k):
                Bm[j, np.unique(idx[lb == j])] = 1.0
            Cm = np.zeros((k, n))
            for i in range(k):
                Cm[i] = ((orig[k] == i) & ins).astype(float)
            inter = Cm @ Bm.T
            union = Cm.sum(axis=1)[:, None] + Bm.sum(axis=1)[None, :] - inter
            res[k][b] = (inter / np.maximum(union, 1e-12)).max(axis=1)
    return res


def consensus(Zc, k, n_cons, frac, gen):
    n = len(Zc)
    co = np.zeros((n, n))
    both = np.zeros((n, n))
    m = int(round(frac * n))
    for _ in range(n_cons):
        idx = np.sort(gen.choice(n, m, replace=False))
        lab = cut_tree(linkage(Zc[idx], "ward"), n_clusters=[k])[:, 0]
        same = (lab[:, None] == lab[None, :]).astype(float)
        co[np.ix_(idx, idx)] += same
        both[np.ix_(idx, idx)] += 1.0
    return co / np.maximum(both, 1.0)


def tucker(a, b):
    return float(abs(a @ b) / math.sqrt(float(a @ a) * float(b @ b)))


# ---------------------------------------------------------------------------------------------------------
# Interpretation (templated from the results)
# ---------------------------------------------------------------------------------------------------------

def jaccard_word(m):
    if m < 0.6:
        return "unstable"
    if m < 0.75:
        return "a pattern with uncertainty"
    if m <= 0.85:
        return "stable"
    return "highly stable"


def describe_cluster(c, variables):
    d = c["distinguishing"][:3]
    if not d:
        return f"{c['label']} (n = {c['n']}): no variable separates it from the other dogs by 0.8 robust SD or more."
    parts = ", ".join(f"{x['direction']} {variables[x['variable']]['name'].lower()} ({x['std_diff']:+.1f})" for x in d)
    return f"{c['label']} (n = {c['n']}, median silhouette {c['median_silhouette']:.2f}): {parts}."


def names(codes, variables):
    n = [variables[c]["name"].lower() for c in codes]
    return ", ".join(n[:-1]) + " and " + n[-1] if len(n) > 1 else n[0]


def build_interpretation(ctx):
    V = ctx["variables"]
    a = ctx["args"]
    axes = ctx["axes"]
    sec = []
    sec.append({"heading": "Question", "paragraphs": [
        f"Do the {ctx['n']} dogs of the {ctx['dataset']['code']} cohort, all positive for Babesia on PCR (146 of 150 B. rossi only), fall into recognisable admission "
        "phenotype groups, or do they form one continuum? And which laboratory and clinical axes carry most of the variance: a regenerative-anaemia axis "
        "(haemoglobin, haematocrit, red cell count, reticulocytes), an inflammatory axis (band and segmented neutrophils, monocytes, lymphocytes, platelets) "
        "and a protein axis (total protein, albumin)?"]})
    nd = len(ctx["dropped"])
    sec.append({"heading": "What was done", "paragraphs": [
        f"{ctx['n_all']} dogs were available; {nd} ({', '.join(d['subject_code'] for d in ctx['dropped'])}) were dropped because more than {int(a.max_missing_subject * 100)} percent "
        f"of the {ctx['p']} input variables were missing, leaving {ctx['n']}. The {ctx['p']} input variables are the measured numeric and ordinal admission values; "
        f"calculated indices ({', '.join(DERIVED_BACK)}) were left out so that no axis is built from a variable and its own parts. "
        f"{len(ctx['transformed'])} skewed non-negative variables were log-transformed ({names(ctx['transformed'], V) if ctx['transformed'] else 'none'}). "
        f"All variables were standardised; {ctx['cells_imputed']} of {ctx['n'] * ctx['p']} cells ({100 * ctx['cells_imputed'] / (ctx['n'] * ctx['p']):.1f} percent) were filled once by iterative regression imputation, "
        f"and standardised values were capped at +/-{a.clip_z:g} for clustering.",
        f"Principal component analysis kept {ctx['n_axes']} axes by parallel analysis ({a.pa_permutations} permutations; the Kaiser rule would keep {ctx['kaiser']}). "
        f"Clusters were found with Ward hierarchical clustering on the standardised variables for k = {a.k_min} to {a.k_max}, requiring at least {a.min_cluster_size} dogs in the smallest cluster; "
        "k was the one with the highest mean silhouette. A Gaussian mixture on the principal components, a simulated no-structure null, bootstrap resampling "
        f"({a.n_boot} resamples) and repeated 80 percent subsampling ({a.n_consensus} subsamples) were used to judge whether the clusters are real. "
        "Cluster labels were then compared with the authors' own classes."]})

    # main axes
    p = []
    for ax in axes[:ctx["n_axes"]]:
        p.append(f"{ax['axis']} (eigenvalue {ax['eigenvalue']:.2f}, {100 * ax['explained_variance_ratio']:.1f} percent of the variance) is led by {names(ax['top_variables'], V)}.")
    p.append(f"The {ctx['n_axes']} retained axes together carry {100 * axes[ctx['n_axes'] - 1]['cumulative']:.1f} percent of the variance.")
    for (label, grp), res in zip(AXIS_GROUPS, ctx["axis_match"]):
        p.append(f"The {label} load most on {res['axis']} (mean absolute loading {res['mean_abs']:.2f}); expected on {res['expected']}"
                 f"{' - as expected' if res['axis'] == res['expected'] else ' - not as expected'}.")
    if not (set(axes[0]["top_variables"]) & set(AXIS_GROUPS[0][1])):
        p.append(f"PC1 is not led by red-cell variables; it is led by {names(axes[0]['top_variables'], V)}. This is a finding about these data, not an error.")
    for line in ctx["exp01_lines"]:
        p.append(line)
    sec.append({"heading": "Main axes", "paragraphs": p})

    # groups
    ks = ctx["k_search"]
    sil = ctx["sil"]
    nul = ctx["null"]
    boot = ctx["boot_clusters"]
    mj = ctx["mean_jaccard_chosen"]
    p = [f"The chosen number of clusters is k = {ctx['k']} (highest Ward mean silhouette among admissible k: " +
         "; ".join(f"k = {x['k']}: {x['ward_silhouette']:.3f}" for x in ks if x["admissible"]) + f"). Mean silhouette at k = {ctx['k']} is {sil:.3f}. "
         "A silhouette below 0.25 means a continuum rather than separate groups; 0.25 to 0.5 is weak structure.",
         f"Cluster sizes: {', '.join(f'{c['label']} {c['n']}' for c in ctx['clusters'])}.",
         f"Against a no-structure null (simulated Gaussian data with the same correlations, {nul['sims']} runs), the 95th percentile of the best silhouette is {nul['null_p95']:.3f}; "
         f"the observed best silhouette is {nul['observed']:.3f}, permutation-style p {fmt_p(nul['p_value'])}.",
         f"Bootstrap stability (Hennig clusterwise Jaccard): " + "; ".join(f"{b['label']} mean {b['mean_jaccard']:.2f} ({jaccard_word(b['mean_jaccard'])})" for b in boot) +
         f". Guide: below 0.6 unstable, 0.6 to 0.75 a pattern with uncertainty, above 0.75 stable, above 0.85 highly stable. Mean over clusters {mj:.2f}.",
         f"Consensus over subsamples: mean co-clustering within clusters " + ", ".join(f"{k} {v:.2f}" for k, v in ctx["cons_within"].items()) +
         f", between clusters {ctx['cons_between']:.2f}; PAC (share of dog pairs with an ambiguous consensus of 0.1 to 0.9) {ctx['pac']:.2f}.",
         f"The Gaussian mixture on the principal components prefers k = {ctx['gmm_k']} ({ctx['gmm_cov']} covariance by BIC)" +
         (f"; at the chosen k its partition agrees with Ward with an adjusted Rand index of {ctx['ari_ward_gmm']:.2f}." if ctx['gmm_k'] != ctx['k'] else
          f", the same k; the two partitions agree with an adjusted Rand index of {ctx['ari_ward_gmm']:.2f}.")]
    neg = []
    if sil < 0.25:
        neg.append(f"mean silhouette {sil:.2f} is below 0.25")
    if sum(1 for b in boot if b["mean_jaccard"] < 0.6) > len(boot) / 2:
        neg.append("most clusters have bootstrap mean Jaccard below 0.6")
    if nul["p_value"] > a.alpha:
        neg.append(f"the silhouette is not better than the null (p {fmt_p(nul['p_value'])})")
    if neg and mj >= 0.75:
        p.append(f"The high bootstrap Jaccard values do not contradict this: with k = {ctx['k']} the split falls along the dominant axis and is reproducible, but a reproducible cut through a continuum is not evidence of separate groups.")
    if neg:
        p.append("Negative finding: " + "; ".join(neg) + ". The cohort is a continuum along the principal axes, not a set of groups; the clusters are only a convenient partition and should not be read as separate phenotype groups.")
    else:
        p.append("Structure criteria are met: silhouette at or above 0.25, bootstrap stability not poor for most clusters, and the silhouette exceeds the null. Even so, treat the clusters as exploratory phenotype groups.")
    p.append("What distinguishes each cluster (difference of the cluster median from the other dogs, in robust standard deviations):")
    for c in ctx["clusters"]:
        p.append(describe_cluster(c, V))
    sec.append({"heading": "Do the dogs form groups?", "paragraphs": p})

    # crosstabs
    p = [f"Cluster labels were cross-tabulated with the authors' derived classes, PCR result for E. canis and the group label. {len(ctx['tests'])} tests were adjusted together with Benjamini-Hochberg.",
         "Circularity: the authors' classes are cut from variables used here (" + "; ".join(f"{t['class_variable']} from {', '.join(t['parents_in_input']) or 'arc, not an input'}" for t in ctx["tests"] if t["circular"]) +
         "). Agreement is therefore expected by construction and is a sanity check, not a discovery."]
    for t in ctx["tests"]:
        if t["descriptive_only"]:
            tot = {}
            for row in t["table"].values():
                for lv_, c_ in row.items():
                    tot[lv_] = tot.get(lv_, 0) + c_
            minor = sorted(c_ for c_ in tot.values() if c_ < a.min_level)
            p.append(f"{t['class_variable']}: too few dogs to test (minority levels have {', '.join(str(x) for x in minor)} dogs); the table is descriptive only (n = {t['n']}).")
        else:
            lo, hi = t["v_ci95"]
            p.append(f"{t['class_variable']} (n = {t['n']}): Cramer's V {t['cramers_v']:.2f} (95 percent interval {lo:.2f} to {hi:.2f}), adjusted p {fmt_p(t['p_adjusted'])}"
                     f"{'; ' + t['levels_merged'] if t['levels_merged'] else ''}.")
    sec.append({"heading": "Comparison with the authors' classes and co-infection", "paragraphs": p})

    # robustness
    p = ["Each sensitivity analysis repeats the standardisation, clustering and k choice with one change and compares the result with the main partition on the dogs they share (adjusted Rand index, ARI) and compares the first three principal axes with the main ones (Tucker congruence, 1 = identical; axes compared in order, shared variables only)."]
    for s in ctx["sens"]:
        p.append(f"{s['name']} (n = {s['n_subjects']}): chosen k = {s['chosen_k']}, silhouette {s['silhouette']:.3f}, ARI with main {s['ari_vs_main']:.2f}, Tucker PC1 to PC3 " + ", ".join(f"{x:.2f}" for x in s["tucker_pc1_3"]) + ".")
    p.append(("The partition is robust by the pre-set rule: complete-case and median-imputation analyses each give the same k or an ARI of at least 0.6 with the main partition."
              if ctx["robust"] else
              "The partition is NOT robust by the pre-set rule: the complete-case and median-imputation analyses do not both give the same k or an ARI of at least 0.6 with the main partition."))
    sec.append({"heading": "Robustness to missing data", "paragraphs": p})

    sec.append({"heading": "Limits", "paragraphs": [
        f"{ctx['n']} dogs and {ctx['p']} correlated variables: the analysis is exploratory. Clusters are phenotype groupings of admission values; the dataset has no outcome, so nothing here is prognostic and nothing is meant for clinical use.",
        "One hospital cohort, B. rossi in 146 of 150 dogs. The 3 E. canis co-infected dogs and the 1 B. vogeli dog support counts only; no tests.",
        "Values are from a single admission, so group membership says nothing about the course of disease.",
        "Missing values were filled once before resampling, so stability is optimistic for the variables with the most gaps (respiratory rate and temperature). Ordinal scores (lymph node score, habitus score) were treated as numbers.",
        "Entry or unit errors in the raw sheet can drive an axis; atypical dogs are handled in a separate experiment (EXP06) and checked against the raw sheet.",
        "UMAP was not available, so the figure coordinates are the first two principal components; they feed no statistic." if not ctx["umap"] else "Figure coordinates are a UMAP embedding; they feed no statistic."]})
    return sec


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
    ap.add_argument("--clip-z", type=float, default=4.0)
    ap.add_argument("--max-missing-subject", type=float, default=0.30)
    ap.add_argument("--max-missing-variable", type=float, default=0.30)
    ap.add_argument("--imputer-max-iter", type=int, default=20)
    ap.add_argument("--pa-permutations", type=int, default=500)
    ap.add_argument("--k-min", type=int, default=2)
    ap.add_argument("--k-max", type=int, default=8)
    ap.add_argument("--min-cluster-size", type=int, default=8)
    ap.add_argument("--gmm-n-init", type=int, default=10)
    ap.add_argument("--null-sims", type=int, default=200)
    ap.add_argument("--n-boot", type=int, default=200)
    ap.add_argument("--n-consensus", type=int, default=200)
    ap.add_argument("--consensus-fraction", type=float, default=0.8)
    ap.add_argument("--min-level", type=int, default=5)
    ap.add_argument("--perm", type=int, default=5000)
    ap.add_argument("--ci-boot", type=int, default=1000)
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--umap-n-neighbors", type=int, default=15)
    ap.add_argument("--umap-min-dist", type=float, default=0.1)
    ap.add_argument("--selftest", action="store_true", help="run the shuffled anaemia_class sanity check; write nothing")
    args = ap.parse_args()

    tidy = json.loads((ROOT / "data" / "tidy" / f"{args.dataset}.json").read_text(encoding="utf-8"))
    variables = {v["code"]: v for v in tidy["variables"]}
    subjects = [s["code"] for s in tidy["subjects"]]
    sidx = {s: i for i, s in enumerate(subjects)}
    n_all = len(subjects)
    group_label = {s["code"]: s["group_label"] for s in tidy["subjects"]}

    input_codes = [v["code"] for v in tidy["variables"]
                   if v["data_type"] in ("N", "O") and v["include_default"] and not v["derived"] and not v.get("derived_from")]
    extra_codes = [c for c in DERIVED_BACK if c in variables]
    all_codes = input_codes + extra_codes
    cidx = {c: i for i, c in enumerate(all_codes)}
    Xall = np.full((n_all, len(all_codes)), np.nan)
    texts = {}
    for o in tidy["observations"]:
        c = o["variable"]
        if c in cidx and o["value_num"] is not None:
            Xall[sidx[o["subject"]], cidx[c]] = o["value_num"]
        elif c in HELD_OUT or c in ("anaemia_class",):
            if o["value_text"] is not None:
                texts.setdefault(c, {})[o["subject"]] = o["value_text"]
    texts["group_label"] = dict(group_label)

    rng = np.random.default_rng(args.seed)

    def child():
        return int(rng.integers(0, 2 ** 31 - 1))

    ks = list(range(args.k_min, args.k_max + 1))

    # ---- Filter ------------------------------------------------------------------------------------------
    X_in = Xall[:, :len(input_codes)]
    miss_frac = np.isnan(X_in).mean(axis=1)
    keep = miss_frac <= args.max_missing_subject
    lab_codes = ["haemoglobin", "rcc", "haematocrit", "total_protein", "albumin"]
    dropped = []
    for i in np.where(~keep)[0]:
        none_lab = all(np.isnan(Xall[i, cidx[c]]) for c in lab_codes if c in cidx)
        dropped.append({"subject_code": subjects[i],
                        "reason": ("no haematology or biochemistry; " if none_lab else "") + f"{int(np.isnan(X_in[i]).sum())} of {len(input_codes)} input variables missing"})
    kept_idx = np.where(keep)[0]
    Xk = X_in[kept_idx]
    vmiss = np.isnan(Xk).mean(axis=0)
    vkeep = vmiss <= args.max_missing_variable
    dropped_vars = [{"code": input_codes[j], "reason": f"{100 * vmiss[j]:.0f} percent missing"} for j in np.where(~vkeep)[0]]
    codes = [c for c, k in zip(input_codes, vkeep) if k]
    Xm = Xk[:, vkeep]
    n, p = Xm.shape
    kept_subjects = [subjects[i] for i in kept_idx]

    # ---- Matrix, PCA --------------------------------------------------------------------------------------
    seed_imp = child()
    M = build_matrix(Xm, codes, {}, "iterative", seed_imp, args.skew_threshold, args.clip_z, args.imputer_max_iter)
    Zs, Zc = M["Zs"], M["Zc"]
    comp, eigv, evr, scores = fit_pca(Zs)
    thr = parallel_analysis(Zs, args.pa_permutations, np.random.default_rng(child()))
    pa_count = 0
    while pa_count < p and eigv[pa_count] > thr[pa_count]:
        pa_count += 1
    n_axes = int(min(max(pa_count, 2), 8))
    kaiser = int((eigv > 1).sum())
    fa = FactorAnalysis(n_components=n_axes, rotation="varimax", random_state=child()).fit(Zs)
    fl = fa.components_.copy()
    for i in range(n_axes):
        if fl[i, np.argmax(np.abs(fl[i]))] < 0:
            fl[i] = -fl[i]

    axes = []
    cum = 0.0
    for i in range(p):
        cum += float(evr[i])
        top = [codes[j] for j in np.argsort(-np.abs(comp[i]))[:3]]
        ax = {"axis": f"PC{i + 1}", "eigenvalue": r(eigv[i]), "explained_variance_ratio": float(evr[i]), "cumulative": cum,
              "loadings": {c: r(comp[i, j]) for j, c in enumerate(codes)}, "top_variables": top}
        if i < n_axes:
            ax["varimax_loadings"] = {c: r(fl[i, j]) for j, c in enumerate(codes)}
        axes.append(ax)
    ev_sum = float(evr.sum())

    # which retained PC carries each expected axis group
    axis_match = []
    for gi, (label, grp) in enumerate(AXIS_GROUPS):
        js = [codes.index(c) for c in grp if c in codes]
        means = [float(np.mean(np.abs(comp[i, js]))) for i in range(n_axes)]
        best = int(np.argmax(means))
        axis_match.append({"axis": f"PC{best + 1}", "mean_abs": means[best], "expected": f"PC{gi + 1}"})

    # ---- Choose k -----------------------------------------------------------------------------------------
    search, best_k = ward_search(Zc, ks, args.min_cluster_size)
    if best_k is None:
        best_k = ks[0]
    k = best_k
    # main partition via sklearn (identical to scipy ward; checked)
    lab_sk = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(Zc)
    ward_vs_sk_ari = adjusted_rand_score(lab_sk, search[k]["labels"])
    main_lab = search[k]["labels"]

    P_gmm = scores[:, :n_axes]
    gmm = {}
    for cov in ("diag", "full"):
        for kk in ks:
            g = GaussianMixture(n_components=kk, covariance_type=cov, n_init=args.gmm_n_init, random_state=child()).fit(P_gmm)
            gmm[(cov, kk)] = (float(g.bic(P_gmm)), g.predict(P_gmm))
    gmm_cov, gmm_k = min(gmm, key=lambda x: gmm[x][0])
    ari_wg = adjusted_rand_score(main_lab, gmm[(gmm_cov, k)][1])

    # parametric null
    corr = np.corrcoef(Zc, rowvar=False)
    null_gen = np.random.default_rng(child())
    null_best = []
    for _ in range(args.null_sims):
        S = null_gen.multivariate_normal(np.zeros(p), corr, size=n, method="eigh")
        res, bk = ward_search(S, ks, args.min_cluster_size)
        null_best.append(res[bk]["sil"] if bk else -1.0)
    null_best = np.array(null_best)
    obs_sil = search[k]["sil"]
    null_p = (int((null_best >= obs_sil).sum()) + 1) / (args.null_sims + 1)

    # ---- Final partition, relabel -------------------------------------------------------------------------
    sizes = np.bincount(main_lab, minlength=k)
    pc1 = scores[:, 0]
    order = sorted(range(k), key=lambda c: (-sizes[c], float(pc1[main_lab == c].mean())))
    remap = {old: new for new, old in enumerate(order)}
    lab = np.array([remap[x] for x in main_lab])
    labels_txt = [f"C{i + 1}" for i in range(k)]
    sil_s = search[k]["sil_samples"]
    # orig partitions by k with the same ordering for the chosen k
    orig = {kk: search[kk]["labels"] for kk in ks}
    orig[k] = lab

    # ---- Stability ----------------------------------------------------------------------------------------
    adm = [kk for kk in ks if search[kk]["admissible"]] or [k]
    jac = jaccard_bootstrap(Zc, adm, orig, args.n_boot, np.random.default_rng(child()))
    mean_jac_k = {kk: float(jac[kk].mean()) for kk in adm}
    boot_clusters = [{"label": labels_txt[i], "mean_jaccard": float(jac[k][:, i].mean()), "median_jaccard": float(np.median(jac[k][:, i])),
                      "share_ge_0_6": float((jac[k][:, i] >= 0.6).mean())} for i in range(k)]
    cons = consensus(Zc, k, args.n_consensus, args.consensus_fraction, np.random.default_rng(child()))
    ord_dogs = np.lexsort((np.arange(n), lab))
    cm = cons[np.ix_(ord_dogs, ord_dogs)]
    ol = lab[ord_dogs]
    off = ~np.eye(n, dtype=bool)
    same = (ol[:, None] == ol[None, :])
    cons_within = {labels_txt[i]: float(cm[(same & off) & (ol[:, None] == i)].mean()) for i in range(k)}
    cons_between = float(cm[~same].mean())
    iu = np.triu_indices(n, 1)
    pac = float(((cm[iu] > 0.1) & (cm[iu] < 0.9)).mean())

    # ---- Cluster summary ----------------------------------------------------------------------------------
    clusters = []
    overall = {}
    for j, c in enumerate(codes):
        v = Xm[:, j][~np.isnan(Xm[:, j])]
        overall[c] = {"median": r(np.median(v)), "q1": r(np.percentile(v, 25)), "q3": r(np.percentile(v, 75)), "n": int(len(v))}
    mad_zero = []
    mads = {}
    for j, c in enumerate(codes):
        v = Xm[:, j][~np.isnan(Xm[:, j])]
        mads[c] = 1.4826 * float(np.median(np.abs(v - np.median(v))))
        if mads[c] == 0:
            mad_zero.append(c)
    for i in range(k):
        m_in = lab == i
        vs = {}
        dist = []
        for j, c in enumerate(codes):
            col = Xm[:, j]
            a_ = col[m_in & ~np.isnan(col)]
            o_ = col[~m_in & ~np.isnan(col)]
            vs[c] = {"median": r(np.median(a_)) if len(a_) else None, "q1": r(np.percentile(a_, 25)) if len(a_) else None,
                     "q3": r(np.percentile(a_, 75)) if len(a_) else None, "n": int(len(a_))}
            if len(a_) and len(o_) and mads[c] > 0:
                sd = (np.median(a_) - np.median(o_)) / mads[c]
                if abs(sd) >= 0.8:
                    dist.append({"variable": c, "std_diff": r(sd), "direction": "higher" if sd > 0 else "lower"})
        dist.sort(key=lambda x: -abs(x["std_diff"]))
        clusters.append({"label": labels_txt[i], "n": int(m_in.sum()), "median_silhouette": r(np.median(sil_s[m_in])),
                         "variables": vs, "distinguishing": dist[:6]})

    # ---- Embedding ----------------------------------------------------------------------------------------
    umap_ok = False
    emb_method = "pca"
    emb = scores[:, :2]
    seed_umap = child()
    try:
        import umap  # noqa: WPS433
        emb = umap.UMAP(n_neighbors=args.umap_n_neighbors, min_dist=args.umap_min_dist, random_state=seed_umap).fit_transform(Zs)
        umap_ok, emb_method = True, "umap"
    except Exception:
        pass

    # ---- Cross-tabulations --------------------------------------------------------------------------------
    cgen = np.random.default_rng(child())
    kept_set = {s: i for i, s in enumerate(kept_subjects)}
    tests = []
    raw_p = []
    for cv in HELD_OUT:
        d = {s: t for s, t in texts.get(cv, {}).items() if s in kept_set}
        subs = sorted(d, key=lambda s: kept_set[s])
        cl = np.array([labels_txt[lab[kept_set[s]]] for s in subs])
        cls = np.array([d[s] for s in subs], dtype=object)
        merged = None
        if cv not in DESCRIPTIVE:
            lv, ct = np.unique(cls.astype(str), return_counts=True)
            rare = [l for l, c_ in zip(lv, ct) if c_ < args.min_level]
            if rare:
                if cv == "left_shift" and "L_shft" in lv:
                    cls = np.array(["left shift present" if x in rare + ["L_shft"] else x for x in cls], dtype=object)
                    merged = f"{', '.join(rare)} merged into L_shft (label 'left shift present')"
                else:
                    cls = np.array(["Other" if x in rare else x for x in cls], dtype=object)
                    merged = f"{', '.join(rare)} merged into Other"
        res = chi_square(cl, cls.astype(str), args.perm, cgen, args.ci_boot)
        parents = [x for x in (variables[cv].get("derived_from") or []) if x in codes] if cv in variables else []
        t = {"class_variable": cv, "n": res["n"], "levels_merged": merged, "parents_in_input": parents, "table": res["table"],
             "chi_square": r(res["chi2"]), "cramers_v": r(res["v"]), "v_ci95": [r(res["ci"][0]), r(res["ci"][1])],
             "p_value": r(res["p"], 6), "descriptive_only": cv in DESCRIPTIVE, "circular": cv not in DESCRIPTIVE}
        raw_p.append(res["p"])
        tests.append(t)
    padj = bh_adjust(raw_p)
    for t, q in zip(tests, padj):
        t["p_adjusted"] = r(q, 6)
        t["significant"] = bool(q < args.alpha and not t["descriptive_only"])
        t["p_adjusted"], t["significant"] = t["p_adjusted"], t["significant"]
    ordered = ["class_variable", "n", "levels_merged", "parents_in_input", "table", "chi_square", "cramers_v", "v_ci95", "p_value",
               "p_adjusted", "significant", "descriptive_only", "circular"]
    tests = [{key: t[key] for key in ordered} for t in tests]

    # ---- Sensitivity --------------------------------------------------------------------------------------
    main_load = {c: comp[:3, j] for j, c in enumerate(codes)}
    kept_pos = {i: t for t, i in enumerate(kept_idx)}
    main_transformed = {c: (c in M["transformed"]) for c in codes}

    def variant(name, dogs_rel, cols, fixed, mode, seed_v):
        if cols is None:
            raw_v = Xm[dogs_rel]
            cd = codes
        else:
            raw_v = Xall[kept_idx][dogs_rel][:, [cidx[c] for c in cols]]
            cd = cols
        mv = build_matrix(raw_v, cd, fixed, mode, seed_v, args.skew_threshold, args.clip_z, args.imputer_max_iter)
        sv, bk = ward_search(mv["Zc"], ks, args.min_cluster_size)
        if bk is None:
            bk = ks[0]
        cv_, _, _, _ = fit_pca(mv["Zs"])
        tk = []
        for pc in range(3):
            xs = [c for c in cd if c in main_load]
            a_ = np.array([cv_[pc, cd.index(c)] for c in xs])
            b_ = np.array([main_load[c][pc] for c in xs])
            tk.append(r(tucker(a_, b_)))
        ari = adjusted_rand_score(lab[dogs_rel], sv[bk]["labels"])
        return {"name": name, "n_subjects": int(len(dogs_rel)), "chosen_k": int(bk), "silhouette": r(sv[bk]["sil"]),
                "ari_vs_main": r(ari), "tucker_pc1_3": tk}

    all_dogs = np.arange(n)
    complete = np.where(~np.isnan(Xm).any(axis=1))[0]
    sens = [variant("S1_complete_case", complete, None, main_transformed, "none", 0),
            variant("S2_median_imputation", all_dogs, None, main_transformed, "median", 0)]
    cols3 = [c for c in codes if c not in ("respiratory_rate", "temperature_c")]
    sens.append(variant("S3_drop_respiratory_rate_temperature", all_dogs, cols3, {c: main_transformed[c] for c in cols3}, "iterative", child()))
    cols4 = codes + extra_codes
    sens.append(variant("S4_add_derived_back", all_dogs, cols4, dict(main_transformed), "iterative", child()))
    sens.append(variant("S5_no_log_transform", all_dogs, None, {c: False for c in codes}, "iterative", child()))
    s12 = sens[:2]
    robust = all(s["chosen_k"] == k or s["ari_vs_main"] >= 0.6 for s in s12)

    # ---- EXP01 comparison ---------------------------------------------------------------------------------
    exp01_lines = []
    ep = ROOT / "data" / "experiments" / "EXP01-DS05-pairwise.json"
    if ep.exists():
        e1 = json.loads(ep.read_text(encoding="utf-8"))
        vc = next((x["payload"] for x in e1["results"] if x["kind"] == "variable_clusters"), None)
        if vc:
            for ax in axes[:min(n_axes, 3)]:
                top = ax["top_variables"]
                hit = None
                for cl_ in vc["clusters"]:
                    if len(set(top) & set(cl_["members"])) >= 2:
                        hit = cl_
                        break
                if hit:
                    inside = [c for c in top if c in hit["members"]]
                    exp01_lines.append(f"{ax['axis']}: {names(inside, variables)} already form one correlation block in the pairwise experiment (EXP01, mean absolute rho {hit['mean_abs_rho']:.2f}), "
                                       "so this axis largely restates a strong pairwise correlation rather than adding a new relation.")
                else:
                    exp01_lines.append(f"{ax['axis']}: its leading variables ({names(top, variables)}) do not sit together in one EXP01 correlation block, so the axis combines relations not seen as a single pairwise block.")

    # ---- Assemble -----------------------------------------------------------------------------------------
    mean_jac_main = float(np.mean([b["mean_jaccard"] for b in boot_clusters]))
    k_search = []
    for kk in ks:
        k_search.append({"k": kk, "ward_silhouette": r(search[kk]["sil"]), "gmm_bic_diag": r(gmm[("diag", kk)][0]), "gmm_bic_full": r(gmm[("full", kk)][0]),
                         "min_cluster_size": search[kk]["min_size"], "admissible": search[kk]["admissible"],
                         "mean_jaccard": r(mean_jac_k[kk]) if kk in mean_jac_k else None})
    null_block = {"observed": r(obs_sil), "null_p95": r(np.percentile(null_best, 95)), "p_value": r(null_p, 6), "sims": args.null_sims}
    for cc in clusters:
        pass
    strongest = max((t for t in tests if not t["descriptive_only"]), key=lambda t: t["cramers_v"])
    summary = (f"{n} dogs, {p} admission variables: {n_axes} principal axes retained by parallel analysis. Ward clustering chose k = {k} "
               f"(mean silhouette {obs_sil:.3f}; null p {fmt_p(null_p)}); mean bootstrap Jaccard {mean_jac_main:.2f}; "
               f"strongest comparison with the authors' classes is {strongest['class_variable']} (Cramer's V {strongest['cramers_v']:.2f}, adjusted p {fmt_p(strongest['p_adjusted'])}; "
               "circular by construction). Exploratory phenotype groups, no outcome in this dataset.")

    cell_imp = int(M["miss"].sum())
    ctx = {"variables": variables, "args": args, "axes": axes, "n": n, "n_all": n_all, "p": p, "dataset": tidy["dataset"], "dropped": dropped,
           "transformed": M["transformed"], "cells_imputed": cell_imp, "n_axes": n_axes, "kaiser": kaiser, "axis_match": axis_match,
           "exp01_lines": exp01_lines, "k_search": k_search, "sil": obs_sil, "null": null_block, "boot_clusters": boot_clusters,
           "mean_jaccard_chosen": mean_jac_main, "k": k, "clusters": clusters, "cons_within": cons_within, "cons_between": cons_between,
           "pac": pac, "gmm_k": gmm_k, "gmm_cov": gmm_cov, "ari_ward_gmm": ari_wg, "tests": tests, "sens": sens, "robust": robust, "umap": umap_ok}

    experiment = {
        "code": args.code, "name": args.name,
        "description": args.description or ("Exploratory phenotype groupings of 148 dogs from admission variables, with stability and null tests; "
                                            "no outcome exists in this dataset and the groups are not subtypes of disease."),
        "method": "clustering", "dataset": args.dataset,
        "parameters": {"seed": args.seed, "skew_threshold": args.skew_threshold, "clip_z": args.clip_z,
                       "max_missing_subject": args.max_missing_subject, "max_missing_variable": args.max_missing_variable,
                       "imputation": "iterative_bayesian_ridge", "imputer_max_iter": args.imputer_max_iter, "pa_permutations": args.pa_permutations,
                       "k_min": args.k_min, "k_max": args.k_max, "min_cluster_size": args.min_cluster_size, "linkage": "ward",
                       "gmm_covariance_types": ["diag", "full"], "gmm_n_init": args.gmm_n_init, "null_sims": args.null_sims,
                       "n_boot": args.n_boot, "n_consensus": args.n_consensus, "consensus_fraction": args.consensus_fraction,
                       "min_level": args.min_level, "perm": args.perm, "ci_boot": args.ci_boot, "alpha": args.alpha,
                       "adjustment": "benjamini_hochberg", "umap": {"n_neighbors": args.umap_n_neighbors, "min_dist": args.umap_min_dist},
                       "held_out": HELD_OUT, "input_variables": codes},
        "script": "scripts/experiment_clustering.py",
        "script_version": hashlib.sha256(SCRIPT.read_bytes()).hexdigest()[:12],
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "n_subjects": n, "n_variables": p, "n_tests": len(tests), "summary": summary,
    }

    pca_payload = {"variables": codes, "n_axes": n_axes, "kaiser_count": kaiser,
                   "parallel_analysis": {"observed": [r(x) for x in eigv], "threshold_95": [r(x) for x in thr]},
                   "axes": axes, "transformed_variables": M["transformed"],
                   "scores": [{"subject_code": kept_subjects[i], "pc1": r(scores[i, 0]), "pc2": r(scores[i, 1]), "pc3": r(scores[i, 2])} for i in range(n)]}
    summary_payload = {"k": k, "clusters": clusters, "overall": overall, "mad_zero_variables": mad_zero,
                       "embedding": {"method": emb_method, "points": [{"subject_code": kept_subjects[i], "x": r(emb[i, 0]), "y": r(emb[i, 1]),
                                                                       "cluster": labels_txt[lab[i]]} for i in range(n)]}}
    stability_payload = {"k_search": k_search, "chosen_k": k, "gmm_best_k": gmm_k, "gmm_covariance": gmm_cov, "ari_ward_gmm": r(ari_wg),
                         "silhouette_null": null_block,
                         "bootstrap": {"clusters": [{**b, "mean_jaccard": r(b["mean_jaccard"]), "median_jaccard": r(b["median_jaccard"]),
                                                     "share_ge_0_6": r(b["share_ge_0_6"])} for b in boot_clusters], "n_boot": args.n_boot},
                         "consensus": {"order": [kept_subjects[i] for i in ord_dogs], "matrix": [[r(x) for x in row] for row in cm.tolist()],
                                       "mean_within": {a_: r(b_) for a_, b_ in cons_within.items()}, "mean_between": r(cons_between), "pac": r(pac)},
                         "sensitivity": sens, "robust": robust}
    run_notes = {"input_variables": [{"code": c, "name": variables[c]["name"], "unit": variables[c].get("unit"),
                                      "n_observed": int((~np.isnan(Xm[:, j])).sum()), "n_imputed": int(M["miss"][:, j].sum()),
                                      "transformed": c in M["transformed"], "clipped_cells": int(M["clipped"][j])} for j, c in enumerate(codes)],
                 "excluded_derived_from": DERIVED_BACK, "dropped_subjects": dropped, "dropped_variables": dropped_vars,
                 "not_tabulated": NOT_TABULATED,
                 "imputation": {"method": "IterativeImputer(BayesianRidge, max_iter=20, sample_posterior=False, initial_strategy=median), once on the standardised matrix before resampling; matrix re-standardised afterwards",
                                "cells_imputed": cell_imp},
                 "notes": ["Ordinal variables (lymph_node_score, habitus_score) treated as numeric.",
                           "Calculated variables (mcv, mch, mchc, wcc, arc, globulin) carry derived_from and are excluded from clustering; sensitivity S4 adds them back.",
                           "Clipping at +/-4 SD applies to the clustering matrix only; PCA and factor analysis use the unclipped standardised matrix.",
                           "Ward partition computed with scikit-learn AgglomerativeClustering; resampling uses scipy Ward linkage (same algorithm, ARI between them = %.3f)." % ward_vs_sk_ari,
                           "Variables with zero MAD cannot enter the 'distinguishing' list: " + (", ".join(mad_zero) if mad_zero else "none"),
                           "Chosen-k Jaccard and consensus use imputed-once data; stability is optimistic for the most-imputed variables."],
                 "environment": {"numpy": np.__version__, "scipy": scipy.__version__, "scikit_learn": sklearn.__version__, "umap_available": umap_ok},
                 "dataset": {"independent_source": tidy["dataset"].get("independent_source"), "licence": tidy["dataset"].get("licence")}}
    results = [
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 0, "payload": {"sections": build_interpretation(ctx)}},
        {"kind": "pca_axes", "title": "Principal axes, loadings and explained variance", "sort_order": 1, "payload": pca_payload},
        {"kind": "cluster_summary", "title": "Cluster profiles (medians, original units)", "sort_order": 2, "payload": summary_payload},
        {"kind": "cluster_stability", "title": "Choice of k, null test, bootstrap and consensus stability", "sort_order": 3, "payload": stability_payload},
        {"kind": "cluster_crosstabs", "title": "Clusters against the authors' classes and PCR", "sort_order": 4, "payload": {"tests": tests}},
        {"kind": "run_notes", "title": "Variables, missing data, dropped dogs and transformations", "sort_order": 5, "payload": run_notes},
    ]
    assignments = [{"subject_code": kept_subjects[i], "cluster_label": labels_txt[lab[i]], "score": r(sil_s[i])} for i in range(n)]

    # ---- Built-in checks ----------------------------------------------------------------------------------
    sk_sil = float(silhouette_samples(Zc, lab).mean())
    print(f"check evr_sum={ev_sum:.8f} sil_mean={obs_sil:.4f} sil_mean_rounded_scores={np.mean([a['score'] for a in assignments]):.4f} sklearn_sil={sk_sil:.4f} "
          f"min={sil_s.min():.3f} max={sil_s.max():.3f} ward_sklearn_vs_scipy_ARI={ward_vs_sk_ari:.3f}")

    if args.selftest:
        t = next(x for x in tests if x["class_variable"] == "anaemia_class")
        d = {s: v for s, v in texts["anaemia_class"].items() if s in kept_set}
        subs = sorted(d, key=lambda s: kept_set[s])
        cl = np.array([labels_txt[lab[kept_set[s]]] for s in subs])
        cls = np.array([d[s] for s in subs])
        g = np.random.default_rng(args.seed + 1)
        pv = [chi_square(cl, g.permutation(cls), args.perm, g)["p"] for _ in range(100)]
        print(f"selftest shuffled anaemia_class: p>0.05 in {sum(1 for x in pv if x > 0.05)} of 100; real V={t['cramers_v']}")
        return

    out = ROOT / "data" / "experiments" / f"{args.code}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"experiment": experiment, "associations": [], "cluster_assignments": assignments, "results": results},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    print(summary)
    print(f"-> {out.relative_to(ROOT)}")
    print(f"k={k} silhouette={obs_sil:.4f} null_p={null_p:.4f} n_axes={n_axes} kaiser={kaiser} gmm_k={gmm_k}({gmm_cov}) ARI_ward_gmm={ari_wg:.3f}")
    for b in boot_clusters:
        print(f"  {b['label']}: n={clusters[labels_txt.index(b['label'])]['n']} mean_jaccard={b['mean_jaccard']:.3f}")
    for t in tests:
        print(f"  {t['class_variable']:14s} V={t['cramers_v']:.3f} p_adj={t['p_adjusted']:.4f} desc={t['descriptive_only']}")
    for s in sens:
        print(f"  {s['name']}: n={s['n_subjects']} k={s['chosen_k']} sil={s['silhouette']} ARI={s['ari_vs_main']} tucker={s['tucker_pc1_3']}")
    print(f"robust={robust}")


if __name__ == "__main__":
    main()
