# EXP02 DS05 clustering: admission phenotype structure in the BET cohort

| Field | Value |
|---|---|
| Experiment code | `EXP02-DS05-clustering` |
| Layer | 1 single dataset |
| Method token | `clustering` (goes in `experiment.method`) |
| Dataset(s) | `DS05` (150 dogs, `data/tidy/DS05.json`; independent source letter is in the tidy `dataset` block) |
| Readiness | ready (tidy file exists) |
| Python environment | `.venv-nlp` (numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.1 are installed). `.venv` has only numpy 2.5.4 and cannot run this script. `umap-learn` and `hdbscan` are NOT installed in either environment, and `.venv-nlp` has no `pip`. Do not install anything: the figure coordinates fall back to the first two principal components (section 3, step 11). Add `scipy>=1.13` and `scikit-learn>=1.5` to `scripts/requirements-experiments.txt` with a comment that EXP02 and EXP06 need them and must run in `.venv-nlp`; list `umap-learn` there as a commented optional line. |
| Estimated build effort | medium (2 to 4 hours of agent work) |
| Suggested model for the building agent | sonnet: many small, well-specified steps, no new statistics to invent |
| Depends on | `data/tidy/DS05.json`; `EXP01-DS05-pairwise` (read its `variable_clusters` result for the interpretation text) |

## 1. Question and hypotheses

Q1. Do the 150 dogs of the BET cohort (all Babesia PCR-positive, 146 B. rossi only) fall into recognisable admission phenotype groups, or do they form one continuum?
Q2. Which laboratory and clinical axes carry most of the variance, and do they match the three axes expected from physiology: a regenerative-anaemia axis (haemoglobin, haematocrit, RCC, reticulocytes), an inflammatory/left-shift axis (band and segmented neutrophils, monocytes, lymphocytes, platelets) and a protein axis (total protein, albumin)?

Expected: PCA axis 1 is anaemia, axis 2 inflammation, axis 3 protein. Cluster structure is expected to be weak (a continuum) because all dogs have the same disease.

Negative finding (a valid result, report it plainly): mean silhouette at the chosen k below 0.25, or bootstrap mean Jaccard below 0.6 for most clusters, or the parametric-null silhouette p value above 0.05. Then the interpretation says the cohort is a continuum along the PCA axes, not a set of groups, and the clusters are only a convenient partition.

## 2. Data

### 2.1 Sources

- `data/tidy/DS05.json`: 150 subjects (`BET001` to `BET150`); `group_label` counts `B. rossi only` 146, `B. rossi + E. canis` 3, `B. vogeli only` 1; `outcome_label` is null for all (no outcome, nothing here is prognostic).
- Raw: `data/raw/DS05/BET Study Dataset.xlsx` (read-only; this script does not read it).
- Licence and `independent_source`: copy from `tidy["dataset"]` into `run_notes`.

### 2.2 Tidy file required

Not applicable: the tidy file exists.

### 2.3 Variables and filters

Clustering input rule: `data_type in (N, O)` and `include_default = true` and `derived = false` and `derived_from` null or empty. This gives **22 variables**:
`age_months, weight_kg, illness_days, temperature_c, pulse, respiratory_rate, lymph_node_score, haemoglobin, rcc, haematocrit, rdw, seg_neutrophils, band_neutrophils, lymphocytes, monocytes, eosinophils, platelets, nrbc_per_100_wbc, reticulocyte_pct, total_protein, albumin, habitus_score`.

The tidy file marks `mcv, mch, mchc, wcc, arc, globulin` as `derived = false` but they carry `derived_from` (arithmetic functions of other columns; `wcc` is the sum of the six differential counts, `globulin` = total_protein - albumin). The `derived_from` condition above excludes them so that no axis is built from a variable and its own parts. State this in `run_notes`. Sensitivity S4 adds them back.

Excluded as not input: `basophils`, `other_cells` (`include_default = false`), `month`, and all `C`, `D`, `T` variables.

