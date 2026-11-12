# SY04 report: poorly regenerative anaemia, pancytopenia and marrow disorders

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/SY04.json` (validator: `OK`, no warnings). View: validated, not seen (no browser used, as the task required).

## Definition

**Changed.** The working definition ("non-regenerative anaemia, pancytopenia or haemophagocytic syndrome") implies marrow failure. The literature does not support that for *Babesia* alone:

- The only marrow study (6 fatal *B. rossi* cases, Onderstepoort) found a **hypercellular** marrow with dyserythropoiesis, more macrophages and plenty of iron. That is ineffective erythropoiesis, not hypoplasia (R1).
- *B. rossi*: the ARC is low for the degree of anaemia, but it rises within days of treatment (R2, R3).
- *B. canis*: pancytopenia is found in 39 to 54% of dogs at presentation and is mostly transient (R5 to R8).
- True marrow hypoplasia or myelofibrosis in tick-borne disease came from chronic *E. canis* (R15) or *Theileria* (R16), not from *Babesia*. Haemophagocytic syndrome is one case report (*B. vulpes*, R10).

The page title in the JSON is "Poorly regenerative anaemia, pancytopenia and marrow disorders". `index.json` still says "Bone marrow failure" (I may not edit it).

## References: 24

| Evidence level of the reference | n | Refs |
|---|---|---|
| A (controlled trial in babesiosis) | 3 | R18 darbepoetin; R21 and R22 N-acetylcysteine (*B. gibsoni*) |
| B (cohort or series of 5 or more dogs with babesiosis) | 13 | R1 to R9, R12, R14, R19, R20 (R20: haemoprotozoan disease, species mixed) |
| C (case report) | 3 | R10, R13, R24 |
| D (other cause, same syndrome) | 4 | R11 haemophagocytic syndrome; R15 chronic *E. canis*; R16 theileriosis; R23 doxycycline for *E. canis* |
| Experimental (in vitro) | 1 | R17 |

Independent studies: R5 (CH11) and R7 (CH12) may overlap (cohorts.json does not merge them). R1 (CH04) and R2 (CH09) are separate Onderstepoort cohorts. Full text was read for 11 references and the abstract only for 13.

## Treatments: 7

| Treatment | Status | Level | Studies |
|---|---|---|---|
| Antibabesial treatment alone (doses in TX00) | standard | B | 3 |
| Transfusion (doses in SY01) | standard | B | 1 |
| Doxycycline for an *E. canis* co-infection: 10 mg/kg PO q24h for 28 days | standard | D | 1 |
| Filgrastim: 10 µg/kg SC | proposed | B | 1 |
| N-acetylcysteine: 15 mg/kg PO for 10 days; 70 mg/kg PO q24h for 14 days; 70 mg/kg PO for 5 days | proposed | A | 3 |
| Immunosuppression for haemophagocytic syndrome (no dose found) | proposed | C | 1 |
| Darbepoetin alfa: 0.5 µg/kg weekly for 3 weeks | no_benefit | A | 1 |

## Answers to the page questions

1. **How common is each form?** The inadequate ARC is usual in *B. rossi* (R2, R3). Pancytopenia is common in acute *B. canis* (R6, R7, R8) and in *B. gibsoni* in one Indian clinic (54 of 120 dogs, R9). Haemophagocytic syndrome is one case (R10).
2. **How much comes from co-infection or drugs?** In the Eastern Cape, *E. canis* co-infection was found in only 2% of *B. rossi* dogs (R14). Elsewhere it is not measured. No source linked the cytopenias to antibabesial drugs.
3. **When can 'non-regenerative' be called?** Not before about 4 to 8 days of anaemia (R1). In *B. rossi* the ARC rose by day 3 of treatment (R3). In *B. canis* it was high by day 14 (R4), but 6 of 19 anaemic dogs had no reticulocytosis by about day 32 (R5).
4. **What did the marrow show?** Hypercellular marrow, dyserythropoiesis and macrophage hyperplasia in *B. rossi* (R1). Hyperplasia with haemophagocytosis in *B. vulpes* (R10).
5. **Does it resolve with antibabesial treatment alone?** In most dogs, yes (R3, R4, R5). One *B. canis* dog took 5 months (R24).

## Not found

- Antibiotic cover for neutropenic dogs with babesiosis: no source. It is listed as an evidence gap, not as a treatment.
- An immunosuppressive drug and dose for haemophagocytic syndrome in babesiosis (R10 abstract only).
- The ACVIM 2002 ehrlichiosis consensus could not be opened (HTTP 403). The doxycycline dose comes from Fourie 2015 (R23) instead.
- No marrow study of surviving dogs, or of *B. canis* or *B. gibsoni*.

## Statements I am least sure of

- **Filgrastim frequency.** The paper says "SID" in the abstract and "single dose" in its Table 1. The page gives both.
- **N-acetylcysteine, 15 mg/kg.** The frequency is not stated, and the paper gives 10 days in the methods and 14 days in the discussion. The dose was translated from a rat model. The study population mixes *Babesia* and *Ehrlichia* and the paper does not give the species by group.
- **N-acetylcysteine, level A.** This rests on two small randomised trials in *B. gibsoni* anaemia, not in marrow failure.
- **Pancytopenia in R9.** The 54 of 120 figure is for "babesiosis" cases in the clinic records; the species is confirmed only for the 20 study dogs.
- **R8 (54% pancytopenia)** comes from the abstract only.

## Decisions for the coordinator

1. **Title.** Accept the new title, or keep "Bone marrow failure" in `index.json` and the JSON. The literature does not show marrow failure caused by *Babesia*.
2. **N-acetylcysteine overlap with SY01.** R21 and R22 treat anaemia in *B. gibsoni* in general. If SY01 also lists N-acetylcysteine, keep one entry and link to it.
3. **Filgrastim** is a human product. Its South African availability was not checked: no source was found.

## Dose check

Every dose and threshold was read a second time against its source. An independent sub-agent also re-checked every row of `evidence.csv` that has a value, with no view of the page. Result: 20 of 21 values match, with no mismatch. The one value the checker could not reach, R14 (2.0%), I read myself in the PubMed abstract ("2.0% (3/149)"). The checker confirmed three conflicts inside the sources themselves, and the page states all three: the filgrastim frequency (R9), 10 or 14 days of N-acetylcysteine (R20), and a "135/324" table note in R7 (the text and the 39.5% fit 342). No change to the page was needed.
