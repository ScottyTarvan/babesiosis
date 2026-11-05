"""Build the clinical-syndrome-plus-treatment re-screen set and its batches.

Takes the excluded records of screening rounds r1-r4 (and the extraction-stage exclusions
and unresolved records) that may describe clinical babesiosis and its treatment, and writes

  search/clinical_treatment/candidates.jsonl           one row per record, with the original decision
  search/clinical_treatment/screen_batches/ct_NN.md    title/abstract batches for the screeners
  search/clinical_treatment/screen_batches/batches.json

Selection: every record excluded as treatment_efficacy or other_out_of_scope; every other
exclusion (except not_canine_babesia, vector_tick, not_research, out_of_window) whose title or
rationale mentions treatment; and extraction-stage exclude_fulltext / unverifiable records whose
title or decision reason mentions treatment.

Usage (from core/):
    python -I scripts/build_clinical_rescreen.py [--size 40]
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search" / "clinical_treatment"
TX = re.compile(r"treat|therap|imidocarb|diminazene|atovaquone|azithromycin|clindamycin|doxycycline|"
                r"transfus|manag|dialysis|plasmapheresis|infusion", re.I)
SKIP_REASONS = {"not_canine_babesia", "vector_tick", "not_research", "out_of_window"}
SCREEN_FILES = [("r1", "search/screening_r1.jsonl"), ("r2", "search/screening_r2.jsonl"),
                ("r3", "search/screening_r3.jsonl"), ("r4", "search/r4/screening.jsonl")]
CAND_FILES = ["search/candidates.jsonl", "search/candidates_r2.jsonl", "search/candidates_r3.jsonl",
              "search/candidates_round2_all.jsonl", "search/candidates_crossref.jsonl",
              "search/candidates_openalex.jsonl", "search/r4/candidates_all.jsonl", "search/r4/candidates.jsonl",
              "search/r4/candidates_r2.jsonl", "search/r4/candidates_r3.jsonl",
              "search/r4/candidates_crossref.jsonl", "search/r4/candidates_openalex.jsonl"]


def load(p):
    p = ROOT / p
    if not p.exists():
        return []
    return [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]


def cand_index():
    idx = {}
    for f in CAND_FILES:
        for r in load(f):
            keys = [r.get("key")]
            if r.get("pmid"):
                keys.append("PMID:" + str(r["pmid"]))
            if r.get("doi"):
                keys.append("DOI:" + str(r["doi"]).lower())
            for k in keys:
                if k and k not in idx:
                    idx[k] = r
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=40)
    a = ap.parse_args()
    idx = cand_index()
    ids = json.load((ROOT / "ids.json").open(encoding="utf-8"))
    key_to_id = {k: v["id"] for k, v in ids.items()}
    rows, seen = [], set()
    for rnd, f in SCREEN_FILES:
        for r in load(f):
            if r["decision"] != "exclude":
                continue
            reason = r.get("exclude_reason")
            c = idx.get(r["key"]) or {}
            blob = (c.get("title") or "") + " " + (r.get("rationale") or "")
            if reason in ("treatment_efficacy", "other_out_of_scope"):
                why = reason
            elif reason not in SKIP_REASONS and TX.search(blob):
                why = f"{reason} (treatment term)"
            else:
                continue
            if r["key"] in seen:
                continue
            seen.add(r["key"])
            rows.append({"key": r["key"], "stage": "screen", "round": rnd, "original_decision": "exclude",
                         "original_reason": reason, "original_rationale": r.get("rationale"), "selected_because": why,
                         "article_id": key_to_id.get(r["key"]), "title": c.get("title"), "abstract": c.get("abstract"),
                         "journal": c.get("journal"), "first_pub_date": c.get("first_pub_date"),
                         "doi": c.get("doi"), "pmid": c.get("pmid"), "type": c.get("type") or c.get("publication_types"),
                         "language": c.get("language")})
    # extraction-stage exclusions and unresolved records
    for r in load("search/extraction_records.jsonl"):
        if r.get("final_decision") not in ("exclude_fulltext", "unverifiable"):
            continue
        blob = (r.get("title") or "") + " " + (r.get("decision_reason") or "") + " " + (r.get("design") or "")
        if not TX.search(blob):
            continue
        key = r.get("key") or (f"PMID:{r['pmid']}" if r.get("pmid") else f"DOI:{(r.get('doi') or '').lower()}")
        if key in seen:
            continue
        seen.add(key)
        c = idx.get(key) or {}
        packet = ROOT / "search" / "packets" / f"{r['id']}.json"
        abstract = c.get("abstract")
        if not abstract and packet.exists():
            abstract = json.load(packet.open(encoding="utf-8")).get("abstract")
        rows.append({"key": key, "stage": "extraction", "round": None, "original_decision": r["final_decision"],
                     "original_reason": r["final_decision"], "original_rationale": r.get("decision_reason"),
                     "selected_because": f"{r['final_decision']} (treatment term)", "article_id": r["id"],
                     "title": r.get("title"), "abstract": abstract, "journal": r.get("journal"),
                     "first_pub_date": r.get("first_pub_date"), "doi": r.get("doi"), "pmid": r.get("pmid"),
                     "type": None, "language": r.get("language")})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "screen_batches").mkdir(exist_ok=True)
    with (OUT / "candidates.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    batches = {}
    for i in range(0, len(rows), a.size):
        name = f"ct_{i // a.size + 1:02d}.md"
        chunk = rows[i:i + a.size]
        lines = [f"# Re-screen batch {name} ({len(chunk)} records)\n"]
        for c in chunk:
            lines.append(f"### {c['key']}")
            lines.append(f"Title: {c.get('title') or '?'}")
            meta = [f"Journal: {c.get('journal') or '?'}", f"First pub: {c.get('first_pub_date') or '?'}",
                    f"DOI: {c.get('doi') or 'No'}", f"Original exclusion: {c['original_reason']}"]
            lines.append(" | ".join(meta))
            lines.append(f"Original rationale: {c.get('original_rationale') or ''}")
            lines.append(f"Abstract: {c.get('abstract') or '(none available)'}")
            lines.append("")
        (OUT / "screen_batches" / name).write_text("\n".join(lines), encoding="utf-8")
        batches[name] = [c["key"] for c in chunk]
    (OUT / "screen_batches" / "batches.json").write_text(json.dumps(batches, indent=1), encoding="utf-8")
    import collections
    print(len(rows), "records;", len(batches), "batches")
    print(collections.Counter(r["selected_because"] for r in rows).most_common())
    print("with abstract:", sum(1 for r in rows if r.get("abstract")))


if __name__ == "__main__":
    main()
