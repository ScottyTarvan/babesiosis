"""Tidy S-CB517 (cytokine study, SRC-A, Onderstepoort; article CB517).

Two PDF tables from the PLoS ONE supplement: S1 (leukocytes) and S2 (SAA, CRP, 7 cytokines), one row per
dog: 97 infected (Case1-Case97) and 15 controls (Control1-Control15). These are the same dogs as S-CB050
cases 1-97 and controls 201-215 (never pool). This script links them by value, records same_dog_as, and
compares the 7 cytokines with the S-CB050 tidy file (run tidy_scb050.py first).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tidylib import (OUT, RAW, TIDY, built_from_entry, check, dict_row, median, neutral_ids, num, var,  # noqa: E402
                     write_dataset, zip_member, mask_ids)
from tidy_scb050 import spearman  # noqa: E402

DS = "S-CB517"
ZIP = RAW / "S-CB517" / "PMC4783066_supplementaryFiles.zip"
S1, S2 = "pone.0150113.s001.pdf", "pone.0150113.s002.pdf"
PDFTOTEXT = Path(r"C:\Program Files\Git\mingw64\bin\pdftotext.exe")
WORK = OUT / "work"
HALF = 0.05 + 1e-9   # published values are rounded to 1 decimal

# (file, column header) -> (name, unit, floor, ceiling, note)
S1_COLS = [
    ("WBC (x10^9/L)", "wbc", "10^9/L", None, None, "ADVIA 2120."),
    ("NEUT (x10^9/L)", "neut_seg", "10^9/L", None, None, "NEUT in the file; the article's Table 1 calls it the segmented neutrophil count. No band count in the file."),
    ("LYMPH (x10^9/L)", "lymph", "10^9/L", None, None, ""),
    ("MONO (x10^9/L)", "mono", "10^9/L", None, None, ""),
    ("EOS (x10^9/L)", "eos", "10^9/L", None, None, ""),
]
S2_COLS = [
    ("SAA (mg/L)", "saa", "mg/L", None, 3001.0, "3001.0 occurs in 4 dogs: read as an above-range code (inferred; not documented). Case44 has 3017.1, above that code, so the code is uncertain; only exact 3001.0 is flagged."),
    ("CRP (mg/L)", "crp", "mg/L", None, None, ""),
    ("IL-2 (pg/mL)", "il2", "pg/mL", 3.4, 50000.0, "Floor 3.4 per record; 50000.0 in Case80 read as the upper limit."),
    ("IL-6 (pg/mL)", "il6", "pg/mL", 3.6, 50000.0, "Floor 3.6 per record; 50000.0 in Case80 read as the upper limit."),
    ("IL-8 (pg/mL)", "il8", "pg/mL", None, None, "No floor documented. The minimum 21.6 occurs in 3 dogs; not flagged."),
    ("IL-10 (pg/mL)", "il10", "pg/mL", 8.4, None, "Floor 8.4 per record."),
    ("IL-18 (pg/mL)", "il18", "pg/mL", 5.7, 50000.0, "Floor 5.7 per record; 50000.0 in Case80 read as the upper limit."),
    ("GM-CSF (pg/mL)", "gmcsf", "pg/mL", 9.1, 50000.0, "Floor 9.1 per record; 50000.0 in Case80 read as the upper limit."),
    ("MCP-1 (pg/mL)", "mcp1", "pg/mL", None, None, "No floor documented."),
]
CYTOKINES = ["il2", "il6", "il8", "il10", "il18", "gmcsf", "mcp1"]
ROW_RE = re.compile(r"^(Case\d+|Control\d+)\s+(?:(Survived|Died)\s+)?(.*)$")


def pdf_text(member):
    """pdftotext -layout on the zip member, through a temporary copy in out/work/."""
    WORK.mkdir(parents=True, exist_ok=True)
    tmp = WORK / member
    tmp.write_bytes(zip_member(ZIP, member))
    try:
        res = subprocess.run([str(PDFTOTEXT), "-layout", str(tmp), "-"], capture_output=True, check=True)
    finally:
        tmp.unlink()
    return res.stdout.decode("utf-8")


def parse(text, cols, label):
    """Rows {original_id: (outcome text or None, [numbers])}. Repeated page headers are skipped."""
    out, headers = {}, 0
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("Case no"):
            headers += 1
            got = re.split(r"\s{2,}", s)
            if got != ["Case no", "Outcome"] + [c[0] for c in cols]:
                raise SystemExit(f"{label}: unexpected header {got}")
            continue
        m = ROW_RE.match(s)
        if not m:
            raise SystemExit(f"{label}: unreadable line {s!r}")
        nums = [num(x) for x in m.group(3).split()]
        if len(nums) != len(cols) or any(v is None for v in nums):
            raise SystemExit(f"{label}: {m.group(1)} has {len(nums)} values, expected {len(cols)}")
        if m.group(1) in out:
            raise SystemExit(f"{label}: duplicate row {m.group(1)}")
        out[m.group(1)] = (m.group(2), nums)
    return out, headers


def main():
    notes, flags = [], []
    t1, t2 = pdf_text(S1), pdf_text(S2)
    rows1, h1 = parse(t1, S1_COLS, "S1")
    rows2, h2 = parse(t2, S2_COLS, "S2")
    if set(rows1) != set(rows2):
        raise SystemExit(f"S1 and S2 dogs differ: {sorted(set(rows1) ^ set(rows2))}")
    order = sorted(rows1, key=lambda o: (o.startswith("Control"), int(re.sub(r"\D", "", o))))

    parsed = []   # (original id, group, vals, censored, died)
    for oid in order:
        o1, n1 = rows1[oid]
        o2, n2 = rows2[oid]
        if o1 != o2:
            flags.append(f"FLAG {oid}: Outcome differs between S1 ({o1}) and S2 ({o2}); S2 used")
        group = "control" if oid.startswith("Control") else "infected"
        if (group == "control") != (o2 is None):
            flags.append(f"FLAG {oid}: group {group} with Outcome {o2}")
        died = {"Died": 1, "Survived": 0, None: None}[o2]
        vals, cens = {}, {}
        for (h, name, unit, floor, ceiling, _), v in list(zip(S1_COLS, n1)) + list(zip(S2_COLS, n2)):
            vals[name] = v
            if ceiling is not None and v == ceiling:   # only the exact code value
                cens[name] = "ceiling"
            elif floor is not None and v <= floor:
                cens[name] = "floor"
                if v < floor:
                    flags.append(f"FLAG {oid}: {name} {v} is below the documented floor {floor}; kept")
        parts = vals["neut_seg"] + vals["lymph"] + vals["mono"] + vals["eos"]
        if group == "infected" and parts < 0.75 * vals["wbc"]:
            flags.append(f"FLAG {oid}: NEUT+LYMPH+MONO+EOS = {parts:.2f} is more than 25% below WBC {vals['wbc']} "
                         "(bands are not in the file, or an entry error); kept")
        parsed.append((oid, group, vals, cens, died))

    # ---- link to S-CB050 by value
    f050 = json.loads((TIDY / "S-CB050.features.json").read_text(encoding="utf-8"))
    o050 = json.loads((TIDY / "S-CB050.outcomes.json").read_text(encoding="utf-8"))
    case_of = {r["dog_id"]: r["original_id"] for r in o050["records"]}
    died050 = {r["dog_id"]: r["values"].get("died") for r in o050["records"]}
    cand = [r for r in f050["records"] if all(k in r["values"] for k in CYTOKINES)]

    def agree(a, b):
        return a == b or (a >= 50000 and b >= 50000)   # the ceiling code is 50000.0 here, 50001.0 in S-CB050

    same_dog, link_detail = {}, {}
    for oid, group, vals, _, _ in parsed:
        scored = sorted(((sum(agree(vals[k], r["values"][k]) for k in CYTOKINES)
                          + (vals["wbc"] == r["values"]["wbc"]) + (vals["neut_seg"] == r["values"]["neut_seg"]), r)
                         for r in cand), key=lambda x: -x[0])
        best, second = scored[0], scored[1]
        n = int(re.sub(r"\D", "", oid))
        implied = str(n) if group == "infected" else str(200 + n)
        if best[0] >= 7 and second[0] <= best[0] - 4 and best[1]["group"] == group:
            same_dog[oid] = best[1]["dog_id"]
        link_detail[oid] = {"best_match_case": case_of[best[1]["dog_id"]], "id_implied_case": implied,
                            "matching_values_of_9": best[0], "next_best_of_9": second[0]}
    by_id = sum(1 for d in link_detail.values() if d["best_match_case"] == d["id_implied_case"])
    unlinked = [o for o in order if o not in same_dog]

    ids = neutral_ids(DS, order)
    records, orecs = [], []
    for oid, group, vals, cens, died in parsed:
        rec = {"dog_id": ids[oid], "group": group, "timepoint": "admission" if group == "infected" else "single",
               "day": None, "values": vals, "censored": cens}
        if oid in same_dog:
            rec["same_dog_as"] = same_dog[oid]
        records.append(rec)
        orecs.append({"dog_id": ids[oid], "original_id": oid, "timepoint": None, "day": None, "values": {"died": died}})

    # ---- compare with S-CB050
    rec050 = {r["dog_id"]: r for r in f050["records"]}
    comp = {}
    for k in CYTOKINES + ["wbc", "neut_seg"]:
        xs, ys, mism = [], [], []
        eq = w1 = 0
        for oid, _, vals, _, _ in parsed:
            if oid not in same_dog:
                continue
            a, b = vals.get(k), rec050[same_dog[oid]]["values"].get(k)
            if a is None or b is None:
                continue
            xs.append(a)
            ys.append(b)
            eq += a == b
            w1 += abs(a - b) <= 0.01 * max(abs(a), abs(b))
            if a != b:
                mism.append({"S-CB517": ids[oid], "S-CB050": same_dog[oid], "S-CB517_value": a, "S-CB050_value": b})
        rho, n = spearman(xs, ys)
        comp[k] = {"n_pairs": n, "n_equal": eq, "n_within_1pct": w1, "spearman_rho": None if rho is None else round(rho, 6),
                   "mismatches": mism}
    # WBC: where the files differ, test whether S-CB050 WBC = S-CB517 NEUT+LYMPH+MONO+EOS + S-CB050 band count
    wbc_expl = []
    for m in comp["wbc"]["mismatches"]:
        a = next(p[2] for p in parsed if ids[p[0]] == m["S-CB517"])
        b = rec050[m["S-CB050"]]["values"]
        s = a["neut_seg"] + a["lymph"] + a["mono"] + a["eos"] + b.get("neut_band", 0)
        wbc_expl.append(abs(s - m["S-CB050_value"]) <= 0.25)
    comp["wbc"]["n_mismatch_where_scb050_wbc_equals_differential_plus_bands"] = sum(wbc_expl)
    died_pairs = [(died, died050[same_dog[oid]]) for oid, g, _, _, died in parsed if g == "infected" and oid in same_dog]
    died_diff = [(ids[oid], same_dog[oid]) for oid, g, _, _, died in parsed
                 if g == "infected" and oid in same_dog and died != died050[same_dog[oid]]]
    comp["died_agreement"] = {"n_pairs": len(died_pairs), "n_equal": sum(a == b for a, b in died_pairs), "differ": died_diff}
    comp["link"] = (f"{len(same_dog)} of {len(order)} rows linked by value (7 cytokines + WBC + segmented neutrophils; "
                    f"best match >= 7 of 9 equal values and at least 4 more than the next best; floor values make 3-4 chance matches common). The best value match is the case implied by the ID "
                    f"(CaseN -> S-CB050 case N; ControlK -> S-CB050 case 200+K) in {by_id} of {len(order)} rows.")
    comp["per_row"] = link_detail
    cyt_summary = "; ".join(f"{k} {comp[k]['n_equal']}/{comp[k]['n_pairs']} equal, {comp[k]['n_within_1pct']} within 1%, "
                            f"rho {comp[k]['spearman_rho']}" for k in CYTOKINES)
    oth_summary = "; ".join(f"{k} {comp[k]['n_equal']}/{comp[k]['n_pairs']} equal, {comp[k]['n_within_1pct']} within 1%"
                            for k in ("wbc", "neut_seg"))

    inf = [p for p in parsed if p[1] == "infected"]
    con = [p for p in parsed if p[1] == "control"]
    floor_counts = {k: sum(1 for p in parsed if p[3].get(k) == "floor") for k in CYTOKINES}
    ceil_cells = sorted(f"{p[0]} {k}" for p in parsed for k, c in p[3].items() if c == "ceiling")
    notes += [
        f"Source: two PDF tables converted with pdftotext -layout (S1 leukocytes, S2 SAA/CRP/cytokines); page headers repeat "
        f"({h1} in S1, {h2} in S2) and were skipped. {len(order)} dogs, the same IDs in both files.",
        "Rows 'CaseN' -> group infected, timepoint admission; rows 'ControlK' -> group control, timepoint single. "
        "Blood was taken at presentation before treatment (article full text).",
        "Outcome (Survived/Died, infected only) -> outcomes file 'died'; controls have no Outcome and died = null. "
        "Original row IDs are kept only in the outcomes file.",
        "NEUT -> neut_seg: the article's Table 1 labels it the segmented neutrophil count. Band neutrophils are not in the file.",
        "Cytokine floors (record; the article sets values below the detection limit to the minimum detectable concentration): "
        "IL-2 3.4, IL-6 3.6, IL-10 8.4, IL-18 5.7, GM-CSF 9.1; flagged censored = floor. Counts at floor: "
        + ", ".join(f"{k} {v}" for k, v in floor_counts.items() if v) + ".",
        "Ceilings: Case80 has 50000.0 in IL-2, IL-6, IL-18 and GM-CSF (S-CB050 gives 50001.0 for the same cells); "
        "SAA 3001.0 in 4 infected dogs is read as an above-range code (inferred; Case44 has 3017.1, so this is uncertain and only exact 3001.0 is flagged). Kept and flagged censored = ceiling ("
        + "; ".join(ceil_cells) + ").",
        "IL-8 and MCP-1 have no documented floor; the IL-8 minimum 21.6 occurs in 3 dogs (not flagged).",
        "No sex, age, weight, band count or days sick in these files.",
        "Same dogs as S-CB050 (never pool): " + comp["link"] + " Field same_dog_as gives the S-CB050 dog_id.",
        "Comparison with S-CB050 (computed from values; it had not been made before): " + cyt_summary
        + ". Also " + oth_summary + f". Died agrees in {comp['died_agreement']['n_equal']} of {comp['died_agreement']['n_pairs']} "
        "infected dogs. Both files keep their own values; see checks file key scb050_comparison for the mismatching pairs.",
        f"FLAG WBC: S-CB517 WBC differs from S-CB050 WBC in {len(comp['wbc']['mismatches'])} linked dogs, always higher here. "
        f"In {sum(wbc_expl)} of them the S-CB050 WBC equals NEUT+LYMPH+MONO+EOS of this file plus the S-CB050 band count (within 0.25), "
        "so the S1 WBC column looks like a different (uncorrected or mis-entered) total; the published Table 1 median WBC of infected dogs "
        "(6.2) matches the S-CB050 values (median 6.22), not this file (median 6.29). Values kept as reported. Prefer S-CB050 WBC "
        "for these dogs. The FLAG lines below on differentials far below WBC are mostly the same dogs.",
        "Died includes euthanasia for poor prognosis (article full text); the label is only in the outcomes file.",
        "No value was changed.",
    ] + flags
    if unlinked:
        notes.append("Rows not linked to S-CB050 by value: " + ", ".join(ids[o] for o in unlinked))

    variables = [var(n, u, h, floor=f, ceiling=c) for h, n, u, f, c, _ in S1_COLS + S2_COLS]
    features = {
        "dataset_id": DS, "independent_source": "SRC-A", "species": "B. rossi",
        "built_from": [built_from_entry(ZIP, S1), built_from_entry(ZIP, S2)],
        "variables": variables, "records": records, "cleaning_notes": notes,
    }
    outcomes = {
        "dataset_id": DS,
        "outcomes": [{"name": "died", "definition": "Died or euthanased for poor prognosis before discharge (Outcome 'Died'); "
                      "0 = survived to discharge; null for controls. Includes euthanasia for poor prognosis (Onderstepoort, CB517 full text)",
                      "includes_euthanasia": True}],
        "records": orecs,
    }
    drows = [dict_row(n, DS, f"{'S1' if (h, n, u, f, c, note) in S1_COLS else 'S2'}: {h}", u, "", note)
             for h, n, u, f, c, note in S1_COLS + S2_COLS]

    # ---- checks (CB517 full text, Table 1 medians)
    def med(rs, k):
        return median([p[2].get(k) for p in rs])
    surv = [p for p in inf if p[4] == 0]
    dead = [p for p in inf if p[4] == 1]
    src = "CB517 full text, Table 1 median"
    checks = {"dataset_id": DS, "checks": [
        check("infected and control rows", [len(inf), len(con)], [97, 15], source="data.md; CB517: 97 infected, 15 controls"),
        check("survived and died", [len(surv), len(dead)], [85, 12], source="CB517: 85 survived, 12 died"),
        check("rows linked to S-CB050 by value", len(same_dog), 112, source="this script"),
        check("value link equals the ID-implied S-CB050 case", by_id, 112, source="this script"),
        check("median WBC, controls", med(con, "wbc"), 10.6, HALF, src),
        check("median WBC, infected", med(inf, "wbc"), 6.2, HALF, src + " (S-CB050 WBC for the same dogs gives 6.22; see cleaning_notes FLAG WBC)"),
        check("median segmented neutrophils, infected", med(inf, "neut_seg"), 4.3, HALF, src),
        check("median lymphocytes, controls", med(con, "lymph"), 2.1, HALF, src),
        check("median eosinophils, controls", med(con, "eos"), 0.7, HALF, src),
        check("median CRP, infected", med(inf, "crp"), 111.3, HALF, src),
        check("median CRP, controls", med(con, "crp"), 2.6, HALF, src),
        check("median SAA, infected", med(inf, "saa"), 933.4, HALF, src),
        check("median SAA, controls", med(con, "saa"), 14.1, HALF, src),
        check("median IL-8, infected", med(inf, "il8"), 1066.3, HALF, src),
        check("median IL-8, controls", med(con, "il8"), 3316.7, HALF, src),
        check("median IL-10, infected", med(inf, "il10"), 620.3, HALF, src),
        check("median IL-10, controls", med(con, "il10"), 44.6, HALF, src),
        check("median MCP-1, infected", med(inf, "mcp1"), 544.2, HALF, src),
        check("median MCP-1, controls", med(con, "mcp1"), 211.7, HALF, src),
        check("median IL-6, non-survivors", med(dead, "il6"), 643.9, HALF, src),
        check("median IL-6, survivors", med(surv, "il6"), 84.1, HALF, src),
    ], "n_dogs": len(records), "n_records": len(records), "floor_counts": floor_counts, "ceiling_cells": ceil_cells,
        "scb050_comparison": comp}
    # Original row IDs (CaseN, ControlK) would reveal the label through data.md's death list: use neutral IDs.
    mask_ids(features, drows, checks, re.compile(r"\b((?:Case|Control)\d+)\b"), lambda m: ids.get(m.group(1)))
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
