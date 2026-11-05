# Clinical syndromes plus treatment: re-screen of excluded records (2026-11-05)

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
