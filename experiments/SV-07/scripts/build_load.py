"""SV-07: build out/author_query_draft.md and the console-loader file out/db/SV-07-01-linkage-audit.json from out/ (analyse.py first)."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "out"
CODE = "SV-07-01-linkage-audit"


def rd(name):
    with open(OUT / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x):
    if x in (None, ""):
        return None
    if x in ("True", "False"):
        return x == "True"
    try:
        v = float(x)
        return int(v) if v.is_integer() and "." not in x and "e" not in x.lower() else v
    except ValueError:
        return x


def typed(rows):
    return [{k: num(v) for k, v in r.items()} for r in rows]


def main():
    res = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
    links = rd("linkage.csv")
    s1, s3, s4, s5 = res["step1"], res["step3"], res["step4"], res["step5"]
    counts = res["link_counts"]
    spec_sha = hashlib.sha256((HERE / "spec.md").read_bytes()).hexdigest()
    script = HERE / "scripts" / "analyse.py"
    script_ver = hashlib.sha256(script.read_bytes()).hexdigest()[:12]

    m = s1["s050_matches"]
    rates = {(r["ds03_block"], r["against"]): r for r in s3["rates"]}
    c1 = rates[("cohort 1", "S-CB050 cohort 1")]
    c2 = rates[("cohort 2", "S-CB050 cohort 2")]
    cc = rates[("controls", "S-CB050 controls")]
    summ = {r["ds03_block"]: r for r in s3["summary"]}
    order = {r["ds03_block"]: r for r in s3["order_check"]}
    hyp = {r["universe"]: r for r in s5["hypergeometric"]}
    contra = [c for c in s5["consistency"] if c["contradiction"]]
    pc = s4["positive_control_best"]

    # ------------------------------------------------------------------ which files share dogs (file-pair table)
    unmatched = [r for r in rd("ds04_vs_scb050.csv") if r["group"] == "fatal" and not r["s050_exact"]]
    cl = min(unmatched, key=lambda r: float(r["nearest_max_reldiff"]))
    near_txt = (f"DS04 case {cl['ds04_case']} vs S-CB050 case {cl['nearest_case']}, {100 * float(cl['nearest_max_reldiff']):.1f}% apart on one count, "
                f"and that dog {cl['nearest_outcome']}")
    file_pairs = [
        dict(file_a="S-CB517", file_b="S-CB050", shared_dogs="112 (all of S-CB517)", certainty="confirmed by values", found_by="SV-G1",
             consequence="Same dogs. Never pool."),
        dict(file_a="DS03 experimental", file_b="DS02 / DS06", shared_dogs="5 Beagles", certainty="confirmed by values", found_by="SV-G1",
             consequence="Same dogs. Never pool."),
        dict(file_a="DS04", file_b="S-CB050", shared_dogs=f"3 of 10 fatal (cases 50, 54, 59 = S-CB050 {m['50']}, {m['54']}, {m['59']})",
             certainty="confirmed by values", found_by="data.md; re-checked here",
             consequence=f"The other 7 fatal DS04 dogs match no S-CB050 row (closest: {near_txt})."),
        dict(file_a="DS03 natural cohort 1", file_b="S-CB050 cases 1-97",
             shared_dogs=f"{summ['cohort 1']['with_s050_candidate']} of {summ['cohort 1']['n_complete']} with full signalment",
             certainty="probable (file level)", found_by="SV-07",
             consequence=f"Signalment twins at {c1['ratio_to_baseline']} times the chance rate; the {order['cohort 1']['unique_pairs']} unique pairs keep the study-number order (BC numbers -> cases 1-97)."),
        dict(file_a="DS03 natural cohort 2", file_b="S-CB050 cases 101-144",
             shared_dogs=f"{summ['cohort 2']['with_s050_candidate']} of {summ['cohort 2']['n_complete']}", certainty="probable (file level); 1 dog confirmed by values",
             found_by="SV-07", consequence=f"Twins at {c2['ratio_to_baseline']} times chance, in BLSC-number order. BLSC29 = S-CB050 127 = DS04 case 54 by haematocrit and reticulocytes."),
        dict(file_a="DS03 controls", file_b="S-CB050 controls 201-215",
             shared_dogs=f"{summ['controls']['with_s050_candidate']} of {summ['controls']['n_complete']}", certainty="probable (file level)",
             found_by="SV-07", consequence=f"Twins at {cc['ratio_to_baseline']} times chance, in CON-number order."),
        dict(file_a="DS07", file_b="DS04", shared_dogs="unknown: 7 shared case numbers", certainty="unverified", found_by="data.md; tested here",
             consequence=f"6 of 7 DS04 numbers below 98 are DS07 'complicated' (p = {hyp['1-97']['p_ge_observed_complicated']:.1e}), but DS07 has no values to check and 2 numbers contradict the CB112 summaries."),
        dict(file_a="DS06 names", file_b="DS02 dog numbers", shared_dogs="5 Beagles (known); name-to-number map", certainty="high_3 = dog 6 probable; the rest unverified",
             found_by="SV-07", consequence="Transcript kinetics did not recover high_3 = dog 6 (positive control failed), so the other names stay unassigned."),
    ]

    # ------------------------------------------------------------------ independent_source proposal (a proposal only)
    proposal = [
        dict(dataset="DS03 natural cohorts 1 and 2, DS03 controls", current="SRC-E", proposed="SRC-A",
             reason="The same dogs as S-CB050 (file-level evidence; one dog confirmed by values)."),
        dict(dataset="DS03 experimental dogs", current="SRC-E", proposed="SRC-B", reason="The DS02 Beagles (SV-G1, confirmed by values)."),
        dict(dataset="DS03 IMHA dogs", current="SRC-E", proposed="SRC-E", reason="No overlap tested or found."),
        dict(dataset="DS04 / S-CB147", current="SRC-G", proposed="SRC-G, with an overlap note to SRC-A",
             reason="3 of 10 fatal dogs are S-CB050 dogs; 7 are not in S-CB050. Count the 3 once in any pooled count."),
        dict(dataset="DS07", current="SRC-C", proposed="SRC-C (unchanged until the authors answer)",
             reason="Overlap with DS04 numbers is unlikely by chance but unverified; CB112 summaries do not fit S-CB050 controls or the S-CB050 2014 cohort as a whole."),
    ]

    interpretation = {"sections": [
        {"heading": "Question", "paragraphs": [
            "Which dogs appear in more than one of the programme's files? Files that share dogs are not independent evidence, and a link "
            "to a file with death, age and sex could give a label to a file that lacks one (DS07)."]},
        {"heading": "What was done", "paragraphs": [
            "Raw files only, standard-library Python. (1) DS04 haematology rows were joined to case numbers by the row order of the five "
            "Stats Tables sheets and checked against S-CB050 by WBC, segmented and band neutrophils within rounding, and by icterus wording "
            "against bilirubin. (2) Every DS04 row was searched in all 161 S-CB050 rows. (3) DS03 natural and control dogs were compared with "
            "S-CB050 on age, weight and sex, with DS05 (Eastern Cape, 2021) as a chance baseline; two checks were added after the first run: "
            "study-number order and a DS03-DS04 value check on haematocrit and reticulocytes. (4) DS06 names were mapped to DS02 dogs by "
            "sampling pattern and by marker-gene kinetics, with a positive control. (5) DS07 numbers were compared with DS04 numbers and with "
            "the CB112 group summaries."]},
        {"heading": "Result", "paragraphs": [
            f"{counts['confirmed by values']} links are confirmed by values, {counts['probable']} are probable and {counts['unverified']} unverified "
            f"(out/linkage.csv). DS04 cases 50, 54 and 59 are S-CB050 cases {m['50']}, {m['54']} and {m['59']} (three equal counts, equal "
            f"signalment, all died); the row-order join that puts them there has a chance probability of {s1['p_three_matches_on_join_rows']:.4f}. "
            "The other seven fatal DS04 dogs match no S-CB050 row.",
            f"New: DS03's natural dogs are S-CB050 dogs. {summ['cohort 1']['with_s050_candidate']} of {summ['cohort 1']['n_complete']} cohort-1 dogs, "
            f"{summ['cohort 2']['with_s050_candidate']} of {summ['cohort 2']['n_complete']} cohort-2 dogs and {summ['controls']['with_s050_candidate']} "
            f"of {summ['controls']['n_complete']} controls have an age-weight-sex twin in the matching S-CB050 block, {c1['ratio_to_baseline']}, "
            f"{c2['ratio_to_baseline']} and {cc['ratio_to_baseline']} times the rate against DS05; every unique pair keeps the study-number order "
            "(Kendall tau 1.0 in all three blocks), and DS03 BLSC29 has the haematocrit (0.07) and reticulocyte % of DS04 case 54 = S-CB050 127.",
            f"DS07: 6 of the 7 DS04 numbers below 98 are DS07 'complicated' (expected about {hyp['1-97']['expected_in_complicated']}, "
            f"p = {hyp['1-97']['p_ge_observed_complicated']:.1e} over 1-97), so the numbering is probably shared. But DS04 case 20 is 144 months "
            "old (CB112 range 6-120) and case 88 was dead on arrival yet is DS07 'uncomplicated'. DS07 death cannot be taken from DS04 yet.",
            f"DS06: high_3 = DS02 dog 6 by sampling pattern. The marker-gene check did not recover that link (best assignment: {pc['assignment']}), "
            "so the other DS06 names stay unverified."]},
        {"heading": "What this does not show", "paragraphs": [
            "Age, weight and sex identify a dog weakly; the DS03-S-CB050 dog-level pairs stay unverified even though the file-level overlap is "
            "clear. No link was made through DS07, which has no clinical values. Absence of a match does not prove different dogs: S-CB050 may "
            "have excluded dogs that another file kept. The independent_source changes are a proposal; /core/datasets.jsonl was not edited. "
            "'Died' in the Onderstepoort files includes euthanasia for poor prognosis."]},
    ]}

    hdr_ds04 = typed(rd("ds04_vs_scb050.csv"))
    primary = {
        "link_counts": counts, "n_links": len(links),
        "file_pairs": file_pairs,
        "headline": [
            {"label": "DS04 dogs confirmed in S-CB050", "value": len(m), "of": 10},
            {"label": "DS03 natural dogs with an S-CB050 twin", "value": summ["cohort 1"]["with_s050_candidate"] + summ["cohort 2"]["with_s050_candidate"],
             "of": summ["cohort 1"]["n_complete"] + summ["cohort 2"]["n_complete"]},
            {"label": "DS04 numbers below 98 in the DS07 complicated list", "value": len(s5["in_complicated"]), "of": len(s5["ds04_numbers_below_98"])},
            {"label": "Independent sources proposed for merging", "value": 1, "of": None, "note": "SRC-E natural dogs into SRC-A"},
        ],
    }
    ds03_payload = {"rates": s3["rates"], "summary": s3["summary"], "order_check": s3["order_check"],
                    "unique_pairs": typed(rd("ds03_unique_pairs.csv")),
                    "baseline_rate_per_1000": s3["baseline_rate_per_1000"],
                    "value_check": s3["ds04_vs_ds03"],
                    "note": "Candidate = same sex, same age in months, weight within 0.1 kg. Baseline: DS05 (Eastern Cape, 2021), which cannot share dogs."}
    ds04_payload = {"join": [{"row": int(k), "case": v} for k, v in s1["join"].items()], "rows": hdr_ds04,
                    "icterus": typed(rd("ds04_icterus_join.csv")),
                    "p_three_matches": s1["p_three_matches_on_join_rows"], "icterus_agree": s1["icterus_agree"], "icterus_n": s1["icterus_n"],
                    "icterus_p_fixed": s1["icterus_p_orders_with_matches_fixed"], "orders_agree": s1["orders_agree"]}
    ds06_payload = {"scores": typed(rd("ds06_assignment_scores.csv")), "positive_control_pass": s4["positive_control_pass"],
                    "markers_present": s4["markers_present"], "markers_absent": s4["markers_absent"], "series": typed(rd("ds06_series.csv"))}
    ds07_payload = {"hypergeometric": s5["hypergeometric"], "consistency": s5["consistency"], "in_complicated": s5["in_complicated"],
                    "in_uncomplicated": s5["in_uncomplicated"], "summary_level": s5["summary_level"]}

    run_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    load = {
        "experiment": {
            "code": CODE,
            "name": "Linkage audit: which dogs appear in more than one file (DS02-DS07, S-CB050, S-CB517)",
            "description": "Which dogs are shared between the programme's files, and can a file without outcomes (DS07) be joined to one with death, age and sex? "
                           "Descriptive: value matches within rounding where files share variables, chance-calibrated signalment matching where they do not.",
            "method": "linkage_audit",
            "dataset": None,
            "parameters": {"package": "SV-07", "role": "descriptive",
                           "datasets": ["DS02", "DS03", "DS04", "DS05", "DS06", "DS07", "S-CB050", "S-CB147", "S-CB517"],
                           "independent_sources": ["SRC-A", "SRC-B", "SRC-C", "SRC-E", "SRC-F", "SRC-G"],
                           "spec_sha256": spec_sha, "seed": None, "tolerance": "max(0.011, 0.5%) for two-decimal counts; Hct 0.005, retic 0.05",
                           "inputs": [f"{k} sha256 {v[:12]}" for k, v in res["inputs"].items()]},
            "script": "/experiments/SV-07/scripts/analyse.py",
            "script_version": script_ver,
            "run_utc": run_utc,
            "n_subjects": None,
            "n_variables": 6,
            "n_tests": 0,
            "summary": (f"{counts['confirmed by values']} links confirmed by values, {counts['probable']} probable, {counts['unverified']} unverified. "
                        f"DS04 cases 50/54/59 = S-CB050 {m['50']}/{m['54']}/{m['59']}; DS03 natural dogs are S-CB050 dogs (twins {c1['ratio_to_baseline']}-"
                        f"{c2['ratio_to_baseline']} times chance, in study-number order); DS07-DS04 number link probable by chance (p {hyp['1-97']['p_ge_observed_complicated']:.0e}) "
                        "but unverified and partly contradicted. No statistical tests."),
        },
        "associations": [],
        "cluster_assignments": [],
        "results": [
            {"kind": "primary_result", "title": "Which files share dogs", "sort_order": 1, "payload": primary},
            {"kind": "ds04_join", "title": "DS04 haematology rows, case numbers and S-CB050 matches", "sort_order": 2, "payload": ds04_payload},
            {"kind": "ds03_signalment", "title": "DS03 against S-CB050 on age, weight and sex, with a DS05 chance baseline", "sort_order": 3, "payload": ds03_payload},
            {"kind": "ds07_numbering", "title": "DS07 sample numbers against DS04 case numbers", "sort_order": 4, "payload": ds07_payload},
            {"kind": "ds06_mapping", "title": "DS06 sample names against DS02 dog numbers", "sort_order": 5, "payload": ds06_payload},
            {"kind": "source_proposal", "title": "Proposed independent_source changes (not applied)", "sort_order": 6, "payload": {"rows": proposal}},
            {"kind": "linkage_table", "title": "All links (out/linkage.csv)", "sort_order": 7, "payload": {"rows": links}},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interpretation},
        ],
    }
    if load["experiment"]["n_subjects"] is None:
        # distinct dogs that appear in at least one link row with a concrete id (approximate: count of DS03+DS04+DS06 dogs examined)
        load["experiment"]["n_subjects"] = 14 + summ["cohort 1"]["n_complete"] + summ["cohort 2"]["n_complete"] + summ["controls"]["n_complete"] + 6
    (OUT / "db").mkdir(exist_ok=True)
    txt = json.dumps(load, indent=1, ensure_ascii=False, allow_nan=False)
    assert len(txt.encode()) < 1_000_000, len(txt.encode())
    (OUT / "db" / f"{CODE}.json").write_text(txt, encoding="utf-8")

    # ------------------------------------------------------------------ author query draft (not sent)
    q = f"""# Draft query to the data owners on case numbering (SV-07)

