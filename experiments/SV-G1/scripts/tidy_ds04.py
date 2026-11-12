"""Tidy DS04 (necropsy liver study, B. rossi, Onderstepoort; SRC-G; article CB147). S-CB147 (the article supplement) is the
same 10 fatal dogs: it is used here only to confirm the IHC values.

Records: controls (4) have one record, timepoint 'single' (blood and liver taken at euthanasia). Fatal cases (10) have two
records: 'admission' (signalment, haematology and biochemistry; blood taken before treatment per CB147) and 'necropsy'
(liver IHC counts, special stains, histopathology scores).
Outcomes: died = 1 for every fatal case, 0 for controls; death_timing as written on the score sheets.
"""
import glob
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tidylib import (RAW, built_from_entry, check, dict_row, median, neutral_ids, num, read_docx_tables, read_xlsx, var,  # noqa: E402
                     write_dataset, sha256_bytes, repo_path)

DS = "DS04"
D = RAW / "DS04"
STATS = D / "Stats Tables.xlsx"
HAEM = D / "stats for haematology.xlsx"
HAEM2 = D / "stats for haematology (1).xlsx"
THESIS = D / "all tables from thesis.docx"
S147 = RAW / "S-CB147" / "PMC13283813_supplementaryFiles.zip"
S050 = RAW / "S-CB050" / "PMC7040022_supplementaryFiles.zip"

CONTROLS = ["2", "4", "9", "11"]
CASES = ["20", "50", "54", "59", "61", "88", "91", "106", "110", "117"]
MARKERS = ["CD3", "CD20", "CD204", "Iba-1", "MAC", "MUM"]
MNAME = {"CD3": "cd3", "CD20": "cd20", "CD204": "cd204", "Iba-1": "iba1", "MAC": "mac387", "MUM": "mum1"}
ZONES = {"CV": ("cl", "centrilobular (central vein)"), "MZ": ("mz", "midzonal"), "PT": ("pt", "portal tract")}
STAINS = {"MSB": "msb", "Pearls": "perls", "LFB": "lfb"}

# Signalment from the score sheets (free text). 'sheet' is the sheet whose text is used; the script asserts that the text
# holds the key words. Ages in years are converted to months (x12).
SIGNAL = {
    "20": dict(sheet="20.1", words=["GSD", "Died before Rx", "FS", "12y"], breed="German Shepherd Dog", sex="female", neuter="neutered", age=144, wt=None, timing="died before treatment", rx=None),
    "50": dict(sheet="50.1", words=["Boerboel", "Died before Rx", "MI", "2.5y", "30.6kg"], breed="Boerboel", sex="male", neuter="intact", age=30, wt=30.6, timing="died before treatment", rx=None),
    "54": dict(sheet="54.2", words=["Boerboel", "Died after Rx", "MI", "9m", "45.6kg"], breed="Boerboel", sex="male", neuter="intact", age=9, wt=45.6, timing="died after treatment", rx="diminazene (berenil), glucose, blood, fluids, oxygen, clopamon"),
    "59": dict(sheet="59.2", words=["GSD", "Died after Rx", "MI", "5 years", "34kg"], breed="German Shepherd Dog", sex="male", neuter="intact", age=60, wt=34.0, timing="died after treatment", rx="diminazene (berenil), blood, glucose, cerenia, fluids with potassium, clopamon, prednisolone"),
    "61": dict(sheet="61.1", words=["Rottweiler", "Died after Rx", "MI", "8 years", "36.4kg"], breed="Rottweiler", sex="male", neuter="intact", age=96, wt=36.4, timing="died after treatment", rx="blood, diminazene (berenil), cerenia, fluids"),
    "88": dict(sheet="88.2", words=["Pitbull", "DOA", "M.", "7m", "12kg"], breed="Pitbull Terrier", sex="male", neuter=None, age=7, wt=12.0, timing="dead on arrival", rx=None),
    "91": dict(sheet="91.1", words=["Boxer", "Died after Rx", "MI", "7 years", "26kg"], breed="Boxer", sex="male", neuter="intact", age=84, wt=26.0, timing="died after treatment", rx="diminazene (berenil), blood"),
    "106": dict(sheet="106.1", words=["Mixed", "Died after Rx", "M.", "3 year", "3kg"], breed="Mixed Breed", sex="male", neuter=None, age=36, wt=3.0, timing="died after treatment", rx="oxygen, blood, diminazene (berenil), furosemide (lasix), voluven"),
    "110": dict(sheet="110.1", words=["Cocker spaniel", "Died after Rx", "M.", "3 years"], breed="Cocker Spaniel", sex="male", neuter=None, age=36, wt=None, timing="died after treatment", rx="diminazene (berenil)"),
    "117": dict(sheet="117.1", words=["Great Dane", "Died on admission", "M.", "4 years", "43.2kg"], breed="Great Dane", sex="male", neuter=None, age=48, wt=43.2, timing="died on admission", rx=None),
    "2": dict(sheet="2.1", words=["6 months", "FI", "Pitbull", "6.5kg"], breed="Pitbull Terrier", sex="female", neuter="intact", age=6, wt=6.5),
    "4": dict(sheet="4.1", words=["7 months", "MI", "Pitbull", "12 kg"], breed="Pitbull Terrier", sex="male", neuter="intact", age=7, wt=12.0),
    "9": dict(sheet="9A.1", words=["3 years", "FI", "Africanis", "13kg"], breed="Africanis", sex="female", neuter="intact", age=36, wt=13.0),
    "11": dict(sheet="11A.1", words=["2 years", "FI", "Boerboel x", "23kg"], breed="Boerboel Cross", sex="female", neuter="intact", age=24, wt=23.0),
}

