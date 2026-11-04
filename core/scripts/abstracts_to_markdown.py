"""Abstract-only Markdown for articles whose full text could not be retrieved, so data/markdown/ has
one file per article.

For every article in articles.jsonl without a full-text conversion (no row from to_markdown.py in
data/markdown_report.jsonl, or an earlier abstract-only row), writes data/markdown/<ID>.md with the same
front matter fields as the full-text files plus `text_coverage: "abstract only"`, and a body of the title,
the authors' abstract (structured abstracts split at their labels) and the author keywords. MeSH terms go
in the front matter only, since they are indexers' terms rather than article text.

Abstract sources, in order: the search packet record (search/packets/<ID>.json), the background and
human-comparator records (search/background_papers.json, human_papers.json), then, with --fetch, PubMed
(by PMID) or the publisher landing page's description meta tags (by DOI), cached in
data/abstracts_fetched.json. To supply one by hand (e.g. copied from the publisher's page), add
{"<ID>": {"abstract": "...", "source": "manual: <where from>"}} to that file and re-run. The review's own summaries in articles/ are never used: they are paraphrases.

When full text is later retrieved, to_markdown.py overwrites the file and its report row.

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/abstracts_to_markdown.py --fetch
"""
import argparse
import datetime as dt
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import to_markdown as T  # noqa: E402
from assign_ids import pending_articles  # noqa: E402

ROOT = T.ROOT
CACHE = ROOT / "data" / "abstracts_fetched.json"
UA = "canine-babesiosis-review/1.0 (research script)"
# Structured-abstract labels: "OBJECTIVE:", "MATERIALS AND METHODS:", "Background:" ...
LABEL = re.compile(r"(?:^|(?<=[.!?)\]]\s))([A-Z][A-Za-z &/,-]{2,40}):\s+")


def local_records():
    recs = {}
    for f in ("background_papers.json", "human_papers.json"):
        p = ROOT / "search" / f
        if p.exists():
            for r in json.loads(p.read_text(encoding="utf-8")):
                if r.get("pmid"):
                    recs[r["pmid"]] = r
    return recs


def fetch_pubmed(pmid):
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        root = ET.fromstring(r.read())
    parts = []
    for at in root.iter("AbstractText"):
        txt = re.sub(r"\s+", " ", "".join(at.itertext())).strip()
        if txt:
            parts.append(f"{at.get('Label')}: {txt}" if at.get("Label") else txt)
    return " ".join(parts) or None


def fetch_landing(doi):
    url = f"https://doi.org/{doi}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))  # some publishers set cookies during redirects
    with opener.open(req, timeout=60) as r:
        page = r.read(5_000_000).decode("utf-8", "ignore")
    best = None
    for m in re.finditer(r"<meta\s+[^>]*>", page, re.I):
        tag = m.group()
        name = re.search(r'(?:name|property)="([^"]+)"', tag)
        content = re.search(r'content="([^"]*)"', tag, re.S)
        if name and content and name.group(1).lower() in ("dc.description", "citation_abstract", "description", "og:description"):
            text = html.unescape(re.sub(r"<[^>]+>", " ", content.group(1)))
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) > len(best or ""):
                best = text
    # publisher descriptions are sometimes cut with an ellipsis; only a full-length one counts
    return best if best and len(best.split()) >= 60 and not best.endswith(("…", "...")) else None


