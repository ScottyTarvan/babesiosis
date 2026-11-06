# Clinical syndromes plus treatment (2026-11-05)

Two passes against one criterion (`screening_criteria.md`), merged in `combined_set.csv`:

1. **Re-screen of excluded records** (this folder's root): records the main review excluded, re-read for syndrome plus treatment.
2. **Tagging of the 444 included CB articles** (`articles/`): the main review's own canine articles, tagged against the same criterion.

## Combined set: `combined_set.csv`

One row per paper that is `include` or `uncertain` in either pass (367 rows: 331 includes, 36 uncertain). Columns: `source` (`main_review` = in `articles.jsonl`, with `article_id`, `primary_category`, `design`, `cohort_id`; `rescreen` = not in `articles.jsonl`), `decision`, `include_type`, `treatment_role` (main-review rows only: `primary` = treatment or response is a study aim, `context` = standard therapy given and outcome or post-treatment values reported, aim elsewhere), `syndromes`, `treatments`, `outcome_reported`, `species`, `coinfection`, `n_dogs`, `rationale`, `stage`, `access_note`. The re-screen's duplicate reference-list entry and one re-screen record that is also a main-review article are dropped.

| Source | include | uncertain |
|---|---|---|
| main_review (171 of 444 tagged) | 171 | 5 |
| rescreen (160 unique papers) | 160 | 31 |

Includes by type: case_report 131, case_series 89, trial 47, review 31, retrospective_series 19, experimental 14. Co-infection in 49; an outcome in 316. Commonest syndrome tags: haemolytic anaemia 215, thrombocytopenia 110, AKI 56, icterus 49, hepatopathy 43. Commonest treatments: imidocarb 132, doxycycline 102, diminazene 84, clindamycin 69, fluids 58, metronidazole 55, azithromycin 54, transfusion 53, atovaquone 52.

Rebuild: `python -I scripts/assemble_clinical_set.py` (after both passes below).

## Pass 2: tagging the included articles (`articles/`)

| File | Content |
|---|---|
| `articles/candidates.jsonl` | The 444 CB articles with design, sample size, finding, abstract (from `search/packets/`), and treatment/outcome sentences from `data/markdown/` where full text exists (230 articles) |
| `articles/batches/ia_NN.md`, `batches.json` | 12 tagging batches given to the screeners |
| `articles/results/ia_NN.json` | First-pass decisions (Claude Sonnet agents) |
| `articles/adjudication_packet_{a,b,c}.md`, `adjudications_{a,b,c}.jsonl` | 82 articles re-read by Claude Opus agents against the local full text (`data/markdown/`), the article note, and open web sources: the 14 uncertains, 11 cohorts excluded as `no_treatment` although they report deaths or recovery, and 30 includes with no drug named. 25 decisions changed |
| `articles/tagging.jsonl` | Final decision per CB article |

Result: include 171 (case_series 68, case_report 48, review 21, retrospective_series 13, trial 11, experimental 10; `treatment_role` primary 65, context 106), uncertain 5 (CB061, CB084, CB268, CB383, CB495: paywalled or no source), exclude 268 (`no_treatment` 259, `no_dog_clinical_data` 4, `prevention_only` 4, `not_peer_reviewed` 1).

Rule applied to the pathophysiology cohorts: dogs sampled at admission "before treatment" with no post-treatment values or outcome are `no_treatment`; a cohort whose paper states the therapy given (even generically) and reports survival, deaths or follow-up values is `include`, `case_series`, `treatment_role: context`. Borderline includes to weigh before use: treatment inferred from MEDLINE indexing rather than the text (CB043, CB446, CB481); treatment described only as "treated" or "antibabesial" (CB011, CB018, CB067, CB111, CB129, CB182, CB306, CB332, CB333, CB338, CB352, CB437, CB468, CB470, CB486); CB129 is a post-mortem bone-marrow study where treatment is incidental. CB372 and CB399 were kept excluded but may describe treatment in full text that could not be read.

Rebuild: `python -I scripts/build_clinical_tagging.py`, run the screeners and adjudicators, then `python -I scripts/assemble_clinical_set.py`.

## Pass 1: re-screen of excluded records

A separate screening pass over records the main review excluded, asking a different question:
does the record describe, in dogs infected with *Babesia*, **a clinical syndrome and the treatment given, with an outcome**?
The main review's decisions in `search/screening_r*.jsonl`, `search/r4/screening.jsonl` and `articles.jsonl` are unchanged.
This folder's includes are **not** in `articles.jsonl` and have no article notes; they are a candidate list for a clinical analysis.

| File | Content |
|---|---|
| `screening_criteria.md` | The question, include types, exclusion codes and record fields |
| `candidates.jsonl` | 379 records: every r1–r4 exclusion coded `treatment_efficacy` or `other_out_of_scope`, other exclusions whose title or rationale mentions treatment, and extraction-stage exclusions/unresolved records with treatment terms. Carries the original decision and rationale |
| `screen_batches/ct_NN.md`, `batches.json` | Title/abstract batches (40 records) given to the screeners |
| `results/ct_NN.json` | First-pass decisions (Claude Sonnet agents, one per batch) |
| `adjudication_packet_{a,b}.md`, `adjudications_{a,b}.jsonl` | The 72 uncertain records and their adjudication (Claude Opus agents, allowed to read DOI landing pages, PubMed, Europe PMC, Crossref and OpenAlex; no paywalls or bot checks bypassed). `sources` and `access_note` say what was read or blocked |
| `screening.jsonl` | Final decision per candidate (adjudication overrides the first pass; `stage` says which) |
| `included.csv` | Includes and remaining uncertains with syndromes, treatments, species, n and rationale |

## Result (2026-11-05)

| Decision | n |
|---|---|
| include | 161 (one paper twice: `PMID:28625019` and its reference-list record `REF:efficacyofazithromycine…`) |
| uncertain | 32 (no abstract reachable: regional journals, eLIBRARY.ru, bot-checked repositories, title-only reference entries) |
| exclude | 186 (`no_treatment` 65, `no_dog_clinical_data` 46, `prevention_only` 28, `babesia_incidental` 19, `not_peer_reviewed` 14, `no_syndrome` 10, `pharmacology_healthy` 4) |

Includes by type: case_report 83, trial 36, case_series 22, review 10, retrospective_series 6, experimental 4.
Rescue rate by original code: `treatment_efficacy` 73 of 145, `other_out_of_scope` 76 of 183.

Caveats: single LLM pass plus adjudication of uncertains only, no duplicate human screening; `syndromes`, `treatments` and `n_dogs`
come from the abstract and are not verified against full text; many includes are small regional case reports (Indian and
Russian/Ukrainian journals) with limited peer review, as in the main review's round 3.

Rebuild: `python -I scripts/build_clinical_rescreen.py`, run the screeners, then `python -I scripts/assemble_clinical_rescreen.py`.

## Caveats for both passes

LLM screening with adjudication of borderlines only, no duplicate human screening. Tags for main-review articles rest on full text for 230 articles and on abstracts for the rest; re-screen tags rest on abstracts. The re-screen's includes have no article IDs, notes, cohort links or full text, and are not in the web app or SQL store. Neither pass changes the main review's decisions.
