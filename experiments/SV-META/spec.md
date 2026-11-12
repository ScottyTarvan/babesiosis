# SV-META spec: meta review of all experiments for research leads

Experiment `SV-META-01-research-leads`, method `meta_review`, role `descriptive`. Written 2026-11-12 before any result was scored.
Package file: [/experiments/SV-META-meta-review.md](../SV-META-meta-review.md).

All labelled files are already seen (rules.md, "Outcome lock"), and the results of the 23 experiments were read before this spec.
The role is therefore `descriptive`: every tier is a hypothesis-generating label, not a confirmation. This spec fixes the rules so that
the scoring is mechanical and can be repeated; it does not make the results blind.

## 1. Question

Does any result of the 23 experiments, alone or with results of other experiments, show a finding worth further research on
(1) severity: a measurement that correlates with severity; (2) mechanism: a mechanism not established in canine babesiosis; or
(3) human parallel: a correlation shared with falciparum malaria, human babesiosis or sepsis that the canine literature has not made?

What would count against the programme yielding a lead: no candidate reaches tier A, B or C, and the tier D leads are only the
SV-06a gap list restated. The report says so in its first sentence if that happens.

## 2. Inputs

- Every package folder: `SV-G1`, `SV-G2`, `SV-01`, `SV-02` (a, b), `SV-03`, `SV-04`, `SV-05`, `SV-06` (a, b), `SV-07`, `SV-08`,
  `SV-09`, `SV-10`, `SV-INT`: `report.md` and every file in `out/`.
- `shared/tidy/*.features.json` and, for the theme indicators of section 5 only, these outcomes files: `S-CB017.outcomes.json`,
  `S-CB517.outcomes.json`, `S-CB516.outcomes.json`, `DS05.outcomes.json`. `DS02` dose group is a design variable in the features file;
  `DS02.outcomes.json` is not opened. `S-CB050.outcomes.json` and `DS07.outcomes.json` are not opened: their contrasts are read from the
  SV-04, SV-05, SV-06b and SV-09 output files. Each opened outcomes file gets a line in `exposure.md`.
- Novelty: `/core/articles.jsonl` (streamed), `/core/articles/*.md`, `/core/data/markdown/CB*.md` (read, never copied),
  `SV-G2/associations_v2.csv`, `dbo.search_articles` / `dbo.search_passages`, PubMed (no user details in a query).

## 3. Step 2: the result census (`out/census.csv`)

One row per quantitative result in an `out/` file: experiment code, measure, comparison or outcome, species, dataset, independent
source (section 4), n, effect type, effect, 95% interval, p, q, family size, role (`primary`, `secondary`, `sensitivity`, `descriptive`,
`positive_control`, `post_hoc`, `observation`), source file and line. Observations with no test (a linkage fact, a gene missing from
a matrix, a design number) get the type `observation`. Each number is read by the program from its file; `scripts/check_census.py`
then reopens each cited file and line and confirms that every number of the row is printed there (to the printed precision). The run
stops if a number is not found.

Rows taken: every row of a test or effect table (`tests.csv`, `contrasts.csv`, `infected_vs_control.csv`, `age_contrasts.csv`,
`ds07_candidates.csv`, `axis_outcome.csv`, `congruence.csv`, `sign_counts.csv`, `primary_deltas.csv`, `load_by_outcome.csv`,
`readings.csv`, `replication_geometry.csv`, `conflicts.csv`, `evidence_matrix_collapsed.csv` consistent cells, `ranked_gaps.csv`,
`linkage` summaries, `power.csv` key scenarios). Per-dog and plotting files (`map_points.csv`, `dog_values.csv`, `set_scores.csv`) are
not census rows.

## 4. Independent sources (after SV-07)

| Source | Files | Species | Severity contrast used here |
|---|---|---|---|
| SRC-A | S-CB050, S-CB517 (same dogs), DS03 natural and controls (same dogs), 3 DS04 dogs | *B. rossi* | died vs survived (includes euthanasia) |
| SRC-B | DS02 = DS01 = DS03 experimental = DS06 (5 Beagles) | *B. rossi* | high dose (3, sicker by design, 1 died) vs low dose (2) |
| SRC-C | DS07 | *B. rossi* | complicated vs uncomplicated |
| SRC-D | S-CB017 | *B. canis* | complicated vs uncomplicated, day 1 |
| SRC-F | DS05 | *B. rossi* | dullness (habitus reversed); a proxy, no hard outcome |
| SRC-G | DS04 | *B. rossi* | none (all fatal) |
| SRC-O | S-CB516 | *B. canis* | died vs survived (includes euthanasia) |
| LIT | published group results (SV-G2, SV-02a, SV-03) | by unit | as published; Onderstepoort units counted once with SRC-A |

A literature unit that reports the dogs of a source above (CH03 = SRC-A, CB112 = SRC-C, CH23 = SRC-D, CH21 = SRC-O, CH09 = SRC-B) is
that source, not another one.

