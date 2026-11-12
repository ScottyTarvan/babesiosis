# SV-08 report: human severity signatures in the Beagle transcriptome

Experiment `SV-08-01-transcriptome-signatures`, method `transcriptome_signature`, role primary (exploratory: 5 dogs, one source),
run 2026-11-12. Spec SHA-256 `e7fdfabd75daee92de3c97b7b0e51f5967889297d539257b2590c1fa1d557547`.

## 1. Question and hypothesis

Do the whole-blood signatures of severe human malaria (neutrophil granule and type 1 interferon genes) rise in the five *B. rossi*
Beagles before treatment, before clinical deterioration, and earlier at the high dose? Hypothesis: both scores rise in most dogs beyond
the composition shift of the day 3 and day 4 libraries, and rise first in the high-dose dogs.

## 2. Inputs

| File | SHA-256 |
|---|---|
| `/core/data/raw/DS06/GSE167201_raw_counts.txt.gz` (DS06, 12,362 genes x 28 samples) | `b2575d138ca08fb7292f3fa46d9f296f02a3d3306f53813b962ce4c993189fc3` |
| `shared/tidy/DS02.features.json` (SV-G1) | `12475e823e588af20e8bec2df5164979c158bdbbb86ddfb96a32afe8aad83e2d` |
| `shared/tidy/DS02.outcomes.json` (SV-G1; `habitus_score` only) | `26831fd671b6168a9228852823d73150cb48896d309f395c9a91858c4506dd67` |
| `ref/symbol_xrefs.json` (Ensembl REST, release 116) | `d2498ae35c3201c7f6fe4c485b25916d8f0fe23ded73a93055edffd655a60efd` |
| `ref/unsymbolled_lookup.json` (Ensembl REST, release 116) | `63e21a82264e47daa51f76835dbc85841628f8610d399771894b998ab80867d1` |
| `scripts/gene_sets.json` (the sets of the package file) | `a56f017dc465b5ee61cf8135460c5dee8b7a5177dd4c8d47b292d3c194a03f4d` |
| `spec.md` | `e7fdfabd75daee92de3c97b7b0e51f5967889297d539257b2590c1fa1d557547` |

Independent sources: 1 (SRC-B). DS02, DS03 experimental and DS06 are the same Beagles (SV-G1, SV-07). `exposure.md` has the
outcomes lines.

## 3. What was done

Python 3.12.12, numpy 2.3.4, scipy 1.16.3 (`scripts/analyse.py` 4cb7afc19085, `scripts/build_load.py` 5b093e0b06e7,
`scripts/fetch_annotation.py` 9d60cbe69e83). As `spec.md`:

- **Score.** All 12,362 genes ranked inside each sample; set score = mean rank percentile (0 to 1) of the mapped set genes.
- **Primary.** Per dog, change from D0 to the last pre-treatment sample (D4; D3 for `high_3`, which died on day 4). Sign count per set,
  exact two-sided sign test (smallest attainable p with 5 dogs: 0.0625). Family of 2 sets; erythroid set reported as a control.
- **Composition background.** Per dog and set, 2,000 random gene sets matched on the dog's D0 expression decile (seed 20261112).
  "Beyond background" = background percentile >= 0.975.
