"""Check a clinical page file against /clinical/content-format.md.

Usage: python -I clinical/shared/validate.py <path to ID.json> [more files]
Standard library only. Ends with OK (exit 0) or with the number of errors (exit 1).
"""
import json
import re
import sys
from pathlib import Path

STATUS = {"standard", "proposed", "conflicting", "no_benefit", "harmful"}
LEVELS = {"A", "B", "C", "D", "E"}
CLASSES = {"antibabesial", "supportive", "specific", "adjunct"}
BASIS = {"babesiosis", "general canine", "human", "working"}
SETTING = {"practice", "referral"}
READ = {"full text", "abstract"}
TOP = ["schema_version", "id", "title", "updated", "definition", "key_points", "description",
       "diagnosis", "approach", "treatments", "prognosis", "evidence_gaps", "references", "search"]
MARK = re.compile(r"\[(R\d+)\]")
BAD_MARK = re.compile(r"\[R\d+\s*[,;-]\s*R?\d+")
NON_METRIC = re.compile(r"(?<![A-Za-z])(lbs?|pounds?|ounces?|oz|fahrenheit|inch(es)?|gallons?|grains?)(?![A-Za-z])|°\s?F|/\s?lb",
                        re.IGNORECASE)
NON_SI = re.compile(r"mg/dl|g/dl|mEq", re.IGNORECASE)


def strings(node, path=""):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from strings(v, f"{path}.{k}" if path else k)


