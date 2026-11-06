"""Build the clinical-syndrome-plus-treatment tagging batches for the included CB articles.

Companion to build_clinical_rescreen.py: that script re-screens the *excluded* records; this one
tags the 444 included canine articles in articles.jsonl against the same criterion
(search/clinical_treatment/screening_criteria.md) so both halves can be merged into one set.

Writes
  search/clinical_treatment/articles/candidates.jsonl        one row per CB article
  search/clinical_treatment/articles/batches/ia_NN.md        tagging batches
  search/clinical_treatment/articles/batches/batches.json

Each batch item carries: title, journal, date, design and sample size from articles.jsonl, the
one-sentence finding, the abstract (search/packets/<ID>.json record), and up to ~1500 characters
of treatment-related sentences from data/markdown/<ID>.md when full text exists (git-ignored,
this machine only).

Usage (from core/):
    python -I scripts/build_clinical_tagging.py [--size 40]
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "search" / "clinical_treatment" / "articles"
TX = re.compile(r"\b(treat\w*|therap\w*|imidocarb|diminazene|atovaquone|azithromycin|clindamycin|doxycycline|"
                r"metronidazole|artesunate|buparvaquone|transfus\w*|dialysis|plasmapheresis|prednisol\w*|"
                r"dexamethasone|fluid therapy|supportive care|survived|died|euthan\w*|mortality|recover\w*|"
                r"outcome|relaps\w*)\b", re.I)
MAX_EXCERPT = 1500


def front_matter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        return {}, text
    fm = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm, text[end + 4:]


def excerpt(md_path):
    """Return (source_format, excerpt) from a full-text markdown file."""
    if not md_path.exists():
        return None, None
    fm, body = front_matter(md_path.read_text(encoding="utf-8", errors="replace"))
    if fm.get("source_format") == "abstract":
        return "abstract", None
    body = re.sub(r"\s+", " ", body)
    sents = re.split(r"(?<=[.!?])\s+(?=[A-Z])", body)
    hits, total = [], 0
    for s in sents:
        if TX.search(s) and 30 < len(s) < 600:
            if total + len(s) > MAX_EXCERPT:
                break
            hits.append(s.strip())
            total += len(s)
    return fm.get("source_format") or "fulltext", " […] ".join(hits) if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=40)
    a = ap.parse_args()
    arts = [json.loads(l) for l in (ROOT / "articles.jsonl").open(encoding="utf-8") if l.strip()]
    rows = []
    for r in arts:
        if not r["id"].startswith("CB"):
            continue
        packet = ROOT / "search" / "packets" / f"{r['id']}.json"
        abstract = None
        if packet.exists():
            abstract = (json.load(packet.open(encoding="utf-8")).get("record") or {}).get("abstract")
        md = ROOT / "data" / "markdown" / f"{r['id']}.en.md"
        if not md.exists():
            md = ROOT / "data" / "markdown" / f"{r['id']}.md"
        fmt, exc = excerpt(md)
        rows.append({"article_id": r["id"], "key": r["key"], "title": r["title"], "journal": r["journal"],
                     "first_pub_date": r["first_pub_date"], "doi": r["doi"], "pmid": r["pmid"],
                     "design": r.get("design"), "sample_size": r.get("sample_size"),
                     "n_infected_dogs": r.get("n_infected_dogs"), "primary_category": r.get("primary_category"),
                     "secondary_tags": r.get("secondary_tags"), "species_short": r.get("species_short"),
                     "one_sentence_finding": r.get("one_sentence_finding"), "abstract": abstract,
                     "fulltext_format": fmt, "treatment_excerpt": exc})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "batches").mkdir(exist_ok=True)
    with (OUT / "candidates.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    batches = {}
    for i in range(0, len(rows), a.size):
        name = f"ia_{i // a.size + 1:02d}.md"
        chunk = rows[i:i + a.size]
        lines = [f"# Tagging batch {name} ({len(chunk)} included articles)\n"]
        for c in chunk:
            lines.append(f"### {c['article_id']}  ({c['key']})")
            lines.append(f"Title: {c['title']}")
            lines.append(" | ".join([f"Journal: {c.get('journal') or '?'}", f"First pub: {c.get('first_pub_date') or '?'}",
                                     f"Species: {c.get('species_short') or '?'}",
                                     f"Category: {c.get('primary_category')} {c.get('secondary_tags') or ''}"]))
            lines.append(f"Design: {c.get('design') or '?'} | Sample: {c.get('sample_size') or '?'}")
            lines.append(f"Finding: {c.get('one_sentence_finding') or ''}")
            lines.append(f"Abstract: {c.get('abstract') or '(none available)'}")
            if c.get("treatment_excerpt"):
                lines.append(f"Full-text sentences mentioning treatment/outcome: {c['treatment_excerpt']}")
            else:
                lines.append(f"Full text: {'not available; abstract only' if c.get('fulltext_format') in (None, 'abstract') else 'available but no treatment/outcome sentences matched'}")
            lines.append("")
        (OUT / "batches" / name).write_text("\n".join(lines), encoding="utf-8")
        batches[name] = [c["article_id"] for c in chunk]
    (OUT / "batches" / "batches.json").write_text(json.dumps(batches, indent=1), encoding="utf-8")
    print(len(rows), "articles;", len(batches), "batches")
    print("with abstract:", sum(1 for r in rows if r.get("abstract")),
          "| full text:", sum(1 for r in rows if r.get("fulltext_format") not in (None, "abstract")),
          "| with treatment excerpt:", sum(1 for r in rows if r.get("treatment_excerpt")))


if __name__ == "__main__":
    main()
