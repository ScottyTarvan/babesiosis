"""Supplementary OpenAlex title/abstract search (keyless; small shared daily budget).

OpenAlex indexes many regional veterinary journals absent from PubMed/Europe PMC.
Uses the precise title_and_abstract.search filter (not relevance search), pages with a
cursor, and keeps works not already present in earlier candidate files.

Writes search/openalex_queries.jsonl and search/candidates_openalex.jsonl. With --round,
reads and writes search/<round>/, leaves out records handled in earlier rounds, and also
applies the round-3 type and title filter (FILTER below): kept records go to
candidates_r3.jsonl, the counts to openalex_filter_log.json.

Usage (from canine-babesiosis-review/):
    python -I scripts/openalex_search.py --start 2016-10-23 --end 2026-10-23
    python -I scripts/openalex_search.py --start 2006-10-23 --end 2016-10-22 --round r4
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
import urllib.request  # noqa: E402
from search import PriorIndex, norm_title, round_dir  # noqa: E402


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "canine-babesiosis-review/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search"
SEARCH = "(babesia OR babesiosis OR babesiose OR piroplasmosis) AND (dog OR dogs OR canine OR canis)"
FILTER = ("type in (article, review) AND title matches babesi*/piroplasm* with canine term in title or abstract, "
          "OR canine term in title with babesi* in abstract")
BAB = re.compile(r"babesi|piroplasm", re.I)
DOG = re.compile(r"\bdogs?\b|canine|canis|canid|puppy|puppies", re.I)


def passes_filter(r):
    """FILTER: returns None when kept, else the drop reason."""
    if r.get("type") not in ("article", "review"):
        return f"type:{r.get('type')}"
    t, a = r.get("title") or "", r.get("abstract") or ""
    if (BAB.search(t) and (DOG.search(t) or DOG.search(a))) or (DOG.search(t) and BAB.search(a)):
        return None
    return "not babesia+canine in title"


def inverted_to_text(inv):
    if not inv:
        return None
    pos = {}
    for w, idx in inv.items():
        for i in idx:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--round", help="read and write search/<round>/ and leave out records from earlier rounds")
    args = ap.parse_args()
    out_dir = round_dir(args.round)
    known_doi, known_pmid, known_title = set(), set(), set()
    known_files = (("candidates.jsonl", "candidates_r2.jsonl", "candidates_crossref.jsonl") if args.round
                   else ("candidates.jsonl", "candidates_round2_all.jsonl"))
    for fn in known_files:
        if not (out_dir / fn).exists():
            continue
        for l in open(out_dir / fn, encoding="utf-8"):
            c = json.loads(l)
            if c.get("doi"):
                known_doi.add(c["doi"].lower())
            if c.get("pmid"):
                known_pmid.add(str(c["pmid"]))
            known_title.add(norm_title(c.get("title")))
    flt = f"title_and_abstract.search:{SEARCH},from_publication_date:{args.start},to_publication_date:{args.end}"
    # Keyless access allows page= paging (cursor paging now needs an API key; none is created).
    rows, page, total = [], 1, None
    while True:
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode({
            "filter": flt, "per-page": 200, "page": page,
            "select": "id,doi,title,publication_date,type,primary_location,ids,language,abstract_inverted_index,authorships"})
        d = json.loads(get(url))
        total = d["meta"]["count"]
        rows += d["results"]
        if not d["results"] or len(rows) >= total:
            break
        page += 1
        time.sleep(0.5)
    new = []
    for w in rows:
        ids = w.get("ids") or {}
        pmid = (ids.get("pmid") or "").rsplit("/", 1)[-1] or None
        doi = (w.get("doi") or "").replace("https://doi.org/", "").lower() or None
        if (doi and doi in known_doi) or (pmid and pmid in known_pmid) or norm_title(w.get("title")) in known_title:
            continue
        src = ((w.get("primary_location") or {}).get("source") or {})
        new.append({"pmid": pmid, "pmcid": (ids.get("pmcid") or "").rsplit("/", 1)[-1] or None, "doi": doi,
                    "title": w.get("title"), "journal": src.get("display_name"),
                    "authors": [a["author"]["display_name"] for a in w.get("authorships", [])][:30],
                    "first_pub_date": w.get("publication_date"), "type": w.get("type"),
                    "language": [w.get("language")] if w.get("language") else [],
                    "abstract": inverted_to_text(w.get("abstract_inverted_index")),
                    "abstract_source": "OpenAlex abstract_inverted_index (reconstructed)",
                    "source_id": w["id"], "src": "OPENALEX", "found_by": ["OA:title_and_abstract"], "in_window": True})
    prior = 0
    if args.round:
        new, prior = PriorIndex(args.round).apply(new, out_dir, "candidates_openalex")
    q = {"id": "OA:title_and_abstract", "source": "OpenAlex", "query": f"filter={flt}",
         "run_date": dt.date.today().isoformat(), "count": total, "returned": len(rows), "new_vs_prior": len(new)}
    if args.round:
        q["prior_rounds"] = prior
    with open(out_dir / "openalex_queries.jsonl", "w", encoding="utf-8") as f:
        f.write(json.dumps(q, ensure_ascii=False) + "\n")
    with open(out_dir / "candidates_openalex.jsonl", "w", encoding="utf-8") as f:
        for r in new:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"total={total} returned={len(rows)} prior_rounds={prior} new={len(new)}")
    if args.round:
        kept, dropped = [], {}
        for r in new:
            why = passes_filter(r)
            if why:
                dropped[why] = dropped.get(why, 0) + 1
            else:
                kept.append(r)
        with open(out_dir / "candidates_r3.jsonl", "w", encoding="utf-8") as f:
            for r in kept:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        (out_dir / "openalex_filter_log.json").write_text(
            json.dumps({"filter": FILTER, "kept": len(kept), "dropped": dropped}, indent=1), encoding="utf-8")
        print(f"filter kept={len(kept)} dropped={dropped}")


if __name__ == "__main__":
    main()
