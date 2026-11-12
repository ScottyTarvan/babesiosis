"""SV-03: severity definition map and marker-evidence matrix.

Reads the SV-G2 extraction (published group results only) and writes out/*.csv and out/results.json.
Run: env/py/Scripts/python -I scripts/analyse.py   (from /experiments/SV-03)
Spec: spec.md (frozen before the first run).
"""
import csv, json, math, re, os, sys, hashlib, collections as C
import numpy as np
from scipy import stats, optimize

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
EXP = os.path.dirname(PKG)
ROOT = os.path.dirname(EXP)
OUT = os.path.join(PKG, "out")
os.makedirs(OUT, exist_ok=True)

ASSOC = os.path.join(EXP, "SV-G2", "associations_v2.csv")
DEFS = os.path.join(EXP, "SV-G2", "definitions_v2.csv")
ARTICLES = os.path.join(ROOT, "core", "articles.jsonl")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def read_csv(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(name, rows, cols):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})


A = read_csv(ASSOC)
D = read_csv(DEFS)

# ---------------------------------------------------------------- harmonisation
def species_group(text):
    t = (text or "").lower()
    has = {k: (k in t) for k in ("rossi", "canis", "gibsoni", "vogeli")}
    if "mixed" in t and "44/45" not in t:
        return "mixed/unspecified", False
    if has["rossi"] and not has["gibsoni"] and not has["vogeli"]:
        return "B. rossi", ("presum" in t or "likely" in t)
    if has["canis"] and not has["rossi"] and not has["gibsoni"] and (not has["vogeli"] or "44/45" in t):
        return "B. canis", ("suspect" in t)
    if has["gibsoni"] and not (has["rossi"] or has["canis"] or has["vogeli"]):
        return "B. gibsoni", False
    if has["vogeli"] and not (has["rossi"] or has["canis"] or has["gibsoni"]):
        return "B. vogeli", False
    return "mixed/unspecified", False


SIGN = {"higher_in_severe": 1, "more_frequent_in_severe": 1, "positive_association": 1,
        "lower_in_severe": -1, "less_frequent_in_severe": -1, "negative_association": -1,
        "no_difference": 0, "mixed": None, "not_stated": None}
UNIVARIABLE = {"group_comparison", "proportion_comparison", "correlation", "univariable_regression", "roc",
               "survival_analysis"}


def row_call(r):
    s = SIGN.get(r["direction"])
    sig = r["significant"]
    if sig == "yes":
        return "H" if s == 1 else "L" if s == -1 else "U"
    if sig == "no":
        return "N"
    if sig == "unclear":
        return "U"
    return "D"


def unit_call(calls, strict=False):
    tested = [c for c in calls if c in "HLN"]
    if strict:
        if tested and all(c == "H" for c in tested):
            return "H"
        if tested and all(c == "L" for c in tested):
            return "L"
        if tested:
            return "N"
    else:
        if "H" in calls and "L" in calls:
            return "X"
        for c in "HLN":
            if c in calls:
                return c
    if "U" in calls:
        return "U"
    return "D"


# --------------------------------------------------- definition components / circularity
COMPONENT_MARKERS = {
    "renal": ["Creatinine", "Urea", "Urine specific gravity", "Urine protein:creatinine ratio", "SDMA", "Cystatin C",
              "Urea:creatinine ratio", "Urinary kidney injury biomarkers", "Urine creatinine",
              "Fractional excretion of electrolytes", "Urine osmolality", "Plasma NGAL"],
    "hepatic or icterus": ["Bilirubin", "ALT", "ALP", "AST", "GGT", "Icterus"],
    "anaemia grade": ["Haematocrit/PCV", "Haemoglobin", "Red blood cell count"],
    "haemoconcentration": ["Haematocrit/PCV", "Haemoglobin", "Red blood cell count"],
    "hypoglycaemia": ["Glucose"],
    "hyperlactataemia": ["Lactate"],
    "pancreatitis": ["Pancreatic enzymes (lipase, amylase, cPLI)"],
    "rhabdomyolysis": ["Creatine kinase"],
    "coagulopathy": ["Platelet count", "Prothrombin time", "aPTT", "Fibrinogen", "D-dimer",
                     "Coagulation factor activity", "Antithrombin", "Viscoelastic testing (TEG/ROTEM)"],
    "SIRS": ["White blood cell count", "Body temperature", "Heart rate", "Respiratory rate / dyspnoea", "SIRS status",
             "Band neutrophils"],
    "collapse": ["Collapse"],
    "cerebral": ["Mentation / neurological signs"],
    "pulmonary": ["Respiratory rate / dyspnoea", "Blood gases and oxygenation"],
    "hypotension or shock": ["Blood pressure"],
}
OUTCOME_CLASS_MARKERS = {
    "anaemia_grade": ["Haematocrit/PCV", "Haemoglobin", "Red blood cell count"],
    "parasitaemia_level": ["Parasitaemia", "Parasite DNA load (qPCR)"],
}
# keywords searched in the definition text (lower case, word-bounded)
MARKER_KEYWORDS = {
    "Creatinine": ["creatinine"], "Urea": ["urea", "bun"], "Bilirubin": ["bilirubin"], "ALT": ["alt"],
    "ALP": ["alp", "ap"], "Haematocrit/PCV": ["haematocrit", "hematocrit", "pcv", "hct", "ht"],
    "Haemoglobin": ["haemoglobin", "hemoglobin", "hgb"], "Glucose": ["glucose", "hypoglyc\\w*"],
    "Lactate": ["lactate", "hyperlactat\\w*"], "Platelet count": ["platelet\\w*", "thrombocytopen\\w*"],
    "Creatine kinase": ["cpk", "ck", "creatine kinase"],
    "Pancreatic enzymes (lipase, amylase, cPLI)": ["cpl\\w*", "lipase"],
    "Parasitaemia": ["parasitaemia", "parasitemia"], "White blood cell count": ["wbc", "leukocyt\\w*", "leucocyt\\w*"],
    "Body temperature": ["temperature", "pyrexia", "fever"], "Collapse": ["collaps\\w*"],
    "Urine specific gravity": ["usg", "specific gravity"], "Icterus": ["icter\\w*", "jaundice\\w*"],
    "Blood gases and oxygenation": ["pao2", "spo2", "hypoxaem\\w*"],
}


