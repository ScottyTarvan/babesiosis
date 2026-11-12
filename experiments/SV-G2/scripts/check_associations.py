"""Check SV-G2 schema-v2 extractions and flatten them into associations_v2.csv and definitions_v2.csv.

Restored from git 8d4c6d9:core/scripts/check_associations.py (the pilot checker, kept unchanged as
check_associations_pilot.py) and changed for SV-G2:

- Reads /experiments/SV-G2/extractions/<ID>.json (or --dir, e.g. second/ for the blind second extractions).
- Validates against /experiments/SV-G2/association_schema_v2.json: top-level enums (setting, sample_timing),
  definition components, the not_extracted list, and load_method on parasite load rows.
- Numbers in severe_value and comparison_value are checked against the text like the other number fields.
- Markers map through /core/data/severity/marker_map.csv plus /experiments/SV-G2/marker_map_v2_additions.csv
  (the owner-merged additions). It never writes to /core/.
- The cohort is taken from /core/cohorts.json (members) and the independent unit is the cohort or, if none, the ID.

Quote checks (unchanged): exact = found after normalisation; near = >= 80% of 4-word shingles found;
partial = >= 50%; not_found = below.

Outputs (full run only, with no --ids): SV-G2/associations_v2.csv, SV-G2/definitions_v2.csv,
SV-G2/out/check_report.md, SV-G2/out/unmapped_markers.csv. With --ids it prints the checks and writes nothing.

Usage (from /experiments/SV-G2/; standard library only):
    python -I scripts/check_associations.py [--ids CB040 CB017] [--dir second] [--no-write]
"""
import argparse
import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
CORE = PKG.parent.parent / "core"
SEV = CORE / "data" / "severity"
MAP = SEV / "marker_map.csv"
MAP_ADD = PKG / "marker_map_v2_additions.csv"
SCHEMA = PKG / "association_schema_v2.json"
NUM_FIELDS = ["statistic", "p_value", "effect_value", "effect_ci", "cutoff", "sensitivity", "specificity",
              "severe_value", "comparison_value"]
LOAD_MARKERS = {"Parasitaemia", "Parasite DNA load (qPCR)"}
NUMBER = re.compile(r"(?<![\w.])\d*\.?\d+")
UP = {"higher_in_severe", "more_frequent_in_severe", "positive_association"}
DOWN = {"lower_in_severe", "less_frequent_in_severe", "negative_association"}


