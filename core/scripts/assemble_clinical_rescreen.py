"""Merge the clinical-syndrome-plus-treatment re-screen results.

Reads search/clinical_treatment/results/ct_NN.json (one JSON array per batch, written by the
screening agents) and optional adjudications in search/clinical_treatment/adjudications.jsonl
(adjudications*.jsonl, same fields; overrides the batch decision by key). Checks that every candidate was screened
once and that the codes are valid, then writes

  search/clinical_treatment/screening.jsonl   one row per candidate: candidate metadata + decision
  search/clinical_treatment/included.csv      the includes and uncertains, for reading

Usage (from core/):
    python -I scripts/assemble_clinical_rescreen.py
"""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "search" / "clinical_treatment"
INCLUDE_TYPES = {"trial", "retrospective_series", "case_series", "case_report", "experimental", "review"}
EXCLUDE_REASONS = {"no_dog_clinical_data", "prevention_only", "pharmacology_healthy", "no_treatment", "no_syndrome",
                   "babesia_incidental", "not_peer_reviewed", "not_research"}
FIELDS = ["decision", "include_type", "exclude_reason", "syndromes", "treatments", "outcome_reported", "species",
          "coinfection", "n_dogs", "rationale"]


def main():
    cands = [json.loads(l) for l in (D / "candidates.jsonl").open(encoding="utf-8") if l.strip()]
    results, problems = {}, []
    for f in sorted((D / "results").glob("ct_*.json")):
        try:
            arr = json.loads(f.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as e:
            problems.append(f"{f.name}: invalid JSON ({e})")
            continue
        for r in arr:
            k = r.get("key")
            if k in results:
                problems.append(f"{f.name}: duplicate key {k}")
            r["batch"] = f.name
            r["stage"] = "screen"
            results[k] = r
    for adj in sorted(D.glob("adjudications*.jsonl")):
        for l in adj.open(encoding="utf-8-sig"):
            if l.strip():
                r = json.loads(l)
                r["stage"] = "adjudicated"
                r.setdefault("batch", results.get(r["key"], {}).get("batch"))
                results[r["key"]] = r
    out, missing = [], []
    for c in cands:
        r = results.get(c["key"])
        if not r:
            missing.append(c["key"])
            continue
        d = r.get("decision")
        if d not in ("include", "exclude", "uncertain"):
            problems.append(f"{c['key']}: bad decision {d!r}")
        if d == "include" and r.get("include_type") not in INCLUDE_TYPES:
            problems.append(f"{c['key']}: bad include_type {r.get('include_type')!r}")
        if d == "exclude" and r.get("exclude_reason") not in EXCLUDE_REASONS:
            problems.append(f"{c['key']}: bad exclude_reason {r.get('exclude_reason')!r}")
        row = dict(c)
        row.pop("abstract", None)
        for k in FIELDS:
            row[k] = r.get(k)
        row["stage"] = r.get("stage")
        row["batch"] = r.get("batch")
        out.append(row)
    extra = set(results) - {c["key"] for c in cands}
    with (D / "screening.jsonl").open("w", encoding="utf-8") as f:
        for row in out:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    cols = ["key", "article_id", "decision", "include_type", "exclude_reason", "first_pub_date", "title", "journal",
            "doi", "pmid", "species", "coinfection", "n_dogs", "syndromes", "treatments", "outcome_reported",
            "original_reason", "rationale", "stage"]
    with (D / "included.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for row in sorted(out, key=lambda x: (x["decision"] != "include", str(x.get("first_pub_date") or ""))):
            if row["decision"] in ("include", "uncertain"):
                r2 = dict(row)
                r2["syndromes"] = "; ".join(row.get("syndromes") or [])
                r2["treatments"] = "; ".join(row.get("treatments") or [])
                w.writerow(r2)
    print(f"candidates {len(cands)}; screened {len(out)}; missing {len(missing)}; unexpected keys {len(extra)}")
    for m in missing[:20]:
        print("  missing:", m)
    for e in list(extra)[:20]:
        print("  unexpected:", e)
    for p in problems[:40]:
        print("  problem:", p)
    print("decisions:", collections.Counter(r["decision"] for r in out).most_common())
    print("include_type:", collections.Counter(r["include_type"] for r in out if r["decision"] == "include").most_common())
    print("exclude_reason:", collections.Counter(r["exclude_reason"] for r in out if r["decision"] == "exclude").most_common())
    print("by original reason (include / uncertain / exclude):")
    byr = collections.defaultdict(collections.Counter)
    for r in out:
        byr[r["original_reason"]][r["decision"]] += 1
    for k, v in sorted(byr.items(), key=lambda x: -sum(x[1].values())):
        print(f"  {k}: {v['include']} / {v['uncertain']} / {v['exclude']}")


if __name__ == "__main__":
    main()
