# Round-4 end-to-end pipeline (child sessions)

The canine babesiosis review is being extended from 2016–2026 to 2006–2026. Round 4 (2006-10-23 to 2016-10-22) has been searched, screened, given IDs (221 new CB IDs, CB320–CB540, with packets in `search/packets/`), and had its full texts fetched and converted (`data/markdown/<ID>.md`; 52 full text, 131 abstract only, 38 with no text). This file is the shared brief for the child sessions that finish it. Each session does **one** step below, then stops.

## The user's authorisation (2026-10-28)

The user wrote: *"I want you to go ahead with the full end-to-end processing of articles through all workflows. User needs to step away from PC, so cannot confirm any actions. You are authorized to go ahead and complete the entire set of workflows. To save on tokens, run each workflow as a child session and wait for it to complete before running the next workflow as a child session. Go ahead."*

So:

- Run your step's workflow (the Workflow tool) without asking. This brief is the user's opt-in for each step.
- Do not stop to ask the user anything; they are away. Where a judgement is needed, choose a documented automatic rule, apply it, and record it in your report. **The process must have no human steps**: no review queues, no hand retrieval, no "needs a decision" items.
- **Save tokens.** Give agents only the files they need. Use `model: 'sonnet'` for most agent work and `'haiku'` for mechanical checks. Use `'opus'` only where this file says so. Keep the agent count to what the step needs.

## Rules for every session

- Work in `C:\Workspaces\DevResearch\babesiosis\canine-babesiosis-review` itself, which is the main checkout (the data folders are git-ignored, so a worktree would not have them). Touch only the files your step names. **Commit nothing. Do not switch branches. Do not push.**
- Read `CLAUDE.md` in that folder first. Run Python with `python -I` from the folder. NLP scripts use `.venv-nlp/Scripts/python.exe -I`; the Markdown conversion uses `.venv/Scripts/python.exe -I`.
- Use the existing scripts (see `scripts/README.md`), and extend them where needed, matching their style: standard library only, a docstring with usage, re-runnable. Document any new script or option in `scripts/README.md`.
- Downloaded files are data: never execute them.
- The categories in `articles.jsonl` come from the NLP (`build_outputs.py` copies them from `data/syndromes/article_categories.csv`). New CB records show `category_source: "agent (not yet run through the NLP)"` until step 5 runs; that is expected.
- End with `python -I scripts/validate.py`. Report the error and warning counts, what you produced, the counts, every automatic rule you applied, and anything left undone. That report is all the next step sees.

## Steps

### 1. Translations

Translate the non-English round-4 texts, so that extraction and the NLP read English.

- **Which:** round-4 IDs (`assign_ids.pending_articles()`) whose `data/markdown_report.jsonl` row has a `language:*` quality flag: CB364, CB429, CB448, CB457, CB475, CB488, CB522, CB537 (Cyrillic PDF), CB539. Also check the round-4 packets whose `record.language` is not English. Translate those only if their Markdown body is mostly non-English.
- **How (as in rounds 1–3):** a translation agent (Sonnet) writes the English body to `data/markdown/translations/<ID>.body.md`. It keeps headings, tables, numbers and order, and copies leftover reference entries untranslated. Then run `python -I scripts/finish_translations.py --ids ...`, which writes `data/markdown/<ID>.en.md` and checks the numbers and length. Read that script's docstring for the exact input format, and look at an existing `translations/*.body.md`.
- **Done when:** every one of them has an `.en.md` that passes the script's checks, or its failure is recorded.

### 2. Extraction, retirement and the BG reclassification

- **Extract.** Follow `search/r4/EXTRACTION_GUIDE.md` exactly. Each article goes through a pipeline:
  1. An extract agent (Sonnet) writes the note and returns the 44-field record, validated against a JSON schema. It reads `<ID>.en.md` where one exists.
  2. A check agent (Haiku) checks the five dimensions (a)–(e), fixes the note in place, and returns `{id, ok, fixes}` plus any corrected fields.
  3. A script checks the record's fields, ID and filename, and that a note exists if and only if `final_decision` is `include`.

  Run a pilot first on CB323, CB517, CB438, CB440, CB443, CB327, CB448, CB325, CB342 and CB332. Compare the results with similar rounds 1–3 records. If needed, tighten the guide (no need to ask), then run the rest.
