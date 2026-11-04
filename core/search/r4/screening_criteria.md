# Title/abstract screening criteria (round 4)

Rounds 1–3 were screened against these criteria. This file restates them, from the review scope in `search/index_overview.md` and the eligibility decisions in `search-log.md`, so that round 4 uses the same rules. The only change is the window.

## Question

The review maps the **pathophysiology of canine babesiosis syndromes**: the mechanisms that link infection to complications, severity and outcome in the host dog. A record is eligible when it reports **host-side data in dogs infected with Babesia** that bear on this question.

## Window

Round 4 covers **2006-10-23 to 2016-10-22 inclusive**, by first publication date (the earlier of the online and issue dates). The search applied this date already. Exclude with `out_of_window` only when the record shows that the original publication falls outside the window. For example, a digitised archive can carry a deposit date in the window while the paper is from an older volume. A record that only says "in press" or gives the year alone stays in.

## Host and parasite

- Host: the domestic dog. Wild *Canis lupus* (grey or Iberian wolf) counts as canine evidence. Red fox, jackal and other non-*Canis* canids are excluded (`not_canine_babesia`) unless dog data are present.
- Parasite: any canine *Babesia*: *B. rossi*, *B. canis* (including *B. canis canis*, *B. canis rossi* and *B. canis vogeli* in the older three-subspecies naming), *B. vogeli*, *B. gibsoni*, *B. vulpes* (*Theileria annae*, *Babesia microti*-like, "Spanish dog isolate"), *B. conradae*, *B. negevi*, and unspecified large or small *Babesia*. Older papers often name only "*B. canis*" or "large *Babesia*" without PCR. That is not a reason to exclude; record the species status as unspecified or suspected.
- Mixed infections (for example with *Ehrlichia*, *Anaplasma*, *Hepatozoon* or *Leishmania*) are eligible only when Babesia-specific host data can be separated out.

## Include (decision `include`)

- Pathophysiology and mechanism studies: inflammation, cytokines, acute-phase proteins, immunity, coagulation, platelets, DIC, endothelium, haemolysis, anaemia, erythrocyte injury, oxidative stress, renal, pulmonary, cerebral, cardiac, hepatic, metabolic, endocrine and acid–base disturbances, omics, virulence on the host side, histopathology and necropsy.
- Biomarker, severity, prognosis and outcome studies in infected dogs.
- **Clinicopathological profiles** of infected dogs (haematology or biochemistry case series). These count as descriptive evidence of the syndromes, so include them.
- Experimental infections that report host responses.
- **Case reports only when they describe a distinct syndrome or a mechanistic observation** (for example Evans syndrome, vasculitis, haemophagocytic syndrome, ARDS, cerebral involvement, pancreatitis, rhabdomyolysis). A routine single case of diagnosis and treatment is excluded (`other_out_of_scope`).
- Narrative or systematic **reviews** whose subject is canine babesiosis pathophysiology, clinical syndromes or complications.
- Regional journals that are not indexed in MEDLINE are kept. Do not exclude a record because of where it was published.

`include_type` is `primary`, `case_report` or `review`.

## Exclude (decision `exclude`) and `exclude_reason`

Use exactly one of these codes:

| Code | Use for |
|---|---|
| `prevalence_epidemiology` | Prevalence, molecular or serological surveys, risk factors and distribution, with no host pathophysiological data |
| `not_canine_babesia` | Other hosts (human, cattle, horse, cat, fox, rodent), other parasites, or *Babesia* in general with no dog data |
| `vector_tick` | Tick and vector studies |
| `diagnostic_test` | Development or comparison of a diagnostic assay, with no host pathophysiology |
| `treatment_efficacy` | Treatment trials whose endpoints are cure or parasite clearance, with no mechanistic outcomes |
| `parasite_biology_only` | Parasite genetics, phylogeny, culture or antigens with no host data |
| `not_peer_reviewed` | Theses, dissertations, conference abstracts, preprints, book chapters |
| `not_research` | Editorials, letters with no data, news, errata |
| `other_out_of_scope` | Eligible topic but no usable pathophysiological content (for example a routine case report) |
| `out_of_window` | The original publication is outside 2006-10-23 to 2016-10-22 (see Window) |

A prevalence, diagnostic or treatment study that **also reports host pathophysiological data** for infected dogs (for example haematology or biochemistry of infected dogs compared with controls, or organ-injury markers) is **included**, not excluded.

## Uncertain (decision `uncertain`)

Use `uncertain` when the abstract is missing or too short to decide, or when it does not say whether Babesia-specific host data are reported. The adjudicator then decides, and may read the DOI landing page.

## Duplicates and existing records

- A second record of the same paper (for example a repository copy or a preprint of an included article) gets the same decision. Say "Duplicate record of <key>" in the rationale.
- A record marked "already in the review as BG…" is a background paper that now falls inside the window. Screen it as a new record.
- A record marked "(retired ID)" was excluded earlier as unverifiable or out of window. Screen it on its content and the dates shown.
- A "reference-list entry; not resolved" record has only a title. Screen on the title; use `uncertain` when the title suggests eligible content.

## Fields for each record

- `primary_category` (included or uncertain records only): one of ERY, INF, END, COA, REN, PUL, NEU, CAR, MET, OXO, SEV, as defined in `docs/ids-and-codes.md`.
- `secondary_tags`: further codes from the same list.
- `species`: a short species note with its status, for example "B. canis (confirmed, PCR)" or "Babesia sp. (suspected, smear only)".
- `rationale`: one or two sentences that give the reason for the decision.