## 5. Step 4: themes and indicators (`out/themes.csv`)

Themes are chosen after the results were seen; every combined p carries that statement and is corrected for the number of themes.
One indicator per independent source, oriented so that a positive value means "more of the mechanism in the more severe dogs".
Effect scale: Cliff's delta (severe minus non-severe) for group contrasts; Spearman rho with dullness (4 minus habitus score) for
SRC-F; Cliff's delta high minus low dose of the change from the dog's own baseline (mean of days −1 and 0, or day 0) to its last
pre-treatment sample for SRC-B. Where a package file already gives the indicator, it is read from that file; otherwise it is
computed from the tidy files: 2,000 bootstrap resamples of dogs (stratified by group), 10,000 label permutations (exact enumeration
for SRC-B: 10 allocations), seed 20261112. Raw values are never compared between files.

| Theme | Expected direction | SRC-A | SRC-B | SRC-C | SRC-D | SRC-F | SRC-O |
|---|---|---|---|---|---|---|---|
| T01 Neutrophil activation, left shift | higher | bands (SV-09 file) | neutrophil-granule transcript score (SV-08 file) | lactoferrin (SV-06b file) | bands (computed) | bands (computed) | – |
| T02 Monocyte and macrophage activation | higher | monocyte count, S-CB517 (computed) | monocyte count (computed) | CD14 (SV-06b file) | monocyte count (computed) | monocyte count (computed) | – |
| T02s same, sensitivity: CCL2 (MCP-1) where measured | higher | MCP-1 (SV-04 file) | MCP-1 pre-treatment change (SV-04 file) | CD14 | MCP-1 (SV-04 file) | monocyte count | – |
| T03 Type 1 interferon | higher | – | interferon transcript score (SV-08 file) | – | – | – | – |
| T04 Haemolysis, cell-free haemoglobin | higher | – | cell-free Hb (computed) | haemoglobin beta (SV-06b file) | – | – | – |
| T05 Coagulation and platelet consumption | more consumption (lower) | – | platelets (computed) | antithrombin (SV-06b file) | platelets (computed) | platelets (computed) | – |
| T06 Endocrine stress response | higher cortisol, lower thyroid | – | – | – | – | – | – (literature only) |
| T07 Anaemia | more anaemia (lower haematocrit) | – | haematocrit drop (SV-02b file) | – (in label) | haematocrit (computed) | haematocrit (computed) | – |
| T08 Inflammation against regeneration at a given haematocrit | higher | – | – | – | – | SV-09 axis 2 (SV-09 file) | – |
| T09 Parasite load and antibody | higher load | – | peak parasitaemia (SV-02b file; set by dose) | – | – | – | log load g (SV-02a file) |
| T10 Host age | two-sided (positive = older) | age (SV-05 file) | – | – | – | age (computed) | age (computed) |
| T11 IL-10 | higher | IL-10 (SV-04 file) | IL-10 pre-treatment change (SV-04 file) | – | IL-10 (SV-04 file) | – | – |
| T12 Lactate, hypoperfusion | higher | – | lactate at peak load (SV-02b file) | – (in label) | – | – | – |
| T13 Acute phase (CRP) | higher | CRP, S-CB517 (computed) | CRP change (computed) | – | – | – | – |
| T14 Size of the cytokine response | higher | perturbation count (SV-04 file) | – | – | perturbation count (SV-04 file) | – | – |

Literature direction calls for the same marker (SV-03 `unit_calls.csv`) from units that are not one of these sources are shown beside
each theme (units higher / lower / not significant). They are not entered into the combined test.

**Circularity flags** (indicator kept in the table, removed from the combined test): SRC-C label contains haematocrit, urea,
creatinine, bilirubin, glucose, lactate and band neutrophils > 1.5 (bands and lactoferrin are therefore circular for T01 in SRC-C);
SRC-D label follows the WHO complicated-malaria classification and all complicated dogs are SIRS-positive (WBC, bands, temperature:
T01 and T14 circular in SRC-D; haematocrit circular for T07 in SRC-D); SRC-B contrast is set by dose, so load (T09) is circular.
**Known-driver flags**: band neutrophils in SRC-A (published, CB050), haematocrit and anaemia in any source (T07), the severity label.

**Combination** (themes with at least 2 non-circular indicators):

- Signed z per source: z = s · Φ⁻¹(1 − p/2), s = +1 if the effect is in the expected direction, −1 if not; p is the two-sided
  permutation p of the indicator.
- Stouffer Z = Σz / √k, one-sided p in the expected direction (two-sided for T10). Fisher's method on the one-sided p values beside it.
- Sign test: number of sources in the expected direction, exact one-sided binomial.
- Leave-one-source-out: Stouffer p with each source dropped; the largest is reported.
- Species: *B. rossi* sources (A, B, C, F) first: this is the primary combined row. *B. canis* (D, O) separately where 2 exist. Then
  all sources as a transfer check (never read as a species difference).
