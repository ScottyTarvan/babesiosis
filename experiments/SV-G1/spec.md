# SV-G1 spec

SV-G1 builds the shared data layer and runs no statistical test, so it has no outcome lock (ledger spec hash `–`).
This file fixes what the one descriptive experiment records.

**Experiment** `SV-G1-01-data-layer-coverage`, method `data_layer_coverage`, role `descriptive`.

**Datasets** (the table in `data.md`): S-CB050, S-CB517, DS07, S-CB017, S-CB516, DS05, DS03, DS02, DS04 (with S-CB147).
DS01 repeats DS02 and gets no file. DS06 is tidied by SV-08.

**Results stored**

1. `dataset_summary`: per dataset the source, species, dogs by group, records, timepoints, variables, harmonised variables,
   share of missing cells, censored cells, outcome names with the number of dogs that have them, checks passed, flags.
2. `coverage_matrix`: harmonised name by dataset, the share of dogs with at least one value.
3. `data_checks`: every check (row counts from `data.md`; at least three published summary numbers for each dataset).
4. `cleaning_flags`: every value kept as reported but flagged as a probable error or contradiction.
5. `dataset_links`: the files that share dogs, and the S-CB517 against S-CB050 cytokine agreement (package step 3).
6. `interpretation`.

**What would count as a failure**: a row count that differs from `data.md` without an explanation; a severity label,
label-bearing ID or derived severity class in a features file (the writer refuses it); a value changed without a note.
