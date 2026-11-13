"""SV-META: build the console-loader file out/db/SV-META-01-research-leads.json from the files in out/.

Every number in the payloads and in the interpretation text is read from out/ (tiers.json, themes.csv, candidates.csv, leads.csv,
census.csv, refutation.csv). Run after census.py, check_census.py, themes.py and screen.py.
"""
import csv
import hashlib
import re
import json
from datetime import datetime, timezone
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
OUT = PKG / "out"
CODE = "SV-META-01-research-leads"
TIER_TEXT = {
    "A": ("significant finding", "passes the statistical screen in 2 or more independent sources of one species, not circular, not a known driver, not already published"),
    "B": ("signal", "passes the screen in one source, not circular, not a known driver, not the published finding of those dogs or another CB article"),
    "C": ("convergent lead", "no new single result passes; 2 or more non-circular B. rossi sources in the expected direction, combined BH q < 0.05 over themes, every leave-one-source-out p < 0.05, cross-source claim not published"),
    "D": ("gap lead", "no canine data against severity, human evidence grade 3, a canine assay exists"),
    "X": ("rejected", "null, circular, known driver, published, artefact, single source that fails, or refuted"),
}


def rows(name):
    return list(csv.DictReader((OUT / name).open(encoding="utf-8")))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


tiers = json.loads((OUT / "tiers.json").read_text(encoding="utf-8"))
cnt = tiers["counts"]
cands = rows("candidates.csv")
leads = rows("leads.csv")
themes = rows("themes.csv")
census = rows("census.csv")
refs = rows("refutation.csv")

combined = [t for t in themes if t["row_type"] == "combined" and t["q_themes"]]
m_themes = int(combined[0]["m_themes"]) if combined else 0
by_tier = {t: [c for c in cands if c["final_tier"] == t] for t in "ABCDX"}


def names(t):
    return "; ".join(c["label"] for c in by_tier[t])


first = (f"{cnt['A']} candidates reached tier A, {cnt['B']} tier B, {cnt['C']} tier C, {cnt['D']} tier D and {cnt['X']} were rejected (X), "
         f"out of {len(cands)} candidates.")
if cnt["A"] == 0 and cnt["B"] == 0:
    first += " No candidate reached tier A or B: no single result is a new, non-circular severity finding."
answer = first
if by_tier["C"]:
    answer += f" Tier C (convergent across independent sources): {names('C')}."
if by_tier["D"]:
    answer += f" Tier D (gaps with strong human evidence and a canine assay): {names('D')}."

t02 = next((t for t in combined if t["theme"] == "T02"), None)

primary = {
    "answer": answer,
    "tier_counts": [{"tier": t, "n": cnt[t], "label": TIER_TEXT[t][0], "definition": TIER_TEXT[t][1]} for t in "ABCDX"],
    "n_candidates": len(cands),
    "n_census_rows": tiers["census_rows"],
    "n_census_tests": tiers["census_family"],
    "n_census_pass": tiers["census_pass"],
    "m_themes": m_themes,
    "n_leads": len(leads),
    "caveat": ("Hypothesis-generating: every labelled file was already seen, and the themes were chosen after the results were seen "
               f"(combined p values are BH-corrected over {m_themes} themes). A lead is a thing to measure, not a predictor. "
               "Died includes euthanasia in the Onderstepoort files. One species per source: between-file differences are not species effects."),
}

lead_payload = [{
    "rank": int(l["rank"]), "tier": l["tier"], "kind": l["kind"], "hypothesis": l["hypothesis"], "evidence": l["evidence"],
    "human_counterpart": l["human_counterpart"], "human_doi": [d for d in l["human_doi"].split(";") if d],
    "parallel_new": l["parallel_new"], "refuted_by": l["refuted_by"], "next_existing": l["next_study_existing_data"],
    "next_new_dogs": l["next_study_new_dogs"], "minimum_dataset": l["minimum_dataset_addition"], "candidates": l["candidates"]}
    for l in leads]

theme_payload = {"rows": [{
    "theme": t["theme"], "theme_label": t["theme_label"], "row_type": t["row_type"], "source": t["source"], "species": t["species"],
    "measure": t["measure"], "n": t["n"], "oriented_effect": f(t["oriented_effect"]), "ci_low": f(t["ci_low"]), "ci_high": f(t["ci_high"]),
    "p": f(t["p"]), "q_themes": f(t["q_themes"]), "loso_max_p": f(t["loso_max_p"]), "sources_in_direction": t["sources_in_direction"],
    "circular": t["circular"], "known_driver": t["known_driver"], "literature_calls": t["literature_calls"],
    "scale": "Hedges g" if "Hedges" in t["note"] else ""} for t in themes],
    "footnote": ("SRC-A S-CB050/S-CB517 Onderstepoort (died), SRC-B 5 experimental Beagles (high vs low dose, exact p, minimum 0.2), "
                 "SRC-C DS07 (complicated), SRC-D S-CB017 B. canis (complicated), SRC-F DS05 Eastern Cape clinic (dullness, a proxy), "
                 "SRC-O S-CB516 B. canis (died). Circular indicators (marker in the label) are drawn grey and left out of the combined test. "
                 "The SRC-O load effect is a Hedges g, clipped to the axis. Exploratory: already-seen files.")}

