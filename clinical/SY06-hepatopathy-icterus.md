# SY06: Hepatopathy and icterus

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Icterus beyond what haemolysis explains, raised liver enzymes, cholestasis or hepatic injury in a dog with babesiosis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Icterus and its cause (before, in or after the liver)
- Liver enzyme changes and liver function
- Liver pathology

## Out of scope

- Hypoglycaemia: SY16
- Pancreatitis as the cause of cholestasis: SY12 (link to it)

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How is icterus from haemolysis told apart from liver injury in practice?
2. Which changes of liver enzymes, bile acids and bilirubin are reported, by species?
3. Is icterus or bilirubin a prognostic sign?
4. What did liver histology show?
5. Is there evidence that an antibabesial drug injures the liver?
6. Is there any tested treatment aimed at the liver in babesiosis?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- S-adenosylmethionine
- silymarin
- ursodeoxycholic acid
- N-acetylcysteine and other antioxidants
- vitamin K
- lactulose in encephalopathy
- nutrition

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | hepatopathy (43); icterus (49); other: cholelithiasis (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Icterus (142); Liver diseases (56); Hyperbilirubinemia (46); Liver damage (30); Hepatitis (17); Cholestasis (17) |
| `/core/search/synthesis/` | `MET.md` |

## Search terms to start with

- canine babesiosis icterus liver
- Babesia rossi hepatopathy
- babesiosis dog bile acids
- babesiosis dog liver histopathology
- babesiosis dog hepatoprotective OR antioxidant treatment

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY06.json` | The page file |
| `/clinical/SY06/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
