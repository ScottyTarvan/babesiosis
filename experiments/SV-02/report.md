# SV-02 report: resistance or tolerance?

Package file: `/experiments/SV-02-resistance-tolerance.md`. The package has three parts. Each part works in its own sub-folder and writes its own section below.

| Part | Folder | Experiment code | Status |
|---|---|---|---|
| a. Load-by-outcome synthesis (literature) | `a/` | `SV-02-01-load-by-outcome` | Done 2026-11-12 |
| b. Reaction norms in the Beagles (DS02) | `b/` | `SV-02-02-beagle-reaction-norms` | Done 2026-11-12 |
| c. Author data request (user decision) | `c/` (to be created) | `SV-02-03-…` if it records an experiment | Not started |

**Layout for parts b and c.** Each part builds its own `spec.md`, `environment.md`, `run.md`, `env/`, `scripts/` and `out/` inside its sub-folder. The console loader reads load files only from `/experiments/SV-02/out/db/`, so every part writes its `<code>.json` there and touches no other part's file. `exposure.md` (package root) is shared and append-only: add one line per outcomes file opened. Add your section below, after part a, using the same numbered headings.

---

## Part a. Parasite load by outcome, from the published contrasts

Experiment `SV-02-01-load-by-outcome`, method `load_outcome_synthesis`, role primary, run 2026-11-12. No hypothesis test (0 of 0).

### a1. Question and hypothesis

Do dogs with severe babesiosis carry more parasites than dogs with mild disease, inside one *Babesia* species and one outcome class? The package hypothesis is that dogs differ more in damage per parasite (tolerance) than in load (resistance). Part a can only ask whether published load-by-outcome contrasts are large and consistent. It cannot measure tolerance.

### a2. Inputs

| File | SHA-256 |
|---|---|
| `/experiments/SV-G2/associations_v2.csv` | `ac19fa31070dc7c3542d48e1989c153ceb687fa892edac6411e1175fad4ce67d` |
| `/core/articles.jsonl` (streamed, DOIs only) | `47b43087eda734a9a1ddd3f926beb6afcb3bf2b1e91adc4363dad0a45eaf958f` |
| `/core/articles/CB*.md` (keyword screen; per-file hashes of the 17 hits are in `a/out/results.json`) | – |
| `a/curated_note_hits.csv` (my decision on each screen hit) | `d5c5df38d137fe392d9a0b44c88012228b59bec77657d2ab68332496093d26b3` |
| `a/spec.md` | `dad666990e2414cc80f49b554eea932a3b92c512d120789a2b7c61edd6f8f46f` |

No dog-level outcomes file was opened (`exposure.md`). No full text was read or copied. The list statements are my own paraphrases of the appraisal notes and the SV-G2 rows.

### a3. What was done

- **Primary set.** From the 740 SV-G2 rows (42 independent units with severity rows), all 10 parasite-load rows were taken: `Parasitaemia`, plus the ddPCR load of CB141. Of these, 6 rows in 6 units compare load with a severity or outcome definition. The 4 CB105 rows (CH09) compare experimental dose groups, where the dose sets the load by design. They were excluded from the primary set and shown as a sensitivity check.
- **Effects.** Each unit's effect was computed where the paper prints enough numbers:
  - CB516: Hedges g of log load, from the medians and ranges (Hozo mean, Wan SD on the log scale).
  - CB141 and CB045: the correlation with a Fisher-z interval.
  - CB038: an odds ratio for smear positivity.
  - The other units go into a direction table, with the load method and sample timing as moderators.
- **Pooling rule** (spec). Pool only with 3 or more independent units that share the species, outcome class and definition, using REML and a Hartung-Knapp interval.
- **Inverse question.** Rows whose groups are defined by load (CH09, CB187, CB241; 37 rows) went to a separate table, "damage by load group". In that table I labelled each marker change as worse or better. This is my own judgement, recorded in `scripts/build_load.py`.
- **Separate list.** I listed results of the form "severe disease at low load" and "protection at unchanged load":
  - From the SV-G2 rows.
  - From a regex screen of the 444 CB appraisal notes. It matched 17 notes. I read each one and kept 5; the reasons for every decision are in `curated_note_hits.csv`. The script stops if the screen and the curated file get out of step.
- **Deviations from `spec.md`:**
  - None in the analysis.
  - Transparency: the spec was written after the load rows had been listed (not analysed), to set the eligibility rules (`exposure.md`).
  - CB038 gives smear positivity rather than a load. It is kept in the direction table as an odds ratio, which the spec allowed only implicitly ("direction table").

