"""Compose search-log.md from the recorded queries, screening decisions and extraction records.

Later rounds (search/rounds.json) add their queries, a candidates-by-source narrative (search/<round>/),
a screening row and an extraction row; excluded and unresolved records are listed with their round.

Usage:
    python -I scripts/build_search_log.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import load_rounds  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "search"


def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()] if p.exists() else []


def esc(s):
    return str(s if s is not None else "").replace("|", "\\|").replace("\n", " ")


REPRO_R1 = ("python -I scripts/search.py --start {start} --end {end}        # PubMed + Europe PMC (+ OpenAlex relevance search, failed keyless)\n"
            "python -I scripts/citations.py --start {start} --end {end}     # backward/forward citation search (Europe PMC)\n"
            "python -I scripts/crossref_search.py --start {start} --end {end}\n"
            "python -I scripts/openalex_search.py --start {start} --end {end}\n")
REPRO_ROUND = ("python -I scripts/search.py --start {start} --end {end} --round {id}\n"
               "python -I scripts/citations.py --start {start} --end {end} --round {id} --registry-seeds\n"
               "python -I scripts/crossref_search.py --start {start} --end {end} --round {id}\n"
               "python -I scripts/openalex_search.py --start {start} --end {end} --round {id}\n"
               "python -I scripts/merge_candidates.py --round {id}                        # -> search/{id}/candidates_all.jsonl\n")


def round_queries(r):
    """Query rows of a later round (search/<round>/), with the round ID in front of the query ID."""
    d = ROOT / r["dir"]
    return [dict(x, id=f"{r['id']}:{x['id']}") for fn in ("queries.jsonl", "crossref_queries.jsonl", "openalex_queries.jsonl")
            for x in jl(d / fn)]


def round_narrative(r):
    """Candidate counts by source for a later round, from the files in search/<round>/."""
    d = ROOT / r["dir"]
    n = {f: len(jl(d / f"{f}.jsonl")) for f in ("candidates", "candidates_r2", "candidates_crossref", "candidates_openalex", "candidates_r3", "citation_hits", "candidates_all")}
    overlap = sum(len(jl(p)) for p in d.glob("*_prior_overlap.jsonl"))
    allc = jl(d / "candidates_all.jsonl")
    multi = sum(1 for x in allc if len(x.get("source_files") or []) > 1)
    existing = sum(1 for x in allc if x.get("existing_id"))
    dups = json.loads((d / "duplicates.json").read_text(encoding="utf-8")) if (d / "duplicates.json").exists() else {}
    flog = json.loads((d / "openalex_filter_log.json").read_text(encoding="utf-8")) if (d / "openalex_filter_log.json").exists() else {}
    dropped = flog.get("dropped", {})
    types = Counter()
    for k, v in dropped.items():
        types["dissertations" if k == "type:dissertation" else "conference papers/abstracts" if k.startswith("type:conference") else
              "Babesia and canine terms not in title" if k.startswith("not ") else "other types"] += v
    return (f"- **Round {r['id'][1:]} ({r['start']} to {r['end']}; searches run {r['run_date']}):** the same database, citation, Crossref and OpenAlex searches, restricted to the earlier window and run with `--round {r['id']}`. "
            f"PubMed + Europe PMC gave {n['candidates']} records; backward and forward citation searching from the registered articles gave {n['citation_hits']} linked records, of which {n['candidates_r2']} were kept (in window, Babesia term in title/abstract); "
            f"Crossref gave {n['candidates_crossref']}; OpenAlex gave {n['candidates_openalex']} not in earlier sets, restricted as in round 3 → {n['candidates_r3']} "
            f"(dropped: {', '.join(f'{k} {v}' for k, v in types.most_common())}). {overlap} records already screened in rounds 1-3 were left out (`*_prior_overlap.jsonl`). "
            f"Merged and deduplicated: {n['candidates_all']} unique candidates ({multi} found by two routes; {existing} already held an article ID, such as background papers inside the new window). "
            f"{len(dups)} further duplicates were merged at screening (`{r['dir']}/duplicates.json`). Earlier keys screened again: {', '.join(r.get('recheck') or []) or 'none'}.")


def main():
    rounds = load_rounds()
    first, later = rounds[0], rounds[1:]
    w_start, w_end = min(r["start"] for r in rounds), max(r["end"] for r in rounds)
    q = jl(S / "queries.jsonl")
    rq = jl(S / "repo_queries.jsonl")
    cq = jl(S / "crossref_queries.jsonl")
    oq = jl(S / "openalex_queries.jsonl")
    scr = {n: jl(S / f"screening_{n}.jsonl") for n in ("r1", "r2", "r3")}
    scr.update({r["id"]: jl(ROOT / r["dir"] / "screening.jsonl") for r in load_rounds()[1:]})
    ex = jl(S / "extraction_records.jsonl")
    reg = json.loads((ROOT / "ids.json").read_text(encoding="utf-8"))
    key_by_id = {v["id"]: k for k, v in reg.items()}
    dups = json.loads((S / "duplicates.json").read_text(encoding="utf-8"))
    cands = len(jl(S / "candidates.jsonl"))
    r2 = len(jl(S / "candidates_round2_all.jsonl"))
    r3 = len(jl(S / "candidates_r3.jsonl"))
    cit = jl(S / "citation_hits.jsonl")
    dup_ids = {v["id"] for v in reg.values() if v.get("retired") and str(v.get("retired_reason", "")).startswith("duplicate:")}
    cb = [r for r in ex if r["id"].startswith("CB")]
    inc = [r for r in cb if r["final_decision"] == "include" and r["id"] not in dup_ids]
    # A record belongs to the first round that screened its key (a later round may screen an earlier key again).
    seen_keys = {x["key"] for n in ("r1", "r2", "r3") for x in scr[n]}
    later_ids = {}
    for r in later:
        keys = {x["key"] for x in scr[r["id"]]} - seen_keys
        later_ids[r["id"]] = {v["id"] for k, v in reg.items() if k in keys}
        seen_keys |= keys

    def round_of(rec):
        return next((rid for rid, ids in later_ids.items() if rec["id"] in ids), first["id"])
    cohorts = json.loads((ROOT / "cohorts.json").read_text(encoding="utf-8"))
    L = ["# Search log and methods\n", "[Back to article index](index.md)\n",
         "## Review window and run\n",
         f"- **Window:** {w_start} to {w_end} inclusive, searched in rounds: "
         + "; ".join(f"{r['id']} {r['start']} to {r['end']} (searches run {r['run_date']}; {r['status']})" for r in rounds)
         + ". Applied to the **first publication date** = the earlier of the electronic (online) and issue dates in the PubMed record; Europe PMC `FIRST_PDATE`; Crossref earliest of published-online/print/issued; OpenAlex `publication_date`. Online-vs-issue discrepancies are recorded per article (`date_note` in [articles.jsonl](articles.jsonl)).",
         "- **Scripts:** all in `scripts/` (Python 3.13 standard library only; run with `python -I` from `canine-babesiosis-review/`). Raw query outputs are kept in `search/` (rounds 1-3) and `search/<round>/` (later rounds); the rounds are listed in `search/rounds.json`.",
         "- **Status: rapid scoping review, not an exhaustive systematic review.** Single-pass, LLM-assisted screening and extraction with a second-screener check (see below); no duplicate independent human screening; no formal risk-of-bias assessment.\n",
         "## Reproduction\n",
         "```bash\n" + REPRO_R1.format(**first) + "".join(REPRO_ROUND.format(**r) for r in later) + "python -I scripts/repo_search.py                                       # dataset repositories\npython -I scripts/fulltext_checks.py search/included_keys_r1.txt        # Europe PMC OA full text: data statements, supplements\npython -I scripts/assign_ids.py                                        # stable IDs (ids.json) + extraction packets\npython -I scripts/fetch_datasets.py data/fetch_spec_repos.json         # downloads with caps + SHA-256 manifest\npython -I scripts/fetch_datasets.py data/fetch_spec_supp.json\npython -I scripts/inspect_files.py DS01 ...                            # structure summaries -> data/inspection/\npython -I scripts/table_dump.py \"<file>[::zip member]\" --sheet N        # read-only table viewer\npython -I scripts/build_datasets.py && python -I scripts/render_datasets.py\npython -I scripts/build_outputs.py && python -I scripts/build_search_log.py\npython -I scripts/validate.py\n```",
         "Re-running the round 1-3 searches overwrites `search/*.jsonl` and will return newer records. A later round (`--round`) writes to its own `search/<round>/` folder and leaves out records already collected or screened in earlier rounds; records that already have an article ID (for example background papers inside the new window) are kept and flagged with `existing_id`. `ids.json` is append-only, so existing IDs never change (excluded records keep their retired IDs).\n",
         "## Databases and queries\n",
         "| Query ID | Source | Exact query | Filters | Run date | Hits | Note |", "|---|---|---|---|---|---|---|"]
    for x in q + cq + oq + [x for r in later for x in round_queries(r)]:
        note = x.get("error") or (f"first {x.get('screened_rows')} relevance-ranked rows screened" if x.get("screened_rows") else "") or (f"{x.get('new_vs_prior')} not in earlier sets" if x.get("new_vs_prior") is not None else "")
        L.append(f"| {x['id']} | {x['source']} | `{esc(x['query'])}` | {esc(x.get('filters'))} | {x['run_date']} | {x.get('count')} | {esc(note)} |")
    L += ["",
          f"- **Deduplication:** by DOI (lower-cased), then PMID, then normalised title (lower-case alphanumerics). PubMed records were preferred; Europe PMC/OpenAlex records carrying a PMID were refetched from PubMed. Near-duplicate titles among eligible records were checked with a similarity ratio >0.8; {len(dups)} duplicates were merged (`search/duplicates.json`).",
          f"- **Round 1 (databases):** {cands} unique in-window records from PubMed + Europe PMC (plus 164 outside the window by first publication date).",
          f"- **Round 2 (citation searching + Crossref):** backward (reference lists) and forward (citing articles) via the Europe PMC references/citations API from the seed review and all 121 round-1 inclusions; {len(cit)} linked records not previously seen; kept if in window and mentioning Babesia/babesiosis/piroplasm in title/abstract → 181. Crossref bibliographic search (8 queries, first 1000 relevance-ranked rows each, title must contain a Babesia term and a canine term) → 88. Total round 2: {r2}.",
          f"- **Round 3 (OpenAlex):** `title_and_abstract.search` filter (2015 records); 1042 not in earlier sets; restricted to type article/review with Babesia + canine terms in title (or canine in title + Babesia in abstract) → {r3}. Excluded by type: dissertations 153, conference papers/abstracts 58, preprints 21, book chapters/books 25, datasets 15 (screened separately for data), other 31 (`search/openalex_filter_log.json`).",
          *[round_narrative(r) for r in later],
          "- **Unavailable sources:** CAB Abstracts (subscription; not accessible), Web of Science and Scopus (subscription), Google Scholar (no API; not used), Harvard Dataverse API (HTTP 403), OpenAlex relevance search with cursor paging (now requires an API key; no account was created) — replaced by keyless page-based `title_and_abstract.search`. Mendeley Data search was not available; one Mendeley dataset was reached through its article.\n",
          "## Screening\n",
          "Title/abstract screening used LLM agents (Claude Sonnet) in 40-record batches against written criteria (see [index](index.md) scope). Every exclusion was re-checked by a second, deliberately liberal screener (Claude Haiku) instructed to rescue any record with host pathophysiological data; rescued and uncertain records were adjudicated by a senior agent (Claude Opus) that could fetch missing abstracts from DOI landing pages. Eligibility was re-checked at extraction against full text where accessible.\n",
          "| Round | Records | Include | Uncertain | Exclude | Exclusion reasons |", "|---|---|---|---|---|---|"]
    for n, d in scr.items():
        c = Counter(x["decision"] for x in d)
        rs = Counter(x["exclude_reason"] for x in d if x["decision"] == "exclude")
        L.append(f"| {n} | {len(d)} | {c['include']} | {c['uncertain']} | {c['exclude']} | {', '.join(f'{k} {v}' for k, v in rs.most_common())} |")
    L += ["", "| Round | Passed to extraction | Included | Merged as duplicates at extraction | Excluded on full text/record | Unresolved | Included by type |", "|---|---|---|---|---|---|---|"]
    for rid in [first["id"]] + [r["id"] for r in later]:
        rr = [r for r in cb if round_of(r) == rid]
        fe = Counter(r["final_decision"] for r in rr)
        nd = sum(1 for r in rr if r["id"] in dup_ids)
        ty = Counter(r.get("include_type") for r in rr if r["final_decision"] == "include" and r["id"] not in dup_ids)
        L.append(f"| {rid} | {len(rr)} | {fe['include'] - nd} | {nd} | {fe['exclude_fulltext']} | {fe['unverifiable']} | {', '.join(f'{k} {v}' for k, v in ty.most_common())} |")
    fe = Counter(r["final_decision"] for r in cb)
    L += ["",
          f"Records passed to extraction (include + uncertain, minus duplicates): {len(cb)}. At extraction: **{len(inc)} included**, {sum(1 for r in cb if r['id'] in dup_ids)} merged as duplicates of another included record (ID retired), {fe['exclude_fulltext']} excluded on full-text/record review, {fe['unverifiable']} unresolved (record could not be verified, or no abstract/full text accessible). Round 4 was screened and extracted with the same criteria (`search/r4/screening_criteria.md`, `search/r4/EXTRACTION_GUIDE.md`); its extraction notes were checked by a second agent (Claude Haiku) and a field and file check in code (`search/r4/extraction_checks.json`).\n",
          "### Eligibility decisions worth noting\n",
          "- Clinicopathological profiles of infected dogs (haematology/biochemistry case series) were **included** as descriptive evidence, because they characterise syndromes; they are labelled `descriptive`.",
          "- Prevalence/molecular surveys, vector studies, diagnostic-assay development and treatment-efficacy trials were excluded unless they reported host pathophysiological data.",
          "- Wild *Canis lupus* (grey/Iberian wolf) studies were kept as canine evidence; red fox and other non-*Canis* canid studies were excluded unless dog data were present (CB150, red fox, excluded).",
          "- Case reports were included only when they described a distinct syndrome or mechanistic observation (e.g. Evans syndrome, vasculitis, haemophagocytic syndrome, ARDS, cerebral involvement).",
          "- Many round-3 inclusions are from regional journals not indexed in MEDLINE; some show signs of limited peer review. They were retained (not excluded on venue) but flagged in notes; most are small descriptive series.",
          "- Seed review (BG001) kept as background; it is a prevalence meta-analysis and is not counted as eligible canine evidence.\n",
          "### Excluded at full-text/record review\n", "| ID (retired) | Round | Reason |", "|---|---|---|"]
    for r in ex:
        if r["final_decision"] == "exclude_fulltext":
            L.append(f"| {r['id']} | {round_of(r)} | {esc(r['decision_reason'])[:300]} |")
    L += ["", "### Unresolved records (not counted)\n", "| ID (retired) | Round | Title | Issue |", "|---|---|---|---|"]
    for r in ex:
        if r["final_decision"] == "unverifiable":
            L.append(f"| {r['id']} | {round_of(r)} | {esc(r['title'])[:90]} | {esc(r['decision_reason'])[:260]} |")
    L += ["", "## Verification\n",
          "- Records with a PMID were taken from the PubMed XML record (title, authors, journal, dates, DOI, PMCID, publication types, CommentsCorrections for errata/retractions). Records without a PMID were verified against Crossref, the DOI landing page or the publisher page by extraction agents; when no authoritative record could be confirmed the record was marked unresolved.",
          "- Summaries were written from the actual abstract (PubMed, publisher page or Crossref); OpenAlex abstracts are reconstructions of inverted indexes and were confirmed against the publisher page where reachable. A second agent (Claude Haiku) cross-checked every canine note against its source abstract (numbers, design, identifiers, ≤8-word verbatim runs, causal language) and edited where needed.",
          f"- Corrections/retractions: PubMed CommentsCorrections were checked for all PubMed records; {sum(1 for r in inc if r.get('corrections') and 'none' not in r['corrections'].lower() and 'not checked' not in r['corrections'].lower())} included records carry a correction note (see `corrections` in articles.jsonl). Non-PubMed records: checked in Crossref `update-to`/`relation` where accessible, otherwise 'not checked'.",
          "- Human comparator papers were selected by category agents and then independently re-verified from the PubMed XML by a second agent before notes were written.\n",
          "## Dataset searches\n", "| Query ID | Repository | Query | Run date | Hits | Returned | Error |", "|---|---|---|---|---|---|---|"]
    for x in rq:
        L.append(f"| {x['id']} | {x['repository']} | `{esc(x['query'])}` | {x['run_date']} | {x.get('count')} | {x.get('returned')} | {esc(x.get('error'))} |")
    L += ["",
          "- Article-linked checks: Europe PMC open-access full-text XML parsed for data-availability statements, supplementary-material/media elements and repository links (`search/fulltext_checks.jsonl`); extraction agents checked publisher pages for the rest. Supplement packages were retrieved from the Europe PMC `supplementaryFiles` endpoint.",
          "- Repository hits were matched to articles by title, accession cross-references in the article, and data content (n, groups, variables) during dataset assessment.",
          "- Download limits: ≤50 MB per file, ≤250 MB total; all downloads in [data/manifest.jsonl](data/manifest.jsonl) with SHA-256.\n",
          "## Coverage limitations\n",
          "- **Not exhaustive.** CAB Abstracts, Web of Science, Scopus and Google Scholar were not searched; regional veterinary literature (India, Ukraine, Russia, Türkiye, Brazil, Eastern Europe) is reached only through Crossref (relevance-capped) and OpenAlex, so further non-indexed papers almost certainly exist.",
          "- **Language:** no language restriction was applied to searching, but screening used English titles/abstracts; non-English records with English abstracts were included (Portuguese, Ukrainian, Russian, German, Romanian, Turkish, French, Serbian). Records whose abstract or full text was only in a language/platform we could not access (e.g. eLIBRARY.ru, CroRIS bot checks) are listed as unresolved. Effect: likely under-representation of Russian- and Chinese-language clinicopathology.",
          f"- **Access:** full text was checked programmatically for PMC open-access articles and via publisher pages for others ({sum(1 for r in inc if r.get('fulltext_checked'))} of {len(inc)} included canine articles); {sum(1 for n in jl(S / 'dataset_negative_checks.jsonl') if n['status_code'] == 5)} could not be read beyond the abstract (dataset status 5).",
          "- **Theses/dissertations** (153 in the round-3 OpenAlex set and 124 in round 4, including University of Pretoria and Indian veterinary theses) and conference abstracts were excluded as not peer-reviewed, although some underlie included papers and datasets (e.g. DS03–DS05 cite UP dissertations).",
          "- **LLM-assisted screening/extraction:** decisions were made by language-model agents following written criteria with a second-screener rescue pass, not by duplicate human reviewers. Misclassification is possible, especially for borderline descriptive papers and for poorly reported regional articles.",
          f"- **Cohort linkage** is inferred from reported institutions, periods and n; {sum(1 for c in cohorts.values() if c['certainty'] == 'confirmed')} of {len(cohorts)} cohort groupings are explicitly confirmed by the authors, the rest are probable (see [research map](research-map.md#cohorts)). Further unrecognised overlap is likely, especially among Onderstepoort, Zagreb and Ukrainian groups.",
          f"- **Search end-date effects:** records first published close to {w_end} may not yet be indexed.\n"]
    (ROOT / "search-log.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("search-log written", len(L))


if __name__ == "__main__":
    main()
