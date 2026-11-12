"""Build the console-loader file out/db/SV-08-01-transcriptome-signatures.json from out/ (way B).

Every number in the payloads and in the interpretation text comes from out/*.csv and out/results.json.
"""
import csv, hashlib, json, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "out"
CODE = "SV-08-01-transcriptome-signatures"
LABEL = {"neutrophil_granule": "Neutrophil granule", "type1_interferon": "Type 1 interferon", "erythroid_control": "Erythroid (composition control)"}
DOG_LABEL = {"low_1": "low_1 (low dose)", "low_2": "low_2 (low dose)", "high_1": "high_1 (high dose)",
             "high_2": "high_2 (high dose)", "high_3": "high_3 (high dose, died day 4)"}


def rd(name):
    with open(OUT / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def fl(v):
    return None if v in ("", None) else float(v)


def it(v):
    return None if v in ("", None) else int(float(v))


def sgn(v, d=3):
    return "–" if v is None else f"{'+' if v >= 0 else ''}{v:.{d}f}"


def main():
    res = json.loads((OUT / "results.json").read_text(encoding="utf-8"))
    scores = rd("set_scores.csv")
    prim = rd("primary_deltas.csv")
    signs = {r["set"]: r for r in rd("sign_counts.csv")}
    timing = rd("timing.csv")
    checks = rd("construct_checks.csv")
    gmap = rd("gene_map.csv")
    unm = rd("unmapped_genes.csv")
    libs = rd("library_sizes.csv")
    verdict = res["verdict"]
    sizes = res["set_sizes"]

    def sc(st):
        s = signs[st]
        return {"set": st, "label": LABEL[st], "in_family": s["in_family"] == "True", "n_dogs": int(s["n_dogs"]),
                "n_genes": sizes[st]["mapped"], "n_genes_fixed": sizes[st]["fixed"],
                "positive": int(s["positive"]), "sign_test_p": fl(s["sign_test_p_two_sided"]),
                "beyond_rise": int(s["beyond_background_rise"]), "beyond_fall": int(s["beyond_background_fall"]),
                "median_delta": fl(s["median_delta"]),
                "s1_positive": int(s["s1_positive"]), "s1_beyond_rise": int(s["s1_beyond_rise"]),
                "s2_positive": int(s["s2_positive"]), "s3_positive": int(s["s3_positive"]),
                "s4_positive_all_loo": int(s["s4_positive_all_loo"]),
                "verdict": verdict.get(st)}

    sets = ["neutrophil_granule", "type1_interferon", "erythroid_control"]
    sc_all = [sc(s) for s in sets]
    nq, ifn, ery = sc_all

    def appears_txt(v):
        return "appears" if v["signature_appears"] else "does not appear (against the hypothesis)"

    primary_payload = {
        "label": "Within-dog change from day 0 to the last pre-treatment sample (DS06, 5 Beagles)",
        "n_dogs": 5, "n_low": 2, "n_high": 3, "n_samples": res["n_samples"], "n_genes_matrix": res["n_genes"],
        "independent_sources": 1, "sources": ["SRC-B (DS06 RNA-seq; DS02 clinical data of the same Beagles)"],
        "sets": sc_all,
        "dogs": [{"dog": p["dog"], "label": DOG_LABEL[p["dog"]], "dose": p["dose"], "set": p["set"],
                  "last_pre_day": int(p["last_pre_day"]), "score_d0": fl(p["score_d0"]), "score_last": fl(p["score_last"]),
                  "delta": fl(p["delta"]), "bg_percentile": fl(p["bg_percentile"]), "bg_lo95": fl(p["bg_delta_lo95"]),
                  "bg_hi95": fl(p["bg_delta_hi95"]), "beyond": p["beyond_background"]} for p in prim],
        "note": "Score = mean within-sample rank percentile of the set genes (0 = lowest-expressed gene, 1 = highest). "
                "Background = 2,000 random gene sets matched on each dog's day-0 expression decile. Sign test: the smallest "
                "attainable two-sided p with 5 dogs is 0.0625. Exploratory; one source; dose aliased with dog.",
    }

    traj = []
    for st in sets:
        dogs = []
        for dog in ["low_1", "low_2", "high_1", "high_2", "high_3"]:
            pts = [{"day": it(r["day"]), "score": fl(r["score"]), "delta": fl(r["delta_vs_d0"]),
                    "bg_percentile": fl(r["bg_percentile"]), "post_treatment": r["post_treatment"] == "True",
                    "parasitaemia_working": fl(r["parasitaemia_working"]), "parasitaemia_alt": fl(r["parasitaemia_alt"]),
                    "library_size": it(r["library_size"])}
                   for r in scores if r["set"] == st and r["dog"] == dog]
            dogs.append({"dog": dog, "label": DOG_LABEL[dog], "dose": dog.split("_")[0], "points": sorted(pts, key=lambda p: p["day"])})
        ref = next((fl(r["score"]) for r in scores if r["set"] == st and r["dog"] == "low_0"), None)
        traj.append({"set": st, "label": LABEL[st], "n_genes": sizes[st]["mapped"], "low_0_d0": ref, "dogs": dogs})

    timing_rows = [{"mapping": t["mapping"], "dog": t["dog"], "dose": t["dose"], "ds02_dog": t["ds02_dog"],
                    "ds02_original_id": t["ds02_original_id"] or None, "set": t["set"], "set_label": LABEL[t["set"]],
                    "first_risen_day": it(t["first_risen_day"]), "deterioration_day": fl(t["deterioration_day"]),
                    "habitus_baseline": fl(t["habitus_baseline"]),
                    "risen_before_deterioration": t["risen_before_deterioration"] == "True"} for t in timing]
    check_rows = [{"mapping": c["mapping"], "set": c["set"], "set_label": LABEL[c["set"]], "variable": c["label"],
                   "dog": c["dog"], "n_points": it(c["n_points"]), "rho": fl(c["spearman_rho"])} for c in checks]
    sens_rows = [{"dog": p["dog"], "label": DOG_LABEL[p["dog"]], "set": p["set"], "set_label": LABEL[p["set"]],
                  "delta": fl(p["delta"]), "s1_delta_d3": fl(p["s1_delta_d3"]), "s1_bg_percentile": fl(p["s1_bg_percentile"]),
                  "s2_delta_log2_uq": fl(p["s2_delta_log2_uq"]), "s3_delta": fl(p["s3_delta_no_retic_genes"]),
                  "s4_min": fl(p["s4_loo_min"]), "s4_max": fl(p["s4_loo_max"])} for p in prim]
    gene_rows = [{"set": g["set"], "set_label": LABEL[g["set"]], "gene": g["gene"], "mapped": g["mapped"] == "True",
                  "row_id": g["row_id"] or None, "how": g["how"] or None,
                  "reason": next((u["reason"] for u in unm if u["gene"] == g["gene"]), None)} for g in gmap]
    lib_rows = [{"sample": l["sample"], "dog": l["dog"], "day": it(l["day"]), "library_size": it(l["library_size"]),
                 "alas2_percentile": fl(l["alas2_percentile"])} for l in libs]

    # ---------- interpretation, numbers from the variables above ----------
    def dline(st):
        return "; ".join(f"{p['dog']} {sgn(fl(p['delta']))} (background percentile {fl(p['bg_percentile']):.2f})"
                         for p in prim if p["set"] == st)

    tw = [t for t in timing_rows if t["mapping"] == "working"]

    def tl(st):
        return "; ".join(f"{t['dog']}: risen {('day ' + str(t['first_risen_day'])) if t['first_risen_day'] is not None else 'never'}, "
                         f"habitus fell {('day ' + format(t['deterioration_day'], 'g')) if t['deterioration_day'] is not None else 'never'}"
                         for t in tw if t["set"] == st)

    def peak_day(st, dog):
        pts = [(fl(r["delta_vs_d0"]), it(r["day"])) for r in scores
               if r["set"] == st and r["dog"] == dog and r["post_treatment"] == "False" and it(r["day"]) > 0]
        return max(pts)[1] if pts else None

    def peaks(st):
        return "; ".join(f"{d} day {peak_day(st, d)}" for d in ["low_1", "low_2", "high_1", "high_2", "high_3"])

    unmapped_txt = ", ".join(f"{u['gene']}" for u in unm)
    med = lambda st, m: next((c["rho"] for c in check_rows if c["set"] == st and c["dog"] == "median of dogs" and c["mapping"] == m), None)
    interp = {"sections": [
        {"heading": "Question", "paragraphs": [
            "Do the whole-blood signatures of severe human malaria (neutrophil granule and type 1 interferon genes) rise in the five "
            "B. rossi Beagles between day 0 and the last sample before treatment, before clinical deterioration, and earlier at the high dose?"]},
        {"heading": "What was done", "paragraphs": [
            f"DS06 whole-blood RNA-seq ({res['n_genes']:,} genes, {res['n_samples']} samples; 5 dogs with a time course). Genes were ranked inside "
            f"each sample; a set score is the mean rank percentile of its genes. Mapped genes: neutrophil granule {nq['n_genes']} of {nq['n_genes_fixed']}, "
            f"type 1 interferon {ifn['n_genes']} of {ifn['n_genes_fixed']}, erythroid control {ery['n_genes']} of {ery['n_genes_fixed']}. "
            f"Not in the matrix: {unmapped_txt}.",
            "The primary result is the change per dog from day 0 to day 4 (day 3 for high_3, which died on day 4), compared with 2,000 random gene sets "
            "matched on day-0 expression, because the day 3 and day 4 libraries collapse and shift to reticulocyte transcripts. Timing used the DS02 "
            "habitus score; the DS06-to-DS02 dog mapping is probable only for high_3 and unverified for the others, so it was run under both "
            "possible mappings inside each dose group. Days 6 and 8 follow treatment and are shown only."]},
        {"heading": "Result", "paragraphs": [
            f"Type 1 interferon: higher than day 0 in {ifn['positive']} of 5 dogs (sign-test p {ifn['sign_test_p']:.3f}), beyond the composition "
            f"background in {ifn['beyond_rise']} of 5. Per dog: {dline('type1_interferon')}. The signature {appears_txt(verdict['type1_interferon'])}.",
            f"Neutrophil granule: higher in {nq['positive']} of 5 dogs (p {nq['sign_test_p']:.3f}), beyond background in {nq['beyond_rise']} of 5. "
            f"Per dog: {dline('neutrophil_granule')}. The signature {appears_txt(verdict['neutrophil_granule'])}.",
            f"Erythroid control: higher in {ery['positive']} of 5 dogs, beyond background in {ery['beyond_rise']} of 5 (the reticulocyte shift).",
            f"Timing (working mapping). Interferon: {tl('type1_interferon')}. Neutrophil granule: {tl('neutrophil_granule')}. "
            f"Risen before deterioration in at least one dog: interferon {'yes' if verdict['type1_interferon']['before_deterioration_working'] else 'no'} "
            f"(alternative mapping {'yes' if verdict['type1_interferon']['before_deterioration_alternative'] else 'no'}), neutrophil granule "
            f"{'yes' if verdict['neutrophil_granule']['before_deterioration_working'] else 'no'} (alternative "
            f"{'yes' if verdict['neutrophil_granule']['before_deterioration_alternative'] else 'no'}). Earlier at the high dose: interferon "
            f"{'yes' if verdict['type1_interferon']['earlier_at_high_dose'] else 'no'}, neutrophil granule {'yes' if verdict['neutrophil_granule']['earlier_at_high_dose'] else 'no'}.",
            f"Pre-treatment day of the highest score (D1, D3, D4): interferon {peaks('type1_interferon')}; neutrophil granule "
            f"{peaks('neutrophil_granule')}. The spec rule for 'earlier at the high dose' needs every high-dose dog to rise before both "
            f"low-dose dogs; it is not met.",
            f"Construct checks (median of per-dog Spearman rho over 3 or 4 pre-treatment points, working mapping): interferon score with plasma IP-10 "
            f"{sgn(med('type1_interferon', 'working'), 2)}, neutrophil-granule score with band neutrophils {sgn(med('neutrophil_granule', 'working'), 2)}, "
            f"erythroid score with reticulocyte % {sgn(med('erythroid_control', 'working'), 2)}."]},
        {"heading": "What this does not show", "paragraphs": [
            "Five dogs from one experiment (one source) show a pattern, not a rate: no sign count can reach p < 0.05. Dose is aliased with dog, and "
            "the dog mapping to the clinical data is unverified except for high_3. It does not show that these genes mark severe natural "
            "babesiosis, that they predict anything, or that the human malaria signatures transfer: several neutrophil granule genes "
            "(the promyelocyte genes) are not in the pre-filtered matrix. No genome-wide screen was run."]},
    ]}

    ifn_v = verdict["type1_interferon"]; nq_v = verdict["neutrophil_granule"]
    summary = (f"Type 1 interferon score rose from day 0 to the last pre-treatment sample in {ifn['positive']} of 5 Beagles "
               f"({ifn['beyond_rise']} beyond the composition background; sign-test p {ifn['sign_test_p']:.3f}); neutrophil granule in "
               f"{nq['positive']} of 5 ({nq['beyond_rise']} beyond background, p {nq['sign_test_p']:.3f}); n 5 dogs, 1 source, exploratory. "
               f"0 of 2 sign tests below 0.05 (minimum attainable 0.0625). 'Earlier at the high dose' not met "
               f"(interferon {'yes' if ifn_v['earlier_at_high_dose'] else 'no'}, neutrophil {'yes' if nq_v['earlier_at_high_dose'] else 'no'}).")

    script = HERE / "scripts" / "analyse.py"
    load = {
        "experiment": {
            "code": CODE,
            "name": "Human severe-malaria blood signatures (neutrophil granule, type 1 interferon) in the B. rossi Beagle transcriptome (DS06)",
            "description": "Do the whole-blood signatures of severe human malaria appear in the five experimentally infected Beagles before "
                           "clinical deterioration, and earlier at the high dose? Hypothesis: both set scores rise from day 0 to the last "
                           "pre-treatment sample beyond the library composition shift, first in the high-dose dogs.",
            "method": "transcriptome_signature",
            "dataset": None,
            "parameters": {"package": "SV-08", "role": "primary", "datasets": ["DS06", "DS02"], "independent_sources": ["SRC-B"],
                           "spec_sha256": res["spec_sha256"], "seed": res["seed"], "n_random_sets": res["n_random_sets"],
                           "score": "mean within-sample rank percentile", "gene_sets": {k: v for k, v in sizes.items()},
                           "mapping_working": res["mapping_working"], "mapping_alternative": res["mapping_alternative"],
                           "versions": res["versions"], "exploratory": True},
            "script": "/experiments/SV-08/scripts/analyse.py",
            "script_version": hashlib.sha256(script.read_bytes()).hexdigest()[:12],
            "run_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "n_subjects": 5, "n_variables": sum(v["mapped"] for v in sizes.values()), "n_tests": 2,
            "summary": summary,
        },
        "associations": [],
        "cluster_assignments": [],
        "results": [
            {"kind": "primary_result", "title": "Primary analysis: within-dog change per set", "sort_order": 1, "payload": primary_payload},
            {"kind": "score_trajectories", "title": "Set scores by day and parasitaemia, each dog", "sort_order": 2, "payload": {"sets": traj}},
            {"kind": "timing", "title": "First risen day against deterioration day", "sort_order": 3, "payload": {"rows": timing_rows, "verdict": verdict}},
            {"kind": "construct_checks", "title": "Construct checks against DS02 measures", "sort_order": 4, "payload": {"rows": check_rows}},
            {"kind": "sensitivity", "title": "Sensitivity checks", "sort_order": 5, "payload": {"rows": sens_rows}},
            {"kind": "gene_mapping", "title": "Gene mapping and unmapped genes", "sort_order": 6, "payload": {"rows": gene_rows}},
            {"kind": "library_sizes", "title": "Library size and ALAS2 rank per sample", "sort_order": 7, "payload": {"rows": lib_rows}},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp},
        ],
    }
    (OUT / "db").mkdir(exist_ok=True)
    (OUT / "db" / f"{CODE}.json").write_text(json.dumps(load, indent=1, allow_nan=False, ensure_ascii=False), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