Held out for comparison (never enter clustering): the authors' derived classes `anaemia_class, left_shift, habitus_class, illness_class, arc_class`, plus `pcr_e_canis` and `group_label`. Circularity to state in the interpretation: `anaemia_class` is cut from `haematocrit`, `left_shift` from `band_neutrophils` and `seg_neutrophils`, `habitus_class` from `habitus_score`, `illness_class` from `illness_days`, `arc_class` from `arc` (itself from `reticulocyte_pct` and `rcc`). All parents except `arc` are inputs, so agreement with these classes is expected by construction and is a sanity check, not a discovery. Record per class which parents are inputs (`parents_in_input`) and set `circular = true`.

Missing data (from the tidy file): 37 of 150 dogs miss at least one of the 22 variables. Observed counts: `respiratory_rate` 126, `temperature_c` 145, `illness_days` 148, `habitus_score` 147, all haematology 148, `total_protein` and `albumin` 144. Dogs `BET065` and `BET066` have no haematology or biochemistry at all.

Rules:
1. Drop any dog missing more than 30 percent of the 22 variables (parameter `max_missing_subject = 0.30`). This removes `BET065` and `BET066`, leaving **148 dogs**. They get no cluster assignment and are listed in `run_notes.dropped_subjects`.
2. Drop any variable missing in more than 30 percent of the remaining dogs (`max_missing_variable = 0.30`). With defaults none is dropped (`respiratory_rate` is about 16 percent missing); keep the check in code.
3. Impute remaining gaps once, on the 148-dog matrix after transformation and standardisation, with `sklearn.impute.IterativeImputer(estimator=BayesianRidge(), max_iter=20, sample_posterior=False, initial_strategy="median", random_state=child seed)`. Record imputed cells per variable.
4. Imputation is done once before resampling, not inside each bootstrap. State this as a limit.

## 3. Method

All randomness comes from one `numpy.random.default_rng(seed)`; draw child seeds with `rng.integers(0, 2**31 - 1)` in a fixed order and pass them as `random_state`. Default `seed = 20261105` (as EXP01). The run reproduces bit-for-bit.

1. **Load.** Subjects x variables matrix from `value_num` (N and O). Held-out categorical table from `value_text`.
2. **Transform.** For each input variable that is non-negative with absolute skewness above 1.0 (`skew_threshold`), replace x by log1p(x). The rule decides, applied uniformly; record which variables were transformed.
3. **Filter, impute, standardise.** Apply section 2.3, then standardise every column to mean 0 and SD 1 (ddof=1) over the 148 dogs. Clip standardised values to +/-4 (`clip_z = 4.0`) for clustering only; record clipped cells. Ordinal variables (`lymph_node_score`, `habitus_score`) are treated as numeric (state this).
4. **PCA.** `PCA(svd_solver="full")` on the standardised matrix. Retain axes by parallel analysis: 500 seeded column-wise permutations (`pa_permutations = 500`), keep axes whose eigenvalue exceeds the 95th percentile of the permuted eigenvalues. Also record the Kaiser count (eigenvalue > 1). `n_axes` = parallel-analysis count, forced into 2 to 8.
5. **Factor analysis.** `FactorAnalysis(n_components=n_axes, rotation="varimax", random_state=child seed)` on the same matrix; store rotated loadings beside the PCA loadings for readability. Describe each axis in the text as "led by" its top 3 absolute loadings; do not invent names.
6. **Choose k.** Candidates k = 2 to 8 (`k_min = 2`, `k_max = 8`). A k is admissible only if the smallest cluster has at least `min_cluster_size = 8` dogs.
   a. Hierarchical: `AgglomerativeClustering(linkage="ward")` on the standardised 22-variable matrix; mean Euclidean silhouette per k.
   b. Gaussian mixture on the first `n_axes` PCA scores: `GaussianMixture(covariance_type in {"diag","full"}, n_init=10, random_state=child seed)`; BIC per k and covariance type. Use the covariance type with the lowest BIC overall.
   c. Chosen k = admissible k with the highest Ward mean silhouette. Report the GMM BIC-optimal k beside it; if different, say so and report the adjusted Rand index (ARI) between the Ward and GMM partitions at the chosen k.
   d. Parametric null: simulate `null_sims = 200` Gaussian datasets of the same size and sample correlation as the standardised matrix, run the identical Ward silhouette search (same k range and admissibility rule), and report p = (count of simulations with best silhouette >= observed + 1) / (sims + 1).
