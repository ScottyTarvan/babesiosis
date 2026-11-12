# SV-02. Resistance or tolerance?

| | |
|---|---|
| Wave | a: 2. b: 1. c: user decision |
| Lane | Cross-study synthesis, then author data |
| Effort | Medium, then large |
| Working folder | `/experiments/SV-02/` |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), then in [data.md](data.md): `DS02` and "Literature inputs".

- **Hypothesis.** Dogs differ more in the damage they suffer at a given parasite load (tolerance) than in the load itself (resistance).
- **Background.** According to PubMed (searched 2026-11-12), no record joins canine babesiosis with "disease tolerance", "tolerance and resistance", "resilience" or "reaction norm". Pieces in the corpus point both ways: load was higher in dogs that died, but the authors doubted it was the only trigger ([10.1016/j.vetpar.2006.05.002](https://doi.org/10.1016/j.vetpar.2006.05.002)); antibody level tracked a haematological score more strongly than load did in 342 *B. canis* dogs (CB141, [10.1186/s13071-025-06997-4](https://doi.org/10.1186/s13071-025-06997-4)); CB516 found no difference by outcome; CB381 found severe anaemia at very low load in *B. gibsoni*; CB375 reports vaccine protection with unchanged parasitaemia. Methods from human malaria: [10.1371/journal.pntd.0009886](https://doi.org/10.1371/journal.pntd.0009886), [10.1084/jem.20241667](https://doi.org/10.1084/jem.20241667), [10.1038/s41564-019-0474-x](https://doi.org/10.1038/s41564-019-0474-x).
- **SV-02a, load-by-outcome synthesis.** Depends on SV-G2. From `associations_v2.csv` take every parasitaemia row. Inside one species and one outcome class, pool the standardised difference in log load (random effects, Hartung-Knapp interval) only if 3 or more independent units share the definition; otherwise give a direction table. Use `load_method` and `sample_timing` as moderators. List separately every result of the form "severe disease at low load" or "protection at unchanged load".
- **SV-02b, reaction norms in the Beagles.** Depends on SV-G1. For each of the 5 dogs, before treatment: haematocrit, lactate and habitus against log parasitaemia. Report each dog's slope and the low-dose and high-dose dogs side by side. Descriptive only.
- **SV-02c, author data request.** A user decision. Draft the request for dog-level load, antibody status, age and outcome from CB141 (342 dogs), CB040 (320 dogs) and RQ-CB145. Planned model: health measure against log load, with age and antibody status as modifiers of the slope, inside one species.
- **Confounders.** Species (never mix). Load method (capillary load is higher than venous). Admission load is one moment: use pseudo-stage from SV-01 where the same dogs have it. Treatment before sampling.
- **Main risk.** Error in measured load flattens slopes and imitates tolerance. Publication bias in SV-02a.
- **Outputs.** `out/load_by_outcome.csv`, `out/reaction_norms.csv`, `out/author_request_draft.md`, `report.md`.
