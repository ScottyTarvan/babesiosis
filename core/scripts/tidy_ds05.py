"""Tidy DS05 (BET study, article CB126) into data/tidy/DS05.json for the experiments loader.

Reads the 'Entire population' and 'CORRESPONDENCE' sheets of
data/raw/DS05/BET Study Dataset.xlsx read-only (stdlib zip + XML), one row per dog
(BET001-BET150), and writes one JSON file with:

  dataset       metadata copied from datasets.jsonl and data/manifest.jsonl, plus cleaning notes
  variables     one entry per raw column, plus recoded helpers (sex, breed_group, complaint flags,
                panting, mucous-membrane flags, habitus score) and the authors' derived classes
                from the CORRESPONDENCE sheet (anaemia grade, left shift, ...; derived = true)
  subjects      one per dog; group_label = infection group (B. rossi only / B. rossi + E. canis / B. vogeli only)
  observations  one per subject x variable with a value (time_point '' - single admission visit)

Every cleaning rule is recorded in the dataset notes or the variable description, so the
loader and the UI can show them. The raw file is never modified.

Usage (from core/): python -I scripts/tidy_ds05.py
"""
import collections
import datetime as dt
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = "DS05"
SRC = ROOT / "data" / "raw" / DATASET / "BET Study Dataset.xlsx"
OUT = ROOT / "data" / "tidy" / f"{DATASET}.json"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
SUBJECT_RE = re.compile(r"^BET\d{3}")  # a few IDs carry a note, e.g. "BET147 (B. rossi + E. canis)"
MIN_COMPLAINT = 8  # a complaint code becomes a flag variable when at least this many dogs carry it


# ---------------------------------------------------------------------------------------------------------
# xlsx reading (stdlib only, read-only)
# ---------------------------------------------------------------------------------------------------------

def col_index(ref):
    n = 0
    for ch in re.match(r"[A-Z]+", ref).group(0):
        n = n * 26 + ord(ch) - 64
    return n - 1


def read_workbook(path):
    """Returns {sheet name: [(row number, {column index: cell text})]}."""
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS):
            shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t")))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rmap = {r.get("Id"): r.get("Target") for r in rels}
    sheets = {}
    for s in wb.find("m:sheets", NS):
        rid = s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        target = rmap[rid]
        path_in_zip = target.lstrip("/") if target.startswith("/") else "xl/" + target
        root = ET.fromstring(z.read(path_in_zip))
        rows = []
        for r in root.findall(".//m:sheetData/m:row", NS):
            cells = {}
            for c in r.findall("m:c", NS):
                v = c.find("m:v", NS)
                if v is None:
                    inline = c.find("m:is", NS)
                    if inline is not None:
                        cells[col_index(c.get("r"))] = "".join(t.text or "" for t in inline.iter(f"{{{NS['m']}}}t")).strip()
                    continue
                text = shared[int(v.text)] if c.get("t") == "s" else v.text
                cells[col_index(c.get("r"))] = (text or "").strip()
            if cells:
                rows.append((int(r.get("r")), cells))
        sheets[s.get("name")] = rows
    return sheets


def to_num(text):
    if text is None or text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


