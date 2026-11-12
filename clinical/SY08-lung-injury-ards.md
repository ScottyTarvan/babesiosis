# SY08: Acute lung injury, ARDS and pulmonary oedema

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Non-cardiogenic pulmonary oedema with dyspnoea and hypoxaemia, often with frothy nasal discharge, in a dog with babesiosis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Acute lung injury and acute respiratory distress syndrome
- Pulmonary oedema, including oedema after fluid therapy
- Blood gas findings of lung failure

## Out of scope

- Fast breathing from anaemia, acidosis, pain or fever with normal lungs (name these as differentials)
- Heart failure: SY09

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. Which criteria did studies in babesiosis use? How do the veterinary consensus definitions of acute lung injury and ARDS apply?
2. How is it told apart from fluid overload, cardiogenic oedema, transfusion-related lung injury and aspiration?
3. Which dogs are at risk (species, haemoconcentration, kidney injury, fluid volume)?
4. What can a practice without blood gas analysis use (pulse oximetry, radiographs, lung ultrasound)?
5. What is the mortality? Did any dog survive with or without ventilation?
6. How must fluids and transfusions be given to a dog at risk?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- oxygen (cage, nasal, high flow)
- mechanical ventilation
- furosemide
- fluid restriction
- colloids or plasma
- glucocorticoids
- bronchodilators
- sedation of the distressed dog

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | ards (14); other: pulmonary oedema (2); other: non-cardiogenic pulmonary oedema (1); other: respiratory distress (2); other: haemoptysis (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Pulmonary Edema (26); Dyspnea (30); Respiratory distress (14); Acute Lung Injury (6) |
| `/core/search/synthesis/` | `PUL.md` |

## Search terms to start with

- canine babesiosis acute respiratory distress syndrome
- babesiosis dog pulmonary oedema
- Babesia rossi lung
- Babesia canis ARDS
- veterinary ALI ARDS consensus definition
- babesiosis dog blood gas

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY08.json` | The page file |
| `/clinical/SY08/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