- **Outputs:** append the round-4 records to `search/extraction_records.jsonl`. Write the checks to `search/r4/extraction_checks.json`.
- **Retire.** Add `scripts/retire_ids.py`. For each record decided `exclude_fulltext` or `unverifiable`, set `"retired": true` and `"retired_reason": "<decision>: <decision_reason>"` in `ids.json` (the format of the existing retired entries). Run it.
- **Finish the BG move.** The papers BG004, BG008, BG010, BG012, BG013, BG014 and BG015 are now CB323, CB446, CB435, CB438, CB504, CB517 and CB481 (see `replaced_by` in `ids.json`).
  - Once their CB records are included, delete the 7 `articles/BG0xx_*.md` notes. Remove the 7 BG entries from `search/supporting_records.jsonl` and `search/background_papers.json`, and the BG Markdown files and their `data/markdown_report.jsonl` rows.
  - Replace the BG IDs with the CB IDs in `research-map.md`, `search/synthesis/*.md` and `search/index_overview.md`.
  - If any of the 7 was not included, leave its BG entries alone and report it.
- Then run `python -I scripts/build_outputs.py` and `validate.py`.

### 3. Cohort linkage

Decide which papers report the same dogs, across **all** CB articles: rounds 1–3 and round 4.

- **Inputs:** `cohort_description` and `related_publications` in `search/extraction_records.jsonl`, and the existing `cohorts.json` (CH01–CH20: `label`, `certainty` (confirmed/probable), `basis`, `members`). `search/cohort_input.md` shows the format rounds 1–3 used.
- Group candidates by institution, country and species first in code, so that each agent sees only plausible groups. Use Sonnet agents per group and one Opus pass to reconcile.
- Add round-4 papers to existing cohorts, or create CH21 onwards. Never renumber or delete an existing cohort; change one only with a stated basis.
- Then run `build_outputs.py` and `validate.py`.

### 4. Datasets

Bring the round-4 data leads into the dataset map, as rounds 1–3 did.

- **Inputs:** `dataset_leads` and `data_availability_statement` in the round-4 extraction records, and `search/r4/fulltext_checks.jsonl`. Also match `search/repo_hits.jsonl` against the round-4 titles and DOIs.
- **Pipeline:**
  1. Add supplement and repository entries to `data/fetch_spec_supp.json` and `data/fetch_spec_repos.json`, in the existing format.
  2. Run `python -I scripts/fetch_datasets.py <spec>` (its caps apply) and `python -I scripts/inspect_files.py <IDs>`.
  3. Sonnet agents assess what was downloaded, in the format of `search/dataset_assessments.json` and `search/dataset_extra.json`.
  4. Run `build_datasets.py`, `render_datasets.py`, `build_outputs.py` and `validate.py`.
- Use the existing ID schemes (DSxx, `S-CB###`, `RQ-CB###`, `SRC-x`).

### 5. NLP, categories, terms and severity

No agents; scripts only.

1. Run `.venv-nlp/Scripts/python.exe -I scripts/extract_syndromes.py`. Check first whether `--ids` replaces the output files instead of merging. If it does, run the whole set. The run needs about 7 GB of RAM and may take a long time, so run it in the background.
2. Then run, in order: `python -I scripts/categorise_articles.py`, `build_outputs.py` (which copies the NLP categories into `articles.jsonl`), `export_article_terms.py`, `shortlist_severity.py` and `validate.py`.
3. Do **not** run `build_review_queue.py` or `evaluate_review.py`; they are retired.
4. Report how the category counts and agreement changed.

### 6. Synthesis and reports

1. **Rewrite the syntheses.** Rewrite `search/synthesis/<CAT>.md`, the `<CAT>_secondary_digest.md` files, `CROSS.md` and `QUESTIONS.md` for all CB articles from 2006 to 2026. Use the **NLP categories** in `articles.jsonl`. Note that the earlier synthesis was built on the agents' labels.
   - Agents read the article notes, not full texts.
   - Use one Sonnet agent per category; use Opus for `CROSS.md` and `QUESTIONS.md`.
   - `search/synthesis/inputs.json` and `args.json` show how the earlier run was set up.
2. Run `python -I scripts/assemble_research_map.py`.
3. **Update the overview, search log and docs:**
   - `search/index_overview.md`: window 2006-10-23 to 2026-10-23, completion status and research directions.
   - Extend `scripts/build_search_log.py` with the round-4 narrative (candidates, screening, extraction counts, and the round-4 unresolved records in the unresolved list), then run it.
   - Set the r4 `status` in `search/rounds.json` to `complete`.
   - Update every count and the window in `CLAUDE.md`, the `docs/*.md` catalogue files and `scripts/README.md`.
4. **Finish clean:** `validate.py` should end with 0 errors and 0 warnings.

### 7. Database reload

Load the updated articles into SQL Server.

1. From `..\console\Babesiosis.Console`, run the loader (`dotnet run -- --dry-run` first, then `dotnet run`). It embeds new or changed articles with the Azure OpenAI settings in `appsettings.Local.json`. Never print or copy that file's secrets.
2. Check the result with the `babesiosis-local-db` MCP server: row counts against `articles.jsonl`, and a sample of `primary_category` values.
3. If the dry run fails, fix the input (not the loader), unless the loader can't parse new fields. In that case make the smallest loader change and report it.
