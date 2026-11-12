"""SV-02b: build the database load file (way B) from b/out/results.json.

Run after analyse.py, from /experiments/SV-02/b:  env/py/Scripts/python.exe -I scripts/build_load.py
Writes /experiments/SV-02/out/db/SV-02-02-beagle-reaction-norms.json (the loader reads <package>/out/db/).
"""
import hashlib
import json
import os
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PART = os.path.dirname(HERE)
PKG = os.path.dirname(PART)
SCRIPT = os.path.join(HERE, "analyse.py")
CODE = "SV-02-02-beagle-reaction-norms"

R = json.load(open(os.path.join(PART, "out", "results.json"), encoding="utf-8"))
SPEC_SHA = R["inputs"]["experiments/SV-02/b/spec.md"]
RUN_UTC = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
SCRIPT_VERSION = hashlib.sha256(open(SCRIPT, "rb").read()).hexdigest()[:12]
MEAS = {m["key"]: m for m in R["measures"]}
DIGITS = {"hct_drop": 3, "lactate": 2, "habitus_loss": 2}
OUTC = os.path.join(os.path.dirname(PKG), "shared", "tidy", "DS02.outcomes.json")
ORIG = {r["dog_id"]: r["original_id"] for r in json.load(open(OUTC, encoding="utf-8"))["records"] if r.get("original_id")}


def f(v, d=2):
    return "–" if v is None else f"{v:.{d}f}"


def label(dog):
    return f"{dog.replace('DS02:', '')} ({ORIG.get(dog, '?')})"


per = R["per_dog"]
dogs = sorted({r["dog_id"] for r in per})
low = [d for d in dogs if R["dose_groups"][d] == "low"]
high = [d for d in dogs if R["dose_groups"][d] == "high"]
dead = [d for d, v in R["died"].items() if v == 1]
readings = R["readings"]
n_shared = sum(1 for m in readings.values() if m["reading"] == "one shared norm")
n_diff = sum(1 for m in readings.values() if m["reading"] == "different norms")
n_cant = sum(1 for m in readings.values() if m["reading"] == "cannot tell")
row = {(r["dog_id"], r["measure"]): r for r in per}


def rng(dlist, m, k):
    v = [row[(d, m)][k] for d in dlist if row[(d, m)][k] is not None]
    return (min(v), max(v), len(v)) if v else (None, None, 0)


def rng_txt(dlist, m, k):
    lo, hi, n = rng(dlist, m, k)
    d = DIGITS[m]
    if n == 0:
        return "not reached"
    return f(lo, d) if n == 1 or lo == hi else f"{f(lo, d)} to {f(hi, d)}"


peak_low = max(row[(d, "hct_drop")]["peak_parasitaemia_pct"] for d in low)
peak_high_min = min(row[(d, "hct_drop")]["peak_parasitaemia_pct"] for d in high)
peak_high_max = max(row[(d, "hct_drop")]["peak_parasitaemia_pct"] for d in high)
n_low_5 = readings["lactate"]["n_low_5pct"]
dd = dead[0] if dead else None
others_high = [d for d in high if d != dd]

against = n_shared == len(readings)
verdict = ("counts against the package hypothesis (all three measures follow one shared norm)" if against else
           f"does not meet the spec's rule for counting against the hypothesis: {n_shared} of {len(readings)} measures read "
           f"'one shared norm', {n_cant} 'cannot tell' and {n_diff} 'different norms'; no measure shows different norms")

headline = (
    f"At a matched parasitaemia of 5% the low-dose damage lay inside the spec margin of the three high-dose Beagles: "
    f"venous lactate {rng_txt(low, 'lactate', 'damage_at_5pct')} vs {rng_txt(high, 'lactate', 'damage_at_5pct')} mmol/L and "
    f"habitus loss {rng_txt(low, 'habitus_loss', 'damage_at_5pct')} vs {rng_txt(high, 'habitus_loss', 'damage_at_5pct')} points "
    f"(only {n_low_5} low-dose dog reached 5%); at 1% lactate was {rng_txt(low, 'lactate', 'damage_at_1pct')} vs "
    f"{rng_txt(high, 'lactate', 'damage_at_1pct')} mmol/L. "
    f"The groups differed in how far load rose before treatment (peak {f(peak_low, 2)}% low dose vs "
    f"{f(peak_high_min, 1)} to {f(peak_high_max, 1)}% high dose), not in damage per parasite."
)
summary = (
    f"Descriptive, 5 B. rossi Beagles (2 low dose, 3 high dose), 1 source. Damage at matched load did not separate the dose groups: "
    f"lactate at 5% parasitaemia {rng_txt(low, 'lactate', 'damage_at_5pct')} (low dose, n {n_low_5}) vs "
    f"{rng_txt(high, 'lactate', 'damage_at_5pct')} mmol/L (high dose); readings {n_shared} of 3 'one shared norm', "
    f"{n_cant} 'cannot tell' (haematocrit), 0 'different norms'. No hypothesis tests (0 of 0)."
)