# ---------------------------------------------------------------------------------------------------------
# Variable definitions
# ---------------------------------------------------------------------------------------------------------
# Raw columns of the 'Entire population' sheet. Fields: code, column, name, unit, type, domain,
# include_default, ref_low, ref_high, description, derived_from.
RAW_COLUMNS = [
    ("sex_status", 1, "Sex and neuter status", None, "C", "signalment", 0, None, None,
     "As recorded: MALE INTACT, FEMALE INTACT, FEMALE SPAYED, MALE CASTRATED. Tested through sex and neutered.", None),
    ("breed", 2, "Breed", None, "C", "signalment", 0, None, None,
     "As recorded (21 values, 90 crossbreeds). Tested through breed_group.", None),
    ("age_months", 3, "Age", "months", "N", "signalment", 1, None, None, None, None),
    ("weight_kg", 4, "Body weight", "kg", "N", "signalment", 1, None, None, None, None),
    ("primary_complaint", 5, "Primary complaint codes", None, "T", "clinical", 0, None, None,
     "Owner complaint codes separated by '/', as recorded (IA, L, WL, HgUr, V, ...). Tested through the complaint_* flags.", None),
    ("illness_days", 6, "Duration of illness", "days", "N", "clinical", 1, None, None,
     "Owner-reported. 'UNKNOWN' stored as missing.", None),
    ("temperature_c", 7, "Rectal temperature", "degrees C", "N", "clinical", 1, None, None, None, None),
    ("pulse", 8, "Pulse rate", "per minute", "N", "clinical", 1, None, None, None, None),
    ("respiratory_rate", 9, "Respiratory rate", "per minute", "N", "clinical", 1, None, None,
     "'P+' (panting, 24 dogs) stored as missing here and as panting = yes.", None),
    ("mucous_membranes", 10, "Mucous membranes", None, "T", "clinical", 0, None, None,
     "Free text as recorded. Tested through mm_pale and mm_icteric.", None),
    ("lymph_node_score", 11, "Peripheral lymph node enlargement", "score 0-2", "O", "clinical", 1, None, None,
     "0 none palpable, 1 one to three nodes palpable, 2 more than three nodes palpable.", None),
    ("ticks", 12, "Ticks present", None, "C", "clinical", 1, None, None, "present / absent at examination.", None),
    ("haemoglobin", 13, "Haemoglobin", "g/L", "N", "haematology", 1, 120, 180, None, None),
    ("rcc", 14, "Red cell count", "x10^12/L", "N", "haematology", 1, 5.5, 8.5, None, None),
    ("haematocrit", 15, "Haematocrit", "L/L", "N", "haematology", 1, 0.37, 0.55, None, None),
    ("mcv", 16, "Mean cell volume", "fL", "N", "haematology", 1, 60, 77, "Calculated index: haematocrit / RCC.", ["haematocrit", "rcc"]),
    ("mch", 17, "Mean cell haemoglobin", "pg", "N", "haematology", 1, None, None, "Calculated index: haemoglobin / RCC.", ["haemoglobin", "rcc"]),
    ("mchc", 18, "Mean cell haemoglobin concentration", "g/dL", "N", "haematology", 1, 32, 36,
     "Calculated index: haemoglobin / haematocrit.", ["haemoglobin", "haematocrit"]),
    ("rdw", 19, "Red cell distribution width", "%", "N", "haematology", 1, None, None, None, None),
    ("wcc", 20, "White cell count", "x10^9/L", "N", "haematology", 1, 6, 15, "Sum of the differential counts.",
     ["seg_neutrophils", "band_neutrophils", "lymphocytes", "monocytes", "eosinophils", "basophils"]),
    ("seg_neutrophils", 21, "Segmented neutrophils", "x10^9/L", "N", "haematology", 1, 3, 11.5, None, None),
    ("band_neutrophils", 22, "Band neutrophils", "x10^9/L", "N", "haematology", 1, 0, 0.5, None, None),
    ("lymphocytes", 23, "Lymphocytes", "x10^9/L", "N", "haematology", 1, 1, 4.8, None, None),
    ("monocytes", 24, "Monocytes", "x10^9/L", "N", "haematology", 1, 0.15, 1.35, None, None),
    ("eosinophils", 25, "Eosinophils", "x10^9/L", "N", "haematology", 1, 0.1, 1.25, "Zero in 84 of 150 dogs.", None),
    ("basophils", 26, "Basophils", "x10^9/L", "N", "haematology", 0, 0, 0.1, "Zero in 146 of 150 dogs; excluded from the default test set.", None),
    ("other_cells", 27, "Other cells", "x10^9/L", "N", "haematology", 0, None, None, "Zero in 148 of 150 dogs; excluded from the default test set.", None),
    ("platelets", 28, "Platelet count", "x10^9/L", "N", "haematology", 1, 200, 500, None, None),
    ("nrbc_per_100_wbc", 29, "Nucleated red cells", "per 100 WBC", "N", "haematology", 1, 0, 9, None, None),
    ("reticulocyte_pct", 30, "Reticulocytes", "%", "N", "haematology", 1, None, None, None, None),
    ("arc", 31, "Absolute reticulocyte count", "x10^9/L", "N", "haematology", 1, None, None,
     "Calculated: reticulocyte % x RCC.", ["reticulocyte_pct", "rcc"]),
    ("total_protein", 32, "Total serum protein", "g/L", "N", "biochemistry", 1, 56, 73, None, None),
    ("albumin", 33, "Albumin", "g/L", "N", "biochemistry", 1, 28, 41, None, None),
    ("globulin", 34, "Globulin", "g/L", "N", "biochemistry", 1, 20, 41, "Calculated: total protein - albumin.", ["total_protein", "albumin"]),
    ("pcr_b_rossi", 35, "Babesia rossi PCR", None, "C", "pathogen", 0, None, None, "positive in 149 of 150; no variance to test.", None),
    ("pcr_b_vogeli", 36, "Babesia vogeli PCR", None, "C", "pathogen", 0, None, None, "positive in 1 of 150.", None),
    ("pcr_e_canis", 37, "Ehrlichia canis PCR", None, "C", "pathogen", 0, None, None, "positive in 3 of 150; too few to test.", None),
    ("pcr_t_equi", 38, "Theileria equi PCR", None, "C", "pathogen", 0, None, None, "positive in 0 of 150.", None),
    ("date_collected", 39, "Date collected", None, "D", "time", 0, None, None, "DD/MM/YYYY in the file, 2021.", None),
    ("season", 40, "Season", None, "C", "time", 1, None, None, "Southern-hemisphere season of the admission date, as coded by the authors.", None),
]

