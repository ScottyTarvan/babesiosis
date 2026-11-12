"""SV-02a: build the database load file (way B) from a/out/results.json.

Run after analyse.py, from /experiments/SV-02/a:  env/py/Scripts/python.exe -I scripts/build_load.py
Writes /experiments/SV-02/out/db/SV-02-01-load-by-outcome.json (the loader reads <package>/out/db/).
"""
import hashlib
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)
PKG = os.path.dirname(PART)
SCRIPT = os.path.join(HERE, "analyse.py")
CODE = "SV-02-01-load-by-outcome"

R = json.load(open(os.path.join(PART, "out", "results.json"), encoding="utf-8"))
C = R["counts"]
SPEC_SHA = R["inputs"]["experiments/SV-02/a/spec.md"]
RUN_UTC = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
SCRIPT_VERSION = hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest()[:12]


def f2(v, d=2):
    return "–" if v is None else f"{v:.{d}f}"


def ci(t):
    return f"{f2(t['ci_lo'])} to {f2(t['ci_hi'])}"


table = R["table"]
by_unit = {t["unit"]: t for t in table}
mort = by_unit.get("CH21")
hes = by_unit.get("CH12")
ab = R["antibody_vs_load"]
cb220 = next((s for s in R["sensitivity"] if s["unit"] == "CB220"), None)
species_groups = sorted({t["species_group"] for t in table})
sources = sorted({t["unit"] for t in table})
not_sig = sum(1 for t in table if t["significant"] in ("no",))
not_tested = sum(1 for t in table if t["significant"] == "not_tested")
low_from_rows = [x for x in R["low_list"] if x["source_level"] == "SV-G2 row"]
low_from_notes = [x for x in R["low_list"] if x["source_level"] != "SV-G2 row"]

dmg = R["damage"]
dmg_units = {}
for d in dmg:
    u = dmg_units.setdefault(d["unit"], {"unit": d["unit"], "article": d["article"], "species_group": d["species_group"],
                                         "definition": d["definition"], "rows": 0, "worse_with_load": 0, "better_with_load": 0,
                                         "no_difference": 0, "doi": d["doi"]})
    u["rows"] += 1
WORSE_IF_HIGHER = {"AST", "ALT", "ALP", "GGT", "Urea", "Creatinine", "Bilirubin", "Haemoglobinuria", "Icterus", "Body temperature",
                   "C-reactive protein", "KC-like (CXCL1)", "IL-10", "Monocyte count", "Eosinophil count", "Potassium",
                   "Phosphate", "Magnesium", "Glucose", "Other clinical signs (composite)"}
for d in dmg:
    u = dmg_units[d["unit"]]
    dirn = d["direction"]
    if dirn == "no_difference":
        u["no_difference"] += 1
        continue
    up = dirn in ("higher_in_severe", "more_frequent_in_severe", "positive_association")
    worse = up == (d["marker"] in WORSE_IF_HIGHER)
    u["worse_with_load" if worse else "better_with_load"] += 1
cb241 = dmg_units.get("CB241")
hct241 = next((d for d in dmg if d["unit"] == "CB241" and d["marker"] == "Haematocrit/PCV"), None)

summary = (
    f"No pooled estimate: no species and outcome class has 3 or more independent units with load against outcome "
    f"(largest cell {C['max_units_in_cell']} units; {C['load_units_primary']} units in {C['cells']} cells, "
    f"{len(species_groups)} species groups). Only one unit gives a load difference by outcome: B. canis nonsurvivors vs survivors "
    f"(CB516, 8 vs 7 dogs, death includes euthanasia), Hedges g of log load {f2(mort['effect'])} ({ci(mort)}); "
    f"{C['significant_higher_in_severe']} of {C['load_units_primary']} units report significantly higher load with severity "
    f"(B. canis HES score, rho {f2(hes['effect'])}). No hypothesis tests (0 of 0)."
)