7. **Final partition.** Ward partition at the chosen k. Relabel `C1`..`Ck` by decreasing size (ties: lower mean PC1 score first). Per-dog `score` = that dog's silhouette (-1 to 1).
8. **Stability.**
   a. Bootstrap (Hennig clusterwise Jaccard): `n_boot = 200` resamples with replacement; recluster with Ward at the chosen k; per original cluster take the maximum Jaccard to any bootstrap cluster. Report mean, median and the share of runs with Jaccard >= 0.6. Quote the guide: mean below 0.6 unstable, 0.6 to 0.75 a pattern with uncertainty, above 0.75 stable, above 0.85 highly stable.
   b. Consensus: `n_consensus = 200` subsamples of 80 percent of dogs without replacement (`consensus_fraction = 0.8`), Ward at the chosen k; co-clustering proportion over pairs sampled together. Report the matrix (dogs ordered by final cluster), mean within-cluster consensus per cluster, mean between-cluster consensus, and PAC (share of pairs with consensus in 0.1 to 0.9).
   c. Mean bootstrap Jaccard (all clusters averaged) for every admissible k, so the reader sees whether the chosen k is special.
9. **Cluster summary.** Per cluster and per input variable, in original units before transformation and using non-imputed values only: median, 25th and 75th percentile, n observed. Also cluster size and median silhouette. `distinguishing`: variables whose cluster median differs from the median of the other dogs by at least 0.8 (difference divided by 1.4826 x overall MAD), top 6 by size.
10. **Cross-tabulations.** For each of `anaemia_class, left_shift, habitus_class, illness_class, arc_class, pcr_e_canis, group_label`: cluster x class table over dogs with the class observed. Merge levels with fewer than 5 dogs (`min_level = 5`): with the current data only `left_shift` `De_L_shift` (1 dog) is affected and it is merged into `L_shft` (label "left shift present"); any other rare level goes into `Other`. Record each merge. Compute chi-square, Cramer's V, a permutation p value (`perm = 5000`, shuffle class labels, same algorithm as `chi_square()` in `scripts/experiment_pairwise.py`, copied, not imported, because `-I` removes the script folder from the import path), and a 95 percent bootstrap percentile interval for V (`ci_boot = 1000`). Benjamini-Hochberg across the 7 tests (copy `bh_adjust`). `pcr_e_canis` (3 positives) and `group_label` (3 and 1 minority dogs) get `descriptive_only = true` and the text says "too few dogs to test". `pcr_b_rossi` (149/1), `pcr_b_vogeli` (1/149) and `pcr_t_equi` (0/150) are not tabulated; say so in `run_notes`.
11. **Figure coordinates.** If `import umap` succeeds: `umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=child seed)` on the standardised matrix, `method: "umap"`. Otherwise (the present state) the first two PCA scores, `method: "pca"`. Never fail on the missing package. Coordinates are for plotting only and feed no statistic.
12. **Sensitivity analyses.** Each reruns steps 3 to 7 with one change and reports chosen k, silhouette, ARI against the main partition on the shared dogs, and Tucker congruence of PC1 to PC3 loadings with the main ones:
    - S1 complete case: dogs with all 22 variables observed (about 111), no imputation.
    - S2 median imputation instead of iterative imputation.
    - S3 drop `respiratory_rate` and `temperature_c` (most missing clinical variables).
    - S4 add back `mcv, mch, mchc, wcc, arc, globulin`.
    - S5 no log transform.
    Call the result robust only if S1 and S2 give the same k or an ARI of at least 0.6 with the main partition.
