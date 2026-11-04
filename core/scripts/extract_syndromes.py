"""Extract clinical syndromes and findings from the article Markdown with scispaCy, linked to UMLS.

Input: one document per article from data/markdown/: <ID>.en.md (English translation) where it exists,
otherwise <ID>.md (full text or abstract only, as converted by to_markdown.py / abstracts_to_markdown.py).
The front matter is read for provenance; the body is split into blocks (prose, list items, table rows
written as "cell; cell; ...") and each block is tagged with its section ("## Results" etc.).

Pipeline (scispaCy 0.6.2, spaCy 3.7):
  1. en_ner_bc5cdr_md NER, trained to find DISEASE (and CHEMICAL) mentions;
  2. en_core_sci_md NER, which marks every biomedical concept (ENTITY), filling gaps between (1)'s
     entities (spaCy keeps entities already set as constraints);
  3. AbbreviationDetector (Schwartz & Hearst), so "IMHA" is linked through its long form;
  4. UMLS EntityLinker (char-3-gram TF-IDF + approximate nearest neighbours), top concept above
     --threshold;
  5. negspacy NegEx (en_clinical termset plus post-negations such as "was absent", "not detected"),
     which sets `negated` on a mention ("no evidence of DIC").
Kept: DISEASE mentions (linked or not) and every UMLS-linked ENTITY mention; `disorder` is true for DISEASE
mentions and concepts with a semantic type in the UMLS "Disorders" group (Disease or Syndrome, Sign or
Symptom, Pathologic Function, Finding, ...). Non-disorder concepts (biomarkers such as cytokines or
malondialdehyde, cells, physiological functions) are kept because mechanism categories (inflammation,
oxidative stress, endothelium) are recognised from them rather than from syndromes. CHEMICAL mentions from
the disease model are dropped (drugs). The semantic types are the UMLS categories; the summaries count
disorder concepts only.

Not handled: uncertainty ("suspected DIC"), or whether a mention is the authors' own finding or
background; use the section field (Results/Case vs Introduction/Discussion) to filter. Negated mentions
stay in mentions.jsonl but are left out of the summaries.

Outputs in data/syndromes/:
  mentions.jsonl          one row per kept mention: article, document, section, sentence, mention text,
                          abbreviation long form, model label, UMLS CUI, concept name, semantic types, score
  article_concepts.csv    one row per article x concept: mention count, sections, found in results/case
  concept_summary.csv     one row per concept: articles and mentions, split full text / abstract only
  run.json                versions, models, settings, document list

Usage (from canine-babesiosis-review/, in the scispaCy environment; see scripts/requirements-nlp.txt):
    .venv-nlp/Scripts/python.exe -I scripts/extract_syndromes.py
    .venv-nlp/Scripts/python.exe -I scripts/extract_syndromes.py --ids CB040 CB022
"""
import argparse
import collections
import csv
import datetime as dt
import json
import re
import sys
import time
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import to_markdown as T  # noqa: E402  (front-matter reader and section classifier; stdlib only)

ROOT = T.ROOT
OUT = ROOT / "data" / "syndromes"
# UMLS semantic group "Disorders" (DISO), McCray et al. 2001
DISORDERS = {"T020": "Acquired Abnormality", "T190": "Anatomical Abnormality", "T049": "Cell or Molecular Dysfunction",
             "T019": "Congenital Abnormality", "T047": "Disease or Syndrome", "T050": "Experimental Model of Disease",
             "T033": "Finding", "T037": "Injury or Poisoning", "T048": "Mental or Behavioral Dysfunction",
             "T191": "Neoplastic Process", "T046": "Pathologic Function", "T184": "Sign or Symptom"}
# results-style negations that follow the finding ("thrombocytopenia was absent")
POST_NEGATIONS = ["absent", "was absent", "were absent", "not observed", "was not observed", "were not observed",
                  "not detected", "was not detected", "were not detected", "not found", "was not found", "were not found",
                  "not present", "was not present", "were not present", "not seen", "was not seen", "were not seen",
                  "did not develop", "was ruled out", "were ruled out"]
RESULT_SECTIONS = {"results", "case", "results_discussion"}


