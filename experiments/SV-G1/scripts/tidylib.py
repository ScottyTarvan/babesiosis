"""Shared helpers for the SV-G1 tidy scripts (standard library only).

Every tidy script builds one dataset and calls write_dataset(), which checks the tidy
file contract of /experiments/rules.md before it writes:

  shared/tidy/<dataset>.features.json
  shared/tidy/<dataset>.outcomes.json
  SV-G1/out/dictionary/<dataset>.csv      merged later into shared/dictionary.csv
  SV-G1/out/checks/<dataset>.json         row counts and the published numbers reproduced
"""
import csv
import hashlib
import io
import json
import math
import sys
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
CORE = REPO / "core"
RAW = CORE / "data" / "raw"
EXP = REPO / "experiments"
SHARED = EXP / "shared"
TIDY = SHARED / "tidy"
OUT = EXP / "SV-G1" / "out"

sys.path.insert(0, str(SHARED / "io"))
from rawio import read_xlsx, read_docx_tables, fnum  # noqa: E402,F401

ID_SALT = "SV-G1-2026-11-12"
GROUPS = {"infected", "control", "comparator"}

# Harmonised names that the package file asks for, with their one unit.
HARMONISED = {
    "age_months": "months", "weight_kg": "kg", "sex": "male/female", "neuter": "intact/neutered",
    "breed": "text", "illness_days": "days", "temp_c": "degC", "hct": "L/L", "hb": "g/L",
    "rbc": "10^12/L", "mcv": "fL", "mchc": "g/L", "retic_pct": "%", "arc": "10^9/L", "wbc": "10^9/L",
    "neut_seg": "10^9/L", "neut_band": "10^9/L", "lymph": "10^9/L", "mono": "10^9/L", "eos": "10^9/L",
    "plt": "10^9/L", "tsp": "g/L", "albumin": "g/L", "globulin": "g/L", "parasitaemia_pct": "%",
    "crp": "mg/L", "saa": "mg/L", "lactate": "mmol/L", "il2": "pg/mL", "il6": "pg/mL", "il8": "pg/mL",
    "il10": "pg/mL", "il18": "pg/mL", "gmcsf": "pg/mL", "mcp1": "pg/mL", "kc": "pg/mL", "mpxi": "index",
}

# Words that must never be a features variable name: they are labels or label proxies.
LABEL_WORDS = ("died", "death", "outcome", "surviv", "complicat", "severity", "habitus", "status_label")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def zip_member(zip_path, name):
    with zipfile.ZipFile(zip_path) as z:
        return z.read(name)


def repo_path(p):
    return "/" + Path(p).resolve().relative_to(REPO).as_posix()


def built_from_entry(path, member=None):
    """One built_from item. For a zip member the hash is of the member bytes."""
    if member is None:
        return {"file": repo_path(path), "sha256": sha256_file(path)}
    return {"file": repo_path(path) + "!" + member, "sha256": sha256_bytes(zip_member(path, member))}


def neutral_ids(dataset_id, original_ids):
    """Map original IDs to neutral IDs <dataset>:dNNN. The order is a salted hash of the original ID,
    so the neutral number carries neither the label nor the original case number."""
    keyed = sorted(original_ids, key=lambda o: hashlib.sha256(f"{ID_SALT}|{dataset_id}|{o}".encode()).hexdigest())
    width = max(3, len(str(len(keyed))))
    return {o: f"{dataset_id}:d{str(i + 1).zfill(width)}" for i, o in enumerate(keyed)}


def num(x):
    """Number from a raw cell; strips floating-point noise (0.1400000000000001 -> 0.14)."""
    v = fnum(x) if not isinstance(x, (int, float)) else float(x)
    if v is None or math.isnan(v) or math.isinf(v):
        return None
    return round(v, 10)


def clean(v):
    if isinstance(v, float):
        if math.isnan(v) or math.isinf(v):
            return None
        r = round(v, 10)
        return r
    return v


def _check(features, outcomes):
    errs = []
    ds = features["dataset_id"]
    if outcomes["dataset_id"] != ds:
        errs.append("dataset_id differs")
    names = [v["name"] for v in features["variables"]]
    if len(names) != len(set(names)):
        errs.append("duplicate variable names")
    for n in names:
        if any(w in n.lower() for w in LABEL_WORDS):
            errs.append(f"label-like variable name in features: {n}")
    nameset = set(names)
    for r in features["records"]:
        if not r["dog_id"].startswith(ds + ":d"):
            errs.append(f"dog_id not neutral: {r['dog_id']}")
        if r["group"] not in GROUPS:
            errs.append(f"bad group {r['group']}")
        extra = set(r["values"]) - nameset
        if extra:
            errs.append(f"values not declared as variables: {sorted(extra)[:5]}")
        for k, c in (r.get("censored") or {}).items():
            if c not in ("floor", "ceiling"):
                errs.append(f"bad censored flag {k}={c}")
            if k not in nameset:
                errs.append(f"censored key not a variable: {k}")
        for k in r:
            if k.lower().startswith("original") or k in ("outcome", "died", "label"):
                errs.append(f"label-bearing key in features record: {k}")
    out_names = {o["name"] for o in outcomes["outcomes"]}
    for r in outcomes["records"]:
        extra = set(r["values"]) - out_names
        if extra:
            errs.append(f"outcome values not declared: {sorted(extra)}")
    fdogs = {r["dog_id"] for r in features["records"]}
    odogs = {r["dog_id"] for r in outcomes["records"]}
    if not odogs <= fdogs:
        errs.append(f"outcome dogs missing from features: {sorted(odogs - fdogs)[:5]}")
    if errs:
        raise SystemExit(f"{ds}: contract check failed:\n  " + "\n  ".join(errs))


