"""Pairwise association experiment over a tidy dataset (data/tidy/<DS>.json).

Tests every pair of variables in the default test set (include_default) with a test that fits
the pair's types, gets p values by permutation (no distributional assumptions, no scipy), and
adjusts them with Benjamini-Hochberg across the whole run:

  numeric / ordinal  x  numeric / ordinal   Spearman rho
  categorical        x  numeric / ordinal   Kruskal-Wallis H (Mann-Whitney when two groups); effect size eta squared
  categorical        x  categorical         chi-square on the contingency table; effect size Cramer's V

Rare categorical levels (fewer than --min-level subjects) are merged into "Other" or dropped,
pairs with fewer than --min-n complete cases are skipped, and a pair where one variable is an
arithmetic function of the other (variable.derived_from) is flagged trivial so it does not
count as a finding.

Also writes, as result payloads: the Spearman matrix of the numeric variables, average-linkage
clusters of variables on 1 - |rho| (which parameters move together), and the top non-trivial
associations.

Output: data/experiments/<code>.json, read by the console ExperimentLoader.

Not stdlib-only: needs numpy. Run with .venv/Scripts/python.exe -I (or any Python with numpy):
    .venv/Scripts/python.exe -I scripts/experiment_pairwise.py --dataset DS05 --code EXP01-DS05-pairwise \
        --name "Admission phenotype associations, BET cohort" [--permutations 5000] [--seed 20261105]
        [--min-n 20] [--min-level 8] [--alpha 0.05] [--include-derived] [--include a,b] [--exclude a,b]
"""
import argparse
import datetime as dt
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()


# ---------------------------------------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------------------------------------

def rankdata(x):
    """Average ranks (1-based) with ties, like scipy.stats.rankdata."""
    uniq, inv, counts = np.unique(x, return_inverse=True, return_counts=True)
    cum = np.cumsum(counts)
    first = cum - counts + 1
    return ((first + cum) / 2.0)[inv]


def bh_adjust(p):
    """Benjamini-Hochberg adjusted p values."""
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
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), nd)


# ---------------------------------------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------------------------------------

def spearman(x, y, B, rng):
    rx, ry = rankdata(x), rankdata(y)
    if rx.std() == 0 or ry.std() == 0:
        return None
    zx = (rx - rx.mean()) / rx.std()
    zy = (ry - ry.mean()) / ry.std()
    n = len(x)
    rho = float((zx * zy).mean())
    Y = rng.permuted(np.tile(zy, (B, 1)), axis=1)
    rho_perm = Y @ zx / n
    p = perm_p(abs(rho), np.abs(rho_perm))
    return {"test": "spearman", "estimate": rho, "estimate_label": "rho", "n": n, "p_value": p,
            "direction": "positive" if rho > 0 else "negative", "detail": {"statistic": rho}}


def kruskal(groups, y, B, rng):
    """groups: array of level labels (str); y: numeric."""
    levels, codes = np.unique(groups, return_inverse=True)
    k = len(levels)
    n = len(y)
    if k < 2:
        return None
    G = np.zeros((n, k))
    G[np.arange(n), codes] = 1.0
    nj = G.sum(axis=0)
    rk = rankdata(y)
    _, tcounts = np.unique(y, return_counts=True)
    tie = 1.0 - float(((tcounts ** 3 - tcounts).sum()) / (n ** 3 - n)) if n > 1 else 1.0

    def H(R):
        S = R @ G
        return 12.0 / (n * (n + 1)) * (S ** 2 / nj).sum(axis=-1) - 3.0 * (n + 1)

    h = float(H(rk))
    h_corr = h / tie if tie > 0 else h
    Rp = rng.permuted(np.tile(rk, (B, 1)), axis=1)
    p = perm_p(h, H(Rp))
    eta2 = max(0.0, (h_corr - k + 1) / (n - k)) if n > k else 0.0
    medians = {str(l): float(np.median(y[codes == i])) for i, l in enumerate(levels)}
    sizes = {str(l): int(nj[i]) for i, l in enumerate(levels)}
    top = max(medians, key=medians.get)
    return {"test": "kruskal_wallis" if k > 2 else "mann_whitney", "estimate": eta2, "estimate_label": "eta_squared",
            "n": n, "p_value": p, "direction": f"higher in {top}",
            "detail": {"statistic": h_corr, "groups": sizes, "medians": medians}}


