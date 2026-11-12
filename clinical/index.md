# Clinical manual index: syndromes of canine babesiosis and their treatment

Version 1, 2026-11-12. The Status column and [ledger.md](ledger.md) say what is done.

**Aim.** A clinical manual in the web app (menu item "Clinical") for veterinarians in practice in South Africa. One page for each clinical syndrome of canine babesiosis: what it is, how to diagnose it, which treatments were proposed, and the evidence, with a linked reference list.

## How to use this folder

1. Read [rules.md](rules.md) once (rules, research method, the steps of a run).
2. Read [content-format.md](content-format.md) (the page file that you write).
3. Open the file of your page from the table below. You do not need the files of other pages.

A path that starts with `/` is from the repository root. Other paths are relative to `/clinical/`.

## Pages

"Treatment papers" and "Term articles" are rough signals of the local material (counted 2026-11-12; the meaning is in [rules.md](rules.md), "Local sources"). They are not evidence counts.

| ID | File | Syndrome | Rail group | Treatment papers | Term articles | Status |
|---|---|---|---|---|---|---|
| TX00 | [TX00-antibabesial-treatment.md](TX00-antibabesial-treatment.md) | Antibabesial treatment and persistence | Parasite treatment | 34 uncomplicated, 34 chronic or relapsing | – | Done 2026-11-12 |
| SY01 | [SY01-severe-haemolytic-anaemia.md](SY01-severe-haemolytic-anaemia.md) | Severe haemolytic anaemia | Blood | 215 | 267 | Done 2026-11-12 |
| SY02 | [SY02-immune-mediated-haemolytic-anaemia.md](SY02-immune-mediated-haemolytic-anaemia.md) | Secondary immune-mediated haemolytic anaemia | Blood | 26 | 33 | Done 2026-11-12 |
| SY03 | [SY03-thrombocytopenia-coagulopathy-dic.md](SY03-thrombocytopenia-coagulopathy-dic.md) | Thrombocytopenia, coagulopathy and DIC | Blood | 110 (DIC 16) | 212 (DIC 38) | Done 2026-11-12 |
| SY04 | [SY04-bone-marrow-failure.md](SY04-bone-marrow-failure.md) | Bone marrow failure | Blood | 13 and 11 | 24 | Done 2026-11-12 |
| SY05 | [SY05-acute-kidney-injury.md](SY05-acute-kidney-injury.md) | Acute kidney injury | Organs | 56 | 53 | Done 2026-11-12 |
| SY06 | [SY06-hepatopathy-icterus.md](SY06-hepatopathy-icterus.md) | Hepatopathy and icterus | Organs | 43 and 49 | 56 | Done 2026-11-12 |
| SY07 | [SY07-cerebral-babesiosis.md](SY07-cerebral-babesiosis.md) | Cerebral babesiosis | Organs | 18 | 37 | Done 2026-11-12 |
| SY08 | [SY08-lung-injury-ards.md](SY08-lung-injury-ards.md) | Acute lung injury, ARDS and pulmonary oedema | Organs | about 19 | 26 | Done 2026-11-12 |
| SY09 | [SY09-cardiac-dysfunction.md](SY09-cardiac-dysfunction.md) | Cardiac dysfunction | Organs | 6 | 17 | Done 2026-11-12 |
| SY12 | [SY12-acute-pancreatitis.md](SY12-acute-pancreatitis.md) | Acute pancreatitis | Organs | 6 | 41 | Done 2026-11-12 |
| SY13 | [SY13-haemorrhagic-gastroenteritis.md](SY13-haemorrhagic-gastroenteritis.md) | Haemorrhagic gastroenteritis and gut signs | Organs | 1 | 3 | Done 2026-11-12 |
| SY15 | [SY15-rhabdomyolysis.md](SY15-rhabdomyolysis.md) | Rhabdomyolysis | Organs | 0 | 15 | Done 2026-11-12 |
| SY10 | [SY10-shock-hypotension.md](SY10-shock-hypotension.md) | Shock and hypotension | Circulation and systemic | 6 | 58 | Done 2026-11-12 |
| SY11 | [SY11-sirs-mods.md](SY11-sirs-mods.md) | SIRS and multiple organ dysfunction | Circulation and systemic | 28 | 70 | Done 2026-11-12 |
| SY14 | [SY14-haemoconcentration.md](SY14-haemoconcentration.md) | Haemoconcentration ("red biliary") | Circulation and systemic | 0 | not found | Done 2026-11-12 |
| SY16 | [SY16-metabolic-endocrine.md](SY16-metabolic-endocrine.md) | Metabolic and endocrine derangements | Metabolic | about 8 | 49 | Done 2026-11-12 |

Only the coordinator changes the Status column (Not started, Running, Done, Blocked).

The definitions are **working definitions** from the classical "complicated babesiosis" framework. They were not checked against the papers. Each agent confirms or corrects the definition of its page from the literature.

## Scope decisions (apply to all pages)

- Heart failure is in SY09. Lung oedema is in SY08.
- The drugs against the parasite are in TX00 only. A syndrome page covers the treatments aimed at the syndrome (for example transfusion, immunosuppression, renal support, ventilation) and links to TX00.
- SY11 is the umbrella page: the definition of complicated disease, triage and the order of care. It links to the organ pages and does not repeat their treatments.
- Co-infection and neonatal disease are modifiers. Record them inside each page; they are not pages.
- Out of scope: prevention (tick control, vaccines), and rare single reports (splenic rupture or torsion, skin lesions, eye signs, reproductive effects).
- Report every finding by *Babesia* species. Most literature on complicated disease is on *B. rossi* and *B. canis*; persistence is mainly *B. gibsoni*. *B. rossi* is the main species in South Africa.

## Order of work

```
Step 0 (coordinator)   CL-00  the Clinical screen: menu item, route, side rail, page renderer   DONE 2026-11-12
Step 1 (any order, one child session for each page)
                       TX00, SY01 to SY16
```

The pages do not depend on each other: a page links to another page by its ID only. The Clinical screen is built, so each agent can see its page in the browser (`/clinical/<ID>`). If agents are scarce, the recommended order is TX00, SY11, SY01, SY05, SY07, SY08, then the others.

## Notes for the coordinator

- The screen is built: [CL-00-shell.md](CL-00-shell.md) says what was built and checked. The rail reads `/webapp/Babesiosis.Web/public/assets/clinical/index.json`; change it when a page is added or a title changes.
- Run each page in its own child session. Give the agent the path of this folder, its page ID and the name of its page file. While `/clinical/` is not committed, the session must share the main checkout: a new worktree would not contain the folder.
- An agent writes only in `/clinical/<ID>/` and one web asset, `/webapp/Babesiosis.Web/public/assets/clinical/<ID>.json`. Two agents never write the same file.
- After each run: read the report, open the page, and check three doses against their sources before you set the Status to Done.

## Decisions that are open for the user

- Whether a veterinarian reviews the pages before the manual is used. The pages are written by AI agents and are not peer reviewed; the screen says so.

## Other files in this folder

| File | Holds |
|---|---|
| [rules.md](rules.md) | Rules for every agent: sources, evidence levels, units, references, the steps of a run, the ledger |
| [content-format.md](content-format.md) | The page file: fields, allowed values, text rules |
| [CL-00-shell.md](CL-00-shell.md) | The specification of the Clinical screen (coordinator) |
| [ledger.md](ledger.md) | One row for each page that was started |
| `shared/example.json` | A page file with every field (placeholder content, not clinical) |
| `shared/validate.py` | Checks a page file against the format. Standard library only |
