# SY01: Severe haemolytic anaemia

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Life-threatening anaemia from intravascular and extravascular haemolysis, with haemoglobinaemia or haemoglobinuria; usually a haematocrit below about 0.15 L/L (15%).

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Anaemia from haemolysis caused by the infection
- The decision to transfuse, the product, the volume and the rate
- Haemoglobinuria as a sign

## Out of scope

- Immune-mediated haemolysis that continues after antibabesial treatment: SY02
- Non-regenerative anaemia and pancytopenia: SY04
- A high haematocrit with haemolysis: SY14
- Kidney injury from haemoglobin: SY05

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. Which haematocrit thresholds and which clinical signs did studies use as the transfusion trigger?
2. Is a grading of anaemia (mild, moderate, severe) in use in babesiosis, and with which limits?
3. Does the degree of anaemia follow the parasitaemia? Does severe anaemia alone change the outcome?
4. What do the sources say about blood typing (DEA 1), cross-matching and transfusion reactions in these dogs?
5. How fast does the haematocrit recover after antibabesial treatment, with and without transfusion?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- packed red cells
- fresh whole blood
- haemoglobin-based oxygen carriers
- oxygen
- fluid therapy in the anaemic dog (and its risks)
- iron, vitamin B12 or haematinics

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | haemolytic anaemia (215) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Anemia (267); Hemoglobinemia (16); Hematuria (27); Erythrocyte destruction (14) |
| `/core/search/synthesis/` | `ERY.md` |

## Search terms to start with

- canine babesiosis anaemia blood transfusion
- Babesia rossi transfusion haematocrit
- babesiosis dog packed red cells outcome
- haemoglobin-based oxygen carrier babesiosis dog
- small animal transfusion guidelines

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY01.json` | The page file |
| `/clinical/SY01/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
