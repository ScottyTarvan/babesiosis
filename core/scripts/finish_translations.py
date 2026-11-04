"""Turn translated article bodies into English Markdown files beside the originals.

Input: data/markdown/translations/<ID>.body.md, an English translation of the body (everything after
the front matter) of data/markdown/<ID>.md. These were produced by LLM translation agents told to keep
headings, tables, numbers and order unchanged and to copy any leftover reference entries untranslated.

For each translation this script:
  - applies the same heading normalisation and reference / back-matter removal as to_markdown.py
    (now that headings are in English they are recognised: "References", "Materials and methods", ...);
  - checks faithfulness: the share of the original's numbers that appear in the translation, and the
    translated/original word ratio;
  - writes data/markdown/<ID>.en.md with the original's front matter plus translation fields
    (translated_from, translation_of, source body hash, translator, checks);
  - adds a "translation" record to data/markdown_report.jsonl and regenerates data/markdown_report.md.

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/finish_translations.py
    python -I scripts/finish_translations.py --ids CB158 CB187
"""
import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assign_ids import pending_articles  # noqa: E402
import to_markdown as T  # noqa: E402

TR = T.OUT / "translations"
TRANSLATOR = "Claude Opus 5.5 (LLM translation agent); not reviewed by a person"
NUM = re.compile(r"\d+(?:[.,]\d+)?")


def source_language(text):
    """Rough language label for the original, from its letters."""
    if re.search(r"[јљњћђџЈЉЊЋЂЏ]", text):
        return "sr"
    if re.search(r"[іїєґІЇЄҐ]", text):
        return "uk"
    if re.search(r"[ыэъЫЭЪ]", text):
        return "ru"
    enough = max(3, len(text) // 500)  # abstracts are short; full texts need more than a stray name
    for lang, chars in (("tr", "ğıİ"), ("pt", "ãõ"), ("pl", "łąężśźń"), ("ro", "ășțşţ"), ("fr", "èêëœ")):  # letters unique to each
        if sum(text.count(c) for c in chars) >= enough:
            return lang
    words = re.findall(r"\w+", text.lower())
    if sum(w in {"les", "des", "une", "avec", "est", "pour", "dans", "du"} for w in words) >= 5:
        return "fr"
    return "unknown"


def words(text):
    return len(re.findall(r"\w+", re.sub(r"(?m)^\|.*$", "", text)))


def finish(aid, arts, rows):
    src = T.OUT / f"{aid}.md"
    fm = T.read_front_matter(src)
    orig_body = src.read_text(encoding="utf-8").split("\n---\n", 1)[1]
    raw = (TR / f"{aid}.body.md").read_text(encoding="utf-8")
    art = arts[aid]
    T.CASE_REPORT = art.get("include_type") == "case_report"
    # the translated title line becomes the heading; it differs from articles.jsonl only where that title is not English
    m = re.match(r"\s*# (.+)\n", raw)
    title = m.group(1).strip() if m else art["title"]
    body = raw[m.end():] if m else raw
    md, removed, ntables, had_refs, _ = T.clean_pdf_md(body, None, title)
    md = T.fix_lookalikes(md)
    sections = [s for s in (T.classify(h) for h in re.findall(r"(?m)^## (.+)$", md)) if s]
    # references already removed from the original before translation count as found
    had_refs = had_refs or any(T.classify(x) == "references" or "reference list" in x for x in fm.get("removed_sections", []))
    flags, nwords, lang = T.quality(md, sections, art, {"title_check": fm.get("title_check")}, had_refs, None, "translation")
    if fm.get("source_format") == "abstract":  # full-text structure checks do not apply to an abstract
        flags = ["abstract_only"] + [f for f in flags if f.startswith("language")]

    # decimal comma and point count as the same number ("1,5 times" -> "1.5 times")
    nums = lambda s: collections.Counter(n.replace(",", ".") for n in NUM.findall(s))
    # cleaned translation against the cleaned original: reference entries the translators copied are not counted
    on, tn = nums(orig_body), nums(md)
    kept = sum(min(c, tn[n]) for n, c in on.items()) / sum(on.values()) if on else 1.0  # no numbers: nothing lost
    ratio = words(md) / max(1, words(orig_body))
    if kept < 0.97:
        flags.append("numbers_lost")  # numbers in the original missing from the translation
    if not 0.75 <= ratio <= 1.6:
        flags.append("length_unusual")  # possible omission or padding
    if words(re.sub(r"(?m)^#.*$", "", orig_body)) < 10:  # a stray name or page range: ratio and language checks mean nothing
        flags = [f for f in flags if f != "length_unusual" and not f.startswith("language")]
        lang = "en"
    if "[unclear:" in raw:
        flags.append("unclear_passages")

    if title != art["title"]:
        fm["title_en"] = title
    fm.update({"language": lang, "translated_from": source_language(orig_body), "translation_of": f"data/markdown/{aid}.md",
               "translation_source_body_sha256": T.body_sha256(src), "translator": TRANSLATOR,
               "translated_utc": dt.datetime.fromtimestamp((TR / f"{aid}.body.md").stat().st_mtime, dt.timezone.utc).isoformat(timespec="seconds"),
               "numbers_kept": round(kept, 3), "length_ratio": round(ratio, 2),
               "word_count": nwords, "table_count": ntables, "sections": sorted(set(sections), key=sections.index),
               "removed_sections": fm.get("removed_sections", []) + removed,
               "quality": "abstract_only" if flags == ["abstract_only"] else "review" if flags else "ok", "quality_flags": flags})
    (T.OUT / f"{aid}.en.md").write_text(T.front_matter(fm) + f"# {title}\n\n" + md.strip() + "\n", encoding="utf-8")
    rows[aid]["translation"] = {"file": f"data/markdown/{aid}.en.md", "translated_from": fm["translated_from"],
                                "source_body_sha256": fm["translation_source_body_sha256"], "numbers_kept": kept,
                                "length_ratio": ratio, "sections": fm["sections"], "quality_flags": flags, "stale": False}
    return fm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    args = ap.parse_args()
    arts = {a["id"]: a for a in map(json.loads, open(T.ROOT / "articles.jsonl", encoding="utf-8"))}
    arts.update({a["id"]: a for a in pending_articles()})  # assigned IDs not yet extracted (round 4)
    rows = {r["id"]: r for r in map(json.loads, open(T.REPORT_JSONL, encoding="utf-8"))}
    ids = args.ids or sorted(p.name.split(".")[0] for p in TR.glob("*.body.md"))
    for aid in ids:
        fm = finish(aid, arts, rows)
        print(aid, fm["translated_from"], f"numbers {fm['numbers_kept']:.0%}", f"length {fm['length_ratio']:.2f}",
              fm["quality"], ",".join(fm["quality_flags"]))
    T.write_report([rows[k] for k in sorted(rows)])


if __name__ == "__main__":
    main()
