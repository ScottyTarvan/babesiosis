"""Reproducible literature search for the canine babesiosis scoping review.

Runs documented PubMed (E-utilities), Europe PMC (REST) and OpenAlex queries,
fetches full PubMed records (including abstracts), deduplicates by DOI / PMID /
normalised title, computes first publication date, and writes:

  search/queries.jsonl     one row per query: source, query string, run date, hit count
  search/hits.jsonl        one row per (query, record id) hit
  search/candidates.jsonl  deduplicated candidate records with abstracts

Usage (from canine-babesiosis-review/):
    python -I scripts/search.py --start 2016-10-23 --end 2026-10-23
    python -I scripts/search.py --start 2006-10-23 --end 2016-10-22 --round r4

Only the Python standard library is used. Requests are throttled to respect
NCBI (<=3 req/s without API key), Europe PMC and OpenAlex rate limits.
Without --round, re-running overwrites the search/ outputs. With --round, the
outputs go to search/<round>/ and records already handled in earlier rounds are
left out (see PriorIndex); the rounds and their windows are listed in
search/rounds.json. IDs are assigned later by scripts/assign_ids.py from a
persistent registry, so they never change.
"""
import argparse
import datetime as dt
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search"
UA = "canine-babesiosis-scoping-review/1.0 (research script; python-urllib)"

HOST = '(Dogs[MeSH Terms] OR dog[tiab] OR dogs[tiab] OR canine[tiab] OR canines[tiab] OR canis[tiab] OR puppy[tiab] OR puppies[tiab])'
BAB = '(Babesia[MeSH Terms] OR Babesiosis[MeSH Terms] OR babesia*[tiab] OR babesiosis[tiab] OR babesioses[tiab] OR babesiose*[tiab] OR piroplasm*[tiab])'
SPECIES = ('("Babesia rossi"[tiab] OR "B. rossi"[tiab] OR "Babesia canis rossi"[tiab] OR "Babesia vogeli"[tiab] '
           'OR "B. vogeli"[tiab] OR "Babesia canis vogeli"[tiab] OR "Babesia canis canis"[tiab] OR "Babesia gibsoni"[tiab] '
           'OR "B. gibsoni"[tiab] OR "Babesia conradae"[tiab] OR "Babesia vulpes"[tiab] OR "Theileria annae"[tiab] '
           'OR "Babesia microti-like"[tiab] OR "Babesia negevi"[tiab] OR "Babesia coco"[tiab] OR "large Babesia"[tiab] '
           'OR "Babesia canis"[tiab])')
MECH = ('(pathophysiol*[tiab] OR pathogenes*[tiab] OR inflammat*[tiab] OR cytokine*[tiab] OR chemokine*[tiab] '
        'OR immun*[tiab] OR coagul*[tiab] OR thromb*[tiab] OR platelet*[tiab] OR fibrin*[tiab] OR haemosta*[tiab] '
        'OR hemosta*[tiab] OR kidney[tiab] OR renal[tiab] OR azotaem*[tiab] OR azotem*[tiab] OR proteinuri*[tiab] '
        'OR lung*[tiab] OR pulmonary[tiab] OR respirat*[tiab] OR cerebral[tiab] OR neurolog*[tiab] OR brain[tiab] '
        'OR cardiac[tiab] OR troponin*[tiab] OR myocard*[tiab] OR heart[tiab] OR hepat*[tiab] OR liver[tiab] '
        'OR glucose[tiab] OR hypoglyc*[tiab] OR lactat*[tiab] OR endotheli*[tiab] OR glycocalyx[tiab] '
        'OR oxidat*[tiab] OR anaemi*[tiab] OR anemi*[tiab] OR haemoly*[tiab] OR hemoly*[tiab] OR erythrocyt*[tiab] '
        'OR transcriptom*[tiab] OR proteom*[tiab] OR metabolom*[tiab] OR lipidom*[tiab] OR genom*[tiab] '
        'OR biomarker*[tiab] OR outcome*[tiab] OR mortality[tiab] OR prognos*[tiab] OR severity[tiab] OR complicat*[tiab] '
        'OR hypotension[tiab] OR cortisol[tiab] OR thyroid[tiab] OR acid-base[tiab] OR electrolyte*[tiab] '
        'OR pancreatit*[tiab] OR rhabdomyolysis[tiab] OR "multiple organ"[tiab] OR "acute phase"[tiab] OR "C-reactive"[tiab] '
        'OR sepsis[tiab] OR SIRS[tiab] OR virulen*[tiab] OR histopatholog*[tiab] OR necrops*[tiab] OR autops*[tiab])')

