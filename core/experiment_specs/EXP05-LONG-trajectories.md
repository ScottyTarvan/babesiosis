# EXP05 LONG trajectories: Longitudinal structure in the beagle series, DS03 and S-CB017

| Field | Value |
|---|---|
| Experiment code | `EXP05-LONG-trajectories` (umbrella summary run, `dataset` = null) plus five sub-runs, one per tidy dataset: `EXP05-DS01-trajectories`, `EXP05-DS02-trajectories`, `EXP05-DS06-trajectories`, `EXP05-DS03-trajectories`, `EXP05-SCB017-trajectories` |
| Layer | 1 single dataset (each sub-run); the umbrella run is a cross-dataset summary with no associations or clusters |
| Method token | `trajectories` (every run, including the umbrella) |
| Dataset(s) | `DS01`, `DS02`, `DS06` (one experiment, SRC-B, cohort CH09); `DS03` (listed as SRC-E, but its 5 experimental dogs are the SRC-B beagles, see 2.1); `S-CB017` (SRC-D, *B. canis*). Umbrella: `null`, because it compares results across the five sub-runs |
| Readiness | tidy files needed for all five datasets |
| Python environment | `.venv-nlp` (Python 3.12; numpy 1.26.4, scipy 1.17.1, scikit-learn 1.9.1 installed; statsmodels is **not** installed in either environment, so the mixed models are numpy REML). Tidy scripts are stdlib-only, except `tidy_ds06.py`, which needs numpy (either environment). Add `scipy>=1.11` and `scikit-learn>=1.5` to `scripts/requirements-experiments.txt` with a note that they are used by `experiment_trajectories.py` in `.venv-nlp` |
| Estimated build effort | large (five tidy scripts about 4 hours; experiment script 4 to 6 hours; all runs under 30 minutes) |
| Suggested model for the building agent | opus: five heterogeneous raw layouts, a hand-written REML, WGCNA-style network steps and many small-n traps |
| Depends on | `scripts/tidy_ds01.py`, `tidy_ds02.py`, `tidy_ds06.py`, `tidy_ds03.py`, `tidy_s-cb017.py` and their `data/tidy/*.json` (tasks of this spec). EXP07 (`POOL01`) will read `DS03.json` and `S-CB017.json`, so keep the variable codes in 2.2 |

## 1. Question and hypotheses

Questions:

1. How do clinical, haematological, cytokine, reticulocyte and transcriptomic markers move together through experimental *B. rossi* infection, and does the timing differ by inoculum dose?
2. In natural *B. canis* infection (S-CB017), do dogs fall into trajectory classes between day 1 and day 7, and does class membership track the complicated label?

Hypotheses:

- H1 (CB098, `articles/CB098_2022_kinetics-inflammatory-response-during-experimental-babesia.md`): inflammatory markers (CRP, IL-6, IL-8, IL-10, IP-10, MCP-1, KC-like, TNF-α) rise before clinical deterioration; the rise is earlier in high-dose dogs (parasitaemia first seen on day 1 in high-dose versus day 3 in low-dose dogs). Expected: these cytokines cluster with parasitaemia and heart rate, and the dose × day interaction is largest on days 2 to 4.
- H2 (CB115): absolute reticulocyte count falls abruptly about 48 hours after parasitaemia is detected and recovers after treatment; reticulocyte haemoglobin content falls as haemoglobin falls. Expected: ARC and CHr form a trajectory cluster distinct from haemoglobin and haematocrit.
- H3 (CB082): whole-blood transcription shows haemolytic or erythroid, metabolic and interferon or antiviral modules whose eigengenes change by day 3 to 4, earlier and larger in high-dose dogs.
- H4 (CB017): day-1 MCP-1 and KC-like are higher in complicated dogs; IL-8 rises from day 1 to 7 in uncomplicated dogs. Expected: a latent trajectory class enriched for complicated dogs.

Negative findings that count: no marker with a BH-significant day effect; dog clusters that reproduce dose group no better than any random split (with 5 dogs only 10 splits exist); in S-CB017 a single latent class (BIC chooses K = 1) or classes unrelated to the complicated label (permutation p ≥ 0.05).

**Six animals permit description only.** Five infected beagles (2 low dose, 3 high dose, one death) cannot support prediction, hypothesis testing about dose, or generalisation. Every beagle result is descriptive kinetics that generates hypotheses for natural-infection cohorts. Any dose comparison has at most 10 distinct label assignments, so its exact permutation p value cannot be smaller than 0.1.

## 2. Data

### 2.1 Sources

All paths relative to `core/`; raw files are read-only. Read xlsx files with the stdlib reader copied from `scripts/tidy_ds05.py` (`read_workbook`). Row and column numbers below are 1-based Excel rows, 0-based column indices as returned by `read_workbook`.

**DS02** (primary beagle file; Figshare 14980281, CC BY 4.0; articles CB098, CB101; SRC-B). `data/raw/DS02/B.Atkinson_Experimental Babesia study raw data.xlsx`. Sheets:

- `Notes`: rows 4 to 9 `Dog name`, `Dog number`, `Procedure`: Banjo 1 `Splenectomized`; Chuckels 2 and Einstein 3 `low dose 10^4`; Frank 4, Hamlet 5, Ozzy 6 `high dose 10^9` (CB101 says 10^8). Row 14 `Exp group 0=low dose; 1=high dose`. Keys: MM 1 Pale, 2 Icteric, 3 Normal, 4 Congested; FP 1 Absent, 2 Weak, 3 Strong; FC 1 Diarrhoea, 2 Normal, 3 Firm.
- `Clinical`, `Haematology`, `Biochemistry`, `Venous blood gas`, `Cytokines`, `Parasitaemias`, `Iron`: row 1 header, rows 2 to 7 dogs 1 to 6; column 0 `Dog number`, column 1 `Exp group` (0 low, 1 high, blank for dog 1); then wide columns `<prefix><day>`.
- Header prefixes (exact, in sheet order): Clinical `H`, `T`, `P`, `RR`, `MM`, `CRT`, `FP`, `AP`, `FC`, `BP(SYS)`, `BP(DIAS)`, `BP(MAP)`, `GLC`, `LAC`; Haematology `Hb`, `RCC`, `HT`, `MCV`, `MCH`, `MCHC`, `RDW`, `WCC`, `SNeut`, `BNeut`, `Lymph`, `Mono`, `Eos`, `Baso`, `Plt`, `NRBC/100WBC`, `Retic%`, `Retic`; Biochemistry `CRP`, `ALB`; Venous blood gas `Lac`; Cytokines `GM-CSF`, `INFg`, `KC`, `IP10`, `IL2`, `IL6`, `IL7`, `IL8`, `IL10`, `IL15`, `IL18`, `MCP1`, `TNFa`; Parasitaemias `D`; Iron `CFHb`.
- Day suffixes: `-1`, `0`, `1` … `8`, and `4.1` (written `4,1` in some cytokine headers, for example `GM-CSF 4,1`), sometimes after a space (`IL2 -1`, `D 4.1`, `GM-CSF 0`). Parse by matching the **longest known prefix** first (so `Retic%` before `Retic`, `IL10` before `IL1`), then the remainder stripped of spaces, with `,` read as `.`. Do not use a lazy regex on the whole header.
- Dog 1 (donor) has one day −1 record in Clinical, Haematology and Biochemistry only. Dog 6 stops at day 4 (died). Column `4.1` (about 108 h) is filled for low-dose dogs 2 and 3 only. Cytokines are present at days −1, 0, 1, 2, 3, 4, 6, 8. Parasitaemia `D -1`…`D7`. `Iron` headers `CFHb1`…`CFHb8` (dog 6 only days 1 to 3).
- Known data problems: monocytes dog 2 day 7 = `68` (others 0.15 to 4.3; probably 0.68); day 0 WCC and lymphocytes raised in all dogs (handling); dog 5 cytokines on days 6 and 8 have extreme values (IL-2 143,098 and 354,790; MCP-1 98,603 and 227,246; GM-CSF 9,220.8 twice); many cytokine and CRP values at the assay floor (0 or 10). `Clinical` `LAC` (point-of-care lactate, days −1 to 8) and `Venous blood gas` `Lac` (blood-gas lactate, days 1 to 8) are two different measurements.