def kw_in(text, kws):
    t = (text or "").lower()
    return any(re.search(r"(?<![a-z0-9])" + k + r"(?![a-z0-9])", t) for k in kws)


DEFKEY = {(d["id"], d["severity_key"]): d for d in D}


def circular(r):
    d = DEFKEY.get((r["id"], r["severity_key"]))
    comps = [c.strip() for c in (r["components"] or "").split(";") if c.strip()]
    m = r["marker"]
    why = []
    for c in comps:
        if m in COMPONENT_MARKERS.get(c, []):
            why.append("component:" + c)
    if m in OUTCOME_CLASS_MARKERS.get(r["outcome_class"], []):
        why.append("outcome class:" + r["outcome_class"])
    if d is not None and m in MARKER_KEYWORDS and kw_in(d["definition"] + " " + d["severity_label"], MARKER_KEYWORDS[m]):
        why.append("named in definition text")
    return why


# --------------------------------------------------------------- sensitivity sets
OP_ROSSI_UNITS = {"CH03", "CB040", "CB035", "CB053", "CB112", "CB125", "CB342", "CB376", "CB418", "CH29", "CH31", "CH04"}
S2_DROP = {"CB105", "CB045", "CB098", "CB441", "CB418", "CB187", "CB537"}

for r in A:
    r["sg"], r["sg_presumed"] = species_group(r["species"] or r["article_species"])
    r["call"] = row_call(r)
    r["family"] = ("multivariable" if r["analysis"] == "multivariable_regression"
                   else "descriptive" if r["analysis"] == "descriptive_only" else "univariable")
    r["circ_why"] = circular(r)
    r["circ"] = bool(r["circ_why"])
    r["unit_s1"] = ("OP-rossi" if (r["sg"] == "B. rossi" and r["independent_unit"] in OP_ROSSI_UNITS)
                    else r["independent_unit"])

# ------------------------------------------------------------------ STEP 1: definition map
def_rows = []
for d in D:
    sg, pres = species_group(d["article_species"])
    rows = [r for r in A if r["id"] == d["id"] and r["severity_key"] == d["severity_key"]]
    sgs = sorted({r["sg"] for r in rows}) or [sg]
    comps = [c.strip() for c in (d["components"] or "").split(";") if c.strip()]
    tested = [r for r in rows if r["call"] in "HLN"]
    def_rows.append({
        "id": d["id"], "independent_unit": d["independent_unit"], "species_group": ";".join(sgs),
        "setting": d["setting"], "sample_timing": d["sample_timing"], "severity_key": d["severity_key"],
        "outcome_class": d["outcome_class"], "severity_label": d["severity_label"], "components": ";".join(comps),
        "n_components": len(comps), "euthanasia_included": d["euthanasia_included"],
        "definition_source": d["definition_source"], "follow_up_horizon": d["follow_up_horizon"],
        "n_rows": len(rows), "n_tested_rows": len(tested),
        "n_tested_rows_marker_in_definition": sum(1 for r in tested if r["circ"]),
        "markers_in_definition": ";".join(sorted({r["marker"] for r in rows if r["circ"]})),
    })
write_csv("definition_map.csv", def_rows, list(def_rows[0].keys()))

SG_ORDER = ["B. rossi", "B. canis", "B. gibsoni", "B. vogeli", "mixed/unspecified"]
comp_units = C.defaultdict(lambda: C.defaultdict(set))
oc_units = C.defaultdict(lambda: C.defaultdict(set))
for d in def_rows:
    for sg in d["species_group"].split(";"):
        for c in d["components"].split(";"):
            if c:
                comp_units[c][sg].add(d["independent_unit"])
                comp_units[c]["all"].add(d["independent_unit"])
        oc_units[d["outcome_class"]][sg].add(d["independent_unit"])
        oc_units[d["outcome_class"]]["all"].add(d["independent_unit"])