PUBMED_QUERIES = {
    "PM1_broad": f"{BAB} AND {HOST}",
    "PM2_species": SPECIES,
    "PM3_mechanism": f"{BAB} AND {HOST} AND {MECH}",
    "PM4_review": f"{BAB} AND {HOST} AND (Review[pt] OR review[ti])",
}

EPMC_QUERIES = {
    # TITLE_ABS/KW restrict matching to title, abstract and keywords (unrestricted Europe PMC
    # queries also match full-text body and reference lists, which is not a topical signal).
    "EP1_broad": ('(TITLE_ABS:(babesia* OR babesiosis OR babesiose OR piroplasm*) OR KW:(babesia* OR babesiosis)) '
                  'AND (TITLE_ABS:(dog OR dogs OR canine OR canines OR canis OR puppy OR puppies) OR KW:(dog OR dogs OR canine))'),
    "EP2_species": ('TITLE_ABS:("Babesia rossi" OR "Babesia vogeli" OR "Babesia gibsoni" OR "Babesia conradae" '
                    'OR "Babesia vulpes" OR "Theileria annae" OR "Babesia canis" OR "Babesia microti-like" OR "Babesia negevi")'),
}

OPENALEX_QUERIES = {
    "OA1_broad": "babesia dog",
    "OA2_canine": "canine babesiosis",
}


def get(url, data=None, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - retried and re-raised
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def norm_title(t):
    t = (t or "").lower()
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"[^a-z0-9]+", "", t)


# ---------------- Rounds ----------------
def load_rounds():
    """Search rounds and their windows (search/rounds.json)."""
    return json.loads((OUT / "rounds.json").read_text(encoding="utf-8"))["rounds"]


def review_window():
    """Overall review window: earliest round start to latest round end."""
    rounds = load_rounds()
    return min(r["start"] for r in rounds), max(r["end"] for r in rounds)


def round_dir(rnd):
    """Output folder: search/ for the original rounds, search/<round>/ for later window extensions."""
    d = OUT / rnd if rnd else OUT
    d.mkdir(parents=True, exist_ok=True)
    return d


def _key_rec(key):
    kind, _, val = key.partition(":")
    if kind == "PMID":
        return {"pmid": val}
    if kind == "DOI":
        return {"doi": val}
    return {"source_id": key}


def _rec_keys(rec):
    out = []
    if rec.get("pmid"):
        out.append(f"pmid:{rec['pmid']}")
    if rec.get("doi"):
        out.append(f"doi:{rec['doi'].lower()}")
    if rec.get("source_id"):
        out.append(f"sid:{rec['source_id']}")
    t = norm_title(rec.get("title"))
    if len(t) > 20:
        out.append(f"t:{t}")
    return out