**DS01** (Mendeley 10.17632/zyhy8z69kt.1, CC BY 4.0; same dogs as DS02). `data/raw/DS01/Raw data.xlsx`, sheet `Sheet1`, rows 1 to 25 a copy of the Notes; from row 27, 35 stacked blocks, each: title row (column 0, e.g. `Habitus`, `Temperature`, `Venous blood gas lactate`, `Parasitemia`, `GM-CSF`), header row at title + 1 (e.g. `H-1`…`H8`; `Lac1`…`Lac8` starting at column 2; `Para -1`…`Para 7`; `GM-CSF-1`…`GM-CSF 8` with `GM-CSF 4,1`), then **row title + 2 = dog 1** (often blank) and **rows title + 3 to title + 7 = dogs 2 to 6**. Block titles in order: Habitus, Temperature, Heart rate, Respiratory rate, Mucous membrane, Capillary refill time, Femoral pulse, Appetite, Fecal consistency, Systolic blood pressure, Diastolic blood pressure, Mean Arterial Pressure, Blood Glucose, Venous blood gas lactate, Haematocrit, White cell count, Mature neutrophil count, Band neutrophil count, Lymphocyte count, Monocyte count, Cell-free hemoglobin, Parasitemia, GM-CSF, IFNg, KC-like, IP-10, IL-2, IL-6, IL-7, IL-8, IL-10, IL-15, IL-18, MCP-1, TNFa. Blocks are 9 rows apart; there is no dog-ID column, so dog identity is the row offset. All DS01 numeric cells occur in DS02 (verified by the dataset curator). `data/raw/DS01/Supplementary data.docx` holds group summaries only and is not used.

**DS06** (GEO GSE167201; article CB082; SRC-B; licence: GEO terms, article CC BY). `data/raw/DS06/GSE167201_raw_counts.txt.gz`: tab-delimited, header `symbol` then 28 sample columns `low_0_D0`, `low_1_D0`…`low_1_D8`, `low_2_D0`…`low_2_D8`, `high_1_D0`…`high_1_D8`, `high_2_D0`…`high_2_D8`, `high_3_D0`, `high_3_D1`, `high_3_D3`; 12,362 gene rows, row ID `ENSCAFG###########_SYMBOL` (1,922 rows repeat the Ensembl ID in the symbol slot); integer RSEM expected counts, no missing values, already CPM-filtered. `data/raw/DS06/GSE167201_series_matrix.txt.gz`: `!Sample_title` (e.g. `high inoculum, day 0, dog 1`), `!Sample_geo_accession` (GSM5098925…GSM5098952), characteristics `breed: beagle`, `Sex: male`, `dose: high|low`. Days sequenced: 0, 1, 3, 4, 6, 8. Library sizes collapse at D3 and D4 in high-dose dogs (0.8 to 7.2 million versus 30 to 44 million); erythroid transcripts rise. The series text says "3 dogs received low dose, 2 received high dose", which contradicts the sample columns (2 low with time series plus `low_0` with D0 only, 3 high); trust the columns.

**DS03** (Figshare, CC BY 4.0; article CB115; recorded as SRC-E). Three workbooks in `data/raw/DS03/`, each with data in `Sheet1` (Sheet2, Sheet3 empty):

- `Babesia Retics_Natural inf and cont_dissertation.xlsx`: row 1 header `No`, `Study no`, `Age (months)`, `Weight (kg)`, `Gender`, `HGB (g/L)`, `HCT (L/L)`, `MCHC (g/L)`, `CHCM (g/L)`, `Ret% (%)`, `ARC (x10^9/L)`, `MCVr (fL)`, `CHCMr (g/L)`, `CHr (pg/cell)`, `CHDWr (pg/cell)`, `RDWr (%)`, `CHDelta (pg)`; section rows 2 `Study cohort 1: Naturally infected Babesia dogs` (85 `BC*` IDs), 88 `Study cohort 2: Naturally infected Babesia dogs` (18 `BLSC*`), 107 `Control dogs` (14 `CON*`).
- `Babesia Retics_IMHA_dissertation.xlsx`: row 1 title, row 2 the same header, 16 dogs `H01`…`H16`.
- `Babesia Retics_ Exp infected dissertation.xlsx`: row 1 title, row 2 header `Case number` then `<VAR>_Day <d>` for VAR in `HGB`, `HCT`, `MCHC`, `CHCM`, `Ret%`, `ARC`, `MCVr`, `CHCMr`, `CHr`, `CHDWr`, `RDWr`, `CHDelta` and d = 1…6 (73 columns); row 3 units (`(g/L)`, `(L/L)`, `%`, `x 10^9/L`, `fL`, `pg`); rows 4 to 8 cases 1 to 5. Case 5 has days 1 to 4 only.
- **Verified overlap:** the experimental cases are the DS02 beagles. HGB of case 1 days 1 to 6 = 134, 135, 131, 138, 89, 77 equals DS02 dog 2 `Hb1`, `Hb2`, `Hb3`, `Hb4`, `Hb5`, `Hb6`; cases 2, 3, 4, 5 match DS02 dogs 3, 4, 5, 6 the same way, and DS03 ARC equals DS02 `Retic` at the same days. So DS03 `Day d` = study day d (post-inoculation, not pre-infection), and case 5 (days 1 to 4) is the high-dose dog that died. The experimental part of DS03 is therefore not independent of SRC-B. The tidy script must re-verify this mapping (section 2.2) and record it in the notes.

**S-CB017** (PLOS ONE S1 Table, CC BY; article CB017; SRC-D; *B. canis*). Member `pone.0190474.s001.xlsx` of `data/raw/S-CB017/PMC5756041_supplementaryFiles.zip` (read in memory with `zipfile`; never extract). Sheets:

- `CYTOKINES`: row 1 `Healthy`, `Var 1`…; row 2 column 1 `SampleID`, columns 2 to 10 `GM-CSF (pg/ml)`, `KC-like (pg/ml)`, `IL-2 (pg/ml)`, `IL-7 (pg/ml)`, `IL-8 (pg/ml)`, `IL-10 (pg/ml)`, `IL-15 (pg/ml)`, `IL-18 (pg/ml)`, `MCP-1 (pg/ml)`; legend in columns 13 to 14 (`B` `UNCOMPLICATED BABESIOSIS`, `BK` `COMPLICATED BABESIOSIS`). Rows 3 to 18 healthy (`H1`…`H8`, `HI1`…`HI8`). Row 19 column 0 `Diseased … day 1` (with runs of spaces): rows 19 to 49 = day 1 (31 dogs). Row 50 column 0 `Diseased … day 7`: rows 50 to 79 = day 7 (30 dogs; `BK11` absent). Column 11 holds `Dead` beside 9 dogs at day 1 and 8 at day 7. One ID is written `BK 1`; remove internal spaces.
- `HEMATOLOGY`: row 2 header `Sample ID`, `Leuko`, `Lymph`, `Neseg. Neut`, `Seg. Neut`, `Mono`, `Eos`, `Thromb`, `HMT`, `Eryt`, `Lymph %`, `Nes. Neut %`, `Seg neut %`, `Mono %`, `Eos %`, `Total gran`, `n:l`; rows 3 to 18 healthy; row 19 `Diseased`, `day 1`; rows 20 to 50 day 1; row 51 `Diseased`, `day 7`; rows 52 to 81 day 7. Columns 19 to 21 hold a reference-range block (ignore).
- Known data problems: `BK9` day 1 `Eryt` = 35 (equals HMT; implausible); `B2` day 7 `Seg. Neut` = 42 (probably 4.2); `BK12` day 7 `Seg. Neut` 1.4 with 59 % of WBC 28.3; floors: IL-10 = 0.8 in 45 of 77 samples, IL-18 = 2 in 18, minima 10 for IL-2 and IL-8, 12 for IL-15. The article reports one death (BK11), so the `Dead` column (17 marks) is not a survival label.

Also read: `data/inspection/<id>.json` and the `datasets.jsonl` records for all five; `articles/CB101_*.md`, `CB098_*.md`, `CB082_*.md`, `CB115_*.md`, `CB017_*.md`. sha256 values come from `data/manifest.jsonl` (DS01 `Raw data.xlsx`; DS02 the xlsx; DS06 `GSE167201_raw_counts.txt.gz`; DS03 the experimental xlsx, with the other two named in notes; S-CB017 the zip).