Status: DRAFT. Not sent. Sending it is a decision for the user. Address it to the corresponding authors of CB112, CB147, CB050 and CB145
(Onderstepoort and Zagreb groups); add the sender's name and affiliation only when the user decides to send.

---

Subject: Case numbering across your *Babesia rossi* datasets (Kuleš et al. 2023; Horrell et al. 2026; Celliers et al. 2020; Seejarim et al. 2023; Goddard et al. 2016 and 2026)

Dear colleagues,

We are reanalysing the public data that accompany several of your papers on *B. rossi* in dogs, and we want to avoid counting the
same dog twice. Matching the files gave the results below. Could you confirm or correct them?

1. **Liver study (Horrell et al. 2026, doi:10.3389/fvets.2026.1765994) and the neutrophil study (Celliers et al. 2020,
   doi:10.3389/fvets.2020.00072).** Fatal cases 50, 54 and 59 of the liver study have the same WBC, segmented and band neutrophil
   counts, age, weight and sex as cases {m['50']}, {m['54']} and {m['59']} of the 2020 supplementary table (the 2014 cohort). Are these the same
   dogs? What register do the liver-study case numbers come from? Are any of the other seven fatal cases (20, 61, 88, 91, 106, 110, 117) in
   another of your published cohorts?
2. **Proteome study (Kuleš et al. 2023, doi:10.1038/s41598-023-37312-9).** The sample list uses numbers 7 to 91 for infected dogs. Six of
   the seven liver-study case numbers below 98 (20, 50, 54, 59, 61, 91) are in its "complicated" list, and 88 is in its "uncomplicated" list.
   Do the proteome sample numbers and the liver-study case numbers come from the same case register? If they do: liver case 20 is recorded
   as 12 years old (the proteome paper gives an age range of 6 to 120 months), and liver case 88 was dead on arrival (death within 24 h
   is a "complicated" criterion). Which records are correct?
