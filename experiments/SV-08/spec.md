# SV-08 spec: human severity signatures in the Beagle transcriptome

Frozen 2026-11-12, before `shared/tidy/DS02.outcomes.json` values were opened. Written from the DS06 count matrix, the DS02
features file, the package file and the SV-07 and SV-02b reports. Package file: `/experiments/SV-08-transcriptome-signatures.md`.

## Question and hypothesis

Do the whole-blood signatures of severe human malaria (neutrophil granule, type 1 interferon) rise in the *B. rossi* Beagles
between day 0 and the last pre-treatment sample, before clinical deterioration, and earlier at the high dose? Hypothesis: both
scores rise in most dogs beyond what the composition shift of the day 3 and day 4 libraries explains, and rise first in the
high-dose dogs.

## Data

- DS06 (`/core/data/raw/DS06/GSE167201_raw_counts.txt.gz`): 12,362 genes x 28 samples, names `<dose>_<dog>_D<day>`. Five dogs with a
  time course: `low_1`, `low_2`, `high_1`, `high_2` (D0, D1, D3, D4, D6, D8) and `high_3` (D0, D1, D3). `low_0` (D0 only) is shown
  as a reference sample, never as a dog.
- DS02 features (`shared/tidy/DS02.features.json`): parasitaemia, reticulocyte %, band neutrophils and plasma IP-10 by dog and day.
- DS02 outcomes (`shared/tidy/DS02.outcomes.json`): `habitus_score` (4 = normal) by dog and day, for the timing of clinical
  deterioration. Opened only after this spec is hashed (`exposure.md`). `died` is a label, not analysed.
- DS06 to DS02 dog mapping (SV-07 4.4): `high_3` = dog 6 = `DS02:d003` (probable). Working mapping for the others (SV-07's best
  value assignment, unverified): `high_1` = dog 4 = `DS02:d004`, `high_2` = dog 5 = `DS02:d002`, `low_1` = dog 2 = `DS02:d005`,
  `low_2` = dog 3 = `DS02:d001`. The alternative mapping swaps the two dogs inside each dose group. Every result that joins DS06
  to DS02 is given under both mappings.

## Gene mapping

The three sets are fixed by the package file (`scripts/gene_sets.json`). A human symbol maps to a DS06 row when (1) the row's
symbol is the same, or (2) the dog Ensembl gene ID that Ensembl REST returns for the symbol (dog Boxer / CanFam3.1-lineage
annotation) is a DS06 row, or (3) a DS06 row without a symbol has that symbol as its current Ensembl display name or names the
protein in its description. Every set gene that does not map is written to `out/unmapped_genes.csv` with the reason (no dog
gene found; dog gene found but not in the pre-filtered matrix). A set is scored with its mapped genes only.

## Score

Inside each sample, rank all 12,362 genes by count (ties averaged) and convert to a percentile `(rank - 1) / (N - 1)`. The set
score is the mean percentile of its mapped genes. The ranks are free of library size; they are not free of composition, which
is why the erythroid control set is reported beside the others.

## Primary analysis

For each of the 5 dogs and each set: delta = score at the last pre-treatment sample minus score at D0. The last pre-treatment
sample is D4 for `low_1`, `low_2`, `high_1`, `high_2` and D3 for `high_3`. D6 and D8 follow treatment and are shown, never
analysed. Report the 5 deltas one by one, and per set a sign count (dogs with delta > 0) with the exact two-sided sign-test p.
With 5 dogs the smallest attainable p is 0.0625: no set can reach 0.05. No other test across dogs. Family: 2 sets (neutrophil
granule, type 1 interferon); the erythroid control is reported, not counted.

**Composition background (per dog, per set).** 2,000 random gene sets of the same size, each random gene drawn from the genes in
the same D0 percentile decile (of that dog's D0 sample) as the set gene it replaces, set genes excluded. The background
percentile of the set's delta among the random deltas says whether the set moved beyond the whole-library shift. "Beyond
background" means a percentile >= 0.975 (rise) or <= 0.025 (fall). Seed 20261112.

## Timing

- Score against day and against parasitaemia (DS02, matched by dog and day under each mapping) for each dog, D0 to D8.
- First risen day: the first sampled day after D0 at which a set's delta is beyond background (>= 0.975).
- Deterioration day: the first day on which `habitus_score` is below the dog's own day -1 and day 0 values (habitus loss of 1 or
  more). DS06 samples only D0, D1, D3, D4, so a score can "precede" deterioration only at a sampled day earlier than it.
- "Earlier at the high dose": the first risen day of every high-dose dog is earlier than that of both low-dose dogs.

## Construct checks (descriptive, no test)

Within each dog over its pre-treatment samples (3 or 4 points), Spearman rho of: the interferon score with plasma IP-10 (the
CXCL10 protein); the neutrophil-granule score with band neutrophils; the erythroid score with reticulocyte %. Under both
mappings. Pooled across dogs only as a median of the per-dog rho.

## Sensitivity

- S1. Last pre-treatment sample = D3 for every dog (the D4 libraries collapse and the D4 sampling time relative to treatment is
  not stated).
- S2. Mean log2(CPM + 1) of the set genes instead of the rank score (upper-quartile scaled library size).
- S3. Ranks computed after removing the genes whose percentile across the 28 samples correlates with the ALAS2 percentile at
  Spearman rho >= 0.8 (the reticulocyte-shift genes).
- S4. Leave one set gene out: the range of the delta.

## What would count against the hypothesis

- The neutrophil-granule or the interferon delta is positive in 2 or fewer of the 5 dogs, or beyond background (>= 0.975) in 2
  or fewer: against "the signature appears" for that set.
- No dog has a first risen day earlier than its deterioration day: against "before clinical deterioration".
- Not every high-dose dog rises before both low-dose dogs: against "earlier at the high dose".

## Limits fixed now

Five dogs, one source (SRC-B). Dose is aliased with dog. A pattern, never a rate. No classifier, no genome-wide screen, no top-gene
list. DS02 and DS03 experimental dogs are the same Beagles and cannot replicate anything here.
