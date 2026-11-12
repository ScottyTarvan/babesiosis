"""SV-07 linkage audit. Reads raw files under /core/data/raw (read-only) and one SV-G1 tidy features file (DS05, the chance baseline).
Writes out/: linkage.csv, results.json and plot-ready CSV files. Standard library only (Python 3.12). Spec: ../spec.md.
"""
import csv
import gzip
import hashlib
import itertools
import json
import math
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
EXP = HERE.parent
ROOT = EXP.parent
RAW = ROOT / "core" / "data" / "raw"
MD = ROOT / "core" / "data" / "markdown"
OUT = HERE / "out"
sys.path.insert(0, str(EXP / "shared" / "io"))
from rawio import fnum, read_docx_tables, read_xlsx  # noqa: E402

F_S050 = RAW / "S-CB050" / "PMC7040022_supplementaryFiles.zip"
F_HAEM = RAW / "DS04" / "stats for haematology.xlsx"
F_STATS = RAW / "DS04" / "Stats Tables.xlsx"
F_THESIS = RAW / "DS04" / "all tables from thesis.docx"
F_DS03N = RAW / "DS03" / "Babesia Retics_Natural inf and cont_dissertation.xlsx"
F_DS02 = RAW / "DS02" / "B.Atkinson_Experimental Babesia study raw data.xlsx"
F_DS06 = RAW / "DS06" / "GSE167201_raw_counts.txt.gz"
F_DS07 = RAW / "DS07" / "sample_list.xlsx"
F_DS05T = EXP / "shared" / "tidy" / "DS05.features.json"
F_SPEC = HERE / "spec.md"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rel(p):
    return "/" + Path(p).resolve().relative_to(ROOT).as_posix()


def agree(a, b):
    """Rounding tolerance of the spec: |a-b| <= max(0.011, 0.5% of the larger value)."""
    return abs(a - b) <= max(0.011, 0.005 * max(abs(a), abs(b)))


def reldiff(a, b):
    m = max(abs(a), abs(b))
    return 0.0 if m == 0 else abs(a - b) / m


def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and xs[o[j + 1]] == xs[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return None if sxx == 0 or syy == 0 else sxy / math.sqrt(sxx * syy)


def hyper_sf(k, N, K, n):
    """P(X >= k) for X ~ Hypergeometric(population N, K successes, n draws)."""
    tot = math.comb(N, n)
    return sum(math.comb(K, i) * math.comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / tot


LINKS = []


def link(da, ia, db, ib, basis, fields, certainty):
    assert certainty in ("confirmed by values", "probable", "unverified")
    LINKS.append(dict(dataset_a=da, id_a=str(ia), dataset_b=db, id_b=str(ib), basis=basis, fields_matched=fields, certainty=certainty))


def write_csv(name, rows, cols=None):
    cols = cols or list(rows[0].keys())
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c) for c in cols})


# ------------------------------------------------------------------ readers
def read_s050():
    z = zipfile.ZipFile(F_S050)
    b = z.read("Table_1.DOCX")
    rows = [r for t in read_docx_tables(b) for r in t]
    hdr = rows[0]
    out = []
    for r in rows[1:]:
        if not r or not r[0].strip().isdigit():
            continue
        d = dict(zip(hdr, r))
        case = int(d["Case"])
        out.append(dict(case=case, age=fnum(d["Age (mos)"]), wt=fnum(d["Weight (kg)"]), sex=d["Gender"].strip().lower(),
                        status=d["Status"].strip().lower(), outcome=d["Outcome"].strip().lower(),
                        wbc=fnum(d["WBC (x10^9/L)"]), seg=fnum(d["Neut Seg (x10^9/L)"]), band=fnum(d["Neut Band (x10^9/L)"]),
                        cohort=1 if (case <= 97 or 201 <= case <= 215) else 2))
    return out, hashlib.sha256(b).hexdigest()


def score_sheets():
    """Signalment and mucous-membrane text of each DS04 score sheet, keyed by case number (first sheet of each case)."""
    res = {}
    for p in sorted((RAW / "DS04").glob("*126*.xlsx")):
        case = re.match(r"^(\d+)", p.name).group(1)
        rows = list(read_xlsx(str(p)).values())[0]
        sig, mm = (rows[2][1] or "").strip(), (rows[3][1] or "").strip()
        res.setdefault(case, []).append(dict(file=p.name, signalment=sig, membranes=mm))
    return res


SIGNAL = {  # DS04 fatal-case signalment, parsed by hand from the score-sheet text (asserted below); age in months
    "20": ("female", 144, None), "50": ("male", 30, 30.6), "54": ("male", 9, 45.6), "59": ("male", 60, 34.0),
    "61": ("male", 96, 36.4), "88": ("male", 7, 12.0), "91": ("male", 84, 26.0), "106": ("male", 36, 3.0),
    "110": ("male", 36, None), "117": ("male", 48, 43.2)}