class PriorIndex:
    """Records handled in earlier rounds: the screening files and screening inputs in search/
    and in the other search/r*/ folders, plus ids.json and articles.jsonl.

    classify(rec) returns ("registered", id, retired) for a record that already has an article
    ID (kept and flagged, so in-window background papers and retired records are re-checked),
    ("seen", file) for a record screened earlier (left out), or None for a new one. Collected
    but unscreened records (for example OpenAlex works dropped by the type filter) count as new,
    and so do the earlier keys listed in the round's "recheck" entry in search/rounds.json
    (records excluded earlier for being outside the old window).
    """
    # Screening inputs: rounds 1-3 in search/, merged candidates in later round folders.
    SCREENED = {"candidates.jsonl", "candidates_round2_all.jsonl", "candidates_r3.jsonl", "candidates_all.jsonl"}

    def __init__(self, current_round):
        self.reg, self.seen = {}, {}
        recheck = set(next((r.get("recheck", []) for r in load_rounds() if r["id"] == current_round), []))
        reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
        for k, v in reg.items():
            self._add(self.reg, _key_rec(k), (v["id"], bool(v.get("retired"))))
        for l in open(ROOT / "articles.jsonl", encoding="utf-8"):
            if l.strip():
                a = json.loads(l)
                self._add(self.reg, a, (a["id"], False))
        dirs = [OUT] + [d for d in sorted(OUT.glob("r*")) if d.is_dir() and d.name != current_round]
        for d in dirs:
            for p in sorted(d.glob("candidates*.jsonl")):
                for l in open(p, encoding="utf-8"):
                    if not l.strip():
                        continue
                    c = json.loads(l)
                    # Retired keys in ids.json carry no title; take it from the candidate record.
                    hit = next((self.reg[k] for k in _rec_keys(c) if k in self.reg), None)
                    if hit:
                        self._add(self.reg, c, hit)
                    if c.get("key") in recheck:
                        continue
                    if p.name in self.SCREENED and (d == OUT or p.name == "candidates_all.jsonl"):
                        self._add(self.seen, c, f"{d.name}/{p.name}")
            for p in sorted(d.glob("screening*.jsonl")):
                for l in open(p, encoding="utf-8"):
                    if l.strip() and json.loads(l)["key"] not in recheck:
                        self._add(self.seen, _key_rec(json.loads(l)["key"]), f"{d.name}/{p.name}")

    @staticmethod
    def _add(index, rec, val):
        for k in _rec_keys(rec):
            index.setdefault(k, val)

    def classify(self, rec):
        keys = _rec_keys(rec)
        for k in keys:
            if k in self.reg:
                return ("registered",) + self.reg[k]
        for k in keys:
            if k in self.seen:
                return ("seen", self.seen[k])
        return None

    def apply(self, recs, out_dir, name):
        """Flag registered records, leave out seen ones (listed in <name>_prior_overlap.jsonl)."""
        kept, overlap = [], []
        for r in recs:
            c = self.classify(r)
            if c and c[0] == "seen":
                overlap.append({"pmid": r.get("pmid"), "doi": r.get("doi"), "source_id": r.get("source_id"),
                                "title": r.get("title"), "first_pub_date": r.get("first_pub_date"), "seen_in": c[1]})
                continue
            if c:
                r["existing_id"], r["existing_retired"] = c[1], c[2]
            kept.append(r)
        with open(out_dir / f"{name}_prior_overlap.jsonl", "w", encoding="utf-8") as f:
            for o in overlap:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
        return kept, len(overlap)


# ---------------- PubMed ----------------
def pubmed_search(term, mindate, maxdate):
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    # Broad publication-date window; exact first-publication filtering is applied afterwards.
    params = {"db": "pubmed", "term": term, "retmode": "json", "retmax": 10000,
              "datetype": "pdat", "mindate": mindate, "maxdate": maxdate}
    body = urllib.parse.urlencode(params).encode()
    d = json.loads(get(base, data=body))
    time.sleep(0.4)
    return d["esearchresult"]["idlist"], int(d["esearchresult"]["count"])


MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def _date(el):
    if el is None:
        return None
    y = el.findtext("Year")
    if not y:
        md = el.findtext("MedlineDate") or ""
        m = re.search(r"(\d{4})", md)
        return f"{m.group(1)}-01-01" if m else None
    mo = el.findtext("Month") or "1"
    mo = int(mo) if mo.isdigit() else MONTHS.get(mo[:3].lower(), 1)
    da = int(el.findtext("Day") or 1)
    return f"{int(y):04d}-{mo:02d}-{da:02d}"


def _date_precision(el):
    if el is None:
        return None
    if el.findtext("Day"):
        return "day"
    if el.findtext("Month"):
        return "month"
    return "year"


