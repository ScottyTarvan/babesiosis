"""SV-INT integration build.

Reads scripts/synthesis.json (the curated synthesis table), checks every quoted number against the cited package report,
checks that every contributing experiment is Done in the ledger, combines every package's exposure.md into one log,
and writes out/ (tables, exposure log) and out/db/SV-INT-01-integration-report.json for the console loader.

Standard library only. No random numbers. Run from /experiments/SV-INT/ as: python -I scripts/build.py
"""
import csv
import hashlib
import json
import re
import sys
from collections import Counter, OrderedDict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
EXP = PKG.parent
OUT = PKG / "out"
CODE = "SV-INT-01-integration-report"

VERDICT_LABELS = {
    "supported": "Supported",
    "contradicted": "Contradicted",
    "not_supported_underpowered": "Not supported (underpowered)",
    "cannot_address": "Cannot address",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def norm(text: str) -> str:
    text = text.replace("−", "-").replace("–", "-").replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", text).strip()


_cache: dict = {}


def report_text(rel: str) -> str:
    if rel not in _cache:
        _cache[rel] = norm((EXP / rel).read_text(encoding="utf-8"))
    return _cache[rel]


def check_quotes(quotes, where, failures):
    for rel, q in quotes:
        if norm(q) not in report_text(rel):
            failures.append(f"{where}: not found in {rel}: {q!r}")


def ledger_status() -> dict:
    status = {}
    for line in (EXP / "ledger.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0].startswith("SV-"):
            status[cells[0]] = cells[3]
    return status


def exposure_log() -> list:
    rows = []
    for path in sorted(EXP.glob("SV-*/**/exposure.md")):
        rel = path.relative_to(EXP).as_posix()
        if rel.startswith("SV-INT/"):
            continue
        pkg = rel.split("/")[0] + ("" if rel.count("/") == 1 else rel.split("/")[1])
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("|"):
                cells = [c.strip() for c in s.strip("|").split("|")]
                if not cells or set("".join(cells)) <= set("-: ") or cells[0].lower().startswith("date"):
                    continue
            elif re.match(r"^\d{4}-\d{2}-\d{2}", s):
                cells = [c.strip() for c in s.split("|")]
            else:
                continue  # prose lines
            rows.append({"package": pkg, "file": rel, "entry": " | ".join(cells)})
    return rows


def main() -> int:
    syn = json.loads((HERE / "synthesis.json").read_text(encoding="utf-8"))
    failures: list = []
    status = ledger_status()

    # 1. quotes and ledger status
    codes = []
    for line in syn["lines"]:
        for f in line["findings"]:
            check_quotes(f["quotes"], f["code"], failures)
            codes.append(f["code"])
    for f in syn["foundations"]:
        check_quotes(f["quotes"], f["code"], failures)
        codes.append(f["code"])
    for key in ("sources_quotes", "candidates_quotes", "decisions_quotes"):
        check_quotes(syn[key], key, failures)
    for c in sorted(set(codes)):
        if status.get(c) != "Done":
            failures.append(f"ledger: {c} is {status.get(c)!r}, not Done")
    done = sorted(c for c, s in status.items() if s == "Done" and not c.startswith("SV-INT"))
    missing = [c for c in done if c not in set(codes)]
    if missing:
        failures.append(f"Done experiments not used by the synthesis: {missing}")
    if failures:
        print("CHECK FAILED", file=sys.stderr)
        for m in failures:
            print("  " + m, file=sys.stderr)
        return 1

    OUT.mkdir(exist_ok=True)
    (OUT / "db").mkdir(exist_ok=True)

    # 2. tables
    strength_counts = Counter()
    table_rows = []
    for line in syn["lines"]:
        for f in line["findings"]:
            strength_counts[f["strength"]] += 1
            table_rows.append(OrderedDict(
                line=line["label"], code=f["code"], asked=f["asked"], found=f["found"], effect=f["effect"], n=f["n"],
                independent_sources="; ".join(f["sources"]), detectable=f["detectable"], strength=f["strength"],
                verdict=VERDICT_LABELS[line["verdict"]]))
    with open(OUT / "synthesis_table.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(table_rows[0].keys()))
        w.writeheader()
        w.writerows(table_rows)

    exp_rows = exposure_log()
    with open(OUT / "exposure_log.md", "w", encoding="utf-8") as fh:
        fh.write("# Combined exposure log (all packages)\n\nBuilt by `SV-INT/scripts/build.py` from every package's `exposure.md`. "
                 "SV-INT itself opened no outcomes file.\n\n| Package | Source file | Entry |\n|---|---|---|\n")
        for r in exp_rows:
            fh.write(f"| {r['package']} | {r['file']} | {r['entry'].replace('|', '/')} |\n")
    with open(OUT / "decisions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["decision", "raised_by", "kind"])
        w.writeheader()
        w.writerows(syn["decisions"])

    # 3. load file
    verdicts = Counter(line["verdict"] for line in syn["lines"])
    n_find = len(table_rows)
    n_exp = len(set(codes))
    reports = sorted({rel for line in syn["lines"] for f in line["findings"] for rel, _ in f["quotes"]}
                     | {rel for f in syn["foundations"] for rel, _ in f["quotes"]})
    inputs = {rel: sha256(EXP / rel)[:12] for rel in reports}
    overall = (
        f"None of the five lines of explanation is supported by a replicated result. Time and parasite cannot be addressed with the "
        f"public files; load cannot be addressed in natural infection (in 5 Beagles damage followed load); host (age) and response "
        f"are not supported, with only large effects detectable. The signals that pass a test restate band neutrophils, anaemia or "
        f"the severity label, and most B. rossi outcome evidence comes from one hospital. The question needs new dog-level data "
        f"(SV-02c, SV-10).")
    lines_payload = [{
        "key": line["key"], "label": line["label"], "question": line["question"], "verdict": line["verdict"],
        "verdict_label": VERDICT_LABELS[line["verdict"]], "verdict_text": line["verdict_text"],
        "packages": sorted({f["code"].rsplit("-", 2)[0] if f["code"].startswith("SV-") else f["code"] for f in line["findings"]}),
        "findings": [{k: f[k] for k in ("code", "asked", "found", "effect", "n", "sources", "detectable", "strength")}
                     for f in line["findings"]],
    } for line in syn["lines"]]
    for lp in lines_payload:
        lp["packages"] = sorted({"-".join(f["code"].split("-")[:2]) for f in lp["findings"]})
    primary = {
        "research_question": syn["research_question"], "overall_answer": overall,
        "verdicts": [{"key": l["key"], "label": l["label"], "verdict": l["verdict"], "verdict_label": l["verdict_label"],
                      "n_findings": len(l["findings"]), "codes": [f["code"] for f in l["findings"]]} for l in lines_payload],
        "n_experiments": n_exp, "n_findings": n_find,
        "strength_counts": [{"strength": k, "label": syn["strength_classes"][k], "n": strength_counts.get(k, 0)}
                            for k in syn["strength_classes"]],
        "strength_classes": syn["strength_classes"],
        "caveat": "Synthesis of the package reports; no new test. Categories and extractions are by language-model agents; "
                  "SV-01's stage score failed validation; SV-06a's grades are one agent's unreviewed judgement; "
                  "died includes euthanasia in the Onderstepoort files; one species per source.",
    }
    summary = (
        f"Across {n_exp} Done experiments ({n_find} findings in 5 lines), no line of explanation is supported by a replicated result: "
        f"{verdicts['cannot_address']} cannot be addressed (time, load in natural infection, parasite) and "
        f"{verdicts['not_supported_underpowered']} are not supported with only large effects detectable (host: age OR 1.23, 0.34 to 4.15, "
        f"detectable OR about 3.7; response). Tested signals restate band neutrophils, anaemia or the label. No new tests (0 of 0).")
    interp = {"sections": [
        {"heading": "Question", "paragraphs": [
            f"{syn['research_question']} SV-INT reads the {n_exp} Done experiments of the programme and asks, for each of five lines "
            f"of explanation (time, load, host, parasite, response), whether the data support it, contradict it, or cannot address it."]},
        {"heading": "What was done", "paragraphs": [
            f"{n_find} findings were tabulated from the package reports, each with its effect, interval, n, independent sources, what "
            f"it could have detected and a strength class. Every number carries a literal quote that the build checks against the "
            f"report. Sources were counted after SV-07's linkage audit (DS03 natural dogs are S-CB050 dogs; DS03 experimental dogs "
            f"are the DS02 Beagles). The decisions for the user in all reports were merged into {len(syn['decisions'])} items, and the "
            f"{len(exp_rows)} exposure entries of all packages into one log. No outcomes file was opened and no test was run."]},
        {"heading": "Result", "paragraphs": [overall] + [f"{l['label']}: {l['verdict_text']}" for l in lines_payload]},
        {"heading": "What this does not show", "paragraphs": [
            "It does not show that time, load, host, parasite or the response do not matter. Most results are nulls from small files "
            "that could detect only large effects (for example OR about 3.7 for age and death, about 0.86 to 1.3 SD for markers).",
            "The candidates (band neutrophils, lactate, MCP-1, the interferon signature, haemoglobin beta, cortisol and thyroid, "
            "antibody) are leads to measure in a new cohort, not predictors. Residual axes are directions in a continuum, not groups "
            "of dogs. SV-02c (the author data request) was not run: it is a user decision."]},
    ]}
    load = {
        "experiment": {
            "code": CODE,
            "name": "Integration: why some dogs develop severe babesiosis, across all experiment packages",
            "description": ("Across the 22 Done experiments, which lines of explanation for severe against mild canine babesiosis "
                            "(time, load, host, parasite, response) do the data support, contradict or fail to address? There is no "
                            "hypothesis test; the synthesis states the strength of each piece of evidence and what it could detect."),
            "method": "integration_synthesis",
            "dataset": None,
            "parameters": {"package": "SV-INT", "role": "descriptive", "datasets": [],
                           "independent_sources": [s["source"] for s in syn["sources"]],
                           "spec_sha256": sha256(PKG / "spec.md"), "seed": None, "reports": inputs,
                           "synthesis_sha256": sha256(HERE / "synthesis.json")},
            "script": "/experiments/SV-INT/scripts/build.py",
            "script_version": sha256(Path(__file__))[:12],
            "run_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_subjects": 0, "n_variables": 0, "n_tests": 0,
            "summary": summary,
        },
        "associations": [], "cluster_assignments": [],
        "results": [
            {"kind": "primary_result", "title": "Verdict per line of explanation", "sort_order": 1, "payload": primary},
            {"kind": "lines", "title": "Findings by line: asked, found, strength", "sort_order": 2, "payload": lines_payload},
            {"kind": "independent_sources", "title": "Independent dog-level sources after the linkage audit", "sort_order": 3,
             "payload": syn["sources"]},
            {"kind": "foundations", "title": "Data layer, extraction and linkage", "sort_order": 4, "payload": [
                {"code": f["code"], "found": f["found"]} for f in syn["foundations"]]},
            {"kind": "candidates", "title": "Candidates to measure (not predictors)", "sort_order": 5, "payload": syn["candidates"]},
            {"kind": "decisions", "title": "Decisions for the user", "sort_order": 6, "payload": syn["decisions"]},
            {"kind": "exposure_log", "title": "Combined exposure log", "sort_order": 7, "payload": exp_rows},
            {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interp},
        ],
    }
    text = json.dumps(load, ensure_ascii=False, indent=1, allow_nan=False)
    (OUT / "db" / f"{CODE}.json").write_text(text, encoding="utf-8")
    print(f"quotes checked: all found; experiments {n_exp}; findings {n_find}; decisions {len(syn['decisions'])}; "
          f"exposure entries {len(exp_rows)}; load file {len(text.encode())} bytes")
    print("verdicts:", dict(verdicts))
    print("strength:", dict(strength_counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
