"""Per-article export: the terms the NLP extracted, the categories it assigned, and the article's summary.

For every article in articles.jsonl (CB, HU and BG):
  - categories: primary_category, secondary_tags and category_source from articles.jsonl (NLP, or the
    agents' label where the NLP found none), the NLP confidence and the rule-based study aim
    (data/syndromes/article_categories.csv);
  - summary: the "Abstract-derived summary" section of the article's note, and one_sentence_finding;
  - terms: every disorder concept extract_syndromes.py found (data/syndromes/article_concepts.csv;
    negated mentions are already left out), with its mention count, the sections it appears in,
    the words used in the text, the category it maps to (data/syndromes/category_map.csv; "-" when
    it counts towards no category) and whether it was studied or only mentioned. "Mentioned only"
    means it appears only in the introduction or discussion, the rule categorise_articles.py uses;
    for reviews every term counts as studied.

Outputs in data/syndromes/:
  article_terms.jsonl   one object per article, terms as lists of objects (complete)
  article_terms.csv     one row per article, terms joined into text (for a spreadsheet):
                        category_terms "Anemia [ERY] (12)", other_terms "Fever (3)", each list
                        studied terms first, then mentioned-only ones marked "*"

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/export_article_terms.py
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYN = ROOT / "data" / "syndromes"
MENTION_SECTIONS = {"introduction", "discussion"}  # as in categorise_articles.py


def summary_of(note):
    if not note.exists():
        return None
    m = re.search(r"^## Abstract-derived summary\s*\n(.*?)(?=^## |\Z)", note.read_text(encoding="utf-8"), re.S | re.M)
    return " ".join(m.group(1).split()) if m else None


def main():
    arts = [json.loads(l) for l in open(ROOT / "articles.jsonl", encoding="utf-8") if l.strip()]
    cats = {r["id"]: r for r in csv.DictReader(open(SYN / "article_categories.csv", encoding="utf-8"))}
    cmap = {r["cui"]: r["category"] for r in csv.DictReader(open(SYN / "category_map.csv", encoding="utf-8"))}
    terms = defaultdict(list)
    for r in csv.DictReader(open(SYN / "article_concepts.csv", encoding="utf-8")):
        terms[r["id"]].append(r)
    out = []
    for a in arts:
        c = cats.get(a["id"], {})
        review = c.get("aim") == "REV"
        tl = []
        for r in terms.get(a["id"], []):
            secs = r["sections"].split("; ") if r["sections"] else []
            tl.append({"concept": r["concept"], "cui": r["cui"], "category": cmap.get(r["cui"], "-"),
                       "mentions": int(r["mentions"]), "studied": review or any(s not in MENTION_SECTIONS for s in secs),
                       "in_results_or_case": r["in_results_or_case"] == "True", "sections": secs,
                       "text_forms": r["mention_texts"].split("; ") if r["mention_texts"] else [],
                       "semantic_types": r["semantic_types"]})
        tl.sort(key=lambda t: (not t["studied"], t["category"] == "-", -t["mentions"], t["concept"]))
        out.append({"id": a["id"], "title": a.get("title"), "year": (a.get("first_pub_date") or "")[:4] or None,
                    "scope_label": a.get("scope_label"), "primary_category": a.get("primary_category"),
                    "secondary_tags": a.get("secondary_tags") or [], "category_source": a.get("category_source"),
                    "nlp_confidence": c.get("confidence"), "aim": c.get("aim"), "source_format": c.get("source_format"),
                    "summary": summary_of(ROOT / a["filename"]), "one_sentence_finding": a.get("one_sentence_finding"),
                    "n_terms": len(tl), "terms": tl})
    with open(SYN / "article_terms.jsonl", "w", encoding="utf-8") as f:
        for o in out:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")

    def joined(tl):
        return "; ".join(f"{t['concept']}" + (f" [{t['category']}]" if t["category"] != "-" else "")
                         + f" ({t['mentions']})" + ("" if t["studied"] else "*") for t in tl)

    cols = ["id", "title", "year", "scope_label", "primary_category", "secondary_tags", "category_source",
            "nlp_confidence", "aim", "source_format", "summary", "one_sentence_finding", "n_terms",
            "category_terms", "other_terms"]
    with open(SYN / "article_terms.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for o in out:
            w.writerow([o["id"], o["title"], o["year"], o["scope_label"], o["primary_category"] if isinstance(o["primary_category"], str) else "",
                        " ".join(o["secondary_tags"]), o["category_source"] or "", o["nlp_confidence"] or "", o["aim"] or "",
                        o["source_format"] or "", o["summary"] or "", o["one_sentence_finding"] or "", o["n_terms"],
                        joined([t for t in o["terms"] if t["category"] != "-"]),
                        joined([t for t in o["terms"] if t["category"] == "-"])])
    print(f"articles={len(out)} with_summary={sum(1 for o in out if o['summary'])} "
          f"with_terms={sum(1 for o in out if o['terms'])} terms={sum(o['n_terms'] for o in out)}")


if __name__ == "__main__":
    main()
