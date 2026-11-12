# SV-G2 report: severity literature extraction (schema v2)

Experiment `SV-G2-01-literature-extraction`, method `literature_extraction`, run 2026-11-12. Descriptive; no hypothesis test.

## 1. Question

Which laboratory markers and host or parasite factors have canine babesiosis studies tested against severity or outcome, under which severity definitions, and in how many independent cohorts? The package extends the 10-article pilot to every full-text tier A/B article, adds the fields that SV-03 (evidence matrix) and SV-02a (parasite load by outcome) need, and measures how reliable the extraction is.

## 2. Inputs

| File | SHA-256 |
|---|---|
| `/core/data/severity/shortlist.csv` | `6dbc75a910393aafbb838091a85d4a753e7254e20cb6dc562070b95de677ba51` |
| `/core/data/severity/association_schema.json` (pilot schema) | `e1ec14b3fbe6673b3b761a42726cccd48adde90c0c74b3d180724d2d2843bfd6` |
| `/core/data/severity/EXTRACTION_GUIDE.md` | `aebf7e43e01898a7c6e6d68203e5c12809eb139d59d65dd782099c7caf3b21ca` |
| `/core/data/severity/marker_map.csv` | `083bedab63112961bef755b2f07e8d28fef043e16a5a7998a1e8a20457096f85` |
| `/core/cohorts.json` | `b2eb1cae1f9300a09ce37ae910ab3b454f2682d0445cbff91093674db75e51bc` |
| `association_schema_v2.json` (built by `scripts/make_schema_v2.py`) | `01ef442d74fe30d53e891765c282a4dd8c7ddc0a9bc26b86f340989d4567bc0f` |
| `spec.md` | `b1b12dafb7675a31a450c66dc13c62c9aee8462888980934f38aeb4af19be880` |

Article texts: `/core/data/markdown/<ID>.md`, or `<ID>.en.md` where it exists (copyrighted, not copied; only short verbatim quotes are in the extraction files). No dog-level outcomes file was opened (`exposure.md`).

## 3. What was done

- **Scope.** 117 articles (116 CB, 1 BG), 99 independent units (cohort in `/core/cohorts.json`, else the article). The 34 abstract-only tier B articles were not extracted (later sensitivity set).
- **Schema v2** adds `setting`, `sample_timing`, `not_extracted`, and per definition `components`, `euthanasia_included`, `definition_source`, `follow_up_horizon`, and per row `severe_value`, `comparison_value`, `summary_type`, `load_method`. Enum values added beyond the package text are listed in `spec.md`.
- **Extraction.** First a calibration batch: the 10 pilot articles were re-extracted (two sub-agents, B00a and B00b) without access to the pilot files. Then 11 sub-agents extracted 9–10 articles each (B01–B11), and 3 sub-agents did the blind second extraction (S1–S3). Each sub-agent wrote only its own folder. All were Claude `claude-opus-5-5` sub-agents.
- **Checker.** `scripts/check_associations.py` was restored from `8d4c6d9` (the original is kept as `check_associations_pilot.py`) and extended for v2. It reads from `SV-G2/`, writes nothing to `/core/`, and checks numbers in the per-group values too.
- **Owner checks.**
  - Spot-checks by hand: 16 articles, at least one per batch (`owner_spot_checks.csv`). 13 agree with the text. 3 are flagged as judgement calls that were kept:
    - CB105: experimental dose groups coded as a severity contrast.
    - CB045: cPL used as a continuous pancreatitis severity measure.
    - CB098: parasitaemia used as a continuous severity measure.
  - Marker proposals from 9 batch files were merged into `marker_map_v2_additions.csv`: 18 new canonical names, for example Collapse, SIRS status, Basophil count, Thrombomodulin, HMGB-1, suPAR, Urine creatinine and Fractional excretion of electrolytes.
  - The 6 differences from the second extraction were resolved against the text (`agreement_resolutions.csv`; 3 primary files changed: CB098, CB106, CB517).
- **Deviations from `spec.md`.**
  - B00 was split into two sub-agents of 5 articles, because the pilot articles are long.
  - The blind second extraction started at the same time as the main batches rather than after them. It was still blind: the second agents were told not to open the primary folders.
  - The agreement resolutions log is `agreement_resolutions.csv` in the package root, not `out/`, so that a clean rerun keeps it.

## 4. Results

**Coverage.** All 117 articles were extracted; none is missing.

- **Articles with severity results.** 49 articles in 42 independent units report at least one marker or factor against a severity or outcome definition. All 42 units are canine.
- **Articles with none: 68 of 117 (58%).** Most compare infected with healthy dogs only, are case series without groups, or are experimental studies with no outcome contrast. The NLP shortlist's tier A/B therefore over-states how much severity evidence there is; the true base is about 42 units.
- **Volume.** 78 severity definitions and 740 rows. By significance: 260 significant, 254 not significant, 192 descriptive only, 34 unclear.
- **Markers.** 131 canonical markers; 75 are reported in 2 or more units.

**Markers by independent units** (`out/tables/markers.csv`). The columns are significantly higher in severe / significantly lower in severe / not significant; the remaining units are descriptive only.

| Marker | Units | Higher / lower / not significant |
|---|---|---|
| Haematocrit/PCV | 21 | 1 / 7 / 4 |
| Creatinine | 16 | 4 / 0 / 3 |
| Urea | 16 | 7 / 0 / 2 |
| Platelet count | 15 | 2 / 1 / 3 |
| White blood cell count | 15 | 3 / 1 / 4 |
| Bilirubin | 14 | 4 / 0 / 4 |

These are direction counts, not effect sizes.

**Host and parasite factors** (units):

