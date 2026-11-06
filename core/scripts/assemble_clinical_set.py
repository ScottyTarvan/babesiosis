"""Merge the included-article tagging and build the combined clinical-plus-treatment set.

Reads
  search/clinical_treatment/articles/results/ia_NN.json     tagging of the 444 included CB articles
  search/clinical_treatment/articles/adjudications*.jsonl   optional overrides by article_id
  search/clinical_treatment/screening.jsonl                 the re-screen of excluded records
                                                            (assemble_clinical_rescreen.py)
and writes
  search/clinical_treatment/articles/tagging.jsonl   one row per CB article: metadata + decision fields
  search/clinical_treatment/combined_set.csv         includes and uncertains from BOTH passes, one row
                                                     per paper, with `source` = main_review | rescreen

Checks: every CB article tagged once; decisions, include types and exclude codes valid; a
re-screen reference-list entry (no PMID/DOI) whose title near-matches an identified record is
dropped as a duplicate; a re-screen record whose DOI, PMID or title matches a main-review article
is dropped as overlap.

Usage (from core/):
    python -I scripts/assemble_clinical_set.py
"""
import collections
import csv
import json
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "search" / "clinical_treatment"
A = D / "articles"
INCLUDE_TYPES = {"trial", "retrospective_series", "case_series", "case_report", "experimental", "review"}
EXCLUDE_REASONS = {"no_dog_clinical_data", "prevention_only", "pharmacology_healthy", "no_treatment", "no_syndrome",
                   "babesia_incidental", "not_peer_reviewed", "not_research"}
ROLES = {"primary", "context", "none", None}
DECISION_FIELDS = ["decision", "include_type", "exclude_reason", "treatment_role", "syndromes", "treatments",
                   "outcome_reported", "species", "coinfection", "n_dogs", "rationale", "sources", "access_note"]
COLS = ["source", "article_id", "key", "decision", "include_type", "treatment_role", "first_pub_date", "title",
        "journal", "doi", "pmid", "species", "coinfection", "n_dogs", "syndromes", "treatments", "outcome_reported",
        "primary_category", "design", "cohort_id", "original_reason", "rationale", "stage", "access_note"]


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:70]


