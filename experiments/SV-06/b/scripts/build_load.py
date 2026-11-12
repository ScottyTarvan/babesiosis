"""SV-06b: build the database load file out/db/SV-06-02-ds07-candidate-tests.json from out/results.json.

Also reads /core/data/raw/DS07/B_Proteins.txt (read-only) for the master-protein check table.
Usage (from /experiments/SV-06/b): env/py/Scripts/python.exe -I scripts/build_load.py
"""
import csv, hashlib, json, os
from datetime import datetime, timezone

ROOT = r"C:\Workspaces\Babesiosis"
PKG = os.path.join(ROOT, "experiments", "SV-06", "b")
OUT = os.path.join(PKG, "out")
RAW = os.path.join(ROOT, "core", "data", "raw", "DS07", "B_Proteins.txt")
CODE = "SV-06-02-ds07-candidate-tests"

# Named family proteins and the rows looked up for the master check (spec section 2).
MASTER_CHECK = [
    ("Haemoglobin beta", ["P60524"], "P60524"),
    ("Haemoglobin alpha", ["P60529"], "J9NXL3"),
    ("Haptoglobin", ["P19006", "G1K2D9"], "A0A5F4DB38"),
    ("Lactoferrin", ["F1PR54"], "F1PR54"),
    ("S100A8", ["C0LQL0", "J9P8S3"], "C0LQL0"),
    ("Histone H4", ["L7N0L3", "J9NRV0", "F2Z4N2"], "L7N0L3"),
    ("Alpha-2-antiplasmin", ["E2R4V3", "A0A5F4CB96"], "E2R4V3"),
    ("Protein C", ["Q28278", "J9NVK0", "A0A5F4CZ73"], "Q28278"),
    ("Antithrombin", ["E2RES2"], "E2RES2"),
    ("Complement factor H", ["A0A5F4BVG1", "E2RK21", "A0A5F4CHF6", "J9NTL7", "A0A5F4CLV4", "A0A5F4BYC6"], "A0A5F4BVG1"),
    ("CD14", ["A0A1S7J0A8"], "A0A1S7J0A8"),
]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def f2(v, d=2, sign=True):
    if v is None:
        return "–"
    return f"{v:+.{d}f}" if sign else f"{v:.{d}f}"


def ptxt(p):
    return "–" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def master_table():
    rows = list(csv.DictReader(open(RAW, encoding="utf-8", errors="replace"), delimiter="\t"))
    ab = [k for k in rows[0] if k.startswith("Abundances (Grouped)")]
    by = {r["Accession"]: r for r in rows}
    vec = lambda r: tuple(r[k].strip() for k in ab)
    out = []
    for name, accs, used in MASTER_CHECK:
        named = [by[a] for a in accs]
        masters = [r for r in named if r["Master"] == "IsMasterProtein"]
        u = by[used]
        identical = all(vec(r) == vec(u) for r in named)
        gn = lambda r: (r["Description"].split("GN=")[1].split(" ")[0] if "GN=" in r["Description"] else "")
        if masters:
            status = "master"
        elif gn(u) and gn(u) in {gn(r) for r in named}:
            status = "candidate only; group master has the same gene symbol"
        else:
            status = "fails: candidate only; group master has no stated identity"
        out.append({"candidate": name, "named_accessions": accs, "named_status": [r["Master"] for r in named],
                    "quantity_accession": used, "quantity_description": u["Description"].split(" OS=")[0], "quantity_gene": gn(u),
                    "coverage_pct": u["Coverage [%]"], "unique_peptides": int(u["# Unique Peptides"]), "psms": int(u["# PSMs"]),
                    "same_abundances_as_named": identical, "check": status,
                    "in_family": not status.startswith("fails")})
    return out