interpretation = {"sections": [
    {"heading": "Question", "paragraphs": [
        "Do dogs with severe babesiosis carry more parasites than dogs with mild disease, inside one Babesia species and one outcome "
        "class? SV-02 asks whether dogs differ more in damage per parasite (tolerance) than in load (resistance); part a looks at "
        "what the published load-by-outcome contrasts can say."]},
    {"heading": "What was done", "paragraphs": [
        f"From the SV-G2 extraction ({C['units_with_severity_rows']} independent units with severity rows), every parasite load row was "
        f"taken: {C['load_rows']} rows. {C['load_rows_primary']} rows in {C['load_units_primary']} units compare load with a severity or "
        "outcome definition. The experimental dose contrast (CB105, CH09) and the rows where load defines the groups were set aside.",
        "The spec allowed a random-effects pool (REML, Hartung-Knapp interval) of the standardised difference in log load only where 3 "
        "or more independent units share one species, one outcome class and one definition. Otherwise each unit is shown in a "
        "direction table with its load method and sample timing. Effects were computed where the paper prints group n and dispersion.",
        f"A separate list collects results of the form 'severe disease at low load' or 'protection at unchanged load': "
        f"{len(low_from_rows)} from the SV-G2 rows and {len(low_from_notes)} from a keyword screen of the appraisal notes "
        f"({C['note_hits']} notes matched; {C['note_hits_included']} kept after reading)."]},
    {"heading": "Result", "paragraphs": [
        f"No cell reached the pooling rule. The largest cell has {C['max_units_in_cell']} units (B. canis severity grade, two different "
        "definitions). The primary analysis therefore has no pooled effect: this is a lack of data, not evidence for either hypothesis.",
        f"B. canis mortality (CB516, 8 nonsurvivors vs 7 survivors, death includes euthanasia): median load 1.25% vs 1.2%, Hedges g of "
        f"log load {f2(mort['effect'])} ({ci(mort)}). With these group sizes only a difference of about {f2(mort['detectable'], 1)} SD "
        "could be detected, so the null is weak.",
        f"B. canis haematological score (CB141, ddPCR load): rho {f2(hes['effect'])} ({ci(hes)}, n {int(hes['n_total'])}). In the same "
        f"cohort antibody level correlates more strongly, and in the opposite direction: rho {f2(ab['antibody_rho'])} "
        f"({f2(ab['antibody_ci'][0])} to {f2(ab['antibody_ci'][1])}, n {ab['antibody_n']}). The two intervals do not overlap, but the "
        "samples differ and the score is built from blood counts, so this is not a formal comparison.",
        f"Large Babesia, jaundiced (late) vs anaemic (early) form (CB220): load slightly lower in the late form; with an assumed equal "
        f"split of 20 dogs, g {f2(cb220['effect'])} ({f2(cb220['ci_lo'])} to {f2(cb220['ci_hi'])}). The more severe form is also the later "
        "one, so stage and severity are mixed here (the question of SV-01). B. gibsoni (CB045): load unrelated to pancreatic injury "
        f"(r {f2(by_unit['CB045']['effect'])}, n 20). Mixed B. gibsoni and B. vogeli (CB038): smear positivity 7 of 17 complicated vs 6 "
        f"of 17 uncomplicated, odds ratio {f2(by_unit['CB038']['effect'])} ({ci(by_unit['CB038'])}). B. canis (CB537): non-overlapping "
        "load ranges (23-68% in severe forms vs 2.5-7% in mild), with no group n or test.",
        f"Where groups were made by load (the inverse question), damage rose with load: in CB241 (B. canis, 4 vs 4 dogs) "
        f"{cb241['worse_with_load']} of {cb241['rows']} markers were worse in the high-load group "
        f"(haematocrit g {f2(hct241['effect'])}, {f2(hct241['ci_lo'])} to {f2(hct241['ci_hi'])}), and in CB187 haemoglobinuria was seen "
        "in all high-load dogs and in none of the low-load dogs. Load therefore carries damage between the extremes.",
        f"The separate list has {C['low_list_items']} items. The strongest are a B. canis vaccination result where clinical disease "
        "was prevented with little change in parasitaemia (CB375, review of experimental work), severe haemolytic anaemia with very low "
        "smear parasitaemia in 29 B. gibsoni dogs (CB381, abstract only), and the sequestration argument for B. canis that peripheral load "
        "understates total load (CB041, review)."]},
    {"heading": "What this does not show", "paragraphs": [
        "It does not show tolerance. With no pooled cell, the literature neither confirms nor rejects that load separates outcome. "
        "The 'low load' items are case-level or review statements without a comparison group; they show that discordant cases exist, "
        "not how common they are.",
        "Every load here is one moment (mostly at admission), by smear in most units, with the site often not stated. Measurement error "
        "in load flattens any slope and can imitate tolerance. Peripheral load may understate sequestered parasites (B. canis).",
        "Load against outcome was reported by only "
        f"{C['load_units_primary']} of {C['units_with_severity_rows']} units with severity rows; studies that measured load and found "
        "nothing may not have printed it (selective reporting). Species are never compared: each species has its own sources and "
        "definitions. No B. rossi unit reports load against a clinical outcome; the only B. rossi contrast is the experimental dose "
        "(CB105), which sets the load by design.",
        "A dog-level test (log load against a health measure, with age and antibody status as modifiers of the slope) needs the "
        "author data of part c, a user decision."]},
]}

effects = []
for t in table:
    if t["effect"] is None:
        continue
    effects.append({"unit": t["unit"], "article": t["article"], "species_group": t["species_group"],
                    "outcome_class": t["outcome_class"], "definition": t["definition"], "effect_type": t["effect_type"],
                    "effect": t["effect"], "ci_lo": t["ci_lo"], "ci_hi": t["ci_hi"], "n": t["n_total"],
                    "basis": t["effect_basis"], "assumed_n": False})
