"""SV-META step 2: the result census.

Reads the out/ files of every package and writes out/census_raw.csv: one row per quantitative result or observation, with the
source file and line (CSV) or JSON pointer (JSON). Every number is copied from its file by this program; check_census.py reopens
each cited location and confirms the numbers are there.

Run from /experiments/SV-META/:  env/py/Scripts/python.exe -I scripts/census.py
"""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
EXP = PKG.parent
OUT = PKG / "out"

FIELDS = ["row_id", "experiment", "package", "result_type", "role", "measure", "comparison", "species", "dataset", "source", "n",
          "effect_type", "effect", "ci_low", "ci_high", "p", "q", "family", "family_size", "source_file", "source_line", "note"]

SRC = {  # dataset -> (independent source after SV-07, species)
    "S-CB050": ("SRC-A", "B. rossi"), "S-CB517": ("SRC-A", "B. rossi"), "DS03": ("SRC-A", "B. rossi"),
    "DS02": ("SRC-B", "B. rossi"), "DS06": ("SRC-B", "B. rossi"), "DS07": ("SRC-C", "B. rossi"),
    "S-CB017": ("SRC-D", "B. canis"), "DS05": ("SRC-F", "B. rossi"), "DS04": ("SRC-G", "B. rossi"),
    "S-CB516": ("SRC-O", "B. canis"),
}

rows = []


def add(**kw):
    r = {k: "" for k in FIELDS}
    r.update({k: ("" if v is None else v) for k, v in kw.items()})
    if r["dataset"] in SRC and not r["source"]:
        r["source"], sp = SRC[r["dataset"]]
        r["species"] = r["species"] or sp
    r["row_id"] = f"C{len(rows) + 1:04d}"
    rows.append(r)


def read_csv(rel):
    """Yield (line_label, row dict). line_label is 'a' or 'a-b' (physical lines, header = line 1)."""
    path = EXP / rel
    with path.open(encoding="utf-8", newline="") as fh:
        rd = csv.reader(fh)
        header = next(rd)
        prev = rd.line_num
        for cells in rd:
            start, end = prev + 1, rd.line_num
            prev = end
            yield (str(start) if start == end else f"{start}-{end}"), dict(zip(header, cells))


def jload(rel):
    return json.loads((EXP / rel).read_text(encoding="utf-8"))


def jget(obj, pointer):
    for part in pointer.strip("/").split("/"):
        obj = obj[int(part)] if isinstance(obj, list) else obj[part]
    return obj


def num(x):
    return "" if x is None else str(x)


# ---------------------------------------------------------------- SV-01
for sub, role_default, code in (("SV-01/out/tests.csv", "primary", "spec construction"),
                                ("SV-01/out/time_anchored/tests.csv", "sensitivity", "time-anchored course (D1)")):
    for ln, r in read_csv(sub):
        role = role_default if r["code"] in ("H1", "H2", "H3") else ("sensitivity" if r["code"].startswith("S") else "descriptive")
        if sub.endswith("time_anchored/tests.csv"):
            role = "sensitivity"
        add(experiment="SV-01-01-habitus-distance", package="SV-01", result_type="test", role=role,
            measure=f"{r['code']}: {r['label']}", comparison=f"habitus grade (DS05), {code}", dataset="DS05",
            source="SRC-F (dogs); SRC-B (course)", species="B. rossi", n=r["n"], effect_type=r["statistic"],
            effect=r["estimate"], ci_low=r["ci_low"], ci_high=r["ci_high"], p=r["p"], q=r["q"],
            family="SV-01 H1-H3" if r["q"] else "", family_size="3" if r["q"] else "", source_file=sub, source_line=ln)
for sub in ("SV-01/out/replication_geometry.csv", "SV-01/out/time_anchored/replication_geometry.csv"):
    for ln, r in read_csv(sub):
        ds = "DS05" if "DS05" in r["group"] else "DS03"
        add(experiment="SV-01-02-ds03-geometry", package="SV-01", result_type="effect",
            role="descriptive" if "time_anchored" not in sub else "sensitivity",
            measure=f"share within 2 spread units of the Beagle course: {r['group']}", comparison="geometry, no test",
            dataset=ds, n=r["n"], effect_type="share", effect=r["share_within_band"], ci_low=r["within_ci_low"],
            ci_high=r["within_ci_high"], source_file=sub, source_line=ln)
