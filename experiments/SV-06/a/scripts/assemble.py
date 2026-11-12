"""SV-06a assembly: family files + local search -> transfer grid, ranked gaps, part-b hand-over, database load file.

Inputs : families/F1..F7.json (sub-agent rows), out/local_hits.json, out/reference_lookup.json (scripts/local_search.py),
         /experiments/shared/tidy/DS02.features.json (variable names only).
Outputs: out/transfer_grid.csv, out/ranked_gaps.csv, out/family_summary.csv, out/candidates_for_partb.json,
         out/db/SV-06-01-transfer-grid.json.
Rules  : spec.md (gap, testable_now and ranking are recomputed here; the agents' own values are kept for comparison).
No random numbers.
"""
import csv, glob, hashlib, json, os, sys
from collections import Counter, OrderedDict
from datetime import datetime, timezone

ROOT = r"C:\Workspaces\Babesiosis"
PKG = os.path.join(ROOT, "experiments", "SV-06", "a")
OUT = os.path.join(PKG, "out")
CODE = "SV-06-01-transfer-grid"

# DS02 variables that measure a mechanism directly (names from shared/tidy/DS02.features.json)
DS02_MAP = {"F1-01": ["cfhb"], "F6-03": ["lactate", "lactate_clinical", "glucose"], "F7-01": ["il10", "tnfa"], "F3-13": ["neut_band"]}
# The part-b analysis family, fixed in /experiments/SV-06-mechanism-transfer.md (gene symbols / DS07 names)
PARTB_FAMILY = OrderedDict([
    ("haemoglobin alpha", ["HBA"]), ("haemoglobin beta", ["HBB"]), ("haptoglobin", ["HP", "LOC479668"]),
    ("lactoferrin", ["LTF"]), ("S100A8", ["S100A8"]), ("histone H4", ["H4C7", "H4C11", "H4-16", "H4"]),
    ("alpha-2-antiplasmin", ["SERPINF2"]), ("protein C", ["PROC"]), ("antithrombin", ["SERPINC1"]),
    ("complement factor H", ["CFH"]), ("CD14", ["CD14", "607076"]),
])
GRADE_ORDER = {"validated": 0, "used_in_dogs": 1, "none": 2}
TEST_ORDER = {"public_file": 0, "stored_samples_only": 1, "no": 2}
STATUS_ORDER = {"none": 0, "measured_no_severity": 1, "severity_tested": 2}


def sha(path, n=None):
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    return h[:n] if n else h


def j(path):
    return json.load(open(path, encoding="utf-8"))