for s in R["sensitivity"]:
    if s["check"].startswith("equal split"):
        effects.append({"unit": s["unit"], "article": s["article"], "species_group": s["species_group"],
                        "outcome_class": s["outcome_class"], "definition": by_unit[s["unit"]]["definition"],
                        "effect_type": s["effect_type"], "effect": s["effect"], "ci_lo": s["ci_lo"], "ci_hi": s["ci_hi"],
                        "n": by_unit[s["unit"]]["n_total"], "basis": s["note"], "assumed_n": True})
if ab:
    effects.append({"unit": ab["unit"], "article": ab["article"], "species_group": ab["species"], "outcome_class": "severity_grade",
                    "definition": ab["outcome"] + " (antibody level, same cohort)", "effect_type": "rho_antibody",
                    "effect": ab["antibody_rho"], "ci_lo": ab["antibody_ci"][0], "ci_hi": ab["antibody_ci"][1],
                    "n": ab["antibody_n"], "basis": ab["note"], "assumed_n": False})

KEYS = ["unit", "article", "species_group", "outcome_class", "definition", "euthanasia_included", "load_method", "sample_timing",
        "analysis", "direction", "significant", "n_total", "n_severe", "n_comparison", "severe_value", "comparison_value",
        "summary_type", "p_value", "effect_type", "effect", "ci_lo", "ci_hi", "detectable", "effect_basis", "doi"]

load = {
    "experiment": {
        "code": CODE,
        "name": "Parasite load in severe vs mild canine babesiosis: synthesis of published contrasts (SV-02a)",
        "description": "Do dogs with severe babesiosis carry a higher parasite load than dogs with mild disease, inside one species "
                       "and one outcome class? The package hypothesis is that dogs differ more in damage per parasite (tolerance) "
                       "than in load (resistance); part a asks what the published load-by-outcome contrasts can say.",
        "method": "load_outcome_synthesis",
        "dataset": None,
        "parameters": {"package": "SV-02", "part": "a", "role": "primary", "datasets": [],
                       "literature_input": "/experiments/SV-G2/associations_v2.csv",
                       "independent_sources": sources, "species_groups": species_groups,
                       "spec_sha256": SPEC_SHA, "seed": R["seed"],
                       "pool_rule": "REML + Hartung-Knapp only with >= 3 independent units sharing species, outcome class and definition",
                       "cells_pooled": C["cells_pooled"],
                       "spec_written_after_listing_rows": True,
                       "input_sha256": R["inputs"], "versions": R["versions"]},
        "script": "/experiments/SV-02/a/scripts/analyse.py",
        "script_version": SCRIPT_VERSION,
        "run_utc": RUN_UTC,
        "n_subjects": int(sum(t["n_total"] or 0 for t in table)),
        "n_variables": 1,
        "n_tests": 0,
        "summary": summary,
    },
    "associations": [],
    "cluster_assignments": [],
    "results": [
        {"kind": "load_cells", "title": "Primary analysis: pooling cells (species × outcome class)", "sort_order": 1,
         "payload": {"cells": R["cells"], "pooled": R["pooled"], "counts": C,
                     "primary": {"unit": mort["unit"], "article": mort["article"], "species_group": mort["species_group"],
                                 "outcome_class": mort["outcome_class"], "effect_type": mort["effect_type"],
                                 "effect": mort["effect"], "ci_lo": mort["ci_lo"], "ci_hi": mort["ci_hi"],
                                 "n_severe": mort["n_severe"], "n_comparison": mort["n_comparison"],
                                 "detectable": mort["detectable"], "doi": mort["doi"]},
                     "load_units": len(sources), "species_groups": species_groups}},
        {"kind": "unit_effects", "title": "Effect of each unit with computable numbers", "sort_order": 2,
         "payload": {"rows": effects}},
        {"kind": "load_by_outcome", "title": "Direction table: load against outcome, by unit", "sort_order": 3,
         "payload": {"rows": [{k: t[k] for k in KEYS} for t in table]}},
        {"kind": "low_load_list", "title": "Severe disease at low load, protection at unchanged load", "sort_order": 4,
         "payload": {"rows": R["low_list"], "note_hits": C["note_hits"], "note_hits_included": C["note_hits_included"]}},
        {"kind": "damage_by_load_group", "title": "Damage by load group (groups defined by load)", "sort_order": 5,
         "payload": {"units": list(dmg_units.values()), "rows": dmg}},
        {"kind": "sensitivity", "title": "Sensitivity: assumed group sizes and the dose contrast", "sort_order": 6,
         "payload": {"rows": R["sensitivity"]}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interpretation},
    ],
}

os.makedirs(os.path.join(PKG, "out", "db"), exist_ok=True)
path = os.path.join(PKG, "out", "db", f"{CODE}.json")
with open(path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(load, f, indent=1, ensure_ascii=False, allow_nan=False)
print(path, os.path.getsize(path), "bytes")
print(summary)
