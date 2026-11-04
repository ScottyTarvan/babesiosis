"""Check the extracted marker-severity associations and flatten them into one table.

Input: data/severity/extractions/<ID>.json, one per article, in the shape of data/severity/association_schema.json.

1. Schema. Required fields, allowed values (the enums are read from the schema file), and every severity_key
   pointing at a defined severity definition.
2. Quotes. Each quote (association and severity definition) is looked up in the article's text_used, after
   normalising both (Unicode, dashes, decimal points, Markdown emphasis and table pipes, whitespace, case).
   exact: found as is. near: >= 80% of its 4-word shingles found (formatting differences). partial: >= 50%.
   not_found: below that; treat the row as unverified.
3. Numbers. Every number in statistic, p_value, effect_value, effect_ci, cutoff, sensitivity and specificity
   must occur somewhere in the text (compared as values, so 0.50 = 0.5 and 0,05 = 0.05). Missing numbers are
   listed; they mean a transcription error, a derived value, or a number read from a figure.
4. Markers. marker is kept when it is a canonical name in data/severity/marker_map.csv. Otherwise the alias
   column is looked up (marker_as_reported, then marker), then the canonical patterns in file order. A marker
   still unmapped is added to the map as an alias row with source "extracted" and a blank marker, to fill in
   by hand ("-" drops it).

Outputs (full run): data/severity/associations.csv (one row per association, with the checks),
data/severity/extraction_report.md, and new alias rows in marker_map.csv. With --ids the checks for those
articles are printed and nothing is written (safe to run while other extractions are in progress).

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/check_associations.py [--ids CB040 CB017]
"""
import argparse
import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEV = ROOT / "data" / "severity"
EXTRACT = SEV / "extractions"
MAP = SEV / "marker_map.csv"
SCHEMA = SEV / "association_schema.json"
NUM_FIELDS = ["statistic", "p_value", "effect_value", "effect_ci", "cutoff", "sensitivity", "specificity"]
NUMBER = re.compile(r"(?<![\w.])\d*\.?\d+")
UP = {"higher_in_severe", "more_frequent_in_severe", "positive_association"}
DOWN = {"lower_in_severe", "less_frequent_in_severe", "negative_association"}