# CB147 article Table 3: median positive cells per HPF over all fields of the group, (infected, control).
ARTICLE_T3 = {
    ("CD3", "pt"): (12, 6), ("CD3", "mz"): (45.5, 16.5), ("CD3", "cl"): (5.0, 3),
    ("CD20", "pt"): (4, 1), ("CD20", "mz"): (9.0, 4.5), ("CD20", "cl"): (11.5, 1.5),
    ("CD204", "pt"): (10, 7.5), ("CD204", "mz"): (125.5, 69), ("CD204", "cl"): (14, 4.5),
    ("Iba-1", "pt"): (11, 9), ("Iba-1", "mz"): (142.4, 107.5), ("Iba-1", "cl"): (12, 6),
    ("MAC", "pt"): (23, 1), ("MAC", "mz"): (192, 22), ("MAC", "cl"): (16, 1),
    ("MUM", "pt"): (3.5, 2), ("MUM", "mz"): (4, 3), ("MUM", "cl"): (4.5, 1),
}

HAEM_COLS = [("rbc", "10^12/L", "Red cell count (x10^12/L)"), ("hct", "L/L", "Ht (L/L)"), ("retic_pct", "%", "Retic count %"),
             ("plt", "10^9/L", "Plt. (x10^9/L)"), ("wbc", "10^9/L", "WCC (x 10^9/L)"), ("neut_seg", "10^9/L", "Neutr.(x10^9/L)"),
             ("neut_band", "10^9/L", "Band (x10^9/L)"), ("lymph", "10^9/L", "Lymph. (x10^9/L)"), ("mono", "10^9/L", "Monoc. (x10^9/L)")]
BIO_COLS = [("tsp", "g/L", "TSP (g/L)"), ("albumin", "g/L", "Albumin (g/L)"), ("globulin", "g/L", "Globulin"), ("alt", "U/L", "ALT (U/L)"),
            ("alp", "U/L", "ALP (U/L)"), ("bilirubin_total", "umol/L", "Tot. bilirubin (umol/L)"), ("glucose", "mmol/L", "Glucose (mmol/L)"),
            ("urea", "mmol/L", "Urea Nitr. (mmol/L)"), ("bile_acids_pre", "umol/L", "Bile acid pre (umol/L)"),
            ("bile_acids_post", "umol/L", "Bile acid post (umol/L)")]


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def ffill_case(rows, start):
    """Rows of a Stats Tables sheet: case number in column 1 on the first of each dog's rows."""
    out, cur = [], None
    for r in rows[start:]:
        if not r or len(r) < 3:
            continue
        if r[1]:
            cur = str(r[1]).strip()
        out.append((cur, r))
    return out


def read_score_sheet(path):
    """Histopathology score sheet: returns (s_number text, signalment, icterus text, {item key: raw score}, total, n col16)."""
    rows = list(read_xlsx(str(path)).values())[0]
    rows = [list(r) + [None] * 20 for r in rows]
    snum = (rows[1][1] or "").strip()
    sig = (rows[2][1] or "").strip()
    ict = (rows[3][1] or "").strip()
    items, zone, s1, s2 = {}, None, None, None
    total = None
    n16 = 0
    for r in rows:
        c0 = (r[0] or "").strip() if isinstance(r[0], str) else r[0]
        if c0 in ("Periportal", "Midzonal", "Centrilobular") and r[1]:
            zone, s1, s2 = c0, None, None
        if zone is None:
            continue
        if r[16] not in (None, ""):
            n16 += 1
        if not (r[1] or r[2] or r[3]):
            if r[14] not in (None, ""):
                total = r[14]
            continue
        if r[1]:
            s1, s2 = r[1].strip(), None
        if r[2]:
            s2 = r[2].strip()
        s3 = r[3].strip() if r[3] else None
        key = (zone, s1, s2 if (r[2] or r[3]) else None, s3)
        items[key] = r[14]
    return snum, sig, ict, items, total, n16