- **Timing.** First sampled day beyond background, against the first day the DS02 habitus score fell below its day −1/0 value. Under the
  working DS06-to-DS02 mapping (SV-07's best value assignment; `high_3` = dog 6 probable, the rest unverified) and the alternative
  (the two dogs of each dose group swapped).
- **Construct checks**, sensitivity S1 to S4, as the spec.

**Deviations and clarifications**

- **D0 (outcome lock).** Before the spec was written, a format probe printed the two outcome definitions of `DS02.outcomes.json`
  (`died`, `habitus_score`); no value. Recorded in `exposure.md`.
- **D1 (gene mapping source).** The spec says "dog Boxer / CanFam3.1-lineage annotation". The CanFam3.1 BioMart archive (Ensembl 103)
  is gone (redirects), so mapping rules 2 and 3 used Ensembl REST release 116 (Boxer, assembly Dog10K_Boxer_Tasha), which keeps the
  CanFam3.1 stable IDs still in use. 854 of the 1,922 DS06 rows without a symbol are retired IDs in release 116 and could not be
  annotated; a set gene hidden among them (most likely HBB) cannot be ruled out.
- **C1 (S3).** The spec does not say what to do with set genes that pass the ALAS2-correlation filter. They were kept in every set.
  Only ALAS2 itself would have been removed (rho 1.0; SLC4A1 0.62; all others ≤ 0.50); 105 background genes were removed.
- **C2 (construct checks).** DS02 has no reticulocyte value on day 0, so the erythroid check has 3 points per dog (2 for `high_3`, no rho).
- **C3 (timing).** The extra low-dose `day_4_1` habitus value counts as day 4. Every dog's baseline habitus was 4.
- No other deviation.

## 4. Results

**Gene mapping.** Type 1 interferon 11 of 11 genes; neutrophil granule **6 of 11** (CTSG, LTF, LCN2, MMP8, MMP9, CAMP); erythroid 2 of
3 (ALAS2, SLC4A1). Not mapped (`out/unmapped_genes.csv`): MPO, ELANE, OLFM4, ARG1 (dog genes exist in Ensembl but are not in the DS06
matrix, which was pre-filtered by CPM: too low in whole blood), CEACAM8 and HBB (no dog gene with that symbol in Ensembl and no unnamed
DS06 row annotated as it). The scored neutrophil set is therefore mostly secondary and tertiary granule genes (LTF, LCN2, MMP8, MMP9,
CAMP) plus CTSG; the promyelocyte genes MPO and ELANE, central to the human signature, are missing.

**Primary (D0 to last pre-treatment sample), 5 dogs, 1 source:**

| Dog | Type 1 interferon change (background percentile) | Neutrophil granule | Erythroid control |
|---|---|---|---|
| low_1 (low dose) | +0.305 (1.00) | +0.102 (0.96) | +0.345 (1.00) |
| low_2 (low dose) | +0.422 (1.00) | +0.130 (0.99) | +0.290 (1.00) |
| high_1 (high dose) | +0.174 (1.00) | +0.167 (1.00) | +0.243 (1.00) |
| high_2 (high dose) | +0.027 (0.77) | +0.276 (1.00) | +0.219 (1.00) |
| high_3 (high dose, died day 4; last sample D3) | +0.386 (1.00) | +0.190 (1.00) | +0.232 (0.98) |

The 95% range of the random-set changes is about −0.06 to +0.08 (interferon) and −0.06 to +0.12 (neutrophil) per dog.

- **Type 1 interferon:** higher in **5 of 5 dogs** (sign-test p 0.0625), beyond background in **4 of 5**. Median change +0.305.
- **Neutrophil granule:** higher in **5 of 5** (p 0.0625), beyond background in **4 of 5**. Median change +0.167.
- **Erythroid control:** higher in 5 of 5, beyond background in 5 of 5: the reticulocyte shift is real, and both signatures rise beyond
  what matched random genes do under the same shift.
- By the spec rule, both signatures **appear**. 0 of 2 sign tests below 0.05 (none can be).

**Timing** (working mapping; the alternative gives the same answers):

| Dog | Interferon first risen | Neutrophil first risen | Habitus first fell |
|---|---|---|---|
| low_1 (dog 2) | day 3 | day 3 | day 4 |
| low_2 (dog 3) | day 1 | day 3 | day 4 |
| high_1 (dog 4) | day 1 | day 1 | day 2 |
| high_2 (dog 5) | day 1 | day 4 | day 2 |
| high_3 (dog 6) | day 1 | day 1 | day 3 |

- **Before clinical deterioration: yes.** The interferon score was beyond background on a sampled day before the habitus fell in all 5
  dogs; the neutrophil score in 4 of 5 (not high_2, whose neutrophil rise came on day 4, after its habitus fell on day 2).
- **Earlier at the high dose: not met (negative).** The spec needs every high-dose dog to rise before both low-dose dogs. The interferon
  score rose on day 1 in all three high-dose dogs but also in low-dose `low_2`. The pattern is a shift in the peak rather than in the
  onset: the interferon score **peaked on day 1 in high_1 and high_2 (and was still rising at day 3 in high_3) and fell back by day 4**
  (high_2 at day 4 is back inside the background, which is why its primary change is small), while both low-dose dogs peaked on day 4.
  This was not a spec rule; it is a description.

**Construct checks** (median of per-dog Spearman rho over 3 or 4 pre-treatment points; working / alternative mapping): interferon score
with plasma IP-10 (CXCL10 protein) +1.00 / +0.95 (every dog ≥ 0.80); neutrophil score with band neutrophils +0.80 / +0.80 (two dogs
negative); erythroid score with reticulocyte % +1.00 / +1.00. The transcript scores follow the matching blood measures; the checks do
not separate the two mappings.

## 5. Stability and sensitivity

| Check | Interferon: dogs with a rise | Neutrophil: dogs with a rise |
|---|---|---|
| Primary | 5 (4 beyond background) | 5 (4 beyond background) |
| S1: D3 as last sample for every dog | 5 (5 beyond background) | 5 (4 beyond background) |
| S2: log2 upper-quartile CPM | 4 (high_2 −0.14) | 5 |
| S3: ranks without 105 reticulocyte-shift genes | 5 | 5 |
| S4: leave one gene out, rise under every drop | 4 (high_2 −0.010 to +0.054) | 5 |

The one unstable cell is the interferon change of high_2 at day 4, which sits near zero because that dog's score had already peaked on
day 1 (S1 at day 3: +0.32, percentile 1.00). Rerun: `out/` deleted and rebuilt; every file byte-identical.

## 6. Confounders

- **Handled.** Library size (within-sample ranks); the composition shift (matched random-set background, S3, the erythroid control);
  post-treatment samples (excluded); the unverified dog mapping (both mappings; same answers).
- **Not handled.** Dose is aliased with dog (2 vs 3). Time since inoculation differs by dose at a matched load. Cell composition beyond
  reticulocytes: a rise in granule transcripts can be a left shift (more immature neutrophils), not a change per cell; the band
  neutrophil check points that way. No uninfected control dogs: day 0 is each dog's own baseline. `low_0` (one D0 sample, maybe the
  donor) is shown only as a reference line.