def format_abstract(text):
    """Split a structured abstract at its labels into '**Label:** text' paragraphs."""
    text = re.sub(r"\s+", " ", text).strip()
    starts = [m for m in LABEL.finditer(text) if m.group(1).isupper() or m.start() == 0 or len(m.group(1).split()) <= 4]
    if len(starts) < 2:
        return text
    paras, prev = [], None
    if starts[0].start() > 0:
        paras.append(text[:starts[0].start()].strip())
    for m in starts:
        if prev:
            paras.append(f"**{prev.group(1).strip().capitalize()}:** {text[prev.end():m.start()].strip()}")
        prev = m
    paras.append(f"**{prev.group(1).strip().capitalize()}:** {text[prev.end():].strip()}")
    return "\n\n".join(p for p in paras if p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="fetch abstracts not stored locally (PubMed, publisher page)")
    args = ap.parse_args()
    arts = [json.loads(l) for l in open(ROOT / "articles.jsonl", encoding="utf-8")] + pending_articles()  # plus assigned IDs not yet extracted
    rows = {r["id"]: r for r in map(json.loads, open(T.REPORT_JSONL, encoding="utf-8"))} if T.REPORT_JSONL.exists() else {}
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    extra = local_records()
    todo = [a for a in arts if a["id"] not in rows or rows[a["id"]].get("source_format") == "abstract"]
    for a in todo:
        rec, source = {}, None
        packet = ROOT / "search" / "packets" / f"{a['id']}.json"
        if packet.exists():
            rec = json.loads(packet.read_text(encoding="utf-8")).get("record") or {}
            source = "search packet record" if rec.get("abstract") else None
        if not rec.get("abstract") and a.get("pmid") in extra:
            rec = {**extra[a["pmid"]], **{k: v for k, v in rec.items() if v}}
            source = "search background/comparator record" if rec.get("abstract") else None
        abstract = rec.get("abstract")
        if not abstract and a["id"] in cache:
            abstract, source = cache[a["id"]]["abstract"], cache[a["id"]]["source"]
        if not abstract and args.fetch:
            for how, fn, key in (("PubMed efetch", fetch_pubmed, a.get("pmid")), ("publisher page description", fetch_landing, a.get("doi"))):
                if not key:
                    continue
                try:
                    abstract = fn(key)
                except Exception as e:  # noqa: BLE001
                    print(a["id"], how, "failed:", type(e).__name__, e)
                time.sleep(0.4)
                if abstract:
                    source = f"{how} ({key}), retrieved {dt.date.today().isoformat()}"
                    cache[a["id"]] = {"abstract": abstract, "source": source}
                    break
        keywords = rec.get("keywords") or []
        body = [f"# {a['title']}", ""]
        if abstract:
            body += ["## Abstract", "", format_abstract(abstract)]
        else:
            body += ["_No abstract or full text could be retrieved for this article._"]
        if keywords:
            body += ["", f"**Keywords:** {'; '.join(keywords)}"]
        md = T.fix_lookalikes("\n".join(body))
        words = len(re.findall(r"\w+", abstract or ""))
        lang = T.language(abstract) if abstract else "none"
        flags = ["abstract_only"] if abstract else ["no_text"]
        if abstract and lang != "en":
            flags.append(f"language:{lang}")
        fm = {"id": a["id"], "title": a["title"], "doi": a.get("doi"), "pmid": a.get("pmid"), "pmcid": a.get("pmcid"),
              "scope_label": a["scope_label"], "include_type": a.get("include_type"),
              "source_format": "abstract", "source_file": None, "source_sha256": None, "source_tier": source,
              "text_coverage": "abstract only; full text not retrieved" if abstract else "title only; no abstract or full text",
              "converter": "abstracts_to_markdown.py",
              "converted_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "language": lang, "title_check": None, "pages": None, "word_count": words, "table_count": 0,
              "sections": ["abstract"] if abstract else [], "removed_sections": [],
              "mesh_terms": rec.get("mesh") or [], "quality": "abstract_only" if abstract else "no_text", "quality_flags": flags}
        (T.OUT / f"{a['id']}.md").write_text(T.front_matter(fm) + md + "\n", encoding="utf-8")
        old = rows.get(a["id"], {})
        rows[a["id"]] = {k: v for k, v in fm.items() if k != "mesh_terms"}
        if old.get("translation"):  # keep the translation record (finish_translations.py); stale if the text changed
            tr = dict(old["translation"])
            tr["stale"] = tr.get("source_body_sha256") != T.body_sha256(T.OUT / f"{a['id']}.md")
            rows[a["id"]]["translation"] = tr
        print(a["id"], fm["quality"], words, "words", source or "")
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    T.write_report([rows[k] for k in sorted(rows)])


if __name__ == "__main__":
    main()