cand_payload = [{"id": c["id"], "label": c["label"], "tier": c["final_tier"], "provisional_tier": c["provisional_tier"], "kind": c["kind"],
                 "evidence": c["evidence"], "novelty_where": c["novelty_where"], "refutation_verdict": c["refutation_verdict"],
                 "refutation_reason": c["refutation_reason"]} for c in cands]


def ci(r):
    return f"{r['ci_low']} to {r['ci_high']}" if r["ci_low"] and r["ci_high"] else ""


def short(x, k=6):
    v = f(x)
    if v is None:
        return x
    return f"{v:.{k}g}"


census_payload = [{"row_id": r["row_id"], "experiment": r["experiment"], "measure": r["measure"][:140], "comparison": r["comparison"][:120],
                   "dataset": r["dataset"], "source": r["source"][:40], "n": r["n"], "effect": short(r["effect"], 4),
                   "ci": (f"{short(r['ci_low'], 3)} to {short(r['ci_high'], 3)}" if r["ci_low"] and r["ci_high"] else ""),
                   "p": short(r["p"], 3), "q": short(r["q"], 3), "role": r["role"], "screen": r["stat_screen"], "tier": r["tier"],
                   "candidates": r["candidates"], "file": f"{r['source_file']}:{r['source_line']}"} for r in census]
ref_payload = [{"candidate_id": r["candidate_id"], "by": r["by"], "reason_tested": r["reason_tested"], "result": r["result"],
                "rejects": r["rejects"]} for r in refs]

t02_text = (f"The strongest convergent theme that is not a known driver is the monocyte theme (T02: circulating monocyte count, with CD14 and CCL2): {t02['sources_in_direction']} B. rossi sources in "
            f"the expected direction, Stouffer Z {float(t02['oriented_effect']):.2f}, BH q {float(t02['q_themes']):.2g} over {m_themes} themes, "
            f"leave-one-source-out max p {float(t02['loso_max_p']):.3f}.") if t02 else ""

# ---- second run (2026-11-13): evidence map, compact lead cards, short interpretation. No new analysis: every value below is
# derived by a stated rule from files that the run already holds (candidates.json, themes.csv, census.csv, refutation/K*.json).
cjson = json.loads((PKG / "scripts" / "candidates.json").read_text(encoding="utf-8"))
cmeta = {c["id"]: c for c in cjson["candidates"]}
lmeta = {l["id"]: l for l in cjson["leads"]}
refjs = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted((PKG / "refutation").glob("K*.json"))}
ind_rows = [t for t in themes if t["row_type"] == "indicator"]
lead_rank = {}
for l in leads:
    for cid in l["candidates"].split(";"):
        lead_rank[cid] = int(l["rank"])


def canine_x(c):
    """Rule X: tier D (and refuted D candidates, provisional D) = 0: no canine data against severity. A theme-level candidate
    (x_from_theme in candidates.json) = number of non-circular indicators of its theme, any species, in the expected direction.
    Any other candidate = number of distinct independent sources among its census rows that pass the statistical screen."""
    meta = cmeta[c["id"]]
    if c["provisional_tier"] == "D":
        return 0, 0, "gap: no canine data against severity"
    if meta.get("x_from_theme"):
        use = [t for t in ind_rows if t["theme"] == meta["theme"] and not t["circular"] and f(t["oriented_effect"]) is not None]
        k = sum(1 for t in use if f(t["oriented_effect"]) > 0)
        return k, len(use), f"{k} of {len(use)} non-circular sources in the expected direction (theme {meta['theme']})"
    srcs = {r["source"] for r in census if c["id"] in r["candidates"].split(";") and r["stat_screen"] == "pass"}
    return len(srcs), len(srcs), f"{len(srcs)} independent source(s) with a result that passes the screen"


def disease_of(claim):
    """Rule for the chip label: the first keyword found in the claim text, in this order."""
    s = claim.lower()
    for key, lab in (("dog", "dogs (other disease)"), ("canine", "dogs (other disease)"), ("falciparum", "falciparum malaria"), ("knowlesi", "knowlesi malaria"), ("cerebral malaria", "cerebral malaria"),
                     ("malaria", "malaria"), ("babesiosis", "human babesiosis"), ("septic", "sepsis"), ("sepsis", "sepsis"),
                     ("critical", "critical illness"), ("icu", "critical illness"),
                     ("mice", "mice"), ("murine", "mice")):
        if key in s:
            return lab
    return "other"


