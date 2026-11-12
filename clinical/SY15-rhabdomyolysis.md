# SY15: Rhabdomyolysis

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Muscle pain, tremors, raised creatine kinase and myoglobinuria in a dog with babesiosis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Muscle injury in babesiosis
- The distinction of myoglobinuria from haemoglobinuria
- The link to kidney injury

## Out of scope

- Kidney injury itself: SY05
- Tremor from a brain cause: SY07

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. The local data have no tagged treatment paper: how many cases are published, in which species?
2. Which signs and which creatine kinase values were reported?
3. How can muscle pigment be told apart from haemoglobin in a haemolytic dog, in practice?
4. Does it occur with other complications?
5. How was it treated, and what was the outcome?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- intravenous fluids
- analgesia
- urine alkalinisation
- rest and nursing
- correction of potassium and calcium

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | none: no paper is tagged. Search the `syndromes` and `rationale` columns for 'rhabdomyolysis', 'myoglobin', 'muscle' |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Rhabdomyolysis (15); Tremor (13); Pain (17) |
| `/core/search/synthesis/` | `MET.md`, `SEV.md` |

## Search terms to start with

- canine babesiosis rhabdomyolysis
- babesiosis dog creatine kinase myoglobin
- Babesia muscle necrosis dog
- rhabdomyolysis dog treatment

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY15.json` | The page file |
| `/clinical/SY15/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
