"""Independent dataset-repository search for canine babesiosis datasets.

Queries public repository APIs (no authentication) and writes:
  search/repo_queries.jsonl  one row per query: repository, query, run date, hit count, error
  search/repo_hits.jsonl     one row per returned record with title, accession, URL and dates

Hits are leads only; each is screened and verified separately before entering datasets.md.

Usage (from canine-babesiosis-review/):
    python -I scripts/repo_search.py
"""
import datetime as dt
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search"
UA = "canine-babesiosis-scoping-review/1.0 (research script; python-urllib)"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def get(url, data=None, headers=None, tries=4):
    for i in range(tries):
        try:
            h = {"User-Agent": UA, **(headers or {})}
            req = urllib.request.Request(url, data=data, headers=h)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:  # noqa: BLE001 - retried and re-raised
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def ncbi(db, term):
    d = json.loads(get(EUTILS + "esearch.fcgi?" + urllib.parse.urlencode(
        {"db": db, "term": term, "retmode": "json", "retmax": 500})))
    ids = d["esearchresult"]["idlist"]
    time.sleep(0.4)
    hits = []
    for i in range(0, len(ids), 100):
        s = json.loads(get(EUTILS + "esummary.fcgi?" + urllib.parse.urlencode(
            {"db": db, "id": ",".join(ids[i:i + 100]), "retmode": "json"})))
        time.sleep(0.4)
        for uid in s["result"].get("uids", []):
            r = s["result"][uid]
            if db == "gds":
                acc = r.get("accession")
                hits.append({"accession": acc, "title": r.get("title"), "summary": (r.get("summary") or "")[:600],
                             "organism": r.get("taxon"), "n_samples": r.get("n_samples"),
                             "pubmed_ids": r.get("pubmedids"), "type": r.get("gdstype"), "date": r.get("pdat"),
                             "url": f"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={acc}"})
            elif db == "bioproject":
                acc = r.get("project_acc")
                hits.append({"accession": acc, "title": r.get("project_title"),
                             "summary": (r.get("project_description") or "")[:600],
                             "organism": r.get("organism_name"), "type": r.get("project_data_type"),
                             "date": r.get("registration_date"),
                             "url": f"https://www.ncbi.nlm.nih.gov/bioproject/{acc}"})
    return int(d["esearchresult"]["count"]), hits


def zenodo(q):
    hits, page, total = [], 1, 0
    while True:
        d = json.loads(get("https://zenodo.org/api/records?" + urllib.parse.urlencode({"q": q, "size": 25, "page": page})))
        total = d["hits"]["total"]
        rows = d["hits"]["hits"]
        hits += [{"accession": h.get("doi"), "title": h["metadata"].get("title"),
                  "type": (h["metadata"].get("resource_type") or {}).get("type"),
                  "date": h["metadata"].get("publication_date"),
                  "related": [r.get("identifier") for r in h["metadata"].get("related_identifiers", [])][:5],
                  "url": h["links"].get("self_html") or h.get("doi_url")} for h in rows]
        if not rows or len(hits) >= total:
            break
        page += 1
        time.sleep(1)
    return total, hits


def figshare(q):
    body = json.dumps({"search_for": q, "page_size": 200}).encode()
    d = json.loads(get("https://api.figshare.com/v2/articles/search", data=body,
                       headers={"Content-Type": "application/json"}))
    hits = [{"accession": h.get("doi"), "title": h.get("title"), "type": h.get("defined_type_name"),
             "date": h.get("published_date"), "url": h.get("url_public_html")} for h in d]
    return len(d), hits


def dryad(q):
    hits, page, total = [], 1, 0
    while True:
        d = json.loads(get("https://datadryad.org/api/v2/search?" + urllib.parse.urlencode(
            {"q": q, "per_page": 100, "page": page})))
        total = d.get("total", 0)
        rows = d.get("_embedded", {}).get("stash:datasets", [])
        hits += [{"accession": r.get("identifier"), "title": r.get("title"), "date": r.get("publicationDate"),
                  "url": "https://datadryad.org/dataset/" + (r.get("identifier") or "")} for r in rows]
        if len(hits) >= total or not rows:
            break
        page += 1
    return total, hits


def pride(q):
    d = json.loads(get("https://www.ebi.ac.uk/pride/ws/archive/v2/search/projects?" + urllib.parse.urlencode(
        {"keyword": q, "pageSize": 100})))
    hits = [{"accession": r.get("accession"), "title": r.get("title"), "organism": r.get("organisms"),
             "date": r.get("publicationDate"),
             "url": f"https://www.ebi.ac.uk/pride/archive/projects/{r.get('accession')}"} for r in d]
    return len(d), hits


