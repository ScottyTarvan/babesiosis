# Brief for SV-06a family sub-agents

You fill one row per mechanism of ONE family of the SV-06a human-to-dog mechanism transfer grid (canine babesiosis severity research). Work only from facts you can cite. A null finding is a finding.

## Read first

1. `C:\Workspaces\Babesiosis\experiments\SV-06\a\spec.md` (the fixed field list and grading rules: follow them exactly).
2. Your family's seed rows in `C:\Workspaces\Babesiosis\experiments\SV-06\a\scripts\mechanisms.json`.
3. Your rows in `C:\Workspaces\Babesiosis\experiments\SV-06\a\out\local_hits.json` (keyword hits in CB notes and CB texts: leads only) and `out\reference_lookup.json` (DS07 proteins and DS06 genes: already computed, do not recompute).

## Sources

- **Human comparators**: notes `C:\Workspaces\Babesiosis\core\articles\HU0*.md` (27 notes; grep them for your mechanism). DOIs: grep `"id": "HU0` lines in `core\articles.jsonl` (never read that file whole; grep only).
- **Canine, local**: CB appraisal notes `core\articles\CB*.md` and CB texts `core\data\markdown\CB*.md` (check `source_format` in the front matter: many are abstract only). Open the hit files and decide for each whether it really measured the mechanism **in dogs with babesiosis**, and whether it compared it **by severity or outcome** (not only infected vs healthy controls). Cohort IDs: `core\cohorts.json` (grep the article ID) — two articles in one cohort are one unit.
- **Also useful**: `C:\Workspaces\Babesiosis\experiments\SV-G2\associations_v2.csv` (740 extracted severity rows from 49 CB articles; grep the marker name) and `experiments\SV-03\report.md` section 4.
- **PubMed**: use the tool `mcp__ea651c22-24db-4a98-a1aa-116b145fa790__search_articles` (load it with ToolSearch `select:mcp__ea651c22-24db-4a98-a1aa-116b145fa790__search_articles,mcp__ea651c22-24db-4a98-a1aa-116b145fa790__get_article_metadata` if needed). If it is unavailable, use WebFetch on `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=...&retmode=json`. For each mechanism run at least: (a) a human severity search (malaria, babesiosis or sepsis + severity/mortality), (b) a canine babesiosis search (`(dog OR canine) AND babesi* AND <marker>`), (c) a canine assay search (`(dog OR canine) AND <marker> AND (validation OR assay OR ELISA)`). Record the query strings. Put no personal or project details in queries.

## Rules

- Cite every claim with a DOI link `https://doi.org/...`. No article text beyond a few words; paraphrase.
- Do not write anywhere except your one output file `C:\Workspaces\Babesiosis\experiments\SV-06\a\families\F<n>.json`. Do not edit other files. Do not commit.
- You may add at most 3 mechanisms of your own (`added_by_agent: "yes"`, ids `F<n>-1x`, with `keywords` (regex list like the seeds) and `dog_genes` and `ds07_desc` (protein-name prefixes as in DS07 descriptions) so the assembly script can search for them).
- Use the grading rules of the spec for `human_grade`, `canine_status`, `canine_assay`, `testable_now`, `gap`. For `testable_now`, use `reference_lookup.json` (DS07 rows with status `master` count; `master_candidate` counts only with a note) and DS02 variables: DS02 (5 experimental Beagles, B. rossi) measured (from `experiments/shared/tidy/DS02.features.json`) cell-free haemoglobin (`cfhb`), CRP, albumin, lactate, glucose, blood pressure, 13 cytokines (GM-CSF, IFN-gamma, KC, IP-10, IL-2, IL-6, IL-7, IL-8, IL-10, IL-15, IL-18, MCP-1, TNF-alpha), haematology with reticulocytes, parasitaemia and clinical scores; nothing else. DS06 is whole-blood RNA-seq of the same Beagles (gene expression, not circulating protein: say so).
- Keep the work bounded: about 3 to 6 PubMed queries per mechanism.

## Output: `F<n>.json`

```json
{
  "family": "F1 Haemolysis and haem scavenging",
  "agent_summary": "2-4 sentences: what is a gap, what is not, surprises.",
  "mechanisms": [
    {
      "mechanism_id": "F1-01", "family": "...", "mechanism": "...", "added_by_agent": "no",
      "human_conditions": ["malaria", "sepsis"],
      "hu_articles": ["HU002", "HU010"],
      "human_key_dois": ["https://doi.org/..."],
      "human_n_studies": 4,
      "human_grade": 3,
      "human_direction": "higher in severe / fatal",
      "cb_confirmed": [{"id": "CB117", "what": "measured haemopexin, 3 vs 3 dogs, infected vs controls", "severity_contrast": false, "cohort": "CH.. or null"}],
      "cb_rejected": ["CB0xx: keyword only, not measured"],
      "canine_pubmed": {"queries": ["..."], "dog_babesiosis_dois": ["https://doi.org/..."]},
      "canine_status": "none | measured_no_severity | severity_tested",
      "canine_severity_units": 0,
      "canine_assay": "validated | used_in_dogs | none",
      "assay_evidence": ["https://doi.org/..."],
      "dog_genes": ["HBB"],
      "testable_now": "public_file | stored_samples_only | no",
      "testable_detail": "DS07 master P60524 (HBB, 45% coverage); DS02 cell-free Hb",
      "gap": "yes | no",
      "notes": "short",
      "keywords": [], "ds07_desc": []
    }
  ]
}
```

`keywords` and `ds07_desc` are needed only for added mechanisms. Write valid JSON (UTF-8). End your reply with one line: the file path and the number of rows.
