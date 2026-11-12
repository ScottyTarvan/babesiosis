# SY09: Cardiac dysfunction

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Myocardial injury, myocarditis, arrhythmia or heart failure in a dog with babesiosis, shown by ECG changes, cardiac troponin, echocardiography or pathology.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Myocardial injury and its markers
- Arrhythmias
- Heart failure and pericardial effusion

## Out of scope

- Hypotension and shock from other causes: SY10
- Non-cardiogenic lung oedema: SY08

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How often are troponin, ECG and echocardiographic changes found, by species, and do they matter clinically?
2. Which arrhythmias are reported, and which needed treatment?
3. Does a cardiac marker predict the outcome?
4. What did pathology show?
5. How does cardiac involvement change fluid and transfusion rates?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- lidocaine and other antiarrhythmic drugs
- pimobendan
- dobutamine
- furosemide
- oxygen
- limits on fluid rate
- correction of potassium and magnesium

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | cardiac (6); other: heart and respiratory failure (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Heart Diseases (17); Myocarditis (10); Myocardial dysfunction (10); myocardial injury (9); Cardiac Arrhythmia (8) |
| `/core/search/synthesis/` | `CAR.md` |

## Search terms to start with

- canine babesiosis cardiac troponin
- babesiosis dog myocarditis
- Babesia rossi heart ECG
- babesiosis dog echocardiography
- babesiosis dog arrhythmia

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY09.json` | The page file |
| `/clinical/SY09/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
