# EXP13 CORPUS graph: marker knowledge graph and link prediction

| Field | Value |
|---|---|
| Experiment code | `EXP13-CORPUS-graph` |
| Layer | 3 corpus |
| Method token | `graph` (goes in `experiment.method`) |
| Dataset(s) | `null`: the input is the corpus-wide severity extraction (`data/severity/associations.csv` after stage 1), not a tidy per-dog dataset. `associations[]` and `cluster_assignments[]` are written as empty lists. |
| Readiness | extraction needed (stage 1). Stage 2 can be smoke-tested on the current 10-article pilot table, but its results are only meaningful after stage 1. |
| Python environment | Stage 1 helper `scripts/severity_batch.py`: standard library only, run with `.venv`. Stage 2 `scripts/experiment_graph.py`: `.venv` (numpy 2.5.4, networkx 3.7 installed). `.venv-nlp` has no networkx and cannot run stage 2. No scipy needed (the ranking AUC is computed from ranks with numpy). No node2vec, gensim or torch is installed in either environment, so the embedding method is skipped (section 3, stage 2 step 6). Do not install anything. Add `networkx>=3.2` to `scripts/requirements-experiments.txt` with the comment `EXP13 stage 2, .venv`. |
| Estimated build effort | large: stage 1 is about 194 full-text and 200 abstract-only extractions by agents plus two human checkpoints (several days of wall time); stage 2 is medium (about 3 hours of agent work) |
| Suggested model for the building agent | opus: it orchestrates the extraction agents, judges their fix-ups and implements the graph scoring; the extraction agents themselves are specified in section 3, stage 1 step 4 |
| Depends on | `data/severity/` pilot files (schema, guide, map, 10 extractions), `scripts/check_associations.py`, `articles.jsonl`, `cohorts.json`, `data/markdown/` (git-ignored, this machine only). EXP08 shares the filter, species and study-unit rules (copy them, do not import). After stage 1, re-run EXP08 unchanged. |

## 1. Question and hypotheses

Questions:

1. Across all canine articles, which markers, outcome classes, species and specimens are connected by tested severity associations, and which markers are hubs (tested against many outcomes in many populations)?
2. Which marker-to-outcome pairs have never been tested but are made plausible by the structure of the evidence (similar markers tested against that outcome, the marker measured in populations that had that outcome)?
3. Does the ranking work: built from articles up to a cut-off year, does it rank higher the pairs that were first tested after that year?

Hypotheses:

