"""K02 refutation checks: SV-09 DS05 axis 2 (inflammation vs regeneration) and habitus. Seed 20261112."""
import json, math, csv, os
import numpy as np
from scipy.stats import rankdata, spearmanr

ROOT = r"C:\Workspaces\Babesiosis\experiments"
TIDY = os.path.join(ROOT, "shared", "tidy")
rng = np.random.default_rng(20261112)
NB, NP = 2000, 5000
LOG05 = {"arc", "neut_seg", "neut_band", "lymph", "mono", "plt", "retic_pct", "wbc", "eos"}
LOG1 = {"nrbc_per100wbc"}

def tr(k, x):
    if x is None: return None
    if k in LOG05: return math.log(x + 0.05)
    if k in LOG1: return math.log(x + 1.0)
    return float(x)

feat = json.load(open(os.path.join(TIDY, "DS05.features.json"), encoding="utf-8"))
outc = {r["dog_id"]: r["values"] for r in json.load(open(os.path.join(TIDY, "DS05.outcomes.json"), encoding="utf-8"))["records"]}
sc = {}
with open(os.path.join(ROOT, "SV-09", "out", "ds05_scores.csv")) as f:
    for row in csv.DictReader(f): sc[row["dog_id"]] = (float(row["pc1"]), float(row["pc2"]))

V = {}
for r in feat["records"]:
    V[r["dog_id"]] = r["values"]
ids = [i for i in sc if outc.get(i, {}).get("habitus_score") is not None]
print("n with score and habitus", len(ids), "of", len(sc))

def col(k, sub=None):
    s = ids if sub is None else sub
    return np.array([np.nan if V[i].get(k) is None else tr(k, V[i][k]) for i in s], float)

def base(sub):
    hct = np.array([V[i]["hct"] for i in sub]); ill = np.array([math.log(V[i]["illness_days"] + 1) for i in sub])
    return np.column_stack([hct, hct ** 2, ill])

def rres(y, D):
    y = rankdata(y); D1 = np.column_stack([np.ones(len(y)), D])
    b, *_ = np.linalg.lstsq(D1, y, rcond=None); return y - D1 @ b

def zres(y, D):  # OLS residual on raw (transformed) scale, standardised
    D1 = np.column_stack([np.ones(len(y)), D]); b, *_ = np.linalg.lstsq(D1, y, rcond=None); e = y - D1 @ b
    return (e - e.mean()) / e.std(ddof=1)

def prho(x, y, D, boot=True, perm=True):
    ok = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(D).any(1)
    x, y, D = x[ok], y[ok], D[ok]; n = len(x)
    a, b = rres(x, D), rres(y, D); obs = float(np.corrcoef(a, b)[0, 1])
    p = None
    if perm:
        cnt = sum(abs(np.corrcoef(a, rng.permutation(b))[0, 1]) >= abs(obs) - 1e-12 for _ in range(NP)); p = (cnt + 1) / (NP + 1)
    lo = hi = None
    if boot:
        bs = []
        for _ in range(NB):
            ix = rng.integers(0, n, n); aa, bb = rres(x[ix], D[ix]), rres(y[ix], D[ix])
            if aa.std() > 0 and bb.std() > 0: bs.append(np.corrcoef(aa, bb)[0, 1])
        lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"n": n, "rho": round(obs, 3), "ci": [None if lo is None else round(float(lo), 3), None if hi is None else round(float(hi), 3)], "p": None if p is None else round(p, 4)}

hab = np.array([outc[i]["habitus_score"] for i in ids], float)
pc2 = np.array([sc[i][1] for i in ids]); pc1 = np.array([sc[i][0] for i in ids])
B = base(ids)
R = {}
R["reproduce_pc2"] = prho(pc2, hab, B)
R["pc1"] = prho(pc1, hab, B, boot=False)
band, mono, seg, lym, wbc = col("neut_band"), col("mono"), col("neut_seg"), col("lymph"), col("wbc")
R["pc2_ctrl_band"] = prho(pc2, hab, np.column_stack([B, band]))
R["pc2_ctrl_band_mono"] = prho(pc2, hab, np.column_stack([B, band, mono]))
R["pc2_ctrl_band_mono_seg_lymph"] = prho(pc2, hab, np.column_stack([B, band, mono, seg, lym]))
R["pc2_ctrl_wbc"] = prho(pc2, hab, np.column_stack([B, wbc]))
# single variables at given hct and illness days
for k in ["mcv", "mchc", "rdw", "arc", "retic_pct", "nrbc_per100wbc", "neut_band", "mono", "neut_seg", "lymph", "wbc", "mch"]:
    R["single_" + k] = prho(col(k), hab, B, boot=True)
