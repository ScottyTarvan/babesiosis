# SV-INT report: why do some dogs develop severe babesiosis? Integration across all packages

Experiment `SV-INT-01-integration-report` (method `integration_synthesis`, role `descriptive`). Run 2026-11-12. No new test (0 of 0).

## 1. Question and hypothesis

Why do some dogs with babesiosis develop severe disease and others mild disease? SV-INT reads the 22 Done experiments of the programme
and asks, for each of five lines of explanation (time, load, host, parasite, response), whether the data support it, contradict it or
cannot address it, and how strong each piece of evidence is. There is no hypothesis test.

## 2. Inputs

- Every package report: `SV-G1/`, `SV-G2/`, `SV-01/`, `SV-02/` (parts a and b), `SV-03/`, `SV-04/`, `SV-05/`, `SV-06/` (parts a and b),
  `SV-07/`, `SV-08/`, `SV-09/`, `SV-10/` `report.md`. Their SHA-256 (12 characters) at the run are in the `parameters.reports` field of the
  experiment row. `rules.md` (detectable-effect table).
- `ledger.md` (22 Done experiments) and the `summary` column of `dbo.experiment` (read through the `babesiosis-local-db` MCP server on
  2026-11-12; all 22 summaries agree with the reports on the numbers quoted here).
- Every package's `exposure.md` (13 files).
- **Spec** `spec.md` SHA-256 `5a3cc3700b3ececa76bec1e0a7bb501c003eb07512d93fc4d96916ded46a945f`. `scripts/synthesis.json`
  `3273234beed899d91e29ea9427c369355081f8e54b8300e71387853b90886f73`; `scripts/build.py` `3e1fd7e1541d…`.
- SV-INT opened no outcomes file. Python 3.12.12 (uv 0.10.4), standard library only. No random numbers.

## 3. What was done

- One row per finding (20 findings from the 22 experiments; SV-G1, SV-G2, SV-07 and SV-10-03 are cross-cutting foundations) in
  `scripts/synthesis.json`: what was asked, what was found, effect with interval, n, independent sources, what it could have detected,
  and a strength class. **Every number carries a literal quote from its report; `build.py` checks all quotes (87 in all) and stops if
  one is missing.** It also stops if a contributing experiment is not `Done` in the ledger or a Done experiment is left out.
- Verdict per line by the rules in `spec.md` (supported / contradicted / not supported, underpowered / cannot address).
- Sources counted after SV-07 (section 4.3 below), not by file or article.
- Decisions for the user merged from all reports (section 9). Exposure logs combined (`out/exposure_log.md`, 29 entries).

**Deviations from the spec:** none. One clarification: the strength class of each finding is my judgement from the report text (the
classes are defined in `spec.md` and on the page).

## 4. Results

### 4.1 The answer

**None of the five lines of explanation is supported by a replicated result.** Time and parasite cannot be addressed with the public
files, and load cannot be addressed in natural infection (inside 5 Beagles, damage followed load). Host (age) and response are not
supported, but only large effects were detectable. The signals that pass a test restate band neutrophils, anaemia or the severity label
itself, and most *B. rossi* outcome evidence comes from one hospital. What the programme mostly learned is about the evidence: there are
fewer independent sources than files, severity definitions fragment the literature, and the deciding studies need new dog-level data
(SV-02c, SV-10).

### 4.2 Line by package by result by strength

