# Data facts for the severity experiments

Read the table and "Never pool these". Then read only the headings for the datasets your package uses (grep for `### DS05`, for example). The rules are in [rules.md](rules.md).

## Datasets

| Dataset | Source | Species, setting | Dogs | Severity label | Main variables | Raw location under `/core/data/raw/` |
|---|---|---|---|---|---|---|
| S-CB050 | SRC-A | *B. rossi*, Onderstepoort | 141 infected (15 died) + 20 controls. Cytokines in 97 infected (12 died) and 15 controls | Death | Age, weight, sex, WBC, segmented and band neutrophils, IL-2, IL-6, IL-8, IL-10, IL-18, GM-CSF, MCP-1, MPXI | `S-CB050/…zip` → `Table_1.DOCX` |
| S-CB517 | SRC-A | Same dogs as cases 1 to 97 and controls 201 to 215 of S-CB050 | 97 + 15 | Death | WBC differential, SAA, CRP, the same 7 cytokines | `S-CB517/…zip` → two PDF tables |
| DS07 | SRC-C | *B. rossi*, archived serum | 14 complicated, 18 uncomplicated, 20 controls | Complicated | Serum proteome, 11 TMT plexes | `DS07/B_Proteins.txt`, `sample_list.xlsx` |
| S-CB017 | SRC-D | *B. canis*, Zagreb | 18 complicated, 13 uncomplicated, 16 controls; days 1 and 7 | Complicated | 9 cytokines, 16 haematology variables | `S-CB017/…zip` → `pone.0190474.s001.xlsx` |
| S-CB516 | SRC-O | *B. canis*, Switzerland | 8 died, 7 survived | Death | Breed, age, sex, weight, 9 clinical signs | `S-CB516/…zip` → two PDFs |
| DS05 | SRC-F | *B. rossi*, Eastern Cape clinic, 2021 | 149 (+1 *B. vogeli*) | None (habitus, haematocrit as proxies) | Signalment, breed, illness duration, CBC, reticulocytes, proteins | `DS05/BET Study Dataset.xlsx` |
| DS03 | SRC-E | *B. rossi*, Onderstepoort | 103 infected, 14 controls, 16 IMHA; 5 experimental dogs | None | Age, weight, sex, 12 red cell and reticulocyte indices | `DS03/*.xlsx` (3 files) |
| DS02 (= DS01) | SRC-B | *B. rossi*, 5 experimental Beagles | 2 low dose, 3 high dose (1 died on day 4) | None | Daily clinical scores, haematology, parasitaemia, 13 cytokines, CRP, lactate, cell-free haemoglobin | `DS02/B.Atkinson_…xlsx` |
| DS06 | SRC-B | Same Beagles | 28 blood samples | None | RNA-seq counts, 12,362 genes | `DS06/GSE167201_*.gz` |
| DS04, S-CB147 | SRC-G | *B. rossi*, necropsy | 10 fatal, 4 controls | All fatal | Liver histology scores, IHC counts, haematology, biochemistry | `DS04/*`, `S-CB147/*` |

The full records are in `/core/datasets.jsonl` (prose fields: read them, do not parse them). Read your dataset's record before you write a spec.

## Never pool these

- S-CB050 with S-CB517: the same dogs.
- DS01, DS02 and DS06: the same 5 Beagles. DS01 repeats DS02.
- DS04 with S-CB147: the same 10 dogs.
- DS04 with S-CB050: at least 3 dogs are shared (see "Linkage facts" below).
- DS03 with S-CB050 or S-CB517: shared dogs are possible and unverified.
- The three sheets of DS05: the same 150 dogs.
- Raw cytokine values across files: different assay runs. Compare within-file contrasts only.

## File facts by dataset

Checked in the raw files on 2026-11-12 unless marked "record" (taken from `datasets.jsonl` and not re-checked).

### S-CB050

One table, 161 data rows. Decimal commas (`4,83`). Columns: `Case, Age (mos), Weight (kg), Gender, Status, Outcome, WBC, Neut Seg, Neut Band, IL-2, IL-6, IL-8, IL-10, IL-18, GM-CSF, MCP-1, MPXI`. Cases 1 to 97 are the 2011 to 2013 cohort and have cytokines; cases 101 to 144 are the 2014 cohort and have none; controls are 201 to 220. Deaths: cases 13, 21, 34, 37, 55, 58, 59, 61, 65, 81, 84, 85, 126, 127, 131. Assay floors per record: IL-2 3.4, GM-CSF 9.1, IL-6 3.6, IL-10 8.4, IL-18 5.7; case 80 has ceiling values.

### S-CB017

Sheet `CYTOKINES`: a healthy block, then two "Diseased" blocks with no day label (31 rows, then 30; the record infers day 1 then day 7). Sheet `HEMATOLOGY`: text rows mark "Diseased day 1" and "Diseased day 7". A side legend gives `B` = uncomplicated, `BK` = complicated. An unlabelled column with the word "Dead" contradicts the article: do not use it. Floors per record: IL-10 0.8 (45 of 77 samples), IL-18 2, IL-2 10, IL-15 12, IL-8 10. The article states that blood was taken 6 to 8 h after imidocarb (record).

### DS07