def chi_square(a, b, B, rng):
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
    resid = (O - E) / np.sqrt(E)
    i, j = np.unravel_index(np.argmax(resid), resid.shape)
    table = {str(la[x]): {str(lb[y]): int(O[x, y]) for y in range(kb)} for x in range(ka)}
    return {"test": "chi_square", "estimate": V, "estimate_label": "cramers_v", "n": n, "p_value": p,
            "direction": f"{la[i]} with {lb[j]} more often than expected",
            "detail": {"statistic": chi2, "table": table}}


# ---------------------------------------------------------------------------------------------------------
# Variable clustering (average linkage on 1 - |rho|)
# ---------------------------------------------------------------------------------------------------------

def cluster_variables(codes, rho, cut):
    m = len(codes)
    D = 1.0 - np.abs(np.nan_to_num(rho, nan=0.0))
    np.fill_diagonal(D, 0.0)
    clusters = [[i] for i in range(m)]
    merges = []
    while len(clusters) > 1:
        best, bi, bj = None, -1, -1
        for i in range(len(clusters)):
            for j in range(i + 1, len(clusters)):
                d = float(np.mean([D[a, b] for a in clusters[i] for b in clusters[j]]))
                if best is None or d < best:
                    best, bi, bj = d, i, j
        if best > cut:
            break
        merges.append({"members": [codes[x] for x in clusters[bi] + clusters[bj]], "distance": round(best, 4)})
        clusters[bi] = clusters[bi] + clusters[bj]
        del clusters[bj]
    out = []
    for c in clusters:
        if len(c) < 2:
            continue
        within = [abs(rho[a, b]) for a in c for b in c if a < b and not np.isnan(rho[a, b])]
        out.append({"members": [codes[x] for x in c], "mean_abs_rho": round(float(np.mean(within)), 4) if within else None})
    out.sort(key=lambda c: -(c["mean_abs_rho"] or 0))
    singletons = [codes[c[0]] for c in clusters if len(c) == 1]
    return out, singletons, merges


# ---------------------------------------------------------------------------------------------------------
# Interpretation note (templated from the results, so every run carries one)
# ---------------------------------------------------------------------------------------------------------

def fmt_p(p):
    return "< 0.001" if p < 0.001 else f"= {p:.3f}"


def sentence(x, variables):
    """One plain sentence for an association row."""
    a, b = variables[x["variable_a"]], variables[x["variable_b"]]
    na, nb = a["name"], b["name"]
    tail = f" (n = {x['n']}, adjusted p {fmt_p(x['p_adjusted'])})"
    if x["test"] == "spearman":
        verb = "rises with" if x["estimate"] > 0 else "falls as"
        verb2 = "" if x["estimate"] > 0 else " rises"
        return f"{na} {verb} {nb}{verb2} (Spearman rho {x['estimate']:+.2f}){tail}."
    if x["test"] in ("mann_whitney", "kruskal_wallis"):
        cat, num = (a, b) if a["data_type"] == "C" else (b, a)
        level = x["direction"].replace("higher in ", "")
        meds = x["detail"].get("medians", {})
        parts = ", ".join(f"{k}: {v:g}" for k, v in meds.items())
        return (f"{num['name']} differs by {cat['name'].lower()} and is highest where {cat['name'].lower()} is "
                f"{level} (medians {parts}; eta squared {x['estimate']:.2f}){tail}.")
    return f"{na} and {nb} are not independent: {x['direction']} (Cramer's V {x['estimate']:.2f}){tail}."


