# Experiment specifications

One Markdown specification per planned experiment, written for an AI agent that will build the experiment, run it, and save the results so the console loader and the web app can show them. The overview that produced this list is `docs/ml-experiment-plan.html`; the first finished experiment, which every spec treats as the worked example, is EXP01 (`scripts/experiment_pairwise.py` to `data/experiments/EXP01-DS05-pairwise.json`).

Paths in every spec are relative to `core/` unless stated. Follow `core/CLAUDE.md` for querying rules: structured files, not rendered reports; join on article `id`; `python -I`; never count `HU`/`BG` as canine evidence.

## Index

| Spec | Layer | Dataset(s) | Readiness | Model used to write it |
|---|---|---|---|---|
| [EXP02-DS05-clustering.md](EXP02-DS05-clustering.md) | 1 | DS05 | tidy file exists | sonnet |
| [EXP03-SRCA-mortality.md](EXP03-SRCA-mortality.md) | 1 | S-CB050, S-CB517 | tidy files needed | opus |
| [EXP04-DS07-proteome.md](EXP04-DS07-proteome.md) | 1 | DS07 | tidy file needed | opus |
| [EXP05-LONG-trajectories.md](EXP05-LONG-trajectories.md) | 1 | DS01, DS02, DS06, DS03, S-CB017 | tidy files needed | opus |
| [EXP06-DS05-anomaly.md](EXP06-DS05-anomaly.md) | 1 | DS05 | tidy file exists | sonnet |
| [EXP07-POOL-haematology.md](EXP07-POOL-haematology.md) | 2 | pooled cohorts | harmonisation needed | opus |
| [EXP08-SEV-evidence.md](EXP08-SEV-evidence.md) | 2 | data/severity | ready | opus |
| [EXP09-COINF-rules.md](EXP09-COINF-rules.md) | 2 | DS05, S-CB013 | tidy file needed | sonnet |
| [EXP10-CORPUS-topics.md](EXP10-CORPUS-topics.md) | 3 | articles, embeddings | ready | sonnet |
| [EXP11-CORPUS-labels.md](EXP11-CORPUS-labels.md) | 3 | articles | gold set needed | sonnet |
| [EXP12-CORPUS-gaps.md](EXP12-CORPUS-gaps.md) | 3 | articles | ready | haiku |
| [EXP13-CORPUS-graph.md](EXP13-CORPUS-graph.md) | 3 | all canine articles | extraction needed | opus |
| [EXP14-CORPUS-cohorts.md](EXP14-CORPUS-cohorts.md) | 3 | full texts, cohorts | ready | sonnet |
| [EXP15-CORPUS-sharing.md](EXP15-CORPUS-sharing.md) | 3 | articles, datasets | ready | haiku |

## Conventions every spec and every built experiment must follow

### Codes and files

- Experiment code: `EXP##-<dataset token>-<method token>`, up to 60 characters, matching `dbo.experiment.experiment_code`. Dataset token is the dataset code for single-dataset runs (`DS05`), or one of `SRCA` (the two Onderstepoort cohorts), `LONG` (longitudinal series), `POOL` (harmonised pool), `SEV` (severity extraction table), `COINF`, `CORPUS`. Method token is one lowercase word.
- Script: `scripts/experiment_<method>.py`, with a module docstring that states inputs, outputs, the exact run command and the non-stdlib dependencies, as `experiment_pairwise.py` does. Add any new package to `scripts/requirements-experiments.txt`.
- Output: `data/experiments/<code>.json`. One file per run; re-running overwrites it. Never write results anywhere else in `data/`.
- Tidy files: `data/tidy/<dataset code>.json`, produced by `scripts/tidy_<dataset code lowercase>.py`, modelled on `scripts/tidy_ds05.py`. The raw file under `data/raw/<dataset code>/` is read-only and never modified. Every cleaning rule is recorded in the dataset `notes` or the variable `description`.

### Python environments

