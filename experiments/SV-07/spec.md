# SV-07 spec: linkage audit

Frozen 2026-11-12 before the matching scripts were run. Package file: [../SV-07-linkage-audit.md](../SV-07-linkage-audit.md).

## Question

Which dogs appear in more than one file? This package has no severity test. It reads raw files directly. The S-CB050 table holds
an `Outcome` column and DS04 holds only fatal cases; both were already seen (the S-CB050 death list is in `data.md`). Outcome is used
only as a consistency check of a link (a DS04 dog must not link to a survivor), never as an analysis variable.

Experiment code `SV-07-01-linkage-audit`, method `linkage_audit`, role `descriptive`.

## Fixed rules

**Certainty classes** (`out/linkage.csv`):

- `confirmed by values`: at least three continuous values agree within rounding (below) and no recorded field contradicts the link.
- `probable`: the link rests on order, pattern or summary evidence whose chance probability is below 0.01, or on two independent
  kinds of evidence that agree, with no contradiction.
- `unverified`: anything else, including weak-identifier candidates (age, weight, sex) and links that a recorded field contradicts.

**Rounding tolerance.** Two values agree if they differ by at most 0.011 in absolute terms (both files print two decimals) or
by at most 0.5% of the larger value, whichever is wider. A "near" match (reported, never a link) is within 5% on every value.

## Steps

1. **DS04 haematology rows to DS04 case numbers.** Evidence, each reported separately:
   a. the row order of `stats for haematology.xlsx` against the case order of every sheet of `Stats Tables.xlsx`;
   b. WBC, segmented and band neutrophil triples against all 161 rows of S-CB050, plus age (DS04 years x 12), weight (within 0.5 kg)
      and sex of the matched case;
   c. icterus wording on the per-case score sheets (`icteric`, `icterus`, `yellow` = icteric) against total bilirubin above 30 umol/L.
      Chance probability: exact enumeration over all orders of the fatal rows that keep the S-CB050 matches fixed (7! orders), and
      over all 10! orders without them.
   Then name the DS04 case numbers of S-CB050 cases 126, 127 and 131.
2. **The other seven fatal DS04 dogs against S-CB050.** For each DS04 haematology row (all 14), the S-CB050 rows within rounding
   tolerance and within 5% on all three values, and the nearest row (largest relative difference over the three values).
   Signalment check against the matched case. Report matches and non-matches.
3. **DS03 natural against S-CB050 on age, weight and sex.** Candidate: same sex, same age in months, weight within 0.1 kg (both
   files have one decimal). For every DS03 dog: the number of S-CB050 dogs with that combination, and the number of DS03 dogs with it.
   Chance baseline: the same rule applied DS03 against DS05 (Eastern Cape, 2021: no shared dogs possible) and S-CB050 against DS05.
   Reported by DS03 cohort (1, 2, controls) against S-CB050 cohort (1 = cases 1–97 and controls 201–215, 2 = the rest). No link is
   asserted: every candidate is `unverified`, with its share count.
4. **DS06 sample names against DS02 dog numbers.** high_3 (series stops after day 3) against DS02 dog 6 (died on day 4): pattern.
   Value check, exploratory: per sample, log2 CPM mean of marker genes for lymphocytes (CD3E, CD3D, CD2, MS4A1, CD79A, CD79B),
   neutrophils (CSF3R, CXCR2, FPR1, MNDA) and monocytes (CD14, CSF1R) against the DS02 absolute lymphocyte, segmented neutrophil
   and monocyte counts on days 0, 1, 3, 4, 6, 8. Within a dose group, remove the group mean per day from both files, then score each
   assignment of DS06 names to DS02 dogs by the mean Spearman correlation of the residuals over the three cell types. Enumerate all
   assignments (high: 3! on days 0, 1, 3, a positive control that should put high_3 on dog 6; high 1/2 and low 1/2: 2 each on all days).
   A name pair becomes `probable` only if the positive control passes and the chosen assignment wins on at least two of the three cell
   types. Otherwise `unverified`. low_0 (one day-0 sample): `unverified`.
5. **DS07.** Read CB112 and CB147 (and CB145, CB050, CB115 for the cohort dates) for where and when samples were collected.
   Overlap of the 7 DS04 case numbers below 98 with the DS07 lists: hypergeometric probability over a universe of 1 to N, N = 91, 97
   and 144. Consistency of the DS04 signalment of those dogs with the CB112 group summaries (sex, neuter status, age range). Draft
   the author query in `out/author_query_draft.md`. Do not send it.

## What would count against

- Step 1: a contradiction between the order join and any of b or c (for example, a DS04 fatal row that matches an S-CB050 survivor).
- Step 3: candidate rates against S-CB050 that are no higher than against DS05 mean no evidence of overlap.
- Step 5: a contradiction between DS04 signalment and the CB112 summary for a number shared by both files.

## Outputs

`out/linkage.csv` (`dataset_a, id_a, dataset_b, id_b, basis, fields_matched, certainty`), `out/results.json`, plot-ready CSVs,
`out/author_query_draft.md`, `out/db/SV-07-01-linkage-audit.json`.