| Line | Verdict | Experiment | Result (effect, 95% CI, n) | Sources | Could detect | Strength |
|---|---|---|---|---|---|---|
| **Time** | Cannot address | SV-01-01-habitus-distance | Habitus vs distance from Beagle course given stage: partial rho -0.24 (-0.39 to -0.07), n 147; +0.08 (-0.08 to 0.24) once haematocrit is controlled. No stage construction passes both validity checks; one Beagle left out reverses dog order in 2 of 5 refits | SRC-B course, SRC-F dogs | \|rho\| ≈ 0.23 | Instrument failed |
| | | SV-01-02-ds03-geometry | 20% (DS03 cohort 1, n 85), 17% (cohort 2, n 18), 24% (DS05, n 147) lie within 2 spread units of the course; 61%, 83%, 61% project onto an end. Median natural haematocrit 0.18 | SRC-A, SRC-F | no test | Descriptive |
| **Load** | Cannot address | SV-02-01-load-by-outcome | No pooled estimate (6 units in 5 cells, max 2). *B. canis* died vs survived (CB516, 8 vs 7): g of log load -0.17 (-1.19 to 0.85). CB141 load rho 0.35 (0.23 to 0.46), n 222; antibody rho -0.65 (-0.73 to -0.56), n 166. No *B. rossi* unit reports load vs clinical outcome | 6 literature units | 1.6 SD (CB516) | No data |
| | | SV-02-02-beagle-reaction-norms | Lactate and habitus loss: one shared norm; haematocrit: cannot tell; 0 different norms. Lactate at 5% load 1.14 (n 1) vs 1.19–1.44 mmol/L. Clear damage only above ~10% parasitaemia | SRC-B (5 dogs) | no test | Descriptive |
| | | SV-03-01-evidence-matrix | Parasitaemia in 4 units: no conflict, no consistent cell | literature | – | No data |
| **Host** | Not supported (underpowered) | SV-05-01-age-death | Died 6/50 young vs 9/90 adult: OR 1.23 (0.34 to 4.15); MH by sex 1.24 (0.41 to 3.77). 0/3 q < 0.05. Died includes euthanasia | SRC-A | OR ≥ ~3.7 | Null, underpowered |
| | | SV-05-02-age-form | Rule: not supported. DS05 haematocrit young − adult HL -0.02 (-0.04 to +0.01), n 55 vs 92; DS03 -0.06 (-0.10 to -0.025) is SRC-A and partly physiological. Young present ~1 day earlier (q 0.090). 1/8 q < 0.05. 7 neutered dogs, not tested | SRC-F, SRC-A | ~0.48 SD | Negative |
| | | SV-10-02-host-genetics | No canine study has genotyped dogs against severity. Design: 142 + 142 pit bull-type dogs (~471 cases) for DEA 1 OR 3 | none | OR 3 | Design only |
| **Parasite** | Cannot address | SV-G2-01-literature-extraction | 2 units test parasite species or genotype | literature | – | No data |
| | | SV-10-01-parasite-genotype | Design: 80 complicated + 120 uncomplicated (≈229 enrolled) for genotype19 OR 2.5; death ≈545 enrolled | none | OR 2.5 | Design only |
| **Response** | Not supported (underpowered) | SV-04-01-il8-direction | No IL-8 conflict: +0.02 (-0.28 to +0.34), 12 vs 85 (S-CB050); +0.15 (-0.29 to +0.56), 18 vs 13 (S-CB017). IL-8 differs only infected vs controls (-0.45 in S-CB050). The *B. rossi* "falls with severity" claim rests on CB037 (abstract only) | SRC-A, SRC-D | 0.86 / 1.05 SD | Negative |
| | | SV-04-02-response-size-balance | Rule reads "balance", weakly: +0.32 (+0.02 to +0.60; p 0.070, q 0.139) and +0.44 (+0.07 to +0.78), carried by MCP-1 (+0.47, +0.22 to +0.70, q 0.052; +0.81). Size only in *B. canis* (+0.71), whose label includes SIRS | SRC-A, SRC-D | 0.86 / 1.05 SD | Weak |
| | | SV-03-01-evidence-matrix | 0 of 423 cells reach 3 units; nothing pooled. Post hoc 4 *B. rossi* cells (temperature, bands, cortisol, thyroid); 0 once Onderstepoort counted once | 42 units | – | No data |
| | | SV-03-02-definition-map | Marker in its own definition in 38 of 504 tested rows; significant 79% vs 47% | 42 units | – | Descriptive |
| | | SV-06-01-transfer-grid | 21 of 37 mechanisms are gaps (21 of 36 grade 2–3, 58%); 10 of 26 grade-3 already have canine severity data. Grades are one agent's unreviewed judgement | literature | – | Descriptive |
| | | SV-06-02-ds07-candidate-tests | None of 10 proteins q < 0.05 (9 tested). Haemoglobin beta +0.48 (+0.09 to +0.82), q 0.133, partly restates the label | SRC-C, 14 vs 18 | 1.0 SD (1.3 after correction) | Negative |
| | | SV-08-01-transcriptome-signatures | Interferon and neutrophil-granule scores rose in 5 of 5 Beagles (sign p 0.0625, the minimum), before habitus fell; also in mild dogs; "earlier at high dose" not met | SRC-B (5 dogs) | p < 0.05 impossible | Weak |
| | | SV-09-01-ds05-residual-axes | 2 stable residual axes, n 140; axis 2 with habitus partial rho -0.26 (-0.40 to -0.10); exploratory | SRC-F | \|rho\| ≈ 0.23 | Weak |
| | | SV-09-02-axis-congruence | 0 of 6 axis-by-block checks replicate | SRC-A, SRC-D | 3–5 shared variables | Negative |
| | | SV-09-03-axis-outcome | S-CB050 died +0.49 (+0.21 to +0.74), q 0.003, but bands alone +0.60 and the score after bands +0.15 (-0.17 to +0.45) | SRC-A, SRC-D | ~0.76 SD | Restates known |

