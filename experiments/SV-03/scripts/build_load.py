"""SV-03: build the two load files for the console loader (way B) from out/results.json and out/*.csv.

Run from /experiments/SV-03/:  env/py/Scripts/python.exe -I scripts/build_load.py
Every number in the text comes from the files in out/.
"""
import csv, hashlib, json, os, time

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
OUT = os.path.join(PKG, "out")
DB = os.path.join(OUT, "db")
os.makedirs(DB, exist_ok=True)

R = json.load(open(os.path.join(OUT, "results.json"), encoding="utf-8"))
with open(os.path.join(HERE, "analyse.py"), "rb") as f:
    SCRIPT_VERSION = hashlib.sha256(f.read()).hexdigest()[:12]
RUN_UTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
META = R["meta"]
SPEC = META["inputs"]["spec.md"]


def rows(name):
    with open(os.path.join(OUT, name), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def typed(r):
    out = {}
    for k, v in r.items():
        if v in ("True", "False"):
            out[k] = v == "True"
        elif v == "":
            out[k] = None
        else:
            try:
                out[k] = int(v)
            except ValueError:
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
    return out


S = R["summary"]
MAIN, D1, D1S1, D1S4 = S["main"], S["D1_collapsed"], S["D1_collapsed_S1"], S["D1_collapsed_S4"]
CIRC = R["circularity"]
SEL = R["selective_reporting"]
SU = META["species_units"]
EUTH = CIRC["euthanasia_in_mortality"]
SOURCES = [f"{k}: {v} units" for k, v in SU.items() if v]

matrix = [typed(r) for r in rows("evidence_matrix.csv")]
matrix_shown = [r for r in matrix if r["tested_units"] >= 2 or r["X"]]
collapsed = [typed(r) for r in rows("evidence_matrix_collapsed.csv")]
conf = [typed(r) for r in rows("conflicts.csv")]
conf_units = [typed(r) for r in rows("conflict_units.csv")]
sel_rows = [typed(r) for r in rows("selective_reporting.csv")]
defmap = [typed(r) for r in rows("definition_map.csv")]
comps = [typed(r) for r in rows("definition_components.csv")]
ocs = [typed(r) for r in rows("definition_outcome_classes.csv")]
circ_rows = [typed(r) for r in rows("circularity.csv")]
near = [typed(r) for r in rows("pooling_near_misses.csv")]
pooled = [typed(r) for r in rows("pooled.csv")]

cons_collapsed = [c for c in collapsed if c["consistent"]]
cons_c3_nc = [c for c in cons_collapsed if (c["H"] + c["L"]) >= 3 and not c["circular"]]
cons_c3_nc_s1 = [c for c in cons_c3_nc if c["S1_consistent"] and (c["S1_H"] + c["S1_L"]) >= 3]
opp_main = [r for r in matrix if (r["H"] and r["L"]) or r["X"]]
opp_between = [r for r in matrix if r["H"] and r["L"]]
conf_verdicts = {}
for c in conf:
    conf_verdicts.setdefault(c["verdict"], []).append(c["conflict"])


def name_list(cs):
    return ", ".join(f"{c['marker']} ({c['consistent_direction']} in severe, {c['species_group']}, "
                     f"{c['H'] + c['L']} of {c['tested_units']} tested units)" for c in cs) or "none"


# ----------------------------------------------------------------- experiment 1
summary1 = (f"No species x outcome-class cell has 3 or more tested independent units (largest: {max(r['tested_units'] for r in matrix)}),"
            f" so nothing was pooled (0 pooled estimates; {MAIN['consistent']} cells consistent in 2 units). With outcome classes "
            f"collapsed (post hoc), {len(cons_c3_nc)} non-circular cells are consistent in 3 or more units, all B. rossi; "
            f"{len(cons_c3_nc_s1)} survive counting Onderstepoort once. 0 tests.")

tiles = {
    "rows": META["rows"], "articles": META["articles"], "units": META["units"], "markers": META["markers"],
    "cells": MAIN["cells"], "cells_ge2_tested": MAIN["cells_ge2_tested"], "cells_ge3_tested": MAIN["cells_ge3_tested"],
    "largest_cell": max(r["tested_units"] for r in matrix), "pooled": len(pooled), "consistent": MAIN["consistent"],
    "collapsed_cells_ge3": D1["cells_ge3_tested"], "collapsed_consistent_ge3_noncircular": len(cons_c3_nc),
    "collapsed_consistent_ge3_noncircular_s1": len(cons_c3_nc_s1),
    "opposite_cells": len(opp_between), "within_unit_conflicts": sum(1 for r in matrix if r["X"]),
    "species_units": SU, "share_not_significant": SEL["overall_share_not_significant"],
}

sens_rows = []
for key, label in [("main", "Primary: marker x outcome class x species"),
                   ("S1_onderstepoort_collapse", "S1: Onderstepoort B. rossi units counted once"),
                   ("S2_no_judgement_calls", "S2: judgement-call definitions and machine translations removed"),
                   ("S3_strict_unit_rule", "S3: strict unit rule"),
                   ("S4_no_circular_units", "S4: units whose marker is in the definition removed"),
                   ("D1_collapsed", "D1 (post hoc): outcome classes collapsed within species"),
                   ("D1_collapsed_S1", "D1 + S1"), ("D1_collapsed_S4", "D1 + S4")]:
    v = S[key]
    sens_rows.append({"set": label, **v})

interp1 = {"sections": [
    {"heading": "Question", "paragraphs": [
        "Which markers and host or parasite factors are linked to severity consistently, once severity definitions are aligned and "
        "each cohort is counted once? Input: the SV-G2 extraction of published group results "
        f"({META['rows']} rows, {META['articles']} articles, {META['units']} independent units, {META['markers']} canonical markers)."]},
    {"heading": "What was done", "paragraphs": [
        "Each row was called significantly higher (H), lower (L), not significant (N), unclear or descriptive, relative to the worse "
        "outcome. Rows were merged into one call per independent unit (cohort in /core/cohorts.json, else the article) for each cell "
        "of marker x outcome class x species group. A cell is consistent when at least 2 tested units agree in one significant "
        "direction, at least two thirds of tested units agree, and no unit points the other way. Multivariable rows are kept apart.",
        "Pooling was allowed only for 3 or more units with one species, one outcome class and a usable summary (Hedges g, Fisher z "
        "or log odds ratio; random effects with REML and the Hartung-Knapp interval).",
        "Deviation D1, added after the primary result: the same matrix with all outcome classes of a species merged, as an "
        "exploratory direction table only (not pooled)."]},
    {"heading": "Result", "paragraphs": [
        f"Primary (negative): of {MAIN['cells']} cells, {MAIN['cells_ge2_tested']} have 2 tested units and none has 3 "
        f"(largest {tiles['largest_cell']}). Nothing could be pooled: {len(near)} cells had 2 units with usable summaries and none "
        f"had 3. {MAIN['consistent']} cells are consistent in 2 units: "
        + "; ".join(f"{c['marker']} {c['consistent_direction']} ({c['outcome_class']}, {c['species_group']})"
                    for c in R["consistent_cells"]) + ".",
        f"D1 (exploratory): with outcome classes merged, {D1['cells_ge3_tested']} cells have 3 or more tested units. Consistent and "
        f"not circular in 3 or more units: {name_list(cons_c3_nc)}. Counting the Onderstepoort B. rossi units once (S1), "
        f"{len(cons_c3_nc_s1)} of these keep 3 agreeing units. Consistent but circular (the marker is part of the definition in "
        f"at least one unit): {', '.join(c['marker'] + ' (' + c['species_group'] + ')' for c in cons_collapsed if c['circular'])}.",
        f"Named conflicts: {'; '.join(f'{k}: ' + ', '.join(v) for k, v in conf_verdicts.items())}. No two independent units in "
        "the extraction report one of these markers in opposite significant directions; the conflicts in the syntheses rest on "
        "comparisons with healthy controls, on articles that were not extracted (CB037 for IL-8 is abstract only), or on a "
        "significant result in one unit against a non-significant one in another.",
        f"Opposite significant directions between units occur in {len(opp_between)} primary cells: "
        + "; ".join(f"{r['marker']} ({r['outcome_class']}, {r['species_group']}: {r['unit_calls']})" for r in opp_between)
        + ". Haematocrit against death in B. rossi is a definition effect: CB040's significant row is the small "
          "haemoconcentration category, CH03's is lower haematocrit in non-survivors.",
        f"Selective reporting check: {SEL['overall_share_not_significant']:.2f} of tested rows are not significant (median by "
        f"article {SEL['median_share_not_significant']:.2f}); {SEL['articles_with_no_not_significant_row']} of "
        f"{SEL['articles_with_tested_rows']} articles report no non-significant row."]},
    {"heading": "What this does not show", "paragraphs": [
        "Direction counts are not effect sizes, and an absent cell is not evidence of no effect: most markers were tested in one "
        "unit for one definition. Species is aliased with source, country, assay and definition; species groups are never "
        f"compared. Death includes euthanasia for poor prognosis in {EUTH.get('yes', 0)} of {sum(EUTH.values())} mortality "
        f"definitions ({EUTH.get('not stated', 0)} do not say). "
        "The D1 table mixes definitions and is exploratory; it was added after the primary result was known. "
        "Categories and calls come from language-model extraction with a 16-article owner check, not a full human review."]},
]}

primary1 = {"tiles": tiles, "consistent_cells": R["consistent_cells"],
            "collapsed_consistent": cons_collapsed, "cross_species": R["cross_species"],
            "note": "Published group results (SV-G2) · independent units, not articles · one species per source, species not compared"}

exp1 = {
    "experiment": {
        "code": "SV-03-01-evidence-matrix",
        "name": "Marker-evidence matrix: which severity markers hold up across independent canine cohorts (literature, SV-G2)",
        "description": ("Which markers and host or parasite factors are linked to severity consistently once definitions are "
                        "aligned and each cohort is counted once? Hypothesis: some markers agree in direction in 3 or more "
                        "independent units of one species and one outcome class, enough to pool."),
        "method": "evidence_matrix", "dataset": None,
        "parameters": {"package": "SV-03", "role": "descriptive", "datasets": [],
                       "literature_input": "/experiments/SV-G2/associations_v2.csv",
                       "independent_sources": sorted({d["independent_unit"] for d in defmap}),
                       "independent_units": META["units"], "species_units": SU, "spec_sha256": SPEC, "seed": None,
                       "pooling_rule": ">= 3 independent units, one species, one outcome class, one usable summary",
                       "deviations": ["D1 outcome classes collapsed (post hoc, exploratory)",
                                      "abstract-only sensitivity set empty (SV-G2 extracted none)"],
                       "inputs_sha256": META["inputs"], "versions": META["versions"]},
        "script": "/experiments/SV-03/scripts/analyse.py", "script_version": SCRIPT_VERSION, "run_utc": RUN_UTC,
        "n_subjects": META["dogs_max_n_per_unit"], "n_variables": META["markers"], "n_tests": len(pooled),
        "summary": summary1,
    },
    "associations": [], "cluster_assignments": [],
    "results": [
        {"kind": "matrix_summary", "title": "Primary analysis: cells, pooling and consistency", "sort_order": 1, "payload": primary1},
        {"kind": "evidence_matrix", "title": "Evidence matrix: cells with 2 or more tested units, or a conflict inside a unit",
         "sort_order": 2, "payload": {"rows": matrix_shown, "all_cells": len(matrix)}},
        {"kind": "evidence_matrix_collapsed", "title": "D1 (post hoc): outcome classes merged within species", "sort_order": 3,
         "payload": {"rows": collapsed}},
        {"kind": "pooling", "title": "Pooling: estimates, near misses", "sort_order": 4,
         "payload": {"pooled": pooled, "near_misses": near,
                     "poolable_if_collapsed": R["collapsed_poolable_if_allowed"],
                     "usable_rows": META["usable_rows_for_pooling"]}},
        {"kind": "named_conflicts", "title": "Conflicts named in the syntheses", "sort_order": 5,
         "payload": {"rows": conf, "units": conf_units}},
        {"kind": "sensitivity", "title": "Sensitivity sets", "sort_order": 6, "payload": {"rows": sens_rows}},
        {"kind": "selective_reporting", "title": "Selective reporting: share of non-significant rows by article", "sort_order": 7,
         "payload": {"summary": SEL, "rows": sel_rows}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp1},
    ],
}

# ----------------------------------------------------------------- experiment 2
top_comps = sorted(comps, key=lambda c: -c["units_all"])[:6]
summary2 = (f"{CIRC['definitions']} severity definitions in {CIRC['definition_units']} independent units; the commonest "
            f"component is {top_comps[0]['component']} ({top_comps[0]['units_all']} units). A tested marker is part of its own "
            f"definition in {CIRC['tested_rows_marker_in_definition']} of {CIRC['tested_rows']} tested rows "
            f"({CIRC['share_rows']:.1%}) and in {CIRC['units_with_marker_in_definition']} of {CIRC['units_tested']} units; "
            f"those rows are significant {CIRC['share_significant_circular']:.0%} of the time against "
            f"{CIRC['share_significant_noncircular']:.0%} for other rows. 0 tests.")
interp2 = {"sections": [
    {"heading": "Question", "paragraphs": [
        "How do canine babesiosis studies define severe disease, how many independent units use each component, and how often is "
        "a marker tested against a definition that contains it?"]},
    {"heading": "What was done", "paragraphs": [
        "Every severity definition extracted by SV-G2 was listed with species, setting, outcome class and components. Components "
        "were counted by independent unit and species group. A tested row was flagged as circular when its marker belongs to a "
        "component of its definition (a fixed marker-to-component map in the spec), when the outcome class is defined by the "
        "marker (anaemia grade, parasitaemia level), or when the marker is named in the definition text."]},
    {"heading": "Result", "paragraphs": [
        f"{CIRC['definitions']} definitions in {CIRC['definition_units']} units; median {CIRC['component_count_median']:.0f} "
        "component per definition. Components by units: "
        + ", ".join(f"{c['component']} {c['units_all']}" for c in top_comps) + ".",
        "Outcome classes by units: " + ", ".join(f"{c['outcome_class']} {c['units_all']}" for c in ocs) + ".",
        f"Circularity: {CIRC['tested_rows_marker_in_definition']} of {CIRC['tested_rows']} tested rows ({CIRC['share_rows']:.1%}), "
        f"in {CIRC['units_with_marker_in_definition']} of {CIRC['units_tested']} units with tests. Circular rows are significant "
        f"{CIRC['share_significant_circular']:.0%} of the time, other rows {CIRC['share_significant_noncircular']:.0%}.",
        "Euthanasia in mortality definitions: " + ", ".join(f"{k} {v}" for k, v in CIRC["euthanasia_in_mortality"].items()) + "."]},
    {"heading": "What this does not show", "paragraphs": [
        "Components are the extractors' coding of the authors' text; the marker-to-component map is a fixed rule and misses "
        "markers that enter a definition indirectly (for example through a clinical score). Species is aliased with source and "
        "setting, so component use by species is not a species difference."]},
]}
exp2 = {
    "experiment": {
        "code": "SV-03-02-definition-map",
        "name": "Severity definition map: definition components by independent unit, and markers tested against their own definition",
        "description": ("How do canine babesiosis studies define severe disease, and how often is a marker tested against a "
                        "definition that contains it? Descriptive; no hypothesis."),
        "method": "evidence_matrix", "dataset": None,
        "parameters": {"package": "SV-03", "role": "descriptive", "datasets": [],
                       "literature_input": "/experiments/SV-G2/definitions_v2.csv",
                       "independent_sources": sorted({d["independent_unit"] for d in defmap}),
                       "independent_units": CIRC["definition_units"], "spec_sha256": SPEC, "seed": None,
                       "inputs_sha256": META["inputs"], "versions": META["versions"]},
        "script": "/experiments/SV-03/scripts/analyse.py", "script_version": SCRIPT_VERSION, "run_utc": RUN_UTC,
        "n_subjects": META["dogs_max_n_per_unit"], "n_variables": len(comps), "n_tests": 0, "summary": summary2,
    },
    "associations": [], "cluster_assignments": [],
    "results": [
        {"kind": "definition_summary", "title": "Primary: definition components and circularity", "sort_order": 1,
         "payload": {"circularity": CIRC, "species_units": SU}},
        {"kind": "definition_components", "title": "Definition components by independent units and species", "sort_order": 2,
         "payload": {"rows": comps}},
        {"kind": "definition_outcome_classes", "title": "Outcome classes by independent units and species", "sort_order": 3,
         "payload": {"rows": ocs}},
        {"kind": "circularity", "title": "Markers tested against a definition that contains them", "sort_order": 4,
         "payload": {"rows": circ_rows}},
        {"kind": "definition_map", "title": "All severity definitions", "sort_order": 5, "payload": {"rows": defmap}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp2},
    ],
}

for e in (exp1, exp2):
    p = os.path.join(DB, e["experiment"]["code"] + ".json")
    txt = json.dumps(e, ensure_ascii=False, allow_nan=False, indent=1)
    with open(p, "w", encoding="utf-8") as f:
        f.write(txt)
    print(p, len(txt.encode("utf-8")), "bytes")
    print("  ", e["experiment"]["summary"])
