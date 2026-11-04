"""Inputs for the category-synthesis agents, from articles.jsonl (NLP categories), the notes, cohorts and datasets.

Writes, per category:
- search/synthesis/<CAT>_secondary_digest.md: one line per CB article whose secondary tags include the category;
- <out>/prim_<CAT>_partN.md: condensed notes of the primary articles (metadata line, abstract-derived summary,
  reviewer interpretation, key limitations), split at about 55,000 characters so an agent can read each part;
- <out>/ctx_<CAT>.md: the cohorts and datasets that touch the category;
and search/synthesis/inputs.json + args.json (the primary and secondary note paths per category).
Round-4 articles (2006-2016) are those whose ID is in a later round of search/rounds.json; the context counts them.

Usage:
    python -I scripts/synthesis_inputs.py <out_dir>
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYN = ROOT / "search" / "synthesis"
CATS = ["ERY", "INF", "END", "COA", "REN", "PUL", "NEU", "CAR", "MET", "OXO", "SEV"]
PART_CHARS = 55000


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def year(a):
    return (a.get("first_pub_date") or "")[:4]


def section(text, name):
    m = re.search(rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)", text, flags=re.M | re.S)
    return m.group(1).strip() if m else ""


def bullet(text, label):
    m = re.search(rf"^- \*\*{re.escape(label)}:?\*\*:?\s*(.*)$", text, flags=re.M)
    return m.group(1).strip() if m else ""


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    arts = [a for a in jl(ROOT / "articles.jsonl") if a["id"].startswith("CB")]
    cohorts = json.loads((ROOT / "cohorts.json").read_text(encoding="utf-8"))
    ds_by_art = defaultdict(list)
    for d in jl(ROOT / "datasets.jsonl"):
        for a in d["linked_articles"]:
            ds_by_art[a].append(d)
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    rounds = json.loads((ROOT / "search" / "rounds.json").read_text(encoding="utf-8"))["rounds"]
    early = {x["key"] for n in ("r1", "r2", "r3") for x in jl(ROOT / "search" / f"screening_{n}.jsonl")}
    later_keys = {x["key"] for r in rounds[1:] for x in jl(ROOT / r["dir"] / "screening.jsonl")} - early
    later = {v["id"] for k, v in reg.items() if k in later_keys}

    def condensed(a):
        t = (ROOT / a["filename"]).read_text(encoding="utf-8")
        ci = section(t, "Critical interpretation")
        sp = "; ".join(f"{s['name']} ({s['status']})" for s in a.get("species") or []) or a.get("species_short") or "unspecified"
        dsl = ", ".join(f"{d['dataset_id']} (status {d['status_code']}; {', '.join(d.get('granularity') or [])})" for d in ds_by_art.get(a["id"], [])) or "none"
        return "\n".join([
            f"### {a['id']} ({year(a)}) {a['title']}",
            f"- file: {a['filename']}",
            f"- species: {sp}; country: {a.get('country')}; design: {a.get('design')}; n: {a.get('sample_size')}",
            f"- scope: {a['scope_label']} / {a.get('include_type')}; evidence: {a.get('evidence_type')}; cohort: {a.get('cohort_id') or 'none'}",
            f"- NLP primary: {a['primary_category']} ({a.get('category_source')}, {a.get('category_confidence')}); secondary: {', '.join(a.get('secondary_tags') or []) or 'none'}; agent label was {a.get('agent_primary_category')}",
            f"- datasets: {dsl}; dataset status {a.get('dataset_status_code')}",
            f"- text read for note: {'full text' if a.get('fulltext_checked') else 'abstract only'}",
            f"**Summary.** {section(t, 'Abstract-derived summary')}",
            f"**Reviewer interpretation.** {bullet(ci, 'Reviewer interpretation')}",
            f"**Key limitations.** {bullet(ci, 'Key limitations (from available information)') or bullet(ci, 'Key limitations')}",
            ""])

    def digest_line(a):
        return (f"- [{a['id']}]({a['filename']}) {year(a)}; {a.get('species_short')}; {a.get('design')}; "
                f"n={a.get('sample_size')}; cohort={a.get('cohort_id')}; {a.get('evidence_type')}; "
                f"primary={a['primary_category']}: {a.get('one_sentence_finding')}")

    key = lambda a: (year(a), a["id"])
    inputs = []
    for c in CATS:
        prim = sorted((a for a in arts if a["primary_category"] == c), key=key)
        sec = sorted((a for a in arts if c in (a.get("secondary_tags") or [])), key=key)
        parts, cur = [], f"# {c}: condensed notes of the {len(prim)} primary articles\n\n"
        for block in (condensed(a) + "\n" for a in prim):
            if len(cur) + len(block) > PART_CHARS and cur.strip():
                parts.append(cur)
                cur = ""
            cur += block
        parts.append(cur)
        for old in out.glob(f"prim_{c}_part*.md"):
            old.unlink()
        for i, p in enumerate(parts, 1):
            (out / f"prim_{c}_part{i}.md").write_text(p, encoding="utf-8")
        (SYN / f"{c}_secondary_digest.md").write_text("\n".join(digest_line(a) for a in sec) + "\n", encoding="utf-8")
        ids = {a["id"] for a in prim + sec}
        ctx = [f"# {c} context", "",
               f"Primary articles: {len(prim)} ({sum(1 for a in prim if a['id'] in later)} from round 4, 2006-2016). Secondary-tagged: {len(sec)}.", "",
               "## Cohorts touching this category (articles in one cohort = one source of evidence)", ""]
        for cid, co in cohorts.items():
            inc = [m for m in co["members"] if m in ids]
            if inc:
                ctx.append(f"- **{cid}** ({co['certainty']}) {co['label']}. Members: {', '.join(co['members'])} (in this category: {', '.join(inc)}). Basis: {co['basis']}")
        ctx += ["", "## Datasets linked to articles in this category", ""]
        seen = set()
        for a in prim + sec:
            for d in ds_by_art.get(a["id"], []):
                if d["dataset_id"] in seen:
                    continue
                seen.add(d["dataset_id"])
                ctx.append(f"- **{d['dataset_id']}** status {d['status_code']} ({d['status']}); rank {d.get('priority_rank')}; source {d.get('independent_source')}; "
                           f"articles {', '.join(d['linked_articles'])}; granularity {', '.join(d.get('granularity') or [])}; {d.get('title')}; "
                           f"n_animals {d.get('n_animals')}; features: {str(d.get('features') or '')[:400]}")
        (out / f"ctx_{c}.md").write_text("\n".join(ctx) + "\n", encoding="utf-8")
        inputs.append({"c": c, "prim": [a["filename"] for a in prim], "sec": [a["filename"] for a in sec]})
        print(c, "primary", len(prim), "secondary", len(sec), "parts", len(parts))
    (SYN / "inputs.json").write_text(json.dumps(inputs, ensure_ascii=False), encoding="utf-8")
    (SYN / "args.json").write_text(json.dumps({"inputs": inputs}, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
