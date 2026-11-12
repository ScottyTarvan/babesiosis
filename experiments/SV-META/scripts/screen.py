"""SV-META steps 3, 6, 7 and 8: screen the census, attach candidates, read the refutation files, assign tiers, write leads.

Inputs: out/census_raw.csv (census.py), out/themes.csv (themes.py), scripts/candidates.json (candidate definitions, novelty and
human counterparts, written by the package agent from the novelty search), refutation/K*.json (one per refutation attempt).
Outputs: out/census.csv, out/candidates.csv, out/refutation.csv, out/leads.csv.

Tier rule (spec section 8): the provisional tier comes from the screen and the theme rows; a refutation can only lower it
(refuted -> X; a lower suggested tier is taken); it can never raise it.
"""
import csv
import json
import re
from math import sqrt
from pathlib import Path

from scipy import stats

PKG = Path(__file__).resolve().parent.parent
OUT = PKG / "out"
ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "X": 4}


def bh(ps):
    m = len(ps)
    order = sorted(range(m), key=lambda i: ps[i])
    q = [0.0] * m
    prev = 1.0
    for rank in range(m, 0, -1):
        i = order[rank - 1]
        prev = min(prev, ps[i] * m / rank)
        q[i] = prev
    return q


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


census = list(csv.DictReader((OUT / "census_raw.csv").open(encoding="utf-8")))
cands = json.loads((PKG / "scripts" / "candidates.json").read_text(encoding="utf-8"))

# ---- census family: every test/effect row with a p value
idx = [i for i, r in enumerate(census) if r["result_type"] in ("test", "effect") and fnum(r["p"]) is not None]
qc = bh([fnum(census[i]["p"]) for i in idx])
for r in census:
    r["q_census"] = ""
for j, i in enumerate(idx):
    census[i]["q_census"] = f"{qc[j]:.4g}"
CENSUS_FAMILY = len(idx)
# a declared family whose source file prints no q: BH inside that family (rows of the same experiment and family label)
fams = {}
for i, r in enumerate(census):
    if r["family"] and not r["q"] and fnum(r["p"]) is not None:
        fams.setdefault((r["experiment"], r["family"]), []).append(i)
for key, members in fams.items():
    qs = bh([fnum(census[i]["p"]) for i in members])
    for i, qv in zip(members, qs):
        census[i]["q"] = f"{qv:.4g}"
        census[i]["note"] = (census[i]["note"] + "; " if census[i]["note"] else "") + "q computed here (BH inside the declared family)"


def null_value(effect_type):
    t = effect_type.lower()
    if "odds" in t:
        return 1.0
    if t in ("phi", "share", "reading", "verdict", "gap rank", "ratio to baseline", "count", "checks passed", "missing",
             "units h/l/n", "expected by chance", "odds ratio detectable"):
        return None
    return 0.0


def ns(n):
    parts = re.findall(r"\d+", n or "")
    return [int(p) for p in parts]


def detectable(r):
    n = ns(r["n"])
    t = r["effect_type"].lower()
    z = stats.norm.ppf(0.975) + stats.norm.ppf(0.8)
    if " vs " in r["n"] and len(n) >= 2 and ("cliff" in t):
        n1, n2 = (n[0] + n[1], n[2]) if "+" in r["n"] and len(n) == 3 else (n[0], n[1])
        d = z * sqrt(1 / n1 + 1 / n2)
        return f"Cliff's delta {2 * stats.norm.cdf(d / sqrt(2)) - 1:.2f} (d {d:.2f})"
    if ("rho" in t) and len(n) == 1 and n[0] > 3:
        return f"|rho| {abs(__import__('math').tanh(z / sqrt(n[0] - 3))):.2f}"
    return ""


def screen(r):
    """Return (pass flag, reason)."""
    if r["result_type"] not in ("test", "effect"):
        return "n/a", "observation or design: no test"
    eff, lo, hi = fnum(r["effect"]), fnum(r["ci_low"]), fnum(r["ci_high"])
    nv = null_value(r["effect_type"])
    if r["experiment"].startswith("SV-08") and r["result_type"] == "test" and "of 5 dogs rose" in r["note"]:
        k = int(re.search(r"(\d+) of 5 dogs rose", r["note"]).group(1))
        return ("pass", "5 of 5 dogs in one direction (minimum p 0.0625); within-dog change, no severity contrast") if k == 5 else \
            ("fail", f"{k} of 5 dogs")
    if nv is None:
        return "n/a", "effect type without a null value"
    ci_ok = None if lo is None or hi is None else (lo > nv or hi < nv)
    q = fnum(r["q"]) if r["q"] else None
    if q is None:
        q = fnum(r["q_census"])
        fam = f"census family of {CENSUS_FAMILY}"
    else:
        fam = f"own family of {r['family_size']}"
    if q is None:
        return ("fail" if not ci_ok else "fail"), "no p value: interval only" + ("" if ci_ok else "; interval includes the null")
    ok = q < 0.05 and (ci_ok is not False)
    why = f"q {q:.3g} ({fam}); interval {'excludes' if ci_ok else ('includes' if ci_ok is False else 'not given for')} the null"
    return ("pass" if ok else "fail"), why


