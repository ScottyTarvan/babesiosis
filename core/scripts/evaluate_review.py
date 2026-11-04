"""Score the scispaCy categorisation, the study-aim rules and the screening agents against the human review decisions.

Input: the review page's decisions, exported with the ArtifactData tool (`list` of collection "decisions"
with out_dir data/syndromes/review/export), i.e. data/syndromes/review/export/decisions/<ID>.json, plus
data/syndromes/article_categories.csv and review/queue.json.

A decision is complete once it has a study aim (`aim`); decisions saved before the aim and the
studied/mentioned split were added are counted separately and left out of the scores until updated.
Human labels: aim, primary (the organ system mainly measured), secondary (other systems studied) and
mentioned (systems only discussed or cited).

The queue is every disagreement (a census) plus a random sample of agreements (`sampled` in queue.json), so
each method's primary-category accuracy over all agent-labelled articles is estimated as
    (correct among reviewed disagreements + sample accuracy x number of agreements) / total
and is reported only once every disagreement is reviewed. Groups are taken from the current
article_categories.csv: if the scoring changed after the queue was built, rebuild the queue first.
Decisions are split by whether the reviewer saw the suggestions before choosing
(`suggestions_seen_before_choice`); blind decisions are the cleaner reference. The agents labelled before the
studied/mentioned split, so their categories are measured against a stricter definition than they used.

Writes data/syndromes/review/evaluation.md and reference_labels.csv (the human labels, for reuse).

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/evaluate_review.py [export_dir]
"""
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REV = ROOT / "data" / "syndromes" / "review"
CATS = ["ERY", "INF", "END", "COA", "REN", "PUL", "NEU", "CAR", "MET", "OXO", "SEV"]