res = jload("SV-01/out/results.json")
add(experiment="SV-01-01-habitus-distance", package="SV-01", result_type="observation", role="descriptive",
    measure="construction check: Beagle pseudo-stage with sampling day (spec construction)", comparison="validity of the stage score",
    dataset="DS02", effect_type="rho", effect=num(res["course_A_stage_vs_day"]), source_file="SV-01/out/results.json",
    source_line="/course_A_stage_vs_day", note="stage score failed: it does not keep the Beagles' time order")

# ---------------------------------------------------------------- SV-02a
for ln, r in read_csv("SV-02/a/out/load_by_outcome.csv"):
    add(experiment="SV-02-01-load-by-outcome", package="SV-02", result_type="effect" if r["effect"] else "observation",
        role="primary", measure=f"parasite load ({r['load_method']})", comparison=f"{r['outcome_class']}: {r['definition']}",
        species=r["species_group"], dataset=f"literature {r['article']}",
        source="SRC-O" if r["article"] == "CB516" else f"LIT {r['unit']}", n=r["n_total"], effect_type=r["effect_type"],
        effect=r["effect"], ci_low=r["ci_lo"], ci_high=r["ci_hi"], p="" if r["p_value"] in ("< 0.001",) else r["p_value"],
        source_file="SV-02/a/out/load_by_outcome.csv", source_line=ln, note=f"direction {r['direction']}; DOI {r['doi']}")
res = jload("SV-02/a/out/results.json")
for k, lab in (("antibody", "antibody level"), ("load", "ddPCR parasite load")):
    add(experiment="SV-02-01-load-by-outcome", package="SV-02", result_type="effect", role="secondary",
        measure=lab, comparison="haematological score (CB141, CH12)", species="B. canis", dataset="literature CB141",
        source="LIT CH12", n=num(res["antibody_vs_load"][f"{k}_n"]), effect_type="rho", effect=num(res["antibody_vs_load"][f"{k}_rho"]),
        ci_low=num(res["antibody_vs_load"][f"{k}_ci"][0]), ci_high=num(res["antibody_vs_load"][f"{k}_ci"][1]),
        source_file="SV-02/a/out/results.json", source_line=f"/antibody_vs_load/{k}_rho",
        note="published (CB141); subsets differ, not a formal comparison")
for ln, r in read_csv("SV-02/a/out/damage_by_load_group.csv"):
    add(experiment="SV-02-01-load-by-outcome", package="SV-02", result_type="effect" if r["effect"] else "observation",
        role="descriptive", measure=f"{r['marker']} by load group", comparison=r["definition"], species=r["species_group"],
        dataset=f"literature {r['article']}", source="SRC-B" if r["unit"] == "CH09" else f"LIT {r['unit']}", n=r["n_total"],
        effect_type=r["effect_type"], effect=r["effect"], ci_low=r["ci_lo"], ci_high=r["ci_hi"],
        source_file="SV-02/a/out/damage_by_load_group.csv", source_line=ln,
        note=f"direction {r['direction']}; significant {r['significant']}; {r['flag']}".strip("; "))

# ---------------------------------------------------------------- SV-02b
for ln, r in read_csv("SV-02/b/out/readings.csv"):
    add(experiment="SV-02-02-beagle-reaction-norms", package="SV-02", result_type="observation", role="primary",
        measure=f"reaction norm reading: {r['measure']}", comparison="damage against log parasitaemia, 5 Beagles", dataset="DS02",
        n="5", effect_type="reading", effect=r["reading"], source_file="SV-02/b/out/readings.csv", source_line=ln)

# ---------------------------------------------------------------- SV-03
for ln, r in read_csv("SV-03/out/conflicts.csv"):
    add(experiment="SV-03-01-evidence-matrix", package="SV-03", result_type="observation", role="primary",
        measure=f"named conflict: {r['conflict']}", comparison="direction calls by independent unit", species=r["species_groups"],
        dataset="literature (SV-G2)", source="LIT", n=r["tested_or_flagged_units"], effect_type="units H/L/N",
        effect=f"{r['H']}/{r['L']}/{r['N']}", source_file="SV-03/out/conflicts.csv", source_line=ln, note=r["verdict"])
