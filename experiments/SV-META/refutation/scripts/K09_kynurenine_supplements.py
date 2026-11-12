"""K09 refutation check: kynurenine and tryptophan in the CB091 and CB071 supplements.

Reads the published supplementary zips in /core/data/raw (read only, nothing extracted to disk).
- CB091 (Rubic 2022, serum, B. canis, 12 infected vs 12 controls), Table S2A, Biocrates p400 HR:
  Kyn, Trp, Kyn/Trp by group.
- CB071 (Kules 2021, urine, B. canis, kidney-function groups A/B/C vs controls):
  Table 2A (targeted p400): Trp by group (kynurenine not a valid analyte in urine);
  Table 1A (untargeted HILIC-MS): any feature annotated as kynurenine, intensity by group.
Kidney group is a severity proxy (C = azotaemic). Exploratory; no correction claimed beyond the count of tests shown.
Run: experiments/SV-META/env/py/Scripts/python.exe -I <this file>
"""
import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[4]
RAW = ROOT / "core" / "data" / "raw"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
rng = np.random.default_rng(20261112)


def read_xlsx(data: bytes):
    """Return {sheet_name: list of rows (dict col_letter -> value)}."""
    z = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rmap = {r.get("Id"): r.get("Target") for r in rels}
    out = {}
    for sh in wb.find("m:sheets", NS):
        rid = sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        target = rmap[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        root = ET.fromstring(z.read(target))
        rows = []
        for r in root.iter("{%s}row" % NS["m"]):
            row = {}
            for c in r.findall("m:c", NS):
                col = re.match(r"[A-Z]+", c.get("r")).group(0)
                v = c.find("m:v", NS)
                if v is None:
                    isel = c.find("m:is", NS)
                    val = "".join(t.text or "" for t in isel.iter("{%s}t" % NS["m"])) if isel is not None else None
                elif c.get("t") == "s":
                    val = shared[int(v.text)]
                else:
                    val = v.text
                row[col] = val
            rows.append(row)
        out[sh.get("name")] = rows
    return out


def inner(zip_path, member_pattern):
    z = zipfile.ZipFile(zip_path)
    for n in z.namelist():
        if re.search(member_pattern, n):
            data = z.read(n)
            if n.endswith(".zip"):
                return z, data
            return z, data
    raise FileNotFoundError(member_pattern)


def fnum(x):
    try:
        f = float(x)
        return f if np.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def mw(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    delta = 2 * u / (len(a) * len(b)) - 1  # Cliff's delta, a vs b
    return delta, p


def col_letters_to_idx(c):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    return n


def main():
    # ---------------- CB091 serum ----------------
    outer = zipfile.ZipFile(RAW / "S-CB091" / "PMC8835742_supplementaryFiles.zip")
    inner_zip = zipfile.ZipFile(io.BytesIO(outer.read([n for n in outer.namelist() if n.endswith(".zip")][0])))
    s2name = [n for n in inner_zip.namelist() if "S2" in n][0]
    sheets = read_xlsx(inner_zip.read(s2name))
    rows = sheets[[k for k in sheets if "2A" in k][0]]
    header_i = next(i for i, r in enumerate(rows) if "Trp" in r.values() and "Kynurenine" in r.values())
    hdr = rows[header_i]
    cK = next(k for k, v in hdr.items() if v == "Kynurenine")
    cT = next(k for k, v in hdr.items() if v == "Trp")
    grp = {"Control": [], "Disease": []}
    for r in rows[header_i + 1:]:
        g = next((v for v in r.values() if v in grp), None)
        k, t = fnum(r.get(cK)), fnum(r.get(cT))
        if g and k is not None and t is not None and t > 0:
            grp[g].append((k, t, k / t))
    print("CB091 serum (p400), n:", {g: len(v) for g, v in grp.items()})
    for j, name in enumerate(["Kyn", "Trp", "Kyn/Trp"]):
        d = [x[j] for x in grp["Disease"]]
        c = [x[j] for x in grp["Control"]]
        delta, p = mw(d, c)
        print(f"  {name}: median infected {np.median(d):.4g}, controls {np.median(c):.4g}, Cliff delta {delta:+.2f}, MW p {p:.3g}")

    # ---------------- CB071 urine ----------------
    z = zipfile.ZipFile(RAW / "S-CB071" / "PMC8484968_supplementaryFiles.zip")
    t2 = read_xlsx(z.read([n for n in z.namelist() if n.lower().endswith("table_2.xlsx")][0]))
    rows = t2[list(t2)[0]]
    header_i = next(i for i, r in enumerate(rows) if "Trp" in r.values())
    hdr = rows[header_i]
    cT = next(k for k, v in hdr.items() if v == "Trp")
    groups = ["Control", "Disease_A", "Disease_B", "Disease_C"]
    g2 = {g: [] for g in groups}
    for r in rows[header_i + 1:]:
        g = next((v for v in r.values() if v in g2), None)
        t = fnum(r.get(cT))
        if g and t is not None:
            g2[g].append(t)
    print("CB071 urine targeted Trp, n:", {g: len(v) for g, v in g2.items()})
    print("  medians:", {g: round(float(np.median(v)), 4) for g, v in g2.items() if v})
    inf = [g for g in groups[1:] if len(g2[g]) >= 3]
    if len(inf) == 3:
        h, p = stats.kruskal(*[g2[g] for g in inf])
        print(f"  Kruskal-Wallis A/B/C: H {h:.2f}, p {p:.3g}")
        delta, p = mw(g2["Disease_C"], g2["Disease_A"])
        print(f"  C (azotaemic) vs A: Cliff delta {delta:+.2f}, MW p {p:.3g}")

    t1 = read_xlsx(z.read([n for n in z.namelist() if n.lower().endswith("table_1.xlsx")][0]))
    rows = t1[[k for k in t1 if k.startswith("A)")][0]]
    # find group label row
    lab_i = next(i for i, r in enumerate(rows[:30]) if sum(1 for v in r.values() if v and str(v).startswith("Disease_")) >= 10)
    labels = rows[lab_i]
    gcols = {g: [c for c, v in labels.items() if v == g] for g in groups}
    print("CB071 untargeted sample columns:", {g: len(v) for g, v in gcols.items()})
    hits = []
    for r in rows[lab_i + 1:]:
        text = " ".join(str(v) for v in r.values() if v and fnum(v) is None)
        if re.search(r"(^|;|\s)(L-)?Kynurenine(;|$|\s)", text):
            hits.append(r)
    print("  features annotated as kynurenine:", len(hits))
    for r in hits:
        ann = [v for v in r.values() if v and fnum(v) is None][:3]
        vals = {g: [fnum(r.get(c)) for c in gcols[g]] for g in groups}
        vals = {g: [x for x in v if x is not None] for g, v in vals.items()}
        print("   annotation:", " | ".join(a[:80] for a in ann))
        print("    n:", {g: len(v) for g, v in vals.items()}, "medians:", {g: round(float(np.median(v)), 1) for g, v in vals.items() if v})
        inf_ok = all(len(vals[g]) >= 3 for g in groups[1:])
        if inf_ok:
            h, p = stats.kruskal(*[vals[g] for g in groups[1:]])
            dCA, pCA = mw(vals["Disease_C"], vals["Disease_A"])
            dIC, pIC = mw(vals["Disease_A"] + vals["Disease_B"] + vals["Disease_C"], vals["Control"])
            print(f"    KW A/B/C p {p:.3g}; C vs A delta {dCA:+.2f} p {pCA:.3g}; infected vs control delta {dIC:+.2f} p {pIC:.3g}")


if __name__ == "__main__":
    sys.exit(main())