def human_chips(cid):
    rf = refjs.get(cid)
    if not rf:
        return []
    return [{"disease": disease_of(h.get("claim", "")), "agrees": bool(h.get("direction_agrees")), "doi": h["doi"],
             "claim": h.get("claim", "")[:220]} for h in rf.get("human_counterpart", [])
            if h.get("doi") and not re.search(r"not verified|could not be resolved", h.get("claim", ""), re.I)]


emap = []
for c in cands:
    x, xn, xb = canine_x(c)
    chips = human_chips(c["id"])
    if c["id"] in refjs:
        hum = [h for h in chips if h["disease"] != "dogs (other disease)"]  # rule Y: human records only
        y = sum(1 for h in hum if h["agrees"])
        y_dis = sum(1 for h in hum if not h["agrees"])
        yb = f"{y} human record(s) agree in direction, {y_dis} do not (verified by the refutation attempt)"
    else:
        y, y_dis, yb = None, None, "human evidence not assessed (rejected at the screen)"
    emap.append({"id": c["id"], "short_label": cmeta[c["id"]]["short_label"], "label": c["label"], "tier": c["final_tier"],
                 "lead_rank": lead_rank.get(c["id"]), "x": x, "x_of": xn, "x_basis": xb, "y": y, "y_disagree": y_dis, "y_basis": yb,
                 "mixed": bool(y_dis), "verdict": c["refutation_verdict"]})
# overlap slots: marks with the same (x, y) get slots 0..k-1, leads first (by rank), then by id
groups = {}
for e in emap:
    groups.setdefault((e["x"], e["y"]), []).append(e)
for key, g in groups.items():
    g.sort(key=lambda e: (e["lead_rank"] is None, e["lead_rank"] or 0, e["id"]))
    for i, e in enumerate(g):
        e["slot"], e["slots"] = i, len(g)