for ln, r in read_csv("SV-03/out/evidence_matrix_collapsed.csv"):
    if r["consistent"] != "True":
        continue
    add(experiment="SV-03-01-evidence-matrix", package="SV-03", result_type="observation", role="post_hoc",
        measure=f"consistent cell (D1, classes merged): {r['marker']}", comparison=f"direction {r['consistent_direction']}",
        species=r["species_group"], dataset="literature (SV-G2)", source="LIT", n=r["tested_units"], effect_type="units H/L/N",
        effect=f"{r['H']}/{r['L']}/{r['N']}", source_file="SV-03/out/evidence_matrix_collapsed.csv", source_line=ln,
        note=f"circular {r['circular']}; S1 Onderstepoort once: {r['S1_tested_units']} tested units, consistent {r['S1_consistent']}")
res = jload("SV-03/out/results.json")
add(experiment="SV-03-01-evidence-matrix", package="SV-03", result_type="observation", role="primary",
    measure="cells with 3 or more tested independent units", comparison="423 marker x outcome class x species cells",
    dataset="literature (SV-G2)", source="LIT", effect_type="count", effect=num(res["summary"]["main"]["cells_ge3_tested"]),
    source_file="SV-03/out/results.json", source_line="/summary/main/cells_ge3_tested", note="nothing pooled")
add(experiment="SV-03-02-definition-map", package="SV-03", result_type="observation", role="primary",
    measure="tested rows with the marker in its own severity definition", comparison="share of tested rows",
    dataset="literature (SV-G2)", source="LIT", n=num(res["circularity"]["tested_rows"]), effect_type="share",
    effect=num(res["circularity"]["share_rows"]), source_file="SV-03/out/results.json", source_line="/circularity/share_rows")

# ---------------------------------------------------------------- SV-04
for ln, r in read_csv("SV-04/out/contrasts.csv"):
    ds = "S-CB050" if r["file"].startswith("S-CB050") else "S-CB017"
    primary = r["floor_handling"] == "as reported" and r["file"] in ("S-CB050", "S-CB017")
    role = "primary" if primary and r["analyte"] == "il8" else ("secondary" if primary else "sensitivity")
    outc = "died vs survived" if ds == "S-CB050" else "complicated vs uncomplicated"
    add(experiment="SV-04-01-il8-direction", package="SV-04", result_type="test", role=role, measure=r["analyte"],
        comparison=f"{outc}, {r['timepoint']}", dataset=ds, n=f"{r['n_severe']} vs {r['n_nonsevere']}", effect_type="Cliff's delta",
        effect=r["cliff_delta"], ci_low=r["cliff_lo"], ci_high=r["cliff_hi"], p=r["p"], q=r["q"],
        family=f"SV-04 {r['file']} {r['floor_handling']}", family_size="6", source_file="SV-04/out/contrasts.csv", source_line=ln,
        note=f"floors {r['floor_handling']}")
for ln, r in read_csv("SV-04/out/infected_vs_control.csv"):
    add(experiment="SV-04-01-il8-direction", package="SV-04", result_type="test", role="post_hoc", measure=r["analyte"],
        comparison="infected vs healthy controls (no outcome; deviation D1)", dataset=r["file"],
        n=f"{r['n_infected']} vs {r['n_control']}", effect_type="Cliff's delta", effect=r["cliff_delta"], ci_low=r["cliff_lo"],
        ci_high=r["cliff_hi"], p=r["p"], source_file="SV-04/out/infected_vs_control.csv", source_line=ln)
res = jload("SV-04/out/results.json")
for f in ("S-CB050", "S-CB017"):
    for k, lab, role in (("T1_perturbation", "perturbation count (size)", "primary"), ("T2_balance", "MCP-1 minus IL-8 balance index", "primary"),
                         ("S1_z", "z-score perturbation", "sensitivity")):
        d = res["experiment2"]["by_file"][f][k]
        add(experiment="SV-04-02-response-size-balance", package="SV-04", result_type="test", role=role, measure=lab,
            comparison="died vs survived" if f == "S-CB050" else "complicated vs uncomplicated", dataset=f,
            n=f"{d['n_severe']} vs {d['n_nonsevere']}", effect_type="Cliff's delta", effect=num(d["cliff_delta"]),
            ci_low=num(d["cliff_lo"]), ci_high=num(d["cliff_hi"]), p=num(d["p"]), q=num(d.get("q")),
            family=f"SV-04-02 {f}" if d.get("q") is not None else "", family_size="2" if d.get("q") is not None else "",
            source_file="SV-04/out/results.json", source_line=f"/experiment2/by_file/{f}/{k}/cliff_delta")

