"""Tidy S-CB516 (natural B. canis infection, Switzerland, SRC-O; article CB516).

One record per dog (15 naturally infected dogs, admission). Source: supplemental file 1, a one-page PDF
table converted with xpdf pdftotext -table. Supplemental file 2 holds figures only (differential WBC
counts as plots) and yields no values.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tidylib import (OUT, RAW, built_from_entry, check, dict_row, neutral_ids, var, write_dataset, zip_member)

DS = "S-CB516"
ZIP = RAW / "S-CB516" / "PMC4913656_supplementaryFiles.zip"
M1 = "JVIM-30-174-s001.pdf"
M2 = "JVIM-30-174-s002.pdf"
WORK = OUT / "work" / "scb516"
PDFTOTEXT_CANDIDATES = [r"C:\Program Files\Git\mingw64\bin\pdftotext.exe", "/mingw64/bin/pdftotext", "pdftotext"]

# The 10 numeric columns after the location, in table order: (name, raw header, unit, note)
SIGNS = [
    ("sign_lethargy", "Apathy / Lethargy", "0/1", "Present in all 15 dogs (no information)."),
    ("sign_pale_mm", "Pale mucous membranes", "0/1", "Present in all 15 dogs (no information)."),
    ("sign_pigmenturia", "Pigmenturia", "0/1", ""),
    ("sign_icterus", "Icterus", "0/1", ""),
    ("sign_fever", "Fieber", "0/1", "Fever flag; threshold not stated (raw header 'Fieber', German for fever)."),
    ("temp_c", "Body temeprature [°C]", "degC", "Body temperature."),
    ("sign_anorexia", "Anorexia", "0/1", ""),
    ("sign_vomiting", "Vomiting", "0/1", ""),
    ("sign_water_hammer_pulse", "Water hammer pulse", "0/1", ""),
    ("sign_epistaxis", "Epistaxis", "0/1", ""),
]


def pdftotext(pdf, txt):
    for exe in PDFTOTEXT_CANDIDATES:
        if Path(exe).exists() or shutil.which(exe):
            subprocess.run([exe, "-table", "-enc", "UTF-8", str(pdf), str(txt)], check=True)
            return exe
    raise SystemExit("pdftotext not found")


def extract():
    """Copy the zip members to the work folder and convert them. Returns (table text, file-2 text)."""
    WORK.mkdir(parents=True, exist_ok=True)
    texts = []
    for m in (M1, M2):
        pdf = WORK / m
        pdf.write_bytes(zip_member(ZIP, m))
        txt = WORK / (pdf.stem + ".table.txt")
        try:
            pdftotext(pdf, txt)
        finally:
            pdf.unlink()   # keep only the text output in the work folder
        texts.append(txt.read_text(encoding="utf-8"))
    return texts


def parse_table(text):
    lines = text.splitlines()
    hi = next(i for i, l in enumerate(lines) if re.match(r"^#\s+Outcome\s+Breed", l))
    h = lines[hi]
    starts = {
        "breed": h.index("Breed"), "age": h.index("Age"), "sex": h.index("Sex"), "weight": h.index("weight"),
        "loc": h.index("on travel history"), "signs": h.index("Lethargy"),
    }
    order = ["breed", "age", "sex", "weight", "loc", "signs"]
    dogs = []
    block = []
    first = next(i for i in range(hi, len(lines)) if "Mo=months)" in lines[i]) + 1   # end of the header continuation lines
    for l in lines[first:]:
        if not l.strip():
            continue
        m = re.match(r"^\s*(\d+)\s+(Died|Survival)\s", l)
        block.append(l)
        if not m:
            continue
        fields = {k: [] for k in order}
        for bl in block:
            for i, k in enumerate(order):
                a = starts[k]
                b = starts[order[i + 1]] if i + 1 < len(order) else None
                piece = bl[a:b].strip() if b else bl[a:].strip()
                if piece:
                    fields[k].append(piece)
        signs = " ".join(fields["signs"]).split()
        dogs.append({
            "num": int(m.group(1)), "outcome": m.group(2),
            "breed": " ".join(fields["breed"]), "age_raw": " ".join(fields["age"]), "sex_raw": " ".join(fields["sex"]),
            "weight_raw": " ".join(fields["weight"]), "loc_raw": " ".join(fields["loc"]), "signs_raw": signs,
        })
        block = []
    return dogs


def age_months(s):
    y = re.search(r"(\d+)\s*Y", s)
    mo = re.search(r"(\d+)\s*Mi?o\b", s)
    if not y and not mo:
        return None
    return (int(y.group(1)) if y else 0) * 12 + (int(mo.group(1)) if mo else 0)


def main():
    table_text, file2_text = extract()
    dogs = parse_table(table_text)
    notes = []
    assert [d["num"] for d in dogs] == list(range(1, 16)), [d["num"] for d in dogs]

    ids = neutral_ids(DS, [str(d["num"]) for d in dogs])
    records, orecs, flags = [], [], []
    for d in dogs:
        vals = {"breed": d["breed"]}
        am = age_months(d["age_raw"])
        vals["age_months"] = am
        if "Mio" in d["age_raw"]:
            flags.append(f"{ids[str(d['num'])]}: age written '{d['age_raw']}' ('Mio' read as months, Mo)")
        sx = d["sex_raw"].lower().split()
        vals["sex"] = "female" if "female" in sx else ("male" if "male" in sx else None)
        if "intact" in sx:
            vals["neuter"] = "intact"
        elif "neutered" in sx or "gelded" in sx:
            vals["neuter"] = "neutered"
        else:
            vals["neuter"] = None
        vals["weight_kg"] = float(d["weight_raw"])
        loc = re.sub(r"\s+", " ", d["loc_raw"]).strip()
        vals["travel_location"] = "Switzerland (no travel history)" if loc.startswith("no travel history") else loc
        vals["travel_abroad"] = 0 if loc.startswith("no travel history") else 1
        if len(d["signs_raw"]) != len(SIGNS):
            raise SystemExit(f"dog {d['num']}: {len(d['signs_raw'])} sign values: {d['signs_raw']}")
        for (name, *_), raw in zip(SIGNS, d["signs_raw"]):
            v = float(raw)
            if name != "temp_c":
                assert v in (0, 1), (d["num"], name, raw)
                v = int(v)
            vals[name] = v
        records.append({"dog_id": ids[str(d["num"])], "group": "infected", "timepoint": "admission", "day": None,
                        "values": vals, "censored": {}})
        orecs.append({"dog_id": ids[str(d["num"])], "original_id": f"#{d['num']}",
                      "values": {"died": 1 if d["outcome"] == "Died" else 0}})
    records.sort(key=lambda r: r["dog_id"])
    orecs.sort(key=lambda r: r["dog_id"])

    # Fever flag against body temperature
    fev = [(r["values"]["temp_c"], r["values"]["sign_fever"]) for r in records]
    max_no = max(t for t, f in fev if f == 0)
    min_yes = min(t for t, f in fev if f == 1)
    no_neuter = [r["dog_id"] for r in records if r["values"]["neuter"] is None]
    counts = {name: sum(r["values"][name] for r in records) for name, *_ in SIGNS if name != "temp_c"}

    notes += [
        "Source: supplemental file 1 (one-page PDF table), converted with xpdf pdftotext 4.00 in '-table' mode from a copy of the "
        "zip member in SV-G1/out/work/scb516/. The '-layout' mode scrambles the wrapped cells of this table; '-table' keeps each "
        "dog's row, with wrapped text (breed, sex, location) on the line above it. Fields were cut at the header column positions.",
        "Supplemental file 2 (differential WBC counts) holds figure panels only; its text is the caption. No values were read "
        "from it. Its dog IDs (D1-3 experimental, N1-11 natural) cannot be linked to the '#' numbers of file 1.",
        "One record per dog: the 15 naturally infected dogs, timepoint 'admission' (signs at admission per the article's results; "
        "the table gives no sampling time). The 3 experimental dogs of the article are not in file 1.",
        "No laboratory values per dog are in the files (the article's lactate, haematology and biochemistry results are group "
        "summaries only).",
        "Neutral dog_id from the table number '#'. The table is sorted by outcome (#1-8 died, #9-15 survived), so the original "
        "number carries the label; it is only in the outcomes file.",
        "Age: text such as '6Y 11 Mo' converted to months (years x 12 + months).",
        "Sex and neuter status from one cell: 'male gelded' and 'female neutered' -> neuter 'neutered'; 'intact' -> 'intact'. "
        f"Neuter status is missing (null) for {len(no_neuter)} dogs whose cell gives only the sex.",
        "travel_location: the 'assumed location of infection based on travel history' as written; 'no travel history "
        "(Switzerland)' is stored as 'Switzerland (no travel history)'. travel_abroad = 1 if a foreign country is named.",
        "Clinical signs are 0/1 as in the table (caption: 0 absent, 1 present). Lethargy and pale mucous membranes are present in "
        "all 15 dogs and carry no information.",
        f"Fever flag against body temperature: highest temperature with fever 0 is {max_no} degC, lowest with fever 1 is {min_yes} "
        "degC; the threshold is not stated (inferred to lie between them). The flag is consistent with temp_c in every dog."
        if max_no < min_yes else f"FLAG: fever flag inconsistent with temp_c (fever 0 up to {max_no}, fever 1 from {min_yes}).",
        "Severity labels and the features: the label here is death, not a complication score, so no clinical-sign column defines "
        "it. Note that icterus, pigmenturia (haemoglobinuria) and epistaxis (bleeding) appear as complications in other severity "
        "definitions (e.g. WHO-style 'complicated' babesiosis in S-CB017); they are kept as features and analysts using a "
        "complication-based label elsewhere should not treat them as independent of it.",
        "Death: 8 dogs labelled 'Died' in file 1. The article says 6 died spontaneously within 24 h of admission and 2 were "
        "euthanised within 48 h for clinical deterioration; which 2 is not in the files. 'died' therefore includes euthanasia.",
        "All dogs received imidocarb (3-6 mg/kg IM, some with doxycycline) after admission sampling per the article; not in the file.",
        "Raw header typos ('Fieber', 'temeprature') are kept in the 'original' fields; the age typo 'Mio' is flagged below.",
    ]
    notes += ["FLAG: " + f for f in flags]

    variables = [
        var("breed", "text", "Breed"),
        var("age_months", "months", "Age (Y= Year; Mo=months)"),
        var("sex", "male/female", "Sex"),
        var("neuter", "intact/neutered", "Sex"),
        var("weight_kg", "kg", "Body weight [kg]"),
        var("travel_location", "text", "Assumed location of infection based on travel history"),
        var("travel_abroad", "0/1", "Assumed location of infection based on travel history"),
    ] + [var(name, unit, raw) for name, raw, unit, _ in SIGNS]

    features = {
        "dataset_id": DS, "independent_source": "SRC-O", "species": "B. canis",
        "built_from": [built_from_entry(ZIP, M1), built_from_entry(ZIP, M2)],
        "variables": variables, "records": records, "cleaning_notes": notes,
    }
    outcomes = {
        "dataset_id": DS,
        "outcomes": [{"name": "died",
                      "definition": "Nonsurvivor: died spontaneously within 24 h of admission (6 dogs) or euthanised within 48 h for "
                                    "clinical deterioration (2 dogs), per the article; file 1 labels all 8 'Died'. Survivors were "
                                    "considered cured (no parasites on smear 14 days after admission).",
                      "includes_euthanasia": True}],
        "records": orecs,
    }

    drows = [
        dict_row("breed", DS, "Breed", "text"),
        dict_row("age_months", DS, "Age (Y= Year; Mo=months)", "months", "years x 12 + months (from text)"),
        dict_row("sex", DS, "Sex", "male/female", "", "From the sex/neuter cell."),
        dict_row("neuter", DS, "Sex", "intact/neutered", "gelded or neutered -> neutered", "Missing for 2 dogs."),
        dict_row("weight_kg", DS, "Body weight [kg]", "kg"),
        dict_row("travel_location", DS, "Assumed location of infection based on travel history", "text", "",
                 "Place of infection assumed from travel history."),
        dict_row("travel_abroad", DS, "Assumed location of infection based on travel history", "0/1",
                 "1 if a foreign country is named", ""),
    ] + [dict_row(name, DS, raw, unit, "", note) for name, raw, unit, note in SIGNS]

    n_died = sum(r["values"]["died"] for r in orecs)
    article = {"sign_lethargy": 15, "sign_pale_mm": 15, "sign_pigmenturia": 10, "sign_icterus": 6, "sign_fever": 5,
               "sign_anorexia": 4, "sign_vomiting": 4, "sign_water_hammer_pulse": 4, "sign_epistaxis": 3}
    clist = [
        check("dogs died, survived", [n_died, len(orecs) - n_died], [8, 7], source="data.md; CB516 methods"),
        check("feature records", len(records), 15, source="data.md"),
    ] + [check(f"dogs with {k[5:]}", counts[k], v, source="CB516 full text, results (n of 15)") for k, v in article.items()] + [
        check("sex: female, male", [sum(r["values"]["sex"] == "female" for r in records),
                                    sum(r["values"]["sex"] == "male" for r in records)], [5, 10], source="record"),
        check("dogs with neuter status missing", len(no_neuter), 2, source="record (#2 and #6)"),
        check("weight range kg", [min(r["values"]["weight_kg"] for r in records), max(r["values"]["weight_kg"] for r in records)],
              [7.0, 62.1], source="record"),
        check("age range months", [min(r["values"]["age_months"] for r in records), max(r["values"]["age_months"] for r in records)],
              [7, 129], source="record: 7 months to 10 years 9 months"),
        check("temperature range degC", [min(r["values"]["temp_c"] for r in records), max(r["values"]["temp_c"] for r in records)],
              [37.8, 40.5], source="record"),
        check("assumed locations: France, Hungary, Russia, Croatia, Serbia, Switzerland",
              [sum(r["values"]["travel_location"] == c for r in records) for c in
               ("France", "Hungary", "Russia", "Croatia", "Serbia", "Switzerland (no travel history)")],
              [4, 2, 1, 1, 1, 6], source="record"),
        check("supplemental file 2 has no numeric table", "caption only" if len(re.findall(r"\d+\.\d", file2_text)) == 0 else "numbers found",
              "caption only", source="record"),
    ]
    checks = {"dataset_id": DS, "checks": clist, "n_dogs": len(records), "n_records": len(records)}
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