13. **Write output** (section 4) and print the summary paragraph, chosen k, silhouette, per-cluster mean Jaccard, and the crosstab V with adjusted p.

## 4. Outputs

### 4.1 Experiment JSON

File `data/experiments/EXP02-DS05-clustering.json`; top-level keys `experiment`, `associations`, `cluster_assignments`, `results`.

`experiment`: `code` = `EXP02-DS05-clustering`; `name` = "Admission phenotype structure, BET cohort"; `description` one plain sentence (exploratory phenotype groupings of 148 dogs; no outcome; not subtypes); `method` = `clustering`; `dataset` = `DS05`; `script` = `scripts/experiment_clustering.py`; `script_version` = first 12 hex characters of the script's SHA-256; `run_utc`; `n_subjects` = 148; `n_variables` = 22; `n_tests` = 7; `summary` = one paragraph (dogs, variables, chosen k, mean silhouette, null p, mean Jaccard, strongest crosstab).

`parameters` (defaults): `{"seed": 20261105, "skew_threshold": 1.0, "clip_z": 4.0, "max_missing_subject": 0.30, "max_missing_variable": 0.30, "imputation": "iterative_bayesian_ridge", "imputer_max_iter": 20, "pa_permutations": 500, "k_min": 2, "k_max": 8, "min_cluster_size": 8, "linkage": "ward", "gmm_covariance_types": ["diag","full"], "gmm_n_init": 10, "null_sims": 200, "n_boot": 200, "n_consensus": 200, "consensus_fraction": 0.8, "min_level": 5, "perm": 5000, "ci_boot": 1000, "alpha": 0.05, "adjustment": "benjamini_hochberg", "umap": {"n_neighbors": 15, "min_dist": 0.1}, "held_out": ["anaemia_class","left_shift","habitus_class","illness_class","arc_class","pcr_e_canis","group_label"], "input_variables": [the 22 codes]}`.

`associations`: empty list (a cluster label is not a variable code).

`cluster_assignments`: 148 rows `{"subject_code": "BET001", "cluster_label": "C1", "score": 0.2134}` (silhouette, 4 decimals). `BET065` and `BET066` are not written.

`results[]` (4 decimals; each payload well under 2 MB):