# ---------------------------------------------------------------- SV-05
for ln, r in read_csv("SV-05/out/age_contrasts.csv"):
    code = "SV-05-01-age-death" if r["family"] == "A" else "SV-05-02-age-form"
    eff, lo, hi, et = r["estimate"], r["ci_low"], r["ci_high"], r["effect"]
    add(experiment=code, package="SV-05", result_type="test", role="primary", measure=f"{r['test']}: {r['measure']}",
        comparison="young (<12 mo) vs adult", dataset=r["dataset"], n=f"{r['n_young']} vs {r['n_adult']}", effect_type=et,
        effect=eff, ci_low=lo, ci_high=hi, p=r["p"], q=r["q"], family=f"SV-05 family {r['family']}",
        family_size="3" if r["family"] == "A" else "8", source_file="SV-05/out/age_contrasts.csv", source_line=ln,
        note=f"Cliff's delta {r['cliff_delta']}" if r["cliff_delta"] else "")
res = jload("SV-05/out/results.json")
for k, ds, lab in (("balance", "S-CB050", "SV-04 balance index by age"), ("z_mean_abs", "S-CB050", "z-score perturbation by age"),
                   ("wbc", "S-CB050", "WBC by age"), ("neut_seg", "S-CB050", "segmented neutrophils by age")):
    d = res["secondary"][k]
    add(experiment="SV-05-02-age-form", package="SV-05", result_type="test", role="secondary", measure=lab,
        comparison="young vs adult", dataset=ds, n=f"{d['n_young']} vs {d['n_adult']}", effect_type="Cliff's delta",
        effect=num(d["cliff"]), ci_low=num(d["cliff_low"]), ci_high=num(d["cliff_high"]), p=num(d["p"]),
        source_file="SV-05/out/results.json", source_line=f"/secondary/{k}/cliff")
d = res["secondary"]["death_by_sex"]
add(experiment="SV-05-01-age-death", package="SV-05", result_type="test", role="secondary", measure="death by sex (male vs female)",
    comparison="died vs survived", dataset="S-CB050", n=f"{d['n_male']} vs {d['n_female']}", effect_type="odds ratio",
    effect=num(d["or"]), ci_low=num(d["or_low"]), ci_high=num(d["or_high"]), p=num(d["p"]), source_file="SV-05/out/results.json",
    source_line="/secondary/death_by_sex/or", note="died includes euthanasia")
for k, v in res["sensitivity"]["S3"].items():
    ds = k.split("_")[0]
    add(experiment="SV-05-02-age-form", package="SV-05", result_type="effect", role="sensitivity", measure=f"S3 {k} with age",
        comparison="age as a continuous variable", dataset=ds, n=num(v.get("n")), effect_type="Spearman rho", effect=num(v["rho"]),
        ci_low=num(v["rho_low"]), ci_high=num(v["rho_high"]),
        source_file="SV-05/out/results.json", source_line=f"/sensitivity/S3/{k}/rho")

# ---------------------------------------------------------------- SV-06a
for ln, r in read_csv("SV-06/a/out/transfer_grid.csv"):
    add(experiment="SV-06-01-transfer-grid", package="SV-06", result_type="observation", role="primary",
        measure=f"{r['mechanism_id']} {r['mechanism']}", comparison=f"human grade {r['human_grade']}; canine status {r['canine_status']}",
        dataset="literature (PubMed, CB notes)", source="LIT", n=r["human_n_studies"], effect_type="gap rank",
        effect=r["rank"], source_file="SV-06/a/out/transfer_grid.csv", source_line=ln,
        note=f"gap {r['gap']}; canine assay {r['canine_assay']}; testable now {r['testable_now']}; human: {r['human_direction'][:160]}")

# ---------------------------------------------------------------- SV-06b
for ln, r in read_csv("SV-06/b/out/ds07_candidates.csv"):
    role = {"positive_control": "positive_control", "secondary": "secondary"}.get(r["role"], "primary")
    add(experiment="SV-06-02-ds07-candidate-tests", package="SV-06", result_type="test" if r["tested"] == "True" else "observation",
        role=role, measure=r["protein"], comparison="complicated vs uncomplicated (plex-stratified permutation)", dataset="DS07",
        n=f"{r['n_comp']} vs {r['n_unc']}", effect_type="Cliff's delta", effect=r["delta"], ci_low=r["delta_lo"], ci_high=r["delta_hi"],
        p=r["p_stratified"], q=r["q_bh"], family="SV-06b family of 10" if r["q_bh"] else "", family_size="10" if r["q_bh"] else "",
        source_file="SV-06/b/out/ds07_candidates.csv", source_line=ln,
        note="not tested: 2 plexes" if r["tested"] != "True" else f"leave-one-plex-out {r['lopo_min']} to {r['lopo_max']}")
    if r["tested"] == "True":
        add(experiment="SV-06-02-ds07-candidate-tests", package="SV-06", result_type="test", role="sensitivity", measure=r["protein"],
            comparison="infected vs healthy controls (S3)", dataset="DS07", n=f"{r['n_comp']}+{r['n_unc']} vs {r['n_ctrl']}",
            effect_type="Cliff's delta", effect=r["delta_infected_vs_control"], p=r["p_infected_vs_control"],
            source_file="SV-06/b/out/ds07_candidates.csv", source_line=ln)

