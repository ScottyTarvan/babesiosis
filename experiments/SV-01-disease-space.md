# SV-01. Stage or trait? Disease-space maps of natural *B. rossi* infection

| | |
|---|---|
| Wave | 1 |
| Lane | Within-dataset statistics |
| Effort | Medium |
| Working folder | `/experiments/SV-01/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): `DS02`, `DS03`, `DS05`.

- **Hypothesis.** Part of the variation in admission severity is the stage a dog has reached on a common course. Dogs that are clinically worst lie off that course, not only later on it.
- **Background.** Hosts can be mapped through "disease space"; non-resilient hosts trace larger loops in red cell by reticulocyte space ([10.1371/journal.pbio.1002436](https://doi.org/10.1371/journal.pbio.1002436)). The regenerative response in *B. rossi* is weak and the reticulocyte count falls about 48 h after parasitaemia appears ([10.1111/vcp.13228](https://doi.org/10.1111/vcp.13228)).
- **Depends on.** SV-G1. **Parallel with:** all of wave 1.
- **Inputs.** Tidy DS02 (daily haematocrit, reticulocytes, band neutrophils, parasitaemia), DS03 experimental, DS05, DS03 natural.
- **Steps.**
  1. Build the reference course from the Beagles in the plane haematocrit by log ARC, using samples before treatment. Parameterise it by position along the curve (pseudo-stage). Draw the post-treatment arm separately.
  2. Project each natural dog onto the curve: record pseudo-stage and distance from the curve in units of the between-Beagle spread.
  3. Repeat in the plane band neutrophils by haematocrit (DS05 and DS02 only).
- **Primary analysis.** In DS05: the association of habitus grade with distance from the curve, among dogs compared at similar pseudo-stage (partial Spearman correlation controlling pseudo-stage; permutation p).
- **Validity check, stated in advance.** Pseudo-stage should rise with owner-reported illness duration in DS05. If it does not, say that the stage score is not validated and report the rest as descriptive.
- **Replication.** DS03 natural dogs have no habitus score. Replicate the geometry only: the share of dogs within the Beagle band, and the distribution of pseudo-stage. Report the two DS03 cohorts separately.
- **Confounders.** One species and one country. Clinic against referral hospital is the replication contrast. Prior treatment is unknown. The Beagle course follows intravenous inoculation and may be faster than tick-borne disease. DS03 "Day 1" is not anchored.
- **Stability.** Refit the curve leaving each Beagle out (5 fits) and report how pseudo-stage changes. Bootstrap the natural dogs.
- **Outputs.** `out/pseudo_stage.csv` (`dog_id, dataset_id, pseudo_stage, distance, plane`), which SV-05 and SV-09 read; map coordinates as CSV; `report.md`.
- **Main risk.** A cross-section cannot separate stage from course. The haematocrit to reticulocyte correlation alone can look like a curve. Five Beagles define the reference.
- **Do not.** Use habitus to build the curve. Call off-curve dogs a subtype.
