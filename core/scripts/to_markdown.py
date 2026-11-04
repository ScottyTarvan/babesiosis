"""Convert retrieved full texts to one sectioned Markdown format for text mining.

Input: data/fulltext_status.jsonl (from fetch_fulltext.py) and the files it lists.
  - JATS XML (Europe PMC): converted directly with ElementTree; sections, lists, tables
    (Markdown pipe tables, colspan/rowspan padded), figure and table captions, table footnotes.
  - PDF: pymupdf4llm (layout mode, page headers/footers off, no OCR), then cleaned: running
    heads and page numbers removed, line-end hyphenation and split paragraphs re-joined,
    bold/italic markers dropped, <sup>/<sub> rewritten as ^x / plain.
Both: headings normalised (known sections -> "## Results" etc., other headings -> "###"),
references and administrative back matter (acknowledgements, funding, conflicts, author
contributions, data availability, supplementary-file listings, footnotes) removed and named
in the front matter. Abbreviation glossaries are kept.

Each output file data/markdown/<ID>.md starts with YAML front matter: identifiers, source
file and SHA-256, converter, language guess, sections found, sections removed, word and
table counts, the fetcher's title check, and quality flags. Quality report:
data/markdown_report.md (readable) and data/markdown_report.jsonl.

Needs pymupdf 2.x (which contains pymupdf4llm) in .venv; see scripts/requirements-markdown.txt.
Usage (from canine-babesiosis-review/):
    .venv/Scripts/python.exe -I scripts/to_markdown.py               # all articles with full text
    .venv/Scripts/python.exe -I scripts/to_markdown.py --ids CB022 CB277
"""
import argparse
import collections
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assign_ids import pending_articles  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "markdown"
STATUS = ROOT / "data" / "fulltext_status.jsonl"
REPORT_MD = ROOT / "data" / "markdown_report.md"
REPORT_JSONL = ROOT / "data" / "markdown_report.jsonl"

# Canonical sections, matched against a heading with numbering and punctuation stripped
CANON = [
    ("abstract", r"abstract|summary|resumo|resumen|rezumat|анотація|аннотация|резюме"),
    ("introduction", r"introduction|background|introdução|introducción|introducere|вступ|введение"),
    ("methods", r"(materials? (and|&) )?methods?|methodology|study design|experimental|materials?|"
                r"materia(l|is) e métodos|material y métodos|materiale? (și|şi|si) metod[ăae]|матеріали.*|материалы.*"),
    ("case", r"(the |index )?case( (\d+|[ivx]+|report|presentation|description|history|details|summary|findings|examination|management))*( and [\w ]+)?|"
             r"relato de caso|descrição do caso|caso cl[ií]nico|prezentare(a)? caz(ului)?"),
    ("results_discussion", r"(results?|observations?|findings) (and|&) discussion"),
    ("results", r"results?|findings|observations?|resultados|rezultate|результати|результаты"),
    ("discussion", r"discussion( and conclusions?)?|(treatment|management) and discussion|discussão|discusión|discuți[ie]|discutii|обговорення|обсуждение"),
    ("conclusion", r"conclusions?|concluding remarks|conclusão|conclusões|conclusiones|concluzi[ie]|висновки|выводы|заключение"),
    ("abbreviations", r"(list of )?abbreviations|glossary"),
]
# Generic headings that mean the case narrative only in case reports (in a cohort study "Treatment" is a methods subsection)
CASE_REPORT_EXTRA = (r"history( and [\w ]+)?|clinical (presentation|history|signs|examination|findings)( and [\w ]+)?|signalment( and [\w ]+)?|"
                     r"examination and treatment|treatment( and (outcome|follow-?up))?|outcome|response to treatment|follow-?up|diagnosis( and treatment)?")
CASE_REPORT = False  # set per article in convert(); each worker process converts one article at a time
REFS = (r"references?|bibliography|literature cited|cited literature|works cited|literature|literatura|kaynaklar|referências( bibliográficas)?|"
        r"referencias( bibliográficas)?|bibliografi[ae]|література|литература|список (використаної )?літератури|список литературы|references and notes|"
        r".{0,40}[\s:]references")  # a references heading merged with the end of the previous item by the layout
