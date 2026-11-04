"""Assemble a later round's screening decisions from the screening workflow's journal.

The workflow (three tiers per batch, as in rounds 1-3: first screener, liberal second
screener on every exclusion, senior adjudicator on rescued and uncertain records) records
each agent's structured result in its journal.jsonl. Agents are labelled screen:<batch>,
screen-rest:<batch> (a retry for records the first screener missed), rescue:<batch> and
adjudicate:<batch>. This script combines them the same way the workflow did:

  - a record the adjudicator decided gets stage "adjudicated", first_decision and, when the
    second screener rescued it, rescue_reason;
  - every other record keeps the first screener's decision with stage "screen".

Every key is checked against search/<round>/screen_batches/batches.json; keys that are
missing, duplicated or unknown are printed and missing ones are not written.

Writes search/<round>/screening.jsonl (fields as search/screening_r*.jsonl).

Usage (from canine-babesiosis-review/):
    python -I scripts/assemble_screening.py --round r4 --journal <workflow transcript dir>/journal.jsonl
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import round_dir  # noqa: E402

FIELDS = ("key", "decision", "include_type", "exclude_reason", "primary_category", "secondary_tags",
          "species", "rationale", "stage", "batch")


def results_by_label(journal):
    """label -> structured result of the last completed agent with that label."""
    labels, out = {}, {}
    for l in open(journal, encoding="utf-8"):
        if not l.strip():
            continue
        e = json.loads(l)
        if e.get("label") and e.get("key"):
            labels[e["key"]] = e["label"]
        res = next((e[k] for k in ("result", "value", "output") if isinstance(e.get(k), dict)), None)
        if res is not None and "records" in res:
            lab = e.get("label") or labels.get(e.get("key"))
            if lab:
                out[lab] = res["records"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", required=True)
    ap.add_argument("--journal", required=True, type=Path)
    args = ap.parse_args()
    d = round_dir(args.round)
    batches = json.loads((d / "screen_batches" / "batches.json").read_text(encoding="utf-8"))
    res = results_by_label(args.journal)
    rows, problems = [], []
    for b, keys in batches.items():
        first = {}
        for r in res.get(f"screen:{b}", []) + res.get(f"screen-rest:{b}", []):
            first.setdefault(r["key"], r)
        resc = {r["key"]: r["reason"] for r in res.get(f"rescue:{b}", []) if r.get("rescue")}
        final = {r["key"]: r for r in res.get(f"adjudicate:{b}", [])}
        unknown = sorted(set(first) - set(keys))
        if unknown:
            problems.append(f"{b}: unknown keys {unknown}")
        for k in keys:
            r = first.get(k)
            if r is None:
                problems.append(f"{b}: no decision for {k}")
                continue
            # The workflow sent only uncertain and rescued records to the adjudicator.
            f = final.get(k) if (r["decision"] == "uncertain" or k in resc) else None
            if f:
                row = {**{x: f.get(x) for x in FIELDS}, "key": k, "stage": "adjudicated", "batch": b,
                       "first_decision": r["decision"]}
                if k in resc:
                    row["rescue_reason"] = resc[k]
            else:
                row = {**{x: r.get(x) for x in FIELDS}, "stage": "screen", "batch": b}
            rows.append(row)
    dup = [k for k, n in Counter(r["key"] for r in rows).items() if n > 1]
    if dup:
        problems.append(f"duplicate keys {dup}")
    with open(d / "screening.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"rows={len(rows)} of {sum(len(v) for v in batches.values())}",
          dict(Counter(r["decision"] for r in rows)), dict(Counter(r["stage"] for r in rows)))
    print("exclude reasons", dict(Counter(r["exclude_reason"] for r in rows if r["decision"] == "exclude")))
    for p in problems:
        print("PROBLEM", p)


if __name__ == "__main__":
    main()
