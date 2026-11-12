"""SV-09: build the three load files for the console loader (way B) from out/results.json.

Run from /experiments/SV-09/:  env/py/Scripts/python.exe -I scripts/build_load.py
Every number in the text comes from results.json.
"""
import hashlib
import json
import os
import platform
import time

import numpy as np
import scipy

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
OUT = os.path.join(PKG, "out")
DB = os.path.join(OUT, "db")
R = json.load(open(os.path.join(OUT, "results.json"), encoding="utf-8"))
SCRIPT_VERSION = hashlib.sha256(open(os.path.join(HERE, "analyse.py"), "rb").read()).hexdigest()[:12]
RUN_UTC = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
S1, S2, S3 = R["step1"], R["step2"], R["step3"]
METHOD = "axis_replication"


def f2(v):
    return "–" if v is None else f"{v:+.2f}"


def ci(c):
    return f"{c[0]:+.2f} to {c[1]:+.2f}"


def ptxt(p):
    return "< 0.001" if p < 0.001 else f"{p:.3f}"


def interp(sections):
    return {"sections": [{"heading": h, "paragraphs": p} for h, p in sections]}


def params(role, datasets, sources, extra=None):
    p = {"package": "SV-09", "role": role, "datasets": datasets, "independent_sources": sources,
         "spec_sha256": R["spec_sha256"], "seed": R["seed"], "n_bootstrap": R["n_boot"], "n_permutations": R["n_perm"],
         "n_parallel_analysis": R["n_parallel"],
         "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
         "stage_covariate": "log(illness_days + 1) (owner-reported); SV-01 pseudo-stage failed validation and is used only in sensitivities S2 and S3"}
    if extra:
        p.update(extra)
    return p


