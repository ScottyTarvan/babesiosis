"""SV-10: render the three memos with their sample-size tables and write one load file per experiment.

Inputs:  memos/memo_*.md (the hand-written memos, with the line SAMPLE_SIZE_TABLE where the table goes)
         scripts/design.json (per memo: code, name, question, recommended scenario, gaps, assumptions)
         out/power.json (from scripts/power.py)
Outputs: out/memo_parasite_genotype.md, out/memo_host_genetics.md, out/memo_minimum_dataset.md
         out/db/<code>.json (way B of run-instructions.md, step 3)
Standard library only. No random numbers.
"""
import datetime
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SCRIPT = ROOT / "scripts" / "power.py"


def sha(path, n=None):
    h = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    return h[:n] if n else h


def fmt(v):
    if v is None or v == "":
        return "–"
    if isinstance(v, float):
        return f"{v:g}" if v >= 0.001 else f"{v:.1e}"
    return f"{v:,}" if isinstance(v, int) else str(v)


def table_md(rows, recommended):
    lines = ["| Scenario | Design | Severe (cases) | Mild (controls) | Total analysed | Cohort to enrol |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        cohort = [f"{r['cohort_needed']:,} ({r['cohort_basis']})"] if r.get("cohort_needed") else []
        mark = " (recommended)" if r["scenario"] == recommended else ""
        lines.append(f"| {r['scenario']}{mark} | {r['design']} | {r['n_cases']:,} | {r['n_controls']:,} | {r['n_total']:,} | "
                     f"{'; '.join(cohort) or '–'} |")
    return "\n".join(lines)


INLINE = [
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"), lambda m: m.group(1) if m.group(1).startswith("10.") else f"{m.group(1)} ({m.group(2)})"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"\1"),
    (re.compile(r"(?<![\w*])\*([^*]+)\*(?![\w*])"), r"\1"),
    (re.compile(r"`([^`]+)`"), r"\1"),
]


def plain(text):
    for rx, rep in INLINE:
        text = rx.sub(rep, text)
    return text.strip()


def parse_memo(md):
    """Markdown to {title, sections: [{heading, blocks}]}: paragraphs, h3, bullet lists, tables."""
    title, sections, cur, para, items, table = "", [], None, [], [], None

    def flush():
        nonlocal para, items, table
        if cur is None:
            para, items, table = [], [], None
            return
        if para:
            cur["blocks"].append({"type": "p", "text": plain(" ".join(para))})
        if items:
            cur["blocks"].append({"type": "ul", "items": [plain(i) for i in items]})
        if table:
            cur["blocks"].append({"type": "table", "header": table[0], "rows": table[1:]})
        para, items, table = [], [], None

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("# "):
            title = plain(line[2:])
            continue
        if line.startswith("## "):
            flush()
            cur = {"heading": plain(line[3:]), "blocks": []}
            sections.append(cur)
            continue
        if cur is None:
            if line.strip():
                cur = {"heading": "Status", "blocks": []}
                sections.append(cur)
            else:
                continue
        if line.startswith("### "):
            flush()
            cur["blocks"].append({"type": "h3", "text": plain(line[4:])})
        elif line.startswith("|"):
            if para or items:
                t = table
                table = None
                flush()
                table = t
            cells = [plain(c) for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c.strip()) for c in cells):
                continue
            table = (table or []) + [cells]
        elif re.match(r"^\s*(-|\d+\.)\s+", line):
            if para or table:
                it = items
                items = []
                flush()
                items = it
            items.append(re.sub(r"^\s*(-|\d+\.)\s+", "", line))
        elif re.match(r"^\s{2,}\S", line) and items:
            items[-1] += " " + line.strip()
        elif not line.strip():
            flush()
        else:
            if items or table:
                flush()
            para.append(line.strip())
    flush()
    return {"title": title, "sections": sections}


