"""SV-05: build the two load files for the console loader (way B) from out/results.json.

Run from /experiments/SV-05/:  env/py/Scripts/python.exe -I scripts/build_load.py
Every number in the text comes from results.json.
"""
import hashlib
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
OUT = os.path.join(PKG, "out")
DB = os.path.join(OUT, "db")

with open(os.path.join(OUT, "results.json"), encoding="utf-8") as f:
    R = json.load(f)
with open(os.path.join(HERE, "analyse.py"), "rb") as f:
    SCRIPT_VERSION = hashlib.sha256(f.read()).hexdigest()[:12]
RUN_UTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

A = R["family_A"]
B = R["family_B"]
S = R["secondary"]
T = R["sensitivity"]
D = R["decision"]
P = R["profile"]
DOGS = R["dogs"]

DIED = "died includes euthanasia for poor prognosis (Onderstepoort)"
SAME = "DS03 natural dogs are S-CB050 dogs (SV-07): one source, not a replication"
EXPL = "exploratory: S-CB050 and DS05 were seen before this plan"
SOURCES = {
    "S-CB050": "S-CB050 (SRC-A, B. rossi, Onderstepoort, 2011-2014)",
    "DS03": "DS03 natural (SRC-A: the same dogs as S-CB050, per SV-07)",
    "DS05": "DS05 (SRC-F, B. rossi, Eastern Cape clinic, 2021)",
}
SRC = {"S-CB050": "SRC-A", "DS03": "SRC-A", "DS05": "SRC-F"}


def s2(v, d=2):
    return "–" if v is None else f"{v:+.{d}f}"


def f2(v, d=2):
    return "–" if v is None else f"{v:.{d}f}"


def pt(p):
    return "–" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def pct(v):
    return "–" if v is None else f"{100 * v:.0f}%"


def rank_row(test, label, ds, c, measure, unit, digits=2, note=""):
    return {"id": test, "test": test, "label": label, "dataset": ds, "source": SRC.get(ds, ds), "measure": measure,
            "effect_label": f"HL difference{', ' + unit if unit else ''}", "scale": "diff", "null_value": 0,
            "estimate": c["hl"], "ci_low": c["hl_low"], "ci_high": c["hl_high"],
            "n_young": c["n_young"], "n_adult": c["n_adult"], "value_label": "median",
            "young_value": c["median_young"], "adult_value": c["median_adult"],
            "young_iqr": c.get("iqr_young"), "adult_iqr": c.get("iqr_adult"),
            "cliff": c["cliff"], "cliff_low": c["cliff_low"], "cliff_high": c["cliff_high"],
            "p": c["p"], "q": c.get("q"), "digits": digits, "detectable_sd": c.get("detectable_sd"), "note": note}


def share_row(test, label, ds, c, measure, note=""):
    return {"id": test, "test": test, "label": label, "dataset": ds, "source": SRC.get(ds, ds), "measure": measure,
            "effect_label": "Difference in share", "scale": "diff", "null_value": 0,
            "estimate": c["diff"], "ci_low": c["diff_low"], "ci_high": c["diff_high"],
            "n_young": c["n_young"], "n_adult": c["n_adult"], "value_label": "share",
            "young_value": c["share_young"], "adult_value": c["share_adult"],
            "events_young": c["events_young"], "events_adult": c["events_adult"],
            "odds_ratio": c["or"], "or_low": c["or_low"], "or_high": c["or_high"],
            "cliff": None, "cliff_low": None, "cliff_high": None,
            "p": c["p"], "q": c.get("q"), "digits": 2, "note": note}


def or_row(test, label, ds, c, measure, est="or", lo="or_low", hi="or_high", note="", young_lab=None):
    return {"id": test, "test": test, "label": label, "dataset": ds, "source": SRC.get(ds, ds), "measure": measure,
            "effect_label": "Odds ratio", "scale": "ratio", "null_value": 1,
            "estimate": c[est], "ci_low": c[lo], "ci_high": c[hi],
            "n_young": c.get("n_young"), "n_adult": c.get("n_adult"), "value_label": "share died",
            "young_value": c.get("share_young"), "adult_value": c.get("share_adult"),
            "events_young": c.get("deaths_young"), "events_adult": c.get("deaths_adult"),
            "cliff": None, "cliff_low": None, "cliff_high": None,
            "p": c["p"], "q": c.get("q"), "digits": 2, "note": note, "group_labels": young_lab}