- `.venv` (Python 3.13, numpy 2.5): default for experiment scripts. Run `.venv/Scripts/python.exe -I scripts/<script>.py` from `core/`.
- `.venv-nlp` (scikit-learn 1.9.1 and the NLP stack): use when scikit-learn, embeddings or text processing are needed. Prefer numpy-only implementations for small statistics, as EXP01 does, so the default environment stays light. State in the spec which environment the script needs and which packages must be installed.
- Always `python -I`. Never load `data/syndromes/mentions.jsonl` whole.

### Tidy dataset JSON (input to Layer 1 and Layer 2)

Top-level keys `dataset`, `variables`, `subjects`, `observations`.

- `dataset`: `code`, `title`, `article_code`, `repository`, `source_record`, `licence`, `independent_source` (SRC letter), `species`, `design`, `source_file`, `source_sha256` (from `data/manifest.jsonl`), `n_subjects`, `notes` (list of cleaning notes), `extracted_utc`, `script`.
- `variables[]`: `code`, `name`, `source_name`, `unit`, `data_type` (`N` numeric, `O` ordinal, `C` categorical, `D` date, `T` text), `domain`, `derived` (bool), `derived_from` (list of parent codes or null), `include_default` (bool, whether the default test set includes it), `ref_low`, `ref_high`, `description`, `levels` (dict of level to count, categorical only), `sort_order`.
- `subjects[]`: `code`, `group_label`, `outcome_label` (null when the dataset has none).
- `observations[]`: `subject`, `variable`, `time_point` (`''` for single-visit data; otherwise a short sortable string such as `D03`), `value_num`, `value_text`, `value_date`.

A pooled or harmonised dataset is itself a tidy dataset with its own code (for example `POOL01`), its own tidy script, provenance per variable (`description` names the source dataset and the unit conversion), `independent_source` set to `POOL` (the database column is 10 characters wide) and the SRC letters it combines listed in `notes`.

### Experiment JSON (output of every experiment)

Top-level keys `experiment`, `associations`, `cluster_assignments`, `results`. The loader (`console/Babesiosis.Console/ExperimentLoader.cs`) reads exactly these.

- `experiment`: `code`, `name`, `description`, `method` (one token; the web app maps known methods to a view and shows unknown ones as formatted JSON), `dataset` (dataset code, or `null` for runs with no single tidy dataset), `parameters` (every setting, including `seed`), `script`, `script_version` (12-character hash of the script file), `run_utc`, `n_subjects`, `n_variables`, `n_tests`, `summary` (one plain-text paragraph).
- `associations[]`: only when `dataset` is set; variable codes must exist in that dataset. Fields `variable_a`, `variable_b`, `test`, `estimate`, `estimate_label`, `n`, `p_value`, `p_adjusted`, `significant`, `trivial`, `direction`, `detail` (object). Empty list when the method produces none.
- `cluster_assignments[]`: only when `dataset` is set; `subject_code` must exist in that dataset. Fields `subject_code`, `cluster_label` (up to 30 characters), `score` (silhouette or membership strength, nullable). Empty list when the method produces none.
- `results[]`: `kind`, `title`, `sort_order`, `payload` (any JSON). Required in every run: one result with `kind = "interpretation"` and payload `{"sections": [{"heading": ..., "paragraphs": [...]}]}`, which the web app renders as the note under the visuals; and one with `kind = "run_notes"` recording what was included, dropped or skipped. Add method-specific kinds for figure data (matrices, cluster summaries, ranked tables). Keep payloads under about 2 MB.

### Loading and viewing

- Load with `console/Babesiosis.Console` run as `Babesiosis.Console --datasets-only` (DatasetLoader then ExperimentLoader). A tidy dataset must be loaded before an experiment that references it. `appsettings.json` `ReviewRoot` must point at `core/`.
- The web app's Experiments screen (`/experiments/<code>`) has a dedicated view for `pairwise_association`; every other method falls back to the interpretation note plus formatted JSON for each result. A spec may ask for a new view as an optional last task, but the experiment must be complete and loadable without it.