### 2.2 Tidy files required

Five scripts, each following `scripts/tidy_ds05.py` (module docstring, `read_workbook` copied in, dataset block from `datasets.jsonl` and the manifest, cleaning notes, level counts, `indent=1`). Each script is self-contained: `python -I` does not put `scripts/` on `sys.path`, so shared tables are copied, not imported. Run each with `.venv/Scripts/python.exe -I scripts/tidy_<code>.py`.

#### Shared rules for the beagle files (DS01, DS02, DS03 experimental part, DS06)

- **time_point**: `D-1`, `D00`, `D01` … `D08`, and `D04.1` for the 108-hour low-dose sample. These sort correctly as strings (`-` sorts before digits; `D04` < `D04.1` < `D05`). Single-visit data use `''`.
- **study_day** variable (`code` `study_day`, `N`, unit `days post-inoculation`, `domain` `design`, `include_default` false): one observation per subject × time point that has any other observation, value = −1, 0, 1 … 8, with `D04.1` = 4.5 (108 h per CB101). The experiment script reads numeric day from this variable, not from the string.
- **dose_group** variable (`C`, `domain` `design`, `include_default` false): `low` / `high`, one observation per infected dog with `time_point` `''`. Donor: no observation.
- **Subjects**: `dog1` … `dog6` in DS01 and DS02. `group_label`: `donor (splenectomised)` for dog 1, `low dose` for dogs 2 and 3, `high dose` for dogs 4, 5, 6. `outcome_label`: `died day 4` for dog 6, `survived` for dogs 2 to 5, null for dog 1.
- **Values**: numeric cells as float; empty cells produce no observation. Keep floor values (0, 10) as recorded and say so in the variable description. Day 0 leukocytosis is kept and noted.

Beagle variable map (DS02 prefix → code; DS01 block title in brackets; all `data_type` N unless stated; `include_default` true unless stated):

| DS02 prefix [DS01 block] | code | name | unit | domain |
|---|---|---|---|---|
| `H` [Habitus] | `habitus` | Habitus score | score 1-4 (O) | clinical |
| `T` [Temperature] | `temperature_c` | Rectal temperature | degrees C | clinical |
| `P` [Heart rate] | `heart_rate` | Heart rate | per minute | clinical |
| `RR` [Respiratory rate] | `respiratory_rate` | Respiratory rate | per minute | clinical |
| `MM` [Mucous membrane] | `mucous_membrane` | Mucous membrane colour | C: Pale, Icteric, Normal, Congested from the key; `include_default` false | clinical |
| `CRT` [Capillary refill time] | `crt` | Capillary refill time | s | clinical |
| `FP` [Femoral pulse] | `femoral_pulse` | Femoral pulse | score 1-3 (O; 1 absent, 3 strong) | clinical |
| `AP` [Appetite] | `appetite` | Appetite score | score 1-4 (O) | clinical |
| `FC` [Fecal consistency] | `faecal_consistency` | Faecal consistency | score 1-3 (O; 1 diarrhoea, 3 firm) | clinical |
| `BP(SYS)` / `BP(DIAS)` / `BP(MAP)` [Systolic / Diastolic / Mean Arterial] | `sbp` / `dbp` / `map` | Systolic / diastolic / mean arterial pressure | mmHg | clinical |
| `GLC` [Blood Glucose] | `glucose` | Blood glucose (point of care) | mmol/L | biochemistry |
| `LAC` [not in DS01] | `lactate_poc` | Lactate (point of care, Clinical sheet) | mmol/L | biochemistry |
| `Lac` [Venous blood gas lactate] | `lactate_vbg` | Venous blood-gas lactate | mmol/L | biochemistry |
| `Hb` | `haemoglobin` | Haemoglobin | g/L | haematology |
| `RCC` | `rcc` | Red cell count | x10^12/L | haematology |
| `HT` [Haematocrit] | `haematocrit` | Haematocrit | L/L | haematology |
| `MCV`, `MCH`, `MCHC`, `RDW` | `mcv`, `mch`, `mchc`, `rdw` | indices | fL, pg, as in file (record magnitude), % | haematology; `derived_from` as in `tidy_ds05.py` |
| `WCC` [White cell count] | `wcc` | White cell count | x10^9/L | haematology |
| `SNeut` [Mature neutrophil count] | `seg_neutrophils` | Segmented (mature) neutrophils | x10^9/L | haematology |
| `BNeut` [Band neutrophil count] | `band_neutrophils` | Band neutrophils | x10^9/L | haematology |
| `Lymph` / `Mono` [Lymphocyte / Monocyte count] | `lymphocytes` / `monocytes` | | x10^9/L | haematology |
| `Eos`, `Baso` | `eosinophils`, `basophils` | | x10^9/L; `basophils` `include_default` false | haematology |
| `Plt` | `platelets` | Platelet count | x10^9/L | haematology |
| `NRBC/100WBC` | `nrbc_per_100_wbc` | Nucleated red cells | per 100 WBC | haematology |
| `Retic%` | `reticulocyte_pct` | Reticulocytes | % | haematology |
| `Retic` | `arc` | Absolute reticulocyte count | x10^9/L | haematology |
| `CRP` | `crp` | C-reactive protein | mg/L | biochemistry |
| `ALB` | `albumin` | Albumin | g/L | biochemistry |
| `D` [Parasitemia] | `parasitaemia_pct` | Parasitaemia | % | pathogen |
| `CFHb` [Cell-free hemoglobin] | `cfhb` | Cell-free haemoglobin | unit not stated | haematology |
| `GM-CSF` `INFg` `KC` `IP10` `IL2` `IL6` `IL7` `IL8` `IL10` `IL15` `IL18` `MCP1` `TNFa` [same titles] | `gm_csf` `ifn_g` `kc_like` `ip_10` `il_2` `il_6` `il_7` `il_8` `il_10` `il_15` `il_18` `mcp_1` `tnf_a` | cytokine names | pg/mL (presumed; not stated in the file) | cytokine |

#### `scripts/tidy_ds02.py` → `data/tidy/DS02.json`

- Parse the seven data sheets with the prefix and day rules above; dog from column 0, dose from column 1 (cross-check against `Notes`).
- Monocytes dog 2 `D07` = 68: store no observation for `monocytes` at that point and add the note "monocytes dog2 D07 recorded as 68, probably 0.68, stored as missing". (Open question 2.)
- Notes to record: dose label 10^9 in the file versus 10^8 in CB101; treatment with diminazene at 96 h (high dose) and 108 h (low dose), so `D05` to `D08` are post-treatment (from CB101, not in the file); dog 6 died on day 4 and its missing later points are informative; day 0 leukocytosis; cytokine and CRP floor values kept as recorded; dog 5 extreme cytokine values on days 6 and 8 kept and flagged; `LAC` and `Lac` are different measurements; DS01 is a subset of this file.
- Expected size: 6 subjects, about 50 variables, about 2,200 observations.

#### `scripts/tidy_ds01.py` → `data/tidy/DS01.json`

- Walk `Sheet1` from row 27: a block starts at a row whose only non-empty cell is column 0 and whose next row is a header row. Map the title to the code with the bracketed DS01 names in the table above; parse each header cell with the prefix and day rules (`MNeut` → `seg_neutrophils`, `Para` → `parasitaemia_pct`, `Lac` → `lactate_vbg`). Dog = `dog1` for row title + 2, `dog2` … `dog6` for rows title + 3 … title + 7. Assert 35 blocks.
- Cross-check: every DS01 value must equal the DS02 value for the same dog, variable and day (read DS02 raw read-only). Record the number of matches and mismatches in the notes; mismatches are listed in the script output, not silently fixed. Apply the same monocyte rule.
- Notes: dog identity inferred from row order and confirmed against DS02; the docx is not used; DS01 and DS02 are one set of six dogs, not two datasets.

#### `scripts/tidy_ds06.py` → `data/tidy/DS06.json` (needs numpy)