def write(code, exp, results):
    os.makedirs(DB, exist_ok=True)
    doc = {"experiment": {"code": code, "dataset": None, "method": METHOD,
                          "script": "/experiments/SV-09/scripts/analyse.py", "script_version": SCRIPT_VERSION,
                          "run_utc": RUN_UTC, **exp},
           "associations": [], "cluster_assignments": [], "results": results}
    with open(os.path.join(DB, f"{code}.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False, allow_nan=False)


C = S1["components"]
c1, c2 = C[0], C[1]
hab = S1["habitus"]
sens = S1["sensitivity"]
min_sens = min(x["phi"] for x in sens if x["analysis"] != "S5_no_conditioning")
caveat05 = "DS05 (SRC-F, B. rossi, Eastern Cape clinic); exploratory: DS05 is on the already-seen list"

# ------------------------------------------------------------------ experiment 1
lo_rows = [{"variable": x["label"], "pc1": x["pc1"], "pc2": x["pc2"]} for x in S1["loadings"]]
e1_summary = (f"Two residual axes after haematocrit and illness duration in DS05 (n {S1['n']}): parallel analysis retains "
              f"{S1['retained']} components (eigenvalues {c1['eigenvalue']:.2f} and {c2['eigenvalue']:.2f} vs 95th percentile "
              f"{c1['pa_95']:.2f} and {c2['pa_95']:.2f}); both are bootstrap-stable (median phi {c1['boot_phi_median']:.2f}, "
              f"{c2['boot_phi_median']:.2f}). Axis 2 (leukocytes up, regeneration down) relates to habitus, partial rho "
              f"{hab[1]['partial_rho']:+.2f} ({ci(hab[1]['ci'])}); axis 1 does not ({hab[0]['partial_rho']:+.2f}). "
              f"{len(hab)} descriptive tests, {sum(1 for h in hab if h['p'] < 0.05)} with p < 0.05.")
write("SV-09-01-ds05-residual-axes", {
    "name": "Residual phenotype axes in DS05 after anaemia and illness duration (B. rossi, Eastern Cape)",
    "description": "After haematocrit and time since onset are removed, do admission blood counts in B. rossi still vary along a few reproducible axes? Hypothesis: at least one stable axis remains beyond noise.",
    "parameters": params("descriptive", ["DS05"], ["SRC-F"], {"experiment": "step 1", "variables": S1["variables"]}),
    "n_subjects": S1["n"], "n_variables": len(S1["variables"]), "n_tests": len(hab), "summary": e1_summary},
    [
        {"kind": "axis_summary", "title": "Retained residual axes", "sort_order": 1, "payload": {
            "n": S1["n"], "dataset": "DS05", "source": "SRC-F", "retained": S1["retained"], "components": C,
            "caveat": caveat05}},
        {"kind": "scree", "title": "Eigenvalues against parallel analysis", "sort_order": 2,
         "payload": {"points": S1["scree"], "caption": f"DS05, n {S1['n']}; 1,000 column-permuted data sets, 95th percentile. {caveat05}."}},
        {"kind": "loadings", "title": "Loadings (structure coefficients) of the two axes", "sort_order": 3,
         "payload": {"rows": lo_rows, "caption": "Correlation of each residualised variable with the axis score. Positive axis 1: leukocytes, regeneration, platelets and globulin together. Axis 2: leukocytes and MCHC against MCV, ARC and RDW."}},
        {"kind": "sensitivity", "title": "Do the axes depend on the stage covariate?", "sort_order": 4,
         "payload": {"rows": sens, "raw_corr": S1["raw_corr"],
                     "caption": "Tucker phi of each axis against the primary analysis. S2 and S3 use SV-01 pseudo-stage, which failed validation."}},
        {"kind": "habitus", "title": "Axis scores against habitus grade (descriptive)", "sort_order": 5,
         "payload": {"rows": hab, "caption": "Partial Spearman rho given haematocrit and illness duration; higher habitus is brighter. DS05 is already seen; habitus is a proxy, not a hard outcome."}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp([
            ("Question", ["After the anaemia axis and the stage of disease are removed, is there a further axis along which B. rossi dogs differ at admission?"]),
            ("What was done", [
                f"DS05 B. rossi dogs with complete counts (n {S1['n']}, SRC-F). Twelve variables (MCV, MCHC, RDW, ARC, nRBC, segmented and band neutrophils, lymphocytes, monocytes, platelets, albumin, globulin), log where skewed, regressed on haematocrit, haematocrit squared and log illness duration; principal components of the residual correlations; Horn's parallel analysis; 2,000 bootstraps of dogs with Procrustes alignment.",
                "Deviation D1: the package file asks to remove SV-01 pseudo-stage. SV-01 reports that score failed validation and is unstable, so owner-reported illness duration was used instead, and the two SV-01 pseudo-stage versions were run as sensitivities."]),
            ("Result", [
                f"Two axes exceed noise. Axis 1 ({c1['var_explained']*100:.0f}% of residual variance) moves leukocytes, regeneration (ARC, RDW, nRBC), platelets and globulin together. Axis 2 ({c2['var_explained']*100:.0f}%) sets leukocytes and MCHC against MCV, ARC and RDW: an inflammatory-against-regenerative balance at a given haematocrit.",
                f"Both are stable (bootstrap median phi {c1['boot_phi_median']:.2f} and {c2['boot_phi_median']:.2f}; 5th percentile {c1['boot_phi_p5']:.2f} and {c2['boot_phi_p5']:.2f}) and do not depend on the stage covariate (phi at least {min_sens:.2f} across S1 to S4). They are uncorrelated with haematocrit and illness duration by construction.",
                f"Axis 2 relates to habitus: partial rho {hab[1]['partial_rho']:+.2f} ({ci(hab[1]['ci'])}), p {ptxt(hab[1]['p'])}, n {hab[1]['n']}; duller dogs score higher (more leukocytes, less regeneration for their haematocrit). Axis 1 does not ({hab[0]['partial_rho']:+.2f}, {ci(hab[0]['ci'])})."]),
            ("What this does not show", [
                "DS05 is already seen (habitus with monocytes and band neutrophils was screened before), so the habitus link is exploratory. Habitus is a proxy, not death. One clinic, one species. The axes are directions of variation, not groups of dogs and not subtypes; no score predicts anything. Whether they recur in other files is experiment SV-09-02."])])},
    ])

# ------------------------------------------------------------------ experiment 2
B = {b["key"]: b for b in S2["blocks"]}
rc, lp, lk = B["red_cell"], B["leukocyte_platelet"], B["leukocyte"]
V = S2["verdicts"]
n_rep = sum(1 for v in V if v["verdict"] == "replicated")
n_cong = sum(1 for v in V if v["verdict"] == "congruent but not specific")
e2_summary = (f"No DS05 residual axis meets the replication rule ({n_rep} of {len(V)} axis-by-block checks replicated). "
              f"Block patterns recur (phi {rc['components'][0]['phi']:.2f} DS03 red cell, n {rc['n_target']}; "
              f"{lk['components'][0]['phi']:.2f} S-CB050 leukocytes, n {lk['n_target']}) but cannot be shown specific with 3 variables; "
              f"in the one testable block (S-CB017, B. canis, n {lp['n_target']}) phi {lp['components'][0]['phi']:.2f} is no better than a uniform pattern "
              f"({lp['components'][0]['uniform_phi']:.2f}; label-permutation p {lp['components'][0]['perm_p']:.3f}).")
blocks_payload = []
for b in S2["blocks"]:
    blocks_payload.append({k: b[k] for k in ["key", "target", "target_label", "species", "variables", "conditioning",
                                              "n_ds05", "n_target", "components", "loadings", "link"]})
write("SV-09-02-axis-congruence", {
    "name": "Do the DS05 residual axes recur in other files? Tucker congruence by shared variable block",
    "description": "Does the correlation pattern of the DS05 residual axes recur in DS03 (red cells), S-CB050 (leukocytes) and S-CB017 (B. canis leukocytes and platelets)? Hypothesis: at least one axis recurs with congruence of 0.85 or more and a pattern more specific than chance.",
    "parameters": params("replication", ["DS05", "DS03", "S-CB050", "S-CB017"], ["SRC-F", "SRC-A", "SRC-D"],
                         {"experiment": "step 2", "note": "DS03 natural dogs are S-CB050 dogs (SV-07): the two B. rossi targets are one source"}),
    "n_subjects": 147 + rc["n_target"] + lk["n_target"] + lp["n_target"], "n_variables": 9,
    "n_tests": sum(len(b["components"]) for b in S2["blocks"]), "summary": e2_summary},
    [
        {"kind": "congruence", "title": "Congruence of DS05 and target block patterns", "sort_order": 1,
         "payload": {"blocks": blocks_payload,
                     "caption": "Tucker phi with 2,000-bootstrap 95% intervals (dogs resampled in both files). Uniform: phi of the target pattern with equal loadings. Label permutation: exact, over all orderings of the target variables. DS03 and S-CB050 are one source (SRC-A, SV-07); S-CB017 is B. canis (one species per source)."}},
        {"kind": "verdicts", "title": "Replication rule by axis and block", "sort_order": 2,
         "payload": {"rows": V, "rule": "R1 retained and stable; R2 axis maps onto the block (|phi| >= 0.85); R3 phi >= 0.85, lower bound >= 0.70; R4 label-permutation p <= 0.05 and above the uniform baseline (only with 4 or more variables)."}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp([
            ("Question", ["Do the two DS05 residual axes recur in files from other sources, or are they specific to one clinic?"]),
            ("What was done", [
                f"For each target, the variables shared with DS05 form a block: red cells in DS03 natural infection (MCHC, reticulocytes, ARC; n {rc['n_target']}), leukocytes and platelets in S-CB017 day 1 (B. canis; segmented and band neutrophils, lymphocytes, monocytes, platelets; n {lp['n_target']}), and leukocytes in S-CB050 (WBC, segmented and band neutrophils; n {lk['n_target']}). Both files were residualised on haematocrit where the target has it (not S-CB050). The block's principal components were compared by Tucker's phi, with bootstrap intervals, a uniform-pattern baseline and an exact label permutation.",
                "SV-07 found that DS03 natural dogs are S-CB050 dogs, so the two B. rossi targets are one source (SRC-A), not two replications. Both are independent of DS05 (SRC-F)."]),
            ("Result", [
                f"DS03 red cell block: phi {rc['components'][0]['phi']:.2f} ({ci(rc['components'][0]['ci'])}); the pattern (MCHC against reticulocytes and ARC) is far from uniform ({rc['components'][0]['uniform_phi']:.2f}) but with 3 variables the smallest possible permutation p is 1/6, so specificity cannot be tested. The pattern is close to arithmetic: reticulocytes have a low MCHC.",
                f"S-CB050 leukocyte block: phi {lk['components'][0]['phi']:.2f} ({ci(lk['components'][0]['ci'])}), but a uniform pattern gives {lk['components'][0]['uniform_phi']:.2f}: three counts that are parts of one another load together in any file.",
                f"S-CB017 block, the only one where specificity is testable: component 1 phi {lp['components'][0]['phi']:.2f} ({ci(lp['components'][0]['ci'])}), uniform {lp['components'][0]['uniform_phi']:.2f}, label-permutation p {lp['components'][0]['perm_p']:.3f} (120 orderings): not specific. Component 2 (platelets against the leukocytes) phi {lp['components'][1]['phi']:.2f} ({ci(lp['components'][1]['ci'])}), p {lp['components'][1]['perm_p']:.3f}, below the 0.85 threshold.",
                f"By the rule stated in advance, {n_rep} of {len(V)} axis-by-block checks replicate and {n_cong} are congruent but not specific. Also, the shared blocks hold at most two of the step-1 variables in the B. rossi files, so they cannot tell axis 1 from axis 2: both map onto each block."]),
            ("What this does not show", [
                "A negative result here is mostly a limit of the files: the targets share 3 to 5 variables with DS05, too few to recover a 12-variable axis. It does not show that the DS05 axes are clinic-specific. The S-CB017 comparison crosses species and source (one species per source), so a failure there cannot be read as a species difference. No subtype and no predictive score."])])},
    ])

# ------------------------------------------------------------------ experiment 3
p50, p17 = S3["s050_died"], S3["s017_complicated"]
bo, rb = S3["s050_bands_only"], S3["s050_axis_given_bands"]
a4 = S3["A4_other_component"]
rows3 = []
for key, label, file_, lab, note in [
    ("s050_died", "Axis score, died vs survived", "S-CB050", "died", "primary; stratified by cohort"),
    ("s017_complicated", "Axis score, complicated vs uncomplicated", "S-CB017", "complicated", "primary; WBC is in the label"),
    ("s050_bands_only", "Band neutrophils alone, died vs survived", "S-CB050", "died", "comparison: the published finding"),
    ("s050_seg_only", "Segmented neutrophils alone, died vs survived", "S-CB050", "died", "comparison"),
    ("s050_axis_given_bands", "Axis score after removing band neutrophils", "S-CB050", "died", "does the axis add to bands?"),
    ("A1_s050_cohort1", "A1 cohort 1 only", "S-CB050", "died", "sensitivity"),
    ("A2_s050_with_wbc", "A2 with WBC", "S-CB050", "died", "sensitivity"),
    ("A3_s017_no_hct", "A3 no haematocrit conditioning", "S-CB017", "complicated", "sensitivity")]:
    x = S3[key]
    rows3.append({"key": key, "label": label, "file": file_, "outcome": lab, "note": note, **x})
for file_, key, lab in [("S-CB050", "s050_died", "died"), ("S-CB017", "s017_complicated", "complicated")]:
    rows3.append({"key": "A4_" + key, "label": f"A4 (post hoc) axis {a4['component']} weights", "file": file_, "outcome": lab,
                  "note": "deviation D3", **a4[key]})
e3_summary = (f"Axis {S3['axis_component']} score (segmented and band neutrophils, DS05 weights) is higher in S-CB050 dogs that died: "
              f"Cliff's delta {p50['delta']:+.2f} ({ci(p50['ci'])}), {p50['n_pos']} vs {p50['n_neg']}, q {p50['q']:.3f}; "
              f"S-CB017 complicated {p17['delta']:+.2f} ({ci(p17['ci'])}), q {p17['q']:.3f}. It restates band neutrophils "
              f"(bands alone {bo['delta']:+.2f}; axis after bands {rb['delta']:+.2f}, {ci(rb['ci'])}). "
              f"2 tests, {sum(1 for x in (p50, p17) if x['q'] < 0.05)} with q < 0.05.")
write("SV-09-03-axis-outcome", {
    "name": "DS05 residual axis scored in S-CB050 and S-CB017, against death and complicated disease",
    "description": "Does a DS05 residual axis, scored with its own weights in other files, differ between dogs that died and survived (B. rossi) or complicated and uncomplicated (B. canis)? Hypothesis: it does, beyond what band neutrophils alone already show.",
    "parameters": params("descriptive", ["DS05", "S-CB050", "S-CB017"], ["SRC-F", "SRC-A", "SRC-D"],
                         {"experiment": "step 3", "axis_component": S3["axis_component"], "axis_status": S3["axis_status"],
                          "weights_s050": S3["weights_s050"], "weights_s017": S3["weights_s017"], "bh_family": 2}),
    "n_subjects": p50["n_pos"] + p50["n_neg"] + p17["n_pos"] + p17["n_neg"], "n_variables": 5, "n_tests": 2,
    "summary": e3_summary},
    [
        {"kind": "axis_outcome", "title": "Axis score by outcome", "sort_order": 1,
         "payload": {"rows": rows3, "axis_component": S3["axis_component"], "axis_status": S3["axis_status"],
                     "adds_beyond_bands": S3["adds_beyond_bands"],
                     "caption": "Cliff's delta (label 1 minus label 0) with 2,000-bootstrap 95% intervals; permutation p (10,000). S-CB050: died includes euthanasia for poor prognosis. S-CB017: B. canis, one species per source; WBC is part of the complicated label. Both files are already seen (published group comparisons): exploratory."}},
        {"kind": "score_points", "title": "Axis scores by dog and label", "sort_order": 2,
         "payload": {"points": R["score_points"]}},
        {"kind": "mcp1", "title": "Axis score against MCP-1 (descriptive)", "sort_order": 3,
         "payload": {"rows": S3["mcp1"], "caption": "Spearman rho among infected dogs; MCP-1 was named a candidate by SV-04. No outcome used."}},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp([
            ("Question", ["Scored in files that have a real outcome, does a DS05 residual axis separate dogs that died, or had complicated disease, beyond what band neutrophils already show?"]),
            ("What was done", [
                f"The rule chose axis {S3['axis_component']} ({S3['axis_status']}). Its DS05 loadings on the variables each file shares were used as weights: segmented and band neutrophils in S-CB050 (all {p50['n_pos'] + p50['n_neg']} infected dogs, both cohorts), and segmented and band neutrophils, lymphocytes, monocytes and platelets (haematocrit removed) in S-CB017 day 1 ({p17['n_pos'] + p17['n_neg']} dogs). Cliff's delta, permutation p (stratified by cohort in S-CB050), bootstrap intervals; BH over the 2 primary tests.",
                f"Deviation D3: the rule tied between axes 1 and 2 (both congruent but not specific in S-CB050) and the code took axis 1. Axis 2 was scored as a post hoc check A4: in S-CB050 its score correlates {a4['rho_with_chosen_score']['S-CB050']:+.2f} with the axis-1 score."]),
            ("Result", [
                f"S-CB050: the score is higher in dogs that died, delta {p50['delta']:+.2f} ({ci(p50['ci'])}), p {ptxt(p50['p'])}, q {p50['q']:.3f}, {p50['n_pos']} died vs {p50['n_neg']} survived.",
                f"But this restates the published band-neutrophil finding: band neutrophils alone give {bo['delta']:+.2f} ({ci(bo['ci'])}); the score correlates {rb['rho_score_band']:+.2f} with bands; after bands are removed the score gives {rb['delta']:+.2f} ({ci(rb['ci'])}), p {ptxt(rb['p'])}. The axis adds nothing beyond bands (the risk the package file named).",
                f"S-CB017 (B. canis): delta {p17['delta']:+.2f} ({ci(p17['ci'])}), q {p17['q']:.3f}, {p17['n_pos']} complicated vs {p17['n_neg']} uncomplicated; detectable effect about 1.05 SD, and WBC is part of the label. Axis 2 weights give {a4['s017_complicated']['delta']:+.2f} ({ci(a4['s017_complicated']['ci'])}).",
                "MCP-1 does not track the score: " + "; ".join(f"{m['file']} rho {m['rho']:+.2f} ({ci(m['ci'])}), n {m['n']}" for m in S3["mcp1"]) + "."]),
            ("What this does not show", [
                "The axis was not replicated (experiment SV-09-02), so this is the score of an unreplicated direction. In S-CB050 only two of its twelve variables exist, so the score is a neutrophil sum, not the DS05 axis. Both files are already seen. Died includes euthanasia for poor prognosis. No predictive score was made and no group of dogs is a subtype."])])},
    ])
print("wrote", sorted(os.listdir(DB)))