3. **Outcome for the proteome dogs.** If the numbering is shared, could you give, for each proteome sample number, the case number in your
   clinical register and whether the dog survived to discharge (with euthanasia shown separately)? This would let the proteome be analysed
   against death rather than against the composite "complicated" label.
4. **Reticulocyte study (Seejarim et al. 2023, doi:10.1111/vcp.13228).** Its natural-infection dogs match the 2020 table by age, weight
   and sex far above chance and in the same order (BC numbers to cases 1–97, BLSC numbers to cases 101–144, CON numbers to controls
   201–215). Are these the same dogs? The paper dates the first cohort October 2013 to July 2015; the 2020 paper dates the matching cohort
   October 2011 to April 2013. Which is correct?
5. **Thromboinflammation study (Goddard et al. 2026, doi:10.3389/fvets.2026.1712262).** It has 97 infected and 15 control dogs from October 2011 to
   April 2013 (protocol V055-11), as do cases 1–97 and controls 201–215 of the 2020 table and the 2016 cytokine paper (Goddard et al. 2016, doi:10.1371/journal.pone.0150113). Are these the same
   dogs, with the same case numbers?

Thank you for your help.

---

Facts behind each question: `/experiments/SV-07/report.md` and `out/linkage.csv`.
"""
    (OUT / "author_query_draft.md").write_text(q, encoding="utf-8")
    print("wrote", OUT / "db" / f"{CODE}.json", len(txt.encode()), "bytes")


if __name__ == "__main__":
    main()