def _dump(obj, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, ensure_ascii=False, indent=1, allow_nan=False)
    path.write_text(text + "\n", encoding="utf-8")


def mask_ids(features, dictionary_rows, checks, pattern, to_neutral):
    """Replace original IDs in the free text of the features file, the dictionary and the check names by neutral IDs.
    pattern: compiled regex whose group 1 is the original ID text; to_neutral(match) -> neutral dog_id or None (leave)."""
    def sub(text):
        if not isinstance(text, str):
            return text
        return pattern.sub(lambda m: to_neutral(m) or m.group(0), text)
    features["cleaning_notes"] = [sub(n) for n in features["cleaning_notes"]]
    for v in features["variables"]:
        v["original"] = sub(v["original"])
    for r in dictionary_rows:
        r["note"] = sub(r.get("note", ""))
    for c in checks.get("checks", []):
        c["name"] = sub(c["name"])
        c["source"] = sub(c.get("source", ""))


def write_dataset(features, outcomes, dictionary_rows, checks):
    """features/outcomes: dicts in the contract format. dictionary_rows: list of dicts with the columns
    harmonised_name, dataset_id, original_column, unit, conversion, note. checks: dict."""
    for r in features["records"]:
        r["values"] = {k: clean(v) for k, v in r["values"].items()}
        r.setdefault("censored", {})
    for r in outcomes["records"]:
        r["values"] = {k: clean(v) for k, v in r["values"].items()}
    _check(features, outcomes)
    ds = features["dataset_id"]
    _dump(features, TIDY / f"{ds}.features.json")
    _dump(outcomes, TIDY / f"{ds}.outcomes.json")
    dpath = OUT / "dictionary" / f"{ds}.csv"
    dpath.parent.mkdir(parents=True, exist_ok=True)
    cols = ["harmonised_name", "dataset_id", "original_column", "unit", "conversion", "note"]
    with open(dpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for row in dictionary_rows:
            w.writerow({c: row.get(c, "") for c in cols})
    failed = [c for c in checks.get("checks", []) if not c.get("pass")]
    checks["n_failed"] = len(failed)
    _dump(checks, OUT / "checks" / f"{ds}.json")
    print(f"{ds}: {len(features['records'])} feature records, {len({r['dog_id'] for r in features['records']})} dogs, "
          f"{len(features['variables'])} variables, {len(outcomes['records'])} outcome records; "
          f"checks {len(checks.get('checks', [])) - len(failed)}/{len(checks.get('checks', []))} passed")
    for c in failed:
        print("   FAILED:", c["name"], c.get("observed"), "expected", c.get("expected"))


def var(name, unit, original, floor=None, ceiling=None):
    return {"name": name, "unit": unit, "original": original, "floor": floor, "ceiling": ceiling}


def dict_row(name, ds, original, unit, conversion="", note=""):
    if name not in HARMONISED:
        note = ("Dataset-specific name (not in the harmonised list). " + note).strip()
    elif HARMONISED[name] not in (unit, "text") and name not in ("sex", "neuter"):
        raise SystemExit(f"{ds}: {name} has unit {unit}, harmonised unit is {HARMONISED[name]}")
    return {"harmonised_name": name, "dataset_id": ds, "original_column": original, "unit": unit,
            "conversion": conversion, "note": note}


def check(name, observed, expected, tol=0.0, source=""):
    if isinstance(expected, (int, float)) and isinstance(observed, (int, float)):
        ok = abs(observed - expected) <= tol
    else:
        ok = observed == expected
    return {"name": name, "observed": observed, "expected": expected, "tolerance": tol, "source": source, "pass": bool(ok)}


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def quantile(xs, q, qtype=7):
    """Type 7 (R default, Excel PERCENTILE.INC) or type 6 (Excel QUARTILE.EXC, SPSS) quantile."""
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    h = (len(xs) - 1) * q if qtype == 7 else min(max((len(xs) + 1) * q - 1, 0), len(xs) - 1)
    lo = math.floor(h)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (h - lo) * (xs[hi] - xs[lo])
