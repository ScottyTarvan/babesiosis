# TX00 report: antibabesial treatment and persistence

Run 2026-11-12. Page file: `/webapp/Babesiosis.Web/public/assets/clinical/TX00.json`. The validator printed `OK` with one warning, which is explained below. The page was **not seen**, because the start of the preview server was declined.

## Definition

The working definition was **confirmed**. One distinction from the sources was added: *clinical cure* (the signs resolve) and *parasitological cure* (blood PCR negative) are separate end points. Diminazene and trypan blue give the first but do not sterilise the infection. Imidocarb at 7 to 7.5 mg/kg is reported to sterilise large *Babesia*. For small *Babesia*, parasitological cure is described as rare.

## References: 32

| Level of the evidence | References |
|---|---|
| A: controlled trials in dogs with babesiosis | 8 (Birkenheuer 2004, Di Cicco 2012, Checa 2017, Lin 2012, Jacobson 1996, Torbica 2013, Pati 2026; Eddlestone 2006 is an experimental controlled study in *E. canis*) |
| B: cohorts and case series of 5 or more dogs | 13 |
| C: case reports | 2 |
| E: reviews and labels | 9 (6 reviews, the FDA FOI summary, the MSD South Africa label page, the pharmacokinetic study in healthy dogs) |

- 12 references are in the local review (CB IDs).
- 14 were read in full text and 18 as abstracts only.
- Every reference was confirmed in PubMed or Crossref, or on the publisher's page for the two labels.
- An independent sub-agent re-checked every dose row against its source and spot-checked the DOI/PMID pairs. Every dose matched. Five small points were corrected:
  - the Schäfer case-report doses
  - the citations for imidocarb overdose
  - a missing second atropine dose (Checa: 0.02 mg/kg SC)
  - a review that conflicts on the repeat dosing of diminazene, now shown as its own row
  - the duration of the CDI regimen

## Treatments: 14

| Treatment | Status | Level |
|---|---|---|
| Diminazene aceturate | standard | A |
| Imidocarb dipropionate | standard | A |
| Atovaquone with azithromycin | standard | A |
| Trypan blue | standard | A (1 study, 19 dogs) |
| Atropine or glycopyrrolate before imidocarb (adjunct) | standard | E |
| Clindamycin, diminazene and imidocarb (CDI) | proposed | A (1 study) |
| Buparvaquone with azithromycin | proposed | A |
| Malarone, azithromycin and artesunate | proposed | A |
| Doxycycline, enrofloxacin and metronidazole ± diminazene | proposed | B |
| Low-dose diminazene, then clindamycin | proposed | E |
| Tafenoquine | proposed | B |
| Doxycycline or clindamycin alone | proposed | E |
| Phenamidine and pentamidine (no dose found) | proposed | A (1 study) |
| Clindamycin, metronidazole and doxycycline | conflicting | A |

No treatment was classed `no_benefit` or `harmful`. Imidocarb against *B. vulpes* and *B. gibsoni* comes close: it is "not recommended" there, and the page says so in the species notes and the evidence summary.

## What was not found

- No controlled trial against *B. rossi* after 1996, and no PCR follow-up of persistence after diminazene in *B. rossi*.
- No dose changes for puppies, pregnancy, or kidney or liver failure. One case report treated puppies through the lactating dam.
- No safety data on giving two diamidines within 24 h (the CDI protocol).
- The doxycycline dose for *E. canis* co-infection: the ACVIM consensus could not be opened (HTTP 403). The page gives no dose and says so.
- South African registration of imidocarb, trypan blue, atovaquone and buparvaquone. Only Berenil R.T.U. is confirmed, from the MSD South Africa product page.
- A dose for glycopyrrolate.

## Statements I am least sure of

- **Trypan blue has the status `standard`.** It rests on a 1996 South African trial of 19 dogs and two reviews. One review says it is "still used in some parts of the world". A reviewer may prefer `proposed`.
- **Jacobson 1996 treated as *B. rossi*.** The study reports "*B. canis*" (the naming of the time) in Onderstepoort dogs. The page says "South African dogs" and marks the species as *B. rossi* (reported as *B. canis*).
- **The low-dose diminazene with clindamycin regimen** comes only from the Karasová 2022 review. The primary study (Shiranaga & Inokuma 2018, JJVR 66:221) could not be opened, and its DOI is not in Crossref.
- **The CDI doses** come from two reviews. The primary Lin 2012 paper was read as an abstract only. One review reports the trial result in the opposite direction to the abstract; the page says so.
- **The Malarone dose (13.5 mg/kg)** does not say whether it means atovaquone alone or the whole tablet. The page says so.
- **Diminazene repeat interval:** Karasová 2022 describes two doses 7 days apart in South Africa. This conflicts with the label and with Miller 2005, which advises no repeat within 21 days. Both are on the page.

## Validator warning

`doses[1]` of diminazene, "0.1 mL per 2 kg body mass", has no per-kg unit. This is intended: it is the South African label's own wording. The label gives a volume, not mg/kg, and rule 3 does not allow a conversion.

## Decisions for the user or the coordinator

1. Whether trypan blue stays `standard` or moves to `proposed`.
2. Whether a South African source (the IVS or MIMS index) should be consulted for the registration of imidocarb and trypan blue.
3. Whether this page should give an *E. canis* doxycycline dose, from a source that can be read.
4. The page has not been seen in the browser. The coordinator should open `/clinical/TX00` once a preview server is allowed.

## Files written

- `/clinical/TX00/search-log.md`, `evidence.csv` (60 rows), `references-check.csv`, `report.md`
- `/webapp/Babesiosis.Web/public/assets/clinical/TX00.json`
- `/clinical/ledger.md`, row TX00 only
