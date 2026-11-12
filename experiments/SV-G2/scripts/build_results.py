"""Describe the SV-G2 extraction and write the load file for experiment SV-G2-01-literature-extraction.

Reads associations_v2.csv, definitions_v2.csv, extractions/*.json, batches/batches.json and out/agreement_*.json.
Writes plot-ready tables to out/tables/*.csv and the console-loader file out/db/SV-G2-01-literature-extraction.json.
Counting unit is the independent unit (cohort from /core/cohorts.json, else the article); rows are never evidence.
Standard library only. Usage (from /experiments/SV-G2/): python -I scripts/build_results.py --run-utc 2026-11-12T00:00:00Z
"""
import argparse
import collections
import csv
import hashlib
import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
CODE = "SV-G2-01-literature-extraction"
UP = {"higher_in_severe", "more_frequent_in_severe", "positive_association"}
DOWN = {"lower_in_severe", "less_frequent_in_severe", "negative_association"}
HOST_CLASSES = {"signalment", "clinical history", "treatment"}
PARASITE_CLASSES = {"parasitology"}
SPECIES_ORDER = ["B. rossi", "B. canis", "B. gibsoni", "B. vogeli", "Other single species", "Mixed or unspecified", "Not canine (BG)"]


def species_group(s, aid):
    if aid.startswith("BG"):
        return "Not canine (BG)"
    low = (s or "").lower()
    hits = [n for n, k in [("B. rossi", "rossi"), ("B. canis", "canis"), ("B. gibsoni", "gibsoni"), ("B. vogeli", "vogeli")] if k in low]
    if "canis rossi" in low:
        hits = ["B. rossi"]
    if "canis vogeli" in low or "c. vogeli" in low:
        hits = ["B. vogeli"]
    if len(hits) == 1 and "mixed" not in low and "unspecified" not in low and "," not in low:
        return hits[0]
    if not hits and low and "mixed" not in low and "unspecified" not in low and "spp" not in low and low not in ("babesia sp.",):
        return "Other single species"
    return "Mixed or unspecified"


def factor_type(cls):
    return "host factor" if cls in HOST_CLASSES else "parasite factor" if cls in PARASITE_CLASSES else \
        "clinical sign or score" if cls in ("clinical sign", "clinical score") else "laboratory or other marker"


def sha12(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:12]


