"""Tiered full-text retrieval for included articles, with a per-article status log.

Tiers, tried in order until one gives a valid file:
  1. Europe PMC full-text XML (open-access subset), using the PubMed or OpenAlex PMCID.
     Valid only if the XML has a <body> (front-matter-only records are rejected).
     Falls back to Europe PMC's PDF render for the same PMCID.
  2. PDF links from OpenAlex open-access locations (best location first).
  3. Links recorded during the review (articles.jsonl fulltext_url, then source_links), then
     publisher landing pages (OpenAlex landing pages, then doi.org): the page's
     citation_pdf_url meta tag, PDF-like links, or the OJS view->download pattern.
A response is kept only if it really is the claimed type (%PDF header or JATS XML);
HTML "PDF" pages are searched once more for the real PDF link.

Files go to data/fulltext/<ID>/fulltext.xml|.pdf (original bytes, never executed).
Limits: 50 MB per file, 1 GB across data/fulltext. Articles already holding a file are
skipped, so the script can be re-run; a PDF or XML placed in data/fulltext/<ID>/ by hand
is picked up as "manual".

After each run every saved file gets a title check (JATS text, or pdftotext's text of the first
three PDF pages if pdftotext is installed); mismatches are listed in fulltext_missing.md, not deleted.
Landing pages whose citation_title does not match the article are rejected (some DOIs are
registered to the wrong article).

Outputs:
  data/fulltext_openalex.json  cached OpenAlex open-access records, keyed by DOI
  data/fulltext_log.jsonl      appended, one row per attempt (tier, url, outcome)
  data/fulltext_status.jsonl   rewritten, one row per article (current state, file, SHA-256)
  data/fulltext_missing.md     rewritten, articles still without full text, for manual retrieval
Articles are those in articles.jsonl plus assigned IDs not yet extracted (assign_ids.pending_articles(),
scope_label "pending extraction"), so full texts can be fetched before extraction. A pending ID that
replaces a reclassified one (BG -> CB) takes over that ID's file and status ("reused_from").

Usage (from canine-babesiosis-review/):
    python -I scripts/fetch_fulltext.py                 # open-access articles (OpenAlex is_oa or PMCID)
    python -I scripts/fetch_fulltext.py --all           # also try closed articles
    python -I scripts/fetch_fulltext.py --ids CB001 CB004 --limit 20 --refresh-openalex
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import http.cookiejar
import json
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assign_ids import pending_articles  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
FT = ROOT / "data" / "fulltext"
OA_CACHE = ROOT / "data" / "fulltext_openalex.json"
LOG = ROOT / "data" / "fulltext_log.jsonl"
STATUS = ROOT / "data" / "fulltext_status.jsonl"
MISSING = ROOT / "data" / "fulltext_missing.md"
FILE_CAP = 50 * 1024 * 1024
TOTAL_CAP = 1024 * 1024 * 1024
# No "python-urllib" in the UA: mod_security on several small-journal hosts answers 406 to it
UA = "canine-babesiosis-review/1.0 (research script)"
EPMC_XML = "https://www.ebi.ac.uk/europepmc/webservices/rest/{}/fullTextXML"
EPMC_PDF = "https://europepmc.org/backend/ptpmcrender.fcgi?accid={}&blobtype=pdf"
SITEWIDE = re.compile(r"polic|guideline|instruction|review.?system|author|template|copyright|licen[cs]e|form|brochure|ethic|board|call.?for", re.I)
# Recorded source_links that never hold the article: abstract databases, metadata APIs, DOAJ (blocks scripts)
SKIP_RECORDED = re.compile(r"pubmed\.ncbi|api\.crossref|openalex\.org|doaj\.org|europepmc\.org/article/|ebi\.ac\.uk/europepmc/webservices", re.I)
STOP = set("with from into dogs canine babesia babesiosis infected naturally study case report among using associated between".split())
lock = threading.Lock()


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_articles():
    """articles.jsonl plus the assigned IDs not yet extracted (scope_label "pending extraction")."""
    return [json.loads(l) for l in open(ROOT / "articles.jsonl", encoding="utf-8")] + pending_articles()


def reuse_replaced(arts, prev):
    """A pending article that replaces a reclassified ID (BG -> CB) takes over that ID's full-text file and status."""
    for a in arts:
        old = a.get("replaces")
        src = existing(old) if old else None
        if not src or existing(a["id"]):
            continue
        dest = FT / a["id"] / src.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        prev[a["id"]] = dict(prev.get(old, {}), id=a["id"], file=dest.relative_to(ROOT).as_posix(), reused_from=old)
        print(f"{a['id']}: reused {src.relative_to(ROOT).as_posix()} from {old}")