# side composites using pc2 loadings on residualised z
L = {"mcv": -0.4684, "mchc": 0.661, "rdw": -0.3073, "arc": -0.4737, "neut_seg": 0.3418, "neut_band": 0.4455, "lymph": 0.4622, "mono": 0.5668}
Z = {k: zres(col(k), B) for k in L}
regen = sum(L[k] * Z[k] for k in ["mcv", "mchc", "rdw", "arc"])
regen_nomchc = sum(L[k] * Z[k] for k in ["mcv", "rdw", "arc"])
leuk = sum(L[k] * Z[k] for k in ["neut_seg", "neut_band", "lymph", "mono"])
R["corr_pc2_regen_side"] = round(float(spearmanr(pc2, regen)[0]), 3)
R["corr_pc2_leuk_side"] = round(float(spearmanr(pc2, leuk)[0]), 3)
R["corr_regen_leuk_side"] = round(float(spearmanr(regen, leuk)[0]), 3)
R["regen_side_alone"] = prho(regen, hab, B)
R["regen_side_no_mchc"] = prho(regen_nomchc, hab, B)
R["leuk_side_alone"] = prho(leuk, hab, B)
R["regen_side_ctrl_band_mono"] = prho(regen, hab, np.column_stack([B, band, mono]))
R["regen_side_no_mchc_ctrl_band_mono"] = prho(regen_nomchc, hab, np.column_stack([B, band, mono]))
R["leuk_side_ctrl_regen"] = prho(leuk, hab, np.column_stack([B, regen]))
# interaction-like: is the contrast (leuk minus regen deficit) more than the sum? product term
R["regen_x_leuk_product"] = prho(regen * leuk, hab, np.column_stack([B, regen, leuk]))
# reticulocyte arithmetic: MCHC residual vs ARC residual
R["arith_mchc_vs_arc_resid_rho"] = round(float(spearmanr(Z["mchc"], Z["arc"])[0]), 3)
R["arith_mchc_vs_mcv_resid_rho"] = round(float(spearmanr(Z["mchc"], Z["mcv"])[0]), 3)
R["pc2_ctrl_mchc"] = prho(pc2, hab, np.column_stack([B, col("mchc")]))
R["pc2_ctrl_arc"] = prho(pc2, hab, np.column_stack([B, col("arc")]))
# co-infection
noec = np.array([V[i].get("pcr_e_canis") != 1 for i in ids])
R["n_e_canis_in_set"] = int((~noec).sum())
R["pc2_no_e_canis"] = prho(pc2[noec], hab[noec], B[noec])
nooth = np.array([V[i].get("pcr_e_canis") != 1 and V[i].get("pcr_b_vogeli") != 1 and V[i].get("pcr_t_equi") != 1 for i in ids])
R["n_any_coinf"] = int((~nooth).sum())
R["pc2_no_coinfection"] = prho(pc2[nooth], hab[nooth], B[nooth])
# illness duration
ill = np.array([V[i]["illness_days"] for i in ids], float)
R["illness_days_quantiles"] = [float(x) for x in np.percentile(ill, [0, 25, 50, 75, 90, 100])]
R["rho_pc2_illness_raw"] = round(float(spearmanr(pc2, ill)[0]), 3)
R["rho_hab_illness_raw"] = round(float(spearmanr(hab, ill)[0]), 3)
short = ill <= 7
R["pc2_illness_le7"] = prho(pc2[short], hab[short], B[short])
R["pc2_illness_gt7"] = prho(pc2[~short], hab[~short], B[~short], boot=False)
illc = np.array([outc[i].get("illness_class") for i in ids])
dmy = np.column_stack([(illc == c).astype(float) for c in ["DI_2", "DI_3"]])
R["pc2_ctrl_illness_class_plus_days"] = prho(pc2, hab, np.column_stack([B, dmy, ill]))
# habitus coding: drop collapsed (0), and binary bright vs not
R["habitus_counts"] = {str(int(k)): int((hab == k).sum()) for k in np.unique(hab)}
nc = hab > 0
R["pc2_no_collapsed"] = prho(pc2[nc], hab[nc], B[nc], boot=False)
R["pc2_vs_bright_binary"] = prho(pc2, (hab == 4).astype(float), B, boot=False)
# temperature/hydration confounders
temp = np.array([np.nan if V[i].get("temp_c") is None else V[i]["temp_c"] for i in ids])
R["pc2_ctrl_temp"] = prho(pc2, hab, np.column_stack([B, temp]), boot=False)
# leave out the top 5% leverage on pc2
q = np.abs(pc2) < np.percentile(np.abs(pc2), 95)
R["pc2_trim_extreme5pct"] = prho(pc2[q], hab[q], B[q], boot=False)
print(json.dumps(R, indent=1))
# between-dog coupling: does more inflammation go with less regeneration at a given hct and illness days?
print("--- coupling (Spearman of residuals at given hct, hct^2, log illness days), 95% bootstrap CI")
def bci(x, y):
    n = len(x); bs = [spearmanr(x[ix], y[ix])[0] for ix in (rng.integers(0, n, n) for _ in range(NB))]
    return round(float(spearmanr(x, y)[0]), 3), [round(float(v), 3) for v in np.percentile(bs, [2.5, 97.5])]
leuk_u = sum(Z[k] for k in ["neut_seg", "neut_band", "lymph", "mono"])
regen_u = Z["arc"] + zres(col("rdw"), B) - 0  # more = more regeneration (ARC, RDW)
C = {}
for a in ["neut_band", "mono", "neut_seg", "lymph"]:
    for b in ["arc", "rdw", "mcv", "mchc"]:
        C[a + "~" + b] = bci(Z[a], Z[b])
C["leuk_unweighted~arc"] = bci(leuk_u, Z["arc"])
C["leuk_unweighted~arc_plus_rdw"] = bci(leuk_u, regen_u)
print(json.dumps(C))
