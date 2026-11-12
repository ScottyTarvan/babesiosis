# SV-G1 report: shared data layer

Experiment `SV-G1-01-data-layer-coverage` (method `data_layer_coverage`, role `descriptive`). Run 2026-11-12.

## 1. Question

What do the shared tidy files hold for the severity programme: which datasets, how many dogs, which variables, how complete, and
which cleaning decisions and flags must later packages know? There is no hypothesis and no statistical test.

## 2. Inputs

Nine datasets from `data.md`, eight independent sources (SRC-A, B, C, D, E, F, G, O). DS01 repeats DS02 and gets no file; DS06 is
tidied by SV-08. The SHA-256 of every raw input (for a zip member, of the member bytes) is in the `built_from` field of each
features file and in `out/summary.json`. No spec hash: SV-G1 has no outcome lock (`spec.md` says what is recorded).

Outputs (first 12 characters of SHA-256 at the final run): `shared/dictionary.csv` 17d1021960a6; tidy files, for example
DS02.features 12475e823e58, DS03.features 2862ac7e6e5f, DS05.features 323238159fb2, S-CB050.features fedde71e2303
(`sha256sum shared/tidy/*` gives the rest).

## 3. What was done

- One standard-library Python 3.12 script per dataset (`scripts/tidy_*.py`), sharing `scripts/tidylib.py`. `write_dataset()` checks
  the contract of `rules.md` before it writes: groups only infected/control/comparator, neutral `dog_id`, no label-like variable name
  in a features file, every value declared as a variable, outcome dogs present in the features file, no NaN.
- **Neutral IDs.** `<dataset>:dNNN`, numbered in a salted SHA-256 order of the original ID, so the number carries neither the label
  nor the case number. Original IDs are only in the outcomes files. Free text in the features files, the dictionary and the check
  names of S-CB050 and S-CB517 names single dogs by neutral ID: their case numbers plus the death list in `data.md` would reveal the label.
- **Labels and proxies only in outcomes files**: death (S-CB050, S-CB517, S-CB516, DS04, DS02), complicated (S-CB017, DS07), DS05 habitus
  grade and every one of the authors' derived classes, the DS02 daily habitus score.
- **Units**: one unit per harmonised name (MCHC g/dL → g/L in DS02 and DS05; haematocrit % → L/L in S-CB017). Every column and
  conversion is a row of `shared/dictionary.csv` (538 rows).
- **Censoring**: values at an assay floor or ceiling keep the reported number and get a `censored` entry (DS02 cytokine zeros and CRP 10;
  S-CB050/S-CB517 record floors and the case-80 ceiling code; S-CB017 floors; DS04 "<1" and ">148").
- **Package steps**: S-CB050 `cohort` (1 = cases 1–97 and controls 201–215). DS02 long format with `post_treatment` (days 5–8), dog 1
  excluded. DS07 one record per dog, log2 ratio to the plex standard (channel 126) per master protein, plus `plex` and `channel`.
  S-CB517 and S-CB516 PDFs converted with pdftotext.
- Three sub-agents built S-CB050/S-CB517, S-CB017/S-CB516 and DS07/DS04 with the same library; I checked their outputs through
  the same contract checks and the summary step.

**Deviations from the package file**
- S-CB516 was converted with `pdftotext -table`, not `-layout`: `-layout` scrambles the wrapped cells of that table.
- DS07 uses PD's "Abundances (Grouped)" (each plex already scaled to its standard = 100); log2(sample/standard) equals log2 of PD's
  "Abundance Ratio" in all 8,235 cells where both exist. The export has no raw per-channel abundance columns.
- DS04 includes the 33 per-slide files: they are repeat histopathology score sheets (2–4 per dog), averaged per dog. DS04 fatal
  dogs have two records (admission blood, necropsy liver); controls have one.
- S-CB017 outcomes also hold `died` (1 dog, inferred from the missing day-7 sample); `complicated` is the label of that file.

## 4. Results

9 datasets, 694 dog records, **574 dogs after the known same-dog links** (S-CB517 = 112 S-CB050 dogs; DS03 experimental = the 5 DS02
Beagles; 3 DS04 dogs = S-CB050 cases), 803 feature records. Checks: **141, of which 133 passed**.

