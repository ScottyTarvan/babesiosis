# SY01 report: severe haemolytic anaemia

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY01.json` (built by [build_sy01.py](build_sy01.py)). Validator: `OK`, with 2 warnings (explained below). Page not seen: the user declined to start the preview server.

## Definition

The working definition was confirmed, with two changes:
- The published limit for severe anaemia is a haematocrit **below 0.15 L/L**, not "about" 0.15 (Leisewitz 2019, 320 *B. rossi* dogs). The same study grades moderate anaemia as 0.15 to 0.24 L/L and mild as 0.25 to 0.36 L/L. Reyers 1998 is said to use 0.15 to 0.29 L/L for moderate, but I saw that only in a later paper that cites it, so it is not on the page.
- Haemoglobinuria is common (84%) but is not part of any published definition. Jacobson (2006) calls the old split into "severe" and "complicated" disease artificial.

## References: 23, by evidence level

| Level | References |
|---|---|
| A (trial in babesiosis) | 1: Zambelli 2009 (packed cells vs Oxyglobin, 12 *B. rossi* dogs) |
| B (cohort or series of 5 or more dogs with babesiosis) | 10: Leisewitz 2019, Reyers 1998, Scheepers 2011, Nel 2004, Keller 2004, Böhm 2006, Piane 2016, Mathews 2026, Adebayo 2025, Abakpa 2023; plus Bumby 2024 (6 fatal dogs, no outcome comparison) |
| C (case reports) | 2: DeStefano 2022, Halder 2022 |
| D (other causes, or a model) | 2: Herter 2022 (cross-match study), Klein 2017 (iron in a canine infection model) |
| E (review, survey, textbook) | 7: Leisewitz 2023, Jacobson 2006, Jacobson & Swan 1995, Köster 2015, Karasová 2022, Collett 2000 (practice survey), Merck Veterinary Manual (Blois) |

All 23 were confirmed by PMID or DOI in PubMed, Europe PMC or Crossref, or on the publisher's page (Merck), with matching title, first author and year (`references-check.csv`). Eleven were read as abstract only.

## Treatments: 7

| Treatment | Status | Level | Studies |
|---|---|---|---|
| Packed red cell transfusion | standard | A | 2 |
| Fresh whole blood transfusion | standard | B | 1 |
| Blood typing, cross-matching and donor screening | standard | D | 1 |
| Haemoglobin-based oxygen carrier (Oxyglobin) | proposed | A | 1 |
| Oxygen supplementation | proposed | E | 0 |
| Intravenous crystalloid fluids | proposed | E | 0 |
| Haematinics (iron, vitamin B complex) | proposed | C | 1 |

Dose rows (5): packed cells 20 mL/kg IV over 4 h (Zambelli 2009); the Onderstepoort volume formula BW × 90 × (25 − PCV) ÷ donor PCV, used for packed cells and whole blood (Scheepers 2011, full text); the general formula with a blood volume of 80 to 90 mL/kg (Merck); Oxyglobin 20 mL/kg IV over 4 h (Zambelli 2009). I re-read every dose and threshold against its source in this run. No sub-agent check was done.

**Validator warnings.** Both are "no per-kg unit" warnings on the Onderstepoort formula. The formula is the dose exactly as the source states it, so I did not rewrite it as mL/kg.

## Answers to the page's questions

1. **Transfusion trigger.** Onderstepoort used a PCV below 15% as a guideline, together with the clinical state (collapse). A *B. gibsoni* review adds severe dyspnoea or tachypnoea. No study tested a trigger.
2. **Grading.** Severe below 0.15 L/L, moderate 0.15 to 0.24 L/L, mild 0.25 to 0.36 L/L (Leisewitz 2019).
3. **Parasitaemia and outcome.** I found no source that ties the degree of anaemia to parasitaemia in *B. rossi*, so the page makes no claim. High parasitaemia was associated with death (Böhm 2006). Severe anaemia alone predicted death poorly: mortality was 14.2%, against 8 to 11% with milder anaemia.
4. **DEA 1, cross-matching and reactions.** There is no babesiosis-specific data on reactions. In a 1993 South African survey, most practices never cross-matched and reactions were said to be rare. DEA 1 type did not affect the rate of infection (Nigeria). First donor–recipient pairs were all compatible (India, *B. gibsoni*). General guidance (Merck, Herter 2022) is on the page.
5. **Haematocrit recovery.** The haematocrit fell on day 1 after diminazene. Medians on day 6 were 0.36 L/L (not transfused) and 0.31 L/L (transfused), still low. Nothing was found beyond day 6.

## What I could not find or verify

- No trial of transfusion against no transfusion, and no trial of different triggers.
- No study of oxygen, fluid strategy or haematinics for babesial anaemia, and no per-kg haematinic dose in any babesiosis source.
- The AVHTM TRACS consensus (2021) is behind a paywall. I read only its abstract and did not cite it.
- The full text of Jacobson & Swan 1995 (fluids, oxygen, haematinics) was not found; abstract only.
- No DEA 1 prevalence for South African dogs.
- No reaction rates in dogs with babesiosis.
- No source on whether Oxyglobin is available in South Africa, so availability is left blank. Human malaria transfusion thresholds were not searched.

## The statements I am least sure of

- The *B. canis*, *B. vogeli* and *B. gibsoni* figures come from one review (Leisewitz 2023), not from primary papers.
- The Bumby 2024 marrow findings (6 fatal dogs) rest on the abstract.
- I gave packed cell transfusion level A because the only randomised trial used it as the comparator. The trial did not test transfusion against none: the coordinator may prefer level B.

## Decisions for the user or coordinator

- Whether to keep the HBOC entry, since the product may no longer be on sale (I found no source either way).
- Whether a veterinarian should review the transfusion approach steps. They follow the Onderstepoort protocol and one veterinary manual.
- Look at the page in the browser: it was not seen in this run.