SEASONS = {"Su": "Summer", "Au": "Autumn", "Wi": "Winter", "Sp": "Spring"}
BREED_GROUPS = {"CROSSBREED": "Crossbreed", "PITBULL": "Pitbull", "BOERBOEL": "Boerboel"}
INFECTION_GROUPS = {"Br_O": "B. rossi only", "Bv_O": "B. vogeli only", "Br_Ec": "B. rossi + E. canis"}

# Columns of the CORRESPONDENCE sheet. (code, column, name, description, kind) where kind is
# 'raw' for a measurement that only exists in this sheet and 'class' for the authors' derived categories.
CORRESPONDENCE_COLUMNS = [
    ("habitus_score", 13, "Habitus (mental status) score",
     "Admission mental status as graded by the authors: 4+ bright, alert and responsive; 3+ mildly depressed; "
     "2+ and 1+ severely depressed or collapsed. Stored as the number (1-4); higher is brighter.", "raw"),
    ("breed_fci_group", 8, "Breed group (authors' FCI-style grouping)",
     "Br_G gundog, Br_H hound, Br_P pastoral, Br_U utility, Br_To toy, Br_Te terrier, Br_W working, Br_NL not listed, Br_M mixed.", "class"),
    ("age_class", 10, "Age class", "Ag_1 under 12 months, Ag_2 12-24 months, Ag_3 over 24 months. Derived from age_months.", "class"),
    ("illness_class", 12, "Duration of illness class", "DI_1 1-3 days, DI_2 4-6 days, DI_3 over 7 days. Derived from illness_days.", "class"),
    ("habitus_class", 14, "Habitus class", "BAR bright alert responsive (4+), Mi_De mildly depressed (3+), De_Co depressed or collapsed (2+ or less). Derived from habitus_score.", "class"),
    ("anaemia_class", 16, "Anaemia grade", "Ht_N non-anaemic, Ht_Mi mild, Ht_Mo moderate, Ht_S severe, Ht_VS very severe. Derived from haematocrit.", "class"),
    ("wcc_class", 18, "White cell count class", "WCC_Lo leukopenia (<6), WCC_N normal (6-15), WCC_Hi leukocytosis (>15 x10^9/L). Derived from wcc.", "class"),
    ("band_class", 20, "Band neutrophil class", "BaN_N normal (0-0.5), BaN_H high (>0.5 x10^9/L). Derived from band_neutrophils.", "class"),
    ("left_shift", 22, "Left shift", "none, L_shft left shift (bands > 0.5), De_L_shift degenerative left shift (bands > segmented). Derived from the neutrophil counts.", "class"),
    ("monocyte_class", 24, "Monocyte class", "Mon_N normal or low (<1.35), Mon_Hi monocytosis (>1.35 x10^9/L). Derived from monocytes.", "class"),
    ("arc_class", 26, "Reticulocyte response class", "ARC_In inadequate (<80), ARC_Mi mild (80-150), ARC_Mo moderate (150-300), ARC_Ma marked (>300 x10^9/L). Derived from arc.", "class"),
    ("arc_class_2", 28, "Reticulocyte response class (second scheme)", "ARC_Lo low (<12.86), ARC_N normal (12.86-115.41), ARC_Hi reticulocytosis (>115.41 x10^9/L). Derived from arc.", "class"),
    ("globulin_class", 30, "Globulin class", "Glo_Lo low (<20), Glo_N normal (20-41), Glo_Hi high (>41 g/L). Derived from globulin.", "class"),
]

