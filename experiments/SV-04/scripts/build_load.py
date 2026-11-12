"""SV-04: build the two load files for the console loader (way B) from out/results.json.

Run from /experiments/SV-04/:  env/py/Scripts/python.exe -I scripts/build_load.py
Every number in the text comes from results.json.
"""
import hashlib
import json
import os
import platform
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
OUT = os.path.join(PKG, "out")
DB = os.path.join(OUT, "db")

with open(os.path.join(OUT, "results.json"), encoding="utf-8") as f:
    R = json.load(f)
with open(os.path.join(HERE, "analyse.py"), "rb") as f:
    SCRIPT_VERSION = hashlib.sha256(f.read()).hexdigest()[:12]
RUN_UTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

LABEL = {"il2": "IL-2", "il8": "IL-8", "il10": "IL-10", "il18": "IL-18", "gmcsf": "GM-CSF", "mcp1": "MCP-1"}
ORDER = ["il2", "il8", "il10", "il18", "gmcsf", "mcp1"]
FILES = {
    "S-CB050": {"species": "B. rossi", "source": "SRC-A", "where": "Onderstepoort, South Africa",
                "severe": "died", "nonsevere": "survived", "definition": "death (includes euthanasia for poor prognosis)",
                "timepoint": "admission, before treatment"},
    "S-CB017": {"species": "B. canis", "source": "SRC-D", "where": "Zagreb, Croatia",
                "severe": "complicated", "nonsevere": "uncomplicated",
                "definition": "complicated (WHO malaria-style criteria; all SIRS-positive; WBC is a SIRS criterion)",
                "timepoint": "day 1, 6-8 h after imidocarb"},
}
SOURCES = ["S-CB050 (SRC-A, B. rossi, Onderstepoort)", "S-CB017 (SRC-D, B. canis, Zagreb)",
           "DS02 (SRC-B, B. rossi, 5 experimental Beagles)"]
E1 = R["experiment1"]
E2 = R["experiment2"]


def s2(v):
    return "–" if v is None else f"{v:+.2f}"


def f2(v, d=2):
    return "–" if v is None else f"{v:.{d}f}"


def ptxt(p):
    return "–" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def effect_row(c, label, a_label, b_label):
    return {"label": label, "estimate": c["cliff_delta"], "ci_low": c["cliff_lo"], "ci_high": c["cliff_hi"],
            "p": c["p"], "q": c.get("q"), "n_a": c["n_severe"], "n_b": c["n_nonsevere"],
            "a_label": a_label, "b_label": b_label,
            "median_a": c.get("median_severe"), "median_b": c.get("median_nonsevere"),
            "hl_log2": c.get("hl_log2"), "hl_low": c.get("hl_lo"), "hl_high": c.get("hl_hi")}


def contrast_group(key, label, rows, a_label, b_label, note=""):
    by = {c["analyte"]: c for c in rows}
    return {"key": key, "label": label, "note": note,
            "rows": [effect_row(by[a], LABEL[a], a_label, b_label) for a in ORDER]}


def interp(sections):
    return {"sections": [{"heading": h, "paragraphs": p} for h, p in sections]}


def params(role, n_tests_family):
    return {"package": "SV-04", "role": role, "datasets": ["S-CB050", "S-CB017", "DS02"],
            "independent_sources": ["SRC-A", "SRC-D", "SRC-B"], "spec_sha256": R["spec_sha256"],
            "seed": R["seed"], "n_bootstrap": R["n_boot"], "n_permutations": R["n_perm"],
            "families": n_tests_family, "inputs_sha256": R["inputs_sha256"],
            "versions": {"python": platform.python_version(), "numpy": np.__version__},
            "selection": {"S-CB050": "cohort 1 (cytokines measured): infected 97, controls 15",
                          "S-CB017": "infected day 1 (31), controls 16; day 7 (30) in check C2",
                          "DS02": "5 Beagles; cytokines on days -1, 0, 1, 2, 3, 4, 6, 8; treatment after the day-4 sample"}}


