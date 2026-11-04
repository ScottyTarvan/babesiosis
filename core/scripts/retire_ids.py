"""Retire the IDs of extracted articles that were not included.

For each record in search/extraction_records.jsonl whose final_decision is exclude_fulltext or
unverifiable, sets "retired": true and "retired_reason": "<decision>: <decision_reason>" on its entry in
ids.json, in the format of the existing retired entries (the reason is cut to 300 characters, as in
rounds 1-3). IDs stay in ids.json, so numbers are never reused. Entries already retired are left as they
are. Without --ids, every such record is checked, so the script is safe to re-run.

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/retire_ids.py
    python -I scripts/retire_ids.py --ids CB327 CB443
    python -I scripts/retire_ids.py --dry-run
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RETIRE = ("exclude_fulltext", "unverifiable")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*", help="only these article IDs")
    ap.add_argument("--dry-run", action="store_true", help="print the changes without writing ids.json")
    a = ap.parse_args()
    reg_path = ROOT / "ids.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    by_id = {v["id"]: v for v in reg.values() if not v.get("source_key")}  # RETIRED:<BG> aliases have source_key
    recs = [json.loads(l) for l in open(ROOT / "search" / "extraction_records.jsonl", encoding="utf-8") if l.strip()]
    changed, missing = [], []
    for r in recs:
        if r.get("final_decision") not in RETIRE or (a.ids and r["id"] not in a.ids):
            continue
        v = by_id.get(r["id"])
        if v is None:
            missing.append(r["id"])
            continue
        if v.get("retired"):
            continue
        v["retired"] = True
        v["retired_reason"] = f"{r['final_decision']}: {(r.get('decision_reason') or '').strip()[:300]}"
        changed.append(r["id"])
    for rid in changed:
        print(f"retired {rid}: {by_id[rid]['retired_reason'][:100]}")
    if missing:
        print("not in ids.json:", " ".join(missing))
    if changed and not a.dry_run:
        reg_path.write_text(json.dumps(reg, indent=1, ensure_ascii=False), encoding="utf-8")  # as assign_ids.py
    print(f"{len(changed)} retired{' (dry run)' if a.dry_run else ''}; {len(missing)} not found")


if __name__ == "__main__":
    main()
