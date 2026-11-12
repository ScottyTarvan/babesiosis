"""SV-09 analysis: phenotype axes after anaemia and stage, replicated across sources.

Run from /experiments/SV-09/:  env/py/Scripts/python.exe -I scripts/analyse.py
Reads the SV-G1 tidy files and SV-01 pseudo-stage, checks their SHA-256 and the spec hash, writes out/.
"""
import csv
import hashlib
import itertools
import json
import math
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
EXP = os.path.dirname(PKG)
TIDY = os.path.join(EXP, "shared", "tidy")
OUT = os.path.join(PKG, "out")

INPUTS = {
    os.path.join(TIDY, "DS05.features.json"): "323238159fb21596dacc02464fe4ebdf7bd54282cd06fdce7535057f28e90a1e",
    os.path.join(TIDY, "DS03.features.json"): "2862ac7e6e5fcec6200024543e4142fbe81eabd2eadef06d4f288bc982eda8a6",
    os.path.join(TIDY, "S-CB017.features.json"): "6ed00495a7296cb9e3a87e5132cfa0f7a6a798068e9c9e811c9efdcada088cac",
    os.path.join(TIDY, "S-CB050.features.json"): "fedde71e230325695e0866bd362d932a83904dc50de7883003dc6431cff9460f",
    os.path.join(EXP, "SV-01", "out", "pseudo_stage.csv"): "bee82f3ee20bc3cc0b1295da1e8151a9355e081787df58f3c1658a50a5a2c24d",
    os.path.join(EXP, "SV-01", "out", "time_anchored", "pseudo_stage.csv"): "ebeb9cdbe4227c70b0449df8e34bed4fbe79c2635024ef485ebf928a28b4e835",
}
SEED = 20261112
N_BOOT = 2000
N_PERM = 10000
N_PA = 1000
rng = np.random.default_rng(SEED)