| kind | sort_order | title | payload |
|---|---|---|---|
| `interpretation` | 0 | Explanation and interpretation | `{"sections": [{"heading": str, "paragraphs": [str]}]}` |
| `pca_axes` | 1 | Principal axes, loadings and explained variance | `{"variables": [22 codes], "n_axes": int, "kaiser_count": int, "parallel_analysis": {"observed": [float], "threshold_95": [float]}, "axes": [{"axis": "PC1", "eigenvalue": float, "explained_variance_ratio": float, "cumulative": float, "loadings": {"haemoglobin": -0.31}, "top_variables": ["haematocrit","haemoglobin","rcc"], "varimax_loadings": {"haemoglobin": -0.8}}], "transformed_variables": [codes], "scores": [{"subject_code": "BET001", "pc1": 0.1, "pc2": -1.2}]}` |
| `cluster_summary` | 2 | Cluster profiles (medians, original units) | `{"k": int, "clusters": [{"label": "C1", "n": int, "median_silhouette": float, "variables": {"haematocrit": {"median": 0.2, "q1": 0.15, "q3": 0.25, "n": 60}}, "distinguishing": [{"variable": "haemoglobin", "std_diff": -1.2, "direction": "lower"}]}], "overall": {"haematocrit": {"median": 0.22, "q1": 0.16, "q3": 0.3, "n": 148}}, "embedding": {"method": "pca", "points": [{"subject_code": "BET001", "x": 0.1, "y": -1.2, "cluster": "C1"}]}}` |
| `cluster_stability` | 3 | Choice of k, null test, bootstrap and consensus stability | `{"k_search": [{"k": 2, "ward_silhouette": float, "gmm_bic_diag": float, "gmm_bic_full": float, "min_cluster_size": int, "admissible": bool, "mean_jaccard": float}], "chosen_k": int, "gmm_best_k": int, "gmm_covariance": "diag", "ari_ward_gmm": float, "silhouette_null": {"observed": float, "null_p95": float, "p_value": float, "sims": 200}, "bootstrap": {"clusters": [{"label": "C1", "mean_jaccard": float, "median_jaccard": float, "share_ge_0_6": float}]}, "consensus": {"order": [codes], "matrix": [[float]], "mean_within": {"C1": float}, "mean_between": float, "pac": float}, "sensitivity": [{"name": "S1_complete_case", "n_subjects": int, "chosen_k": int, "silhouette": float, "ari_vs_main": float, "tucker_pc1_3": [float]}]}` |
| `cluster_crosstabs` | 4 | Clusters against the authors' classes and PCR | `{"tests": [{"class_variable": "anaemia_class", "n": int, "levels_merged": str or null, "parents_in_input": ["haematocrit"], "table": {"C1": {"Ht_S": int}}, "chi_square": float, "cramers_v": float, "v_ci95": [lo, hi], "p_value": float, "p_adjusted": float, "significant": bool, "descriptive_only": bool, "circular": bool}]}` |
| `run_notes` | 5 | Variables, missing data, dropped dogs and transformations | `{"input_variables": [{"code": str, "name": str, "unit": str, "n_observed": int, "n_imputed": int, "transformed": bool, "clipped_cells": int}], "excluded_derived_from": ["mcv","mch","mchc","wcc","arc","globulin"], "dropped_subjects": [{"subject_code": "BET065", "reason": "no haematology or biochemistry"}], "dropped_variables": [], "not_tabulated": ["pcr_b_rossi","pcr_b_vogeli","pcr_t_equi"], "imputation": {"method": str, "cells_imputed": int}, "environment": {"numpy": str, "scipy": str, "scikit_learn": str, "umap_available": false}, "dataset": {"independent_source": str, "licence": str}}` |

`interpretation` section headings, exactly: "Question", "What was done", "Main axes", "Do the dogs form groups?", "Comparison with the authors' classes and co-infection", "Robustness to missing data", "Limits". Plain language for a veterinary reader; every number is computed, none typed. Use the EXP01 `variable_clusters` result (in `data/experiments/EXP01-DS05-pairwise.json`) to say whether an axis only repeats one strong pairwise correlation.

### 4.2 Other artefacts

None. No images or CSVs.

## 5. Acceptance checks

1. The script runs with `.venv-nlp/Scripts/python.exe -I`, no network, no unlisted package, and prints the summary.
2. JSON keys are exactly as in 4.1; `n_subjects` = number of `cluster_assignments` = 148; every `subject_code` exists in `data/tidy/DS05.json`; every label is at most 30 characters; `n_variables` = 22 = length of `parameters.input_variables`; `n_tests` = 7.
3. Two runs with the same seed give identical files except `run_utc`.
4. PCA: explained variance ratios over all axes sum to 1 within 1e-6. If PC1 is not led by red-cell variables, name what leads it in the text (a finding, not an error).
5. Per-dog silhouettes lie in [-1, 1] and their mean equals the reported silhouette for the chosen k to 4 decimals.
6. Permutation sanity: shuffle `anaemia_class` in a test harness (nothing saved) 100 times; p_value above 0.05 in at least 90 of them.
7. `anaemia_class` x cluster should give Cramer's V of at least 0.3 if haematology drives PC1; if not, check the code before accepting.
8. Sensitivity S1 to S5 present; ARI in [-1, 1]; the text states robust or not by the step-12 rule.
9. Interpretation uses "phenotype group" or "cluster", never "subtype", claims no clinical use, and reports a negative result honestly if the section-1 criteria hold.
10. After the console load, `dbo.cluster_assignment` holds 148 rows for this experiment and `dbo.experiment_result` holds the six kinds.