- H1: haematology and acid-base markers (`Haematocrit/PCV`, `Lactate`, `Body temperature`) are hubs: tested against mortality and complicated disease in the most populations (motivated by the pilot, where `Haematocrit/PCV` x `mortality` has the most units, and by CB040, n = 320).
- H2: *B. rossi* and *B. canis* share few tested markers outside haematology (the pilot's oxidative-stress and cytokine rows come from single-species articles).
- H3: link prediction beats chance: temporal-validation ranking AUC above the 95th percentile of 1000 random rankings and above the degree-product (preferential attachment) baseline.

Negative findings that count: hubs that are hubs only because one large article tested many outcomes (checked by the cohort-weighted degree); temporal validation no better than random or than degree product; fewer than 5 pairs first tested after the cut-off (validation not evaluable). All are reported.

## 2. Data

### 2.1 Sources

- **Article scope** (`articles.jsonl`, 481 records; re-count at run time): `scope_label` `core canine evidence` 404, `canine review` 40, `human comparator` 27, `background` 10. Stage 1 extracts `core canine evidence` only. Reviews are excluded because their findings are cited from other articles (the guide forbids extracting cited findings); `HU` and `BG` are never canine evidence. Fields used: `id`, `scope_label`, `species_short`, `cohort_id` (101 of 444 `CB` articles have one), `first_pub_date` (no blanks among core articles; year range 2006 to 2026), `primary_category`.
- **Text availability** (`data/markdown_report.jsonl`, 540 rows including retired IDs; join to `articles.jsonl` on `id` and take scope from there): core canine articles by `source_format`: `pdf` 134, `jats_xml` 70 (204 full text), `abstract` 200. Full-text Markdown `quality`: `ok` 168, `review` 36. 33 articles have an English translation `data/markdown/<ID>.en.md`, which is then the `text_used`. Full-text word counts: median 2954, maximum 9122, total about 699,000 words. Section headings come from the front matter `sections` list (for example `["abstract", "introduction", "methods", "results", "discussion", "abbreviations"]`) and the Markdown `##` headings.
- **Pilot extraction** (`data/severity/`): `extractions/<ID>.json` for CB006, CB017, CB040, CB050, CB053, CB141, CB145, CB202, CB238, CB263 (top-level keys `id`, `text_used`, `extracted_by` e.g. `claude-opus-5-5 (extract-4)`, `extracted_utc`, `article_notes`, `skipped_infected_vs_healthy`, `severity_definitions`, `associations`). Flattened to `associations.csv`: 275 rows, quote_check `exact` 275, numbers_missing blank in all rows, 82 markers, 21 severity definitions (see EXP08 section 2.1 for every column and distinct value). Remaining full-text core articles to extract: 204 - 10 = 194.
- **Shortlist** `data/severity/shortlist.csv`: 196 rows, columns `id, tier, rank_score, tested_sentences, outcome_sentences, source_format, aim, nlp_primary, species, n_infected, design, cohort, marker_hints, title`; `tier` A 31, B 120, C 45; `source_format` pdf 72, jats_xml 45, abstract 79. It covers 116 of the 204 full-text core articles and 76 of the 200 abstract-only ones (4 shortlist rows are not core canine evidence). It sets the extraction order, not the scope.
- **Hints** `data/severity/candidate_sentences.jsonl`: `id`, `section`, `tested`, `sentence`, `marker_hints[]` (grep by ID; never load other large files whole).
- **Schema and rules**: `data/severity/association_schema.json` (required top-level `id, text_used, extracted_by, severity_definitions, associations`; enums listed in EXP08 section 2.1), `data/severity/EXTRACTION_GUIDE.md`, `data/severity/marker_map.csv` (399 rows; `alias, marker, marker_class, pattern, cui, source, note, articles`; `source` `seed` 159 canonical markers, `scispacy` 240 aliases of which 162 have a blank `marker`).
- **Checker** `scripts/check_associations.py` (stdlib): with `--ids` it prints schema errors, quote checks (`exact`, `near` >= 80% of 4-word shingles, `partial` >= 50%, `not_found`) and numbers not found in the text, and writes nothing; without `--ids` it rewrites `associations.csv` and `extraction_report.md` and appends unmapped markers to `marker_map.csv` as alias rows with `source` `extracted` and blank `marker`. It globs `data/severity/extractions/*.json`, so no other `.json` file may be put in that folder.
- **Cohorts** `cohorts.json`: 38 cohorts (`probable` 35, `confirmed` 3), each `label, certainty, basis, members`.
- **SQL (optional)**: `dbo.article_section` holds the same text as `data/markdown/` in passages of about 500 words with `section_kind` (`abstract`, `methods`, `results`, `results_discussion`, `discussion`, `case`, ...) and `section_order`; `dbo.article` has `has_full_text`, `text_source`, `text_quality`. `EXEC dbo.search_passages @question, @article_codes, @section_kinds` can find result passages in long papers. Default: build prompts from the Markdown files, because quotes are verified against `text_used`, which is a Markdown path. Use SQL only to locate passages when a paper exceeds the prompt budget.
- **Not used**: `data/syndromes/` (the concept CSVs named in `CLAUDE.md`, `concept_summary.csv`, `article_concepts.csv`) is absent on this machine; the graph does not need it. `marker_map.csv` has a `cui` column that can later link markers to UMLS concepts.
- Licence: full texts are copyrighted and git-ignored; prompt packets that contain them are written outside the repository (stage 1 step 3). Extractions hold short verbatim quotes, as in the pilot.

### 2.2 Tidy file required

Not applicable (no per-dog data). The equivalent preparatory step is the stage 1 extraction, specified in section 3.

### 2.3 Variables and filters

Stage 2 uses the same row filters as EXP08 (copy the code): `CB` IDs with `scope_label = core canine evidence`; `quote_check` in `exact, near`; blank `errors`; canonical marker via `marker_map.csv`; `confidence` in `high, medium` (`low` rows are excluded from edges and counted in `run_notes`); species groups `B. rossi`, `B. canis`, `B. gibsoni / B. vogeli`, `unspecified` by the EXP08 rules; study unit = `cohort` when non-blank, else `id`; outcome node = `outcome_class`, or `specific_complication: <complication>`. Abstract-only rows (`source_type = abstract`) are kept with edge weight multiplied by `--abstract-weight` (default 0.5). Rows with `analysis = descriptive_only` or `significant` in `not_tested, unclear` give a `measured` edge but not a `tested` edge (section 3, stage 2 step 1).

## 3. Method

### Stage 1: extraction to all canine articles

1. **Plan the work.** `scripts/severity_batch.py plan` reads `articles.jsonl`, `data/markdown_report.jsonl`, `shortlist.csv` and the existing extraction files, and writes `data/severity/extractions/index.csv` (CSV, not JSON, because the checker globs `*.json`). One row per in-scope article (404), columns:
   `id, batch, track, text_used, source_format, md_quality, shortlist_tier, cohort_id, status, extracted_by, extracted_utc, n_definitions, n_associations, quote_exact, quote_near, quote_fail, numbers_missing, parse_errors, unmapped, attempts, reviewer, note`.
   - `track` = `fulltext` (source_format `pdf` or `jats_xml`) or `abstract`.
   - `status` starts as `done` for the 10 pilot articles (`extracted_by` copied from their files) and `pending` for the rest; later values `extracted`, `validated`, `no_severity_content`, `failed`, `needs_review`.
   - Order and batches: full-text track first, ordered by shortlist tier (A, B, C, then not shortlisted), then `rank_score` descending, then `id`; then the abstract track in the same order. Batch size `--batch-size` default 10 articles; batches numbered `F01...` (full text, 20 batches for 194 articles) and `A01...` (abstract, 20 batches).
   - `text_used` = `data/markdown/<ID>.en.md` when it exists, else `data/markdown/<ID>.md`.
2. **Agent per article.** One extraction agent per article (articles are long and tables need the whole context); at most `--concurrency` 5 agents at once; a batch is finished when all of its articles are `extracted` or `failed`.
3. **Prompt packets.** `scripts/severity_batch.py packet --batch F01 --out <dir outside the repo, e.g. %TEMP%/exp13_packets>` writes one packet per article. A packet contains, in this order:
   - the full `EXTRACTION_GUIDE.md`;
   - the full `association_schema.json`;
   - the canonical marker list: every `marker_map.csv` row with `source = seed`, or `source = manual` with a `pattern`, as `marker | marker_class` lines (159 now);
   - the article context: `id`, `title`, `species_short`, `cohort_id` and the other members of that cohort with their titles (from `cohorts.json`), and `md_quality` (`review` means the PDF conversion was flagged);
   - the hint sentences for the ID from `candidate_sentences.jsonl`;
   - the article text from `text_used`: the YAML front matter, then the sections Abstract, Methods (all subsections, which hold the study population, the outcome definition and the statistical analysis), Results, any combined Results and Discussion, Case/Case presentation, every table, and figure captions. Introduction, Discussion (when separate), References, Abbreviations and Acknowledgements are left out to save context; they hold cited findings that must not be extracted. Section selection uses the `##` headings, matched case-insensitively to `abstract|method|material|result|case|table|figure`; if fewer than 2 sections match (unusual layouts), include the whole file.
   - the output path `data/severity/extractions/<ID>.json`, the required `extracted_by` value, and the instruction to write only that file.
   - Abstract-track packets contain the same guide, schema and marker list, and the whole abstract file.
4. **Extraction model.** Full-text track: **claude-opus-5-5** (the model of the pilot, `extracted_by` `claude-opus-5-5 (EXP13 F##)`). Reason: the pilot with this model gave 275 of 275 exact quotes and no number misses on PDF-converted tables; the task needs verbatim copying from garbled tables, about 25 enum fields, and judgement on what counts as a severity comparison versus an infected-vs-healthy comparison; and 36 full texts have conversion `quality = review`. Abstract track: a current Sonnet model (`extracted_by` `<sonnet model id> (EXP13 A##, abstract-only)`): abstracts are short and the rows few, so the cheaper model is adequate, and the checker catches quote errors. Re-extract with Opus any abstract article whose validation fails twice.
   - Agent prompt (fixed text, prepended to the packet): "You extract marker-severity associations from one canine babesiosis article. Follow the guide exactly. Write only data/severity/extractions/<ID>.json. Quotes must be copied character for character from the article text below; never paraphrase. Copy numbers as printed. If the article has no comparison of any marker between severity or outcome groups, write the file with empty severity_definitions and associations and say so in article_notes. When done, run `.venv/Scripts/python.exe -I scripts/check_associations.py --ids <ID>` and fix every problem it reports, or explain it in the row's note. Report the checker's last output."
5. **Validation per article** (`scripts/severity_batch.py validate --batch F01`, which loads `check_associations.py` with `importlib.util.spec_from_file_location` and calls its `check_article` for the batch IDs, writing nothing in `data/severity/` except `index.csv`):
   - schema: no schema errors (enums, required fields, every `severity_key` defined);
   - quotes: every association and severity-definition quote must be `exact` or `near` in `text_used`; rows with `partial` or `not_found` are sent back to the agent once with the failing quotes listed; still failing after the second attempt, the row is deleted and recorded in the article's `article_notes`;
   - numbers occur in the text: `numbers_missing` must be empty or each missing number explained in the row's `note` (figure reading, derived percentage);
   - numbers parse (new check, in `severity_batch.py`): `n_total`, `n_severe`, `n_comparison` are integers or null and `n_severe + n_comparison <= n_total` when all three are given; `effect_value` parses as one number after the EXP08 normalisation (Unicode minus, thousands commas, decimal commas); `effect_ci` parses as two numbers with low <= high, or contains `infinity`; `p_value` matches `^(<|>|<=|=)?\s*\d*\.?\d+$`, `NS` or is null; `sensitivity` and `specificity` parse as a number (with or without `%`) or are null. Failures go back to the agent with the list;
   - markers map: every `marker` must be canonical or resolve through an alias. An unmapped marker is either corrected to a canonical name by the agent, or added by the building agent as a new canonical row in `marker_map.csv` (`alias` = lowercased name, `marker`, `marker_class`, `pattern` = a regex that matches it, `source` = `manual`, `note` = `EXP13 batch <F##>`). `unmapped` must be 0 before the batch closes;
   - consistency: `direction` agrees with `significant` (`no_difference` only with `significant` `no` or `not_tested`); abstract-track rows all have `source_type = abstract` and `confidence` `medium` or `low` (validator downgrades `high` to `medium` and logs it).
   Then `status` = `validated` (or `no_severity_content` when both arrays are empty, or `failed` after 2 attempts with the reason in `note`).
6. **Close the batch.** When every article in the batch is `validated`, `no_severity_content` or `failed`, run the full checker once, serially, never while agents are writing: `.venv/Scripts/python.exe -I scripts/check_associations.py`. It regenerates `associations.csv` and `extraction_report.md` and appends any remaining unmapped aliases (there should be none).
7. **Abstract-only rows.** For the 200 abstract-only core articles, extract only rows where the abstract names the marker, the severity or outcome groups, and the direction or the significance; a non-significant row only when the abstract says so explicitly (`did not differ`, `no association`). `source_type = abstract`, `location = Abstract`, `confidence` at most `medium`, `article_notes` starts with `ABSTRACT ONLY.`, `extracted_by` ends with `abstract-only`. Group sizes are usually missing: leave the n fields null rather than guess. These rows are flagged in the graph (`abstract_only = true`) and weighted 0.5.
8. **Human checkpoint A (calibration, after batch F01).** A reviewer reads 20 randomly drawn rows from F01 (`severity_batch.py sample --batch F01 --n 20 --seed 20261105` prints `id`, `row`, `marker`, `outcome_class`, `direction`, `significant`, `quote`, `location`) against the papers and records `correct` / `wrong field <name>` per row in `experiment_specs/EXP13-calibration.json`. Continue only if at least 18 of 20 have marker, outcome class, direction and significance right; otherwise revise the agent prompt and redo F01. Repeat the 20-row check after F10 and after A01.
9. **Coverage report.** `severity_batch.py status` prints counts by `status`, `track`, year and species; these feed `extraction_coverage` (stage 2).

### Stage 2: graph and link prediction

Seed `20261105` for every random step (`numpy.random.default_rng(seed)`; networkx calls that sample take `seed=`).

1. **Rows to edges.** Filter rows as in section 2.3. Aggregate to study units (cohort else article). Nodes, each with `node_id` = `<type>:<name>`:
   - `marker` (canonical name; attributes `marker_class`, `n_units`, `n_articles`);
   - `outcome` (outcome node as in 2.3);
   - `species` (the 4 species groups);
   - `specimen` normalised from `specimen` by first match, lowercased: `urine` -> `urine`; `csf` -> `CSF`; `tissue|necropsy|histolog` -> `tissue`; `arterial` -> `arterial blood`; `plasma` -> `plasma`; `serum` -> `serum`; `whole blood|edta|blood` -> `whole blood`; `clinical examination|echocardiograph|imaging` -> `clinical examination`; `signalment|questionnaire|history|record` -> `history and signalment`; else `other`; blank -> `not stated` (pilot values include `serum`, `whole blood (EDTA)`, `arterial blood`, `clinical examination (echocardiography)`, `citrated plasma`, `urine (cystocentesis)`, `referring veterinarian questionnaire`, `signalment record`);
   - `article` (attributes `year` from `first_pub_date`, `track`);
   - `cohort` (study unit; for articles without a cohort the unit node is `unit:<ID>`; attributes `members`, `certainty`).
   Edges:
   - `marker`-`outcome` **tested** edge when at least one unit has a row with `significant` in `yes, no` for that pair. Attributes: `n_rows`, `n_units`, `units`, `articles`, `n_sig_yes`, `n_sig_no`, `direction_counts` (dict of `direction` values), `consensus` (EXP08 rules on unit-level signs), `n_total_sum` (sum over units of the largest `n_total` per unit), `weight` = sum over units of unit weight (1, times `abstract_weight` for abstract-only units, times 0.5 for `medium`), `first_year` (earliest article year), `abstract_only` (all rows abstract), `species_groups`.
   - `marker`-`outcome` **measured** edge (`descriptive_only`, `not_tested`, `unclear` only): kept in the export with `kind = measured` but not used as a "tested" link.
   - `marker`-`species`, `marker`-`specimen`: weight = number of units.
   - `unit`-`marker`, `unit`-`outcome`, `unit`-`species`: weight 1 (the unit measured that marker, used that outcome definition, studied that species).
   - `article`-`unit` (`member_of`).
2. **Graph views.** `G_full`: all nodes and edges (the export). `G_k` (knowledge view): `G_full` without article nodes (articles duplicate their units), used for centrality. `B`: the bipartite marker-outcome graph of tested edges, used for link prediction.
3. **Graph summary.** Node counts per type, edge counts per kind, density of `B`, number of connected components of `G_k` and the size of the largest, degree distribution of markers in `B` (min, median, max), and the share of tested edges supported by a single unit.
4. **Hub markers.** For each marker: `degree_B` (outcomes tested), `weighted_degree_B` (sum of `weight` over tested edges), `units` (distinct units), `species_groups`, `specimens`, betweenness centrality in `G_k` (`networkx.betweenness_centrality(G_k, normalized=True, weight=None)`; exact when `G_k` has at most `--betweenness-exact-max` 3000 nodes, else `k=--betweenness-k` 1000 sampled with `seed`), and the share of tested units with `significant = yes`. Rank by `weighted_degree_B`, ties by betweenness, then name; report the top `--top-hubs` 20 with their `marker_class`. Flag `single_article_hub = true` when more than half of the marker's weight comes from one unit.
5. **Link prediction scores** for candidate pairs: every marker m with at least `--min-marker-units` 2 units and every outcome o with at least `--min-outcome-units` 3 units, where (m, o) has no tested edge. Scores (all computed on `B` and the unit layer; deterministic):
   - `cn3` (bipartite common neighbours, length-3 paths): `sum over m' in N_B(o) of |N_B(m) ∩ N_B(m')|`;
   - `aa3` (bipartite Adamic-Adar): `sum over m' in N_B(o), o' in N_B(m) ∩ N_B(m') of 1 / log(1 + deg_B(o')) * 1 / log(1 + deg_B(m'))`;
   - `comeasure`: number of units that measured m (unit-marker edge) and also used outcome o in any test (unit-outcome edge), so the data to test the pair probably already existed; plus `comeasure_units` list;
   - `pa` (preferential attachment, baseline only): `deg_B(m) * deg_B(o)`.
   Combined score = mean of the rank percentiles of `cn3`, `aa3` and `comeasure` (percentile = average rank / number of candidates); ties broken by marker then outcome name. Report the top `--top-pairs` 50 with the evidence: the neighbour markers m' tested against o with their consensus and units (top 5 by `weight`), the outcomes m was tested against, the `comeasure_units`, the species groups of m and of o, and a one-line plain reason (for example "tested in 3 populations against complicated disease; 4 markers of the same class are tested against mortality in 6 populations; 2 populations measured it in dogs that also had a mortality definition"). A species-gap list: (m, o, species) triples tested in one species group but not in another where both the marker and the outcome occur in that other species.
6. **Embeddings.** If `importlib.util.find_spec("node2vec")` or `find_spec("gensim")` finds a package in the running environment, compute node2vec embeddings (dimensions 32, walk length 20, 10 walks per node, p = q = 1, window 5, seed) on `G_k` and score pairs by cosine similarity; otherwise set `embeddings = "skipped: no node2vec or gensim in .venv"` in `run_notes`. With the current environments it is skipped. Do not install a package for it.
7. **Temporal validation.** Cut-off year `--cutoff-year` default 2021 (core articles by year: 2021 to 2026 hold 168 of 404). Build `B_train` from units whose earliest article has `year < cutoff`; positives = candidate pairs (under the same `min_*_units` rules computed on the training graph) that become tested edges using only articles with `year >= cutoff`; negatives = the other candidate pairs. Score candidates on the training graph; report, per score (`cn3`, `aa3`, `comeasure`, `combined`, `pa`): ranking AUC (Mann-Whitney from numpy ranks, ties averaged), average precision, precision at 10 and 20, recall at 50; and a random baseline: 1000 random permutations of the scores (seeded), the AUC distribution's mean and 95th percentile, and the empirical p value `(count(random AUC >= observed) + 1) / 1001`. Sensitivity cut-offs `--sensitivity-cutoffs` 2019, 2023. If a cut-off has fewer than `--min-positives` 5 positives, record `evaluable = false` and give no metrics for it. Abstract-only rows count in both the training graph and the positives (flagged); a sensitivity run without abstract rows is reported.
8. **Multiple testing.** Only the temporal-validation p values are tests (5 scores x 3 cut-offs = 15); BH across these 15. Pair scores are rankings, not tests.

## 4. Outputs

### 4.1 Experiment JSON

`data/experiments/EXP13-CORPUS-graph.json`.

`experiment`:

- `code` `EXP13-CORPUS-graph`; `name` `Marker knowledge graph and untested marker-outcome pairs`; `description` one sentence; `method` `graph`; `dataset` `null`.
- `parameters` (defaults):

```json
{
  "seed": 20261105,
  "input": "data/severity/associations.csv",
  "quote_ok": ["exact", "near"],
  "confidence": ["high", "medium"],
  "medium_weight": 0.5,
  "abstract_weight": 0.5,
  "study_unit": "cohort_else_article",
  "outcome_node": "class_plus_complication",
  "min_marker_units": 2,
  "min_outcome_units": 3,
  "scores": ["cn3", "aa3", "comeasure"],
  "baseline": "pa",
  "combine": "mean_rank_percentile",
  "top_hubs": 20,
  "top_pairs": 50,
  "betweenness_exact_max": 3000,
  "betweenness_k": 1000,
  "embeddings": "node2vec_if_installed",
  "node2vec": {"dimensions": 32, "walk_length": 20, "num_walks": 10, "p": 1, "q": 1, "window": 5},
  "cutoff_year": 2021,
  "sensitivity_cutoffs": [2019, 2023],
  "min_positives": 5,
  "random_permutations": 1000,
  "adjustment": "benjamini_hochberg",
  "pair_review": null,
  "extraction": {"batch_size": 10, "concurrency": 5, "fulltext_model": "claude-opus-5-5", "abstract_model": "sonnet", "max_attempts": 2}
}
```

- `script` `scripts/experiment_graph.py`; `script_version` 12-character SHA-256 prefix; `run_utc`.
- `n_subjects` = study units in the graph; `n_variables` = marker nodes; `n_tests` = 15 (temporal-validation tests; fewer when cut-offs are not evaluable).
- `summary`: units, articles, markers, outcomes, tested edges, top 3 hubs, temporal-validation AUC of the combined score at the main cut-off, and the review status of predicted pairs.

`associations`: `[]`. `cluster_assignments`: `[]`.

`results[]`:

| kind | title | sort_order | payload |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | `{"sections": [...]}` |
| `extraction_coverage` | How much of the corpus is extracted | 1 | see below |
| `graph_summary` | The marker graph at a glance | 2 | see below |
| `hub_markers` | Hub markers | 3 | see below |
| `predicted_pairs` | Untested marker-outcome pairs ranked by graph evidence | 4 | see below |
| `temporal_validation` | Does the ranking predict pairs tested later? | 5 | see below |
| `run_notes` | Rows included and dropped, settings, skipped steps | 6 | see below |

- `extraction_coverage`: `{"status": "pilot" | "partial" | "complete", "in_scope": 404, "by_track": {"fulltext": {"in_scope": 204, "validated": 10, "no_severity_content": 0, "failed": 0, "pending": 194}, "abstract": {"in_scope": 200, "...": 0}}, "rows": 275, "rows_abstract_only": 0, "quote_check": {"exact": 275}, "confidence": {"high": 231, "medium": 36, "low": 8}, "markers": 82, "new_markers_added": 0, "by_year": {"2006": {"in_scope": 4, "extracted": 0}}, "by_species_group": {...}, "calibration": [{"batch": "F01", "correct": 19, "of": 20}]}`. `status` = `pilot` while only the 10 pilot articles are extracted, `complete` when no in-scope article is `pending`. Read from `index.csv`.
- `graph_summary`: `{"nodes": {"marker": 82, "outcome": 6, "species": 4, "specimen": 9, "cohort": 9, "article": 10}, "edges": {"tested": 120, "measured": 6, "marker_species": 90, "marker_specimen": 85, "unit_marker": 150, "unit_outcome": 25, "article_unit": 10}, "density_B": 0.24, "components_G_k": 1, "largest_component": 120, "marker_degree_B": {"min": 1, "median": 1, "max": 5}, "single_unit_edges_share": 0.82}`.
- `hub_markers`: `{"hubs": [{"rank": 1, "marker", "marker_class", "degree_B", "weighted_degree_B", "units", "betweenness", "share_significant", "species_groups", "specimens", "outcomes", "single_article_hub": false}]}`.
- `predicted_pairs`: `{"review_status": "pending" | "reviewed", "pairs": [{"rank", "marker", "marker_class", "outcome", "combined", "cn3", "aa3", "comeasure", "pa", "evidence": {"neighbour_markers": [{"marker", "consensus", "units"}], "marker_outcomes": [...], "comeasure_units": [...], "species_marker": [...], "species_outcome": [...], "reason": "..."}, "review": null}], "species_gaps": [{"marker", "outcome", "tested_in": ["B. rossi"], "untested_in": ["B. canis"]}]}`. `review` after checkpoint B: `{"verdict": "plausible" | "implausible" | "already_tested_elsewhere" | "not_meaningful", "reviewer", "comment"}`.
- `temporal_validation`: `{"cutoffs": [{"year": 2021, "main": true, "evaluable": true, "n_train_units": 120, "n_candidates": 900, "n_positives": 14, "scores": {"combined": {"auc": 0.71, "ap": 0.08, "p_at_10": 0.2, "p_at_20": 0.15, "recall_at_50": 0.43, "random_auc_mean": 0.5, "random_auc_p95": 0.63, "p": 0.004, "p_adjusted": 0.03}}, "positives": [{"marker", "outcome", "first_year", "rank_combined"}], "without_abstract_rows": {"auc_combined": 0.69}}]}`.
- `run_notes`: `{"filter_counts": {...}, "dropped": [{"id", "row", "reason"}], "species_groups": {...}, "specimen_map": {"whole blood (EDTA)": "whole blood"}, "embeddings": "skipped: no node2vec or gensim in .venv", "betweenness": "exact", "edge_export": "data/experiments/EXP13-CORPUS-graph.edges.csv", "node_export": "data/experiments/EXP13-CORPUS-graph.nodes.csv", "pair_review_file": null}`.

Interpretation sections, in order: `Question`; `What was extracted` (coverage, models, checks, human calibration); `What the graph shows` (hubs with numbers, species overlap, H1 and H2); `Untested pairs worth a look` (only pairs reviewed `plausible` at checkpoint B are named; before review the section says the list is unreviewed and names none); `Does the ranking work` (temporal validation, H3); `Limits`.

### 4.2 Other artefacts

- `data/experiments/EXP13-CORPUS-graph.edges.csv`: columns `source, target, source_type, target_type, kind, weight, n_units, n_rows, n_sig_yes, n_sig_no, consensus, direction_counts (JSON), n_total_sum, first_year, abstract_only, species_groups (semicolon list), units (semicolon list), articles (semicolon list)`. One row per edge of `G_full`.
- `data/experiments/EXP13-CORPUS-graph.nodes.csv`: `node_id, type, name, marker_class, year, n_units, degree_B, weighted_degree_B, betweenness`.
  Both are CSV, so `ExperimentLoader` (which reads `data/experiments/*.json` only) ignores them. They are for Gephi or Cytoscape.
- Stage 1: `data/severity/extractions/<ID>.json` (one per article), `data/severity/extractions/index.csv`, regenerated `data/severity/associations.csv`, `extraction_report.md`, new `manual` rows in `marker_map.csv`; `experiment_specs/EXP13-calibration.json` and `experiment_specs/EXP13-pair-review.json`. Prompt packets stay outside the repository and are deleted after the run (they contain copyrighted text).

## 5. Acceptance checks

Stage 1:

1. `index.csv` has 404 rows; no row is `pending`; every `validated` and `no_severity_content` article has `data/severity/extractions/<ID>.json`; `failed` rows have a reason. Count with `python -I`.
2. The full checker run reports 0 schema errors, every quote `exact` or `near`, and every `numbers_missing` entry explained in `note`; `extraction_report.md` lists 0 unmapped rows.
3. `severity_batch.py validate` over all batches reports 0 parse errors.
4. Calibration file shows at least 18 of 20 correct for F01, F10 and A01.
5. Every abstract-track row has `source_type = abstract` and `confidence` not `high`.
6. The 10 pilot extraction files are byte-identical to before (`git diff --stat data/severity/extractions/` shows no change for them; they are tracked in git if `data/severity/` is tracked, otherwise compare SHA-256 recorded at the start).

Stage 2:

7. `--self-test`: on a hand-built 4-marker, 3-outcome bipartite graph in the docstring, `cn3`, `aa3` and the Mann-Whitney AUC equal hand-computed values; AUC of a perfect ranking is 1.0 and of the reversed ranking 0.0.
8. Re-running with the same seed gives identical JSON apart from `run_utc`, and identical CSVs.
9. Counts: marker nodes equal the distinct canonical markers in the filtered rows; tested edges equal the distinct (marker, outcome) pairs with a tested row; no candidate pair is already a tested edge.
10. Random-score null: replacing the combined score with a seeded random score in a check run gives a temporal AUC within the random 95% band.
11. Spot check 5 predicted pairs (seeded) by grepping `associations.csv`: the marker and outcome really never co-occur in a tested row.
12. The console loads the JSON; `dbo.experiment` has `EXP13-CORPUS-graph` with `method = 'graph'` and `dbo.experiment_result` has 7 rows for it.
13. `predicted_pairs.review_status` is `reviewed` and the interpretation names only `plausible` pairs before the page is shared.

## 6. Caveats and reporting language

- **Extraction errors propagate.** Every edge comes from an LLM extraction checked automatically for quotes and numbers and sampled by a human (20 rows per checkpoint); unsampled rows may still have wrong direction or significance. Rows failing the quote check never enter the graph.
- **Abstract-only evidence** (200 of 404 articles) gives only the results the authors chose to put in the abstract, which favours significant findings; their edges are half-weighted and flagged.
- **Absence of an edge** means the pair was not found in the extracted articles of this review window (2006 to 2026), not that nobody tested it. Say "not tested in the reviewed articles".
- **Non-independence.** Study units merge articles sharing a cohort; 35 of 38 cohorts are `probable`.
- **Hubs** reflect research attention (what is easy or popular to measure), not biological importance. A hub is not a better marker.
- **Predicted pairs** are hypotheses for a researcher to consider, ranked by how the evidence network is shaped; they are not predictions that the association exists, and none may be described as a likely finding until reviewed. Temporal validation measures whether the ranking anticipated research attention, not truth.
- **Species** are kept as nodes and split; `unspecified` is a group, not a species.
- **Pilot.** Until stage 1 is complete, `extraction_coverage.status` is `pilot` and the interpretation says that the graph covers 10 articles.

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md`, `TEMPLATE.md`, `core/CLAUDE.md`, this spec, `experiment_specs/EXP08-SEV-evidence.md` (filters, species groups, study units), `data/severity/EXTRACTION_GUIDE.md`, `association_schema.json`, `docs/nlp-and-severity.md` (severity part), `scripts/check_associations.py` (all of it), `scripts/experiment_pairwise.py` (output assembly, hash), two pilot extraction files (`CB050.json`, `CB040.json`). Done: you can say which checker functions `severity_batch.py` will call.
2. **Tidy (stage 1 tooling).** Write `scripts/severity_batch.py` (stdlib; subcommands `plan`, `packet --batch --out`, `validate --batch`, `sample --batch --n --seed`, `status`), with a module docstring. Record the SHA-256 of the 10 pilot extraction files in its `plan` output. Run `.venv/Scripts/python.exe -I scripts/severity_batch.py plan --batch-size 10`. Done: `data/severity/extractions/index.csv` has 404 rows, 10 `done`, 394 `pending`, batches F01 to F20 and A01 to A20.
3. **Extract batch F01.** `.venv/Scripts/python.exe -I scripts/severity_batch.py packet --batch F01 --out "$TEMP/exp13_packets"`; launch one claude-opus-5-5 agent per article (at most 5 at a time) with the agent prompt from stage 1 step 4 and the packet; then `.venv/Scripts/python.exe -I scripts/severity_batch.py validate --batch F01`; send failures back once; then `.venv/Scripts/python.exe -I scripts/check_associations.py`. Done: every F01 row is `validated`, `no_severity_content` or `failed`.
4. **Checkpoint A.** `.venv/Scripts/python.exe -I scripts/severity_batch.py sample --batch F01 --n 20 --seed 20261105`; stop and ask the user (or the named reviewer) to check the 20 rows and fill `experiment_specs/EXP13-calibration.json`. Continue only at 18 of 20 or better. Done: the file exists with the verdicts.
5. **Extract the rest.** Repeat task 3 for F02 to F20 (checkpoint again after F10), then A01 to A20 with the Sonnet model (checkpoint after A01). Run the full checker once per closed batch, never concurrently with agents. Done: section 5 checks 1 to 6 pass.
6. **Script.** Write `scripts/experiment_graph.py` (numpy, networkx; docstring with inputs, outputs, run command, `.venv`), one argparse option per parameter in 4.1 plus `--code`, `--name`, `--self-test`, `--pair-review <json>`. Copy the EXP08 filter, species and unit code rather than importing. Add `networkx>=3.2` to `scripts/requirements-experiments.txt`. Smoke-test on the pilot table before task 5 finishes if useful. Done: `--help` lists every option; `--self-test` passes.
7. **Run.** From `core/`:
   `.venv/Scripts/python.exe -I scripts/experiment_graph.py --code EXP13-CORPUS-graph --name "Marker knowledge graph and untested marker-outcome pairs" --seed 20261105`
   Expected runtime 1 to 3 minutes (1000 random permutations x 3 cut-offs; exact betweenness on a few hundred nodes). Done: the JSON and both CSVs exist; `predicted_pairs.review_status = "pending"`.
8. **Checkpoint B (before predicted pairs are published).** Give the top 30 `predicted_pairs` with their evidence to a veterinary reviewer; record `{"marker", "outcome", "verdict", "reviewer", "comment"}` per pair in `experiment_specs/EXP13-pair-review.json`. Re-run task 7 adding `--pair-review experiment_specs/EXP13-pair-review.json`. Done: `review_status = "reviewed"`; the interpretation names only `plausible` pairs. Do not load or share the page with predicted pairs named before this step; loading with `pending` status is allowed for internal checking.
9. **Load.** `Babesiosis.Console --datasets-only` (`ReviewRoot` = `core/`). Through `babesiosis-local-db` (read `docs/database.md` first): `SELECT e.experiment_code, e.method, COUNT(*) FROM dbo.experiment e JOIN dbo.experiment_result r ON r.experiment_id = e.experiment_id WHERE e.experiment_code = 'EXP13-CORPUS-graph' GROUP BY e.experiment_code, e.method;` returns `graph` and 7. Done: the row arrives and `/experiments/EXP13-CORPUS-graph` shows the interpretation.
10. **Verify.** Run section 5 checks 7 to 13. Re-run EXP08 with its unchanged command so it uses the full table, and reload.
11. **Document.** Add `severity_batch.py` and `experiment_graph.py` to `scripts/README.md`; update `docs/nlp-and-severity.md` (severity section: extraction now covers all core canine articles, `index.csv`, abstract-only flag) and the `associations.csv` row of the table in `core/CLAUDE.md` (no longer "pilot, 10 articles"); update `docs/database.md` result kinds if listed; mark EXP13 in `docs/ml-experiment-plan.html` if status is tracked.
12. **Optional.** A web view for `method = 'graph'` (hub table, predicted-pairs table with evidence, temporal-validation plot), only after tasks 1 to 11 pass.

## 8. Open questions

1. Who are the human reviewers for checkpoints A and B? Default: the user; the building agent stops and asks at each checkpoint rather than skipping it.
2. Should canine reviews (40) be extracted for rows they report from their own data? Default: no; out of scope.
3. Extraction cost: about 194 Opus and 200 Sonnet agent runs (roughly 15 to 30 thousand input tokens each for full texts). Default: proceed batch by batch, and report token use after F01 so the user can stop.
4. Should `medium` confidence rows form edges? Default: yes, at weight 0.5; `low` rows do not.
5. Main cut-off year. Default 2021, with 2019 and 2023 as sensitivity; if 2021 has fewer than 5 positives, the earliest evaluable sensitivity cut-off becomes the main one and this is recorded.
6. Outcome granularity: 9 outcome classes make a small bipartite graph. Default: class plus complication name; a finer split by `severity_label` is not attempted.
7. A node embedding needs a package that is not installed. Default: skip and record; installing `node2vec` or `gensim` is the user's decision.
8. `data/syndromes/` is absent on this machine. Default: not needed; concept links through `marker_map.csv` `cui` are a later extension.