all_def_units = {d["independent_unit"] for d in def_rows}
comp_rows = []
for c, v in sorted(comp_units.items(), key=lambda kv: -len(kv[1]["all"])):
    row = {"component": c, "units_all": len(v["all"]), "share_of_units": round(len(v["all"]) / len(all_def_units), 3)}
    for sg in SG_ORDER:
        row[sg] = len(v.get(sg, ()))
    comp_rows.append(row)
write_csv("definition_components.csv", comp_rows, ["component", "units_all", "share_of_units"] + SG_ORDER)
oc_rows = []
for c, v in sorted(oc_units.items(), key=lambda kv: -len(kv[1]["all"])):
    row = {"outcome_class": c, "units_all": len(v["all"])}
    for sg in SG_ORDER:
        row[sg] = len(v.get(sg, ()))
    oc_rows.append(row)
write_csv("definition_outcome_classes.csv", oc_rows, ["outcome_class", "units_all"] + SG_ORDER)

tested_rows = [r for r in A if r["call"] in "HLN"]
circ_tested = [r for r in tested_rows if r["circ"]]
units_with_circ = {r["independent_unit"] for r in circ_tested}
units_tested = {r["independent_unit"] for r in tested_rows}
circ_sig = sum(1 for r in circ_tested if r["call"] in "HL")
noncirc_sig = sum(1 for r in tested_rows if not r["circ"] and r["call"] in "HL")
circ_summary = {
    "tested_rows": len(tested_rows), "tested_rows_marker_in_definition": len(circ_tested),
    "share_rows": round(len(circ_tested) / len(tested_rows), 3),
    "units_tested": len(units_tested), "units_with_marker_in_definition": len(units_with_circ),
    "share_units": round(len(units_with_circ) / len(units_tested), 3),
    "share_significant_circular": round(circ_sig / max(1, len(circ_tested)), 3),
    "share_significant_noncircular": round(noncirc_sig / max(1, len(tested_rows) - len(circ_tested)), 3),
    "definitions": len(def_rows), "definition_units": len(all_def_units),
    "euthanasia_in_mortality": dict(C.Counter(d["euthanasia_included"] or "not stated" for d in def_rows
                                              if d["outcome_class"] == "mortality")),
    "component_count_median": float(np.median([d["n_components"] for d in def_rows])),
}
circ_reasons = C.Counter()
for r in circ_tested:
    for w in r["circ_why"]:
        circ_reasons[(r["marker"], w)] += 1
write_csv("circularity.csv",
          [{"marker": m, "reason": w, "tested_rows": n} for (m, w), n in circ_reasons.most_common()],
          ["marker", "reason", "tested_rows"])

# ------------------------------------------------------------------ STEP 2: evidence matrix
def build_matrix(rows, unit_key="independent_unit", strict=False, drop_circ=False):
    cells = C.defaultdict(lambda: C.defaultdict(list))   # cell -> unit -> calls
    mv = C.defaultdict(lambda: C.defaultdict(list))
    circ_units = C.defaultdict(set)
    pres_units = C.defaultdict(set)
    cls = {}
    for r in rows:
        if drop_circ and r["circ"]:
            continue
        cell = (r["marker"], r["outcome_class"], r["sg"])
        cls[cell] = r["marker_class"]
        if r["circ"]:
            circ_units[cell].add(r[unit_key])
        if r["sg_presumed"]:
            pres_units[cell].add(r[unit_key])
        if r["family"] == "multivariable":
            mv[cell][r[unit_key]].append(r["call"])
        else:
            cells[cell][r[unit_key]].append(r["call"])
    out = {}
    for cell in set(cells) | set(mv):
        uc = {u: unit_call(c, strict) for u, c in cells[cell].items()}
        cnt = C.Counter(uc.values())
        tested = cnt["H"] + cnt["L"] + cnt["N"] + cnt["X"]
        top = max(("H", "L"), key=lambda k: cnt[k])
        opp = "L" if top == "H" else "H"
        consistent = (tested >= 2 and cnt[top] >= 2 and cnt[top] / tested >= 2 / 3 and cnt[opp] == 0
                      and cnt["X"] == 0)
        mvc = {u: unit_call(c) for u, c in mv[cell].items()}
        out[cell] = {"marker": cell[0], "marker_class": cls[cell], "outcome_class": cell[1], "species_group": cell[2],
                     "units": len(uc), "tested_units": tested, "H": cnt["H"], "L": cnt["L"], "N": cnt["N"],
                     "X": cnt["X"], "U": cnt["U"], "D": cnt["D"],
                     "consistent": consistent, "consistent_direction": (("higher" if top == "H" else "lower")
                                                                        if consistent else ""),
                     "multivariable_units": len(mvc),
                     "multivariable_calls": ";".join(f"{u}:{c}" for u, c in sorted(mvc.items())),
                     "circular_units": len(circ_units[cell]), "circular": bool(circ_units[cell]),
                     "presumed_species_units": ";".join(sorted(pres_units[cell])),
                     "unit_calls": ";".join(f"{u}:{c}" for u, c in sorted(uc.items()))}
    return out


