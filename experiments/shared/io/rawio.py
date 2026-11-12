"""Minimal read-only xlsx/docx readers (stdlib only)."""
import zipfile, io, re
import xml.etree.ElementTree as ET
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

def col2idx(ref):
    s = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in s:
        n = n * 26 + ord(ch) - 64
    return n - 1

def read_xlsx(src):
    """src: path or bytes. Returns {sheet_name: [[cell,...],...]}"""
    z = zipfile.ZipFile(io.BytesIO(src) if isinstance(src, bytes) else src)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            ss.append("".join(t.text or "" for t in si.iter("{%s}t" % NS["m"])))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rid2t = {r.get("Id"): r.get("Target") for r in rels}
    out = {}
    for s in wb.find("m:sheets", NS):
        t = rid2t[s.get("{%s}id" % NS["r"])]
        p = t.lstrip("/") if t.startswith("/") else "xl/" + t
        rows = []
        for row in ET.fromstring(z.read(p)).iter("{%s}row" % NS["m"]):
            cells = []
            for c in row.findall("m:c", NS):
                i = col2idx(c.get("r"))
                v = c.find("m:v", NS)
                if c.get("t") == "s" and v is not None:
                    val = ss[int(v.text)]
                elif c.get("t") == "inlineStr":
                    val = "".join(t.text or "" for t in c.iter("{%s}t" % NS["m"]))
                else:
                    val = v.text if v is not None else None
                while len(cells) < i:
                    cells.append(None)
                cells.append(val)
            rows.append(cells)
        out[s.get("name")] = rows
    return out

def read_docx_tables(src):
    z = zipfile.ZipFile(io.BytesIO(src) if isinstance(src, bytes) else src)
    root = ET.fromstring(z.read("word/document.xml"))
    tables = []
    for tbl in root.iter("{%s}tbl" % NS["w"]):
        rows = []
        for tr in tbl.findall("w:tr", NS):
            rows.append(["".join(t.text or "" for t in tc.iter("{%s}t" % NS["w"])).strip() for tc in tr.findall("w:tc", NS)])
        tables.append(rows)
    return tables

def fnum(x):
    try:
        return float(str(x).replace(",", ".").replace("<", "").replace(">", "").strip())
    except Exception:
        return None
