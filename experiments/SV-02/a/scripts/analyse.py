"""SV-02a: parasite load by outcome, synthesis of the SV-G2 extraction rows.

Reads /experiments/SV-G2/associations_v2.csv, /core/articles.jsonl (streamed, for DOIs) and the appraisal
notes /core/articles/CB*.md (keyword screen for the separate list). Writes a/out/. No dog-level outcomes file.
Spec: a/spec.md (its SHA-256 is checked). Run with env/py (numpy, scipy).
"""
import csv
import glob
import hashlib
import json
import math
import os
import re
import sys

import numpy as np
from scipy import optimize, stats

HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)                      # /experiments/SV-02/a
EXP = os.path.dirname(os.path.dirname(PART))      # /experiments
ROOT = os.path.dirname(EXP)                       # repository root
OUT = os.path.join(PART, "out")

ASSOC = os.path.join(EXP, "SV-G2", "associations_v2.csv")
ARTICLES = os.path.join(ROOT, "core", "articles.jsonl")
NOTES = os.path.join(ROOT, "core", "articles")
CURATED = os.path.join(PART, "curated_note_hits.csv")
SPEC = os.path.join(PART, "spec.md")

EXPECTED = {
    "spec.md": "dad666990e2414cc80f49b554eea932a3b92c512d120789a2b7c61edd6f8f46f",
}

LOAD_MARKERS = {"Parasitaemia", "Parasite DNA load (qPCR)"}
SEED = 20261112  # no random step in this script; recorded for the convention


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def species_group(s):
    s = (s or "").lower()
    if "mixed" in s or ("gibsoni" in s and "vogeli" in s):
        return "mixed"
    for k in ("rossi", "canis", "gibsoni", "vogeli"):
        if k in s:
            return "B. " + k
    return "unspecified"


def num(x):
    x = (x or "").strip().replace(",", ".").replace("*", "")
    try:
        return float(x)
    except ValueError:
        return None


def parse_mean_sem(v):
    m = re.match(r"^\s*([-\d.,]+)\*?\s*±\s*([-\d.,]+)\*?\s*$", v or "")
    return (num(m.group(1)), num(m.group(2))) if m else (None, None)


def parse_median_range(v):
    m = re.match(r"^\s*([\d.,]+)\*?\s*\(([\d.,]+)\s*[–-]\s*([\d.,]+)\)\s*$", v or "")
    return tuple(num(g) for g in m.groups()) if m else (None, None, None)


def lognormal_from_mean_sd(mean, sd):
    s2 = math.log(1 + (sd / mean) ** 2)
    return math.log(mean) - s2 / 2, math.sqrt(s2)


def log_from_median_range(med, lo, hi, n):
    """Hozo (2005) mean and Wan (2014) SD on the log scale."""
    a, m, b = math.log(lo), math.log(med), math.log(hi)
    mean = (a + 2 * m + b) / 4
    xi = 2 * stats.norm.ppf((n - 0.375) / (n + 0.25))
    return mean, (b - a) / xi


def hedges_g(m1, s1, n1, m2, s2, n2):
    sp = math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    d = (m1 - m2) / sp
    j = 1 - 3 / (4 * (n1 + n2) - 9)
    g = j * d
    var = (n1 + n2) / (n1 * n2) + g ** 2 / (2 * (n1 + n2))
    se = math.sqrt(var)
    return g, g - 1.96 * se, g + 1.96 * se, var


def fisher_ci(r, n):
    z, se = math.atanh(r), 1 / math.sqrt(n - 3)
    return math.tanh(z - 1.96 * se), math.tanh(z + 1.96 * se)


def detectable_d(n1, n2, power=0.8, alpha=0.05):
    df = n1 + n2 - 2
    tcrit = stats.t.ppf(1 - alpha / 2, df)
    f = lambda d: (1 - stats.nct.cdf(tcrit, df, d * math.sqrt(n1 * n2 / (n1 + n2)))) - power
    return optimize.brentq(f, 0.01, 20)


def detectable_rho(n, power=0.8, alpha=0.05):
    return math.tanh((stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)) / math.sqrt(n - 3))


def odds_ratio(a, n1, c, n2):
    b, d = n1 - a, n2 - c
    if min(a, b, c, d) == 0:
        a, b, c, d = a + .5, b + .5, c + .5, d + .5
    lor = math.log(a * d / (b * c))
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    return math.exp(lor), math.exp(lor - 1.96 * se), math.exp(lor + 1.96 * se)


