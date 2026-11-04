"""Supplementary Crossref discovery search for journals not indexed in PubMed/Europe PMC.

Crossref is a DOI registry, not a curated index: relevance ranking is loose and many
records lack abstracts. Only records whose TITLE mentions Babesia/babesiosis/piroplasm
and a canine term (or a canine Babesia species) are kept, and only when they are not
already in search/candidates.jsonl or search/candidates_r2.jsonl.

Writes search/crossref_queries.jsonl and search/candidates_crossref.jsonl. With --round,
reads and writes search/<round>/ and leaves out records handled in earlier rounds.

Crossref dates of retro-digitised archives are often the deposit date, not the original
publication date; records whose Crossref dates span more than a year get "date_spread".

Usage (from canine-babesiosis-review/):
    python -I scripts/crossref_search.py --start 2016-10-23 --end 2026-10-23
    python -I scripts/crossref_search.py --start 2006-10-23 --end 2016-10-22 --round r4
"""
import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import PriorIndex, get, norm_title, round_dir  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search"
QUERIES = ["canine babesiosis", "babesia dogs", "Babesia canis", "Babesia rossi", "Babesia gibsoni",
           "Babesia vogeli", "Babesia vulpes", "babesiosis dogs pathogenesis"]
BAB = re.compile(r"babesi|piroplasm", re.I)
DOG = re.compile(r"\bdogs?\b|canine|canis|canid|puppy|puppies|rossi|vogeli|gibsoni|conradae|vulpes|jackal|wolf|wolves|fox", re.I)


def date_of(item):
    for k in ("published-online", "published-print", "issued"):
        dp = (item.get(k) or {}).get("date-parts") or [[None]]
        if dp[0] and dp[0][0]:
            parts = dp[0] + [1, 1]
            yield k, f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--round", help="read and write search/<round>/ and leave out records from earlier rounds")
    args = ap.parse_args()
    out_dir = round_dir(args.round)
    known_doi, known_title = set(), set()
    for fn in ("candidates.jsonl", "candidates_r2.jsonl"):
        p = out_dir / fn
        if p.exists():
            for l in open(p, encoding="utf-8"):
                c = json.loads(l)
                if c.get("doi"):
                    known_doi.add(c["doi"].lower())
                known_title.add(norm_title(c.get("title")))
    qrows, keep = [], {}
    for q in QUERIES:
        rows, cursor, total = [], "*", None
        while cursor and len(rows) < 1000:
            url = "https://api.crossref.org/works?" + urllib.parse.urlencode({
                "query.bibliographic": q, "rows": 500, "cursor": cursor,
                "filter": f"from-pub-date:{args.start},until-pub-date:{args.end},type:journal-article",
                "select": "DOI,title,container-title,published-online,published-print,issued,author,abstract"})
            m = json.loads(get(url))["message"]
            total = m.get("total-results")
            rows += m.get("items", [])
            cursor = m.get("next-cursor") if m.get("items") else None
            time.sleep(1)
        qrows.append({"id": f"CR:{q}", "source": "Crossref", "query": f"query.bibliographic={q}",
                      "filters": f"from-pub-date:{args.start},until-pub-date:{args.end},type:journal-article; first 1000 by relevance",
                      "run_date": dt.date.today().isoformat(), "count": total, "screened_rows": len(rows)})
        for it in rows:
            title = (it.get("title") or [""])[0]
            doi = (it.get("DOI") or "").lower()
            if not (BAB.search(title) and DOG.search(title)):
                continue
            if doi in known_doi or norm_title(title) in known_title:
                continue
            dates = dict(date_of(it))
            first = min(dates.values()) if dates else None
            if not first or not (args.start <= first <= args.end):
                continue
            rec = keep.setdefault(doi, {
                "pmid": None, "doi": doi, "title": title,
                "journal": (it.get("container-title") or [None])[0],
                "authors": [f"{a.get('family', '')} {a.get('given', '')[:1]}".strip() for a in it.get("author", [])],
                "first_pub_date": first, "crossref_dates": dates,
                "abstract": re.sub(r"<[^>]+>", "", it.get("abstract") or "") or None,
                "language": [it.get("language")] if it.get("language") else [],
                "found_by": [], "in_window": True, "src": "CROSSREF"})
            if dates and int(max(dates.values())[:4]) - int(first[:4]) > 1:
                rec["date_spread"] = True
            rec["found_by"].append(f"CR:{q}")
        print(q, total, len(rows), len(keep))
    recs, prior = list(keep.values()), 0
    if args.round:
        recs, prior = PriorIndex(args.round).apply(recs, out_dir, "candidates_crossref")
    with open(out_dir / "crossref_queries.jsonl", "w", encoding="utf-8") as f:
        for q in qrows:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    with open(out_dir / "candidates_crossref.jsonl", "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"prior_rounds={prior} kept={len(recs)}")


if __name__ == "__main__":
    main()