### Statistics and reporting rules

- Permutation p values where distributional assumptions are doubtful; Benjamini-Hochberg across the whole run; effect sizes with intervals next to every p value.
- Nested cross-validation for anything predictive, with feature selection inside the inner loop; report the events-per-variable ratio.
- Species is always a variable, never pooled silently. Cohort or `independent_source` decides what counts as replication.
- Clusters are phenotype groupings, never "subtypes". No predictive model is described as clinically usable.
- Fixed seed in `parameters`; the run must reproduce bit-for-bit from the tidy file.
- The interpretation text states the question, what was done, the main findings with numbers, and the limits, in plain language for a veterinary reader.

## What a spec is for

A spec is read by a building agent that has not seen this conversation. It must be able to open the spec, read the files it names, write the tidy script if one is needed, write the experiment script, run both, load the results, and know when it is done. `TEMPLATE.md` gives the section order; every section is filled, and "not applicable" is written where a section does not apply rather than omitted.

## Findings made while writing the specs

The spec writers inspected the raw files and found facts that the plan page and `datasets.jsonl` did not state. Each is recorded in the spec concerned; they are repeated here because they change what counts as independent evidence.

- **S-CB517 is not a second cohort.** Its 112 dogs are S-CB050 cases 1 to 97 and controls 201 to 215, with identical cytokine values and the same 12 deaths (EXP03). The cross-cohort transfer planned for EXP03 is replaced by a temporal split inside S-CB050, and POOL01 merges S-CB517 into S-CB050.
- **The SRC-B beagles appear in four places.** DS01 is a subset of DS02, and the five experimental dogs in DS03 are DS02 dogs 2 to 6 (matched on haemoglobin, EXP05). `datasets.jsonl` lists DS03 as SRC-E only; POOL01 excludes those five dogs and the 16 IMHA dogs.
- **DS07 has 224 master proteins, not thousands**; 112 pass the article's own filter (EXP04).
- **S-CB013 screens for B. vogeli, A. platys and two haemotropic mycoplasma targets.** It has no Ehrlichia column, and four of its headers are misnamed (EXP09).
- **`data/severity/associations.csv` has 275 rows**, not 290 (a line count over quoted multi-line fields). CB050 and CB145 share cohort CH03, so the pilot has 9 study units (EXP08).
- **`data/syndromes/` is absent on this machine.** EXP10, EXP11 and EXP13 treat its CSVs as optional.
- **Environments.** `.venv` has numpy only (no scipy, no pip); `.venv-nlp` has scikit-learn 1.9.1 and scipy but no umap-learn, hdbscan, bertopic, sentence-transformers or statsmodels. Specs fall back to PCA coordinates, scikit-learn's HDBSCAN, TF-IDF similarity and numpy REML accordingly.
- **DS05 variables with `derived = false` but a `derived_from` parent** (mcv, mch, mchc, wcc, arc, globulin) are excluded from the EXP02 and EXP06 inputs; BET065 and BET066 have no laboratory data.
- **Side files the specs expect:** `experiment_specs/EXP06-raw-check.json` (hand-written raw-sheet check), the EXP11 gold-set CSV, the EXP14 review-queue CSV, and `data/severity/extractions/index.csv` for EXP13. Their paths are given in each spec.

## Decisions left open

Every spec ends with a section 8 listing the decisions its writer could not settle, each with a default the building agent takes if nobody answers. The ones that cross specs: whether to correct the S-CB517 and DS03 entries in `datasets.jsonl` (default no, until a human confirms); whether canine reviews enter the corpus experiments (EXP10 yes, EXP12 yes with a sensitivity flag, EXP13 and EXP15 no); who labels the EXP11 gold set and reviews the EXP13 checkpoints (default: the project owner, with an independent LLM agent as the weaker fallback for labelling).