# ---- payloads -----------------------------------------------------------------------------------
reading_rows = []
for m, rd in readings.items():
    reading_rows.append({
        "measure": m, "label": MEAS[m]["label"], "unit": MEAS[m]["unit"], "reading": rd["reading"],
        "same_sign": rd["same_sign"], "low_inside_high_1pct": rd["low_inside_high_1pct"],
        "low_inside_high_5pct": rd["low_inside_high_5pct"], "separate_1pct": rd["separate_1pct"],
        "separate_5pct": rd["separate_5pct"], "residual_outlier_dog": rd["residual_outlier_dog"],
        "n_low_5pct": rd["n_low_5pct"], "n_high_5pct": rd["n_high_5pct"], "margin": R["margins"][m],
        "low_at_1pct": rng_txt(low, m, "damage_at_1pct"), "high_at_1pct": rng_txt(high, m, "damage_at_1pct"),
        "low_at_5pct": rng_txt(low, m, "damage_at_5pct"), "high_at_5pct": rng_txt(high, m, "damage_at_5pct"),
    })

primary = {
    "label": "Reaction norms: damage against log parasitaemia, before treatment (DS02)",
    "headline": headline,
    "status": f"{n_shared} of 3 one shared norm · {n_cant} cannot tell · {n_diff} different norms",
    "verdict": verdict,
    "n_dogs": len(dogs), "n_low": len(low), "n_high": len(high), "n_points": sum(1 for _ in R["points"]),
    "independent_sources": 1, "sources": ["SRC-B (DS02; DS03 experimental dogs and DS06 are the same 5 Beagles)"],
    "readings": reading_rows,
}

dog_rows = []
for r in per:
    dog_rows.append({
        "dog": label(r["dog_id"]), "original_id": ORIG.get(r["dog_id"]), "dose_group": r["dose_group"], "died": r["died"],
        "measure": r["measure"], "measure_label": MEAS[r["measure"]]["label"], "unit": MEAS[r["measure"]]["unit"],
        "n_points": r["n_points"], "slope": r["slope"], "ci_low": r["ci_lo"], "ci_high": r["ci_hi"], "theil_sen": r["theil_sen"],
        "damage_at_1pct": r["damage_at_1pct"], "damage_at_5pct": r["damage_at_5pct"],
        "peak_parasitaemia_pct": r["peak_parasitaemia_pct"], "peak_timepoint": r["peak_timepoint"], "damage_at_peak": r["damage_at_peak"],
        "mean_residual": R["pooled"][r["measure"]]["mean_residual"].get(r["dog_id"]),
    })

charts = []
for m in MEAS:
    dser = []
    for d in dogs:
        pts = [{"x": p["log10_load"], "y": p[m], "timepoint": p["timepoint"], "parasitaemia_pct": p["parasitaemia_pct"]}
               for p in R["points"] if p["dog_id"] == d and p[m] is not None]
        rr = row[(d, m)]
        xs = [p["x"] for p in pts]
        line = []
        if rr["slope"] is not None and xs:
            line = [{"x": x, "y": rr["intercept"] + rr["slope"] * x} for x in (min(xs), max(xs))]
        dser.append({"dog": label(d), "dose_group": R["dose_groups"][d], "died": R["died"].get(d), "points": pts, "fit": line})
    allx = [p["log10_load"] for p in R["points"]]
    pl = R["pooled"][m]
    charts.append({
        "measure": m, "label": MEAS[m]["label"], "unit": MEAS[m]["unit"], "offset": R["offset"],
        "dogs": dser,
        "pooled": [{"x": x, "y": pl["intercept"] + pl["slope"] * x} for x in (min(allx), max(allx))] if pl["slope"] is not None else [],
        "pooled_slope": pl["slope"],
        "matched_loads_pct": R["targets_pct"],
        "footnote": (f"DS02, 5 B. rossi Beagles, {pl['n_points']} pre-treatment dog-days (days 1 to 4 and the extra low-dose day-4 sample). "
                     f"x = log10(parasitaemia % + {R['offset']}); lines are per-dog OLS fits; dashed line is the pooled fit, "
                     f"which ignores repeated measures. Descriptive; one source; dose and dog are aliased."),
    })

