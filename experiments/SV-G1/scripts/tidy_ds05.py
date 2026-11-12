"""Tidy DS05 (BET study, 150 dogs with natural babesiosis, Eastern Cape 2021; SRC-F; article CB126).

Features: 'Entire population' sheet. Outcomes (severity proxies): habitus grade and the authors'
derived classes from the 'CORRESPONDENCE' sheet. The 'Crossbreed vs Purebreed' sheet repeats the same dogs.
"""
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tidylib import (RAW, built_from_entry, check, dict_row, median, neutral_ids, num, quantile, read_xlsx, var,  # noqa: E402
                     write_dataset)

DS = "DS05"
SRC = RAW / "DS05" / "BET Study Dataset.xlsx"

# column index -> (name, unit, kind, factor, conversion, note); kind n = number, t = text, special handled below
COLS = {
    3: ("age_months", "months", "n", 1, "", ""),
    4: ("weight_kg", "kg", "n", 1, "", ""),
    5: ("complaint_codes", "text", "t", None, "", "Owner complaint codes as recorded, separated by '/' (IA inappetance, L lethargy, HgUr haemoglobinuria, WL weight loss, V vomiting, D diarrhoea)."),
    6: ("illness_days", "days", "n", 1, "", "Owner-reported. 'UNKNOWN' (2 dogs) stored as null."),
    7: ("temp_c", "degC", "n", 1, "", ""),
    8: ("heart_rate", "beats/min", "n", 1, "", "Pulse rate."),
    9: ("resp_rate", "breaths/min", "n", 1, "", "'P+' (panting) stored as null; see panting."),
    10: ("mucous_membranes", "text", "t", None, "", "Free text as recorded."),
    11: ("lymph_node_score", "score 0-2", "n", 1, "", "0 none palpable, 1 one to three nodes palpable, 2 more than three nodes palpable (summary rows of the sheet)."),
    12: ("ticks", "0/1", "n", 1, "", "1 present, 0 absent."),
    13: ("hb", "g/L", "n", 1, "", ""),
    14: ("rbc", "10^12/L", "n", 1, "", ""),
    15: ("hct", "L/L", "n", 1, "", ""),
    16: ("mcv", "fL", "n", 1, "", ""),
    17: ("mch", "pg", "n", 1, "", ""),
    18: ("mchc", "g/L", "n", 10, "x10 (g/dL to g/L)", "The units row gives g/dL."),
    19: ("rdw", "%", "n", 1, "", "RCDW in the file."),
    20: ("wbc", "10^9/L", "n", 1, "", ""),
    21: ("neut_seg", "10^9/L", "n", 1, "", ""),
    22: ("neut_band", "10^9/L", "n", 1, "", ""),
    23: ("lymph", "10^9/L", "n", 1, "", ""),
    24: ("mono", "10^9/L", "n", 1, "", ""),
    25: ("eos", "10^9/L", "n", 1, "", ""),
    26: ("baso", "10^9/L", "n", 1, "", ""),
    27: ("other_cells", "10^9/L", "n", 1, "", "'Other' cells in the differential."),
    28: ("plt", "10^9/L", "n", 1, "", ""),
    29: ("nrbc_per100wbc", "per 100 WBC", "n", 1, "", ""),
    30: ("retic_pct", "%", "n", 1, "", ""),
    31: ("arc", "10^9/L", "n", 1, "", ""),
    32: ("tsp", "g/L", "n", 1, "", "Total serum protein."),
    33: ("albumin", "g/L", "n", 1, "", ""),
    34: ("globulin", "g/L", "n", 1, "", "Calculated by the authors (total protein - albumin)."),
    35: ("pcr_b_rossi", "0/1", "n", 1, "", "qPCR result."),
    36: ("pcr_b_vogeli", "0/1", "n", 1, "", "qPCR result."),
    37: ("pcr_e_canis", "0/1", "n", 1, "", "qPCR result."),
    38: ("pcr_t_equi", "0/1", "n", 1, "", "qPCR result."),
    39: ("date_collected", "date", "t", None, "DD/MM/YYYY -> YYYY-MM-DD", ""),
    40: ("season", "text", "t", None, "Su/Au/Wi/Sp -> summer/autumn/winter/spring", "Southern-hemisphere season, as coded by the authors."),
}
SEASONS = {"Su": "summer", "Au": "autumn", "Wi": "winter", "Sp": "spring"}
# CORRESPONDENCE sheet: column -> (outcome name, definition)
CORR = {
    13: ("habitus_score", "Admission mental status (habitus) graded by the authors: 4 bright, alert and responsive; 3 mildly depressed; "
                          "2 and 1 severely depressed; 0 = 'COLLAPSED' in the file (coded 0 here; the authors class it with <2+). Higher is brighter"),
    14: ("habitus_class", "Authors' habitus class: BAR (4+), Mi_De (3+), De_Co (2+ or less, or collapsed)"),
    16: ("anaemia_class", "Authors' anaemia grade from haematocrit: Ht_N, Ht_Mi, Ht_Mo, Ht_S, Ht_VS"),
    18: ("wcc_class", "Authors' white cell class: WCC_Lo (<6), WCC_N, WCC_Hi (>15 x10^9/L)"),
    20: ("band_class", "Authors' band neutrophil class: BaN_N (0-0.5), BaN_H (>0.5 x10^9/L)"),
    22: ("left_shift_class", "Authors' left shift class: L_shft (bands > 0.5), De_L_shift (bands > segmented); empty = none"),
    24: ("monocyte_class", "Authors' monocyte class: Mon_N, Mon_Hi (>1.35 x10^9/L)"),
    26: ("arc_class", "Authors' reticulocyte class: ARC_In (<80), ARC_Mi, ARC_Mo, ARC_Ma (>300 x10^9/L)"),
    28: ("arc_class_2", "Authors' second reticulocyte class: ARC_Lo (<12.86), ARC_N, ARC_Hi (>115.41 x10^9/L)"),
    30: ("globulin_class", "Authors' globulin class: Glo_Lo (<20), Glo_N, Glo_Hi (>41 g/L)"),
    12: ("illness_class", "Authors' illness duration class: DI_1 1-3 days, DI_2 4-6, DI_3 more than 7"),
}
ID_RE = re.compile(r"^(BET\d{3})")