CLASS_PARENTS = {
    "age_class": ["age_months"], "illness_class": ["illness_days"], "habitus_class": ["habitus_score"],
    "anaemia_class": ["haematocrit"], "wcc_class": ["wcc"], "band_class": ["band_neutrophils"],
    "left_shift": ["band_neutrophils", "seg_neutrophils"], "monocyte_class": ["monocytes"],
    "arc_class": ["arc"], "arc_class_2": ["arc"], "globulin_class": ["globulin"], "breed_fci_group": ["breed"],
}


# ---------------------------------------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------------------------------------

def jl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def yes_no(flag):
    return "yes" if flag else "no"


def main():
    notes = []
    sheets = read_workbook(SRC)
    main_rows = sheets["Entire population"]
    corr_rows = sheets["CORRESPONDENCE"]

    header = {i: t for i, t in main_rows[0][1].items()}
    data_rows = [(rn, cells) for rn, cells in main_rows if SUBJECT_RE.match(cells.get(0, ""))]
    notes.append(f"'Entire population' sheet: header row 1, units row 2, {len(data_rows)} dog rows (BET001-BET150); "
                 "the summary rows below the data (e.g. '82/150 MALE INTACT') were ignored.")
    annotated = []
    for rn, cells in data_rows:
        if cells[0] != cells[0][:6]:
            annotated.append(cells[0])
            cells[0] = cells[0][:6]
    if annotated:
        notes.append("Subject IDs with a note in the cell were cut to the ID: " + "; ".join(annotated) + ".")

    corr_by_subject = {}
    for rn, cells in corr_rows:
        if SUBJECT_RE.match(cells.get(0, "")):
            cells[0] = cells[0][:6]
            corr_by_subject[cells[0]] = cells
    notes.append(f"'CORRESPONDENCE' sheet: {len(corr_by_subject)} dog rows read for habitus and the authors' derived classes; "
                 "the 'Crossbreed vs Purebreed' sheet repeats the same dogs and was not used.")

    variables = []
    observations = []
    subjects = []
    sort = 0

    def add_var(code, name, unit, dtype, domain, include, ref_low=None, ref_high=None, description=None,
                derived_from=None, derived=False, source_name=None):
        nonlocal sort
        sort += 1
        variables.append({
            "code": code, "name": name, "source_name": source_name, "unit": unit, "data_type": dtype,
            "domain": domain, "derived": bool(derived), "derived_from": derived_from, "include_default": bool(include),
            "ref_low": ref_low, "ref_high": ref_high, "description": description, "levels": None, "sort_order": sort,
        })

    def add_obs(subject, code, num=None, text=None, date=None):
        if num is None and text in (None, "") and date is None:
            return
        observations.append({"subject": subject, "variable": code, "time_point": "",
                             "value_num": num, "value_text": text, "value_date": date})

    # Raw columns
    for code, col, name, unit, dtype, domain, include, lo, hi, desc, parents in RAW_COLUMNS:
        add_var(code, name, unit, dtype, domain, include, lo, hi, desc, parents, source_name=header.get(col, "").strip())

    # Recoded helpers
    add_var("sex", "Sex", None, "C", "signalment", 1, description="Male / Female, from sex_status.")
    add_var("neutered", "Neutered", None, "C", "signalment", 0,
            description="yes / no, from sex_status. Only 7 of 150 dogs are neutered, so it is excluded from the default test set.")
    add_var("breed_group", "Breed group", None, "C", "signalment", 1,
            description="Crossbreed, Pitbull, Boerboel or Other purebred (every other breed, 21 dogs across 18 breeds).")
    add_var("purebred", "Purebred", None, "C", "signalment", 0, description="yes / no. Redundant with breed_group; excluded from the default test set.")
    add_var("panting", "Panting at examination", None, "C", "clinical", 1, description="yes where respiratory rate was recorded as 'P+'.")
    add_var("mm_pale", "Pale mucous membranes", None, "C", "clinical", 1,
            description="yes where the mucous membrane text contains 'PALE' (including 'PALE PINK'); 'PMG' and 'HYPERAEMIC' are no.")
    add_var("mm_icteric", "Icteric mucous membranes", None, "C", "clinical", 1,
            description="yes where the mucous membrane text contains 'ICTER' (icteric or slight icterus).")
    add_var("month", "Month of admission", "1-12", "N", "time", 0, description="From date_collected. Season is the tested form.")

    # Complaint flags: find codes carried by at least MIN_COMPLAINT dogs
    complaint_counts = collections.Counter()
    complaint_tokens = {}
    for rn, cells in data_rows:
        tokens = [t.strip().upper() for t in cells.get(5, "").split("/") if t.strip()]
        complaint_tokens[cells[0]] = tokens
        complaint_counts.update(set(tokens))
    complaint_codes = [c for c, n in complaint_counts.most_common() if n >= MIN_COMPLAINT]
    for c in complaint_codes:
        add_var(f"complaint_{c.lower()}", f"Primary complaint includes {c}", None, "C", "clinical", 1,
                description=f"yes where the primary complaint codes include '{c}' ({complaint_counts[c]} dogs). Code as recorded by the authors.")
    notes.append("Primary complaint codes with at least %d dogs became yes/no flags: %s. Rarer codes stay in the primary_complaint text only."
                 % (MIN_COMPLAINT, ", ".join(f"{c} ({complaint_counts[c]})" for c in complaint_codes)))

    # CORRESPONDENCE columns
    for code, col, name, desc, kind in CORRESPONDENCE_COLUMNS:
        if kind == "raw":
            add_var(code, name, "score 1-4", "O", "clinical", 1, description=desc, source_name="Mental status (habitus)")
        else:
            add_var(code, name, None, "C", "derived", 0, description=desc, derived_from=CLASS_PARENTS.get(code), derived=True)

    # Observations
    mismatches = 0
    for rn, cells in data_rows:
        sid = cells[0]
        corr = corr_by_subject.get(sid, {})
        group = INFECTION_GROUPS.get(corr.get(2, "").strip(), None)
        subjects.append({"code": sid, "group_label": group, "outcome_label": None})

        for code, col, name, unit, dtype, domain, include, lo, hi, desc, parents in RAW_COLUMNS:
            raw = cells.get(col, "")
            if dtype in ("N", "O"):
                add_obs(sid, code, num=to_num(raw))
            elif dtype == "T":
                add_obs(sid, code, text=raw or None)
            elif dtype == "D":
                m = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", raw)
                if m:
                    d = dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
                    add_obs(sid, code, date=d.isoformat())
                    add_obs(sid, "month", num=float(d.month))
            elif dtype == "C":
                if code == "season":
                    add_obs(sid, code, text=SEASONS.get(raw, raw or None))
                elif code == "ticks":
                    add_obs(sid, code, text={"0": "absent", "1": "present"}.get(raw))
                elif code.startswith("pcr_"):
                    add_obs(sid, code, text={"0": "negative", "1": "positive"}.get(raw))
                else:
                    add_obs(sid, code, text=raw or None)

        sex_status = cells.get(1, "").upper()
        if sex_status:
            add_obs(sid, "sex", text="Male" if sex_status.startswith("MALE") else "Female")
            add_obs(sid, "neutered", text=yes_no("SPAYED" in sex_status or "CASTRATED" in sex_status))
        breed = cells.get(2, "").upper()
        if breed:
            add_obs(sid, "breed_group", text=BREED_GROUPS.get(breed, "Other purebred"))
            add_obs(sid, "purebred", text=yes_no(breed != "CROSSBREED"))
        add_obs(sid, "panting", text=yes_no(cells.get(9, "").upper().startswith("P")))
        mm = cells.get(10, "").upper()
        if mm:
            add_obs(sid, "mm_pale", text=yes_no("PALE" in mm))
            add_obs(sid, "mm_icteric", text=yes_no("ICTER" in mm))
        for c in complaint_codes:
            add_obs(sid, f"complaint_{c.lower()}", text=yes_no(c in complaint_tokens[sid]))

        for code, col, name, desc, kind in CORRESPONDENCE_COLUMNS:
            raw = corr.get(col, "").strip()
            if kind == "raw":
                m = re.match(r"^(\d)\+?$", raw)
                add_obs(sid, code, num=float(m.group(1)) if m else None)
            elif code == "left_shift":
                add_obs(sid, code, text=raw or ("none" if corr else None))
            else:
                add_obs(sid, code, text=raw or None)

        # Sanity check: haematocrit should agree between the two sheets
        if corr and to_num(corr.get(15)) is not None and to_num(cells.get(15)) is not None \
                and abs(to_num(corr.get(15)) - to_num(cells.get(15))) > 1e-6:
            mismatches += 1
    notes.append(f"Haematocrit agrees between the two sheets for all dogs except {mismatches}.")
    notes.append("Numeric cells that hold text ('UNKNOWN', 'P+') are stored as missing for the numeric variable.")
    notes.append("MCV, MCH, MCHC, WCC, ARC and globulin are arithmetic functions of other columns (derived_from); "
                 "associations with their parents are flagged trivial by the experiment scripts.")

    # Level counts for categorical variables
    level_counts = collections.defaultdict(collections.Counter)
    for o in observations:
        if o["value_text"] is not None:
            level_counts[o["variable"]][o["value_text"]] += 1
    for v in variables:
        if v["data_type"] == "C":
            v["levels"] = dict(level_counts[v["code"]].most_common())

    # Dataset metadata
    ds = next(d for d in jl(ROOT / "datasets.jsonl") if d["dataset_id"] == DATASET)
    manifest = [m for m in jl(ROOT / "data" / "manifest.jsonl") if m["dataset_id"] == DATASET]
    dataset = {
        "code": DATASET,
        "title": ds["title"],
        "article_code": (ds.get("linked_articles") or [None])[0],
        "repository": ds.get("repository"),
        "source_record": ds.get("accession_or_doi") or ds.get("landing_url"),
        "licence": ds.get("licence"),
        "independent_source": ds.get("independent_source"),
        "species": ds.get("species"),
        "design": ds.get("design"),
        "source_file": SRC.relative_to(ROOT).as_posix(),
        "source_sha256": manifest[0]["sha256"] if manifest else None,
        "n_subjects": len(subjects),
        "notes": notes,
        "extracted_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "script": "scripts/tidy_ds05.py",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"dataset": dataset, "variables": variables, "subjects": subjects,
                               "observations": observations}, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"{DATASET}: {len(subjects)} subjects, {len(variables)} variables, {len(observations)} observations -> {OUT.relative_to(ROOT)}")
    for n in notes:
        print(" -", n)
    print("default test set:", ", ".join(v["code"] for v in variables if v["include_default"]))


if __name__ == "__main__":
    main()
