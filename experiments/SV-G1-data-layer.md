# SV-G1. Shared data layer

| | |
|---|---|
| Wave | 0 |
| Lane | Groundwork |
| Effort | Medium |
| Working folder | `/experiments/SV-G1/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): every dataset: read all of data.md.

- **Goal.** Tidy features and outcomes files for every dataset in the table in [data.md](data.md), and one variable dictionary.
- **Depends on.** Nothing. **Parallel:** one sub-agent per dataset; the owner merges the dictionary.
- **Steps.**
  1. The reader is in `shared/io/rawio.py`. Extend it there if a file needs more.
  2. For each dataset, read the `datasets.jsonl` record, then the raw file. Write the two tidy files (the tidy file contract in [rules.md](rules.md)). Record every cleaning decision in `cleaning_notes`. Do not correct a value silently: keep the raw value and add a flag.
  3. S-CB517 and S-CB516: convert the PDFs with `pdftotext -layout`. For S-CB517, check for 97 infected and 15 control rows, then compare the 7 cytokines with S-CB050 cases 1 to 97 and controls 201 to 215 and report the agreement (the record says this comparison was never made). For S-CB516, check for 8 dogs that died and 7 that survived.
  4. S-CB050: add `cohort` (1 for cases 1 to 97 and controls 201 to 215; 2 for the rest).
  5. DS02: long format, one record per dog and day, with `post_treatment` true or false. Exclude dog 1.
  6. DS07: one record per dog with log2 ratio to the plex standard for each master protein, plus `plex` and `channel`. Keep missing as `null`.
  7. DS06 is tidied by SV-08, not here.
  8. Write `dictionary.csv` with these harmonised names where the dataset has the variable: `age_months, weight_kg, sex, neuter, breed, illness_days, temp_c, hct, hb, rbc, mcv, mchc, retic_pct, arc, wbc, neut_seg, neut_band, lymph, mono, eos, plt, tsp, albumin, globulin, parasitaemia_pct, crp, saa, lactate, il2, il6, il8, il10, il18, gmcsf, mcp1, kc, mpxi`. Convert units to one unit per name and record the conversion (for example haematocrit as L/L).
- **Checks.** Row counts equal those in the dataset table in [data.md](data.md). Each features file reproduces three published summary numbers from its article note. A hash of each input is recorded.
- **Outputs.** `shared/tidy/*.json`, `shared/dictionary.csv`, `SV-G1/report.md` with a coverage table (variable by dataset).
- **Do not.** Put a severity label, a label-bearing ID or a derived severity class in a features file.