def norm_name(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[‐‑‒–—−]", "-", s)
    return s.replace("β", "beta").replace("α", "alpha").replace("γ", "gamma").replace("κ", "kappa")


def fix_commas(s):
    s = re.sub(r"(?<![\d.,])([1-9]\d{0,2})((?:,\d{3})+)(?![\d,])", lambda m: m.group(1) + m.group(2).replace(",", ""), s)
    return re.sub(r"(\d),(\d)", r"\1.\2", s)


def norm_text(s):
    s = norm_name(s)
    s = s.replace("·", ".").replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = fix_commas(s)
    s = re.sub(r"<br\s*/?>|</?[a-z][a-z0-9]*(\s[^<>]*)?/?>", " ", s)
    s = re.sub(r"[*_|\\`#]", " ", s)
    s = re.sub(r"\s*([≤≥<>=±:;,()\[\]/%-])\s*", r"\1", s)
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


def enum_of(spec):
    if "enum" in spec:
        return set(spec["enum"])
    if "const" in spec:
        return {spec["const"]}
    return None


def schema_rules():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    props = schema["properties"]
    top_enums = {k: enum_of(v) for k, v in props.items() if enum_of(v)}
    rules = {}
    for part in ("severity_definitions", "associations"):
        items = props[part]["items"]
        enums = {k: enum_of(v) for k, v in items["properties"].items() if enum_of(v)}
        rules[part] = (items["required"], enums, set(items["properties"]))
    components = set(props["severity_definitions"]["items"]["properties"]["components"]["items"]["enum"])
    ne = props["not_extracted"]["items"]
    return schema["required"], set(props), top_enums, rules, components, (ne["required"], set(ne["properties"]["reason"]["enum"]))


def load_map():
    with open(MAP, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    canon = {r["marker"]: r["marker_class"] for r in rows if r["pattern"]}
    alias = {r["alias"]: (r["marker"], r["marker_class"]) for r in rows}
    patterns = [(r["marker"], r["marker_class"], r["pattern"]) for r in rows if r["pattern"]]
    if MAP_ADD.exists():
        with open(MAP_ADD, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("canonical") == "yes":
                    canon[r["marker"]] = r["marker_class"]
                if r.get("alias"):
                    alias[norm_name(r["alias"])] = (r["marker"], r["marker_class"])
    return canon, alias, patterns


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


def load_context():
    cohorts = json.loads((CORE / "cohorts.json").read_text(encoding="utf-8"))
    member = {m: cid for cid, c in cohorts.items() for m in c.get("members", [])}
    articles = {}
    with open(CORE / "articles.jsonl", encoding="utf-8") as fh:
        for line in fh:
            a = json.loads(line)
            articles[a["id"]] = {"species_short": a.get("species_short") or "", "doi": a.get("doi") or "",
                                 "cohort_id": a.get("cohort_id") or ""}
    with open(SEV / "shortlist.csv", encoding="utf-8") as fh:
        short = {r["id"]: r for r in csv.DictReader(fh)}
    return member, articles, short


def check_article(path, ctx, canon, alias, patterns, member, articles, short):
    required_top, known_top, top_enums, rules, components, (ne_req, ne_reasons) = ctx
    data = json.loads(path.read_text(encoding="utf-8"))
    aid = data.get("id") or path.stem
    errors = [f"missing {k}" for k in required_top if k not in data]
    errors += [f"unknown top-level field {k}" for k in data if k not in known_top]
    errors += [f"{k}={data[k]!r} not allowed" for k, allowed in top_enums.items() if k in data and data[k] not in allowed]
    if aid != path.stem:
        errors.append(f"id {aid!r} does not match file name")
    for i, ne in enumerate(data.get("not_extracted") or []):
        errors += [f"not_extracted[{i}] missing {k}" for k in ne_req if not ne.get(k)]
        if ne.get("reason") and ne["reason"] not in ne_reasons:
            errors.append(f"not_extracted[{i}] reason {ne['reason']!r} not allowed")
    text_path = CORE / data.get("text_used", f"data/markdown/{aid}.md")
    if not text_path.exists():
        errors.append(f"text_used not found: {text_path}")
        doc = ""
    else:
        raw = text_path.read_text(encoding="utf-8")
        raw = re.sub(r"\A---\n.*?\n---\n", "", raw, flags=re.S)
        doc = norm_text(raw)
    doc_numbers = numbers(doc)
    art = articles.get(aid, {})
    sl = short.get(aid, {})
    cohort = member.get(aid, "")
    unit = cohort or aid

    def validate(obj, part):
        req, enums, known = rules[part]
        errs = [f"missing {k}" for k in req if obj.get(k) in (None, "", [])]
        errs += [f"{k}={obj[k]!r} not allowed" for k, allowed in enums.items() if k in obj and obj[k] not in allowed]
        errs += [f"unknown field {k}" for k in obj if k not in known]
        return errs

    defs = {}
    def_rows = []
    for d in data.get("severity_definitions", []):
        errs = validate(d, "severity_definitions")
        bad = [c for c in d.get("components") or [] if c not in components]
        if bad:
            errs.append(f"components not allowed: {bad}")
        if d.get("key") in defs:
            errs.append(f"duplicate key {d.get('key')}")
        defs[d.get("key")] = d
        def_rows.append({
            "id": aid, "cohort": cohort, "independent_unit": unit, "article_species": art.get("species_short", ""),
            "tier": sl.get("tier", ""), "source_format": sl.get("source_format", ""),
            "setting": data.get("setting", ""), "sample_timing": data.get("sample_timing", ""),
            "severity_key": d.get("key"), "outcome_class": d.get("outcome_class", ""),
            "complication": d.get("complication") or "", "severity_label": d.get("label", ""),
            "components": "; ".join(d.get("components") or []), "euthanasia_included": d.get("euthanasia_included", ""),
            "definition_source": d.get("definition_source", ""), "follow_up_horizon": d.get("follow_up_horizon") or "",
            "severe_group": d.get("severe_group") or "", "comparison_group": d.get("comparison_group") or "",
            "definition": d.get("definition", ""), "n_associations": 0,
            "quote_check": quote_check(d.get("quote", ""), doc), "errors": "; ".join(errs), "quote": d.get("quote", ""),
        })
    by_key = {r["severity_key"]: r for r in def_rows}
    rows = []
    for i, a in enumerate(data.get("associations", []), 1):
        errs = validate(a, "associations")
        d = defs.get(a.get("severity_key"))
        if not d:
            errs.append(f"severity_key {a.get('severity_key')!r} not defined")
            d = {}
        else:
            by_key[a["severity_key"]]["n_associations"] += 1
        missing = sorted({n for f in NUM_FIELDS for n in numbers(str(a.get(f) or "")) if n not in doc_numbers})
        marker, cls, status = map_marker(a, canon, alias, patterns)
        if marker in LOAD_MARKERS and not a.get("load_method"):
            errs.append("load_method missing on a parasite load row")
        if (a.get("severe_value") or a.get("comparison_value")) and not a.get("summary_type"):
            errs.append("summary_type missing with group values")
        rows.append({
            "id": aid, "row": i, "cohort": cohort, "independent_unit": unit, "article_species": art.get("species_short", ""),
            "tier": sl.get("tier", ""), "source_format": sl.get("source_format", ""),
            "setting": data.get("setting", ""), "sample_timing": data.get("sample_timing", ""),
            "severity_key": a.get("severity_key"), "outcome_class": d.get("outcome_class", ""),
            "complication": d.get("complication") or "", "severity_label": d.get("label", ""),
            "components": "; ".join(d.get("components") or []), "euthanasia_included": d.get("euthanasia_included", ""),
            "definition_source": d.get("definition_source", ""), "follow_up_horizon": d.get("follow_up_horizon") or "",
            "marker_as_reported": a.get("marker_as_reported", ""), "marker_extracted": a.get("marker", ""),
            "marker": marker, "marker_class": cls or a.get("marker_class", ""), "map_status": status,
            **{k: a.get(k) if a.get(k) is not None else "" for k in [
                "specimen", "timepoint", "species", "species_confirmation", "subgroup", "n_total", "n_severe",
                "n_comparison", "analysis", "direction", "significant", "severe_value", "comparison_value", "summary_type",
                "load_method", "statistic", "p_value", "effect_type", "effect_value", "effect_ci", "cutoff", "sensitivity",
                "specificity", "adjusted_for", "source_type", "location", "confidence"]},
            "quote_check": quote_check(a.get("quote", ""), doc),
            "numbers_missing": "; ".join(f"{n:g}" for n in missing),
            "errors": "; ".join(errs), "note": a.get("note") or "", "quote": a.get("quote", ""),
        })
    return {"id": aid, "data": data, "errors": errors, "defs": def_rows, "rows": rows}


def summarise(res):
    rows = res["rows"]
    qc = collections.Counter(r["quote_check"] for r in rows)
    lines = [f"{res['id']}: {len(res['defs'])} severity definitions, {len(rows)} associations; quotes "
             + ", ".join(f"{k} {v}" for k, v in sorted(qc.items()))]
    lines += [f"  ERROR {e}" for e in res["errors"]]
    for d in res["defs"]:
        if d["errors"] or d["quote_check"] not in ("exact", "near"):
            lines.append(f"  {d['severity_key']}: quote {d['quote_check']}" + (f"; {d['errors']}" if d["errors"] else ""))
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


def write_csv(path, rows):
    if not rows:
        return
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def write_report(results, path):
    rows = [r for res in results for r in res["rows"]]
    defs = [d for res in results for d in res["defs"]]
    qc = collections.Counter(r["quote_check"] for r in rows)
    dq = collections.Counter(d["quote_check"] for d in defs)
    out = ["# SV-G2 checker report", "", "Built by `scripts/check_associations.py` from `extractions/`.", "",
           f"- Articles: {len(results)}",
           f"- Severity definitions: {len(defs)}; definition quotes: " + ", ".join(f"{k} {v}" for k, v in sorted(dq.items())),
           f"- Associations: {len(rows)}; quotes: " + ", ".join(f"{k} {v}" for k, v in sorted(qc.items())),
           f"- Rows with numbers not in text: {sum(bool(r['numbers_missing']) for r in rows)}",
           f"- Rows with schema errors: {sum(bool(r['errors']) for r in rows)}; articles with top-level errors: "
           f"{sum(bool(res['errors']) for res in results)}",
           f"- Unmapped marker rows: {sum(r['map_status'] == 'unmapped' for r in rows)}", "", "## Problems", "", "```"]
    out += [summarise(res) for res in results]
    out += ["```"]
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--dir", default="extractions", help="folder of extraction files, relative to SV-G2/")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="print only articles with problems")
    args = ap.parse_args()
    ctx = schema_rules()
    canon, alias, patterns = load_map()
    member, articles, short = load_context()
    paths = sorted((PKG / args.dir).glob("*.json"))
    if args.ids:
        paths = [p for p in paths if p.stem in set(args.ids)]
    results = []
    for p in paths:
        try:
            results.append(check_article(p, ctx, canon, alias, patterns, member, articles, short))
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            print(f"{p.stem}: cannot read ({type(e).__name__}: {e})")
    for res in results:
        s = summarise(res)
        if not args.quiet or "\n" in s:
            print(s)
    if args.ids or args.no_write or args.dir != "extractions":
        return
    rows = [r for res in results for r in res["rows"]]
    write_csv(PKG / "associations_v2.csv", rows)
    write_csv(PKG / "definitions_v2.csv", [d for res in results for d in res["defs"]])
    (PKG / "out").mkdir(exist_ok=True)
    write_report(results, PKG / "out" / "check_report.md")
    um = collections.Counter((r["marker_as_reported"], r["marker_extracted"], r["marker_class"], r["id"])
                             for r in rows if r["map_status"] == "unmapped")
    write_csv(PKG / "out" / "unmapped_markers.csv",
              [{"marker_as_reported": k[0], "marker_extracted": k[1], "marker_class": k[2], "id": k[3], "rows": n}
               for k, n in sorted(um.items())])
    print(f"{len(results)} articles, {len(rows)} associations")


if __name__ == "__main__":
    main()
