"""SV-META step 4: agreement between independent sources, by mechanism theme.

One indicator per independent source and theme (spec section 5), oriented so that a positive value means more of the mechanism in
the more severe dogs. Indicators that another package already printed are read from its out/ file (file and line recorded);
the rest are computed here from the SV-G1 tidy files. Then Stouffer, Fisher, sign test and leave-one-source-out per theme, BH over
the primary combined rows. Writes out/themes.csv and out/theme_indicators.json.

Run from /experiments/SV-META/:  env/py/Scripts/python.exe -I scripts/themes.py
"""
import csv
import hashlib
import itertools
import json
from math import sqrt
from pathlib import Path

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
EXP = PKG.parent
TIDY = EXP / "shared" / "tidy"
OUT = PKG / "out"
SEED = 20261112
NBOOT, NPERM = 2000, 10000
SPEC_SHA = "9f41ddf629757e4f31569c305eb2a607cd84bf0eb91b1190adcfae96038f6238"

if hashlib.sha256((PKG / "spec.md").read_bytes()).hexdigest() != SPEC_SHA:
    raise SystemExit("spec.md changed after the lock")


def load(name):
    return json.loads((TIDY / name).read_text(encoding="utf-8"))


def read_csv(rel):
    with (EXP / rel).open(encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh)
        header = next(rd)
        prev = rd.line_num
        for cells in rd:
            start, end = prev + 1, rd.line_num
            prev = end
            yield (str(start) if start == end else f"{start}-{end}"), dict(zip(header, cells))


def find_row(rel, **match):
    for ln, r in read_csv(rel):
        if all(r[k] == v for k, v in match.items()):
            return ln, r
    raise KeyError(f"{rel} {match}")