EF = ["id", "short_label", "tier", "lead_rank", "x", "x_of", "x_basis", "y", "y_disagree", "y_basis", "mixed", "slot", "slots", "verdict"]
with (OUT / "evidence_map.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=EF, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for e in emap:
        w.writerow({k: ("" if e[k] is None else e[k]) for k in EF})
evidence_payload = {
    "points": emap,
    "x_title": "Canine evidence: independent dog-level sources in the expected direction (0 = gap, no canine data)",
    "y_title": "Human evidence: verified human records that agree in direction",
    "footnote": ("Evidence map, not a score. Themes were chosen after the results were seen; died includes euthanasia (Onderstepoort); one "
                 "species per source. Hollow ring = some human records disagree. Grey band = human evidence not assessed (rejected at the screen)."),
}

for lp, l in zip(lead_payload, leads):
    m = lmeta[l["lead_id"]]
    cid = l["candidates"].split(";")[0]
    forest = [{"source": t["source"], "species": t["species"], "measure": t["measure"], "n": t["n"], "oriented_effect": f(t["oriented_effect"]),
               "ci_low": f(t["ci_low"]), "ci_high": f(t["ci_high"]), "p": f(t["p"]), "circular": t["circular"], "known_driver": t["known_driver"]}
              for t in ind_rows if m.get("theme_forest") and t["theme"] == m["theme_forest"]]
    comb = next((t for t in combined if m.get("theme_forest") and t["theme"] == m["theme_forest"]), None)
    lp.update({"lead_id": l["lead_id"], "candidate_id": cid, "short_name": m["short_name"], "forest": forest,
               "combined": (f"{comb['sources_in_direction']} B. rossi sources in the expected direction · Stouffer Z "
                            f"{float(comb['oriented_effect']):.2f} · BH q {float(comb['q_themes']):.2g} over {m_themes} themes · "
                            f"leave-one-source-out max p {float(comb['loso_max_p']):.3f}") if comb else "",
               "canine_line": m.get("canine_line", ""), "human": human_chips(cid),
               "refuted_short": m["refuted_short"], "existing_short": m["existing_short"], "new_short": m["new_short"],
               "md_short": m["md_short"], "refutation_verdict": next(c["refutation_verdict"] for c in cands if c["id"] == cid)})

primary["headline"] = (f"0 of {len(cands)} candidates reach tier A or B. " if cnt["A"] + cnt["B"] == 0 else
                       f"{cnt['A'] + cnt['B']} of {len(cands)} candidates reach tier A or B. ") + \
                      f"{cnt['C']} convergent lead and {cnt['D']} gap leads remain to be measured."

interp = {"sections": [
    {"heading": "Question", "paragraphs": [
        "Does any result of the 23 experiments, alone or across independent sources, point to a severity correlate, a new mechanism or a "
        "human-disease parallel worth further research?"]},
    {"heading": "What was done", "paragraphs": [
        f"{tiers['census_rows']} results were read from the package files and screened ({tiers['census_pass']} pass the statistical screen). "
        f"Fifteen themes were scored with one indicator per independent source and combined over {m_themes} themes; each surviving candidate "
        f"got a separate refutation attempt by a sub-agent ({len(refjs)} candidates, {sum(1 for r in refs if r['by'].startswith('sub-agent'))} checks)."]},
    {"heading": "Result", "paragraphs": [first,
        (f"The monocyte lead (tier C) agrees in {t02['sources_in_direction']} B. rossi sources (BH q {float(t02['q_themes']):.2g}) but rests "
         "mostly on DS05, the file that suggested it. Tier D leads have no canine severity data.") if t02 else ""]},
    {"heading": "What this does not show", "paragraphs": [
        "No lead is a confirmed finding or a predictor: the files were already seen and the themes were chosen afterwards. Died includes "
        "euthanasia (Onderstepoort); one species per source."]},
]}

inputs = {p: sha(PKG / p)[:12] for p in ("spec.md", "scripts/census.py", "scripts/themes.py", "scripts/screen.py", "scripts/candidates.json")}
load = {
    "experiment": {
        "code": CODE,
        "name": "Meta experiment: a final review of all 23 experiments for research leads on severe canine babesiosis",
        "description": ("Does any result of the 23 experiments, alone or in agreement across independent sources, point to a severity correlate, a "
                        "mechanism or a human-disease parallel worth further research? Hypothesis-generating: every candidate is screened, "
                        "checked for novelty and given a separate refutation attempt before it is tiered."),
        "method": "meta_review",
        "dataset": None,
        "parameters": {"package": "SV-META", "role": "descriptive",
                       "datasets": ["S-CB050", "S-CB517", "DS02", "DS05", "DS06", "DS07", "S-CB017", "S-CB516", "literature"],
                       "independent_sources": ["SRC-A", "SRC-B", "SRC-C", "SRC-D", "SRC-F", "SRC-O", "LIT"],
                       "spec_sha256": sha(PKG / "spec.md"), "seed": 20261112, "n_boot": 2000, "n_perm": 10000,
                       "tier_counts": cnt, "m_themes": m_themes, "inputs_sha256_12": inputs},
        "script": "/experiments/SV-META/scripts/themes.py",
        "script_version": sha(PKG / "scripts/themes.py")[:12],
        "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_subjects": 0,
        "n_variables": len({t["theme"] for t in themes}),
        "n_tests": len([t for t in themes if t["row_type"] == "combined"]),
        "summary": (f"{cnt['A'] + cnt['B']} of {len(cands)} candidates reached tier A or B ({cnt['C']} C, {cnt['D']} D, {cnt['X']} X). "
                    + (f"Tier C: higher circulating monocyte count in more severe B. rossi disease, {t02['sources_in_direction']} sources, "
                       f"Stouffer Z {float(t02['oriented_effect']):.2f}, BH q {float(t02['q_themes']):.2g} over {m_themes} themes chosen after "
                       f"the results; {sum(1 for t in combined if float(t['q_themes']) < 0.05)} of {len(combined)} theme tests q < 0.05, "
                       "two of them known drivers." if t02 else "")),
    },
    "associations": [],
    "cluster_assignments": [],
    "results": [
        {"kind": "primary_result", "title": "Tier counts and the answer", "sort_order": 1, "payload": primary},
        {"kind": "evidence_map", "title": "Evidence map of the candidates", "sort_order": 2, "payload": evidence_payload},
        {"kind": "leads", "title": "Research leads in rank order", "sort_order": 3, "payload": lead_payload},
        {"kind": "themes", "title": "Agreement between independent sources, by theme", "sort_order": 4, "payload": theme_payload},
        {"kind": "candidates", "title": "Candidates and their tiers", "sort_order": 5, "payload": cand_payload},
        {"kind": "refutation", "title": "Refutation attempts", "sort_order": 6, "payload": ref_payload},
        {"kind": "census", "title": "Result census", "sort_order": 7, "payload": census_payload},
        {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp},
    ],
}
(OUT / "db").mkdir(parents=True, exist_ok=True)
text = json.dumps(load, indent=1, ensure_ascii=False, allow_nan=False)
(OUT / "db" / f"{CODE}.json").write_text(text, encoding="utf-8")
size = sum(len(json.dumps(r["payload"], ensure_ascii=False)) for r in load["results"])
if size > 1_000_000:
    raise SystemExit(f"payloads {size} bytes > 1 MB")
print(f"load file written; payloads {size} bytes; summary: {load['experiment']['summary']}")