MAIN_VARS = ["mcv", "mchc", "rdw", "arc", "nrbc_per100wbc", "neut_seg", "neut_band", "lymph", "mono", "plt", "albumin", "globulin"]
LOG05 = {"arc", "neut_seg", "neut_band", "lymph", "mono", "plt", "retic_pct", "wbc"}
LOG1 = {"nrbc_per100wbc"}
LABEL = {"mcv": "MCV", "mchc": "MCHC", "rdw": "RDW", "arc": "ARC", "nrbc_per100wbc": "nRBC", "neut_seg": "Seg. neutrophils",
         "neut_band": "Band neutrophils", "lymph": "Lymphocytes", "mono": "Monocytes", "plt": "Platelets", "albumin": "Albumin",
         "globulin": "Globulin", "retic_pct": "Reticulocytes %", "wbc": "WBC"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def check_inputs():
    for p, exp in INPUTS.items():
        got = sha256(p)
        if got != exp:
            raise SystemExit(f"hash changed: {p} {got}")
    spec = sha256(os.path.join(PKG, "spec.md"))
    expo = open(os.path.join(PKG, "exposure.md"), encoding="utf-8").read()
    rows = re.findall(r"\| (shared/tidy/\S+\.outcomes\.json) \| ([0-9a-f]{64}) \| ([0-9a-f]{64}) \|", expo)
    for f, h, s in rows:
        if s != spec:
            raise SystemExit("spec hash differs from exposure.md")
        if sha256(os.path.join(EXP, f)) != h:
            raise SystemExit(f"outcomes file changed: {f}")
    return spec


def tr(v, x):
    if x is None:
        return None
    if v in LOG05:
        return math.log(x + 0.05)
    if v in LOG1:
        return math.log(x + 1.0)
    return float(x)


def load(name):
    return json.load(open(os.path.join(TIDY, name), encoding="utf-8"))


def residualise(X, C):
    """OLS residuals of each column of X on intercept + C, then standardised."""
    n = X.shape[0]
    D = np.column_stack([np.ones(n)] + ([C] if C is not None and C.size else []))
    beta, *_ = np.linalg.lstsq(D, X, rcond=None)
    R = X - D @ beta
    sd = R.std(axis=0, ddof=1)
    sd[sd == 0] = 1.0
    return (R - R.mean(axis=0)) / sd


def ranks(a):
    from scipy.stats import rankdata
    return np.apply_along_axis(rankdata, 0, a)


def pca(Z, spearman=False):
    if spearman:
        Z = ranks(Z)
        Z = (Z - Z.mean(0)) / Z.std(0, ddof=1)
    R = np.corrcoef(Z, rowvar=False)
    w, V = np.linalg.eigh(R)
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    L = V * np.sqrt(np.clip(w, 0, None))  # structure coefficients
    for j in range(L.shape[1]):
        k = np.argmax(np.abs(L[:, j]))
        if L[k, j] < 0:
            L[:, j] *= -1
            V[:, j] *= -1
    S = Z @ V
    return w, L, S, V


def phi(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = math.sqrt(float(a @ a) * float(b @ b))
    return float(a @ b) / d if d > 0 else float("nan")


def procrustes(L, ref):
    U, _, Vt = np.linalg.svd(L.T @ ref)
    return L @ (U @ Vt)


def ci(a):
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def cliffs(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    gt = (x[:, None] > y[None, :]).sum()
    lt = (x[:, None] < y[None, :]).sum()
    return float(gt - lt) / (len(x) * len(y))


def spearman(x, y):
    from scipy.stats import rankdata
    return float(np.corrcoef(rankdata(x), rankdata(y))[0, 1])


def bh(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    o = np.argsort(ps)
    q = np.empty(m)
    prev = 1.0
    for i in range(m - 1, -1, -1):
        prev = min(prev, ps[o[i]] * m / (i + 1))
        q[o[i]] = prev
    return q.tolist()


def r(x, k=3):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return None
    return round(float(x), k)


def write_csv(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for row in rows:
            w.writerow(["" if v is None else v for v in row])


# ---------------------------------------------------------------- data
def ds05_dogs():
    d = load("DS05.features.json")
    out = []
    for rec in d["records"]:
        v = rec["values"]
        if v.get("pcr_b_rossi") != 1 or v.get("hct") is None:
            continue
        vals = dict(v)
        if vals.get("globulin") == 1.0:  # known entry error (spec)
            vals["globulin"] = None
            vals["albumin"] = None
        out.append((rec["dog_id"], vals))
    return out


def read_stage(path):
    m = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["plane"] == "A_hct_logarc" and row["dataset_id"] == "DS05":
                m[row["dog_id"]] = float(row["pseudo_stage"])
    return m


def matrix(dogs, vars_, extra):
    ids, X, C = [], [], []
    for did, v in dogs:
        xs = [tr(k, v.get(k)) for k in vars_]
        cs = [e(did, v) for e in extra]
        if any(a is None for a in xs) or any(a is None for a in cs):
            continue
        ids.append(did)
        X.append(xs)
        C.append(cs)
    return ids, np.array(X, float), np.array(C, float)


HCT = lambda did, v: v.get("hct")
HCT2 = lambda did, v: None if v.get("hct") is None else v["hct"] ** 2
ILL = lambda did, v: None if v.get("illness_days") is None else math.log(v["illness_days"] + 1)


def parallel(Z):
    p = Z.shape[1]
    E = np.empty((N_PA, p))
    for b in range(N_PA):
        P = np.column_stack([rng.permutation(Z[:, j]) for j in range(p)])
        E[b] = np.sort(np.linalg.eigvalsh(np.corrcoef(P, rowvar=False)))[::-1]
    return np.percentile(E, 95, axis=0)


def main():
    os.makedirs(OUT, exist_ok=True)
    spec_sha = check_inputs()
    res = {"spec_sha256": spec_sha, "seed": SEED, "n_boot": N_BOOT, "n_perm": N_PERM, "n_parallel": N_PA}

    # ------------------------------------------------------------ step 1
    dogs = ds05_dogs()
    stage_spec = read_stage(os.path.join(EXP, "SV-01", "out", "pseudo_stage.csv"))
    stage_ta = read_stage(os.path.join(EXP, "SV-01", "out", "time_anchored", "pseudo_stage.csv"))
    STG = lambda did, v: stage_spec.get(did)
    STA = lambda did, v: stage_ta.get(did)
    ids, X, C = matrix(dogs, MAIN_VARS, [HCT, HCT2, ILL, STG, STA])
    n1 = len(ids)
    hct = C[:, 0]
    cov = {"primary": C[:, [0, 1, 2]], "S1_hct_only": C[:, [0, 1]], "S2_spec_pseudo_stage": C[:, [0, 1, 3]],
           "S3_time_anchored_stage": C[:, [0, 1, 4]], "S5_no_conditioning": None}
    Z = residualise(X, cov["primary"])
    w, L, S, V = pca(Z)
    pa = parallel(Z)
    retained = 0
    for k in range(len(w)):
        if w[k] > pa[k]:
            retained += 1
        else:
            break
    m = max(retained, 2)
    # bootstrap stability
    bphi = np.full((N_BOOT, m), np.nan)
    for b in range(N_BOOT):
        idx = rng.integers(0, n1, n1)
        Zb = residualise(X[idx], cov["primary"][idx])
        _, Lb, _, _ = pca(Zb)
        Lb = procrustes(Lb[:, :m], L[:, :m])
        for j in range(m):
            bphi[b, j] = phi(Lb[:, j], L[:, j])
    stab = []
    for j in range(m):
        med = float(np.median(bphi[:, j]))
        p5 = float(np.percentile(bphi[:, j], 5))
        stab.append({"component": j + 1, "eigenvalue": r(w[j]), "pa_95": r(pa[j]), "retained": j < retained,
                     "var_explained": r(w[j] / len(w)), "boot_phi_median": r(med), "boot_phi_p5": r(p5),
                     "stable": bool(med >= 0.85 and p5 >= 0.70)})
    # sensitivities
    sens = []
    for key in ["S1_hct_only", "S2_spec_pseudo_stage", "S3_time_anchored_stage", "S4_spearman", "S5_no_conditioning"]:
        if key == "S4_spearman":
            _, Ls, _, _ = pca(Z, spearman=True)
        else:
            Zs = residualise(X, cov[key])
            _, Ls, _, _ = pca(Zs)
        Lr = procrustes(Ls[:, :m], L[:, :m])
        for j in range(m):
            sens.append({"analysis": key, "component": j + 1, "phi": r(phi(Lr[:, j], L[:, j]))})
    # correlation of score with haematocrit and illness days (raw), to show conditioning
    raw_corr = []
    for j in range(m):
        raw_corr.append({"component": j + 1, "rho_hct": r(spearman(S[:, j], hct)),
                         "rho_illness_days": r(spearman(S[:, j], C[:, 2]))})
    # habitus (secondary, DS05 outcomes)
    out05 = {rec["dog_id"]: rec["values"] for rec in load("DS05.outcomes.json")["records"]}
    hab = np.array([out05.get(i, {}).get("habitus_score") for i in ids], dtype=object)
    ok = np.array([h is not None for h in hab])
    habv = hab[ok].astype(float)
    from scipy.stats import rankdata
    Dh = np.column_stack([np.ones(ok.sum()), cov["primary"][ok]])

    def rres(y, D):
        y = rankdata(y)
        b_, *_ = np.linalg.lstsq(D, y, rcond=None)
        return y - D @ b_

    habres = []
    hr = rres(habv, Dh)
    for j in range(m):
        sr = rres(S[ok, j], Dh)
        obs = float(np.corrcoef(sr, hr)[0, 1])
        cnt = 0
        for _ in range(N_PERM):
            if abs(np.corrcoef(sr, rng.permutation(hr))[0, 1]) >= abs(obs) - 1e-12:
                cnt += 1
        bs = []
        nn = int(ok.sum())
        for _ in range(N_BOOT):
            idx = rng.integers(0, nn, nn)
            a = rres(S[ok, j][idx], Dh[idx])
            c = rres(habv[idx], Dh[idx])
            if a.std() > 0 and c.std() > 0:
                bs.append(np.corrcoef(a, c)[0, 1])
        habres.append({"component": j + 1, "n": nn, "partial_rho": r(obs), "ci": [r(x) for x in ci(bs)],
                       "p": r((cnt + 1) / (N_PERM + 1), 4)})
    loadings = []
    for i, v in enumerate(MAIN_VARS):
        loadings.append({"variable": v, "label": LABEL[v], **{f"pc{j+1}": r(L[i, j]) for j in range(m)}})
    write_csv("loadings.csv", ["block", "dataset", "variable", "component", "loading"],
              [["ds05_main", "DS05", v, j + 1, r(L[i, j], 4)] for i, v in enumerate(MAIN_VARS) for j in range(m)])
    write_csv("ds05_scree.csv", ["component", "eigenvalue", "parallel_95"],
              [[k + 1, r(w[k], 4), r(pa[k], 4)] for k in range(len(w))])
    write_csv("ds05_scores.csv", ["dog_id"] + [f"pc{j+1}" for j in range(m)],
              [[ids[i]] + [r(S[i, j], 4) for j in range(m)] for i in range(n1)])
    res["step1"] = {"n": n1, "variables": MAIN_VARS, "retained": retained, "components": stab, "sensitivity": sens,
                    "raw_corr": raw_corr, "habitus": habres, "loadings": loadings,
                    "scree": [{"component": k + 1, "eigenvalue": r(w[k]), "pa_95": r(pa[k])} for k in range(len(w))]}

    # ------------------------------------------------------------ step 2
    ds03 = [(rec["dog_id"], rec["values"]) for rec in load("DS03.features.json")["records"]
            if rec["group"] == "infected" and rec["values"].get("setting") == "natural"]
    s017 = [(rec["dog_id"], rec["values"]) for rec in load("S-CB017.features.json")["records"]
            if rec["group"] == "infected" and rec["timepoint"] == "day_1"]
    s050_recs = [rec for rec in load("S-CB050.features.json")["records"] if rec["group"] == "infected"]
    s050 = [(rec["dog_id"], rec["values"]) for rec in s050_recs]
    blocks = [
        {"key": "red_cell", "target": "DS03", "target_label": "DS03 natural infection (SRC-A)", "species": "B. rossi",
         "vars": ["mchc", "retic_pct", "arc"], "cond": True, "dogs": ds03},
        {"key": "leukocyte_platelet", "target": "S-CB017", "target_label": "S-CB017 day 1 (SRC-D)", "species": "B. canis",
         "vars": ["neut_seg", "neut_band", "lymph", "mono", "plt"], "cond": True, "dogs": s017},
        {"key": "leukocyte", "target": "S-CB050", "target_label": "S-CB050 infected (SRC-A)", "species": "B. rossi",
         "vars": ["wbc", "neut_seg", "neut_band"], "cond": False, "dogs": s050},
    ]
    cong_rows, block_res = [], []
    for blk in blocks:
        vs = blk["vars"]
        ext = [HCT, HCT2] if blk["cond"] else []
        _, Xa, Ca = matrix(dogs, vs, ext)
        _, Xb, Cb = matrix(blk["dogs"], vs, ext)
        Ca = Ca if blk["cond"] else None
        Cb = Cb if blk["cond"] else None
        Za = residualise(Xa, Ca)
        Zb = residualise(Xb, Cb)
        wa, La, _, _ = pca(Za)
        wb, Lb, _, _ = pca(Zb)
        k = 2 if len(vs) >= 5 else 1
        Lb_r = procrustes(Lb[:, :k], La[:, :k]) if k > 1 else Lb[:, :1] * np.sign(phi(Lb[:, 0], La[:, 0]))
        obs = [phi(Lb_r[:, j], La[:, j]) for j in range(k)]
        # bootstrap both files
        bs = np.full((N_BOOT, k), np.nan)
        for b in range(N_BOOT):
            ia = rng.integers(0, len(Xa), len(Xa))
            ib = rng.integers(0, len(Xb), len(Xb))
            _, La_b, _, _ = pca(residualise(Xa[ia], None if Ca is None else Ca[ia]))
            _, Lb_b, _, _ = pca(residualise(Xb[ib], None if Cb is None else Cb[ib]))
            if k > 1:
                Lbr = procrustes(Lb_b[:, :k], La_b[:, :k])
            else:
                Lbr = Lb_b[:, :1] * np.sign(phi(Lb_b[:, 0], La_b[:, 0]))
            for j in range(k):
                bs[b, j] = phi(Lbr[:, j], La_b[:, j])
        # label permutation (exact)
        perms = list(itertools.permutations(range(len(vs))))
        pp = []
        for j in range(k):
            ge = 0
            for pm in perms:
                Lp = Lb[list(pm), :k]
                Lpr = procrustes(Lp, La[:, :k]) if k > 1 else Lp[:, :1]
                if abs(phi(Lpr[:, j], La[:, j])) >= abs(obs[j]) - 1e-12:
                    ge += 1
            pp.append(ge / len(perms))
        uni = [abs(phi(Lb_r[:, j], np.ones(len(vs)))) for j in range(k)]
        # link to DS05 residual axes
        shared = [v for v in vs if v in MAIN_VARS]
        link = []
        for jj in range(m):
            a = [L[MAIN_VARS.index(v), jj] for v in shared]
            bvec = [La[vs.index(v), 0] for v in shared]
            link.append({"component": jj + 1, "variables": shared, "phi": r(phi(a, bvec))})
        comps = []
        for j in range(k):
            lo, hi = ci(bs[:, j])
            comps.append({"component": j + 1, "phi": r(obs[j]), "ci": [r(lo), r(hi)], "perm_p": r(pp[j], 4),
                          "n_perms": len(perms), "uniform_phi": r(uni[j]), "specificity_testable": len(vs) >= 4,
                          "var_explained_ds05": r(wa[j] / len(vs)), "var_explained_target": r(wb[j] / len(vs))})
            cong_rows.append([blk["key"], blk["target"], j + 1, len(Xa), len(Xb), r(obs[j], 4), r(lo, 4), r(hi, 4),
                              r(uni[j], 4), r(pp[j], 4), len(perms)])
        lrows = []
        for i, v in enumerate(vs):
            lrows.append({"variable": v, "label": LABEL[v], "ds05": [r(La[i, j]) for j in range(k)],
                          "target": [r(Lb_r[i, j]) for j in range(k)]})
        block_res.append({"key": blk["key"], "target": blk["target"], "target_label": blk["target_label"],
                          "species": blk["species"], "variables": vs, "conditioning": "haematocrit, haematocrit²" if blk["cond"] else "none",
                          "n_ds05": len(Xa), "n_target": len(Xb), "components": comps, "loadings": lrows, "link": link})
    with open(os.path.join(OUT, "loadings.csv"), "a", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, lineterminator="\n")
        for b in block_res:
            for lr in b["loadings"]:
                for j in range(len(lr["ds05"])):
                    wr.writerow([b["key"], "DS05", lr["variable"], j + 1, lr["ds05"][j]])
                    wr.writerow([b["key"], b["target"], lr["variable"], j + 1, lr["target"][j]])
    write_csv("congruence.csv", ["block", "target", "component", "n_ds05", "n_target", "phi", "ci_low", "ci_high",
                                 "uniform_phi", "label_perm_p", "n_label_perms"], cong_rows)
    # replication rule
    verdicts = []
    for jj in range(m):
        st = stab[jj]
        for b in block_res:
            lk = b["link"][jj]["phi"]
            c1 = b["components"][0]
            R1 = st["retained"] and st["stable"]
            R2 = lk is not None and abs(lk) >= 0.85
            R3 = c1["phi"] >= 0.85 and c1["ci"][0] >= 0.70
            R4 = (c1["perm_p"] <= 0.05 and c1["phi"] > c1["uniform_phi"]) if c1["specificity_testable"] else None
            if R1 and R2 and R3 and R4 is True:
                verdict = "replicated"
            elif R1 and R2 and R3 and R4 is None:
                verdict = "congruent but not specific"
            else:
                verdict = "not replicated"
            verdicts.append({"component": jj + 1, "block": b["key"], "R1": bool(R1), "R2": bool(R2), "R3": bool(R3),
                             "R4": R4, "verdict": verdict})
    res["step2"] = {"blocks": block_res, "verdicts": verdicts}

    # ------------------------------------------------------------ step 3
    rank_v = {"replicated": 2, "congruent but not specific": 1, "not replicated": 0}
    chosen, chosen_status = None, None
    for blk_key in ["leukocyte", "leukocyte_platelet"]:
        cand = [v for v in verdicts if v["block"] == blk_key and v["verdict"] != "not replicated"]
        if cand:
            cand.sort(key=lambda v: -rank_v[v["verdict"]])
            chosen, chosen_status = cand[0]["component"], f"{cand[0]['verdict']} ({blk_key})"
            break
    if chosen is None:
        sums = [abs(L[MAIN_VARS.index("neut_seg"), j]) + abs(L[MAIN_VARS.index("neut_band"), j]) for j in range(m)]
        chosen = int(np.argmax(sums)) + 1
        chosen_status = "not replicated"
    jj = chosen - 1

    def weights(vs, col=None):
        wv = np.array([L[MAIN_VARS.index(v), jj if col is None else col] for v in vs])
        return wv / np.linalg.norm(wv)

    o050 = {rec["dog_id"]: rec["values"] for rec in load("S-CB050.outcomes.json")["records"]}
    o017 = {rec["dog_id"]: rec["values"] for rec in load("S-CB017.outcomes.json")["records"]}

    def score_file(dogs_, vs, cond, wv=None):
        ext = [HCT, HCT2] if cond else []
        idd, Xs, Cs = matrix(dogs_, vs, ext)
        Zs = residualise(Xs, Cs if cond else None)
        wv = weights(vs) if wv is None else wv
        return idd, Zs @ wv, Zs

    def contrast(score, lab, strata=None):
        score = np.asarray(score)
        lab = np.asarray(lab)
        obs = cliffs(score[lab == 1], score[lab == 0])
        strata = np.zeros(len(lab), int) if strata is None else np.asarray(strata)
        cnt = 0
        for _ in range(N_PERM):
            lp = lab.copy()
            for s in np.unique(strata):
                ix = np.where(strata == s)[0]
                lp[ix] = rng.permutation(lab[ix])
            if abs(cliffs(score[lp == 1], score[lp == 0])) >= abs(obs) - 1e-12:
                cnt += 1
        i1, i0 = np.where(lab == 1)[0], np.where(lab == 0)[0]
        bs = [cliffs(score[rng.choice(i1, len(i1))], score[rng.choice(i0, len(i0))]) for _ in range(N_BOOT)]
        return {"delta": r(obs), "ci": [r(x) for x in ci(bs)], "p": r((cnt + 1) / (N_PERM + 1), 4),
                "n_pos": int(len(i1)), "n_neg": int(len(i0)),
                "median_pos": r(float(np.median(score[i1]))), "median_neg": r(float(np.median(score[i0])))}

    def resid_contrast(score, band, lab, strata):
        score, band, lab = np.asarray(score), np.asarray(band), np.asarray(lab)

        def rd(ix):
            D = np.column_stack([np.ones(len(ix)), band[ix]])
            b_, *_ = np.linalg.lstsq(D, score[ix], rcond=None)
            e = score[ix] - D @ b_
            return e

        e = rd(np.arange(len(lab)))
        out = contrast(e, lab, strata)
        # bootstrap with re-fit
        i1, i0 = np.where(lab == 1)[0], np.where(lab == 0)[0]
        bs = []
        for _ in range(N_BOOT):
            ix = np.concatenate([rng.choice(i1, len(i1)), rng.choice(i0, len(i0))])
            eb = rd(ix)
            lb = lab[ix]
            bs.append(cliffs(eb[lb == 1], eb[lb == 0]))
        out["ci"] = [r(x) for x in ci(bs)]
        out["rho_score_band"] = r(spearman(score, band))
        return out

    s3 = {"axis_component": chosen, "axis_status": chosen_status}
    # S-CB050
    v050 = ["neut_seg", "neut_band"]
    id50, sc50, Z50 = score_file(s050, v050, False)
    coh = {rec["dog_id"]: rec["values"].get("cohort") for rec in s050_recs}
    lab50 = np.array([o050[i]["died"] for i in id50])
    st50 = np.array([coh[i] for i in id50])
    prim50 = contrast(sc50, lab50, st50)
    band50 = np.array([tr("neut_band", dict(s050)[i]["neut_band"]) for i in id50])
    seg50 = np.array([tr("neut_seg", dict(s050)[i]["neut_seg"]) for i in id50])
    bands_only = contrast(band50, lab50, st50)
    seg_only = contrast(seg50, lab50, st50)
    resid50 = resid_contrast(sc50, band50, lab50, st50)
    c1 = st50 == 1
    a1 = contrast(sc50[c1], lab50[c1])
    # A2 with wbc: DS05 leukocyte block component 1 weights
    lb = [b for b in block_res if b["key"] == "leukocyte"][0]
    w_a2 = np.array([x["ds05"][0] for x in lb["loadings"]])
    w_a2 = w_a2 / np.linalg.norm(w_a2)
    _, sc50b, _ = score_file(s050, ["wbc", "neut_seg", "neut_band"], False, w_a2)
    a2 = contrast(sc50b, lab50, st50)
    # S-CB017
    v017 = ["neut_seg", "neut_band", "lymph", "mono", "plt"]
    id17, sc17, _ = score_file(s017, v017, True)
    lab17 = np.array([o017[i]["complicated"] for i in id17])
    prim17 = contrast(sc17, lab17)
    _, sc17n, _ = score_file(s017, v017, False)
    a3 = contrast(sc17n, lab17)
    # A4 (post hoc, deviation D3): the other retained component, same files
    alt = 1 if jj == 0 else 0
    _, sc50c, _ = score_file(s050, v050, False, weights(v050, alt))
    _, sc17c, _ = score_file(s017, v017, True, weights(v017, alt))
    a4_50 = contrast(sc50c, lab50, st50)
    a4_17 = contrast(sc17c, lab17)
    a4_rho = [r(spearman(sc50, sc50c)), r(spearman(sc17, sc17c))]
    q = bh([prim50["p"], prim17["p"]])
    prim50["q"], prim17["q"] = r(q[0], 4), r(q[1], 4)
    # MCP-1 descriptive
    mcp = []
    for name, idd, sc, dd in [("S-CB050 cohort 1", id50, sc50, dict(s050)), ("S-CB017 day 1", id17, sc17, dict(s017))]:
        pairs = [(s_, math.log(dd[i]["mcp1"])) for i, s_ in zip(idd, sc) if dd[i].get("mcp1") is not None and dd[i]["mcp1"] > 0
                 and (name != "S-CB050 cohort 1" or coh[i] == 1)]
        a = np.array([p_[0] for p_ in pairs])
        b_ = np.array([p_[1] for p_ in pairs])
        obs = spearman(a, b_)
        cnt = sum(1 for _ in range(N_PERM) if abs(spearman(a, rng.permutation(b_))) >= abs(obs) - 1e-12)
        bs = []
        for _ in range(N_BOOT):
            ix = rng.integers(0, len(a), len(a))
            bs.append(spearman(a[ix], b_[ix]))
        mcp.append({"file": name, "n": len(a), "rho": r(obs), "ci": [r(x) for x in ci(bs)], "p": r((cnt + 1) / (N_PERM + 1), 4)})
    s3.update({
        "weights_s050": {v: r(x) for v, x in zip(v050, weights(v050))},
        "weights_s017": {v: r(x) for v, x in zip(v017, weights(v017))},
        "s050_died": prim50, "s017_complicated": prim17, "s050_bands_only": bands_only, "s050_seg_only": seg_only,
        "s050_axis_given_bands": resid50, "A1_s050_cohort1": a1, "A2_s050_with_wbc": a2,
        "A3_s017_no_hct": a3, "mcp1": mcp,
        "A4_other_component": {"component": alt + 1, "weights_s050": {v: r(x) for v, x in zip(v050, weights(v050, alt))},
                               "weights_s017": {v: r(x) for v, x in zip(v017, weights(v017, alt))},
                               "s050_died": a4_50, "s017_complicated": a4_17,
                               "rho_with_chosen_score": {"S-CB050": a4_rho[0], "S-CB017": a4_rho[1]}},
    })
    adds = not (resid50["ci"][0] <= 0 <= resid50["ci"][1] or abs(prim50["delta"]) <= abs(bands_only["delta"]))
    s3["adds_beyond_bands"] = bool(adds)
    res["step3"] = s3
    rows = []
    for nm, x in [("S-CB050 died: axis score", prim50), ("S-CB017 complicated: axis score", prim17),
                  ("S-CB050 died: band neutrophils alone", bands_only), ("S-CB050 died: segmented neutrophils alone", seg_only),
                  ("S-CB050 died: axis given bands", resid50), ("A1 S-CB050 cohort 1", a1), ("A2 S-CB050 with WBC", a2),
                  ("A3 S-CB017 no haematocrit conditioning", a3),
                  ("A4 (post hoc) S-CB050 died: other component", a4_50), ("A4 (post hoc) S-CB017 complicated: other component", a4_17)]:
        rows.append([nm, x["n_pos"], x["n_neg"], x["delta"], x["ci"][0], x["ci"][1], x["p"], x.get("q")])
    write_csv("axis_outcome.csv", ["analysis", "n_label1", "n_label0", "cliffs_delta", "ci_low", "ci_high", "perm_p", "bh_q"], rows)
    pts = [["S-CB050", i, r(s_, 4), int(l_)] for i, s_, l_ in zip(id50, sc50, lab50)]
    pts += [["S-CB017", i, r(s_, 4), int(l_)] for i, s_, l_ in zip(id17, sc17, lab17)]
    write_csv("axis_scores_by_label.csv", ["file", "dog_id", "score", "label"], pts)
    res["score_points"] = [{"file": p_[0], "score": p_[2], "label": p_[3]} for p_ in pts]
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, allow_nan=False)
    print(json.dumps({k: res[k] for k in ["step1", "step2", "step3"]}, indent=1)[:20000])


if __name__ == "__main__":
    main()
