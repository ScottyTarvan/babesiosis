# SY07: Cerebral babesiosis

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Neurological signs of acute onset (seizures, coma, ataxia, paresis, behaviour change) caused by the infection, not by hypoglycaemia or another cause.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Central nervous signs in acute babesiosis
- Brain pathology
- The causes that must be ruled out first

## Out of scope

- Hypoglycaemia as the cause of the signs: SY16 (but name it as the first thing to rule out)
- Muscle tremor and pain from rhabdomyolysis: SY15

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. Which signs are reported, how often, and in which species?
2. What is the first thing to measure in a babesiosis dog with seizures or coma (glucose)?
3. How is cerebral babesiosis told apart from delayed diminazene toxicity, hepatic or uraemic encephalopathy, and the other causes of seizures in South African dogs (distemper, rabies)?
4. What did pathology and imaging show (haemorrhage, malacia, sludging of red cells)?
5. What is the mortality, and do survivors recover fully?
6. Is any treatment beyond antibabesial and supportive care supported by evidence?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- diazepam or midazolam
- phenobarbital
- levetiracetam
- mannitol
- hypertonic saline
- glucocorticoids
- glucose
- oxygen and nursing care of the recumbent dog

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | cerebral (18); other: cerebral signs (1); other: paraplegia (2) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Seizures (37); Ataxia (19); Comatose (15); Tremor (13); Cerebral Edema (2) |
| `/core/search/synthesis/` | `NEU.md` |

## Search terms to start with

- cerebral babesiosis dog
- Babesia rossi neurological
- babesiosis dog seizures
- canine babesiosis brain pathology
- diminazene neurotoxicity dog
- status epilepticus dog consensus treatment

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY07.json` | The page file |
| `/clinical/SY07/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
