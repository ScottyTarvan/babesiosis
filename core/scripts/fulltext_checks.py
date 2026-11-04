"""Full-text data-availability and supplement checks for included articles.

For every included record with a PMCID, retrieves the Europe PMC full-text XML
(open-access subset only; non-OA PMC records return 404 and are logged as such) and
extracts:
  - data availability / availability of data statements
  - supplementary-material items (label, caption, file name, link)
  - external links pointing at data repositories (GEO, SRA/ENA, PRIDE, MetaboLights,
    BioStudies, Zenodo, Figshare, Dryad, Mendeley Data, Dataverse, OSF, GitHub)
  - the abstract and section titles (used only to tell agents what was checked)

Writes search/fulltext_checks.jsonl, one row per included article.

Usage (from canine-babesiosis-review/):
    python -I scripts/fulltext_checks.py search/included_keys.txt [out.jsonl]
where included_keys.txt lists one "PMID:<id>|PMC<id>|DOI:<doi>" key per line. The output defaults
to search/fulltext_checks.jsonl; later rounds write their own (search/r4/fulltext_checks.jsonl).
"""
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import UA  # noqa: E402,F401
import urllib.request  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search"
REPO = re.compile(r"(ncbi\.nlm\.nih\.gov/(geo|sra|bioproject|biosample|nuccore)|ebi\.ac\.uk/(ena|pride|metabolights|biostudies|arrayexpress)"
                  r"|zenodo|figshare|datadryad|dryad|mendeley\.com/datasets|data\.mendeley|dataverse|osf\.io|github\.com"
                  r"|\bGSE\d+|\bPRJ[NED][A-Z]?\d+|\bPXD\d+|\bMTBLS\d+|\bSR[APRSX]\d{5,}|\bE-MTAB-\d+)", re.I)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "canine-babesiosis-scoping-review/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # noqa: BLE001
        return f"error:{type(e).__name__}", b""


def txt(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else ""


def analyse(xml_bytes):
    root = ET.fromstring(xml_bytes)
    das = []
    for sec in root.iter("sec"):
        title = txt(sec.find("title"))
        st = (sec.get("sec-type") or "").lower()
        if "availab" in st or re.search(r"data (availability|access|sharing)|availability of (data|supporting)", title, re.I):
            das.append(txt(sec)[:1500])
    for fn in root.iter("fn"):
        t = txt(fn)
        if re.search(r"data (availability|access)|availability of data", t[:80], re.I):
            das.append(t[:1500])
    for n in root.iter("notes"):
        t = txt(n)
        if re.search(r"data (availability|access)|availability of data", t[:120], re.I):
            das.append(t[:1500])
    supp = []
    for sm in root.iter("supplementary-material"):
        media = sm.find("media")
        href = None
        for el in [sm, media] if media is not None else [sm]:
            for k, v in el.attrib.items():
                if k.endswith("href"):
                    href = v
        supp.append({"label": txt(sm.find("label")), "caption": txt(sm.find("caption"))[:400], "file": href})
    # Some publishers (e.g. BMC) emit bare <media> elements outside <supplementary-material>.
    seen = {s["file"] for s in supp}
    for media in root.iter("media"):
        href = next((v for k, v in media.attrib.items() if k.endswith("href")), None)
        if href and href not in seen:
            seen.add(href)
            supp.append({"label": txt(media.find("label")), "caption": txt(media.find("caption"))[:400], "file": href})
    links = set()
    for el in root.iter():
        for k, v in el.attrib.items():
            if k.endswith("href") and REPO.search(v or ""):
                links.add(v)
    body = txt(root.find("body")) if root.find("body") is not None else ""
    for m in REPO.finditer(body):
        links.add(m.group(0))
    titles = [txt(s.find("title")) for s in root.iter("sec") if s.find("title") is not None][:40]
    return {"data_availability": list(dict.fromkeys(das)), "supplementary": supp,
            "repository_links": sorted(links), "section_titles": titles, "has_body": bool(body)}


def main():
    keys = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
    rows = []
    for line in keys:
        key, pmcid, doi = (line.split("|") + ["", ""])[:3]
        row = {"key": key, "pmcid": pmcid or None, "checked": dt.date.today().isoformat()}
        if pmcid:
            url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
            status, body = fetch(url)
            row["fulltext_url"] = url
            row["fulltext_status"] = status
            if status == 200 and body:
                try:
                    row.update(analyse(body))
                except ET.ParseError as e:
                    row["parse_error"] = str(e)
            time.sleep(0.3)
        else:
            row["fulltext_status"] = "no_pmcid"
        rows.append(row)
        print(key, row.get("fulltext_status"), len(row.get("supplementary", [])), len(row.get("repository_links", [])))
    with open(Path(sys.argv[2]) if len(sys.argv) > 2 else OUT / "fulltext_checks.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
