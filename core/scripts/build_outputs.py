"""Build machine-readable outputs and the master index from curated inputs.

Inputs (all under canine-babesiosis-review/):
  ids.json                          stable ID registry (scripts/assign_ids.py)
  search/extraction_records.jsonl   per-article structured records from extraction agents
  search/supporting_records.jsonl   human comparator (HU) and extra background (BG) records
  cohorts.json                      {cohort_id: {"label", "basis", "members": [ID, ...]}}
  datasets.jsonl                    curated dataset records (status, granularity, linked IDs)

Outputs:
  articles.jsonl                    one row per included/supporting article (explicit nulls)
  index.md                          master index (overview text from search/index_overview.md)
  articles/*.md                     fills the "Cohort identifier", "Dataset status", "Primary category"
                                    and "Secondary tags" rows

Categories: the review's categories for CB articles are the NLP categories in
data/syndromes/article_categories.csv (categorise_articles.py: nlp_primary, nlp_secondary). The
extraction agents' labels are kept as agent_primary_category / agent_secondary_tags, and are used
only where the NLP finds no category (category_source says which). There is no human review step.

Usage:
    python -I scripts/build_outputs.py
"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "search"
# Access date of the round 1-3 records; records from later rounds carry their own access_date.
DEFAULT_ACCESS_DATE = "2026-10-23"
CAT_NAMES = {
    "ERY": "Erythrocyte injury, haemolysis, anaemia and immune-mediated processes",
    "INF": "Inflammation, innate/adaptive immunity and immunopathology",
    "END": "Endothelium, microcirculation, perfusion and tissue hypoxia",
    "COA": "Coagulation, platelets, immunothrombosis and DIC",
    "REN": "Renal injury and renal function",
    "PUL": "Pulmonary injury and gas exchange",
    "NEU": "Neurological and cerebral disease",
    "CAR": "Cardiac injury and haemodynamics",
    "MET": "Hepatic, metabolic, endocrine and acid-base disturbances",
    "OXO": "Oxidative stress, host-parasite interaction, omics and virulence",
    "SEV": "Multisystem clinical phenotype, severity and outcome",
}
CAT_ORDER = list(CAT_NAMES)
# Short names used in the notes' "Primary category" row (the most common wording in rounds 1-3).
NOTE_CAT = {
    "ERY": "erythrocyte injury/haemolysis/anaemia/immune-mediated",
    "INF": "inflammation/immunity/acute phase/immunopathology",
    "END": "endothelium/microcirculation/perfusion/hypoxia",
    "COA": "coagulation/platelets/immunothrombosis/DIC",
    "REN": "renal",
    "PUL": "pulmonary",
    "NEU": "neurological/cerebral",
    "CAR": "cardiac/haemodynamic",
    "MET": "hepatic/metabolic/endocrine/glucose/lactate/acid-base/electrolytes",
    "OXO": "oxidative stress/host-parasite interaction/omics/virulence",
    "SEV": "multisystem clinical phenotype, severity and outcome",
}
NLP_CATEGORIES = ROOT / "data" / "syndromes" / "article_categories.csv"
DS_STATUS = {1: "Public download verified", 2: "Public record verified; file retrieval unverified",
             3: "Request-only or controlled access", 4: "Not located after documented checks",
             5: "Not assessed/access blocked"}
STATUS_SHORT = {1: "verified download", 2: "public record (files unverified)", 3: "request-only",
                4: "not located", 5: "not assessed/blocked"}


def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()] if path.exists() else []


def md_escape(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def nlp_categories():
    """id -> (primary, [secondary], confidence) from categorise_articles.py; primary "none" when nothing scored."""
    if not NLP_CATEGORIES.exists():
        return {}
    return {r["id"]: (r["nlp_primary"], r["nlp_secondary"].split(), r["confidence"])
            for r in csv.DictReader(open(NLP_CATEGORIES, encoding="utf-8"))}


def categories(rid, r, nlp):
    """The review's categories for one CB record: NLP where it found one, else the agents' labels."""
    agent_p, agent_s = r.get("primary_category"), r.get("secondary_tags") or []
    if not rid.startswith("CB"):  # BG001 (seed review) keeps its own label; only canine evidence is categorised
        return {"primary_category": agent_p, "secondary_tags": agent_s, "category_source": None,
                "category_confidence": None, "agent_primary_category": None, "agent_secondary_tags": None}
    n = nlp.get(rid)
    if n and n[0] in CAT_NAMES:
        return {"primary_category": n[0], "secondary_tags": n[1], "category_source": "nlp",
                "category_confidence": n[2], "agent_primary_category": agent_p, "agent_secondary_tags": agent_s}
    return {"primary_category": agent_p, "secondary_tags": agent_s,
            "category_source": "agent (NLP found no category)" if n else "agent (not yet run through the NLP)",
            "category_confidence": None, "agent_primary_category": agent_p, "agent_secondary_tags": agent_s}


def category_rows(c):
    """Note rows for the categories, saying where they came from."""
    p = c["primary_category"]
    if c["category_source"] == "nlp":
        src = f"NLP, {c['category_confidence']} confidence"
        if c["agent_primary_category"] and c["agent_primary_category"] != p:
            src += f"; agent label was {c['agent_primary_category']}"
    else:  # "agent (NLP found no category)" -> "agent label; NLP found no category"
        src = "agent label; " + c["category_source"][len("agent ("):-1]
    prim =f"{p} — {NOTE_CAT.get(p, '?')} ({src})" if p else f"not assigned ({src})"
    sec = (", ".join(c["secondary_tags"]) or "none") + (" (NLP)" if c["category_source"] == "nlp" else "")
    return prim, sec


def anchor(s):
    return re.sub(r"[^a-z0-9 -]", "", s.lower()).strip().replace(" ", "-")


def main():
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    by_id = {v["id"]: dict(v, key=k) for k, v in reg.items()}
    recs = {r["id"]: r for r in jl(S / "extraction_records.jsonl")}
    sup = {r["id"]: r for r in jl(S / "supporting_records.jsonl")}
    cohorts = json.loads((ROOT / "cohorts.json").read_text(encoding="utf-8")) if (ROOT / "cohorts.json").exists() else {}
    member_cohort = {m: cid for cid, c in cohorts.items() for m in c["members"]}
    datasets = jl(ROOT / "datasets.jsonl")
    art_ds = defaultdict(list)
    for d in datasets:
        for a in d.get("linked_articles") or []:
            art_ds[a].append(d)
    ds_negative = {r["article_id"]: r for r in jl(S / "dataset_negative_checks.jsonl")}
    nlp = nlp_categories()

    rows = []
    for rid, r in sorted(recs.items()):
        if r.get("final_decision") != "include" or by_id.get(rid, {}).get("retired"):
            continue
        dlist = art_ds.get(rid, [])
        if dlist:
            best = min(d["status_code"] for d in dlist)
            ds_status_code = best
            ds_text = "; ".join(f"{STATUS_SHORT[d['status_code']]} — [{d['dataset_id']}](../datasets.md#{d['dataset_id'].lower()})" for d in sorted(dlist, key=lambda d: d["status_code"]))
        else:
            neg = ds_negative.get(rid)
            ds_status_code = neg["status_code"] if neg else 5
            ds_text = f"{STATUS_SHORT[ds_status_code]}" + (f" — {neg['basis']}" if neg else "")
        cohort = member_cohort.get(rid)
        cats = categories(rid, r, nlp)
        row = {
            "id": rid, "key": by_id[rid]["key"], "filename": f"articles/{by_id[rid]['filename']}",
            "scope_label": r.get("scope_label"), "include_type": r.get("include_type"),
            "title": r.get("title"), "authors": r.get("authors") or [], "journal": r.get("journal"),
            "volume_issue_pages": r.get("volume_issue_pages"), "first_pub_date": r.get("first_pub_date"),
            "online_date": r.get("online_date"), "issue_date": r.get("issue_date"), "date_note": r.get("date_note"),
            "doi": r.get("doi"), "pmid": r.get("pmid"), "pmcid": r.get("pmcid"), "language": r.get("language"),
            "corrections": r.get("corrections"), "species": r.get("species") or [], "species_short": r.get("species_short"),
            "host": r.get("host"), "country": r.get("country"), "design": r.get("design"),
            "sample_size": r.get("sample_size"), "n_infected_dogs": r.get("n_infected_dogs"), "n_controls": r.get("n_controls"),
            "cohort_id": cohort, **cats,
            "evidence_type": r.get("evidence_type"), "one_sentence_finding": r.get("one_sentence_finding"),
            "abstract_available": r.get("abstract_available"), "abstract_source": r.get("abstract_source"),
            "fulltext_checked": r.get("fulltext_checked"), "fulltext_url": r.get("fulltext_url"),
            "supplement_checked": r.get("supplement_checked"), "repository_checked": r.get("repository_checked"),
            "data_availability_statement": r.get("data_availability_statement"),
            "dataset_ids": [d["dataset_id"] for d in dlist] or None, "dataset_status_code": ds_status_code,
            "dataset_status": DS_STATUS[ds_status_code],
            "source_links": r.get("source_links") or [], "access_date": r.get("access_date") or DEFAULT_ACCESS_DATE,
            "verification_notes": r.get("verification_notes"),
        }
        rows.append(row)
        # Fill the two late-bound rows in the note (idempotent: rows are replaced each run).
        note = ROOT / row["filename"]
        if note.exists():
            t = note.read_text(encoding="utf-8")
            if cohort:
                ctext = f"{cohort} — {cohorts[cohort]['label']} (see [research map](../research-map.md#cohorts))"
            else:
                ctext = "none assigned (no overlapping publication identified)"
            t = re.sub(r"^\| Cohort identifier \|.*\|$", f"| Cohort identifier | {md_escape(ctext)} |", t, flags=re.M)
            t = re.sub(r"^\| Dataset status \|.*\|$", f"| Dataset status | {ds_text} |", t, flags=re.M)
            if cats["category_source"]:
                prim, sec = category_rows(cats)
                t = re.sub(r"^\| Primary category \|.*\|$", lambda m: f"| Primary category | {md_escape(prim)} |", t, flags=re.M)
                t = re.sub(r"^\| Secondary tags \|.*\|$", lambda m: f"| Secondary tags | {md_escape(sec)} |", t, flags=re.M)
            note.write_text(t, encoding="utf-8")
    built = {r["id"] for r in rows}
    for sid, r in sorted(sup.items()):
        # A reclassified background paper (retired, replaced_by a CB ID) leaves once its CB record is built.
        if by_id.get(sid, {}).get("retired") and by_id[sid].get("replaced_by") in built:
            continue
        rows.append(dict({k: None for k in rows[0]} if rows else {}, **dict(r, access_date=r.get("access_date") or DEFAULT_ACCESS_DATE)))
    with open(ROOT / "articles.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    canine = [r for r in rows if r["id"].startswith("CB")]
    core = [r for r in canine if r["scope_label"] == "core canine evidence"]
    reviews = [r for r in canine if r["scope_label"] == "canine review"]
    cat_counts = Counter(r["primary_category"] for r in canine)
    cohort_ids = {r["cohort_id"] for r in core if r["cohort_id"]}
    independent = sum(1 for r in core if not r["cohort_id"]) + len(cohort_ids)
    overview = (S / "index_overview.md").read_text(encoding="utf-8") if (S / "index_overview.md").exists() else ""
    L = []
    L.append("# Canine babesiosis: pathophysiology evidence and dataset map\n")
    L.append(overview.strip() + "\n")
    L.append("## Counts\n")
    L.append(f"- Canine articles included: **{len(canine)}** ({len(core)} primary studies/case reports; {len(reviews)} canine reviews).")
    L.append(f"- Independent cohorts/data sources among primary canine studies: **{independent}** ({len(cohort_ids)} shared cohort identifiers covering {sum(1 for r in core if r['cohort_id'])} articles).")
    L.append(f"- Supporting references (not counted as eligible canine evidence): {sum(1 for r in rows if r['id'].startswith('HU'))} human comparator, {sum(1 for r in rows if r['id'].startswith('BG'))} background.\n")
    L.append("| Primary category | Articles (primary category; sums to total) | Articles tagged as secondary (overlapping) |")
    L.append("|---|---|---|")
    sec = Counter(t for r in canine for t in set(r["secondary_tags"]) if t != r["primary_category"])
    for c in CAT_ORDER:
        L.append(f"| [{c} — {CAT_NAMES[c]}](#{anchor(c + ' — ' + CAT_NAMES[c])}) | {cat_counts.get(c, 0)} | {sec.get(c, 0)} |")
    L.append(f"| **Total** | **{sum(cat_counts.values())}** | (overlapping; not summed) |\n")
    L.append("Categories are assigned by the NLP (scispaCy concepts scored by `scripts/categorise_articles.py`), with no human "
             f"review. Where the NLP finds no category, the extraction agents' label is used ({sum(1 for r in canine if r['category_source'] != 'nlp')} "
             "articles); `category_source` in [articles.jsonl](articles.jsonl) says which, and `agent_primary_category` keeps the agents' label.\n")
    L.append("Other outputs: [research map](research-map.md) · [datasets](datasets.md) · [search log](search-log.md) · "
             "[articles.jsonl](articles.jsonl) · [datasets.jsonl](datasets.jsonl) · [download manifest](data/manifest.jsonl)\n")
    L.append("Dataset status codes: 1 = public download verified; 2 = public record verified, file retrieval unverified; "
             "3 = request-only/controlled; 4 = not located after documented checks; 5 = not assessed/access blocked.\n")
    L.append("## Core canine articles by primary category\n")
    for c in CAT_ORDER:
        group = sorted([r for r in canine if r["primary_category"] == c], key=lambda r: (r["first_pub_date"] or "", r["id"]))
        L.append(f"### {c} — {CAT_NAMES[c]}\n")
        if not group:
            L.append("_No included articles._\n")
            continue
        L.append("| ID | Year | Title | Journal | Species | Design | Finding (one sentence) | Data |")
        L.append("|---|---|---|---|---|---|---|---|")
        for r in group:
            title = f"[{md_escape(r['title'])}]({r['filename']})"
            design = md_escape(r["design"]) + (" *(review)*" if r["scope_label"] == "canine review" else "")
            L.append(f"| {r['id']} | {(r['first_pub_date'] or '')[:4]} | {title} | {md_escape(r['journal'])} | "
                     f"{md_escape(r['species_short'])} | {design} | {md_escape(r['one_sentence_finding'])} | {r['dataset_status_code']} |")
        L.append("")
    L.append("## Supporting references (excluded from canine counts)\n")
    L.append("| ID | Scope | Year | Title | Journal | Relevance |")
    L.append("|---|---|---|---|---|---|")
    for r in sorted([r for r in rows if not r["id"].startswith("CB")], key=lambda r: r["id"]):
        L.append(f"| {r['id']} | {r['scope_label']} | {(r.get('first_pub_date') or '')[:4]} | [{md_escape(r['title'])}]({r['filename']}) | "
                 f"{md_escape(r.get('journal'))} | {md_escape(r.get('one_sentence_finding'))} |")
    (ROOT / "index.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"canine={len(canine)} core={len(core)} reviews={len(reviews)} independent={independent} supporting={len(rows) - len(canine)}")
    print(dict(cat_counts))


if __name__ == "__main__":
    main()
