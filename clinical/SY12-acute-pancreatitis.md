# SY12: Acute pancreatitis

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Vomiting, abdominal pain and raised pancreatic lipase, or pancreatitis on imaging, in a dog with babesiosis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Pancreatitis as a complication of babesiosis
- Its diagnosis in a dog that is already ill

## Out of scope

- Vomiting and diarrhoea with no pancreatic cause: SY13

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How often is pancreatitis found, by species, and by which test?
2. How reliable are lipase tests and ultrasound in a dog with babesiosis?
3. With which other complications does it occur?
4. Does it change the outcome?
5. Is any treatment tested in babesiosis, or is all guidance from general canine pancreatitis?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- opioid analgesia
- maropitant, ondansetron, metoclopramide
- early enteral feeding and a low-fat diet
- fluids
- fuzapladib
- gastric protection
- antibiotics (and whether they are indicated)

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | pancreatitis (6) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Pancreatitis (41); Abdominal Pain (15); Vomiting (81) |
| `/core/search/synthesis/` | `MET.md` |

## Search terms to start with

- canine babesiosis pancreatitis
- Babesia rossi pancreatitis
- babesiosis dog pancreatic lipase
- acute pancreatitis dog treatment review

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY12.json` | The page file |
| `/clinical/SY12/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
