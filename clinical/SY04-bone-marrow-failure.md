# SY04: Bone marrow failure

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Non-regenerative anaemia, pancytopenia or haemophagocytic syndrome in a dog with babesiosis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Anaemia with no adequate reticulocyte response
- Pancytopenia and bicytopenia
- Haemophagocytic syndrome
- Bone marrow findings

## Out of scope

- Regenerative haemolytic anaemia: SY01
- Leukopenia or thrombocytopenia alone in acute disease: SY03 and SY11

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How common is each form, by species and by acute or chronic infection?
2. How much of it is explained by co-infection (*Ehrlichia canis*, *Leishmania*) or by drugs?
3. When is the regenerative response expected, so that 'non-regenerative' is not called too early?
4. What did bone marrow samples show?
5. Does it resolve with antibabesial treatment alone?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- antibabesial treatment alone
- treatment of the co-infection (doxycycline)
- transfusion
- immunosuppression
- erythropoietin or darbepoetin
- granulocyte colony-stimulating factor
- antibiotic cover in neutropenia

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | non-regenerative anaemia (13); pancytopenia (11); other: haemophagocytic syndrome (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Pancytopenia (24); Normocytic normochromic anemia (25); Erythrophagocytosis (19); Leukopenia (87) |
| `/core/search/synthesis/` | `ERY.md` |

## Search terms to start with

- babesiosis dog pancytopenia
- Babesia non-regenerative anaemia dog
- babesiosis dog bone marrow
- haemophagocytic syndrome Babesia dog
- Babesia gibsoni chronic anaemia

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY04.json` | The page file |
| `/clinical/SY04/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
