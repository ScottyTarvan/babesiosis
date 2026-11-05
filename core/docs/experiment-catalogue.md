# Experiment catalogue: classical statistics over the review's data

Candidate experiments that can be run over the data already in this repository with classical statistics and descriptive analysis. Machine learning (predictive models, classifiers, subject clustering, cross-validated feature selection) is out of scope here and is planned separately in `docs/ml-experiment-plan.html` and `experiment_specs/`. Paths are relative to `core/`. Written 2026-11-05 from `datasets.jsonl`, `data/inspection/`, `data/tidy/DS05.json`, `data/experiments/EXP01-DS05-pairwise.json`, `articles.jsonl`, `cohorts.json`, `data/severity/associations.csv` and `data/terms/`. Nothing was run.

## Read this first

**Codes.** Codes follow the brief: `EXP02` onward, in the form `EXP##-<dataset or ARTICLES>-<method>`. The ML plan's index in `experiment_specs/README.md` also reserves `EXP02` to `EXP15` for its own specs (none of those spec files exist yet). `dbo.experiment.experiment_code` must be unique, so whoever merges the two plans must renumber one series; the simplest is to move the ML set to `EXP40` onward, since this catalogue uses `EXP02` to `EXP34`. Dataset tokens used here: a dataset code with the hyphen dropped (`SCB050` for S-CB050), `SRCA`/`SRCB` for the source group when a run joins its datasets, `POOL` for a harmonised cross-cohort table, `SEV` for `data/severity/`, `ARTICLES` for the article table.

