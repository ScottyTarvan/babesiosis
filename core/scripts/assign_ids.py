"""Assign stable article IDs and build per-article extraction packets.

IDs live in ids.json (key -> {id, filename}); existing entries are never renumbered.
New canine records (include or uncertain at screening) get the next CB number in
first-publication-date order. An ID whose record is later excluded at full-text review
is retired (kept in ids.json with "retired": true) rather than reused.

Rounds 1-3 are read from search/; later rounds (search/rounds.json) from
search/<round>/candidates_all.jsonl, screening.jsonl and duplicates.json.

A background (BG) paper that a later round screens in is reclassified: its source key
gets a new CB ID ("replaces": "BG…"), and the BG entry is kept, retired, under
"RETIRED:<BG ID>" with "source_key" and "replaced_by". A retired record that a later
round finds again under another key gets a new CB ID, and the retired entry gets
"replaced_by".

Writes search/packets/<ID>.json containing everything an extraction agent needs.

Usage (from canine-babesiosis-review/):
    python -I scripts/assign_ids.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import load_rounds  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "search"
STOP = {"a", "an", "the", "of", "in", "and", "with", "for", "on", "to", "by", "dogs", "dog", "canine", "from", "at", "as", "is", "its"}


def slug(title, n=6):
    words = [w for w in re.sub(r"[^a-z0-9 ]+", " ", re.sub(r"<[^>]+>", "", title.lower())).split() if w not in STOP]
    return "-".join(words[:n]) or "untitled"


def key_of(x):
    return x.get("key") or (f"PMID:{x['pmid']}" if x.get("pmid") else (f"DOI:{x['doi']}" if x.get("doi") else x.get("source_id")))


def pending_articles():
    """Article-like rows for CB IDs that have a packet but no articles.jsonl row yet (assigned, not yet
    extracted), so fetch_fulltext.py, to_markdown.py and abstracts_to_markdown.py can work on them before
    extraction. Retired IDs are left out. scope_label is "pending extraction"; "replaces" names a
    reclassified ID whose files can be reused."""
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    done = {json.loads(l)["id"] for l in open(ROOT / "articles.jsonl", encoding="utf-8") if l.strip()}
    out = []
    for v in reg.values():
        p = S / "packets" / f"{v['id']}.json"
        if v.get("retired") or not v["id"].startswith("CB") or v["id"] in done or not p.exists():
            continue
        pk = json.loads(p.read_text(encoding="utf-8"))
        r = pk.get("record") or {}
        out.append({"id": v["id"], "title": r.get("title") or "", "doi": r.get("doi"), "pmid": r.get("pmid"),
                    "pmcid": r.get("pmcid"), "first_pub_date": r.get("first_pub_date") or r.get("year"),
                    "scope_label": "pending extraction", "include_type": (pk.get("screening") or {}).get("include_type"),
                    "fulltext_url": None, "source_links": [], "replaces": v.get("replaces")})
    return sorted(out, key=lambda a: a["id"])


def main():
    reg_path = ROOT / "ids.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {}
    cands = {}
    for fn in ("candidates.jsonl", "candidates_round2_all.jsonl", "candidates_r3.jsonl"):
        for l in open(S / fn, encoding="utf-8"):
            x = json.loads(l)
            cands[key_of(x)] = x
    scr = {}
    for fn in ("screening_r1.jsonl", "screening_r2.jsonl", "screening_r3.jsonl"):
        for l in open(S / fn, encoding="utf-8"):
            x = json.loads(l)
            scr[x["key"]] = dict(x, screening_round=fn[10:12])
    dups = json.loads((S / "duplicates.json").read_text(encoding="utf-8")) if (S / "duplicates.json").exists() else {}
    ft = {}
    for r in load_rounds()[1:]:
        d = ROOT / r["dir"]
        if not (d / "screening.jsonl").exists():
            continue
        for l in open(d / "candidates_all.jsonl", encoding="utf-8"):
            x = json.loads(l)
            cands[key_of(x)] = x
        for l in open(d / "screening.jsonl", encoding="utf-8"):
            x = json.loads(l)
            scr[x["key"]] = dict(x, screening_round=r["id"])
        if (d / "duplicates.json").exists():
            dups.update(json.loads((d / "duplicates.json").read_text(encoding="utf-8")))
        if (d / "fulltext_checks.jsonl").exists():
            for l in open(d / "fulltext_checks.jsonl", encoding="utf-8"):
                x = json.loads(l)
                ft[x["key"]] = x
    if (S / "fulltext_checks.jsonl").exists():
        for l in open(S / "fulltext_checks.jsonl", encoding="utf-8"):
            x = json.loads(l)
            ft[x["key"]] = x
    # Seed review: background reference.
    if "PMID:38695207" not in reg:
        reg["PMID:38695207"] = {"id": "BG001", "filename": "BG001_2024_global-systematic-review-meta-analysis-babesiosis.md"}
    keep = [k for k, s in scr.items() if s["decision"] in ("include", "uncertain") and k not in dups]
    keep.sort(key=lambda k: ((cands[k].get("first_pub_date") or f"{cands[k].get('year', '9999')}-12-31"), k))
    used = [int(v["id"][2:]) for v in reg.values() if v["id"].startswith("CB")]
    nxt = max(used, default=0) + 1
    key_by_id = {v["id"]: k for k, v in reg.items()}
    later = {r["id"] for r in load_rounds()[1:]}
    for k in keep:
        old = reg.get(k)
        if old and not (old["id"].startswith("BG") and scr[k]["screening_round"] in later):
            continue
        c = cands[k]
        year = (c.get("first_pub_date") or c.get("year") or "0000")[:4]
        new = {"id": f"CB{nxt:03d}", "filename": f"CB{nxt:03d}_{year}_{slug(c['title'])}.md"}
        if old:
            # Background paper inside a later round's window, screened in: reclassified as canine evidence.
            reg[f"RETIRED:{old['id']}"] = dict(old, retired=True, source_key=k, replaced_by=new["id"], retired_reason=(
                f"reclassified: inside the {scr[k]['screening_round']} window and included at screening, "
                f"so it is canine evidence ({new['id']}), not a background paper"))
            new["replaces"] = old["id"]
        elif c.get("existing_retired") and c.get("existing_id") in key_by_id:
            # A retired record found again under another key.
            reg[key_by_id[c["existing_id"]]]["replaced_by"] = new["id"]
            new["replaces"] = c["existing_id"]
        reg[k] = new
        nxt += 1
    reg_path.write_text(json.dumps(reg, indent=1, ensure_ascii=False), encoding="utf-8")
    (S / "packets").mkdir(exist_ok=True)
    dup_keys = {}
    for dk, dv in dups.items():
        dup_keys.setdefault(dv["canonical"], []).append(dk)
    for k, v in reg.items():
        if v.get("retired") or k not in cands and k != "PMID:38695207":
            continue
        if not v["id"].startswith("CB") and k != "PMID:38695207":  # HU/BG supporting records have no packet
            continue
        c = cands.get(k, {})
        packet = {"id": v["id"], "filename": v["filename"], "key": k, "record": c,
                  "screening": scr.get(k), "fulltext_check": ft.get(k)}
        # Later-round extras, left out of round 1-3 packets so those stay unchanged.
        if v.get("replaces"):
            packet["replaces"] = v["replaces"]
        if dup_keys.get(k) and scr.get(k, {}).get("screening_round") in later:
            packet["duplicate_records"] = [{"key": dk, "basis": dups[dk]["basis"], "record": cands.get(dk)} for dk in dup_keys[k]]
        (S / "packets" / f"{v['id']}.json").write_text(json.dumps(packet, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"registry={len(reg)} canine_ids={sum(1 for v in reg.values() if v['id'].startswith('CB'))}")


if __name__ == "__main__":
    main()