Strength counts over the 20 findings: no data 4, design only 2, instrument failed 1, null underpowered 1, negative 4, restates known 1,
weak 3, descriptive 4. **No finding is a replicated positive result.**

### 4.3 Which lines the data support, contradict, or cannot address

- **Supported:** none.
- **Contradicted:** none. No pre-stated rule that counts against a line was met with enough power to rule out a moderate effect. The
  closest: SV-04-01 removes the premise of the response line (the IL-8 conflict is not in the dog-level files), and SV-02-02 saw no
  tolerance difference in 5 Beagles.
- **Not supported, underpowered:** host (age), response.
- **Cannot address:** time (reference course too short, stage score failed), load in natural infection (no data), parasite (no data),
  and host genetics, breed and neuter status.

### 4.4 Independent sources (after SV-07)

| Source | Files | Species | Setting | Outcome label |
|---|---|---|---|---|
| SRC-A | S-CB050; S-CB517 (all 112 are S-CB050 dogs); DS03 natural cohorts and controls (file level probable); 3 of 10 fatal DS04 dogs | *B. rossi* | Onderstepoort referral hospital | died, 15 of 141 (includes euthanasia) |
| SRC-B | DS02 = DS01 = DS03 experimental = DS06 | *B. rossi* | 5 experimental Beagles | habitus; 1 died |
| SRC-C | DS07 (CB112) | *B. rossi* | archived serum; counted with Onderstepoort by SV-03; number link to DS04 unverified | complicated 14 vs 18 |
| SRC-D | S-CB017 | *B. canis* | Zagreb | complicated 18 vs 13 |
| SRC-E | DS03 IMHA dogs only (if SV-07's proposal is accepted) | – | comparator | none |
| SRC-F | DS05 | *B. rossi* | clinic, another province | habitus only |
| SRC-G | DS04 (CB147) | *B. rossi* | OVAH tissue bank (Onderstepoort) | all died, no contrast |
| SRC-O | S-CB516 | *B. canis* | not stated in the reports | died 8 vs 7 |

**What this means.** *B. rossi* natural infection with an outcome contrast comes from SRC-A and SRC-C, both counted with Onderstepoort.
DS03 is not a replication of S-CB050: it is the same dogs. DS05 is the only *B. rossi* source from elsewhere and has no hard outcome.
In the literature (SV-03), every replicated *B. rossi* signal (band neutrophils, cortisol, thyroid, hypothermia) is from one hospital, and
none keeps 3 units once Onderstepoort is counted once. Between-source contrasts are also between species (one species per source).

### 4.5 Candidates to measure (not predictors)

| Candidate | Experiments | Evidence | Why it is not a predictor |
|---|---|---|---|
| Band neutrophils | SV-03-01, SV-09-03 | 2 *B. rossi* units (CB040, CH03); S-CB050 died +0.60 | One hospital, already published |
| Lactate | SV-03-01, SV-02-02 | higher with death in 3 units (CB040, CH21, CH18) | direction counts only; part of several definitions |
| MCP-1 | SV-04-01/02, SV-03-01 | +0.47 (q 0.052) and +0.81; 2 units, 2 species | two sources, different species, definitions and times; does not track the SV-09 score |
| Interferon / neutrophil signatures | SV-08-01 | rose in 5 of 5 Beagles before habitus fell | rose in mild dogs too; 5 dogs, 1 source |
| Haemoglobin beta | SV-06-02 | +0.48 (+0.09 to +0.82), q 0.133 | not significant after correction; partly the label; sample haemolysis not separable |
| Cortisol, thyroid | SV-03-01 | 3 *B. rossi* units, post hoc merged classes | 0 at 3 units once Onderstepoort counted once |
| Antibody level | SV-02-01 | rho -0.65 vs load 0.35 (CB141, *B. canis*) | one cohort, no formal comparison; a lead for SV-02c |

## 5. Stability and checks

- 87 quotes checked against the reports; all found. All 22 Done experiments are used; all contributing codes are `Done` in the ledger.
- Rerun: `out/` deleted and rebuilt; the CSV files and the exposure log were byte-identical, the load file identical except `run_utc`.
- The verdicts do not depend on one experiment: each "cannot address" verdict rests on at least two packages.

## 6. Confounders carried from the packages

- Species is aliased with source, country, assay and definition (rule 6); no between-file difference is attributed to species.
- "Died" in the Onderstepoort files includes euthanasia for poor prognosis.
- Most dog-level labelled files are already seen; SV-01, SV-04, SV-05, SV-09 outcome results are exploratory.
- Extractions and categories are language-model work (SV-G2 agreement 0.99 on a 20% blind sample; 16-article owner check).

## 7. What this does not show

- That time, load, host, parasite or the response do not matter. Most results are nulls from small files: age and death could detect
  only OR ≈ 3.7; markers ≈ 0.76 to 1.3 SD; the Beagle work has 5 dogs.
- That any candidate predicts severity. No predictive model was fitted; the residual axes are directions of variation, not groups of
  dogs or subtypes.
- SV-01's stage score failed validation, so nothing here says that severe dogs are "late". SV-06a's grades are one agent's unreviewed
  judgement, so its ranking is a reading list, not an order of importance.
- SV-02c (the author data request) was not run: it is a user decision.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files:** every number (quoted from the reports and checked by `build.py`); the 22 database summaries; the exposure logs.
- **Taken from documentation:** the package results themselves (SV-INT did not re-run any analysis); SV-07's linkage findings.
- **Inferred:** the strength class of each finding and the verdict of each line (rules in `spec.md`); SRC-C's Onderstepoort membership
  (SV-03's S1 set, not confirmed by SV-07).

## 9. Decisions for the user (de-duplicated)

| # | Decision | Raised by |
|---|---|---|
| 1 | Send the case-numbering query (DS07/DS04 register, DS07 outcomes, DS03 dates, CB145 cohort). Draft `SV-07/out/author_query_draft.md`, not sent | SV-07; index.md |
| 2 | Run SV-02c: ask the authors of CB141 (342 *B. canis*), CB040 (320 *B. rossi*) and RQ-CB145 for dog-level load, antibody, age, outcome | SV-02a; index.md |
| 3 | Change `independent_source` in `/core/datasets.jsonl` and the "never pool" list: DS03 natural and controls → SRC-A, DS03 experimental → SRC-B, DS04 overlap note | SV-07; SV-05 |
| 4 | Correct `data.md` (S-CB017 day 1/day 7 labels; DS07 172 proteins; DS04 score sheets; DS03 Day 1 anchored; DS03 natural = S-CB050; DS04 54 = BLSC29) | SV-G1; SV-07; SV-05 |
| 5 | Use the S-CB050 WBC for the 24 flagged S-CB517 dogs | SV-G1 |
| 6 | Replace the pilot extractions under `/core/data/severity/` with SV-G2 v2; add the 18 new marker names to `marker_map.csv` | SV-G2; index.md |
| 7 | Extract the 34 abstract-only tier B articles (CB037 first) or obtain the CB037 full text | SV-G2; SV-03; SV-04 |
| 8 | Accept merged outcome definitions for a harmonised *B. canis* meta-analysis (10 cells reach 3–4 units) | SV-03 |
| 9 | Accept the DS03–S-CB050 pairs at dog level, to join DS03 red-cell values to S-CB050 death as a new, separately locked analysis | SV-05; SV-09 |
| 10 | Second, independent review of the SV-06a grades | SV-06a |
| 11 | Accept haptoglobin through its group master, and the low-coverage rank tests replacing the presence test (DS07) | SV-06b |
| 12 | Re-quantify DS06 from SRA PRJNA703846 to recover MPO and ELANE (large download) | SV-08 |
| 13 | Pursue any SV-10 design; set severity thresholds; one load-adjustment rule; CB379 full text; rank memo 3's plasma panel by SV-06a (now possible) | SV-10 |
| 14 | Which package to deepen. Proposal: SV-02c first (cheapest dog-level load and outcome), then the SV-10-03 cohort with ≥ 200 dogs outside Onderstepoort; the DS03–S-CB050 join (item 9) is cheapest but rests on unverified links | SV-INT |

## Software and outputs

Python 3.12.12 (uv 0.10.4), standard library. Outputs: `out/synthesis_table.csv`, `out/decisions.csv`, `out/exposure_log.md`,
`out/db/SV-INT-01-integration-report.json`. Database via the console loader (way B). View
`experiment-integration-synthesis-view.component.*`, seen at `http://127.0.0.1:4400/experiments/SV-INT-01-integration-report` on
2026-11-12 in the light and the dark theme: no raw JSON card, no console error.