- Age 12
- Sex or neuter status 8
- Parasitaemia 6
- Body weight 5
- Breed 5
- Co-infection 4
- Parasite species or genotype 2
- Travel history 1
- Days sick 1
- Parasite DNA load (qPCR) 1
- Prior treatment 1
- Splenectomy: 0. Antibody titre or serostatus: 1 unit (CH12, CB141, correlation with a haematological score; class immunology, so it is not in the host-factor table).

**Parasite load method** (SV-02a): 6 units with parasitaemia rows. The method is "smear, site not stated" in 4, capillary smear in 1, and venous smear in 1. One unit used ddPCR (coded `other`). Load against outcome is thin: no unit reports parasitaemia significantly higher in the severe group.

**By species** (units with rows):

- *B. rossi* 11
- *B. canis* 16
- *B. gibsoni* 4
- *B. vogeli* 1
- Mixed or unspecified 11

**By outcome class** (units using it):

- mortality 16
- severity grade or score 11
- anaemia grade 10
- complicated vs uncomplicated 9
- specific complication 8
- parasitaemia level 3
- treatment intensity 3
- other 2
- organ dysfunction 1

**Definition components** (units):

- death 20
- other 15
- renal 14
- anaemia grade 13
- hepatic or icterus 11
- cerebral 7
- pulmonary 6
- collapse 6

**Euthanasia and timing.**

- Euthanasia in mortality definitions: included 11, not stated 6, excluded 1.
- Setting (articles): referral hospital 59. The rest are spread over mixed, primary clinic, experimental, laboratory, field and shelter settings.
- Sample timing (articles): not stated 74, before treatment 29, mixed 14.

**Cohorts.** 14 shared cohorts contribute rows. The largest is CH03 (CB050, CB145 and CB517: one Onderstepoort *B. rossi* cohort, 53 rows, counted once).

**What could not be extracted** (items / articles):

- no per-group result 29 / 28
- figure only 19 / 17
- supplement not in text 12 / 11
- other 6 / 5
- outcome groups mixed with controls 3 / 3
- garbled table 1 / 1
- group sizes unclear 1 / 1

## 5. Stability and checks

- **Checker.** All 740 row quotes and all 78 definition quotes are exact. There are no schema errors and no unmapped markers. 3 rows have a number the checker cannot find, all explained in the row notes: one lactate IQR garbled in the PDF conversion (CB040), and degrees of freedom printed as "F 1, 362" (CB492, 2 rows).
- **Blind second extraction** (24 articles, seed 20261112). Rows were matched on article, canonical marker and outcome class.
  - Coverage: 0.954 of the primary keys were found by the second extractor, and 1.00 of the second extractor's keys by the primary.
  - Significance agreement 0.990, kappa 0.985, on 104 matched pairs.
  - Direction agreement 0.981.
  - Outcome classes: Jaccard 0.958; the sets are identical in 23 of 24 articles.
  - The spec's threshold (agreement ≥ 0.8, coverage ≥ 0.7) is met.
- **Calibration against the pilot** (10 articles, schema v1 extractions by another agent).
  - Coverage 0.92 in each direction.
  - Significance agreement 0.922, kappa 0.863, on 141 matched pairs.
  - Direction agreement 0.957.
- **Rerun.** `out/` was deleted and rebuilt from the commands in `run.md`. `out/`, `associations_v2.csv` and `definitions_v2.csv` came back byte-identical.

## 6. Confounders

- **Handled.** Cohorts are counted once (independent units), and the BG article is flagged.
- **Not handled.**
  - Species is aliased with source, setting and definition, so the species counts are not a species comparison.
  - Cohort links come from `/core/cohorts.json` only. CB040 (320 Onderstepoort *B. rossi* dogs, 2006–2016) is a unit of its own there, although its dogs very probably overlap CH03, CH04 and CH09. SV-03 should treat Onderstepoort *B. rossi* units as possibly overlapping.
  - Selective reporting: markers printed only when significant inflate the direction columns. SV-03 will report the share of not-significant rows by article.

## 7. What this does not show

- It is not a synthesis, and direction counts are not effect sizes.
- Several judgement calls change what counts as "severity". They are flagged and should be reviewed in SV-03:
  - dose groups (CB105)
  - continuous cPL (CB045)
  - continuous parasitaemia (CB098)
  - renal markers as continuous severity (CB441)
  - transfusion as treatment intensity (CB418)
- Extraction was done by language-model agents with an owner spot-check of 16 articles, not by a full human review. Two texts (CB187, CB537) are unreviewed machine translations.

## 8. Verified, documented or inferred

- **Verified in files.** Quotes (checker), the spot-checked rows (`owner_spot_checks.csv`), and all counts (computed by the scripts from the extraction files).
- **Taken from documentation.** Cohort membership (`/core/cohorts.json`) and article species (`/core/articles.jsonl`; species groups were mapped by keyword in `build_results.py`).
- **Inferred.** That the 68 articles with no rows have no severity contrast. Each is explained in its `article_notes`; the spot-checks and the second extraction agree on all 11 such articles in the sample (the second extractor also found no rows).

## 9. Next step and decisions

- SV-03 and SV-02a can start. Their inputs are `associations_v2.csv` and `definitions_v2.csv`, with the columns the package names.
- **User decision.** Whether these v2 extractions should replace the pilot under `/core/data/severity/` (`extractions/`, `associations.csv`, `marker_map.csv`). Nothing in `/core/` was changed.
- **User decision.** Whether to add the 18 new canonical marker names (`marker_map_v2_additions.csv`) to `/core/data/severity/marker_map.csv`.
- **Optional.** Extract the 34 abstract-only tier B articles as the sensitivity set.

Versions: Python 3.13.14 (standard library only), uv 0.10.4, console loader `/console/Babesiosis.Console` (.NET 10), Angular build of `/webapp/Babesiosis.Web`.