def lst(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def main():
    fams = sorted(glob.glob(os.path.join(PKG, "families", "F[0-9].json")))
    if len(fams) != 7:
        print(f"expected 7 family files, found {len(fams)}", file=sys.stderr)
        return 1
    hits = j(os.path.join(OUT, "local_hits.json"))
    look = j(os.path.join(OUT, "reference_lookup.json"))
    ds02_vars = {v["name"] for v in j(os.path.join(ROOT, "experiments", "shared", "tidy", "DS02.features.json"))["variables"]}

    rows, fam_summ, checks = [], [], []
    for f in fams:
        fam = j(f)
        fam_summ.append({"family": fam["family"], "agent_summary": fam.get("agent_summary", "")})
        for m in fam["mechanisms"]:
            mid = m["mechanism_id"]
            h = hits["hits"].get(mid, {})
            lk = look["lookup"].get(mid, {})
            if not h or not lk:
                checks.append(f"{mid}: not in local search output (run local_search.py after the family files)")
            ds07_master = [p for p in lk.get("ds07_master", []) if p["status"] == "master"]
            ds07_cand = [p for p in lk.get("ds07_master", []) if p["status"] != "master"]
            ds06 = lk.get("ds06_genes", [])
            ds02 = [v for v in DS02_MAP.get(mid, []) if v in ds02_vars]
            status = m.get("canine_status", "")
            assay = m.get("canine_assay", "")
            queries = lst((m.get("canine_pubmed") or {}).get("queries"))
            # testable_now (spec rule)
            if assay == "none" and not (ds07_master or ds02):
                testable = "no"
            elif ds07_master or ds06 or ds02:
                testable = "public_file"
            else:
                testable = "stored_samples_only"
            sev_now = "yes" if ds07_master else "no"
            strict = "public_file" if (ds07_master or ds02) else ("no" if assay == "none" else "stored_samples_only")   # only DS07 has a severity label and circulating protein
            gap = "yes" if status in ("none", "measured_no_severity") and queries else "no"
            if m.get("gap") and m.get("gap") != gap:
                checks.append(f"{mid}: agent gap {m.get('gap')} vs rule {gap}")
            if m.get("testable_now") and m.get("testable_now") != testable:
                checks.append(f"{mid}: agent testable_now {m.get('testable_now')} vs rule {testable}")
            rows.append(OrderedDict([
                ("mechanism_id", mid), ("family", m.get("family", fam["family"])), ("mechanism", m["mechanism"]),
                ("added_by_agent", m.get("added_by_agent", "no")),
                ("human_conditions", "; ".join(lst(m.get("human_conditions")))),
                ("hu_articles", "; ".join(lst(m.get("hu_articles")))),
                ("human_key_dois", "; ".join(lst(m.get("human_key_dois")))),
                ("human_n_studies", m.get("human_n_studies")), ("human_grade", m.get("human_grade")),
                ("human_direction", m.get("human_direction", "")),
                ("cb_note_hits", len(h.get("cb_note_hits", []))), ("cb_text_hits", len(h.get("cb_text_hits", []))),
                ("cb_confirmed", "; ".join(f"{c.get('id')}{' (severity)' if c.get('severity_contrast') else ''}" for c in lst(m.get("cb_confirmed")))),
                ("canine_pubmed_queries", " || ".join(queries)),
                ("canine_dog_babesiosis_dois", "; ".join(lst((m.get("canine_pubmed") or {}).get("dog_babesiosis_dois")))),
                ("canine_status", status), ("canine_severity_units", m.get("canine_severity_units", 0)),
                ("canine_assay", assay), ("assay_evidence", "; ".join(lst(m.get("assay_evidence")))),
                ("dog_genes", "; ".join(lst(m.get("dog_genes")) or lk.get("dog_genes", []))),
                ("ds07_master", "; ".join(f"{p['accession']} {p['gn'] or p['description']} ({p['coverage_pct']}%)" for p in ds07_master)),
                ("ds07_master_candidate", "; ".join(f"{p['accession']} {p['gn'] or p['description']} ({p['coverage_pct']}%)" for p in ds07_cand)),
                ("ds06_genes", "; ".join(e["ensembl"] for e in ds06)),
                ("ds02_measured", "; ".join(ds02)),
                ("testable_now", testable), ("testable_now_without_ds06", strict), ("severity_contrast_testable_now", sev_now),
                ("gap", gap), ("rank", ""), ("notes", m.get("notes", "")),
            ]))

    # ranking (spec rule)
    elig = [r for r in rows if r["gap"] == "yes" and (r["human_grade"] or 0) >= 2 and r["canine_assay"] in ("validated", "used_in_dogs")]
    elig.sort(key=lambda r: (-(r["human_grade"] or 0), GRADE_ORDER[r["canine_assay"]], TEST_ORDER[r["testable_now"]],
                             STATUS_ORDER.get(r["canine_status"], 9), r["mechanism_id"]))
    for i, r in enumerate(elig[:10], 1):
        r["rank"] = i
    ranked = [r for r in rows if r["rank"] != ""]
    beyond = elig[10:]
    # sensitivity (post hoc, D2): DS06 RNA does not count as "testable now"
    elig_s = sorted(elig, key=lambda r: (-(r["human_grade"] or 0), GRADE_ORDER[r["canine_assay"]], TEST_ORDER[r["testable_now_without_ds06"]],
                                         STATUS_ORDER.get(r["canine_status"], 9), r["mechanism_id"]))[:10]
    strict_ids = [r["mechanism_id"] for r in elig_s]
    moved_in = [r["mechanism"] for r in elig_s if r["rank"] == ""]
    moved_out = [r["mechanism"] for r in ranked if r["mechanism_id"] not in strict_ids]
    ranked.sort(key=lambda r: r["rank"])

    os.makedirs(os.path.join(OUT, "db"), exist_ok=True)
    with open(os.path.join(OUT, "transfer_grid.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with open(os.path.join(OUT, "ranked_gaps.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(ranked)

    # family summary
    fsum = []
    for fs in fam_summ:
        fr = [r for r in rows if r["family"] == fs["family"]]
        c = Counter(r["canine_status"] for r in fr)
        fsum.append(OrderedDict([("family", fs["family"]), ("mechanisms", len(fr)),
                                 ("none", c.get("none", 0)), ("measured_no_severity", c.get("measured_no_severity", 0)),
                                 ("severity_tested", c.get("severity_tested", 0)),
                                 ("gaps", sum(r["gap"] == "yes" for r in fr)),
                                 ("grade_ge2", sum((r["human_grade"] or 0) >= 2 for r in fr)),
                                 ("ranked", sum(r["rank"] != "" for r in fr)),
                                 ("agent_summary", fs["agent_summary"])]))
    with open(os.path.join(OUT, "family_summary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fsum[0].keys()))
        w.writeheader(); w.writerows(fsum)

    # part-b hand-over
    gene_to_mech = {}
    for r in rows:
        for g in [x.strip() for x in r["dog_genes"].split(";") if x.strip()]:
            gene_to_mech.setdefault(g, []).append(r["mechanism_id"])
    all_ds07 = {}
    for mid, lk in look["lookup"].items():
        for p in lk.get("ds07_master", []):
            all_ds07.setdefault(p["accession"], p).setdefault("mechanisms", [])
            if mid not in all_ds07[p["accession"]]["mechanisms"]:
                all_ds07[p["accession"]]["mechanisms"].append(mid)
    partb_rows = []
    for name, syms in PARTB_FAMILY.items():
        prot = [p for p in all_ds07.values() if p["gn"] in syms]
        mechs = sorted({m for s in syms for m in gene_to_mech.get(s, [])} | {m for p in prot for m in p.get("mechanisms", [])})
        partb_rows.append(OrderedDict([("partb_candidate", name), ("gene_symbols", syms),
                                       ("ds07", [{k: p[k] for k in ("accession", "gn", "description", "coverage_pct", "status")} for p in prot]),
                                       ("mechanisms", mechs)]))
    handover = {
        "produced_by": "SV-06a (/experiments/SV-06/a/scripts/assemble.py)", "spec_sha256": sha(os.path.join(PKG, "spec.md")),
        "note": "Part b's analysis family is fixed in /experiments/SV-06-mechanism-transfer.md; this file maps it to mechanisms and lists every mechanism with its dog genes. DS07 status 'master_candidate' is not a master protein: part b decides.",
        "partb_family_map": partb_rows,
        "mechanisms": [OrderedDict([("mechanism_id", r["mechanism_id"]), ("family", r["family"]), ("mechanism", r["mechanism"]),
                                    ("dog_genes", [x.strip() for x in r["dog_genes"].split(";") if x.strip()]),
                                    ("ds07_master", [p for p in look["lookup"].get(r["mechanism_id"], {}).get("ds07_master", [])]),
                                    ("ds06_ensembl", [x for x in r["ds06_genes"].split("; ") if x]),
                                    ("ds02_measured", [x for x in r["ds02_measured"].split("; ") if x]),
                                    ("canine_status", r["canine_status"]), ("gap", r["gap"]), ("rank", r["rank"] or None),
                                    ("human_grade", r["human_grade"])]) for r in rows],
    }
    json.dump(handover, open(os.path.join(OUT, "candidates_for_partb.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    # numbers for the text
    n = len(rows)
    n_gap = sum(r["gap"] == "yes" for r in rows)
    g2 = [r for r in rows if (r["human_grade"] or 0) >= 2]
    g2_gap = [r for r in g2 if r["gap"] == "yes"]
    g3 = [r for r in rows if (r["human_grade"] or 0) >= 3]
    g3_tested = [r for r in g3 if r["canine_status"] == "severity_tested"]
    st = Counter(r["canine_status"] for r in rows)
    n_added = sum(r["added_by_agent"] == "yes" for r in rows)
    ranked_in_ds07 = [r for r in ranked if r["severity_contrast_testable_now"] == "yes"]
    ranked_no_ds07 = [r for r in ranked if r["severity_contrast_testable_now"] != "yes"]
    excluded_no_assay = [r for r in rows if r["gap"] == "yes" and (r["human_grade"] or 0) >= 2 and r["canine_assay"] == "none"]
    share = (len(g2_gap) / len(g2)) if g2 else None
    premise = "holds" if share is not None and share >= 0.5 else "is weak"

    names = lambda rs: "; ".join(f"{r['rank'] or r['mechanism_id']}. {r['mechanism']}" if r['rank'] else r["mechanism"] for r in rs)
    summary = (f"{n} mechanisms in 7 families: {n_gap} are gaps (no canine severity data; {st.get('none', 0)} never measured in dogs with "
               f"babesiosis), {st.get('severity_tested', 0)} already tested against severity. {len(g2_gap)} of {len(g2)} mechanisms with "
               f"human grade 2 or 3 are gaps; {len(elig)} meet the ranking rule; of the top {len(ranked)}, {len(ranked_in_ds07)} have a protein in the DS07 proteome. No statistical tests.")

    run_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    interp = {"sections": [
        {"heading": "Question", "paragraphs": [
            "Which mechanisms linked to severity in malaria, human babesiosis and sepsis have not been measured against severity in dogs with babesiosis, "
            "have a canine assay, and could be tested now? Premise: most mechanisms with good human evidence are unmeasured in dogs."]},
        {"heading": "What was done", "paragraphs": [
            f"Seven sub-agents, one per mechanism family, graded {n} mechanisms ({n - n_added} seeds fixed in the spec, {n_added} added by agents) "
            "on the human evidence (HU comparator notes, then targeted PubMed searches), the canine evidence (a keyword search of the 444 CB notes "
            f"and {look['meta']['n_cb_texts']} CB texts, of which {look['meta']['n_cb_texts_fulltext']} are full texts, read and confirmed by the agent, then PubMed), "
            "the canine assay, and whether a public file holds the protein or gene. Gap, testability and rank were then recomputed by a script from the rules of the spec.",
            "Ranking rule: a gap, human grade 2 or more, and a canine assay; then ordered by human grade, assay, test-now and the number of canine studies. At most 10."]},
        {"heading": "Result", "paragraphs": [
            f"{n_gap} of {n} mechanisms are gaps: {st.get('none', 0)} were never measured in dogs with babesiosis and {st.get('measured_no_severity', 0)} were measured "
            f"only against controls or over time. {st.get('severity_tested', 0)} have canine severity data.",
            f"Of {len(g2)} mechanisms with human grade 2 or 3, {len(g2_gap)} are gaps ({'' if share is None else f'{100*share:.0f}%'}), so the premise {premise}. "
            f"Of the {len(g3)} grade-3 mechanisms, {len(g3_tested)} already have canine severity data.",
            f"{len(elig)} mechanisms meet the ranking rule; the top {len(ranked)}: {names(ranked)}."
            + (f" Eligible but below the cut of 10: {'; '.join(r['mechanism'] for r in beyond)}." if beyond else ""),
            (f"{len(ranked_in_ds07)} ranked mechanisms have a master protein in the DS07 serum proteome (complicated against uncomplicated B. rossi), so part b can look at them now: "
             f"{'; '.join(r['mechanism'] for r in ranked_in_ds07) or 'none'}. The other {len(ranked_no_ds07)} have no circulating-protein measure in any public file (at most DS06 blood RNA) and need stored samples and a canine assay.")
            ,
            (f"Sensitivity (post hoc): if DS06 blood RNA does not count as testable now, the top 10 gains {'; '.join(moved_in) or 'nothing'} and loses {'; '.join(moved_out) or 'nothing'}."),
            (f"Gaps with strong human evidence but no canine assay found (excluded from the ranking): {'; '.join(r['mechanism'] for r in excluded_no_assay)}."
             if excluded_no_assay else "Every gap with strong human evidence has some canine assay.")]},
        {"heading": "What this does not show", "paragraphs": [
            "A gap means not found in PubMed and in the local corpus on 2026-11-12; about half the CB texts are abstracts only, and one database was searched. "
            "Grades are agent judgements recorded with their DOIs; no human reviewed them.",
            "Human evidence does not transfer by itself: B. rossi, B. canis and B. gibsoni differ from P. falciparum (no cytoadherence of the same kind is established), "
            "and sepsis is a different disease. The list says what to measure, not what will be found.",
            "A DS06 gene is expression in the blood of 5 experimental Beagles, not circulating protein, and that file has no severity contrast beyond one death. "
            "DS07 has a severity label but 14 against 18 dogs and no clinical values; proteins that follow anaemia (haemoglobin, haptoglobin) partly restate the label. No test was run here."]},
    ]}

    load = {
        "experiment": {
            "code": CODE,
            "name": "Human-to-dog mechanism transfer grid: severity mechanisms from malaria, human babesiosis and sepsis that are unmeasured in canine babesiosis",
            "description": ("Which mechanisms linked to severity in malaria, human babesiosis and sepsis have not been measured against severity in dogs with babesiosis, "
                            "have a canine assay, and could be tested now? Premise: most mechanisms with good human evidence are unmeasured in dogs."),
            "method": "mechanism_transfer_grid", "dataset": None,
            "parameters": {"package": "SV-06", "part": "a", "role": "descriptive", "datasets": ["DS07 (protein list only)", "DS06 (gene list only)", "DS02 (variable names only)"],
                           "independent_sources": ["SRC-C", "SRC-B"], "spec_sha256": sha(os.path.join(PKG, "spec.md")), "seeds": None,
                           "families": 7, "mechanisms": n, "added_by_agents": n_added, "pubmed_date": "2026-11-12",
                           "note": "No outcomes file opened; no statistical test."},
            "script": "/experiments/SV-06/a/scripts/assemble.py", "script_version": sha(os.path.abspath(__file__), 12),
            "run_utc": run_utc, "n_subjects": 0, "n_variables": n, "n_tests": 0, "summary": summary,
        },
        "results": [
            {"kind": "primary_result", "title": "Ranked gaps and grid totals", "sort_order": 1, "payload": {
                "n_mechanisms": n, "n_seed": n - n_added, "n_added": n_added, "n_gap": n_gap,
                "status_counts": {k: st.get(k, 0) for k in ("none", "measured_no_severity", "severity_tested")},
                "n_grade_ge2": len(g2), "n_grade_ge2_gap": len(g2_gap), "share_grade_ge2_gap": None if share is None else round(share, 3),
                "n_grade3": len(g3), "n_grade3_severity_tested": len(g3_tested), "premise": premise,
                "sensitivity_without_ds06": {"ranked": [{"rank": i + 1, "mechanism_id": r["mechanism_id"], "mechanism": r["mechanism"],
                                                          "testable_now_without_ds06": r["testable_now_without_ds06"]} for i, r in enumerate(elig_s)],
                                             "moved_in": moved_in, "moved_out": moved_out},
                "n_eligible": len(elig), "eligible_not_ranked": [r["mechanism"] for r in beyond],
                "n_ranked": len(ranked), "n_ranked_in_ds07": len(ranked_in_ds07),
                "excluded_no_assay": [r["mechanism"] for r in excluded_no_assay],
                "ranked": [{k: r[k] for k in ("rank", "mechanism_id", "family", "mechanism", "human_grade", "human_n_studies", "human_conditions",
                                              "human_direction", "canine_status", "canine_assay", "testable_now", "severity_contrast_testable_now",
                                              "ds07_master", "human_key_dois", "assay_evidence")} for r in ranked]}},
            {"kind": "family_summary", "title": "Canine status by mechanism family", "sort_order": 2, "payload": {"rows": fsum}},
            {"kind": "transfer_grid", "title": "The transfer grid", "sort_order": 3, "payload": {"rows": [
                {k: r[k] for k in ("mechanism_id", "family", "mechanism", "added_by_agent", "human_conditions", "hu_articles", "human_grade",
                                   "human_n_studies", "human_direction", "cb_note_hits", "cb_text_hits", "cb_confirmed", "canine_status",
                                   "canine_severity_units", "canine_assay", "testable_now", "severity_contrast_testable_now", "ds07_master",
                                   "ds02_measured", "gap", "rank", "human_key_dois", "canine_dog_babesiosis_dois", "assay_evidence", "notes")}
                for r in rows]}},
            {"kind": "partb_handover", "title": "Hand-over to part b: the DS07 candidate family mapped to mechanisms", "sort_order": 4, "payload": {
                "file": "/experiments/SV-06/a/out/candidates_for_partb.json",
                "rows": [{"partb_candidate": p["partb_candidate"], "ds07": "; ".join(f"{d['accession']} {d['gn']} {d['status']} ({d['coverage_pct']}%)" for d in p["ds07"]) or "not found",
                          "mechanisms": "; ".join(p["mechanisms"])} for p in partb_rows]}},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp},
        ],
        "checks": checks,
    }
    json.dump(load, open(os.path.join(OUT, "db", f"{CODE}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False, allow_nan=False)
    print(summary)
    print("checks:", len(checks)); [print("  ", c) for c in checks]
    print("ranked:", [(r["rank"], r["mechanism_id"], r["mechanism"][:40], r["severity_contrast_testable_now"]) for r in ranked])
    return 0


if __name__ == "__main__":
    sys.exit(main())
