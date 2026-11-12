"""Check that every number in out/census_raw.csv is printed at its cited source location.

CSV sources: the cited physical line(s) must contain each numeric field as printed. JSON sources: the pointer must resolve, and
every numeric field of the row must appear in the JSON object that holds the pointer (compared as numbers). Stops on a failure.
"""
import csv
import json
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
EXP = PKG.parent
NUMERIC = ["n", "effect", "ci_low", "ci_high", "p", "q"]

def numbers_in(text):
    return re.findall(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", text)

def jget(obj, pointer):
    parts = pointer.strip("/").split("/")
    parent = obj
    for part in parts:
        parent, obj = obj, (obj[int(part)] if isinstance(obj, list) else obj[part])
    return parent, obj

def flat_numbers(o, acc):
    if isinstance(o, dict):
        for v in o.values(): flat_numbers(v, acc)
    elif isinstance(o, list):
        for v in o: flat_numbers(v, acc)
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        acc.append(float(o))
    return acc

lines_cache, json_cache, fails, checked = {}, {}, [], 0
rows = list(csv.DictReader((PKG / "out" / "census_raw.csv").open(encoding="utf-8")))
for r in rows:
    src = r["source_file"]
    vals = []
    for f in NUMERIC:
        v = r[f].strip()
        if not v:
            continue
        vals += [x for x in numbers_in(v)] if f == "n" or "/" in v or " vs " in v else ([v] if numbers_in(v) else [])
    if src.endswith(".csv"):
        if src not in lines_cache:
            lines_cache[src] = (EXP / src).read_text(encoding="utf-8").splitlines()
        a, _, b = r["source_line"].partition("-")
        text = "\n".join(lines_cache[src][int(a) - 1:int(b or a)])
        for v in vals:
            checked += 1
            if v not in text:
                fails.append(f"{r['row_id']}: {v!r} not on {src}:{r['source_line']}")
    else:
        if src not in json_cache:
            json_cache[src] = json.loads((EXP / src).read_text(encoding="utf-8"))
        try:
            parent, leaf = jget(json_cache[src], r["source_line"])
        except (KeyError, IndexError, ValueError) as e:
            fails.append(f"{r['row_id']}: pointer {r['source_line']} not in {src}"); continue
        pool = flat_numbers(parent, [])
        for v in vals:
            checked += 1
            x = float(v)
            if not any(abs(x - y) <= 1e-9 * max(1, abs(y)) for y in pool):
                fails.append(f"{r['row_id']}: {v!r} not in {src}{r['source_line']} (parent object)")
if fails:
    print("\n".join(fails[:50])); print(f"FAILED: {len(fails)} of {checked} numbers"); sys.exit(1)
print(f"census check: {checked} numbers in {len(rows)} rows found at their cited locations")