def reml_hk(y, v):
    """Random effects, REML tau^2, Hartung-Knapp-Sidik-Jonkman interval. Used only for k >= 3."""
    y, v = np.asarray(y, float), np.asarray(v, float)
    k, tau2 = len(y), 0.0
    for _ in range(500):
        w = 1 / (v + tau2)
        mu = np.sum(w * y) / np.sum(w)
        new = max(0.0, np.sum(w ** 2 * ((y - mu) ** 2 - v)) / np.sum(w ** 2) + 1 / np.sum(w))
        if abs(new - tau2) < 1e-10:
            break
        tau2 = new
    w = 1 / (v + tau2)
    mu = np.sum(w * y) / np.sum(w)
    q = np.sum(w * (y - mu) ** 2) / (k - 1)
    se = math.sqrt(max(q, 1e-12) / np.sum(w))
    t = stats.t.ppf(0.975, k - 1)
    return {"mu": mu, "lo": mu - t * se, "hi": mu + t * se, "tau2": tau2, "k": k}


def r3(x):
    return None if x is None else round(float(x), 3)


def main():
    os.makedirs(OUT, exist_ok=True)
    if sha256(SPEC) != EXPECTED["spec.md"]:
        sys.exit("spec.md changed after it was frozen")
    inputs = {p: sha256(p) for p in (ASSOC, CURATED, SPEC)}

    rows = list(csv.DictReader(open(ASSOC, encoding="utf-8")))
    dois = {}
    with open(ARTICLES, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            dois[d["id"]] = d.get("doi")

    def doi_link(i):
        return f"https://doi.org/{dois[i]}" if dois.get(i) else None

    units_with_rows = sorted({r["independent_unit"] for r in rows})

    # ---------------- primary set: load against an outcome ----------------
    load_rows = [r for r in rows if r["marker"] in LOAD_MARKERS]
    primary, excluded = [], []
    for r in load_rows:
        if r["outcome_class"] == "parasitaemia_level":
            excluded.append((r, "outcome is load"))
        elif "dose" in r["severity_label"].lower():
            excluded.append((r, "groups defined by inoculum dose"))
        else:
            primary.append(r)

    table = []
    for r in primary:
        sp = species_group(r["species"])
        rec = {
            "unit": r["independent_unit"], "article": r["id"], "row": int(r["row"]), "species_group": sp,
            "species_reported": r["species"], "outcome_class": r["outcome_class"],
            "definition": r["severity_label"], "euthanasia_included": r["euthanasia_included"],
            "load_method": r["load_method"] or "not stated", "sample_timing": r["sample_timing"],
            "analysis": r["analysis"], "direction": r["direction"], "significant": r["significant"],
            "n_total": num(r["n_total"]), "n_severe": num(r["n_severe"]), "n_comparison": num(r["n_comparison"]),
            "severe_value": r["severe_value"], "comparison_value": r["comparison_value"],
            "summary_type": r["summary_type"], "p_value": r["p_value"],
            "effect_type": None, "effect": None, "ci_lo": None, "ci_hi": None, "variance": None,
            "effect_basis": None, "detectable": None, "doi": doi_link(r["id"]),
        }
        n1, n2 = rec["n_severe"], rec["n_comparison"]
        if r["summary_type"] == "median and range" and n1 and n2:
            m1, lo1, hi1 = parse_median_range(r["severe_value"])
            m2, lo2, hi2 = parse_median_range(r["comparison_value"])
            a = log_from_median_range(m1, lo1, hi1, int(n1))
            b = log_from_median_range(m2, lo2, hi2, int(n2))
            g, lo, hi, var = hedges_g(a[0], a[1], n1, b[0], b[1], n2)
            rec.update(effect_type="hedges_g_log_load", effect=g, ci_lo=lo, ci_hi=hi, variance=var,
                       effect_basis="log-scale mean (Hozo 2005) and SD (Wan 2014) from median and range",
                       detectable=detectable_d(int(n1), int(n2)))
        elif r["summary_type"] == "mean and SEM":
            rec["effect_basis"] = "group n not printed; direction only (equal split in sensitivity)"
        elif r["analysis"] == "correlation" and num(r["effect_value"]) is not None and rec["n_total"]:
            rho, n = num(r["effect_value"]), int(rec["n_total"])
            lo, hi = fisher_ci(rho, n)
            rec.update(effect_type="rho" if r["effect_type"] == "rho" else "r", effect=rho, ci_lo=lo, ci_hi=hi,
                       effect_basis="correlation with a continuous severity measure; Fisher-z interval",
                       detectable=detectable_rho(n))
        elif r["summary_type"] == "other" and "of 17" in r["severe_value"]:
            a = int(re.match(r"\s*(\d+)", r["severe_value"]).group(1))
            c = int(re.search(r"group-2:\s*(\d+)", r["comparison_value"]).group(1))
            orr, lo, hi = odds_ratio(a, 17, c, 17)
            rec.update(effect_type="odds_ratio_smear_positive", effect=orr, ci_lo=lo, ci_hi=hi,
                       effect_basis="smear positivity (detectable load), complicated vs uncomplicated; Woolf interval")
        else:
            rec["effect_basis"] = "no group n or dispersion printed; direction only"
        table.append(rec)

    # cells and pooling rule
    cells = {}
    for t in table:
        cells.setdefault((t["species_group"], t["outcome_class"]), []).append(t)
    cell_rows, pooled = [], []
    for (sp, oc), ts in sorted(cells.items()):
        units = sorted({t["unit"] for t in ts})
        defs = sorted({t["definition"] for t in ts})
        g_units = [t for t in ts if t["effect_type"] == "hedges_g_log_load"]
        eligible = len(units) >= 3 and len(defs) == 1 and len(g_units) >= 3
        cell_rows.append({"species_group": sp, "outcome_class": oc, "units": len(units), "unit_ids": units,
                          "definitions": len(defs), "units_with_g": len(g_units), "pooled": eligible,
                          "reason": "pooled" if eligible else
                          f"{len(units)} unit(s), {len(defs)} definition(s), {len(g_units)} with a computable g; rule needs 3 units sharing one definition"})
        if eligible:
            res = reml_hk([t["effect"] for t in g_units], [t["variance"] for t in g_units])
            pooled.append({"species_group": sp, "outcome_class": oc, **{k: r3(v) for k, v in res.items()}})

    # sensitivity: equal split for mean and SEM rows
    sensitivity = []
    for t in table:
        if t["summary_type"] == "mean and SEM" and t["n_total"]:
            n1 = n2 = t["n_total"] / 2
            ms1, se1 = parse_mean_sem(t["severe_value"])
            ms2, se2 = parse_mean_sem(t["comparison_value"])
            a = lognormal_from_mean_sd(ms1, se1 * math.sqrt(n1))
            b = lognormal_from_mean_sd(ms2, se2 * math.sqrt(n2))
            g, lo, hi, _ = hedges_g(a[0], a[1], n1, b[0], b[1], n2)
            sensitivity.append({"check": "equal split of n_total", "unit": t["unit"], "article": t["article"],
                                "species_group": t["species_group"], "outcome_class": t["outcome_class"],
                                "n_severe": n1, "n_comparison": n2, "effect_type": "hedges_g_log_load",
                                "effect": r3(g), "ci_lo": r3(lo), "ci_hi": r3(hi),
                                "detectable": r3(detectable_d(int(n1), int(n2))),
                                "note": "group sizes assumed; log-normal moment conversion of mean and SD (SD = SEM x sqrt(n))"})
    for r, why in excluded:
        if why.startswith("groups defined by inoculum dose"):
            m1, lo1, hi1 = parse_median_range(r["severe_value"])
            m2, _, _ = parse_median_range(r["comparison_value"])
            sensitivity.append({"check": "dose contrast (excluded from primary)", "unit": r["independent_unit"],
                                "article": r["id"], "species_group": species_group(r["species"]),
                                "outcome_class": r["outcome_class"], "n_severe": num(r["n_severe"]),
                                "n_comparison": num(r["n_comparison"]), "effect_type": "median ratio",
                                "effect": r3(m1 / m2) if m1 and m2 else None, "ci_lo": None, "ci_hi": None,
                                "detectable": None,
                                "note": f"{r['timepoint']}: high dose {r['severe_value']} vs low dose {r['comparison_value']} %"})

    # moderators
    moderators = []
    for t in table:
        moderators.append({"unit": t["unit"], "article": t["article"], "species_group": t["species_group"],
                           "load_method": t["load_method"], "sample_timing": t["sample_timing"],
                           "direction": t["direction"], "significant": t["significant"]})

    # ---------------- damage by load group (inverse question) ----------------
    damage = []
    for r in rows:
        if r["outcome_class"] != "parasitaemia_level":
            continue
        rec = {"unit": r["independent_unit"], "article": r["id"], "species_group": species_group(r["species"]),
               "definition": r["severity_label"], "marker": r["marker"], "marker_as_reported": r["marker_as_reported"],
               "n_high": num(r["n_severe"]), "n_low": num(r["n_comparison"]), "n_total": num(r["n_total"]),
               "high_value": r["severe_value"], "low_value": r["comparison_value"], "direction": r["direction"],
               "significant": r["significant"], "effect_type": None, "effect": None, "ci_lo": None, "ci_hi": None,
               "flag": None, "doi": doi_link(r["id"])}
        if r["summary_type"] == "mean and SEM" and rec["n_high"] and rec["n_low"]:
            m1, s1 = parse_mean_sem(r["severe_value"])
            m2, s2 = parse_mean_sem(r["comparison_value"])
            if None not in (m1, s1, m2, s2) and (s1 > 0 or s2 > 0):
                g, lo, hi, _ = hedges_g(m1, s1 * math.sqrt(rec["n_high"]), rec["n_high"],
                                        m2, s2 * math.sqrt(rec["n_low"]), rec["n_low"])
                rec.update(effect_type="hedges_g", effect=r3(g), ci_lo=r3(lo), ci_hi=r3(hi))
                if abs(g) > 5:
                    rec["flag"] = "implausibly large: the printed +/- is unlikely to be an SEM of these n; read as direction only"
        elif r["summary_type"] == "count and percent" and rec["n_high"] and rec["n_low"]:
            a = int(re.match(r"\s*(\d+)", r["severe_value"]).group(1))
            c = int(re.match(r"\s*(\d+)", r["comparison_value"]).group(1))
            rec.update(effect_type="risk_difference", effect=r3(a / rec["n_high"] - c / rec["n_low"]))
        elif r["analysis"] == "correlation" and num(r["effect_value"]) is not None:
            rec.update(effect_type="rho (serial samples pooled)", effect=num(r["effect_value"]))
        damage.append(rec)

    # ---------------- separate list ----------------
    low_list = []
    for t in table:
        kind = None
        if t["direction"] == "no_difference":
            kind = "no load difference by outcome" if t["outcome_class"] == "mortality" else "load unrelated to a complication"
        elif t["direction"] == "lower_in_severe":
            kind = "lower load in the severe group"
        elif t["effect_type"] == "odds_ratio_smear_positive" and t["ci_lo"] < 1 < t["ci_hi"]:
            kind = "detectable load similar across severity groups"
        if kind:
            low_list.append({"kind": kind, "unit": t["unit"], "article": t["article"], "species": t["species_group"],
                             "design": t["definition"], "n_dogs": t["n_total"], "source_level": "SV-G2 row",
                             "statement": f"severe {t['severe_value']} vs comparison {t['comparison_value']}"
                                          + (f"; p {t['p_value']}" if t["p_value"] else "")
                                          + (f"; {t['effect_type']} {r3(t['effect'])} ({r3(t['ci_lo'])} to {r3(t['ci_hi'])})" if t["effect"] is not None else ""),
                             "doi": t["doi"]})
    ab = [r for r in rows if r["marker"] == "Antibody titre / serostatus" and r["analysis"] == "correlation"]
    ld = [t for t in table if t["unit"] in {r["independent_unit"] for r in ab} and t["effect_type"] == "rho"]
    antibody_vs_load = None
    if ab and ld:
        a_rho, a_n = num(ab[0]["effect_value"]), int(num(ab[0]["n_total"]))
        l = ld[0]
        alo, ahi = fisher_ci(a_rho, a_n)
        antibody_vs_load = {"unit": l["unit"], "article": l["article"], "species": l["species_group"],
                            "outcome": l["definition"],
                            "antibody_rho": a_rho, "antibody_ci": [r3(alo), r3(ahi)], "antibody_n": a_n,
                            "load_rho": l["effect"], "load_ci": [r3(l["ci_lo"]), r3(l["ci_hi"])], "load_n": int(l["n_total"]),
                            "note": "Different n (antibody tested in a subset); the correlation between load and antibody is not printed, so the two coefficients cannot be compared formally"}
        low_list.append({"kind": "antibody tracks severity more than load", "unit": l["unit"], "article": l["article"],
                         "species": l["species_group"], "design": l["definition"], "n_dogs": a_n,
                         "source_level": "SV-G2 row",
                         "statement": f"antibody rho {a_rho} ({r3(alo)} to {r3(ahi)}, n {a_n}) vs load rho {l['effect']} ({r3(l['ci_lo'])} to {r3(l['ci_hi'])}, n {int(l['n_total'])})",
                         "doi": l["doi"]})

    pat = re.compile(r"[^.]*parasit(a)?emi[^.]*\b(low|unchanged|not correlat|no correlation|did not correlate|independent of|regardless|despite|unrelated|no association|not associated|not related)\b[^.]*\.|"
                     r"[^.]*\b(low|unchanged|despite)\b[^.]*parasit(a)?emi[^.]*\.", re.I)
    hits = {}
    for f in sorted(glob.glob(os.path.join(NOTES, "CB*.md"))):
        t = open(f, encoding="utf-8").read()
        if pat.search(t):
            hits[os.path.basename(f)[:5]] = sha256(f)
    curated = {r["id"]: r for r in csv.DictReader(open(CURATED, encoding="utf-8"))}
    missing = sorted(set(hits) - set(curated))
    extra = sorted(set(curated) - set(hits))
    if missing or extra:
        sys.exit(f"curated_note_hits.csv out of step with the screen: missing {missing}, extra {extra}")
    for i, c in sorted(curated.items()):
        if c["decision"] == "include":
            low_list.append({"kind": c["kind"], "unit": i, "article": i, "species": c["species"], "design": c["design"],
                             "n_dogs": num(c["n_dogs"]), "source_level": c["source_level"], "statement": c["statement"],
                             "doi": doi_link(i)})

    # ---------------- write ----------------
    def wcsv(name, recs, fields=None):
        fields = fields or list(recs[0].keys())
        with open(os.path.join(OUT, name), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            for r in recs:
                w.writerow({k: (r3(v) if isinstance(v, float) else ("; ".join(v) if isinstance(v, list) else v)) for k, v in r.items()})

    wcsv("load_by_outcome.csv", table)
    wcsv("cells.csv", cell_rows)
    wcsv("sensitivity.csv", sensitivity)
    wcsv("moderators.csv", moderators)
    wcsv("damage_by_load_group.csv", damage)
    wcsv("low_load_list.csv", low_list)
    wcsv("excluded_load_rows.csv", [{"unit": r["independent_unit"], "article": r["id"], "row": r["row"],
                                     "reason": why, "definition": r["severity_label"], "timepoint": r["timepoint"]}
                                    for r, why in excluded])

    articles_with_rows = sorted({r["id"] for r in rows})
    results = {
        "inputs": {os.path.relpath(p, ROOT).replace("\\", "/"): h for p, h in inputs.items()},
        "articles_jsonl_sha256": sha256(ARTICLES),
        "note_hits": hits,
        "seed": SEED,
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": __import__("scipy").__version__},
        "counts": {
            "units_with_severity_rows": len(units_with_rows),
            "articles_with_severity_rows": len(articles_with_rows),
            "load_rows": len(load_rows),
            "load_rows_primary": len(primary),
            "load_units_primary": len({t["unit"] for t in table}),
            "load_units_excluded_only": sorted({r["independent_unit"] for r, _ in excluded} - {t["unit"] for t in table}),
            "cells": len(cell_rows),
            "cells_pooled": len(pooled),
            "max_units_in_cell": max(c["units"] for c in cell_rows),
            "units_with_g": sum(1 for t in table if t["effect_type"] == "hedges_g_log_load"),
            "significant_higher_in_severe": sum(1 for t in table if t["significant"] == "yes" and t["direction"] in ("higher_in_severe", "positive_association")),
            "damage_rows": len(damage),
            "damage_units": len({d["unit"] for d in damage}),
            "low_list_items": len(low_list),
            "note_hits": len(hits),
            "note_hits_included": sum(1 for c in curated.values() if c["decision"] == "include"),
        },
        "pooled": pooled,
        "antibody_vs_load": antibody_vs_load,
        "table": table, "cells": cell_rows, "sensitivity": sensitivity, "damage": damage, "low_list": low_list,
    }
    with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, indent=1, ensure_ascii=False, allow_nan=False,
                  default=lambda o: float(o) if isinstance(o, np.floating) else str(o))
    print(json.dumps(results["counts"], indent=1))


if __name__ == "__main__":
    main()