def ebisearch(domain, q):
    d = json.loads(get(f"https://www.ebi.ac.uk/ebisearch/ws/rest/{domain}?" + urllib.parse.urlencode(
        {"query": q, "format": "json", "size": 100, "fields": "name,description"})))
    hits = [{"accession": e["id"], "title": (e.get("fields", {}).get("name") or [None])[0],
             "summary": ((e.get("fields", {}).get("description") or [""])[0] or "")[:600],
             "url": f"https://www.ebi.ac.uk/metabolights/{e['id']}"} for e in d.get("entries", [])]
    return d.get("hitCount"), hits


def biostudies(q):
    d = json.loads(get("https://www.ebi.ac.uk/biostudies/api/v1/search?" + urllib.parse.urlencode(
        {"query": q, "pageSize": 100})))
    hits = [{"accession": h.get("accession"), "title": h.get("title"), "type": h.get("type"),
             "date": h.get("release_date"), "files": h.get("files"),
             "url": f"https://www.ebi.ac.uk/biostudies/studies/{h.get('accession')}"} for h in d.get("hits", [])]
    return d.get("totalHits"), hits


def dataverse(q):
    d = json.loads(get("https://dataverse.harvard.edu/api/search?" + urllib.parse.urlencode(
        {"q": q, "type": "dataset", "per_page": 100})))
    items = d.get("data", {}).get("items", [])
    hits = [{"accession": i.get("global_id"), "title": i.get("name"), "date": i.get("published_at"),
             "url": i.get("url")} for i in items]
    return d.get("data", {}).get("total_count"), hits


QUERIES = [
    ("GEO DataSets", "gds", ncbi_gds := (lambda q: ncbi("gds", q)), 'babesia AND ("Canis lupus familiaris"[Organism] OR dog OR dogs OR canine OR "Babesia canis" OR "Babesia gibsoni" OR "Babesia rossi" OR "Babesia vogeli")'),
    ("GEO DataSets", "gds-all-babesia", ncbi_gds, "babesia OR babesiosis"),
    ("NCBI BioProject", "bioproject-host", lambda q: ncbi("bioproject", q), 'babesia AND ("Canis lupus familiaris"[Organism] OR dog OR canine OR canis)'),
    ("NCBI BioProject", "bioproject-species", lambda q: ncbi("bioproject", q), '"Babesia gibsoni"[Organism] OR "Babesia canis"[Organism] OR "Babesia rossi"[Organism] OR "Babesia vogeli"[Organism] OR "Babesia conradae"[Organism] OR "Babesia vulpes"[Organism]'),
    ("Zenodo", "zenodo", zenodo, "babesia AND (dog OR dogs OR canine OR canis)"),
    ("Figshare", "figshare-dog", figshare, "babesia dog"),
    ("Figshare", "figshare-canine", figshare, "canine babesiosis"),
    ("Figshare", "figshare-rossi", figshare, "Babesia rossi"),
    ("Figshare", "figshare-canis", figshare, "Babesia canis"),
    ("Figshare", "figshare-gibsoni", figshare, "Babesia gibsoni"),
    ("Figshare", "figshare-babesiosis", figshare, "babesiosis"),
    ("Dryad", "dryad", dryad, "babesia"),
    ("PRIDE", "pride", pride, "babesia"),
    ("MetaboLights", "metabolights", lambda q: ebisearch("metabolights", q), "babesia OR babesiosis"),
    ("BioStudies", "biostudies", biostudies, 'babesia AND (dog OR canine) AND (dataset OR "supplementary data")'),
    ("Harvard Dataverse", "dataverse", dataverse, "babesia"),
]


def main():
    OUT.mkdir(exist_ok=True)
    run_date = dt.date.today().isoformat()
    qrows, hrows = [], []
    for repo, qid, fn, q in QUERIES:
        try:
            n, hits = fn(q)
            err = None
        except Exception as e:  # noqa: BLE001
            n, hits, err = None, [], f"{type(e).__name__}: {e}"
        qrows.append({"id": qid, "repository": repo, "query": q,
                      "run_date": run_date, "count": n, "returned": len(hits), "error": err})
        for h in hits:
            hrows.append({"query": qid, "repository": repo, **h})
        print(repo, qid, n, len(hits), err or "")
    with open(OUT / "repo_queries.jsonl", "w", encoding="utf-8") as f:
        for q in qrows:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    with open(OUT / "repo_hits.jsonl", "w", encoding="utf-8") as f:
        for h in hrows:
            f.write(json.dumps(h, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
