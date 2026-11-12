# SV-07 report: linkage audit

Experiment `SV-07-01-linkage-audit` (method `linkage_audit`, role `descriptive`). Run 2026-11-12. Spec SHA-256 `be985d2414d9b0037f8e24e8d395164eaf4788ccc26f22f3e01a8a4a89d00bee`.

## 1. Question

Which dogs appear in more than one of the programme's files? There is no hypothesis test. The practical question: can DS07
(proteome, label "complicated") be joined to a file with death, age and sex?

## 2. Inputs

Raw files (SHA-256, first 12): S-CB050 `Table_1.DOCX` ec02b1d7a08f (zip 8113a933face); DS04 `stats for haematology.xlsx` 248bb18e79e3,
`Stats Tables.xlsx` 352c1bec22e2, `all tables from thesis.docx` 64dff05245fd and the 33 score sheets; DS03
`Babesia Retics_Natural inf and cont_dissertation.xlsx` 0a3e3e74835c; DS02 workbook a4a19a8d97e6; DS06 `GSE167201_raw_counts.txt.gz`
b2575d138ca0; DS07 `sample_list.xlsx` 3119957fa2b3; chance baseline `shared/tidy/DS05.features.json` 323238159fb2. Article texts read
(not copied): CB112, CB147, CB145, CB050, CB517, CB115. Spec hash above. Exposure log: `exposure.md`.

## 3. What was done

Python 3.12.12, standard library only (`scripts/analyse.py` cb43b93ac892, `scripts/build_load.py` e4a9d12738bc). Steps 1–5 of the
spec, in order. Rounding tolerance: max(0.011, 0.5%) for two-decimal counts.

**Deviations from the spec**

- **D1.** Marker genes CD14 and FPR1 are not in the DS06 count matrix (pre-filtered). Monocytes use CSF1R only; neutrophils use CSF3R,
  CXCR2 and MNDA.
