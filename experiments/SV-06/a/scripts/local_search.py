"""SV-06a local evidence search and reference lookup (deterministic, stdlib only).

For each mechanism (seed list in scripts/mechanisms.json plus agent additions in families/F*.json):
  * keyword hits in the 444 CB appraisal notes (/core/articles/CB*.md) and the CB texts (/core/data/markdown/CB*.md);
  * the canine gene symbols found as master proteins in DS07 B_Proteins.txt (GN= in the description);
  * the canine genes present in DS06 GSE167201_raw_counts.txt.gz (symbol suffix of the Ensembl ID).
Writes out/local_hits.json and out/reference_lookup.json.
"""
import csv, glob, gzip, json, os, re, sys

ROOT = r"C:\Workspaces\Babesiosis"
PKG = os.path.join(ROOT, "experiments", "SV-06", "a")
NOTES = os.path.join(ROOT, "core", "articles")
TEXTS = os.path.join(ROOT, "core", "data", "markdown")
DS07 = os.path.join(ROOT, "core", "data", "raw", "DS07", "B_Proteins.txt")
DS06 = os.path.join(ROOT, "core", "data", "raw", "DS06", "GSE167201_raw_counts.txt.gz")


def load_mechanisms():
    mech = json.load(open(os.path.join(PKG, "scripts", "mechanisms.json"), encoding="utf-8"))["mechanisms"]
    seen = {m["id"] for m in mech}
    for f in sorted(glob.glob(os.path.join(PKG, "families", "F*.json"))):
        fam = json.load(open(f, encoding="utf-8"))
        for row in fam.get("mechanisms", []):
            if row.get("added_by_agent") == "yes" and row["mechanism_id"] not in seen:
                mech.append({"id": row["mechanism_id"], "family": row.get("family", fam.get("family")),
                             "mechanism": row["mechanism"], "keywords": row.get("keywords", []),
                             "genes": row.get("dog_genes", []), "ds07_desc": row.get("ds07_desc", []), "added": True})
                seen.add(row["mechanism_id"])
    return mech


def compile_kw(kws):
    """Left boundary always; right boundary when the keyword ends in a capital or digit (acronyms).
    Case-sensitive when the keyword looks like an acronym (two capitals in a row, capital-digit, or camel case)."""
    out = []
    for k in kws:
        bare = k.replace("\\b", "")
        pat = r"(?<![A-Za-z0-9])" + bare
        if bare[-1].isdigit() or bare[-1].isupper():
            pat += r"(?![A-Za-z0-9])"
        sensitive = re.search(r"[A-Z]{2}|[A-Z]-?\d|[a-z][A-Z]", bare) is not None
        out.append(re.compile(pat, 0 if sensitive else re.IGNORECASE))
    return out


def read_corpus(folder, pattern):
    docs = {}
    for p in sorted(glob.glob(os.path.join(folder, pattern))):
        aid = os.path.basename(p).split("_")[0].split(".")[0]
        txt = open(p, encoding="utf-8", errors="replace").read()
        if folder == TEXTS:  # drop YAML front matter, keep source_format
            fm = re.match(r"---\n(.*?)\n---\n", txt, re.S)
            sf = re.search(r'source_format:\s*"?([^"\n]+)', fm.group(1)).group(1) if fm else "unknown"
            txt = txt[fm.end():] if fm else txt
            docs[aid] = (txt, sf)
        else:
            docs[aid] = (txt, None)
    return docs


def ds07_lookup():
    """Master proteins and master-protein candidates of DS07, with gene symbol (GN=) and description."""
    rows = list(csv.reader(open(DS07, encoding="utf-8", errors="replace"), delimiter="	"))
    h = rows[0]
    i_m, i_acc, i_desc, i_cov = h.index("Master"), h.index("Accession"), h.index("Description"), h.index("Coverage [%]")
    out = []
    for r in rows[1:]:
        if r[i_m] not in ("IsMasterProtein", "IsMasterProteinCandidate"):
            continue
        g = re.search(r"GN=(\S+)", r[i_desc])
        out.append({"gn": g.group(1) if g else "", "accession": r[i_acc],
                    "description": re.sub(r"\s+OS=.*", "", r[i_desc]), "coverage_pct": r[i_cov],
                    "status": "master" if r[i_m] == "IsMasterProtein" else "master_candidate"})
    return out


def ds06_lookup():
    genes = {}
    with gzip.open(DS06, "rt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            ens = line.split("\t", 1)[0]
            sym = ens.split("_", 1)[1] if "_" in ens else ""
            genes.setdefault(sym.upper(), []).append(ens)
    return genes


def main():
    mech = load_mechanisms()
    notes = {k: v for k, v in read_corpus(NOTES, "CB*.md").items()}
    texts = read_corpus(TEXTS, "CB*.md")
    ds07, ds06 = ds07_lookup(), ds06_lookup()
    # description search in DS07 for proteins without a usable GN (by mechanism keyword)
    hits, lookup = {}, {}
    for m in mech:
        pats = compile_kw(m["keywords"])
        nh = sorted(a for a, (t, _) in notes.items() if any(p.search(t) for p in pats))
        th = sorted(a for a, (t, _) in texts.items() if any(p.search(t) for p in pats))
        hits[m["id"]] = {"mechanism": m["mechanism"], "keywords": m["keywords"],
                         "cb_note_hits": nh, "cb_text_hits": th,
                         "cb_text_hits_fulltext": sorted(a for a in th if texts[a][1] != "abstract")}
        g7, g6 = [], []
        dpats = [re.compile(re.escape(d), re.IGNORECASE) for d in m.get("ds07_desc", [])]
        for p in ds07:
            if p["gn"] in m["genes"] or any(dp.match(p["description"]) for dp in dpats):
                g7.append(p)
        for g in m["genes"]:
            for e in ds06.get(g.upper(), []):
                g6.append({"gene": g, "ensembl": e})
        lookup[m["id"]] = {"mechanism": m["mechanism"], "dog_genes": m["genes"], "ds07_master": g7, "ds06_genes": g6}
    meta = {"n_cb_notes": len(notes), "n_cb_texts": len(texts),
            "n_cb_texts_fulltext": sum(1 for _, (t, sf) in texts.items() if sf != "abstract"),
            "n_ds07_master": sum(p["status"] == "master" for p in ds07), "n_ds07_candidate": sum(p["status"] != "master" for p in ds07), "n_ds06_genes": sum(len(v) for v in ds06.values())}
    os.makedirs(os.path.join(PKG, "out"), exist_ok=True)
    json.dump({"meta": meta, "hits": hits}, open(os.path.join(PKG, "out", "local_hits.json"), "w", encoding="utf-8"), indent=1)
    json.dump({"meta": meta, "lookup": lookup}, open(os.path.join(PKG, "out", "reference_lookup.json"), "w", encoding="utf-8"), indent=1)
    print(json.dumps(meta))
    for k in hits:
        print(k, len(hits[k]["cb_note_hits"]), len(hits[k]["cb_text_hits"]),
              [(x["gn"] or x["description"][:20], x["status"][:6]) for x in lookup[k]["ds07_master"]], len(lookup[k]["ds06_genes"]))


if __name__ == "__main__":
    sys.exit(main())
