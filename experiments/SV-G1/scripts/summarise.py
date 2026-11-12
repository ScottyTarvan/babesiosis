"""Merge the per-dataset outputs of the SV-G1 tidy scripts and describe the data layer.

Writes:
  shared/dictionary.csv                         one row per (variable, dataset)
  SV-G1/out/coverage.csv                        harmonised name x dataset: share of dogs with a value
  SV-G1/out/datasets.csv                        one row per dataset
  SV-G1/out/summary.json                        everything the report and the database rows use
  SV-G1/out/db/SV-G1-01-data-layer-coverage.json  the load file for the console loader (run-instructions.md, way B)
"""
import csv
import datetime as dt
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tidylib import HARMONISED, OUT, SHARED, TIDY  # noqa: E402

CODE = "SV-G1-01-data-layer-coverage"
ORDER = ["S-CB050", "S-CB517", "DS07", "S-CB017", "S-CB516", "DS05", "DS03", "DS02", "DS04"]
SPECIES = {}
# Known links between files (data.md "Never pool these" and what SV-G1 found). Pairs of (file, file, what).
LINKS = [
    ("S-CB517", "S-CB050", "Same dogs: S-CB050 cases 1-97 and controls 201-215"),
    ("DS03", "DS02", "The 5 DS03 experimental dogs are the 5 DS02 Beagles (matched by value in SV-G1)"),
    ("DS04", "S-CB050", "At least 3 fatal DS04 dogs are S-CB050 cases 126, 127 and 131 (matched by value)"),
    ("DS03", "S-CB050", "Possible, unverified (same hospital)"),
    ("DS07", "DS04", "Possible, not confirmed (case numbers overlap; no shared values)"),
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(ds):
    f = json.loads((TIDY / f"{ds}.features.json").read_text(encoding="utf-8"))
    o = json.loads((TIDY / f"{ds}.outcomes.json").read_text(encoding="utf-8"))
    c = json.loads((OUT / "checks" / f"{ds}.json").read_text(encoding="utf-8"))
    return f, o, c


def main(final=True):
    present = [ds for ds in ORDER if (TIDY / f"{ds}.features.json").exists()]
    missing = [ds for ds in ORDER if ds not in present]
    if final and missing:
        raise SystemExit(f"tidy files missing for: {missing}")

    # 1. dictionary
    rows = []
    for ds in present:
        with open(OUT / "dictionary" / f"{ds}.csv", encoding="utf-8") as fh:
            rows += list(csv.DictReader(fh))
    cols = ["harmonised_name", "dataset_id", "original_column", "unit", "conversion", "note"]
    rows.sort(key=lambda r: (0 if r["harmonised_name"] in HARMONISED else 1,
                             list(HARMONISED).index(r["harmonised_name"]) if r["harmonised_name"] in HARMONISED else 0,
                             r["harmonised_name"], ORDER.index(r["dataset_id"])))
    with open(SHARED / "dictionary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)

    # 2. per-dataset description and coverage
    datasets, coverage, checks_all, flags, notes_count = [], {}, [], [], {}
    total_records = 0
    sources = set()
    for ds in present:
        f, o, c = load(ds)
        recs = f["records"]
        dogs = sorted({r["dog_id"] for r in recs})
        groups = defaultdict(set)
        for r in recs:
            groups[r["group"]].add(r["dog_id"])
        names = [v["name"] for v in f["variables"]]
        cells = len(recs) * len(names)
        filled = sum(1 for r in recs for n in names if r["values"].get(n) is not None)
        censored = sum(len(r.get("censored") or {}) for r in recs)
        tps = sorted({r.get("timepoint") or "" for r in recs})
        harmonised = [n for n in HARMONISED if n in names]
        for n in HARMONISED:
            if n in names:
                with_value = {r["dog_id"] for r in recs if r["values"].get(n) is not None}
                coverage[(n, ds)] = round(len(with_value) / len(dogs), 4) if dogs else None
        outcome_dogs = defaultdict(set)
        for r in o["records"]:
            for k, v in r["values"].items():
                if v is not None:
                    outcome_dogs[k].add(r["dog_id"])
        ds_flags = [n for n in f["cleaning_notes"] if n.startswith("FLAG")]
        flags += [{"dataset": ds, "note": n} for n in ds_flags]
        n_pass = sum(1 for x in c["checks"] if x["pass"])
        for x in c["checks"]:
            checks_all.append({"dataset": ds, "check": x["name"], "observed": x["observed"], "expected": x["expected"],
                               "source": x["source"], "pass": x["pass"]})
        sources.add(f["independent_source"])
        total_records += len(recs)
        datasets.append({
            "dataset": ds, "independent_source": f["independent_source"], "species": f["species"],
            "dogs": len(dogs), "infected": len(groups.get("infected", ())), "control": len(groups.get("control", ())),
            "comparator": len(groups.get("comparator", ())), "records": len(recs),
            "timepoints": [t for t in tps if t], "variables": len(names), "harmonised_variables": len(harmonised),
            "missing_pct": round(100 * (1 - filled / cells), 1) if cells else None,
            "censored_cells": censored,
            "outcomes": [{"name": od["name"], "dogs_with_value": len(outcome_dogs.get(od["name"], ()))} for od in o["outcomes"]],
            "checks_passed": n_pass, "checks_total": len(c["checks"]), "flags": len(ds_flags),
            "cleaning_notes": len(f["cleaning_notes"]),
            "inputs": f["built_from"],
        })

    # 3. distinct dogs after the confirmed links
    by = {d["dataset"]: d for d in datasets}
    dog_records = sum(d["dogs"] for d in datasets)
    dup = 0
    if "S-CB517" in by:
        f517 = json.loads((TIDY / "S-CB517.features.json").read_text(encoding="utf-8"))
        dup += len({r["dog_id"] for r in f517["records"] if r.get("same_dog_as")})
    if "DS03" in by:
        f03 = json.loads((TIDY / "DS03.features.json").read_text(encoding="utf-8"))
        dup += len({r["dog_id"] for r in f03["records"] if r.get("same_dog_as")})
    if "DS04" in by:
        c04 = json.loads((OUT / "checks" / "DS04.json").read_text(encoding="utf-8"))
        # Three fatal DS04 dogs are S-CB050 cases 126, 127 and 131 (matched by value; DS04 checks file).
        linked = [c for c in c04["checks"] if "S-CB050" in c["name"] and c["pass"]]
        dup += 3 if linked else 0
    distinct = dog_records - dup

    # 4. CSVs
    with open(OUT / "coverage.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["harmonised_name"] + present)
        for n in HARMONISED:
            w.writerow([n] + ["" if coverage.get((n, ds)) is None else coverage[(n, ds)] for ds in present])
    with open(OUT / "datasets.csv", "w", newline="", encoding="utf-8") as fh:
        keys = ["dataset", "independent_source", "species", "dogs", "infected", "control", "comparator", "records",
                "variables", "harmonised_variables", "missing_pct", "censored_cells", "checks_passed", "checks_total", "flags"]
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(datasets)

    comparison = None
    if "S-CB517" in by:
        c517 = json.loads((OUT / "checks" / "S-CB517.json").read_text(encoding="utf-8"))
        comparison = {k: v for k, v in (c517.get("scb050_comparison") or {}).items() if k != "per_row"} or None

    n_checks = len(checks_all)
    n_pass = sum(1 for c in checks_all if c["pass"])
    harmonised_used = sorted({n for (n, _ds) in coverage}, key=list(HARMONISED).index)
    summary = {
        "code": CODE, "datasets": datasets, "coverage": [{"name": n, "dataset": ds, "share": v} for (n, ds), v in coverage.items()],
        "harmonised_names": list(HARMONISED), "harmonised_used": harmonised_used,
        "checks": checks_all, "flags": flags, "links": [{"a": a, "b": b, "what": w} for a, b, w in LINKS if a in by and b in by],
        "scb050_scb517_comparison": comparison, "dog_records": dog_records, "distinct_dogs_after_links": distinct,
        "feature_records": total_records, "independent_sources": sorted(sources), "missing_datasets": missing,
        "dictionary_rows": len(rows),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    if final:
        write_load_file(summary)
    print(f"{len(present)} datasets, {dog_records} dog records ({distinct} after known links), {total_records} feature records, "
          f"{len(rows)} dictionary rows, checks {n_pass}/{n_checks}, flags {len(flags)}")


def write_load_file(s):
    script = Path(__file__).resolve()
    ds = s["datasets"]
    n_checks = len(s["checks"])
    n_pass = sum(1 for c in s["checks"] if c["pass"])
    failed = [c for c in s["checks"] if not c["pass"]]
    n_vars = len({r["harmonised_name"] for r in csv.DictReader(open(SHARED / "dictionary.csv", encoding="utf-8"))})
    run_utc = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    cov_matrix = {
        "datasets": [d["dataset"] for d in ds],
        "names": s["harmonised_names"],
        "share": [[next((c["share"] for c in s["coverage"] if c["name"] == n and c["dataset"] == d["dataset"]), None)
                   for d in ds] for n in s["harmonised_names"]],
    }
    cmp_ = s["scb050_scb517_comparison"]
    def para_cmp():
        if not cmp_:
            return "The S-CB517 against S-CB050 comparison was not stored."
        return "S-CB517 against S-CB050 (same dogs): " + json.dumps(cmp_.get("summary", cmp_), ensure_ascii=False)[:600]
    summary_text = (f"{len(ds)} datasets tidied from {len(s['independent_sources'])} independent sources: {s['dog_records']} dog records "
                    f"({s['distinct_dogs_after_links']} after the known same-dog links), {s['feature_records']} feature records, "
                    f"{s['dictionary_rows']} dictionary rows. Data checks: {n_checks}, passed {n_pass}.")
    interpretation = {"sections": [
        {"heading": "Question", "paragraphs": [
            "What does the shared data layer hold: which datasets, how many dogs, which variables, how complete, and which cleaning "
            "decisions and flags a later package must know? SV-G1 runs no statistical test; it records counts, coverage and checks."]},
        {"heading": "What was done", "paragraphs": [
            f"Each raw file was read with a script of its own (Python 3.12, standard library) and written as a features file and an "
            f"outcomes file in the contract of rules.md. Severity labels and label proxies are only in the outcomes files; dog IDs are "
            f"neutral (a salted hash order). Units were converted to one unit per harmonised name; {s['dictionary_rows']} rows in "
            f"shared/dictionary.csv record every column and conversion.",
            "Each dataset was checked against its row counts in data.md and against published summary numbers from its article note "
            "or the authors' own summary rows. Values were never corrected silently: suspect values are kept and flagged."]},
        {"heading": "Result", "paragraphs": [
            summary_text,
            "Per dataset: " + "; ".join(f"{d['dataset']} {d['dogs']} dogs, {d['variables']} variables, {d['missing_pct']}% cells missing, "
                                        f"checks {d['checks_passed']}/{d['checks_total']}" for d in ds) + ".",
            ("Failed checks: " + "; ".join(f"{c['dataset']}: {c['check']} (observed {c['observed']}, expected {c['expected']})" for c in failed)
             + ".") if failed else "Every check passed.",
            f"{len(s['flags'])} values are flagged as probable entry errors or contradictions and kept as reported.",
            "Same-dog links: " + "; ".join(f"{l['a']} with {l['b']}: {l['what']}" for l in s["links"]) + ".",
            para_cmp()]},
        {"heading": "What this does not show", "paragraphs": [
            "Coverage is the share of dogs with at least one value; it says nothing about quality or comparability across files. "
            "Raw cytokine values from different files are different assay runs and must not be pooled. Species is aliased with source. "
            "No association with severity was computed here."]},
    ]}
    payload_dataset_rows = [{k: d[k] for k in ("dataset", "independent_source", "species", "dogs", "infected", "control", "comparator",
                                                "records", "timepoints", "variables", "harmonised_variables", "missing_pct",
                                                "censored_cells", "outcomes", "checks_passed", "checks_total", "flags")} for d in ds]
    load = {
        "experiment": {
            "code": CODE,
            "name": "Shared data layer: datasets, dogs, variables and coverage of the tidy files (SV-G1)",
            "description": "What do the tidy features and outcomes files of the severity programme hold, and how complete are they? "
                           "A descriptive record with no hypothesis: counts, variable coverage, missingness, checks and cleaning flags.",
            "method": "data_layer_coverage",
            "dataset": None,
            "parameters": {"package": "SV-G1", "role": "descriptive", "datasets": [d["dataset"] for d in ds],
                           "independent_sources": s["independent_sources"], "spec_sha256": None,
                           "seed": None, "id_salt": "SV-G1-2026-11-12",
                           "inputs": [i["file"] + " sha256 " + i["sha256"][:12] for d in ds for i in d["inputs"]]},
            "script": "/experiments/SV-G1/scripts/summarise.py",
            "script_version": sha(script)[:12],
            "run_utc": run_utc,
            "n_subjects": s["distinct_dogs_after_links"], "n_variables": n_vars, "n_tests": n_checks,
            "summary": summary_text,
        },
        "associations": [], "cluster_assignments": [],
        "results": [
            {"kind": "dataset_summary", "title": "Datasets in the data layer", "sort_order": 1,
             "payload": {"rows": payload_dataset_rows, "dog_records": s["dog_records"],
                         "distinct_dogs_after_links": s["distinct_dogs_after_links"],
                         "independent_sources": s["independent_sources"], "feature_records": s["feature_records"],
                         "checks_total": n_checks, "checks_passed": n_pass}},
            {"kind": "coverage_matrix", "title": "Coverage of the harmonised variables", "sort_order": 2, "payload": cov_matrix},
            {"kind": "data_checks", "title": "Checks against data.md and published numbers", "sort_order": 3,
             "payload": {"rows": [{**c, "observed": json.dumps(c["observed"], ensure_ascii=False),
                                   "expected": json.dumps(c["expected"], ensure_ascii=False)} for c in s["checks"]]}},
            {"kind": "cleaning_flags", "title": "Flagged values (kept as reported)", "sort_order": 4, "payload": {"rows": s["flags"]}},
            {"kind": "dataset_links", "title": "Files that share dogs", "sort_order": 5,
             "payload": {"rows": s["links"], "scb050_scb517_comparison": cmp_}},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interpretation},
        ],
    }
    text = json.dumps(load, indent=1, ensure_ascii=False, allow_nan=False)
    if len(text.encode("utf-8")) > 1_000_000:
        raise SystemExit("load file above 1 MB")
    (OUT / "db").mkdir(parents=True, exist_ok=True)
    (OUT / "db" / f"{CODE}.json").write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(final="--partial" not in sys.argv)