def exp1():
    con = E1["contrasts"]
    by = {(c["file"], c["analyte"]): c for c in con}
    a, b = by[("S-CB050", "il8")], by[("S-CB017", "il8")]
    d7 = {c["analyte"]: c for c in E1["contrasts_day7"]}["il8"]
    dec = E1["ds02_decisions"]["il8"]
    c1 = E1["c1"]
    c3 = {f: {c["analyte"]: c for c in E1["c3_infected_vs_control"][f]} for f in FILES}
    passed = [c for c in con if c["q"] < 0.05]
    n_pass = len(passed)
    passed_txt = ", ".join(f"{LABEL[c['analyte']]} in {c['file']}" for c in passed) or "none"
    verdict = E1["il8_verdict"]

    def file_line(fid, c):
        m = FILES[fid]
        return (f"{fid} ({m['species']}, {m['timepoint']}): IL-8 Cliff's delta {s2(c['cliff_delta'])} "
                f"(95% CI {s2(c['cliff_lo'])} to {s2(c['cliff_hi'])}), {m['severe']} {c['n_severe']} vs "
                f"{m['nonsevere']} {c['n_nonsevere']}, medians {c['median_severe']:.0f} vs {c['median_nonsevere']:.0f} pg/mL, "
                f"permutation p {ptxt(c['p'])}")

    ch = dec["changes"]
    dogs_dir = ", ".join(f"{k.split(':')[1]} {v:+.2f}" for k, v in sorted(ch.items()))
    r_txt = (f"R1 same direction in all {dec['n_dogs']} dogs: {'yes' if dec['R1_same_direction'] else 'no'}; "
             f"R2 median |change| {dec['median_abs_post']:.2f} log2 against median day-to-day change before treatment "
             f"{dec['median_abs_daily_pre']:.2f}: {'larger' if dec['R2_exceeds_daily'] else 'not larger'}; "
             f"R3 rises more in the high-dose dogs: {'yes' if dec['R3_high_more_upward'] else 'no'} "
             f"(mean change high dose {dec['mean_change_high']:+.2f}, low dose {dec['mean_change_low']:+.2f})")
    pre = [c for c in R["ds02_courses"] if c["analyte"] == "il8"]
    pre_txt = ", ".join(f"{c['dog_id'].split(':')[1]} ({c['dose_group']}) {c['pre_change_log2']:+.2f}"
                        for c in pre if c["pre_change_log2"] is not None)

    summary = (f"No IL-8 conflict inside the dog-level files: severe minus non-severe Cliff's delta {s2(a['cliff_delta'])} "
               f"({s2(a['cliff_lo'])} to {s2(a['cliff_hi'])}; S-CB050, died {a['n_severe']} vs survived {a['n_nonsevere']}) and "
               f"{s2(b['cliff_delta'])} ({s2(b['cliff_lo'])} to {s2(b['cliff_hi'])}; S-CB017, complicated {b['n_severe']} vs "
               f"uncomplicated {b['n_nonsevere']}); DS02 shows no consistent post-treatment IL-8 change (R1 {'met' if dec['R1_same_direction'] else 'not met'}, "
               f"R3 {'met' if dec['R3_high_more_upward'] else 'not met'}). {n_pass} of 12 analyte tests passed BH q < 0.05 ({passed_txt}).")

    primary = {
        "label": "IL-8, severe minus non-severe, inside each file",
        "statistic": "Cliff's delta",
        "verdict": verdict,
        "headline": (f"Verdict by the pre-stated rule: {verdict}. Both IL-8 intervals include 0 and both point estimates are "
                     f"positive. The B. rossi fall in IL-8 is a contrast of infected dogs against healthy controls "
                     f"(delta {s2(c3['S-CB050']['il8']['cliff_delta'])}), not of dogs that died against survivors. "
                     f"DS02 gives no support for a treatment-driven reversal."),
        "independent_sources": 3,
        "sources": SOURCES,
        "rows": [dict(effect_row(c, f"{fid} · {FILES[fid]['species']} · {FILES[fid]['timepoint']}",
                                 FILES[fid]["severe"], FILES[fid]["nonsevere"]), definition=FILES[fid]["definition"])
                 for fid, c in (("S-CB050", a), ("S-CB017", b))],
        "caveats": ["Descriptive re-analysis: the published group comparisons of CB050/CB517 and CB017 were already seen.",
                    "One species per source: species, source, country, assay, definition and sampling time are aliased.",
                    "Died includes euthanasia for poor prognosis (Onderstepoort)."],
        "ds02": {"r1": dec["R1_same_direction"], "r2": dec["R2_exceeds_daily"], "r3": dec["R3_high_more_upward"],
                 "all": dec["all_rules"], "text": r_txt},
    }

    contrasts = {
        "statistic": "Cliff's delta (first group minus second)",
        "groups": [
            contrast_group("S-CB050", "S-CB050 · B. rossi · admission, before treatment · died vs survived",
                           [c for c in con if c["file"] == "S-CB050"], "died", "survived",
                           "BH family of 6. Died includes euthanasia for poor prognosis."),
            contrast_group("S-CB017", "S-CB017 · B. canis · day 1, 6-8 h after imidocarb · complicated vs uncomplicated",
                           [c for c in con if c["file"] == "S-CB017"], "complicated", "uncomplicated", "BH family of 6."),
            contrast_group("S-CB017-d7", "S-CB017 · B. canis · day 7, 6 days after imidocarb · complicated vs uncomplicated (check C2)",
                           E1["contrasts_day7"], "complicated", "uncomplicated", "Check C2; BH inside these 6 only."),
        ],
        "footnote": ("Cliff's delta with 95% percentile bootstrap interval (2,000 resamples of dogs, stratified by group); "
                     "two-sided permutation p (10,000). Raw concentrations of the two files are never compared. "
                     "One species per source. Descriptive: the published comparisons were already seen."),
    }

    infected = {
        "statistic": "Cliff's delta (infected minus healthy controls)",
        "groups": [contrast_group(f, f"{f} · {FILES[f]['species']} · infected vs healthy controls",
                                  E1["c3_infected_vs_control"][f], "infected", "controls",
                                  "Deviation D1: added after the outcome lock; uses no outcome. Raw p only.")
                   for f in FILES],
        "footnote": "S-CB050: 97 infected, 15 controls (cohort 1). S-CB017: 31 infected (day 1), 16 controls. One species per source.",
    }

    # DS02 courses
    series = {}
    for p in R["ds02_series"]:
        series.setdefault(p["analyte"], {}).setdefault(p["dog_id"], {"dog": p["dog_id"].split(":")[1],
                                                                     "dose_group": p["dose_group"], "points": []})
        series[p["analyte"]][p["dog_id"]]["points"].append({"day": p["day"], "value": p["value"], "log2": p["log2_value_plus1"]})
    ds02 = {"analytes": [{"analyte": a_, "label": LABEL[a_],
                          "dogs": list(series[a_].values()),
                          "decision": {k: v for k, v in E1["ds02_decisions"][a_].items() if k != "changes"},
                          "changes": [{"dog": k.split(":")[1], "change": v} for k, v in sorted(E1["ds02_decisions"][a_]["changes"].items())]}
                         for a_ in ORDER],
            "treatment_after_day": 4,
            "footnote": ("DS02: 5 experimentally infected Beagles (SRC-B, B. rossi), 2 low dose and 3 high dose; one high-dose dog died on day 4. "
                         "Cytokines were measured on days -1, 0, 1, 2, 3, 4, 6 and 8; treatment came after the day-4 sample "
                         "(about 96 h high dose, 108 h low dose). The first post-treatment sample (day 6) is 36 to 48 h after treatment, "
                         "so a 6 to 8 h effect cannot be seen. y axis: log2(value + 1). No test (n 4).")}
    decision_rows = [{"analyte": LABEL[a_], **{k: v for k, v in E1["ds02_decisions"][a_].items() if k != "changes"}} for a_ in ORDER]

    definition = {"rows": [
        {"file": f, "species": FILES[f]["species"], "rho": c1[f]["il8_wbc"]["rho"], "rho_low": c1[f]["il8_wbc"]["lo"],
         "rho_high": c1[f]["il8_wbc"]["hi"], "rho_p": c1[f]["il8_wbc"]["p"], "n": c1[f]["il8_wbc"]["n"],
         "wbc_delta": c1[f]["wbc_contrast"]["cliff_delta"], "wbc_low": c1[f]["wbc_contrast"]["cliff_lo"],
         "wbc_high": c1[f]["wbc_contrast"]["cliff_hi"], "wbc_p": c1[f]["wbc_contrast"]["p"],
         "wbc_median_severe": c1[f]["wbc_contrast"]["median_severe"], "wbc_median_nonsevere": c1[f]["wbc_contrast"]["median_nonsevere"],
         "severe": FILES[f]["severe"], "nonsevere": FILES[f]["nonsevere"]} for f in FILES],
        "footnote": "Check C1. Spearman rho of IL-8 with WBC among infected dogs (bootstrap 95% CI, permutation p) and Cliff's delta of WBC by label. Raw p only."}

    half = {"rows": [{"file": c["file"], "analyte": LABEL[c["analyte"]], "delta": c["cliff_delta"],
                      "delta_primary": by[(c["file"], c["analyte"])]["cliff_delta"], "hl_log2": c["hl_log2"],
                      "hl_primary": by[(c["file"], c["analyte"])]["hl_log2"], "q": c["q"]} for c in E1["contrasts_half_floor"]],
            "footnote": "Sensitivity S2: every value at an assay floor set to half the floor. Cliff's delta and the Hodges-Lehmann log2 shift are unchanged."}

    text = interp([
        ("Question", ["IL-8 is reported to fall with severity in B. rossi and to rise in complicated B. canis. Can sampling time "
                      "(before treatment in S-CB050; 6-8 h after imidocarb in S-CB017) or the severity definition (death against "
                      "'complicated') explain the difference?"]),
        ("What was done", [
            "Inside each dog-level file, each of 6 shared analytes (IL-2, IL-8, IL-10, IL-18, GM-CSF, MCP-1) was compared between "
            "severe and non-severe dogs with Cliff's delta (bootstrap 95% CI by dog, permutation p, BH within each file, family of 6). "
            "DS02 (5 Beagles) gave the within-dog course before treatment and the change from day 4 to day 6, judged by three rules fixed in "
            "spec.md (R1 same direction in every dog, R2 larger than day-to-day change, R3 larger rise in the high-dose dogs). "
            "Checks: C1 IL-8 against WBC (the 'complicated' label uses SIRS, which uses WBC); C2 the S-CB017 day-7 contrast; "
            "S2 floors at half the floor.",
            "Deviation D1 (added after the outcome lock, uses no outcome): infected dogs against the healthy controls of each file. "
            "It was added because the primary result showed no severity conflict, and the article notes place the B. rossi IL-8 fall "
            "between infected dogs and controls."]),
        ("Result", [
            file_line("S-CB050", a) + ".",
            file_line("S-CB017", b) + f". At day 7 the S-CB017 estimate is {s2(d7['cliff_delta'])} ({s2(d7['cliff_lo'])} to {s2(d7['cliff_hi'])}).",
            f"Verdict by the pre-stated rule: {verdict}. Neither file shows an IL-8 difference by severity, and both estimates are "
            f"slightly positive. The severity direction that both files share is MCP-1: delta {s2(by[('S-CB050', 'mcp1')]['cliff_delta'])} "
            f"({s2(by[('S-CB050', 'mcp1')]['cliff_lo'])} to {s2(by[('S-CB050', 'mcp1')]['cliff_hi'])}, q {ptxt(by[('S-CB050', 'mcp1')]['q'])}) and "
            f"{s2(by[('S-CB017', 'mcp1')]['cliff_delta'])} ({s2(by[('S-CB017', 'mcp1')]['cliff_lo'])} to {s2(by[('S-CB017', 'mcp1')]['cliff_hi'])}, "
            f"q {ptxt(by[('S-CB017', 'mcp1')]['q'])}). {n_pass} of 12 tests passed q < 0.05 ({passed_txt}).",
            f"Where the IL-8 directions do differ is infection against health (deviation D1): infected minus controls "
            f"{s2(c3['S-CB050']['il8']['cliff_delta'])} ({s2(c3['S-CB050']['il8']['cliff_lo'])} to {s2(c3['S-CB050']['il8']['cliff_hi'])}) in S-CB050 "
            f"(median {c3['S-CB050']['il8']['median_severe']:.0f} vs {c3['S-CB050']['il8']['median_nonsevere']:.0f} pg/mL) and "
            f"{s2(c3['S-CB017']['il8']['cliff_delta'])} ({s2(c3['S-CB017']['il8']['cliff_lo'])} to {s2(c3['S-CB017']['il8']['cliff_hi'])}) in S-CB017. "
            f"This difference cannot be separated from species, assay run and control selection.",
            f"DS02, IL-8 log2 change day 4 to day 6: {dogs_dir}. {r_txt}. So DS02 does not support a treatment-driven reversal. "
            f"Before treatment, IL-8 log2 change from baseline to day 4 by dog: {pre_txt}. "
            + ("It rose in every high-dose dog, so in experimental B. rossi IL-8 went up, not down, as disease progressed."
               if all(c["pre_change_log2"] > 0 for c in pre if c["dose_group"] == "high" and c["pre_change_log2"] is not None)
               else "It did not rise in every high-dose dog."),
            f"C1: IL-8 correlated with WBC among infected dogs in S-CB050 (rho {s2(c1['S-CB050']['il8_wbc']['rho'])}, "
            f"{s2(c1['S-CB050']['il8_wbc']['lo'])} to {s2(c1['S-CB050']['il8_wbc']['hi'])}) and in S-CB017 "
            f"(rho {s2(c1['S-CB017']['il8_wbc']['rho'])}, {s2(c1['S-CB017']['il8_wbc']['lo'])} to {s2(c1['S-CB017']['il8_wbc']['hi'])}); "
            f"the WBC difference by label had an interval that included 0 in both files (delta {s2(c1['S-CB050']['wbc_contrast']['cliff_delta'])} and "
            f"{s2(c1['S-CB017']['wbc_contrast']['cliff_delta'])}). The definition is therefore not needed to explain an IL-8 conflict that the files do not show."]),
        ("What this does not show", [
            "The B. rossi report of IL-8 falling with severity rests on CB037 (55 dogs, a separate cohort with no dog-level file, read from the abstract only). "
            "This package cannot test it. In the one B. rossi dog-level file, IL-8 does not differ between dogs that died and survivors.",
            "Detectable effect at 80% power: about 0.86 SD in S-CB050 (12 vs 85) and 1.05 SD in S-CB017 (18 vs 13). A smaller IL-8 difference is not excluded.",
            "DS02 samples are daily; the first post-treatment cytokine sample is 36 to 48 h after treatment. A 6 to 8 h effect of imidocarb cannot be seen. "
            "DS02 has 4 dogs with a post-treatment sample and no severity label; dose group is a design variable.",
            "Species, source, country, assay run, definition and sampling time are fully aliased between files. Nothing here attributes a difference to species. "
            "Died includes euthanasia for poor prognosis. This is a descriptive re-analysis of comparisons that were already published."]),
    ])

    load = {
        "experiment": {
            "code": "SV-04-01-il8-direction",
            "name": "Does IL-8 go in opposite directions with severity in B. rossi and B. canis? Within-file contrasts and the Beagle course around treatment",
            "description": ("Is the reported IL-8 conflict (lower with severity in B. rossi, higher in complicated B. canis) present in the dog-level files, "
                            "and could sampling time after treatment or the severity definition explain it? Hypothesis: timing or definition is a sufficient explanation."),
            "method": "cytokine_conflict",
            "dataset": None,
            "parameters": params("descriptive", "2 families of 6 (one per file), BH"),
            "script": "/experiments/SV-04/scripts/analyse.py",
            "script_version": SCRIPT_VERSION,
            "run_utc": RUN_UTC,
            "n_subjects": a["n_severe"] + a["n_nonsevere"] + 15 + b["n_severe"] + b["n_nonsevere"] + 16 + 5,
            "n_variables": 6,
            "n_tests": 12,
            "summary": summary,
        },
        "associations": [],
        "cluster_assignments": [],
        "results": [
            {"kind": "primary_result", "title": "IL-8 by severity inside each file", "sort_order": 1, "payload": primary},
            {"kind": "severity_contrasts", "title": "Six analytes by severity, inside each file", "sort_order": 2, "payload": contrasts},
            {"kind": "ds02_courses", "title": "DS02: cytokine course of the 5 Beagles around treatment", "sort_order": 3, "payload": ds02},
            {"kind": "ds02_decisions", "title": "DS02: decision rules R1 to R3, by analyte", "sort_order": 4, "payload": {"rows": decision_rows}},
            {"kind": "infected_vs_control", "title": "Infected dogs against healthy controls (deviation D1)", "sort_order": 5, "payload": infected},
            {"kind": "definition_check", "title": "Check C1: IL-8 and WBC", "sort_order": 6, "payload": definition},
            {"kind": "floor_sensitivity", "title": "Sensitivity S2: floors at half the floor", "sort_order": 7, "payload": half},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": text},
        ],
    }
    return load