# ------------------------------------------------------------------ statistics
def cliff(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float((np.sign(x[:, None] - y[None, :])).mean())


def cliff_test(x, y, rng):
    """Cliff's delta x minus y, stratified bootstrap CI, two-sided permutation p."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = cliff(x, y)
    boots = np.array([cliff(rng.choice(x, len(x)), rng.choice(y, len(y))) for _ in range(NBOOT)])
    pooled = np.concatenate([x, y])
    nx = len(x)
    cnt = 0
    for _ in range(NPERM):
        rng.shuffle(pooled)
        if abs(cliff(pooled[:nx], pooled[nx:])) >= abs(d) - 1e-12:
            cnt += 1
    return d, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)), (cnt + 1) / (NPERM + 1), len(x), len(y)


def cliff_exact(x, y):
    """Exact two-sided permutation over all allocations (SRC-B: 3 vs 2 dogs, 10 allocations)."""
    x, y = list(map(float, x)), list(map(float, y))
    d = cliff(x, y)
    pooled = x + y
    idx = range(len(pooled))
    n_ge = n_all = 0
    for comb in itertools.combinations(idx, len(x)):
        a = [pooled[i] for i in comb]
        b = [pooled[i] for i in idx if i not in comb]
        n_all += 1
        if abs(cliff(a, b)) >= abs(d) - 1e-12:
            n_ge += 1
    return d, None, None, n_ge / n_all, len(x), len(y)


def spearman_test(x, y, rng):
    x, y = np.asarray(x, float), np.asarray(y, float)
    rho = float(stats.spearmanr(x, y).statistic)
    n = len(x)
    boots = []
    for _ in range(NBOOT):
        i = rng.integers(0, n, n)
        boots.append(stats.spearmanr(x[i], y[i]).statistic)
    boots = np.array(boots, float)
    boots = boots[~np.isnan(boots)]
    rx = stats.rankdata(x)
    ry = stats.rankdata(y)
    cnt = 0
    for _ in range(NPERM):
        if abs(np.corrcoef(rx, rng.permutation(ry))[0, 1]) >= abs(rho) - 1e-12:
            cnt += 1
    return rho, float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5)), (cnt + 1) / (NPERM + 1), n, None


def bh(ps):
    ps = np.asarray(ps, float)
    m = len(ps)
    order = np.argsort(ps)
    q = np.empty(m)
    prev = 1.0
    for rank, i in reversed(list(enumerate(order, start=1))):
        prev = min(prev, ps[i] * m / rank)
        q[i] = prev
    return q


# ------------------------------------------------------------------ data
def by_dog_outcome(name, label):
    d = load(name)
    return {r["dog_id"]: r["values"].get(label) for r in d["records"]}


def scb017_day1():
    f = load("S-CB017.features.json")
    lab = by_dog_outcome("S-CB017.outcomes.json", "complicated")
    recs = [r for r in f["records"] if r["group"] == "infected" and r["timepoint"] == "day_1"]
    return recs, lab


def group_values(recs, lab, var):
    sev = [r["values"][var] for r in recs if lab.get(r["dog_id"]) == 1 and r["values"].get(var) is not None]
    non = [r["values"][var] for r in recs if lab.get(r["dog_id"]) == 0 and r["values"].get(var) is not None]
    return sev, non


def ds05_pairs(var):
    f = load("DS05.features.json")
    hab = by_dog_outcome("DS05.outcomes.json", "habitus_score")
    xs, ys = [], []
    for r in f["records"]:
        if r["values"].get("pcr_b_rossi") != 1.0:
            continue
        v, h = r["values"].get(var), hab.get(r["dog_id"])
        if v is None or h is None:
            continue
        xs.append(v)
        ys.append(4 - h)  # dullness
    return xs, ys


def ds02_change(var):
    """Per dog: last pre-treatment value minus baseline (mean of days -1 and 0; else the earliest pre-treatment value)."""
    f = load("DS02.features.json")
    dogs = {}
    for r in f["records"]:
        if r["post_treatment"]:
            continue
        dogs.setdefault(r["dog_id"], []).append(r)
    out = {"high": [], "low": []}
    notes = []
    for dog, recs in sorted(dogs.items()):
        dose = recs[0]["values"]["dose_group"]
        recs = sorted(recs, key=lambda r: (r["day"], r["timepoint"]))
        vals = [(r["timepoint"], r["values"].get(var)) for r in recs if r["values"].get(var) is not None]
        base = [v for t, v in vals if t in ("day_-1", "day_0")]
        if base:
            b = float(np.mean(base))
        else:
            b = vals[0][1]
            notes.append(f"{dog}: baseline = {vals[0][0]}")
        out[dose].append(vals[-1][1] - b)
    return out["high"], out["low"], notes


# ------------------------------------------------------------------ indicators
rng = np.random.default_rng(SEED)
IND = []  # theme, source, species, measure, raw effect, sign, oriented effect, lo, hi, p, n, provenance, circular, known_driver


def put(theme, source, species, measure, effect, lo, hi, p, n, prov, sign=1, circular="", known="", note=""):
    o = None if effect is None else sign * effect
    olo, ohi = (None, None) if lo is None else ((lo, hi) if sign == 1 else (-hi, -lo))
    IND.append(dict(theme=theme, source=source, species=species, measure=measure, effect=effect, sign=sign, oriented=o,
                    ci_low=olo, ci_high=ohi, p=p, n=n, provenance=prov, circular=circular, known_driver=known, note=note))


def from_file(theme, source, species, measure, rel, match, eff, lo, hi, p, n, sign=1, circular="", known="", note=""):
    ln, r = find_row(rel, **match)
    g = lambda k: (None if k is None or r[k] == "" else float(r[k]))
    put(theme, source, species, measure, g(eff), g(lo), g(hi), g(p), r[n] if n in r else n, f"{rel}:{ln}", sign, circular, known, note)


def computed(theme, source, species, measure, res, prov, sign=1, circular="", known="", note=""):
    d, lo, hi, p, n1, n2 = res
    n = f"{n1} vs {n2}" if n2 is not None else str(n1)
    put(theme, source, species, measure, round(d, 4), None if lo is None else round(lo, 4), None if hi is None else round(hi, 4),
        round(p, 4), n, prov, sign, circular, known, note)


recs017, lab017 = scb017_day1()
s517 = load("S-CB517.features.json")
lab517 = by_dog_outcome("S-CB517.outcomes.json", "died")
recs517 = [r for r in s517["records"] if r["group"] == "infected"]
s516 = load("S-CB516.features.json")
lab516 = by_dog_outcome("S-CB516.outcomes.json", "died")

SV08 = "SV-08/out/primary_deltas.csv"


def sv08_dose(set_name):
    hi, lo = [], []
    for ln, r in read_csv(SV08):
        if r["set"] == set_name:
            (hi if r["dose"] == "high" else lo).append(float(r["delta"]))
    return cliff_exact(hi, lo)


def sv04_ds02(analyte):
    hi, lo = [], []
    for ln, r in read_csv("SV-04/out/ds02_courses.csv"):
        if r["analyte"] == analyte and r["pre_change_log2"] != "":
            (hi if r["dose_group"] == "high" else lo).append(float(r["pre_change_log2"]))
    return cliff_exact(hi, lo)


def sv02b_peak(measure):
    hi, lo = [], []
    for ln, r in read_csv("SV-02/b/out/reaction_norms.csv"):
        if r["measure"] == measure:
            (hi if r["dose_group"] == "high" else lo).append(float(r["damage_at_peak"]))
    return cliff_exact(hi, lo)


def sv02b_peak_load():
    hi, lo = [], []
    seen = set()
    for ln, r in read_csv("SV-02/b/out/reaction_norms.csv"):
        if r["dog_id"] in seen:
            continue
        seen.add(r["dog_id"])
        (hi if r["dose_group"] == "high" else lo).append(float(r["peak_parasitaemia_pct"]))
    return cliff_exact(hi, lo)


R, C, F_, D_, O_, B_ = "SRC-A", "SRC-C", "SRC-F", "SRC-D", "SRC-O", "SRC-B"
BR, BC = "B. rossi", "B. canis"
TIDYP = "computed from shared/tidy"
NOTE_B = "high vs low dose (3 vs 2 Beagles), exact p over 10 allocations; minimum two-sided p 0.2"

# T01 neutrophil activation and left shift
from_file("T01", R, BR, "band neutrophils, died vs survived (S-CB050)", "SV-09/out/axis_outcome.csv",
          {"analysis": "S-CB050 died: band neutrophils alone"}, "cliffs_delta", "ci_low", "ci_high", "perm_p", "15 vs 126",
          known="published severity finding (CB050, CB040)")
computed("T01", B_, BR, "neutrophil-granule transcript score change (DS06)", sv08_dose("neutrophil_granule"), SV08 + " (dose contrast)",
         note=NOTE_B)
from_file("T01", C, BR, "lactoferrin, complicated vs uncomplicated (DS07)", "SV-06/b/out/ds07_candidates.csv", {"key": "ltf"},
          "delta", "delta_lo", "delta_hi", "p_stratified", "14 vs 17", circular="label contains band neutrophils > 1.5")
computed("T01", D_, BC, "band neutrophils, complicated vs uncomplicated, day 1 (S-CB017)",
         cliff_test(*group_values(recs017, lab017, "neut_band"), rng), TIDYP + "/S-CB017", circular="label: SIRS (bands, WBC)")
computed("T01", F_, BR, "band neutrophils with dullness (DS05)", spearman_test(*ds05_pairs("neut_band"), rng), TIDYP + "/DS05",
         known="band neutrophils (already seen in DS05)")

# T02 monocyte and macrophage activation
computed("T02", R, BR, "monocyte count, died vs survived (S-CB517 = S-CB050 dogs)",
         cliff_test(*group_values(recs517, lab517, "mono"), rng), TIDYP + "/S-CB517")
hi, lo, nb = ds02_change("mono")
computed("T02", B_, BR, "monocyte count change (DS02)", cliff_exact(hi, lo), TIDYP + "/DS02", note=NOTE_B)
from_file("T02", C, BR, "CD14, complicated vs uncomplicated (DS07)", "SV-06/b/out/ds07_candidates.csv", {"key": "cd14"},
          "delta", "delta_lo", "delta_hi", "p_stratified", "14 vs 18", known="published severity finding (CB112, same dogs)")
computed("T02", D_, BC, "monocyte count, complicated vs uncomplicated, day 1 (S-CB017)",
         cliff_test(*group_values(recs017, lab017, "mono"), rng), TIDYP + "/S-CB017")
computed("T02", F_, BR, "monocyte count with dullness (DS05)", spearman_test(*ds05_pairs("mono"), rng), TIDYP + "/DS05",
         known="monocytes with habitus already seen (EXP01)")

# T02s CCL2 (MCP-1) sensitivity
from_file("T02s", R, BR, "MCP-1, died vs survived (S-CB050)", "SV-04/out/contrasts.csv",
          {"file": "S-CB050", "analyte": "mcp1", "floor_handling": "as reported"}, "cliff_delta", "cliff_lo", "cliff_hi", "p", "12 vs 85",
          known="published severity finding (CB517)")
computed("T02s", B_, BR, "MCP-1 change baseline to day 4, log2 (DS02, SV-04 file)", sv04_ds02("mcp1"),
         "SV-04/out/ds02_courses.csv (dose contrast)", note=NOTE_B)
from_file("T02s", C, BR, "CD14, complicated vs uncomplicated (DS07)", "SV-06/b/out/ds07_candidates.csv", {"key": "cd14"},
          "delta", "delta_lo", "delta_hi", "p_stratified", "14 vs 18", known="published severity finding (CB112, same dogs)")
from_file("T02s", D_, BC, "MCP-1, complicated vs uncomplicated, day 1 (S-CB017)", "SV-04/out/contrasts.csv",
          {"file": "S-CB017", "analyte": "mcp1", "floor_handling": "as reported"}, "cliff_delta", "cliff_lo", "cliff_hi", "p", "18 vs 13",
          known="published severity finding (CB017)")
IND.append(dict(IND[[i for i, x in enumerate(IND) if x["theme"] == "T02" and x["source"] == F_][0]], theme="T02s"))

# T03 type 1 interferon
computed("T03", B_, BR, "type 1 interferon transcript score change (DS06)", sv08_dose("type1_interferon"), SV08 + " (dose contrast)",
         note=NOTE_B)

# T04 haemolysis and cell-free haemoglobin
hi, lo, nb = ds02_change("cfhb")
computed("T04", B_, BR, "cell-free haemoglobin change (DS02)", cliff_exact(hi, lo), TIDYP + "/DS02", note=NOTE_B + "; " + "; ".join(nb))
from_file("T04", C, BR, "haemoglobin beta, complicated vs uncomplicated (DS07)", "SV-06/b/out/ds07_candidates.csv", {"key": "hbb"},
          "delta", "delta_lo", "delta_hi", "p_stratified", "14 vs 18",
          note="label contains haematocrit < 0.15 and bilirubin > 30: partly restates the label; sample haemolysis not separable")

# T05 coagulation and platelet consumption (lower = more consumption, sign -1)
hi, lo, nb = ds02_change("plt")
computed("T05", B_, BR, "platelet change (DS02), lower = more consumption", cliff_exact(hi, lo), TIDYP + "/DS02", sign=-1, note=NOTE_B)
from_file("T05", C, BR, "antithrombin, complicated vs uncomplicated (DS07), lower = more consumption",
          "SV-06/b/out/ds07_candidates.csv", {"key": "serpinc1"}, "delta", "delta_lo", "delta_hi", "p_stratified", "14 vs 18", sign=-1)
computed("T05", D_, BC, "platelets, complicated vs uncomplicated, day 1 (S-CB017), lower = more consumption",
         cliff_test(*group_values(recs017, lab017, "plt"), rng), TIDYP + "/S-CB017", sign=-1)
computed("T05", F_, BR, "platelets with dullness (DS05), lower = more consumption", spearman_test(*ds05_pairs("plt"), rng),
         TIDYP + "/DS05", sign=-1)

# T07 anaemia (known driver)
computed("T07", B_, BR, "haematocrit drop at peak load (DS02, SV-02b file)", sv02b_peak("hct_drop"),
         "SV-02/b/out/reaction_norms.csv (dose contrast)", known="anaemia", note=NOTE_B)
computed("T07", D_, BC, "haematocrit, complicated vs uncomplicated, day 1 (S-CB017), lower = more anaemia",
         cliff_test(*group_values(recs017, lab017, "hct"), rng), TIDYP + "/S-CB017", sign=-1,
         circular="label: WHO complicated-malaria criteria include severe anaemia", known="anaemia")
computed("T07", F_, BR, "haematocrit with dullness (DS05), lower = more anaemia", spearman_test(*ds05_pairs("hct"), rng),
         TIDYP + "/DS05", sign=-1, known="anaemia (habitus with haematocrit already seen)")

# T08 inflammation against regeneration (SV-09 axis 2)
res9 = json.loads((EXP / "SV-09/out/results.json").read_text(encoding="utf-8"))
h2 = res9["step1"]["habitus"][1]
put("T08", F_, BR, "SV-09 residual axis 2 with dullness (partial, after haematocrit and illness days)", h2["partial_rho"],
    h2["ci"][0], h2["ci"][1], h2["p"], str(h2["n"]), "SV-09/out/results.json/step1/habitus/1", sign=-1,
    note="partial rho with habitus (higher = brighter) reversed to dullness")

# T09 parasite load and antibody
computed("T09", B_, BR, "peak parasitaemia before treatment (DS02, SV-02b file)", sv02b_peak_load(),
         "SV-02/b/out/reaction_norms.csv (dose contrast)", circular="dose sets the load by design", note=NOTE_B)
from_file("T09", O_, BC, "log parasite load, died vs survived (CB516, SV-02a file)", "SV-02/a/out/load_by_outcome.csv",
          {"unit": "CH21"}, "effect", "ci_lo", "ci_hi", "p_value", "8 vs 7", note="Hedges g from medians and ranges, not Cliff's delta")

# T10 host age (two-sided; positive = older in severe)
from_file("T10", R, BR, "age, died minus survived (S-CB050, SV-05 A3)", "SV-05/out/age_contrasts.csv", {"test": "A3"},
          "cliff_delta", "cliff_low", "cliff_high", "p", "15 vs 125")
computed("T10", F_, BR, "age with dullness (DS05)", spearman_test(*ds05_pairs("age_months"), rng), TIDYP + "/DS05")
computed("T10", O_, BC, "age, died vs survived (S-CB516)", cliff_test(*group_values(
    [r for r in s516["records"]], lab516, "age_months"), rng), TIDYP + "/S-CB516")

# T11 IL-10
from_file("T11", R, BR, "IL-10, died vs survived (S-CB050)", "SV-04/out/contrasts.csv",
          {"file": "S-CB050", "analyte": "il10", "floor_handling": "as reported"}, "cliff_delta", "cliff_lo", "cliff_hi", "p", "12 vs 85")
computed("T11", B_, BR, "IL-10 change baseline to day 4, log2 (DS02, SV-04 file)", sv04_ds02("il10"),
         "SV-04/out/ds02_courses.csv (dose contrast)", note=NOTE_B)
from_file("T11", D_, BC, "IL-10, complicated vs uncomplicated, day 1 (S-CB017)", "SV-04/out/contrasts.csv",
          {"file": "S-CB017", "analyte": "il10", "floor_handling": "as reported"}, "cliff_delta", "cliff_lo", "cliff_hi", "p", "18 vs 13")

# T12 lactate
computed("T12", B_, BR, "venous lactate at peak load (DS02, SV-02b file)", sv02b_peak("lactate"),
         "SV-02/b/out/reaction_norms.csv (dose contrast)", note=NOTE_B)

# T13 acute phase (CRP)
computed("T13", R, BR, "CRP, died vs survived (S-CB517 = S-CB050 dogs)", cliff_test(*group_values(recs517, lab517, "crp"), rng),
         TIDYP + "/S-CB517", known="published: no outcome difference (CB517, CB145)")
hi, lo, nb = ds02_change("crp")
computed("T13", B_, BR, "CRP change (DS02)", cliff_exact(hi, lo), TIDYP + "/DS02", note=NOTE_B)

# T14 size of the cytokine response
res4 = json.loads((EXP / "SV-04/out/results.json").read_text(encoding="utf-8"))
for src, f, sp, circ in ((R, "S-CB050", BR, ""), (D_, "S-CB017", BC, "label: SIRS")):
    d = res4["experiment2"]["by_file"][f]["T1_perturbation"]
    put("T14", src, sp, f"cytokine perturbation count ({f}, SV-04)", d["cliff_delta"], d["cliff_lo"], d["cliff_hi"], d["p"],
        f"{d['n_severe']} vs {d['n_nonsevere']}", f"SV-04/out/results.json/experiment2/by_file/{f}/T1_perturbation", circular=circ)

THEMES = {
    "T01": ("Neutrophil activation and left shift", "higher"),
    "T02": ("Monocyte and macrophage activation", "higher"),
    "T02s": ("Monocyte activation, sensitivity with CCL2 (MCP-1)", "higher"),
    "T03": ("Type 1 interferon response", "higher"),
    "T04": ("Haemolysis and cell-free haemoglobin", "higher"),
    "T05": ("Coagulation and platelet consumption", "more consumption"),
    "T06": ("Endocrine stress response (cortisol, thyroid)", "higher cortisol, lower thyroid"),
    "T07": ("Anaemia (known driver)", "more anaemia"),
    "T08": ("Inflammation against regeneration at a given haematocrit", "higher"),
    "T09": ("Parasite load and antibody", "higher load"),
    "T10": ("Host age", "two-sided"),
    "T11": ("Anti-inflammatory IL-10", "higher"),
    "T12": ("Lactate and hypoperfusion", "higher"),
    "T13": ("Acute phase response (CRP)", "higher"),
    "T14": ("Size of the cytokine response", "higher"),
}

# literature calls beside each theme (SV-03 unit_calls.csv), excluding units that are dog-level sources here
LIT_MARKERS = {"T01": ["Band neutrophils"], "T02": ["Monocyte count"], "T02s": ["MCP-1 (CCL2)"], "T05": ["Platelet count"],
               "T06": ["Cortisol", "Thyroid hormones"], "T07": ["Haematocrit/PCV"], "T09": ["Parasitaemia"], "T10": ["Age"],
               "T11": ["IL-10"], "T12": ["Lactate"], "T13": ["C-reactive protein"]}
SAME_DOGS = {"CH03", "CB112", "CH23", "CH21", "CH09"}
lit = {}
for ln, r in read_csv("SV-03/out/unit_calls.csv"):
    for t, ms in LIT_MARKERS.items():
        if r["marker"] in ms and r["independent_unit"] not in SAME_DOGS and r["family"] == "univariable":
            lit.setdefault(t, {}).setdefault(r["species_group"], []).append(f"{r['independent_unit']}:{r['marker']}:{r['unit_call']}")


def lit_summary(t):
    out = []
    for sp, calls in sorted(lit.get(t, {}).items()):
        units = {}
        for c in calls:
            u, m, call = c.split(":")
            units.setdefault(u, set()).add(call)
        h = sum(1 for v in units.values() if "H" in v and "L" not in v)
        l_ = sum(1 for v in units.values() if "L" in v and "H" not in v)
        n = sum(1 for v in units.values() if v <= {"N", "U", "D"} and "N" in v)
        out.append(f"{sp}: {h} higher, {l_} lower, {n} not significant ({len(units)} units)")
    return "; ".join(out)


# ------------------------------------------------------------------ combination
def signed_z(ind):
    p = min(max(ind["p"], 1e-12), 1.0)
    z = stats.norm.isf(p / 2)
    return z if ind["oriented"] > 0 else -z


def combine(inds, two_sided=False):
    zs = [signed_z(i) for i in inds]
    k = len(zs)
    Z = sum(zs) / sqrt(k)
    p_st = 2 * stats.norm.sf(abs(Z)) if two_sided else float(stats.norm.sf(Z))
    one = [i["p"] / 2 if i["oriented"] > 0 else 1 - i["p"] / 2 for i in inds]
    chi = -2 * sum(np.log(max(x, 1e-300)) for x in one)
    p_f = float(stats.chi2.sf(chi, 2 * k))
    pos = sum(1 for i in inds if i["oriented"] > 0)
    p_sign = float(stats.binomtest(pos, k, 0.5, alternative="greater").pvalue) if not two_sided else \
        float(stats.binomtest(pos, k, 0.5).pvalue)
    loso = []
    for j in range(k):
        rest = [z for i, z in enumerate(zs) if i != j]
        Zr = sum(rest) / sqrt(len(rest))
        loso.append(2 * stats.norm.sf(abs(Zr)) if two_sided else float(stats.norm.sf(Zr)))
    return dict(k=k, Z=Z, p_stouffer=p_st, p_fisher=p_f, positive=pos, p_sign=p_sign,
                loso_max=max(loso) if loso else None, loso_detail=loso)


rows = []
primary_idx = []
for t, (label, direction) in THEMES.items():
    inds = [i for i in IND if i["theme"] == t]
    for i in inds:
        rows.append(dict(theme=t, theme_label=label, row_type="indicator", source=i["source"], species=i["species"],
                         measure=i["measure"], n=i["n"], effect=i["effect"], sign=i["sign"], oriented_effect=i["oriented"],
                         ci_low=i["ci_low"], ci_high=i["ci_high"], p=i["p"], circular=i["circular"], known_driver=i["known_driver"],
                         provenance=i["provenance"], note=i["note"]))
    two = direction == "two-sided"
    for scope, sel in (("B. rossi", lambda i: i["species"] == BR), ("B. canis", lambda i: i["species"] == BC),
                       ("all sources (transfer check)", lambda i: True)):
        use = [i for i in inds if sel(i) and not i["circular"] and i["oriented"] is not None]
        if len(use) < 2:
            continue
        if scope.startswith("all") and len(use) == len([i for i in inds if i["species"] == BR and not i["circular"]]):
            continue  # no B. canis indicator added: same as the B. rossi row
        c = combine(use, two)
        row = dict(theme=t, theme_label=label, row_type="combined", source="; ".join(i["source"] for i in use), species=scope,
                   measure=f"{len(use)} sources: Stouffer Z {c['Z']:.2f}", n=str(c["k"]), effect=round(c["Z"], 4), sign="",
                   oriented_effect=round(c["Z"], 4), ci_low="", ci_high="", p=round(c["p_stouffer"], 6),
                   p_fisher=round(c["p_fisher"], 6), sources_in_direction=f"{c['positive']} of {c['k']}",
                   p_sign=round(c["p_sign"], 4), loso_max_p=round(c["loso_max"], 6),
                   circular="", known_driver="; ".join(sorted({i["known_driver"] for i in use if i["known_driver"]})),
                   provenance="computed here", note="themes chosen after the results were seen" + ("; two-sided" if two else "; one-sided"))
        rows.append(row)
        if scope == "B. rossi" and t != "T02s":
            primary_idx.append(len(rows) - 1)
    if not inds:
        rows.append(dict(theme=t, theme_label=label, row_type="literature_only", source="LIT", species="", measure="no dog-level indicator",
                         note="literature direction calls only"))
for r in rows:
    r["literature_calls"] = lit_summary(r["theme"]) if r["row_type"] != "indicator" else ""

q = bh([rows[i]["p"] for i in primary_idx])
for j, i in enumerate(primary_idx):
    rows[i]["q_themes"] = round(float(q[j]), 6)
    rows[i]["m_themes"] = len(primary_idx)
    rows[i]["bonferroni_p"] = round(min(1.0, rows[i]["p"] * len(primary_idx)), 6)

FIELDS = ["theme", "theme_label", "row_type", "source", "species", "measure", "n", "effect", "sign", "oriented_effect", "ci_low",
          "ci_high", "p", "p_fisher", "sources_in_direction", "p_sign", "loso_max_p", "q_themes", "m_themes", "bonferroni_p",
          "circular", "known_driver", "literature_calls", "provenance", "note"]
with (OUT / "themes.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if r.get(k) is None else r.get(k, "")) for k in FIELDS})
(OUT / "theme_indicators.json").write_text(json.dumps(IND, indent=1, allow_nan=False), encoding="utf-8")
print(f"theme rows {len(rows)}; indicators {len(IND)}; primary combined rows {len(primary_idx)}")
for r in rows:
    if r["row_type"] == "combined":
        print(r["theme"], r["species"], r["source"], "Z", r["effect"], "p", r["p"], "q", r.get("q_themes", ""), "loso", r["loso_max_p"],
              r["sources_in_direction"])
