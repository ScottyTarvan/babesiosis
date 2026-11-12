"""K01 refutation checks: monocyte and macrophage activation vs severity (theme T02).

Reads the tidy files in /experiments/shared/tidy only. Seed 20261112. No predictive model.
Run: experiments/SV-META/env/py/Scripts/python.exe -I K01_checks.py
"""
import json
import itertools
from math import sqrt
from pathlib import Path

import numpy as np
from scipy import stats

SEED = 20261112
NBOOT, NPERM = 2000, 10000
TIDY = Path(__file__).resolve().parents[3] / "shared" / "tidy"
rng = np.random.default_rng(SEED)


def load(name):
    return json.loads((TIDY / name).read_text(encoding="utf-8"))


def outcome(name, label):
    return {r["dog_id"]: r["values"].get(label) for r in load(name)["records"]}


def cliff(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float((np.sign(x[:, None] - y[None, :])).mean())


def cliff_test(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = cliff(x, y)
    boots = [cliff(rng.choice(x, len(x)), rng.choice(y, len(y))) for _ in range(NBOOT)]
    pooled = np.concatenate([x, y])
    cnt = 0
    for _ in range(NPERM):
        rng.shuffle(pooled)
        if abs(cliff(pooled[:len(x)], pooled[len(x):])) >= abs(d) - 1e-12:
            cnt += 1
    return dict(d=round(d, 3), ci=[round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)],
                p=round((cnt + 1) / (NPERM + 1), 4), n=[len(x), len(y)])


def resid_rank(y, covs):
    """Residual of rank(y) after OLS on ranks of covariates (rank-based partial)."""
    ry = stats.rankdata(y)
    X = np.column_stack([np.ones(len(y))] + [stats.rankdata(c) for c in covs]) if covs else np.ones((len(y), 1))
    beta, *_ = np.linalg.lstsq(X, ry, rcond=None)
    return ry - X @ beta


def partial_spearman(x, y, covs):
    x, y = np.asarray(x, float), np.asarray(y, float)
    covs = [np.asarray(c, float) for c in covs]
    rx, ry = resid_rank(x, covs), resid_rank(y, covs)
    r = float(np.corrcoef(rx, ry)[0, 1])
    n, k = len(x), len(covs)
    t = r * sqrt((n - 2 - k) / max(1e-12, 1 - r * r))
    p_t = float(2 * stats.t.sf(abs(t), n - 2 - k))
    boots = []
    for _ in range(NBOOT):
        i = rng.integers(0, n, n)
        bx, by = resid_rank(x[i], [c[i] for c in covs]), resid_rank(y[i], [c[i] for c in covs])
        if bx.std() > 0 and by.std() > 0:
            boots.append(np.corrcoef(bx, by)[0, 1])
    return dict(r=round(r, 3), ci=[round(float(np.percentile(boots, 2.5)), 3), round(float(np.percentile(boots, 97.5)), 3)],
                p=float(f"{p_t:.3g}"), n=n, k=k)


def z_one_sided(p_two, positive=True):
    p1 = p_two / 2 if positive else 1 - p_two / 2
    return float(stats.norm.isf(p1))


def stouffer(zs):
    Z = sum(zs) / sqrt(len(zs))
    return dict(Z=round(Z, 3), p=float(f"{stats.norm.sf(Z):.3g}"))


out = {}

# ---------------- DS05 (SRC-F) ----------------
f = load("DS05.features.json")
hab = outcome("DS05.outcomes.json", "habitus_score")
rows = []
for r in f["records"]:
    v = r["values"]
    if v.get("pcr_b_rossi") != 1.0 or hab.get(r["dog_id"]) is None or v.get("mono") is None:
        continue
    rows.append(dict(v, dull=4 - hab[r["dog_id"]], dog=r["dog_id"]))
ds = {}
mono = np.array([r["mono"] for r in rows], float)
dull = np.array([r["dull"] for r in rows], float)
rho0 = stats.spearmanr(mono, dull)
ds["n"] = len(rows)
ds["mono_dull_rho"] = [round(float(rho0.statistic), 3), float(f"{rho0.pvalue:.3g}")]
ds["dullness_counts"] = {int(k): int((dull == k).sum()) for k in np.unique(dull)}
# other leukocytes and anaemia with dullness
for var in ["wbc", "neut_seg", "neut_band", "lymph", "eos", "hct", "illness_days", "plt", "temp_c"]:
    pr = [(r[var], r["dull"]) for r in rows if r.get(var) is not None]
    a = np.array(pr, float)
    s = stats.spearmanr(a[:, 0], a[:, 1])
    ds[f"{var}_dull_rho"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), len(pr)]