def openalex_records(dois, refresh):
    cache = json.loads(OA_CACHE.read_text(encoding="utf-8")) if OA_CACHE.exists() and not refresh else {}
    todo = [d for d in dois if d not in cache]
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        url = ("https://api.openalex.org/works?per-page=50&select=doi,ids,open_access,best_oa_location,locations"
               "&filter=doi:" + "|".join(chunk))
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
            data = json.load(r)
        for w in data["results"]:
            cache[(w.get("doi") or "").replace("https://doi.org/", "").lower()] = w
        for d in chunk:
            cache.setdefault(d, None)  # not in OpenAlex; cached so it is not re-queried
        time.sleep(0.2)
    OA_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache


def title_words(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return [w for w in re.sub(r"[^a-z0-9 ]", " ", s).split() if len(w) > 3 and w not in STOP]


def title_overlap(title, text):
    """Share of the article's title words found in text; None if text has too little Latin script to judge."""
    letters = [c for c in text if c.isalpha()]
    if not letters or sum(c.isascii() for c in letters) < 0.5 * len(letters):
        return None  # mostly Cyrillic etc.; English title words cannot be expected
    words, have = title_words(title), set(title_words(text))
    if not words or len(have) < 3:
        return None
    return sum(w in have for w in words) / len(words)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta_pdf, self.links, self.title = [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        name = (a.get("name") or "").lower()
        if tag == "meta" and name == "citation_pdf_url" and a.get("content"):
            self.meta_pdf.append(a["content"])
        elif tag == "meta" and name == "citation_title" and a.get("content"):
            self.title = a["content"]
        elif tag in ("a", "iframe", "embed", "object"):
            href = a.get("href") or a.get("src") or a.get("data")
            if href:
                self.links.append(href)


def site(url):
    return ".".join(urllib.parse.urlparse(url).netloc.split(":")[0].split(".")[-2:])


def pdf_candidates(html, base):
    """PDF URLs on a landing page, the page's citation_title (None if absent), and whether the URLs
    came from citation_pdf_url (trusted) rather than a generic link scan."""
    p = LinkParser()
    try:
        p.feed(html)
    except Exception:  # noqa: BLE001 - malformed HTML; use whatever was parsed
        pass
    out = list(p.meta_pdf)
    if not out:  # generic link scan only without a citation_pdf_url; same site, no journal-wide documents
        out = [l for l in p.links if re.search(r"\.pdf($|\?)|/pdf/|/pdfdirect/|/download/|/epdf/", l, re.I)
               and site(urllib.parse.urljoin(base, l)) == site(base) and not SITEWIDE.search(l)]
    urls = []
    for u in out:
        u = urllib.parse.urljoin(base, u.strip())
        # OJS: /article/view/<a>/<b> is an HTML viewer; /article/download/<a>/<b> is the file
        u2 = re.sub(r"/article/view/(\d+)/(\d+)", r"/article/download/\1/\2", u)
        for x in (u2, u):
            if x.startswith("http") and x not in urls:
                urls.append(x)
    return urls[:6], p.title, bool(p.meta_pdf)


def get(opener, url, retry=True):
    url = urllib.parse.quote(url, safe=":/?&=%#+,;@~!$'()*[]")  # some hosts link file names with spaces
    # text/html first: doi.org content negotiation answers 406/404 to application/xml or pdf
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8"})
    try:
        return _read(opener, req)
    except Exception as e:  # noqa: BLE001
        code = getattr(e, "code", None)
        transient = code in (500, 502, 503, 504) or (code is None and isinstance(e, (urllib.error.URLError, ConnectionError, TimeoutError)))
        if not (retry and transient):
            raise
        time.sleep(3)
        return _read(opener, req)


def _read(opener, req):
    with opener.open(req, timeout=60) as r:
        clen = r.headers.get("Content-Length")
        if clen and int(clen) > FILE_CAP:
            raise ValueError("over_50MB")
        data = r.read(FILE_CAP + 1)
        if len(data) > FILE_CAP:
            raise ValueError("over_50MB")
        return data, r.headers.get("Content-Type") or "", r.geturl(), r.status


def kind(data):
    head = data[:2048].lstrip()
    if b"%PDF" in data[:1024]:
        return "pdf"
    if head.startswith(b"<?xml") or head.startswith(b"<article") or head.startswith(b"<!DOCTYPE article"):
        return "xml"
    if b"<html" in head.lower() or b"<!doctype html" in head.lower():
        return "html"
    return "other"


def attempt(art, tier, url, outcome, attempts, **extra):
    row = {"id": art["id"], "tier": tier, "url": url, "outcome": outcome, "time": now(), **extra}
    attempts.append(row)


def try_pdf(opener, art, tier, url, attempts, depth=0, verify=False):
    """Fetch url; return (bytes, final_url) for a real PDF, following one HTML hop.
    verify: reject a PDF whose first pages lack the article title (for generic-scan links)."""
    try:
        data, ctype, final, status = get(opener, url)
    except Exception as e:  # noqa: BLE001
        code = getattr(e, "code", None)
        attempt(art, tier, url, f"error:{code or type(e).__name__}", attempts)
        return None
    k = kind(data)
    if k == "pdf":
        if verify:
            with tempfile.TemporaryDirectory() as tmp:
                p = Path(tmp) / "check.pdf"
                p.write_bytes(data)
                if title_check(art["title"], p) == "low":
                    attempt(art, tier, url, "title_mismatch:pdf", attempts, final_url=final)
                    return None
        return data, final
    if k == "html" and depth == 0:
        cands, page_title, from_meta = pdf_candidates(data.decode("utf-8", "ignore"), final)
        cands = [c for c in cands if c != url]
        # Some DOIs resolve to a different article; trust the page only if its title matches
        ov = title_overlap(art["title"], page_title) if page_title else None
        if ov is not None and ov < 0.5:
            attempt(art, tier, url, f"title_mismatch:{page_title[:60]}", attempts, final_url=final)
            return None
        attempt(art, tier, url, f"html_page:{len(cands)}_pdf_links", attempts, final_url=final)
        for c in cands:
            got = try_pdf(opener, art, tier, c, attempts, depth=1, verify=not from_meta)
            if got:
                return got
        return None
    attempt(art, tier, url, f"not_pdf:{k}:{ctype[:40]}", attempts, final_url=final)
    return None


def oa_locations(w):
    if not w:
        return [], []
    locs = [w.get("best_oa_location")] + (w.get("locations") or [])
    locs = [l for l in locs if l and l.get("is_oa")]
    pdfs, pages = [], []
    for l in locs:
        if l.get("pdf_url") and (l["pdf_url"], l.get("license")) not in pdfs:
            pdfs.append((l["pdf_url"], l.get("license")))
        if l.get("landing_page_url") and (l["landing_page_url"], l.get("license")) not in pages:
            pages.append((l["landing_page_url"], l.get("license")))
    return pdfs, pages


def existing(aid):
    d = FT / aid
    for name in ("fulltext.xml", "fulltext.pdf"):
        if (d / name).exists():
            return d / name
    if d.exists():
        for p in sorted(d.iterdir()):
            if p.suffix.lower() in (".pdf", ".xml"):
                return p
    return None


def total_size():
    return sum(p.stat().st_size for p in FT.rglob("*") if p.is_file()) if FT.exists() else 0


def save(art, data, ext):
    with lock:
        if total_size() + len(data) > TOTAL_CAP:
            return None
        dest = FT / art["id"] / f"fulltext.{ext}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    return dest


def fetch_one(art, w):
    attempts = []
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    pmcid = art.get("pmcid")
    if not pmcid and ((w or {}).get("ids") or {}).get("pmcid"):
        tail = w["ids"]["pmcid"].rstrip("/").rsplit("/", 1)[-1]
        pmcid = tail if tail.upper().startswith("PMC") else f"PMC{tail}"
    # Tier 1: Europe PMC XML
    if pmcid:
        url = EPMC_XML.format(pmcid)
        try:
            data, _, final, _ = get(opener, url)
            if kind(data) == "xml" and b"<body" in data:
                return attempts, data, "xml", "europepmc_xml", url, "see PMC record"
            attempt(art, "europepmc_xml", url, "no_body", attempts)
        except Exception as e:  # noqa: BLE001
            attempt(art, "europepmc_xml", url, f"error:{getattr(e, 'code', None) or type(e).__name__}", attempts)
        # Europe PMC's PDF render: PMC's own pages now block scripted access
        got = try_pdf(opener, art, "europepmc_pdf", EPMC_PDF.format(pmcid), attempts)
        if got:
            return attempts, got[0], "pdf", "europepmc_pdf", got[1], "see PMC record"
    pdfs, pages = oa_locations(w)
    # Tier 2: OpenAlex PDF links
    for url, lic in pdfs:
        got = try_pdf(opener, art, "openalex_pdf", url, attempts)
        if got:
            return attempts, got[0], "pdf", "openalex_pdf", got[1], lic
    seen = {u for u, _ in pdfs}
    # Tier 3a: links recorded during the review (fulltext_url was checked by hand; source_links are pages)
    recorded = [(art["fulltext_url"], False)] if art.get("fulltext_url") else []
    recorded += [(u, True) for u in art.get("source_links") or [] if not SKIP_RECORDED.search(u)]
    for url, verify in recorded:
        if url in seen:
            continue
        seen.add(url)
        got = try_pdf(opener, art, "recorded_link", url, attempts, verify=verify)
        if got:
            return attempts, got[0], "pdf", "recorded_link", got[1], None
    # Tier 3b: landing pages
    doi_url = f"https://doi.org/{art['doi']}" if art.get("doi") else None
    for url, lic in pages + ([(doi_url, None)] if doi_url else []):
        if url in seen:
            continue
        seen.add(url)
        got = try_pdf(opener, art, "landing_page", url, attempts)
        if got:
            return attempts, got[0], "pdf", "landing_page", got[1], lic
    return attempts, None, None, None, None, None


def title_check(title, path):
    """ok / low / unchecked: does the file's first pages carry the article title? Uses pdftotext if installed."""
    if path.suffix.lower() == ".xml":
        text = path.read_text(encoding="utf-8", errors="ignore")[:200000]
    elif shutil.which("pdftotext"):
        try:
            out = subprocess.run(["pdftotext", "-l", "3", "-enc", "UTF-8", str(path), "-"], capture_output=True, timeout=60)
        except Exception:  # noqa: BLE001
            return "unchecked"
        text = out.stdout.decode("utf-8", "ignore")
    else:
        return "unchecked"
    ov = title_overlap(title, text)
    return "unchecked" if ov is None else ("ok" if ov >= 0.6 else "low")


def write_status(arts, oa, prev):
    rows = []
    for a in arts:
        w = oa.get((a.get("doi") or "").lower())
        p = existing(a["id"])
        r = prev.get(a["id"], {})
        row = {"id": a["id"], "doi": a.get("doi"), "pmcid": a.get("pmcid"), "scope_label": a["scope_label"],
               "oa_status": (w or {}).get("open_access", {}).get("oa_status") if w else ("no_doi" if not a.get("doi") else "not_in_openalex")}
        if p:
            data = p.read_bytes()
            row.update({"status": r.get("status") if r.get("file") == p.relative_to(ROOT).as_posix() else "manual",
                        "file": p.relative_to(ROOT).as_posix(), "format": p.suffix.lstrip(".").lower(), "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(), "source_url": r.get("source_url"),
                        "license": r.get("license"), "retrieved_utc": r.get("retrieved_utc")})
            if r.get("reused_from"):
                row["reused_from"] = r["reused_from"]
            if row["status"] in (None, "missing", "failed", "not_attempted"):
                row["status"] = "manual"
            same = r.get("sha256") == row["sha256"] and r.get("title_check")
            row["title_check"] = r["title_check"] if same else title_check(a["title"], p)
        else:
            row.update({"status": r.get("status") if r.get("status") == "failed" else "not_attempted",
                        "last_attempt_utc": r.get("last_attempt_utc"), "last_outcomes": r.get("last_outcomes", [])})
        rows.append(row)
    with open(STATUS, "w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def write_missing(rows, arts):
    by_id = {a["id"]: a for a in arts}
    miss = [r for r in rows if not r.get("file")]
    lines = ["# Articles without full text", "",
             f"Generated {now()} by `scripts/fetch_fulltext.py`. {len(rows) - len(miss)} of {len(rows)} articles have full text.",
             "", "To add one by hand, save the PDF (or JATS XML) as `data/fulltext/<ID>/fulltext.pdf` and re-run the script; it is recorded as `manual`.",
             "", "| ID | Year | Title | Scope | Open access | Status | Last outcomes | Link |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(miss, key=lambda r: (r["status"] != "failed", r["oa_status"] in ("closed", "no_doi", "not_in_openalex"), r["id"])):
        a = by_id[r["id"]]
        link = f"[DOI](https://doi.org/{a['doi']})" if a.get("doi") else (f"[PubMed](https://pubmed.ncbi.nlm.nih.gov/{a['pmid']}/)" if a.get("pmid") else "")
        title = a["title"].replace("|", "/")[:90]
        outs = "; ".join(r.get("last_outcomes") or [])[:80].replace("|", "/")
        lines.append(f"| {r['id']} | {(a.get('first_pub_date') or '')[:4]} | {title} | {r['scope_label']} | {r['oa_status']} | {r['status']} | {outs} | {link} |")
    check = [r for r in rows if r.get("file") and r.get("title_check") != "ok"]
    lines += ["", "## Files to check by eye", "",
              "The article title was not found in the first pages (`low`: scanned, odd font encoding, or possibly the wrong document) "
              "or could not be checked (`unchecked`: non-Latin script, or pdftotext not installed). Delete a wrong file and re-run.",
              "", "| ID | Title | Title check | File |", "|---|---|---|---|"]
    for r in sorted(check, key=lambda r: (r["title_check"] != "low", r["id"])):
        lines.append(f"| {r['id']} | {by_id[r['id']]['title'].replace('|', '/')[:90]} | {r['title_check']} | [{r['format']}](../{r['file']}) |")
    MISSING.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="also try articles OpenAlex marks closed")
    ap.add_argument("--ids", nargs="*", help="only these article IDs")
    ap.add_argument("--limit", type=int, help="at most this many articles (after filtering)")
    ap.add_argument("--retry-failed", action="store_true", help="re-try articles that failed before")
    ap.add_argument("--refresh-openalex", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    arts = load_articles()
    oa = openalex_records(sorted({a["doi"].lower() for a in arts if a.get("doi")}), args.refresh_openalex)
    prev = {}
    if STATUS.exists():
        prev = {r["id"]: r for r in map(json.loads, open(STATUS, encoding="utf-8"))}
    reuse_replaced(arts, prev)

    def eligible(a):
        if args.ids and a["id"] not in args.ids:
            return False
        if existing(a["id"]):
            return False
        if prev.get(a["id"], {}).get("status") == "failed" and not (args.retry_failed or args.ids):
            return False
        w = oa.get((a.get("doi") or "").lower())
        return args.all or bool(a.get("pmcid")) or bool(w and w["open_access"]["is_oa"])

    todo = [a for a in arts if eligible(a)][: args.limit]
    print(f"{len(todo)} articles to fetch")
    done = 0
    with cf.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(fetch_one, a, oa.get((a.get("doi") or "").lower())): a for a in todo}
        for f in cf.as_completed(futs):
            a = futs[f]
            try:
                attempts, data, ext, tier, src, lic = f.result()
            except Exception as e:  # noqa: BLE001
                attempts, data = [{"id": a["id"], "tier": "fatal", "url": None, "outcome": f"error:{type(e).__name__}:{e}", "time": now()}], None
            row = prev.setdefault(a["id"], {"id": a["id"]})
            if data:
                dest = save(a, data, ext)
                if dest:
                    attempts.append({"id": a["id"], "tier": tier, "url": src, "outcome": f"saved:{ext}", "time": now(), "bytes": len(data)})
                    row.update({"status": tier, "file": dest.relative_to(ROOT).as_posix(), "source_url": src,
                                "license": lic, "retrieved_utc": now()})
                else:
                    attempts.append({"id": a["id"], "tier": tier, "url": src, "outcome": "skipped_total_cap", "time": now()})
                    data = None
            if not data:
                row.update({"status": "failed", "last_attempt_utc": now(),
                            "last_outcomes": [f"{x['tier']}:{x['outcome']}" for x in attempts][-4:]})
            with lock, open(LOG, "a", encoding="utf-8") as fh:
                for x in attempts:
                    fh.write(json.dumps(x, ensure_ascii=False) + "\n")
            done += 1
            print(f"[{done}/{len(todo)}] {a['id']} {row['status']}", flush=True)

    rows = write_status(arts, oa, prev)
    write_missing(rows, arts)
    counts = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("status:", dict(sorted(counts.items(), key=lambda kv: -kv[1])))
    print(f"total data/fulltext = {total_size() / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