## 6. Caveats and reporting language

- 148 dogs, 22 correlated variables; exploratory. Clusters are phenotype groupings, never "subtypes". Nothing is prognostic: DS05 has no outcome.
- One hospital cohort; B. rossi in 146 of 150 dogs. The 3 E. canis co-infected dogs and the 1 B. vogeli dog support counts only, no tests.
- The authors' classes are cut from variables used here, so agreement is partly by construction (`circular`).
- Imputation once before resampling: stability is optimistic for `respiratory_rate` (about 16 percent imputed) and `temperature_c`.
- Admission cross-section: group membership says nothing about the course of disease.
- Silhouette below 0.25 means a continuum; say so.
- Entry or unit errors in the raw sheet can drive an axis; EXP06 lists atypical dogs and these are checked against the raw sheet.

## 7. Build plan for the agent

1. **Read.** `experiment_specs/README.md`, `TEMPLATE.md`, `core/CLAUDE.md`, this spec, `scripts/experiment_pairwise.py` (docstring, `rankdata`, `bh_adjust`, `perm_p`, `chi_square`, argparse, how `experiment` and `results` are built and `script_version` hashed), `data/tidy/DS05.json` (variables), `data/experiments/EXP01-DS05-pairwise.json` (`variable_clusters`). Done: you can list the 22 input variables from memory of the file.
2. **Tidy.** None. Done: `data/tidy/DS05.json` exists.
3. **Script.** Write `scripts/experiment_clustering.py` with a module docstring (inputs, outputs, run command, dependencies numpy, scipy, scikit-learn, optional umap-learn) and one argparse option per parameter in 4.1, with the stated defaults. Copy `bh_adjust`, `perm_p` and the chi-square test; do not import `experiment_pairwise.py`. Update `scripts/requirements-experiments.txt`. Done: `--help` lists every parameter.
4. **Run.** From `core/`:
   `.venv-nlp/Scripts/python.exe -I scripts/experiment_clustering.py --dataset DS05 --code EXP02-DS05-clustering --name "Admission phenotype structure, BET cohort" --seed 20261105`
   Expected runtime under 3 minutes. Done: the file exists and the summary is printed.
5. **Load.** Run `Babesiosis.Console --datasets-only` (`appsettings.json` `ReviewRoot` must point at `core/`). Check via `babesiosis-local-db` (read `docs/database.md` for table and column names first): the count of `dbo.cluster_assignment` rows for `EXP02-DS05-clustering` is 148 and `dbo.experiment_result` has the six kinds.
6. **Verify.** Run every check in section 5; fix and rerun until all pass.
7. **Document.** Add `experiment_clustering.py` to `scripts/README.md`; add the experiment to `docs/database.md` if experiments are listed there; update EXP02 status in `docs/ml-experiment-plan.html` if the page tracks status.
8. **Optional.** A web view under `webapp/Babesiosis.Web/src/app/modules/experiments/views/` (PCA scatter by cluster, loadings bars, consensus heatmap), only after tasks 1 to 7 pass.

## 8. Open questions

1. Arithmetic-derived variables (`mcv, mch, mchc, wcc, arc, globulin`): default excluded (22 variables); S4 shows the effect.
2. UMAP is not installed and `.venv-nlp` has no pip. Default: PCA coordinates; the script uses `umap` automatically if it is later installed.
3. Non-circular comparison with the authors' classes re-derived without parents. Default: not done; flag `circular`.
4. Final partition from Ward or GMM. Default: Ward at the silhouette-optimal k, GMM reported with ARI.
5. Cluster names. Default: only `C1`..`Ck`; the text describes each by its `distinguishing` variables.
6. Imputation inside each resample. Default: once, before resampling, listed as a limit.
7. Level order for merging rare classes in `anaemia_class` and `arc_class`: default merge into `Other` unless the order is stated in the variable `description` in `DS05.json`.