SIGNAL_WORDS = {"20": ["FS", "12y"], "50": ["MI", "2.5y", "30.6kg"], "54": ["MI", "9m", "45.6kg"], "59": ["MI", "5 years", "34kg"],
                "61": ["MI", "8 years", "36.4kg"], "88": ["M.", "7m", "12kg"], "91": ["MI", "7 years", "26kg"],
                "106": ["M.", "3 year", "3kg"], "110": ["M.", "3 years"], "117": ["M.", "4 years", "43.2kg"]}
NEUTER = {"20": "neutered", "50": "intact", "54": "intact", "59": "intact", "61": "intact", "91": "intact", "88": None, "106": None,
          "110": None, "117": None}


def main():
    OUT.mkdir(exist_ok=True)
    res = {"inputs": {}}
    for p in (F_S050, F_HAEM, F_STATS, F_THESIS, F_DS03N, F_DS02, F_DS06, F_DS07, F_DS05T, F_SPEC):
        res["inputs"][rel(p)] = sha(p)
    s050, s050_member_sha = read_s050()
    res["inputs"][rel(F_S050) + "!Table_1.DOCX"] = s050_member_sha
    assert len(s050) == 161, len(s050)

    # ================================================================ step 1: DS04 rows -> case numbers
    st = read_xlsx(str(F_STATS))
    ihc_order = [r[1].strip() for r in st["IHC"][2:] if len(r) > 1 and r[1]]
    sheet_orders = {"IHC": ihc_order}
    for s in ("Special Stains", "Score Sheet", "Sheet1"):
        sheet_orders[s] = [r[1].strip() for r in st[s][2:] if len(r) > 1 and r[1] and r[1].strip().isdigit()][:14]
    sheet_orders["Total Phenotypes"] = [r[1].strip() for r in st["Total Phenotypes"] if len(r) > 1 and r[1] and r[1].strip().isdigit()][:14]
    orders_agree = all(v == ihc_order for v in sheet_orders.values())
    hw = read_xlsx(str(F_HAEM))
    hrows = [r for r in hw["Haematology"][1:] if r and r[0] in ("0", "1")]
    brows = [r for r in hw["Biochemistries"][1:] if r and r[0] in ("0", "1")]
    flags = [r[0] for r in hrows]
    assert flags == ["0"] * 4 + ["1"] * 10, flags
    controls = [c for c in ihc_order if c in ("2", "4", "9", "11")]
    cases = [c for c in ihc_order if c not in controls]
    join = controls + cases           # haematology row i (1-based) -> case number
    haem = []
    for i, (hr, br) in enumerate(zip(hrows, brows)):
        haem.append(dict(row=i + 1, flag=hr[0], case=join[i], wbc=fnum(hr[5]), seg=fnum(hr[6]), band=fnum(hr[7]),
                         hct=fnum(hr[2]), bili=fnum(br[6])))
    sheets = score_sheets()
    for c, words in SIGNAL_WORDS.items():
        txt = sheets[c][0]["signalment"] + " | " + " | ".join(s["signalment"] for s in sheets[c][1:])
        for w in words:
            assert w in txt, (c, w, txt)

    # 1b and step 2: haematology triples against all S-CB050 rows
    s050_tri = [r for r in s050 if None not in (r["wbc"], r["seg"], r["band"])]
    step2 = []
    for h in haem:
        exact, near, best = [], [], None
        for r in s050_tri:
            ds = [reldiff(h[k], r[k]) for k in ("wbc", "seg", "band")]
            if all(agree(h[k], r[k]) for k in ("wbc", "seg", "band")):
                exact.append(r)
            if max(ds) <= 0.05:
                near.append(r)
            if best is None or max(ds) < best[0]:
                best = (max(ds), r)
        n_wbc_only = sum(1 for r in s050_tri if agree(h["wbc"], r["wbc"]))
        sig = SIGNAL.get(h["case"])
        sig_ok = None
        if exact and sig:
            r = exact[0]
            sig_ok = (r["sex"] == sig[0] and r["age"] == sig[1] and (sig[2] is None or r["wt"] is None or abs(r["wt"] - sig[2]) <= 0.5))
        step2.append(dict(row=h["row"], ds04_case=h["case"], group="control" if h["flag"] == "0" else "fatal",
                          wbc=h["wbc"], seg=h["seg"], band=h["band"],
                          s050_exact=";".join(str(r["case"]) for r in exact), s050_near_5pct=";".join(str(r["case"]) for r in near),
                          s050_rows_matching_wbc_alone=n_wbc_only,
                          nearest_case=best[1]["case"], nearest_max_reldiff=round(best[0], 4),
                          nearest_outcome=best[1]["outcome"], nearest_status=best[1]["status"],
                          exact_outcome=";".join(r["outcome"] for r in exact),
                          signalment_agrees=sig_ok,
                          s050_age=exact[0]["age"] if exact else None, s050_wt=exact[0]["wt"] if exact else None,
                          s050_sex=exact[0]["sex"] if exact else None,
                          ds04_age=sig[1] if sig else None, ds04_wt=sig[2] if sig else None, ds04_sex=sig[0] if sig else None))
    write_csv("ds04_vs_scb050.csv", step2)
    matched = {r["ds04_case"]: int(r["s050_exact"]) for r in step2 if r["s050_exact"]}
    assert all(";" not in r["s050_exact"] for r in step2)

    # 1c: icterus wording vs bilirubin, chance by exact enumeration
    def icteric(text):
        t = text.lower()
        return any(w in t for w in ("icter", "yellow"))
    fatal = [h for h in haem if h["flag"] == "1"]
    ict_case = {c: icteric(sheets[c][0]["membranes"]) for c in cases}
    bili_hi = [h["bili"] is not None and h["bili"] > 30 for h in fatal]
    obs_agree = sum(1 for h, b in zip(fatal, bili_hi) if ict_case[h["case"]] == b)
    perm_all = perm_fixed = n_fixed = 0
    n_all = 0
    fixed_pos = {i: h["case"] for i, h in enumerate(fatal) if h["case"] in matched}
    for p in itertools.permutations(cases):
        n_all += 1
        a = sum(1 for i, c in enumerate(p) if ict_case[c] == bili_hi[i])
        if a >= obs_agree:
            perm_all += 1
        if all(p[i] == c for i, c in fixed_pos.items()):
            n_fixed += 1
            if a >= obs_agree:
                perm_fixed += 1
    # chance of the three S-CB050 hits landing on the rows that the order join gives: 1 / (10*9*8)
    p_three = 1 / (10 * 9 * 8)
    icterus_rows = [dict(row=h["row"], ds04_case=h["case"], membranes_text=sheets[h["case"]][0]["membranes"],
                         icteric_text=ict_case[h["case"]], bilirubin_umol_l=h["bili"], bilirubin_gt_30=b,
                         agrees=ict_case[h["case"]] == b) for h, b in zip(fatal, bili_hi)]
    write_csv("ds04_icterus_join.csv", icterus_rows)
    res["step1"] = dict(
        sheet_orders=sheet_orders, orders_agree=orders_agree, join={str(i + 1): c for i, c in enumerate(join)},
        s050_matches={c: matched[c] for c in matched}, p_three_matches_on_join_rows=p_three,
        icterus_agree=obs_agree, icterus_n=len(fatal),
        icterus_p_all_orders=perm_all / n_all, icterus_p_orders_with_matches_fixed=perm_fixed / n_fixed,
        n_orders_all=n_all, n_orders_fixed=n_fixed)
    for h in haem:
        if h["case"] in matched:
            link("DS04 haematology", f"row {h['row']}", "DS04", f"case {h['case']}", "row order of Stats Tables sheets; S-CB050 triple and signalment; icterus vs bilirubin",
                 "WBC, segmented, band (via S-CB050); age, weight, sex", "confirmed by values")
        elif h["flag"] == "1":
            link("DS04 haematology", f"row {h['row']}", "DS04", f"case {h['case']}",
                 f"row order of the 5 Stats Tables sheets; the order rule is validated by the 3 S-CB050 hits on the rows it predicts "
                 f"(chance {p_three:.4f}); icterus wording vs bilirubin is uninformative ({obs_agree}/{len(fatal)} agree, p = {perm_fixed / n_fixed:.2f})",
                 "order", "probable")
        else:
            link("DS04 haematology", f"row {h['row']}", "DS04", f"case {h['case']}", "row order only (controls: all bilirubin 0, no icterus)", "order", "unverified")
    for h in step2:
        if h["s050_exact"]:
            link("DS04", f"case {h['ds04_case']}", "S-CB050", f"case {h['s050_exact']}", "WBC, segmented and band neutrophils equal within rounding; age, weight and sex equal; both died",
                 "wbc; neut_seg; neut_band; age_months; weight_kg; sex", "confirmed by values")

    # ================================================================ step 3: DS03 natural vs S-CB050 (and DS05 baseline)
    w3 = read_xlsx(str(F_DS03N))["Sheet1"]
    ds03, block = [], None
    for r in w3[1:]:
        if not r or not r[0]:
            continue
        t = r[0].strip()
        if t.startswith("Study cohort 1"):
            block = "cohort 1"
        elif t.startswith("Study cohort 2"):
            block = "cohort 2"
        elif t.startswith("Control"):
            block = "controls"
        elif t.isdigit() and len(r) > 4 and r[1]:
            ds03.append(dict(block=block, id=r[1].strip(), age=fnum(r[2]), wt=fnum(r[3]), sex=(r[4] or "").strip().lower() or None))
    assert [sum(1 for d in ds03 if d["block"] == b) for b in ("cohort 1", "cohort 2", "controls")] == [85, 18, 14]
    d5 = json.loads(F_DS05T.read_text(encoding="utf-8"))
    ds05 = [dict(id=r["dog_id"], age=r["values"].get("age_months"), wt=r["values"].get("weight_kg"), sex=r["values"].get("sex"))
            for r in d5["records"]]

    def sigmatch(a, b):
        return (None not in (a["age"], a["wt"], a["sex"], b["age"], b["wt"], b["sex"]) and a["sex"] == b["sex"]
                and a["age"] == b["age"] and abs(a["wt"] - b["wt"]) <= 0.1 + 1e-9)

    s050_inf = [r for r in s050 if r["status"] == "infected"]
    s050_ctl = [r for r in s050 if r["status"] == "control"]
    cand_rows, summary3 = [], []
    for d in ds03:
        pool = s050_ctl if d["block"] == "controls" else s050_inf
        hits = [r for r in pool if sigmatch(d, r)]
        same03 = sum(1 for e in ds03 if e is not d and sigmatch(d, e))
        hits05 = [e for e in ds05 if sigmatch(d, e)] if d["block"] != "controls" else []
        for r in hits:
            cand_rows.append(dict(ds03_block=d["block"], ds03_id=d["id"], age=d["age"], wt=d["wt"], sex=d["sex"], s050_case=r["case"],
                                  s050_cohort=r["cohort"], s050_wt=r["wt"], n_s050_sharing=len(hits), n_other_ds03_sharing=same03))
        d["n_s050"], d["n_ds05"], d["complete"] = len(hits), len(hits05), None not in (d["age"], d["wt"], d["sex"])
        d["s050_cohorts"] = sorted({r["cohort"] for r in hits})
    write_csv("ds03_vs_scb050_candidates.csv", cand_rows,
              ["ds03_block", "ds03_id", "age", "wt", "sex", "s050_case", "s050_cohort", "s050_wt", "n_s050_sharing", "n_other_ds03_sharing"])
    for b in ("cohort 1", "cohort 2", "controls"):
        ds = [d for d in ds03 if d["block"] == b and d["complete"]]
        pool = s050_ctl if b == "controls" else s050_inf
        row = dict(ds03_block=b, n_complete=len(ds), with_s050_candidate=sum(1 for d in ds if d["n_s050"] > 0),
                   with_unique_s050_candidate=sum(1 for d in ds if d["n_s050"] == 1),
                   with_s050_c1=sum(1 for d in ds if 1 in d["s050_cohorts"]), with_s050_c2=sum(1 for d in ds if 2 in d["s050_cohorts"]),
                   s050_pool=len([r for r in pool if None not in (r["age"], r["wt"])]),
                   with_ds05_candidate=None if b == "controls" else sum(1 for d in ds if d["n_ds05"] > 0),
                   ds05_pool=None if b == "controls" else len(ds05))
        summary3.append(row)
    # baseline 2: S-CB050 infected vs DS05
    s050_vs_ds05 = dict(n=sum(1 for r in s050_inf if None not in (r["age"], r["wt"])),
                        with_ds05_candidate=sum(1 for r in s050_inf if any(sigmatch(r, e) for e in ds05)))
    # pair-level rate: candidate pairs / possible pairs (removes pool-size differences)
    def pair_rate(A, B):
        A = [a for a in A if None not in (a["age"], a["wt"], a["sex"])]
        B = [b for b in B if None not in (b["age"], b["wt"], b["sex"])]
        k = sum(1 for a in A for b in B if sigmatch(a, b))
        return dict(pairs=len(A) * len(B), candidate_pairs=k, per_1000=round(1000 * k / (len(A) * len(B)), 3))
    rates = []
    for b in ("cohort 1", "cohort 2"):
        A = [d for d in ds03 if d["block"] == b]
        for lab, B in (("S-CB050 cohort 1", [r for r in s050_inf if r["cohort"] == 1]),
                       ("S-CB050 cohort 2", [r for r in s050_inf if r["cohort"] == 2]), ("DS05 (baseline)", ds05)):
            rates.append(dict(ds03_block=b, against=lab, **pair_rate(A, B)))
    rates.append(dict(ds03_block="S-CB050 infected", against="DS05 (baseline)", **pair_rate(s050_inf, ds05)))
    rates.append(dict(ds03_block="controls", against="S-CB050 controls", **pair_rate([d for d in ds03 if d["block"] == "controls"], s050_ctl)))
    # order check (added after the first run, deviation D2): do DS03 study numbers map onto S-CB050 case numbers in the same order?
    mono = []
    for b in ("cohort 1", "cohort 2", "controls"):
        prs = sorted(((int(re.sub(r"\D", "", c["ds03_id"])), c["s050_case"]) for c in cand_rows if c["ds03_block"] == b and c["n_s050_sharing"] == 1))
        seq = [p[1] for p in prs]
        inv = sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])
        npair = len(seq) * (len(seq) - 1) // 2
        mono.append(dict(ds03_block=b, unique_pairs=len(seq), order_inversions=inv, pairs_compared=npair,
                         kendall_tau=round(1 - 2 * inv / npair, 4) if npair else None,
                         p_all_in_order_by_chance=float(f"{1 / math.factorial(len(seq)):.3g}") if inv == 0 else None))
    write_csv("ds03_order_check.csv", mono)
    write_csv("ds03_unique_pairs.csv", [dict(ds03_block=c["ds03_block"], ds03_id=c["ds03_id"], ds03_number=int(re.sub(r"\D", "", c["ds03_id"])),
                                             s050_case=c["s050_case"]) for c in cand_rows if c["n_s050_sharing"] == 1])
    # value check (added, deviation D3): DS04 haematology rows against DS03 natural dogs on haematocrit and reticulocyte %,
    # equal after rounding to the coarser file (Hct 2 decimals; DS04 retic 1 decimal -> tolerance 0.05)
    d3rows = [r for r in w3 if r and r[0] and r[0].strip().isdigit() and len(r) > 9 and r[1]]
    d3vals = {r[1].strip(): (fnum(r[6]), fnum(r[9]), fnum(r[2]), fnum(r[3]), (r[4] or "").strip().lower()) for r in d3rows}
    ds04_ds03 = []
    for h in haem:
        hrw = hrows[h["row"] - 1]
        hct, ret = fnum(hrw[2]), fnum(hrw[3])
        hits = [k for k, v in d3vals.items() if v[0] is not None and v[1] is not None
                and abs(v[0] - hct) <= 0.005 + 1e-9 and abs(v[1] - ret) <= 0.05 + 1e-9]
        sig = SIGNAL.get(h["case"])
        for k in hits or [None]:
            v = d3vals.get(k)
            ds04_ds03.append(dict(row=h["row"], ds04_case=h["case"], ds04_hct=hct, ds04_retic_pct=ret, ds03_id=k,
                                  ds03_hct=v[0] if v else None, ds03_retic_pct=v[1] if v else None,
                                  ds03_age=v[2] if v else None, ds03_wt=v[3] if v else None, ds03_sex=v[4] if v else None,
                                  signalment_agrees=(bool(sig) and v[4] == sig[0] and v[2] == sig[1] and (sig[2] is None or v[3] is None or abs(v[3] - sig[2]) <= 0.5)) if v else None))
    write_csv("ds04_vs_ds03.csv", ds04_ds03)
    for r in ds04_ds03:
        if r["ds03_id"] and r["signalment_agrees"]:
            link("DS04", f"case {r['ds04_case']}", "DS03", f"{r['ds03_id']} (cohort 2)", "haematocrit and reticulocyte % equal within rounding; age, weight and sex equal",
                 "hct; retic_pct; age_months; weight_kg; sex", "confirmed by values")
            s5 = matched.get(r["ds04_case"])
            if s5:
                link("DS03", f"{r['ds03_id']} (cohort 2)", "S-CB050", f"case {s5}", f"chain through DS04 case {r['ds04_case']} (both links confirmed by values)",
                     "via DS04: hct, retic_pct; wbc, neut_seg, neut_band; signalment", "confirmed by values")

    # file-level evidence: observed candidate pairs against the number expected at the DS05 baseline rate (Poisson upper tail)
    base = next(r for r in rates if r["ds03_block"] == "cohort 1" and r["against"] == "DS05 (baseline)")
    base_all = (base["candidate_pairs"] + next(r for r in rates if r["ds03_block"] == "S-CB050 infected")["candidate_pairs"]) / (
        base["pairs"] + next(r for r in rates if r["ds03_block"] == "S-CB050 infected")["pairs"])
    def pois_sf(k, lam):
        if k == 0:
            return 1.0
        return sum(math.exp(-lam + i * math.log(lam) - math.lgamma(i + 1)) for i in range(k, k + 400))
    for r in rates:
        r["expected_at_baseline"] = round(r["pairs"] * base_all, 2)
        r["ratio_to_baseline"] = round(r["candidate_pairs"] / (r["pairs"] * base_all), 1)
        r["p_poisson"] = float(f"{pois_sf(r['candidate_pairs'], r['pairs'] * base_all):.3g}")
    write_csv("ds03_match_rates.csv", rates)
    write_csv("ds03_summary.csv", summary3)
    res["step3"] = dict(summary=summary3, rates=rates, s050_vs_ds05=s050_vs_ds05, n_candidate_pairs=len(cand_rows),
                        baseline_rate_per_1000=round(1000 * base_all, 3), order_check=mono,
                        ds04_vs_ds03=[r for r in ds04_ds03 if r["ds03_id"]])
    for blk, tgt in (("cohort 1", "S-CB050 cohort 1"), ("cohort 2", "S-CB050 cohort 2"), ("controls", "S-CB050 controls")):
        r = next(x for x in rates if x["ds03_block"] == blk and x["against"] == tgt)
        s = next(x for x in summary3 if x["ds03_block"] == blk)
        m = next(x for x in mono if x["ds03_block"] == blk)
        link(f"DS03 {blk} (file level)", f"{s['n_complete']} dogs with full signalment", tgt.replace(" cohort", " cohort").replace("S-CB050 controls", "S-CB050 controls 201-215"),
             "file level", f"{s['with_s050_candidate']}/{s['n_complete']} DS03 dogs have an age-weight-sex twin; candidate pairs {r['ratio_to_baseline']} times the DS05 baseline "
             f"(p = {r['p_poisson']:.1e}); the {m['unique_pairs']} unique pairs follow the study-number order with no inversion (Kendall tau {m['kendall_tau']}). "
             "Dog-level pairs stay unverified (spec step 3)", "age_months; weight_kg; sex (summary)", "probable")
    for c in cand_rows:
        link("DS03", f"{c['ds03_id']} ({c['ds03_block']})", "S-CB050", f"case {c['s050_case']}",
             f"age, weight (within 0.1 kg) and sex equal; {c['n_s050_sharing']} S-CB050 dog(s) and {c['n_other_ds03_sharing'] + 1} DS03 dog(s) share the combination",
             "age_months; weight_kg; sex", "unverified")

    # ================================================================ step 4: DS06 names vs DS02 dogs
    w2 = read_xlsx(str(F_DS02))["Haematology"]
    h2 = w2[0]
    ds02 = {}
    for r in w2[1:]:
        if not r or not r[0] or r[0] == "1":
            continue
        dog = r[0]
        for j, c in enumerate(h2):
            m = re.match(r"^(Lymph|SNeut|Mono)(-?\d+(?:\.\d)?)$", c or "")
            if m and m.group(2) in ("0", "1", "3", "4", "6", "8") and j < len(r):
                ds02.setdefault(dog, {}).setdefault(m.group(1), {})[int(m.group(2))] = fnum(r[j])
    markers = {"Lymph": ["CD3E", "CD3D", "CD2", "MS4A1", "CD79A", "CD79B"], "SNeut": ["CSF3R", "CXCR2", "FPR1", "MNDA"], "Mono": ["CD14", "CSF1R"]}
    want = {g for v in markers.values() for g in v}
    with gzip.open(F_DS06, "rt") as f:
        cols = f.readline().rstrip("\n").split("\t")[1:]
        lib = [0] * len(cols)
        expr = {}
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 2:
                continue
            v = [int(float(x)) for x in p[1:]]
            lib = [a + b for a, b in zip(lib, v)]
            sym = p[0].split("_", 1)[1] if "_" in p[0] else p[0]
            if sym in want:
                expr[sym] = v
    present = {k: [g for g in v if g in expr] for k, v in markers.items()}
    samples = {}
    for i, c in enumerate(cols):
        m = re.match(r"^(low|high)_(\d)_D(\d)$", c)
        samples.setdefault(f"{m.group(1)}_{m.group(2)}", {})[int(m.group(3))] = i
    def score(name, cell, day):
        i = samples[name][day]
        return sum(math.log2(expr[g][i] / lib[i] * 1e6 + 1) for g in present[cell]) / len(present[cell])
    def resid_corr(names, dogs, days, cell):
        """Mean over pairs of the Spearman correlation of residuals (minus group mean per day) between DS06 name and DS02 dog."""
        rn = {n: [score(n, cell, d) - sum(score(m, cell, d) for m in names) / len(names) for d in days] for n in names}
        rd = {g: [ds02[g][cell][d] - sum(ds02[h][cell][d] for h in dogs) / len(dogs) for d in days] for g in dogs}
        return rn, rd
    ass_rows = []
    def test(names, dogs, days, label):
        out = []
        per_cell = {c: resid_corr(names, dogs, days, c) for c in markers}
        for perm in itertools.permutations(dogs):
            cs = {}
            for c, (rn, rd) in per_cell.items():
                rs = [spearman(rn[n], rd[g]) for n, g in zip(names, perm)]
                rs = [x for x in rs if x is not None]
                cs[c] = sum(rs) / len(rs) if rs else None
            vals = [v for v in cs.values() if v is not None]
            out.append(dict(test=label, assignment="; ".join(f"{n}=dog {g}" for n, g in zip(names, perm)), days=",".join(map(str, days)),
                            lymph=round(cs["Lymph"], 3), neut=round(cs["SNeut"], 3), mono=round(cs["Mono"], 3),
                            mean=round(sum(vals) / len(vals), 3)))
        best = max(out, key=lambda r: r["mean"])
        for r in out:
            r["best"] = r is best
            # cell types on which this assignment beats every other assignment
            r["wins"] = sum(1 for k in ("lymph", "neut", "mono") if all(r[k] > o[k] for o in out if o is not r))
        ass_rows.extend(out)
        return best, out
    pc_best, _ = test(["high_1", "high_2", "high_3"], ["4", "5", "6"], [0, 1, 3], "positive control: high dose, days 0,1,3")
    pc_pass = "high_3=dog 6" in pc_best["assignment"]
    hb, _ = test(["high_1", "high_2"], ["4", "5"], [0, 1, 3, 4, 6, 8], "high dose 1/2, all days")
    lb, _ = test(["low_1", "low_2"], ["2", "3"], [0, 1, 3, 4, 6, 8], "low dose 1/2, all days")
    write_csv("ds06_assignment_scores.csv", ass_rows)
    series = []
    for n, ds in sorted(samples.items()):
        for d, i in sorted(ds.items()):
            series.append(dict(ds06_name=n, day=d, library_size=lib[i], lymph_score=round(score(n, "Lymph", d), 3),
                               neut_score=round(score(n, "SNeut", d), 3), mono_score=round(score(n, "Mono", d), 3)))
    write_csv("ds06_series.csv", series)
    res["step4"] = dict(markers_present=present, markers_absent={k: [g for g in v if g not in expr] for k, v in markers.items()},
                        positive_control_best=pc_best, positive_control_pass=pc_pass, high_best=hb, low_best=lb,
                        days_per_name={n: sorted(d) for n, d in samples.items()})
    link("DS06", "high_3", "DS02", "dog 6", "sample pattern: series stops after day 3; DS02 dog 6 died on day 4 (only high-dose dog with no sample after day 4)",
         "sampling pattern; dose group", "probable")
    for best in (hb, lb):
        ok = pc_pass and best["wins"] >= 2
        for pair in best["assignment"].split("; "):
            n, g = pair.split("=")
            link("DS06", n, "DS02", g, f"dose group; marker-gene residual correlation with DS02 counts (mean rho {best['mean']}, wins {best['wins']}/3 cell types; positive control {'passed' if pc_pass else 'failed'})",
                 "dose group; lymphocyte/neutrophil/monocyte kinetics (exploratory)", "probable" if ok else "unverified")
    link("DS06", "low_0", "DS02", "dog 1 (donor)?", "single day-0 sample labelled low dose; DS02 dog 1 is the splenectomised donor with one baseline sample. Not in the files", "none", "unverified")

    # ================================================================ step 5: DS07 numbering
    sl = read_xlsx(str(F_DS07))
    rows7 = list(sl.values())[0]
    lists = {}   # the group lists are label/ID pairs in columns 0-1 and 3-4
    for r in rows7:
        for j in (0, 3):
            if j + 1 < len(r) and r[j] and r[j + 1] not in (None, ""):
                lists.setdefault(r[j].strip(), []).append(str(r[j + 1]).strip())
    comp_key = next(k for k in lists if k.lower().startswith("compl"))
    unc_key = next(k for k in lists if k.lower().startswith("uncompl"))
    comp = {int(x) for x in lists[comp_key] if x.isdigit()}
    unc = {int(x) for x in lists[unc_key] if x.isdigit()}
    assert len(comp) == 14 and len(unc) == 18, (lists.keys(), len(comp), len(unc))
    ds04_low = [int(c) for c in cases if int(c) < 98]
    in_comp = sorted(set(ds04_low) & comp)
    in_unc = sorted(set(ds04_low) & unc)
    hyp = []
    for N in (91, 97, 144):
        hyp.append(dict(universe=f"1-{N}", expected_in_complicated=round(len(ds04_low) * 14 / N, 2),
                        p_ge_observed_complicated=hyper_sf(len(in_comp), N, 14, len(ds04_low)),
                        expected_in_any_infected=round(len(ds04_low) * 32 / N, 2),
                        p_ge_observed_any=hyper_sf(len(in_comp) + len(in_unc), N, 32, len(ds04_low))))
    write_csv("ds07_numbering_chance.csv", hyp)
    # consistency of DS04 signalment with the CB112 group summaries (read from CB112: complicated group 4 females (2 spayed),
    # 10 males (none castrated); uncomplicated 5 females (1 spayed), 13 males (4 castrated); infected age range 6-120 months;
    # complicated includes death within 24 h of admission)
    cons = []
    for c in sorted(ds04_low):
        s = SIGNAL[str(c)]
        grp = "complicated" if c in comp else ("uncomplicated" if c in unc else "absent")
        issues = []
        if not (6 <= s[1] <= 120):
            issues.append(f"age {s[1]} months is outside the CB112 infected range 6-120")
        if grp == "complicated" and s[0] == "male" and NEUTER[str(c)] == "neutered":
            issues.append("castrated male, but CB112 complicated males are all intact")
        if grp == "uncomplicated" and "DOA" in sheets[str(c)][0]["signalment"]:
            issues.append("dead on arrival in DS04, but CB112 counts death within 24 h as complicated")
        cons.append(dict(ds04_case=c, ds07_group=grp, sex=s[0], neuter=NEUTER[str(c)], age_months=s[1],
                         timing=re.search(r"(Died[^.]*|DOA)", sheets[str(c)][0]["signalment"]).group(1),
                         s050_case=matched.get(str(c)), contradiction="; ".join(issues) or None))
    write_csv("ds07_ds04_consistency.csv", cons)
    res["step5"] = dict(ds07_lists={k: v for k, v in lists.items()}, ds04_numbers_below_98=ds04_low, in_complicated=in_comp,
                        in_uncomplicated=in_unc, hypergeometric=hyp, consistency=cons)
    for c in cons:
        if c["ds07_group"] == "absent":
            continue
        cert = "unverified"
        basis = (f"same number; DS07 '{c['ds07_group']}'; 6 of 7 DS04 numbers below 98 are DS07 complicated (p = "
                 f"{hyp[1]['p_ge_observed_complicated']:.1e} over 1-97); no shared values to check")
        if c["contradiction"]:
            basis += f"; contradiction: {c['contradiction']}"
        link("DS07", c["ds04_case"], "DS04", f"case {c['ds04_case']}", basis, "case number only", cert)
        if c["s050_case"]:
            link("DS07", c["ds04_case"], "S-CB050", f"case {c['s050_case']}", f"through DS04 case {c['ds04_case']} (number link unverified)",
                 "case number only (chain)", "unverified")
    # S-CB517 = S-CB050 and DS03 experimental = DS02 were confirmed by SV-G1; listed for completeness
    link("S-CB517", "cases 1-97, controls 201-215", "S-CB050", "same case numbers", "SV-G1: 7 cytokines equal in 111-112 of 112 dogs", "cytokines; neut_seg; WBC; died", "confirmed by values")
    link("DS03 experimental", "dogs 1-5", "DS02", "dogs 2-6", "SV-G1: ARC equal on every day, 139 of 140 cells equal", "haematology by day", "confirmed by values")

    # summary-level: S-CB050 signalment by cohort against the CB112 summaries (controls: 20, 6 female, median age 21, 12-120)
    def summ(rs):
        ages = sorted(r["age"] for r in rs if r["age"] is not None)
        n = len(ages)
        med = None if not n else (ages[n // 2] if n % 2 else (ages[n // 2 - 1] + ages[n // 2]) / 2)
        return dict(n=len(rs), female=sum(1 for r in rs if r["sex"] == "female"), median_age=med,
                    age_min=ages[0] if ages else None, age_max=ages[-1] if ages else None)
    res["step5"]["summary_level"] = {
        "CB112 controls (article)": dict(n=20, female=6, median_age=21, age_min=12, age_max=120),
        "CB112 infected (article)": dict(n=32, female=9, median_age=28, age_min=6, age_max=120),
        "S-CB050 controls 201-220": summ(s050_ctl), "S-CB050 controls 216-220 (2014)": summ([r for r in s050_ctl if r["cohort"] == 2]),
        "S-CB050 infected 101-144 (2014)": summ([r for r in s050_inf if r["cohort"] == 2]),
        "S-CB050 infected 1-97 (2011-13)": summ([r for r in s050_inf if r["cohort"] == 1]),
        "DS03 controls": summ([d for d in ds03 if d["block"] == "controls"])}

    # ================================================================ write
    confirmed = {(r["dataset_a"], r["id_a"].split(" ")[0], r["dataset_b"], r["id_b"]) for r in LINKS if r["certainty"] == "confirmed by values"}
    LINKS[:] = [r for r in LINKS if r["certainty"] == "confirmed by values"
                or (r["dataset_a"], r["id_a"].split(" ")[0], r["dataset_b"], r["id_b"]) not in confirmed]
    LINKS.sort(key=lambda r: ({"confirmed by values": 0, "probable": 1, "unverified": 2}[r["certainty"]], r["dataset_a"], r["dataset_b"]))
    write_csv("linkage.csv", LINKS, ["dataset_a", "id_a", "dataset_b", "id_b", "basis", "fields_matched", "certainty"])
    res["link_counts"] = {k: sum(1 for r in LINKS if r["certainty"] == k) for k in ("confirmed by values", "probable", "unverified")}
    (OUT / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(json.dumps({k: res[k] for k in ("link_counts",)}, indent=1))
    print(json.dumps(res["step1"], indent=1, default=str)[:1500])


if __name__ == "__main__":
    main()