for var in ["wbc", "neut_seg", "neut_band", "hct", "illness_days"]:
    pr = [(r["mono"], r[var]) for r in rows if r.get(var) is not None]
    a = np.array(pr, float)
    s = stats.spearmanr(a[:, 0], a[:, 1])
    ds[f"mono_vs_{var}_rho"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}")]
# monocyte fraction of WBC
pr = np.array([(r["mono"] / r["wbc"], r["dull"]) for r in rows if r.get("wbc")], float)
s = stats.spearmanr(pr[:, 0], pr[:, 1])
ds["mono_fraction_dull_rho"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), len(pr)]
# partial correlations
sets = {"hct": ["hct"], "wbc": ["wbc"], "neut_seg": ["neut_seg"], "neut_band": ["neut_band"], "illness_days": ["illness_days"],
        "hct+wbc": ["hct", "wbc"], "hct+neut_seg+neut_band": ["hct", "neut_seg", "neut_band"],
        "all5: hct, wbc, neut_seg, neut_band, illness_days": ["hct", "wbc", "neut_seg", "neut_band", "illness_days"],
        "all5 + lymph + plt + temp_c": ["hct", "wbc", "neut_seg", "neut_band", "illness_days", "lymph", "plt", "temp_c"]}
partial = {}
for name, cv in sets.items():
    sub = [r for r in rows if all(r.get(c) is not None for c in cv)]
    partial[name] = partial_spearman([r["mono"] for r in sub], [r["dull"] for r in sub], [[r[c] for r in sub] for c in cv])
ds["partial_mono_dull"] = partial
# leukocytes other than monocytes after adjusting for monocytes (specificity check)
spec = {}
for var in ["wbc", "neut_seg", "neut_band", "lymph"]:
    sub = [r for r in rows if r.get(var) is not None]
    spec[f"{var}_dull_given_mono"] = partial_spearman([r[var] for r in sub], [r["dull"] for r in sub], [[r["mono"] for r in sub]])
ds["specificity_other_leukocytes_given_mono"] = spec
# exclude E. canis co-infection (monocytic ehrlichiosis)
sub = [r for r in rows if r.get("pcr_e_canis") != 1.0]
s = stats.spearmanr([r["mono"] for r in sub], [r["dull"] for r in sub])
ds["exclude_e_canis"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), len(sub)]
# three-class habitus: BAR (dull 0) vs others; dichotomies
for cut in (1, 2):
    hi = [r["mono"] for r in rows if r["dull"] >= cut]
    lo = [r["mono"] for r in rows if r["dull"] < cut]
    ds[f"cliff_mono_dull_ge{cut}"] = cliff_test(hi, lo)
# drop top 5% monocyte values (outlier sensitivity)
q95 = np.percentile(mono, 95)
keep = mono <= q95
s = stats.spearmanr(mono[keep], dull[keep])
ds["drop_top5pct_mono"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), int(keep.sum())]
out["DS05_SRC-F"] = ds

