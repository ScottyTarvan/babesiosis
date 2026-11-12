"""Tidy DS03 (reticulocyte study, SRC-E; article CB115).

Three workbooks: natural infection (two cohorts) and healthy controls; IMHA comparators;
5 experimentally infected dogs on days 1-6. The experimental dogs are the DS02 Beagles
(matched here by value), so their records carry same_dog_as = the DS02 dog_id.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tidylib import (RAW, TIDY, built_from_entry, check, dict_row, median, neutral_ids, num, read_xlsx, var,  # noqa: E402
                     write_dataset)

DS = "DS03"
F_NAT = RAW / "DS03" / "Babesia Retics_Natural inf and cont_dissertation.xlsx"
F_IMHA = RAW / "DS03" / "Babesia Retics_IMHA_dissertation.xlsx"
F_EXP = RAW / "DS03" / "Babesia Retics_ Exp infected dissertation.xlsx"

# raw header -> (name, unit, factor, conversion, note)
COLS = {
    "Age (months)": ("age_months", "months", 1, "", ""),
    "Weight (kg)": ("weight_kg", "kg", 1, "", ""),
    "Gender": ("sex", "male/female", None, "Male -> male, Female -> female", "Neuter status not recorded."),
    "HGB (g/L)": ("hb", "g/L", 1, "", ""),
    "HCT (L/L)": ("hct", "L/L", 1, "", ""),
    "MCHC (g/L)": ("mchc", "g/L", 1, "", ""),
    "CHCM (g/L)": ("chcm", "g/L", 1, "", "ADVIA cell haemoglobin concentration mean."),
    "Ret% (%)": ("retic_pct", "%", 1, "", ""),
    "ARC (x10^9/L)": ("arc", "10^9/L", 1, "", ""),
    "MCVr (fL)": ("mcvr", "fL", 1, "", "Mean reticulocyte volume."),
    "CHCMr (g/L)": ("chcmr", "g/L", 1, "", "Reticulocyte CHCM."),
    "CHr (pg/cell)": ("chr", "pg", 1, "", "Reticulocyte haemoglobin content."),
    "CHDWr (pg/cell)": ("chdwr", "pg", 1, "", "Reticulocyte haemoglobin distribution width."),
    "RDWr (%)": ("rdwr", "%", 1, "", "Reticulocyte red cell distribution width."),
    "CHDelta (pg)": ("chdelta", "pg", 1, "", "CHr minus CH of mature red cells."),
}
# experimental file: prefix -> raw header in COLS
EXP_PREFIX = {"HGB": "HGB (g/L)", "HCT": "HCT (L/L)", "MCHC": "MCHC (g/L)", "CHCM": "CHCM (g/L)", "Ret%": "Ret% (%)",
              "ARC": "ARC (x10^9/L)", "MCVr": "MCVr (fL)", "CHCMr": "CHCMr (g/L)", "CHr": "CHr (pg/cell)",
              "CHDWr": "CHDWr (pg/cell)", "RDWr": "RDWr (%)", "CHDelta": "CHDelta (pg)"}


def convert(header, raw):
    name, unit, factor, _, _ = COLS[header]
    if name == "sex":
        t = (raw or "").strip().lower()
        return t if t in ("male", "female") else None
    v = num(raw)
    return None if v is None else round(v * factor, 10)


def table_rows(rows, header):
    """Yield (section, row) for data rows of a sheet with section label rows."""
    section = None
    for r in rows:
        if not r or all(c is None for c in r):
            continue
        first = (r[0] or "").strip()
        if first.isdigit() and len(r) > 1 and r[1]:
            yield section, r
        elif first and first != header[0]:
            section = first


def main():
    notes = []
    original = []   # (original id, group, setting, cohort, timepoint, day, values)
    nat = read_xlsx(str(F_NAT))["Sheet1"]
    hdr = nat[0]
    counts = {"cohort 1": 0, "cohort 2": 0, "control": 0, "imha": 0, "experimental": 0}
    for section, r in table_rows(nat, hdr):
        vals = {}
        for j, h in enumerate(hdr):
            if h in COLS:
                v = convert(h, r[j] if j < len(r) else None)
                if v is not None:
                    vals[COLS[h][0]] = v
        sid = r[1].strip()
        if section.startswith("Study cohort 1"):
            group, cohort = "infected", 1
            counts["cohort 1"] += 1
        elif section.startswith("Study cohort 2"):
            group, cohort = "infected", 2
            counts["cohort 2"] += 1
        elif section.startswith("Control"):
            group, cohort = "control", None
            counts["control"] += 1
        else:
            raise SystemExit(f"unknown section {section}")
        vals["setting"] = "natural" if group == "infected" else "healthy"
        if cohort:
            vals["cohort"] = cohort
        original.append((sid, group, "admission" if group == "infected" else "single", None, vals))

    imha = read_xlsx(str(F_IMHA))["Sheet1"]
    ihdr = imha[1]
    for section, r in table_rows(imha[1:], ihdr):
        vals = {}
        for j, h in enumerate(ihdr):
            if h in COLS:
                v = convert(h, r[j] if j < len(r) else None)
                if v is not None:
                    vals[COLS[h][0]] = v
        vals["setting"] = "imha"
        counts["imha"] += 1
        original.append((r[1].strip(), "comparator", "admission", None, vals))

    exp = read_xlsx(str(F_EXP))["Sheet1"]
    ehdr = exp[1]
    exp_rows = [r for r in exp[3:] if r and (r[0] or "").strip().isdigit()]
    for r in exp_rows:
        case = r[0].strip()
        counts["experimental"] += 1
        for day in range(1, 7):
            vals = {}
            for j, h in enumerate(ehdr):
                if not h or "_Day " not in h:
                    continue
                pre, d = h.split("_Day ")
                if int(d) != day:
                    continue
                v = convert(EXP_PREFIX[pre], r[j] if j < len(r) else None)
                if v is not None:
                    vals[COLS[EXP_PREFIX[pre]][0]] = v
            if vals:
                vals["setting"] = "experimental"
                original.append((f"exp case {case}", "infected", f"day_{day}", float(day), vals))

    # Link the experimental dogs to DS02 by value: ARC (a distinctive 4-digit value) must be equal on every DS03 day.
    # Then compare every shared variable and list the cells that differ.
    ds02 = json.loads((TIDY / "DS02.features.json").read_text(encoding="utf-8"))
    ds02_day = {}
    for rec in ds02["records"]:
        if rec["sample"] == "daily" and 1 <= rec["day"] <= 6:
            ds02_day[(rec["dog_id"], rec["day"])] = rec["values"]
    ds02_dogs = sorted({k[0] for k in ds02_day})
    same_dog, diffs, compared = {}, [], 0
    exp_ids = sorted({o[0] for o in original if o[0].startswith("exp case")})
    for sid in exp_ids:
        days = {o[3]: o[4] for o in original if o[0] == sid}
        cands = [dog for dog in ds02_dogs
                 if all(ds02_day.get((dog, d), {}).get("arc") == v.get("arc") for d, v in days.items())]
        if len(cands) != 1:
            continue
        dog = cands[0]
        same_dog[sid] = dog
        for d, v in days.items():
            for k in ("hb", "hct", "mchc", "retic_pct", "arc"):
                a, b = v.get(k), ds02_day.get((dog, d), {}).get(k)
                if a is None or b is None:
                    continue
                compared += 1
                if k == "retic_pct" and abs(a - b) <= 0.05 + 1e-9:
                    continue   # DS02 gives Ret% to 1 decimal, DS03 to 2
                if k == "mchc" and abs(a - b) <= 10:
                    continue   # different analyser outputs (DS02 g/dL x10); compared for gross errors only
                if a != b:
                    diffs.append(f"{dog} day {int(d)} {k}: DS03 {a}, DS02 {b}")

    ids = neutral_ids(DS, sorted({o[0] for o in original}))
    records = []
    for sid, group, tp, day, vals in original:
        rec = {"dog_id": ids[sid], "group": group, "timepoint": tp, "day": day, "values": vals, "censored": {}}
        if sid in same_dog:
            rec["same_dog_as"] = same_dog[sid]
        records.append(rec)

    imha_no_idx = sum(1 for o in original if o[2] == "admission" and o[4].get("setting") == "imha" and "mcvr" not in o[4])
    nat_missing_weight = sum(1 for o in original if o[4].get("setting") == "natural" and "weight_kg" not in o[4])
    notes += [
        "Natural-infection file: section rows 'Study cohort 1', 'Study cohort 2' and 'Control dogs' set group and cohort; "
        f"{counts['cohort 1']} + {counts['cohort 2']} infected dogs and {counts['control']} controls.",
        f"IMHA file: {counts['imha']} dogs, group 'comparator'. The article abstract says 10 IMHA dogs; "
        f"{imha_no_idx} of the {counts['imha']} have no reticulocyte indices (MCVr and later columns empty).",
        f"Experimental file: {counts['experimental']} dogs on days 1-6, long format (timepoint day_1 to day_6).",
        f"The {len(same_dog)} experimental dogs are the DS02 Beagles: ARC is equal on every DS03 day (DS03 day n = DS02 day n; "
        "the DS02 4.1 sample is left out). Field same_dog_as gives the DS02 dog_id. So DS03 'Day 1' is day 1 after inoculation, "
        "and these 5 dogs must never be pooled with DS02 as extra dogs. "
        f"Of {compared} shared cells (Hb, HCT, MCHC within 10 g/L, Ret% within 0.05, ARC), {len(diffs)} differ: "
        + ("; ".join(diffs) if diffs else "none") + ". Both values are kept as reported in their own files.",
        "values.setting: natural, healthy, imha or experimental. values.cohort: 1 or 2 for natural infection (two collection series, "
        "BC* and BLSC* IDs); null otherwise.",
        "No severity label or outcome is in any DS03 file. The outcomes file is empty by design.",
        "Units as given in the header row; MCHC is already g/L. No conversion was needed.",
        f"{nat_missing_weight} naturally infected dogs have no weight; rows with short length are padded as missing.",
        "Overlap with S-CB050 or S-CB517 (same hospital) is possible and unverified (data.md).",
        "Floating-point noise in the cells was rounded to 10 decimals.",
    ]

    used = {k for r in records for k in r["values"]}
    variables = [var(c[0], c[1], h) for h, c in COLS.items() if c[0] in used]
    variables += [var("setting", "category", "section of the source file"),
                  var("cohort", "1/2", "section row 'Study cohort 1' or 'Study cohort 2'")]
    features = {
        "dataset_id": DS, "independent_source": "SRC-E", "species": "B. rossi",
        "built_from": [built_from_entry(F_NAT), built_from_entry(F_IMHA), built_from_entry(F_EXP)],
        "variables": variables, "records": records, "cleaning_notes": notes,
    }
    outcomes = {"dataset_id": DS, "outcomes": [], "records": []}

    drows = [dict_row(c[0], DS, h, c[1], c[3], c[4]) for h, c in COLS.items() if c[0] in used]
    drows.append(dict_row("setting", DS, "file and section", "category", "", "natural, healthy, imha, experimental"))
    drows.append(dict_row("cohort", DS, "section row", "1/2", "", "Natural infection collection series."))

    # Checks
    nat_hct = [o[4].get("hct") for o in original if o[4].get("setting") == "natural"]
    con_hct = [o[4].get("hct") for o in original if o[4].get("setting") == "healthy"]
    para = {}
    for rec in ds02["records"]:
        v = rec["values"].get("parasitaemia_pct")
        if v and v > 0 and rec["dog_id"] not in para:
            para[rec["dog_id"]] = rec["day"]
    arc_drop = []
    for sid, dog in same_dog.items():
        series = {o[3]: o[4].get("arc") for o in original if o[0] == sid}
        d0 = para.get(dog)
        # ARC 2 to 3 days after first parasitaemia falls below 60% of its value on the day of detection or the day after
        early = [series.get(d0), series.get(d0 + 1)] if d0 is not None else []
        late = [series.get(d0 + 2), series.get(d0 + 3)] if d0 is not None else []
        early = [x for x in early if x is not None]
        late = [x for x in late if x is not None]
        if early and late:
            arc_drop.append(min(late) < 0.6 * max(early))
    checks = {"dataset_id": DS, "checks": [
        check("naturally infected dogs (cohort 1 + cohort 2)", [counts["cohort 1"], counts["cohort 2"]], [85, 18],
              source="data.md; CB115 note: 103 naturally infected"),
        check("healthy controls", counts["control"], 14, source="CB115 note: 14 healthy controls"),
        check("IMHA dogs in the file", counts["imha"], 16, source="data.md (the article reports 10)"),
        check("experimental dogs", counts["experimental"], 5, source="CB115 note: five experimentally infected dogs"),
        check("median haematocrit lower in natural B. rossi than in controls",
              [median(nat_hct), median(con_hct), median(nat_hct) < median(con_hct)], [None, None, True],
              source="CB115 note: haematocrit low in B. rossi relative to controls (p < .001)") | {
            "pass": median(nat_hct) < median(con_hct)},
        check("ARC 2-3 days after parasitaemia is detected falls below 60% of its value on days 0-1 of detection, in every experimental dog",
              [len(arc_drop), all(arc_drop)], [5, True],
              source="CB115 note: ARC dropped abruptly about 48 h after parasitaemia was detected"),
        check("experimental dogs linked to DS02 by value", len(same_dog), 5, source="this script"),
    ], "n_dogs": len({r['dog_id'] for r in records}), "n_records": len(records), "same_dog_as": same_dog, "ds02_cell_differences": diffs}
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
