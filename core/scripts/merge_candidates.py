"""Merge one round's candidate files into the screening input for that round.

Reads search/<round>/candidates.jsonl (databases), candidates_r2.jsonl (citations),
candidates_crossref.jsonl and candidates_r3.jsonl (OpenAlex after the type and title
filter), deduplicates by DOI, then PMID, then normalised title (earlier files win; empty
fields are filled from later ones; found_by is merged), and gives every record a `key`
in the assign_ids.py form (PMID:…, else DOI:…, else the source ID).

Writes search/<round>/candidates_all.jsonl and prints counts per source file.

Usage (from canine-babesiosis-review/):
    python -I scripts/merge_candidates.py --round r4
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import _rec_keys, round_dir  # noqa: E402

FILES = ("candidates.jsonl", "candidates_r2.jsonl", "candidates_crossref.jsonl", "candidates_r3.jsonl")


def key_of(x):
    return f"PMID:{x['pmid']}" if x.get("pmid") else (f"DOI:{x['doi']}" if x.get("doi") else x.get("source_id"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    args = ap.parse_args()
    d = round_dir(args.round)
    recs, index = {}, {}
    for fn in FILES:
        p = d / fn
        n = new = 0
        if p.exists():
            for l in open(p, encoding="utf-8"):
                if not l.strip():
                    continue
                r, n = json.loads(l), n + 1
                key = next((index[k] for k in _rec_keys(r) if k in index), None)
                if key is None:
                    key, new = key_of(r), new + 1
                    recs[key] = dict(r, key=key, found_by=[], source_files=[])
                c = recs[key]
                for k, v in r.items():
                    if c.get(k) in (None, [], "") and v not in (None, [], ""):
                        c[k] = v
                c["found_by"] = sorted(set(c["found_by"]) | set(r.get("found_by") or []))
                c["source_files"].append(fn)
                for k in _rec_keys(c):
                    index.setdefault(k, key)
        print(f"{fn}: {n} records, {new} new")
    out = sorted(recs.values(), key=lambda c: (c.get("first_pub_date") or c.get("year") or "", c["key"]))
    with open(d / "candidates_all.jsonl", "w", encoding="utf-8") as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    flagged = sum(1 for c in out if c.get("existing_id"))
    print(f"merged={len(out)} with_existing_id={flagged} no_abstract={sum(1 for c in out if not c.get('abstract'))}")


if __name__ == "__main__":
    main()