- Correction: Benjamini-Hochberg over the primary combined rows of all themes that have one; the number of such themes is stated.
  The statement "themes chosen after results were seen" is beside every combined p.

## 6. Step 3: the screen (columns of `census.csv`)

- **Statistical:** pass if the 95% interval excludes no effect and q < 0.05 in the result's own declared family. A result outside any
  declared family (secondary, sensitivity, post hoc, computed here) needs BH q < 0.05 over all census rows with a p value (the census
  family, size stated). Five Beagles (SRC-B): pass only with complete separation (Cliff's delta ±1, or the same direction in all 5
  dogs for a within-dog change); the minimum attainable p is stated.
- **Independence:** the number of independent sources that show a passing result in the same direction for the same marker.
- **Circularity:** `label` (marker in the severity definition), `known_driver` (restates anaemia, band neutrophils or the label), or
  `none`.
- **Novelty:** `published_same_dogs` (in the article that published the dataset), `published_other` (another CB article reports the
  same marker with severity in the same direction), `human_only` (known in a human disease, not in dogs), `not_found`. Record where.
- **Power:** detectable effect at 80% power, two-sided alpha 0.05, by normal approximation (stated as Cliff's delta or rho).

## 7. Steps 5 and 6: human parallels and refutation

- For each candidate (sections 8 and 9), the SV-06a top gaps and the SV-08 signatures: the counterpart in falciparum malaria, human
  babesiosis or sepsis, the direction, whether it agrees, a DOI for each claim, and whether a CB article already makes the parallel.
  "New" only if no CB article and no PubMed record found makes it. `HU` articles are used first.
- Refutation: each candidate that survives the screen with a provisional tier A, B or C, and each tier D lead, gets a separate attempt
  to reject it by a sub-agent with a fresh context and only the candidate's evidence pointers. Reasons it may use: the same dogs counted
  twice; the marker is in the label; the result does not survive correction for tests or themes; already published; an artefact of
  sample or assay; the direction changes in a sensitivity analysis. The attempt and its result go in `out/refutation.csv`. A refuted
  candidate becomes X. Candidates that are X at the screen get a refutation row that cites the screen reason.

## 8. Step 7: tiers (sharpened; none made easier)

A candidate is (a) a marker with at least one census row that passes the statistical screen, (b) a theme, or (c) a gap or signature
from SV-06a or SV-08.

- **A, significant finding:** passes the statistical screen in at least 2 independent sources of one species, no passing indicator is
  circular or a known driver, and the finding is not already published as a severity finding (novelty `not_found` or `human_only`).
- **B, signal:** passes the statistical screen in exactly 1 source (or in 2 or more, but A fails only on novelty in all but one), not
  circular, not a known driver, and the passing result is not the published severity finding of the article that reported those dogs
  nor of another CB article.
- **C, convergent lead:** not A or B; at least 2 non-circular *B. rossi* indicators (or all-source indicators for the transfer check)
  in the expected direction and none with an interval that excludes 0 in the opposite direction; primary combined BH q < 0.05;
  leave-one-source-out p < 0.05 for every source dropped; and the cross-source claim is not already published in a CB article.
- **D, gap lead:** no canine data against severity (SV-06a status `none` or `measured_no_severity`, or a signature with no severity
  contrast), human evidence grade 3 in SV-06a (or a severe-malaria signature from the human literature for SV-08), and a canine assay
  that exists (validated or used in dogs).
- **X, rejected:** null, circular, known driver, published, artefact, single source that fails the screen, or refuted in step 6.
  Kept with the reason.

## 9. Step 8: research leads (`out/leads.csv`)

At most 10, ordered by tier (A, B, C, D), then within a tier by: A and B, the smallest q; C, the smallest combined q; D, SV-06a rank,
moving a lead up when a public file can test it now (DS07, DS06, the DS03–S-CB050 join). Each lead: hypothesis (one sentence), kind of
finding (severity, mechanism, human parallel), tier, evidence (codes, effects, sources), human counterpart with DOI, refuting result,
cheapest next study with existing data, the study that needs new dogs (SV-10 memo), and the measurement to add to the SV-10-03 minimum
dataset. A candidate is a thing to measure, not a predictor. No predictive model; no clustering; the words "subtype" and "endotype"
are not used.

## 10. Database and view

Way B (console loader): `out/db/SV-META-01-research-leads.json` with results `primary_result` (tier counts, the answer),
`leads`, `themes`, `census`, `refutation`, `interpretation`. View `experiment-meta-review-view.component.*`.

## 11. Software and seeds

Python 3.12 in `env/py` (uv), numpy and scipy pinned in `requirements.txt`. Seed 20261112 for every bootstrap and permutation.