### a4. Results

**Primary: no pooled estimate.** No species × outcome-class cell reached 3 units:

- 6 units fall into 5 cells. The largest cell has 2 units: *B. canis* severity grade, with two different definitions (CB141 haematological score and CB537 clinical form).
- No *B. rossi* unit reports load against a clinical outcome.
- This is a lack of data. It is not evidence for resistance or for tolerance.

| Unit (article) | Species | Outcome | n | Load method / timing | Result |
|---|---|---|---|---|---|
| CH21 (CB516) | *B. canis* | died vs survived (euthanasia included) | 8 vs 7 | smear, site not stated / before treatment | median 1.25% vs 1.2%, p = 1; **g of log load −0.17 (−1.19 to 0.85)**; detectable at 80% power: 1.6 SD |
| CH12 (CB141) | *B. canis* | haematological score (0–11) | 222 | ddPCR / before treatment | rho 0.35 (0.23 to 0.46), significant: the only significant "more load, more severe" result |
| CB537 | *B. canis* | severe/moderately severe vs mild forms | not given | smear / not stated | ranges 23–68% vs 2.5–7%; no n, no test (unreviewed machine translation) |
| CB045 | *B. gibsoni* | pancreatic injury (Spec cPL, continuous) | 20 | smear / before treatment | r 0.09 (−0.37 to 0.51) |
| CB220 | large *Babesia*, unspecified | jaundiced (late) vs anaemic (early) form | 20 | smear / not stated | mean 11.2 vs 13.4% (lower in the more severe form); no test; g −0.39 (−1.27 to 0.49) if an equal split is assumed |
| CB038 | mixed *B. gibsoni*/*B. vogeli* | complicated vs uncomplicated | 17 vs 17 | capillary smear (positivity) / not stated | 7 vs 6 smear-positive; OR 1.28 (0.32 to 5.13) |

Summary of the 6 units:

- 1 is significantly higher in the severe group (a correlation with a score made of blood counts).
- 2 show no difference.
- 1 is lower in the more severe form.
- 2 are descriptive only.

**Antibody against load in the same cohort (CH12).** Antibody level correlates with the haematological score more strongly than load does, and in the opposite direction:

- Antibody: rho −0.65 (−0.73 to −0.56), n 166.
- Load: rho 0.35 (0.23 to 0.46), n 222.

The two intervals do not overlap. But the subsets differ and the correlation between load and antibody is not printed, so this is not a formal comparison.

**Damage by load group (the inverse question).** Where groups were made by load, damage was worse in the high-load group:

- CB241 (*B. canis*, 4 vs 4): 25 of 28 markers were worse in the high-load group. Haematocrit g −3.0 (−5.0 to −1.0); haemoglobin g −3.4. Three liver-enzyme g values above 5 are flagged as implausible: the printed ± is unlikely to be an SEM.
- CB187: haemoglobinuria in 29 of 29 high-load dogs vs 0 of 35 low-load dogs.
- CH09: in 5 experimental Beagles, KC-like, IL-10 and CRP rise with load and neutrophils fall.

So load does carry damage between the extremes of load.

**Separate list (10 items, `a/out/low_load_list.csv`).**

*From the SV-G2 rows:*

- CB516: no load difference by death.
- CB220: lower load in the late, jaundiced form.
- CB045: load unrelated to pancreatitis.
- CB038: detectable load similar across grades.
- CB141: antibody tracks the score more than load.

*From the appraisal notes:*

- [CB375](https://doi.org/10.4102/jsava.v80i2.174) (review of experimental work). Vaccination prevented clinical disease after *B. canis* challenge, with little change in parasitaemia. The timing of parasite control did not track recovery.
- [CB381](https://doi.org/10.1089/vbz.2008.0116) (abstract only, 29 *B. gibsoni* dogs). Severe haemolytic anaemia with very low smear parasitaemia.
- [CB041](https://doi.org/10.3390/pathogens8030094) (review). In *B. canis*, sequestration makes peripheral load understate total load.
- [CB514](https://doi.org/10.1515/bvip-2015-0074) (review). Disease signs at about 1–2% parasitaemia in experimental *B. canis*.
- [CB175](https://doi.org/10.1590/1678-4162-9966) (single fatal case). Low smear parasitaemia.

Most of these items have no comparison group. They show that discordant dogs exist, not how common they are.

### a5. Stability and sensitivity

- CB220, equal split of the 20 dogs: g −0.39 (−1.27 to 0.49), direction unchanged.
- CB105 dose contrast (excluded): the high-dose dogs had median load 11.1% vs 0.08% at 72 h and 45.5% vs 3.9% at 96 h. All 3 high-dose dogs collapsed and no low-dose dog did. Load and dose go together by design, so this says nothing about tolerance between dogs.
- Leave-one-out is not applicable, because there is no pooled cell.
- Rerun: `out/` was deleted and rebuilt from `a/run.md`. All CSV files and `results.json` came back byte-identical. The load file differs only in `run_utc`.

### a6. Confounders

- **Handled.** Species is never pooled. Cohorts are counted once (`independent_unit`). The dose design is excluded. Euthanasia is flagged (CB516: death includes euthanasia).
- **Not handled.**
  - Load method: smear site is often not stated, and capillary load runs higher than venous.
  - One sampling moment per dog. The more severe form in CB220 is also the later one, so stage and severity are mixed (see SV-01).
  - Treatment before sampling is often not stated.
  - The score in CB141 is built from blood counts that load itself can change.

### a7. What this does not show

- It does not show tolerance, and it does not reject resistance.
- Measurement error in a single smear flattens slopes and can imitate tolerance.
- Peripheral load may understate sequestered parasites (*B. canis*).
- Publication bias:
  - Only 6 of 42 units with severity rows report load against outcome.
  - Studies that measured load and found nothing may not have printed it.
  - The large Onderstepoort *B. rossi* cohorts (CB040, CH03) have no load-by-outcome row in the extraction.
- The discordant-case list is not a rate.

### a8. Verified in files, taken from documentation, or inferred

- **Verified in files.** Every number in the tables, computed by `a/scripts/analyse.py` from the SV-G2 rows.
- **Taken from documentation.**
  - The SV-G2 extraction and its judgement calls (CB105, CB098).
  - The appraisal notes behind the five note-derived list items. CB381 is abstract-only.
- **Inferred.**
  - The worse/better labels in the damage table.
  - The log-normal and median/range conversions behind the g values, which assume roughly log-normal load.
  - The equal split for CB220.

### a9. Next step and decisions

- **Part b** (DS02 Beagles, reaction norms) can run now. It depends only on SV-G1, which is done.
- **Part c is a user decision.** Should a request go to the authors of CB141 (342 *B. canis* dogs), CB040 (320 *B. rossi* dogs) and RQ-CB145, asking for dog-level load, antibody status, age and outcome? Part a shows that the published literature cannot answer the load question: no species × outcome cell can be pooled. The CB141 antibody result is the strongest lead to test as a slope modifier.

Versions: Python 3.12.12 (uv 0.10.4), numpy 2.3.4, scipy 1.16.3; console loader `/console/Babesiosis.Console` (.NET 10); Angular build of `/webapp/Babesiosis.Web`.

---

## Part b. Reaction norms in the DS02 Beagles

Experiment `SV-02-02-beagle-reaction-norms`, method `reaction_norm`, role descriptive, run 2026-11-12. No hypothesis test (0 of 0).

### b1. Question and hypothesis

Inside one experiment of 5 Beagles infected with *B. rossi* (2 low dose, 3 high dose), does each dog lose health along one shared line of damage against log parasitaemia (one reaction norm), or do dogs at the same load differ in damage? The package hypothesis is that dogs differ more in damage per parasite (tolerance) than in load (resistance); with 5 dogs part b can only describe it.

### b2. Inputs

| File | SHA-256 |
|---|---|
| `/experiments/shared/tidy/DS02.features.json` (SV-G1) | `12475e823e588af20e8bec2df5164979c158bdbbb86ddfb96a32afe8aad83e2d` |
| `/experiments/shared/tidy/DS02.outcomes.json` (SV-G1; `habitus_score`, and `died` as a label only) | `26831fd671b6168a9228852823d73150cb48896d309f395c9a91858c4506dd67` |
| `b/spec.md` | `0b44ffb3d1dab6e244c2d6f441a6bd747c890010d8d4009e92b6587bb2ac7724` |

Independent sources: 1 (SRC-B). The DS03 experimental dogs and DS06 are the same 5 Beagles (SV-G1; SV-07, "Which files share dogs"), and DS01 repeats DS02. None of them was used, and none would count as a replication. `exposure.md` has the outcomes line.

### b3. What was done

- **Window.** Pre-treatment dog-days with a parasitaemia value: days 1 to 4 and the extra low-dose day-4 sample (`day_4_1`). 22 dog-days in 5 dogs (4 or 5 per dog).
- **Load.** `x = log10(parasitaemia % + 0.01)`; zeros kept.
- **Damage** (larger is worse): haematocrit drop from the dog's own baseline (mean of days −1 and 0), venous blood-gas lactate, and habitus loss (4 minus the daily habitus score; 4 = normal).
- **Per dog and measure:**
  - OLS slope with a 95% t interval (1 or 2 residual df), and the Theil-Sen slope.
  - Damage interpolated at 1% and 5% parasitaemia where the dog's series spans that load (never extrapolated).
  - Peak load and the damage at the peak.
  - One pooled descriptive line per measure (it ignores repeated measures), and each dog's mean residual from it.
- **Reading rule** (fixed in the spec before the habitus values were opened):
  - "One shared norm": every slope has the same sign, and the low-dose damage at 5% lies inside the high-dose range (± margin 0.03 L/L, 0.5 mmol/L, 1 habitus point).
  - "Different norms": the dose groups separate at 1% or 5% by more than the margin, or one dog's mean residual is more than twice that of every other dog.
  - Otherwise "cannot tell".
- **Deviations and clarifications:**
  - D0 (outcome lock). Before `spec.md` was written, a format probe of `DS02.outcomes.json` printed the outcome definitions and the `died` value of 2 dogs (both 0). No habitus value was seen. That dog 6 died on day 4 was already in `data.md`. Recorded in `exposure.md`.
  - C1. The spec does not say which label wins when a "different" criterion and the "shared" criterion both hold. The script gives "different norms" precedence. The case did not arise.
  - C2. The spec's data-window section mentions a day-1 baseline for venous lactate, but its variable list analyses lactate as measured. Lactate was analysed as measured; no lactate baseline was applied.
  - No other deviation.

### b4. Results

**Primary: no measure shows different norms.** Venous lactate reads **one shared norm**, habitus loss **one shared norm**, haematocrit drop **cannot tell**.

| Measure | Low dose at 5% | High dose at 5% | Low dose at 1% | High dose at 1% | Slopes share a sign | Reading |
|---|---|---|---|---|---|---|
| Venous lactate (mmol/L) | 1.14 (n 1) | 1.19 to 1.44 | 0.96 to 1.17 | 1.20 to 1.52 | yes | one shared norm |
| Habitus loss (points) | 1.00 (n 1) | 1.19 to 1.87 | 0.59 to 0.71 | 0.00 to 1.16 | yes | one shared norm |
| Haematocrit drop (L/L) | −0.014 (n 1) | −0.039 to 0.051 | −0.009 to 0.006 | −0.075 to 0.001 | no | cannot tell |

Only one low-dose dog reached 5% (the other peaked at 4.71%).

Per dog (OLS slope per log10 unit with its 95% interval; peak load; damage at the peak):

| Dog | Dose | Lactate slope | Habitus slope | Haematocrit slope | Peak load | Lactate / habitus loss / Hct drop at peak |
|---|---|---|---|---|---|---|
| d001 (dog 3) | low | +0.03 (−0.41 to 0.48) | +0.38 (0.15 to 0.60) | −0.012 (−0.040 to 0.016) | 6.81% (day 4.1) | 1.17 / 1 / −0.03 |
| d005 (dog 2) | low | +0.13 (−0.67 to 0.93) | +0.19 (−0.33 to 0.71) | +0.014 (0.002 to 0.027) | 4.71% (day 4.1) | 1.31 / 0 / 0.01 |
| d002 (dog 5) | high | +1.63 (−2.34 to 5.61) | +0.72 (0.20 to 1.23) | +0.020 (−0.088 to 0.129) | 59.8% (day 4) | 6.56 / 2 / 0.105 |
| d004 (dog 4) | high | +0.60 (−0.97 to 2.17) | +0.77 (0.17 to 1.37) | +0.046 (0.013 to 0.079) | 34.95% (day 4) | 3.05 / 2 / 0.09 |
| d003 (dog 6, died day 4) | high | +1.70 (−3.81 to 7.21) | +1.07 (−0.35 to 2.49) | +0.085 (−0.132 to 0.302) | 45.54% (day 4) | 7.50 / 3 / 0.225 |

- **Where the dose groups overlap** (up to about 7% parasitaemia), the low-dose damage lies inside the margin of the high-dose range. The low-dose values sit at or just below the low end of that range. If that is real, it points to dose or to time since inoculation, not to one dog that tolerates more.
- **The groups differ in how far load rose before treatment:** peaks of 4.7% and 6.8% (low dose) against 35% to 60% (high dose). Clear damage (lactate above 3 mmol/L, habitus loss of 2 or more, a haematocrit drop near 0.1 L/L) appears only above about 10% parasitaemia, and only the high-dose dogs got there.
- **Haematocrit cannot be read** because d001 has a slightly negative slope: the low-dose haematocrit did not fall before treatment.
- **The dog that died** (d003) had the most damage at its peak load of 45.5%: haematocrit drop 0.225 L/L, lactate 7.5 mmol/L, habitus loss 3. The two other high-dose dogs, at peaks of 35% and 60%, had 0.09 to 0.105 L/L, 3.05 to 6.56 mmol/L and a habitus loss of 2. This hints at less tolerance at high load in that dog. But its mean residual from the pooled line was not twice that of every other dog (for lactate the largest absolute residual was d004's, −0.56), so the rule does not call it a different norm. It is one dog on one day.
- **Against the hypothesis?** The spec counts the result against the package hypothesis only if all three measures read "one shared norm". Two do and one cannot be read, so the rule is not met. No measure supports tolerance differences either.
- **Negative result:** in these 5 Beagles, damage followed load. There is no sign that dogs differed in damage per parasite at the loads where they can be compared.

### b5. Stability and sensitivity

13 of 14 checks give the primary reading (`b/out/sensitivity.csv`):

- Offsets of 0.001 and 0.1, and positive loads only (no offset): readings unchanged for all three measures.
- Raw haematocrit instead of the drop: cannot tell (unchanged).
- Without the dog that died: readings unchanged.
- Clinical (hand-held) lactate instead of blood-gas lactate: **cannot tell** instead of one shared norm. The high-dose dogs have no clinical lactate on day 4, so this check has no high-load points.
- Rerun: `b/out/` was deleted and rebuilt from `b/run.md`. Every file came back byte-identical; the load file differs only in `run_utc`.

### b6. Confounders

- **Handled.** One species, one experiment, one source. Post-treatment samples excluded. The donor dog was already excluded by SV-G1. Each dog is its own baseline for haematocrit.
- **Not handled.**
  - Dose and dog are aliased (2 low, 3 high): a dose effect on the norm cannot be told from a dog effect.
  - Time since inoculation: at a matched load, a high-dose dog is about one day earlier than a low-dose dog.
  - Treatment at about 96 h (high dose) and 108 h (low dose) cuts the low-dose series at 5% to 7%, so the norms overlap only at low loads.
  - Load is one peripheral smear per day. Sequestered parasites are not counted.

### b7. What this does not show

- It cannot estimate how much dogs vary in tolerance: 5 dogs, per-dog intervals with 1 or 2 df, no test.
- Error in measured load flattens slopes and can imitate tolerance (the main risk of the package). Here that error would push toward "different norms", which was not seen.
- Damage is not linear in log load: it is flat, then rises above about 10%. The slopes are rough summaries; the matched-load values carry the reading.
- It says nothing about natural infection, other species, or severity classes in clinical cohorts. DS03 and DS06 hold the same dogs and cannot replicate it.

### b8. Verified in files, taken from documentation, or inferred

- **Verified in files.** Every number above, computed by `b/scripts/analyse.py` from the SV-G1 tidy files.
- **Taken from documentation.** Treatment times, dose levels and the day-4 death of dog 6 (SV-G1 cleaning notes, `data.md`, CB101). The habitus scale (4 = normal; DS01 supplementary table, through SV-G1).
- **Inferred.** That day 4 and `day_4_1` are pre-treatment (SV-G1). The 0.01 offset as a detection floor. The reading margins (set in the spec, not derived from assay error).

### b9. Next step and decisions

- Part b leaves no decision for the user.
- The only route to a real tolerance estimate is still dog-level load and outcome data from a natural-infection cohort (part c, a user decision).
- SV-08 (Beagle transcriptome) could check whether d003 differs in expression at a matched load. But only one DS06 sample name is mapped (high_3 = dog 6; SV-07).

Versions: Python 3.12.12 (uv 0.10.4), numpy 2.3.4, scipy 1.16.3; console loader `/console/Babesiosis.Console` (.NET 10); Angular build of `/webapp/Babesiosis.Web`.
