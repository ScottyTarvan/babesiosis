# SV-02b spec: reaction norms in the DS02 Beagles

Frozen 2026-11-12, before the analysis script was written and before any habitus value was read. Package file: `/experiments/SV-02-resistance-tolerance.md`, part b. Experiment code `SV-02-02-beagle-reaction-norms`, method `reaction_norm`, role `descriptive`.

## Question and hypothesis

Inside one experiment of 5 Beagles infected with *B. rossi* (2 low dose, 3 high dose), does each dog lose health along the same line of damage against log parasitaemia (one shared reaction norm), or do dogs at a similar load differ in damage (different tolerance)? The package hypothesis is that dogs differ more in damage per parasite (tolerance) than in load (resistance). With 5 dogs this part is descriptive only: no hypothesis test, no p-value.

## Inputs

- `/experiments/shared/tidy/DS02.features.json` (SV-G1; SHA-256 recorded and checked by the script).
- `/experiments/shared/tidy/DS02.outcomes.json`, for `habitus_score` only, opened after this spec is hashed (`exposure.md`). `died` is used only as a label on the plot (dog `DS02:d003` died on day 4; the fact is already in `/experiments/data.md`).
- Linkage: DS03 experimental dogs are these same 5 Beagles and DS06 is their transcriptome (SV-G1, SV-07). Neither is used, and neither would count as an independent replication. Independent sources: 1 (SRC-B).

## Data window

- Dogs: the 5 infected dogs of the tidy file (the donor is already excluded).
- Samples: pre-treatment only (`post_treatment` false) with a parasitaemia value: days 1 to 4 and the extra low-dose sample `day_4_1`. Days −1 and 0 have no parasitaemia; their health values form the dog's own baseline (mean of days −1 and 0 where present; for venous lactate, which starts on day 1, the day-1 value).
- The day-6 parasitaemia of 0 recorded for the dog that died on day 4 is post-treatment and is not used.

## Variables

- Load: `x = log10(parasitaemia_pct + 0.01)`. The offset 0.01 percentage points is about one infected cell in 10,000, close to the smallest non-zero value in the file (0.05). Zeros are kept.
- Health measures (each oriented so that a larger value is worse):
  1. **Haematocrit drop**: baseline haematocrit minus haematocrit (L/L).
  2. **Venous lactate** (blood gas, `lactate`, mmol/L). Low-dose dogs have no blood-gas value on day 4, but have one at `day_4_1`; high-dose dogs have day 4.
  3. **Habitus loss**: 4 minus `habitus_score` (scale 1 to 4, 4 = normal).
  A dog-day with a missing measure is dropped for that measure only.

## Primary analysis (descriptive)

For each dog and each measure:

- **Reaction-norm slope**: ordinary least squares slope of the health measure on `x`, with its 95% t interval (df = points − 2; none if fewer than 3 points), and the Theil-Sen slope beside it.
- **Damage at matched load**: the health measure linearly interpolated (in `x`) at a common load of 1% and of 5% parasitaemia, if the dog's pre-treatment series spans that load; otherwise empty, never extrapolated.
- **Peak**: the highest pre-treatment load and the damage at that sample.

Report the 5 dogs side by side, grouped low dose and high dose, with n points per dog. Also report one pooled descriptive line per measure (OLS over all dog-days, slope only, labelled as ignoring repeated measures) and each dog's mean residual from it.

## Reading rule, fixed now

For each measure:

- **One shared norm (damage follows load)**: every dog's slope has the same sign, and at the matched load of 5% the damage of the low-dose dogs lies inside the range of the high-dose dogs (or within 0.03 L/L haematocrit, 0.5 mmol/L lactate, 1 habitus point of it).
- **Different norms (consistent with tolerance differences)**: at a matched load the low-dose and high-dose ranges do not overlap by more than those margins, or one dog's mean residual from the pooled line is more than twice as large as that of any other dog.
- Otherwise: **cannot tell**.

The result counts against the package hypothesis if all three measures read "one shared norm". It counts for it only weakly, because any difference is confounded with dose and with time since inoculation (a high-dose dog reaches 5% about one day earlier than a low-dose dog) and because treatment at about 96 h (high dose) and 108 h (low dose) cuts the series short.

## Stability and sensitivity

- Offset 0.001 and 0.1 instead of 0.01; positive-load points only (no offset).
- Clinical lactate (`lactate_clinical`) in place of venous lactate. High-dose dogs have no clinical lactate on day 4, so this is a weaker check.
- Haematocrit as the raw value instead of the drop (the slope does not change; the matched-load value does).
- Leave out the dog that died.

## Family and tests

No hypothesis test (n_tests = 0). Intervals are per-dog OLS intervals with 1 or 2 residual degrees of freedom and are expected to be very wide. Seed 20261112 is recorded; nothing is random.

## What this cannot show

- Dose and dog are aliased: two low-dose dogs, three high-dose dogs. A dose effect on the norm cannot be told from a dog effect.
- Measurement error in the smear flattens slopes and can look like tolerance (main risk in the package file).
- Peripheral parasitaemia may understate sequestered parasites.
- Nothing about natural infection or other species.