**Files the brief names that are not in this checkout.** `data/syndromes/` (`article_concepts.csv`, `concept_summary.csv`, `article_categories.csv`, `mentions.jsonl`) does not exist here on 2026-11-05. What does exist: `data/terms/<ID>.json` for all 481 articles (one entry per UMLS disorder concept with mentions per section, affirmed and negated counts, and the article's `source_format`), `data/terms/term_display.csv` (1,215 curated rows), and `articles.jsonl`, which carries both the NLP categories (`primary_category`, `secondary_tags`, `category_confidence`) and the agents' labels (`agent_primary_category`, `agent_secondary_tags`). Every literature experiment below is specified against the files that exist; where `article_concepts.csv` would be better, it says so.

**Shapes every proposal reuses.** A tidy file is `data/tidy/<code>.json` with `dataset`, `variables[]` (code, name, unit, `data_type` N/O/C/D/T, `domain`, `derived`, `derived_from`, `include_default`, `ref_low`, `ref_high`, `levels`), `subjects[]` (`code`, `group_label`, `outcome_label`) and long `observations[]` (`subject`, `variable`, `time_point`, `value_num`, `value_text`, `value_date`). An experiment file is `data/experiments/<code>.json` with `experiment` (code, name, method, dataset, `parameters` with `seed`, script, `script_version`, counts, `summary`), `associations[]`, `cluster_assignments[]` (always empty here) and `results[]` (`kind`, `title`, `sort_order`, `payload`). Every run writes an `interpretation` result (`{"sections":[{"heading","paragraphs"}]}`) and a `run_notes` result. The web app has a dedicated view only for `method = pairwise_association` (kinds `spearman_matrix`, `variable_clusters`, `top_associations`); any other method shows the interpretation note plus formatted JSON for each result until a view is written. Literature runs set `experiment.dataset = null`.

**Statistical house rules applied throughout.** Rank-based or exact tests; p values by permutation with the unit of resampling stated (dog, or dog-day within dog, or article/cohort); Benjamini-Hochberg across the whole run; an effect size with a bootstrap interval next to every p value (Spearman rho, Cliff's delta, Hodges-Lehmann shift, epsilon squared, Cramér's V, kappa, log2 median ratio); fixed `seed` in `parameters`; derived variables tested against their arithmetic parents are flagged `trivial`; species is a variable, never pooled silently; article counts are deduplicated by `cohort_id` and dataset evidence by `independent_source`.

**Four generic views would cover almost every new result kind.** Rather than one view per experiment, the app needs: `effect_table` (a ranked list of variable, estimate, interval, p, p_adjusted, drawn as a forest plot, with a volcano toggle when there are hundreds of rows), `grouped_distribution` (per-variable box-and-strip plots by group, with n per group), `matrix_heatmap` (any labelled numeric matrix with optional cell annotations: confusion, evidence, cohort by variable, correlation) and `trajectories` (small multiples of value against time per subject, with group colour and a treatment marker). Each proposal names which of these it writes; a few need a fifth, `paired_change` (slope chart day 1 to day 7 per dog), which is a thin variant of `trajectories`.

## Index, ranked by value over effort

Value: H means it bears on severity, outcome or a published claim; M means structure, reference values or review method; L means descriptive only or a tiny n. Effort: S means a parameter run or a short script over an existing tidy file; M means one tidy script plus one new experiment script; L means a hard tidy step (PDF or docx tables, omics) or a new dependency. Batch letters refer to the shared tidy steps in the next section.

| Rank | Code | Name | Value | Effort | Batch | Priority |
|---|---|---|---|---|---|---|
| 1 | EXP03-SCB050-groups | Admission markers by survival and by infection status, Onderstepoort pooled cohorts | H | M | A | high |
| 2 | EXP02-SCB050-pairwise | Association structure of cytokines, MPXI and neutrophils | M | S (after A) | A | high |
| 3 | EXP10-SCB017-groups | Chemokines and haematology, complicated vs uncomplicated B. canis, day 1 and day 7 | H | M | D | high |
| 4 | EXP27-SEV-matrix | Marker-versus-severity evidence matrix from the pilot extraction | H | S | none | high |
| 5 | EXP06-DS07-abundance | Per-protein differential abundance across control, uncomplicated and complicated | H | L | C | high |
| 6 | EXP07-DS07-agreement | Rerun versus the published 78-protein list | H | S (after C) | C | high |
| 7 | EXP26-ARTICLES-agreement | NLP categories versus the agents' labels | M | S | none | high |
| 8 | EXP11-SCB017-paired | Within-dog change day 1 to day 7 by group | H | S (after D) | D | high |
| 9 | EXP12-DS03-groups | Reticulocyte indices across natural, IMHA, healthy and experimental dogs | M | M | E | medium |
| 10 | EXP13-DS03-adequacy | Regenerative adequacy: ARC against haematocrit by group | H | S (after E) | E | medium |
| 11 | EXP04-SCB517-groups | Survival contrasts with SAA, CRP and full differentials added | H | L | A | medium |
| 12 | EXP05-SRCA-linkage | Are S-CB050 cohort 1 and S-CB517 the same rows? | M | S (after A) | A | medium |
| 13 | EXP24-ARTICLES-trends | Category, species and study-type trends by period, cohort-deduplicated | M | S | none | medium |
| 14 | EXP28-ARTICLES-availability | Data availability by period, journal, country and access | M | S | none | medium |
| 15 | EXP25-ARTICLES-syndromes | Syndromes cited versus studied | M | M | none | medium |
| 16 | EXP19-DS05-habitus | Habitus as a severity proxy | M | S | none (DS05 exists) | medium |
| 17 | EXP22-POOL-haematology | Admission haematology distributions across cohorts and species | M | L | A, D, E + mapping | medium |
| 18 | EXP29-SEV-reanalysis | Do recomputed effects agree with the extracted literature rows? | H | S (after A, C, D) | A, C, D | medium |
| 19 | EXP15-DS02-trajectory | Within-dog time course of the experimental B. rossi infection | M | M | B | medium |
| 20 | EXP16-DS02-onset | Order in which markers depart from baseline | H | S (after B) | B | medium |
| 21 | EXP20-DS05-correspondence | Reproduce the authors' correspondence analysis of derived classes | L | S | none | medium |
| 22 | EXP08-DS07-structure | Protein co-variation within infected dogs | M | S (after C) | C | medium |
| 23 | EXP09-SCB017-pairwise | Day-1 chemokine and haematology structure | M | S (after D) | D | medium |
| 24 | EXP14-DS03-trajectory | Reticulocyte collapse in the five experimental dogs | L | S (after B, E) | B, E | low |
| 25 | EXP34-SCB133-matrix | Does the published B. canis correlation matrix agree with the DS05 matrix? | M | S | none | low |
| 26 | EXP17-DS06-timecourse | Paired day-by-dog transcript changes before treatment | M | L (new dependency) | B | low |
| 27 | EXP18-SRCB-join | Erythroid transcripts against reticulocyte indices on the same dog-days | M | M (after B) | B | low |
| 28 | EXP21-POOL-controls | Healthy-control distributions per dataset, side by side | L | S (after A, D, E) | A, D, E | low |
| 29 | EXP32-SCB071-trend | Urinary metabolites ordered by kidney function | L | M | G | low |
| 30 | EXP31-DS04-reproducibility | Repeat-scoring agreement and zonal gradients in fatal liver pathology | L | M | G | low |
| 31 | EXP30-SCB013-coinfection | PCV and platelets against pathogen status in community dogs | L | M | G | low |
| 32 | EXP33-SRCH-abundance | Targeted serum and salivary metabolite panels, infected vs healthy | L | M | G | low |

Considered and left out, with the reason: DS08 (5 vs 2 dogs with exports, identification-only); S-CB042 (14 dogs with laboratory values, heterogeneous laboratories, no comparator); S-CB516 (15 dogs, two signs present in all, no laboratory values in the files); S-CB106 and S-CB148 (summary tables, no per-dog rows); DS09 beyond a one-line Fisher test (four phosphopeptides, 10 vs 10, detection dominated by parent-protein abundance); S-CB005 (wolves, PCR result only); S-CB476 and the other `summary statistics only` or `protein list only` supplements.

## Shared tidy steps (batch these)

| Batch | Tidy script | Raw input | Produces | Used by |
|---|---|---|---|---|
| A | `tidy_scb050.py`, `tidy_scb517.py`, then `tidy_srca.py` to join them by case ID | S-CB050 `Table_1.DOCX` (one 162-row table, decimal commas); S-CB517 `pone.0150113.s001.pdf` and `.s002.pdf` (PDF tables, need `pdftotext` or pymupdf in `.venv`) | `S-CB050.json`, `S-CB517.json`, `SRCA.json` (one row per dog, columns from both files, `cohort` 1 or 2, `outcome_label` Survived/Died/Control) | EXP02, EXP03, EXP04, EXP05, EXP21, EXP22, EXP29 |
| B | `tidy_ds02.py` (DS02 is a verified superset of DS01; DS01's docx is summary only), extended with the DS03 experimental sheet and the DS06 sample table | DS02 xlsx, 7 data sheets, wide by day; DS03 `Babesia Retics_ Exp infected dissertation.xlsx`; DS06 `GSE167201_raw_counts.txt.gz` and series matrix | `DS02.json` with `time_point` `D-1` to `D8` (`D4.1` kept as its own point, flagged pre-treatment for LD dogs), subjects dog 2 to 6, `group_label` LD/HD; counts matrix left as a separate file reference, not long observations (12,362 genes x 28 would be 346k rows; store a per-sample QC table instead) | EXP14, EXP15, EXP16, EXP17, EXP18 |
| C | `tidy_ds07.py` | DS07 `B_Proteins.txt` (224 master proteins; 55 IS-ratio columns), `sample_list.xlsx` (plex x channel to dog and group), S-CB112 `41598_2023_37312_MOESM1_ESM.xlsx` Table S1 (78 published rows with log2FC and FDR) | `DS07.json`: subjects = 52 dogs with `group_label` control/uncomplicated/complicated, variables = proteins (code = accession, name = gene symbol) on log2 IS-ratio, plus `plex` and `channel` as subject variables; published statistics kept in a side table inside `dataset.notes` or a second tidy file `S-CB112.json` | EXP06, EXP07, EXP08, EXP29 |
| D | `tidy_scb017.py` | S-CB017 `pone.0190474.s001.xlsx`, sheets CYTOKINES and HEMATOLOGY (day encoded by block order; group by ID prefix) | `S-CB017.json`: 47 subjects, `group_label` healthy/uncomplicated/complicated, `time_point` `D01`, `D07` (controls `D01` only), the unexplained `Dead` column stored as `dead_flag_unverified` with `include_default = false` | EXP09, EXP10, EXP11, EXP21, EXP22, EXP29 |
| E | `tidy_ds03.py` | DS03 natural-and-controls and IMHA xlsx files | `DS03.json`: 133 subjects, `group_label` natural cohort 1 / natural cohort 2 / IMHA / healthy; the experimental sheet goes into batch B because those dogs are the DS02 Beagles (see EXP14) | EXP12, EXP13, EXP21, EXP22 |
| F | none | `data/tidy/DS05.json` exists | | EXP19, EXP20, EXP22, EXP34 |
| G | `tidy_scb013.py`, `tidy_ds04.py`, `tidy_scb071.py` (and `_scb091`, `_scb137`, targeted tables only) | per record | one tidy file each | EXP30, EXP31, EXP32, EXP33 |
| Mapping | `canonical_code` on `dbo.variable`, set by the tidy scripts through a shared `scripts/variable_map.json` | | harmonised codes and unit conversions for haematocrit, haemoglobin, WBC, segmented/total/band neutrophils, lymphocytes, monocytes, eosinophils, platelets, albumin, total protein, reticulocyte %, ARC, and the seven shared cytokines | EXP21, EXP22, EXP29 |

New experiment scripts, each reused by several codes: `experiment_groups.py` (group contrasts with effect sizes; EXP03, EXP04, EXP10, EXP12, EXP30, EXP33), `experiment_paired.py` (within-subject change; EXP11, EXP14, EXP15), `experiment_abundance.py` (many features, few groups, blocked permutation; EXP06, EXP32, EXP33, EXP17 with a count-model backend), `experiment_agreement.py` (two labellings or two estimate sets; EXP05, EXP07, EXP26, EXP29, EXP34), `experiment_literature.py` with sub-commands (EXP24, EXP25, EXP28), `experiment_evidence.py` (EXP27), and `experiment_pool.py` (EXP21, EXP22). `experiment_pairwise.py` is reused unchanged for EXP02, EXP08, EXP09 and EXP19.

## Family 1: Onderstepoort B. rossi cohorts (S-CB050, S-CB517; SRC-A; article CB050, CB517; cohort CH03)

These two files describe the same dogs: S-CB050 cohort 1 (cases 1 to 97 and controls 201 to 215) is the S-CB517 cohort, with the same seven cytokines. S-CB050 adds cohort 2 (44 infected, 5 controls, no cytokines), age, weight, sex, MPXI and band neutrophils; S-CB517 adds SAA, CRP, lymphocytes, monocytes and eosinophils. Everything in this family is one source of evidence.

### EXP03-SCB050-groups: admission markers by survival and by infection status

1. **Code and name.** `EXP03-SCB050-groups`, Survival and infection contrasts in the pooled Onderstepoort B. rossi cohorts.
2. **Question.** Which admission markers differ between dogs that died and dogs that survived, and between infected dogs and healthy controls, with what effect size? This is the only verified dataset with a hard outcome, and the article's claim (MPXI higher in non-survivors, MPXI correlated with IL-6 in non-survivors) has never been re-tested at dog level.
3. **Data.** S-CB050 tidy (batch A). Variables: `mpxi`, `wbc`, `seg_neutrophils`, `band_neutrophils`, `il2`, `il6`, `il8`, `il10`, `il18`, `gmcsf`, `mcp1`, `age_months`, `weight_kg`, `sex`. Contrast 1: Died (15) vs Survived (126) among 141 infected; cytokines available for 12 deaths and 85 survivors (cohort 1 only). Contrast 2: infected (141) vs control (20; 15 with cytokines). Exclusions: none beyond structural missingness; MPXI missing in 1, weight in 10, age in 1.
4. **Method.** Per variable: Mann-Whitney with a permutation p value (10,000 label shuffles within cohort, so cohort is a stratum), Cliff's delta and Hodges-Lehmann median shift with percentile-bootstrap 95% intervals (dog-level bootstrap). Sex vs outcome by Fisher's exact test with an odds ratio and exact interval. Age- and weight-adjusted sensitivity: aligned-rank test with age tertile as a second stratum. Cytokines log-transformed for display only; floor values (IL-2 3.4, GM-CSF 9.1, IL-6 3.6) treated as tied minima, which rank tests handle, plus a sensitivity run that dichotomises each floored analyte at detected/undetected and uses Fisher. BH across all tests in the run (both contrasts together, about 30 tests). Unit of resampling: dog.
5. **Outputs.** `effect_table` (one row per variable and contrast: delta, shift, interval, p, p_adjusted, n per group), `grouped_distribution` (box-and-strip per variable by Died/Survived/Control), `interpretation`, `run_notes`. `associations[]` populated with one row per variable x contrast (test `mann_whitney`, estimate Cliff's delta) so the SQL findings query works unchanged.
6. **Caveats.** Fifteen deaths; the outcome includes euthanasia for poor prognosis, so it partly reflects clinician decisions. Two cohorts from different years pooled, cytokines only in cohort 1, so cohort is confounded with assay run and must stay a stratum. Sampling time relative to treatment is not in the file. WBC, segmented and band neutrophils are arithmetic relatives (flag seg + band vs WBC as `trivial` in any pairwise reading).
7. **Effort.** Tidy: yes, `tidy_scb050.py` over `Table_1.DOCX` (decimal commas, non-breaking-space blanks). New script `experiment_groups.py`. New view: `effect_table` and `grouped_distribution`.
8. **Priority: high.** Only hard-outcome dataset, cheap once the docx is tidied, and the groups script is reused by five other experiments.

### EXP02-SCB050-pairwise: association structure of cytokines, MPXI and neutrophils

1. **Code and name.** `EXP02-SCB050-pairwise`, Admission association structure, Onderstepoort pooled cohorts.
2. **Question.** How do the seven cytokines, MPXI, neutrophil counts, age and weight co-vary in infected dogs, and does the structure differ in non-survivors? The article reports MPXI-IL-6 rho 0.615 in non-survivors only; this tests whether that survives multiplicity and whether the whole cytokine block moves together.
3. **Data.** S-CB050 tidy. Infected dogs with cytokines (97), run three ways: all infected, survivors only (85), and with `outcome_label` and `sex` included as categorical variables. Non-survivors alone (12) is too few for a matrix and is reported descriptively only.
4. **Method.** `experiment_pairwise.py` as it stands: Spearman, Kruskal-Wallis/Mann-Whitney, chi-square, permutation p values, BH, trivial flags (seg + band against WBC), average-linkage variable clusters at |rho| >= 0.4. Unit: dog.
5. **Outputs.** The existing kinds `spearman_matrix`, `variable_clusters`, `top_associations`, `interpretation`, `run_notes`. Existing pairwise view renders it.
6. **Caveats.** About a quarter of IL-2 and GM-CSF values sit at the assay floor, which compresses rho; one dog has four ceiling values (50001). Cohort 2 contributes no cytokines, so the matrix is cohort 1 only. Age and weight are missing in 11 dogs.
7. **Effort.** Tidy: shared with EXP03. Script: parameter change only (`--dataset S-CB050 --include ...`). New view: no.
8. **Priority: high**, because it is nearly free once batch A exists and gives the first non-DS05 structure for comparison with EXP01.

### EXP04-SCB517-groups: survival contrasts with SAA, CRP and full differentials

1. **Code and name.** `EXP04-SCB517-groups`, Acute-phase proteins, leukocyte differentials and cytokines by survival, Goddard 2016 cohort.
2. **Question.** Do SAA, CRP, lymphocyte, monocyte and eosinophil counts differ by survival and by infection status, and do the cytokine contrasts reproduce the published ones (IL-6 and MCP-1 higher in non-survivors; IL-10 and MCP-1 higher and IL-8 lower than controls)? Acute-phase proteins are the most widely reported severity markers in the literature and this is the only per-dog SAA/CRP table in the collection.
3. **Data.** S-CB517 tidy (batch A): 97 infected (85 Survived, 12 Died), 15 controls; variables `wbc`, `neut_total`, `lymphocytes`, `monocytes`, `eosinophils`, `saa`, `crp`, seven cytokines. No age, sex or weight.
4. **Method.** Same as EXP03 (groups script), unit dog, BH across the run. Eosinophils are 0.00 in 60 of 97 infected dogs: report eosinopenia as a proportion with a Clopper-Pearson interval and a Fisher test against controls rather than a rank test. Flag the 17 rows where differentials sum to well below WBC in `run_notes` and run a sensitivity excluding them.
5. **Outputs.** As EXP03.
6. **Caveats.** Same dogs as S-CB050 cohort 1 (not a replication). Twelve deaths. No covariates in the file, although the article reports a sex imbalance and a days-sick effect. PDF tables need scripted extraction and a row-count check (97 + 15).
7. **Effort.** Tidy: yes, PDF table extraction (`pdftotext -layout` or pymupdf; add to `requirements-experiments.txt`). Script: groups script. New view: no beyond EXP03.
8. **Priority: medium.** High value but the PDF tidy is the costliest step in batch A, and EXP03 already answers the survival question for the cytokines.

### EXP05-SRCA-linkage: are S-CB050 cohort 1 and S-CB517 the same rows?

1. **Code and name.** `EXP05-SRCA-linkage`, Row-level agreement between the two Onderstepoort supplements.
2. **Question.** Do the seven cytokine values match case for case between S-CB050 cases 1 to 97 and S-CB517, so that the two files can be joined into one 161-dog table with 24 variables? The joined table is the input the pooled experiments need, and the match is asserted in `datasets.jsonl` but not verified.
3. **Data.** Both tidy files; the 97 infected and 15 control rows that should coincide; 7 cytokines.
4. **Method.** Exact-match rate per analyte, Spearman and concordance correlation coefficient per analyte, Bland-Altman limits on log values, and a list of every discordant cell. No p values needed; report mismatches. Also test the ID alignment hypothesis against a shifted alignment (offset by one) to catch an off-by-one in the published table.
5. **Outputs.** `matrix_heatmap` (analyte x statistic) and a discordance table in `run_notes`; `interpretation` states whether `SRCA.json` is safe to build.
6. **Caveats.** The S-CB050 ceiling is 50001 against 50000 in S-CB517, so round before matching. If more than a few cells differ, the join must be by value matching, not by case number.
7. **Effort.** Tidy: shared with batch A. Script: `experiment_agreement.py` (new, small). New view: `matrix_heatmap`.
8. **Priority: medium.** Zero clinical content, but it decides whether the pooled table is honest.

## Family 2: DS07 serum proteome (SRC-C; article CB112; S-CB112 published list)

### EXP06-DS07-abundance: per-protein differential abundance across the three classes

1. **Code and name.** `EXP06-DS07-abundance`, Serum protein abundance in control, uncomplicated and complicated B. rossi babesiosis.
2. **Question.** Which serum proteins differ between the three classes once plex is accounted for, and which differ between complicated and uncomplicated infection specifically, with effect sizes? The published list (78 proteins across groups, 21 between the infected classes) came from a parametric pipeline; a rank-based, plex-blocked rerun with explicit missingness handling tests how stable those calls are.
3. **Data.** DS07 tidy (batch C): 52 dogs (20 control, 18 uncomplicated, 14 complicated); log2 IS-ratio per master protein. Feature filter: proteins observed in at least 39 of 52 samples (131 proteins) as the primary set, at least 26 of 52 (156) as sensitivity. Drop the three unused channels of plex 11.
4. **Method.** Per protein: Kruskal-Wallis across the three classes with permutation p (labels shuffled within plex, 10,000 draws), then the two pairwise contrasts of interest (control vs infected pooled; uncomplicated vs complicated) by Mann-Whitney with plex-stratified permutation. Effect size: log2 ratio of group medians with dog-level bootstrap interval, and Cliff's delta. Missing values stay missing (no imputation); for proteins failing the filter, a detection-frequency Fisher test per contrast is reported in a separate table. BH across all proteins within each contrast family (three families, stated in parameters). Unit of resampling: dog, within plex.
5. **Outputs.** `effect_table` per contrast with volcano toggle (log2 ratio against -log10 p_adjusted), `grouped_distribution` for the top 20 proteins, `matrix_heatmap` of the top 40 proteins by dog ordered by class and plex, `interpretation`, `run_notes` (filter counts, plex layout check). `associations[]` written with `variable_a` = protein, `variable_b` = `group` so the SQL findings path works.
6. **Caveats.** The complicated label is defined partly by haematocrit, urea, creatinine, bilirubin, glucose and lactate, none of which are in the files, so proteins that track haemolysis or renal injury (haemoglobin subunits, haptoglobin, hemopexin) partly restate the label; name them as such in the interpretation. Missingness is plex-structured and abundance-dependent (MNAR). Fourteen complicated dogs against 131 proteins: expect few survivors of BH in the infected-class contrast, and say so beforehand. Treatment and sampling time are unknown.
7. **Effort.** Tidy: yes, the plex x channel to dog join from `sample_list.xlsx` is the fiddly part (channel 126 is the internal standard, not a control dog). Script: `experiment_abundance.py` (new). New view: volcano toggle on `effect_table`, `matrix_heatmap`.
8. **Priority: high.** The only severity-labelled omics table, and the published result is directly testable.

### EXP07-DS07-agreement: rerun versus the published 78-protein list

1. **Code and name.** `EXP07-DS07-agreement`, Agreement between EXP06 and Supplementary Table S1 of CB112.
2. **Question.** How many of the 78 published differential proteins (and the 21 infected-class proteins) are recovered by the rank-based rerun, and do the directions and magnitudes agree? Marker lists that depend on the pipeline should not be carried into the review as settled.
3. **Data.** EXP06 output and `S-CB112` Table S1 (78 rows: accession, gene, p, FDR, log2FC for A/B, A/C, B/C). Join on accession.
4. **Method.** Overlap counts with the hypergeometric expectation, Cohen's kappa on the significant/not call per protein per contrast (over the proteins tested by both), Spearman and concordance correlation between published log2FC and the rerun's log2 median ratio per contrast, sign agreement rate with an exact binomial interval. List proteins called by one analysis only.
5. **Outputs.** `effect_table`-style scatter data (published vs rerun estimate per contrast), `matrix_heatmap` of the kappa and overlap statistics, `interpretation`, `run_notes`.
6. **Caveats.** The published analysis used different filtering and a parametric moderated test, so disagreement is expected at the margin and is not an error in either. Accessions in Table S1 may include non-master isoforms; map through gene symbol as a fallback and report how many needed it.
7. **Effort.** Tidy: shared with batch C (Table S1 read in the same script). Script: `experiment_agreement.py`. New view: `matrix_heatmap` (shared).
8. **Priority: high**, as the natural companion to EXP06 and almost free once it exists.

### EXP08-DS07-structure: protein co-variation within infected dogs

1. **Code and name.** `EXP08-DS07-structure`, Which serum proteins move together in infected dogs.
2. **Question.** Do the acute-phase, lipoprotein, complement and coagulation proteins form the blocks the article's pathway annotation implies, when correlation is computed within the 32 infected dogs rather than driven by the control contrast?
3. **Data.** DS07 tidy, infected dogs only (32), the 60 most variable proteins among those observed in at least 26 of 32 infected samples.
4. **Method.** `experiment_pairwise.py` with `--include` set to those proteins (Spearman, permutation, BH, average-linkage clusters). Unit: dog.
5. **Outputs.** Existing kinds (`spearman_matrix`, `variable_clusters`, `top_associations`); existing view.
6. **Caveats.** 60 proteins give 1,770 pairs in 32 dogs; after BH only strong correlations survive, and the clusters are descriptive. TMT ratio compression flattens correlations. Plex is not removable inside a pairwise run; report the plex-balanced design in the notes.
7. **Effort.** Tidy: shared. Script: parameter change. New view: no.
8. **Priority: medium.**

## Family 3: S-CB017 B. canis cytokines and haematology at two time points (SRC-D; article CB017; cohort CH23)

### EXP10-SCB017-groups: complicated vs uncomplicated at day 1 and at day 7

1. **Code and name.** `EXP10-SCB017-groups`, Chemokines and haematology by complication status, B. canis, day 1 and day 7.
2. **Question.** Do day-1 MCP-1 and KC-like separate complicated from uncomplicated dogs as published (MCP-1 p = 0.00016, AUC 0.906), what are the effect sizes with intervals, and do the haematology variables that help define the label (WBC) dominate the contrast? MCP-1 is the one chemokine reported as a severity marker in both B. canis (this cohort) and B. rossi (SRC-A), so a dog-level effect size here is the B. canis half of that comparison.
3. **Data.** S-CB017 tidy (batch D). Day 1: 18 complicated vs 13 uncomplicated; day 7: 17 vs 13; healthy 16 (single sample). Nine cytokines and 16 haematology variables (drop the percentage differentials as arithmetic relatives of the absolute counts, or flag trivial).
4. **Method.** Groups script: Mann-Whitney with permutation p, Cliff's delta, Hodges-Lehmann shift with bootstrap intervals; infected vs healthy as a second contrast family at day 1 only. Floored analytes (IL-10 at 0.8 in 45 of 77 rows, IL-18, IL-2, IL-15) get the detected/undetected Fisher sensitivity. Day 1 is the primary family; day 7 is secondary and labelled post-treatment. BH within family. Unit: dog (day 1 and day 7 analysed as separate families, never pooled as 61 rows).
5. **Outputs.** `effect_table`, `grouped_distribution`, `interpretation`, `run_notes`; `associations[]` populated.
6. **Caveats.** Complication was defined by WHO malaria-style criteria including SIRS, of which WBC is a component, so WBC and possibly band neutrophils partly restate the label. Cytokine draws were 6 to 8 hours after imidocarb and 8 of the 16 healthy dogs apparently had prophylactic imidocarb. Day labelling in the cytokine sheet is by block order only; the tidy script must check the block sizes (31 then 30) and the medians against the article. Four haematology cells look like entry errors (BK9 erythrocytes 35, B2 day-7 segmented neutrophils 42) and should be set missing with a note.
7. **Effort.** Tidy: yes, `tidy_scb017.py` (two sheets, group from ID prefix, day from block order). Script: groups script. New view: as EXP03.
8. **Priority: high.** Direct replication of a published severity claim in the second species, cheap tidy.

### EXP11-SCB017-paired: within-dog change day 1 to day 7 by group

1. **Code and name.** `EXP11-SCB017-paired`, Paired change in chemokines and leukocytes over the first week, by complication status.
2. **Question.** Which analytes change within dogs between presentation and day 7, does the change differ between complicated and uncomplicated dogs, and does the published IL-8 rise in uncomplicated dogs hold with a paired test and an interval?
3. **Data.** S-CB017 tidy; 30 dogs with both days (13 uncomplicated, 17 complicated); 9 cytokines and the absolute haematology counts.
4. **Method.** Per analyte: Wilcoxon signed-rank with an exact p (n = 13 and 17 permit exact enumeration) or sign-flip permutation, Hodges-Lehmann paired shift with bootstrap interval, within each group; group difference in change by Mann-Whitney on the within-dog differences with permutation p and Cliff's delta. BH across analytes within each of the three families. Unit: dog (the pair is the unit; sign flips within dog).
5. **Outputs.** `paired_change` (slope chart per analyte: day 1 to day 7 per dog, coloured by group) and `effect_table`; `interpretation`; `run_notes`.
6. **Caveats.** Every dog was treated, so change is treatment plus recovery, not natural history. The one death (BK11) is informative dropout. Floored analytes produce many zero differences; report the number of ties and use the exact test that handles them.
7. **Effort.** Tidy: shared with EXP10. Script: `experiment_paired.py` (new, small; also used by EXP14 and EXP15). New view: `paired_change`.
8. **Priority: high**, because it is the only natural-infection repeated-measures table and the script is reused.

### EXP09-SCB017-pairwise: day-1 chemokine and haematology structure

1. **Code and name.** `EXP09-SCB017-pairwise`, Cross-sectional structure of chemokines and haematology in B. canis at presentation.
2. **Question.** How do KC-like, IL-8 and MCP-1 relate to anaemia, thrombocytopenia, left shift and leukocyte counts at day 1, and does the published inverse IL-8 to erythrocyte correlation in uncomplicated dogs survive BH?
3. **Data.** S-CB017 tidy, day-1 rows of the 31 infected dogs, 9 cytokines plus absolute haematology counts and `group_label` as a categorical variable.
4. **Method.** `experiment_pairwise.py`, parameters only; a second run on the 16 healthy dogs if `min_n` is lowered to 16 (state it). Unit: dog.
5. **Outputs.** Existing kinds and view.
6. **Caveats.** Thirty-one dogs for about 300 pairs; expect few findings after BH. Percentage and absolute differentials are arithmetic relatives: include only the absolute counts. Group membership is itself associated with WBC by definition.
7. **Effort.** Tidy: shared. Script: parameter change. New view: no.
8. **Priority: medium.**

## Family 4: DS03 reticulocyte indices (SRC-E; article CB115)

Note found while cataloguing: the DS03 experimental sheet is the DS01/DS02 Beagle experiment. Experimental cases 1 to 5 match DS02 dogs 2 to 6 cell for cell on haemoglobin and haematocrit for Day 1 to Day 6 (checked read-only on 2026-11-05: 58 of 59 populated cells identical, the one difference being case 5 Day 3 haemoglobin 120 against dog 6 day 3 Hb 118; day 4.1 is skipped), and case 5 stops at Day 4 as dog 6 died on day 4. So DS03 "Day k" is day k after inoculation, the experimental part of DS03 belongs to source group SRC-B rather than SRC-E, and the reticulocyte indices can be joined to the DS02 cytokine series at dog-day level. The tidy script for batch B should record this and `datasets.jsonl` should be corrected in a later pass (not part of this catalogue).

### EXP12-DS03-groups: reticulocyte indices across natural, IMHA, healthy and experimental dogs

1. **Code and name.** `EXP12-DS03-groups`, Reticulocyte count and indices by disease group.
2. **Question.** Do ARC, Ret%, MCVr, CHr, CHCMr, CHDWr, RDWr and CHDelta differ between natural B. rossi, IMHA and healthy dogs after allowing for age and sex, and are the two natural cohorts alike? The article's conclusion that the B. rossi response is inadequate rests on these comparisons at n = 10 IMHA; the file has 16.
3. **Data.** DS03 tidy (batch E): natural cohort 1 (85), natural cohort 2 (18), IMHA (16), healthy (14); 12 variables plus age, weight, sex. Exclude the flagged implausible values (IMHA MCHC up to 478, BC24 RDWr 1.6) by setting them missing with a note.
4. **Method.** Kruskal-Wallis across the four groups with permutation p and epsilon squared; pairwise Mann-Whitney with Cliff's delta and bootstrap intervals for the three contrasts of interest (B. rossi vs IMHA, B. rossi vs healthy, cohort 1 vs cohort 2). Age confounding (controls median 56 months, cases 11 to 19): aligned-rank ANCOVA on age and sex, and a restricted analysis to dogs under 36 months, both as sensitivity. BH across the index family. Unit: dog.
5. **Outputs.** `effect_table`, `grouped_distribution`, `interpretation`, `run_notes`.
6. **Caveats.** The indices are collinear and partly derived from each other (ARC from Ret% and RBC; CHDelta from CHr), so count the family honestly and flag derived pairs. Controls are older and mostly female. Prior treatment and transfusion are not recorded; IMHA dogs may be on immunosuppressants. The IMHA n (16) differs from the article (10), so numbers will not reproduce exactly.
7. **Effort.** Tidy: yes, `tidy_ds03.py` (three sheets with a cohort header row to parse). Script: groups script. New view: as EXP03.
8. **Priority: medium.**

### EXP13-DS03-adequacy: regenerative adequacy, ARC against haematocrit by group

1. **Code and name.** `EXP13-DS03-adequacy`, Does ARC rise with falling haematocrit equally in B. rossi and IMHA?
2. **Question.** Is the slope of log ARC on haematocrit flatter in B. rossi than in IMHA, which is the quantitative form of "inadequate regenerative response"? This is the mechanistic question behind the article and it has not been tested as an interaction.
3. **Data.** DS03 tidy, natural B. rossi (103) and IMHA (16), plus healthy (14) as the reference band; variables `arc`, `reticulocyte_pct`, `haematocrit`, `chr`, `mcvr`, with age.
4. **Method.** Within-group Spearman of log ARC on haematocrit with bootstrap interval; the group difference in relationship by a permutation test of the group x haematocrit interaction in a rank-based linear model (ranks of log ARC on haematocrit, group, interaction; shuffle group labels 10,000 times within haematocrit tertile). Repeat for Ret% and CHr. Also classify each dog as above or below the expected ARC for its haematocrit using the IMHA line, and report the proportion of B. rossi dogs below it with an exact interval. Unit: dog.
5. **Outputs.** New payload for a `scatter_by_group` view (x, y, group per dog, fitted rank-regression lines) and `effect_table`; `interpretation`; `run_notes`. If the app prefers not to add a view, the scatter can be rendered from `grouped_distribution` binned by haematocrit class.
6. **Caveats.** Sixteen IMHA dogs anchor the comparison line, so the interaction test has little power and the interval will be wide. Time since onset differs between diseases (IMHA is often subacute), which alone can produce a flatter B. rossi slope. ARC is computed from Ret% and RBC, and haematocrit co-varies with RBC, so some of the correlation is arithmetic; report the Ret% version alongside.
7. **Effort.** Tidy: shared. Script: small addition to the groups script or a short dedicated script. New view: `scatter_by_group` (optional).
8. **Priority: medium**, high scientific interest for the ERY category but limited by the IMHA n.

### EXP14-DS03-trajectory: reticulocyte collapse in the five experimental dogs

1. **Code and name.** `EXP14-DS03-trajectory`, ARC and reticulocyte indices over six days of experimental B. rossi infection.
2. **Question.** Does ARC rise and then fall about 48 hours after parasitaemia in every dog, and what is the per-dog magnitude? Descriptive kinetics only.
3. **Data.** Batch B tidy (the DS03 experimental sheet joined to DS02 dog-days): 5 dogs, days 1 to 6, 12 variables; 4 dogs with complete series.
4. **Method.** Per-dog trajectories, Friedman test across days per variable with exact or permutation p (within-dog permutations of day labels), and median change from day 1 per day with a range. No dose contrast (2 vs 3). Unit: dog-day permuted within dog.
5. **Outputs.** `trajectories`, `interpretation`, `run_notes`.
6. **Caveats.** Five dogs, treatment on day 4 or 4.1, dog 6 died on day 4 (informative dropout). Parasitaemia for the alignment comes from DS02.
7. **Effort.** Tidy: batch B. Script: `experiment_paired.py` Friedman mode. New view: `trajectories`.
8. **Priority: low** on its own; run as part of EXP15.

## Family 5: experimental infection time course (DS01, DS02, DS06; SRC-B; articles CB098, CB101, CB082; cohort CH09)

DS02 contains every numeric cell of DS01 plus about 700 more, so DS02 is the tidy source and DS01's workbook is not read; DS01's docx is used only to check units and scale definitions. Five infected dogs: low dose dogs 2 and 3, high dose dogs 4, 5 and 6 (dog 6 died on day 4). Treatment at 96 h (HD) and 108 h (LD, the "4.1" column). Days 5 to 8 are post-treatment.

### EXP15-DS02-trajectory: within-dog time course of the experimental infection

1. **Code and name.** `EXP15-DS02-trajectory`, Clinical, haematological, acute-phase and cytokine trajectories in five Beagles.
2. **Question.** For each of about 50 variables, when does it depart from its own baseline and by how much, before treatment, and how does the post-treatment surge look? This is the only dataset in which the sequence of host responses is observable rather than inferred from admission snapshots.
3. **Data.** DS02 tidy (batch B): dogs 2 to 6; baseline = days -1 and 0 (noting the day-0 leukocytosis artefact, so use day -1 as the primary baseline and the mean as sensitivity); pre-treatment days 1 to 4 (4.1 for LD); post-treatment days 5 to 8. Variables: clinical (habitus, appetite, temperature, pulse, respiratory rate, MAP), haematology (Hb, HCT, RCC, platelets, WCC, segmented and band neutrophils, lymphocytes, monocytes, reticulocytes, NRBC), biochemistry (CRP, albumin, lactate, glucose), parasitaemia, cell-free haemoglobin, 13 cytokines. Exclude the flagged dog 2 day-7 monocyte entry and treat dog 5 day 6 and 8 cytokines as suspect (sensitivity run without them).
4. **Method.** Per variable: change from baseline per dog per day; a sign-flip permutation test of the median change at each pre-treatment day (five dogs give 32 sign patterns, so the smallest two-sided p is 1/16: report it as such and lean on the effect size); Friedman across pre-treatment days; and a linear mixed model with a random intercept per dog and day as a factor, reported as estimates with profile intervals and no p values (numpy implementation of the REML or a simple two-stage summary; state which). Dose contrast descriptive only (2 vs 3). BH across variables for the Friedman family only. Unit: dog; permutations within dog.
5. **Outputs.** `trajectories` (small multiples per variable, dogs as lines, LD/HD colour, treatment marker per dog, reference range band from `ref_low`/`ref_high` where the sheet gives one), `effect_table` of median change at day 3 and day 4 per variable, `interpretation`, `run_notes`.
6. **Caveats.** Humane endpoints were defined by haematocrit and habitus, so treatment timing is a function of two of the variables under study. Everything after day 4 is treatment plus disease. Cytokine zeros are detection-limit substitutions. The HD dose label disagrees between the file (10^9) and the article (10^8). Dog identity and dose are confounded.
7. **Effort.** Tidy: yes, `tidy_ds02.py` (wide columns `Hb-1`, `Hb0`, ... `Hb8` across seven sheets into long form with `time_point`; abbreviation keys recovered from DS01's block names and the docx). Script: `experiment_paired.py` time-course mode. New view: `trajectories`.
8. **Priority: medium.** High descriptive value for the INF and ERY categories, but n = 5 limits every inference to effect sizes.

### EXP16-DS02-onset: the order in which markers depart from baseline

1. **Code and name.** `EXP16-DS02-onset`, Temporal ordering of host responses relative to parasitaemia.
2. **Question.** In what order do CRP, band neutrophils, monocytes, individual cytokines, temperature, haematocrit, lactate and MAP first leave the dog's own baseline, is that order the same in every dog, and where does first detectable parasitaemia sit in it? The article (CB098) states that inflammation preceded clinical disease; this makes the ordering explicit and tests its consistency.
3. **Data.** DS02 tidy, pre-treatment days only (days -1 to 4, 4.1), dogs 2 to 6, about 30 variables with at least a day -1 baseline.
4. **Method.** Per dog and variable, onset day = first day the value exceeds the baseline by more than a stated threshold (for variables with a reference range, outside it; otherwise more than 2 times the between-baseline-day difference, or a log2 fold change of 1 for cytokines; thresholds in `parameters`, sensitivity over two settings). Rank variables by onset within each dog; consistency across dogs by Kendall's W with a permutation p (shuffle variable labels within dog). Report the median onset rank per variable with the range across dogs, and the lag from first parasitaemia. Unit: dog.
5. **Outputs.** New payload `onset_order` (variable x dog onset-day matrix, drawable with `matrix_heatmap`, plus a ranked list drawable with `effect_table`), `interpretation`, `run_notes`.
6. **Caveats.** Sampling is daily, so ties are frequent and the ordering is coarse. Cytokines are sampled on fewer days than the clinical variables. Detection-limit substitution makes the cytokine baseline artificially stable, which biases onset early. Five dogs; W is descriptive.
7. **Effort.** Tidy: shared with EXP15. Script: small, after EXP15. New view: none beyond `matrix_heatmap`.
8. **Priority: medium**, high interest per unit of effort once batch B exists.

### EXP17-DS06-timecourse: paired day-by-dog transcript changes before treatment

1. **Code and name.** `EXP17-DS06-timecourse`, Whole-blood transcriptome change from day 0 to day 1 and day 3, within dog.
2. **Question.** Which genes and gene sets change within dogs on day 1 and day 3 after inoculation, before treatment, and how much of the apparent change is erythroid and reticulocyte composition rather than leukocyte transcription? The article's pathway claims (haemolytic, metabolic, interferon and antiviral) came from a design that did not isolate pre-treatment days.
3. **Data.** DS06 counts: 12,362 genes x 28 samples; pre-treatment contrasts D1 vs D0 and D3 vs D0 in the five dogs that have them (low_1, low_2, high_1, high_2, high_3), so five pairs each. D4 is ambiguous (treatment day) and D6/D8 post-treatment: secondary. Library sizes collapse at D3 and D4 in the high-dose dogs (down to 0.8 million), so a sample QC table comes first.
4. **Method.** Rank-based per-gene tests cannot work here (five pairs give a smallest exact p of 1/16, so no gene can pass BH), so this experiment needs a parametric moderated count model: pyDESeq2 (add to `requirements-experiments.txt`, run in `.venv-nlp`) with design `~ dog + day`, contrasts D1 vs D0 and D3 vs D0, BH per contrast; TMM-style normalisation checked against DESeq2's size factors; an erythroid composition score (ALAS2, HBB, HBA, SLC4A1 and similar, from the symbol column) added as a covariate in a sensitivity model and used to label composition-driven genes. Gene-set level: a competitive rank test (camera-like, with inter-gene correlation estimated from the data) on interferon, erythroid, neutrophil and complement sets; curated set definitions stored in `parameters`. Unit of resampling: dog (the model's pairing); no sample-level permutation.
5. **Outputs.** `effect_table` per contrast with volcano toggle (log2 fold change, s.e., p_adjusted), a per-sample QC table (library size, erythroid score, zero fraction) drawable with `matrix_heatmap`, gene-set `effect_table`, `interpretation`, `run_notes`. `experiment.dataset` = DS06 but `associations[]` left empty (the gene list would be 12k rows; keep it in the result payload capped to the top 500 by adjusted p).
6. **Caveats.** Five dogs; dog and dose are nested so dose cannot be estimated. The D3 and D4 library collapse is a composition and technical effect; results that vanish when the erythroid score is a covariate are composition, not transcription. The GEO metadata has errors (species mapping text, dog counts). Samples within dog are not independent; the design handles it, cross-validation would not.
7. **Effort.** Tidy: QC table in batch B; counts stay in the raw file. Script: `experiment_abundance.py` with a count-model backend. New dependency: pyDESeq2. New view: shared `effect_table`.
8. **Priority: low** relative to effort, because only the day-1 and day-3 contrasts are clean and the dependency is heavy; worth doing after the natural-infection experiments.

### EXP18-SRCB-join: erythroid transcripts against reticulocyte indices on the same dog-days

1. **Code and name.** `EXP18-SRCB-join`, Cross-layer check of composition: transcriptome erythroid score, reticulocyte indices and haematocrit.
2. **Question.** On matched dog-days, does the whole-blood erythroid transcript score track the measured reticulocyte percentage and ARC (DS03 experimental sheet, DS02), which would confirm that the D3/D4 transcriptome shift is reticulocytosis? A composition confirmation makes the DS06 pathway claims readable.
3. **Data.** Batch B joined table: dog-days with a DS06 sample and DS02/DS03 haematology (D0, D1, D3, D4, D6, D8 for four dogs; D0, D1, D3 for the dog that died). About 27 dog-days from five dogs.
4. **Method.** Repeated-measures correlation (within-dog centring, Bland and Altman 1995) between erythroid score and Ret%, ARC, HCT, Hb, with a permutation p that shuffles days within dog; per-dog Spearman as a check. Unit: dog-day within dog.
5. **Outputs.** `scatter_by_group` (dog as group) or `trajectories` overlay; `effect_table`; `interpretation`; `run_notes`.
6. **Caveats.** The DS06 sample labels (`low_1`, `high_2`) are not mapped to DS02 dog numbers; `high_3` is dog 6 (died) and `low_0` is probably the donor, but low_1/low_2 and high_1/high_2 are ambiguous and must be resolved by matching the erythroid score to the Hb trajectory, which is circular for this experiment unless the mapping is confirmed from the authors. State the mapping as an assumption in `parameters`.
7. **Effort.** Tidy: batch B. Script: small. New view: none.
8. **Priority: low**, conditional on EXP17 and the dog mapping.

## Family 6: DS05 extensions (SRC-F; article CB126; tidy file exists)

### EXP19-DS05-habitus: habitus as a severity proxy

1. **Code and name.** `EXP19-DS05-habitus`, Admission variables across habitus classes.
2. **Question.** Which laboratory and clinical variables trend monotonically across the authors' three habitus classes (bright/alert, mildly depressed, depressed/collapsed), and how large are the differences between the extreme classes? DS05 has no outcome; habitus is the nearest thing to a clinician severity judgement in it, and EXP01 only reported its Spearman rho with each numeric variable.
3. **Data.** `DS05.json`: `habitus_class` (10 / 47 / 93) or `habitus_score` as ordered groups; the 28 numeric default variables and the 11 categorical ones. n = 150 (148 with CBC, 144 with proteins).
4. **Method.** Jonckheere-Terpstra trend test by permutation per numeric variable; Cliff's delta between the extreme classes with bootstrap interval; chi-square with Cramér's V and permutation p for categorical variables (mucous membranes, panting, complaints); BH across the run. Flag `anaemia_class` and the other derived classes as trivial against their parents. Unit: dog.
5. **Outputs.** `effect_table`, `grouped_distribution` (three habitus classes), `interpretation`, `run_notes`.
6. **Caveats.** Habitus is scored by the same clinician at the same examination as pale and icteric mucous membranes, pulse and temperature, so those associations are not independent observations. Only 10 dogs in the bright class. No treatment or outcome, so nothing here is prognostic.
7. **Effort.** Tidy: no. Script: groups script in trend mode. New view: as EXP03.
8. **Priority: medium**, cheap and the only severity-flavoured reading DS05 can give.

### EXP20-DS05-correspondence: reproduce the authors' correspondence analysis of the derived classes

1. **Code and name.** `EXP20-DS05-correspondence`, Multiple correspondence analysis of the CORRESPONDENCE-sheet categories.
2. **Question.** Do the authors' categorical classes (anaemia grade, WCC class, band class, left shift, monocyte class, ARC classes, globulin class, age, illness duration, breed group, habitus) arrange along the same axes the article describes, and how much inertia do the first two axes carry? A reproduction with a stated method and intervals, and a check that the picture is not an artefact of categorising continuous variables.
3. **Data.** `DS05.json`, the 13 `derived = true` class variables plus `season`, `sex`, `mm_pale`, `mm_icteric`; 150 dogs.
4. **Method.** Multiple correspondence analysis (indicator matrix SVD, numpy), Benzécri-corrected inertia, category coordinates and contributions, bootstrap intervals on the first two axes by resampling dogs; a parallel run on the continuous parents (PCA on ranks) to show how much structure survives categorisation. Pairwise chi-square with Cramér's V among the classes, with parent-child pairs flagged trivial. Unit: dog.
5. **Outputs.** New payload `ca_biplot` (category coordinates, contributions, inertia per axis) and `matrix_heatmap` of Cramér's V; `interpretation`; `run_notes`.
6. **Caveats.** Every class is a cut of a measured variable already in EXP01, so the axes largely restate the EXP01 clusters (red cell mass, left shift, regenerative response). `arc_class` and `arc_class_2` are two cuts of the same variable. Descriptive; no p values are meaningful for the axes themselves.
7. **Effort.** Tidy: no. Script: new, small. New view: `ca_biplot` (or export coordinates and skip the view).
8. **Priority: medium-low**, included because the brief asks for the derived classes and it closes the loop with the article.

## Family 7: cross-dataset questions that need only harmonised codes

### EXP22-POOL-haematology: admission haematology distributions across cohorts and species

1. **Code and name.** `EXP22-POOL-haematology`, Haematocrit, leukocyte and platelet distributions across the individual-level cohorts.
2. **Question.** How do admission haematocrit, white cell count, neutrophils, lymphocytes, monocytes, eosinophils and platelets compare between the B. rossi cohorts (DS05 Eastern Cape, SRC-A Onderstepoort, DS03 Onderstepoort), the B. canis cohorts (S-CB017 Zagreb, DS09/S-CB019 Zagreb) and the B. vogeli field dogs (S-CB013), and are the cohort differences larger than the species differences? Admission haematology is the most widely reported evidence in the literature and these are the only per-dog distributions available to anchor it.
3. **Data.** One tidy file per cohort with `canonical_code` set: DS05 (148 B. rossi), SRCA (141 B. rossi, use one copy of the duplicated dogs), DS03 natural (103, haematocrit and reticulocytes only), S-CB017 day 1 (31 B. canis), S-CB019 S1 (10 B. canis, after fixing the unit mismatch in its differentials), S-CB013 (7 B. vogeli positives; 89 negatives as a field reference). Variable mapping needed: haematocrit (L/L; S-CB017 HMT % divided by 100; S-CB013 PCV L/L), WBC (x10^9/L everywhere), neutrophils (DS05 segmented and band separately; S-CB050 segmented and band; S-CB517 total NEUT, definition unknown; S-CB017 segmented and non-segmented), lymphocytes, monocytes, eosinophils, platelets (absent from SRC-A), albumin and total protein (DS05 only among these). Record every conversion in the pooled tidy file `POOL01.json` with `independent_source` listing the letters.
4. **Method.** Per variable: Kruskal-Wallis across cohorts with permutation p and epsilon squared; pairwise Cliff's delta with bootstrap intervals for pre-specified contrasts (DS05 vs SRCA, same species different clinic; SRCA vs S-CB017, different species; natural B. rossi vs field B. vogeli); proportion outside each sheet's own reference range with exact intervals. Species as a stratum in a second pass. BH across the run. Unit: dog; no dog appears in two cohorts after de-duplicating SRC-A.
5. **Outputs.** New payload `cohort_distributions` (per variable: cohort, species, n, median, quartiles, 5th and 95th percentiles, reference range), drawable as side-by-side boxes in `grouped_distribution`; `effect_table` of contrasts; `interpretation`; `run_notes` with the mapping table.
6. **Caveats.** Cohorts differ by analyser, laboratory reference range, case mix (tertiary referral vs primary clinic vs field survey) and sampling relative to treatment, and every such difference is confounded with species. S-CB517 NEUT may be total rather than segmented. S-CB013 dogs are mostly subclinical. The DS03 natural cohorts may share dogs with SRC-A (same hospital, unverified), so DS03 is reported but not combined with SRC-A in any pooled statistic.
7. **Effort.** Tidy: batches A, D, E plus `variable_map.json` and `tidy_pool01.py`. Script: `experiment_pool.py`. New view: `grouped_distribution` with cohort facets.
8. **Priority: medium.** Useful reference distributions for the review and the first cross-cohort check of EXP01, but it is the largest tidy burden in the catalogue.

### EXP21-POOL-controls: healthy-control distributions per dataset, side by side

1. **Code and name.** `EXP21-POOL-controls`, Healthy-dog values for the shared cytokine panel, acute-phase proteins and reticulocyte indices.
2. **Question.** What do the healthy controls in SRC-A (15 to 20 dogs, seven cytokines, SAA, CRP, MPXI), S-CB017 (16 dogs, nine cytokines on a different panel), DS03 (14 dogs, reticulocyte indices) and DS07 (20 dogs, proteins) look like, as robust percentile ranges with intervals? These are not reference intervals (ASVCP guidance needs 40 or more for a robust interval and 120 for a non-parametric one) and must not be labelled as such; they are the comparison bands the case experiments use.
3. **Data.** Controls from batches A, D, E (and C for DS07 as a side table).
4. **Method.** Median, 2.5th and 97.5th percentiles by the robust method with bootstrap intervals, per dataset; no pooling across datasets (different panels and analysers); detection-floor proportion per analyte. Unit: dog.
5. **Outputs.** `cohort_distributions` payload as in EXP22; `interpretation` stating plainly that these are small-n comparison bands.
6. **Caveats.** Eight of the 16 S-CB017 healthy dogs had prophylactic imidocarb. Control selection and matching are undocumented in SRC-A. Fifteen to twenty dogs give wide percentile intervals.
7. **Effort.** Tidy: shared. Script: `experiment_pool.py` sub-command. New view: shared.
8. **Priority: low.**

## Family 8: literature-level experiments (articles.jsonl, cohorts.json, data/terms, data/severity)

Units: 444 CB articles; 101 of them sit in 38 cohorts, so there are about 381 independent units (343 singletons plus 38 cohorts) when one unit per cohort is counted. Every count below is reported twice: per article and per unit. Period effects are confounded with search round (rounds 1 to 3 covered 2016 to 2026, round 4 covered 2006 to 2016 with its own strategy), so trends should be reported within round or with round as a stratum.

### EXP24-ARTICLES-trends: category, species and study-type trends by period, cohort-deduplicated

1. **Code and name.** `EXP24-ARTICLES-trends`, What the literature studied, by five-year period.
2. **Question.** Has the mix of primary categories, Babesia species, study types (primary, case report, review), evidence types and countries shifted across 2006 to 2026, and does deduplication by cohort change the picture? The research map quotes raw article counts; this gives the deduplicated, interval-bearing version.
3. **Data.** `articles.jsonl`, CB only: `first_pub_date` (year), `primary_category`, `secondary_tags`, `species_short` (normalise the free-text variants to B. canis, B. gibsoni, B. rossi, B. vogeli, B. vulpes, mixed/unspecified), `include_type`, `evidence_type` (collapse to descriptive, associational, mechanistic, prognostic, review), `country` (normalise the top 12 by keyword), `cohort_id`. Periods: 2006 to 2010, 2011 to 2015, 2016 to 2020, 2021 to 2026. Units: article, and cohort-deduplicated (a cohort is placed in the period of its first article and takes its modal category).
4. **Method.** Chi-square of category by period with permutation p (shuffle periods across units) and Cramér's V with bootstrap interval; per category, a Cochran-Armitage trend on the proportion per period with an exact interval on each proportion; standardised residuals per cell to say which category-period combinations are over- or under-represented. Same for species and include_type. BH across the families. Unit of resampling: independent unit (article or cohort), stated per table.
5. **Outputs.** New payload `trend_table` (period x category counts and proportions with intervals, per article and per unit), drawable with `matrix_heatmap` plus a line variant; `interpretation`; `run_notes` listing the normalisation maps.
6. **Caveats.** Categories are automatic (NLP, no human review; 144 of 428 low confidence); run the whole thing a second time on the agents' labels and report where the trend conclusions differ. Period is confounded with search round and with full-text availability (which affects NLP categorisation). Absence in the index is absence in the search, not in the literature.
7. **Effort.** Tidy: no. Script: `experiment_literature.py trends`. New view: `matrix_heatmap` and a line chart (or JSON only at first).
8. **Priority: medium.** Ready to run and directly feeds the review's descriptive epidemiology.

### EXP25-ARTICLES-syndromes: syndromes cited versus studied

1. **Code and name.** `EXP25-ARTICLES-syndromes`, Which clinical syndromes are mentioned in the literature and which are actually studied.
2. **Question.** For each syndrome concept shown on the dashboard (acute kidney injury, cerebral babesiosis, ARDS, DIC, SIRS, hypoglycaemia, hepatopathy, icterus, haemoconcentration, pancreatitis and so on), how many independent units mention it, how many study it (an affirmed mention in title, results, case or conclusion), and what is the studied-to-mentioned ratio with an interval? A syndrome that is cited everywhere and studied nowhere is a research gap the review can name.
3. **Data.** `data/terms/<ID>.json` for the 444 CB articles (sections and affirmed counts per concept; `source_format` per article), `data/terms/term_display.csv` (`action = show`, `display_name` merges), `articles.jsonl` for `cohort_id`, `primary_category`, period. The "studied" rule is the console TermLoader rule. If `data/syndromes/article_concepts.csv` is regenerated, its `in_results_or_case` column is the equivalent and should be used in preference.
4. **Method.** Per concept: mentioned units, studied units, studied proportion with a Wilson interval; the same split by category and by period; concepts ranked by the gap (mentioned minus studied) and by the ratio. Chi-square with permutation p for the concept x category table of studied units; Cramér's V. Stratify by `source_format` (abstract-only articles can only "study" in the abstract, which inflates the ratio) and report both strata. Unit: independent unit (cohort-deduplicated).
5. **Outputs.** New payload `cited_vs_studied` (concept, mentioned, studied, ratio, interval, by stratum), drawable as a dumbbell chart from `effect_table`; `matrix_heatmap` for concept x category; `interpretation`; `run_notes` with the concept list used.
6. **Caveats.** UMLS linking at threshold 0.85 has known mislinks (the display map hides 13 concepts but not all problems); 230 of 481 articles are abstract-only, so section-based "studied" status is only meaningful for the 251 with full text. Negated mentions are excluded but hedged ones are not.
7. **Effort.** Tidy: no. Script: `experiment_literature.py syndromes` (reads 444 small JSON files). New view: dumbbell variant of `effect_table`.
8. **Priority: medium.**

### EXP26-ARTICLES-agreement: NLP categories versus the agents' labels

1. **Code and name.** `EXP26-ARTICLES-agreement`, Agreement between the two automatic category labellings.
2. **Question.** Beyond the raw 54% primary-category agreement, how far above chance is it (kappa with an interval), which category pairs are confused, and does agreement depend on NLP confidence, full-text availability, period or species? Neither labelling is a gold standard; the experiment measures reliability, and the confusion structure tells the review which categories are not well separated by either method.
3. **Data.** `articles.jsonl`, the 428 CB articles where the NLP found a category (the 16 that fell back to the agents' label agree trivially and are excluded); `primary_category` vs `agent_primary_category`; `secondary_tags` vs `agent_secondary_tags`; `category_confidence`; `fulltext_checked` or, better, `source_format` from `data/markdown_report.jsonl` joined by id; period; species.
4. **Method.** Cohen's kappa (unweighted) for primary category with a bootstrap interval over articles; per-category kappa and positive agreement; the 11 x 11 confusion matrix with standardised residuals; Jaccard overlap of the secondary tag sets per article (median, interval) and of the union of primary plus secondary. Agreement by stratum (confidence high vs low, full text vs abstract, period, species) with permutation p for the difference in kappa. Unit: article (cohort does not matter for a labelling-agreement question, but report the deduplicated kappa as a sensitivity).
5. **Outputs.** `matrix_heatmap` (confusion matrix with counts and residuals), `effect_table` (kappa by stratum with intervals), `interpretation`, `run_notes`.
6. **Caveats.** Kappa is depressed when categories are unbalanced (ERY and INF dominate) and when the two schemes define SEV differently (the agents used SEV for 121 articles, the NLP for 59, by design of the SEV spread rule). The agents saw the extraction packet (often the abstract); the NLP saw the full text where available. Neither is ground truth.
7. **Effort.** Tidy: no. Script: `experiment_agreement.py labels`. New view: `matrix_heatmap`.
8. **Priority: high**, because it is ready today, cheap, and the review currently reports the 54% figure without an interval or a confusion structure.

### EXP27-SEV-matrix: marker-versus-severity evidence matrix from the pilot extraction

1. **Code and name.** `EXP27-SEV-matrix`, Which markers are consistently associated with severity or death across the extracted articles.
2. **Question.** Across the 275 verified rows from 10 articles, which markers are higher or lower in severe disease consistently across independent cohorts, which disagree, and which were tested once? Pooled effect sizes are mostly impossible (effect types differ), so this is a vote-count synthesis with an honest denominator, not a meta-analysis.
3. **Data.** `data/severity/associations.csv`, rows with `quote_check` exact or near (all 275 currently exact); fields `id`, `cohort`, `article_species`, `outcome_class` (mortality 149, complicated 41, anaemia grade 29, severity grade 17, organ dysfunction 15, other 24), `marker`, `marker_class`, `direction`, `significant`, `n_total`, `n_severe`, `effect_type`, `effect_value`, `effect_ci`, `confidence`. Independent units: CB050 and CB145 are both CH03, so 9 units; CB141 is CH12, CB202 CH08, CB263 CH18 (single members in the pilot).
4. **Method.** Collapse to one row per marker x outcome class x unit (within a unit, keep the adjusted or largest-n analysis; record the rule). Per marker x outcome class: units tested, units significant in each direction, a sign test on direction across units (exact binomial, only where 3 or more units), and a consistency index (largest same-direction share). Where two or more units report the same effect type with intervals (ROC AUC with CI, or median difference), a random-effects pooled estimate (DerSimonian-Laird, numpy) with I squared, clearly labelled as exploratory; otherwise none. Species as a split. BH across the sign tests. Unit of resampling: cohort.
5. **Outputs.** New payload `evidence_matrix` (marker x outcome class: units tested, direction votes, consistency, pooled estimate when any), drawable with `matrix_heatmap`; `effect_table` for the few pooled estimates (forest); `interpretation`; `run_notes` (collapsing rule, rows dropped).
6. **Caveats.** Ten articles: one B. rossi case series (CB040) contributes 78 rows, so the matrix is dominated by one cohort and one species, and the sign tests rarely reach three units. Severity definitions differ (21 definitions across 10 articles); the outcome_class grouping hides that. Rows marked `not_tested` or `unclear` are excluded, which biases toward reported positives. `experiment.dataset = null`.
7. **Effort.** Tidy: no. Script: `experiment_evidence.py`. New view: `matrix_heatmap`. The ML plan's EXP08 describes the same analysis; it is classical and belongs here.
8. **Priority: high.** Ready today and it is the review's central question, even if the answer is mostly "tested once".

### EXP29-SEV-reanalysis: do recomputed effects agree with the extracted literature rows?

1. **Code and name.** `EXP29-SEV-reanalysis`, Literature rows versus dog-level recomputation for the articles that have data.
2. **Question.** For the extracted rows whose underlying dogs are in a tidy file (CB050 and CB145 via SRCA, CB017 via S-CB017), do the direction and significance recomputed in EXP03, EXP04 and EXP10 agree with what the articles reported and the extractor recorded? This validates both the extraction pipeline and the reanalysis before either is trusted at scale.
3. **Data.** `associations.csv` rows for CB050 (5), CB145 (31), CB017 (28); the matching EXP03/EXP04/EXP10 `associations[]` rows, joined by canonical marker and contrast.
4. **Method.** Per matched row: agreement of direction (exact), of significance at 0.05 (before and after BH), and the recomputed effect size with interval next to the reported statistic. Kappa over matched rows with a bootstrap interval; a table of disagreements with the quoted sentence. No new p values beyond those.
5. **Outputs.** `matrix_heatmap` (agreement statistics) and a disagreement table in the payload; `interpretation`; `run_notes` (rows unmatched and why).
6. **Caveats.** The articles used different tests (parametric, unadjusted), so disagreement on significance near 0.05 is expected; disagreement on direction is the finding to chase. CB145's dogs are in S-CB517 but CB145's own variables (its paper is on something else in CH03) may not all be in the file; report coverage.
7. **Effort.** Tidy: none beyond batches A and D. Script: `experiment_agreement.py reanalysis`. New view: shared.
8. **Priority: medium**, after its inputs exist.

### EXP28-ARTICLES-availability: data availability by period, journal, country and access

1. **Code and name.** `EXP28-ARTICLES-availability`, Who shares individual-level data and whether that has changed.
2. **Question.** How does dataset status (1 verified download, 2 record only, 3 request-only, 4 not located after checks, 5 not assessable) vary by five-year period, journal family, country, species, study type and open-access status (PMCID present), among the articles that could be assessed? Data sharing is part of the review's methods discussion and the pattern decides where future data requests should go.
3. **Data.** `articles.jsonl` CB: `dataset_status_code`, `first_pub_date`, `journal` (normalise case and the top 15 names; group the rest as other), `country` (top 12), `species_short`, `include_type`, `pmcid`, `fulltext_checked`, `supplement_checked`, `repository_checked`, `data_availability_statement` (present or not), `cohort_id`. Primary analysis among assessed articles (codes 1 to 4, n = 253); accessibility (code 5 vs not, n = 444) analysed separately.
4. **Method.** Chi-square with permutation p and Cramér's V for status by each factor; proportions with Wilson intervals; standardised residuals; Cochran-Armitage trend for "any shared data (codes 1 to 3)" by period. Per unit (cohort) as sensitivity. BH across the factors. No regression (the ML plan has a logistic version as EXP15; the contingency version here is the classical one).
5. **Outputs.** New payload `availability_table` (factor level x status counts and proportions with intervals), drawable with `matrix_heatmap`; `interpretation`; `run_notes` with normalisation maps.
6. **Caveats.** Code 5 means the review could not access the article, not that the authors withheld data; mixing it in inflates the apparent non-sharing of paywalled journals. Supplement and repository checks were done for only 239 and 233 articles, so "not located" is partly "not looked for"; report the checked flags per period. Period is confounded with search round.
7. **Effort.** Tidy: no. Script: `experiment_literature.py availability`. New view: shared.
8. **Priority: medium.**

## Family 9: smaller experiments (low priority, cheap to add later)

### EXP34-SCB133-matrix: does the published B. canis correlation matrix agree with the DS05 matrix?

1. **Code and name.** `EXP34-SCB133-matrix`, Correlation-of-correlations between CB133's pooled Spearman matrix and EXP01.
2. **Question.** For the 11 variables both report (rectal temperature, total protein, albumin, globulins, haematocrit, WBC, segmented neutrophils, lymphocytes, monocytes, eosinophils, platelets), do the pairwise rho values from a German B. canis cohort (84 dogs, four groups pooled) correlate with those from the Eastern Cape B. rossi cohort? A cheap cross-species, cross-country check of whether the admission correlation structure is generic.
3. **Data.** S-CB133 `mmc1.xlsx` (21 x 21 matrix, 210 pairs; parse the typos listed in `datasets.jsonl`), EXP01 `spearman_matrix` payload. 55 shared pairs.
4. **Method.** Spearman and concordance correlation between the two sets of 55 rho values; a Mantel-type permutation test (permute variable labels, 10,000 draws); a list of the pairs that differ most. Unit: variable (label permutation).
5. **Outputs.** `effect_table`-style scatter (pair, rho CB133, rho DS05) and `matrix_heatmap` of differences; `interpretation`; `run_notes`.
6. **Caveats.** CB133 pooled acute cases with seropositive, Mycoplasma and healthy dogs, so its correlations mix between-group with within-group structure; DS05 is cases only. The two are expected to differ for that reason alone, and the experiment can only show how much.
7. **Effort.** Tidy: a 20-line reader for the matrix (no tidy file needed; store the matrix in the experiment's `parameters`). Script: `experiment_agreement.py matrix`. New view: shared.
8. **Priority: low.**

### EXP30-SCB013-coinfection: PCV and platelets against pathogen status in community dogs

1. **Code and name.** `EXP30-SCB013-coinfection`, Haematology by B. vogeli, A. platys and haemoplasma status in 96 free-ranging dogs.
2. **Question.** Is B. vogeli PCR positivity associated with lower PCV or platelets once A. platys and haemoplasma status, site and body condition are allowed for, and does Ct track PCV in the 7 positives? Low value for pathophysiology (B. vogeli is mild) but the only multi-pathogen per-dog table.
3. **Data.** S-CB013 tidy (batch G): 96 dogs; `pcv`, `platelets`, pathogen flags, site, body condition, age class, sex.
4. **Method.** Fisher exact and Mann-Whitney permutation with Cliff's delta per pathogen; site-stratified permutation; Spearman of Babesia Ct against PCV (n = 7, interval only). Flag the PCV and PLT flag columns and the derived "alone"/"polymicrobial" columns as trivial. Unit: dog.
5. **Outputs.** `effect_table`, `grouped_distribution`, `interpretation`, `run_notes`.
6. **Caveats.** Seven positives, four co-infected; site confounded with date; the "control" column coding looks inverted and must be re-derived from the pathogen columns.
7. **Effort.** Tidy: yes, small. Script: groups script. New view: shared.
8. **Priority: low.**

### EXP31-DS04-reproducibility: repeat-scoring agreement and zonal gradients in fatal liver pathology

1. **Code and name.** `EXP31-DS04-reproducibility`, Intra-observer agreement of the liver histology scores and zonal gradients of immunohistochemistry counts.
2. **Question.** How reproducible are the semi-quantitative 0 to 3 scores across the 2 to 4 scoring sessions per dog, and do the six immunohistochemistry markers show the portal-to-centrilobular gradient the article reports, tested within dog? A methods question that qualifies the tissue evidence used in the END, MET and INF syntheses.
3. **Data.** DS04 (batch G): 31 populated score sheets for 14 dogs (about 70 items each); `Stats Tables.xlsx` IHC counts (6 markers x 3 zones x 3 fields per dog).
4. **Method.** Weighted kappa and ICC(2,1) per item across sessions with bootstrap intervals over dogs; Friedman across zones per marker within dog (using the per-dog mean of three fields) with exact p and Kendall's W; infected vs control per marker by Mann-Whitney permutation (10 vs 4) with Cliff's delta. BH within family. Unit: dog.
5. **Outputs.** `effect_table`, `matrix_heatmap` (item x agreement statistic), `grouped_distribution`, `interpretation`, `run_notes`.
6. **Caveats.** Four controls scored in a different period from the ten cases (batch and blinding), fatal cases only, zeros used as missing in the haematology sheet, and the haematology rows cannot be linked to case IDs.
7. **Effort.** Tidy: yes, 33 workbooks with inconsistent layouts (the heaviest tidy in this family). Script: `experiment_agreement.py sessions` plus groups. New view: shared.
8. **Priority: low.**

### EXP32-SCB071-trend: urinary metabolites ordered by kidney function

1. **Code and name.** `EXP32-SCB071-trend`, Targeted urinary metabolites across control, non-azotaemic low-UPC, non-azotaemic proteinuric and azotaemic B. canis dogs.
2. **Question.** Which of the 42 targeted analytes trend monotonically with the kidney-function ordering, with effect sizes? Renal involvement is the second most studied complication (REN, 40 primary articles) and this is the only per-dog renal-staged table.
3. **Data.** S-CB071 Table 2A (34 dogs: 12 / 6 / 10 / 6), 42 analytes, 8.4% NA treated as below detection.
4. **Method.** Jonckheere-Terpstra by permutation per analyte, Cliff's delta between control and group C with bootstrap interval, detection-frequency Fisher for analytes with many NAs; BH across the 42. Exclude creatinine and creatine (they define the groups). Unit: dog.
5. **Outputs.** `effect_table`, `grouped_distribution`, `interpretation`, `run_notes`.
6. **Caveats.** Groups of 6; the `_B`/`_Z` sample suffixes suggest cases and controls were processed separately (batch); groups are defined by creatinine and UPC, which are not given per dog; no non-babesial kidney comparator.
7. **Effort.** Tidy: yes, small (one sheet). Script: `experiment_abundance.py` trend mode. New view: shared.
8. **Priority: low.**

### EXP33-SRCH-abundance: targeted serum and salivary metabolite panels, infected vs healthy

1. **Code and name.** `EXP33-SRCH-abundance`, Infected versus healthy differences in the Zagreb targeted metabolomics tables.
2. **Question.** Which targeted serum (S-CB091, 205 analytes, 12 vs 12) and salivary (S-CB137, 39 analytes, 14 vs 14) analytes differ between B. canis-infected and healthy dogs under a rank-based test with BH, and how many of the published hits survive? Hypothesis-generating only; infected vs healthy is dominated by generic illness and acute-phase change.
3. **Data.** Targeted tables only (S2A, S3); untargeted features are left out (thousands of features in 24 to 28 dogs).
4. **Method.** Mann-Whitney permutation with Cliff's delta and bootstrap interval per analyte; detection Fisher for analytes with heavy NA; BH per dataset; agreement with the published significant lists (overlap and sign). Unit: dog.
5. **Outputs.** `effect_table` with volcano toggle, `interpretation`, `run_notes`.
6. **Caveats.** Age and sex differ between groups; run order and batch unknown; no severity label, so nothing about pathophysiology beyond "differs from healthy". The three Zagreb studies may share dogs (CH06), so they are one source.
7. **Effort.** Tidy: yes, two small readers. Script: `experiment_abundance.py`. New view: shared.
8. **Priority: low.**

## Leakage and confounding traps, collected

- **Treatment timing.** DS01/DS02/DS06: treatment at day 4 or 4.1, triggered by haematocrit and habitus endpoints; days 5 to 8 are post-treatment. S-CB017: cytokine draws 6 to 8 hours after imidocarb; day 7 is post-treatment; 8 healthy dogs apparently had prophylactic imidocarb. DS07, SRC-A, DS03 natural: sampling time relative to treatment not recorded.
- **Outcome used as predictor.** S-CB017: WBC is a SIRS criterion and SIRS defines "complicated". DS07: haematocrit, urea, creatinine, bilirubin, glucose, lactate and death within 24 h define "complicated", so proteins tracking haemolysis or renal injury restate it. SRC-A: outcome includes euthanasia for poor prognosis. S-CB013: anaemia and thrombocytopenia flags are functions of PCV and PLT. S-CB071: groups are cut on creatinine and UPC.
- **Derived variables against parents.** DS05: MCV, MCH, MCHC, WCC, ARC, globulin and all 13 authors' classes; SRC-A: WBC against segmented plus band; S-CB017: percentage against absolute differentials; DS03: ARC from Ret% and RBC, CHDelta from CHr. Flag as `trivial` everywhere.
- **Pooled cohorts with batch effects.** S-CB050: two cohorts, two years, cytokines in one; DS07: 11 TMT plexes, spurious values in three unused channels; DS03: two natural cohorts of unknown difference; S-CB133: four clinical groups pooled in one matrix; DS04: controls and cases scored in different months; S-CB071: case and control sample suffixes suggest separate processing.
- **Duplicated animals across files.** S-CB050 cohort 1 = S-CB517 (CH03); DS01 = DS02 and the DS03 experimental sheet = the DS02 dogs = the DS06 dogs (CH09); the three Zagreb metabolomics tables may share dogs (CH06); DS04 = S-CB147 (CH04). Count by `independent_source`, with the DS03 correction above.
- **Literature.** Period confounded with search round and with full-text availability; categories automatic; 230 abstract-only articles; status 5 is inaccessibility, not non-sharing; cohort deduplication changes every count.

## What the unlabelled datasets cannot answer

DS05, DS03 (natural), DS02, DS06, S-CB013 and the metabolomics tables have no outcome or severity label. They give association structure, kinetics, reference-style distributions and reproductions of published descriptive claims. They cannot say which admission finding predicts death or complication, cannot rank markers prognostically, and any grouping found in them is a phenotype description, not a subtype. The catalogue states this in every such entry so the interpretation notes carry it forward.

## The five to run first, in order

1. **EXP03-SCB050-groups.** Tidy the S-CB050 docx (batch A, the easy half), write `experiment_groups.py` and the `effect_table` and `grouped_distribution` views. This unlocks the only hard outcome in the collection and the script three other families reuse.
2. **EXP02-SCB050-pairwise.** A parameter run of the existing pairwise script on the file from step 1; the existing view renders it, so it is the first non-DS05 result on the Experiments screen with no app work.
3. **EXP10-SCB017-groups, then EXP11-SCB017-paired.** Tidy the one xlsx (batch D), rerun the groups script for the second species and the published MCP-1 claim, then add the paired script for the only natural-infection repeated measures. One tidy step, two high-value results.
4. **EXP27-SEV-matrix with EXP26-ARTICLES-agreement.** Both read files that exist today and need no tidy step; together they replace two unqualified numbers in the review (the marker evidence list and the 54% agreement) with intervals and structure, and they exercise the `matrix_heatmap` view that the DS07 pair needs next.
5. **EXP06-DS07-abundance, then EXP07-DS07-agreement.** The heaviest tidy step among the high-priority items (plex and channel join), but the only severity-labelled omics table, and the published 78-protein list is directly testable.

After these, the natural order is EXP04 and EXP05 (finish batch A with the PDF tables and the linkage check), EXP12 and EXP13 (DS03), EXP24, EXP25 and EXP28 (the rest of the literature family), then batch B (EXP15, EXP16) when there is appetite for the experimental time course.
