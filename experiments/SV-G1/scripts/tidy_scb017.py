"""Tidy S-CB017 (natural B. canis infection, Zagreb, SRC-D; article CB017).

Long format: one record per dog and day. Infected dogs have day 1 (admission) and day 7; healthy
controls have one record. The label (complicated / uncomplicated) is in the original ID prefix
(BK / B): the neutral dog_id hides it, and the label and original ID go only to the outcomes file.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tidylib import (RAW, built_from_entry, check, dict_row, median, neutral_ids, num, read_xlsx, var,
                     write_dataset, zip_member)

DS = "S-CB017"
ZIP = RAW / "S-CB017" / "PMC5756041_supplementaryFiles.zip"
MEMBER = "pone.0190474.s001.xlsx"

# Cytokine sheet: raw header prefix -> (name, assay floor per the record, note)
CYTO = [
    ("GM-CSF", "gmcsf", None, ""),
    ("KC-like", "kc", None, "KC-like (canine CXCL1 homologue); the panel reports KC-like and IL-8 separately."),
    ("IL-2", "il2", 10, ""),
    ("IL-7", "il7", None, ""),
    ("IL-8", "il8", 10, ""),
    ("IL-10", "il10", 0.8, ""),
    ("IL-15", "il15", 12, ""),
    ("IL-18", "il18", 2, ""),
    ("MCP-1", "mcp1", None, ""),
]
# Haematology sheet: raw header -> (name, unit, factor, conversion, note). Units are not in the header;
# they follow the reference-range block of the sheet and the size of the values.
HAEM = [
    ("Leuko", "wbc", "10^9/L", 1, "", "Leukocytes."),
    ("Lymph", "lymph", "10^9/L", 1, "", ""),
    ("Neseg. Neut", "neut_band", "10^9/L", 1, "", "Non-segmented (band) neutrophils (Croatian 'nesegmentirani')."),
    ("Seg. Neut", "neut_seg", "10^9/L", 1, "", ""),
    ("Mono", "mono", "10^9/L", 1, "", ""),
    ("Eos", "eos", "10^9/L", 1, "", ""),
    ("Thromb", "plt", "10^9/L", 1, "", "Thrombocytes."),
    ("HMT", "hct", "L/L", 0.01, "/100 (% to L/L)", "Haematocrit; raw values are % (reference 37-55)."),
    ("Eryt", "rbc", "10^12/L", 1, "", "Erythrocytes."),
    ("Lymph %", "lymph_pct", "%", 1, "", "Percent of WBC."),
    ("Nes. Neut %", "neut_band_pct", "%", 1, "", "Percent of WBC."),
    ("Seg neut %", "neut_seg_pct", "%", 1, "", "Percent of WBC."),
    ("Mono %", "mono_pct", "%", 1, "", "Percent of WBC."),
    ("Eos %", "eos_pct", "%", 1, "", "Percent of WBC."),
    ("Total gran", "gran_total_pct", "%", 1, "", "Total granulocytes (segmented + band neutrophils), percent of WBC."),
    ("n:l", "nl_ratio", "ratio", 1, "", "Neutrophil to lymphocyte ratio; in the file it equals Total gran % / Lymph %."),
]
COUNT_PCT = [("lymph", "lymph_pct"), ("neut_band", "neut_band_pct"), ("neut_seg", "neut_seg_pct"),
             ("mono", "mono_pct"), ("eos", "eos_pct")]


def norm_id(x):
    return re.sub(r"\s+", "", x or "")


def read_cytokines(rows, notes):
    """Return {(block, original id): {name: value}}, dead_flags {(block, id)}, and the block sizes."""
    header = rows[1]
    col = {}
    for j, h in enumerate(header):
        if h is None:
            continue
        for raw, name, _, _ in CYTO:
            if h.startswith(raw + " ("):
                col[name] = j
    assert len(col) == 9, col
    block = None
    out, dead, sizes = {}, set(), defaultdict(int)
    renamed, labels = [], []
    for r in rows[2:]:
        if not r or len(r) < 2 or r[1] is None:
            continue
        if r[0] is not None:
            label = re.sub(r"\s+", " ", r[0]).strip().lower()
            block = {"diseased day 1": "dis1", "diseased day 7": "dis2"}[label]
            labels.append(repr(r[0]))
        oid_raw = r[1]
        oid = norm_id(oid_raw)
        if oid != oid_raw:
            renamed.append(f"'{oid_raw}' -> '{oid}'")
        b = block or "healthy"
        out[(b, oid)] = {name: num(r[j]) if j < len(r) else None for name, j in col.items()}
        sizes[b] += 1
        if len(r) > 11 and r[11] and r[11].strip().lower() == "dead":
            dead.add((b, oid))
    # The healthy block starts at row 2 (the row 0 label is 'Healthy'); rows before the first 'Diseased'
    # label have block None and are counted as healthy above.
    if renamed:
        notes.append("Cytokine sheet: sample IDs with an inner space were joined to the haematology IDs: " + ", ".join(renamed) + ".")
    return out, dead, dict(sizes), labels


def read_haematology(rows):
    header = [h.strip() if h else None for h in rows[0]]
    col = {}
    for raw, name, *_ in HAEM:
        col[name] = header.index(raw)
    out, sizes = {}, defaultdict(int)
    block = "healthy"
    for r in rows[1:]:
        if not r or r[0] is None:
            continue
        first = r[0].strip()
        if first.lower().startswith("diseased"):
            day = (r[1] or "").strip().lower()
            block = {"day 1": "dis1", "day 7": "dis2"}[day]
            continue
        oid = norm_id(first)
        out[(block, oid)] = {name: num(r[j]) for name, j in col.items()}
        sizes[block] += 1
    return out, dict(sizes)


def main():
    raw = zip_member(ZIP, MEMBER)
    wb = read_xlsx(raw)
    notes = []
    assert not any(any(c for c in row) for row in wb.get("Hoja1", [])), "Hoja1 is not empty"

    cyto, dead_flags, cyto_sizes, cyto_labels = read_cytokines(wb["CYTOKINES"], notes)
    haem, haem_sizes = read_haematology(wb["HEMATOLOGY"])

    # --- Day of the two unlabelled cytokine blocks -------------------------------------------------
    ids_dis1 = {o for b, o in cyto if b == "dis1"}
    ids_dis2 = {o for b, o in cyto if b == "dis2"}
    h_dis1 = {o for b, o in haem if b == "dis1"}
    h_dis2 = {o for b, o in haem if b == "dis2"}
    only_first = sorted(ids_dis1 - ids_dis2)
    il10_floor_share = {b: sum(1 for (bb, _), v in cyto.items() if bb == b and v["il10"] == 0.8) for b in ("dis1", "dis2")}

    # --- Join the two sheets on the original ID and block --------------------------------------------
    keys = sorted(set(cyto) | set(haem))
    missing_in = [(k, "cytokines") for k in keys if k not in cyto] + [(k, "haematology") for k in keys if k not in haem]
    if missing_in:
        notes.append("FLAG: samples present in only one sheet: " + "; ".join(f"{k[1]} {k[0]} (no {s})" for k, s in missing_in))

    def is_control(oid):
        return oid.startswith("H")

    originals = sorted({o for _, o in keys})
    ids = neutral_ids(DS, originals)

    # --- Haematology consistency flags (values kept as reported) ------------------------------------
    flags, nl_mismatch = [], []
    for k in keys:
        v = haem.get(k)
        if not v:
            continue
        b, oid = k
        tp = {"healthy": "control", "dis1": "day 1", "dis2": "day 7"}[b]
        wbc = v["wbc"]
        for cnt, pct in COUNT_PCT:
            exp = round(v[pct] * wbc / 100, 2)
            if abs(v[cnt] - exp) > 0.5 and abs(v[cnt] - exp) > 0.25 * max(exp, 0.1):
                flags.append(f"{ids[oid]} {tp}: {cnt} {v[cnt]} vs {pct} {v[pct]}% of WBC {wbc} = {exp}")
        if abs(v["gran_total_pct"] - v["neut_seg_pct"] - v["neut_band_pct"]) > 1:
            flags.append(f"{ids[oid]} {tp}: gran_total_pct {v['gran_total_pct']} differs from seg % + band %")
        if v["lymph_pct"]:
            nl = v["gran_total_pct"] / v["lymph_pct"]
            nlc = (v["neut_seg"] + v["neut_band"]) / v["lymph"] if v["lymph"] else None
            ok_pct = abs(nl - v["nl_ratio"]) <= max(0.15, 0.05 * nl)
            ok_cnt = nlc is not None and abs(nlc - v["nl_ratio"]) <= max(0.15, 0.05 * nlc)
            if not (ok_pct or ok_cnt):
                nl_mismatch.append(f"{ids[oid]} {tp}: nl_ratio {v['nl_ratio']} vs gran % / lymph % = {nl:.1f}"
                                   + (f" and (seg + band) / lymph counts = {nlc:.1f}" if nlc is not None else ""))
        else:
            nl_mismatch.append(f"{ids[oid]} {tp}: lymph_pct 0, nl_ratio {v['nl_ratio']}")
        mcv = v["hct"] * 10 / v["rbc"] if v["rbc"] else None
        if mcv is None or not 50 <= mcv <= 90:
            flags.append(f"{ids[oid]} {tp}: hct {v['hct']}% and rbc {v['rbc']} give MCV {mcv:.0f} fL (implausible; rbc is probably the haematocrit typed twice)")

    # --- Records ------------------------------------------------------------------------------------
    records = []
    cens_counts = defaultdict(int)
    floors = {name: fl for _, name, fl, _ in CYTO}
    for (b, oid) in keys:
        vals = {}
        for name, v in (cyto.get((b, oid)) or {}).items():
            vals[name] = v
        for raw_h, name, unit, factor, conv, note in HAEM:
            hv = (haem.get((b, oid)) or {}).get(name)
            vals[name] = None if hv is None else round(hv * factor, 10)
        cens = {}
        for name, fl in floors.items():
            if fl is not None and vals.get(name) is not None and vals[name] <= fl:
                cens[name] = "floor"
                cens_counts[name] += 1
        if is_control(oid):
            vals["control_subgroup"] = "HI" if oid.startswith("HI") else "H"
            rec = {"dog_id": ids[oid], "group": "control", "timepoint": "single", "day": None}
        else:
            vals["control_subgroup"] = None
            d = 1 if b == "dis1" else 7
            rec = {"dog_id": ids[oid], "group": "infected", "timepoint": f"day_{d}", "day": d}
        rec["values"] = vals
        rec["censored"] = cens
        records.append(rec)
    records.sort(key=lambda r: (r["dog_id"], r["day"] or 0))

    below = {name: sum(1 for k, v in cyto.items() if v[name] is not None and fl is not None and v[name] < fl)
             for _, name, fl, _ in CYTO}
    mins = {name: min(v[name] for v in cyto.values() if v[name] is not None) for _, name, _, _ in CYTO}

    variables = []
    for raw_h, name, fl, note in CYTO:
        variables.append(var(name, "pg/mL", f"CYTOKINES!{raw_h} (pg/ml)", floor=fl))
    for raw_h, name, unit, factor, conv, note in HAEM:
        variables.append(var(name, unit, f"HEMATOLOGY!{raw_h}"))
    variables.append(var("control_subgroup", "H/HI", "Sample ID prefix of the healthy dogs (H1-8, HI1-8)"))

    n_inf = sum(1 for o in originals if not is_control(o))
    n_ctl = sum(1 for o in originals if is_control(o))
    notes += [
        "Source: S1 Table workbook (sheets CYTOKINES, HEMATOLOGY; the third sheet 'Hoja1' is empty). Both sheets were joined on the "
        "original sample ID and the block (healthy, diseased day 1, diseased day 7); every sample is in both sheets.",
        "Long format: one record per dog and day. Infected dogs: timepoint day_1 (admission) and day_7 (6 days after imidocarb), "
        "numeric day 1 and 7. Healthy controls: one record, timepoint 'single', day null.",
        f"Day of the cytokine blocks: the record and data.md say the two 'Diseased' blocks of the CYTOKINES sheet "
        f"({cyto_sizes.get('dis1')} and {cyto_sizes.get('dis2')} rows) have no day label. They do: the label cells read "
        f"{' and '.join(cyto_labels)}; the day text sits after a run of spaces and is hidden in a narrow column. The blocks were "
        "assigned from these labels. Independent support: (a) the only ID in the day-1 block and not in the day-7 block is "
        f"{', '.join(only_first)}, the same dog that is the only one missing from the haematology 'Diseased day 7' block "
        "(the article reports one death and n = 30 on day 7); (b) the medians of each block reproduce the article's Table 2 "
        "day-1 and day-7 medians for all 9 cytokines (checks file); (c) IL-10 is at its floor in "
        f"{il10_floor_share['dis1']} of {cyto_sizes.get('dis1')} day-1 and {il10_floor_share['dis2']} of "
        f"{cyto_sizes.get('dis2')} day-7 samples, matching the reported day-7 IL-10 median of 1 pg/mL.",
        "Haematology day labels come from the text rows 'Diseased day 1' and 'Diseased day 7' of the HEMATOLOGY sheet.",
        "Neutral dog_id: the original IDs (H*, HI*, B*, BK*) carry the label (B = uncomplicated, BK = complicated, per the side legend "
        "of the CYTOKINES sheet). They are replaced by salted-hash IDs; the original ID is only in the outcomes file.",
        "Blood for cytokines was taken 6-8 h after imidocarb dipropionate (6 mg/kg SC on day 1) per the article, so day-1 values are "
        "early post-treatment, not pre-treatment. All infected dogs also had supportive care (fluids, anti-inflammatories, transfusion "
        "if haematocrit < 20%) that the file does not record.",
        "Healthy controls: 8 'H' and 8 'HI' dogs. control_subgroup keeps this prefix. The article describes two control subgroups of 8: "
        "dogs given prophylactic imidocarb (group 2a) and dogs at routine visits (group 2b). Reading HI as the imidocarb subgroup is an "
        "inference from the prefix; the file does not say so. The article says group 2a was sampled at admission and 6 days later, but "
        "the file has one sample per control dog; which time point it is, is not stated.",
        "Assay floors (per the record, confirmed as the minimum value in the file): IL-10 0.8, IL-18 2, IL-2 10, IL-15 12, IL-8 10 pg/mL. "
        "Values at the floor are kept and flagged 'floor' in censored. Counts over all 77 samples: "
        + ", ".join(f"{k} {cens_counts[k]}" for k in ("il10", "il18", "il2", "il15", "il8")) + ". "
        "Observed minima of all cytokines: " + ", ".join(f"{k} {v}" for k, v in mins.items()) + ". "
        "Values below a floor: " + (", ".join(f"{k} {n}" for k, n in below.items() if n) or "none") + ".",
        "FLAG: the IL-2 floor of 10 occurs once (one control sample); the next-lowest IL-2 value 12.1 is frequent and may also be a "
        "floor-like interpolated value. Only the record's floors were flagged. Cytokine values are heavily quantised (repeated values "
        "such as IL-18 83, 144.9, 188.4); kept as reported.",
        "FLAG: the CYTOKINES sheet has an unlabelled column with the word 'Dead' beside "
        f"{len({o for b, o in dead_flags if b == 'dis1'})} complicated dogs in the first block and "
        f"{len({o for b, o in dead_flags if b == 'dis2'})} in the second. The article reports one death. The column is not used "
        "as an outcome and nothing from it is in the features or outcomes file.",
        "Haematology units are not in the headers. They follow the reference-range block of the sheet: counts 10^9/L, erythrocytes "
        "10^12/L, HMT %, differentials %. HMT was converted from % to L/L (/100). No other unit was changed.",
        "The reference-range block of the HEMATOLOGY sheet (haematology and biochemistry ranges, with no data) was not read.",
        "The file has no haemoglobin, red cell indices, parasitaemia, biochemistry, CRP, clinical signs, age, sex or breed. The article "
        "gives sex only as group totals (complicated 8 female, 10 male; uncomplicated 5 female, 8 male).",
        "Haematology consistency checks (count against % x WBC, total granulocytes against segmented + band %, MCV implied by "
        "HMT / erythrocytes). Values are kept as reported; each failure is a FLAG below.",
    ]
    notes += ["FLAG: " + f for f in flags]
    notes += [
        (f"The n:l ratio equals Total gran % / Lymph % or (segmented + band) / lymphocyte counts (within 5% or 0.15) in "
         f"{len(keys) - len(nl_mismatch)} of {len(keys)} samples, "
         "so a high n:l (for example 99) follows the reported percentages and is not flagged on its own."
         + (" FLAG: exceptions: " + "; ".join(nl_mismatch) + "." if nl_mismatch else "")),
        "Floating-point noise in the cells was rounded to 10 decimals.",
    ]

    features = {
        "dataset_id": DS, "independent_source": "SRC-D", "species": "B. canis",
        "built_from": [built_from_entry(ZIP, MEMBER)],
        "variables": variables, "records": records, "cleaning_notes": notes,
    }

    # --- Outcomes -----------------------------------------------------------------------------------
    orecs = []
    for o in originals:
        if is_control(o):
            continue
        died = 1 if o in only_first else 0
        orecs.append({"dog_id": ids[o], "original_id": o,
                      "values": {"complicated": 1 if o.startswith("BK") else 0, "died": died}})
    outcomes = {
        "dataset_id": DS,
        "outcomes": [
            {"name": "complicated",
             "definition": "Complicated (1, ID prefix BK) vs uncomplicated (0, prefix B) babesiosis as classified by the authors from "
                           "clinical manifestations and laboratory data, following the WHO classification of complicated malaria; "
                           "all complicated dogs were SIRS-positive and 66% MODS-positive (article). Assigned at admission. "
                           "Inflammatory markers and WBC (a SIRS criterion) partly define this label.",
             "includes_euthanasia": None},
            {"name": "died",
             "definition": "Death during the study (article: one complicated dog died). Which dog is inferred: the only infected dog "
                           "with no day-7 sample. Cause and timing not reported. The unlabelled 'Dead' column of the workbook "
                           "contradicts the article and is NOT used.",
             "includes_euthanasia": None},
        ],
        "records": orecs,
    }

    # --- Dictionary -----------------------------------------------------------------------------------
    drows = []
    for raw_h, name, fl, note in CYTO:
        n = (note + (f" Assay floor {fl} pg/mL (record); values at the floor flagged in censored." if fl is not None else "")).strip()
        drows.append(dict_row(name, DS, f"CYTOKINES!{raw_h} (pg/ml)", "pg/mL", "", "Milliplex canine panel (Luminex). " + n))
    for raw_h, name, unit, factor, conv, note in HAEM:
        drows.append(dict_row(name, DS, f"HEMATOLOGY!{raw_h}", unit, conv, note))
    drows.append(dict_row("control_subgroup", DS, "Sample ID prefix H / HI (controls only)", "H/HI", "",
                          "Design variable; HI probably the prophylactic-imidocarb subgroup (inferred)."))

    # --- Checks ---------------------------------------------------------------------------------------
    def block_median(block, name, prefix=None):
        return median([v[name] for (b, o), v in cyto.items() if b == block and (prefix is None or
                       (o.startswith("BK") if prefix == "BK" else (o.startswith("B") and not o.startswith("BK"))))])

    t2 = {  # Table 2 medians (rounded integers in the article)
        ("healthy", None): [87, 39, 17, 55, 137, 1, 77, 83, 193],
        ("dis1", None): [182, 532, 96, 101, 856, 560, 160, 188, 390],
        ("dis2", None): [196, 561, 49, 80, 2754, 1, 219, 207, 237],
        ("dis1", "B"): [143, 330, 89, 51, 601, 461, 111, 145, 224],
        ("dis1", "BK"): [254, 567, 131, 139, 908, 592, 265, 188, 576],
        ("dis2", "B"): [154, 440, 28, 68, 2852, 1, 184, 145, 191],
        ("dis2", "BK"): [254, 830, 65, 84, 1911, 1, 253, 225, 365],
    }
    label = {"healthy": "healthy", "dis1": "day 1", "dis2": "day 7"}
    n_bk = sum(1 for o in originals if o.startswith("BK"))
    n_b = sum(1 for o in originals if o.startswith("B") and not o.startswith("BK"))
    clist = [
        check("dogs: complicated, uncomplicated, controls", [n_bk, n_b, n_ctl], [18, 13, 16], source="data.md; CB017 note"),
        check("samples per block (cytokines): healthy, day 1, day 7",
              [cyto_sizes.get("healthy"), cyto_sizes.get("dis1"), cyto_sizes.get("dis2")], [16, 31, 30], source="data.md; CB017 Table 2"),
        check("samples per block (haematology): healthy, day 1, day 7",
              [haem_sizes.get("healthy"), haem_sizes.get("dis1"), haem_sizes.get("dis2")], [16, 31, 30], source="data.md; record"),
        check("feature records (dog-days)", len(records), 77, source="16 + 31 + 30"),
        check("infected dogs missing on day 7 (one death)", only_first, ["BK11"], source="record; CB017 note: day-7 n = 30 after one death"),
        check("haematology day-7 block lacks the same dog", sorted(h_dis1 - h_dis2), only_first, source="internal"),
        check("IL-10 at floor 0.8 in 45 of 77 samples", cens_counts["il10"], 45, source="record"),
    ]
    for (block, pre), exp in t2.items():
        obs = [round(block_median(block, name, pre), 1) for _, name, _, _ in CYTO]
        grp = {None: "all", "B": "uncomplicated", "BK": "complicated"}[pre]
        within = all(abs(o - e) <= 0.51 for o, e in zip(obs, exp))
        clist.append({"name": f"Table 2 medians, {label[block]} {grp} (9 cytokines, GM-CSF..MCP-1)", "observed": obs,
                      "expected": exp, "tolerance": 0.51, "source": "CB017 full text, Table 2 (medians rounded to integers)",
                      "pass": within})
    checks = {"dataset_id": DS, "checks": clist, "n_dogs": len(originals), "n_records": len(records),
              "day_assignment": {"cytokine_block_labels": cyto_labels,
                                 "evidence": "label text in the block cells (hidden after spaces); ID missing from the day-7 block = "
                                             "only dog missing from haematology day 7; Table 2 medians by block; IL-10 floor share"}}
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
