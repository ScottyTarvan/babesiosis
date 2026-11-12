# SV-07. Linkage audit

| | |
|---|---|
| Wave | 0 |
| Lane | Groundwork |
| Effort | Small |
| Working folder | `/experiments/SV-07/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): "Linkage facts", `DS04`, `S-CB050`, `DS03`, `DS06`, `DS02`, `DS07`.

- **Goal.** Establish which dogs appear in more than one file, starting from "Linkage facts" in [data.md](data.md).
- **Depends on.** Nothing. Uses raw files directly (it may finish before SV-G1).
- **Steps.**
  1. Match DS04 haematology rows to DS04 case numbers, using `all tables from thesis.docx` and the per-case files. Then name the DS04 case numbers that correspond to S-CB050 cases 126, 127 and 131.
  2. Search S-CB050 for the other seven DS04 dogs with a tolerance for rounding. Report matches and non-matches.
  3. DS03 natural against S-CB050 on age, weight and sex. These fields identify a dog weakly: report candidate matches with a count of how many dogs share each combination. Do not assert a link.
  4. DS06 sample names against DS02 dog numbers: use the death on day 4 and the sample pattern; mark the rest unverified.
  5. DS07: read the CB112 and CB147 texts for statements about where and when the samples were collected. Draft a short query to the data owners about the case numbering of DS07, DS04, S-CB050 and CB145. Sending it is a user decision.
- **Outputs.** `out/linkage.csv` (`dataset_a, id_a, dataset_b, id_b, basis, fields_matched, certainty` with certainty one of confirmed by values, probable, unverified), `out/author_query_draft.md`, `report.md` with the consequence for `independent_source` (a proposal only: do not edit `/core/datasets.jsonl`).
- **Why it matters.** If DS07 dogs can be joined to a file with death, age and sex, SV-06b can use death in place of the circular "complicated" label.