M = build_matrix(A)
M_s1 = build_matrix(A, unit_key="unit_s1")
M_s2 = build_matrix([r for r in A if r["id"] not in S2_DROP])
M_s3 = build_matrix(A, strict=True)
M_s4 = build_matrix(A, drop_circ=True)
SENS = {"S1_onderstepoort_collapse": M_s1, "S2_no_judgement_calls": M_s2, "S3_strict_unit_rule": M_s3,
        "S4_no_circular_units": M_s4}

matrix_rows = []
for cell, v in sorted(M.items(), key=lambda kv: (-kv[1]["tested_units"], kv[0])):
    row = dict(v)
    for k, MM in SENS.items():
        w = MM.get(cell)
        row[k] = ("" if w is None else
                  f"{w['tested_units']}t {w['H']}H/{w['L']}L/{w['N']}N/{w['X']}X" + (" consistent" if w["consistent"] else ""))
        row[k + "_consistent"] = bool(w and w["consistent"])
    matrix_rows.append(row)
mcols = ["marker", "marker_class", "outcome_class", "species_group", "units", "tested_units", "H", "L", "N", "X", "U",
         "D", "consistent", "consistent_direction", "circular", "circular_units", "presumed_species_units",
         "multivariable_units", "multivariable_calls", "unit_calls"] + [k for k in SENS] + [k + "_consistent" for k in SENS]
write_csv("evidence_matrix.csv", matrix_rows, mcols)

# unit-level calls (long format)
uc_rows = []
groups = C.defaultdict(list)
for r in A:
    groups[(r["marker"], r["outcome_class"], r["sg"], r["independent_unit"], r["family"])].append(r)
for (m, oc, sg, u, fam), rs in sorted(groups.items()):
    uc_rows.append({"marker": m, "outcome_class": oc, "species_group": sg, "independent_unit": u, "family": fam,
                    "articles": ";".join(sorted({r["id"] for r in rs})), "rows": len(rs),
                    "row_calls": "".join(r["call"] for r in rs), "unit_call": unit_call([r["call"] for r in rs]),
                    "circular": any(r["circ"] for r in rs),
                    "timing": ";".join(sorted({r["sample_timing"] for r in rs})),
                    "setting": ";".join(sorted({r["setting"] for r in rs}))})
write_csv("unit_calls.csv", uc_rows, list(uc_rows[0].keys()))

# ------------------------------------------------------------------ STEP 3: pooling
def norm(s):
    s = (s or "").replace("−", "-").replace("±", " +- ")
    s = re.sub(r"[nN]\s*=\s*\d+", " ", s)
    s = re.sub(r"(\d),(\d)", r"\1.\2", s)
    s = re.sub(r"(\d)\s*[–—-]\s*(?=\d)", r"\1 to ", s)
    return s


def nums(s):
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", norm(s))]


def qnorm(p):
    return stats.norm.ppf(p)


def mean_sd(val, st, n):
    x = nums(val)
    if st in ("mean and SD", "mean and SEM"):
        if len(x) < 2:
            return None
        m, s = x[0], x[1]
        if st == "mean and SEM":
            s = s * math.sqrt(n)
        return m, s
    if st == "median and IQR":
        if len(x) < 3:
            return None
        m, q1, q3 = x[0], x[1], x[2]
        if not (q1 <= m <= q3):
            return None
        return (q1 + m + q3) / 3, (q3 - q1) / (2 * qnorm((0.75 * n - 0.125) / (n + 0.25)))
    if st == "median and range":
        if len(x) < 3:
            return None
        m, a, b = x[0], x[1], x[2]
        if not (a <= m <= b):
            return None
        return (a + 2 * m + b) / 4, (b - a) / (2 * qnorm((n - 0.375) / (n + 0.25)))
    return None


def to_int(s):
    try:
        return int(float(norm(s).split()[0]))
    except Exception:
        return None


def hedges(r):
    n1, n2 = to_int(r["n_severe"]), to_int(r["n_comparison"])
    if not n1 or not n2 or n1 < 2 or n2 < 2:
        return None
    a, b = mean_sd(r["severe_value"], r["summary_type"], n1), mean_sd(r["comparison_value"], r["summary_type"], n2)
    if not a or not b or a[1] <= 0 or b[1] <= 0:
        return None
    sp = math.sqrt(((n1 - 1) * a[1] ** 2 + (n2 - 1) * b[1] ** 2) / (n1 + n2 - 2))
    d = (a[0] - b[0]) / sp
    J = 1 - 3 / (4 * (n1 + n2) - 9)
    g = J * d
    v = (n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2))
    return g, v, n1 + n2


