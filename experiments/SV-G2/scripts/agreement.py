"""Agreement between two extractions of the same articles (spec.md, "Quality check").

Compares a reference folder (default extractions/) with a second folder (default second/) for the articles present
in both, and optionally the v2 calibration batch with the pilot files in /core/data/severity/extractions/ (--pilot).

Outputs (in out/): agreement_<name>.json (summary) and agreement_<name>_pairs.csv (every matched and unmatched key).
Standard library only. Usage (from /experiments/SV-G2/):
    python -I scripts/agreement.py --name second
    python -I scripts/agreement.py --name pilot --other ../../core/data/severity/extractions
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_associations import load_map, map_marker  # noqa: E402

PKG = Path(__file__).resolve().parent.parent
UP = {"higher_in_severe", "more_frequent_in_severe", "positive_association"}
DOWN = {"lower_in_severe", "less_frequent_in_severe", "negative_association"}


def dgroup(d):
    return "up" if d in UP else "down" if d in DOWN else "null" if d == "no_difference" else "other"


def keyed(path, canon, alias, patterns):
    data = json.loads(path.read_text(encoding="utf-8"))
    cls = {d["key"]: d["outcome_class"] for d in data.get("severity_definitions", [])}
    rows = collections.OrderedDict()
    for a in data.get("associations", []):
        marker = map_marker(a, canon, alias, patterns)[0] or a.get("marker", "")
        k = (marker, cls.get(a.get("severity_key"), ""))
        rows.setdefault(k, a)  # first row by row order
    return set(cls.values()), rows


def kappa(pairs):
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return None if pe == 1 else round((po - pe) / (1 - pe), 3)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--ref", default="extractions")
    ap.add_argument("--other", default="second")
    args = ap.parse_args()
    canon, alias, patterns = load_map()
    ref_dir, oth_dir = PKG / args.ref, (PKG / args.other).resolve()
    ids = sorted({p.stem for p in ref_dir.glob("*.json")} & {p.stem for p in oth_dir.glob("*.json")})
    class_pairs = class_union = same_sets = 0
    pairs_out, sig_pairs = [], []
    matched = same_dir = same_sig = same_both = ref_keys = oth_keys = 0
    per_article = []
    for i in ids:
        c1, r1 = keyed(ref_dir / f"{i}.json", canon, alias, patterns)
        c2, r2 = keyed(oth_dir / f"{i}.json", canon, alias, patterns)
        class_pairs += len(c1 & c2)
        class_union += len(c1 | c2)
        same_sets += c1 == c2
        ref_keys += len(r1)
        oth_keys += len(r2)
        m = d_ok = s_ok = 0
        for k in sorted(set(r1) | set(r2)):
            a, b = r1.get(k), r2.get(k)
            row = {"id": i, "marker": k[0], "outcome_class": k[1], "in_ref": a is not None, "in_other": b is not None,
                   "dir_ref": a.get("direction") if a else "", "dir_other": b.get("direction") if b else "",
                   "sig_ref": a.get("significant") if a else "", "sig_other": b.get("significant") if b else ""}
            if a and b:
                m += 1
                dd = dgroup(a["direction"]) == dgroup(b["direction"])
                ss = a["significant"] == b["significant"]
                d_ok += dd
                s_ok += ss
                same_both += dd and ss
                sig_pairs.append((a["significant"], b["significant"]))
                row["same_direction"], row["same_significance"] = dd, ss
            pairs_out.append(row)
        matched += m
        same_dir += d_ok
        same_sig += s_ok
        per_article.append({"id": i, "classes_ref": sorted(c1), "classes_other": sorted(c2), "keys_ref": len(r1),
                            "keys_other": len(r2), "matched": m, "same_direction": d_ok, "same_significance": s_ok})
    rnd = lambda x, y: round(x / y, 3) if y else None
    summary = {
        "name": args.name, "reference": args.ref, "other": args.other, "articles": len(ids),
        "outcome_class": {"jaccard_pooled": rnd(class_pairs, class_union), "articles_identical_sets": same_sets},
        "matched_pairs": matched, "ref_keys": ref_keys, "other_keys": oth_keys,
        "coverage_ref_found_by_other": rnd(matched, ref_keys), "coverage_other_found_by_ref": rnd(matched, oth_keys),
        "direction_agreement": rnd(same_dir, matched), "significance_agreement": rnd(same_sig, matched),
        "both_agree": rnd(same_both, matched), "significance_kappa": kappa(sig_pairs),
        "per_article": per_article,
    }
    out = PKG / "out"
    out.mkdir(exist_ok=True)
    (out / f"agreement_{args.name}.json").write_text(json.dumps(summary, indent=1, allow_nan=False), encoding="utf-8")
    with open(out / f"agreement_{args.name}_pairs.csv", "w", encoding="utf-8", newline="") as fh:
        fields = ["id", "marker", "outcome_class", "in_ref", "in_other", "dir_ref", "dir_other", "sig_ref", "sig_other",
                  "same_direction", "same_significance"]
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(pairs_out)
    print(json.dumps({k: v for k, v in summary.items() if k != "per_article"}, indent=1))


if __name__ == "__main__":
    main()
