# EXP04 DS07 proteome: Serum proteome classes in B. rossi babesiosis

| Field | Value |
|---|---|
| Experiment code | `EXP04-DS07-proteome` |
| Layer | 1 single dataset |
| Method token | `proteome` (goes in `experiment.method`) |
| Dataset(s) | `DS07` (PRIDE PXD039022, article CB112, independent source SRC-C). Comparator only, not analysed: `S-CB112` (the article's Supplementary Table S1) |
| Readiness | tidy file needed (`data/tidy/DS07.json` does not exist yet) |
| Python environment | `.venv-nlp` (Python 3.12; scikit-learn 1.9.1, scipy 1.17.1, numpy 1.26.4 already installed; nothing to install). The tidy script needs only the stdlib and runs in either environment. Add `scikit-learn>=1.5` and `scipy>=1.11` to `scripts/requirements-experiments.txt` with a comment that they are needed by `experiment_proteome.py` in `.venv-nlp` |
| Estimated build effort | medium (tidy script about 1 hour; experiment script 3 to 4 hours; full run 30 to 60 minutes) |
| Suggested model for the building agent | opus: a hand-written sparse PLS-DA, nested resampling with permutation of the whole pipeline, and leakage control need careful reasoning |
| Depends on | `scripts/tidy_ds07.py` → `data/tidy/DS07.json` (task 2 of this spec). No other experiment |

## 1. Question and hypotheses

Questions:

1. Which serum proteins separate healthy control, uncomplicated and complicated *B. rossi* babesiosis, and which of them are selected stably across resamples rather than by chance?
2. Once the easy healthy-versus-infected contrast is removed, which proteins separate complicated from uncomplicated infection?

Hypotheses (from CB112, `articles/CB112_2023_serum-proteome-profiling-naturally-acquired-babesia.md`, and the article's Table 1):

- H1. Complicated disease shows higher CD14 (`A0A1S7J0A8`), ITIH4 (`H9GWY3`), APOE (`P18649`), ORM1 (`F6Y713`), fibrinogen alpha (`F1PBL4`) and complement regulators CFI, CFP, C8G, C2 than uncomplicated disease.
- H2. Complicated disease shows lower RBP4 (`A0A5F4CED7`), transferrin (`E2QZQ1`, `J9P430`), Gc-globulin (`F1P841`), SERPING1 (`F1PYX9`), PROS1 (`A0A5F4D8W3`) and fibronectin (`A0A5F4BW32`).
- H3. The three-class contrast is dominated by an acute-phase, complement and lipoprotein signal that separates controls from all infected dogs (the article's PCA, PC1 30% of variance).

Negative finding: in the complicated-versus-uncomplicated pass, a pipeline whose cross-validated balanced accuracy does not beat the label-permutation null (permutation p ≥ 0.05), or a stable panel (selection frequency ≥ 0.7) that is empty. Either result is reported as a finding, not as a failure of the run.

## 2. Data

### 2.1 Sources

All paths are relative to `core/`. Raw files are read-only.

| File | What it holds | Use |
|---|---|---|
| `data/raw/DS07/B_Proteins.txt` | Proteome Discoverer 2.3 protein export, tab-delimited UTF-8, 677 data rows × 206 columns | Abundances. Keep rows where column `Master` = `IsMasterProtein` (224 rows, 224 unique `Accession`). The other `Master` values (`IsMasterProteinCandidate` 235, `None` 206, `IsMasterProteinRejected` 10, `IsMasterProteinCandidateRejected` 2) are dropped |
| `data/raw/DS07/sample_list.xlsx` | One sheet `Sheet1`, the TMT layout and the group lists | Sample identity and group |
| `data/raw/DS07/B_ProteinGroups.txt` | Presence/absence flags per protein group, no abundances | Not used (record in notes) |
| `data/inspection/DS07.json` | Inspection previews of the three files | Read for orientation |
| `datasets.jsonl` record `dataset_id = "DS07"` | Title, licence (CC0 on PRIDE), `independent_source` = `SRC-C`, `linked_articles` = `["CB112"]`, missingness and limitations text | Dataset block metadata |
| `data/manifest.jsonl` rows `dataset_id = "DS07"` | sha256 per file (`B_Proteins.txt` 2fc5d617…, `sample_list.xlsx` 3119957f…) | `source_sha256` (use the `B_Proteins.txt` row) |
| `data/raw/S-CB112/PMC10290096_supplementaryFiles.zip`, member `41598_2023_37312_MOESM1_ESM.xlsx`, sheet `Table S1` | The article's 78 Kruskal-Wallis-significant proteins. Header row 2: `Accession`, `Gene ID`, `Pvalue`, `FDR`, `Master`, `Description`, `log2FC(AB)`, `log2FC(AC)`, `log2FC(BC)` (A control, B uncomplicated, C complicated; `ns` where the pairwise post-hoc was not significant; 21 rows have a numeric `log2FC(BC)`) | Comparator only. Read in memory with `zipfile`; never extract to disk. All 78 accessions are among the 224 master proteins |

Key column facts in `B_Proteins.txt` (verified):

- Identity: `Accession` (UniProt, col 3), `Description` (col 4, contains `GN=<symbol>` for 172 of 224 master proteins; 15 are `Uncharacterized protein`), `# Unique Peptides` (col 10), `# Peptides`, `Coverage [%]`, `MW [kDa]`.
- Quantities: 55 columns `Abundance Ratio: (F<k>, <ch>) / (F<k>, 126)` for plex k = 1…11 and channel ch = 127…131; and 66 columns `Abundances (Grouped): F<k>, <ch>` (channel 126 is the pooled internal standard, fixed at 100). Ratio equals grouped abundance / 100 to three decimals in every cell checked; use the ratio columns. Empty cell = not quantified. Minimum observed ratio 0.01.
- Channels `F11` 129, 130, 131 are unused in the layout but carry spurious values: drop them. That leaves 52 sample channels = 52 dogs.
- `Found in Sample: [Sn] Fk: ch, Control/Sample` columns label channel 126 as `Control`: this is the internal standard pool, not a control dog. Do not use these labels for group.

`sample_list.xlsx` layout (read with the stdlib xlsx reader copied from `scripts/tidy_ds05.py`; row and column numbers are 1-based as in Excel):

- TMT scheme: row 2 holds channel headers `126`…`131` in columns L…Q; rows 3 to 13 hold plex labels `B1`…`B11` in column K, `IS1`…`IS11` in column L (channel 126), and dog IDs in columns M…Q (channels 127…131). Plex `B11` has only `20z` (127) and `56` (128).
- Groups: column A `Controls` with IDs `1z`…`20z` in column B (rows 3 to 22; one ID is `2z ` with a trailing space, strip it); column D `Complicated babesiosis` with numeric IDs in column E (rows 3 to 16, 14 dogs); column A `Uncomplicated babesiosis` with IDs in column B (rows 25 to 42, 18 dogs).
- Note that `15`/`15z` and `16`/`16z` are different dogs (case and control). Match on the exact stripped string.

Licence: PRIDE states CC0; article CC BY. Independent source SRC-C; no other dataset in this review shares these dogs (overlap unverified, per `datasets.jsonl`).

### 2.2 Tidy file required

Write `scripts/tidy_ds07.py`, following `scripts/tidy_ds05.py` (same module docstring shape, same `read_workbook` stdlib xlsx reader copied into the file, same dataset block, `json.dumps(..., ensure_ascii=False, indent=1)`). Do not import from `tidy_ds05.py`: `python -I` does not put the script folder on `sys.path`. Run: `.venv/Scripts/python.exe -I scripts/tidy_ds07.py`.

Steps:

1. Parse `sample_list.xlsx` into `{(plex k, channel): dog_id}` from the TMT scheme and `{dog_id: group}` from the group lists. Assert 52 unique IDs, each in exactly one group (20 / 18 / 14) and exactly one channel. Fail loudly otherwise.
2. Parse `B_Proteins.txt` with `csv` (tab delimiter). Keep `IsMasterProtein` rows. Map each ratio column `(F<k>, <ch>)` to a dog through step 1; drop `F11` 129 to 131 and assert that exactly 52 columns map.
3. Subjects (52): `code` = the stripped dog ID as in the layout (`1z`…`20z`, `7`, `15`, …); `group_label` = `control`, `uncomplicated` or `complicated`; `outcome_label` = null for controls, otherwise `uncomplicated` / `complicated` (the severity class is the only outcome-like label).
4. Design and technical variables (`include_default = false` for all, so that the pairwise default set never tests them as features):

| code | name | data_type | domain | value |
|---|---|---|---|---|
| `disease_group` | Disease group (CB112) | C | design | `control` / `uncomplicated` / `complicated`; levels with counts |
| `severity_class` | Complicated vs uncomplicated (infected dogs only) | C | design | `uncomplicated` / `complicated`; no observation for controls |
| `tmt_plex` | TMT plex | C | technical | `B1`…`B11` |
| `tmt_channel` | TMT channel | C | technical | `127`…`131` |
| `n_proteins_quantified` | Proteins quantified in this sample | N | technical | count of non-empty ratios across the 224 master proteins |

5. Protein variables (224), one per master protein, in file order:
   - `code` = `prot_` + `Accession` (for example `prot_F1P8Z5`); all under 60 characters.
   - `name` = `<GN symbol> – <description before " OS=">` (for example `APOB – Apolipoprotein B`); when there is no `GN=`, use the description alone.
   - `source_name` = `Accession`.
   - `unit` = `log2 ratio to internal standard`; `data_type` = `N`; `domain` = `proteome`; `derived` = false; `derived_from` = null; `ref_low`/`ref_high` = null; `levels` = null.
   - `include_default` = true when `# Unique Peptides` ≥ 2 and the protein is quantified in at least 26 of the 52 sample channels (≥ 50 %, the article's rule). This gives 112 proteins (128 pass the peptide rule, 156 the detection rule).
   - `description` = `Gene <symbol or 'none'>; <# Unique Peptides> unique peptides; coverage <Coverage [%]> %; MW <MW [kDa]> kDa; quantified in <n>/52 samples.` Add `; in CB112 Table S1` when the accession is in Table S1 (read from the S-CB112 zip as above; if the zip is missing, skip this clause and add a note).
6. Observations: one per dog × protein with a non-empty ratio, `time_point` = `''`, `value_num` = `log2(ratio)` rounded to 6 decimals. Empty ratios produce no observation (missing). Plus one observation per dog for each design and technical variable. Expected protein observations about 10,200 (14,784 cells less about 31 % empty before dropping F11 129 to 131; the script prints the exact count).
7. Dataset block: as in `tidy_ds05.py`, `code` `DS07`, `article_code` `CB112`, `source_file` `data/raw/DS07/B_Proteins.txt`, `source_sha256` from the manifest row for that file, `script` `scripts/tidy_ds07.py`, `species` and `design` from `datasets.jsonl`.
8. Cleaning notes to write into `dataset.notes` (each one a sentence; numbers filled from the run):
   - Only `IsMasterProtein` rows kept (224 of 677).
   - Values are `Abundance Ratio` (sample / internal standard channel 126 of the same plex), stored as log2. No normalisation, filtering or imputation is applied in the tidy file; the experiment script applies median normalisation and its own missing-value filter (EXP04 parameters `min_unique_peptides` = 2, `min_detect_frac` = 0.5, normalisation = per-sample median over proteins complete in all 52 samples, imputation = training-fold protein minimum minus 1 on the log2 scale).
   - Plex 11 channels 129 to 131 are unused in `sample_list.xlsx` and were dropped although they carry values in 46 to 90 proteins.
   - Group membership comes from the `sample_list.xlsx` group lists joined by plex and channel; Proteome Discoverer's `Control` label marks the internal standard, not control dogs.
   - Missing values (about 31 % of protein × sample cells) are plex-structured and probably abundance-dependent (missing not at random); a missing value is never stored as zero.
   - `include_default` = at least 2 unique peptides and quantified in at least 26 of 52 samples (112 proteins).
   - `B_ProteinGroups.txt` and peptide-level data were not used.

### 2.3 Variables and filters

- Analysis set: protein variables with `include_default = true` (112 expected). The script recomputes the rule from parameters `min_unique_peptides` (default 2, read from the description) and `min_detect_frac` (default 0.5, from the observations) and asserts it agrees with the tidy flag at default settings.
- Label variables: `disease_group` (three-class pass, n = 52: 20 / 18 / 14) and `severity_class` (second pass, n = 32: 18 / 14).
- Held out: `tmt_plex` (used only for the confounding check and the within-plex sensitivity analysis), `tmt_channel`, `n_proteins_quantified` (reported, not modelled).
- Complete-case sensitivity set: proteins quantified in all 52 samples (96 expected; the script prints the number).
- No subject exclusions. Events per variable for the second pass: 14 complicated / 112 proteins = 0.125, reported in every performance result.

## 3. Method

Implement in `scripts/experiment_proteome.py`, run with `.venv-nlp/Scripts/python.exe -I`. Seeds: a single `--seed` (default `20261105`). Derive every random stream from it deterministically: outer CV repeat r uses `seed + 1000 * r`; inner CV uses `seed + 1000 * r + 10 * fold + 1`; stability subsample b uses `seed + 500000 + b`; permutation b uses `seed + 900000 + b`; bootstrap uses `seed + 7`. Pass the same integers as `random_state` to scikit-learn. The run must reproduce bit-for-bit.

1. **Load.** Read `data/tidy/DS07.json`; build X (52 × p) of log2 ratios with NaN for missing, rows in subject order, columns in variable `sort_order`. Build labels from `disease_group` and `severity_class` observations.
2. **Filter.** Keep proteins meeting `min_unique_peptides` and `min_detect_frac` (step 2.3). Record kept and dropped counts in `run_notes`.
3. **Median normalisation (label-free, done once on all samples).** For each sample, subtract the median of its log2 values over the proteins that are complete in all 52 samples; then add back the grand median of those sample medians so the scale stays interpretable. This uses no labels, so doing it before cross-validation does not leak. Record the per-sample shifts (min, median, max) in `run_notes`.
4. **Imputation (inside every training fold).** For each protein, missing values in both training and test samples are set to (minimum observed value of that protein in the training samples) − 1, that is half the minimum on the ratio scale (left-censored, missing-not-at-random assumption). For the univariable screen in step 8, no imputation: tests use observed values only.
5. **Standardisation (inside every training fold).** z-score each protein with training mean and SD; apply the same to the test fold.
6. **Sparse PLS-DA (numpy implementation; no package provides it).** Algorithm (Lê Cao et al. 2011, regression-mode deflation as in mixOmics `splsda`):
   - Y = one-hot class matrix, centred and scaled by training columns.
   - For component h = 1…H: M = Xₕᵀ Yₕ; initialise a, b from the first left and right singular vectors of M. Repeat until ‖a − a_old‖ < 1e-6 or 500 iterations: a ← M b; soft-threshold a so that exactly `keepX` entries are non-zero (λ = the (keepX + 1)-th largest |aⱼ|, aⱼ ← sign(aⱼ)·max(|aⱼ| − λ, 0)); a ← a/‖a‖; b ← Mᵀa; b ← b/‖b‖. Scores t = Xₕ a; X loadings p = Xₕᵀt/(tᵀt); Y loadings c = Yₕᵀt/(tᵀt); deflate Xₕ₊₁ = Xₕ − t pᵀ and Yₕ₊₁ = Yₕ − t cᵀ.
   - Prediction: test scores T* = X* W (PᵀW)⁻¹; assign the class whose training centroid in score space is nearest (Euclidean; mixOmics `centroids.dist`).
   - H = `spls_ncomp_multiclass` (2) for three classes, `spls_ncomp_binary` (1) for two. `keepX` (same for every component) tuned over `spls_keepx_grid` = [5, 10, 20, 40] in the inner loop by balanced accuracy.
   - Selected proteins = union of non-zero weights across components.
7. **Multinomial elastic net (scikit-learn).** `LogisticRegression(solver="saga", l1_ratio=..., C=..., max_iter=20000, tol=1e-4, class_weight="balanced", random_state=...)`. In scikit-learn 1.9 the multiclass loss is multinomial by default; if the installed version still requires `penalty="elasticnet"` for `l1_ratio` to apply, pass it. Record the exact constructor arguments and any convergence warnings (count) in `run_notes`. Grid: `enet_C_grid` = [0.01, 0.03, 0.1, 0.3, 1, 3] × `enet_l1_ratio_grid` = [0.5, 0.9], tuned in the inner loop by balanced accuracy (ties: smaller C, then larger l1_ratio). Selected proteins = non-zero coefficient for any class.
8. **Resampling and validation.**
   - Outer loop: repeated stratified k-fold, `outer_folds` = 5, `outer_repeats` = 20 (100 test folds per pass). Inner loop: stratified `inner_folds` = 4, one repeat, for tuning only. Imputation, standardisation and tuning sit inside the folds (steps 4, 5).
   - Metrics per repeat (pooling the 5 test folds of that repeat): balanced accuracy, per-class recall, confusion matrix; for the elastic net also macro one-vs-rest AUC (`roc_auc_score(..., multi_class="ovr", average="macro")`) for three classes and plain AUC for two. Report mean, SD and the 2.5th/97.5th percentiles across the 20 repeats.
   - **Label-permutation test of the whole pipeline.** For each model and pass: permute the label vector (`numpy.random.default_rng(seed + 900000 + b).permutation`) and rerun the complete nested pipeline with a lighter outer scheme (`perm_outer_folds` = 5, `perm_outer_repeats` = 2). Compute the observed statistic with the same 5 × 2 scheme and the same fold seeds on the true labels. Statistic = mean balanced accuracy. B = `permutations_spls` (200) for sPLS-DA and `permutations_enet` (100) for the elastic net. p = (1 + #{null ≥ observed}) / (1 + B). Report the null mean and 95th percentile beside the observed value.
9. **Stability selection.** For each pass and model: B = `stability_subsamples` (100) stratified subsamples of `stability_fraction` (0.5) of the dogs without replacement; impute and standardise within the subsample; fit at fixed hyperparameters = the modal value chosen across the 100 outer-fold tunings (elastic net: modal (C, l1_ratio); sPLS-DA: modal keepX). Selection frequency per protein = share of subsamples in which it is selected. Stable panel = frequency ≥ `stability_threshold` (0.7) under the elastic net (primary); report the sPLS-DA frequency alongside and flag proteins stable under both. Also record, per protein, the frequency of selection across the 100 outer training folds. Report the Meinshausen-Bühlmann bound on expected false selections E[V] ≤ q² / ((2π − 1)·p), with q = mean number selected per subsample, π the threshold and p the number of proteins.
   - Direction per panel protein: for the three-class pass, the class with the highest median normalised value and the sign of the mean elastic-net coefficient for each class across stability fits; for the binary pass, `higher in complicated` or `lower in complicated` from the sign of the median difference (complicated − uncomplicated), with the Hodges-Lehmann shift in log2 units.
10. **Second pass.** Repeat steps 4 to 9 on the 32 infected dogs with `severity_class` as the label (binary models: sPLS-DA with 1 component; elastic net reduces to binomial logistic). Proteins are filtered again on detection within the 32 dogs at the same threshold.
11. **Univariable screen (stored as associations).**
    - Family A: Kruskal-Wallis H for each analysed protein against `disease_group` (observed values only, n per protein = dogs with a value). Permutation p with `kw_permutations` (10,000) label permutations, vectorised in numpy (rank once, permute labels; same approach as `experiment_pairwise.py`). Effect size eta² = (H − k + 1)/(n − k), with a stratified bootstrap 95 % interval (`bootstrap` = 2000 resamples).
    - Family B: Mann-Whitney U for each protein against `severity_class` (infected dogs only). Permutation p (10,000). Effect size rank-biserial r = 2U/(n₁n₂) − 1 with bootstrap 95 % interval; Hodges-Lehmann shift (complicated − uncomplicated, log2) in `detail`.
    - Benjamini-Hochberg across both families together (the whole run), `alpha` = 0.05. A test is skipped (and listed in `run_notes`) when any group has fewer than 3 observed values.
12. **Article comparison.** From Table S1: set S78 = all 78 accessions; set S21 = rows with numeric `log2FC(BC)`, with sign. Compare with Family A significant set (overlap, Jaccard) and with Family B significant set and the binary stable panel (overlap, Jaccard, sign agreement against `log2FC(BC)`). The article analysed the same 52 dogs, so agreement is a reproduction check, not replication.
13. **Pathway grouping (no network calls).** Assign every analysed protein to one class by the first matching rule on gene symbol (from `GN=`) or description, case-insensitive:

| Order | Class | Gene symbol rule | Description keywords |
|---|---|---|---|
| 1 | Complement | `^C[1-9]`, `^CF[BDHIP]$`, `^C4BP`, `^SERPING1$`, `^CD55$`, `^CD59$`, `^MASP`, `^MBL`, `^FCN` | complement, properdin, C3/C5 convertase |
| 2 | Coagulation and fibrinolysis | `^F[0-9]+[AB]?$`, `^FG[ABG]$`, `^PLG$`, `^KNG1$`, `^SERPINC1$`, `^SERPIND1$`, `^PROS1$`, `^PROC$`, `^HRG$`, `^VWF$`, `^THBS`, `^HABP2$` | fibrinogen, prothrombin, plasminogen, coagulation, kininogen, antithrombin |
| 3 | Acute-phase and protease inhibitors | `^ORM`, `^HP$`, `^HPX$`, `^SAA`, `^CRP$`, `^LBP$`, `^LRG1$`, `^ITIH`, `^SERPINA`, `^A2M$`, `^AMBP$`, `^CP$`, `^FETUB$`, `^AHSG$` | acute phase, haptoglobin, hemopexin, alpha-1-acid, inter-alpha-trypsin, serpin, macroglobulin, ceruloplasmin |
| 4 | Lipoprotein and lipid transport | `^APO`, `^PON`, `^LCAT$`, `^CLU$`, `^PLTP$`, `^RBP4$`, `^AFM$` | apolipoprotein, paraoxonase, retinol-binding, clusterin |
| 5 | Metal and hormone transport | `^TF$`, `^GC$`, `^TTR$`, `^ALB$`, `^SHBG$`, `^SERPINA6$` (if not caught above) | transferrin, albumin, transthyretin, vitamin D-binding, Gc-globulin, metal-binding |
| 6 | Immunoglobulins and innate immunity | `^IG[HKLJ]`, `^CD14$`, `^LTF$`, `^LYZ$`, `^PGLYRP`, `^S100` | immunoglobulin, Ig , lactotransferrin, CD14, monocyte differentiation |
| 7 | Extracellular matrix and cytoskeleton | `^FN1$`, `^FBLN`, `^TGFBI$`, `^ECM1$`, `^GSN$`, `^ACT[BG]`, `^VTN$`, `^LUM$`, `^COL` | fibronectin, fibulin, gelsolin, actin, vitronectin, collagen |
| 8 | Unassigned | anything else, including `Uncharacterized protein` and `LOC` symbols | |

    Store the rules (as above) in the payload so a reader can audit them. Where the article's own text names a class for a protein (CB112 Discussion: complement CFI, CFP, C2, SERPING1, C8G; acute-phase ORM1, ITIH2, ITIH4; extracellular matrix TGFBI), the rule table above already agrees; do not read `data/markdown/` at run time (it is git-ignored).
14. **Sensitivity analyses** (performance and univariable families only, `outer_repeats` = 5 to save time): (a) complete-case proteins only, no imputation; (b) within-plex centring (subtract each protein's plex mean, computed on all samples of that plex, after step 3). Also report a chi-square (permutation, 10,000) of `tmt_plex` × `disease_group` as a confounding check. Store under `model_performance.sensitivity` and `univariable_screen.sensitivity`.
15. **`--shuffle-labels` flag** (for acceptance only): permutes the class labels once with `seed + 1` before step 6 and writes to `data/experiments/EXP04-DS07-proteome-shuffled.json` only when `--out` is given; never overwrite the main file with a shuffled run. Default: off.

## 4. Outputs

### 4.1 Experiment JSON

`data/experiments/EXP04-DS07-proteome.json`.

`experiment` block:

- `code` `EXP04-DS07-proteome`; `name` `Serum proteome classes in B. rossi babesiosis (DS07)`; `description` one paragraph naming both passes, the models and the permutation test; `method` `proteome`; `dataset` `DS07`; `script` `scripts/experiment_proteome.py`; `script_version` first 12 hex characters of the sha256 of the script file; `run_utc`; `n_subjects` 52; `n_variables` = proteins analysed in pass 1; `n_tests` = number of associations written; `summary` = one plain-text paragraph with the stable-panel sizes, the two observed balanced accuracies with permutation p values, and the number of BH-significant proteins per family.
- `parameters` (all defaults):

```json
{
  "seed": 20261105,
  "min_unique_peptides": 2,
  "min_detect_frac": 0.5,
  "normalisation": "per-sample median over proteins complete in all samples",
  "imputation": "training-fold protein minimum minus 1 (log2)",
  "outer_folds": 5, "outer_repeats": 20, "inner_folds": 4,
  "spls_ncomp_multiclass": 2, "spls_ncomp_binary": 1, "spls_keepx_grid": [5, 10, 20, 40],
  "enet_C_grid": [0.01, 0.03, 0.1, 0.3, 1, 3], "enet_l1_ratio_grid": [0.5, 0.9],
  "enet_max_iter": 20000, "enet_tol": 0.0001, "class_weight": "balanced",
  "stability_subsamples": 100, "stability_fraction": 0.5, "stability_threshold": 0.7,
  "permutations_spls": 200, "permutations_enet": 100,
  "perm_outer_folds": 5, "perm_outer_repeats": 2,
  "kw_permutations": 10000, "bootstrap": 2000, "alpha": 0.05,
  "adjustment": "benjamini_hochberg",
  "article_table": "data/raw/S-CB112/PMC10290096_supplementaryFiles.zip!41598_2023_37312_MOESM1_ESM.xlsx!Table S1",
  "shuffle_labels": false
}
```

`associations[]` (written): one row per Family A and Family B test.

- Family A: `variable_a` = protein code, `variable_b` = `disease_group`, `test` `kruskal_wallis`, `estimate` eta², `estimate_label` `eta_squared`, `n`, `p_value` (permutation), `p_adjusted` (BH, whole run), `significant`, `trivial` false, `direction` = group with the highest median (`control`, `uncomplicated` or `complicated`), `detail` `{"statistic": H, "ci_low":…, "ci_high":…, "medians": {"control":…, "uncomplicated":…, "complicated":…}, "n_by_group": {...}, "in_article_s1": true}`.
- Family B: `variable_b` = `severity_class`, `test` `mann_whitney`, `estimate` rank-biserial r, `estimate_label` `rank_biserial`, `direction` `higher in complicated` / `lower in complicated`, `detail` `{"U":…, "hl_shift_log2":…, "ci_low":…, "ci_high":…, "article_log2fc_bc": number or null}`.

`cluster_assignments[]`: empty list (the method produces no subject clusters).

`results[]`:

| kind | title | sort_order | payload |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | `{"sections": [{"heading": …, "paragraphs": [...]}]}` |
| `protein_panel` | Stable protein panels per contrast | 1 | see below |
| `model_performance` | Cross-validated performance against the permutation null | 2 | see below |
| `univariable_screen` | Univariable screen and comparison with CB112 | 3 | see below |
| `pathway_groups` | Panel proteins grouped by protein class | 4 | see below |
| `run_notes` | Proteins analysed, filters, imputation, skipped tests | 5 | see below |

`protein_panel` payload:

```json
{"threshold": 0.7, "mb_bound": {"three_class": {"q": 9.4, "p": 112, "expected_false": 1.1}, "complicated_vs_uncomplicated": {...}},
 "contrasts": [
  {"contrast": "three_class", "n": 52, "proteins": [
    {"code": "prot_A1B2C3", "gene": "CD14", "name": "CD14 – Monocyte differentiation antigen CD14",
     "freq_enet": 0.93, "freq_spls": 0.88, "freq_outer_cv": 0.95, "stable_both": true,
     "direction": "highest in complicated", "coef_sign_by_class": {"control": -1, "uncomplicated": 0, "complicated": 1},
     "hl_shift_log2": null, "p_adjusted_univariable": 0.0004, "in_article_s1": true, "in_article_table1": true, "protein_class": "Immunoglobulins and innate immunity"}]},
  {"contrast": "complicated_vs_uncomplicated", "n": 32, "proteins": [...]}],
 "all_frequencies": {"three_class": [{"code": "...", "freq_enet": 0.12, "freq_spls": 0.05}], "complicated_vs_uncomplicated": [...]}}
```

`model_performance` payload:

```json
{"contrasts": [
  {"contrast": "three_class", "n": 52, "class_counts": {"control": 20, "uncomplicated": 18, "complicated": 14},
   "events_per_variable": null,
   "models": [
    {"model": "spls_da", "balanced_accuracy": {"mean": 0.81, "sd": 0.04, "p2_5": 0.73, "p97_5": 0.88},
     "auc": null, "recall_by_class": {...}, "confusion_matrix": {"labels": [...], "counts": [[...]]},
     "chosen_hyperparameters": {"keepX": {"10": 41, "20": 59}},
     "permutation": {"scheme": "5x2", "observed": 0.80, "null_mean": 0.34, "null_p95": 0.45, "p": 0.005, "B": 200}},
    {"model": "elastic_net", "...": "..."}]},
  {"contrast": "complicated_vs_uncomplicated", "n": 32, "events_per_variable": 0.125, "models": [...]}],
 "chance_balanced_accuracy": {"three_class": 0.333, "complicated_vs_uncomplicated": 0.5},
 "plex_confounding": {"chi_square": 12.3, "p": 0.6},
 "sensitivity": [{"analysis": "complete_case_proteins", "n_proteins": 96, "contrasts": [...]}, {"analysis": "within_plex_centring", "...": "..."}]}
```

`univariable_screen` payload: `{"families": [{"family": "kruskal_wallis_disease_group", "n_tests": 112, "n_significant": 70, "top": [first 30 rows by p_adjusted with code, gene, eta2, ci, p, p_adjusted, direction, medians]}, {"family": "mann_whitney_severity_class", ...}], "article_comparison": {"s78": {"overlap": 60, "ours_only": 10, "article_only": 18, "jaccard": 0.68}, "s21": {"overlap": 15, "sign_agreement": 15, "jaccard": 0.5}, "stable_binary_panel_vs_s21": {...}}, "sensitivity": [...]}`.

`pathway_groups` payload: `{"rules": [{"order": 1, "class": "Complement", "gene_patterns": [...], "keywords": [...]}, ...], "contrasts": [{"contrast": "three_class", "groups": [{"class": "Complement", "proteins": ["CFI", "CFP"], "n_panel": 2, "n_analysed": 14}]}, ...], "analysed_by_class": {"Complement": 14, ...}}`.

`run_notes` payload: `{"proteins_total": 224, "proteins_analysed_pass1": 112, "proteins_analysed_pass2": 110, "dropped": [{"code": ..., "reason": "fewer than 2 unique peptides" | "quantified in 20/52"}], "normalisation_shift": {"min": ..., "median": ..., "max": ...}, "imputed_cells_fraction": 0.09, "skipped_tests": [...], "enet_constructor": "LogisticRegression(solver='saga', ...)", "convergence_warnings": 0, "runtime_seconds": ..., "environment": {"python": "3.12.12", "numpy": "1.26.4", "scikit_learn": "1.9.1", "scipy": "1.17.1"}}`.

`interpretation` sections (headings, in order): `Question`, `What was done`, `Healthy versus infected`, `Complicated versus uncomplicated`, `How this compares with the article`, `Limits`. Numbers in every section; plain language for a veterinary reader.

### 4.2 Other artefacts

- `data/tidy/DS07.json` (task 2).
- No CSVs or figures. Everything else lives in the experiment JSON.

## 5. Acceptance checks

1. Tidy file: 52 subjects (20 control, 18 uncomplicated, 14 complicated); 224 protein variables + 5 design or technical variables; 112 proteins with `include_default = true`; no observation from plex F11 channels 129 to 131. Spot check: subject `1z` (plex B1, channel 127), variable `prot_F1P8Z5` (APOB) has `value_num` = log2(0.719) = −0.476. Subject `20z` and `56` are the only B11 samples.
2. The console loads both files without error: `dotnet run --project console/Babesiosis.Console -- --datasets-only` from the repository root. SQL: `SELECT COUNT(*) FROM dbo.subject s JOIN dbo.dataset d ON d.dataset_id = s.dataset_id WHERE d.dataset_code = 'DS07'` returns 52 (check the exact column names in `console/Babesiosis.Console/Database/schema.sql`); `SELECT COUNT(*) FROM dbo.association a JOIN dbo.experiment e ON e.experiment_id = a.experiment_id WHERE e.experiment_code = 'EXP04-DS07-proteome'` equals `n_tests`; six rows in `dbo.experiment_result` for the code.
3. Counts: `n_subjects` = 52, `n_variables` = proteins analysed in pass 1, `n_tests` = len(associations).
4. Reproducibility: run twice with the same seed; the two JSON files are identical apart from `run_utc` and `runtime_seconds`.
5. Null behaviour: a `--shuffle-labels --out <scratch path>` run gives three-class balanced accuracy within 0.333 ± 0.1 and binary within 0.5 ± 0.1, and BH-significant associations in at most 5 % of tests. Delete the shuffled file afterwards; it must not stay in `data/experiments/`.
6. Sanity against CB112: Family A finds most of the 78 Table S1 proteins (expect Jaccard above 0.5; report whatever it is); controls separate from infected dogs with three-class balanced accuracy well above chance; CD14, ITIH4 and APOE are higher and RBP4 lower in complicated than uncomplicated dogs in Family B (direction, whatever the significance).
7. sPLS-DA check: on a synthetic two-class matrix with 5 informative of 100 features (n = 40, seed fixed), the implementation selects the informative features with keepX = 5 and balanced accuracy above 0.9. Run this as a `--self-test` flag that prints PASS/FAIL and writes nothing.
8. The interpretation reads correctly for a veterinary reader, states the permutation p next to every accuracy, and never calls a panel a diagnostic or prognostic test.

## 6. Caveats and reporting language

- Features outnumber samples: 112 analysed proteins against 52 dogs, and 32 dogs (14 events) in the key contrast, an events-per-variable ratio of about 0.13. (The plan page said "thousands of proteins"; the processed export has 224 master proteins, 112 after the article's filters.) A single cross-validated accuracy is not meaningful without the permutation null; always report both.
- Controls are healthy, younger (median 21 versus 28 months) and unmatched; healthy versus infected separation is largely an acute-phase signal and is expected, not a discovery.
- Label leakage: "complicated" was defined partly by haematocrit, urea, creatinine, bilirubin, glucose, lactate, collapse, cerebral signs and death within 24 hours. Proteins that track those organ-function measures will separate the classes by construction.
- Treatment and sampling time are unknown (retrospective archived serum); diminazene, transfusion or fluids may have preceded sampling.
- Missing values are plex-linked and abundance-dependent; imputation at the training minimum assumes left-censoring. The complete-case sensitivity analysis shows how much depends on it.
- Batch: 11 TMT plexes; groups are spread across plexes but not perfectly balanced, and plex 11 has two samples.
- Same dogs as the article: agreement with Table S1 or Table 1 is a reproduction check, not independent replication. One cohort, one source (SRC-C).
- Wording: "stable panel" and "candidate markers", never "biomarker signature", "diagnostic test" or "prognostic score". Protein classes come from a fixed keyword table, not from enrichment analysis, and are a reading aid.

## 7. Build plan for the agent

All commands from `C:\Workspaces\Babesiosis\core` unless stated.

1. **Read.** `experiment_specs/README.md`, this spec, `scripts/tidy_ds05.py`, `scripts/experiment_pairwise.py` (helpers `rankdata`, `bh_adjust`, permutation loop, output writer), `data/inspection/DS07.json`, the DS07 record in `datasets.jsonl`, `articles/CB112_2023_serum-proteome-profiling-naturally-acquired-babesia.md`. Done when you can state the TMT layout and the 52-to-channel mapping.
2. **Tidy.** Write `scripts/tidy_ds07.py` (section 2.2) and run `.venv/Scripts/python.exe -I scripts/tidy_ds07.py`. Done when it prints `DS07: 52 subjects, 229 variables, <n> observations` and acceptance check 1 passes (check with a short `python -I -c` that prints only counts and the spot-check value).
3. **Script.** Write `scripts/experiment_proteome.py` with a module docstring that states inputs (`data/tidy/DS07.json`, the S-CB112 zip), output, the run command, the flags (`--seed`, `--quick`, `--self-test`, `--shuffle-labels`, `--out`, and one flag per parameter in section 4.1) and the dependencies (numpy, scipy, scikit-learn; `.venv-nlp`). `--quick` sets `outer_repeats` 2, permutations 10, stability 20, `kw_permutations` 1000, for development only, and writes `"quick": true` into parameters. Add `scikit-learn>=1.5` and `scipy>=1.11` to `scripts/requirements-experiments.txt`. Done when `--self-test` prints PASS and a `--quick --out <scratchpad>/exp04-quick.json` run completes.
4. **Run.** `.venv-nlp/Scripts/python.exe -I scripts/experiment_proteome.py --code EXP04-DS07-proteome` (expected 30 to 60 minutes; the permutation loops dominate). Done when `data/experiments/EXP04-DS07-proteome.json` exists, is under 2 MB, and the script prints the summary paragraph.
5. **Load.** From `C:\Workspaces\Babesiosis`: `dotnet run --project console/Babesiosis.Console -- --datasets-only`. Then run the SQL checks in acceptance check 2 through the `babesiosis-local-db` MCP or `sqlcmd`.
6. **Verify.** Acceptance checks 3 to 8. Record the results (pass/fail with numbers) in your final report.
7. **Document.** Add rows for `tidy_ds07.py` and `experiment_proteome.py` to `scripts/README.md` (same style as the `experiment_pairwise.py` row, including the environment); add `DS07` and `EXP04-DS07-proteome` to the loaded-data lists in `docs/database.md` if that file enumerates them; set EXP04's status in `docs/ml-experiment-plan.html` to done if the page carries a status badge.
8. **Optional.** A dedicated web view under `webapp/Babesiosis.Web/src/app/modules/experiments/views/` for method `proteome` (panel table with frequency bars, performance against null). Only after everything above passes.

## 8. Open questions

1. **Imputation rule.** Left-censored "minimum minus 1 on log2" assumes missing means low abundance; the inspection notes say missingness follows plex. Default: as specified, plus the complete-case sensitivity analysis. Alternative if asked: k-nearest-neighbour imputation within plex.
2. **Plex adjustment in the main analysis.** The `datasets.jsonl` record recommends plex as a fixed or random effect. Default: no adjustment in the main analysis (ratios are already to the per-plex internal standard), within-plex centring as a sensitivity analysis, and the plex × group confounding check reported.
3. **Detection threshold for the second pass.** Default: re-apply `min_detect_frac` = 0.5 within the 32 infected dogs; proteins failing it are dropped from pass 2 only.
4. **Which model's selection defines the panel.** Default: elastic-net stability frequency ≥ 0.7 is the panel; sPLS-DA frequency is shown and `stable_both` flagged. If both are wanted as panels, add a second list rather than merging.
5. **Paired-label proteins in Table S1.** `J9P430` and `E2QZQ1` are both labelled TF in the article; keep them as separate variables (different accessions). Default: no merging of accessions that share a gene symbol.
6. **Article p values.** Some FDR values in CB112 Table 1 are smaller than their p values (for example FBLN1 p 4.6e-5, FDR 2.3e-5; PROS1 p 2.5e-4, FDR 1.1e-4), which BH adjustment cannot produce. Default: use the article's lists only as sets and signs, never its p values.
