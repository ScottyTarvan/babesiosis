# SV-G2. Severity literature extraction (schema v2)

| | |
|---|---|
| Wave | 0 |
| Lane | Groundwork for cross-study synthesis |
| Effort | Large |
| Working folder | `/experiments/SV-G2/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): "Literature inputs" only.

- **Goal.** Extend the marker-against-severity extraction from 10 articles to every tier A and B article with full text, and add the fields that SV-02 and SV-03 need.
- **Depends on.** Nothing. **Parallel:** batches of about 10 articles for each sub-agent; one JSON file per article, so writers never collide.
- **Scope.** `shortlist.csv` rows with `tier` A or B and `source_format` not `abstract`: 117 articles, 99 independent units. Ten are done; re-extract them under v2 as the calibration batch. The 34 abstract-only tier B articles form a later sensitivity set.
- **Method.** Follow `/core/data/severity/EXTRACTION_GUIDE.md` and `association_schema.json` exactly, with these additions (schema v2):
  - In each `severity_definitions` entry: `components` (a list from: death, collapse, cerebral, renal, hepatic or icterus, pulmonary, hypotension or shock, coagulopathy, haemoconcentration, hypoglycaemia, hyperlactataemia, pancreatitis, rhabdomyolysis, SIRS, MODS, anaemia grade, score, other); `euthanasia_included` (yes, no, not stated); `definition_source` (for example WHO malaria criteria, SIRS and MODS, author-defined, not stated); `follow_up_horizon`.
  - In each article: `setting` (referral hospital, primary clinic, laboratory submissions, shelter, experimental, not stated); `sample_timing` (before treatment, hours after treatment, not stated).
  - In each association: `severe_value` and `comparison_value` with `summary_type` (mean and SD, median and IQR, median and range, count and percent), copied as printed; `load_method` for parasitaemia rows (capillary smear, venous smear, qPCR, not stated).
  - Extract host and parasite factors with the same care as laboratory markers: age, sex, neuter status, breed, body weight, days sick, antibody status, co-infection, splenectomy, prior treatment, parasitaemia, parasite genotype. Most have canonical names in `marker_map.csv`; propose new names in a batch file.
- **Files.** Write to `SV-G2/extractions/<ID>.json`. Do not write in `/core/data/severity/`. Restore the checker into `SV-G2/scripts/` (`git show 8d4c6d9:core/scripts/check_associations.py`), point it at `SV-G2/extractions/`, and extend it for the v2 fields. New marker names go to `SV-G2/marker_map_additions/<batch>.csv`; the owner merges them.
- **Quality.** Every quote must pass the checker as `exact` or `near`. A second agent extracts a random 20% sample without seeing the first extraction; the owner reports agreement on outcome class, direction and significance, and resolves differences.
- **Outputs.** The extraction files; `SV-G2/associations_v2.csv` (one row per marker by definition by subgroup by analysis, with `cohort` filled from `/core/cohorts.json`); `SV-G2/definitions_v2.csv`; `report.md` with counts by species, outcome class and independent unit.
- **Do not.** Extract infected-against-healthy comparisons. Compute numbers that the article does not print. Count rows as evidence: count independent units.