| Dataset | Source | Species | Dogs | Infected / control / comparator | Records | Variables | Cells missing | Checks | Flags |
|---|---|---|---|---|---|---|---|---|---|
| S-CB050 | SRC-A | B. rossi | 161 | 141 / 20 / 0 | 161 | 15 | 14.7% | 21/22 | 0 |
| S-CB517 | SRC-A | B. rossi | 112 | 97 / 15 / 0 | 112 | 14 | 0.0% | 20/21 | 18 |
| DS07 | SRC-C | B. rossi | 52 | 32 / 20 / 0 | 52 | 226 | 30.8% | 11/12 | 0 |
| S-CB017 | SRC-D | B. canis | 47 | 31 / 16 / 0 | 77 | 26 | 3.0% | 14/14 | 10 |
| S-CB516 | SRC-O | B. canis | 15 | 15 / 0 / 0 | 15 | 17 | 0.8% | 18/18 | 1 |
| DS05 | SRC-F | B. rossi | 150 | 150 / 0 / 0 | 150 | 42 | 1.4% | 12/12 | 2 |
| DS03 | SRC-E | B. rossi | 138 | 108 / 14 / 16 | 161 | 17 | 7.3% | 7/7 | 0 |
| DS02 | SRC-B | B. rossi | 5 | 5 / 0 / 0 | 51 | 50 | 15.2% | 5/5 | 1 |
| DS04 | SRC-G | B. rossi | 14 | 10 / 4 / 0 | 24 | 131 | 45.1% | 25/30 | 7 |

All row counts equal `data.md`. S-CB050 has 141 infected dogs (15 died), with cytokines in 97 (12 died) and 15 controls;
S-CB517 has 97 + 15; S-CB516 has 8 died and 7 survived; S-CB017 has 18 complicated, 13 uncomplicated, 16 controls, 31 day-1 and
30 day-7 samples.

**Coverage** (% of dogs with at least one value; blank = the file lacks the variable):

| harmonised_name | S-CB050 | S-CB517 | DS07 | S-CB017 | S-CB516 | DS05 | DS03 | DS02 | DS04 |
|---|---|---|---|---|---|---|---|---|---|
| age_months | 99 |  |  |  | 100 | 100 | 95 |  | 100 |
| weight_kg | 94 |  |  |  | 100 | 100 | 86 |  | 86 |
| sex | 100 |  |  |  | 100 | 100 | 96 |  | 100 |
| neuter |  |  |  |  | 87 | 100 |  |  | 71 |
| breed |  |  |  |  | 100 | 100 |  |  | 100 |
| illness_days |  |  |  |  |  | 99 |  |  |  |
| temp_c |  |  |  |  | 100 | 97 |  | 100 |  |
| hct |  |  |  | 100 |  | 99 | 100 | 100 | 100 |
| hb |  |  |  |  |  | 99 | 100 | 100 |  |
| rbc |  |  |  | 100 |  | 99 |  | 100 | 100 |
| mcv |  |  |  |  |  | 99 |  | 100 |  |
| mchc |  |  |  |  |  | 99 | 100 | 100 |  |
| retic_pct |  |  |  |  |  | 99 | 100 | 100 | 100 |
| arc |  |  |  |  |  | 99 | 100 | 100 |  |
| wbc | 100 | 100 |  | 100 |  | 99 |  | 100 | 100 |
| neut_seg | 100 | 100 |  | 100 |  | 99 |  | 100 | 100 |
| neut_band | 100 |  |  | 100 |  | 99 |  | 100 | 100 |
| lymph |  | 100 |  | 100 |  | 99 |  | 100 | 100 |
| mono |  | 100 |  | 100 |  | 99 |  | 100 | 100 |
| eos |  | 100 |  | 100 |  | 99 |  | 100 |  |
| plt |  |  |  | 100 |  | 99 |  | 100 | 100 |
| tsp |  |  |  |  |  | 96 |  |  | 100 |
| albumin |  |  |  |  |  | 96 |  | 100 | 100 |
| globulin |  |  |  |  |  | 96 |  |  | 93 |
| parasitaemia_pct |  |  |  |  |  |  |  | 100 |  |
| crp |  | 100 |  |  |  |  |  | 100 |  |
| saa |  | 100 |  |  |  |  |  |  |  |
| lactate |  |  |  |  |  |  |  | 100 |  |
| il2, il8, il10, il18, gmcsf, mcp1 | 70 | 100 |  | 100 |  |  |  | 100 |  |
| il6 | 70 | 100 |  |  |  |  |  | 100 |  |
| kc |  |  |  | 100 |  |  |  | 100 |  |
| mpxi | 99 |  |  |  |  |  |  |  |  |

