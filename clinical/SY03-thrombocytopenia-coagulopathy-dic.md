# SY03: Thrombocytopenia, coagulopathy and DIC

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

A low platelet count with or without bleeding, through to consumptive coagulopathy (disseminated intravascular coagulation) with prolonged clotting times, thrombosis or haemorrhage.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Thrombocytopenia of babesiosis and its mechanisms
- Bleeding, thrombosis and DIC
- Viscoelastic and clotting tests

## Out of scope

- Evans syndrome: SY02
- Pancytopenia: SY04
- Gut bleeding as a syndrome: SY13

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How often do dogs with severe thrombocytopenia bleed? At which counts?
2. Which criteria for DIC did studies in babesiosis use?
3. Are dogs with babesiosis hypercoagulable or hypocoagulable, by species and by severity?
4. Does the platelet count or a clotting test predict the outcome?
5. How fast does the platelet count recover after antibabesial treatment? What does a count that stays low suggest (co-infection with *Ehrlichia* or *Anaplasma*)?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- fresh frozen plasma
- fresh whole blood or platelet products
- heparin (unfractionated or low molecular weight)
- antiplatelet drugs
- glucocorticoids for immune thrombocytopenia
- tranexamic acid
- vincristine

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | thrombocytopenia (110); dic (16); other: haemorrhagic signs; other: epistaxis and ocular signs |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Thrombocytopenia (212); Disseminated Intravascular Coagulation (38); Blood Coagulation Disorders (43); Hemorrhage (79); Epistaxis (18); Thrombosis (17); Petechiae (12) |
| `/core/search/synthesis/` | `COA.md` |

## Search terms to start with

- canine babesiosis thrombocytopenia bleeding
- babesiosis dog disseminated intravascular coagulation
- Babesia rossi thromboelastography
- Babesia canis haemostasis
- babesiosis dog heparin OR plasma

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY03.json` | The page file |
| `/clinical/SY03/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