def fisher(r):
    if r["effect_type"] not in ("r", "rho"):
        return None
    x = nums(r["effect_value"])
    n = to_int(r["n_total"])
    if not x or not n or n < 5 or abs(x[0]) >= 1:
        return None
    s = SIGN.get(r["direction"])
    rr = abs(x[0]) * (s if s in (1, -1) else (1 if x[0] >= 0 else -1))
    return math.atanh(rr), 1 / (n - 3), n


def log_or(r):
    def frac(s, n):
        s = norm(s)
        m = re.search(r"(\d+)\s*/\s*(\d+)", s) or re.search(r"(\d+)\s+of\s+(\d+)", s)
        if m:
            return int(m.group(1)), int(m.group(2))
        m = re.match(r"\s*(\d+)\b", s)
        if m and n:
            return int(m.group(1)), n
        return None
    if r["summary_type"] != "count and percent":
        return None
    a = frac(r["severe_value"], to_int(r["n_severe"]))
    b = frac(r["comparison_value"], to_int(r["n_comparison"]))
    if not a or not b or a[0] > a[1] or b[0] > b[1]:
        return None
    x1, n1 = a
    x2, n2 = b
    c = 0.5 if 0 in (x1, n1 - x1, x2, n2 - x2) else 0
    lo = math.log(((x1 + c) * (n2 - x2 + c)) / ((n1 - x1 + c) * (x2 + c)))
    v = 1 / (x1 + c) + 1 / (n1 - x1 + c) + 1 / (x2 + c) + 1 / (n2 - x2 + c)
    return lo, v, n1 + n2


def timing_rank(r):
    t = (r["sample_timing"] or "") + " " + (r["timepoint"] or "")
    t = t.lower()
    if "before treatment" in t or "pre-treatment" in t:
        return 0
    if any(k in t for k in ("admission", "presentation", "diagnosis", "day 0")):
        return 1
    return 2


def reml(y, v):
    y, v = np.asarray(y), np.asarray(v)
    k = len(y)

    def nll(t2):
        w = 1 / (v + t2)
        mu = np.sum(w * y) / np.sum(w)
        return 0.5 * (np.sum(np.log(v + t2)) + np.log(np.sum(w)) + np.sum(w * (y - mu) ** 2))
    res = optimize.minimize_scalar(nll, bounds=(0, max(10.0, 10 * np.var(y) + 1)), method="bounded")
    t2 = max(0.0, float(res.x))
    if nll(0.0) <= nll(t2):
        t2 = 0.0
    w = 1 / (v + t2)
    mu = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * (y - mu) ** 2) / (k - 1))
    se_hk = math.sqrt(max(q, 1e-12) / np.sum(w))
    tcrit = stats.t.ppf(0.975, k - 1)
    # DerSimonian-Laird
    w0 = 1 / v
    mu0 = np.sum(w0 * y) / np.sum(w0)
    Q = float(np.sum(w0 * (y - mu0) ** 2))
    t2dl = max(0.0, (Q - (k - 1)) / (np.sum(w0) - np.sum(w0 ** 2) / np.sum(w0)))
    wd = 1 / (v + t2dl)
    mud = float(np.sum(wd * y) / np.sum(wd))
    sed = math.sqrt(1 / np.sum(wd))
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    pi = None
    if k >= 3:
        tp = stats.t.ppf(0.975, k - 2)
        s = math.sqrt(t2 + se_hk ** 2)
        pi = (mu - tp * s, mu + tp * s)
    return {"k": k, "estimate": mu, "ci_low": mu - tcrit * se_hk, "ci_high": mu + tcrit * se_hk, "tau2": t2,
            "dl_estimate": mud, "dl_ci_low": mud - 1.96 * sed, "dl_ci_high": mud + 1.96 * sed, "I2": I2, "Q": Q,
            "pi_low": pi[0] if pi else None, "pi_high": pi[1] if pi else None}


EXTRACTORS = {"SMD (Hedges g)": hedges, "Fisher z (correlation)": fisher, "log odds ratio": log_or}
cand = C.defaultdict(lambda: C.defaultdict(list))
usable_rows = 0
for r in A:
    if r["family"] != "univariable":
        continue
    for kind, f in EXTRACTORS.items():
        if kind == "SMD (Hedges g)" and r["analysis"] != "group_comparison":
            continue
        e = f(r)
        if e:
            usable_rows += 1
            cand[(r["marker"], r["outcome_class"], r["sg"], kind)][r["independent_unit"]].append((r, e))

