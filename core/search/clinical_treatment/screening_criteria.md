# Re-screen: clinical syndromes plus treatment (2026-11-05)

## Why this re-screen exists

The review's screening criteria (`search/r4/screening_criteria.md`) admit a record only when it reports **host pathophysiological data**. Two exclusion codes therefore removed most clinical-management literature: `treatment_efficacy` (trials whose endpoints are cure or parasite clearance) and `other_out_of_scope` (routine case reports of diagnosis and treatment). This pass re-screens those exclusions, and any other exclusion whose title or rationale mentions treatment, against a **different question**. It does not change the main review's decisions; its output is a separate list.

## Question

Which records describe, in **dogs infected with *Babesia***, both

1. a **clinical syndrome or presentation** (clinical signs, a named complication such as anaemia, IMHA, thrombocytopenia, AKI, hepatopathy, icterus, cerebral signs, ARDS, shock, pancreatitis, or clinicopathological findings), **and**
2. **treatment** given to those dogs (antibabesial drugs, antibiotics, immunosuppressants, transfusion, fluids, dialysis, oxygen, adjuncts, alternative remedies), with some statement of **response or outcome** (recovery, relapse, death, change in parasitaemia or laboratory values, time to recovery).

Both parts must concern dogs. The treatment need not be effective and the design need not be controlled.

## Host and parasite

As in the main review: domestic dog (and wild *Canis lupus*); any canine *Babesia* species, including old "*B. canis*" or "large/small *Babesia*" names without PCR. Co-infections (*Ehrlichia*, *Anaplasma*, *Hepatozoon*, *Trypanosoma*, *Leishmania*) are **eligible** when babesiosis is one of the diagnoses being treated; record `coinfection: true`. Exclude only when *Babesia* is incidental (a history item, or a smear finding that was not treated or discussed).

## Include (decision `include`) and `include_type`

| `include_type` | Use for |
|---|---|
| `trial` | Prospective or randomised comparison of treatments in infected dogs (drug, regimen, adjunct, fluid, transfusion), with clinical or laboratory endpoints |
| `retrospective_series` | Retrospective case series reporting therapy and outcome |
| `case_series` | Prospective or descriptive series of several dogs with signs, treatment and course |
| `case_report` | One or two dogs with presentation, treatment and outcome, including routine cases, treatment failures, adverse drug effects and relapses |
| `experimental` | Experimental infection in dogs where disease was produced and then treated, with clinical course reported |
| `review` | Narrative or systematic review, guideline or consensus whose subject includes treatment of canine babesiosis |

Include a record whose title suggests one of these and whose abstract is missing only as `uncertain`, not `include`.

## Exclude (decision `exclude`) and `exclude_reason`

| Code | Use for |
|---|---|
| `no_dog_clinical_data` | In vitro, mouse, rat or other animal models; non-canine hosts; parasite genetics or drug-resistance genotyping with no treated dogs described |
| `prevention_only` | Acaricide, collar, repellent or vaccine trials whose endpoint is prevention of infection or transmission, with no treatment of clinical disease |
| `pharmacology_healthy` | Pharmacokinetics, toxicity or drug interaction studies in healthy dogs |
| `no_treatment` | Dog clinical or laboratory data are reported but no treatment or outcome is described (pure prevalence, diagnostic, or descriptive records) |
| `no_syndrome` | Treatment is discussed but no clinical presentation of the treated dogs is given (for example a drug-availability letter, a product analysis) |
| `babesia_incidental` | Treated dogs had another primary disease and *Babesia* is incidental |
| `not_peer_reviewed` | Theses, dissertations, conference abstracts, preprints, book chapters |
| `not_research` | Editorials, letters with no data, news, errata |

## Uncertain (decision `uncertain`)

Use `uncertain` when the abstract is missing or too short to decide, or when it is unclear whether treatment or outcome is described. Give the best guess of `include_type` and say what is missing.

## Fields for each record

Return one JSON object per record with exactly these fields:

- `key` (string, as given)
- `decision`: `include`, `exclude` or `uncertain`
- `include_type`: one of the codes above, or null
- `exclude_reason`: one of the codes above, or null
- `syndromes`: list of short lower-case labels for the clinical syndromes or complications described, from this vocabulary where it fits: `haemolytic anaemia`, `imha`, `thrombocytopenia`, `pancytopenia`, `non-regenerative anaemia`, `icterus`, `aki`, `hepatopathy`, `pancreatitis`, `cerebral`, `ards`, `shock`, `sirs/mods`, `dic`, `cardiac`, `uncomplicated`, `chronic/relapsing`, `neonatal`, `coinfection`, `other: <term>`; empty list when none
- `treatments`: list of interventions named (drug or intervention names in lower case, for example `imidocarb`, `diminazene`, `atovaquone`, `azithromycin`, `clindamycin`, `doxycycline`, `transfusion`, `fluids`, `prednisolone`, `n-acetylcysteine`, `haemodialysis`, `homeopathic`); empty list when none
- `outcome_reported`: true when recovery, relapse, death, or post-treatment values are reported
- `species`: short species note, for example `B. gibsoni (PCR)` or `Babesia sp. (smear)`
- `coinfection`: true or false
- `n_dogs`: integer or null
- `rationale`: one or two sentences