sens_rows = []
seen = set()
for s in R["sensitivity"]:
    k = (s["check"], s["measure"])
    if k in seen:
        continue
    seen.add(k)
    rows = [x for x in R["sensitivity"] if (x["check"], x["measure"]) == k]
    slopes = [x["slope"] for x in rows if x["slope"] is not None]
    sens_rows.append({
        "check": s["check"], "measure": s["measure"], "measure_label": MEAS[s["measure"]]["label"], "reading": s["reading"],
        "primary_reading": readings[s["measure"]]["reading"], "n_dogs": len(rows),
        "slope_min": min(slopes) if slopes else None, "slope_max": max(slopes) if slopes else None,
        "n_negative_slopes": sum(1 for v in slopes if v < 0),
    })
n_sens_same = sum(1 for s in sens_rows if s["reading"] == s["primary_reading"])

dd_txt = ""
if dd:
    o = others_high
    dd_txt = (
        f"The dog that died ({label(dd)}, high dose) had the most damage at its peak load of {f(row[(dd, 'hct_drop')]['peak_parasitaemia_pct'], 1)}%: "
        f"haematocrit drop {f(row[(dd, 'hct_drop')]['damage_at_peak'], 3)} L/L, lactate {f(row[(dd, 'lactate')]['damage_at_peak'])} mmol/L and "
        f"habitus loss {f(row[(dd, 'habitus_loss')]['damage_at_peak'], 0)}, against {rng_txt(o, 'hct_drop', 'damage_at_peak')} L/L, "
        f"{rng_txt(o, 'lactate', 'damage_at_peak')} mmol/L and {rng_txt(o, 'habitus_loss', 'damage_at_peak')} in the other high-dose dogs at "
        f"peaks of {f(min(row[(d, 'hct_drop')]['peak_parasitaemia_pct'] for d in o), 1)} to "
        f"{f(max(row[(d, 'hct_drop')]['peak_parasitaemia_pct'] for d in o), 1)}%. Its mean residual from the pooled line was not twice that of "
        f"every other dog, so the spec's rule does not call it a different norm. It is one dog on one day, and it was not treated."
    )