pooled_rows, pooled_points = [], []
cells_ge2_usable = 0
for key, units in sorted(cand.items()):
    if len(units) >= 2:
        cells_ge2_usable += 1
    if len(units) < 3:
        continue
    chosen = []
    for u, lst in sorted(units.items()):
        lst.sort(key=lambda re_: (timing_rank(re_[0]), -re_[1][2], int(re_[0]["row"])))
        chosen.append((u, lst[0]))
    y = [c[1][1][0] for c in chosen]
    v = [c[1][1][1] for c in chosen]
    res = reml(y, v)
    back = (lambda z: math.tanh(z)) if key[3].startswith("Fisher") else (
        (lambda z: math.exp(z)) if key[3] == "log odds ratio" else (lambda z: z))
    circ = any(c[1][0]["circ"] for c in chosen)
    row = {"marker": key[0], "outcome_class": key[1], "species_group": key[2], "effect": key[3],
           "k_units": res["k"], "units": ";".join(c[0] for c in chosen),
           "articles": ";".join(c[1][0]["id"] for c in chosen),
           "estimate": back(res["estimate"]), "ci_low": back(res["ci_low"]), "ci_high": back(res["ci_high"]),
           "pi_low": None if res["pi_low"] is None else back(res["pi_low"]),
           "pi_high": None if res["pi_high"] is None else back(res["pi_high"]),
           "dl_estimate": back(res["dl_estimate"]), "dl_ci_low": back(res["dl_ci_low"]),
           "dl_ci_high": back(res["dl_ci_high"]), "tau2": res["tau2"], "I2": res["I2"],
           "n_dogs": sum(c[1][1][2] for c in chosen), "circular": circ,
           "s1_units": len({("OP-rossi" if (key[2] == "B. rossi" and c[0] in OP_ROSSI_UNITS) else c[0])
                            for c in chosen})}
    pooled_rows.append(row)
    for u, (r, e) in chosen:
        se = math.sqrt(e[1])
        pooled_points.append({"marker": key[0], "outcome_class": key[1], "species_group": key[2], "effect": key[3],
                              "unit": u, "article": r["id"], "row": r["row"], "n": e[2],
                              "estimate": back(e[0]), "ci_low": back(e[0] - 1.96 * se),
                              "ci_high": back(e[0] + 1.96 * se), "timepoint": r["timepoint"],
                              "summary_type": r["summary_type"], "circular": r["circ"]})
pcols = ["marker", "outcome_class", "species_group", "effect", "k_units", "units", "articles", "n_dogs", "estimate",
         "ci_low", "ci_high", "pi_low", "pi_high", "dl_estimate", "dl_ci_low", "dl_ci_high", "tau2", "I2", "circular",
         "s1_units"]
if not pooled_rows:
    pooled_rows_out = []
else:
    pooled_rows_out = pooled_rows
write_csv("pooled.csv", pooled_rows_out, pcols)
write_csv("pooled_points.csv", pooled_points,
          ["marker", "outcome_class", "species_group", "effect", "unit", "article", "row", "n", "estimate", "ci_low",
           "ci_high", "timepoint", "summary_type", "circular"])
# cells with 2 usable units (near misses) for the report
near = [{"marker": k[0], "outcome_class": k[1], "species_group": k[2], "effect": k[3], "k_units": len(u),
         "units": ";".join(sorted(u))} for k, u in sorted(cand.items()) if len(u) == 2]
write_csv("pooling_near_misses.csv", near, ["marker", "outcome_class", "species_group", "effect", "k_units", "units"])

# ------------------------------------------------------------------ STEP 4: named conflicts
CONFLICTS = [
    ("IL-8", ["IL-8 (CXCL8)"], None),
    ("Fibrinogen", ["Fibrinogen"], None),
    ("aPTT", ["aPTT"], None),
    ("MDA", ["Malondialdehyde / TBARS"], None),
    ("SOD and catalase", ["Superoxide dismutase", "Catalase"], None),
    ("Parasitaemia", ["Parasitaemia", "Parasite DNA load (qPCR)"], None),
    ("Platelets against death", ["Platelet count"], "mortality"),
    ("Lactate", ["Lactate"], None),
    ("MCP-1 (candidate, SV-04)", ["MCP-1 (CCL2)"], None),
]
conf_rows, conf_units = [], []
for name, markers, oc_only in CONFLICTS:
    rs = [r for r in A if r["marker"] in markers and (oc_only is None or r["outcome_class"] == oc_only)
          and r["family"] != "descriptive"]
    allrs = [r for r in A if r["marker"] in markers and (oc_only is None or r["outcome_class"] == oc_only)]
    g = C.defaultdict(list)
    for r in rs:
        g[(r["independent_unit"], r["sg"], r["outcome_class"], r["marker"], r["family"])].append(r)
    units = []
    for (u, sg, oc, m, fam), lst in sorted(g.items()):
        call = unit_call([x["call"] for x in lst])
        units.append({"conflict": name, "unit": u, "articles": ";".join(sorted({x["id"] for x in lst})),
                      "marker": m, "species_group": sg, "outcome_class": oc, "family": fam, "call": call,
                      "row_calls": "".join(x["call"] for x in lst),
                      "timing": ";".join(sorted({x["sample_timing"] for x in lst})),
                      "setting": ";".join(sorted({x["setting"] for x in lst})),
                      "circular": any(x["circ"] for x in lst)})
    conf_units += units
    sigH = [x for x in units if x["call"] in ("H", "X") and x["family"] == "univariable"]
    sigL = [x for x in units if x["call"] in ("L", "X") and x["family"] == "univariable"]
    n_units = len({x["unit"] for x in units})
    desc_units = len({r["independent_unit"] for r in allrs}) - n_units
    if not sigH or not sigL or (len(sigH) == 1 and sigH == sigL and sigH[0]["call"] != "X"):
        verdict = "no conflict in the extracted evidence"
    else:
        pairs = [(a, b) for a in sigH for b in sigL if a is not b or a["call"] == "X"]
        if all(a["species_group"] != b["species_group"] for a, b in pairs):
            verdict = "aliased with species"
        elif all(a["outcome_class"] != b["outcome_class"] or a["circular"] or b["circular"] for a, b in pairs):
            verdict = "explained by definition"
        elif all(a["timing"] != b["timing"] for a, b in pairs):
            verdict = "explained by timing"
        else:
            verdict = "unresolved"
    uni = [x for x in units if x["family"] == "univariable"]
    cnt = {k: len({x["unit"] for x in uni if x["call"] == k or (k in "HL" and x["call"] == "X")}) for k in "HLNXU"}
    conf_rows.append({"conflict": name, "markers": ";".join(markers), "outcome_filter": oc_only or "",
                      "tested_or_flagged_units": n_units, "descriptive_only_units": max(0, desc_units),
                      "H": cnt["H"], "L": cnt["L"], "N": cnt["N"], "X": cnt["X"], "U": cnt["U"],
                      "species_groups": ";".join(sorted({x["species_group"] for x in units})),
                      "verdict": verdict,
                      "pattern": (f"{cnt['H']} unit(s) significantly higher, {cnt['L']} lower, {cnt['N']} with a "
                                  f"non-significant result, {cnt['U']} unclear (univariable; a unit can appear under "
                                  f"two calls when it used several definitions)")})