# ---------------- S-CB517 (SRC-A) ----------------
f = load("S-CB517.features.json")
died = outcome("S-CB517.outcomes.json", "died")
recs = [r for r in f["records"] if r["group"] == "infected" and died.get(r["dog_id"]) is not None]
a = {}
x = [r["values"]["mono"] for r in recs if died[r["dog_id"]] == 1 and r["values"].get("mono") is not None]
y = [r["values"]["mono"] for r in recs if died[r["dog_id"]] == 0 and r["values"].get("mono") is not None]
a["mono_died_vs_survived"] = cliff_test(x, y)
a["mono_median_died_survived"] = [float(np.median(x)), float(np.median(y))]
fx = [r["values"]["mono"] / r["values"]["wbc"] for r in recs if died[r["dog_id"]] == 1 and r["values"].get("wbc")]
fy = [r["values"]["mono"] / r["values"]["wbc"] for r in recs if died[r["dog_id"]] == 0 and r["values"].get("wbc")]
a["mono_fraction_died_vs_survived"] = cliff_test(fx, fy)
xw = [r["values"]["wbc"] for r in recs if died[r["dog_id"]] == 1]
yw = [r["values"]["wbc"] for r in recs if died[r["dog_id"]] == 0]
a["wbc_died_vs_survived"] = cliff_test(xw, yw)
xn = [r["values"]["neut_seg"] for r in recs if died[r["dog_id"]] == 1]
yn = [r["values"]["neut_seg"] for r in recs if died[r["dog_id"]] == 0]
a["neut_seg_died_vs_survived"] = cliff_test(xn, yn)
# monocyte residual after WBC ranks, compared by outcome
mv = np.array([r["values"]["mono"] for r in recs], float)
wv = np.array([r["values"]["wbc"] for r in recs], float)
lab = np.array([died[r["dog_id"]] for r in recs])
res = resid_rank(mv, [wv])
a["mono_resid_wbc_died_vs_survived"] = cliff_test(res[lab == 1], res[lab == 0])
# MCP-1 vs monocyte count among infected
pr = np.array([(r["values"]["mono"], r["values"]["mcp1"]) for r in recs if r["values"].get("mcp1") is not None], float)
s = stats.spearmanr(pr[:, 0], pr[:, 1])
a["mono_vs_mcp1_rho"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), len(pr)]
xm = [r["values"]["mcp1"] for r in recs if died[r["dog_id"]] == 1 and r["values"].get("mcp1") is not None]
ym = [r["values"]["mcp1"] for r in recs if died[r["dog_id"]] == 0 and r["values"].get("mcp1") is not None]
a["mcp1_died_vs_survived"] = cliff_test(xm, ym)
out["S-CB517_SRC-A"] = a

# ---------------- S-CB017 (SRC-D, B. canis) ----------------
f = load("S-CB017.features.json")
comp = outcome("S-CB017.outcomes.json", "complicated")
recs = [r for r in f["records"] if r["group"] == "infected" and r["timepoint"] == "day_1" and comp.get(r["dog_id"]) is not None]
d = {}
for var in ["mono", "wbc", "neut_seg", "neut_band", "mcp1", "mono_pct"]:
    x = [r["values"][var] for r in recs if comp[r["dog_id"]] == 1 and r["values"].get(var) is not None]
    y = [r["values"][var] for r in recs if comp[r["dog_id"]] == 0 and r["values"].get(var) is not None]
    d[f"{var}_complicated_vs_not"] = cliff_test(x, y)
mv = np.array([r["values"]["mono"] for r in recs], float)
wv = np.array([r["values"]["wbc"] for r in recs], float)
lab = np.array([comp[r["dog_id"]] for r in recs])
res = resid_rank(mv, [wv])
d["mono_resid_wbc_complicated_vs_not"] = cliff_test(res[lab == 1], res[lab == 0])
pr = np.array([(r["values"]["mono"], r["values"]["mcp1"]) for r in recs], float)
s = stats.spearmanr(pr[:, 0], pr[:, 1])
d["mono_vs_mcp1_rho_day1"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), len(pr)]
out["S-CB017_SRC-D"] = d

# ---------------- DS07 (SRC-C) CD14 vs haemoglobin beta ----------------
f = load("DS07.features.json")
comp = outcome("DS07.outcomes.json", "complicated")
CD14, HBB, HBA = "p_a0a1s7j0a8", "p_p60524", "p_j9nxl3"
recs = [r for r in f["records"] if r["group"] == "infected" and comp.get(r["dog_id"]) is not None
        and r["values"].get(CD14) is not None]
c = {}
x = [r["values"][CD14] for r in recs if comp[r["dog_id"]] == 1]
y = [r["values"][CD14] for r in recs if comp[r["dog_id"]] == 0]
c["cd14_unadjusted"] = cliff_test(x, y)
sub = [r for r in recs if r["values"].get(HBB) is not None]
cv = np.array([r["values"][CD14] for r in sub], float)
hv = np.array([r["values"][HBB] for r in sub], float)
lab = np.array([comp[r["dog_id"]] for r in sub])
s = stats.spearmanr(cv, hv)
c["cd14_vs_hbb_rho_infected"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), len(sub)]
for g in (0, 1):
    s = stats.spearmanr(cv[lab == g], hv[lab == g])
    c[f"cd14_vs_hbb_rho_within_complicated_{g}"] = [round(float(s.statistic), 3), float(f"{s.pvalue:.3g}"), int((lab == g).sum())]
