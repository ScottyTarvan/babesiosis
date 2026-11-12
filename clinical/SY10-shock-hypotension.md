# SY10: Shock and hypotension

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Circulatory collapse and hypotension in a dog with babesiosis, including the peracute form.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Hypotension and its measurement
- Shock: hypovolaemic, distributive, anaemic
- The collapsed dog on arrival
- Lactate as a sign of perfusion

## Out of scope

- Organ failures that follow: the organ pages
- The inflammatory response as a whole: SY11
- Lactate and glucose as metabolic problems: SY16

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How often is hypotension found, at which pressures, and does it follow the severity of disease?
2. What kind of shock is it? What do the sources say about blood volume in babesiosis?
3. How is a fluid bolus given to a dog that is anaemic and at risk of lung oedema? Which end points?
4. When is blood the right fluid?
5. Was any vasopressor or steroid tested in babesiosis?
6. What is the outcome of the collapsed dog?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- isotonic crystalloid bolus
- synthetic colloids
- hypertonic saline
- blood products
- noradrenaline, dopamine, vasopressin
- hydrocortisone
- oxygen

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | shock (6) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Shock (58); Septic Shock (23); Hyperlactatemia (11) |
| `/core/search/synthesis/` | `END.md`, `SEV.md` |

## Search terms to start with

- canine babesiosis hypotension
- Babesia rossi blood pressure
- babesiosis dog shock fluid therapy
- babesiosis dog lactate
- babesiosis dog collapse peracute

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY10.json` | The page file |
| `/clinical/SY10/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