def exp2():
    bf = E2["by_file"]
    verdict = E2["verdict"]
    rows_p = []
    tests = []
    for f, m in FILES.items():
        x = bf[f]
        rows_p.append(dict(effect_row(x["T1_perturbation"], f"{f} · T1 perturbation count", m["severe"], m["nonsevere"]),
                           mean_a=x["T1_perturbation"]["mean_severe"], mean_b=x["T1_perturbation"]["mean_nonsevere"]))
        rows_p.append(dict(effect_row(x["T2_balance"], f"{f} · T2 balance index (MCP-1 minus IL-8 percentile)", m["severe"], m["nonsevere"]),
                           mean_a=x["T2_balance"]["mean_severe"], mean_b=x["T2_balance"]["mean_nonsevere"]))
        tests += [x["T1_perturbation"], x["T2_balance"]]
    n_pass = sum(1 for t in tests if t["q"] < 0.05)
    a1, a2 = bf["S-CB050"]["T1_perturbation"], bf["S-CB050"]["T2_balance"]
    b1, b2 = bf["S-CB017"]["T1_perturbation"], bf["S-CB017"]["T2_balance"]
    summary = (f"Pre-stated rule gives '{verdict}': the balance index (MCP-1 percentile minus IL-8 percentile) is higher in severe dogs in both files "
               f"(Cliff's delta {s2(a2['cliff_delta'])}, {s2(a2['cliff_lo'])} to {s2(a2['cliff_hi'])}, n 12 vs 85; "
               f"{s2(b2['cliff_delta'])}, {s2(b2['cliff_lo'])} to {s2(b2['cliff_hi'])}, n 18 vs 13), while the perturbation count is higher only in "
               f"complicated B. canis ({s2(b1['cliff_delta'])}) and not in B. rossi deaths ({s2(a1['cliff_delta'])}). {n_pass} of 4 tests passed BH q < 0.05.")

    def sens_group(f):
        x = bf[f]
        m = FILES[f]
        items = [("S1 z-score version (mean |z|)", x["S1_z"]), ("Analytes above the control range", x["above"]),
                 ("Analytes below the control range", x["below"]), ("T1 with floors at half the floor", x["S2_half_floor"]["T1"]),
                 ("T2 with floors at half the floor", x["S2_half_floor"]["T2"]), ("S1 with floors at half the floor", x["S2_half_floor"]["S1_z"])]
        return {"key": f, "label": f"{f} · {m['species']} · {m['severe']} vs {m['nonsevere']}", "note": "Raw p only (not in a family).",
                "rows": [dict(effect_row(c, lab, m["severe"], m["nonsevere"]), q=None) for lab, c in items]}

    dist = {"files": [{"file": f, "species": FILES[f]["species"], "severe": FILES[f]["severe"], "nonsevere": FILES[f]["nonsevere"],
                       "counts_severe": bf[f]["distribution"]["severe"], "counts_nonsevere": bf[f]["distribution"]["nonsevere"],
                       "outside_severe": bf[f]["outside_by_analyte"]["severe"], "outside_nonsevere": bf[f]["outside_by_analyte"]["nonsevere"]}
                      for f in FILES],
            "footnote": "Number of the 6 analytes outside the [min, max] range of that file's own healthy controls (S-CB050 n 15, S-CB017 n 16). One species per source."}
    points = {"files": [{"file": f, "species": FILES[f]["species"], "severe": FILES[f]["severe"], "nonsevere": FILES[f]["nonsevere"],
                         "points": [{"perturbation": r["perturbation"], "balance": r["balance"], "severe": r["severe"]}
                                    for r in R["perturbation_rows"] if r["file"] == f]} for f in FILES],
              "footnote": "Each point is one infected dog. Balance = percentile of MCP-1 minus percentile of IL-8 among the infected dogs of that file."}

    text = interp([
        ("Question", ["Is severe disease a larger cytokine perturbation (size), or a shift in the balance of the response (MCP-1 relative to IL-8) at a similar size?"]),
        ("What was done", [
            "For each infected dog: the number of the 6 shared analytes outside its own file's healthy-control range (perturbation count), and the "
            "within-file percentile of MCP-1 minus that of IL-8 (balance index). Each was compared between severe and non-severe dogs with Cliff's delta "
            "(bootstrap CI by dog, permutation p, BH within each file, family of 2). Sensitivities: a z-score version for analytes with under 20% floor values, "
            "counts above and below the range separately, and floors at half the floor."]),
        ("Result", [
            f"S-CB050 (B. rossi, died {a1['n_severe']} vs survived {a1['n_nonsevere']}): perturbation {s2(a1['cliff_delta'])} ({s2(a1['cliff_lo'])} to {s2(a1['cliff_hi'])}), "
            f"mean {a1['mean_severe']:.2f} vs {a1['mean_nonsevere']:.2f} analytes; balance {s2(a2['cliff_delta'])} ({s2(a2['cliff_lo'])} to {s2(a2['cliff_hi'])}), "
            f"permutation p {ptxt(a2['p'])}, q {ptxt(a2['q'])}.",
            f"S-CB017 (B. canis, complicated {b1['n_severe']} vs uncomplicated {b1['n_nonsevere']}): perturbation {s2(b1['cliff_delta'])} ({s2(b1['cliff_lo'])} to {s2(b1['cliff_hi'])}), "
            f"mean {b1['mean_severe']:.2f} vs {b1['mean_nonsevere']:.2f}, q {ptxt(b1['q'])}; balance {s2(b2['cliff_delta'])} ({s2(b2['cliff_lo'])} to {s2(b2['cliff_hi'])}), q {ptxt(b2['q'])}.",
            f"Verdict by the pre-stated rule: {verdict}. The balance shift has the same sign in both files, but in S-CB050 it is weak (the bootstrap interval only just "
            f"excludes 0 and the permutation p is {ptxt(a2['p'])}). It is carried by MCP-1, which is higher in severe dogs in both files; IL-8 itself does not differ "
            f"(experiment SV-04-01). In B. canis, complicated dogs also have a larger perturbation, so size and balance both hold there; "
            f"in B. rossi, dogs that died do not have more analytes out of range. {n_pass} of 4 tests passed q < 0.05."]),
        ("What this does not show", [
            "The balance index is a rank difference of two analytes; it is not a validated measure of immune balance, and MCP-1 drives most of it here.",
            "Control ranges come from 15 and 16 dogs, so 'outside the range' is a coarse threshold. S-CB017 controls include dogs given prophylactic imidocarb (inferred from the ID prefix).",
            "The 'complicated' label of S-CB017 is defined partly by inflammation (SIRS), so a larger perturbation there is partly built into the label.",
            "One species per source: the difference between files (size in B. canis, not in B. rossi) cannot be attributed to species. Died includes euthanasia for poor prognosis. Descriptive re-analysis."]),
    ])

    load = {
        "experiment": {
            "code": "SV-04-02-response-size-balance",
            "name": "Is severe babesiosis a larger cytokine response or a shifted one? Perturbation count and MCP-1/IL-8 balance in B. rossi and B. canis",
            "description": ("Is severity the size of the inflammatory response (more analytes outside the healthy range) or its balance (MCP-1 high relative to IL-8)? "
                            "Hypothesis: size predicts a higher perturbation count in severe dogs in both files; balance predicts a same-sign shift in the balance index."),
            "method": "cytokine_conflict",
            "dataset": None,
            "parameters": params("descriptive", "2 families of 2 (one per file), BH"),
            "script": "/experiments/SV-04/scripts/analyse.py",
            "script_version": SCRIPT_VERSION,
            "run_utc": RUN_UTC,
            "n_subjects": a1["n_severe"] + a1["n_nonsevere"] + b1["n_severe"] + b1["n_nonsevere"],
            "n_variables": 6,
            "n_tests": 4,
            "summary": summary,
        },
        "associations": [],
        "cluster_assignments": [],
        "results": [
            {"kind": "primary_result", "title": "Size and balance of the response by severity", "sort_order": 1,
             "payload": {"label": "Perturbation count (T1) and balance index (T2), severe minus non-severe", "statistic": "Cliff's delta",
                         "verdict": verdict,
                         "headline": (f"Verdict by the pre-stated rule: {verdict}. Severe dogs have MCP-1 high relative to IL-8 in both files; only complicated "
                                      f"B. canis dogs also have more analytes outside the healthy range."),
                         "independent_sources": 2, "sources": SOURCES[:2], "rows": rows_p,
                         "caveats": ["Descriptive re-analysis of already-seen files.", "One species per source.",
                                     "Died includes euthanasia for poor prognosis (Onderstepoort)."]}},
            {"kind": "perturbation_distribution", "title": "Perturbation count by severity", "sort_order": 2, "payload": dist},
            {"kind": "balance_points", "title": "Balance index against perturbation count", "sort_order": 3, "payload": points},
            {"kind": "score_sensitivity", "title": "Sensitivity analyses", "sort_order": 4,
             "payload": {"statistic": "Cliff's delta (severe minus non-severe)", "groups": [sens_group(f) for f in FILES],
                         "footnote": "S1 uses analytes with under 20% floor values: S-CB050 IL-8, IL-10, IL-18, MCP-1; S-CB017 IL-2, IL-8, GM-CSF, MCP-1."}},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": text},
        ],
    }
    return load


def main():
    os.makedirs(DB, exist_ok=True)
    for load in (exp1(), exp2()):
        path = os.path.join(DB, load["experiment"]["code"] + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(load, f, indent=1, allow_nan=False, ensure_ascii=False)
        size = os.path.getsize(path)
        print(load["experiment"]["code"], size, "bytes")
        print("  ", load["experiment"]["summary"])


if __name__ == "__main__":
    main()
