"""Inspect downloaded dataset files (stdlib only) and summarise their structure.

Supports .xlsx (sheet names, dimensions, header row and first data rows), .csv/.tsv/.txt
(header and row count), .docx (table count, first rows of each table), .zip (member list,
and recursive inspection of supported members in memory), .xls (flagged: BIFF format
needs xlrd, not inspected). Files are read as data only; nothing is executed.

Writes data/inspection/<dataset_id>.json and prints a compact summary.

Usage (from canine-babesiosis-review/):
    python -I scripts/inspect_files.py DS01 [DS02 ...]
"""
import csv
import gzip
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
MAX_ROWS = 6


def col_index(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n - 1


def xlsx(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rmap = {r.get("Id"): r.get("Target") for r in rels}
    sheets = []
    for s in wb.find("m:sheets", NS):
        rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        target = rmap.get(rid, "")
        path = "xl/" + target.lstrip("/").replace("xl/", "") if not target.startswith("/xl/") else target.lstrip("/")
        try:
            root = ET.fromstring(z.read(path))
        except KeyError:
            sheets.append({"name": s.get("name"), "error": f"missing {path}"})
            continue
        rows = root.findall(".//m:sheetData/m:row", NS)
        preview, max_cols = [], 0
        for r in rows:
            vals = {}
            for c in r.findall("m:c", NS):
                v = c.find("m:v", NS)
                t = c.get("t")
                if t == "inlineStr":
                    val = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
                elif v is None:
                    continue
                elif t == "s":
                    val = shared[int(v.text)]
                else:
                    val = v.text
                vals[col_index(c.get("r"))] = val
            if vals:
                max_cols = max(max_cols, max(vals) + 1)
                if len(preview) < MAX_ROWS:
                    preview.append([vals.get(i, "") for i in range(min(max(vals) + 1, 40))])
        sheets.append({"name": s.get("name"), "n_rows": len(rows), "n_cols": max_cols, "preview": preview})
    return {"format": "xlsx", "sheets": sheets}


def docx(data):
    z = zipfile.ZipFile(io.BytesIO(data))
    root = ET.fromstring(z.read("word/document.xml"))
    tables = []
    for tbl in root.iter(f"{{{NS['w']}}}tbl"):
        rows = tbl.findall("w:tr", NS)
        prev = []
        for tr in rows[:MAX_ROWS]:
            prev.append(["".join(t.text or "" for t in tc.iter(f"{{{NS['w']}}}t"))[:40] for tc in tr.findall("w:tc", NS)][:20])
        tables.append({"n_rows": len(rows), "preview": prev})
    paras = ["".join(t.text or "" for t in p.iter(f"{{{NS['w']}}}t")) for p in root.iter(f"{{{NS['w']}}}p")]
    return {"format": "docx", "n_tables": len(tables), "tables": tables[:15],
            "first_text": [p for p in paras if p.strip()][:5]}


def delimited(data, name):
    text = data.decode("utf-8", errors="replace")
    dialect = "\t" if name.lower().endswith((".tsv", ".txt")) and "\t" in text[:2000] else ","
    rows = list(csv.reader(io.StringIO(text), delimiter=dialect))
    return {"format": "delimited", "delimiter": dialect, "n_rows": len(rows),
            "n_cols": max((len(r) for r in rows), default=0), "preview": [r[:30] for r in rows[:MAX_ROWS]]}


def inspect(name, data, depth=0):
    low = name.lower()
    try:
        if low.endswith((".xlsx", ".xlsm")):
            return xlsx(data)
        if low.endswith(".docx"):
            return docx(data)
        if low.endswith((".csv", ".tsv", ".txt")):
            return delimited(data, name)
        if low.endswith(".gz") and depth < 3:
            inner = gzip.decompress(data)
            return dict(inspect(name[:-3], inner, depth + 1), compressed=True, uncompressed_bytes=len(inner))
        if low.endswith(".xls"):
            return {"format": "xls (BIFF)", "note": "legacy Excel; requires xlrd to parse; not inspected"}
        if low.endswith(".zip") and depth < 3:
            z = zipfile.ZipFile(io.BytesIO(data))
            members = [{"name": i.filename, "bytes": i.file_size} for i in z.infolist()]
            inner = {}
            for i in z.infolist():
                if i.file_size < 50 * 1024 * 1024 and not i.is_dir():
                    inner[i.filename] = inspect(i.filename, z.read(i), depth + 1)
            return {"format": "zip", "members": members, "inspected": inner}
        if low.endswith(".pdf"):
            return {"format": "pdf", "note": "document; tables not machine-extracted"}
        return {"format": "other", "head_bytes": data[:80].hex()}
    except Exception as e:  # noqa: BLE001
        return {"format": "error", "error": f"{type(e).__name__}: {e}"}


def main():
    outdir = ROOT / "data" / "inspection"
    outdir.mkdir(parents=True, exist_ok=True)
    for ds in sys.argv[1:]:
        res = {}
        for p in sorted((ROOT / "data" / "raw" / ds).rglob("*")):
            if p.is_file():
                res[p.relative_to(ROOT).as_posix()] = inspect(p.name, p.read_bytes())
        (outdir / f"{ds}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
        for f, r in res.items():
            if r.get("format") == "xlsx":
                print(ds, f, [(s.get("name"), s.get("n_rows"), s.get("n_cols")) for s in r["sheets"]])
            else:
                print(ds, f, r.get("format"), {k: v for k, v in r.items() if k in ("n_rows", "n_cols", "n_tables", "note")})


if __name__ == "__main__":
    main()
