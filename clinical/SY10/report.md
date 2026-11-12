# SY10 Shock and hypotension: run report

Run 2026-11-12, started 10:54 UTC. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY10.json`. The validator prints `OK` with no warnings. The page was not viewed in a browser, by instruction: `validated, not seen`. The page agent ran as a subagent and could not write this file; the coordinator saved its report text here unchanged.

## Definition

The working definition is confirmed, with changes. Shock is circulatory failure with poor perfusion: hypotension, clinical collapse or both, often with hyperlactataemia. It is mainly vasodilatory (hyperdynamic) shock on a background of anaemia.
- No study uses the same blood pressure cut-off:
  - more than 3 SD below healthy controls (Jacobson 2000, B. rossi)
  - MAP below 80 mmHg (Zygner 2014, B. canis)
  - systolic below 100 mmHg (Weingart 2023, B. canis)
- Collapse ("unable to stand unaided") is the marker with the best outcome data. In 320 B. rossi dogs the odds ratio for death was 8.36 (Leisewitz 2019).
- Severe anaemia alone gives a fast heart rate with normal pressure (Zambelli 2009), so anaemia alone is not counted as shock.
- Reviews name a "peracute" form, but no study reports it as a separate group.

## References: 28, all confirmed

24 were confirmed in PubMed, 3 in Crossref (CB200, CB217, CB263) and 1 on the publisher's site (Torti 2014, Hrčak). 9 were read in full text and 19 as abstracts.

| Level | Count | References |
|---|---|---|
| A (trial in babesiosis) | 3 | R7 Zambelli 2009; R18 Dubova 2020 and R21 Dubova 2022 (one cohort, CH13) |
| B (babesiosis cohort or series) | 15 | R1, R3, R4, R5, R6, R8, R9, R14, R15, R16, R17, R19, R20, R22, R25 |
| D (other cause, or human malaria) | 6 | R11 FEAST, R12 Hanson 2013, R23 Goggs 2026 consensus, R24 Summers 2021, R27 Borrelli 2021, R28 Hayes 2016 |
| E (review) | 4 | R2 Köster 2015, R10 Montealegre 2021, R13 Jacobson 2006, R26 Solano-Gallego 2016 |

## Treatments: 8

| Treatment | Status | Level | Dose and its source |
|---|---|---|---|
| Isotonic crystalloid bolus | standard | D | 10 to 15 mL/kg IV, repeated after reassessment (canine sepsis review, R10) |
| Packed red cell transfusion | standard | A | 20 mL/kg over 4 h (B. rossi randomised trial, R7) |
| Noradrenaline infusion | proposed | E | 0.1 to 1 µg/kg/min (R10) |
| Dopamine infusion | proposed | C | 10 µg/kg/min (babesiosis case series, R22) |
| Hypertonic saline 7.5% | proposed | D | 4 mL/kg (dogs with gastric dilatation-volvulus, abstract only, R27) |
| Dextran 40 (rheopolyglucin), alone or with dipyridamole | proposed | A by design only | 5 mL/kg once a day for 3 days (R18); 5 mL/kg of the mixture (R21, abstract) |
| Hydroxyethyl starch | harmful | D | no dose given |
| Hydrocortisone | no_benefit | D | no dose given; none in the sources read |

Every dose and threshold was read a second time against its source in this run, by me; no sub-agent was used. Lactate values were converted from mg/dL by dividing by 9.01: 22.5 becomes 2.5 mmol/L, 45 becomes 5.0 and 40 becomes 4.4.

## Answers to the page questions

1. **How often is hypotension found?**
   - B. rossi: 5 of 10 complicated, 2 of 10 severe uncomplicated and 0 of 10 mild cases.
   - B. canis: 7 of 48 dogs in Poland and 3 of 49 in Germany.
   - It rises with severity, but pressure did not separate survivors from non-survivors in 30 B. rossi dogs.
2. **What kind of shock is it?** Reviews describe a hyperdynamic, vasodilatory shock with leaky vessels and a weakened heart. Blood volume has never been measured in B. rossi. The only measurement (Ukraine, dye dilution) is in dogs whose species was not identified.
3. **How is a bolus given to an anaemic dog at risk of lung oedema?** Only general canine guidance was found: 10 to 15 mL/kg at a time, reassessing after each bolus. The human malaria trials (FEAST in children, Hanson in adults) argue against liberal volumes.
4. **When is blood the right fluid?** For the anaemic dog with a fast heart rate. In a B. rossi trial, packed red cells improved acid-base status and pressure.
5. **Was any vasopressor or steroid tested?**
   - Dopamine was used in one Indian series, with no effect reported.
   - There are no noradrenaline or vasopressin data in babesiosis.
   - No steroid was tested. B. rossi dogs do not show adrenal insufficiency (Schoeman 2008).
6. **What is the outcome of the collapsed dog?** The odds ratio for death was 8.36, and 24 of the 34 deaths were in collapsed dogs (the source does not separate euthanasia). Hypotension that did not respond to fluid was fatal in all 10 Croatian dogs that had it.

## Not found

- Any fluid trial in babesiosis.
- A vasopressin dose, or oxygen data in shocked dogs.
- A hydrocortisone dose.
- Use of hypertonic saline, albumin or steroids in babesiosis.
- Shock data for B. gibsoni or B. vogeli.
- The 2024 AAHA fluid therapy guidelines: access was blocked, so they are not cited.

## Statements I am least sure of

- **Hypertonic saline dose (R27).** From the abstract only; it says "every 15 minutes" but not how many boluses.
- **Dextran-dipyridamole dose (R21).** From the abstract only; its 45 mg dextran per kg does not match 5 mL/kg of a 10% solution. The page flags this.
- **Dextran evidence level.** It is level A by design only.
- **Torti 2014 (R4).** Only the abstract was read, and it does not say what its ± values are.
- **Matijatko 2009 (R8).** The species is not stated in the abstract; the page says so.

## Decisions for the user

- Whether to keep the dextran row at level A.
- Whether someone with access should check the AAHA 2024 doses and add them.
- Whether to delete the PDF the web tool saved automatically outside the repository. It was not read.