def interpretation(rows, findings, clusters, singletons, variables, tested, num, cat, n_subj, args, dataset):
    by_domain = {}
    for c in tested:
        by_domain.setdefault(variables[c].get("domain") or "other", []).append(variables[c]["name"])
    sections = []

    # 1. What was tested
    domains = "; ".join(f"{d}: {', '.join(names)}" for d, names in by_domain.items())
    sections.append({"heading": "What was tested", "paragraphs": [
        f"{n_subj} subjects from dataset {dataset['code']} ({dataset.get('title', '').split(' (')[0]}). "
        f"{len(tested)} variables were tested in every pairing: {len(num)} numeric or ordinal and {len(cat)} categorical, grouped by domain as {domains}.",
        f"Each pair got a test that fits its types: Spearman rank correlation for two numeric variables, a Kruskal-Wallis or Mann-Whitney test "
        f"with an eta-squared effect size for a category against a number, and a chi-square test with Cramer's V for two categories. "
        f"P values come from {args.permutations:,} permutations rather than a distributional formula, and all {len(rows)} tests were adjusted "
        f"together with the Benjamini-Hochberg procedure at a false discovery rate of {args.alpha:g}. The smallest p value a permutation test "
        f"can report is about 1 in {args.permutations:,}, so the strongest associations share one floor value and are not ranked among themselves by p.",
        "The heatmap shows the Spearman correlation between every pair of numeric variables: warm cells are positive, cool cells negative, "
        "and the neutral mid-tone is no correlation. Pairs where one variable is an arithmetic function of the other (for example a calculated index "
        "and the measurements it is calculated from) are marked trivial and excluded from the findings below, because they must correlate.",
    ]})

    # 2. Structure: clusters
    paras = []
    if clusters:
        paras.append(f"Average-linkage clustering on 1 minus the absolute correlation, cut at |rho| of {1 - args.cluster_cut:.1f}, groups the numeric variables "
                     f"into {len(clusters)} blocks that move together. Read these as descriptive groupings of measurements, not as patient subtypes.")
        for c in clusters:
            names = [variables[m]["name"] for m in c["members"]]
            parents = {p for m in c["members"] for p in (variables[m].get("derived_from") or [])}
            arith = " Part of this block is arithmetic: some members are calculated from others." if parents & set(c["members"]) else ""
            paras.append(f"{', '.join(names[:-1])} and {names[-1]} (mean |rho| {c['mean_abs_rho']:.2f}).{arith}")
        if singletons:
            paras.append("Not in any block at this cut: " + ", ".join(variables[s]["name"] for s in singletons) + ".")
    else:
        paras.append("No block of numeric variables reached the clustering cut, so the measured parameters vary largely independently of one another.")
    sections.append({"heading": "How the parameters group", "paragraphs": paras})

    # 3. Cross-domain findings
    def dom(code):
        return variables[code].get("domain") or "other"
    cross = [x for x in findings if dom(x["variable_a"]) != dom(x["variable_b"])]
    within = [x for x in findings if dom(x["variable_a"]) == dom(x["variable_b"])]
    paras = [f"{len(findings)} non-trivial pairs stay significant after adjustment: {len(cross)} link different domains and {len(within)} sit within one domain. "
             "The cross-domain pairs are the ones most likely to say something new, because within-domain correlations among laboratory values are largely expected."]
    for x in cross[:14]:
        paras.append(sentence(x, variables))
    if len(cross) > 14:
        paras.append(f"A further {len(cross) - 14} cross-domain pairs are in the findings table, ordered by adjusted p and effect size.")
    if not cross:
        paras.append("No association between variables of different domains survived adjustment.")
    sections.append({"heading": "Strongest associations across domains", "paragraphs": paras})

    # 4. Signalment and host factors
    host = [c for c in tested if dom(c) in ("signalment", "time")]
    paras = []
    for h in host:
        hits = [x for x in findings if h in (x["variable_a"], x["variable_b"])]
        if hits:
            others = ", ".join(variables[x["variable_b"] if x["variable_a"] == h else x["variable_a"]]["name"] for x in hits[:8])
            more = f" and {len(hits) - 8} more" if len(hits) > 8 else ""
            paras.append(f"{variables[h]['name']}: {len(hits)} associations survive adjustment, with {others}{more}. The strongest is: " + sentence(hits[0], variables))
        else:
            paras.append(f"{variables[h]['name']}: no association survived adjustment. With {n_subj} subjects this excludes large effects, not small ones.")
    if paras:
        sections.append({"heading": "Signalment, season and other host factors", "paragraphs": paras})

    # 5. Quiet variables
    quiet = [variables[c]["name"] for c in tested if dom(c) not in ("signalment", "time")
             and not any(c in (x["variable_a"], x["variable_b"]) for x in findings)]
    if quiet:
        sections.append({"heading": "Variables with no surviving association", "paragraphs": [
            ", ".join(quiet) + ". Each of these was tested against every other variable and nothing passed the false discovery threshold. "
            "That is informative in itself when the variable was expected to track others, and unremarkable for rare or near-constant variables."]})

    # 6. Caveats
    caveats = [
        "Associations, not causes: every value was taken at one admission, so the direction of any relationship is not identifiable from these data.",
        f"{n_subj} subjects against {len(tested)} variables is a small sample for {len(rows)} tests. The false discovery rate controls the expected share of false positives among the reported findings, "
        "not the chance that any one finding is real, and effect sizes near the threshold should be treated as leads.",
    ]
    if not any(s.get("outcome_label") for s in dataset.get("subjects", [])):
        caveats.append("The dataset carries no outcome or severity label, so no finding here can be read as prognostic. Any severity reading relies on clinical proxies such as habitus or anaemia grade.")
    if args.min_level:
        caveats.append(f"Categorical levels with fewer than {args.min_level} subjects were merged into Other or dropped, so rare breeds, complaints or groups are not tested on their own.")
    caveats.append("Variable clusters are a summary of the correlation matrix. They describe which measurements co-vary and should not be called phenotypes or subtypes without an independent cohort.")
    sections.append({"heading": "How far to trust this", "paragraphs": caveats})
    return sections