# ---------------------------------------------------------------- SV-07
for ln, r in read_csv("SV-07/out/ds03_match_rates.csv"):
    add(experiment="SV-07-01-linkage-audit", package="SV-07", result_type="observation", role="primary",
        measure=f"signalment twins: DS03 {r['ds03_block']} against {r['against']}", comparison="twin pairs against a DS05 baseline",
        dataset="DS03", source="SRC-A", species="B. rossi", n=r["pairs"], effect_type="ratio to baseline", effect=r["ratio_to_baseline"],
        p=r["p_poisson"], source_file="SV-07/out/ds03_match_rates.csv", source_line=ln, note="linkage, not a severity result")
for ln, r in read_csv("SV-07/out/ds07_numbering_chance.csv"):
    add(experiment="SV-07-01-linkage-audit", package="SV-07", result_type="observation", role="primary",
        measure=f"DS04 case numbers in the DS07 complicated list, universe {r['universe']}", comparison="hypergeometric chance",
        dataset="DS07", source="SRC-C", species="B. rossi", effect_type="expected by chance", effect=r["expected_in_complicated"],
        p=r["p_ge_observed_complicated"], source_file="SV-07/out/ds07_numbering_chance.csv", source_line=ln,
        note="6 of 7 observed; link unverified")

# ---------------------------------------------------------------- SV-08
for ln, r in read_csv("SV-08/out/sign_counts.csv"):
    add(experiment="SV-08-01-transcriptome-signatures", package="SV-08", result_type="test",
        role="primary" if r["in_family"] == "True" else "positive_control", measure=f"{r['set']} score, D0 to last pre-treatment sample",
        comparison="within-dog change (no severity contrast)", dataset="DS06", n=r["n_dogs"], effect_type="median change",
        effect=r["median_delta"], p=r["sign_test_p_two_sided"], family="SV-08 2 sets" if r["in_family"] == "True" else "",
        family_size="2" if r["in_family"] == "True" else "", source_file="SV-08/out/sign_counts.csv", source_line=ln,
        note=f"{r['positive']} of {r['n_dogs']} dogs rose; {r['beyond_background_rise']} beyond background; minimum p 0.0625")
for ln, r in read_csv("SV-08/out/primary_deltas.csv"):
    add(experiment="SV-08-01-transcriptome-signatures", package="SV-08", result_type="effect", role="descriptive",
        measure=f"{r['set']} score change, dog {r['dog']} ({r['dose']} dose)", comparison="D0 to last pre-treatment sample",
        dataset="DS06", n="1", effect_type="change in mean rank percentile", effect=r["delta"], ci_low=r["bg_delta_lo95"],
        ci_high=r["bg_delta_hi95"], source_file="SV-08/out/primary_deltas.csv", source_line=ln,
        note=f"interval is the matched random-set background; background percentile {r['bg_percentile']}")
for ln, r in read_csv("SV-08/out/unmapped_genes.csv"):
    add(experiment="SV-08-01-transcriptome-signatures", package="SV-08", result_type="observation", role="descriptive",
        measure=f"gene not scored: {r['gene']} ({r['set']})", comparison="DS06 count matrix", dataset="DS06", effect_type="missing",
        effect="not in matrix", source_file="SV-08/out/unmapped_genes.csv", source_line=ln, note=r["reason"])

# ---------------------------------------------------------------- SV-09
res = jload("SV-09/out/results.json")
for i, h in enumerate(res["step1"]["habitus"]):
    add(experiment="SV-09-01-ds05-residual-axes", package="SV-09", result_type="test", role="descriptive",
        measure=f"residual axis {h['component']} with habitus (partial)", comparison="habitus grade, after haematocrit and illness days",
        dataset="DS05", n=num(h["n"]), effect_type="partial rho", effect=num(h["partial_rho"]), ci_low=num(h["ci"][0]),
        ci_high=num(h["ci"][1]), p=num(h["p"]), family="SV-09-01 2 axes", family_size="2",
        source_file="SV-09/out/results.json", source_line=f"/step1/habitus/{i}/partial_rho", note="DS05 already seen: exploratory")