def rho_row(key, label, ds, c):
    return {"id": key, "test": key, "label": label, "dataset": ds, "source": SRC.get(ds, ds), "measure": "Spearman rho with age",
            "effect_label": "Spearman rho", "scale": "diff", "null_value": 0,
            "estimate": c["rho"], "ci_low": c["rho_low"], "ci_high": c["rho_high"],
            "n_young": c["n"], "n_adult": None, "value_label": "n dogs", "young_value": None, "adult_value": None,
            "cliff": None, "cliff_low": None, "cliff_high": None, "p": None, "q": None, "digits": 2,
            "note": "age continuous (S3); positive = higher with age"}


def write(code, exp, results):
    os.makedirs(DB, exist_ok=True)
    doc = {"experiment": exp, "associations": [], "cluster_assignments": [], "results": results}
    text = json.dumps(doc, indent=1, ensure_ascii=False, allow_nan=False)
    assert len(text.encode("utf-8")) < 1_000_000
    with open(os.path.join(DB, f"{code}.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def params(role, datasets, sources, extra=None):
    p = {"package": "SV-05", "role": role, "datasets": datasets, "independent_sources": sources,
         "spec_sha256": R["spec_sha256"], "seed": R["seed"], "permutations": R["b_perm"], "bootstrap": R["b_boot"],
         "young_cut_months": R["young_cut_months"], "contrast": "young (< 12 months) minus adult (>= 12 months)",
         "versions": R["versions"]}
    p.update(extra or {})
    return p


# ======================= Experiment 1: age and death (family A) =======================
A1, A2, A3 = A["A1"], A["A2"], A["A3"]
passed_a = sum(1 for k in ("A1", "A2", "A3") if A[k]["q"] is not None and A[k]["q"] < 0.05)
code1 = "SV-05-01-age-death"
summary1 = (f"S-CB050: {A1['deaths_young']} of {A1['n_young']} dogs under 12 months died against {A1['deaths_adult']} of "
            f"{A1['n_adult']} older dogs, odds ratio {f2(A1['or'])} (95% CI {f2(A1['or_low'])} to {f2(A1['or_high'])}, "
            f"Fisher p {pt(A1['p'])}); sex-stratified MH OR {f2(A2['mh_or'])} ({f2(A2['mh_low'])} to {f2(A2['mh_high'])}). "
            f"Only an OR of about {f2(A1['detectable_or_above_1'], 1)} or more (or {f2(A1['detectable_or_below_1'])} or less) "
            f"was detectable. {passed_a} of 3 tests q < 0.05.")
exp1 = {
    "code": code1,
    "name": "Age group and death in B. rossi (S-CB050): dogs under 12 months against older dogs",
    "description": ("Do dogs under 12 months die of B. rossi babesiosis more or less often than older dogs, and does sex change that? "
                    "The package hypothesis is that age changes the form of severe disease more than the overall risk."),
    "method": "age_sex_contrast",
    "dataset": None,
    "parameters": params("descriptive", ["S-CB050"], ["SRC-A"],
                         {"tests": ["A1 Fisher exact", "A2 MH stratified by sex, permutation within sex", "A3 age by outcome"],
                          "family": "A (3 tests, BH)", "outcome": "died, includes euthanasia for poor prognosis"}),
    "script": "/experiments/SV-05/scripts/analyse.py",
    "script_version": SCRIPT_VERSION,
    "run_utc": RUN_UTC,
    "n_subjects": A1["n_young"] + A1["n_adult"], "n_variables": 3, "n_tests": 3,
    "summary": summary1,
}
contrast_rows1 = [
    or_row("A1", "Death, young vs adult", "S-CB050", A1, "died (incl. euthanasia)",
           note=f"Fisher exact; conditional MLE OR with exact interval. Detectable at 80% power: OR >= {f2(A1['detectable_or_above_1'])} or <= {f2(A1['detectable_or_below_1'])}"),
    or_row("A2", "Death, young vs adult, stratified by sex", "S-CB050", dict(A2, n_young=A1["n_young"], n_adult=A1["n_adult"], share_young=A1["share_young"],
                share_adult=A1["share_adult"], deaths_young=A1["deaths_young"], deaths_adult=A1["deaths_adult"]),
           "died (incl. euthanasia)", est="mh_or", lo="mh_low", hi="mh_high",
           note=f"Mantel-Haenszel OR, RGB interval; p from 10,000 permutations within sex ({A2['deaths_young_obs']} young deaths observed, {f2(A2['deaths_young_expected'])} expected)"),
]
c = A3
contrast_rows1.append({"id": "A3", "test": "A3", "label": "Age in months, died minus survived", "dataset": "S-CB050", "source": "SRC-A",
                       "measure": "age months", "effect_label": "HL difference, months", "scale": "diff", "null_value": 0,
                       "estimate": c["hl_months"], "ci_low": c["hl_low"], "ci_high": c["hl_high"],
                       "n_young": c["n_died"], "n_adult": c["n_survived"], "value_label": "median months",
                       "young_value": c["median_died"], "adult_value": c["median_survived"],
                       "young_iqr": c["iqr_died"], "adult_iqr": c["iqr_survived"],
                       "cliff": c["cliff"], "cliff_low": c["cliff_low"], "cliff_high": c["cliff_high"],
                       "p": c["p"], "q": c["q"], "digits": 1, "note": "groups are died (first) and survived (second), not age groups",
                       "group_labels": ["died", "survived"]})
strata_rows = []
for sex, t in A2["by_sex"].items():
    strata_rows.append({"stratum": sex, "deaths_young": t["deaths_young"], "n_young": t["n_young"],
                        "deaths_adult": t["deaths_adult"], "n_adult": t["n_adult"], "or": t["or"],
                        "or_low": t["or_low"], "or_high": t["or_high"], "p": t["p"]})
ds = S["death_by_sex"]
results1 = [
    {"kind": "primary_result", "title": "Primary analysis: death by age group (A1)", "sort_order": 1, "payload": {
        "label": "S-CB050, 140 infected dogs with an age (1 has none), death by age group",
        "statistic": "Odds ratio, young over adult",
        "verdict": "No age difference detectable",
        "independent_sources": 1, "sources": [SOURCES["S-CB050"]],
        "rows": [contrast_rows1[0]],
        "headline": (f"{pct(A1['share_young'])} of young dogs and {pct(A1['share_adult'])} of adults died. The interval "
                     f"({f2(A1['or_low'])} to {f2(A1['or_high'])}) is wide: with {A1['deaths_young'] + A1['deaths_adult']} deaths "
                     f"only an odds ratio of about {f2(A1['detectable_or_above_1'], 1)} or more, or {f2(A1['detectable_or_below_1'])} "
                     "or less, could be detected. A null result here is not evidence of equal risk."),
        "caveats": [DIED + ".", EXPL + ".", "Age stands in for prior exposure, breed and size, which are not recorded.",
                    "Neuter status is not recorded in S-CB050."]}},
    {"kind": "contrasts", "title": "Family A: risk tests (BH over 3)", "sort_order": 2, "payload": {
        "groups": [{"key": "risk", "label": "Death and age, S-CB050", "note": "", "rows": contrast_rows1}],
        "footnote": f"S-CB050, SRC-A, B. rossi. {DIED}. {EXPL}."}},
    {"kind": "strata", "title": "Death by age group within each sex (A2)", "sort_order": 3, "payload": {
        "rows": strata_rows,
        "sex_contrast": {"deaths_male": ds["deaths_male"], "n_male": ds["n_male"], "deaths_female": ds["deaths_female"],
                         "n_female": ds["n_female"], "or": ds["or"], "or_low": ds["or_low"], "or_high": ds["or_high"], "p": ds["p"]},
        "footnote": ("Odds ratio young over adult in each sex, conditional MLE with exact interval. The sex contrast (male over "
                     "female) is secondary and not in the family. Sex differs between cases and controls in SRC-A; no control is used.")}},
    {"kind": "age_bands", "title": "Deaths by age band (descriptive)", "sort_order": 4, "payload": {
        "rows": P["death_S-CB050"],
        "footnote": f"S-CB050, 140 infected dogs. Descriptive, no test. {DIED}."}},
]
interp1 = {"sections": [
    {"heading": "Question", "paragraphs": [
        "Do dogs under 12 months die of B. rossi babesiosis more or less often than older dogs? This is step 1 of SV-05, "
        "whose hypothesis is that age changes the form of severe disease (anaemia in young dogs, inflammation in adults) more "
        "than it changes the risk of death."]},
    {"heading": "What was done", "paragraphs": [
        f"S-CB050 (Onderstepoort, SRC-A) has {DOGS['S-CB050']['infected']} infected dogs, {DOGS['S-CB050']['age_missing']} without an age: "
        f"{A1['n_young']} under 12 months and {A1['n_adult']} older. Death (which includes euthanasia for poor prognosis) by age "
        "group was tested with Fisher's exact test (A1), then stratified by sex with a Mantel-Haenszel odds ratio and a permutation "
        "test within sex (A2), and age in months was compared between dogs that died and survived (A3). Benjamini-Hochberg over the "
        "3 tests. The spec was frozen before the outcome file was opened, but the age medians by outcome had been seen, so this "
        "step is exploratory."]},
    {"heading": "Result", "paragraphs": [
        f"{A1['deaths_young']} of {A1['n_young']} young dogs ({pct(A1['share_young'])}) and {A1['deaths_adult']} of {A1['n_adult']} "
        f"adults ({pct(A1['share_adult'])}) died: odds ratio {f2(A1['or'])} (95% CI {f2(A1['or_low'])} to {f2(A1['or_high'])}), "
        f"p {pt(A1['p'])}. Within sex: females {f2(A2['by_sex']['female']['or'])} ({f2(A2['by_sex']['female']['or_low'])} to "
        f"{f2(A2['by_sex']['female']['or_high'])}), males {f2(A2['by_sex']['male']['or'])} ({f2(A2['by_sex']['male']['or_low'])} to "
        f"{f2(A2['by_sex']['male']['or_high'])}); pooled {f2(A2['mh_or'])} ({f2(A2['mh_low'])} to {f2(A2['mh_high'])}), "
        f"p {pt(A2['p'])}. Dogs that died were not older: median {f2(A3['median_died'], 0)} against {f2(A3['median_survived'], 0)} months, "
        f"Hodges-Lehmann difference {s2(A3['hl_months'], 0)} months ({s2(A3['hl_low'], 0)} to {s2(A3['hl_high'], 0)}), "
        f"Cliff's delta {s2(A3['cliff'])} ({s2(A3['cliff_low'])} to {s2(A3['cliff_high'])}). {passed_a} of 3 tests pass q < 0.05. "
        f"Death by sex (secondary): {ds['deaths_male']} of {ds['n_male']} males, {ds['deaths_female']} of {ds['n_female']} females, "
        f"OR {f2(ds['or'])} ({f2(ds['or_low'])} to {f2(ds['or_high'])})."]},
    {"heading": "What this does not show", "paragraphs": [
        f"It does not show that age has no effect on risk: with {A1['deaths_young'] + A1['deaths_adult']} deaths only an odds ratio of "
        f"about {f2(A1['detectable_or_above_1'], 1)} or more (or {f2(A1['detectable_or_below_1'])} or less) was detectable. One source "
        "only; age stands in for prior exposure, breed and size, which are not recorded, and neuter status is not in the file. "
        "The 'died' label includes euthanasia for poor prognosis, which can depend on cost and owner decisions."]},
]}
results1.append({"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp1})
write(code1, exp1, results1)

# ======================= Experiment 2: form of disease (family B) =======================
keys = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"]
passed_b = sum(1 for k in keys if B[k]["q"] is not None and B[k]["q"] < 0.05)
rows = {
    "B1": rank_row("B1", "Haematocrit, DS05", "DS05", B["B1"], "haematocrit", "L/L"),
    "B2": rank_row("B2", "Haematocrit, DS03 natural", "DS03", B["B2"], "haematocrit", "L/L", note=SAME),
    "B6": share_row("B6", "Severe anaemia (hct < 0.15), DS05", "DS05", B["B6"], "share with hct < 0.15 L/L"),
    "B3": rank_row("B3", "Band neutrophils, DS05", "DS05", B["B3"], "band neutrophils", "10^9/L"),
    "B4": rank_row("B4", "Band neutrophils, S-CB050", "S-CB050", B["B4"], "band neutrophils", "10^9/L"),
    "B5": rank_row("B5", "SV-04 perturbation count, S-CB050 cohort 1", "S-CB050", B["B5"], "cytokines outside control range", "count", 1),
    "B7": share_row("B7", "Left shift (bands > 0.5), DS05", "DS05", B["B7"], "share with bands > 0.5 x10^9/L"),
    "B8": rank_row("B8", "Illness duration before presentation, DS05", "DS05", B["B8"], "days ill", "days", 1),
}
verdict = D["verdict"]
b1, b2 = B["B1"], B["B2"]
headline2 = (f"Verdict by the pre-stated rule: {verdict}. The anaemia signal needed DS05 (the independent source) to show a lower "
             f"haematocrit in young dogs: HL {s2(b1['hl'])} L/L ({s2(b1['hl_low'])} to {s2(b1['hl_high'])}), which includes 0. "
             f"DS03 shows it ({s2(b2['hl'])}, {s2(b2['hl_low'])} to {s2(b2['hl_high'])}), but DS03 dogs are S-CB050 dogs and healthy "
             "young controls also have a lower haematocrit (check C1). No adult excess of bands or cytokine perturbation. "
             f"Young dogs presented about one day earlier (DS05, HL {s2(B['B8']['hl'], 0)} day, Cliff's delta {s2(B['B8']['cliff'])}, "
             f"{s2(B['B8']['cliff_low'])} to {s2(B['B8']['cliff_high'])}; q {pt(B['B8']['q'])}).")
code2 = "SV-05-02-age-form"
summary2 = (f"Form of disease by age group (young < 12 months minus adult): DS05 haematocrit HL {s2(b1['hl'])} L/L "
            f"({s2(b1['hl_low'])} to {s2(b1['hl_high'])}, n {b1['n_young']} vs {b1['n_adult']}); DS03 {s2(b2['hl'])} "
            f"({s2(b2['hl_low'])} to {s2(b2['hl_high'])}; same dogs as S-CB050); no adult excess of bands or perturbation. "
            f"Verdict: {verdict}. {passed_b} of 8 tests q < 0.05.")
exp2 = {
    "code": code2,
    "name": "Age group and the form of B. rossi disease: anaemia, left shift, cytokine perturbation and illness duration",
    "description": ("Is severe B. rossi disease anaemia-dominant in dogs under 12 months and inflammatory in older dogs? "
                    "Haematocrit, band neutrophils, the SV-04 cytokine perturbation and days ill are compared by age group inside each source, side by side."),
    "method": "age_sex_contrast",
    "dataset": None,
    "parameters": params("descriptive", ["DS05", "DS03", "S-CB050"], ["SRC-A", "SRC-F"],
                         {"family": "B (8 tests, BH)",
                          "inputs_from_other_packages": ["/experiments/SV-04/out/perturbation.csv (column severe not used)"],
                          "linkage": "DS03 natural dogs counted as SRC-A (SV-07); DS03 not pooled with S-CB050",
                          "n_subjects_note": "DS05 149 + S-CB050 140; the 101 DS03 dogs with age are S-CB050 dogs and are not counted again"}),
    "script": "/experiments/SV-05/scripts/analyse.py",
    "script_version": SCRIPT_VERSION,
    "run_utc": RUN_UTC,
    "n_subjects": DOGS["DS05"]["b_rossi"] + A1["n_young"] + A1["n_adult"], "n_variables": 6, "n_tests": 8,
    "summary": summary2,
}
foot2 = (f"Young = under 12 months; every effect is young minus adult. DS05: SRC-F, 147 dogs with a CBC. DS03 natural: SRC-A "
         f"(same dogs as S-CB050, SV-07). S-CB050: SRC-A. One species, two independent sources; contrasts are shown side by side, never pooled. {EXPL}.")
results2 = [
    {"kind": "primary_result", "title": "Primary analysis: is the form of disease different by age?", "sort_order": 1, "payload": {
        "label": "Anaemia and inflammatory form by age group, inside each source",
        "statistic": "Hodges-Lehmann difference, young minus adult",
        "verdict": verdict,
        "signals": {"anaemia": D["anaemia_form_signal"], "inflammatory": D["inflammatory_form_signal"], "risk": D["risk_signal"],
                    "against": D["against"]},
        "independent_sources": 2, "sources": [SOURCES["DS05"], SOURCES["DS03"], SOURCES["S-CB050"]],
        "rows": [rows["B1"], rows["B2"], rows["B3"], rows["B4"], rows["B5"]],
        "headline": headline2,
        "caveats": [EXPL + ".", SAME + ".", "Age stands in for prior exposure, breed and size, which are not recorded.",
                    "Healthy young dogs have a lower haematocrit than adults, so part of any young-adult difference is normal physiology."]}},
    {"kind": "contrasts", "title": "Family B: form tests (BH over 8)", "sort_order": 2, "payload": {
        "groups": [
            {"key": "anaemia", "label": "Anaemia form (lower in young = negative)", "note": SAME + ".",
             "rows": [rows["B1"], rows["B2"], rows["B6"]]},
            {"key": "inflammation", "label": "Inflammatory form (higher in adults = negative)", "note": "",
             "rows": [rows["B3"], rows["B4"], rows["B5"], rows["B7"]]},
            {"key": "timing", "label": "Presentation timing", "note": "Do young dogs present earlier? (step 4)", "rows": [rows["B8"]]},
        ],
        "footnote": foot2}},
]
sec_rows = [
    rank_row("balance", "SV-04 balance index (MCP-1 minus IL-8 percentile), S-CB050 cohort 1", "S-CB050", S["balance"], "balance", "points", 1),
    rank_row("z", "SV-04 z-score perturbation, S-CB050 cohort 1", "S-CB050", S["z_mean_abs"], "mean |z|", "SD"),
    rank_row("wbc", "WBC, S-CB050", "S-CB050", S["wbc"], "WBC", "10^9/L"),
    rank_row("seg", "Segmented neutrophils, S-CB050", "S-CB050", S["neut_seg"], "segmented", "10^9/L"),
]
sex_rows = [
    dict(rank_row("sex_hct", "Haematocrit, male minus female, DS05", "DS05", S["ds05_hct_by_sex"], "haematocrit", "L/L"),
         group_labels=["male", "female"]),
    dict(rank_row("sex_band", "Band neutrophils, male minus female, DS05", "DS05", S["ds05_band_by_sex"], "bands", "10^9/L"),
         group_labels=["male", "female"]),
]
results2.append({"kind": "secondary", "title": "Secondary contrasts (no claim, not in a family)", "sort_order": 3, "payload": {
    "groups": [{"key": "age", "label": "Other age contrasts (young minus adult)", "note": "", "rows": sec_rows},
               {"key": "sex", "label": "Sex contrasts (male minus female)", "note": "Sex differs between cases and controls in SRC-A.", "rows": sex_rows}],
    "footnote": foot2}})
s2r = T["S2"]
sens_groups = [
    {"key": "S1", "label": "S1: severe anaemia at hct < 0.20 (DS05)", "note": "",
     "rows": [share_row("S1", "Severe anaemia (hct < 0.20), DS05", "DS05", T["S1_severe_anaemia_020"], "share with hct < 0.20")]},
    {"key": "S2", "label": f"S2: DS05 without the {s2r['n_excluded']} E. canis co-infected dogs", "note": "",
     "rows": [rank_row("S2-B1", "Haematocrit", "DS05", s2r["B1"], "haematocrit", "L/L"),
              rank_row("S2-B3", "Band neutrophils", "DS05", s2r["B3"], "bands", "10^9/L"),
              share_row("S2-B6", "Severe anaemia (hct < 0.15)", "DS05", s2r["B6"], "share"),
              share_row("S2-B7", "Left shift (bands > 0.5)", "DS05", s2r["B7"], "share"),
              rank_row("S2-B8", "Illness duration", "DS05", s2r["B8"], "days", "days", 1)]},
    {"key": "S4", "label": "S4: DS05 inside each sex", "note": "",
     "rows": [rank_row(f"S4-{sx}-{k}", f"{'Haematocrit' if k == 'B1' else 'Band neutrophils'}, {sx}", "DS05", T["S4"][sx][k],
                       "", "L/L" if k == "B1" else "10^9/L") for sx in ("male", "female") for k in ("B1", "B3")]},
    {"key": "S3", "label": "S3: age as a continuous variable (Spearman rho, positive = higher with age)", "note": "",
     "rows": [rho_row("S3-1", "Haematocrit, DS05", "DS05", T["S3"]["DS05_hct"]),
              rho_row("S3-2", "Haematocrit, DS03 natural", "DS03", T["S3"]["DS03_hct"]),
              rho_row("S3-3", "Band neutrophils, DS05", "DS05", T["S3"]["DS05_band"]),
              rho_row("S3-4", "Band neutrophils, S-CB050", "S-CB050", T["S3"]["S-CB050_band"]),
              rho_row("S3-5", "Perturbation count, S-CB050 cohort 1", "S-CB050", T["S3"]["S-CB050_perturbation"]),
              rho_row("S3-6", "Illness duration, DS05", "DS05", T["S3"]["DS05_illness_days"])]},
]
results2.append({"kind": "sensitivity", "title": "Sensitivity checks S1 to S4", "sort_order": 4, "payload": {
    "groups": sens_groups, "footnote": foot2}})
c1 = T["C1"]
results2.append({"kind": "control_check", "title": "Check C1: haematocrit by age in healthy controls (DS03 = S-CB050 controls)", "sort_order": 5,
                 "payload": {"n_young": c1["n_young"], "n_adult": c1["n_adult"], "young_values": c1["young"],
                             "median_adult": c1["median_adult"], "range_adult": c1["range_adult"],
                             "footnote": ("Healthy control dogs of DS03 (the S-CB050 controls). Only 2 are under 12 months, so this "
                                          "is a description: their haematocrit is below every adult control.")}})
profile_series = []
for key, ds_, lab in (("hct_DS05", "DS05", "Haematocrit, DS05 (SRC-F)"), ("hct_DS03", "DS03", "Haematocrit, DS03 natural (SRC-A)"),
                      ("band_DS05", "DS05", "Bands, DS05 (SRC-F)"), ("band_S-CB050", "S-CB050", "Bands, S-CB050 (SRC-A)"),
                      ("illness_DS05", "DS05", "Illness days, DS05 (SRC-F)")):
    profile_series.append({"key": key, "label": lab, "dataset": ds_, "points": P[key]})
results2.append({"kind": "age_profile", "title": "Median by age band in each source (descriptive)", "sort_order": 6, "payload": {
    "bands": P["bands"], "measures": [
        {"key": "hct", "label": "Haematocrit (L/L)", "series": [s for s in profile_series if s["key"].startswith("hct")]},
        {"key": "band", "label": "Band neutrophils (10^9/L)", "series": [s for s in profile_series if s["key"].startswith("band")]},
        {"key": "illness", "label": "Illness duration (days)", "series": [s for s in profile_series if s["key"].startswith("illness")]}],
    "footnote": "Median and interquartile range per age band (months). Descriptive, no test. " + SAME + "."}})
nt = S["neuter"]
neuter_rows = []
for v, lab in (("age_months", "Age (months)"), ("weight_kg", "Weight (kg)"), ("hct", "Haematocrit (L/L)"),
               ("neut_band", "Band neutrophils (10^9/L)"), ("illness_days", "Illness duration (days)")):
    neuter_rows.append({"variable": lab, "neutered": nt["vars"][v]["neutered"], "intact_adult": nt["vars"][v]["intact_adult"]})
results2.append({"kind": "neuter_description", "title": "Neuter status in DS05 (described, not tested)", "sort_order": 7, "payload": {
    "n_neutered": nt["n_neutered"], "n_neutered_young": nt["n_neutered_young"], "sex_neutered": nt["sex_neutered"],
    "rows": neuter_rows,
    "footnote": f"DS05 has {nt['n_neutered']} neutered dogs ({nt['sex_neutered']['female']} female, {nt['sex_neutered']['male']} male), all adults: too few to test. Median (range) against intact adults. S-CB050 does not record neuter status."}})

b3, b4, b5, b6, b7, b8 = (B[k] for k in ("B3", "B4", "B5", "B6", "B7", "B8"))
interp2 = {"sections": [
    {"heading": "Question", "paragraphs": [
        "Is severe B. rossi disease anaemia-dominant in dogs under 12 months and inflammatory in older dogs? The package hypothesis "
        "is that age changes the form of disease more than the risk of death (the risk part is SV-05-01)."]},
    {"heading": "What was done", "paragraphs": [
        f"Inside each source, young dogs (under 12 months) were compared with adults on haematocrit (DS05, {b1['n_young']} vs {b1['n_adult']}; "
        f"DS03 natural, {b2['n_young']} vs {b2['n_adult']}), band neutrophils (DS05; S-CB050, {b4['n_young']} vs {b4['n_adult']}), the SV-04 "
        f"cytokine perturbation count (S-CB050 cohort 1, {b5['n_young']} vs {b5['n_adult']}), the share of dogs with severe anaemia and with a "
        "left shift (DS05) and days ill before presentation (DS05). Hodges-Lehmann differences with 2,000 bootstrap resamples of dogs, "
        "permutation p values (10,000), Benjamini-Hochberg over the 8 tests. A decision rule was written before the analysis. "
        "SV-07 found that the DS03 natural dogs are S-CB050 dogs, so DS03 is counted as the same source (SRC-A), never pooled and "
        "never called a replication; the independent sources are SRC-A and SRC-F (DS05). No outcome label is used in this experiment. "
        "S-CB050 and DS05 were seen before this plan, so the result is exploratory."]},
    {"heading": "Result", "paragraphs": [
        f"Verdict by the rule: {verdict}. Haematocrit in young minus adult dogs: DS05 {s2(b1['hl'])} L/L ({s2(b1['hl_low'])} to "
        f"{s2(b1['hl_high'])}, medians {f2(b1['median_young'])} vs {f2(b1['median_adult'])}), DS03 {s2(b2['hl'])} ({s2(b2['hl_low'])} to "
        f"{s2(b2['hl_high'])}, medians {f2(b2['median_young'])} vs {f2(b2['median_adult'])}, q {pt(b2['q'])}). The lower haematocrit "
        "of young dogs is clear only in the Onderstepoort dogs, and the two healthy young controls there are also below every "
        f"adult control (check C1), so part of it is the normal age difference. Severe anaemia: {pct(b6['share_young'])} of young vs "
        f"{pct(b6['share_adult'])} of adult DS05 dogs (difference {s2(b6['diff'])}, {s2(b6['diff_low'])} to {s2(b6['diff_high'])}).",
        f"No adult excess of inflammation: bands DS05 {s2(b3['hl'])} ({s2(b3['hl_low'])} to {s2(b3['hl_high'])}), S-CB050 {s2(b4['hl'])} "
        f"({s2(b4['hl_low'])} to {s2(b4['hl_high'])}); perturbation count Cliff's delta {s2(b5['cliff'])} ({s2(b5['cliff_low'])} to "
        f"{s2(b5['cliff_high'])}); left shift {pct(b7['share_young'])} vs {pct(b7['share_adult'])} ({s2(b7['diff'])}, {s2(b7['diff_low'])} "
        f"to {s2(b7['diff_high'])}). DS05 points the hypothesised way (fewer bands in young dogs) but every interval includes 0.",
        f"Young dogs presented earlier: median {f2(b8['median_young'], 0)} vs {f2(b8['median_adult'], 0)} days ill, HL {s2(b8['hl'], 0)} "
        f"({s2(b8['hl_low'], 0)} to {s2(b8['hl_high'], 0)}), Cliff's delta {s2(b8['cliff'])} ({s2(b8['cliff_low'])} to {s2(b8['cliff_high'])}), "
        f"p {pt(b8['p'])}, q {pt(b8['q'])}. {passed_b} of 8 tests pass q < 0.05 (DS03 haematocrit only). The 7 neutered DS05 dogs are "
        "all adults and are described, not tested."]},
    {"heading": "What this does not show", "paragraphs": [
        "It does not show that age does not change the form of disease: each contrast could detect only a difference of about "
        f"{f2(b1['detectable_sd'], 1)} SD or more. There is no outcome label in DS05 or DS03, so 'form of severe disease' is read "
        "from the whole infected population, not from the severe dogs. Age stands in for prior exposure, breed and size, which are "
        "not recorded. A between-source difference (DS03 against DS05) cannot be attributed to age: source, region, year and "
        "case mix differ."]},
]}
results2.append({"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp2})
write(code2, exp2, results2)
print("wrote", code1, code2)
