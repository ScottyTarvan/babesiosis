"""Validate the review outputs: syntax, identifiers, duplicates, links, counts, checksums.

Usage (from canine-babesiosis-review/):
    python -I scripts/validate.py
Exits non-zero if any error is found; warnings are printed but do not fail.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import review_window  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
W_START, W_END = review_window()
VALID_SCOPE = {"core canine evidence", "canine review", "human comparator", "background"}
CATS = {"ERY", "INF", "END", "COA", "REN", "PUL", "NEU", "CAR", "MET", "OXO", "SEV"}
errors, warnings = [], []


def jl(p):
    out = []
    for i, l in enumerate(open(p, encoding="utf-8"), 1):
        if l.strip():
            try:
                out.append(json.loads(l))
            except json.JSONDecodeError as e:
                errors.append(f"{p.name}:{i} invalid JSON: {e}")
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    arts = jl(ROOT / "articles.jsonl")
    dsets = jl(ROOT / "datasets.jsonl")
    man = jl(ROOT / "data" / "manifest.jsonl")
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    retired = {v["id"] for v in reg.values() if v.get("retired")}
    # Reclassified records (retired with replaced_by, e.g. a BG paper that became a CB article).
    replaced = {v["id"]: v["replaced_by"] for v in reg.values() if v.get("retired") and v.get("replaced_by")}
    ids = [a["id"] for a in arts]
    for i, c in Counter(ids).items():
        if c > 1:
            errors.append(f"duplicate article id {i}")
    for field in ("doi", "pmid"):
        vals = [str(a[field]).lower() for a in arts if a.get(field)]
        for v, c in Counter(vals).items():
            if c > 1:
                errors.append(f"duplicate {field} {v}")
    for a in arts:
        if a["scope_label"] not in VALID_SCOPE:
            errors.append(f"{a['id']} invalid scope {a['scope_label']}")
        if a["id"].startswith("CB") and a["primary_category"] not in CATS:
            errors.append(f"{a['id']} invalid primary category {a['primary_category']}")
        if a["id"] in replaced and replaced[a["id"]] not in ids:
            warnings.append(f"{a['id']} is reclassified as {replaced[a['id']]}; it stays in articles.jsonl until {replaced[a['id']]} is extracted")
        elif a["id"] in retired:
            errors.append(f"{a['id']} is retired but present in articles.jsonl")
        note = ROOT / a["filename"]
        if not note.exists():
            errors.append(f"{a['id']} note missing {a['filename']}")
            continue
        t = note.read_text(encoding="utf-8")
        if "[Back to article index](../index.md)" not in t:
            errors.append(f"{a['id']} missing backlink")
        if "{{" in t:
            errors.append(f"{a['id']} unfilled placeholder")
        if f"| {a['id']} |" not in t:
            errors.append(f"{a['id']} ID row missing in note")
        if a.get("pmid") and a["pmid"] not in t:
            warnings.append(f"{a['id']} PMID {a['pmid']} not shown in note")
        if a.get("doi") and a["doi"].lower() not in t.lower():
            warnings.append(f"{a['id']} DOI not shown in note")
        fp = (a["first_pub_date"] or "")[:10]
        # A partial date (YYYY or YYYY-MM) is compared with the same-length prefix of the window bounds.
        if a["id"].startswith("CB") and not (fp and W_START[:len(fp)] <= fp <= W_END[:len(fp)]):
            warnings.append(f"{a['id']} first_pub_date {a['first_pub_date']} check window")
    for p in sorted((ROOT / "articles").glob("*.md")):
        pid = p.name.split("_")[0]
        if pid in replaced and replaced[pid] in ids:
            warnings.append(f"superseded note {p.name}: {pid} was reclassified as {replaced[pid]}; delete this note")
        elif pid not in ids:
            errors.append(f"orphan note {p.name}")
    # dataset consistency
    dids = [d["dataset_id"] for d in dsets]
    for i, c in Counter(dids).items():
        if c > 1:
            errors.append(f"duplicate dataset id {i}")
    by_art = {}
    for d in dsets:
        if d["status_code"] not in (1, 2, 3):
            errors.append(f"dataset {d['dataset_id']} unexpected status {d['status_code']}")
        if d["status_code"] == 1 and not d.get("downloaded_files"):
            errors.append(f"dataset {d['dataset_id']} status 1 without downloaded files")
        for a in d.get("linked_articles") or []:
            if a not in ids:
                errors.append(f"dataset {d['dataset_id']} links unknown/retired article {a}")
            by_art.setdefault(a, []).append(d["status_code"])
    for a in arts:
        if a["id"].startswith("CB"):
            exp = min(by_art[a["id"]]) if a["id"] in by_art else None
            if exp is not None and a["dataset_status_code"] != exp:
                errors.append(f"{a['id']} dataset status {a['dataset_status_code']} != linked dataset status {exp}")
            if exp is None and a["dataset_status_code"] not in (4, 5):
                errors.append(f"{a['id']} has no dataset but status {a['dataset_status_code']}")
    # manifest checksums
    for m in man:
        f = ROOT / m["file"]
        if not f.exists():
            errors.append(f"manifest file missing {m['file']}")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != m["sha256"]:
            errors.append(f"checksum mismatch {m['file']}")
    raw_files = {p.relative_to(ROOT).as_posix() for p in (ROOT / "data" / "raw").rglob("*") if p.is_file()}
    for extra in raw_files - {m["file"] for m in man}:
        errors.append(f"file in data/raw without manifest row: {extra}")
    total = sum(m["bytes"] for m in man)
    if total > 250 * 1024 * 1024 or any(m["bytes"] > 50 * 1024 * 1024 for m in man):
        errors.append("download caps exceeded")
    # links and absolute paths in markdown
    mds = [ROOT / n for n in ("index.md", "datasets.md", "research-map.md", "search-log.md")] + sorted((ROOT / "articles").glob("*.md"))
    anchors = {}
    for md in mds:
        if not md.exists():
            errors.append(f"missing output {md.name}")
            continue
        t = md.read_text(encoding="utf-8")
        if re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]|/c/Workspaces|/Users/|AppData", t):
            errors.append(f"absolute local path in {md.relative_to(ROOT)}")
        for m in re.finditer(r"\]\(([^)\s]+)\)", t):
            link = m.group(1)
            if link.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, frag = link.partition("#")
            target = (md.parent / path).resolve() if path else md
            if not target.exists():
                errors.append(f"broken link in {md.relative_to(ROOT)}: {link}")
                continue
            if frag and target.suffix == ".md":
                if target not in anchors:
                    tt = target.read_text(encoding="utf-8")
                    a = set(re.findall(r'<a id="([^"]+)"', tt))
                    for h in re.findall(r"^#+\s+(.*)$", tt, flags=re.M):
                        a.add(re.sub(r"[^\w\- ]", "", h.lower()).strip().replace(" ", "-"))
                    anchors[target] = a
                if frag not in anchors[target]:
                    warnings.append(f"anchor not found in {md.relative_to(ROOT)}: {link}")
        for rid in re.findall(r"\b(CB\d{3})\b", t):
            if rid in retired and md.name not in ("search-log.md",):
                warnings.append(f"{md.relative_to(ROOT)} mentions retired {rid}")
    # index counts
    idx = (ROOT / "index.md").read_text(encoding="utf-8")
    canine = [a for a in arts if a["id"].startswith("CB")]
    rows = re.findall(r"^\| (CB\d{3}) \|", idx, flags=re.M)
    if sorted(rows) != sorted(a["id"] for a in canine):
        errors.append(f"index rows ({len(rows)}) do not match canine articles ({len(canine)})")
    m = re.search(r"\| \*\*Total\*\* \| \*\*(\d+)\*\*", idx)
    if not m or int(m.group(1)) != len(canine):
        errors.append("index primary-category total does not equal canine article count")
    print(f"articles={len(arts)} canine={len(canine)} datasets={len(dsets)} manifest={len(man)} ({total / 1e6:.1f} MB)")
    for w in sorted(set(warnings)):
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(set(warnings))} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