- **D2 (added after the first run).** The DS03–S-CB050 twins looked ordered, so I added an order check: Kendall tau between the
  DS03 study number and the S-CB050 case number of each unique twin. The spec's certainty rule for step 3 was kept: every dog-level
  pair stays `unverified`. The file-level overlap is written as one `probable` row per DS03 block (the spec's "summary evidence with
  chance probability below 0.01").
- **D3 (added).** Because the order check put DS03 BLSC29 on S-CB050 case 127 (= DS04 case 54), I matched all 14 DS04 haematology rows
  against DS03 on haematocrit and reticulocyte %. DS04 prints reticulocytes with one decimal, so the tolerance there is 0.05, not the
  spec's two-decimal rule.
- **D4.** Step 1c (icterus against bilirubin) turned out uninformative (see 4.1). The seven non-S-CB050 fatal rows rest on the order rule,
  which the three S-CB050 hits validate; they are `probable` under the spec's "order evidence with chance below 0.01".

## 4. Results

Links in `out/linkage.csv`: **10 confirmed by values, 11 probable, 126 unverified** (147 rows).

### 4.1 DS04 rows and case numbers (step 1)

- All five Stats Tables sheets list the cases in one order (controls 2, 4, 9, 11; cases 50, 20, 117, 110, 54, 59, 91, 61, 88, 106).
  The haematology sheet has 4 control rows then 10 fatal rows. Joining row *i* to the *i*-th case of that order puts the three S-CB050
  matches exactly on cases 50, 54 and 59; under a random order of the fatal rows that has probability 1/720 = 0.0014.
- **S-CB050 cases 126, 127 and 131 are DS04 cases 50, 54 and 59** (WBC/segmented/band equal to two decimals; age 30, 9, 60 months,
  weight 30.6, 45.6, 34.0 kg and sex equal; all died). This confirms data.md and SV-G1.
- Icterus wording agrees with bilirubin above 30 µmol/L in 8 of 10 fatal rows, but most dogs are icteric: p = 0.37 over the 5,040
  orders that keep the three matches fixed (0.18 over all 10! orders). It neither supports nor contradicts the join.
- Controls (4) rest on order only (all bilirubin 0): `unverified`.

### 4.2 The other seven fatal DS04 dogs in S-CB050 (step 2)

No match for cases 20, 61, 88, 91, 106, 110, 117. The nearest S-CB050 rows differ by 4.8% to 24.9% on at least one count. The closest
(case 88 against S-CB050 case 2, 4.8%) is a survivor with a different signalment (24 months, female; DS04 88 is 7 months, male): not
the same dog. Four DS04 controls do not match S-CB050 controls either. So only 3 of the 10 fatal DS04 dogs are S-CB050 dogs.

### 4.3 DS03 natural against S-CB050 (step 3) — new finding

Twin = same sex, same age in months, weight within 0.1 kg.

| DS03 block (n with full signalment) | Has an S-CB050 twin | In the matching S-CB050 block | Twin pairs vs chance | p (Poisson) | Unique twins in study-number order |
|---|---|---|---|---|---|
| Cohort 1 (78) | 77 | cases 1–97: 77 | 59× | 1e-105 | 75 of 75 (tau 1.0) |
| Cohort 2 (17) | 17 | cases 101–144: 17 | 119× | 1e-29 | 17 of 17 (tau 1.0) |
| Controls (13) | 12 | controls 201–215: 12 | 254× | 2e-25 | 12 of 12 (tau 1.0) |

Chance baseline: 0.19 twin pairs per 1,000 pairs (DS03 cohort 1 and S-CB050 against DS05, which cannot share dogs); against DS05 only
3 of 78 cohort-1 dogs and 0 of 17 cohort-2 dogs have a twin. Cross-block twins (DS03 cohort 1 against S-CB050 cases 101–144) are at
chance (2 pairs, 3×, p 0.14).

The order check is the strongest evidence: DS03 numbers BC02–BC107 map onto S-CB050 cases 1–97, BLSC1–BLSC42 onto 101–139 and CON2–CON22
onto 201–214 with no inversion. The S-CB050 case numbers look like a renumbering of the same enrolment registers, skipping excluded dogs.
The two ambiguous cohort-1 dogs (BC27, BC100) each have one twin that fits the order (cases 26 and 91).

**Value confirmation (D3):** DS03 BLSC29 has haematocrit 0.07 and reticulocytes 3.17% (DS04 case 54: 0.07 and 3.2%) and the same age,
weight and sex. So DS03 BLSC29 = DS04 case 54 = S-CB050 case 127, confirmed by values. No other DS04 row matches a DS03 dog.

Conclusion: **DS03's natural cohorts and controls are S-CB050 dogs.** SRC-E is not independent of SRC-A. Per the spec, the dog-level pairs
stay `unverified`; the file-level rows are `probable`.

### 4.4 DS06 names and DS02 dogs (step 4)

- `high_3` = DS02 dog 6 by sampling pattern (series stops after day 3; dog 6 died on day 4): `probable`.
- Value check: the positive control **failed**. With days 0, 1 and 3, the best of the six high-dose assignments put high_3 on dog 5
  (mean residual rho 0.28) and the true one scored −0.06. Five Beagles with similar kinetics leave too little between-dog signal. The
  other assignments (high_1 = dog 4, high_2 = dog 5, mean rho 0.39; low_1 = dog 2, low_2 = dog 3, 0.27) therefore stay `unverified`.
  `low_0` (one day-0 sample) may be the splenectomised donor, dog 1: `unverified`.

### 4.5 DS07 (step 5)

- **Where and when.** CB112: dogs admitted as patients to "the Clinic" (the methods name neither the hospital nor the dates), ethics
  V0034-14, serum archived at −80 °C after routine biochemistry; complicated = collapse, cerebral signs, death within 24 h, or one of
  seven laboratory thresholds. CB147: liver from a tissue bank at OVAH; serum and EDTA taken before treatment; ethics REC040-21; no
  collection dates. For comparison: S-CB050 cohort 1 Oct 2011–Apr 2013 (V055-11; = CB145 and CB517), cohort 2 Jan–Dec 2014 (V091-13);
  CB115 (DS03) dates its first cohort Oct 2013–Jul 2015, which contradicts the matches in 4.3.
- **Numbering.** 6 of the 7 DS04 numbers below 98 (20, 50, 54, 59, 61, 91) are in the DS07 "complicated" list of 14; 88 is in
  "uncomplicated". Expected about 1.0 by chance; p (6 or more) = 2.0e-05 over 1–97 (2.9e-05 over 1–91, 1.8e-06 over 1–144). The numbering
  is probably shared.
- **Contradictions with the CB112 summaries.** DS04 case 20 is 144 months old; CB112 gives an infected age range of 6–120 months. DS04
  case 88 was dead on arrival; CB112 counts death within 24 h as complicated, but DS07 88 is uncomplicated. The other five agree (intact
  males, as all CB112 complicated males are; 20 is a spayed female, and CB112 has 2 spayed females in the complicated group).
- **Summary level.** CB112 controls (20; 6 female; median 21 months, 12–120) do not fit S-CB050 controls (20; 13 female; median 46, 3–84)
  or DS03 controls. CB112 infected (32; age up to 120 months) cannot all be S-CB050 2014 dogs (oldest 91 months).
- If the numbering holds, DS07 dogs 50, 54 and 59 are S-CB050 cases 126, 127 and 131 (all died), and DS07 54 is also DS03 BLSC29.
  That is 3 dogs: not enough to replace the "complicated" label, and unverified. **DS07 cannot take death from another file yet.**

### Which files share dogs (summary)

| Files | Shared dogs | Certainty |
|---|---|---|
| S-CB517 – S-CB050 | all 112 of S-CB517 | confirmed (SV-G1) |
| DS03 experimental – DS02/DS06 | 5 Beagles | confirmed (SV-G1) |
| DS04 – S-CB050 | 3 of 10 fatal (50/54/59 = 126/127/131) | confirmed |
| DS03 natural and controls – S-CB050 | 106 of 108 with signalment (77 + 17 + 12) | file level probable; 1 dog confirmed |
| DS04 – DS03 | 1 (case 54 = BLSC29) | confirmed |
| DS07 – DS04 (and through it S-CB050) | up to 7 by number | unverified |
| DS06 names – DS02 numbers | high_3 = dog 6 | probable; rest unverified |

## 5. Stability and sensitivity

- Step 1: the S-CB050 matches are exact (0.0% difference); no other S-CB050 row is within 5% of those three rows.
- Step 3: the twin rate stays far above baseline in every block; widening the number range or removing the order check does not change
  the file-level conclusion. The baseline uses two comparisons (DS03 and S-CB050 against DS05) with similar rates (0.26 and 0.15 per 1,000).
- Step 5: the hypergeometric p stays below 1e-4 for every number range tried (1–91, 1–97, 1–144).
- Repeat: two full reruns from an empty `out/` gave byte-identical outputs.

## 6. Confounders

- Age, weight and sex are weak identifiers and DS03 and S-CB050 come from one hospital, so twins could come from the same population
  without being the same dogs. The DS05 baseline (another province) may understate within-hospital similarity. The order check answers
  this: same-population dogs would not line up in study-number order.
- DS07 numbers may coincide with DS04 numbers through a shared register without being the same dogs (two registers with similar ranges).

## 7. What this does not show

- No dog-level link to DS07: DS07 has no clinical values. The number link remains unverified.
- A non-match does not prove different dogs: S-CB050 may have excluded dogs that DS04 kept (DS04 has dogs dead on arrival).
- The DS03–S-CB050 dog-level pairs are not confirmed by values (no shared continuous variable), except BLSC29.
- The DS06 mapping beyond high_3 is unresolved.
- `/core/datasets.jsonl` was not edited; the source changes below are a proposal.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files:** every match, count, rate, order check and probability above; the DS07 lists; DS04 signalment.
- **From documentation:** cohort dates and ethics numbers (CB050, CB145, CB517, CB115, CB112, CB147); CB112 group summaries and the
  "complicated" definition.
- **Inferred:** that S-CB050 case numbers are a renumbering of the BC, BLSC and CON registers; that DS07 and DS04 share a numbering;
  that low_0 is the donor dog.

## Consequence for `independent_source` (proposal only)

| Dataset | Now | Proposed | Reason |
|---|---|---|---|
| DS03 natural cohorts 1 and 2, DS03 controls | SRC-E | SRC-A | Same dogs as S-CB050 |
| DS03 experimental dogs | SRC-E | SRC-B | The DS02 Beagles (SV-G1) |
| DS03 IMHA dogs | SRC-E | SRC-E | No overlap tested |
| DS04 / S-CB147 | SRC-G | SRC-G, overlap note to SRC-A | 3 of 10 fatal dogs are S-CB050 dogs |
| DS07 | SRC-C | unchanged until the authors answer | Number overlap unverified |

For the packages now: **never pool DS03 natural dogs with S-CB050 or S-CB517**, and treat a DS03 result and an S-CB050 result as one
source, not a replication. This affects SV-01 (its DS03 "replication" is the S-CB050 cohort) and SV-09 (axis replication).

## 9. Next step and decisions for the user

1. **Send the case-numbering query?** Draft: `out/author_query_draft.md` (not sent). It asks about the DS07/DS04 register, DS07
   outcomes, the DS03 dates and the CB145 cohort.
2. **Change `independent_source`** in `/core/datasets.jsonl` (and the "Never pool" list in `data.md`) as proposed above: a coordinator
   and user decision.
3. data.md corrections for the coordinator: DS03 natural dogs are S-CB050 dogs; DS04 case 54 is also DS03 BLSC29.

## Software

Python 3.12.12 (uv 0.10.4), standard library only; `shared/io/rawio.py`; .NET console loader (way B); Angular view
`experiment-linkage-audit-view.component.*`.