def text_all(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def parse_pubmed(xml_bytes):
    out = []
    root = ET.fromstring(xml_bytes)
    for art in root.findall("PubmedArticle"):
        mc = art.find("MedlineCitation")
        a = mc.find("Article")
        pmid = mc.findtext("PMID")
        ids = {i.get("IdType"): i.text for i in art.findall("PubmedData/ArticleIdList/ArticleId")}
        doi = ids.get("doi")
        if not doi:
            for e in a.findall("ELocationID"):
                if e.get("EIdType") == "doi":
                    doi = e.text
        abst = []
        for at in a.findall("Abstract/AbstractText"):
            lab = at.get("Label")
            abst.append((f"{lab}: " if lab else "") + text_all(at))
        authors = []
        for au in a.findall("AuthorList/Author"):
            if au.findtext("CollectiveName"):
                authors.append(au.findtext("CollectiveName"))
            else:
                authors.append(f"{au.findtext('LastName') or ''} {au.findtext('Initials') or ''}".strip())
        issue_el = a.find("Journal/JournalIssue/PubDate")
        epub_el = None
        for ad in a.findall("ArticleDate"):
            if ad.get("DateType") == "Electronic":
                epub_el = ad
        hist = {}
        for p in art.findall("PubmedData/History/PubMedPubDate"):
            hist[p.get("PubStatus")] = _date(p)
        pts = [p.text for p in a.findall("PublicationTypeList/PublicationType")]
        corrections = []
        for c in mc.findall("CommentsCorrectionsList/CommentsCorrections"):
            rt = c.get("RefType")
            if rt in ("ErratumIn", "RetractionIn", "ExpressionOfConcernIn", "CorrectedandRepublishedIn", "RetractionOf", "ErratumFor"):
                corrections.append({"type": rt, "ref": c.findtext("RefSource"), "pmid": c.findtext("PMID")})
        mesh = [m.findtext("DescriptorName") for m in mc.findall("MeshHeadingList/MeshHeading")]
        kw = [text_all(k) for k in mc.findall("KeywordList/Keyword")]
        issue_date = _date(issue_el)
        epub_date = _date(epub_el)
        cands = [d for d in (epub_date, issue_date) if d]
        # PubMed "pubmed" history date is a fallback only when neither epub nor issue date exists.
        first = min(cands) if cands else hist.get("pubmed")
        out.append({
            "pmid": pmid, "pmcid": ids.get("pmc"), "doi": doi.lower() if doi else None,
            "title": text_all(a.find("ArticleTitle")),
            "authors": authors,
            "journal": a.findtext("Journal/Title"),
            "journal_abbrev": a.findtext("Journal/ISOAbbreviation"),
            "volume": a.findtext("Journal/JournalIssue/Volume"),
            "issue": a.findtext("Journal/JournalIssue/Issue"),
            "pages": a.findtext("Pagination/MedlinePgn"),
            "language": [l.text for l in a.findall("Language")],
            "issue_date": issue_date, "issue_date_precision": _date_precision(issue_el),
            "epub_date": epub_date, "pubmed_entry_date": hist.get("pubmed"),
            "first_pub_date": first,
            "publication_types": pts,
            "mesh": mesh, "keywords": kw,
            "abstract": "\n".join(abst) if abst else None,
            "corrections": corrections,
        })
    return out


def pubmed_fetch(pmids):
    recs = []
    for i in range(0, len(pmids), 150):
        chunk = pmids[i:i + 150]
        body = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"}).encode()
        recs += parse_pubmed(get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", data=body))
        time.sleep(0.4)
    return recs


# ---------------- Europe PMC ----------------
def epmc_search(query, start, end):
    q = f"({query}) AND (FIRST_PDATE:[{start} TO {end}])"
    cursor, rows, total = "*", [], None
    while True:
        url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?" +
               urllib.parse.urlencode({"query": q, "format": "json", "pageSize": 1000,
                                       "cursorMark": cursor, "resultType": "core"}))
        d = json.loads(get(url))
        total = d.get("hitCount")
        res = d.get("resultList", {}).get("result", [])
        rows += res
        nxt = d.get("nextCursorMark")
        if not res or not nxt or nxt == cursor:
            break
        cursor = nxt
        time.sleep(0.3)
    return q, rows, total


def epmc_norm(r):
    return {
        "source_id": f"{r.get('source')}:{r.get('id')}", "src": r.get("source"),
        "pmid": r.get("pmid"), "pmcid": r.get("pmcid"),
        "doi": (r.get("doi") or "").lower() or None,
        "title": r.get("title"), "authors": [a.strip() for a in (r.get("authorString") or "").rstrip(".").split(",") if a.strip()],
        "journal": (r.get("journalInfo") or {}).get("journal", {}).get("title"),
        "first_pub_date": r.get("firstPublicationDate"),
        "epub_date": r.get("electronicPublicationDate"),
        "language": [r.get("language")] if r.get("language") else [],
        "publication_types": (r.get("pubTypeList") or {}).get("pubType", []),
        "abstract": re.sub(r"<[^>]+>", "", r.get("abstractText") or "") or None,
        "is_oa": r.get("isOpenAccess"), "in_epmc": r.get("inEPMC"),
        "has_suppl": r.get("hasSuppl"), "has_data": r.get("hasData"),
    }


# ---------------- OpenAlex ----------------
def openalex_search(query, start, end):
    rows, cursor, total = [], "*", None
    while cursor:
        url = ("https://api.openalex.org/works?" + urllib.parse.urlencode({
            "search": query,
            "filter": f"from_publication_date:{start},to_publication_date:{end}",
            "per-page": 200, "cursor": cursor,
            "select": "id,doi,title,publication_date,type,primary_location,ids,language"}))
        d = json.loads(get(url))
        total = d["meta"]["count"]
        rows += d["results"]
        cursor = d["meta"].get("next_cursor")
        if not d["results"]:
            break
        time.sleep(0.25)
    return rows, total


def oa_norm(w):
    ids = w.get("ids") or {}
    pmid = (ids.get("pmid") or "").rsplit("/", 1)[-1] or None
    pmcid = (ids.get("pmcid") or "").rsplit("/", 1)[-1] or None
    doi = (w.get("doi") or "").replace("https://doi.org/", "").lower() or None
    src = ((w.get("primary_location") or {}).get("source") or {})
    return {"source_id": w["id"], "pmid": pmid, "pmcid": pmcid, "doi": doi, "title": w.get("title"),
            "journal": src.get("display_name"), "first_pub_date": w.get("publication_date"),
            "type": w.get("type"), "language": [w.get("language")] if w.get("language") else []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--round", help="write to search/<round>/ and leave out records from earlier rounds")
    args = ap.parse_args()
    out = round_dir(args.round)
    run_date = dt.date.today().isoformat()
    # Broad PubMed pdat window (one year either side) so records whose issue date and
    # e-pub date straddle the boundaries are captured, then filtered on first_pub_date.
    s_y, e_y = int(args.start[:4]) - 1, int(args.end[:4]) + 1
    queries, hits = [], []
    pm_ids = set()
    for name, q in PUBMED_QUERIES.items():
        ids, n = pubmed_search(q, f"{s_y}/01/01", f"{e_y}/12/31")
        queries.append({"id": name, "source": "PubMed", "query": q,
                        "filters": f"datetype=pdat mindate={s_y}/01/01 maxdate={e_y}/12/31 (then first_pub_date filter)",
                        "run_date": run_date, "count": n})
        hits += [{"query": name, "pmid": i} for i in ids]
        pm_ids |= set(ids)
        print(name, n)
    epmc_rows = {}
    for name, q in EPMC_QUERIES.items():
        full_q, rows, n = epmc_search(q, args.start, args.end)
        queries.append({"id": name, "source": "Europe PMC", "query": full_q, "filters": "resultType=core",
                        "run_date": run_date, "count": n})
        for r in rows:
            nr = epmc_norm(r)
            epmc_rows[nr["source_id"]] = nr
            hits.append({"query": name, "source_id": nr["source_id"], "pmid": nr["pmid"], "doi": nr["doi"]})
        print(name, n)
    oa_rows = {}
    for name, q in OPENALEX_QUERIES.items():
        # OpenAlex now meters keyless use against a small shared daily budget; failures are
        # recorded as a coverage limitation rather than aborting the run (no account is created).
        try:
            rows, n = openalex_search(q, args.start, args.end)
            err = None
        except Exception as e:  # noqa: BLE001
            rows, n, err = [], None, f"{type(e).__name__}: {e}"
        queries.append({"id": name, "source": "OpenAlex", "query": f"search={q}",
                        "filters": f"from_publication_date:{args.start},to_publication_date:{args.end}",
                        "run_date": run_date, "count": n, "error": err})
        for w in rows:
            nr = oa_norm(w)
            oa_rows[nr["source_id"]] = nr
            hits.append({"query": name, "source_id": nr["source_id"], "pmid": nr["pmid"], "doi": nr["doi"]})
        print(name, n)

    # Records found outside PubMed but carrying a PMID are fetched from PubMed for a uniform record.
    extra_pmids = {r["pmid"] for r in list(epmc_rows.values()) + list(oa_rows.values()) if r.get("pmid")}
    all_pmids = sorted(pm_ids | extra_pmids, key=int)
    pm_recs = {r["pmid"]: r for r in pubmed_fetch(all_pmids)}
    # Europe PMC metadata for PubMed records (OA flags, supplement flags, firstPublicationDate).
    epmc_by_pmid = {r["pmid"]: r for r in epmc_rows.values() if r.get("pmid")}

    cands, by_doi, by_title = {}, {}, {}

    def add(rec, found_by):
        key = None
        if rec.get("doi") and rec["doi"] in by_doi:
            key = by_doi[rec["doi"]]
        elif norm_title(rec.get("title")) in by_title:
            key = by_title[norm_title(rec.get("title"))]
        if key is None:
            key = f"PMID:{rec['pmid']}" if rec.get("pmid") else (f"DOI:{rec['doi']}" if rec.get("doi") else rec.get("source_id"))
            cands[key] = dict(rec, found_by=set())
        c = cands[key]
        c["found_by"] |= found_by
        for k, v in rec.items():
            if c.get(k) in (None, [], "") and v not in (None, [], ""):
                c[k] = v
        if c.get("doi"):
            by_doi[c["doi"]] = key
        by_title[norm_title(c.get("title"))] = key

    hit_map = {}
    for h in hits:
        k = h.get("pmid") or h.get("doi") or h.get("source_id")
        hit_map.setdefault(k, set()).add(h["query"])
    for pmid, r in pm_recs.items():
        e = epmc_by_pmid.get(pmid) or {}
        r["epmc_first_pub_date"] = e.get("first_pub_date")
        r["is_oa"], r["has_suppl"] = e.get("is_oa"), e.get("has_suppl")
        add(r, hit_map.get(pmid, set()))
    for r in epmc_rows.values():
        if not r.get("pmid"):
            add(r, hit_map.get(r.get("doi") or r["source_id"], set()) | hit_map.get(r["source_id"], set()))
    for r in oa_rows.values():
        if not r.get("pmid"):
            add(r, hit_map.get(r.get("doi") or r["source_id"], set()) | hit_map.get(r["source_id"], set()))

    kept, out_window = [], 0
    for c in cands.values():
        fp = c.get("first_pub_date")
        c["in_window"] = bool(fp and args.start <= fp <= args.end)
        if c.get("epmc_first_pub_date") and fp and c["epmc_first_pub_date"] != fp:
            c["date_discrepancy"] = f"PubMed-derived {fp} vs Europe PMC firstPublicationDate {c['epmc_first_pub_date']}"
        if c.get("epub_date") and c.get("issue_date") and c["epub_date"] != c["issue_date"]:
            c["online_vs_issue"] = f"online {c['epub_date']}; issue {c['issue_date']} ({c.get('issue_date_precision')})"
        c["found_by"] = sorted(c["found_by"])
        if c["in_window"]:
            kept.append(c)
        else:
            out_window += 1
    kept.sort(key=lambda c: (c.get("first_pub_date") or "", c.get("pmid") or ""))
    in_window, prior = len(kept), 0
    if args.round:
        kept, prior = PriorIndex(args.round).apply(kept, out, "candidates")
    with open(out / "queries.jsonl", "w", encoding="utf-8") as f:
        for q in queries:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    with open(out / "hits.jsonl", "w", encoding="utf-8") as f:
        for h in hits:
            f.write(json.dumps(h, ensure_ascii=False) + "\n")
    with open(out / "candidates.jsonl", "w", encoding="utf-8") as f:
        for c in kept:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"raw hits={len(hits)} unique={len(cands)} in_window={in_window} outside_window={out_window} "
          f"prior_rounds={prior} kept={len(kept)}")


if __name__ == "__main__":
    main()
