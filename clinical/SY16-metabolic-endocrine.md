# SY16: Metabolic and endocrine derangements

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Hypoglycaemia, hyperlactataemia, acid-base and electrolyte disturbance, and the adrenal and thyroid changes of critical illness, in a dog with babesiosis.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Hypoglycaemia and hyperglycaemia
- Lactate
- Acid-base and electrolyte disturbances
- Cortisol, thyroid hormones and insulin in acute disease

## Out of scope

- Perfusion and shock: SY10
- The use of these values for triage: SY11 (link to it)

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. How common is hypoglycaemia, at which glucose values, in which dogs (puppies, collapsed dogs), and what is its link with death?
2. How is it treated, and how often does it come back?
3. What do admission lactate and its change after treatment mean?
4. Which acid-base patterns are found? Why is a mixed disturbance common, and when is bicarbonate given?
5. Which electrolyte changes need treatment?
6. What do the studies of cortisol, ACTH and thyroid hormones show? Is there any evidence for treating with steroids or thyroid hormone?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- glucose bolus and infusion
- feeding
- bicarbonate
- potassium supplementation
- fluid choice
- hydrocortisone
- thyroid hormone (and whether it is ever indicated)

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | other: hypoglycaemia (3); other: endocrine (2); other: acidosis (1); other: hyperkalaemia (1); other: euthyroid sick syndrome (1); other: hyperinsulinaemia/hypercortisolaemia (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Hypoglycemia (49); Metabolic acidosis (25); Hyperlactatemia (11); Hyponatremia (12); Hypernatremia (15); Adrenal Gland Hyperfunction (4) |
| `/core/search/synthesis/` | `MET.md` |

## Search terms to start with

- canine babesiosis hypoglycaemia
- Babesia rossi lactate glucose
- babesiosis dog acid-base
- babesiosis dog cortisol
- babesiosis dog thyroid
- babesiosis dog electrolytes

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY16.json` | The page file |
| `/clinical/SY16/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