def main():
    wb = read_xlsx(str(SRC))
    main_rows = wb["Entire population"]
    notes = []
    data = []
    for r in main_rows[2:]:
        if not r or not r[0]:
            break          # stop at the first blank ID
        data.append(r)
    annotated = [r[0] for r in data if r[0].strip() != ID_RE.match(r[0]).group(1)]
    ids_orig = [ID_RE.match(r[0]).group(1) for r in data]
    ids = neutral_ids(DS, ids_orig)

    records = []
    raw_by_id = {}
    for r, oid in zip(data, ids_orig):
        vals = {}
        cell = lambda j: (r[j].strip() if j < len(r) and r[j] is not None else None)  # noqa: E731
        sx = (cell(1) or "").upper()
        vals["sex"] = "male" if sx.startswith("MALE") else ("female" if sx.startswith("FEMALE") else None)
        vals["neuter"] = ("neutered" if ("SPAYED" in sx or "CASTRATED" in sx) else "intact") if sx else None
        vals["breed"] = (cell(2) or "").title() or None
        for j, (name, unit, kind, factor, _, _) in COLS.items():
            c = cell(j)
            if kind == "n":
                v = num(c)
                vals[name] = None if v is None else round(v * factor, 10)
            elif name == "date_collected":
                m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", c or "")
                vals[name] = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))).isoformat() if m else None
            elif name == "season":
                vals[name] = SEASONS.get(c, c)
            else:
                vals[name] = c or None
        vals["panting"] = 1 if (cell(9) or "").upper().startswith("P") else 0
        vals = {k: v for k, v in vals.items() if v is not None}
        raw_by_id[oid] = r
        records.append({"dog_id": ids[oid], "group": "infected", "timepoint": "admission", "day": None,
                        "values": vals, "censored": {}})

    # Outcomes from the CORRESPONDENCE sheet
    corr = {}
    for r in wb["CORRESPONDENCE"]:
        if r and r[0] and ID_RE.match(str(r[0]).strip()):
            corr[ID_RE.match(r[0].strip()).group(1)] = r
    orecs = []
    hct_mismatch = 0
    collapsed = 0
    for oid in ids_orig:
        r = corr.get(oid)
        vals = {}
        if r is not None:
            for j, (name, _) in CORR.items():
                c = r[j].strip() if j < len(r) and r[j] else None
                if name == "habitus_score":
                    if c and c.upper() == "COLLAPSED":
                        vals[name] = 0
                        collapsed += 1
                    else:
                        m = re.match(r"^(\d)\+?$", c or "")
                        vals[name] = int(m.group(1)) if m else None
                    vals["habitus_raw"] = c
                elif name == "left_shift_class":
                    vals[name] = c or "none"
                else:
                    vals[name] = c
            a, b = num(r[15] if len(r) > 15 else None), num(raw_by_id[oid][15])
            if a is not None and b is not None and abs(a - b) > 1e-9:
                hct_mismatch += 1
        orecs.append({"dog_id": ids[oid], "original_id": oid, "values": vals})
    outcome_defs = [{"name": n, "definition": d, "includes_euthanasia": False} for _, (n, d) in sorted(CORR.items(), key=lambda x: x[0])]
    outcome_defs.insert(1, {"name": "habitus_raw", "definition": "Habitus cell as written in the file (1+ to 4+ or COLLAPSED)",
                            "includes_euthanasia": False})
    outcomes = {"dataset_id": DS, "outcomes": outcome_defs, "records": orecs}

    no_cbc = [o for o, rec in zip(ids_orig, records) if "hb" not in rec["values"]]
    panting = sum(r["values"]["panting"] for r in records)
    rcc_flag = raw_by_id.get("BET048")
    notes += [
        f"'Entire population' sheet: header row 1, units row 2, {len(data)} dog rows; reading stops at the first blank ID. "
        "The authors' summary rows below the data (medians with ranges, counts) were not read as data; they are used as checks.",
        "IDs with a note in the cell were cut to the ID: " + "; ".join(annotated) + ". The notes give the infection (also in the PCR columns).",
        f"{len(no_cbc)} dogs have no CBC or biochemistry (BET065 and BET066 in the file).",
        f"Respiratory rate 'P+' (panting, {panting} dogs) is null in resp_rate and 1 in panting.",
        "Duration of illness 'UNKNOWN' is null.",
        "sex and neuter split from the SEX column (MALE INTACT, FEMALE SPAYED, ...).",
        "MCHC converted from g/dL to g/L (x10).",
        "FLAG (kept as reported): one dog (BET048 in the file) has red cell count 7.89 x10^12/L, the same number as its WCC, while its "
        f"haematocrit is {num(rcc_flag[15])} L/L and MCV {num(rcc_flag[16])} fL (HCT/MCV gives about "
        f"{round(num(rcc_flag[15]) / num(rcc_flag[16]) * 1000, 2)} x10^12/L). Probable entry error in rbc.",
        "FLAG (kept as reported): one dog (BET021 in the file) has globulin 1 g/L while total protein minus albumin is "
        f"{round(num(raw_by_id['BET021'][32]) - num(raw_by_id['BET021'][33]), 1)} g/L. Probable entry error in globulin.",
        "The habitus grade and the authors' derived classes (anaemia, WCC, bands, left shift, monocytes, ARC, globulin, illness "
        "duration) are in the outcomes file only: earlier work used them as severity proxies. "
        f"Habitus 'COLLAPSED' ({collapsed} dogs) is coded 0 in habitus_score; habitus_raw keeps the text.",
        f"Haematocrit agrees between the two sheets for all dogs except {hct_mismatch}.",
        "One dog is B. vogeli only (pcr_b_vogeli = 1, pcr_b_rossi = 0); 3 dogs are B. rossi + E. canis. They stay in the file with "
        "group 'infected'; filter on the PCR columns.",
        "The old DS05 tidy file (git 8d4c6d9) was used as a reference for column meanings only.",
        "Floating-point noise in the cells was rounded to 10 decimals.",
    ]

    variables = [var("sex", "male/female", "SEX"), var("neuter", "intact/neutered", "SEX"), var("breed", "text", "BREED")]
    header = main_rows[0]
    units = main_rows[1]
    for j, (name, unit, kind, _, _, _) in COLS.items():
        orig = (header[j] or "").strip() + (f" {units[j].strip()}" if j < len(units) and units[j] else "")
        variables.append(var(name, unit, orig))
    variables.append(var("panting", "0/1", "RESP = 'P+'"))
    features = {
        "dataset_id": DS, "independent_source": "SRC-F", "species": "B. rossi",
        "built_from": [built_from_entry(SRC)], "variables": variables, "records": records, "cleaning_notes": notes,
    }

    drows = [dict_row("sex", DS, "SEX", "male/female", "MALE ... -> male, FEMALE ... -> female", ""),
             dict_row("neuter", DS, "SEX", "intact/neutered", "SPAYED or CASTRATED -> neutered", ""),
             dict_row("breed", DS, "BREED", "text", "title case", "")]
    for j, (name, unit, kind, _, conv, note) in COLS.items():
        drows.append(dict_row(name, DS, (header[j] or "").strip(), unit, conv, note))
    drows.append(dict_row("panting", DS, "RESP", "0/1", "'P+' -> 1", ""))

    # Checks against the authors' summary row (median (IQR)) and the article note
    def col(name):
        return [r["values"].get(name) for r in records]
    summary = main_rows[153]
    def pub_median(j):
        return num(summary[j].split("(")[0]) if j < len(summary) and summary[j] else None
    checks_list = [
        check("dogs", len(records), 150, source="data.md; CB126 note: 150 dogs"),
        check("B. rossi qPCR positive", sum(1 for v in col("pcr_b_rossi") if v == 1), 149, source="CB126 note: B. rossi 149"),
        check("B. vogeli qPCR positive", sum(1 for v in col("pcr_b_vogeli") if v == 1), 1, source="CB126 note: B. vogeli 1"),
        check("E. canis co-infection", sum(1 for v in col("pcr_e_canis") if v == 1), 3, source="CB126 note: 3 dogs (2.0%) E. canis"),
        check("T. equi", sum(1 for v in col("pcr_t_equi") if v == 1), 0, source="CB126 note: no Theileria"),
        check("male intact", sum(1 for r in records if r["values"].get("sex") == "male" and r["values"].get("neuter") == "intact"),
              82, source="authors' summary row of the sheet: 82/150 MALE INTACT"),
    ]
    for j, name in [(3, "age_months"), (13, "hb"), (15, "hct"), (31, "arc"), (33, "albumin")]:
        checks_list.append(check(f"median {name}", median(col(name)), pub_median(j), tol=1e-6,
                                 source=f"authors' summary row of the sheet: '{summary[j]}'"))
    checks_list.append(check("ARC quartiles (type 6, as Excel QUARTILE.EXC) vs the summary row",
                             [round(quantile(col('arc'), .25, 6), 2), round(quantile(col('arc'), .75, 6), 2)],
                             [52.38, 174.28], source="authors' summary row: '102,05 (52,38 - 174,28)'") )
    checks = {"dataset_id": DS, "checks": checks_list, "n_dogs": len(records), "n_records": len(records)}
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
