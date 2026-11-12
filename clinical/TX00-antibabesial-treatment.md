# TX00: Antibabesial treatment and persistence

A page of the clinical manual (cross-cutting section). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

The drugs aimed at the parasite itself, in uncomplicated disease and as the base of treatment in every syndrome; and persistent infection: chronic, relapsing or carrier dogs, and treatment failure.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## Note for this page

This page is a section, not a syndrome. In the page file, use `diagnosis` for the diagnosis of the infection itself (smear, PCR, serology, species identification) and of persistence, and give every antibabesial treatment the class `antibabesial`. Other pages link here and do not repeat these doses, so this page must be complete.

## In scope

- Every antibabesial drug and combination protocol, by *Babesia* species (large: *B. rossi*, *B. canis*, *B. vogeli*; small: *B. gibsoni*, *B. conradae*, *B. vulpes*)
- Dose, route, repeat interval, adverse effects, antidotes and premedication
- Uncomplicated disease: what is treated, and what recovery looks like
- Persistence: relapse, the carrier state, treatment failure, drug resistance, the test of cure
- Treatment of the common co-infections where it changes the antibabesial plan (for example *Ehrlichia canis*)

## Out of scope

- Supportive treatment of a complication: the syndrome pages
- Prevention: tick control and vaccines

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. Which drug is the first choice for each species, and what is the evidence that it clears the parasite or only the clinical signs?
2. What is the safety margin of each drug? Which adverse effects are reported (for example the cholinergic effects of imidocarb, the delayed neurological toxicity of diminazene), at which doses, and how are they prevented or treated?
3. Can a dose be repeated, and after what interval? Can two antibabesial drugs be given together?
4. Which drugs are used in South Africa for *B. rossi* (diminazene, imidocarb, trypan blue), and what do the sources say about each?
5. Which combination protocols exist for *B. gibsoni* and other small *Babesia*, and what are their clearance and relapse rates?
6. What is known about resistance (for example atovaquone and the cytochrome b gene)?
7. When is a PCR test of cure done, and what does a positive result in a healthy dog mean?
8. Which dogs relapse (splenectomy, immunosuppression, co-infection), and how is a relapse treated?
9. Do the dose or the drug change in a puppy, a pregnant bitch, or a dog with kidney or liver failure?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- diminazene aceturate
- imidocarb dipropionate
- trypan blue
- phenamidine and pentamidine
- atovaquone with azithromycin
- atovaquone with proguanil
- buparvaquone
- clindamycin, alone and in combinations (with diminazene and imidocarb; with doxycycline and metronidazole)
- doxycycline, enrofloxacin and metronidazole combinations
- artemisinin derivatives
- atropine or glycopyrrolate before imidocarb

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | uncomplicated (34); chronic/relapsing (34); coinfection (44); the `treatments` column: imidocarb 132, doxycycline 102, diminazene 84, clindamycin 69, azithromycin 54, atovaquone 52 |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Parasitemia; Reinfection; Chronic Infection; Coinfection |
| `/core/search/synthesis/` | `OXO.md`, `SEV.md` |

## Search terms to start with

- canine babesiosis treatment review
- Babesia rossi diminazene imidocarb trypan blue
- Babesia gibsoni atovaquone azithromycin
- Babesia gibsoni clindamycin diminazene imidocarb combination
- diminazene toxicity dog
- imidocarb adverse effects dog
- Babesia gibsoni relapse PCR treatment failure
- Babesia conradae treatment
- Babesia vulpes OR microti-like treatment dog

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/TX00.json` | The page file |
| `/clinical/TX00/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