res = resid_rank(cv, [hv])
c["cd14_resid_hbb"] = cliff_test(res[lab == 1], res[lab == 0])
# also partial point-biserial: rank(CD14) ~ complicated controlling rank(HBB)
pc = partial_spearman(cv, lab.astype(float), [hv])
c["cd14_complicated_partial_on_hbb"] = pc
# plex-centred CD14 (subtract plex median among all dogs in the plex, incl. controls)
allr = [r for r in f["records"] if r["values"].get(CD14) is not None]
plexmed = {}
for p in set(r["values"]["plex"] for r in allr):
    plexmed[p] = float(np.median([r["values"][CD14] for r in allr if r["values"]["plex"] == p]))
x = [r["values"][CD14] - plexmed[r["values"]["plex"]] for r in recs if comp[r["dog_id"]] == 1]
y = [r["values"][CD14] - plexmed[r["values"]["plex"]] for r in recs if comp[r["dog_id"]] == 0]
c["cd14_plex_centred"] = cliff_test(x, y)
xh = [r["values"][HBB] for r in sub if comp[r["dog_id"]] == 1]
yh = [r["values"][HBB] for r in sub if comp[r["dog_id"]] == 0]
c["hbb_complicated_vs_not"] = cliff_test(xh, yh)
out["DS07_SRC-C"] = c

# ---------------- combinations ----------------
# indicator two-sided p values from themes.csv (T02, T02s)
P = {"A_mono": 0.1738, "A_mcp1": 0.008699, "B_mono": 0.4, "B_mcp1": 0.2, "C_cd14": 0.07269, "F_mono": 0.0001,
     "D_mono": 0.2315, "D_mcp1": 0.0001}
comb = {}
comb["as_reported_ACBF"] = stouffer([z_one_sided(P[k]) for k in ["A_mono", "B_mono", "C_cd14", "F_mono"]])
comb["drop_F_(hypothesis-generating source)"] = stouffer([z_one_sided(P[k]) for k in ["A_mono", "B_mono", "C_cd14"]])
comb["drop_F_and_C_(published CB112)"] = stouffer([z_one_sided(P[k]) for k in ["A_mono", "B_mono"]])
comb["drop_F_and_B_(dose not severity, n 5)"] = stouffer([z_one_sided(P[k]) for k in ["A_mono", "C_cd14"]])
comb["monocyte_count_only_A_B_F"] = stouffer([z_one_sided(P[k]) for k in ["A_mono", "B_mono", "F_mono"]])
comb["monocyte_count_only_A_B (no F)"] = stouffer([z_one_sided(P[k]) for k in ["A_mono", "B_mono"]])
# F with fully adjusted partial correlation
pf = out["DS05_SRC-F"]["partial_mono_dull"]["all5: hct, wbc, neut_seg, neut_band, illness_days"]
comb["F_replaced_by_partial_all5"] = stouffer([z_one_sided(P["A_mono"]), z_one_sided(P["B_mono"]), z_one_sided(P["C_cd14"]),
                                              z_one_sided(max(pf["p"], 1e-12), pf["r"] > 0)])
pcd = out["DS07_SRC-C"]["cd14_resid_hbb"]
comb["C_replaced_by_cd14_resid_hbb"] = stouffer([z_one_sided(P["A_mono"]), z_one_sided(P["B_mono"]),
                                                z_one_sided(pcd["p"], pcd["d"] > 0), z_one_sided(P["F_mono"])])
# all marker choices per source (A: mono or MCP-1; B: mono or MCP-1; C: CD14; F: mono)
grid = []
for a_, b_ in itertools.product(["A_mono", "A_mcp1"], ["B_mono", "B_mcp1"]):
    grid.append((a_, b_, stouffer([z_one_sided(P[a_]), z_one_sided(P[b_]), z_one_sided(P["C_cd14"]), z_one_sided(P["F_mono"])])["Z"]))
comb["marker_choice_grid_with_F"] = grid
grid2 = []
for a_, b_ in itertools.product(["A_mono", "A_mcp1"], ["B_mono", "B_mcp1"]):
    grid2.append((a_, b_, stouffer([z_one_sided(P[a_]), z_one_sided(P[b_]), z_one_sided(P["C_cd14"])])["Z"]))
comb["marker_choice_grid_without_F"] = grid2
# Bonferroni over 8 themes and the 2 marker variants (16 looks), for drop-F set
comb["note"] = "one-sided Stouffer, equal weights, two-sided indicator p halved; F p is a permutation floor (1e-4)"
out["combinations"] = comb

print(json.dumps(out, indent=1))
