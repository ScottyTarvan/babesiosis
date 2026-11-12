"""SV-08: human severity signatures (neutrophil granule, type 1 interferon) in the DS06 Beagle transcriptome.

Follows /experiments/SV-08/spec.md. Reads the DS06 count matrix, the SV-G1 DS02 tidy files and ref/ (Ensembl annotation
fetched once by fetch_annotation.py). Writes out/*.csv and out/results.json. Seed 20261112.
"""
import csv, gzip, hashlib, json, math, re, sys
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import rankdata, spearmanr, binomtest

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "out"
REF = HERE / "ref"
RAW = Path(r"C:\Workspaces\Babesiosis\core\data\raw\DS06\GSE167201_raw_counts.txt.gz")
TIDY = Path(r"C:\Workspaces\Babesiosis\experiments\shared\tidy")
FEAT = TIDY / "DS02.features.json"
OUTC = TIDY / "DS02.outcomes.json"
SPEC = HERE / "spec.md"
SPEC_SHA = "e7fdfabd75daee92de3c97b7b0e51f5967889297d539257b2590c1fa1d557547"
SEED = 20261112
N_RAND = 2000
SETS = json.loads((HERE / "scripts" / "gene_sets.json").read_text(encoding="utf-8"))["sets"]
SET_ORDER = ["neutrophil_granule", "type1_interferon", "erythroid_control"]
FAMILY = ["neutrophil_granule", "type1_interferon"]
DOGS = ["low_1", "low_2", "high_1", "high_2", "high_3"]
LAST_PRE = {"low_1": 4, "low_2": 4, "high_1": 4, "high_2": 4, "high_3": 3}
PRE_DAYS = [0, 1, 3, 4]
# SV-07 4.4: high_3 = dog 6 (probable); others = SV-07 best value assignment (unverified). Alternative swaps within dose.
MAP_WORK = {"low_1": "DS02:d005", "low_2": "DS02:d001", "high_1": "DS02:d004", "high_2": "DS02:d002", "high_3": "DS02:d003"}
MAP_ALT = {"low_1": "DS02:d001", "low_2": "DS02:d005", "high_1": "DS02:d002", "high_2": "DS02:d004", "high_3": "DS02:d003"}
PROTEIN_NAMES = {  # used only for genes that do not map by symbol or Ensembl ID (spec, gene mapping rule 3)
    "MPO": r"myeloperoxidase", "ELANE": r"elastase,? neutrophil", "OLFM4": r"olfactomedin 4",
    "CEACAM8": r"CEA cell adhesion molecule 8|carcinoembryonic antigen.*8", "ARG1": r"arginase[ -]1",
    "HBB": r"hemoglobin subunit beta|haemoglobin subunit beta|beta[- ]globin", "CTSG": r"cathepsin G",
}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def r4(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


def write_csv(name, rows, cols):
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: ("" if r.get(c) is None else r.get(c)) for c in cols})