S-CB050 cytokines are 70% because cohort 2 (cases 101–144 and controls 216–220) has none, by design.

**Linkage found here**
- **DS03 experimental = DS02 Beagles.** ARC is equal on every DS03 day; DS03 day n = DS02 day n (the DS02 4.1 sample left out). Of 140
  shared cells one differs (one dog, day 3 Hb: 120 in DS03, 118 in DS02). DS03 "Day 1" is therefore anchored to inoculation. Field `same_dog_as`.
- **S-CB517 = S-CB050** (package step 3, never compared before): all 112 rows link by value to the case their ID implies. The 7 cytokines
  agree exactly in 111–112 of 112 pairs each and within 1% in all; the only differences are the case-80 ceiling code (50000 vs 50001).
  Segmented neutrophils 112/112 equal; WBC 88/112 equal (see flags). Died agrees in 97/97. Field `same_dog_as`.
- **DS04** fatal dogs join the haematology rows by case order (3 confirmed by S-CB050 values and signalment; chance 1 in 720); controls by order only.

## 5. Checks and flags

Failed checks (8, all reported, none hidden):
- S-CB050: survivors male:female 83:43 against 82:43 published (the file has one more infected dog than the article, 141 against 140).
- S-CB517: median WBC of infected dogs 6.29 against 6.2 published; the S-CB050 WBC of the same dogs gives 6.22 (see flag).
- DS07: 172 master proteins carry a gene symbol, not the 163 in `data.md`.
- DS04: fatal-case age mean 55.0 (52.8 published) and median 42 (50) months, median weight 32.3 (34) kg; two IHC per-dog means differ
  from S-CB147 Table 2 and the authors' Sheet1 averages (case 20 Iba-1 centrilobular, case 106 CD3 portal: the authors' averages
  disagree with their own field counts).

39 values are flagged and kept as reported. Among them:
- **S-CB517 WBC**: in 24 dogs it is higher than S-CB050; in all 24, S-CB050 WBC = this file's differential + the S-CB050 band count.
  Prefer S-CB050 WBC for these dogs.
- **DS02**: the dog that died on day 4 has a parasitaemia of 0 in the day-6 column.
- **DS05**: one dog's red cell count equals its WCC; one dog's globulin is 1 g/L.
- **S-CB017**: the "Dead" column is not used; 7 count/percentage contradictions.
- **DS04**: two controls with two different signalments; case 88 is dead on arrival in DS04 but "uncomplicated" in DS07.

## 6. Confounders

Not applicable as such (no test). For users of the files: species is aliased with source; raw cytokines of different files are
different assay runs; "died" in the Onderstepoort files (S-CB050, S-CB517, DS04) includes euthanasia for poor prognosis; DS04 histology
was scored unblinded and controls before cases.

## 7. What this does not show

Coverage is the presence of a value, not its quality or its comparability across files. No association with severity was computed.
Dogs shared between files beyond the links above (DS03 with S-CB050, DS07 with DS04) are not resolved; SV-07 does that.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files**: every count, coverage share, check and flag above; the DS03–DS02, S-CB517–S-CB050 and DS04–S-CB050 links;
  the S-CB017 cytokine block labels ("Diseased … day 1" and "… day 7", padded with spaces in a narrow column).
- **From documentation**: units not stated in the files (DS02 CRP mg/L, cytokines pg/mL, cell-free Hb mg/L assumed), treatment times
  in DS02, the euthanasia wording, the article numbers used in the checks.
- **Inferred**: DS02 day 4 and the 4.1 sample are pre-treatment; S-CB517 SAA 3001.0 is an above-range code; DS07 plex Bk = PD
  fraction Fk; DS04 control join by order; S-CB017 `died` for one dog.

## 9. Next step and decisions for the user

- `data.md` needs corrections, which only the coordinator makes: S-CB017 cytokine blocks are labelled day 1 and day 7 (not inferred);
  DS07 has 172 gene-symbol master proteins (not 163); the DS04 per-slide files are histopathology score sheets; DS03 "Day 1" is
  anchored (the experimental dogs are the DS02 Beagles).
- Whether S-CB517 analyses should use the S-CB050 WBC for the 24 flagged dogs (recommended).

## Software

Python 3.12.12 (uv), standard library only; pdftotext (Poppler, Git for Windows); .NET console loader; Angular build for the view.
Script versions (SHA-256, 12 characters) are in the load file (`summarise.py`) and `run.md` repeats the run: two complete repeats gave
byte-identical tidy files, dictionary and checks.
