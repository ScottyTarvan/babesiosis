"""Build or update the curated term display map, data/terms/term_display.csv.

Reads every data/terms/<ID>.json (written by extract_terms.py) and ranks the UMLS concepts (CUIs) by the number of
CB articles with at least one affirmed mention. Writes one row per CUI:

    cui, concept, articles, action, display_name, note

- action: "show" or "hide". New rows default to "show".
- display_name: merges several CUIs under one label in the dashboard; blank = use concept.
- note: why a row was hidden, merged or renamed.

The file is meant for editing by hand. On a re-run, existing rows keep their action, display_name and note; only
concept and articles are refreshed. Rows whose CUI no longer appears in any term file are kept with articles = 0
when they carry a manual edit (action "hide", a display_name or a note) and dropped otherwise.

The Babesiosis.Console loader reads this file: hidden terms are flagged in dbo.term and left out of the dashboard.

Usage (from core/):
    python -I scripts/build_term_display.py
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TERMS = ROOT / "data" / "terms"
OUT = TERMS / "term_display.csv"
FIELDS = ["cui", "concept", "articles", "action", "display_name", "note"]
ACTIONS = {"show", "hide"}


def count_terms():
    """CB article count (affirmed mentions only) and preferred name per CUI, over all term files."""
    articles, concepts = Counter(), {}
    files = sorted(TERMS.glob("*.json"))
    for path in files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        is_canine = str(doc.get("id", path.stem)).upper().startswith("CB")
        for term in doc.get("terms", []):
            cui = term["term"]
            concepts.setdefault(cui, term.get("concept") or cui)
            if is_canine and term.get("mentions_affirmed", 0) > 0:
                articles[cui] += 1
    return files, articles, concepts


def read_existing():
    if not OUT.exists():
        return {}
    with open(OUT, encoding="utf-8", newline="") as fh:
        return {row["cui"]: row for row in csv.DictReader(fh) if row.get("cui")}


def is_manual(row):
    return row.get("action", "show") != "show" or bool(row.get("display_name")) or bool(row.get("note"))


def main():
    files, articles, concepts = count_terms()
    if not files:
        sys.exit(f"No term files in {TERMS}. Run extract_terms.py first.")

    old = read_existing()
    rows, problems = [], []

    for cui, concept in concepts.items():
        prev = old.get(cui, {})
        action = (prev.get("action") or "show").strip().lower()
        if action not in ACTIONS:
            problems.append(f"{cui}: unknown action '{prev.get('action')}', kept as written")
            action = prev.get("action")
        rows.append({
            "cui": cui,
            "concept": concept,
            "articles": articles.get(cui, 0),
            "action": action,
            "display_name": (prev.get("display_name") or "").strip(),
            "note": (prev.get("note") or "").strip(),
        })

    dropped = 0
    for cui, prev in old.items():
        if cui in concepts:
            continue
        if is_manual(prev):
            rows.append({**{f: prev.get(f, "") for f in FIELDS}, "articles": 0})
            problems.append(f"{cui} ({prev.get('concept')}): manual row kept, but no term file lists it")
        else:
            dropped += 1

    rows.sort(key=lambda r: (-int(r["articles"]), r["concept"].lower(), r["cui"]))

    with open(OUT, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    manual = sum(1 for r in rows if is_manual(r))
    hidden = sum(1 for r in rows if r["action"] == "hide")
    merged = Counter(r["display_name"] for r in rows if r["display_name"])
    print(f"Term files read:      {len(files)}")
    print(f"Terms (CUIs):         {len(rows)}  (new {sum(1 for r in rows if r['cui'] not in old)}, dropped {dropped})")
    print(f"Manual rows kept:     {manual}  (hidden {hidden}, display names {sum(merged.values())} on {len(merged)} labels)")
    print(f"Written:              {OUT.relative_to(ROOT).as_posix()}")
    for line in problems:
        print(f"  - {line}")


if __name__ == "__main__":
    main()