def document_for(aid):
    en = T.OUT / f"{aid}.en.md"
    return en if en.exists() else T.OUT / f"{aid}.md"


def blocks(body):
    """(text, section, kind) blocks; table rows become 'cell; cell; ...' lines, separator rows dropped."""
    section, out = "title", []
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para:
            continue
        if para.startswith("# "):
            out.append((para[2:].strip(), "title", "title"))
            section = "unlabelled"  # text before the first recognised heading: authors, unheaded abstract or introduction
            continue
        m = re.match(r"^(#{2,4})\s+(.+)$", para)
        if m and "\n" not in para:
            if len(m.group(1)) == 2:
                section = T.classify(m.group(2)) or m.group(2).strip().lower()
            out.append((m.group(2).strip(), section, "heading"))
            continue
        if para.startswith("|"):
            for row in para.splitlines():
                if re.fullmatch(r"\|?(\s*:?-+:?\s*\|)+\s*", row.strip()):
                    continue
                cells = [c.strip() for c in row.strip().strip("|").split("|") if c.strip()]
                if cells:
                    out.append(("; ".join(cells), section, "table_row"))
            continue
        out.append((re.sub(r"\*\*|\^", "", para), section, "list" if para.startswith("- ") else "prose"))
    return out


def build_pipeline(threshold):
    import spacy
    from scispacy.abbreviation import AbbreviationDetector  # noqa: F401  (registers the factory)
    from scispacy.linking import EntityLinker  # noqa: F401

    nlp = spacy.load("en_core_sci_md")
    bc5 = spacy.load("en_ner_bc5cdr_md")
    nlp.add_pipe("ner", name="ner_bc5cdr", source=bc5, before="ner")
    nlp.add_pipe("abbreviation_detector")
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls", "threshold": threshold})
    from negspacy.negation import Negex  # noqa: F401  (registers the factory)
    from negspacy.termsets import termset
    ts = termset("en_clinical")
    ts.add_patterns({"following_negations": POST_NEGATIONS})
    nlp.add_pipe("negex", config={"neg_termset": ts.get_patterns()})
    nlp.max_length = 2_000_000
    return nlp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--threshold", type=float, default=0.85, help="minimum UMLS link score (scispaCy default 0.7)")
    args = ap.parse_args()
    warnings.filterwarnings("ignore")

    arts = [json.loads(l) for l in open(ROOT / "articles.jsonl", encoding="utf-8")]
    if args.ids:
        arts = [a for a in arts if a["id"] in args.ids]
    t0 = time.time()
    nlp = build_pipeline(args.threshold)
    linker = nlp.get_pipe("scispacy_linker")
    tree = linker.kb.semantic_type_tree
    print(f"pipeline ready in {time.time() - t0:.0f}s: {nlp.pipe_names}", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    mentions, docs_used = [], []
    for i, a in enumerate(arts, 1):
        path = document_for(a["id"])
        fm = T.read_front_matter(path)
        body = path.read_text(encoding="utf-8").split("\n---\n", 1)[1]
        parts = blocks(body)
        # one Doc per article so abbreviations defined early resolve later; offsets map back to blocks
        text, spans, pos = [], [], 0
        for b, section, kind in parts:
            spans.append((pos, pos + len(b), section, kind))
            text.append(b)
            pos += len(b) + 2
        doc = nlp("\n\n".join(text))
        long_forms = {a_.start: a_._.long_form.text for a_ in doc._.abbreviations}
        n_kept = 0
        for e in doc.ents:
            if e.label_ == "CHEMICAL":
                continue
            cui, score, name, types = None, None, None, []
            if e._.kb_ents:
                cui, score = e._.kb_ents[0]
                ent = linker.kb.cui_to_entity[cui]
                name, types = ent.canonical_name, list(ent.types)
            disorder = e.label_ == "DISEASE" or bool(set(types) & DISORDERS.keys())
            if not disorder and not cui:
                continue  # unlinked non-disease spans carry nothing to categorise
            st, en, section, kind = next(((st, en, s, k) for st, en, s, k in spans if st <= e.start_char < en), (0, 0, "?", "?"))
            if kind == "heading":
                continue
            mentions.append({
                "id": a["id"], "document": path.relative_to(ROOT).as_posix(), "source_format": fm.get("source_format"),
                "translated": path.name.endswith(".en.md"), "section": section, "block": kind,
                # sentence context, cut to the mention's own block (table rows and captions are separate blocks)
                "sentence": doc.text[max(e.sent.start_char, st):min(e.sent.end_char, en)].strip()[:400],
                "mention": e.text, "abbreviation_of": long_forms.get(e.start),
                "label": e.label_, "disorder": disorder, "negated": bool(e._.negex), "cui": cui, "concept": name, "score": round(score, 3) if score else None,
                "semantic_types": [{"tui": t, "name": tree.get_canonical_name(t)} for t in types]})
            n_kept += 1
        docs_used.append({"id": a["id"], "document": path.relative_to(ROOT).as_posix(), "source_format": fm.get("source_format"),
                          "words": fm.get("word_count"), "mentions": n_kept})
        print(f"[{i}/{len(arts)}] {a['id']} {fm.get('source_format')} {n_kept} mentions", flush=True)

    with open(OUT / "mentions.jsonl", "w", encoding="utf-8") as fh:
        for m in mentions:
            fh.write(json.dumps(m, ensure_ascii=False) + "\n")

    # article x concept; unlinked DISEASE mentions are grouped by their lower-cased text
    per = collections.defaultdict(lambda: {"mentions": 0, "sections": set(), "texts": collections.Counter()})
    meta = {}
    for m in (m for m in mentions if m["disorder"] and not m["negated"]):
        key = (m["id"], m["cui"] or f"UNLINKED:{m['mention'].lower()}")
        p = per[key]
        p["mentions"] += 1
        p["sections"].add(m["section"])
        p["texts"][m["mention"].lower()] += 1
        meta[key[1]] = (m["concept"] or m["mention"].lower(), "; ".join(t["name"] for t in m["semantic_types"]) or "unlinked")
    fmt = {d["id"]: d["source_format"] for d in docs_used}
    with open(OUT / "article_concepts.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "source_format", "cui", "concept", "semantic_types", "mentions", "in_results_or_case", "sections", "mention_texts"])
        for (aid, key), p in sorted(per.items()):
            w.writerow([aid, fmt[aid], key, *meta[key], p["mentions"], bool(p["sections"] & RESULT_SECTIONS),
                        "; ".join(sorted(p["sections"])), "; ".join(t for t, _ in p["texts"].most_common(5))])

    summ = collections.defaultdict(lambda: {"articles": set(), "full": set(), "abstract": set(), "results": set(), "mentions": 0})
    for (aid, key), p in per.items():
        s = summ[key]
        s["articles"].add(aid)
        (s["abstract"] if fmt[aid] == "abstract" else s["full"]).add(aid)
        if p["sections"] & RESULT_SECTIONS:
            s["results"].add(aid)
        s["mentions"] += p["mentions"]
    with open(OUT / "concept_summary.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cui", "concept", "semantic_types", "articles", "articles_full_text", "articles_abstract_only",
                    "articles_in_results_or_case", "mentions"])
        for key, s in sorted(summ.items(), key=lambda kv: (-len(kv[1]["articles"]), kv[0])):
            w.writerow([key, *meta[key], len(s["articles"]), len(s["full"]), len(s["abstract"]), len(s["results"]), s["mentions"]])

    import scispacy
    import spacy
    (OUT / "run.json").write_text(json.dumps({
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "spacy": spacy.__version__, "scispacy": scispacy.__version__,
        "models": {n: nlp.meta.get("name") for n in ["en_core_sci_md"]} | {"ner_bc5cdr": "en_ner_bc5cdr_md"},
        "pipeline": nlp.pipe_names, "linker": "umls", "threshold": args.threshold, "post_negations": POST_NEGATIONS,
        "kept": "DISEASE mentions, and ENTITY mentions linked to a UMLS Disorders-group semantic type",
        "documents": docs_used, "mentions": len(mentions), "seconds": round(time.time() - t0)}, indent=1), encoding="utf-8")
    print(f"{len(mentions)} mentions, {len(summ)} concepts, {len(docs_used)} documents, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
