"""Build the queue for the human category review page (data/syndromes/review/).

The queue holds every article where the scispaCy categorisation and the agents' category disagree on the
primary category, then a random sample of articles where they agree (to check whether both can be wrong
together). Each item carries what a reviewer needs to decide: title, journal and year, design, species,
sample, whether only the abstract was available, the review's own abstract-derived summary (articles/*.md,
written for this review, not the authors' text), a DOI/PubMed link, and both methods' categories with the
evidence behind the scispaCy call, its studied/mentioned split and the rule-based study aim.

Articles already reviewed (exported to data/syndromes/review/export/decisions/) stay in the queue even when
a rescoring moves them out of the disagreements; they are marked as not part of the random sample
(`sampled` false), so the whole-set estimate uses only the census of disagreements and the random sample.

Writes data/syndromes/review/queue.json, published with the review page. Decisions are kept in the page's
database and exported with the ArtifactData tool to data/syndromes/review/export/.

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/build_review_queue.py [--agree-sample 30] [--seed 20261025]
"""
import argparse
import csv
import json
import sys
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from categorise_articles import AIMS  # noqa: E402
SYN = ROOT / "data" / "syndromes"
OUT = SYN / "review" / "queue.json"
CATEGORIES = {
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


def summary(aid):
    p = next((ROOT / "articles").glob(f"{aid}_*.md"), None)
    if not p:
        return ""
    m = re.search(r"^## Abstract-derived summary\s*\n(.*?)(?=^## |\Z)", p.read_text(encoding="utf-8"), re.S | re.M)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--agree-sample", type=int, default=30)
    ap.add_argument("--seed", type=int, default=20261025)
    args = ap.parse_args()
    arts = {a["id"]: a for a in map(json.loads, open(ROOT / "articles.jsonl", encoding="utf-8"))}
    rows = [r for r in csv.DictReader(open(SYN / "article_categories.csv", encoding="utf-8")) if r["agent_primary"]]
    dis = [r for r in rows if r["agree_primary"] != "True"]
    agr = [r for r in rows if r["agree_primary"] == "True"]
    random.Random(args.seed).shuffle(agr)
    sample = sorted(agr[: args.agree_sample], key=lambda r: r["id"])
    in_queue = {r["id"] for r in dis + sample}
    done = {p.stem for p in (SYN / "review" / "export" / "decisions").glob("*.json")}
    earlier = [r for r in agr if r["id"] in done and r["id"] not in in_queue]
    # disagreements: high-confidence scispaCy calls first (most informative), then by ID
    dis.sort(key=lambda r: (r["confidence"] != "high", r["id"]))

    items = []
    for group, rs in (("disagreement", dis), ("agreement sample", sample), ("agreement, reviewed earlier", earlier)):
        for r in rs:
            a = arts[r["id"]]
            scores = {c: float(r[f"score_{c}"]) for c in CATEGORIES}
            mscores = {c: float(r[f"mscore_{c}"]) for c in CATEGORIES}
            link = (f"https://doi.org/{a['doi']}" if a.get("doi") else
                    f"https://pubmed.ncbi.nlm.nih.gov/{a['pmid']}/" if a.get("pmid") else None)
            items.append({
                "id": r["id"], "group": group, "sampled": group != "agreement, reviewed earlier", "title": a["title"], "journal": a.get("journal"),
                "year": (a.get("first_pub_date") or "")[:4], "design": a.get("design"), "sample": a.get("sample_size"),
                "species": a.get("species_short"), "type": a.get("include_type"),
                "text": "abstract only" if r["source_format"] == "abstract" else "full text",
                "finding": a.get("one_sentence_finding"), "summary": summary(r["id"]), "link": link,
                "nlp": {"primary": r["nlp_primary"], "secondary": r["nlp_secondary"].split(), "confidence": r["confidence"],
                        "mentioned": r["nlp_mentioned"].split(), "aim": r["aim"], "aim_evidence": r["aim_evidence"],
                        "evidence": r["primary_evidence"], "scores": {c: round(s, 1) for c, s in scores.items() if s > 0},
                        "mscores": {c: round(s, 1) for c, s in mscores.items() if s > 0}},
                "agent": {"primary": r["agent_primary"], "secondary": r["agent_secondary"].split()},
            })
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"categories": CATEGORIES, "aims": AIMS, "seed": args.seed, "items": items}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(dis)} disagreements + {len(sample)} agreements + {len(earlier)} reviewed earlier = {len(items)} items; {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
