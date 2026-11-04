"""Assemble research-map.md from the category syntheses, comparator analysis and cohorts.

Inputs: search/synthesis/{CROSS,ERY,...,SEV,QUESTIONS}.md (agent-written syntheses),
search/human_comparators_raw.json, cohorts.json, articles.jsonl, datasets.jsonl, ids.json.
Article links of the form [CB054](articles/...) are normalised to the registered filename,
and bare "PMID n" mentions of registered papers gain a link to their note.

Usage:
    python -I scripts/assemble_research_map.py
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYN = ROOT / "search" / "synthesis"
CATS = ["ERY", "INF", "END", "COA", "REN", "PUL", "NEU", "CAR", "MET", "OXO", "SEV"]
NAMES = {"ERY": "Erythrocyte injury, haemolysis, anaemia and immune-mediated processes", "INF": "Inflammation, innate/adaptive immunity and immunopathology",
         "END": "Endothelium, microcirculation, perfusion and tissue hypoxia", "COA": "Coagulation, platelets, immunothrombosis and DIC",
         "REN": "Renal injury and renal function", "PUL": "Pulmonary injury and gas exchange", "NEU": "Neurological and cerebral disease",
         "CAR": "Cardiac injury and haemodynamics", "MET": "Hepatic, metabolic, endocrine and acid-base disturbances",
         "OXO": "Oxidative stress, host-parasite interaction, omics and virulence", "SEV": "Multisystem clinical phenotype, severity and outcome"}


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def esc(s):
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def anchor(h):
    return re.sub(r"[^\w\- ]", "", h.lower()).strip().replace(" ", "-")


def main():
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    fn = {v["id"]: v["filename"] for v in reg.values() if not v.get("retired") and v.get("filename")}
    pmid2id = {k.split(":", 1)[1]: v["id"] for k, v in reg.items() if k.startswith("PMID:") and not v.get("retired")}
    arts = jl(ROOT / "articles.jsonl")
    canine = [a for a in arts if a["id"].startswith("CB")]
    cohorts = json.loads((ROOT / "cohorts.json").read_text(encoding="utf-8"))
    ds = jl(ROOT / "datasets.jsonl")

    def fix(text, demote=0):
        text = re.sub(r"\[((?:CB|HU|BG)\d{3})\]\(articles/[^)]*\)",
                      lambda m: f"[{m.group(1)}](articles/{fn[m.group(1)]})" if m.group(1) in fn else m.group(1), text)
        # Plain IDs not already linked
        text = re.sub(r"(?<![\[\w/])((?:CB|HU|BG)\d{3})(?![\]\w_])",
                      lambda m: f"[{m.group(1)}](articles/{fn[m.group(1)]})" if m.group(1) in fn else m.group(1), text)

        def pm(m):
            p = m.group(2)
            i = pmid2id.get(p)
            return f"{m.group(0)} ([{i}](articles/{fn[i]}))" if i and i in fn and f"[{i}]" not in text[max(0, m.start() - 80):m.end() + 80] else m.group(0)
        text = re.sub(r"(PMID[:\s]*)(\d{6,8})", pm, text)
        text = text.replace("](datasets.md#rq-", "](datasets.md#rq-")
        text = text.replace("(search/synthesis/QUESTIONS.md)", "(#research-questions)")
        if demote:
            text = re.sub(r"^(#+) ", lambda m: "#" * (len(m.group(1)) + demote) + " ", text, flags=re.M)
        return text

    member = {m: cid for cid, c in cohorts.items() for m in c["members"]}
    L = ["# Canine babesiosis research map\n",
         "[Back to article index](index.md) · [Datasets](datasets.md) · [Search log](search-log.md)\n",
         "This map synthesises the canine articles in the [index](index.md), published 2006-10-23 to 2026-10-23, by pathophysiological category. Each article's categories are assigned automatically by the NLP classifier (`scripts/categorise_articles.py`), with no human review, so a few articles sit in a category that is not their main subject; the category sections name these. Categories were revised from the provisional list by adding **SEV (multisystem clinical phenotype, severity and outcome)** for the large body of multi-organ clinicopathological and outcome studies that have no dominant organ or mechanism. Each article has one primary category (counts reconcile with the index) and any number of secondary tags (counts overlap and are not additive). Article counts are reported separately from independent cohorts: articles sharing a cohort identifier (see [Cohorts](#cohorts)) are not independent replication.\n",
         "Throughout, a **syndrome** is a clinical complication (e.g. AKI, ARDS, cerebral babesiosis), a **mechanism** is a proposed causal process (e.g. cell-free haemoglobin–driven endothelial injury), and a **severity biomarker** is a measured variable associated with severity or outcome (e.g. CRP, lactate); associations are not treated as mechanisms.\n",
         "## Category map\n",
         "| Category | Primary articles | Independent cohorts among primary (primary studies) | Secondary-tagged articles (overlapping) | Species (primary) | Evidence type (primary) | Verified individual-level datasets |",
         "|---|---|---|---|---|---|---|"]
    ds_by_art = defaultdict(list)
    for d in ds:
        if d["status_code"] == 1 and d.get("priority_rank"):
            for a in d["linked_articles"]:
                ds_by_art[a].append(d["dataset_id"])
    tot = Counter()
    for c in CATS:
        prim = [a for a in canine if a["primary_category"] == c]
        core = [a for a in prim if a["scope_label"] == "core canine evidence"]
        indep = len({member.get(a["id"], a["id"]) for a in core})
        sec = sum(1 for a in canine if c in (a["secondary_tags"] or []))
        sp = Counter(a["species_short"] if a["species_short"] in ("B. rossi", "B. canis", "B. gibsoni", "B. vogeli") else "other/mixed/unspecified" for a in prim)
        ev = Counter(("review" if a["scope_label"] == "canine review" else (a["evidence_type"] or "").split(" ")[0].split("/")[0]) for a in prim)
        dsl = sorted({d for a in prim for d in ds_by_art.get(a["id"], [])})
        tot["prim"] += len(prim)
        L.append(f"| [{c} — {NAMES[c]}](#{anchor(c + ' — ' + NAMES[c])}) | {len(prim)} | {indep} ({len(core)}) | {sec} | "
                 f"{', '.join(f'{k} {v}' for k, v in sp.most_common())} | {', '.join(f'{k} {v}' for k, v in ev.most_common())} | "
                 f"{', '.join(f'[{d}](datasets.md#{d.lower()})' for d in dsl) or 'none'} |")
    L.append(f"| **Total** | **{tot['prim']}** | — | (overlapping) | | | |\n")
    L.append("Datasets listed are those linked to primary-category articles; several datasets also serve other categories (see each section's *Data available*).\n")
    L.append("## Cross-cutting themes\n")
    L.append(fix((SYN / "CROSS.md").read_text(encoding="utf-8").split("\n", 1)[1].strip()) + "\n")
    L.append("## Category synthesis\n")
    for c in CATS:
        t = (SYN / f"{c}.md").read_text(encoding="utf-8").strip()
        t = re.sub(r"^#+ .*\n", f"### {c} — {NAMES[c]}\n", t, count=1)
        L.append(fix(t) + "\n")
    L.append("## Human disease comparison\n")
    L.append("Human comparator papers ([HU notes](index.md#supporting-references-excluded-from-canine-counts)) were selected per category as search leads, not equivalences. Strength: **directly demonstrated in both** = the same pathway or marker was measured in both hosts; **mechanistically plausible** = a pathway demonstrated in humans with consistent but indirect canine evidence; **speculative** = analogy only. Shared clinical signs alone were not accepted as a connection.\n")
    L.append("| Category | Shared pathway | Canine evidence | Human evidence | Key differences | Strength |")
    L.append("|---|---|---|---|---|---|")
    raw = json.loads((ROOT / "search" / "human_comparators_raw.json").read_text(encoding="utf-8"))
    for c in sorted(raw, key=lambda x: CATS.index(x["category"])):
        for k in c["connections"]:
            L.append(f"| {c['category']} | {esc(k['shared_pathway'])} | {esc(fix(k['canine_evidence']))} | {esc(fix(k['human_evidence']))} | {esc(k['differences'])} | **{k['strength']}** — {esc(k['strength_rationale'])} |")
    L.append("")
    q = fix((SYN / "QUESTIONS.md").read_text(encoding="utf-8"), demote=1)
    q = re.sub(r"^## .*\n", "## Research questions\n", q, count=1)
    L.append(q.strip() + "\n")
    L.append("## Cohorts\n")
    L.append("Shared cohort identifiers group publications that report the same animals (confirmed = stated by the authors; probable = inferred from institution, period, design and n). Ungrouped articles may still overlap; see the [search log](search-log.md#coverage-limitations).\n")
    L.append("| Cohort | Label | Certainty | Members | Basis |\n|---|---|---|---|---|")
    for cid, c in cohorts.items():
        mem = ", ".join(f"[{m}](articles/{fn[m]})" for m in c["members"] if m in fn)
        L.append(f"| {cid} | {esc(c['label'])} | {c['certainty']} | {mem} | {esc(c['basis'])} |")
    out = "\n".join(L) + "\n"
    (ROOT / "research-map.md").write_text(out, encoding="utf-8")
    print("research-map.md", len(out))


if __name__ == "__main__":
    main()