def main():
    power = json.loads((OUT / "power.json").read_text(encoding="utf-8"))
    design = json.loads((ROOT / "scripts" / "design.json").read_text(encoding="utf-8"))
    (OUT / "db").mkdir(parents=True, exist_ok=True)
    run_utc = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    script_version = sha(SCRIPT, 12)
    spec_sha = sha(ROOT / "spec.md")

    for d in design["memos"]:
        rows = [r for r in power["rows"] if r["memo"] == d["memo"]]
        rec = next((r for r in rows if r["scenario"] == d["recommended_scenario"]), None)
        if rec is None:
            raise SystemExit(f"recommended scenario not found for {d['memo']}: {d['recommended_scenario']}")
        src = (ROOT / "memos" / f"memo_{d['memo']}.md").read_text(encoding="utf-8")
        if "SAMPLE_SIZE_TABLE" not in src:
            raise SystemExit(f"memo_{d['memo']}.md has no SAMPLE_SIZE_TABLE line")
        rendered = src.replace("SAMPLE_SIZE_TABLE", table_md(rows, d["recommended_scenario"]))
        out_md = OUT / f"memo_{d['memo']}.md"
        out_md.write_text(rendered, encoding="utf-8", newline="\n")
        memo = parse_memo(rendered)
        words = len(re.findall(r"\w+", rendered))

        cohort = rec["cohort_needed"]
        recommendation = {
            "design": rec["design"], "scenario": rec["scenario"], "n_total": rec["n_total"],
            "n_cases": rec["n_cases"], "n_controls": rec["n_controls"],
            "cohort_needed": d.get("cohort_override", cohort), "detects": d["detects"], "basis": d["basis"],
        }
        size_rows = [dict(r, recommended=(r["scenario"] == d["recommended_scenario"])) for r in rows]
        primary = {"memo_title": d["short_title"], "question": d["question"], "recommendation": recommendation,
                   "assumptions": d["assumptions"], "gaps": d["gaps"], "caveat": d["caveat"]}
        sample = {"rows": size_rows, "calibration": power["calibration"],
                  "death_proportion": power["assumptions"]["death_proportion"],
                  "severe_proportion": power["assumptions"]["severe_set_proportion"],
                  "complicated_proportion": power["assumptions"]["complicated_proportion"]}
        memo_payload = {"title": memo["title"], "file": f"out/memo_{d['memo']}.md", "words": words, "sections": memo["sections"]}

        rec_text = (f"The recommended scenario ({rec['scenario']}) needs {rec['n_cases']:,} severe and {rec['n_controls']:,} mild dogs "
                    f"({rec['n_total']:,} in all)")
        if recommendation["cohort_needed"]:
            rec_text += f", from a cohort of about {recommendation['cohort_needed']:,} enrolled dogs"
        rec_text += f". It detects {d['detects']}."
        span = (min(r["n_total"] for r in rows), max(r["n_total"] for r in rows))
        interpretation = {"sections": [
            {"heading": "Question", "paragraphs": [d["question"]]},
            {"heading": "What was done", "paragraphs": [
                d["what_was_done"],
                f"Sample sizes: {len(rows)} scenarios from scripts/power.py (normal approximations, power 0.8, two-sided). "
                f"Formula check: the cohort formula gives a detectable OR of {power['calibration']['cohort_framing_detectable_or']} "
                f"for the S-CB050 age contrast; SV-05 reported {power['calibration']['sv05_reported']}."]},
            {"heading": "Result", "paragraphs": [rec_text, d["basis"],
                f"Across the scenarios the total ranges from {span[0]:,} to {span[1]:,} dogs."]},
            {"heading": "What this does not show", "paragraphs": d["does_not_show"]},
        ]}

        load = {
            "experiment": {
                "code": d["code"], "name": d["name"], "description": d["description"], "method": "study_design",
                "dataset": None,
                "parameters": {"package": "SV-10", "role": "descriptive", "datasets": [], "independent_sources": [],
                               "spec_sha256": spec_sha, "seed": None, "memo": f"/experiments/SV-10/out/memo_{d['memo']}.md",
                               "power": 0.8, "death_proportion": power["assumptions"]["death_proportion"],
                               "severe_proportion": power["assumptions"]["severe_set_proportion"],
                               "recommended_scenario": rec["scenario"]},
                "script": "/experiments/SV-10/scripts/power.py", "script_version": script_version, "run_utc": run_utc,
                "n_subjects": 0, "n_variables": 0, "n_tests": 0,
                "summary": f"{rec_text} No data analysed; {len(rows)} sample-size scenarios; 0 tests.",
            },
            "associations": [], "cluster_assignments": [],
            "results": [
                {"kind": "primary_result", "title": "Recommended design and sample size", "sort_order": 1, "payload": primary},
                {"kind": "sample_size", "title": "Sample-size scenarios", "sort_order": 2, "payload": sample},
                {"kind": "memo_sections", "title": "Design memo", "sort_order": 3, "payload": memo_payload},
                {"kind": "interpretation", "title": "Explanation and interpretation", "sort_order": 9, "payload": interpretation},
            ],
        }
        text = json.dumps(load, ensure_ascii=False, indent=1, allow_nan=False)
        if len(text.encode("utf-8")) > 900_000:
            raise SystemExit(f"{d['code']}: payloads too large")
        (OUT / "db" / f"{d['code']}.json").write_text(text, encoding="utf-8", newline="\n")
        print(d["code"], rec["n_total"], words, "words")


if __name__ == "__main__":
    main()
