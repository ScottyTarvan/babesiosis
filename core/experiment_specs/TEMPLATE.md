# EXP## <dataset token> <method token>: <name>

| Field | Value |
|---|---|
| Experiment code | `EXP##-<TOKEN>-<method>` |
| Layer | 1 single dataset / 2 pooled or evidence table / 3 corpus |
| Method token | `<method>` (goes in `experiment.method`) |
| Dataset(s) | codes, or `null` with the reason |
| Readiness | ready / tidy file needed / harmonisation needed / extraction needed |
| Python environment | `.venv` or `.venv-nlp`; packages to add |
| Estimated build effort | small (under 2 hours of agent work) / medium / large |
| Suggested model for the building agent | haiku / sonnet / opus, with one line of reasoning |
| Depends on | other experiment codes or tidy files that must exist first |

## 1. Question and hypotheses

What the experiment asks, as one or two questions. Named hypotheses where the literature gives them, each with the direction expected and the article that motivates it. What result would count as a negative finding.

## 2. Data

### 2.1 Sources

Exact files: tidy JSON codes, raw files under `data/raw/<id>/` with their sheet or table names, `data/inspection/<id>.json`, `datasets.jsonl` record fields, `articles.jsonl` fields, severity CSVs, SQL tables. Licence and independent-source letters for every dataset used.

### 2.2 Tidy file required (when readiness is not "ready")

For each tidy file to create: the raw sheet or table, the subject identifier column, the variable mapping (raw column to `code`, `name`, `unit`, `data_type`, `domain`, reference range), the recodes and derived variables, the `group_label` and `outcome_label` rules, the `time_point` rule for longitudinal data, and the cleaning notes to record. Name the script `scripts/tidy_<code>.py` and say that it follows `scripts/tidy_ds05.py`.

### 2.3 Variables and filters

Which variables enter the analysis (by `code`, or the rule such as `include_default = true and derived = false`), which are held out for comparison, exclusions, minimum counts, missing-data rule.

## 3. Method

Numbered steps an agent can implement without further decisions. For each step: algorithm, parameters with defaults, seed handling, what is computed, what is stored. Include:

- preprocessing (standardisation, transforms, imputation and its sensitivity analysis)
- the main analysis
- validation (resampling, permutation nulls, stability, nested cross-validation where predictive)
- multiple-testing control and the family it covers
- effect sizes and intervals

Name any formula or algorithm that a numpy-only implementation must reproduce, and say when scikit-learn or another package is justified instead.

## 4. Outputs

### 4.1 Experiment JSON

The `experiment` block field by field, including the full `parameters` object with defaults. Whether `associations` and `cluster_assignments` are written and with what fields. Every `results[]` kind with its `title`, `sort_order` and a payload schema (field names and types, with a small example). The `interpretation` sections to write, by heading. The `run_notes` payload.

### 4.2 Other artefacts

Figures data, CSV exports or tables that belong somewhere else, with their paths. Nothing outside `data/experiments/` and `data/tidy/` unless justified.

## 5. Acceptance checks

Concrete checks the building agent runs before declaring the experiment done: the JSON loads with the console, counts match (`n_subjects`, `n_variables`, `n_tests`), the run reproduces from the seed, the permutation null behaves (for example a shuffled label gives no significant results at the chosen alpha more often than alpha), sanity comparisons against the source article's published numbers, and the interpretation reads correctly for a veterinary reader.

## 6. Caveats and reporting language

The limits that must appear in the interpretation and in any write-up: sample size and events, non-independence, species, label definitions, extraction confidence, and the wording rules (phenotype groupings not subtypes; rankings not prognostic scores; gaps in the index not gaps in the literature).

## 7. Build plan for the agent

Ordered tasks, each with what done looks like:

1. Read: the files to read first.
2. Tidy: scripts to write and run, if any.
3. Script: the experiment script, its command line, its docstring.
4. Run: the exact command and expected runtime.
5. Load: the console command and the SQL check that the rows arrived.
6. Verify: the acceptance checks from section 5.
7. Document: update `scripts/README.md` and `docs/database.md` rows; add the experiment to `docs/ml-experiment-plan.html` status if the page is kept.
8. Optional: a dedicated web view (`webapp/Babesiosis.Web/src/app/modules/experiments/views/`), only after everything above passes.

## 8. Open questions

Decisions the spec writer could not settle from the files, each with the default the building agent should take if nobody answers.
