"""Write the title/abstract screening batches for one later round.

Reads search/<round>/candidates_all.jsonl and writes search/<round>/screen_batches/<round>_NN.md
(40 records each, in the format of search/screen_batches/r1_*.md - r3_*.md) and
search/<round>/screen_batches/batches.json ({batch file: [keys]}), the work list for the
screening workflow. Records that already have an article ID say so, and Crossref date
spreads and unresolved citation records are shown, so the screeners can check them.

Usage (from canine-babesiosis-review/):
    python -I scripts/build_screen_batches.py --round r4 [--size 40]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import round_dir  # noqa: E402


def block(c):
    meta = [f"Journal: {c.get('journal') or '?'}",
            f"First pub: {c.get('first_pub_date') or c.get('year') or '?'}"]
    if c.get("publication_types"):
        meta.append("Types: " + ", ".join(c["publication_types"]))
    elif c.get("type"):
        meta.append(f"Type: {c['type']}")
    if c.get("language"):
        meta.append("Lang: " + ", ".join(x for x in c["language"] if x))
    meta.append(f"Src: {c.get('src') or 'MED'}")
    meta.append(f"DOI: {c['doi']}" if c.get("doi") else "DOI: No")
    if c.get("found_by"):
        meta.append("Found by: " + ", ".join(c["found_by"][:4]) + (" ..." if len(c["found_by"]) > 4 else ""))
    lines = [f"### {c['key']}", f"Title: {c.get('title') or '?'}", " | ".join(meta)]
    notes = []
    if c.get("existing_id"):
        notes.append(f"already in the review as {c['existing_id']}" + (" (retired ID)" if c.get("existing_retired") else ""))
    if c.get("online_vs_issue"):
        notes.append(f"dates: {c['online_vs_issue']}")
    if c.get("crossref_dates"):
        notes.append("Crossref dates: " + ", ".join(f"{k} {v}" for k, v in c["crossref_dates"].items()))
    if c.get("date_spread"):
        notes.append("Crossref dates span more than a year: check the original publication date")
    if c.get("unresolved"):
        notes.append("reference-list entry; not resolved to a published record")
    if notes:
        lines.append("Notes: " + "; ".join(notes))
    if c.get("mesh"):
        lines.append("MeSH: " + "; ".join(c["mesh"]))
    src = c.get("abstract_source")
    lines.append((f"Abstract ({src}): " if src else "Abstract: ") + (c.get("abstract") or "none available"))
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    ap.add_argument("--size", type=int, default=40)
    args = ap.parse_args()
    d = round_dir(args.round)
    cands = [json.loads(l) for l in open(d / "candidates_all.jsonl", encoding="utf-8") if l.strip()]
    out = d / "screen_batches"
    out.mkdir(exist_ok=True)
    manifest = {}
    for i in range(0, len(cands), args.size):
        chunk = cands[i:i + args.size]
        name = f"{args.round}_{i // args.size + 1:02d}.md"
        (out / name).write_text("\n".join(block(c) for c in chunk), encoding="utf-8")
        manifest[name] = [c["key"] for c in chunk]
    (out / "batches.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"records={len(cands)} batches={len(manifest)}")


if __name__ == "__main__":
    main()