write_csv("conflicts.csv", conf_rows, list(conf_rows[0].keys()))
write_csv("conflict_units.csv", conf_units, list(conf_units[0].keys()))

# ------------------------------------------------------------------ selective reporting
by_art = C.defaultdict(lambda: C.Counter())
for r in A:
    by_art[(r["id"], r["independent_unit"])][r["call"]] += 1
sel_rows = []
for (a, u), c in sorted(by_art.items()):
    t = c["H"] + c["L"] + c["N"]
    sel_rows.append({"id": a, "independent_unit": u, "rows": sum(c.values()), "tested_rows": t,
                     "significant_rows": c["H"] + c["L"], "not_significant_rows": c["N"],
                     "share_not_significant": round(c["N"] / t, 3) if t else None,
                     "descriptive_rows": c["D"], "unclear_rows": c["U"]})
write_csv("selective_reporting.csv", sel_rows, list(sel_rows[0].keys()))
tested_arts = [s for s in sel_rows if s["tested_rows"]]
share_ns = [s["share_not_significant"] for s in tested_arts]
zero_ns = [s["id"] for s in tested_arts if s["not_significant_rows"] == 0]
sel_summary = {"articles_with_tested_rows": len(tested_arts), "median_share_not_significant": float(np.median(share_ns)),
               "q1": float(np.percentile(share_ns, 25)), "q3": float(np.percentile(share_ns, 75)),
               "articles_with_no_not_significant_row": len(zero_ns), "those_articles": zero_ns,
               "overall_share_not_significant": round(sum(s["not_significant_rows"] for s in tested_arts) /
                                                      sum(s["tested_rows"] for s in tested_arts), 3)}

# ------------------------------------------------- D1 (post hoc): outcome classes collapsed
# Added after the primary matrix had no cell with 3 tested units. Exploratory: a unit call across all its
# severity definitions within one species group. Not pooled.
A_any = [dict(r, outcome_class="any severity contrast") for r in A]
M_any = build_matrix(A_any)
M_any_s1 = build_matrix(A_any, unit_key="unit_s1")
M_any_s4 = build_matrix(A_any, drop_circ=True)
any_rows = []
for cell, v in sorted(M_any.items(), key=lambda kv: (-kv[1]["tested_units"], kv[0])):
    if v["tested_units"] < 2:
        continue
    row = dict(v)
    w1, w4 = M_any_s1.get(cell), M_any_s4.get(cell)
    row["S1_tested_units"] = w1["tested_units"] if w1 else 0
    row["S1_H"], row["S1_L"], row["S1_N"], row["S1_X"] = ((w1["H"], w1["L"], w1["N"], w1["X"]) if w1 else (0, 0, 0, 0))
    row["S1_consistent"] = bool(w1 and w1["consistent"])
    row["S4_tested_units"] = w4["tested_units"] if w4 else 0
    row["S4_consistent"] = bool(w4 and w4["consistent"])
    any_rows.append(row)
write_csv("evidence_matrix_collapsed.csv", any_rows,
          ["marker", "marker_class", "species_group", "units", "tested_units", "H", "L", "N", "X", "U", "D",
           "consistent", "consistent_direction", "circular", "circular_units", "presumed_species_units",
           "multivariable_units", "unit_calls",
           "S1_tested_units", "S1_H", "S1_L", "S1_N", "S1_X", "S1_consistent", "S4_tested_units", "S4_consistent"])
