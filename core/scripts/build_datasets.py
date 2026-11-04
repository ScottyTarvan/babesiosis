"""Assemble datasets.jsonl and search/dataset_negative_checks.jsonl.

Sources:
  search/dataset_assessments.json   agent assessments of downloaded datasets (status 1)
  search/dataset_extra.json         curated records: summary-only supplements, public records
                                    awaiting retrieval (status 2) and sequence-only resources
  search/extraction_records.jsonl   per-article dataset leads (request-only -> status 3;
                                    no lead -> status 4 if full text/publisher page checked, else 5);
                                    retired IDs (ids.json) are skipped
  search/r4/fulltext_checks.jsonl   check dates, used as verification_date for round-4 records
  data/manifest.jsonl               files actually downloaded (sizes, checksums)

Usage:
    python -I scripts/build_datasets.py
"""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "search"
# Verification date of the round 1-3 records; records from later rounds carry their own verification_date.
DEFAULT_VERIFICATION_DATE = "2026-10-23"
STATUS = {1: "Public download verified", 2: "Public record verified; file retrieval unverified",
          3: "Request-only or controlled access", 4: "Not located after documented checks",
          5: "Not assessed/access blocked"}


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def main():
    manifest = defaultdict(list)
    for m in jl(ROOT / "data" / "manifest.jsonl"):
        manifest[m["dataset_id"]].append(m)
    recs = {r["id"]: r for r in jl(S / "extraction_records.jsonl")}
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    retired = {v["id"] for v in reg.values() if v.get("retired")}
    # Round-4 records have no verification_date; their full-text check date stands in.
    checked_on = {reg[c["key"]]["id"]: c["checked"] for c in jl(S / "r4" / "fulltext_checks.jsonl") if c["key"] in reg}
    included = {i for i, r in recs.items() if r["final_decision"] == "include" and i.startswith("CB") and i not in retired}
    out = []
    for a in json.loads((S / "dataset_assessments.json").read_text(encoding="utf-8")):
        parts = [("S-CB106", ["CB106"]), ("S-CB148", ["CB148"])] if a["dataset_id"] == "S-CB106-CB148" else [(a["dataset_id"], a["corresponds_to_articles"])]
        for did, arts in parts:
            folders = [did] + (["S-CB019"] if did == "DS09" else [])
            files = [{"file": m["file"], "bytes": m["bytes"], "sha256": m["sha256"], "url": m["url"], "retrieved_utc": m["retrieved_utc"]}
                     for f in folders for m in manifest.get(f, [])]
            rec = {k: a.get(k) for k in a if k not in ("dataset_id", "corresponds_to_articles")}
            rec.update({"dataset_id": did, "linked_articles": [x for x in arts if x in included],
                        "status": STATUS[a["status_code"]], "downloaded_files": files,
                        "verification_date": a.get("verification_date") or DEFAULT_VERIFICATION_DATE})
            if a["dataset_id"] == "S-CB106-CB148":
                rec["note"] = "Assessed jointly with the other PDF supplement in one agent run; fields may mix both — see correspondence_evidence."
            out.append(rec)
    extra = json.loads((S / "dataset_extra.json").read_text(encoding="utf-8"))
    for e in extra:
        files = [{"file": m["file"], "bytes": m["bytes"], "sha256": m["sha256"], "url": m["url"], "retrieved_utc": m["retrieved_utc"]}
                 for m in manifest.get(e["dataset_id"], [])]
        rec = dict(e, status=STATUS[e["status_code"]], downloaded_files=files, verification_date=e.get("verification_date") or DEFAULT_VERIFICATION_DATE)
        rec["linked_articles"] = [x for x in e.get("linked_articles", []) if x in included]
        out.append(rec)
    linked = defaultdict(list)
    for d in out:
        for a in d["linked_articles"]:
            linked[a].append(d["dataset_id"])
    neg = []
    for i in sorted(included):
        r = recs[i]
        req = [d for d in r["dataset_leads"] if d["kind"] == "request_only"]
        if req and i not in linked:
            did = f"RQ-{i}"
            out.append({"dataset_id": did, "title": f"Data stated available on request ({i})", "linked_articles": [i],
                        "repository": None, "accession_or_doi": None, "landing_url": None, "direct_download_urls": [],
                        "licence": "not specified", "status_code": 3, "status": STATUS[3],
                        "granularity": [d["likely_granularity"] for d in req], "raw_vs_processed": None,
                        "n_animals": r.get("n_infected_dogs"), "n_animals_basis": "article-reported infected dogs; data not seen",
                        "statement": " ".join(d["description"] for d in req), "downloaded_files": [],
                        "verification_date": r.get("verification_date") or checked_on.get(i) or DEFAULT_VERIFICATION_DATE,
                        "unverified_fields": ["all data fields (not retrieved; authors not contacted)"]})
            linked[i].append(did)
        if i in linked:
            continue
        checked = r.get("fulltext_checked") or r.get("supplement_checked") or r.get("repository_checked")
        basis = "; ".join(d["description"] for d in r["dataset_leads"])[:400] or None
        neg.append({"article_id": i, "status_code": 4 if checked else 5,
                    "basis": basis or ("full text/publisher page checked; no dataset found" if checked else "full text not accessible"),
                    "data_availability_statement": r.get("data_availability_statement")})
    with open(ROOT / "datasets.jsonl", "w", encoding="utf-8") as f:
        for d in out:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    with open(S / "dataset_negative_checks.jsonl", "w", encoding="utf-8") as f:
        for n in neg:
            f.write(json.dumps(n, ensure_ascii=False) + "\n")
    from collections import Counter
    print("datasets", len(out), Counter(d["status_code"] for d in out), "negative", Counter(n["status_code"] for n in neg))


if __name__ == "__main__":
    main()