def load_counts():
    with gzip.open(RAW, "rt", encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split("\t")[1:]
        ids, rows = [], []
        for line in f:
            p = line.rstrip("\n").split("\t")
            ids.append(p[0])
            rows.append([float(v) for v in p[1:]])
    return ids, header, np.array(rows)


def parse_sample(s):
    m = re.match(r"(low|high)_(\d)_D(\d)$", s)
    return {"sample": s, "dose": m.group(1), "dog": f"{m.group(1)}_{m.group(2)}", "day": int(m.group(3))}


def map_genes(ids):
    ens = [i.split("_", 1)[0] for i in ids]
    sym = [i.split("_", 1)[1] for i in ids]
    by_sym = {s: k for k, s in enumerate(sym) if s != ens[k]}
    by_ens = {e: k for k, e in enumerate(ens)}
    xrefs = json.loads((REF / "symbol_xrefs.json").read_text(encoding="utf-8"))
    lookup = json.loads((REF / "unsymbolled_lookup.json").read_text(encoding="utf-8"))
    gene_map, unmapped = [], []
    for st in SET_ORDER:
        for g in SETS[st]:
            row, how, note = None, None, ""
            if g in by_sym:
                row, how = by_sym[g], "symbol in DS06 row"
            dog_ids = [x["id"] for x in xrefs.get(g, []) if x.get("type") == "gene"]
            if row is None:
                for d in dog_ids:
                    if d in by_ens:
                        row, how = by_ens[d], "Ensembl dog gene ID"
                        break
            if row is None:
                pat = PROTEIN_NAMES.get(g)
                for e, v in sorted(lookup.items()):
                    if not v or e not in by_ens:
                        continue
                    if (v.get("display_name") or "").upper() == g or (pat and re.search(pat, v.get("description") or "", re.I)):
                        row, how = by_ens[e], f"current Ensembl annotation of unnamed row ({v.get('display_name')}: {v.get('description')})"
                        break
            rec = {"set": st, "gene": g, "mapped": row is not None, "row_id": ids[row] if row is not None else None,
                   "how": how, "dog_ensembl_ids": ";".join(dog_ids)}
            gene_map.append(rec)
            if row is None:
                reason = ("dog gene found in Ensembl (" + ";".join(dog_ids) + ") but not in the DS06 matrix, which was pre-filtered by CPM"
                          if dog_ids else "no dog gene with this symbol in Ensembl, and no unnamed DS06 row annotated as it")
                unmapped.append({"set": st, "gene": g, "dog_ensembl_ids": ";".join(dog_ids), "reason": reason})
            rec["_row"] = row
    return gene_map, unmapped


def percentiles(counts):
    n = counts.shape[0]
    pct = np.empty_like(counts)
    for j in range(counts.shape[1]):
        pct[:, j] = (rankdata(counts[:, j], method="average") - 1) / (n - 1)
    return pct


def main():
    if sha(SPEC) != SPEC_SHA:
        sys.exit("spec.md changed after the outcome lock")
    OUT.mkdir(exist_ok=True)
    ids, samples, counts = load_counts()
    meta = [parse_sample(s) if not s.startswith("low_0") else {"sample": s, "dose": "low", "dog": "low_0", "day": 0} for s in samples]
    col = {(m["dog"], m["day"]): j for j, m in enumerate(meta)}
    gene_map, unmapped = map_genes(ids)
    set_rows = {st: [g["_row"] for g in gene_map if g["set"] == st and g["_row"] is not None] for st in SET_ORDER}
    all_set_rows = sorted({r for v in set_rows.values() for r in v})

    pct = percentiles(counts)
    libsize = counts.sum(axis=0)
    uq = np.array([np.percentile(counts[counts[:, j] > 0, j], 75) for j in range(counts.shape[1])])
    log_uq = np.log2(counts / uq * uq.mean() / libsize.mean() * 1e6 + 1)  # UQ-scaled log2 CPM (S2)

    # S3: drop the reticulocyte-shift genes (percentile rho >= 0.8 with ALAS2 across 28 samples); set genes always kept
    alas2 = next(g["_row"] for g in gene_map if g["gene"] == "ALAS2")
    rho_alas2 = np.array([spearmanr(pct[i], pct[alas2]).statistic if np.ptp(pct[i]) > 0 else 0.0 for i in range(len(ids))])
    keep = (rho_alas2 < 0.8)
    keep[all_set_rows] = True
    n_dropped = int((~keep).sum())
    sub_idx = np.where(keep)[0]
    pct_s3_sub = percentiles(counts[sub_idx])
    pos_in_sub = {g: k for k, g in enumerate(sub_idx)}

    def score(st, j, kind="rank", rows=None):
        rows = set_rows[st] if rows is None else rows
        if not rows:
            return None
        if kind == "rank":
            return float(np.mean(pct[rows, j]))
        if kind == "s2":
            return float(np.mean(log_uq[rows, j]))
        if kind == "s3":
            return float(np.mean(pct_s3_sub[[pos_in_sub[r] for r in rows], j]))

    # composition background: per dog and set, 2,000 random sets matched on the dog's D0 percentile decile
    rng = np.random.default_rng(SEED)
    exclude = np.zeros(len(ids), bool)
    exclude[all_set_rows] = True
    background = {}
    for dog in DOGS:
        j0 = col[(dog, 0)]
        dec = np.minimum((pct[:, j0] * 10).astype(int), 9)
        pools = {d: np.where((dec == d) & ~exclude)[0] for d in range(10)}
        for st in SET_ORDER:
            rows = set_rows[st]
            if not rows:
                continue
            draws = np.stack([rng.choice(pools[dec[r]], size=N_RAND, replace=True) for r in rows], axis=1)  # N_RAND x k
            background[(dog, st)] = draws

    def bg_percentile(dog, st, j):
        draws = background[(dog, st)]
        j0 = col[(dog, 0)]
        rd = pct[draws, j].mean(axis=1) - pct[draws, j0].mean(axis=1)
        d = score(st, j) - score(st, j0)
        return float((np.sum(rd < d) + 0.5 * np.sum(rd == d)) / len(rd)), float(np.percentile(rd, 2.5)), float(np.percentile(rd, 97.5))

    feats = json.loads(FEAT.read_text(encoding="utf-8"))
    ds02 = {}
    for r in feats["records"]:
        if r["timepoint"] in ("day_0", "day_1", "day_3", "day_4", "day_6", "day_8"):
            ds02[(r["dog_id"], int(r["day"]))] = r["values"]
    outc = json.loads(OUTC.read_text(encoding="utf-8"))
    habitus, orig = {}, {}
    for r in outc["records"]:
        if r.get("original_id"):
            orig[r["dog_id"]] = r["original_id"]
        v = r.get("values", {}).get("habitus_score")
        if v is not None and r.get("day") is not None:
            habitus.setdefault(r["dog_id"], []).append((float(r["day"]), r.get("timepoint"), v))

    # ---------- set scores per sample ----------
    score_rows = []
    for j, m in enumerate(meta):
        for st in SET_ORDER:
            s = score(st, j)
            dog = m["dog"]
            delta = bgp = lo = hi = None
            if dog in DOGS:
                delta = s - score(st, col[(dog, 0)])
                if m["day"] > 0:
                    bgp, lo, hi = bg_percentile(dog, st, j)
            pw = ds02.get((MAP_WORK.get(dog), m["day"]), {}) if dog in DOGS else {}
            pa = ds02.get((MAP_ALT.get(dog), m["day"]), {}) if dog in DOGS else {}
            score_rows.append({
                "sample": m["sample"], "dog": dog, "dose": m["dose"], "day": m["day"],
                "post_treatment": m["day"] >= 6, "set": st, "n_genes": len(set_rows[st]), "score": r4(s),
                "delta_vs_d0": r4(delta), "bg_percentile": r4(bgp), "bg_delta_lo95": r4(lo), "bg_delta_hi95": r4(hi),
                "score_log2_uq": r4(score(st, j, "s2")), "score_rank_no_retic_genes": r4(score(st, j, "s3")),
                "library_size": int(libsize[j]),
                "ds02_dog_working": MAP_WORK.get(dog), "parasitaemia_working": pw.get("parasitaemia_pct"),
                "ds02_dog_alt": MAP_ALT.get(dog), "parasitaemia_alt": pa.get("parasitaemia_pct"),
            })
    write_csv("set_scores.csv", score_rows, list(score_rows[0].keys()))
    write_csv("unmapped_genes.csv", unmapped, ["set", "gene", "dog_ensembl_ids", "reason"])
    write_csv("gene_map.csv", gene_map, ["set", "gene", "mapped", "row_id", "how", "dog_ensembl_ids"])
    write_csv("library_sizes.csv", [{"sample": m["sample"], "dog": m["dog"], "day": m["day"], "library_size": int(libsize[j]),
                                     "alas2_percentile": r4(pct[alas2, j])} for j, m in enumerate(meta)],
              ["sample", "dog", "day", "library_size", "alas2_percentile"])

    # ---------- primary: delta D0 -> last pre-treatment, per dog ----------
    primary = []
    for dog in DOGS:
        j0, jl, j3 = col[(dog, 0)], col[(dog, LAST_PRE[dog])], col[(dog, 3)]
        for st in SET_ORDER:
            d = score(st, jl) - score(st, j0)
            bgp, lo, hi = bg_percentile(dog, st, jl)
            d_s1 = score(st, j3) - score(st, j0)
            bgp_s1, _, _ = bg_percentile(dog, st, j3)
            d_s2 = score(st, jl, "s2") - score(st, j0, "s2")
            d_s3 = score(st, jl, "s3") - score(st, j0, "s3")
            loo = [score(st, jl, rows=[r for r in set_rows[st] if r != x]) - score(st, j0, rows=[r for r in set_rows[st] if r != x])
                   for x in set_rows[st]] if len(set_rows[st]) > 1 else [d]
            primary.append({"dog": dog, "dose": dog.split("_")[0], "set": st, "n_genes": len(set_rows[st]),
                            "last_pre_day": LAST_PRE[dog], "score_d0": r4(score(st, j0)), "score_last": r4(score(st, jl)),
                            "delta": r4(d), "bg_percentile": r4(bgp), "bg_delta_lo95": r4(lo), "bg_delta_hi95": r4(hi),
                            "beyond_background": "rise" if bgp >= 0.975 else ("fall" if bgp <= 0.025 else "no"),
                            "s1_delta_d3": r4(d_s1), "s1_bg_percentile": r4(bgp_s1), "s2_delta_log2_uq": r4(d_s2),
                            "s3_delta_no_retic_genes": r4(d_s3), "s4_loo_min": r4(min(loo)), "s4_loo_max": r4(max(loo))})
    write_csv("primary_deltas.csv", primary, list(primary[0].keys()))

    signs = []
    for st in SET_ORDER:
        rows = [p for p in primary if p["set"] == st]
        k = sum(p["delta"] > 0 for p in rows)
        kb = sum(p["beyond_background"] == "rise" for p in rows)
        kf = sum(p["beyond_background"] == "fall" for p in rows)
        sens = {}
        for key, name in (("s1_delta_d3", "s1"), ("s2_delta_log2_uq", "s2"), ("s3_delta_no_retic_genes", "s3")):
            sens[name + "_positive"] = sum(p[key] > 0 for p in rows)
        sens["s1_beyond_rise"] = sum(p["s1_bg_percentile"] >= 0.975 for p in rows)
        sens["s4_positive_all_loo"] = sum(p["s4_loo_min"] > 0 for p in rows)
        signs.append({"set": st, "in_family": st in FAMILY, "n_dogs": len(rows), "positive": k,
                      "sign_test_p_two_sided": r4(binomtest(k, len(rows), 0.5).pvalue),
                      "beyond_background_rise": kb, "beyond_background_fall": kf,
                      "median_delta": r4(float(np.median([p["delta"] for p in rows]))), **sens})
    write_csv("sign_counts.csv", signs, list(signs[0].keys()))

    # ---------- timing ----------
    def first_risen(dog, st):
        for day in (1, 3, 4):
            if day > LAST_PRE[dog]:
                break
            bgp, _, _ = bg_percentile(dog, st, col[(dog, day)])
            if bgp >= 0.975:
                return day
        return None

    def deterioration(ds02_dog):
        h = sorted(habitus.get(ds02_dog, []))
        base = [v for d, tp, v in h if d in (-1.0, 0.0)]
        if not base:
            return None, None
        b = min(base)
        for d, tp, v in h:
            if d > 0 and v < b:
                return d, b
        return None, b

    timing = []
    for mapping_name, mp in (("working", MAP_WORK), ("alternative", MAP_ALT)):
        for dog in DOGS:
            det, base = deterioration(mp[dog])
            for st in SET_ORDER:
                fr = first_risen(dog, st)
                timing.append({"mapping": mapping_name, "dog": dog, "dose": dog.split("_")[0], "ds02_dog": mp[dog],
                               "ds02_original_id": orig.get(mp[dog]), "set": st, "first_risen_day": fr,
                               "habitus_baseline": base, "deterioration_day": det,
                               "risen_before_deterioration": (fr is not None and det is not None and fr < det)})
    write_csv("timing.csv", timing, list(timing[0].keys()))

    habitus_rows = [{"ds02_dog": k, "original_id": orig.get(k), "day": d, "timepoint": tp, "habitus_score": v}
                    for k in sorted(habitus) for d, tp, v in sorted(habitus[k])]
    write_csv("habitus.csv", habitus_rows, ["ds02_dog", "original_id", "day", "timepoint", "habitus_score"])

    verdict = {}
    for st in FAMILY:
        s = next(x for x in signs if x["set"] == st)
        appears = not (s["positive"] <= 2 or s["beyond_background_rise"] <= 2)
        tw = [t for t in timing if t["mapping"] == "working" and t["set"] == st]
        before = any(t["risen_before_deterioration"] for t in tw)
        before_alt = any(t["risen_before_deterioration"] for t in timing if t["mapping"] == "alternative" and t["set"] == st)
        fr = {t["dog"]: t["first_risen_day"] for t in tw}
        inf = lambda v: 99 if v is None else v
        low_min = min(inf(fr["low_1"]), inf(fr["low_2"]))
        earlier_high = all(inf(fr[d]) < low_min for d in ("high_1", "high_2", "high_3"))
        verdict[st] = {"signature_appears": appears, "before_deterioration_working": before,
                       "before_deterioration_alternative": before_alt, "earlier_at_high_dose": earlier_high}

    # ---------- construct checks ----------
    checks = []
    pairs = [("type1_interferon", "ip10", "plasma IP-10 (CXCL10 protein)"),
             ("neutrophil_granule", "neut_band", "band neutrophils"),
             ("erythroid_control", "retic_pct", "reticulocyte %")]
    for mapping_name, mp in (("working", MAP_WORK), ("alternative", MAP_ALT)):
        for st, var, label in pairs:
            rhos = []
            for dog in DOGS:
                xs, ys = [], []
                for day in PRE_DAYS:
                    if day > LAST_PRE[dog]:
                        continue
                    v = ds02.get((mp[dog], day), {}).get(var)
                    if v is None:
                        continue
                    xs.append(score(st, col[(dog, day)]))
                    ys.append(v)
                rho = spearmanr(xs, ys).statistic if len(xs) >= 3 and np.ptp(ys) > 0 and np.ptp(xs) > 0 else None
                rho = None if rho is None or not math.isfinite(rho) else rho
                rhos.append(rho)
                checks.append({"mapping": mapping_name, "set": st, "ds02_variable": var, "label": label, "dog": dog,
                               "n_points": len(xs), "spearman_rho": r4(rho)})
            vals = [r for r in rhos if r is not None]
            checks.append({"mapping": mapping_name, "set": st, "ds02_variable": var, "label": label, "dog": "median of dogs",
                           "n_points": len(vals), "spearman_rho": r4(float(np.median(vals))) if vals else None})
    write_csv("construct_checks.csv", checks, ["mapping", "set", "ds02_variable", "label", "dog", "n_points", "spearman_rho"])

    results = {
        "spec_sha256": SPEC_SHA, "seed": SEED, "n_random_sets": N_RAND,
        "inputs": {str(RAW): sha(RAW), str(FEAT): sha(FEAT), str(OUTC): sha(OUTC),
                   "ref/symbol_xrefs.json": sha(REF / "symbol_xrefs.json"),
                   "ref/unsymbolled_lookup.json": sha(REF / "unsymbolled_lookup.json"),
                   "scripts/gene_sets.json": sha(HERE / "scripts" / "gene_sets.json")},
        "versions": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__},
        "n_genes": len(ids), "n_samples": len(samples), "n_dogs": len(DOGS),
        "set_sizes": {st: {"fixed": len(SETS[st]), "mapped": len(set_rows[st])} for st in SET_ORDER},
        "s3_genes_dropped": n_dropped, "sign_counts": signs, "verdict": verdict,
        "mapping_working": MAP_WORK, "mapping_alternative": MAP_ALT, "last_pre_day": LAST_PRE,
    }
    (OUT / "results.json").write_text(json.dumps(results, indent=1, allow_nan=False), encoding="utf-8")
    for s in signs:
        print(s)
    print(json.dumps(verdict, indent=1))


if __name__ == "__main__":
    main()