BACK = (r"ackno?w\w*|funding( statement| information| sources)?|financial support|conflicts? of interests?.*|competing interests?|"
        r"declaration( of competing interest)?s?|declarations of interest|statements and declarations|ethics declarations|disclosures?|"
        r"author(s|ship)?.?.? contributions?|funding sources?|contributor information|credit authorship.*|"
        r"data availability( statement)?|availability of data.*|(appendix [a-z\d]+\.? )?supplementary (information|materials?|data)|supporting information|associated data|"
        r"footnotes|notes|publisher'?s note|ethics( statement| approval.*)?|ethical (approval|statement).*|consent (for publication|to publish)|"
        r"institutional review board statement|informed consent statement|animal ethics.*|orcid.*|author information|additional information|"
        r"additional files?|electronic supplementary material|source of support.*|article history|correspondence|address for correspondence")
ARTICLE_TYPE = (r"((original|research|review|clinical|short|brief|full length) )?(research )?(article|paper|communication|report|note)|"
                r"case (report|study)|open access|research|review")
FOOTNOTE = re.compile(r"^\*+\s*(corresponding author|correspondence|e-?mail|address for correspondence)", re.I)
# "12. Smith AB, Jones C. Title. J Vet. 2010;..." or "- Smith, A.B. (2010) ..." - surname, initials, and a year
REF_ENTRY = re.compile(r"^(-\s*)?(\[?\d{1,3}[.\])]\s+)?([a-z]{1,3}\s)*[A-ZÀ-Ž][\w'’\-]+(\s[A-ZÀ-Ž][\w'’\-]{2,})?,?\s+([A-ZÀ-Ž][.\-]?\s?){1,3}[,.].*\b(19|20)\d\d\b", re.S)
KEEP_AFTER_REFS = re.compile(r"^(table|figure|fig\.?|appendix|supplementary table)\b", re.I)


def heading_key(text, collapse=False):
    t = re.sub(r"<[^>]+>|[*_`#]", "", text).strip().lower()
    if collapse:  # before numbering is stripped, or the "I" of "I ntroduction" reads as a Roman numeral
        t = collapse_letters(t)
    t = re.sub(r"^(\d+(\.\d+)*|[ivx]+)[.)]?\s*\|?\s+", "", t)  # "2.1 Methods", "IV. Results", "1 | INTRODUCTION"
    return re.sub(r"[\s:.’']+$", "", t).strip()


def collapse_letters(k):
    """Undo spaced or small-caps PDF headings: "o r i g i n a l" -> "original", "r esults a nd d iscussion" -> "results and discussion"."""
    if re.fullmatch(r"(\w )+\w", k):
        return k.replace(" ", "")
    return re.sub(r"(?<!\w)(\w) (?=\w{2,})", r"\1", k)


def classify(text):
    for cand in dict.fromkeys((heading_key(text), heading_key(text, collapse=True))):
        if re.fullmatch(REFS, cand):
            return "references"
        if re.fullmatch(BACK, cand):
            return "back"
        for name, pat in CANON:
            if re.fullmatch(pat, cand):
                return name
        if CASE_REPORT and re.fullmatch(CASE_REPORT_EXTRA, cand):
            return "case"
    return None


# ---------- JATS ----------

def text_of(el):
    """Inline text; citation xrefs dropped, sup -> ^x, everything else flattened."""
    if el is None:
        return ""
    out = [el.text or ""]
    for ch in el:
        if ch.tag == "xref" and ch.get("ref-type") in ("bibr", "fn"):
            pass
        elif ch.tag == "sup":
            inner = text_of(ch).strip()
            out.append(f"^{inner}" if inner else "")
        elif ch.tag in ("table-wrap", "fig", "list", "disp-formula"):
            pass  # block content inside <p> is emitted separately
        else:
            out.append(text_of(ch))
        out.append(ch.tail or "")
    s = re.sub(r"\s+", " ", "".join(out))
    # brackets left empty by dropped citations: "[, ]", "( ; )", "^,"
    s = re.sub(r"\s?[\[(]\s*(?:[,;–\-]\s*)*[\])]", "", s)
    return re.sub(r"\^[,–\-\s]*(?=\s|$|[.,;])", "", s)