- Subjects: `low_0`, `low_1`, `low_2`, `high_1`, `high_2`, `high_3` (GEO names; mapping to DS02 dog numbers is not stated, open question 3). `group_label` `low dose` / `high dose`; `outcome_label` `died day 4` for `high_3` (CB082 note), `survived` for the four other dogs with a time series, null for `low_0`. `low_0` has D0 only: note that it may be the donor (DS02 dog 1), unverified.
- time_point from the column suffix (`D0` → `D00`, `D8` → `D08`); `study_day` and `dose_group` variables as in the shared rules.
- Gene processing (record every step in the notes):
  1. Read counts as integers (12,362 × 28).
  2. Size factors by the median-of-ratios method (DESeq): per gene geometric mean across samples over genes with no zero count; size factor of a sample = median over those genes of count / geometric mean.
  3. Value = log2(count / size factor + 1).
  4. Keep genes with count-per-million ≥ 1 in at least 3 samples (`min_cpm` 1, `min_samples` 3).
  5. Select the `top_genes` = 3,000 genes with the largest variance of the log2 values across all 28 samples. (WGCNA usually uses 3,000 to 5,000; 3,000 keeps the tidy file near 12 MB.)
- Gene variables: `code` = `g_` + Ensembl ID (for example `g_ENSCAFG00000000007`); `name` = symbol, or the Ensembl ID when the symbol slot repeats it; `source_name` = full row ID; `unit` `log2 normalised count`; `data_type` N; `domain` `transcriptome`; `include_default` true; `description` = `Variance rank <r> of 12,362; mean log2 <m>.`
- Technical variables (`include_default` false, `domain` `technical`, one observation per sample): `library_size_m` (sum of raw counts / 1e6 over all 12,362 genes) and `size_factor`.
- Observations: 3,000 genes × 28 samples + 2 × 28 technical + study_day and dose_group, about 84,100 rows. Store all 3,000 so EXP05 and any later experiment use the same set.
- Notes: RSEM expected counts, STAR to CanFam3.1; the series text contradicts the columns on dose counts; diminazene on day 4, so D06 and D08 are post-treatment; library sizes collapse at D03 and D04 in high-dose dogs with erythroid transcripts rising, so composition and normalisation effects are large; top-variance selection is computed across all samples including those.

#### `scripts/tidy_ds03.py` → `data/tidy/DS03.json`

All three files go into one tidy dataset (EXP07 depends on the single-visit dogs):

- Subjects: natural cohort 1 (`BC*`, 85), natural cohort 2 (`BLSC*`, 18), controls (`CON*`, 14), IMHA (`H01`…`H16`), experimental `EXP1`…`EXP5`. Total 138. `group_label`: `natural cohort 1`, `natural cohort 2`, `control`, `IMHA`, `experimental low dose` (EXP1, EXP2), `experimental high dose` (EXP3, EXP4, EXP5). `outcome_label`: `died day 4` for EXP5, `survived` for EXP1 to EXP4, null for the rest.
- Section headers in the natural file assign cohort 1, cohort 2 and controls; rows whose `Study no` is empty are skipped (3 rows).
- Variables (codes requested by EXP07; keep them):

| Raw header (natural / IMHA) | Experimental prefix | code | unit | data_type | domain |
|---|---|---|---|---|---|
| `Age (months)` | – | `age_months` | months | N | signalment (`include_default` false) |
| `Weight (kg)` | – | `weight_kg` | kg | N | signalment (`include_default` false) |
| `Gender` | – | `sex` | Male / Female | C | signalment (`include_default` false) |
| `HGB (g/L)` | `HGB` | `haemoglobin` | g/L | N | haematology |
| `HCT (L/L)` | `HCT` | `haematocrit` | L/L | N | haematology |
| `MCHC (g/L)` | `MCHC` | `mchc` | g/L | N | haematology |
| `CHCM (g/L)` | `CHCM` | `chcm` | g/L | N | haematology |
| `Ret% (%)` | `Ret%` | `reticulocyte_pct` | % | N | haematology |
| `ARC (x10^9/L)` | `ARC` | `arc` | x10^9/L | N | haematology (`derived_from` [`reticulocyte_pct`]) |
| `MCVr (fL)` | `MCVr` | `mcvr` | fL | N | reticulocyte |
| `CHCMr (g/L)` | `CHCMr` | `chcmr` | g/L | N | reticulocyte |
| `CHr (pg/cell)` | `CHr` | `chr` | pg/cell | N | reticulocyte |
| `CHDWr (pg/cell)` | `CHDWr` | `chdwr` | pg/cell (pg in the experimental file) | N | reticulocyte |
| `RDWr (%)` | `RDWr` | `rdwr` | % | N | reticulocyte |
| `CHDelta (pg)` | `CHDelta` | `chdelta` | pg | N | reticulocyte (`derived_from` [`chr`]) |

- Plus `study_day`, `dose_group` (experimental dogs only) and `cohort_group` (C, `domain` `design`, `include_default` false; value = the group label, one observation per subject).
- time_point: `''` for natural, control and IMHA dogs; `D01`…`D06` for experimental dogs (`study_day` 1…6).
- Overlap check inside the script: read DS02 `Haematology` (read-only); for each experimental case, find the DS02 dog whose `Hb1`, `Hb2`, `Hb3`, `Hb4`, `Hb5`, `Hb6` equal the case's `HGB_Day 1`…`HGB_Day 6` (ignoring blanks). Assert the mapping is EXP1→dog2, EXP2→dog3, EXP3→dog4, EXP4→dog5, EXP5→dog6, and that ARC equals DS02 `Retic` at the same day for at least 90 % of non-empty cells. Write the mapping into the notes and into each EXP subject's `group_label` source (description of `cohort_group`).
- Implausible values: experimental case 5 `MCHC_Day 4` = 595 g/L and IMHA MCHC up to 478, `BC24` `RDWr` 1.6 and `CHDWr` 1.0: keep as recorded, list them in the notes (open question 4).
- Notes: CB115 reports 10 IMHA dogs, the file has 16; cohort definitions are truncated in the file; controls are older and mostly female; the five experimental dogs are the SRC-B beagles (so the `independent_source` SRC-E applies to the natural, control and IMHA dogs only; do not edit `datasets.jsonl`, report it).

#### `scripts/tidy_s-cb017.py` → `data/tidy/S-CB017.json`

- Script name follows the rule `tidy_<code lowercase>.py`; the hyphen is fine because the file is run, not imported. Dataset `code` = `S-CB017`.
- Subjects: 47 (16 healthy `H1`…`H8`, `HI1`…`HI8`; 13 `B1`…`B13`; 18 `BK1`…`BK18`). `group_label` `healthy` / `B. canis infected`. `outcome_label` `uncomplicated` (B prefix) / `complicated` (BK prefix) / null for healthy. Day block by row range (section 2.1); infected time_point `D01` / `D07`, healthy `''`.
- Variables:

| Raw header | code | unit | domain |
|---|---|---|---|
| `GM-CSF (pg/ml)` … `MCP-1 (pg/ml)` | `gm_csf`, `kc_like`, `il_2`, `il_7`, `il_8`, `il_10`, `il_15`, `il_18`, `mcp_1` | pg/mL | cytokine |
| `Leuko` | `wcc` | x10^9/L | haematology |
| `Lymph` | `lymphocytes` | x10^9/L | haematology |
| `Neseg. Neut` | `band_neutrophils` | x10^9/L | haematology |
| `Seg. Neut` | `seg_neutrophils` | x10^9/L | haematology |
| `Mono` | `monocytes` | x10^9/L | haematology |
| `Eos` | `eosinophils` | x10^9/L | haematology |
| `Thromb` | `platelets` | x10^9/L | haematology |
| `HMT` | `haematocrit` | L/L (file value in % divided by 100; say so in the description) | haematology |
| `Eryt` | `rcc` | x10^12/L | haematology |
| `Lymph %`, `Nes. Neut %`, `Seg neut %`, `Mono %`, `Eos %`, `Total gran` | `lymphocytes_pct`, `band_neutrophils_pct`, `seg_neutrophils_pct`, `monocytes_pct`, `eosinophils_pct`, `granulocytes_pct` | % | haematology (`include_default` false, `derived` true, `derived_from` the count and `wcc`) |
| `n:l` | `nl_ratio` | ratio | haematology (`derived` true, `derived_from` [`seg_neutrophils`, `band_neutrophils`, `lymphocytes`]) |
| column 11 of `CYTOKINES` | `dead_marker_in_file` | C (`Dead` / absent → no observation) | design (`include_default` false; description: "unexplained marker beside 9 complicated dogs; contradicts the article's single death; not an outcome") |