`sample_list.xlsx` has the group lists in columns 0 to 4 and the TMT layout in columns 10 to 16 (plexes B1 to B11; channel 126 is the pooled standard; plex B11 has 2 samples). Some IDs have a trailing space (`2z `). Control IDs end in `z`. Complicated: 81, 91, 7, 15, 16, 20, 24, 37, 40, 43, 50, 54, 59, 61. Uncomplicated: 69, 88, 74, 56, 70, 33, 64, 28, 26, 71, 42, 45, 72, 58, 30, 19, 55, 73. About 31% of abundance cells are empty and the gaps follow the plex (record). 163 master proteins carry a gene symbol; others must be found by description.

### DS05

Sheet `Entire population`: row 0 is the header, row 1 the units and reference ranges, data start at row 2 (`BET001`). The sheet has about 1,000 rows, mostly empty: stop at the first blank ID. Respiratory rate is `P+` (panting) in 24 dogs. Dates are DD/MM/YYYY. Sheet `CORRESPONDENCE` holds the habitus grade and the authors' category codes. BET065 and BET066 have no CBC. Known entry problems: BET048 red cell count, BET021 globulin 1 g/L. The old tidy script and output are a reference: `git show 8d4c6d9:core/scripts/tidy_ds05.py`, `git show 8d4c6d9:core/data/tidy/DS05.json`.

### DS02

Sheets: `Notes, Clinical, Haematology, Biochemistry, Venous blood gas, Cytokines, Parasitaemias, Iron`. One row per dog; columns are `<variable><day>` with days -1 to 8 and `4.1` (an extra day-4 sample for the low-dose dogs). `Exp group` 0 = low dose (dogs 2 and 3), 1 = high dose (dogs 4, 5, 6). Dog 1 is the splenectomised donor: exclude it. Dog 6 died on day 4. Treatment was at about 96 h (high dose) and 108 h (low dose) per record: flag later samples as post-treatment.

### DS03

The experimental file has 12 variables by 6 days for 5 dogs. "Day 1" is not anchored to inoculation in the file (record).

### DS06

Sample names are `low_0, low_1, low_2, high_1, high_2, high_3` by day. `high_3` stops after day 3. The mapping to DS02 dog numbers is not in the files. Library size collapses on days 3 and 4 with a shift to reticulocyte transcripts (record).

### DS04

`Stats Tables.xlsx` has IHC counts with case numbers (controls 2, 4, 9, 11; cases 20, 50, 54, 59, 61, 88, 91, 106, 110, 117). `stats for haematology.xlsx` has one row per dog with a 0/1 group flag and no case number.

## Linkage facts

Found on 2026-11-12.

- **Confirmed by values.** Three fatal dogs in the DS04 haematology sheet have the same WBC, segmented and band neutrophil counts as S-CB050 cases 126, 127 and 131 (103.55 / 67.31 / 21.75; 21.60 / 15.12 / 0.86; 14.36 / 9.19 / 2.87). Those are the three deaths of the 2014 cohort. So DS04 is not fully independent of SRC-A, and the two files use different case numbers.
- **Not confirmed.** Six of the seven DS04 case numbers below 98 (20, 50, 54, 59, 61, 91) are in the DS07 "complicated" list, where chance predicts about one. Case 88 is in the DS07 "uncomplicated" list although DS04 records it as dead on arrival. DS07 has no clinical values, so this cannot be checked by matching values.
- **Not supported.** DS07 numbers do not appear to be S-CB050 case numbers: S-CB050 cases 20, 50, 54 and 91 survived.

SV-07 takes this further. Until it reports, treat DS04 as overlapping SRC-A and treat DS07 as a separate source with unknown overlap.

## Literature inputs

- `/core/data/severity/`: `shortlist.csv` (196 articles; tier A 31, B 120, C 45), `association_schema.json`, `EXTRACTION_GUIDE.md`, `marker_map.csv`, `extractions/` (10 articles), `associations.csv` (275 rows). The column `marker_hints` in the shortlist holds general NLP concepts and is not a list of markers.
- `/core/search/synthesis/`: `QUESTIONS.md`, `CROSS.md` and one file per category. Narrative only.
- `/core/articles/<ID>_*.md`: one appraisal note per article.
- Human comparators: `HU001` to `HU027` in `/core/articles.jsonl` and `/core/articles/`.

## What the data cannot support

Do not design a package around any of these. If your work depends on one, stop and report.

- Parasite load against severity in natural infection at dog level. No public file has it.
- Host genetics. Breed against a hard outcome.
- Dog-level severity analysis in *B. gibsoni* or *B. vogeli*.
- A species comparison inside one study.
- Days sick against a hard outcome (illness duration is only in DS05).
- Treatment effects. External validation. Prediction.

## Where these facts come from

- **Checked in files on 2026-11-12:** the counts and file facts in this file that are not marked "record"; the Python environment; `pdftotext`; which folders are git-ignored; the shortlist and pilot counts; the proteins named in SV-06; the three value matches between DS04 and S-CB050.
- **Taken from `datasets.jsonl`, the article notes, the syntheses or the old programme in git, and not re-checked:** everything marked "record"; the contents of S-CB517, DS03, DS06 and S-CB516; the old experiment results; article findings quoted by ID.
- **Inferred:** the DS07 to DS04 numbering link; that the PubMed gaps are true gaps (one database, abstracts only); the detectable effects (normal approximations); the day order of the S-CB017 cytokine blocks.
