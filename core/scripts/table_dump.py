"""Dump rows of a downloaded table for review (stdlib only; read-only).

Supports .xlsx sheets, .docx tables, delimited text, optionally gzip-compressed or
inside a zip (use "archive.zip::member/path" and nested "a.zip::b.zip::c.xlsx").

Usage (from canine-babesiosis-review/):
    python -I scripts/table_dump.py <file[::member...]> [--sheet NAME|INDEX] [--rows N] [--cols N]
"""
import argparse
import csv
import gzip
import io
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def load(spec):
    parts = spec.split("::")
    data = Path(parts[0]).read_bytes()
    name = parts[0]
    for p in parts[1:]:
        data = zipfile.ZipFile(io.BytesIO(data)).read(p)
        name = p
    if name.lower().endswith(".gz"):
        data, name = gzip.decompress(data), name[:-3]
    return name, data


def xlsx_rows(data, sheet):
    z = zipfile.ZipFile(io.BytesIO(data))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = [(s.get("name"), rels[s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")])
              for s in wb.find("m:sheets", NS)]
    print("sheets:", [s[0] for s in sheets])
    idx = int(sheet) if sheet is not None and str(sheet).isdigit() else next((i for i, s in enumerate(sheets) if s[0] == sheet), 0)
    target = sheets[idx][1].lstrip("/")
    path = target if target.startswith("xl/") else "xl/" + target
    root = ET.fromstring(z.read(path))
    print("sheet:", sheets[idx][0])
    for r in root.findall(".//m:sheetData/m:row", NS):
        vals = {}
        for c in r.findall("m:c", NS):
            v = c.find("m:v", NS)
            t = c.get("t")
            if t == "inlineStr":
                val = "".join(x.text or "" for x in c.iter(f"{{{NS['m']}}}t"))
            elif v is None:
                continue
            else:
                val = shared[int(v.text)] if t == "s" else v.text
            col = 0
            for ch in re.match(r"[A-Z]+", c.get("r")).group(0):
                col = col * 26 + ord(ch) - 64
            vals[col - 1] = val
        yield [vals.get(i, "") for i in range(max(vals) + 1)] if vals else []


def docx_rows(data, table):
    root = ET.fromstring(zipfile.ZipFile(io.BytesIO(data)).read("word/document.xml"))
    tbls = list(root.iter(f"{{{NS['w']}}}tbl"))
    print("tables:", len(tbls))
    t = tbls[int(table or 0)]
    for tr in t.findall("w:tr", NS):
        yield ["".join(x.text or "" for x in tc.iter(f"{{{NS['w']}}}t")) for tc in tr.findall("w:tc", NS)]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--sheet")
    ap.add_argument("--rows", type=int, default=30)
    ap.add_argument("--cols", type=int, default=60)
    a = ap.parse_args()
    name, data = load(a.spec)
    low = name.lower()
    if low.endswith((".xlsx", ".xlsm")):
        rows = xlsx_rows(data, a.sheet)
    elif low.endswith(".docx"):
        rows = docx_rows(data, a.sheet)
    else:
        text = data.decode("utf-8", errors="replace")
        delim = "\t" if "\t" in text[:2000] else ","
        rows = csv.reader(io.StringIO(text), delimiter=delim)
    n = 0
    for row in rows:
        if n >= a.rows:
            break
        print(" | ".join(str(c)[:24] for c in row[:a.cols]))
        n += 1


if __name__ == "__main__":
    main()
