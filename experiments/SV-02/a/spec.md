# SV-02a spec: parasite load by outcome, from the literature

Frozen 2026-11-12, before the analysis script was written. Package file: `/experiments/SV-02-resistance-tolerance.md`, part a.

## Question and hypothesis

Do dogs with severe babesiosis carry a higher parasite load than dogs with mild disease, inside one *Babesia* species and one outcome class? The package hypothesis is that dogs differ more in damage per parasite (tolerance) than in load (resistance). Part a can only test the weaker statement that published load-by-outcome contrasts are small or inconsistent; it cannot measure tolerance.

## Outcome lock

No dog-level outcomes file is opened. The input is published aggregate results extracted by SV-G2 (`/experiments/SV-G2/associations_v2.csv`). The parasitaemia rows were listed (not analysed) on 2026-11-12 to write the eligibility rules below, so this synthesis is not blind to the published results. `exposure.md` records that.

## Inputs

- `/experiments/SV-G2/associations_v2.csv` and `definitions_v2.csv` (SHA-256 recorded by the script; it stops if they change).
- `/core/cohorts.json` only through the `independent_unit` column that SV-G2 already filled.
- For the separate list only: the appraisal notes `/core/articles/<ID>_*.md` (keyword screen, then read by the agent). No full text is copied.

## Eligible rows (primary set)

1. `marker` is `Parasitaemia` or `Parasite DNA load (qPCR)` (SV-G2 maps ddPCR there with `load_method = other`).
2. The row compares load with a severity or outcome definition: `outcome_class` is not `parasitaemia_level`, and the groups are not defined by the experimental dose. CB105 (CH09, high vs low inoculum dose) is listed but excluded from the primary set, because dose sets the load by design.
3. Rows where the outcome *is* load (`outcome_class = parasitaemia_level`: CB098, CB187, CB241) are the inverse question (damage by load group). They go to a second table, "damage by load group", not to the pool.
4. Antibody rows of CH12 (CB141) go to the separate list as a comparison with the load row of the same cohort.

## Primary analysis

- Unit: independent unit (`independent_unit`). One unit gives one effect per outcome class; if a unit has several rows in one class, the row closest to admission and before treatment is used.
- Cell: species group × outcome class × definition. Species groups: *B. canis*, *B. rossi*, *B. gibsoni*, *B. vogeli*, mixed/unspecified. Never pooled across species.
- Effect: standardised mean difference of log load (severe minus comparison), Hedges' g, where the per-group data allow it:
  - mean and SD or SEM with group n: log-normal moment conversion (sigma² = ln(1 + SD²/mean²), mu = ln(mean) − sigma²/2).
  - median and range with group n: mean and SD of log load from log(min), log(median), log(max) (Hozo et al. 2005 for the mean, Wan et al. 2014 for the SD).
  - a correlation with a continuous severity score: Spearman rho with a Fisher-z 95% interval, converted to d = 2r/√(1−r²) only for display, flagged.
  - group n not printed: the unit stays in the direction table; an equal split of `n_total` is used only in a labelled sensitivity line.
- Pooling: random effects (REML tau²) with the Hartung-Knapp-Sidik-Jonkman interval, **only** in a cell with 3 or more independent units that share the definition and have a computable effect. Otherwise the cell gets a direction table (direction, significance, n, load method, sample timing).
- Moderators: `load_method` and `sample_timing`, tabulated by unit. Meta-regression only if a pooled cell has 10 or more units.

## Separate list

Every result of the form "severe disease at low load" or "protection or recovery at unchanged load", from (a) the SV-G2 rows (no difference by outcome, lower load in the severe group, load unrelated to a complication, antibody tracking severity more than load) and (b) the appraisal notes, keyword screen for sentences with parasitaemia and one of low, unchanged, despite, not correlated, independent of, unrelated. Each hit is read and kept only if it describes dogs (not wolves) with a clinical state and a load statement. Each item gets species, design, n, source level (SV-G2 row, full-text note, abstract-only note) and a DOI.

## Stability and sensitivity

- Equal-split n for units with only `n_total`.
- CB105 dose contrast shown beside the primary set.
- Leave-one-unit-out on any pooled cell (none expected).
- Detectable effect for each computable unit: the standardised difference with 80% power at two-sided alpha 0.05 for its group sizes.

## Family and tests

No hypothesis test is planned beyond the per-unit intervals. If a pooled cell exists, its one test is the family (size = number of pooled cells), BH-controlled.

## What would count against the hypothesis

A pooled cell, or a consistent direction table (3 or more units in one species and class, all significantly higher load in the severe group, with standardised differences above 0.8), would mean load separates outcome well and argues for resistance. Absence of pooled cells is not evidence for tolerance: it is absence of data.
