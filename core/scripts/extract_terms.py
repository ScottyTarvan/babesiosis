"""Extract terms from each article's Markdown with scispaCy, one output file per article.

Uses the same pipeline and keep rules as extract_syndromes.py (bc5cdr DISEASE NER + core scientific NER,
abbreviation resolution, UMLS linking, NegEx), but writes data/terms/<ID>.json for each article instead of one
combined mentions file, so terms can be counted across articles afterwards.

A term is one UMLS concept (cui) whose semantic type is in the UMLS Disorders group, except "Finding" (T033),
which holds modifiers such as "Severe", "Infected" and "Reduced". Unlinked mentions are dropped. Per article each
term has its mention count, how many of those mentions were negated, the sections it appears in and the surface
forms seen. Count a term's article frequency as the number of files that list it; use `mentions_affirmed` to
ignore negated mentions.

Input: <ID>.en.md where it exists, otherwise <ID>.md, for every article in articles.jsonl.

Usage (from core/, in the scispaCy environment; see scripts/requirements-nlp.txt):
    .venv-nlp/Scripts/python.exe -I scripts/extract_terms.py
    .venv-nlp/Scripts/python.exe -I scripts/extract_terms.py --ids CB040 CB022
"""
import argparse
import collections
import datetime as dt
import json
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract_syndromes as X  # noqa: E402
import to_markdown as T  # noqa: E402

ROOT = T.ROOT
OUT = ROOT / "data" / "terms"
KEEP_TYPES = {t for t in X.DISORDERS if t != "T033"}


def terms_for(nlp, linker, tree, text_parts):
    """Aggregate the kept mentions of one article into terms."""
    text, spans, pos = [], [], 0
    for b, section, kind in text_parts:
        spans.append((pos, pos + len(b), section, kind))
        text.append(b)
        pos += len(b) + 2
    doc = nlp("\n\n".join(text))
    agg = {}
    for e in doc.ents:
        if e.label_ == "CHEMICAL":
            continue
        cui, score, name, types = None, None, None, []
        if e._.kb_ents:
            cui, score = e._.kb_ents[0]
            ent = linker.kb.cui_to_entity[cui]
            name, types = ent.canonical_name, list(ent.types)
        if not cui or not set(types) & KEEP_TYPES:
            continue
        section, kind = next(((s, k) for st, en, s, k in spans if st <= e.start_char < en), ("?", "?"))
        if kind == "heading":
            continue
        key = cui
        t = agg.setdefault(key, {
            "term": key, "concept": name,
            "semantic_types": [tree.get_canonical_name(x) for x in types],
            "mentions": 0, "mentions_negated": 0, "mentions_affirmed": 0,
            "sections": collections.Counter(), "forms": collections.Counter(), "best_score": None})
        t["mentions"] += 1
        t["mentions_negated" if e._.negex else "mentions_affirmed"] += 1
        t["sections"][section] += 1
        t["forms"][e.text.lower()] += 1
        if score and (t["best_score"] is None or score > t["best_score"]):
            t["best_score"] = round(float(score), 3)
    out = []
    for t in sorted(agg.values(), key=lambda t: (-t["mentions"], t["term"])):
        t["sections"] = dict(t["sections"].most_common())
        t["forms"] = dict(t["forms"].most_common(8))
        out.append(t)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--threshold", type=float, default=0.85, help="minimum UMLS link score")
    args = ap.parse_args()
    warnings.filterwarnings("ignore")

    arts = [json.loads(l) for l in open(ROOT / "articles.jsonl", encoding="utf-8")]
    if args.ids:
        arts = [a for a in arts if a["id"] in args.ids]
    t0 = time.time()
    nlp = X.build_pipeline(args.threshold)
    linker = nlp.get_pipe("scispacy_linker")
    tree = linker.kb.semantic_type_tree
    print(f"pipeline ready in {time.time() - t0:.0f}s: {nlp.pipe_names}", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for i, a in enumerate(arts, 1):
        path = X.document_for(a["id"])
        fm = T.read_front_matter(path)
        body = path.read_text(encoding="utf-8").split("\n---\n", 1)[1]
        terms = terms_for(nlp, linker, tree, X.blocks(body))
        total += len(terms)
        rec = {"id": a["id"], "document": path.relative_to(ROOT).as_posix(), "source_format": fm.get("source_format"),
               "translated": path.name.endswith(".en.md"), "words": fm.get("word_count"),
               "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "threshold": args.threshold, "kept_types": sorted(KEEP_TYPES), "term_count": len(terms), "terms": terms}
        (OUT / f"{a['id']}.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[{i}/{len(arts)}] {a['id']} {fm.get('source_format')} {len(terms)} terms", flush=True)
    print(f"{len(arts)} files, {total} terms, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