- Plus `complication_group` (C, `domain` `design`, `include_default` false; `uncomplicated` / `complicated` for infected dogs, `healthy` for healthy dogs; time_point `''`) and `study_day` (1 or 7 for infected dogs; no observation for healthy dogs).
- Data-entry rules: `BK9` D01 `Eryt` = 35 → missing; `B2` D07 `Seg. Neut` = 42 → missing; keep `BK12` D07 as recorded. Note each.
- Notes: cytokine draw 6 to 8 h after imidocarb on day 1; all infected dogs treated; day-7 values are post-treatment; floor values (IL-10 0.8, IL-18 2, IL-2 and IL-8 10, IL-15 12) kept and counted; H and HI are probably the article's subgroups 2a and 2b (8 healthy dogs given prophylactic imidocarb); complicated defined by WHO malaria-style criteria with SIRS, so WBC is label-defining; BK11 has no day-7 sample (the article's one death).

### 2.3 Variables and filters

Per sub-run, the **marker set** is numeric or ordinal variables with `include_default = true`, excluding `domain` in (`design`, `technical`, `signalment`), and requiring at least `min_dogs` (default 4 for beagle runs, 20 for S-CB017) dogs with at least `min_points` (default 3 for beagle runs, 2 for S-CB017) observations in the analysis window, and a non-zero variance. Dropped markers are listed in `run_notes`.

- **Analysis windows** (parameter `window`): beagle runs (DS01, DS02, DS03): primary `pretreatment` = study_day ≤ 4.5 (D-1 to D04.1 for DS01/DS02; D01 to D04 for DS03); secondary `full` = all days. DS06: primary `pretreatment` = D00, D01, D03, D04; `full` for the network (step 4). S-CB017: D01 and D07 (D07 is post-treatment; there is no pre-treatment window beyond D01).
- **Subjects**: infected dogs only (`dose_group` present); the donor (`dog1`, `low_0`) is excluded from models and listed. DS03: experimental dogs only for trajectories; natural, control and IMHA dogs are used only for the reference ranges in step 7.
- **Transform** (parameter `log_markers`): log(x + c) for skewed markers, with c = half the smallest positive value of that marker: all cytokines, `crp`, `parasitaemia_pct`, `cfhb`, `lactate_poc`, `lactate_vbg`, `arc`, `band_neutrophils`, `nrbc_per_100_wbc`. Others untransformed.
- **Floors**: in S-CB017, a marker with more than `max_floor_frac` (0.5) of values at its minimum is dropped from the latent-class model (IL-10 expected) but kept in the mixed models.
- **Outliers** (DS02 dog 5 cytokines days 6 and 8): kept in the main run; `full`-window sensitivity without them (step 8).

## 3. Method

One script, `scripts/experiment_trajectories.py`, run once per sub-run with `--dataset <code> --code <experiment code>`, and once with `--summary` for the umbrella run. Environment `.venv-nlp`. `--seed` default `20261105`; every random stream is `numpy.random.default_rng(seed + offset)` with fixed offsets per step (permutations +100000, bootstrap +200000, GMM `random_state` = seed + 300000, DTW none). Bit-for-bit reproducible.

1. **Load and shape.** Read the tidy file; build a long table (dog, marker, study_day, value); apply window, subject and transform rules (2.3).

2. **Linear mixed-effects models (every sub-run, every marker).**
   - Model: yᵢₜ = Xᵢₜβ + uᵢ + εᵢₜ, uᵢ ~ N(0, σ²ᵤ) dog random intercept, εᵢₜ ~ N(0, σ²). Fixed effects: intercept, day as a categorical factor (reference = the first window day: `D-1` for DS01/DS02, `D01` for DS03, `D00` for DS06, `D01` for S-CB017), group main effect (dose: `high` vs `low`; S-CB017: `complicated` vs `uncomplicated`), and group × day interactions. Days present for only one group (for example `D04.1`, low dose only) enter as a day level without an interaction term. Drop any column that makes X rank-deficient and list it.
   - Estimation: numpy REML for a single random intercept. With λ = σ²ᵤ/σ², V = I + λZZᵀ is block-diagonal by dog; profile out σ² and β (GLS: β̂ = (XᵀV⁻¹X)⁻¹XᵀV⁻¹y) and maximise the restricted log-likelihood ℓ_R(λ) = −½[(n − p)·log σ̂² + log|V| + log|XᵀV⁻¹X|] over log λ ∈ [−10, 10] with `scipy.optimize.minimize_scalar` (bounded; tolerance 1e-10). Use the per-dog block inverse (Sherman-Morrison) so no n × n matrix is formed. If the optimum is at the lower bound, report σ²ᵤ = 0 (equivalent to ordinary least squares).
   - Self-test (`--self-test`): on a simulated balanced one-way design (8 groups × 5 observations, seed fixed) REML σ²ᵤ must equal the ANOVA estimator (MSB − MSW)/5 to 1e-6, and β must equal the OLS mean.
   - Within-dog tests: Wald tests of day effects using the t distribution with residual df = n_obs − rank(X) − (n_dogs − 1) (conservative, as in a fixed-dog model). Omnibus day effect: Wald χ² over all day terms / its df, referred to F(df_day, df_resid). Per-day contrast versus reference: estimate, 95 % CI, p.
   - Between-dog tests (group main effect and group × day): exact permutation of group labels across dogs, refitting the model each time. Beagle runs: all distinct assignments (C(5,2) = 10), so p ≥ 0.1 by construction; S-CB017: `permutations` (default 5000) random relabellings of the 31 infected dogs keeping 13 / 18. Statistic = Wald χ² of the interaction block (S-CB017: also of the main effect, since only two days).
   - Effect size: each day contrast divided by the marker's pooled baseline SD (SD at the reference day across dogs), so markers are comparable; report also on the transformed scale.
   - Multiple testing: Benjamini-Hochberg across all association p values in the sub-run (`alpha` 0.05).
   - Stored as associations (2 per marker): (marker, `study_day`, test `lmm_day`, estimate = largest absolute standardised day contrast with its sign, `estimate_label` `max_std_day_effect`); (marker, `dose_group` or `complication_group`, test `lmm_group_x_day`, estimate = mean absolute standardised interaction, `estimate_label` `mean_std_interaction`). `detail` holds σ²ᵤ, σ², ICC, n_obs, n_dogs, all day contrasts with CI, permutation count, and dropped columns. `direction`: for `lmm_day`, `peak on D03` / `nadir on D04` (day of the largest contrast and its sign); for the interaction, the group with the larger mean standardised change.

3. **Trajectory clustering (every sub-run).**
   - Per-dog standardisation: for each (dog, marker), z-score that dog's own trajectory over the window (shape, not level); trajectories with fewer than `min_points` values or zero variance are dropped.
   - **Marker clusters** (which markers move together): distance between two markers = 1 − Pearson r of their per-dog z-trajectories concatenated across dogs on the days both observed (pairwise complete; require at least 8 shared points, else distance 1). Average linkage (`scipy.cluster.hierarchy.linkage(method="average")` on the condensed matrix). Number of clusters k chosen in 2…min(8, m − 1) by the mean silhouette on the precomputed distance; ties to smaller k. Sensitivity: dynamic time warping distance (numpy DTW on the dose-group mean z-trajectories, Sakoe-Chiba band `dtw_window` = 1 time step), same linkage and k; report the adjusted Rand index between the two partitions.
   - **Dog clusters** (stored as `cluster_assignments`): dog-to-dog distance = mean over shared markers of (1 − r) between the two dogs' z-trajectories on shared days; average linkage; k = `dog_k` (default 2). `cluster_label` `T1` / `T2` (ordered by the cluster containing the dog with the earliest parasitaemia peak where available, otherwise by size); `score` = silhouette of that dog. Cross-tabulate against dose group and outcome. Exact permutation check: share of the 10 possible 2/3 splits that agree with dose as well as or better than the observed clustering.
   - S-CB017 with two time points: marker clusters use the per-dog change (D07 − D01, on the transformed scale, standardised across dogs) as the trajectory; dog clusters are replaced by the latent classes of step 6.