cand_any = C.defaultdict(set)
for (m, oc, sg, kind), units in cand.items():
    cand_any[(m, sg, kind)] |= set(units)
any_poolable = sorted([{"marker": k[0], "species_group": k[1], "effect": k[2], "k_units": len(u)}
                       for k, u in cand_any.items() if len(u) >= 3], key=lambda x: -x["k_units"])

# ------------------------------------------------------------------ summary numbers
cells = list(M.values())
def summ(MM):
    cs = list(MM.values())
    cons = [c for c in cs if c["consistent"]]
    return {"cells": len(cs), "cells_ge2_tested": sum(1 for c in cs if c["tested_units"] >= 2),
            "cells_ge3_tested": sum(1 for c in cs if c["tested_units"] >= 3),
            "consistent": len(cons), "consistent_noncircular": sum(1 for c in cons if not c["circular"]),
            "consistent_ge3": sum(1 for c in cons if c["H"] + c["L"] >= 3),
            "consistent_ge3_noncircular": sum(1 for c in cons if c["H"] + c["L"] >= 3 and not c["circular"]),
            "cells_with_opposite_significant": sum(1 for c in cs if (c["H"] and c["L"]) or c["X"])}
summary = {"main": summ(M), **{k: summ(v) for k, v in SENS.items()},
           "D1_collapsed": summ(M_any), "D1_collapsed_S1": summ(M_any_s1), "D1_collapsed_S4": summ(M_any_s4)}
consistent_cells = [c for c in sorted(cells, key=lambda c: (-(c["H"] + c["L"]), -c["tested_units"], c["marker"]))
                    if c["consistent"]]
for c in consistent_cells:
    cell = (c["marker"], c["outcome_class"], c["species_group"])
    c["survives"] = {k: bool(SENS[k].get(cell) and SENS[k][cell]["consistent"]) for k in SENS}
# markers consistent in the same direction in two or more species groups (direction table only)
by_marker = C.defaultdict(set)
for c in consistent_cells:
    if c["species_group"] != "mixed/unspecified":
        by_marker[(c["marker"], c["consistent_direction"])].add(c["species_group"])
cross_species = [{"marker": m, "direction": d, "species_groups": sorted(s)} for (m, d), s in by_marker.items()
                 if len(s) >= 2]

meta = {
    "inputs": {"associations_v2.csv": sha(ASSOC), "definitions_v2.csv": sha(DEFS),
               "cohorts.json": sha(os.path.join(ROOT, "core", "cohorts.json")),
               "spec.md": sha(os.path.join(PKG, "spec.md"))},
    "script_sha256": sha(os.path.abspath(__file__)),
    "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": __import__("scipy").__version__},
    "rows": len(A), "units": len({r["independent_unit"] for r in A}), "articles": len({r["id"] for r in A}),
    "species_units": {sg: len({r["independent_unit"] for r in A if r["sg"] == sg}) for sg in SG_ORDER},
    "usable_rows_for_pooling": usable_rows,
    "dogs_max_n_per_unit": sum(max((to_int(r["n_total"]) or 0) for r in A if r["independent_unit"] == u)
                               for u in {r["independent_unit"] for r in A}),
    "markers": len({r["marker"] for r in A}), "cells_with_2_usable_units": cells_ge2_usable,
}
results = {"meta": meta, "summary": summary, "circularity": circ_summary, "selective_reporting": sel_summary,
           "consistent_cells": consistent_cells, "cross_species": cross_species, "pooled": pooled_rows,
           "pooled_points": pooled_points, "conflicts": conf_rows, "conflict_units": conf_units,
           "collapsed": any_rows, "collapsed_poolable_if_allowed": any_poolable, "components": comp_rows, "outcome_classes": oc_rows, "near_misses": near}
with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, indent=1, allow_nan=False, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
print(json.dumps({"summary": summary, "circ": circ_summary, "sel": sel_summary, "meta": meta}, indent=1))
print("pooled", len(pooled_rows))
for p in pooled_rows:
    print(" ", p["marker"], p["outcome_class"], p["species_group"], p["effect"], p["k_units"],
          round(p["estimate"], 2), round(p["ci_low"], 2), round(p["ci_high"], 2))
print("consistent cells")
for c in consistent_cells:
    print(" ", c["marker"], "|", c["outcome_class"], "|", c["species_group"], c["H"], c["L"], c["N"], c["tested_units"],
          "circ" if c["circular"] else "", {k[:2]: v for k, v in c["survives"].items()})
for c in conf_rows:
    print(c)
print("collapsed", json.dumps(summary["D1_collapsed"]), json.dumps(summary["D1_collapsed_S1"]))
for c in any_rows:
    print(" ", c["marker"], "|", c["species_group"], c["tested_units"], c["H"], c["L"], c["N"], c["X"],
          "CONS" if c["consistent"] else "", "S1:" + str(c["S1_tested_units"]) + ("C" if c["S1_consistent"] else ""),
          "circ" if c["circular"] else "", c["unit_calls"])
print("poolable if collapsed", any_poolable)