for ln, r in read_csv("SV-09/out/congruence.csv"):
    add(experiment="SV-09-02-axis-congruence", package="SV-09", result_type="test", role="replication",
        measure=f"Tucker phi, {r['block']} block component {r['component']}", comparison=f"DS05 against {r['target']}",
        dataset=r["target"], n=r["n_target"], effect_type="phi", effect=r["phi"], ci_low=r["ci_low"], ci_high=r["ci_high"],
        p=r["label_perm_p"], source_file="SV-09/out/congruence.csv", source_line=ln, note=f"uniform-pattern phi {r['uniform_phi']}")
for ln, r in read_csv("SV-09/out/axis_outcome.csv"):
    ds = "S-CB050" if "S-CB050" in r["analysis"] else "S-CB017"
    role = "descriptive" if r["bh_q"] else ("post_hoc" if "post hoc" in r["analysis"] else "sensitivity")
    add(experiment="SV-09-03-axis-outcome", package="SV-09", result_type="test", role=role, measure=r["analysis"],
        comparison="died vs survived" if ds == "S-CB050" else "complicated vs uncomplicated", dataset=ds,
        n=f"{r['n_label1']} vs {r['n_label0']}", effect_type="Cliff's delta", effect=r["cliffs_delta"], ci_low=r["ci_low"],
        ci_high=r["ci_high"], p=r["perm_p"], q=r["bh_q"], family="SV-09-03 2 tests" if r["bh_q"] else "",
        family_size="2" if r["bh_q"] else "", source_file="SV-09/out/axis_outcome.csv", source_line=ln)

# ---------------------------------------------------------------- SV-10
for ln, r in read_csv("SV-10/out/power.csv"):
    add(experiment={"parasite_genotype": "SV-10-01-parasite-genotype", "host_genetics": "SV-10-02-host-genetics"}.get(
        r["memo"], "SV-10-03-minimum-dataset"), package="SV-10", result_type="design", role="descriptive",
        measure=r["scenario"], comparison=r["design"], dataset="none (planning)", source="none", n=r["n_total"],
        effect_type="odds ratio detectable", effect=r["odds_ratio"], source_file="SV-10/out/power.csv", source_line=ln,
        note=f"cohort needed {r['cohort_needed']}")

# ---------------------------------------------------------------- SV-G1, SV-G2, SV-INT
for ln, r in read_csv("SV-G1/out/datasets.csv"):
    add(experiment="SV-G1-01-data-layer-coverage", package="SV-G1", result_type="observation", role="descriptive",
        measure=f"tidy file {r['dataset']}", comparison="dogs and checks", dataset=r["dataset"], n=r["dogs"], effect_type="checks passed",
        effect=f"{r['checks_passed']}/{r['checks_total']}", source_file="SV-G1/out/datasets.csv", source_line=ln,
        note=f"missing {r['missing_pct']}%; flags {r['flags']}")
for ln, r in read_csv("SV-G2/out/tables/markers.csv"):
    add(experiment="SV-G2-01-literature-extraction", package="SV-G2", result_type="observation", role="descriptive",
        measure=f"marker tested against severity: {r['marker']}", comparison=r["outcome_classes"][:120], species=r["species_groups"],
        dataset="literature (SV-G2)", source="LIT", n=r["units"], effect_type="units H/L/N",
        effect=f"{r['units_sig_higher']}/{r['units_sig_lower']}/{r['units_not_significant']}",
        source_file="SV-G2/out/tables/markers.csv", source_line=ln)
for ln, r in read_csv("SV-INT/out/synthesis_table.csv"):
    add(experiment="SV-INT-01-integration-report", package="SV-INT", result_type="observation", role="descriptive",
        measure=f"line {r['line']}: {r['code']}", comparison=r["asked"][:150], dataset="all", source=r["independent_sources"][:80],
        effect_type="verdict", effect=r["verdict"], source_file="SV-INT/out/synthesis_table.csv", source_line=ln,
        note=f"strength {r['strength']}")

OUT.mkdir(exist_ok=True)
with (OUT / "census_raw.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
print(f"census rows: {len(rows)}")