interpretation = {"sections": [
    {"heading": "Question", "paragraphs": [
        "SV-02 asks whether dogs with babesiosis differ more in the damage they suffer at a given parasite load (tolerance) than in the load "
        "itself (resistance). Part b looks inside one experiment: 5 Beagles infected with B. rossi (2 low dose, 3 high dose). Does every dog "
        "lose health along the same line of damage against log parasitaemia (one shared reaction norm), or do dogs at the same load differ?"]},
    {"heading": "What was done", "paragraphs": [
        f"For each dog, the pre-treatment samples with a parasitaemia value (days 1 to 4, and the extra day-4 sample of the low-dose dogs; "
        f"{primary['n_points']} dog-days) were plotted as three health measures against log10(parasitaemia % + {R['offset']}): the drop of "
        f"haematocrit from the dog's own baseline (days -1 and 0), venous lactate, and habitus loss (4 minus the daily habitus score). "
        f"Each dog got an OLS slope with its 95% interval and a Theil-Sen slope, and its damage was interpolated at a common load of 1% and "
        f"5% where its series spanned that load. A reading rule written in the spec before the habitus values were opened labels each measure "
        f"'one shared norm', 'different norms' or 'cannot tell'. There is no hypothesis test.",
        "Clarifications of the spec: when a 'different norms' criterion and the 'shared norm' criterion both hold, 'different norms' wins (it "
        "did not arise); venous lactate is analysed as measured, as the spec's variable list says, so the baseline sentence for lactate was not "
        "applied. Before the spec was written a format probe printed the 'died' value of two dogs; no habitus value was seen."]},
    {"heading": "Result", "paragraphs": [
        headline,
        f"Readings: venous lactate '{readings['lactate']['reading']}', habitus '{readings['habitus_loss']['reading']}', haematocrit "
        f"'{readings['hct_drop']['reading']}'. Haematocrit cannot be read because the slopes do not share a sign: low-dose "
        f"{label(low[0])} has slope {f(row[(low[0], 'hct_drop')]['slope'], 3)} L/L per log10 unit, the other dogs "
        f"{rng_txt([d for d in dogs if d != low[0]], 'hct_drop', 'slope')}. Haematocrit fell only at loads the low-dose dogs never reached "
        f"before treatment. Only {n_low_5} low-dose dog reached 5%; the other peaked at {f(row[(low[1], 'hct_drop')]['peak_parasitaemia_pct'], 2)}%.",
        f"So the result {verdict}. In these 5 dogs damage followed load; nothing here suggests that one dog tolerated a given load better "
        f"than another at the loads where they overlap. The low-dose values sit at or just below the low end of the high-dose range; "
        f"if that is real, it points to dose or time since inoculation, not to a dog that tolerates more.",
        dd_txt,
        f"Sensitivity: {n_sens_same} of {len(sens_rows)} checks (other offsets, positive loads only, clinical lactate, raw haematocrit, "
        f"leaving out the dog that died) give the same reading as the primary analysis."]},
    {"heading": "What this does not show", "paragraphs": [
        "Five dogs from one experiment (1 independent source) cannot measure how much dogs differ in tolerance, and the per-dog intervals have "
        "1 or 2 residual degrees of freedom. Dose and dog are aliased, and at a matched load a high-dose dog is about one day earlier after "
        "inoculation than a low-dose dog. Treatment at about 96 h (high dose) and 108 h (low dose) cut the low-dose series at 5 to 7% "
        "parasitaemia, so the norms overlap only at low loads, where there was little damage to compare. Error in a single smear flattens "
        "slopes; peripheral parasitaemia may understate sequestered parasites. The damage-load relation is not linear in log load (flat, then "
        "a rise above about 10%), so the slopes are rough summaries; the matched-load values carry the reading. Nothing here applies to natural "
        "infection, other species, or the DS03 and DS06 files, which hold the same dogs."]},
]}
interpretation["sections"] = [{"heading": s["heading"], "paragraphs": [p for p in s["paragraphs"] if p]} for s in interpretation["sections"]]

load = {
    "experiment": {
        "code": CODE,
        "name": "Damage against parasite load in each of the 5 experimentally infected Beagles (DS02, B. rossi)",
        "description": ("Do the 5 Beagles infected with B. rossi lose haematocrit, lactate balance and habitus along one shared line against log "
                        "parasitaemia, or do dogs at the same load differ in damage? The package hypothesis is that dogs differ more in damage "
                        "per parasite (tolerance) than in load (resistance); here it can only be described, not tested."),
        "method": "reaction_norm",
        "dataset": None,
        "parameters": {"package": "SV-02", "part": "b", "role": "descriptive", "datasets": ["DS02"], "independent_sources": ["SRC-B"],
                       "linked_files_not_used": ["DS01", "DS03 experimental dogs", "DS06"],
                       "spec_sha256": SPEC_SHA, "seed": R["seed"], "load_offset_pct": R["offset"], "matched_loads_pct": R["targets_pct"],
                       "margins": R["margins"], "window": "pre-treatment, days 1-4 and day_4_1",
                       "versions": R["versions"], "inputs": R["inputs"]},
        "script": "/experiments/SV-02/b/scripts/analyse.py",
        "script_version": SCRIPT_VERSION,
        "run_utc": RUN_UTC,
        "n_subjects": len(dogs), "n_variables": 4, "n_tests": 0,
        "summary": summary,
    },
    "associations": [],
    "cluster_assignments": [],
    "results": [
        {"kind": "primary_result", "title": "Primary result: reading of the reaction norms", "sort_order": 1, "payload": primary},
        {"kind": "reaction_norms", "title": "Damage against log parasitaemia, by dog", "sort_order": 2, "payload": {"charts": charts}},
        {"kind": "dog_slopes", "title": "Per-dog slopes, matched-load damage and peak", "sort_order": 3, "payload": {"rows": dog_rows}},
        {"kind": "sensitivity", "title": "Sensitivity checks", "sort_order": 4, "payload": {"rows": sens_rows}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interpretation},
    ],
}

dst = os.path.join(PKG, "out", "db")
os.makedirs(dst, exist_ok=True)
text = json.dumps(load, indent=1, ensure_ascii=False, allow_nan=False)
open(os.path.join(dst, f"{CODE}.json"), "w", encoding="utf-8").write(text)
print(summary)
print(len(text.encode("utf-8")), "bytes")
