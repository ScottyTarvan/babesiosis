# SY13: Haemorrhagic gastroenteritis and gut signs

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Haemorrhagic diarrhoea, melaena or severe vomiting in a dog with babesiosis, not explained by pancreatitis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Vomiting, diarrhoea, melaena and haematochezia in babesiosis
- Whether a distinct gut syndrome exists

## Out of scope

- Pancreatitis: SY12
- Bleeding from coagulopathy: SY03 (name it as a differential)
- Uraemic gastritis: SY05

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. First: is this a distinct syndrome in the literature? The local evidence is thin (one treatment paper). Report what you find, even if the answer is no.
2. How often are gut signs reported, by species?
3. What is the cause where one was found: ischaemia, coagulopathy, uraemia, pancreatitis, a drug effect (for example the cholinergic effect of imidocarb), a co-infection?
4. How is it told apart from parvovirus enteritis in a young South African dog, and can the two occur together?
5. Is any treatment tested in babesiosis?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- fluid and electrolyte replacement
- antiemetics
- omeprazole or other acid suppressants
- sucralfate
- antibiotics (and whether they are indicated)
- enteral nutrition
- plasma or blood for losses

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | other: gastroenteritis (1); other: fever, epistaxis, melaena (1); other: fever, lethargy, vomiting (1); other: fever, lethargy, leukopenia, diarrhoea (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Vomiting (81); Diarrhea (50); Melena (13); Gastroenteritis (3); Hematochezia (2) |
| `/core/search/synthesis/` | `MET.md`, `SEV.md` |

## Search terms to start with

- canine babesiosis haemorrhagic gastroenteritis
- babesiosis dog melaena OR haematochezia
- babesiosis dog vomiting diarrhoea
- Babesia gastrointestinal dog
- babesiosis parvovirus co-infection dog

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY13.json` | The page file |
| `/clinical/SY13/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