def main():
    arts = {r["id"]: r for r in (json.loads(l) for l in (ROOT / "articles.jsonl").open(encoding="utf-8"))
            if r["id"].startswith("CB")}
    cands = [json.loads(l) for l in (A / "candidates.jsonl").open(encoding="utf-8") if l.strip()]
    results, problems = {}, []
    for f in sorted((A / "results").glob("ia_*.json")):
        try:
            arr = json.loads(f.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as e:
            problems.append(f"{f.name}: invalid JSON ({e})")
            continue
        for r in arr:
            k = r.get("article_id")
            if k in results:
                problems.append(f"{f.name}: duplicate article {k}")
            r["batch"], r["stage"] = f.name, "screen"
            results[k] = r
    for adj in sorted(A.glob("adjudications*.jsonl")):
        for l in adj.open(encoding="utf-8-sig"):
            if l.strip():
                r = json.loads(l)
                r["stage"] = "adjudicated"
                r.setdefault("batch", results.get(r["article_id"], {}).get("batch"))
                results[r["article_id"]] = r
    tagged, missing = [], []
    for c in cands:
        r = results.get(c["article_id"])
        if not r:
            missing.append(c["article_id"])
            continue
        d = r.get("decision")
        if d not in ("include", "exclude", "uncertain"):
            problems.append(f"{c['article_id']}: bad decision {d!r}")
        if d == "include" and r.get("include_type") not in INCLUDE_TYPES:
            problems.append(f"{c['article_id']}: include with include_type {r.get('include_type')!r}")
        if d == "exclude" and r.get("exclude_reason") not in EXCLUDE_REASONS:
            problems.append(f"{c['article_id']}: exclude with reason {r.get('exclude_reason')!r}")
        if r.get("treatment_role") not in ROLES:
            problems.append(f"{c['article_id']}: treatment_role {r.get('treatment_role')!r}")
        a = arts[c["article_id"]]
        row = {k: c.get(k) for k in ("article_id", "key", "title", "journal", "first_pub_date", "doi", "pmid",
                                     "design", "primary_category", "fulltext_format")}
        row["cohort_id"] = a.get("cohort_id")
        row.update({k: r.get(k) for k in DECISION_FIELDS})
        row["stage"], row["batch"] = r["stage"], r.get("batch")
        tagged.append(row)
    extra = set(results) - {c["article_id"] for c in cands}
    if extra:
        problems.append(f"results for unknown articles: {sorted(extra)[:10]}")
    if missing:
        problems.append(f"{len(missing)} articles not tagged: {missing[:10]}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print(" -", p)
        if missing or any("invalid JSON" in p for p in problems):
            raise SystemExit(1)
    with (A / "tagging.jsonl").open("w", encoding="utf-8") as f:
        for row in tagged:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # ---- combined set ----
    main_rows = []
    for t in tagged:
        if t["decision"] == "exclude":
            continue
        row = {k: t.get(k) for k in COLS}
        row["source"], row["original_reason"] = "main_review", None
        main_rows.append(row)
    art_doi = {(a.get("doi") or "").lower() for a in arts.values() if a.get("doi")}
    art_pmid = {str(a.get("pmid")) for a in arts.values() if a.get("pmid")}
    art_titles = {norm_title(a["title"]) for a in arts.values()}
    rescreen = [json.loads(l) for l in (D / "screening.jsonl").open(encoding="utf-8") if l.strip()]
    kept, seen_titles, dropped_dup, overlap = [], {}, [], []
    # records with a PMID/DOI first, so title-duplicate reference entries fall onto them
    for r in sorted((r for r in rescreen if r["decision"] != "exclude"),
                    key=lambda r: (not (r.get("pmid") or r.get("doi")), r["key"])):
        if ((r.get("doi") or "").lower() in art_doi or str(r.get("pmid")) in art_pmid
                or norm_title(r.get("title")) in art_titles):
            overlap.append(r["key"])
            continue
        nt = norm_title(r.get("title"))
        # a reference-list entry (no PMID/DOI) whose title near-matches an identified record is the same paper
        if nt and not (r.get("pmid") or r.get("doi")):
            match = next((k for t, k in seen_titles.items() if SequenceMatcher(None, nt, t).ratio() > 0.9), None)
            if match:
                dropped_dup.append((r["key"], match))
                continue
        seen_titles[nt] = r["key"]
        row = {k: r.get(k) for k in COLS}
        row["source"] = "rescreen"
        kept.append(row)
    rows = main_rows + kept
    rows.sort(key=lambda r: (r["decision"] != "include", r.get("first_pub_date") or "", r.get("title") or ""))
    with (D / "combined_set.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            r = dict(r)
            for k in ("syndromes", "treatments"):
                r[k] = "; ".join(r.get(k) or [])
            if isinstance(r.get("access_note"), list):
                r["access_note"] = "; ".join(r["access_note"])
            w.writerow(r)

    # ---- report ----
    C = collections.Counter
    inc_t = [t for t in tagged if t["decision"] == "include"]
    print(f"tagged {len(tagged)} articles:", dict(C(t["decision"] for t in tagged)))
    print(" include types:", dict(C(t["include_type"] for t in inc_t)))
    print(" treatment_role (includes):", dict(C(t["treatment_role"] for t in inc_t)))
    print(" exclude reasons:", dict(C(t["exclude_reason"] for t in tagged if t["decision"] == "exclude")))
    print(" by primary category (includes):", C(t["primary_category"] for t in inc_t).most_common())
    print(" stage:", dict(C(t["stage"] for t in tagged)))
    print(f"rescreen: kept {len(kept)}, dropped title duplicates {dropped_dup}, overlap with main review {overlap}")
    print(f"combined_set.csv: {len(rows)} rows;", dict(C((r["source"], r["decision"]) for r in rows)))
    inc = [r for r in rows if r["decision"] == "include"]
    print(" includes by type:", dict(C(r["include_type"] for r in inc)))
    print(" top syndromes:", C(s for r in inc for s in (r.get("syndromes") or [])).most_common(12))
    print(" top treatments:", C(s for r in inc for s in (r.get("treatments") or [])).most_common(12))


if __name__ == "__main__":
    main()