4. **Co-expression modules (DS06 only), WGCNA-style, numpy plus scipy.**
   - Input: 3,000 genes × 28 samples (all days, `full` window, including `low_0`), log2 values from the tidy file.
   - Signed adjacency aᵢⱼ = ((1 + rᵢⱼ)/2)^β with Pearson r across samples.
   - Soft threshold β: for β in [1…10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30], connectivity kᵢ = Σⱼ aᵢⱼ − 1; scale-free fit = −sign(slope)·R² of log10 p(k) on log10 k over 10 equal-width bins of k (empty bins dropped). Choose the smallest β with fit ≥ `scale_free_r2` (0.80); if none, β = 16 (WGCNA guidance for signed networks with 20 to 30 samples). Store the whole fit table.
   - Topological overlap TOMᵢⱼ = (Σᵤ aᵢᵤaᵤⱼ + aᵢⱼ)/(min(kᵢ, kⱼ) + 1 − aᵢⱼ), diagonal 1; dissimilarity 1 − TOM.
   - Average-linkage tree on 1 − TOM; static cut at `cut_height` (0.97) with `scipy.cluster.hierarchy.fcluster(criterion="distance")`; clusters smaller than `min_module_size` (30) go to module `M0` (unassigned, WGCNA's grey). Number the remaining modules `M1`, `M2`, … by size.
   - Eigengenes: per module, first principal component of the gene-standardised expression (SVD); sign set so the eigengene correlates positively with the module's mean expression; variance explained recorded. Merge modules whose eigengenes correlate above 1 − `merge_cut` (merge_cut 0.25, so r > 0.75), recompute, renumber.
   - Module membership kME = Pearson r of each gene with each eigengene; hub genes = top 10 by kME in their module.
   - Composition check: correlation of each eigengene with log `library_size_m` and with `size_factor`; flag modules with |r| > 0.7 as likely composition or technical modules.
   - Eigengenes over days: run the mixed model of step 2 on each eigengene (`pretreatment` window D00 to D04, and `full`), and tabulate dose-group mean ± SD by day.
   - Within-dog sensitivity: centre each gene within dog (dropping `low_0`), rebuild the network at the chosen β, and report the adjusted Rand index of gene assignments against the main modules. Cut-height sensitivity at 0.95 and 0.99 (adjusted Rand index).
   - Gene-level associations: for DS06 the marker set in step 2 is the 3,000 genes (2 associations per gene, BH across all 6,000 tests in the sub-run). Dog clusters (step 3) use the module eigengenes (not genes) as markers.

5. **Reference context (DS03 only).** For the experimental dogs, express each reticulocyte marker at each day as a z-score against the 14 control dogs (median and MAD) and report, per day, the share of natural-cohort dogs (cohorts 1 and 2 pooled) whose value lies below the experimental dogs' median. Descriptive only; stored in the `mixed_effects` payload under `reference`.

6. **Latent-class trajectory grouping (S-CB017 only).**
   - Features per infected dog: for each latent-class marker (the 9 cytokines minus any dropped by `max_floor_frac`; haematology as a second, label-leaky set run separately), the transformed day-1 value and the change D07 − D01, each standardised across dogs. With two time points a growth-curve latent class model reduces to a mixture on (level, change); say so in the interpretation.
   - Model: `sklearn.mixture.GaussianMixture(covariance_type="diag", n_init=50, max_iter=1000, random_state=seed + 300000)` for K = 1…`max_classes` (4); choose K by BIC (ties to smaller K). Fit on the 30 dogs with both days; assign `BK11` (day 1 only) by the posterior from the marginal mixture over its day-1 features (diagonal covariance makes the marginal exact). Report entropy (1 − Σ p log p / (n log K)) and the smallest class size; if the smallest class has fewer than 4 dogs, also report the K − 1 solution.
   - Stability: refit on 200 bootstrap resamples at the chosen K; co-assignment matrix; mean adjusted Rand index of bootstrap versus full assignments (Hungarian matching not needed for ARI).
   - Class versus outcome: K × 2 table of class by `complication_group`; Fisher exact test when K = 2, otherwise permutation chi-square (`permutations` 5000, labels permuted across dogs); Cramér's V with bootstrap 95 % CI (2000); adjusted Rand index between classes and the label. Repeat for the haematology set and for the three article markers only (`mcp_1`, `kc_like`, `il_8`) as sensitivity.
   - `cluster_assignments`: one row per infected dog, `cluster_label` `LC1`…`LCK` (ordered by mean standardised day-1 MCP-1, lowest first), `score` = posterior probability of the assigned class.
   - Healthy dogs are not clustered; their medians are the reference shown in the class profiles.

7. **Cross-run summary (`--summary`, umbrella `EXP05-LONG-trajectories`, dataset null).** Reads the five sub-run JSON files (not the tidy files) and writes:
   - DS01 versus DS02 concordance: for shared markers, correlation and maximum absolute difference of the `lmm_day` estimates (expected identical; any difference is an extraction error).
   - DS03 versus DS02 concordance for `haemoglobin`, `arc`, `reticulocyte_pct` on shared days (same dogs).
   - DS06 eigengenes versus DS02 markers: correlation between dose-group mean eigengene trajectories and dose-group mean marker trajectories over shared days (0, 1, 3, 4, 6, 8); descriptive only, since dog identities across GEO and DS02 are not linked.
   - S-CB017 versus beagle cytokine direction for markers present in both (`gm_csf`, `kc_like`, `il_2`, `il_7`, `il_8`, `il_10`, `il_15`, `il_18`, `mcp_1`): sign of change after treatment, side by side. Different species (*B. canis* versus *B. rossi*): a comparison, not replication.
   - No associations, no cluster assignments.

8. **Sensitivity runs inside each beagle sub-run** (stored under `run_notes.sensitivity`): `full` window; DS02/DS01 `full` window without dog 5 day 6 and 8 cytokines; reference day `D00` instead of `D-1`. Report how many markers change BH significance.

## 4. Outputs

### 4.1 Experiment JSON

Six files in `data/experiments/`: `EXP05-DS01-trajectories.json`, `EXP05-DS02-trajectories.json`, `EXP05-DS06-trajectories.json`, `EXP05-DS03-trajectories.json`, `EXP05-SCB017-trajectories.json`, `EXP05-LONG-trajectories.json`.

`experiment` block (each sub-run): `code`; `name` (for example `Marker trajectories in experimentally infected beagles (DS02)`, `Chemokine trajectory classes in B. canis (S-CB017)`); `description`; `method` `trajectories`; `dataset` (`DS01`, `DS02`, `DS06`, `DS03`, `S-CB017`; umbrella `null`); `script` `scripts/experiment_trajectories.py`; `script_version` (12 hex of sha256); `run_utc`; `n_subjects` (dogs analysed; donor excluded); `n_variables` (markers analysed; DS06 = genes); `n_tests` (= len(associations)); `summary` (one paragraph with numbers and the sentence "Six animals permit description only." in beagle runs).

`parameters` (defaults; keys that do not apply to a sub-run are still written with value null):

```json
{
  "seed": 20261105, "window": "pretreatment", "reference_day": "D-1",
  "min_dogs": 4, "min_points": 3, "log_markers": ["gm_csf", "...", "crp", "parasitaemia_pct", "cfhb", "lactate_poc", "lactate_vbg", "arc", "band_neutrophils", "nrbc_per_100_wbc"],
  "reml_log_lambda_bounds": [-10, 10], "permutations": 5000, "bootstrap": 2000, "alpha": 0.05, "adjustment": "benjamini_hochberg",
  "marker_cluster_k_max": 8, "min_shared_points": 8, "dtw_window": 1, "dog_k": 2,
  "wgcna_top_genes": 3000, "wgcna_beta_grid": [1,2,3,4,5,6,7,8,9,10,12,14,16,18,20,22,24,26,28,30], "scale_free_r2": 0.8, "beta_fallback": 16,
  "cut_height": 0.97, "min_module_size": 30, "merge_cut": 0.25, "hub_genes": 10,
  "max_classes": 4, "gmm_n_init": 50, "gmm_bootstrap": 200, "max_floor_frac": 0.5
}
```

S-CB017 overrides: `min_dogs` 20, `min_points` 2, `reference_day` `D01`. DS03: `reference_day` `D01`. DS06: `reference_day` `D00`.

`associations[]`: written for every sub-run (section 3 step 2), variable codes from that sub-run's tidy file; `trivial` true when one variable is in the other's `derived_from` (not expected here). Umbrella: empty.

`cluster_assignments[]`: beagle and DS06 runs, one row per infected dog (`T1`/`T2`, silhouette); S-CB017, one row per infected dog (`LC1`…, posterior). Umbrella: empty.

`results[]` per sub-run:

| kind | title | sort_order | in runs |
|---|---|---|---|
| `interpretation` | Explanation and interpretation | 0 | all six |
| `trajectory_clusters` | Markers and dogs with similar trajectories | 1 | all sub-runs |
| `mixed_effects` | Mixed-model day and group effects per marker | 2 | all sub-runs |
| `modules` | Co-expression modules | 3 | DS06 |
| `module_eigengenes` | Module eigengenes over days | 4 | DS06 |
| `class_vs_outcome` | Latent trajectory classes against the complicated label | 3 | S-CB017 |
| `cross_dataset` | Agreement across the longitudinal datasets | 1 | umbrella |
| `run_notes` | Dogs, markers and days included, dropped or skipped | 9 | all six |

Payload schemas (small examples):

- `trajectory_clusters`: `{"days": ["D-1","D00","D01","D02","D03","D04","D04.1"], "marker_clusters": [{"cluster": "C1", "markers": ["crp","il_6","heart_rate"], "mean_profile_by_group": {"low": [..per day..], "high": [...]}}], "k": 4, "silhouette": 0.31, "merges": [[i, j, height, size]], "marker_order": [...], "dtw_ari": 0.62, "dog_clusters": {"k": 2, "assignments": {"dog2": "T1"}, "vs_dose": [[2,0],[1,2]], "vs_outcome": [...], "permutation_share_as_good": 0.3}}`. S-CB017: `trajectory` = `change D07 - D01`.
- `mixed_effects`: `{"window": "pretreatment", "markers": [{"code": "crp", "transform": "log", "n_obs": 30, "n_dogs": 5, "sigma2_dog": 0.12, "sigma2_resid": 0.4, "icc": 0.23, "day_effects": [{"day": "D03", "estimate": 1.8, "std_estimate": 2.1, "ci": [0.9, 2.7], "p": 0.002}], "group_by_day": [{"day": "D03", "estimate": 0.9, "ci": [...], "perm_p": 0.2}], "means": {"low": {"D-1": ...}, "high": {...}}}], "reference": null}` (DS03 fills `reference`).
- `modules` (DS06): `{"beta": 14, "scale_free_fit": [{"beta": 1, "r2": 0.1, "mean_k": 950}], "cut_height": 0.97, "n_modules": 9, "modules": [{"module": "M1", "n_genes": 610, "variance_explained": 0.58, "hub_genes": [{"code": "g_ENSCAF...", "symbol": "ALAS2", "kme": 0.97}], "r_library_size": -0.81, "flag_composition": true}], "genes": [{"code": "g_...", "module": "M1", "kme": 0.91}], "sensitivity": {"cut_0.95_ari": 0.8, "cut_0.99_ari": 0.7, "within_dog_ari": 0.5}}`. Keep under 2 MB: the `genes` array holds 3,000 short rows.
- `module_eigengenes` (DS06): `{"days": ["D00","D01","D03","D04","D06","D08"], "eigengenes": [{"module": "M1", "values": [{"subject": "high_1", "time_point": "D03", "value": 0.31}], "mean_by_group_day": {"high": {"D00": -0.1, "...": 0}, "low": {...}}, "lmm": {"day_p_min": 0.001, "interaction_perm_p": 0.1}}]}`.
- `class_vs_outcome` (S-CB017): `{"feature_sets": [{"set": "cytokines", "markers": [...], "dropped_floor": ["il_10"], "bic": [{"k": 1, "bic": 812.3}], "k": 2, "entropy": 0.86, "class_sizes": {"LC1": 17, "LC2": 14}, "class_profiles": [{"class": "LC1", "marker": "mcp_1", "day1_mean_z": -0.4, "change_mean_z": 0.1}], "crosstab": {"rows": ["LC1","LC2"], "cols": ["uncomplicated","complicated"], "counts": [[10,7],[3,11]]}, "test": "fisher_exact", "p": 0.03, "cramers_v": 0.39, "cramers_v_ci": [0.1, 0.65], "ari": 0.12, "bootstrap_mean_ari": 0.7}, {"set": "haematology", ...}, {"set": "article_markers", ...}], "healthy_reference": {"mcp_1": {"median": 177, "iqr": [160, 200]}}}`.
- `cross_dataset` (umbrella): `{"ds01_vs_ds02": {"n_markers": 30, "max_abs_diff": 0.0}, "ds03_vs_ds02": [...], "ds06_vs_ds02": [{"module": "M1", "marker": "haemoglobin", "r_group_mean": -0.9, "n_points": 12}], "scb017_vs_beagle": [{"marker": "il_8", "beagle_direction": "rise after treatment", "scb017_direction": "rise D01 to D07 in uncomplicated"}]}`.
- `run_notes`: `{"subjects_included": [...], "subjects_excluded": [{"code": "dog1", "reason": "donor, single baseline"}], "markers_included": [...], "markers_dropped": [{"code": "basophils", "reason": "zero variance"}], "rank_deficient_columns": [...], "sensitivity": [{"analysis": "full window", "n_significant": 12, "changed": ["il_2"]}], "reml_boundary_fits": ["il_15"], "environment": {...}, "runtime_seconds": ...}`.

`interpretation` sections (headings, in order): `Question`, `What was done`, `What moved and when`, `Groups of markers` (DS06: `Gene modules`; S-CB017: `Trajectory classes and the complicated label`), `Limits`. Beagle runs state in `Limits`: "Six animals permit description only: two low-dose and three high-dose dogs, one of which died on day 4. No result here is a test of dose or a basis for prediction." The umbrella interpretation summarises the five runs and the overlap findings (DS01 = DS02; DS03 experimental = DS02 dogs).

### 4.2 Other artefacts

Tidy files `data/tidy/DS01.json`, `DS02.json`, `DS06.json`, `DS03.json`, `S-CB017.json`. Nothing else.

## 5. Acceptance checks

1. Tidy counts: DS02 6 subjects (1 donor, 2 low, 3 high); DS01 6 subjects and 0 value mismatches against DS02 (the script prints the count); DS06 6 subjects, 28 subject × time points, 3,000 gene variables, `high_3` has D00, D01, D03 only; DS03 138 subjects (85 + 18 + 14 + 16 + 5) and the EXP-to-dog mapping printed and asserted; S-CB017 47 subjects, 31 infected at `D01`, 30 at `D07`, no `BK11` at `D07`, `haematocrit` values between 0.1 and 0.7.
2. Spot checks: DS02 `dog2` `haemoglobin` at `D04.1` = 127; `dog6` `lactate_vbg` at `D04` = 7.5; DS02 `dog4` `parasitaemia_pct` at `D04` = 34.95; DS03 `EXP3` `haemoglobin` at `D04` = 95; DS06 `low_1` gene `g_ENSCAFG00000000007` at `D04` has the lowest value of that dog's series (raw count 99 against about 1,000 to 1,600); S-CB017 `BK16` `mcp_1` at `D01` = 1232.3.
3. Console load from the repository root: `dotnet run --project console/Babesiosis.Console -- --datasets-only`; no orphan errors. SQL per code: association count = `n_tests`; cluster-assignment count = infected dogs (5, 5, 5, 5, 31; umbrella 0); experiment_result rows = number of result kinds listed for that run.
4. REML self-test passes (`--self-test` prints PASS for the ANOVA identity and for a DTW distance check on two hand-computed sequences).
5. Reproducibility: rerun DS02 and S-CB017 with the same seed; identical JSON apart from `run_utc` and `runtime_seconds`.
6. Null behaviour: `--shuffle-days` (permutes day labels within each dog, seed + 1, writes only with `--out <scratch path>`) gives BH-significant `lmm_day` results in no more than 5 % of markers; in S-CB017 a `--shuffle-labels` run gives class-versus-outcome p ≥ 0.05 in at least 19 of 20 seeds (run 20 seeds with `--quick`).
7. Sanity against the articles: in DS02, parasitaemia rises earlier in high-dose dogs (first non-zero D01 versus D03); CRP and IL-6 show positive day effects by D03 to D04; ARC drops between D03 and D04 in high-dose dogs (CB115); in S-CB017, day-1 MCP-1 is higher in complicated dogs (direction), and IL-8 rises from D01 to D07 in uncomplicated dogs. In DS06, at least one module correlates strongly with library size (expected erythroid or composition module): report it rather than hide it.
8. DS01 versus DS02 `lmm_day` estimates for shared markers agree to 1e-9 (umbrella `cross_dataset`).
9. The interpretations contain the sentence on six animals, use "phenotype groupings" or "trajectory classes", never "subtypes", and never call a class predictive.

## 6. Caveats and reporting language

- **Six animals permit description only.** Five infected beagles (2 low, 3 high), one death; DS01, DS02, DS06 and the experimental part of DS03 are all the same dogs (cohort CH09), so the four beagle sub-runs are four views of one experiment, not replication. Dose comparisons have 10 possible label assignments and a minimum p of 0.1.
- Dose, disease stage and treatment are confounded: high-dose dogs were treated at 96 h, low-dose at 108 h; days 5 to 8 are post-treatment, and the dog that died has no later data (informative missingness). There is no uninfected or untreated control; the day −1 and day 0 samples are the only baseline, and day 0 carries a handling leukocytosis.
- Cytokine units are presumed pg/mL; floor values are censored, not true zeros; dog 5's post-treatment cytokine values look like assay saturation.
- DS06: whole-blood transcription mixes regulation with cell-composition change (erythroid and reticulocyte RNA rises as library sizes collapse at D3 and D4). Modules that track library size are composition modules first. Gene modules from 28 correlated samples of 6 dogs are exploratory; WGCNA assumes independent samples.
- DS03: the natural, control and IMHA groups are single-visit and are only reference context; IMHA n in the file (16) differs from the article (10); `independent_source` SRC-E does not apply to the five experimental dogs.
- S-CB017: *B. canis*, not *B. rossi*; two time points only, so "trajectory" means level plus change; day-1 cytokines were drawn 6 to 8 h after imidocarb; the complicated label is defined by SIRS and WHO-style criteria, so WBC and inflammatory markers partly define it; 31 dogs, 18 events. The `Dead` column in the file is not used.
- Wording: "trajectory classes" or "phenotype groupings", never "subtypes"; "descriptive kinetics"; no class or cluster is a prognostic tool.

## 7. Build plan for the agent

All commands from `C:\Workspaces\Babesiosis\core` unless stated.

1. **Read.** `experiment_specs/README.md`, this spec, `scripts/tidy_ds05.py`, `scripts/experiment_pairwise.py`, the five inspection JSONs and `datasets.jsonl` records, the five article notes. Done when you can state each file's layout as in 2.1.
2. **Tidy DS02.** Write and run `.venv/Scripts/python.exe -I scripts/tidy_ds02.py`. Done when acceptance checks 1 and 2 pass for DS02.
3. **Tidy DS01.** `.venv/Scripts/python.exe -I scripts/tidy_ds01.py`; done when it reports 35 blocks and 0 mismatches against DS02.
4. **Tidy DS03.** `.venv/Scripts/python.exe -I scripts/tidy_ds03.py`; done when 138 subjects and the asserted mapping EXP1→dog2 … EXP5→dog6 print.
5. **Tidy S-CB017.** `.venv/Scripts/python.exe -I scripts/tidy_s-cb017.py`; done when 47 subjects, 31 / 30 infected per day.
6. **Tidy DS06.** `.venv/Scripts/python.exe -I scripts/tidy_ds06.py`; done when 3,000 genes × 28 samples and the file is under 20 MB.
7. **Script.** Write `scripts/experiment_trajectories.py` with a docstring (inputs, outputs, every flag including `--dataset`, `--code`, `--summary`, `--seed`, `--window`, `--quick`, `--self-test`, `--shuffle-days`, `--shuffle-labels`, `--out`, dependencies numpy, scipy, scikit-learn, environment `.venv-nlp`, and the run commands below). Add `scipy>=1.11` and `scikit-learn>=1.5` to `scripts/requirements-experiments.txt`. Done when `--self-test` prints PASS.
8. **Run** (each under 5 minutes; DS06 the longest):
   - `.venv-nlp/Scripts/python.exe -I scripts/experiment_trajectories.py --dataset DS02 --code EXP05-DS02-trajectories`
   - `.venv-nlp/Scripts/python.exe -I scripts/experiment_trajectories.py --dataset DS01 --code EXP05-DS01-trajectories`
   - `.venv-nlp/Scripts/python.exe -I scripts/experiment_trajectories.py --dataset DS03 --code EXP05-DS03-trajectories`
   - `.venv-nlp/Scripts/python.exe -I scripts/experiment_trajectories.py --dataset DS06 --code EXP05-DS06-trajectories`
   - `.venv-nlp/Scripts/python.exe -I scripts/experiment_trajectories.py --dataset S-CB017 --code EXP05-SCB017-trajectories`
   - `.venv-nlp/Scripts/python.exe -I scripts/experiment_trajectories.py --summary --code EXP05-LONG-trajectories`
9. **Load.** From `C:\Workspaces\Babesiosis`: `dotnet run --project console/Babesiosis.Console -- --datasets-only`; run the SQL checks of acceptance check 3 (column names from `console/Babesiosis.Console/Database/schema.sql`).
10. **Verify.** Acceptance checks 4 to 9; write results with numbers into your final report. Delete any shuffled or quick outputs written outside the scratchpad.
11. **Document.** Rows for the five tidy scripts and `experiment_trajectories.py` in `scripts/README.md`; dataset and experiment entries in `docs/database.md` if it enumerates them; EXP05 status in `docs/ml-experiment-plan.html`. Report (do not edit) that `datasets.jsonl` lists DS03 as SRC-E although its experimental dogs are SRC-B.
12. **Optional.** A web view for method `trajectories` (small-multiple line charts by dose group, module heat map) only after everything passes.

## 8. Open questions

1. **DS01 as a separate sub-run.** DS01 is a strict subset of DS02 (same dogs, same values). Default: build and run it as specified, as an extraction-consistency check; the interpretation says it adds no information. If unwanted, skip task 3 and the DS01 run.
2. **DS02 monocyte value 68 (dog 2, day 7).** Default: stored as missing with a note. Alternative: recode to 0.68.
3. **GEO dog identities (DS06).** `high_3` is almost certainly DS02 dog 6 (died day 4) and `low_0` may be the donor (dog 1), but the other mappings are not stated. Default: keep GEO names; no cross-dataset per-dog linkage; the umbrella compares group means only.
4. **Implausible reticulocyte values in DS03** (EXP5 MCHC day 4 = 595 g/L; IMHA MCHC up to 478; BC24 RDWr 1.6, CHDWr 1.0). Default: keep, list in notes, and run the DS03 models with and without EXP5 day 4 MCHC as a sensitivity.
5. **Day 0 versus day −1 as baseline.** Default: `D-1` (before handling leukocytosis); `D00` as sensitivity.
6. **D04.1 handling.** Default: its own day level (study_day 4.5) without an interaction term because only low-dose dogs have it.
7. **S-CB017 healthy subgroups H and HI.** Default: pooled as healthy (the article merged them); not used in models.
8. **Number of DS06 genes.** Default 3,000 by variance across all samples. If the composition effect dominates selection, an alternative is variance after within-dog centring; report as sensitivity only.
9. **Haematology in the S-CB017 latent classes.** WBC and haematocrit partly define "complicated". Default: cytokines are the primary feature set; haematology reported separately and labelled as label-leaky.