def check(path):
    errors, warnings = [], []
    err, warn = errors.append, warnings.append
    try:
        page = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"not valid JSON: {exc}"], []

    for key in TOP:
        if key not in page:
            err(f"missing field: {key}")
    if errors:
        return errors, warnings
    if page["schema_version"] != 1:
        err("schema_version must be 1")
    stem = Path(path).stem
    if page["id"] != stem and stem != "example":
        err(f"id {page['id']!r} does not match the file name {stem!r}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(page["updated"])):
        err("updated must be YYYY-MM-DD")
    if not 3 <= len(page["key_points"]) <= 6 and stem != "example":
        warn("key_points: give 3 to 6")

    refs = {}
    for i, r in enumerate(page["references"]):
        key = r.get("ref", "")
        if not re.fullmatch(r"R\d+", key):
            err(f"references[{i}]: ref must be R<number>")
        if key in refs:
            err(f"references: {key} is defined twice")
        refs[key] = r
        for f in ("authors", "year", "title", "type", "read"):
            if not r.get(f):
                err(f"references {key}: missing {f}")
        if not (r.get("doi") or r.get("pmid") or r.get("url")):
            err(f"references {key}: needs a doi, a pmid or a url")
        if r.get("doi", "").lower().startswith(("http", "doi:")):
            err(f"references {key}: doi must be the bare DOI (10.…)")
        if r.get("url") and not r["url"].startswith("https://"):
            err(f"references {key}: url must start with https://")
        if r.get("read") and r["read"] not in READ:
            err(f"references {key}: read must be one of {sorted(READ)}")
        if r.get("article_id") and not re.fullmatch(r"(CB|HU|BG)\d{3}", r["article_id"]):
            err(f"references {key}: article_id must be a local ID such as CB050")

    def need_refs(item, where):
        got = item.get("refs")
        if not got:
            err(f"{where}: refs is empty")
            return
        for k in got:
            if k not in refs:
                err(f"{where}: {k} is not in references")

    cited = set()
    for where, text in strings({k: v for k, v in page.items() if k != "references"}):
        cited.update(MARK.findall(text))
        if BAD_MARK.search(text):
            err(f"{where}: write each citation as its own marker, [R1][R2]")
        if "<" in text and re.search(r"<[a-zA-Z/]", text):
            err(f"{where}: no HTML")
        if NON_METRIC.search(text):
            err(f"{where}: non-metric unit: {NON_METRIC.search(text).group(0)!r}")
        if NON_SI.search(text):
            warn(f"{where}: use SI units ({NON_SI.search(text).group(0)!r} found)")
    for where, text in strings(page):
        if where.endswith("refs") or ".refs[" in where:
            cited.add(text)
    for k in sorted(cited - set(refs)):
        err(f"citation {k} is not in references")
    for k in sorted(set(refs) - cited):
        warn(f"reference {k} is not cited")

    if "[R" not in page["definition"]:
        err("definition: no citation")
    for i, d in enumerate(page["description"]):
        if not d.get("heading") or not d.get("text"):
            err(f"description[{i}]: needs heading and text")
        elif "[R" not in d["text"]:
            warn(f"description[{i}]: no citation")

    dx = page["diagnosis"]
    for part in ("criteria", "clinical_signs", "tests", "differentials"):
        if part not in dx:
            err(f"diagnosis: missing {part}")
            continue
        for i, item in enumerate(dx[part]):
            need_refs(item, f"diagnosis.{part}[{i}]")
    for i, c in enumerate(dx.get("criteria", [])):
        if c.get("basis") not in BASIS:
            err(f"diagnosis.criteria[{i}]: basis must be one of {sorted(BASIS)}")
        if not c.get("criterion") or not c.get("threshold"):
            err(f"diagnosis.criteria[{i}]: needs criterion and threshold")
    for i, g in enumerate(dx.get("grading", [])):
        need_refs(g, f"diagnosis.grading[{i}]")

    for i, s in enumerate(page["approach"]):
        if s.get("setting") not in SETTING:
            err(f"approach[{i}]: setting must be one of {sorted(SETTING)}")
        if not s.get("action") or not s.get("detail"):
            err(f"approach[{i}]: needs action and detail")

    if not page["treatments"]:
        warn("treatments is empty: is that the finding?")
    for i, t in enumerate(page["treatments"]):
        where = f"treatments[{i}] ({t.get('name', '?')})"
        for f in ("name", "aim", "evidence_summary"):
            if not t.get(f):
                err(f"{where}: missing {f}")
        if t.get("class") not in CLASSES:
            err(f"{where}: class must be one of {sorted(CLASSES)}")
        if t.get("status") not in STATUS:
            err(f"{where}: status must be one of {sorted(STATUS)}")
        if t.get("evidence_level") not in LEVELS:
            err(f"{where}: evidence_level must be A to E")
        if not isinstance(t.get("independent_studies"), int):
            err(f"{where}: independent_studies must be a whole number")
        need_refs(t, where)
        for j, d in enumerate(t.get("doses", [])):
            dw = f"{where} doses[{j}]"
            for f in ("drug", "dose", "route", "frequency", "context"):
                if not d.get(f):
                    err(f"{dw}: missing {f}")
            if d.get("dose") and not re.search(r"\d", d["dose"]):
                err(f"{dw}: dose has no number")
            if d.get("dose") and not re.search(r"/kg|/m2|/m²|%|/dog|/h\b", d["dose"]):
                warn(f"{dw}: dose {d['dose']!r} has no per-kg unit: check it")
            need_refs(d, dw)

    pr = page["prognosis"]
    if not pr.get("text"):
        err("prognosis: missing text")
    for i, ind in enumerate(pr.get("indicators", [])):
        need_refs(ind, f"prognosis.indicators[{i}]")
    for i, rel in enumerate(page.get("related", [])):
        if not re.fullmatch(r"(SY\d{2}|TX00)", rel.get("id", "")):
            err(f"related[{i}]: id must be a page ID")
    if not page["search"].get("date") or not page["search"].get("sources"):
        err("search: needs date and sources")
    return errors, warnings


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    total = 0
    for path in argv[1:]:
        errors, warnings = check(path)
        print(path)
        for w in warnings:
            print(f"  warning: {w}")
        for e in errors:
            print(f"  ERROR: {e}")
        total += len(errors)
    print("OK" if total == 0 else f"{total} error(s)")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