def norm_name(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[‐‑‒–—−]", "-", s)
    return s.replace("β", "beta").replace("α", "alpha").replace("γ", "gamma").replace("κ", "kappa")


def fix_commas(s):
    s = re.sub(r"(?<![\d.,])([1-9]\d{0,2})((?:,\d{3})+)(?![\d,])", lambda m: m.group(1) + m.group(2).replace(",", ""), s)  # 63,761.79
    return re.sub(r"(\d),(\d)", r"\1.\2", s)  # decimal commas: 0,05


def norm_text(s):
    s = norm_name(s)
    s = s.replace("·", ".").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = fix_commas(s)
    s = re.sub(r"<br\s*/?>|</?[a-z][a-z0-9]*(\s[^<>]*)?/?>", " ", s)  # real tags only: "p < 0.001 ... > 19" is text
    s = re.sub(r"[*_|\\`#]", " ", s)
    s = re.sub(r"\s*([≤≥<>=±:;,()\[\]/%-])\s*", r"\1", s)  # spacing around symbols varies between converters
    return re.sub(r"\s+", " ", s).strip()


def numbers(s):
    out = set()
    for n in NUMBER.findall(fix_commas(s or "")):
        try:
            out.add(round(float(n), 6))
        except ValueError:
            pass
    return out


def quote_check(quote, doc):
    q = norm_text(quote)
    if not q:
        return "missing"
    if q in doc:
        return "exact"
    words = q.split()
    if len(words) < 4:
        return "not_found"
    shingles = [" ".join(words[i:i + 4]) for i in range(len(words) - 3)]
    frac = sum(s in doc for s in shingles) / len(shingles)
    return "near" if frac >= 0.8 else "partial" if frac >= 0.5 else "not_found"


def schema_rules():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    props = schema["properties"]
    rules = {}
    for part in ("severity_definitions", "associations"):
        items = props[part]["items"]
        enums = {k: set(v["enum"]) for k, v in items["properties"].items() if "enum" in v}
        rules[part] = (items["required"], enums, set(items["properties"]))
    return schema["required"], rules


def load_map():
    with open(MAP, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    canon = {r["marker"]: r["marker_class"] for r in rows if r["pattern"]}
    alias = {r["alias"]: (r["marker"], r["marker_class"]) for r in rows}
    patterns = [(r["marker"], r["marker_class"], r["pattern"]) for r in rows if r["pattern"]]
    return rows, canon, alias, patterns


def map_marker(a, canon, alias, patterns):
    if a.get("marker") in canon:
        return a["marker"], canon[a["marker"]], "canonical"
    for name in (a.get("marker_as_reported"), a.get("marker")):
        hit = alias.get(norm_name(name))
        if hit and hit[0]:
            return (hit[0], hit[1], "dropped") if hit[0] == "-" else (hit[0], canon.get(hit[0], hit[1]), "alias")
    for name in (a.get("marker_as_reported"), a.get("marker")):
        low = norm_name(name)
        for marker, cls, pat in patterns:
            if re.search(pat, low):
                return marker, cls, "pattern"
    return "", "", "unmapped"


def check_article(path, required_top, rules, canon, alias, patterns, articles):
    data = json.loads(path.read_text(encoding="utf-8"))
    aid = data.get("id") or path.stem
    errors = [f"missing {k}" for k in required_top if k not in data]
    text_path = ROOT / data.get("text_used", f"data/markdown/{aid}.md")
    if not text_path.exists():
        errors.append(f"text_used not found: {text_path}")
        doc = ""
    else:
        raw = text_path.read_text(encoding="utf-8")
        raw = re.sub(r"\A---\n.*?\n---\n", "", raw, flags=re.S)
        doc = norm_text(raw)
    doc_numbers = numbers(doc)
    art = articles.get(aid, {})

    def validate(obj, part):
        req, enums, known = rules[part]
        errs = [f"missing {k}" for k in req if obj.get(k) in (None, "")]
        errs += [f"{k}={obj[k]!r} not allowed" for k, allowed in enums.items() if k in obj and obj[k] not in allowed]
        errs += [f"unknown field {k}" for k in obj if k not in known]
        return errs

    defs = {}
    def_checks = []
    for d in data.get("severity_definitions", []):
        defs[d.get("key")] = d
        def_checks.append({"key": d.get("key"), "errors": validate(d, "severity_definitions"),
                           "quote_check": quote_check(d.get("quote", ""), doc)})
    rows = []
    for i, a in enumerate(data.get("associations", []), 1):
        errs = validate(a, "associations")
        d = defs.get(a.get("severity_key"))
        if not d:
            errs.append(f"severity_key {a.get('severity_key')!r} not defined")
            d = {}
        missing = sorted({n for f in NUM_FIELDS for n in numbers(str(a.get(f) or "")) if n not in doc_numbers})
        marker, cls, status = map_marker(a, canon, alias, patterns)
        rows.append({
            "id": aid, "row": i, "cohort": art.get("cohort_id") or "", "article_species": art.get("species_short") or "",
            "severity_key": a.get("severity_key"), "outcome_class": d.get("outcome_class", ""),
            "complication": d.get("complication") or "", "severity_label": d.get("label", ""),
            "marker_as_reported": a.get("marker_as_reported", ""), "marker_extracted": a.get("marker", ""),
            "marker": marker, "marker_class": cls or a.get("marker_class", ""), "map_status": status,
            **{k: a.get(k) if a.get(k) is not None else "" for k in [
                "specimen", "timepoint", "species", "species_confirmation", "subgroup", "n_total", "n_severe",
                "n_comparison", "analysis", "direction", "significant", "statistic", "p_value", "effect_type",
                "effect_value", "effect_ci", "cutoff", "sensitivity", "specificity", "adjusted_for", "source_type",
                "location", "confidence"]},
            "quote_check": quote_check(a.get("quote", ""), doc),
            "numbers_missing": "; ".join(f"{n:g}" for n in missing),
            "errors": "; ".join(errs), "note": a.get("note") or "", "quote": a.get("quote", ""),
        })
    return {"id": aid, "data": data, "errors": errors, "defs": def_checks, "rows": rows}


def summarise(res):
    rows = res["rows"]
    qc = collections.Counter(r["quote_check"] for r in rows)
    lines = [f"{res['id']}: {len(res['defs'])} severity definitions, {len(rows)} associations; quotes "
             + ", ".join(f"{k} {v}" for k, v in sorted(qc.items()))]
    lines += [f"  ERROR {e}" for e in res["errors"]]
    for d in res["defs"]:
        if d["errors"] or d["quote_check"] not in ("exact", "near"):
            lines.append(f"  {d['key']}: quote {d['quote_check']}" + (f"; {'; '.join(d['errors'])}" if d["errors"] else ""))
    for r in rows:
        probs = []
        if r["quote_check"] not in ("exact", "near"):
            probs.append(f"quote {r['quote_check']}")
        if r["numbers_missing"]:
            probs.append(f"numbers not in text: {r['numbers_missing']}")
        if r["errors"]:
            probs.append(r["errors"])
        if r["map_status"] == "unmapped":
            probs.append(f"marker unmapped ({r['marker_extracted']!r})")
        if probs:
            lines.append(f"  row {r['row']} {r['marker_as_reported']!r}: " + "; ".join(probs))
    return "\n".join(lines)


def write_report(results, path):
    rows = [r for res in results for r in res["rows"]]
    qc = collections.Counter(r["quote_check"] for r in rows)
    out = ["# Marker-severity extraction report", "",
           "Built by `scripts/check_associations.py` from `data/severity/extractions/`. Quote checks: exact = found "
           "verbatim after normalisation; near = >= 80% of 4-word shingles found; partial = >= 50%; not_found = "
           "unverified. Numbers not in text = values in the statistic fields that occur nowhere in the article text.", "",
           f"- Articles: {len(results)}",
           f"- Severity definitions: {sum(len(r['defs']) for r in results)}",
           f"- Associations: {len(rows)} (significant: {sum(r['significant'] == 'yes' for r in rows)}, "
           f"not significant: {sum(r['significant'] == 'no' for r in rows)})",
           "- Quotes: " + ", ".join(f"{k} {v}" for k, v in sorted(qc.items())),
           f"- Rows with numbers not in text: {sum(bool(r['numbers_missing']) for r in rows)}",
           f"- Rows with schema errors: {sum(bool(r['errors']) for r in rows)}",
           f"- Markers: {len({r['marker'] for r in rows if r['marker']})} distinct; unmapped rows: "
           f"{sum(r['map_status'] == 'unmapped' for r in rows)}", "",
           "## Per article", "",
           "| ID | Species | Cohort | Definitions | Rows | Sig. yes / no | Quotes exact+near / total | Number misses | Errors |",
           "|---|---|---|---|---|---|---|---|---|"]
    for res in results:
        rs = res["rows"]
        out.append(f"| {res['id']} | {rs[0]['article_species'] if rs else ''} | {rs[0]['cohort'] if rs else ''} | "
                   f"{len(res['defs'])} | {len(rs)} | {sum(r['significant'] == 'yes' for r in rs)} / "
                   f"{sum(r['significant'] == 'no' for r in rs)} | "
                   f"{sum(r['quote_check'] in ('exact', 'near') for r in rs)} / {len(rs)} | "
                   f"{sum(bool(r['numbers_missing']) for r in rs)} | {len(res['errors']) + sum(bool(r['errors']) for r in rs)} |")
    out += ["", "## Problems to check", "", "```"]
    out += [summarise(res) for res in results]
    mapped = collections.Counter((r["marker_as_reported"], r["marker_extracted"], r["marker"], r["map_status"])
                                 for r in rows if r["map_status"] in ("alias", "pattern", "unmapped"))
    out += ["```", "", "## Marker mappings to check", "",
            "Rows whose marker was not already a canonical name: mapped through an alias, a pattern (least reliable), "
            "or not at all. Fix wrong ones with a manual row in `marker_map.csv`.", "",
            "| As reported | Extractor's marker | Mapped to | How | Rows |", "|---|---|---|---|---|"]
    out += [f"| {a} | {e} | {m} | {s} | {n} |" for (a, e, m, s), n in sorted(mapped.items(), key=lambda kv: kv[0][3])]
    out += ["", "## Severity definitions", "",
            "| ID | Key | Class | Label | Definition |", "|---|---|---|---|---|"]
    for res in results:
        for d in res["data"].get("severity_definitions", []):
            cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")
            out.append(f"| {res['id']} | {d.get('key')} | {d.get('outcome_class')}"
                       f"{' (' + cell(d.get('complication')) + ')' if d.get('complication') else ''} | "
                       f"{cell(d.get('label'))} | {cell(d.get('definition'))} |")
    # preview of the evidence matrix: articles per marker and outcome class, by direction of significant results
    cells = collections.defaultdict(lambda: {"up": set(), "down": set(), "null": set()})
    for r in rows:
        if not r["marker"] or r["marker"] == "-":
            continue
        c = cells[(r["marker_class"], r["marker"], r["outcome_class"])]
        if r["significant"] == "yes" and r["direction"] in UP:
            c["up"].add(r["id"])
        elif r["significant"] == "yes" and r["direction"] in DOWN:
            c["down"].add(r["id"])
        elif r["significant"] == "no" or r["direction"] == "no_difference":
            c["null"].add(r["id"])
    out += ["", "## Evidence preview", "",
            "Articles per marker and outcome class: significant with higher values in (or positively associated with) "
            "the worse outcome, significant lower, and not significant. Articles, not rows; linked cohorts are not "
            "merged here.", "", "| Class | Marker | Outcome | Higher | Lower | Not significant |", "|---|---|---|---|---|---|"]
    for (cls, marker, oc), c in sorted(cells.items()):
        fmt = lambda s: ", ".join(sorted(s)) if s else ""
        out.append(f"| {cls} | {marker} | {oc} | {fmt(c['up'])} | {fmt(c['down'])} | {fmt(c['null'])} |")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def add_unmapped(map_rows, results):
    known = {r["alias"] for r in map_rows}
    new = []
    for res in results:
        for r in res["rows"]:
            alias = norm_name(r["marker_as_reported"])
            if r["map_status"] == "unmapped" and alias and alias not in known:
                known.add(alias)
                new.append({"alias": alias, "marker": "", "marker_class": "", "pattern": "", "cui": "",
                            "source": "extracted", "articles": "",
                            "note": f"from {r['id']}; extractor proposed {r['marker_extracted']!r} ({r['marker_class']})"})
    if new:
        with open(MAP, "a", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, fieldnames=list(map_rows[0])).writerows(new)
    return len(new)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    args = ap.parse_args()
    required_top, rules = schema_rules()
    map_rows, canon, alias, patterns = load_map()
    articles = {}
    with open(ROOT / "articles.jsonl", encoding="utf-8") as fh:
        for line in fh:
            a = json.loads(line)
            articles[a["id"]] = a
    paths = sorted(EXTRACT.glob("*.json"))
    if args.ids:
        paths = [p for p in paths if p.stem in set(args.ids)]
    results = []
    for p in paths:
        try:
            results.append(check_article(p, required_top, rules, canon, alias, patterns, articles))
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            print(f"{p.stem}: cannot read ({type(e).__name__}: {e})")
    for res in results:
        print(summarise(res))
    if args.ids:
        return
    rows = [r for res in results for r in res["rows"]]
    if rows:
        with open(SEV / "associations.csv", "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    write_report(results, SEV / "extraction_report.md")
    print(f"{len(results)} articles, {len(rows)} associations; {add_unmapped(map_rows, results)} new aliases in marker_map.csv")


if __name__ == "__main__":
    main()