# ---------------------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--code", required=True, help="experiment code, e.g. EXP01-DS05-pairwise")
    ap.add_argument("--name", required=True)
    ap.add_argument("--description", default=None)
    ap.add_argument("--permutations", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=20261105)
    ap.add_argument("--min-n", type=int, default=20, help="minimum complete cases per pair")
    ap.add_argument("--min-level", type=int, default=8, help="minimum subjects per categorical level")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--cluster-cut", type=float, default=0.6, help="average-linkage cut on 1-|rho| (0.6 = |rho| >= 0.4)")
    ap.add_argument("--include-derived", action="store_true", help="also test the derived classes (derived = true)")
    ap.add_argument("--include", default="", help="comma-separated variable codes to add to the test set")
    ap.add_argument("--exclude", default="", help="comma-separated variable codes to leave out")
    args = ap.parse_args()

    tidy = json.loads((ROOT / "data" / "tidy" / f"{args.dataset}.json").read_text(encoding="utf-8"))
    variables = {v["code"]: v for v in tidy["variables"]}
    subjects = [s["code"] for s in tidy["subjects"]]
    idx = {s: i for i, s in enumerate(subjects)}
    n_subj = len(subjects)

    include = {c.strip() for c in args.include.split(",") if c.strip()}
    exclude = {c.strip() for c in args.exclude.split(",") if c.strip()}
    selected = []
    for v in tidy["variables"]:
        if v["data_type"] not in ("N", "O", "C") or v["code"] in exclude:
            continue
        if v["include_default"] or v["code"] in include or (args.include_derived and v["derived"]):
            selected.append(v["code"])

    # Column arrays
    num = {}
    cat = {}
    for code in selected:
        if variables[code]["data_type"] in ("N", "O"):
            num[code] = np.full(n_subj, np.nan)
        else:
            cat[code] = np.array([None] * n_subj, dtype=object)
    for o in tidy["observations"]:
        c = o["variable"]
        if c in num and o["value_num"] is not None:
            num[c][idx[o["subject"]]] = o["value_num"]
        elif c in cat and o["value_text"] is not None:
            cat[c][idx[o["subject"]]] = o["value_text"]

    # Categorical level handling
    dropped = []
    level_notes = {}
    for code in list(cat):
        col = cat[code]
        present = col[col != None]  # noqa: E711
        levels, counts = np.unique(present.astype(str), return_counts=True)
        rare = [l for l, k in zip(levels, counts) if k < args.min_level]
        if rare:
            merged = np.where(np.isin(col.astype(str), rare), "Other", col)
            other_n = int(np.count_nonzero(merged.astype(str) == "Other"))
            if other_n >= args.min_level and len(rare) > 1:
                cat[code] = merged
                level_notes[code] = f"levels {', '.join(rare)} merged into Other ({other_n})"
            else:
                cat[code] = np.where(np.isin(col.astype(str), rare), None, col)
                level_notes[code] = f"levels {', '.join(rare)} dropped ({other_n} subjects set missing)"
        col = cat[code]
        present = col[col != None]  # noqa: E711
        if len(np.unique(present.astype(str))) < 2 or len(present) < args.min_n:
            dropped.append({"variable": code, "reason": "fewer than two usable levels"})
            del cat[code]
    for code in list(num):
        col = num[code]
        ok = col[~np.isnan(col)]
        if len(ok) < args.min_n or ok.std() == 0:
            dropped.append({"variable": code, "reason": "too few values or no variance"})
            del num[code]

    tested = list(num) + list(cat)
    rng = np.random.default_rng(args.seed)
    B = args.permutations
    rows = []
    skipped = []

    def parents(code):
        return set(variables[code].get("derived_from") or [])

    for a, b in itertools.combinations(tested, 2):
        a_num, b_num = a in num, b in num
        if a_num and b_num:
            mask = ~np.isnan(num[a]) & ~np.isnan(num[b])
            if mask.sum() < args.min_n:
                skipped.append({"a": a, "b": b, "n": int(mask.sum())})
                continue
            res = spearman(num[a][mask], num[b][mask], B, rng)
        elif a_num != b_num:
            c, q = (b, a) if a_num else (a, b)
            mask = (cat[c] != None) & ~np.isnan(num[q])  # noqa: E711
            if mask.sum() < args.min_n:
                skipped.append({"a": a, "b": b, "n": int(mask.sum())})
                continue
            res = kruskal(cat[c][mask].astype(str), num[q][mask], B, rng)
        else:
            mask = (cat[a] != None) & (cat[b] != None)  # noqa: E711
            if mask.sum() < args.min_n:
                skipped.append({"a": a, "b": b, "n": int(mask.sum())})
                continue
            res = chi_square(cat[a][mask].astype(str), cat[b][mask].astype(str), B, rng)
        if res is None:
            skipped.append({"a": a, "b": b, "n": int(mask.sum()), "reason": "no variance in complete cases"})
            continue
        res["variable_a"], res["variable_b"] = a, b
        res["trivial"] = b in parents(a) or a in parents(b)
        rows.append(res)

    padj = bh_adjust([x["p_value"] for x in rows])
    for x, q in zip(rows, padj):
        x["p_adjusted"] = float(q)
        x["significant"] = bool(q < args.alpha)

    # Spearman matrix and variable clusters over the numeric/ordinal set
    ncodes = list(num)
    m = len(ncodes)
    rho = np.full((m, m), np.nan)
    nn = np.zeros((m, m), dtype=int)
    lookup = {(x["variable_a"], x["variable_b"]): x for x in rows}
    for i in range(m):
        rho[i, i] = 1.0
        nn[i, i] = int((~np.isnan(num[ncodes[i]])).sum())
        for j in range(i + 1, m):
            x = lookup.get((ncodes[i], ncodes[j])) or lookup.get((ncodes[j], ncodes[i]))
            if x:
                rho[i, j] = rho[j, i] = x["estimate"]
                nn[i, j] = nn[j, i] = x["n"]
    clusters, singletons, merges = cluster_variables(ncodes, rho, args.cluster_cut)

    findings = [x for x in rows if x["significant"] and not x["trivial"]]
    findings.sort(key=lambda x: (x["p_adjusted"], -abs(x["estimate"] or 0)))
    n_sig = sum(1 for x in rows if x["significant"])
    n_triv = sum(1 for x in rows if x["significant"] and x["trivial"])
    summary = (f"{len(rows)} pairs tested among {len(tested)} variables in {n_subj} subjects "
               f"({len(num)} numeric/ordinal, {len(cat)} categorical). {n_sig} pairs have BH-adjusted p < {args.alpha}, "
               f"of which {n_triv} are arithmetic (trivial) and {len(findings)} are findings to look at. "
               f"{len(clusters)} variable clusters at |rho| >= {1 - args.cluster_cut:.1f}.")

    def clean(x):
        out = {k: x[k] for k in ("variable_a", "variable_b", "test", "estimate_label", "n", "direction", "trivial", "significant")}
        out["estimate"] = r(x["estimate"])
        out["p_value"] = r(x["p_value"], 6)
        out["p_adjusted"] = r(x["p_adjusted"], 6)
        out["detail"] = x["detail"]
        return out

    experiment = {
        "code": args.code,
        "name": args.name,
        "description": args.description or (
            "Every pair of admission variables tested with a type-appropriate rank or contingency test, permutation p values, "
            "Benjamini-Hochberg adjustment across the run. Exploratory: associations, not causes, and no severity label exists in this dataset."),
        "method": "pairwise_association",
        "dataset": args.dataset,
        "parameters": {"permutations": B, "seed": args.seed, "min_n": args.min_n, "min_level": args.min_level, "alpha": args.alpha,
                       "cluster_cut": args.cluster_cut, "include_derived": args.include_derived,
                       "include": sorted(include), "exclude": sorted(exclude), "adjustment": "benjamini_hochberg"},
        "script": "scripts/experiment_pairwise.py",
        "script_version": hashlib.sha256(SCRIPT.read_bytes()).hexdigest()[:12],
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "n_subjects": n_subj,
        "n_variables": len(tested),
        "n_tests": len(rows),
        "summary": summary,
    }
    results = [
        {"kind": "spearman_matrix", "title": "Spearman correlation matrix (numeric and ordinal variables)", "sort_order": 1,
         "payload": {"variables": ncodes, "rho": [[r(v) for v in row] for row in rho.tolist()], "n": nn.tolist()}},
        {"kind": "variable_clusters", "title": f"Variables that move together (average linkage, |rho| >= {1 - args.cluster_cut:.1f})", "sort_order": 2,
         "payload": {"clusters": clusters, "singletons": singletons, "merges": merges}},
        {"kind": "top_associations", "title": "Strongest non-trivial associations (BH-adjusted)", "sort_order": 3,
         "payload": {"associations": [clean(x) for x in findings[:40]]}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 0,
         "payload": {"sections": interpretation(rows, findings, clusters, singletons, variables, tested, num, cat, n_subj, args,
                                                {**tidy["dataset"], "subjects": tidy["subjects"]})}},
        {"kind": "run_notes", "title": "Variables tested, levels merged, pairs skipped", "sort_order": 4,
         "payload": {"tested": [{"code": c, "name": variables[c]["name"], "domain": variables[c].get("domain"),
                                 "type": "numeric" if c in num else "categorical",
                                 "n": int((~np.isnan(num[c])).sum()) if c in num else int((cat[c] != None).sum()),  # noqa: E711
                                 "levels": (dict(zip(*[a.tolist() for a in np.unique(cat[c][cat[c] != None].astype(str), return_counts=True)]))  # noqa: E711
                                            if c in cat else None)} for c in tested],
                     "level_handling": level_notes, "dropped": dropped, "skipped_pairs": skipped}},
    ]

    out = ROOT / "data" / "experiments" / f"{args.code}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"experiment": experiment, "associations": [clean(x) for x in rows],
                               "cluster_assignments": [], "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")

    print(summary)
    print(f"-> {out.relative_to(ROOT)}")
    print("\nTop findings:")
    for x in findings[:25]:
        est = f"{x['estimate_label']}={x['estimate']:.3f}"
        print(f"  {x['variable_a']:22s} x {x['variable_b']:22s} {x['test']:14s} {est:22s} n={x['n']:3d} p_adj={x['p_adjusted']:.4f}  {x['direction']}")
    print("\nVariable clusters:")
    for c in clusters:
        print(f"  |rho| {c['mean_abs_rho']}: {', '.join(c['members'])}")


if __name__ == "__main__":
    main()
