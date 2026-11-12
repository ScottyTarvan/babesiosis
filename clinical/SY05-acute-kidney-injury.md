# SY05: Acute kidney injury

A page of the clinical manual (syndrome). One agent, one child session.

**Read first:** [rules.md](rules.md) and [content-format.md](content-format.md). The list of all pages is in [index.md](index.md).

## Working definition

Azotaemia that persists after rehydration, oliguria or anuria, and haemoglobinuric nephropathy; includes glomerulonephritis and protein-losing nephropathy after infection.

This definition was not checked against the papers. Confirm it or correct it from the literature, and record the change in `definition_note`.

## In scope

- Acute kidney injury in acute babesiosis
- Early markers of kidney injury
- Fluid balance in the oliguric dog
- Glomerular disease and chronic kidney disease after babesiosis

## Out of scope

- Rhabdomyolysis as the cause of pigment: SY15
- Lung oedema from fluid overload: SY08 (link to it)

## Questions for this page

Answer the eight questions of [rules.md](rules.md) ("What every page answers"), and these:

1. Which criteria did studies in babesiosis use (creatinine, urine output, the IRIS grading of acute kidney injury)? Why can urea mislead in a haemolytic dog?
2. Which early markers were tested in babesiosis (urinary proteins and enzymes, SDMA, NGAL, cystatin C), and are they of use in practice?
3. What is the cause: haemoglobin, hypoxia, hypotension, immune complexes? Does it change the treatment?
4. How is fluid therapy given and limited? Which signs show overload?
5. Which dogs need referral for dialysis, and what was the outcome?
6. Does the dose of an antibabesial drug change in kidney failure?
7. How often does kidney disease persist?

## Treatments to check

These are candidates from the local data and from general practice. A name in this list is not evidence, and the list is not complete. For each one, find the evidence for it, against it, or report that there is none. Add every other treatment that you find.

- intravenous fluids, with the rate and the end points
- furosemide
- mannitol
- dopamine or fenoldopam
- haemodialysis and peritoneal dialysis
- urine alkalinisation
- antiemetics and gastric protection in uraemia
- renoprotective diet and ACE inhibitors for proteinuria

Antibabesial drugs are in TX00: link to it, and give here only what is specific to this syndrome (for example a dose change, or a drug to avoid).

## Local starting points

Counts are from 2026-11-12. The labels are automatic (rule 11).

| Source | Look for |
|---|---|
| `/core/search/clinical_treatment/combined_set.csv`, column `syndromes` | aki (56); other: protein-losing nephropathy (2); other: proteinuria (2); other: glomerulonephritis (1); other: azotaemia (2); other: fanconi syndrome (1) |
| `/core/data/terms/term_display.csv`, column `concept` (CB articles) | Kidney Failure (53); Azotemia (62); Injury of kidney (20); Glomerulonephritis (23); Oliguria (15); Acute Kidney Tubular Necrosis (12); Chronic Kidney Diseases (12) |
| `/core/search/synthesis/` | `REN.md` |

## Search terms to start with

- canine babesiosis acute kidney injury
- Babesia rossi renal
- Babesia canis acute renal failure haemodialysis
- babesiosis dog urinary biomarkers
- IRIS grading acute kidney injury dog
- babesiosis dog glomerulonephritis proteinuria

Add the species names, the candidate treatments and the terms that the first papers use.

## Output

| File | Content |
|---|---|
| `/webapp/Babesiosis.Web/public/assets/clinical/SY05.json` | The page file |
| `/clinical/SY05/search-log.md`, `evidence.csv`, `references-check.csv`, `report.md` | The working files ([rules.md](rules.md), steps 2 to 6) |
| `/clinical/ledger.md` | Your row |