def read_csv(p):
    with open(p, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def write_csv(p, rows, fields=None):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields or (list(rows[0]) if rows else ["empty"]))
        w.writeheader()
        w.writerows(rows)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-utc", required=True)
    args = ap.parse_args()
    rows = read_csv(PKG / "associations_v2.csv")
    defs = read_csv(PKG / "definitions_v2.csv")
    plan = json.loads((PKG / "batches" / "batches.json").read_text(encoding="utf-8"))
    scope = sorted(i for b in plan["batches"].values() for i in b)
    files = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((PKG / "extractions").glob("*.json"))}
    import importlib.util
    spec = importlib.util.spec_from_file_location("chk", PKG / "scripts" / "check_associations.py")
    chk = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(chk)
    member, articles, short = chk.load_context()
    unit_of = {i: member.get(i) or i for i in scope}
    sp_of = {i: species_group(articles.get(i, {}).get("species_short", "") or short.get(i, {}).get("species", ""), i) for i in scope}
    for r in rows:
        r["species_group"] = sp_of.get(r["id"], "Mixed or unspecified")
        r["factor_type"] = factor_type(r["marker_class"])
        r["dgroup"] = "up" if r["significant"] == "yes" and r["direction"] in UP else \
            "down" if r["significant"] == "yes" and r["direction"] in DOWN else \
            "null" if r["significant"] == "no" or r["direction"] == "no_difference" else "other"
    T = PKG / "out" / "tables"

    # 1. Overview
    with_rows = sorted({r["id"] for r in rows})
    no_rows = [i for i in scope if i in files and i not in with_rows]
    missing = [i for i in scope if i not in files]
    units_scope = sorted({unit_of[i] for i in scope})
    units_rows = sorted({unit_of[i] for i in with_rows})
    qc = collections.Counter(r["quote_check"] for r in rows)
    dq = collections.Counter(d["quote_check"] for d in defs)
    canine_units_rows = sorted({unit_of[i] for i in with_rows if i.startswith("CB")})
    overview = {
        "articles_in_scope": len(scope), "articles_extracted": len(files), "articles_missing": missing,
        "articles_with_associations": len(with_rows), "articles_without_associations": len(no_rows),
        "independent_units_in_scope": len(units_scope), "independent_units_with_associations": len(units_rows),
        "canine_units_with_associations": len(canine_units_rows),
        "severity_definitions": len(defs), "association_rows": len(rows),
        "rows_significant": sum(r["significant"] == "yes" for r in rows), "rows_not_significant": sum(r["significant"] == "no" for r in rows),
        "rows_not_tested": sum(r["significant"] == "not_tested" for r in rows),
        "canonical_markers": len({r["marker"] for r in rows if r["marker"]}),
        "markers_in_2plus_units": 0,
        "quote_check_rows": dict(qc), "quote_check_definitions": dict(dq),
        "rows_numbers_not_in_text": sum(bool(r["numbers_missing"]) for r in rows),
        "rows_schema_errors": sum(bool(r["errors"]) for r in rows),
        "rows_unmapped_marker": sum(r["map_status"] == "unmapped" for r in rows),
        "calibration_batch": plan["batches"]["B00"],
    }

    # 2. Markers (canonical) by units and direction
    by_marker = collections.defaultdict(lambda: {"rows": 0, "articles": set(), "units": set(), "up": set(), "down": set(),
                                                 "null": set(), "classes": set(), "species": set(), "outcomes": set()})
    for r in rows:
        if not r["marker"] or r["marker"] == "-":
            continue
        m = by_marker[r["marker"]]
        m["rows"] += 1
        m["articles"].add(r["id"])
        m["units"].add(r["independent_unit"])
        m["classes"].add(r["marker_class"])
        m["species"].add(r["species_group"])
        m["outcomes"].add(r["outcome_class"])
        if r["dgroup"] in ("up", "down", "null"):
            m[r["dgroup"]].add(r["independent_unit"])
    marker_rows = sorted(({
        "marker": k, "marker_class": sorted(v["classes"])[0], "factor_type": factor_type(sorted(v["classes"])[0]),
        "units": len(v["units"]), "articles": len(v["articles"]), "rows": v["rows"],
        "units_sig_higher": len(v["up"]), "units_sig_lower": len(v["down"]), "units_not_significant": len(v["null"]),
        "outcome_classes": "; ".join(sorted(v["outcomes"])), "species_groups": "; ".join(s for s in SPECIES_ORDER if s in v["species"]),
    } for k, v in by_marker.items()), key=lambda x: (-x["units"], -x["articles"], x["marker"]))
    overview["markers_in_2plus_units"] = sum(m["units"] >= 2 for m in marker_rows)
    write_csv(T / "markers.csv", marker_rows)

    by_class = collections.defaultdict(lambda: {"rows": 0, "units": set(), "articles": set(), "markers": set()})
    for r in rows:
        c = by_class[r["marker_class"] or "unmapped"]
        c["rows"] += 1
        c["units"].add(r["independent_unit"])
        c["articles"].add(r["id"])
        c["markers"].add(r["marker"])
    class_rows = sorted(({"marker_class": k, "factor_type": factor_type(k), "units": len(v["units"]), "articles": len(v["articles"]),
                          "markers": len(v["markers"]), "rows": v["rows"]} for k, v in by_class.items()), key=lambda x: -x["units"])
    write_csv(T / "marker_classes.csv", class_rows)
    factor_rows = [m for m in marker_rows if m["factor_type"] in ("host factor", "parasite factor")]
    write_csv(T / "host_parasite_factors.csv", factor_rows, list(marker_rows[0]) if marker_rows else None)

    # load method on parasite load rows
    lm = collections.defaultdict(lambda: {"rows": 0, "units": set()})
    for r in rows:
        if r["marker"] in ("Parasitaemia", "Parasite DNA load (qPCR)"):
            x = lm[(r["marker"], r["load_method"] or "missing")]
            x["rows"] += 1
            x["units"].add(r["independent_unit"])
    load_rows = [{"marker": k[0], "load_method": k[1], "units": len(v["units"]), "rows": v["rows"]} for k, v in sorted(lm.items())]
    write_csv(T / "load_methods.csv", load_rows, ["marker", "load_method", "units", "rows"])

    # 3. Species
    sp = collections.defaultdict(lambda: {"articles": set(), "units": set(), "rows": 0, "art_scope": set()})
    for i in scope:
        sp[sp_of[i]]["art_scope"].add(i)
    for r in rows:
        x = sp[r["species_group"]]
        x["articles"].add(r["id"])
        x["units"].add(r["independent_unit"])
        x["rows"] += 1
    species_rows = [{"species_group": s, "articles_in_scope": len(sp[s]["art_scope"]), "articles_with_rows": len(sp[s]["articles"]),
                     "units_with_rows": len(sp[s]["units"]), "rows": sp[s]["rows"]} for s in SPECIES_ORDER if s in sp]
    write_csv(T / "species.csv", species_rows)

    # 4. Outcome class (definitions and rows) and components
    oc = collections.defaultdict(lambda: {"definitions": 0, "def_units": set(), "rows": 0, "row_units": set()})
    for d in defs:
        oc[d["outcome_class"]]["definitions"] += 1
        oc[d["outcome_class"]]["def_units"].add(d["independent_unit"])
    for r in rows:
        oc[r["outcome_class"]]["rows"] += 1
        oc[r["outcome_class"]]["row_units"].add(r["independent_unit"])
    outcome_rows = sorted(({"outcome_class": k, "definitions": v["definitions"], "units_defining": len(v["def_units"]),
                            "rows": v["rows"], "units_with_rows": len(v["row_units"])} for k, v in oc.items()), key=lambda x: -x["units_defining"])
    write_csv(T / "outcome_classes.csv", outcome_rows)
    comp = collections.defaultdict(lambda: {"definitions": 0, "units": set()})
    for d in defs:
        for c in [c.strip() for c in d["components"].split(";") if c.strip()]:
            comp[c]["definitions"] += 1
            comp[c]["units"].add(d["independent_unit"])
    component_rows = sorted(({"component": k, "definitions": v["definitions"], "units": len(v["units"])} for k, v in comp.items()), key=lambda x: -x["units"])
    write_csv(T / "definition_components.csv", component_rows)
    simple = lambda field: [{"value": k, "definitions": n} for k, n in collections.Counter(d[field] or "missing" for d in defs).most_common()]
    euth_rows = [{"value": k, "definitions": n} for k, n in collections.Counter(d["euthanasia_included"] for d in defs if d["outcome_class"] == "mortality").most_common()]
    setting_rows = [{"value": k, "articles": n} for k, n in collections.Counter(files[i].get("setting", "missing") for i in files).most_common()]
    timing_rows = [{"value": k, "articles": n} for k, n in collections.Counter(files[i].get("sample_timing", "missing") for i in files).most_common()]
    write_csv(T / "settings.csv", setting_rows)
    write_csv(T / "sample_timing.csv", timing_rows)
    write_csv(T / "mortality_euthanasia.csv", euth_rows, ["value", "definitions"])
    source_rows = simple("definition_source")

    # 5. Independent units
    un = collections.defaultdict(lambda: {"articles": set(), "with_rows": set(), "rows": 0, "defs": 0, "species": set()})
    for i in scope:
        un[unit_of[i]]["articles"].add(i)
        un[unit_of[i]]["species"].add(sp_of[i])
    for r in rows:
        un[r["independent_unit"]]["with_rows"].add(r["id"])
        un[r["independent_unit"]]["rows"] += 1
    for d in defs:
        un[d["independent_unit"]]["defs"] += 1
    unit_rows = sorted(({"independent_unit": k, "is_cohort": k.startswith("CH"), "articles": " ".join(sorted(v["articles"])),
                         "n_articles": len(v["articles"]), "articles_with_rows": len(v["with_rows"]), "definitions": v["defs"], "rows": v["rows"],
                         "species_groups": "; ".join(s for s in SPECIES_ORDER if s in v["species"])} for k, v in un.items()),
                       key=lambda x: (-x["rows"], x["independent_unit"]))
    write_csv(T / "independent_units.csv", unit_rows)
    cohort_rows = [u for u in unit_rows if u["is_cohort"]]

    # 6. Not extracted
    ne = collections.Counter()
    ne_art = collections.defaultdict(set)
    for i, f in files.items():
        for x in f.get("not_extracted") or []:
            ne[x.get("reason", "other")] += 1
            ne_art[x.get("reason", "other")].add(i)
    ne_rows = [{"reason": k, "items": n, "articles": len(ne_art[k])} for k, n in ne.most_common()]
    write_csv(T / "not_extracted.csv", ne_rows, ["reason", "items", "articles"])
    no_assoc_rows = [{"id": i, "unit": unit_of[i], "species_group": sp_of[i],
                      "skipped_infected_vs_healthy": files[i].get("skipped_infected_vs_healthy"),
                      "reason": (files[i].get("article_notes") or "")[:300]} for i in no_rows]
    write_csv(T / "articles_without_associations.csv", no_assoc_rows, ["id", "unit", "species_group", "skipped_infected_vs_healthy", "reason"])

    # 7. Agreement
    agreement = {}
    for name in ("second", "pilot"):
        p = PKG / "out" / f"agreement_{name}.json"
        if p.exists():
            a = json.loads(p.read_text(encoding="utf-8"))
            agreement[name] = {k: v for k, v in a.items() if k != "per_article"}
    resolutions = PKG / "agreement_resolutions.csv"
    if resolutions.exists():
        agreement["resolutions"] = len(read_csv(resolutions))

    # Load file
    sec = agreement.get("second", {})
    top = [m for m in marker_rows[:12]]
    top_text = ", ".join(f"{m['marker']} ({m['units']})" for m in top[:6])
    summary = (f"{overview['articles_extracted']} of {overview['articles_in_scope']} full-text tier A/B articles extracted under schema v2: "
               f"{overview['association_rows']} marker-by-severity rows from {overview['articles_with_associations']} articles in "
               f"{overview['independent_units_with_associations']} independent units ({overview['severity_definitions']} severity definitions, "
               f"{overview['canonical_markers']} canonical markers, {overview['markers_in_2plus_units']} in 2 or more units). "
               f"Blind 20% second extraction: significance agreement {sec.get('significance_agreement')}, direction agreement "
               f"{sec.get('direction_agreement')} on {sec.get('matched_pairs')} matched pairs. Descriptive; no tests.")
    interp = {"sections": [
        {"heading": "Question", "paragraphs": [
            "Which laboratory markers and host or parasite factors have published canine babesiosis studies tested against severity or outcome, "
            "under which definitions, in which species and in how many independent cohorts? SV-G2 is the groundwork for SV-03 (evidence matrix) "
            "and SV-02a (parasite load by outcome); it has no hypothesis test."]},
        {"heading": "What was done", "paragraphs": [
            f"Every shortlist article with tier A or B and a full text ({overview['articles_in_scope']} articles, "
            f"{overview['independent_units_in_scope']} independent units) was extracted by sub-agents in batches of about 10 under schema v2, "
            "which adds definition components, euthanasia, definition source, follow-up horizon, setting, sample timing, per-group values with "
            "summary type, the parasite load method, and a list of what could not be extracted. The ten pilot articles were re-extracted first as a "
            "calibration batch. Every quote was checked against the article text by the checker; the owner checked a sample of each batch by hand. "
            f"A blind second extraction of a random 20% sample ({sec.get('articles', 0)} articles, seed {plan['seed']}) measured agreement.",
            "Counts are independent units: articles that share a cohort in /core/cohorts.json count once. Rows are not evidence."]},
        {"heading": "Result", "paragraphs": [
            f"{overview['association_rows']} rows ({overview['rows_significant']} significant, {overview['rows_not_significant']} not significant, "
            f"{overview['rows_not_tested']} not tested) from {overview['articles_with_associations']} articles; "
            f"{overview['articles_without_associations']} articles reported nothing against severity. "
            f"Markers reported in the most independent units: {top_text}.",
            f"Quotes: {qc.get('exact', 0)} exact and {qc.get('near', 0)} near of {len(rows)} rows. "
            f"Second extraction: coverage {sec.get('coverage_ref_found_by_other')} of the first extraction's marker-by-outcome keys, "
            f"significance agreement {sec.get('significance_agreement')} (kappa {sec.get('significance_kappa')}), direction agreement "
            f"{sec.get('direction_agreement')}."]},
        {"heading": "What this does not show", "paragraphs": [
            "This is a description of what was reported, not a synthesis: direction counts are not effect sizes, and markers reported only when "
            "significant (selective reporting) inflate the 'higher' and 'lower' columns. Species is aliased with source, setting and definition: "
            "do not compare species from these counts. Categories and cohort links come from NLP and agent extraction with one owner check, not a "
            "full human review. The 34 abstract-only tier B articles are not included. Mortality definitions usually count euthanasia as death."]},
    ]}
    load = {
        "experiment": {
            "code": CODE,
            "name": "Severity literature extraction: markers and host or parasite factors tested against severity (117 articles, schema v2)",
            "description": "Which markers and host or parasite factors have canine babesiosis studies tested against severity or outcome, under which "
                           "definitions and in how many independent cohorts? Descriptive groundwork for SV-03 and SV-02a; no hypothesis is tested.",
            "method": "literature_extraction",
            "dataset": None,
            "parameters": {"package": "SV-G2", "role": "descriptive", "datasets": [], "independent_sources": [],
                           "scope": "shortlist tier A/B, source_format not abstract", "articles": len(scope),
                           "independent_units": len(units_scope), "spec_sha256": hashlib.sha256((PKG / "spec.md").read_bytes()).hexdigest(),
                           "seed": plan["seed"], "second_sample_n": plan["second_n"], "schema": "association_schema_v2.json",
                           "schema_sha256": hashlib.sha256((PKG / "association_schema_v2.json").read_bytes()).hexdigest()},
            "script": "/experiments/SV-G2/scripts/build_results.py",
            "script_version": sha12(PKG / "scripts" / "build_results.py"),
            "run_utc": args.run_utc,
            "n_subjects": overview["articles_extracted"], "n_variables": overview["canonical_markers"], "n_tests": 0,
            "summary": summary,
        },
        "associations": [], "cluster_assignments": [],
        "results": [
            {"kind": "extraction_overview", "title": "Coverage of the extraction", "sort_order": 1, "payload": overview},
            {"kind": "markers", "title": "Markers and factors by independent units", "sort_order": 2, "payload": {"rows": marker_rows}},
            {"kind": "marker_classes", "title": "Records by marker class", "sort_order": 3, "payload": {"rows": class_rows}},
            {"kind": "host_parasite_factors", "title": "Host and parasite factors", "sort_order": 4,
             "payload": {"rows": factor_rows, "load_methods": load_rows}},
            {"kind": "species", "title": "Records by species", "sort_order": 5, "payload": {"rows": species_rows}},
            {"kind": "outcome_definitions", "title": "Severity definitions", "sort_order": 6,
             "payload": {"outcome_classes": outcome_rows, "components": component_rows, "mortality_euthanasia": euth_rows,
                         "definition_sources": source_rows[:15], "settings": setting_rows, "sample_timing": timing_rows}},
            {"kind": "independent_units", "title": "Records by cohort and independent unit", "sort_order": 7,
             "payload": {"rows": unit_rows, "cohorts": len(cohort_rows)}},
            {"kind": "not_extracted", "title": "What could not be extracted", "sort_order": 8,
             "payload": {"reasons": ne_rows, "articles_without_associations": [{k: v for k, v in r.items() if k != "reason"} for r in no_assoc_rows],
                         "articles_missing": missing}},
            {"kind": "agreement", "title": "Agreement with the blind second extraction and the pilot", "sort_order": 9, "payload": agreement},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 10, "payload": interp},
        ],
    }
    db = PKG / "out" / "db"
    db.mkdir(parents=True, exist_ok=True)
    text = json.dumps(load, indent=1, ensure_ascii=False, allow_nan=False)
    (db / f"{CODE}.json").write_text(text, encoding="utf-8")
    print(f"wrote {db / (CODE + '.json')} ({len(text.encode('utf-8')) // 1024} KB)")
    print(summary)


if __name__ == "__main__":
    main()
