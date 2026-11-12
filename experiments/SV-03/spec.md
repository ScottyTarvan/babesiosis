# SV-03 spec: severity definition map and marker-evidence matrix

Frozen 2026-11-12 before the analysis script was run. Inputs are published group results only (the SV-G2 extraction); no dog-level outcomes file is opened. All published group comparisons are on the "already seen" list of `rules.md`, so every experiment is `descriptive` in role. Before this spec I looked only at column value counts of `SV-G2/associations_v2.csv` and at the SV-G2 report tables.

## Inputs

- `SV-G2/associations_v2.csv` (740 rows) and `SV-G2/definitions_v2.csv` (78 definitions).
- `/core/cohorts.json` (through the `independent_unit` column of SV-G2) and `/core/articles.jsonl` (country field, streamed).
- SV-07 report (link table) and SV-04 report section 9, for unit merging and the IL-8 conflict.

## Experiments

- `SV-03-01-evidence-matrix` (method `evidence_matrix`): steps 2 to 4 of the package file.
- `SV-03-02-definition-map` (method `evidence_matrix`): step 1.

## Harmonisation

- **Species group** from the row `species` (else `article_species`): *B. rossi* when it names rossi and no other species (includes "presumed B. rossi", flagged); *B. canis* when it names canis (or canis canis) and no rossi, gibsoni or vogeli (the one row "canis canis 44/45, vogeli 1/45" is *B. canis*); *B. gibsoni*; *B. vogeli*; everything else "mixed/unspecified". Never pooled across groups.
- **Sign** relative to the worse outcome: higher_in_severe, more_frequent_in_severe, positive_association = `+`; lower, less_frequent, negative = `-`; no_difference = `0`; mixed and not_stated = `?`.
- **Row call**: significant yes and sign `+` = H; yes and `-` = L; significant no = N; unclear = U; not_tested = D (descriptive). Significant yes with sign `?` = U.
- **Analysis family**: univariable (group_comparison, proportion_comparison, correlation, univariable_regression, roc, survival_analysis) versus multivariable_regression. Multivariable rows are reported in their own column and never combined with univariable rows; descriptive_only rows count as D.
- **Unit call** (per independent unit x marker x outcome class x species group, univariable rows): both H and L present = X (conflict inside the unit); else H if any H; else L if any L; else N if any N; else U; else D. Sensitivity "strict": H or L only if every tested row of that unit in the cell is significant in that direction, else N.
- **Cell** = canonical marker x outcome class x species group. Counts are independent units by unit call.
- **Consistent cell**: at least 2 tested units (H+L+N+X), at least 2/3 of tested units share one significant direction, and no unit has the opposite significant direction.

## Definition map (step 1)

- One row per definition: article, unit, species group, setting, outcome class, components, euthanasia, follow-up, n rows.
- For each component: number of independent units using it, by species group.
- **Marker in definition** (circularity): a row is flagged when its canonical marker belongs to a definition component through a fixed map (renal: creatinine, urea, urine specific gravity, UPC, SDMA, cystatin C, GFR; hepatic or icterus: bilirubin, ALT, ALP, AST, GGT, bile acids; anaemia grade: haematocrit/PCV, haemoglobin, red cell count; hypoglycaemia: glucose; hyperlactataemia: lactate; pancreatitis: cPL and lipase; rhabdomyolysis: CK; coagulopathy: platelets, PT, aPTT, fibrinogen, D-dimer; haemoconcentration: haematocrit; SIRS: WBC, temperature, heart and respiratory rate; collapse: collapse), or when the outcome class is anaemia_grade (red cell markers) or parasitaemia_level (parasitaemia), or when a marker keyword appears in the definition text. Report how often a tested marker is part of its own definition (share of tested rows and of units).
- A matrix cell is "circular" if any of its units has a flagged row. Sensitivity: counts without the flagged units.

## Pooling (step 3)

- Only cells with 3 or more independent units of one species group, one outcome class and one usable summary kind:
  - SMD: univariable group comparisons with n per group and both group values parsable as mean and SD, mean and SEM, median and IQR, or median and range. Medians are converted with Wan et al. 2014 (doi:10.1186/1471-2288-14-135). Hedges g, positive = higher in severe.
  - Correlation: r or rho with n, Fisher z.
  - log OR from 2x2 counts (count and percent).
- One estimate per unit per cell: the row with the earliest timepoint (sample_timing "before treatment" first, then row order), ties broken by larger n.
- Random effects, REML tau-squared, Hartung-Knapp-Sidik-Jonkman 95% interval; DerSimonian-Laird reported beside it; I-squared; a prediction interval when k >= 3.
- Never pool multivariable with univariable effects, or across species. Everything else stays in the direction table.

## Named conflicts (step 4)

IL-8, fibrinogen, aPTT, MDA, SOD and catalase, parasitaemia, platelets against death, lactate. For each: the unit calls by species and outcome class, with definition, timing and setting. Verdict rule, applied in this order:
1. No two units with opposite significant directions in the extraction: "no conflict in the extracted evidence" (state what the conflict rests on, for example an abstract-only article that was not extracted).
2. Opposite directions only across species groups: "aliased with species" (cannot be attributed to species, rule 6).
3. Opposite directions only across outcome classes, or one side circular: "explained by definition".
4. Opposite directions only across sample timing: "explained by timing".
5. Otherwise "unresolved".

IL-8: also weigh CB037 (abstract only, not extracted) against CB517 (CH03), as SV-04 asked. MCP-1 is reported as a candidate cell.

## Sensitivity sets

- S1 Onderstepoort collapse: all natural-infection *B. rossi* units from Onderstepoort or a South African academic hospital (CH03, CB040, CB035, CB053, CB112, CB125, CB342, CB376, CB418, CH29, CH31, CH04) counted as one unit, because of the overlaps in SV-G2 section 6 and SV-07 (DS04 shares dogs with S-CB050; DS07 numbers probably follow DS04).
- S2 judgement calls and translations removed: CB105, CB045, CB098, CB441, CB418 (flagged definitions) and CB187, CB537 (machine translations).
- S3 strict unit rule (above).
- S4 circular units removed.
- Abstract-only sensitivity: SV-G2 extracted no abstract-only article, so this set is empty; reported as a deviation from the package text.

## Selective reporting check

Share of tested rows that are not significant, by article and by unit. Articles with tested rows but 0% not significant are listed. Funnel-type tests are not done (too few units per cell).

## What counts against the hypothesis that markers hold up

If no cell outside circular definitions is consistent in 3 or more independent units of one species, the answer is that no marker holds up across independent cohorts; a consistent cell that disappears under S1 is a single-source finding.

## Tests

No hypothesis test. `n_tests` = number of pooled estimates.
