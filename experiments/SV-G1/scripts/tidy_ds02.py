"""Tidy DS02 (experimental B. rossi infection of 5 Beagles, SRC-B; articles CB098, CB101).

Long format: one record per dog and sampling day. Dog 1 (splenectomised donor) is excluded.
DS01 repeats DS02 (same dogs) and gets no tidy file of its own.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collections import defaultdict

from tidylib import (RAW, built_from_entry, check, dict_row, neutral_ids, num, read_xlsx, var, write_dataset)

DS = "DS02"
SRC = RAW / "DS02" / "B.Atkinson_Experimental Babesia study raw data.xlsx"

# (sheet, raw prefix, name, unit, conversion factor, conversion text, note)
SPEC = [
    ("Clinical", "T", "temp_c", "degC", 1, "", "Rectal temperature."),
    ("Clinical", "P", "heart_rate", "beats/min", 1, "", "Pulse rate (CB101 supplementary table: pulse in bpm)."),
    ("Clinical", "RR", "resp_rate", "breaths/min", 1, "", ""),
    ("Clinical", "MM", "mm_colour", "code", 1, "", "Notes sheet: 1 pale, 2 icteric, 3 normal, 4 congested."),
    ("Clinical", "CRT", "crt", "s", 1, "", "Capillary refill time; unit not given in the file (assumed seconds)."),
    ("Clinical", "FP", "femoral_pulse", "code", 1, "", "Notes sheet: 1 absent, 2 weak, 3 strong."),
    ("Clinical", "AP", "appetite_score", "score 1-4", 1, "", "Scale 1-4 per the DS01 supplementary table; direction not defined in the file."),
    ("Clinical", "FC", "faecal_code", "code", 1, "", "Notes sheet: 1 diarrhoea, 2 normal, 3 firm."),
    ("Clinical", "BP(SYS)", "bp_sys", "mmHg", 1, "", ""),
    ("Clinical", "BP(DIAS)", "bp_dia", "mmHg", 1, "", ""),
    ("Clinical", "BP(MAP)", "bp_map", "mmHg", 1, "", ""),
    ("Clinical", "GLC", "glucose", "mmol/L", 1, "", "Unit not given in the file; values 5-9 fit mmol/L."),
    ("Clinical", "LAC", "lactate_clinical", "mmol/L", 1, "",
     "Lactate on the Clinical sheet (probably a hand-held meter). The harmonised 'lactate' is the venous blood gas value."),
    ("Haematology", "Hb", "hb", "g/L", 1, "", ""),
    ("Haematology", "RCC", "rbc", "10^12/L", 1, "", ""),
    ("Haematology", "HT", "hct", "L/L", 1, "", ""),
    ("Haematology", "MCV", "mcv", "fL", 1, "", ""),
    ("Haematology", "MCH", "mch", "pg", 1, "", ""),
    ("Haematology", "MCHC", "mchc", "g/L", 10, "x10 (g/dL to g/L)", "Raw values about 33 are g/dL."),
    ("Haematology", "RDW", "rdw", "%", 1, "", ""),
    ("Haematology", "WCC", "wbc", "10^9/L", 1, "", ""),
    ("Haematology", "SNeut", "neut_seg", "10^9/L", 1, "", ""),
    ("Haematology", "BNeut", "neut_band", "10^9/L", 1, "", ""),
    ("Haematology", "Lymph", "lymph", "10^9/L", 1, "", ""),
    ("Haematology", "Mono", "mono", "10^9/L", 1, "", ""),
    ("Haematology", "Eos", "eos", "10^9/L", 1, "", ""),
    ("Haematology", "Baso", "baso", "10^9/L", 1, "", ""),
    ("Haematology", "Plt", "plt", "10^9/L", 1, "", ""),
    ("Haematology", "NRBC/100WBC", "nrbc_per100wbc", "per 100 WBC", 1, "", ""),
    ("Haematology", "Retic%", "retic_pct", "%", 1, "", "Days 1-8 only."),
    ("Haematology", "Retic", "arc", "10^9/L", 1, "",
     "Absolute reticulocyte count; unit not given in the file. The values equal the ARC (x10^9/L) of the same dogs in DS03."),
    ("Biochemistry", "CRP", "crp", "mg/L", 1, "", "Unit not given in the file (mg/L assumed). 10 is the reporting floor."),
    ("Biochemistry", "ALB", "albumin", "g/L", 1, "", ""),
    ("Venous blood gas", "Lac", "lactate", "mmol/L", 1, "", "Venous blood gas lactate, days 1-8."),
    ("Cytokines", "GM-CSF", "gmcsf", "pg/mL", 1, "", "Milliplex canine panel; unit pg/mL per CB098 (not in the file). 0 = below detection."),
    ("Cytokines", "INFg", "ifng", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "KC", "kc", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IP10", "ip10", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IL2", "il2", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IL6", "il6", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IL7", "il7", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IL8", "il8", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IL10", "il10", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IL15", "il15", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "IL18", "il18", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "MCP1", "mcp1", "pg/mL", 1, "", "0 = below detection."),
    ("Cytokines", "TNFa", "tnfa", "pg/mL", 1, "", "0 = below detection."),
    ("Parasitaemias", "D", "parasitaemia_pct", "%", 1, "", "Unit not given in the file (% parasitised red cells assumed)."),
    ("Iron", "CFHb", "cfhb", "mg/L", 1, "", "Cell-free haemoglobin; unit not given in the file (mg/L is an assumption)."),
]
CYTOKINES = {s[2] for s in SPEC if s[0] == "Cytokines"}
DAYS = ["-1", "0", "1", "2", "3", "4", "4.1", "5", "6", "7", "8"]
# Treatment with diminazene at about 96 h (high dose) and 108 h (low dose), per the DS02 record (CB101).
# Day 4 is 96 h. The 4.1 sample exists only for the low-dose dogs and is read as the ~108 h pre-treatment sample.


def parse_header(h):
    """'IL2 0 ' -> ('IL2', '0'); 'GM-CSF 4,1' -> ('GM-CSF', '4.1'); 'D 4.1' -> ('D','4.1'); 'Hb-1' -> ('Hb','-1')."""
    h = h.strip().replace(",", ".")
    m = re.match(r"^(.*?)\s*(-?\d+(?:\.\d)?)$", h)
    if not m:
        return None
    prefix, day = m.group(1).strip(), m.group(2)
    if day not in DAYS:
        return None
    return prefix, day


def main():
    wb = read_xlsx(str(SRC))
    notes = []
    values = defaultdict(dict)       # (dog number, day) -> {name: value}
    dose = {}
    by_prefix = {(s[0], s[1]): s for s in SPEC}
    seen_cols = defaultdict(int)
    unknown = []
    for sheet in ["Clinical", "Haematology", "Biochemistry", "Venous blood gas", "Cytokines", "Parasitaemias", "Iron"]:
        rows = wb[sheet]
        header = rows[0]
        for row in rows[1:]:
            if not row or row[0] is None:
                continue
            dog = int(float(row[0]))
            if dog == 1:
                continue
            if len(row) > 1 and row[1] is not None:
                dose[dog] = int(float(row[1]))
            for j, h in enumerate(header[2:], start=2):
                if h is None:
                    continue
                ph = parse_header(h)
                if ph is None or (sheet, ph[0]) not in by_prefix:
                    if h not in unknown:
                        unknown.append(h)
                    continue
                spec = by_prefix[(sheet, ph[0])]
                seen_cols[spec[2]] += 1
                v = num(row[j]) if j < len(row) else None
                if v is None:
                    continue
                values[(dog, ph[1])][spec[2]] = round(v * spec[4], 10)
    habitus_raw = {}
    for row in wb["Clinical"][1:]:
        if row and row[0] and int(float(row[0])) != 1:
            for j, h in enumerate(wb["Clinical"][0][2:], start=2):
                ph = parse_header(h) if h else None
                if ph and ph[0] == "H":
                    v = num(row[j]) if j < len(row) else None
                    if v is not None:
                        habitus_raw[(int(float(row[0])), ph[1])] = v
    if unknown:
        notes.append("Raw columns not read: " + ", ".join(unknown) + " (Clinical 'H' habitus scores go to the outcomes file).")

    dogs = sorted({d for d, _ in values} | {d for d, _ in habitus_raw})
    ids = neutral_ids(DS, [str(d) for d in dogs])
    # Last day with a haemoglobin value: the end of the clinical record of each dog.
    last_day = {d: max(float(day) for (dd, day), v in values.items() if dd == d and "hb" in v) for d in dogs}
    late_para = [(d, day) for (d, day), v in values.items() if last_day[d] <= 4 and float(day) > 4]

    records = []
    censored_counts = defaultdict(int)
    for d in dogs:
        for day in DAYS:
            vals = values.get((d, day))
            if not vals:
                continue
            vals = dict(vals)
            vals["dose_group"] = "high" if dose[d] == 1 else "low"
            cens = {}
            for k, v in vals.items():
                if k in CYTOKINES and v == 0:
                    cens[k] = "floor"
                if k == "crp" and v == 10:
                    cens[k] = "floor"
            for k in cens:
                censored_counts[k] += 1
            dval = float(day)
            records.append({
                "dog_id": ids[str(d)], "group": "infected",
                "timepoint": "day_" + day.replace(".", "_"), "day": 4.0 if day == "4.1" else dval,
                "sample": "second_day4_sample" if day == "4.1" else "daily",
                "post_treatment": dval >= 5,
                "values": vals, "censored": cens,
            })
    notes += [
        "Dog 1 (splenectomised donor, one baseline sample) is excluded, as the package file requires.",
        "One record per dog and sampling day. 'day' is the column suffix of the raw file (days after inoculation, -1 to 8; "
        "the file does not define the unit). The raw suffix '4.1' (low-dose dogs only) is an extra day-4 sample: "
        "timepoint 'day_4_1', day 4, sample 'second_day4_sample'.",
        "post_treatment is true for days 5 to 8. Treatment was at about 96 h (high dose) and 108 h (low dose) per the record; "
        "the file has no treatment column. Day 4 and the 4.1 sample are taken as pre-treatment (inferred).",
        "Dose group: Exp group 0 = low dose (10^4), 1 = high dose. The Notes sheet says 10^9 for the high dose; CB101 says 10^8 "
        "(unresolved, record). Stored as the design variable dose_group (low/high), not as a severity label.",
        "One dog has no clinical or haematology record after day 4 (death on day 4, CB101). Its missing later days are informative, not random.",
        "FLAG: the same dog has a parasitaemia of 0 in the day-6 column (raw cell Parasitaemias!K7), two days after its death. "
        "The value is kept as reported and flagged here; treat it as a probable entry error. "
        f"Affected dog-days: {len(late_para)}.",
        "Cytokine values of 0 are kept as 0 and flagged 'floor' in censored (below detection; no detection limits in the file). "
        f"Counts: " + ", ".join(f"{k} {n}" for k, n in sorted(censored_counts.items()) if k != "crp") + ".",
        f"CRP values of 10 are kept and flagged 'floor' ({censored_counts['crp']} samples): 10 is the reporting floor (record).",
        "In the high-dose dogs the 4.1 column is empty except for Retic% and Retic (reticulocytes), which hold a value there. "
        "These values are kept as reported (timepoint day_4_1); their sampling time is not documented. DS03 does not include them.",
        "MCHC converted from g/dL to g/L (x10). No other unit was changed.",
        "Floating-point noise in the cells was rounded to 10 decimals (0.28999999999999998 -> 0.29).",
        "Very high cytokine values on days 6 and 8 in one high-dose dog (IL-6, IL-8 and others above 10,000 pg/mL) are kept as reported; "
        "CB098 reports a post-treatment cytokine surge.",
        "Clinical lactate (lactate_clinical) and venous blood gas lactate (lactate) are two measurements; the harmonised 'lactate' is the blood gas value.",
        "The DS03 experimental file holds the same 5 dogs (identical Hb, HCT, Ret% and ARC values; DS03 days 1-6 = DS02 days 1-6, "
        "without the 4.1 sample). See the DS03 features file, field same_dog_as.",
        "DS01 (Mendeley) repeats these dogs and values and has no tidy file of its own.",
    ]

    names_in_data = {k for r in records for k in r["values"]}
    variables = [var(s[2], s[3], f"{s[0]}!{s[1]}<day>") for s in SPEC if s[2] in names_in_data]
    for v in variables:
        if v["name"] == "crp":
            v["floor"] = 10
        if v["name"] in CYTOKINES:
            v["floor"] = 0
    variables.append(var("dose_group", "low/high", "Exp group (0 = low dose, 1 = high dose)"))

    features = {
        "dataset_id": DS, "independent_source": "SRC-B", "species": "B. rossi",
        "built_from": [built_from_entry(SRC)],
        "variables": variables, "records": records, "cleaning_notes": notes,
    }

    # Outcomes: death of one dog (day 4) and the daily habitus score (a clinical severity proxy).
    died_dog = [d for d in dogs if last_day[d] <= 4]
    orecs = []
    for d in dogs:
        orecs.append({"dog_id": ids[str(d)], "original_id": f"dog {d}", "timepoint": None, "day": None,
                      "values": {"died": 1 if d in died_dog else 0}})
    for (d, day), h in sorted(habitus_raw.items(), key=lambda x: (x[0][0], float(x[0][1]))):
        orecs.append({"dog_id": ids[str(d)], "original_id": f"dog {d}", "timepoint": "day_" + day.replace(".", "_"),
                      "day": 4.0 if day == "4.1" else float(day), "values": {"habitus_score": h}})
    outcomes = {
        "dataset_id": DS,
        "outcomes": [
            {"name": "died", "definition": "Died on day 4 of the experimental infection (inferred from the end of the data and CB101); "
                                           "the file has no outcome column", "includes_euthanasia": None},
            {"name": "habitus_score", "definition": "Daily habitus score from the Clinical sheet (column H), scale 1-4; "
                                                    "per the DS01 supplementary table 4 is normal. One record per dog and day",
             "includes_euthanasia": False},
        ],
        "records": orecs,
    }

    # Dictionary
    drows = []
    for s in SPEC:
        if s[2] in names_in_data:
            drows.append(dict_row(s[2], DS, f"{s[0]}!{s[1]}<day>", s[3], s[5], s[6]))
    drows.append(dict_row("dose_group", DS, "Exp group", "low/high", "0 -> low, 1 -> high", "Design variable."))

    # Checks
    def first_positive(d):
        for day in DAYS:
            v = values.get((d, day), {}).get("parasitaemia_pct")
            if v is not None and v > 0:
                return float(day)
        return None
    hd = [d for d in dogs if dose[d] == 1]
    ld = [d for d in dogs if dose[d] == 0]
    checks = {"dataset_id": DS, "checks": [
        check("infected dogs (3 high dose + 2 low dose)", [len(hd), len(ld)], [3, 2], source="data.md; CB098 note"),
        check("feature records (dog-days)", len(records), sum(1 for k in values), source="internal"),
        check("parasitaemia first detected on day 1 in all high-dose dogs", sorted({first_positive(d) for d in hd}), [1.0],
              source="CB098 note: detected day 1 high dose"),
        check("parasitaemia first detected on day 3 in all low-dose dogs", sorted({first_positive(d) for d in ld}), [3.0],
              source="CB098 note: detected day 3 low dose"),
        check("one high-dose dog has no data after day 4", [len(died_dog), all(d in hd for d in died_dog)], [1, True],
              source="CB101 note: one high-dose dog died on day 4"),
    ], "n_dogs": len(dogs), "n_records": len(records)}

    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
