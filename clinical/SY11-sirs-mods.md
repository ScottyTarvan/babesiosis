# SY11: SIRS and multiple organ dysfunction

A page of the clinical manual (umbrella syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

A systemic inflammatory response to the infection with dysfunction of two or more organs; the umbrella for 'complicated' babesiosis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## Note for this page

This is the page that a clinician opens first for a very sick dog. Make `approach` the triage and the order of care, and fill `related` with every organ page. The severity experiments of this project (`/experiments/`) studied markers of severity: you can cite the published articles that they used, not the experiments.

## In scope

- The definitions of uncomplicated and complicated babesiosis, and their history
- The criteria of the systemic inflammatory response and of organ dysfunction as used in dogs with babesiosis
- Triage: which dog on arrival is likely to become complicated or die
- The order of care for a dog with more than one complication
- Treatments aimed at the inflammatory response

## Out of scope

- The treatment of each organ failure: the organ pages (link to each)
- Antibabesial drugs: TX00

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. Which definitions of complicated disease are in use, and how do they differ between *B. rossi* and *B. canis* studies?
2. How often do dogs meet the inflammatory response criteria, and does that predict anything?
3. Which admission findings predict death (for example lactate, glucose, cortisol, band neutrophils, urea, parasitaemia, collapse)? Give thresholds only as the studies give them, and say that none is validated as a rule.
4. Which scoring systems were tried?
5. Was any anti-inflammatory or immunomodulating treatment tested, and with what result?
6. What is the mortality of complicated disease, by species and setting?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- glucocorticoids
- non-steroidal anti-inflammatory drugs
- pentoxifylline
- antioxidants (N-acetylcysteine, vitamins C and E)
- antibiotics for suspected bacterial sepsis
- plasma
- general intensive care bundles from canine sepsis guidelines

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | sirs/mods (28); other: complicated babesiosis (4) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Multiple Organ Failure (70); Systemic Inflammatory Response Syndrome (61); Septicemia (36); Cytokine Storm (12) |
| `/core/search/synthesis/` | `SEV.md`, `INF.md` |

## Search terms to start with

- complicated canine babesiosis definition
- Babesia rossi SIRS MODS
- canine babesiosis prognostic indicators mortality
- Babesia canis complicated uncomplicated
- babesiosis dog outcome score

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY11.json` | The page file |
| `/clinical/SY11/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
