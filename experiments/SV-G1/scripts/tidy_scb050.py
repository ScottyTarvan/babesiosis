"""Tidy S-CB050 (MPXI study, SRC-A, Onderstepoort; article CB050).

One Word table (Supplementary Table 1): one row per dog, 141 infected and 20 controls. Two pooled
cohorts: cases 1-97 and controls 201-215 (Oct 2011 - Apr 2013, cytokines measured) and cases 101-144
and controls 216-220 (2014, no cytokines). Outcome (died) goes to the outcomes file only.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tidylib import (RAW, built_from_entry, check, dict_row, median, neutral_ids, num, quantile, read_docx_tables,  # noqa: E402
                     var, write_dataset, zip_member, mask_ids)

DS = "S-CB050"
ZIP = RAW / "S-CB050" / "PMC7040022_supplementaryFiles.zip"
MEMBER = "Table_1.DOCX"

# raw header -> (name, unit, floor, ceiling, conversion, note)
COLS = {
    "Age (mos)": ("age_months", "months", None, None, "", ""),
    "Weight (kg)": ("weight_kg", "kg", None, None, "", ""),
    "WBC (x10^9/L)": ("wbc", "10^9/L", None, None, "", "ADVIA 2120."),
    "Neut Seg (x10^9/L)": ("neut_seg", "10^9/L", None, None, "", ""),
    "Neut Band (x10^9/L)": ("neut_band", "10^9/L", None, None, "", ""),
    "IL-2 (pg/mL)": ("il2", "pg/mL", 3.4, 50001.0, "", "Floor 3.4 per record; 50001 in case 80 read as the upper limit."),
    "IL-6 (pg/mL)": ("il6", "pg/mL", 3.6, 50001.0, "", "Floor 3.6 per record; 50001 in case 80 read as the upper limit."),
    "IL-8 (pg/mL)": ("il8", "pg/mL", None, None, "", "No floor documented. The minimum 21.6 occurs in 3 dogs; not flagged."),
    "IL-10 (pg/mL)": ("il10", "pg/mL", 8.4, None, "", "Floor 8.4 per record."),
    "IL-18 (pg/mL)": ("il18", "pg/mL", 5.7, 50001.0, "", "Floor 5.7 per record; 50001 in case 80 read as the upper limit."),
    "GM-CSF (pg/mL)": ("gmcsf", "pg/mL", 9.1, 50001.0, "", "Floor 9.1 per record; 50001 in case 80 read as the upper limit."),
    "MCP-1 (pg/mL)": ("mcp1", "pg/mL", None, None, "", "No floor documented."),
    "MPXI": ("mpxi", "index", None, None, "", "ADVIA neutrophil myeloperoxidase index (unitless)."),
}
HALF = 0.05 + 1e-9   # published values are rounded to 1 decimal
CYTOKINES = ["il2", "il6", "il8", "il10", "il18", "gmcsf", "mcp1"]


def cohort_of(case):
    return 1 if (1 <= case <= 97 or 201 <= case <= 215) else 2


def spearman(xs, ys):
    """Spearman rho (average ranks for ties), standard library only."""
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None, len(pairs)

    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    rx, ry = ranks([p[0] for p in pairs]), ranks([p[1] for p in pairs])
    n = len(pairs)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / (sxx * syy) ** 0.5, n


def main():
    notes = []
    tables = read_docx_tables(zip_member(ZIP, MEMBER))
    if len(tables) != 1:
        raise SystemExit(f"expected 1 table, found {len(tables)}")
    hdr = [h.strip() for h in tables[0][0]]
    rows = [r for r in tables[0][1:] if r and (r[0] or "").strip()]
    col = {h: j for j, h in enumerate(hdr)}
    expected_hdr = ["Case", "Age (mos)", "Weight (kg)", "Gender", "Status", "Outcome"] + list(COLS)[2:]
    if hdr != expected_hdr:
        raise SystemExit(f"unexpected header: {hdr}")

    parsed = []   # (case, group, vals, censored, died)
    flags = []
    for r in rows:
        cell = lambda h: (r[col[h]] or "").strip() if col[h] < len(r) else ""  # noqa: E731
        case = int(cell("Case"))
        status = cell("Status").lower()
        group = {"infected": "infected", "control": "control"}[status]
        outcome = cell("Outcome").lower()
        died = {"died": 1, "survived": 0, "control": None}[outcome]
        if (group == "control") != (outcome == "control"):
            flags.append(f"FLAG case {case}: Status {cell('Status')} with Outcome {cell('Outcome')}")
        vals, cens = {}, {}
        g = cell("Gender").lower()
        if g in ("male", "female"):
            vals["sex"] = g
        elif g:
            flags.append(f"FLAG case {case}: Gender '{cell('Gender')}' not read")
        for h, (name, unit, floor, ceiling, _, _) in COLS.items():
            v = num(cell(h))
            if v is None:
                continue
            vals[name] = v
            if ceiling is not None and v == ceiling:   # only the exact code value
                cens[name] = "ceiling"
            elif floor is not None and v <= floor:
                cens[name] = "floor"
                if v < floor:
                    flags.append(f"FLAG case {case}: {name} {v} is below the documented floor {floor}; kept")
        vals["cohort"] = cohort_of(case)
        parsed.append((case, group, vals, cens, died))

    ids = neutral_ids(DS, [str(p[0]) for p in parsed])
    records, orecs = [], []
    for case, group, vals, cens, died in parsed:
        did = ids[str(case)]
        records.append({"dog_id": did, "group": group, "timepoint": "admission" if group == "infected" else "single",
                        "day": None, "values": vals, "censored": cens})
        orecs.append({"dog_id": did, "original_id": str(case), "timepoint": None, "day": None, "values": {"died": died}})

    inf = [p for p in parsed if p[1] == "infected"]
    con = [p for p in parsed if p[1] == "control"]
    c1_inf = [p for p in inf if p[2]["cohort"] == 1]
    c1_con = [p for p in con if p[2]["cohort"] == 1]
    with_cyt = [p for p in parsed if any(k in p[2] for k in CYTOKINES)]
    ceil_cells = sorted(f"case {p[0]} {k}" for p in parsed for k, c in p[3].items() if c == "ceiling")
    floor_counts = {k: sum(1 for p in parsed if p[3].get(k) == "floor") for k in CYTOKINES}
    miss = {k: sum(1 for p in parsed if k not in p[2]) for k in ("age_months", "weight_kg", "mpxi")}
    missing_mpxi = [p[0] for p in parsed if "mpxi" not in p[2]]
    missing_age = [p[0] for p in parsed if "age_months" not in p[2]]

    notes += [
        f"Source: one Word table, {len(rows)} data rows; decimal commas read as decimal points.",
        "Status -> group (Infected -> infected, Control -> control). Outcome (Survived/Died) -> outcomes file 'died'; "
        "controls have Outcome 'Control' and died = null.",
        "Original case numbers are kept only in the outcomes file (original_id); dog_id is neutral.",
        "Gender holds only Male or Female: sex is recorded, neuter status is not in the file (no neuter variable).",
        "values.cohort: 1 for cases 1-97 and controls 201-215 (Oct 2011 - Apr 2013, cytokines measured); "
        "2 for cases 101-144 and controls 216-220 (2014, no cytokine columns). Cohort is confounded with assay availability and year.",
        f"Cohort 1 has {len(c1_inf)} infected dogs in the file; the article reports 96. The article reports 140 infected in total; "
        f"the file has {len(inf)}. Case {', '.join(map(str, missing_mpxi))} has no MPXI, which may explain the published n of 140/96 "
        "for MPXI analyses (inferred, not stated).",
        "Cytokine floors (record; the article sets values below the detection limit to the minimum detectable concentration): "
        "IL-2 3.4, IL-6 3.6, IL-10 8.4, IL-18 5.7, GM-CSF 9.1. Values equal to the floor are flagged censored = floor. "
        "Counts at floor: " + ", ".join(f"{k} {v}" for k, v in floor_counts.items() if v) + ".",
        "Ceiling: case 80 has 50001.0 in IL-2, IL-6, IL-18 and GM-CSF, read as an above-range code; kept as 50001.0 and flagged "
        "censored = ceiling (" + "; ".join(ceil_cells) + "). S-CB517 gives the same cells as 50000.0.",
        "IL-8 and MCP-1 have no documented floor; IL-8 has its minimum 21.6 in 3 dogs, which may be an undocumented floor (not flagged).",
        f"Missing (null): age in case {', '.join(map(str, missing_age))}; weight in {miss['weight_kg']} dogs; MPXI in case "
        f"{', '.join(map(str, missing_mpxi))}; all 7 cytokines in cohort 2 ({len(parsed) - len(with_cyt)} dogs).",
        "Blood was taken at presentation before treatment (article full text). Infected: timepoint admission; controls: single.",
        "Never pool with S-CB517 (same dogs: cases 1-97 and controls 201-215) or with DS04 (at least 3 shared dogs, data.md).",
        "Died includes euthanasia for poor prognosis (article full text); the label is only in the outcomes file.",
        "No value was changed. Floating-point noise was rounded to 10 decimals.",
    ] + flags

    variables = [var("sex", "male/female", "Gender")]
    variables += [var(n, u, h, floor=f, ceiling=c) for h, (n, u, f, c, _, _) in COLS.items()]
    variables.append(var("cohort", "1/2", "derived from Case number (package step 4)"))
    features = {
        "dataset_id": DS, "independent_source": "SRC-A", "species": "B. rossi",
        "built_from": [built_from_entry(ZIP, MEMBER)],
        "variables": variables, "records": records, "cleaning_notes": notes,
    }
    outcomes = {
        "dataset_id": DS,
        "outcomes": [{"name": "died", "definition": "Died or euthanased for poor prognosis (Outcome 'Died'); 0 = survived "
                      "(Outcome 'Survived'); null for controls. Includes euthanasia for poor prognosis (Onderstepoort, CB050 full text)",
                      "includes_euthanasia": True}],
        "records": orecs,
    }

    drows = [dict_row("sex", DS, "Gender", "male/female", "Male -> male, Female -> female", "Neuter status not recorded.")]
    drows += [dict_row(n, DS, h, u, conv, note) for h, (n, u, f, c, conv, note) in COLS.items()]
    drows.append(dict_row("cohort", DS, "Case", "1/2", "cases 1-97, 201-215 -> 1; cases 101-144, 216-220 -> 2",
                          "Collection series; cytokines only in cohort 1."))

    # ---- checks
    def vals_of(group_rows, k):
        return [p[2].get(k) for p in group_rows]
    surv = [p for p in inf if p[4] == 0]
    dead = [p for p in inf if p[4] == 1]
    sexes = lambda rs: [sum(1 for p in rs if p[2].get("sex") == "male"), sum(1 for p in rs if p[2].get("sex") == "female")]  # noqa: E731
    inf_mpxi = [p for p in inf if "mpxi" in p[2]]
    rho_il8, n_il8 = spearman(vals_of(inf_mpxi, "mpxi"), vals_of(inf_mpxi, "il8"))
    rho_il10, n_il10 = spearman(vals_of(inf_mpxi, "mpxi"), vals_of(inf_mpxi, "il10"))
    r1 = lambda x: None if x is None else round(x, 3)  # noqa: E731
    src = "CB050 full text (Results)"
    checks = {"dataset_id": DS, "checks": [
        check("data rows", len(rows), 161, source="data.md"),
        check("infected dogs", len(inf), 141, source="data.md (article reports 140)"),
        check("deaths among infected", len(dead), 15, source="data.md; CB050: 15 died"),
        check("controls", len(con), 20, source="data.md; CB050: 20 controls"),
        check("dogs with cytokines: infected, infected died, controls",
              [sum(1 for p in with_cyt if p[1] == "infected"), sum(1 for p in with_cyt if p[4] == 1),
               sum(1 for p in with_cyt if p[1] == "control")], [97, 12, 15], source="data.md"),
        check("cohort 1 infected and controls", [len(c1_inf), len(c1_con)], [97, 15],
              source="data.md (article: 96 + 15)"),
        check("case 80 ceiling cells", len(ceil_cells), 4, source="record: 50001 ceiling in case 80"),
        check("median MPXI, infected", median(vals_of(inf, "mpxi")), 19.2, HALF, src + ": 19.2 (IQR 14.9-22.8)"),
        check("median MPXI, controls", median(vals_of(con, "mpxi")), 16.8, HALF, src + ": 16.8 (IQR 12.8-19.7)"),
        check("median MPXI, non-survivors", median(vals_of(dead, "mpxi")), 22.8, HALF, src + ": 22.8 (IQR 17.7-26.1)"),
        check("median MPXI, survivors", median(vals_of(surv, "mpxi")), 19.0, HALF, src + ": 19.0 (IQR 14.7-21.8)"),
        check("MPXI quartiles, infected (type 6)", [r1(quantile(vals_of(inf, "mpxi"), .25, 6)), r1(quantile(vals_of(inf, "mpxi"), .75, 6))],
              [14.9, 22.8], source=src) | {"pass": abs(quantile(vals_of(inf, "mpxi"), .25, 6) - 14.9) <= 0.05
                                          and abs(quantile(vals_of(inf, "mpxi"), .75, 6) - 22.8) <= 0.05},
        check("median segmented neutrophils, controls", median(vals_of(con, "neut_seg")), 5.8, HALF, src + ": 5.8"),
        check("median segmented neutrophils, infected", median(vals_of(inf, "neut_seg")), 4.0, HALF, src + ": 4.0"),
        check("median band neutrophils, non-survivors", median(vals_of(dead, "neut_band")), 1.0, HALF, src + ": 1.0"),
        check("median age, infected (months)", median(vals_of(inf, "age_months")), 20, 0.5, src + ": 20"),
        check("median age, controls (months)", median(vals_of(con, "age_months")), 46, 0.5, src + ": 46"),
        check("male:female, controls", sexes(con), [7, 13], source=src),
        check("male:female, non-survivors", sexes(dead), [10, 5], source=src),
        check("male:female, survivors", sexes(surv), [82, 43], source=src + " (125 survivors; the file has one more)"),
        check("Spearman MPXI vs IL-8, infected", r1(rho_il8), -0.350, 0.005, src + f": r = -0.350 (n here {n_il8})"),
        check("Spearman MPXI vs IL-10, infected", r1(rho_il10), 0.211, 0.005, src + f": r = 0.211 (n here {n_il10})"),
    ], "n_dogs": len(records), "n_records": len(records), "floor_counts": floor_counts, "ceiling_cells": ceil_cells}
    # Original case numbers would reveal the label through data.md's death list: name single dogs by neutral ID.
    case_re = re.compile(r"\b[Cc]ases? (\d+)\b(?!\s*(?:-|to)\s*\d)")
    mask_ids(features, drows, checks, case_re,
             lambda m: ("dog " + ids[m.group(1)]) if m.group(1) in ids else None)
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
