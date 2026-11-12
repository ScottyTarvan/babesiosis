"""Fetch the public Ensembl annotation needed to map the fixed gene sets onto the DS06 rows.

Writes into ref/ (once; the analysis reads only ref/ afterwards):
  ref/unsymbolled_lookup.json   Ensembl REST POST /lookup/id for the DS06 rows with no symbol
  ref/symbol_xrefs.json         Ensembl REST /xrefs/symbol (dog, CanFam3.1-lineage Boxer annotation) for every set gene
No user or project detail is sent: only Ensembl gene IDs and gene symbols, with a generic User-Agent.
"""
import gzip, json, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
RAW = Path(r"C:\Workspaces\Babesiosis\core\data\raw\DS06\GSE167201_raw_counts.txt.gz")
REF = HERE / "ref"
SETS = json.loads((HERE / "scripts" / "gene_sets.json").read_text(encoding="utf-8"))
REST = "https://rest.ensembl.org"
SPECIES = "canis_lupus_familiarisboxer"
UA = {"User-Agent": "generic-client", "Content-Type": "application/json", "Accept": "application/json"}


def get(url, data=None):
    for attempt in range(5):
        try:
            if data is None:  # GET through curl (urllib timed out on this machine; curl did not)
                r = subprocess.run(["curl", "-s", "-m", "60", "-A", UA["User-Agent"], "-H", "Accept: application/json", url],
                                   capture_output=True, check=True)
                return json.loads(r.stdout.decode("utf-8"))
            hdr = UA
            req = urllib.request.Request(url, data=data, headers=hdr, method="POST" if data else "GET")
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # rate limit or network: back off
            print("retry", attempt, url, e, file=sys.stderr)
            time.sleep(2 + 3 * attempt)
    raise RuntimeError(url)


def main():
    REF.mkdir(exist_ok=True)
    ids = []
    with gzip.open(RAW, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            rid = line.split("\t", 1)[0]
            ens, sym = rid.split("_", 1)
            if ens == sym:
                ids.append(ens)
    out = {}
    if (REF / "unsymbolled_lookup.json").exists():  # fetched once; delete the file to fetch again
        ids = []
    for i in range(0, len(ids), 1000):
        chunk = ids[i:i + 1000]
        res = get(f"{REST}/lookup/id", json.dumps({"ids": chunk}).encode())
        for k in chunk:
            v = res.get(k)
            out[k] = None if v is None else {"display_name": v.get("display_name"), "description": v.get("description"),
                                             "biotype": v.get("biotype"), "assembly_name": v.get("assembly_name")}
        time.sleep(1)
    if ids:
        (REF / "unsymbolled_lookup.json").write_text(json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
    xr = {}
    for genes in SETS["sets"].values():
        for g in genes:
            print("xref", g, flush=True)
            xr[g] = get(f"{REST}/xrefs/symbol/{SPECIES}/{g}?object_type=gene")
            time.sleep(0.2)
    (REF / "symbol_xrefs.json").write_text(json.dumps(xr, indent=1, sort_keys=True), encoding="utf-8")
    info = get(f"{REST}/info/data")
    (REF / "ensembl_release.json").write_text(json.dumps({"rest_release": info, "species": SPECIES,
                                                          "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}),
                                              encoding="utf-8")
    print("done", flush=True)


if __name__ == "__main__":
    main()