def load_decisions(export_dir):
    out = {}
    for p in sorted(Path(export_dir).rglob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        d = d.get("data", d) if isinstance(d, dict) else {}
        if d.get("id") and d.get("primary"):
            out[d["id"]] = d
    return out


def kappa(pairs):
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[l] * cb[l] for l in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def pct(a, b):
    return f"{a}/{b} ({a / b:.0%})" if b else "0/0"


def jac(a, b):
    return len(a & b) / len(a | b) if a | b else 1.0


def main():
    export = Path(sys.argv[1]) if len(sys.argv) > 1 else REV / "export"
    dec_all = load_decisions(export)
    rows = {r["id"]: r for r in csv.DictReader(open(ROOT / "data" / "syndromes" / "article_categories.csv", encoding="utf-8")) if r["agent_primary"]}
    queue = {i["id"]: i for i in json.loads((REV / "queue.json").read_text(encoding="utf-8"))["items"]}
    dec = {i: d for i, d in dec_all.items() if d.get("aim") and i in rows}
    old = sorted(i for i, d in dec_all.items() if not d.get("aim"))
    n_dis_total = sum(r["agree_primary"] != "True" for r in rows.values())
    n_agr_total = len(rows) - n_dis_total
    reviewed = sorted(dec)
    if not reviewed:
        print(f"no complete decisions under {export} ({len(old)} saved before the study aim was added)")
        return

    def stats(ids):
        res = {}
        for name, key in (("scispaCy", "nlp_primary"), ("agents", "agent_primary")):
            pairs = [(rows[i][key], dec[i]["primary"]) for i in ids]
            res[name] = (sum(a == b for a, b in pairs), len(pairs), kappa(pairs))
        return res

    dis = [i for i in reviewed if rows[i]["agree_primary"] != "True"]
    agr = [i for i in reviewed if rows[i]["agree_primary"] == "True" and queue.get(i, {}).get("sampled", True)]
    blind = [i for i in reviewed if not dec[i].get("suggestions_seen_before_choice")]
    L = ["# Category review: methods against the human reference", "",
         f"{len(reviewed)} articles reviewed: {len(dis)} of {n_dis_total} disagreements, {len(agr)} from the agreement sample "
         f"({n_agr_total} agreements in all); {len(blind)} decided blind (suggestions hidden until the choice). "
         f"{sum(bool(dec[i].get('unsure')) for i in reviewed)} marked unsure. "
         f"{len(old)} decision{'s' if len(old) != 1 else ''} saved before the study aim was added are not scored until updated"
         f"{': ' + ', '.join(old) if old else ''}. Method: `scripts/evaluate_review.py`.", "",
         "## Primary category (organ system mainly measured)", "",
         "| Set | scispaCy correct | agents correct | scispaCy kappa | agents kappa |", "|---|---|---|---|---|"]
    for label, ids in (("All reviewed", reviewed), ("Disagreements", dis), ("Agreement sample", agr), ("Blind decisions only", blind),
                       ("Full text", [i for i in reviewed if rows[i]["source_format"] != "abstract"]),
                       ("Abstract only", [i for i in reviewed if rows[i]["source_format"] == "abstract"])):
        s = stats(ids)
        L.append(f"| {label} | {pct(*s['scispaCy'][:2])} | {pct(*s['agents'][:2])} | {s['scispaCy'][2]:.2f} | {s['agents'][2]:.2f} |")
    if agr and len(dis) == n_dis_total:
        agr_ok = sum(rows[i]["nlp_primary"] == dec[i]["primary"] for i in agr) / len(agr)  # same for both methods here
        est = {name: (sum(rows[i][key] == dec[i]["primary"] for i in dis) + agr_ok * n_agr_total) / len(rows)
               for name, key in (("scispaCy", "nlp_primary"), ("agents", "agent_primary"))}
        L += ["", f"Estimated accuracy over all {len(rows)} agent-labelled articles (disagreements reviewed in full; agreements "
                  f"from the {len(agr)}-article sample, {agr_ok:.0%} correct): scispaCy {est['scispaCy']:.0%}, agents {est['agents']:.0%}."]
    else:
        L += ["", "Whole-set accuracy is estimated once every disagreement and part of the agreement sample are reviewed."]

    L += ["", "## Per category (all reviewed)", "", "| Human category | Articles | scispaCy agrees | agents agree |", "|---|---|---|---|"]
    by = collections.defaultdict(list)
    for i in reviewed:
        by[dec[i]["primary"]].append(i)
    for c in CATS + ["NONE"]:
        ids = by.get(c, [])
        if ids:
            L.append(f"| {c} | {len(ids)} | {pct(sum(rows[i]['nlp_primary'] == c for i in ids), len(ids))} | "
                     f"{pct(sum(rows[i]['agent_primary'] == c for i in ids), len(ids))} |")

    # study aim: keyword rules against the reviewer
    aim_pairs = [(rows[i]["aim"], dec[i]["aim"]) for i in reviewed]
    L += ["", "## Study aim (keyword rules)", "",
          f"Rules correct: {pct(sum(a == b for a, b in aim_pairs), len(aim_pairs))}; kappa {kappa(aim_pairs):.2f}.", "",
          "| Reviewer's aim | Articles | Rules agree | Rules said instead |", "|---|---|---|---|"]
    by_aim = collections.defaultdict(list)
    for a, h in aim_pairs:
        by_aim[h].append(a)
    for h in sorted(by_aim, key=lambda h: -len(by_aim[h])):
        got = by_aim[h]
        wrong = collections.Counter(a for a in got if a != h)
        L.append(f"| {h} | {len(got)} | {pct(sum(a == h for a in got), len(got))} | "
                 f"{', '.join(f'{a} {n}' for a, n in wrong.most_common()) or ''} |")

    # studied vs mentioned
    studied = {i: {dec[i]["primary"], *dec[i].get("secondary", [])} - {"NONE"} for i in reviewed}
    mentioned = {i: set(dec[i].get("mentioned", [])) for i in reviewed}
    nlp_st = {i: {rows[i]["nlp_primary"], *rows[i]["nlp_secondary"].split()} - {"none"} for i in reviewed}
    nlp_me = {i: set(rows[i]["nlp_mentioned"].split()) for i in reviewed}
    ag_st = {i: {rows[i]["agent_primary"], *rows[i]["agent_secondary"].split()} for i in reviewed}
    n = len(reviewed)
    L += ["", "## Studied and mentioned categories", "",
          "Mean overlap (Jaccard) with the reviewer's sets, and how often a category the reviewer marked as only mentioned was "
          "counted as studied (primary or secondary).", "",
          "| | Studied set overlap | Mentioned set overlap | Mentioned-only categories counted as studied |", "|---|---|---|---|",
          f"| scispaCy | {sum(jac(nlp_st[i], studied[i]) for i in reviewed) / n:.2f} | {sum(jac(nlp_me[i], mentioned[i]) for i in reviewed) / n:.2f} | "
          f"{pct(sum(len(nlp_st[i] & mentioned[i]) for i in reviewed), sum(len(mentioned[i]) for i in reviewed))} |",
          f"| agents | {sum(jac(ag_st[i], studied[i]) for i in reviewed) / n:.2f} | n/a (no split) | "
          f"{pct(sum(len(ag_st[i] & mentioned[i]) for i in reviewed), sum(len(mentioned[i]) for i in reviewed))} |"]
    (REV / "evaluation.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    with open(REV / "reference_labels.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "aim", "primary", "secondary", "mentioned", "unsure", "decided_blind", "note", "saved_at",
                    "rule_aim", "agent_primary", "nlp_primary"])
        for i in reviewed:
            d = dec[i]
            w.writerow([i, d["aim"], d["primary"], " ".join(d.get("secondary") or []), " ".join(d.get("mentioned") or []),
                        bool(d.get("unsure")), not d.get("suggestions_seen_before_choice"), d.get("note", ""), d.get("saved_at"),
                        rows[i]["aim"], rows[i]["agent_primary"], rows[i]["nlp_primary"]])
    print(f"{len(reviewed)} complete decisions ({len(old)} awaiting a study aim); wrote {REV / 'evaluation.md'} and reference_labels.csv")


if __name__ == "__main__":
    main()