cand_by_row = {}
for c in cands["candidates"]:
    for m in c.get("census_match", []):
        for r in census:
            if r["experiment"].startswith(m["experiment"]) and all(s.lower() in (r["measure"] + " | " + r["comparison"] + " | " +
                                                                               r["dataset"]).lower() for s in m["contains"]):
                cand_by_row.setdefault(r["row_id"], []).append(c["id"])

# ---- refutation files
refs = {}
for p in sorted((PKG / "refutation").glob("K*.json")):
    refs[p.stem] = json.loads(p.read_text(encoding="utf-8"))

ref_rows = []
for c in cands["candidates"]:
    prov = c["provisional_tier"]
    final = prov
    if c["id"] in refs:
        rf = refs[c["id"]]
        for a in rf["attempts"]:
            ref_rows.append(dict(candidate_id=c["id"], candidate=c["label"], provisional_tier=prov, by="sub-agent (fresh context)",
                                 reason_tested=a["reason_tested"], method=a["method"], result=a["result"],
                                 rejects="yes" if a["rejects"] else "no"))
        verdict = rf["verdict"]
        sug = rf.get("suggested_tier", prov)
        if verdict == "refuted":
            final = "X"
        elif sug in ORDER and ORDER[sug] > ORDER[prov]:
            final = sug
        c["refutation_verdict"] = verdict
        c["refutation_reason"] = rf["verdict_reason"]
        c["suggested_tier"] = sug
        c["canine_parallel_already_made"] = rf.get("canine_parallel_already_made", "")
        c["human_counterpart_checked"] = rf.get("human_counterpart", [])
    else:
        ref_rows.append(dict(candidate_id=c["id"], candidate=c["label"], provisional_tier=prov, by="screen (package agent)",
                             reason_tested=c.get("screen_reason_code", "screen"), method="screen of spec section 6",
                             result=c["screen_reason"], rejects="yes" if prov == "X" else "no"))
        c["refutation_verdict"] = "rejected at screen" if prov == "X" else "not attempted"
        c["refutation_reason"] = c["screen_reason"]
        c["suggested_tier"] = prov
    c["final_tier"] = final

tiers = {c["id"]: c["final_tier"] for c in cands["candidates"]}
for r in census:
    flag, why = screen(r)
    r["stat_screen"], r["stat_reason"] = flag, why
    r["detectable"] = detectable(r)
    ids = cand_by_row.get(r["row_id"], [])
    r["candidates"] = ";".join(ids)
    r["tier"] = min((tiers[i] for i in ids), key=lambda t: ORDER[t]) if ids else ("X" if flag == "pass" else "")
    meta = next((c for c in cands["candidates"] if c["id"] in ids), None)
    r["circularity"] = meta["circularity"] if meta else ""
    r["novelty"] = meta["novelty"] if meta else ""

FIELDS = list(census[0].keys())
with (OUT / "census.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(census)

unmatched_pass = [r["row_id"] for r in census if r["stat_screen"] == "pass" and not r["candidates"]]
if unmatched_pass:
    raise SystemExit(f"passing census rows without a candidate: {unmatched_pass}")

CF = ["id", "label", "kind", "theme", "provisional_tier", "final_tier", "circularity", "novelty", "novelty_where", "sources",
      "evidence", "screen_reason", "refutation_verdict", "refutation_reason"]
with (OUT / "candidates.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=CF, lineterminator="\n", extrasaction="ignore")
    w.writeheader()
    for c in cands["candidates"]:
        w.writerow({k: c.get(k, "") for k in CF})

RF = ["candidate_id", "candidate", "provisional_tier", "by", "reason_tested", "method", "result", "rejects"]
with (OUT / "refutation.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=RF, lineterminator="\n")
    w.writeheader()
    w.writerows(ref_rows)

# ---- leads: only candidates whose final tier is A-D, in the order of candidates.json "lead_order"
leads = []
for rank, lid in enumerate(cands["lead_order"], start=1):
    L = next(l for l in cands["leads"] if l["id"] == lid)
    t = min((tiers[k] for k in L["candidates"]), key=lambda x: ORDER[x])
    if t == "X":
        continue
    leads.append(dict(rank=len(leads) + 1, lead_id=lid, tier=t, kind=L["kind"], hypothesis=L["hypothesis"],
                      candidates=";".join(L["candidates"]), evidence=L["evidence"], human_counterpart=L["human_counterpart"],
                      human_doi=";".join(L["human_doi"]), parallel_new=L["parallel_new"], refuted_by=L["refuted_by"],
                      next_study_existing_data=L["next_existing"], next_study_new_dogs=L["next_new_dogs"],
                      minimum_dataset_addition=L["minimum_dataset"]))
if len(leads) > 10:
    raise SystemExit("more than 10 leads")
LF = list(leads[0].keys()) if leads else ["rank"]
with (OUT / "leads.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=LF, lineterminator="\n")
    w.writeheader()
    w.writerows(leads)

counts = {t: sum(1 for c in cands["candidates"] if c["final_tier"] == t) for t in "ABCDX"}
(OUT / "tiers.json").write_text(json.dumps({"counts": counts, "census_family": CENSUS_FAMILY,
                                            "census_rows": len(census),
                                            "census_pass": sum(1 for r in census if r["stat_screen"] == "pass"),
                                            "leads": len(leads)}, indent=1), encoding="utf-8")
print("tiers", counts, "leads", len(leads), "census pass", sum(1 for r in census if r["stat_screen"] == "pass"))
