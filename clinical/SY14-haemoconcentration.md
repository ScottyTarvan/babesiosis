# SY14: Haemoconcentration ("red biliary")

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

A high or rising haematocrit despite haemolysis, from fluid shift out of the vessels; linked in the literature to cerebral, lung and kidney complications.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Haemoconcentration in babesiosis and its definition
- Its link to other complications and to death
- Fluid treatment

## Out of scope

- Dehydration with a normal response to fluids (name it as a differential)
- The complications themselves: SY05, SY07, SY08

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. Which haematocrit threshold defines it in the literature? The local data have no tagged paper: this page depends on the web search, mainly South African work on *B. rossi*.
2. How common is it, and is it reported outside *B. rossi*?
3. What is the proposed mechanism?
4. How strong is the link with lung oedema, cerebral signs, kidney injury and death?
5. How was it treated, and with what result?
6. How does the clinician recognise it when the haematocrit looks 'normal' in a dog that must be anaemic?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- crystalloid fluids
- colloids
- plasma
- the rate and the end points of fluid therapy
- what to avoid (blood transfusion, fluid overload)

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | none: no paper is tagged. Search the `syndromes` and `rationale` columns for 'haemoconcentration' and 'red biliary' |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | none shown. Search `/core/data/markdown/` and the notes for 'haemoconcentration', 'hemoconcentration', 'red biliary' |
| `/core/search/synthesis/` | `END.md`, `SEV.md` |

## Search terms to start with

- red biliary babesiosis
- haemoconcentration canine babesiosis
- hemoconcentration Babesia rossi
- complicated babesiosis haemoconcentration lung oedema
- Onderstepoort babesiosis haemoconcentration

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY14.json` | The page file |
| `/clinical/SY14/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