def main():
    res = json.load(open(os.path.join(OUT, "results.json"), encoding="utf-8"))
    cands = res["candidates"]
    fam = [c for c in cands if c["in_family"]]
    tested = [c for c in fam if c["tested"]]
    mech = [c for c in tested if c["role"] == "mechanism"]
    by = {c["key"]: c for c in cands}
    best = min(tested, key=lambda c: c["p_stratified"])
    best_mech = min(mech, key=lambda c: c["p_stratified"])
    n_q05 = len(res["family_hits_q05"])
    n_p05 = sum(1 for c in tested if c["p_stratified"] < 0.05)
    pcs = [by["ltf"], by["cd14"]]
    untested = [c for c in fam if not c["tested"]]
    low = [c for c in tested if c["coverage_rule"] == "low coverage"]
    mt = master_table()
    hba = by["hba"]
    verdict = "Supported" if res["mechanism_hits_q05"] else "Not shown"

    def cand_row(c):
        r = {k: c.get(k) for k in ["key", "protein", "accession", "mechanism", "role", "expected_direction", "coverage_rule",
                                   "n_comp", "n_unc", "n_ctrl", "plexes_observed", "tested", "median_comp", "median_unc", "median_ctrl",
                                   "delta", "delta_lo", "delta_hi", "hl_log2", "hl_lo", "hl_hi", "hl_sd_units", "p_stratified", "q_bh",
                                   "presence_fisher_p", "detectable_sd_a05", "detectable_sd_a005"]}
        return r

    headline = (f"None of the {len(fam)} family proteins differs at q < 0.05 between {res['n_comp']} complicated and "
                f"{res['n_unc']} uncomplicated dogs ({len(tested)} tested; {n_p05} with p < 0.05). The smallest p is "
                f"{best['protein'].lower()}: Cliff's delta {f2(best['delta'])} ({f2(best['delta_lo'])} to {f2(best['delta_hi'])}), "
                f"p {ptxt(best['p_stratified'])}, q {ptxt(best['q_bh'])}.") if not n_q05 else (
                f"{n_q05} of {len(fam)} family proteins differ at q < 0.05: {', '.join(res['family_hits_q05'])}.")
    caveats = ["One proteome, one source (SRC-C), no replication.",
               "The complicated label includes anaemia and laboratory thresholds: haemoglobin and haptoglobin partly restate it.",
               "No covariates (age, sex, treatment, time from onset, sample haemolysis) are in the files.",
               f"Detectable effect about {by['hbb']['detectable_sd_a05']} SD at alpha 0.05, about {by['hbb']['detectable_sd_a005']} SD after correction for {len(fam)} tests."]
    primary = {"label": "Complicated against uncomplicated B. rossi, plex-stratified permutation, BH over 10 proteins",
               "verdict": verdict, "statistic": "Cliff's delta (complicated vs uncomplicated) with 95% bootstrap interval",
               "dataset": "DS07", "independent_sources": 1, "sources": ["DS07 (SRC-C), B. rossi, archived serum, 11 TMT plexes"],
               "n_comp": res["n_comp"], "n_unc": res["n_unc"], "n_ctrl": res["n_ctrl"], "family_size": len(fam),
               "n_tested": len(tested), "n_q05": n_q05, "n_p05": n_p05,
               "positive_controls_consistent": res["positive_controls_consistent"],
               "positive_controls": [{"protein": c["protein"], "delta": c["delta"], "delta_lo": c["delta_lo"], "delta_hi": c["delta_hi"],
                                      "p": c["p_stratified"], "q": c["q_bh"]} for c in pcs],
               "best": cand_row(best), "best_mechanism": cand_row(best_mech),
               "headline": headline, "caveats": caveats}
    candidate_tests = {"rows": [cand_row(c) for c in fam],
                       "footnote": (f"DS07, SRC-C, B. rossi: {res['n_comp']} complicated vs {res['n_unc']} uncomplicated dogs; one species, one source. "
                                    f"Value: log2 ratio to the plex's pooled standard. p: labels permuted inside each plex ({res['n_perm']:,} permutations, "
                                    f"seed {res['seed']}); interval: {res['n_boot']:,} bootstrap resamples of dogs within each group. "
                                    f"q: Benjamini-Hochberg over {len(fam)} proteins (an untested protein counts in the family size). "
                                    "Lactoferrin and CD14 are positive controls (CB112 reported them higher in complicated dogs).")}
    secondary = {"rows": [cand_row(hba)],
                 "footnote": "Haemoglobin alpha fails the master-protein check: P60529 is a candidate only and its group master J9NXL3 "
                             "(LOC100855558, 'Uncharacterized protein') has no stated identity. Outside the family; no claim."}
    dog_values = {"proteins": [{"key": c["key"], "label": c["protein"], "in_family": c["in_family"],
                                "points": [{"dog_id": p["dog_id"], "plex": p["plex"], "group": p["group"], "value": p["value"]}
                                           for p in res["dog_values"] if p["protein"] == c["key"]]} for c in cands],
                  "footnote": "Each point is one dog (log2 ratio to the plex standard). A missing value is missing for the whole plex. "
                              "Controls are shown for context and are not in the primary test."}
    sens_rows = []
    for c in cands:
        if not c["tested"]:
            sens_rows.append({"key": c["key"], "protein": c["protein"], "tested": False})
            continue
        sens_rows.append({"key": c["key"], "protein": c["protein"], "tested": True, "in_family": c["in_family"],
                          "delta": c["delta"], "p_stratified": c["p_stratified"],
                          "delta_unstratified": c["delta_unstratified"], "p_unstratified": c["p_unstratified"],
                          "lopo_min": c["lopo_min"], "lopo_max": c["lopo_max"], "lopo_sign_change": c["lopo_sign_change"],
                          "delta_infected_vs_control": c["delta_infected_vs_control"], "p_infected_vs_control": c["p_infected_vs_control"],
                          "rho_with_hbb": c["rho_with_hbb"], "n_rho": c["n_rho"]})
    sensitivity = {"rows": sens_rows,
                   "footnote": "S1 unstratified permutation; S2 leave-one-plex-out range of delta; S3 infected (32) vs controls (20), "
                               "plex-stratified, not corrected; S5 Spearman rho with haemoglobin beta among infected dogs. Not in the family."}
    plex = {"rows": [{"plex": k, **v} for k, v in res["plex_layout"].items()],
            "footnote": "TMT layout from sample_list.xlsx; channel 126 of each plex is the pooled standard. Labels are permuted inside each plex."}
    master = {"rows": mt, "footnote": "Checked in /core/data/raw/DS07/B_Proteins.txt before the outcome lock opened: column Master, "
                                      "and for candidate-only rows the master protein with identical grouped abundances (66 cells)."}

    sig_unstrat = [c["protein"] for c in tested if c["p_unstratified"] < 0.05]
    ivc = sorted([c for c in tested if c["p_infected_vs_control"] is not None and c["p_infected_vs_control"] < 0.05],
                 key=lambda c: c["p_infected_vs_control"])
    hb_track = [c for c in tested if c["key"] not in ("hbb",) and c["rho_with_hbb"] is not None and c["rho_with_hbb"] >= 0.4]
    interp = {"sections": [
        {"heading": "Question", "paragraphs": [
            "Do serum proteins of mechanisms linked to severity in human malaria, human babesiosis and sepsis (haemolysis and haem scavenging, "
            "neutrophil granule proteins and histones, fibrinolysis and anticoagulant consumption, complement regulation) differ between "
            "complicated and uncomplicated B. rossi babesiosis in the one public canine serum proteome (DS07)?",
            "Hypothesis: at least one mechanism candidate (not a positive control) differs at q < 0.05."]},
        {"heading": "What was done", "paragraphs": [
            f"The 11 proteins were fixed by the package file and mapped to accessions by part a. Before the outcome lock opened, each was checked "
            f"as a master protein in B_Proteins.txt. Haemoglobin alpha failed: its group master has no stated identity. It was dropped from the "
            f"family and is shown once as a secondary result. Haptoglobin is quantified through its group master A0A5F4DB38, which has the "
            f"haptoglobin gene symbol LOC479668. The family has {len(fam)} proteins.",
            f"For each protein: Cliff's delta, complicated against uncomplicated, on the log2 ratio to the plex standard; a permutation p "
            f"with labels permuted inside each of the 11 TMT plexes ({res['n_perm']:,} permutations, seed {res['seed']}); a 95% bootstrap "
            f"interval ({res['n_boot']:,} resamples of dogs); Benjamini-Hochberg over {len(fam)} proteins.",
            "Missing values in DS07 are missing for a whole plex. So a presence test only tests how the groups were placed in plexes. "
            "Proteins seen in less than 60% of a group were therefore tested on the observed dogs only and flagged as low coverage. "
            f"A protein with fewer than 3 observed dogs in a group was not tested: {', '.join(c['protein'] + ' (' + str(c['n_comp']) + ' complicated, ' + str(c['n_unc']) + ' uncomplicated, plexes ' + ', '.join(c['plexes_observed']) + ')' for c in untested) or 'none'}."]},
        {"heading": "Result", "paragraphs": [
            headline,
            f"Positive controls: lactoferrin delta {f2(by['ltf']['delta'])} ({f2(by['ltf']['delta_lo'])} to {f2(by['ltf']['delta_hi'])}) and "
            f"CD14 {f2(by['cd14']['delta'])} ({f2(by['cd14']['delta_lo'])} to {f2(by['cd14']['delta_hi'])}) are both higher in complicated "
            f"dogs, the direction CB112 reported for the same data. The value pipeline is "
            f"{'consistent' if res['positive_controls_consistent'] else 'NOT consistent'} with the source article. Neither control "
            f"passes the family correction (q {ptxt(by['ltf']['q_bh'])} and {ptxt(by['cd14']['q_bh'])}).",
            f"Mechanism candidates: haemoglobin beta is higher in complicated dogs (delta {f2(by['hbb']['delta'])}, {f2(by['hbb']['delta_lo'])} to "
            f"{f2(by['hbb']['delta_hi'])}; Hodges-Lehmann shift {f2(by['hbb']['hl_log2'])} log2 units; p {ptxt(by['hbb']['p_stratified'])}, "
            f"q {ptxt(by['hbb']['q_bh'])}). Its interval excludes zero but it does not pass the correction, and it partly restates the label. "
            f"S100A8 points the same way (delta {f2(by['s100a8']['delta'])}, {f2(by['s100a8']['delta_lo'])} to {f2(by['s100a8']['delta_hi'])}, "
            f"n {by['s100a8']['n_comp']} vs {by['s100a8']['n_unc']}). Haptoglobin {f2(by['hp']['delta'])}, alpha-2-antiplasmin "
            f"{f2(by['serpinf2']['delta'])}, protein C {f2(by['proc']['delta'])} (low coverage, n {by['proc']['n_comp']} vs {by['proc']['n_unc']}), "
            f"antithrombin {f2(by['serpinc1']['delta'])} and factor H {f2(by['cfh']['delta'])}: all intervals include zero. "
            f"Histone H4 could not be tested.",
            f"Checks: leave-one-plex-out never changes the sign of the haemoglobin beta, lactoferrin, CD14 or S100A8 deltas. The unstratified "
            f"test gives p < 0.05 for {', '.join(sig_unstrat) if sig_unstrat else 'no protein'}. Against controls, "
            f"{', '.join(c['protein'] + ' (' + f2(c['delta_infected_vs_control']) + ')' for c in ivc) if ivc else 'no protein'} differ at p < 0.05. "
            f"Of these, {', '.join(c['protein'] for c in ivc if c['p_stratified'] >= 0.05) or 'none'} do not differ by complicated status (p >= 0.05): "
            f"they move with infection more than with complicated disease. "
            f"Among infected dogs, {', '.join(c['protein'] + ' (rho ' + f2(c['rho_with_hbb']) + ')' for c in hb_track)} rise with haemoglobin beta."]},
        {"heading": "What this does not show", "paragraphs": [
            f"A null here is 'not shown', not 'absent': with {res['n_comp']} against {res['n_unc']} dogs the test detects about "
            f"{by['hbb']['detectable_sd_a05']} SD at alpha 0.05 and about {by['hbb']['detectable_sd_a005']} SD after correction.",
            "DS07 is one source with no replication. It has no covariates (age, sex, treatment, time from onset, sample haemolysis index), "
            "and its label is defined partly by haematocrit, urea, creatinine, bilirubin, glucose and lactate. A haemoglobin difference may "
            "come from in-vivo haemolysis, anaemia severity or haemolysis of the stored sample, and these cannot be told apart.",
            "Serum proteomics measures total protein, not activity. Alpha-2-antiplasmin and protein C amounts do not test fibrinolytic "
            "shutdown or protein C activation. Haptoglobin was measured as total haptoglobin group abundance, not as free haptoglobin. "
            "This is not a screen of the proteome, and no protein outside the fixed family was looked at."]},
    ]}

    run_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = (f"{headline} Positive controls lactoferrin and CD14 are higher in complicated dogs, as CB112 reported. "
               f"{len(tested)} tests, {n_q05} passed at q < 0.05.")
    load = {
        "experiment": {
            "code": CODE,
            "name": "Human severity-mechanism proteins in the B. rossi serum proteome: complicated against uncomplicated (DS07)",
            "description": ("Do serum proteins of mechanisms linked to severity in human disease (haemolysis and haem scavenging, neutrophil "
                            "granule proteins, fibrinolysis and anticoagulants, complement regulation) differ between complicated and "
                            "uncomplicated B. rossi babesiosis in DS07? Hypothesis: at least one mechanism candidate differs at q < 0.05."),
            "method": "proteome_candidate_test",
            "dataset": None,
            "parameters": {"package": "SV-06", "part": "b", "role": "primary", "datasets": ["DS07"], "independent_sources": ["SRC-C"],
                           "species": "B. rossi", "spec_sha256": res["spec_sha256"], "seed": res["seed"], "n_permutations": res["n_perm"],
                           "n_bootstrap": res["n_boot"], "family": [c["accession"] for c in fam], "family_size": len(fam),
                           "fdr": "Benjamini-Hochberg", "permutation": "labels inside each TMT plex",
                           "inputs_sha256": res["inputs"], "numpy": res["numpy"],
                           "handover": "/experiments/SV-06/a/out/candidates_for_partb.json"},
            "script": "/experiments/SV-06/b/scripts/analyse.py",
            "script_version": res["script_sha256"][:12],
            "run_utc": run_utc,
            "n_subjects": res["n_comp"] + res["n_unc"] + res["n_ctrl"],
            "n_variables": len(cands),
            "n_tests": len(tested),
            "summary": summary,
        },
        "associations": [], "cluster_assignments": [],
        "results": [
            {"kind": "primary_result", "title": "Primary result", "sort_order": 1, "payload": primary},
            {"kind": "candidate_tests", "title": "Family tests: complicated against uncomplicated", "sort_order": 2, "payload": candidate_tests},
            {"kind": "dog_values", "title": "Values by dog", "sort_order": 3, "payload": dog_values},
            {"kind": "sensitivity", "title": "Stability and sensitivity checks", "sort_order": 4, "payload": sensitivity},
            {"kind": "secondary", "title": "Secondary: haemoglobin alpha (outside the family)", "sort_order": 5, "payload": secondary},
            {"kind": "master_check", "title": "Master-protein check of the fixed family", "sort_order": 6, "payload": master},
            {"kind": "plex_layout", "title": "TMT plex layout", "sort_order": 7, "payload": plex},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp},
        ],
    }
    os.makedirs(os.path.join(OUT, "db"), exist_ok=True)
    s = json.dumps(load, ensure_ascii=False, allow_nan=False, indent=1)
    open(os.path.join(OUT, "db", f"{CODE}.json"), "w", encoding="utf-8").write(s)
    with open(os.path.join(OUT, "master_check.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(mt[0].keys())); w.writeheader()
        for r in mt:
            w.writerow({k: (";".join(v) if isinstance(v, list) else v) for k, v in r.items()})
    print("load file bytes", len(s)); print(summary)
    for r in mt:
        print(r["candidate"], r["quantity_accession"], r["check"], r["same_abundances_as_named"])


if __name__ == "__main__":
    main()