## 7. What this does not show

- Five dogs from one experiment show a pattern, not a rate. No sign count can reach p < 0.05.
- It does not show that these signatures mark **severe** disease: every dog rose, including the low-dose dogs with mild disease; within
  5 dogs the size of the rise does not separate the dog that died (high_3: interferon +0.39, neutrophil +0.19) from the low-dose dogs
  (+0.31 to +0.42; +0.10 to +0.13). What transfers is the response to infection, not yet a severity gradient.
- The human neutrophil signature does not transfer fully: its promyelocyte genes (MPO, ELANE) and OLFM4, CEACAM8 and ARG1 are not in the
  matrix. The neutrophil result rests on 6 genes.
- No classifier, no genome-wide screen, no top-gene list. Natural infection, other species and clinical cohorts are not covered.

## 8. Verified in files, taken from documentation, or inferred

- **Verified in files.** Every number above, computed by `scripts/analyse.py` from DS06, the SV-G1 DS02 files and `ref/`.
- **Taken from documentation.** Treatment at about day 4 (record; DS06 D4 timing relative to dosing is not stated); dog 6 died on day 4;
  the DS06 mapping status (SV-07); that the human severe-malaria signatures are neutrophil granule and type 1 interferon genes (the
  package file; not re-checked against the human literature here).
- **Inferred.** That MPO, ELANE, OLFM4 and ARG1 are missing because of the CPM filter (their dog genes exist; the filter is in the record);
  that the high-dose interferon peak on day 1 reflects the larger inoculum (dose and dog are aliased).

## 9. Next step and decisions for the user

- No decision is required for this package.
- Possible next step (not done): the raw FASTQ files are in SRA (PRJNA703846). Re-quantifying without the CPM filter would recover MPO
  and ELANE and let the full human neutrophil set be scored. That is a download of a large public data set: a coordinator decision.
- For SV-INT: the interferon response is early (day 1) at the high dose and later at the low dose in these Beagles, and it is mirrored by
  plasma IP-10. A natural-infection cohort with IP-10 or interferon transcripts and an outcome would be needed to test it as a severity
  marker (SV-10 minimum dataset).

## Software

Python 3.12.12 (uv 0.10.4), numpy 2.3.4, scipy 1.16.3; curl for Ensembl REST; .NET console loader (way B); Angular view
`experiment-transcriptome-signature-view.component.*`.
