# SY02: Secondary immune-mediated haemolytic anaemia

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Antibody-mediated red cell destruction (persistent agglutination, spherocytes, a positive Coombs test) that goes on despite antibabesial treatment; includes Evans syndrome (with immune thrombocytopenia).

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Immune-mediated haemolysis triggered by *Babesia*
- The distinction from primary immune-mediated haemolytic anaemia and from haemolysis by the parasite
- Immunosuppression in an infected dog

## Out of scope

- Haemolysis that stops with antibabesial treatment: SY01
- Thrombocytopenia alone: SY03

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How often are the Coombs test, saline agglutination and spherocytes positive in babesiosis, by species? Does a positive test alone change the treatment?
2. Which criteria did studies use to start immunosuppression? When, in relation to the antibabesial drug?
3. What is the evidence that immunosuppression helps, and the evidence that it harms (relapse, failure to clear the parasite, carrier state)?
4. How do the general canine consensus statements on immune-mediated haemolytic anaemia treat infection-triggered disease?
5. How long is treatment continued, and how is it withdrawn?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- prednisolone or other glucocorticoids
- azathioprine, ciclosporin, mycophenolate
- human intravenous immunoglobulin
- transfusion
- antithrombotic drugs
- splenectomy

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | imha (26); other: evans syndrome (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Autoimmune hemolytic anemia (33); Erythrophagocytosis (19) |
| `/core/search/synthesis/` | `ERY.md`, `INF.md` |

## Search terms to start with

- babesiosis dog immune-mediated haemolytic anaemia
- Babesia Coombs positive dog
- babesiosis dog prednisolone immunosuppression
- Babesia gibsoni IMHA glucocorticoid
- ACVIM consensus immune-mediated hemolytic anemia treatment

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY02.json` | The page file |
| `/clinical/SY02/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