def md_table(table):
    """<table> -> Markdown pipe table, padding colspan/rowspan cells."""
    grid, pending = [], {}
    for tr in table.iter("tr"):
        row, col = [], 0
        it = iter([c for c in tr if c.tag in ("th", "td")])
        while True:
            while col in pending:
                row.append("")
                pending[col] -= 1
                if not pending[col]:
                    del pending[col]
                col += 1
            c = next(it, None)
            if c is None:
                break
            txt = text_of(c).strip().replace("|", "/")
            span, rspan = int(c.get("colspan", 1) or 1), int(c.get("rowspan", 1) or 1)
            for i in range(span):
                row.append(txt if i == 0 else "")
                if rspan > 1:
                    pending[col] = rspan - 1
                col += 1
        if row:
            grid.append(row)
    if not grid:
        return ""
    width = max(len(r) for r in grid)
    grid = [r + [""] * (width - len(r)) for r in grid]
    lines = ["| " + " | ".join(grid[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(r) + " |" for r in grid[1:]]
    return "\n".join(lines)


def jats_blocks(el, depth, out, removed, tables):
    for ch in el:
        tag = ch.tag
        if tag == "sec":
            t = ch.find("title")
            title = text_of(t).strip() if t is not None else ""
            kind = classify(title) if title else None
            if kind in ("references", "back"):
                removed.append(title)
                continue
            if title:
                # known sections are normalised only at the top level; nested ones keep their own title
                out.append(f"## {CANON_TITLE[kind]}" if kind and depth == 0 else f"{'#' * min(depth + 2, 4)} {title}")
            jats_blocks(ch, depth + 1, out, removed, tables)
        elif tag == "p":
            txt = text_of(ch).strip()
            if txt:
                out.append(txt)
            jats_blocks(ch, depth, out, removed, tables)  # tables/lists nested in <p>
        elif tag == "list":
            for li in ch.findall("list-item"):
                out.append("- " + " ".join(text_of(p).strip() for p in li.findall(".//p") or [li]))
        elif tag == "table-wrap":
            tables.append(1)
            label = text_of(ch.find("label")).strip() if ch.find("label") is not None else "Table"
            cap = " ".join(text_of(x).strip() for x in ch.findall("caption/*"))
            out.append(f"**{label}.** {cap}".strip())
            for tb in ch.iter("table"):
                out.append(md_table(tb))
            for fn in ch.findall("table-wrap-foot//p") + ch.findall("table-wrap-foot/fn"):
                txt = text_of(fn).strip()
                if txt:
                    out.append(f"> {txt}")
        elif tag == "fig":
            label = text_of(ch.find("label")).strip() if ch.find("label") is not None else "Figure"
            cap = " ".join(text_of(x).strip() for x in ch.findall("caption/*"))
            if cap:
                out.append(f"**{label}.** {cap}")
        elif tag in ("disp-quote", "boxed-text", "statement"):
            jats_blocks(ch, depth, out, removed, tables)
        elif tag == "def-list":
            for item in ch.findall("def-item"):
                out.append(f"- {text_of(item.find('term')).strip()}: {text_of(item.find('def')).strip()}")
        elif tag in ("ref-list", "ack", "fn-group", "notes"):
            t = ch.find("title")
            removed.append(text_of(t).strip() if t is not None else tag)


CANON_TITLE = {"abstract": "Abstract", "introduction": "Introduction", "methods": "Methods", "case": "Case presentation",
               "results_discussion": "Results and discussion", "results": "Results", "discussion": "Discussion",
               "conclusion": "Conclusion", "abbreviations": "Abbreviations"}


def convert_jats(path):
    root = ET.parse(path).getroot()
    out, removed, tables = [], [], []
    abstracts = root.findall(".//front/article-meta/abstract")
    main = [a for a in abstracts if not a.get("abstract-type")] or abstracts[:1]
    for a in main:
        out.append("## Abstract")
        sub = []
        for ch in a:
            if ch.tag == "sec":
                t = ch.find("title")
                if t is not None:
                    sub.append(f"**{text_of(t).strip()}** " + " ".join(text_of(p).strip() for p in ch.findall("p")))
                else:
                    sub += [text_of(p).strip() for p in ch.findall("p")]
            elif ch.tag == "p":
                sub.append(text_of(ch).strip())
        out += [s for s in sub if s]
    body = root.find("body")
    if body is not None:
        jats_blocks(body, 0, out, removed, tables)
    back = root.find("back")
    for ch in back if back is not None else []:
        if ch.tag == "glossary":
            out.append("## Abbreviations")
            jats_blocks(ch, 1, out, removed, tables)
        elif ch.tag == "app-group":
            out.append("## Appendix")
            jats_blocks(ch, 1, out, removed, tables)
        else:  # sec, ref-list, ack, fn-group, notes: kept or removed by jats_blocks' rules
            jats_blocks([ch], 0, out, removed, tables)
    floats = root.find("floats-group")
    if floats is not None:
        out.append("## Tables and figures")
        jats_blocks(floats, 1, out, removed, tables)
    had_refs = root.find(".//ref-list") is not None
    return "\n\n".join(out), removed, len(tables), had_refs, None


# ---------- PDF ----------

def convert_pdf(path, title):
    import pymupdf  # imported here so the JATS path needs only the standard library
    import pymupdf4llm
    with pymupdf.open(path) as doc:
        pages = doc.page_count
        md = pymupdf4llm.to_markdown(doc, header=False, footer=False, use_ocr=False)
    return clean_pdf_md(md, pages, title)


def strip_inline(s):
    s = re.sub(r"<sup>(.*?)</sup>", lambda m: f"^{m.group(1)}" if m.group(1).strip() else "", s)
    s = s.replace("<br>", " ")
    s = re.sub(r"</?(sub|span|em|strong|i|b|u|mark|s|small)\b[^>]*>", "", s)
    s = re.sub(r"\*\*|__", "", s)
    s = re.sub(r"(?<![\w*])_(?!\s)(.+?)(?<!\s)_(?![\w*])", r"\1", s)  # _italic_
    return re.sub(r"[ \t]{2,}", " ", s)


def clean_pdf_md(md, pages, title):
    lines = [l.rstrip() for l in md.splitlines()]
    # running heads: short non-table lines repeated on several pages (page numbers ignored), bare page numbers,
    # the PDF's own title and article-type label (the file gets its title from articles.jsonl), corresponding-author notes
    norm = lambda l: re.sub(r"[\d\W_]+", " ", strip_inline(l)).strip().lower()
    counts = collections.Counter(norm(l) for l in lines if l.strip() and not l.lstrip().startswith("|"))
    tw = set(re.findall(r"\w{4,}", title.lower()))
    def drop(l):
        n, bare = norm(l), strip_inline(l).strip("# ").strip()
        if not bare:
            return False
        if re.fullmatch(r"(page\s*)?\d{1,4}(\s*(of|/)\s*\d{1,4})?", bare, re.I) or FOOTNOTE.match(bare):
            return True
        nw = set(re.findall(r"\w{4,}", n))
        if l.startswith("#") and (re.fullmatch(ARTICLE_TYPE, n) or re.fullmatch(ARTICLE_TYPE.replace(" ", ""), n.replace(" ", "")) or
                                  (tw and len(nw & tw) >= 0.7 * len(tw))):
            return True
        if tw and len(nw & tw) >= 0.9 * len(tw) and len(nw) <= len(tw) + 3:  # title repeated as a running line
            return True
        return (counts[n] >= 2 and len(bare) < 140 and not l.lstrip().startswith("|")
                and (l.startswith("#") or re.search(r"journal|vol\.?|issn|doi|http|www\.|\b(19|20)\d\d\b|page|pp\.", bare, re.I)))
    lines = [l for l in lines if not drop(l)]
    # paragraphs, joining ones split by page or column breaks
    paras, cur = [], []
    for l in lines + [""]:
        if l.strip():
            cur.append(l.strip())
        elif cur:
            paras.append(cur)
            cur = []
    blocks = []
    for p in paras:
        is_table = p[0].startswith("|")
        text = "\n".join(p) if is_table else " ".join(p)
        if blocks and not is_table and not text.startswith(("#", "- ", "* ", ">")):
            prev = blocks[-1]
            if not prev.startswith(("#", "|")):
                if re.search(r"\w-$", prev) and re.match(r"[a-z]", text):
                    blocks[-1] = prev[:-1] + text
                    continue
                if not re.search(r"[.:;?!)\]]$", prev) and re.match(r"[a-z(\d]", text):
                    blocks[-1] = prev + " " + text
                    continue
        blocks.append(text)
    blocks = [re.sub(r"(\w)- (?=[a-z])", r"\1", b) if not b.startswith("|") else b for b in blocks]  # in-line hyphenation
    # Skipping: after a references heading, until the next known section, table or figure (layout often puts
    # tables after the reference list). After an administrative heading, only its own short text: these often sit
    # mid-article as first-page footnotes, so skipping stops at any heading, a continued sentence or a long block.
    out, removed, tables, skipping, had_refs, last_kind = [], [], 0, None, False, None
    for b in blocks:
        # "References" / "Conflict of interest" set as a bold lead-in or a short bold line rather than a heading
        lead = re.match(r"^(?:[-*] )?\*\*(.{2,60}?)\*\*", b)
        if not b.startswith("#") and lead and classify(lead.group(1)) in ("references", "back"):
            kind = classify(lead.group(1))
            removed.append(strip_inline(lead.group(1)).strip())
            had_refs |= kind == "references"
            skipping = "refs" if kind == "references" or skipping == "refs" else "back"
            continue
        if b.startswith("#"):
            head = strip_inline(b.lstrip("#").strip())
            kind = classify(head)
            if kind in ("references", "back"):
                removed.append(head)
                had_refs |= kind == "references"
                skipping = "refs" if kind == "references" or skipping == "refs" else "back"
                continue
            if skipping == "refs" and not (kind or KEEP_AFTER_REFS.match(head)):
                continue
            skipping = None
            # a repeat of the current section ("2.2 Methodologies" under "2 Materials and methods") stays a subheading
            out.append(f"## {CANON_TITLE[kind]}" if kind and kind != last_kind else f"### {head}")
            last_kind = kind or last_kind
            continue
        if b.startswith("|"):
            rows = [r for r in b.splitlines() if not re.fullmatch(r"\|(-+\|)+", r.strip())]
            refs = sum(any(REF_ENTRY.match(c.strip()) for c in r.strip("|").split("|")) for r in rows)
            if len(rows) >= 2 and refs >= 0.5 * len(rows):  # a reference list laid out as a table
                removed.append(f"(reference list laid out as a table, {len(rows)} rows)")
                had_refs = True
                continue
            tables += 1
            skipping = None  # tables placed after the reference list are kept
            out.append("\n".join(strip_inline(r) for r in b.splitlines()))
            continue
        text = strip_inline(b)
        if skipping == "refs" and not KEEP_AFTER_REFS.match(text):
            continue
        if skipping == "back" and not (re.match(r"[a-z\d(]", text) or len(text.split()) > 150):
            continue
        skipping = None
        out.append(text)
    # reference entries left at the end (no recognisable heading, or the tail of a list split by a column break):
    # 2+ reference-like entries, or one numbered entry; up to 3 short trailing lines after them (licence,
    # "Conflict of interest: none", an entry the pattern misses) go too. Repeated, because interleaved columns
    # put such short lines between runs of entries.
    while True:
        tail = 0
        while tail < min(3, len(out)) and not REF_ENTRY.match(out[-1 - tail]) and len(out[-1 - tail].split()) < 40:
            tail += 1
        n = 0
        while tail + n < len(out) and REF_ENTRY.match(out[-1 - tail - n]):
            n += 1
        if not (n >= 2 or (n == 1 and re.match(r"(-\s*)?\[?\d{1,3}[.\])]", out[-1 - tail]))):
            break
        out = out[:-(n + tail)]
        removed.append(f"(unlabelled reference list, {n + tail} entries)")
        had_refs = True
    return "\n\n".join(out), removed, tables, had_refs, pages


# ---------- checks and output ----------

# Cyrillic letters that look Latin. Papers typeset in Cyrillic fonts mix them into Latin words ("Babesiа",
# "Вabesia", "Р < 0,05"), which then fail to match the real word.
LOOKALIKE = str.maketrans("АВЕКМНОРСТХаеорсухіІЅѕјЈ", "ABEKMHOPCTXaeopcyxiISsjJ")


def fix_lookalikes(s):
    def word(m):
        w = m.group()
        lat = sum(c.isascii() and c.isalpha() for c in w)
        cyr = sum("Ѐ" <= c <= "ӿ" for c in w)
        return w.translate(LOOKALIKE) if lat and cyr and lat >= cyr else w
    s = re.sub(r"\w+", word, s)
    return re.sub(r"(?<![\wЀ-ӿ])Р(?=\s*[<>≤≥=])", "P", s)


EN_STOP = set("the and of in with was were to for that this is are by from on as at an be or which".split())


def language(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return "none"
    latin = sum(c.isascii() for c in letters) / len(letters)
    if latin < 0.5:
        cyr = sum("Ѐ" <= c <= "ӿ" for c in letters) / len(letters)
        return "cyrillic" if cyr > 0.3 else "non-latin"
    words = re.findall(r"[a-z]+", text.lower())
    return "en" if words and sum(w in EN_STOP for w in words) / len(words) > 0.08 else "non-english-latin"


def quality(md, sections, art, st, had_refs, pages, fmt):
    flags = []
    body = re.sub(r"(?m)^\|.*$", "", md)
    words = len(re.findall(r"\w+", body))
    bad = sum(1 for c in md if c == "�" or "" <= c <= "")
    if bad > 0.005 * max(1, len(md)):
        flags.append("garbled_text")  # fonts without a Unicode map; needs OCR
    lang = language(body)
    if lang != "en":
        flags.append(f"language:{lang}")
    if fmt == "pdf" and pages and words / pages < 120:
        flags.append("little_text_per_page")  # likely scanned
    if words < 800:
        flags.append("short_text")
    core = {"introduction", "methods", "results", "discussion", "case", "results_discussion"}
    if not core & set(sections):
        flags.append("no_sections_detected")
    elif art.get("include_type") != "review" and not {"results", "case", "results_discussion"} & set(sections):
        flags.append("no_results_or_case_section")
    if not had_refs:
        flags.append("references_not_found")
    if st.get("title_check") != "ok":
        flags.append(f"title_check:{st.get('title_check')}")
    return flags, words, lang


def yaml_val(v):
    if isinstance(v, list):
        return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in v) + "]"
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    return json.dumps(str(v), ensure_ascii=False)


def convert(args):
    global CASE_REPORT
    art, st, versions = args
    CASE_REPORT = art.get("include_type") == "case_report"
    src = ROOT / st["file"]
    fmt = "jats_xml" if src.suffix.lower() == ".xml" else "pdf"
    try:
        md, removed, ntables, had_refs, pages = convert_jats(src) if fmt == "jats_xml" else convert_pdf(src, art["title"])
    except Exception as e:  # noqa: BLE001
        return {"id": art["id"], "error": f"{type(e).__name__}: {e}"}
    md = fix_lookalikes(md)
    sections =[s for s in (classify(h) for h in re.findall(r"(?m)^## (.+)$", md)) if s]
    flags, words, lang = quality(md, sections, art, st, had_refs, pages, fmt)
    fm = {"id": art["id"], "title": art["title"], "doi": art.get("doi"), "pmid": art.get("pmid"), "pmcid": art.get("pmcid"),
          "scope_label": art["scope_label"], "include_type": art.get("include_type"),
          "source_format": fmt, "source_file": st["file"], "source_sha256": st["sha256"], "source_tier": st["status"],
          "converter": "to_markdown.py JATS (stdlib)" if fmt == "jats_xml" else f"to_markdown.py + pymupdf4llm {versions}",
          "converted_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
          "language": lang, "title_check": st.get("title_check"), "pages": pages, "word_count": words, "table_count": ntables,
          "sections": sorted(set(sections), key=sections.index), "removed_sections": removed,
          "quality": "review" if flags else "ok", "quality_flags": flags}
    text = front_matter(fm) + f"# {art['title']}\n\n" + md.strip() + "\n"
    (OUT / f"{art['id']}.md").write_text(text, encoding="utf-8")
    return fm


def write_report(rows):
    with open(REPORT_JSONL, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    abstract_rows = [r for r in rows if r.get("source_format") == "abstract"]
    full = [r for r in rows if r.get("source_format") != "abstract"]
    ok = [r for r in full if r.get("quality") == "ok"]
    flagc = collections.Counter(f.split(":")[0] if not f.startswith(("language", "title_check")) else f for r in full for f in r.get("quality_flags", []))
    L = ["# Markdown conversion report", "",
         f"Generated {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')} by `scripts/to_markdown.py`. "
         f"{len(rows)} articles: {len(full)} from full text ({sum(r.get('source_format') == 'jats_xml' for r in rows)} JATS XML, "
         f"{sum(r.get('source_format') == 'pdf' for r in rows)} PDF), of which {len(ok)} pass every check; "
         f"{len(abstract_rows)} abstract-only (full text not retrieved; see the last section).", "",
         "## Flags", "", "| Flag | Articles | Meaning |", "|---|---|---|"]
    meaning = {"garbled_text": "PDF fonts lack a Unicode map; text is unusable without OCR",
               "little_text_per_page": "probably scanned pages; needs OCR",
               "short_text": "under 800 words (short case reports, or incomplete text)",
               "no_sections_detected": "no standard section headings found; text is one block",
               "no_results_or_case_section": "primary study or case report without a Results or Case heading",
               "references_not_found": "no reference heading found; reference list may remain in the text"}
    for f, n in flagc.most_common():
        m = meaning.get(f, "not English; translate or use a multilingual model" if f.startswith("language") else
                        "fetcher could not confirm the title (see fulltext_missing.md)" if f.startswith("title_check") else "")
        L.append(f"| `{f}` | {n} | {m} |")
    L += ["", "## Articles to review", "", "| ID | Source | Words | Tables | Sections | Flags |", "|---|---|---|---|---|---|"]
    for r in sorted((r for r in full if r.get("quality") != "ok"), key=lambda r: (-len(r.get("quality_flags", [])), r["id"])):
        if "error" in r:
            L.append(f"| {r['id']} | | | | | error: {r['error']} |")
            continue
        L.append(f"| [{r['id']}](markdown/{r['id']}.md) | {r['source_format']} | {r['word_count']} | {r['table_count']} | "
                 f"{', '.join(r['sections'])} | {', '.join(r['quality_flags'])} |")
    trs = [r for r in rows if r.get("translation")]
    if trs:
        L += ["", "## English translations", "",
              "Machine translations (LLM, not reviewed by a person) of non-English articles, made by `scripts/finish_translations.py` "
              "from translated bodies in `data/markdown/translations/`. Use `<ID>.en.md` for extraction where it exists. "
              "*Numbers kept*: share of the original's numbers found in the translation. *Length*: translated words / original words. "
              "*Stale*: the original was re-converted after translating, so the translation should be redone.", "",
              "| ID | From | Translation | Numbers kept | Length | Sections | Flags | Stale |", "|---|---|---|---|---|---|---|---|"]
        for r in trs:
            t = r["translation"]
            L.append(f"| {r['id']} | {t['translated_from']} | [{r['id']}.en.md](markdown/{r['id']}.en.md) | {t['numbers_kept']:.0%} | "
                     f"{t['length_ratio']:.2f} | {', '.join(t['sections'])} | {', '.join(t['quality_flags']) or 'ok'} | {'yes' if t.get('stale') else ''} |")
    if abstract_rows:
        L += ["", "## Abstract-only articles", "",
              "Full text could not be retrieved (see `data/fulltext_missing.md`); the file holds the title, the authors' abstract and "
              "keywords, written by `scripts/abstracts_to_markdown.py`. Re-running `to_markdown.py` after adding a full text replaces it.", "",
              "| ID | Scope | Words | Language | Abstract source |", "|---|---|---|---|---|"]
        for r in abstract_rows:
            L.append(f"| [{r['id']}](markdown/{r['id']}.md) | {r['scope_label']} | {r['word_count']} | {r['language']} | {r.get('source_tier') or 'none'} |")
    REPORT_MD.write_text("\n".join(L) + "\n", encoding="utf-8")


def body_sha256(path):
    """Hash of a Markdown file's body (after the front matter), which does not change with the conversion timestamp."""
    text = Path(path).read_text(encoding="utf-8") if Path(path).exists() else ""
    return hashlib.sha256(text.split("\n---\n", 1)[-1].encode("utf-8")).hexdigest()


def read_front_matter(path):
    """Front matter written by convert(): one `key: JSON value` per line."""
    head = Path(path).read_text(encoding="utf-8").split("\n---\n", 1)[0].removeprefix("---\n")
    return {k: json.loads(v) for k, v in (l.split(": ", 1) for l in head.splitlines())}


def front_matter(fm):
    return "---\n" + "\n".join(f"{k}: {yaml_val(v)}" for k, v in fm.items()) + "\n---\n\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    arts = {a["id"]: a for a in map(json.loads, open(ROOT / "articles.jsonl", encoding="utf-8"))}
    arts.update({a["id"]: a for a in pending_articles()})  # assigned IDs not yet extracted
    sts = [r for r in map(json.loads, open(STATUS, encoding="utf-8")) if r.get("file")]
    if args.ids:
        sts = [r for r in sts if r["id"] in args.ids]
    try:
        import pymupdf
        import pymupdf4llm
        versions = f"{pymupdf4llm.version} / pymupdf {pymupdf.__version__}"
    except ImportError:
        versions = None
        if any(r["file"].endswith(".pdf") for r in sts):
            raise SystemExit("PDFs need pymupdf 2.x: .venv/Scripts/python.exe -m pip install -r scripts/requirements-markdown.txt")
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(arts[r["id"]], r, versions) for r in sts]
    results = {}
    with cf.ProcessPoolExecutor(max_workers=args.workers) as ex:
        for fm in ex.map(convert, jobs):
            results[fm["id"]] = fm
            print(fm["id"], fm.get("quality", "ERROR"), ",".join(fm.get("quality_flags", [])) or fm.get("error", ""), flush=True)
    # keep report rows for articles not re-converted this run, and translation records for those that were;
    # a translation made from a different body (finish_translations.py records its hash) is marked stale
    if REPORT_JSONL.exists():
        for r in map(json.loads, open(REPORT_JSONL, encoding="utf-8")):
            new = results.setdefault(r["id"], r)
            if new is not r and r.get("translation") and "error" not in new:
                tr = dict(r["translation"])
                tr["stale"] = tr.get("source_body_sha256") != body_sha256(OUT / f"{r['id']}.md")
                new["translation"] = tr
    write_report([results[k] for k in sorted(results)])
    print(collections.Counter(r.get("quality", "error") for r in results.values()))


if __name__ == "__main__":
    main()