def main():
    notes, flags = [], []
    wb = read_xlsx(str(STATS))

    # ---------------- IHC (3 fields per zone per dog)
    ihc = ffill_case(wb["IHC"], 2)
    hdr = wb["IHC"][1]
    ihc_order = []
    fields = {}          # (case, var) -> [values]
    blanks = 0
    groupflag = {}
    for case, r in ihc:
        if case not in ihc_order:
            ihc_order.append(case)
        groupflag[case] = r[2]
        for j in range(3, 21):
            zone, mk = hdr[j].split(" ", 1)
            name = f"ihc_{MNAME[mk]}_{ZONES[zone][0]}"
            v = num(r[j]) if j < len(r) else None
            if v is None:
                blanks += 1
            fields.setdefault((case, name), []).append(v)
    n_ihc_cells = sum(len(v) for v in fields.values())
    if set(ihc_order) != set(CONTROLS + CASES):
        raise SystemExit(f"IHC case numbers differ: {ihc_order}")
    if any(groupflag[c] != "0" for c in CONTROLS) or any(groupflag[c] != "1" for c in CASES):
        raise SystemExit("IHC Control/Case flag does not match the case lists")
    # per-dog means, compared with the authors' Sheet1 averages
    sheet1 = {str(r[1]).strip(): r for r in wb["Sheet1"][2:16] if r and len(r) > 2 and r[1]}
    h1 = wb["Sheet1"][1]
    s1_diff = []
    for c in CONTROLS + CASES:
        for j in range(2, 20):
            zone, mk = h1[j].split(" ", 1)
            name = f"ihc_{MNAME[mk]}_{ZONES[zone][0]}"
            m = mean(fields[(c, name)])
            a = num(sheet1[c][j])
            if (m is None) != (a is None) or (m is not None and abs(m - a) > 1e-6):
                s1_diff.append(f"case {c} {zone} {mk}: fields {fields[(c, name)]}, Sheet1 {round(a, 2)}")

    # ---------------- special stains
    ss = ffill_case(wb["Special Stains"], 2)
    hss = wb["Special Stains"][1]
    sfields = {}
    for case, r in ss:
        for j in range(3, 12):
            zone, st = hss[j].split(" ", 1)
            sfields.setdefault((case, f"stain_{STAINS[st]}_{ZONES[zone][0]}"), []).append(num(r[j]) if j < len(r) else None)

    # ---------------- histology total scores (Score Sheet) and per-session score sheets
    scores = {}
    for case, r in ffill_case(wb["Score Sheet"], 2):
        scores.setdefault(case, []).append(num(r[3]))
    sheet_files = sorted(p for p in glob.glob(str(D / "*126*.xlsx")))
    sessions = {}      # case -> list of (file, items)
    blank_files, total_mismatch, sig_text, col16_files, nonnum = [], [], {}, [], []
    for p in sheet_files:
        fn = Path(p).name
        m = re.match(r"^(\d+)(A?)\.0?(\d)", fn)
        case = m.group(1)
        snum, sig, ict, items, total, n16 = read_score_sheet(p)
        sig_text[fn.split(" ")[0]] = (sig, ict)
        vals = {k: v for k, v in items.items() if v not in (None, "")}
        if not vals:
            blank_files.append(fn)
            continue
        if n16:
            col16_files.append(fn)
        for k, v in vals.items():
            if num(v) is None:
                nonnum.append(f"{fn}: {k} = {v!r}")
        fname_total = int(re.search(r"(\d+)-126", fn).group(1))
        s = sum(num(v) for v in vals.values() if num(v) is not None)
        if num(total) != fname_total or abs(s - fname_total) > 1e-9:
            total_mismatch.append(f"{fn}: file name {fname_total}, total cell {total}, sum of items {s:g}")
        sessions.setdefault(case, []).append((fn, vals))
    # item variables
    item_keys = []
    for case in sessions:
        for fn, vals in sessions[case]:
            for k in vals:
                if k not in item_keys:
                    item_keys.append(k)
    zcode = {"Periportal": "pp", "Midzonal": "mz", "Centrilobular": "cl"}
    item_name = {}
    for k in item_keys:
        zone, a, b, c = k
        parts = [p for p in (a, b, c) if p]
        nm = "histo_" + zcode[zone] + "_" + slug(" ".join(parts).replace("Pigments:", "pigment"))
        nm = nm.replace("haematopoeisis", "haematopoiesis").replace("haemmorrhage", "haemorrhage")
        item_name[k] = nm
    if len(set(item_name.values())) != len(item_name):
        raise SystemExit("histology item names collide")

    # ---------------- haematology / biochemistry (no case numbers)
    hw, hw2 = read_xlsx(str(HAEM)), read_xlsx(str(HAEM2))
    def data_rows(sheet):
        return [r for r in sheet[1:] if r and r[0] in ("0", "1")]
    same_copy = all(data_rows(hw[s]) == data_rows(hw2[s]) for s in ("Haematology", "Biochemistries"))
    extra_rows = {s: len([r for r in hw[s] if any(r)]) - len([r for r in hw2[s] if any(r)]) for s in ("Haematology", "Biochemistries")}
    hrows, brows = data_rows(hw["Haematology"]), data_rows(hw["Biochemistries"])
    ctrl_order = [c for c in ihc_order if c in CONTROLS]
    case_order = [c for c in ihc_order if c in CASES]
    flag_seq = [r[0] for r in hrows]
    if flag_seq != ["0"] * 4 + ["1"] * 10 or [r[0] for r in brows] != flag_seq:
        raise SystemExit(f"unexpected haematology group flags {flag_seq}")
    join = ctrl_order + case_order     # row i of the haematology sheets -> case number (by the IHC sheet order)
    blood = {}
    censored = {}
    zero_to_null = []
    for i, case in enumerate(join):
        hr, br = hrows[i], brows[i]
        v = {}
        for j, (name, _, _) in enumerate(HAEM_COLS, start=1):
            v[name] = num(hr[j]) if j < len(hr) else None
        for j, (name, _, _) in enumerate(BIO_COLS, start=1):
            raw = br[j].strip() if j < len(br) and br[j] is not None else None
            if raw is None or raw == "":
                v[name] = None
            elif raw == "x":
                v[name] = None
            elif raw.startswith("<"):
                v[name] = num(raw[1:])
                censored.setdefault(case, {})[name] = "floor"
            elif raw.startswith(">"):
                v[name] = num(raw[1:])
                censored.setdefault(case, {})[name] = "ceiling"
            else:
                v[name] = num(raw)
            if v[name] == 0 and name in ("bilirubin_total", "glucose", "urea", "bile_acids_pre"):
                zero_to_null.append(f"{name} ({'control' if case in CONTROLS else 'fatal case'})")
                v[name] = None
        blood[case] = v
        blood[case]["_raw_glob"] = br[3] if len(br) > 3 else None
        blood[case]["_tsp_alb"] = (num(br[1]), num(br[2]))

    # ---------------- S-CB050 linkage (values only)
    s050_bytes = zipfile.ZipFile(S050).read("Table_1.DOCX")
    s050 = {r[0].strip(): r for t in read_docx_tables(s050_bytes) for r in t if r and r[0].strip() in ("126", "127", "131")}
    link = {}
    for sc, r in s050.items():
        trip = tuple(num(x) for x in r[6:9])
        age, wt = num(r[1]), num(r[2])
        hits = [c for c in CASES if (blood[c]["wbc"], blood[c]["neut_seg"], blood[c]["neut_band"]) == trip]
        link[sc] = {"wbc_seg_band": trip, "s050_age_months": age, "s050_weight_kg": wt, "ds04_case_by_join": hits,
                    "ds04_signalment_of_that_case": [(SIGNAL[h]["age"], SIGNAL[h]["wt"]) for h in hits]}

    # ---------------- signalment assertions
    sig_conflicts = []
    for case, s in SIGNAL.items():
        text = sig_text[s["sheet"]][0]
        for w in s["words"]:
            if w not in text:
                raise SystemExit(f"signalment of {case} ({s['sheet']}): '{w}' not in '{text}'")
    for key in sorted(sig_text):
        case = re.match(r"^(\d+)", key).group(1)
        sig_conflicts.append((case, key, sig_text[key][0]))

    # ---------------- build records
    ids = neutral_ids(DS, CONTROLS + CASES)
    records = []
    def tissue_values(case):
        v = {}
        for (c, name), xs in fields.items():
            if c == case:
                v[name] = mean(xs)
        for (c, name), xs in sfields.items():
            if c == case:
                v[name] = mean(xs)
        sc = [x for x in scores.get(case, []) if x is not None]
        v["histo_total_score"] = mean(sc)
        v["histo_n_scorings"] = len(sc)
        sess = sessions.get(case, [])
        for k, nm in item_name.items():
            xs = [num(vals[k]) for fn, vals in sess if k in vals]
            v[nm] = mean(xs)
        return v
    def admission_values(case):
        s = SIGNAL[case]
        v = {"breed": s["breed"], "sex": s["sex"], "neuter": s["neuter"], "age_months": s["age"], "weight_kg": s["wt"],
             "mucous_membranes_text": sig_text[s["sheet"]][1] or None}
        if case in CASES:
            v["treatment_text"] = s["rx"]
        v.update({k: x for k, x in blood[case].items() if not k.startswith("_")})
        return v
    for case in CONTROLS:
        v = admission_values(case)
        v.update(tissue_values(case))
        records.append({"dog_id": ids[case], "group": "control", "timepoint": "single", "day": None,
                        "values": v, "censored": censored.get(case, {})})
    for case in CASES:
        records.append({"dog_id": ids[case], "group": "infected", "timepoint": "admission", "day": None,
                        "values": admission_values(case), "censored": censored.get(case, {})})
        records.append({"dog_id": ids[case], "group": "infected", "timepoint": "necropsy", "day": None,
                        "values": tissue_values(case), "censored": {}})
    records.sort(key=lambda r: (r["dog_id"], r["timepoint"]))

    # ---------------- variables and dictionary
    variables, drows = [], []
    def add(name, unit, original, conversion="", note=""):
        variables.append(var(name, unit, original))
        drows.append(dict_row(name, DS, original, unit, conversion, note))
    add("breed", "text", "Signalment (score sheet)", "free text -> breed name", "From the score-sheet signalment line.")
    add("sex", "male/female", "Signalment (score sheet)", "M/MI/FI/FS -> male/female", "")
    add("neuter", "intact/neutered", "Signalment (score sheet)", "MI/FI -> intact, FS -> neutered; 'M' alone -> null", "")
    add("age_months", "months", "Signalment (score sheet)", "years x12", "")
    add("weight_kg", "kg", "Signalment (score sheet)", "", "Missing for cases 20 and 110 in the sheets.")
    add("mucous_membranes_text", "text", "Hx of icteric mucous membranes (absent / Present)", "", "Free text as written (colour, or 'Absent' in controls).")
    add("treatment_text", "text", "Signalment (score sheet)", "", "Fatal cases only: treatments listed on the sheet; given after the blood sample. Null = none listed.")
    for name, unit, orig in HAEM_COLS:
        add(name, unit, f"stats for haematology.xlsx / Haematology: {orig}", "",
            "Mature (segmented) neutrophils." if name == "neut_seg" else ("Zero in 6 of 10 fatal cases: true zero or not done is unknown." if name == "retic_pct" else ""))
    for name, unit, orig in BIO_COLS:
        nt = {"bilirubin_total": "0 in all 4 controls = not measured (CB147) -> null.",
              "glucose": "0 in all 4 controls = not measured (CB147) -> null.",
              "urea": "0 in 3 fatal cases -> null (placeholder; the article medians exclude them).",
              "bile_acids_pre": "0 in 3 fatal cases -> null (placeholder; the article medians exclude them). '<1' -> 1 with censored floor.",
              "bile_acids_post": "Controls only. '<1' -> 1 floor, '>148' -> 148 ceiling.",
              "globulin": "'x' in one fatal case -> null.",
              "urea_": ""}.get(name, "")
        add(name, unit, f"stats for haematology.xlsx / Biochemistries: {orig}", "", nt)
    for mk in MARKERS:
        for zc, (z, zl) in ZONES.items():
            add(f"ihc_{MNAME[mk]}_{z}", "positive cells per HPF", f"Stats Tables.xlsx / IHC: {zc} {mk}",
                "mean of the 3 high-power fields (blank fields ignored)", f"{mk} positive cells, {zl}.")
    for st, s in STAINS.items():
        for zc, (z, zl) in ZONES.items():
            add(f"stain_{s}_{z}", "score or count per HPF (scale undocumented)", f"Stats Tables.xlsx / Special Stains: {zc} {st}",
                "mean of the 3 fields", f"{st} stain, {zl}. MSB is 0/1 in the file; Perls and LFB look like counts.")
    add("histo_total_score", "points (out of 126)", "Stats Tables.xlsx / Score Sheet: Score out of 126", "mean of the dog's scoring sessions",
        "Sum of the ordinal item scores of one session; 2-4 unblinded repeat scorings per dog.")
    add("histo_n_scorings", "count", "Stats Tables.xlsx / Score Sheet", "number of sessions listed", "")
    for k, nm in item_name.items():
        add(nm, "ordinal 0-3 (mean of sessions)", "score sheet: " + " / ".join(p for p in k if p), "mean over the dog's populated score sheets, 'Score' column",
            "Present only in the control 'A' template." if "intravascular" in nm or "extravascular" in nm else "")

    # ---------------- notes
    ctrl_join = ", ".join(f"row {i + 1} = control {c}" for i, c in enumerate(ctrl_order))
    case_join = ", ".join(f"row {i + 5} = case {c}" for i, c in enumerate(case_order))
    notes += [
        "One tidy dataset for DS04 and S-CB147 (same 10 fatal dogs). 14 dogs: controls 2, 4, 9, 11; fatal cases 20, 50, 54, 59, 61, "
        "88, 91, 106, 110, 117. Controls have one record (timepoint 'single'); fatal cases have an 'admission' record (signalment, "
        "blood) and a 'necropsy' record (liver).",
        "Blood timepoint: CB147 states that serum and EDTA blood were taken before any treatment, so blood values are 'admission'.",
        f"Haematology/biochemistry join. The two haematology sheets have no case number, only a 0/1 group flag (4 controls then 10 "
        f"cases). Rows were joined to case numbers by the order of the IHC sheet in Stats Tables.xlsx ({ctrl_join}; {case_join}). "
        "Evidence: (1) the WBC, segmented and band neutrophil counts of case rows 1, 5 and 6 equal S-CB050 cases 126, 127 and 131 "
        "(see linkage below), and S-CB050 gives those dogs age 30 months/30.6 kg, 9 months/45.6 kg and 60 months/34 kg, which is "
        "the signalment of DS04 cases 50, 54 and 59, the 1st, 5th and 6th cases in the IHC order (chance of three such hits under "
        "a random order: 1 in 720); (2) the two dogs whose sheets record non-icteric mucous membranes (88 cyanotic, 106 white) get "
        "the two lowest bilirubins (7.2 and 9.4 umol/L); every dog recorded as icteric gets 15.4 umol/L or more. Confidence: high for the fatal "
        "cases. The controls (rows 1-4 -> 2, 4, 9, 11) follow the same rule but no value confirms them: moderate confidence.",
        f"'stats for haematology (1).xlsx' has the same data rows as 'stats for haematology.xlsx' (identical: {same_copy}); it lacks "
        f"the summary rows below the data (extra non-empty rows in the first copy: {extra_rows}). Only the first copy is used.",
        "Linkage to S-CB050 (do not pool): fatal cases 50, 54 and 59 here are S-CB050 cases 126, 127 and 131 (the three deaths of "
        "the 2014 cohort), confirmed by identical WBC / segmented / band counts and by age and weight. DS04 is not independent of SRC-A.",
        "S-CB147 (Table_2.DOCX of the article supplement) lists per-case IHC values for the same 10 cases and group medians for "
        "controls. All values were compared with the per-dog means computed here (checks file). S-CB147 adds no per-dog value that "
        "is not in DS04; its Table_1.DOCX is the blank scoring rubric. No value was taken from S-CB147.",
        f"IHC: 3 high-power fields per zone per dog (rows of the IHC sheet). Per-dog value = mean of the non-blank fields; "
        f"{blanks} of {n_ihc_cells} field cells are blank. The authors' 'Sheet1' averages agree with these means "
        f"except: {'; '.join(s1_diff) or 'none'}. FLAG (kept as computed here): in the first, the authors divided by 3 with a blank field (blank counted as 0); the second does not follow from the fields. The thesis tables and S-CB147 Table_2 carry the authors' values (7.3 and 14.5). The thesis and S-CB147 call the per-case values 'median number of positive cells/HPF', but they "
        "equal the mean of the fields (e.g. values in thirds); the zone-level 'total medians' are medians over all fields of the group.",
        "Sheet1 has a stray summary row and two stray case numbers (88, 106) below the data; 'Total Phenotypes' is the sum over "
        "zones per field and is not used (derivable).",
        "Special stains (MSB, Perls, LFB): 3 fields per zone per dog; per-dog mean. The scale is not documented (MSB is 0/1; Perls "
        "and LFB look like counts).",
        f"Histopathology: {len(sheet_files)} score sheets. Blank templates not used: {', '.join(blank_files)}. Item scores are read "
        "from the 'Score' column and averaged over the dog's populated sheets (repeat, unblinded scoring sessions of the same "
        "specimen, not time points). Controls were scored mostly in January to early March 2022 and cases in March to April 2022 "
        "(scorer drift is confounded with group). Narrative fields (autolysis, lesion distribution, congestion, haemorrhage, which "
        "are marked by highlighting, not numbers) are not read.",
        "Two sheet templates: the control 'A' sheets (2A, 4A, 9A, 11A; January-February 2022) split extramedullary haematopoiesis "
        "into intravascular and extravascular and lack the periportal 'Sinusoids/Space of Disse oedema' row in some sheets; the "
        "other sheets have one extramedullary haematopoiesis item. Both forms are kept as separate variables (null where the "
        "template lacks them). So item sums are not on one scale across templates.",
        f"An unlabelled second score column (column Q) is filled in {len(col16_files)} sheets ({', '.join(col16_files)}); it is "
        "undocumented and not used.",
        "histo_total_score = mean of the 'Score out of 126' values in the Score Sheet (all listed sessions). The Score Sheet lists "
        "a third scoring of control 11 (30) with no sheet file, and 68 for case 88 whose sheet (88.1) is a blank template; these "
        "totals are kept in histo_total_score, while the item means use only populated sheets.",
        ("Session totals: every populated sheet's total cell equals its file-name total and the sum of its items."
         if not total_mismatch else "FLAG (kept as reported): session totals that do not agree: " + "; ".join(total_mismatch) + "."),
        ("Non-numeric item scores: none." if not nonnum else "FLAG (stored as null): non-numeric item scores: " + "; ".join(nonnum) + "."),
        "Signalment comes from the score sheets (free text) and is the same in the dog's sheets except for the control sheets below. "
        "Ages in years were converted to months (x12). 'M' without I/C -> neuter null.",
        "FLAG (resolved by the article): control 4 has two signalments: sheets 4.1 and 4A.3 say 'Unknown. 7 months. MI. Pitbull. "
        "12 kg' (the same as case 88's signalment), sheets 4A.1 and 4A.2 say 'Dexter. 3 years. MI. JRT. 7kg'. Control 9: sheets "
        "9A.1-9A.2 say 'Teddy. 3 years. FI. Africanis. 13kg', 9A.3 says '... Bull terrier. 23kg'. The CB147 control means and "
        "medians (age 18.3/15.5 months, weight 13.6/12.5 kg, breeds Pitbull, Africanis, Boerboel) are reproduced only with "
        "control 4 = Pitbull 7 months 12 kg and control 9 = Africanis 13 kg, so those are used; the other texts are treated as "
        "template carry-over. All repeat scorings stay assigned to the case number of the Score Sheet.",
        "FLAG (kept as reported): the fatal cases' ages from the sheets (mean 55.0, median 42 months) do not reproduce the CB147 "
        "mean 52.8 and median 50 months, and their weights (8 dogs) give median 32.3 kg against the article's 34 kg (the mean "
        "28.9 kg agrees). The ages are kept as written on the sheets; one or more ages in the article's source must differ.",
        "FLAG (kept as reported): case 106 weighs 3 kg at 3 years (mixed breed). It is consistent with the article's mean weight.",
        "FLAG (kept as reported): case 88 is 'DOA' on its sheet; the same number 88 is in the DS07 'uncomplicated' list (data.md "
        "linkage facts; unverified numbering link).",
        "Zero as a missing code: " + ", ".join(sorted(set(zero_to_null))) + " zeros were set to null (bilirubin and glucose: not "
        "measured in controls per CB147 Table 2; urea and pre-prandial bile acids: 3 fatal cases each, and the CB147 medians 28.3 "
        "and 22 are reproduced only without these zeros; the thesis medians 20.7 and 8.5 include them).",
        "FLAG (kept as reported): reticulocyte % is 0 in 6 of 10 fatal cases; true zero or not done is unknown.",
        "FLAG (kept as reported): monocytes 0 x10^9/L in one fatal case.",
        "FLAG (stored as null): globulin 'x' in one fatal case (its TSP minus albumin is "
        f"{round(blood[case_order[2]]['_tsp_alb'][0] - blood[case_order[2]]['_tsp_alb'][1], 1)} g/L)." if blood[case_order[2]]["_raw_glob"] == "x"
        else "Globulin 'x' in one fatal case stored as null.",
        "Censored: bile acids '<1' -> 1 (floor) and '>148' -> 148 (ceiling); see 'censored' in the records.",
        "Bile acids post-prandial: controls only (none in fatal cases).",
        "Thesis text vs data: the thesis table gives WCC maximum 105.6 and band minimum 1 x10^9/L; the data hold 103.55 and 0.51. "
        "The data values are kept.",
        "Units: urea is 'Urea Nitr. (mmol/L)' in the file, stored as urea mmol/L as written.",
        "All infected dogs are fatal: there is no outcome contrast within infected dogs. The outcome file has died (all 1 for "
        "cases) and the death timing text.",
    ]

    features = {"dataset_id": DS, "independent_source": "SRC-G", "species": "B. rossi",
                "built_from": [built_from_entry(STATS), built_from_entry(HAEM)] +
                              [built_from_entry(Path(p)) for p in sheet_files],
                "variables": variables, "records": records, "cleaning_notes": notes}

    orecs = []
    for case in CONTROLS + CASES:
        s = SIGNAL[case]
        orecs.append({"dog_id": ids[case], "original_id": case,
                      "values": {"died": 1 if case in CASES else 0, "death_timing": s.get("timing")}})
    outcomes = {"dataset_id": DS, "outcomes": [
        {"name": "died", "definition": "Fatal B. rossi case: died (7) or euthanised for a very grave prognosis (3) at OVAH (CB147); "
                                       "which dogs were euthanised is not in the files. 0 = healthy control (euthanised for welfare, not disease).",
         "includes_euthanasia": True},
        {"name": "death_timing", "definition": "As written on the score sheet: died before treatment, died on admission, dead on arrival, "
                                               "died after treatment. Null for controls.", "includes_euthanasia": True}],
        "records": orecs}

    # ---------------- checks
    def grp(name, cases, src=blood):
        return [src[c][name] for c in cases]
    def field_median(name, cases):
        return median([x for c in cases for x in fields[(c, name)]])
    thesis = read_docx_tables(str(THESIS))
    t_inf = {}
    cur = None
    for r in thesis[10][2:]:
        cur = r[0] or cur
        t_inf[(cur, r[1])] = num(r[2].split("(")[0])
    t_ctl = {}
    cur = None
    for r in thesis[2][1:]:
        cur = r[0] or cur
        t_ctl[(cur, r[1])] = num(r[2].split("(")[0])
    mk_t = {"CD3": "CD3", "CD20": "CD20", "CD204": "CD204", "Iba-1": "Iba-1", "MAC": "MAC387", "MUM": "MUM-1"}
    zl_t = {"PT": "Portal tract", "MZ": "Midzonal", "CV": "Centrilobular"}
    med_bad_inf, med_bad_ctl = [], []
    for mk in MARKERS:
        for zc, (z, _) in ZONES.items():
            nm = f"ihc_{MNAME[mk]}_{z}"
            a, b = field_median(nm, CASES), t_inf[(mk_t[mk], zl_t[zc])]
            if abs(a - b) > 0.05:
                med_bad_inf.append(f"{nm}: {a} vs {b}")
            a, b = field_median(nm, CONTROLS), t_ctl[(mk_t[mk], zl_t[zc])]
            if abs(a - b) > 0.05:
                med_bad_ctl.append(f"{nm}: {a} vs {b}")
    # S-CB147 Table_2 per-case values
    t2 = read_docx_tables(zipfile.ZipFile(S147).read("Table_2.DOCX"))
    s147_n = 0
    s147_bad = []
    zmap = {"Portal tract": "pt", "Midzonal": "mz", "Centrilobular": "cl"}
    for mk, tb in zip(MARKERS, t2):
        cur = None
        for r in tb[2:]:
            if r[0].startswith("Case"):
                cur = r[0].split()[1]
            elif r[0].startswith("Total"):
                cur = None
            if cur is None:
                continue
            s147_n += 1
            mine = mean(fields[(cur, f"ihc_{MNAME[mk]}_{zmap[r[1]]}")])
            if abs(round(mine, 1) - num(r[2])) > 0.051:
                s147_bad.append(f"case {cur} {MNAME[mk]} {zmap[r[1]]}: S-CB147 {r[2]}, mean of fields here {round(mine, 2)}")
    art_bad_inf, art_bad_ctl = [], []
    for (mk, z), (vi, vc) in ARTICLE_T3.items():
        nm = f"ihc_{MNAME[mk]}_{z}"
        a = field_median(nm, CASES)
        if abs(a - vi) > 0.15:
            art_bad_inf.append(f"{nm}: {a} vs {vi}")
        a = field_median(nm, CONTROLS)
        if abs(a - vc) > 0.15:
            art_bad_ctl.append(f"{nm}: {a} vs {vc}")
    notes.append(
        "IHC group medians: the medians over all fields of each group reproduce the published CB147 Table 3 (checks file). "
        f"The thesis tables ('all tables from thesis.docx') differ from the data in {len(med_bad_inf)} infected and "
        f"{len(med_bad_ctl)} control marker-zones (e.g. CD3 portal tract 9 vs 12 here and in the article); this answers the "
        "S-CB147 record's unreconciled CD3 difference: the article, not the thesis, matches the data.")
    ages = [SIGNAL[c]["age"] for c in CASES]
    wts = [SIGNAL[c]["wt"] for c in CASES if SIGNAL[c]["wt"] is not None]
    cages = [SIGNAL[c]["age"] for c in CONTROLS]
    cwts = [SIGNAL[c]["wt"] for c in CONTROLS]
    checks_list = [
        check("dogs", len({r["dog_id"] for r in records}), 14, source="data.md: 10 fatal + 4 controls"),
        check("fatal cases", sum(1 for r in orecs if r["values"]["died"] == 1), 10, source="data.md; CB147 note"),
        check("controls", sum(1 for r in orecs if r["values"]["died"] == 0), 4, source="data.md; CB147 note"),
        check("feature records (4 single + 10 admission + 10 necropsy)", len(records), 24, source="design of this file"),
        check("haematology copies identical (data rows)", same_copy, True, source="the two 'stats for haematology' files"),
        check("median RBC, fatal cases", round(median(grp("rbc", CASES)), 1), 2.1, source="CB147 full text, Results/Hematology: median 2.1 x10^12/L"),
        check("median haematocrit, fatal cases", round(median(grp("hct", CASES)), 1), 0.2, source="CB147 full text: median 0.2 L/L"),
        check("median platelets, fatal cases", median(grp("plt", CASES)), 40.5, tol=1e-9, source="CB147 full text: median 40.5 x10^9/L"),
        check("median ALT, fatal cases", median(grp("alt", CASES)), 86.5, tol=1e-9, source="CB147 Table 2: ALT 86.5 U/L"),
        check("median ALT, controls", median(grp("alt", CONTROLS)), 21.4, tol=1e-9, source="CB147 Table 2: ALT 21.4 U/L"),
        check("median urea, fatal cases (zeros as missing)", median(grp("urea", CASES)), 28.3, tol=1e-9, source="CB147 Table 2: urea 28.3 mmol/L"),
        check("median pre-prandial bile acids, fatal cases (zeros as missing)", median(grp("bile_acids_pre", CASES)), 22, tol=1e-9,
              source="CB147 Table 2: bile acids 22 umol/L"),
        check("median albumin, fatal cases", median(grp("albumin", CASES)), 19.6, tol=0.051, source="CB147 Table 2: albumin 19.6 g/L"),
        check("median TSP, controls", median(grp("tsp", CONTROLS)), 51.3, tol=1e-9, source="CB147 Table 2: TSP 51.3 g/L"),
        check("fatal cases female", sum(1 for c in CASES if SIGNAL[c]["sex"] == "female"), 1, source="CB147 full text: one female, nine males"),
        check("controls female", sum(1 for c in CONTROLS if SIGNAL[c]["sex"] == "female"), 3, source="CB147 full text: three females, one male"),
        check("mean age, controls (months)", sum(cages) / 4, 18.3, tol=0.051, source="CB147 full text: mean 18.3 months"),
        check("median age, controls (months)", median(cages), 15.5, tol=1e-9, source="CB147 full text: median 15.5 months"),
        check("mean weight, controls (kg)", sum(cwts) / 4, 13.6, tol=0.051, source="CB147 full text: mean 13.6 kg"),
        check("median weight, controls (kg)", median(cwts), 12.5, tol=1e-9, source="CB147 full text: median 12.5 kg"),
        check("mean weight, fatal cases (kg; 8 with a weight)", sum(wts) / len(wts), 28.9, tol=0.051, source="CB147 full text: mean 28.9 kg"),
        check("median weight, fatal cases (kg; 8 with a weight)", median(wts), 34, tol=1e-9, source="CB147 full text: median 34 kg"),
        check("mean age, fatal cases (months)", sum(ages) / 10, 52.8, tol=0.051, source="CB147 full text: mean 52.8 months"),
        check("median age, fatal cases (months)", median(ages), 50, tol=1e-9, source="CB147 full text: median 50 months"),
        check("IHC field-level medians (all fields of the group), fatal cases, vs CB147 Table 3 (18 marker-zones): mismatches",
              art_bad_inf, [], source="CB147 full text, Table 3 (median per HPF, infected)"),
        check("IHC field-level medians (all fields of the group), controls, vs CB147 Table 3 (18 marker-zones): mismatches",
              art_bad_ctl, [], source="CB147 full text, Table 3 (median per HPF, controls)"),
        check("S-CB147 Table_2 per-case IHC values equal the per-dog field means (rounded to 0.1): mismatches", s147_bad, [],
              source=f"S-CB147 Table_2.DOCX, {s147_n} values"),
        check("IHC per-dog means vs authors' Sheet1 averages: mismatches", s1_diff, [], source="Stats Tables.xlsx / Sheet1"),
        check("S-CB050 linkage: rows matching cases 126, 127, 131 by WBC/seg/band are cases 50, 54, 59 under the join",
              [link[k]["ds04_case_by_join"] for k in ("126", "127", "131")], [["50"], ["54"], ["59"]],
              source="data.md linkage facts; S-CB050 Table_1.DOCX"),
        check("S-CB050 age/weight of cases 126, 127, 131 equal DS04 signalment of the joined cases",
              [(link[k]["s050_age_months"], link[k]["s050_weight_kg"]) for k in ("126", "127", "131")],
              [(float(SIGNAL[c]["age"]), SIGNAL[c]["wt"]) for c in ("50", "54", "59")], source="S-CB050 Table_1.DOCX vs DS04 score sheets"),
    ]
    checks = {"dataset_id": DS, "checks": checks_list, "n_dogs": 14, "n_records": len(records),
              "s_cb050_linkage": link,
              "thesis_ihc_medians_that_differ_from_the_data": {"infected": med_bad_inf, "controls": med_bad_ctl},
              "check_sources": [{"file": repo_path(S147) + "!Table_2.DOCX", "sha256": sha256_bytes(zipfile.ZipFile(S147).read("Table_2.DOCX"))},
                                {"file": repo_path(S050) + "!Table_1.DOCX", "sha256": sha256_bytes(s050_bytes)},
                                built_from_entry(THESIS), built_from_entry(HAEM2)],
              "haematology_join": {"rule": "row order of the haematology sheets = case order of the IHC sheet in Stats Tables.xlsx",
                                   "rows_to_cases": join,
                                   "confidence": "high for fatal cases (3 of 10 confirmed by S-CB050 values and signalment; bilirubin "
                                                 "consistent with recorded icterus); moderate for controls (order only)"}}
    write_dataset(features, outcomes, drows, checks)


if __name__ == "__main__":
    main()
