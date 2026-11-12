"""SV-01: build the figures and the two database load files (way B) from out/.

Run after analyse.py:  env/py/Scripts/python.exe -I scripts/build_load.py   (from /experiments/SV-01)
Writes out/figure_map_A.svg, out/figure_map_B.svg, out/db/SV-01-01-habitus-distance.json, out/db/SV-01-02-ds03-geometry.json.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("svg")
matplotlib.rcParams["svg.hashsalt"] = "SV-01"
import matplotlib.pyplot as plt  # noqa: E402

PKG = Path(__file__).resolve().parents[1]
OUT = PKG / "out"
SCRIPT = PKG / "scripts" / "analyse.py"

R = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
T = R["time_anchored"]
RUN_UTC = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
SCRIPT_VERSION = hashlib.sha256(SCRIPT.read_bytes()).hexdigest()[:12]

GROUP_LABELS = {
    "DS05": "DS05 natural (clinic, Eastern Cape)",
    "DS03_c1": "DS03 natural, cohort 1 (Onderstepoort)",
    "DS03_c2": "DS03 natural, cohort 2 (Onderstepoort)",
    "DS03_healthy": "DS03 healthy controls (reference)",
    "DS03_imha": "DS03 IMHA comparators (reference)",
}


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    return None if v in ("", None) else float(v)


def f2(v, d=2):
    return "–" if v is None else f"{v:.{d}f}"


def pct(v):
    return "–" if v is None else f"{100 * v:.0f}%"


def p_text(p):
    return "–" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


MAP = read_csv(OUT / "map_points.csv")
CURVES = read_csv(OUT / "curves.csv")
CURVES_T = read_csv(OUT / "time_anchored" / "curves.csv")
HAB = {r["dog_id"]: int(r["habitus_score"]) for r in read_csv(OUT / "ds05_habitus_for_map.csv")}


def curve(rows, plane, arm):
    return [{"x": num(r["hct"]), "y": num(r["y"]), "stage": num(r["stage"])}
            for r in rows if r["plane"] == plane and r["arm"] == arm]


def beagles(plane):
    return [{"dog": r["dog_id"], "day": num(r["day"]), "timepoint": r["timepoint"], "x": num(r["hct"]), "y": num(r["y"]),
             "post": r["post_treatment"] == "1", "stage": num(r["pseudo_stage"]), "distance": num(r["distance"])}
            for r in MAP if r["plane"] == plane and r["group"] == "DS02_beagle"]


def group_points(plane, key, with_habitus=False):
    pts = []
    for r in MAP:
        if r["plane"] == plane and r["group"] == key:
            p = {"id": r["dog_id"], "x": num(r["hct"]), "y": num(r["y"]), "stage": num(r["pseudo_stage"]),
                 "distance": num(r["distance"]), "beyond_end": r["beyond_end"] == "1"}
            if with_habitus:
                p["habitus"] = HAB.get(r["dog_id"])
            pts.append(p)
    return pts


def map_payload(plane, keys, habitus):
    y_label = "log10 reticulocytes (ARC, 10^9/L)" if plane == "A" else "log10 (band neutrophils + 0.05), 10^9/L"
    return {
        "plane": plane,
        "x_label": "Haematocrit (L/L)",
        "y_label": y_label,
        "y_is_log10": True,
        "y_offset": 0.0 if plane == "A" else 0.05,
        "course": curve(CURVES, plane, "pre"),
        "post_arm": curve(CURVES, plane, "post"),
        "course_time_anchored": curve(CURVES_T, plane, "pre"),
        "beagles": beagles(plane),
        "groups": [{"key": k, "label": GROUP_LABELS[k], "colour_by_habitus": habitus and k == "DS05",
                    "points": group_points(plane, k, habitus and k == "DS05")} for k in keys],
        "spread_sd_units": R[f"course_{plane}"]["spread_sd_units"],
        "within_band_distance": 2.0,
    }


# ---------------------------------------------------------------- figures (for report.md)

def figure(plane, keys, path):
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    colours = {"DS05": "#3366b0", "DS03_c1": "#c6483a", "DS03_c2": "#d98c1f", "DS03_healthy": "#4b9b5f", "DS03_imha": "#7d5ba6"}
    for k in keys:
        pts = group_points(plane, k)
        ax.scatter([p["x"] for p in pts], [p["y"] for p in pts], s=14, alpha=0.55, color=colours[k], label=GROUP_LABELS[k])
    b = beagles(plane)
    pre = [p for p in b if not p["post"]]
    post = [p for p in b if p["post"]]
    ax.scatter([p["x"] for p in pre], [p["y"] for p in pre], s=40, marker="D", color="black", label="Beagles before treatment")
    ax.scatter([p["x"] for p in post], [p["y"] for p in post], s=40, marker="D", facecolors="none", edgecolors="black",
               label="Beagles after treatment")
    c = curve(CURVES, plane, "pre")
    ax.plot([p["x"] for p in c], [p["y"] for p in c], color="black", lw=2.2, label="Reference course (spec construction)")
    ct = curve(CURVES_T, plane, "pre")
    ax.plot([p["x"] for p in ct], [p["y"] for p in ct], color="black", lw=1.5, ls="--", label="Time-anchored course (deviation D1)")
    cp = curve(CURVES, plane, "post")
    if cp:
        ax.plot([p["x"] for p in cp], [p["y"] for p in cp], color="grey", lw=1.5, ls=":", label="Post-treatment arm")
    ax.set_xlabel("Haematocrit (L/L)")
    ax.set_ylabel("log10 ARC (10^9/L)" if plane == "A" else "log10 (band neutrophils + 0.05)")
    ax.set_title(f"SV-01 disease space, plane {plane}")
    ax.legend(fontsize=7, loc="best")
    fig.tight_layout()
    fig.savefig(path, metadata={"Date": None})
    plt.close(fig)


# ---------------------------------------------------------------- load files

def tests_rows(src):
    return [{**t, "p_text": p_text(t["p"]), "q_text": p_text(t["q"])} for t in src["tests"]]


def checks(src, label):
    v = src["validity"]
    sv = src["course_A_stage_vs_day"]
    return {
        "construction": label,
        "rows": [
            {"name": "Construction check (added after the first run): Beagle pseudo-stage rises with day",
             "estimate": sv, "detail": f"Spearman rho of pseudo-stage with sampling day over the 22 pre-treatment Beagle points: {f2(sv)}",
             "passed": sv is not None and sv >= 0.5},
            {"name": "Validity check (stated in advance): pseudo-stage rises with owner-reported illness duration (DS05)",
             "estimate": v["estimate"], "ci_low": v["ci_low"], "ci_high": v["ci_high"], "p": v["p"], "n": v["n"],
             "detail": f"rho {f2(v['estimate'])} (95% CI {f2(v['ci_low'])} to {f2(v['ci_high'])}), permutation p {p_text(v['p'])}, n {v['n']}",
             "passed": bool(v["passed"])},
        ],
    }


def exp1():
    h1, s3 = R["H1"], R["S3"]
    th1, ts3 = T["H1"], T["S3"]
    geo = {g["group"]: g for g in R["geometry"]}
    tgeo = {g["group"]: g for g in T["geometry"]}
    n_dogs = h1["n"]
    summary = (f"Exploratory (DS05 already seen). Habitus against distance from the Beagle course, controlling pseudo-stage: "
               f"partial rho {f2(h1['estimate'])} (95% CI {f2(h1['ci_low'])} to {f2(h1['ci_high'])}), p {p_text(h1['p'])}, n {n_dogs} dogs; "
               f"it vanishes once haematocrit is also controlled (partial rho {f2(s3['estimate'])}). "
               f"The stage score is not validated: the spec curve does not keep the Beagles' time order (rho {f2(R['course_A_stage_vs_day'])}) "
               f"and the time-anchored course fails the illness-duration check. {len(R['tests'])} tests; "
               f"{sum(1 for t in R['tests'] if t['p'] is not None and t['p'] < 0.05)} with p < 0.05.")
    interp = {"sections": [
        {"heading": "Question", "paragraphs": [
            "Is part of the variation in admission severity of natural B. rossi infection the stage a dog has reached on a common course, "
            "and are the clinically worst dogs off that course rather than only later on it?",
            "The reference course comes from 5 experimentally infected Beagles (DS02, SRC-B) in the plane haematocrit by log reticulocytes. "
            "Severity is the habitus grade of DS05 (SRC-F, 147 B. rossi dogs; 4 bright to 0 collapsed). DS05 was examined before this plan, "
            "so every result here is exploratory."]},
        {"heading": "What was done", "paragraphs": [
            f"A principal curve (cubic in arc length) was fitted to the {R['course_A']['n_points']} pre-treatment Beagle samples, as spec.md fixed. "
            f"Each DS05 dog was projected onto it: pseudo-stage is the position along the curve (0 to 1) and distance is the gap to the curve "
            f"in units of the Beagles' own scatter ({f2(R['course_A']['spread_sd_units'])} SD units). "
            "The primary test is the partial Spearman correlation of habitus with distance, controlling pseudo-stage "
            "(10,000 Freedman-Lane permutations, 2,000 bootstrap resamples of dogs, seed 20261112).",
            f"Deviation D1: the spec fit did not converge ({R['course_A']['iterations']} iterations) and re-ordered the Beagle samples, so its "
            f"pseudo-stage barely follows the sampling day (rho {f2(R['course_A_stage_vs_day'])}). A time-anchored course (the curve parameter "
            f"kept at the sampling day) keeps the order better (rho {f2(T['course_A_stage_vs_day'])}). Its results are shown beside the spec "
            "results as a sensitivity; the spec results stay primary because the deviation was chosen after outcome numbers had been printed."]},
        {"heading": "Result", "paragraphs": [
            f"Primary (spec construction): partial rho {f2(h1['estimate'])} (95% CI {f2(h1['ci_low'])} to {f2(h1['ci_high'])}), "
            f"permutation p {p_text(h1['p'])}, BH q {p_text(h1['q'])}, n {n_dogs}. Dogs further from the course had a duller habitus. "
            f"Controlling haematocrit as well (S3) removes it: partial rho {f2(s3['estimate'])} (95% CI {f2(s3['ci_low'])} to {f2(s3['ci_high'])}). "
            f"Distance largely restates anaemia, which was already known to track habitus (rho {f2(R['axes_vs_blood']['habitus_vs_hct'])}).",
            f"Pseudo-stage with habitus (H2): rho {f2(R['H2']['estimate'])} (95% CI {f2(R['H2']['ci_low'])} to {f2(R['H2']['ci_high'])}). "
            f"Band-neutrophil plane (H3): partial rho {f2(R['H3']['estimate'])} (95% CI {f2(R['H3']['ci_low'])} to {f2(R['H3']['ci_high'])}), q {p_text(R['H3']['q'])}.",
            f"Geometry: {pct(geo['DS05']['share_beyond_end'])} of DS05 dogs project onto an end of the Beagle course and only "
            f"{pct(geo['DS05']['share_within_band'])} lie within 2 spread units of it. The pre-treatment Beagles span haematocrit "
            f"{f2(R['beagle_hct_range'][0])} to {f2(R['beagle_hct_range'][1])}; the median DS05 dog has {f2(geo['DS05']['median_hct'])}.",
            f"Time-anchored course (D1): {pct(tgeo['DS05']['share_past_late_end'])} of dogs lie past its late end; the illness-duration check fails "
            f"(rho {f2(T['validity']['estimate'])}, opposite to the prediction); habitus with distance given stage: partial rho {f2(th1['estimate'])} "
            f"(95% CI {f2(th1['ci_low'])} to {f2(th1['ci_high'])}), {f2(ts3['estimate'])} with haematocrit also controlled.",
            "Leaving one Beagle out changes the curve a lot: under the spec construction the rank agreement of pseudo-stage with the full fit ranges "
            f"from {f2(min(l['spearman_stage_vs_full'] for l in R['loo']))} to {f2(max(l['spearman_stage_vs_full'] for l in R['loo']))}."]},
        {"heading": "What this does not show", "paragraphs": [
            "It does not show that severe dogs are \"late\" or \"off course\": the stage score is not validated under either construction, "
            "and most natural dogs are more anaemic than any Beagle before treatment, so the 5-dog course cannot place them.",
            "Distance from the course is mostly a restatement of anaemia. Off-course dogs are not a subtype. No prediction is made.",
            "Single species and country; prior treatment unknown; the Beagle course follows intravenous inoculation. DS05 has no hard outcome; habitus is a proxy."]},
    ]}
    tests = tests_rows(R)
    ttests = tests_rows(T)
    results = [
        {"kind": "primary_result", "title": "Primary analysis: habitus against distance from the Beagle course (DS05)", "sort_order": 1, "payload": {
            "label": "Habitus grade with distance from the Beagle course, controlling pseudo-stage (plane haematocrit by log ARC)",
            "statistic": "partial Spearman rho", "estimate": h1["estimate"], "ci_low": h1["ci_low"], "ci_high": h1["ci_high"],
            "p": h1["p"], "q": h1["q"], "n": n_dogs, "n_unit": "dogs", "independent_sources": 2,
            "sources": ["SRC-B (5 Beagles, reference course)", "SRC-F (DS05)"],
            "expected_direction": "negative (higher habitus is brighter)",
            "status": "exploratory: DS05 was already seen; stage score not validated",
            "headline": f"partial rho {f2(h1['estimate'])} (95% CI {f2(h1['ci_low'])} to {f2(h1['ci_high'])}), n {n_dogs}; "
                        f"{f2(s3['estimate'])} once haematocrit is also controlled",
            "secondary": [
                {"label": "Same, also controlling haematocrit (S3)", "estimate": s3["estimate"], "ci_low": s3["ci_low"], "ci_high": s3["ci_high"], "p": s3["p"], "n": s3["n"]},
                {"label": "Time-anchored course (deviation D1)", "estimate": th1["estimate"], "ci_low": th1["ci_low"], "ci_high": th1["ci_high"], "p": th1["p"], "n": th1["n"]},
                {"label": "Time-anchored course, also controlling haematocrit", "estimate": ts3["estimate"], "ci_low": ts3["ci_low"], "ci_high": ts3["ci_high"], "p": ts3["p"], "n": ts3["n"]},
            ]}},
        {"kind": "checks", "title": "Construction and validity checks", "sort_order": 2, "payload": {
            "sets": [checks(R, "Spec construction (primary)"), checks(T, "Time-anchored course (deviation D1)")]}},
        {"kind": "map_plane_a", "title": "Disease space: haematocrit by reticulocytes", "sort_order": 3,
         "payload": {**map_payload("A", ["DS05"], True),
                     "footnote": f"DS02 (5 Beagles, SRC-B) and DS05 (n {n_dogs}, SRC-F). One species (B. rossi), one country. Exploratory: DS05 already seen. "
                                 "Colour of DS05 dogs: habitus grade."}},
        {"kind": "map_plane_b", "title": "Disease space: haematocrit by band neutrophils", "sort_order": 4,
         "payload": {**map_payload("B", ["DS05"], True),
                     "footnote": "DS02 and DS05 only. Exploratory: DS05 already seen."}},
        {"kind": "tests_table", "title": "All tests", "sort_order": 5, "payload": {
            "family_size": 3, "correction": "Benjamini-Hochberg over H1 to H3", "sets": [
                {"construction": "Spec construction (primary)", "rows": tests},
                {"construction": "Time-anchored course (deviation D1)", "rows": ttests}]}},
        {"kind": "stability_loo", "title": "Leave one Beagle out", "sort_order": 6, "payload": {
            "sets": [{"construction": "Spec construction (primary)", "rows": R["loo"]},
                     {"construction": "Time-anchored course (deviation D1)", "rows": T["loo"]}]}},
        {"kind": "habitus_table", "title": "Position on the map by habitus grade (DS05)", "sort_order": 7, "payload": {
            "rows": R["habitus_table"]}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp},
    ]
    return {
        "experiment": {
            "code": "SV-01-01-habitus-distance",
            "name": "Habitus grade against distance from the Beagle reference course in natural B. rossi infection (DS05)",
            "description": "Is admission severity in natural B. rossi infection partly the stage a dog has reached on a common course, and are the worst dogs off that course? "
                           "Habitus grade in DS05 is tested against distance from a course built from 5 experimentally infected Beagles, controlling position along it.",
            "method": "disease_space_map",
            "dataset": None,
            "parameters": {"package": "SV-01", "role": "descriptive", "datasets": ["DS02", "DS05"],
                           "independent_sources": ["SRC-B", "SRC-F"], "spec_sha256": R["spec_sha256"], "seed": R["seed"],
                           "n_permutations": 10000, "n_bootstrap": 2000, "inputs_sha256": R["inputs_sha256"],
                           "deviations": ["D1 time-anchored course reported as sensitivity", "construction check added after the first run"],
                           "versions": R["versions"]},
            "script": "/experiments/SV-01/scripts/analyse.py",
            "script_version": SCRIPT_VERSION,
            "run_utc": RUN_UTC,
            "n_subjects": n_dogs + 5, "n_variables": 5, "n_tests": len(tests),
            "summary": summary,
        },
        "associations": [], "cluster_assignments": [], "results": results,
    }


def exp2():
    geo = {g["group"]: g for g in R["geometry"]}
    tgeo = {g["group"]: g for g in T["geometry"]}
    c1, c2, d5 = geo["DS03_c1"], geo["DS03_c2"], geo["DS05"]
    n_nat = c1["n"] + c2["n"]
    keys = ["DS03_c1", "DS03_c2", "DS03_healthy", "DS03_imha"]
    rows = []
    for construction, src in (("Spec construction (primary)", geo), ("Time-anchored course (deviation D1)", tgeo)):
        for k in ["DS03_c1", "DS03_c2", "DS05", "DS03_healthy", "DS03_imha"]:
            g = src[k]
            rows.append({"construction": construction, "group": k, "label": GROUP_LABELS[k], **g})
    summary = (f"Geometry only (DS03 has no outcome). Within 2 spread units of the Beagle course: cohort 1 {pct(c1['share_within_band'])} "
               f"(95% CI {pct(c1['within_ci_low'])} to {pct(c1['within_ci_high'])}, n {c1['n']}), cohort 2 {pct(c2['share_within_band'])} "
               f"(n {c2['n']}), against DS05 {pct(d5['share_within_band'])}; projected onto an end of the course: {pct(c1['share_beyond_end'])}, "
               f"{pct(c2['share_beyond_end'])} and {pct(d5['share_beyond_end'])}. No tests.")
    interp = {"sections": [
        {"heading": "Question", "paragraphs": [
            "Does the geometry seen in DS05 (where natural dogs sit relative to the Beagle course) repeat in the two natural-infection cohorts of DS03, "
            "a referral hospital series with no severity score?"]},
        {"heading": "What was done", "paragraphs": [
            "The DS03 dogs were projected onto the same Beagle course as SV-01-01 (spec construction, with the time-anchored course as a sensitivity). "
            "For each cohort: share within 2 spread units (Wilson 95% CI), share projected onto an end of the course, and the pseudo-stage distribution. "
            "Healthy controls and IMHA dogs of DS03 are projected as reference groups. No test between DS03 and DS05: different sources and settings "
            "(clinic against referral hospital)."]},
        {"heading": "Result", "paragraphs": [
            f"Cohort 1 (n {c1['n']}): {pct(c1['share_within_band'])} within the band (95% CI {pct(c1['within_ci_low'])} to {pct(c1['within_ci_high'])}), "
            f"{pct(c1['share_beyond_end'])} on an end (95% CI {pct(c1['beyond_ci_low'])} to {pct(c1['beyond_ci_high'])}), median haematocrit {f2(c1['median_hct'])}.",
            f"Cohort 2 (n {c2['n']}): {pct(c2['share_within_band'])} within (95% CI {pct(c2['within_ci_low'])} to {pct(c2['within_ci_high'])}), "
            f"{pct(c2['share_beyond_end'])} on an end, median haematocrit {f2(c2['median_hct'])}.",
            f"DS05 for comparison (n {d5['n']}): {pct(d5['share_within_band'])} within, {pct(d5['share_beyond_end'])} on an end. "
            f"Healthy controls: {pct(geo['DS03_healthy']['share_within_band'])} within, none on an end.",
            f"Time-anchored course: within the band {pct(tgeo['DS03_c1']['share_within_band'])} (cohort 1), {pct(tgeo['DS03_c2']['share_within_band'])} (cohort 2), "
            f"{pct(tgeo['DS05']['share_within_band'])} (DS05); past the late end {pct(tgeo['DS03_c1']['share_past_late_end'])}, "
            f"{pct(tgeo['DS03_c2']['share_past_late_end'])} and {pct(tgeo['DS05']['share_past_late_end'])}.",
            "The geometry repeats: in both settings most naturally infected dogs lie outside the range that the 5 Beagles covered before treatment, "
            "mainly because they are more anaemic."]},
        {"heading": "What this does not show", "paragraphs": [
            "Nothing about severity: DS03 has no outcome. The pseudo-stage is not validated (SV-01-01).",
            "DS03 \"Day 1\" in the experimental file is day 1 after inoculation of the same 5 Beagles; those records were not used. "
            "Overlap of DS03 dogs with S-CB050 or S-CB517 is possible and unverified. One species, one country; prior treatment unknown."]},
    ]}
    results = [
        {"kind": "primary_result", "title": "Replication of the geometry in DS03", "sort_order": 1, "payload": {
            "label": "Share of DS03 cohort 1 dogs within 2 spread units of the Beagle course (plane haematocrit by log ARC)",
            "statistic": "proportion", "estimate": c1["share_within_band"], "ci_low": c1["within_ci_low"], "ci_high": c1["within_ci_high"],
            "p": None, "q": None, "n": c1["n"], "n_unit": "dogs", "independent_sources": 2,
            "sources": ["SRC-B (5 Beagles, reference course)", "SRC-E (DS03)"],
            "status": "descriptive geometry; no outcome in DS03",
            "headline": f"{pct(c1['share_within_band'])} within the band in cohort 1 (n {c1['n']}), {pct(c2['share_within_band'])} in cohort 2 (n {c2['n']}); "
                        f"DS05 {pct(d5['share_within_band'])}",
            "secondary": [
                {"label": "Cohort 2 within the band", "estimate": c2["share_within_band"], "ci_low": c2["within_ci_low"], "ci_high": c2["within_ci_high"], "p": None, "n": c2["n"]},
                {"label": "Cohort 1 on an end of the course", "estimate": c1["share_beyond_end"], "ci_low": c1["beyond_ci_low"], "ci_high": c1["beyond_ci_high"], "p": None, "n": c1["n"]},
                {"label": "Cohort 2 on an end of the course", "estimate": c2["share_beyond_end"], "ci_low": c2["beyond_ci_low"], "ci_high": c2["beyond_ci_high"], "p": None, "n": c2["n"]},
                {"label": "DS05 within the band (comparison)", "estimate": d5["share_within_band"], "ci_low": d5["within_ci_low"], "ci_high": d5["within_ci_high"], "p": None, "n": d5["n"]},
            ]}},
        {"kind": "map_plane_a", "title": "Disease space: haematocrit by reticulocytes (DS03)", "sort_order": 3,
         "payload": {**map_payload("A", keys, False),
                     "footnote": f"DS02 (5 Beagles, SRC-B) and DS03 (SRC-E): natural cohorts 1 and 2 (n {n_nat}), healthy controls and IMHA dogs as reference. "
                                 "No outcome in DS03. One species, one country."}},
        {"kind": "geometry_table", "title": "Geometry by cohort", "sort_order": 4, "payload": {"rows": rows}},
        {"kind": "stage_histogram", "title": "Pseudo-stage distribution (spec construction)", "sort_order": 5, "payload": {
            "bins": [round(i / 10, 1) for i in range(11)],
            "groups": [{"key": k, "label": GROUP_LABELS[k], "n": geo[k]["n"], "counts": geo[k]["stage_histogram"]}
                       for k in ["DS03_c1", "DS03_c2", "DS05"]]}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp},
    ]
    return {
        "experiment": {
            "code": "SV-01-02-ds03-geometry",
            "name": "Where natural B. rossi dogs lie relative to the Beagle reference course: replication in the two DS03 cohorts",
            "description": "Does the disease-space geometry seen in DS05 repeat in the DS03 referral-hospital cohorts? "
                           "The share of dogs within the Beagle band and the pseudo-stage distribution are reported per cohort; DS03 has no outcome.",
            "method": "disease_space_map",
            "dataset": None,
            "parameters": {"package": "SV-01", "role": "replication", "datasets": ["DS02", "DS03"],
                           "independent_sources": ["SRC-B", "SRC-E"], "spec_sha256": R["spec_sha256"], "seed": R["seed"],
                           "n_bootstrap": 2000, "inputs_sha256": R["inputs_sha256"], "versions": R["versions"]},
            "script": "/experiments/SV-01/scripts/analyse.py",
            "script_version": SCRIPT_VERSION,
            "run_utc": RUN_UTC,
            "n_subjects": 138, "n_variables": 2, "n_tests": 0,
            "summary": summary,
        },
        "associations": [], "cluster_assignments": [], "results": results,
    }


def main():
    figure("A", ["DS05", "DS03_c1", "DS03_c2", "DS03_healthy"], OUT / "figure_map_A.svg")
    figure("B", ["DS05"], OUT / "figure_map_B.svg")
    db = OUT / "db"
    db.mkdir(exist_ok=True)
    for load in (exp1(), exp2()):
        text = json.dumps(load, indent=1, allow_nan=False, ensure_ascii=False)
        (db / f"{load['experiment']['code']}.json").write_text(text, encoding="utf-8")
        print(load["experiment"]["code"], len(text.encode("utf-8")), "bytes")
        print("  ", load["experiment"]["summary"])


if __name__ == "__main__":
    main()
