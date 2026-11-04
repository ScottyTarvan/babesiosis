"""Render datasets.md from datasets.jsonl, adding priority ranks and independent-source groups.

Priority ranks and source groups are curated below (reviewer judgement from the agent
assessments: mechanistic relevance, independent n, phenotype richness, documentation,
reuse terms, feasibility). They are written back into datasets.jsonl so the Markdown and
JSONL stay consistent.

Usage:
    python -I scripts/render_datasets.py
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (dataset_id, independent source group, one-line rationale for rank)
PRIORITY = [
    ("S-CB050", "SRC-A", "Largest verified B. rossi cohort with a hard outcome (survival) and admission cytokines/MPXI; one row per dog."),
    ("DS01", "SRC-B", "Controlled experimental B. rossi infection: daily multi-system clinical, haematology, lactate, cell-free Hb and 13-plex cytokine time series."),
    ("DS06", "SRC-B", "Whole-blood RNA-seq time course from the same experimental programme (CH09) — enables within-dog integration with DS01/DS02 if dogs can be matched."),
    ("DS07", "SRC-C", "Serum TMT proteome of 52 dogs with control/uncomplicated/complicated labels; RAW data also public."),
    ("S-CB017", "SRC-D", "B. canis (Croatia) per-dog cytokines and haematology at two time points with complicated/uncomplicated labels."),
    ("DS03", "SRC-E", "Reticulocyte indices in natural (n≈118) and experimental B. rossi plus IMHA and healthy comparators; low-dimensional, statistics-friendly. Its experimental subset overlaps SRC-B and its natural cohorts may overlap other Onderstepoort cohorts."),
    ("DS05", "SRC-F", "150 naturally infected dogs (B. rossi) with admission clinical exam, CBC, reticulocytes, proteins and co-infection PCR; no outcome label."),
    ("DS02", "SRC-B", "Overlapping copy of the DS01 experiment (UP repository version, with extra variables); use with DS01, not as replication."),
    ("S-CB517", "SRC-A", "Per-dog leukocyte differentials, SAA, CRP and 7 cytokines with survival for 112 dogs (97 B. rossi, 15 controls); its cytokines duplicate 112 of the S-CB050 dogs, so use it to add the acute phase proteins and differentials, not as replication."),
    ("DS04", "SRC-G", "Fatal B. rossi liver histopathology/IHC score sheets with haematology/biochemistry (Onderstepoort tissue bank, CH04)."),
    ("S-CB147", "SRC-G", "Published per-dog liver IHC tables for the same CH04 dogs as DS04."),
    ("S-CB071", "SRC-H", "Urine metabolomics (untargeted + targeted) by kidney-function group, B. canis (Zagreb MetaDog, CH06)."),
    ("S-CB091", "SRC-H", "Serum multi-platform metabolomics, B. canis vs controls (CH06; probable dog overlap with S-CB071/S-CB137)."),
    ("S-CB137", "SRC-H", "Salivary metabolomics, B. canis vs controls (CH06)."),
    ("DS09", "SRC-I", "Serum phosphoproteome (B. canis, 10 vs 10) with per-dog clinical values in the article supplement."),
    ("DS08", "SRC-J", "Serum extracellular-vesicle proteome (B. canis vs healthy); processed exports only partly downloaded."),
    ("S-CB042", "SRC-K", "B. vulpes clinical data from North American dogs; sparse clinicopathology, heavy co-infection."),
    ("S-CB516", "SRC-O", "15 client-owned B. canis dogs (Switzerland) with travel history, clinical signs and survival (8 died); no laboratory values in machine-readable form."),
    ("S-CB013", "SRC-L", "Per-dog PCV/platelets/qPCR in free-roaming Australian dogs (B. vogeli, A. platys); few positives."),
    ("S-CB106", "SRC-M", "Per-dog PCR clearance after imidocarb in 9 German dogs (treatment-focused)."),
    ("S-CB005", "SRC-N", "Free-ranging wolves: per-animal PCR and cause of death; epidemiological only."),
]


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


def esc(s):
    return (str(s) if s is not None else "not specified").replace("|", "\\|").replace("\n", " ")


def art_links(ids, fn):
    return ", ".join(f"[{i}](articles/{fn[i]})" for i in ids if i in fn) or "none (not linked to an included article)"


def main():
    ds = jl(ROOT / "datasets.jsonl")
    by = {d["dataset_id"]: d for d in ds}
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    fn = {v["id"]: v["filename"] for v in reg.values() if not v.get("retired")}
    for rank, (did, src, why) in enumerate(PRIORITY, 1):
        by[did].update({"priority_rank": rank, "independent_source": src, "rank_rationale": why})
    for d in ds:
        d.setdefault("priority_rank", None)
        d.setdefault("independent_source", None)
        d.setdefault("rank_rationale", None)
    with open(ROOT / "datasets.jsonl", "w", encoding="utf-8") as f:
        for d in ds:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    indiv = [by[p[0]] for p in PRIORITY]
    n_src = len({p[1] for p in PRIORITY})
    summ = [d for d in ds if d["status_code"] == 1 and d["dataset_id"] not in {p[0] for p in PRIORITY}]
    st2 = [d for d in ds if d["status_code"] == 2]
    st3 = [d for d in ds if d["status_code"] == 3]
    neg = jl(ROOT / "search" / "dataset_negative_checks.jsonl")
    L = ["# Canine babesiosis dataset catalogue\n", "[Back to article index](index.md) · [Research map](research-map.md) · [datasets.jsonl](datasets.jsonl) · [download manifest](data/manifest.jsonl)\n",
         "Verification date: 2026-10-23 (rounds 1–3) and 2026-10-28 (round 4, articles published 2006–2016). Files were downloaded only where public and ≤50 MB (total cap 250 MB); original bytes and SHA-256 checksums are in [data/manifest.jsonl](data/manifest.jsonl) and structure summaries in `data/inspection/`. No authors were contacted, no access controls were bypassed and no terms were accepted. Large raw omics files (PRIDE RAW, SRA FASTQ) were **not** downloaded; their retrieval route is given below.\n",
         "## Summary\n",
         f"- **{len(indiv)} verified-download dataset records with individual dog/sample-level data**, representing **{n_src} independent animal sources** (records sharing a source letter overlap in animals; see `independent_source`).",
         f"- {len(summ)} further verified downloads contain only summary statistics, protein lists or no data (listed separately; not patient-level).",
         f"- {len(st2)} public records verified without file retrieval (mostly parasite-side genomic/proteomic resources without host phenotypes).",
         f"- {len(st3)} articles state data are available on request (not pursued).",
         f"- Remaining included articles: {Counter(n['status_code'] for n in neg)[4]} with no dataset located after documented checks (status 4) and {Counter(n['status_code'] for n in neg)[5]} not assessable because full text was inaccessible (status 5).\n",
         "No dataset combines a large independent cohort, a hard outcome, rich multi-system phenotypes and omics. Every verified dataset is small relative to its feature count; most are suited to effect-size estimation, mixed models and hypothesis generation rather than predictive ML. Exploratory clusters from any of them must not be described as disease subtypes.\n",
         "## Ranked verified downloads (individual dog/sample-level)\n",
         "| Rank | Dataset | Source group | Species | Linked articles | Animals (samples) | Granularity | Outcome labels | Licence | Mech./Pheno./Doc./Feas. (1–5) |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for d in indiv:
        L.append(f"| {d['priority_rank']} | [{d['dataset_id']}](#{d['dataset_id'].lower()}) | {d['independent_source']} | {esc(d.get('species'))[:60]} | {art_links(d['linked_articles'], fn)} | "
                 f"{esc(d.get('n_animals'))} ({esc(d.get('n_samples'))}) | {', '.join(d['granularity'])} | {esc(d.get('outcomes'))[:90]} | {esc(d.get('licence'))[:40]} | "
                 f"{d.get('mechanistic_relevance')}/{d.get('phenotype_richness')}/{d.get('documentation')}/{d.get('feasibility')} |")
    L.append("\nRanking weighs mechanistic relevance first, then independent sample size, phenotype richness (outcomes, multi-system variables, time points), documentation, reuse terms and analytical feasibility.\n")
    L.append("## Dataset entries\n")
    for d in indiv:
        L.append(f'<a id="{d["dataset_id"].lower()}"></a>\n### {d["dataset_id"]} — {esc(d.get("title"))}\n')
        L.append(f"**Why ranked {d['priority_rank']}:** {d['rank_rationale']}\n")
        rows = [
            ("Status", d["status"]), ("Linked articles", art_links(d["linked_articles"], fn)),
            ("Correspondence check", d.get("correspondence_evidence")), ("Repository / accession", f"{esc(d.get('repository'))} / {esc(d.get('accession_or_doi'))}"),
            ("Landing page", d.get("landing_url")), ("Licence / reuse terms", d.get("licence")), ("Species", d.get("species")), ("Design", d.get("design")),
            ("Granularity", ", ".join(d["granularity"])), ("Raw vs processed", d.get("raw_vs_processed")),
            ("Independent animals", f"{d.get('n_animals')} — {d.get('n_animals_basis')}"), ("Samples", d.get("n_samples")),
            ("Groups and controls", d.get("groups_and_controls")), ("Time points", d.get("time_points")), ("Features", d.get("features")),
            ("Outcomes", d.get("outcomes")), ("Data dictionary", d.get("data_dictionary")), ("Missingness", d.get("missingness")),
            ("Technical requirements", d.get("technical_requirements")), ("Files", d.get("files_summary")), ("Overlaps", d.get("overlaps")),
        ]
        L.append("| Field | Value |\n|---|---|")
        for k, v in rows:
            L.append(f"| {k} | {esc(v)} |")
        files = d.get("downloaded_files") or []
        if files:
            L.append(f"\n**Downloaded files ({len(files)}; {sum(f['bytes'] for f in files) / 1e6:.2f} MB):** " +
                     "; ".join(f"`{f['file']}` ({f['bytes']:,} B, sha256 `{f['sha256'][:12]}…`)" for f in files[:8]) +
                     (f"; … {len(files) - 8} more in the manifest" if len(files) > 8 else ""))
        L.append(f"\n**Suitable questions:** {esc(d.get('suitable_questions'))}\n")
        L.append(f"**Recommended methods:** {esc(d.get('recommended_methods'))}\n")
        L.append(f"**Limitations (small n/high p, batch, confounding, leakage, splitting, validation, cross-species):** {esc(d.get('limitations'))}\n")
        if d.get("unverified_fields"):
            L.append(f"**Unverified fields:** {esc('; '.join(d['unverified_fields']))}\n")
        if d.get("note"):
            L.append(f"_{d['note']}_\n")
    L.append("## Verified downloads without individual-level data\n")
    L.append("These files were retrieved and inspected but hold means/SDs, correlation matrices, protein/feature lists or no data. They are not patient-level observations and were not ranked.\n")
    L.append("| Dataset | Linked articles | Granularity | Contents |\n|---|---|---|---|")
    for d in summ:
        L.append(f"| <a id=\"{d['dataset_id'].lower()}\"></a>{d['dataset_id']} | {art_links(d['linked_articles'], fn)} | {', '.join(d['granularity'])} | {esc(d.get('files_summary') or d.get('features'))[:220]} |")
    L.append("\n## Public records verified; file retrieval unverified\n")
    L.append("Relevant public records exist but files were not retrieved (size caps or no host phenotypes). Sequence/proteome resources without clinical phenotypes are not suitable for clinical ML.\n")
    L.append("| Dataset | Repository / accession | Linked articles | Granularity | Notes |\n|---|---|---|---|---|")
    for d in st2:
        L.append(f"| <a id=\"{d['dataset_id'].lower()}\"></a>{d['dataset_id']} | [{esc(d.get('repository'))} {esc(d.get('accession_or_doi'))}]({d.get('landing_url')}) | {art_links(d['linked_articles'], fn)} | {', '.join(d['granularity'])} | {esc(d.get('title'))[:90]}. {esc(d.get('files_summary'))[:150]} |")
    L.append("\nAlso public but not downloaded: raw RNA-seq reads for DS06 (SRA, via BioProject [PRJNA703846](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA703846)) and RAW mass-spectrometry files for DS07–DS09 (PRIDE FTP; 11–23 GB per project). Retrieve with the PRIDE/ENA FTP links on each landing page; checksums are provided by the repositories.\n")
    L.append("## Request-only candidates\n")
    L.append("Authors state data are available on request. Not contacted; contents, granularity and terms are unverified.\n")
    L.append("| Record | Article | Statement (abridged) |\n|---|---|---|")
    for d in st3:
        L.append(f"| <a id=\"{d['dataset_id'].lower()}\"></a>{d['dataset_id']} | {art_links(d['linked_articles'], fn)} | {esc(d.get('statement'))[:200]} |")
    L.append("\n## Remaining articles: negative and unassessed checks\n")
    L.append("Status 4 = full text, publisher page, supplement list or repository links were checked and no dataset was found (statements such as 'all data are in the article' count as no separate dataset). Status 5 = full text not accessible (paywall, bot protection or no online full text), so only the abstract was assessed. A few status-4 articles print per-dog values in article tables (small case series); these are noted in the article files but not catalogued as datasets.\n")
    L.append("| Article | Status | Basis (abridged) |\n|---|---|---|")
    for n in neg:
        L.append(f"| [{n['article_id']}](articles/{fn[n['article_id']]}) | {n['status_code']} | {esc(n['basis'])[:160]} |")
    (ROOT / "datasets.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("indiv", len(indiv), "sources", n_src, "summary", len(summ), "st2", len(st2), "st3", len(st3), "neg", len(neg))


if __name__ == "__main__":
    main()
