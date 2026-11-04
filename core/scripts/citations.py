"""Backward and forward citation searching via the Europe PMC references/citations API.

Seeds: the seed review plus every record included at title/abstract screening
(search/screening_r1.jsonl). For each seed PMID, fetches its reference list
(backward) and citing articles (forward). New records (not already in
search/candidates.jsonl) are kept as candidates when the title (and abstract,
for records with a PMID) mentions Babesia/babesiosis/piroplasm and the first
publication date falls in the review window. Reference-list entries without a
PMID are kept when the title mentions Babesia and the year is in the window,
then resolved via Crossref title search where possible.

Writes search/citation_hits.jsonl (every new linked record with provenance) and
search/candidates_r2.jsonl (deduplicated, in-window, Babesia-mentioning records).

With --round, reads and writes search/<round>/, takes the seeds from --seed-file
(a screening file; its include decisions) or, with --registry-seeds, from every
non-retired article in articles.jsonl that has a PMID, and leaves out records
handled in earlier rounds.

Usage (from canine-babesiosis-review/):
    python -I scripts/citations.py --start 2016-10-23 --end 2026-10-23 [--extra-seeds PMID ...]
    python -I scripts/citations.py --start 2006-10-23 --end 2016-10-22 --round r4 --registry-seeds
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import PriorIndex, get, norm_title, pubmed_fetch, round_dir  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search"
SEED_PMID = "38695207"
BAB = re.compile(r"babesi|piroplasm|theileria annae", re.I)


def epmc_list(pmid, kind):
    rows, page = [], 1
    while True:
        url = (f"https://www.ebi.ac.uk/europepmc/webservices/rest/MED/{pmid}/{kind}?"
               + urllib.parse.urlencode({"format": "json", "pageSize": 1000, "page": page}))
        d = json.loads(get(url))
        key = "referenceList" if kind == "references" else "citationList"
        sub = "reference" if kind == "references" else "citation"
        items = (d.get(key) or {}).get(sub, [])
        rows += items
        if len(rows) >= d.get("hitCount", 0) or not items:
            break
        page += 1
        time.sleep(0.2)
    time.sleep(0.2)
    return rows


def crossref_title(title):
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(
        {"query.bibliographic": title, "rows": 1, "select": "DOI,title,issued,container-title,type"})
    try:
        items = json.loads(get(url))["message"]["items"]
    except Exception:  # noqa: BLE001
        return None
    if items and norm_title((items[0].get("title") or [""])[0]) == norm_title(title):
        return items[0]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--extra-seeds", nargs="*", default=[])
    ap.add_argument("--round", help="read and write search/<round>/ and leave out records from earlier rounds")
    ap.add_argument("--seed-file", type=Path, default=OUT / "screening_r1.jsonl",
                    help="screening file whose include decisions are the seeds")
    ap.add_argument("--registry-seeds", action="store_true",
                    help="seed from every non-retired article in articles.jsonl with a PMID instead")
    args = ap.parse_args()
    out_dir = round_dir(args.round)
    cands = [json.loads(l) for l in open(out_dir / "candidates.jsonl", encoding="utf-8")]
    known_pmids = {c["pmid"] for c in cands if c.get("pmid")}
    known_titles = {norm_title(c.get("title")) for c in cands}
    if args.registry_seeds:
        arts = [json.loads(l) for l in open(ROOT / "articles.jsonl", encoding="utf-8") if l.strip()]
        base = [a["pmid"] for a in arts if a.get("pmid")]
    else:
        scr = [json.loads(l) for l in open(args.seed_file, encoding="utf-8")]
        base = [s["key"].split(":", 1)[1] for s in scr if s["decision"] == "include" and s["key"].startswith("PMID:")]
    seeds = [SEED_PMID] + base + args.extra_seeds
    seeds = list(dict.fromkeys(seeds))
    hits, new_pmids, title_only = [], {}, {}
    for i, p in enumerate(seeds):
        for kind in ("references", "citations"):
            for r in epmc_list(p, kind):
                pmid = r.get("id") if r.get("source") == "MED" else None
                title = r.get("title") or ""
                year = str(r.get("pubYear") or "")
                rec = {"seed": p, "direction": "backward" if kind == "references" else "forward",
                       "pmid": pmid, "title": title, "year": year, "doi": (r.get("doi") or "").lower() or None}
                if pmid and pmid in known_pmids:
                    continue
                if norm_title(title) in known_titles:
                    continue
                hits.append(rec)
                if pmid:
                    new_pmids.setdefault(pmid, []).append(f"{rec['direction']}:{p}")
                elif BAB.search(title) and year and args.start[:4] <= year <= args.end[:4]:
                    title_only.setdefault(norm_title(title), dict(rec, via=[]))["via"].append(f"{rec['direction']}:{p}")
        if (i + 1) % 20 == 0:
            print(f"{i + 1}/{len(seeds)} seeds, {len(new_pmids)} new PMIDs, {len(title_only)} title-only")
    recs = pubmed_fetch(sorted(new_pmids, key=int))
    out = []
    for r in recs:
        fp = r.get("first_pub_date")
        if not (fp and args.start <= fp <= args.end):
            continue
        if not BAB.search((r.get("title") or "") + " " + (r.get("abstract") or "")):
            continue
        r["found_by"] = ["citation:" + v for v in new_pmids[r["pmid"]]]
        r["in_window"] = True
        out.append(r)
    for t, rec in title_only.items():
        cr = crossref_title(rec["title"])
        time.sleep(0.3)
        out.append({"pmid": None, "doi": (cr or {}).get("DOI", "").lower() or rec.get("doi"),
                    "title": rec["title"], "journal": ((cr or {}).get("container-title") or [None])[0],
                    "first_pub_date": None, "year": rec["year"], "abstract": None,
                    "found_by": ["citation:" + v for v in rec["via"]], "unresolved": cr is None,
                    "source_id": f"REF:{t[:60]}"})
    prior = 0
    if args.round:
        out, prior = PriorIndex(args.round).apply(out, out_dir, "candidates_r2")
    with open(out_dir / "citation_hits.jsonl", "w", encoding="utf-8") as f:
        for h in hits:
            f.write(json.dumps(h, ensure_ascii=False) + "\n")
    with open(out_dir / "candidates_r2.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"seeds={len(seeds)} linked_new={len(hits)} new_pmids={len(new_pmids)} prior_rounds={prior} kept={len(out)}")


if __name__ == "__main__":
    main()
