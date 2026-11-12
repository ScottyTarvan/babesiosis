# SV-G2 extraction guide (schema v2)

For the agent that extracts one batch of articles. Read this file, then `/core/data/severity/EXTRACTION_GUIDE.md` (the pilot guide; its procedure, "Do not extract" and "Edge cases" all still apply), then `/experiments/SV-G2/association_schema_v2.json` in full. Paths in the pilot guide that start with `data/` are under `/core/`. The repository root is `C:\Workspaces\Babesiosis`.

## What changes from the pilot guide

| Pilot guide says | Under v2 |
|---|---|
| Write `data/severity/extractions/<ID>.json` | Write `/experiments/SV-G2/<your folder>/<ID>.json` (the folder your brief names). Write nothing else, except your marker proposals file |
| Schema `association_schema.json` | Schema `/experiments/SV-G2/association_schema_v2.json` |
| `python -I scripts/check_associations.py --ids <ID>` | `cd C:\Workspaces\Babesiosis\experiments\SV-G2` then `python -I scripts/check_associations.py --dir <your folder> --ids <ID> [<ID> ...]` |
| Unmapped markers go to the map | Propose new names in your proposals file (below). Never edit `/core/` |

`text_used` stays relative to `/core/`: `data/markdown/<ID>.md`, or `data/markdown/<ID>.en.md` when that file exists (use the English file then).

Do not open `/core/data/severity/extractions/` or `/core/data/severity/associations.csv` (the pilot results), and do not open any other file in `/experiments/SV-G2/` except this guide, the schema, `marker_map_v2_additions.csv` and the checker. The extraction must be your own.

## New fields (schema v2)

Every file: `"schema_version": "v2"`, `setting`, `sample_timing`, `not_extracted` (an array; `[]` if nothing was left out).

Each severity definition: `components`, `euthanasia_included`, `definition_source`, `follow_up_horizon`.

- `components`: what makes a dog "severe" in this definition. Complicated vs uncomplicated: list the complications that the authors name (for example `["cerebral", "renal", "pulmonary", "hepatic or icterus", "haemoconcentration", "hypoglycaemia"]`). Mortality: `["death"]`. A clinical score: `["score"]`. Anaemia grading: `["anaemia grade"]`. Use `other` for anything not in the list, and say what it is in `definition`.
- `euthanasia_included`: `yes` if euthanised dogs are counted as dead or severe; `not applicable` for definitions not about death.
- `definition_source`: `author-defined`, `not stated`, or what the article cites (for example `Jacobson and Clark 1994 complications`, `SIRS criteria`, `IRIS AKI grading`, `WHO malaria criteria`).

Each association:

- `severe_value` and `comparison_value`: the per-group values exactly as printed, with their spread (`"6.1 (3.2-9.8)"`, `"12/15 (80%)"`). `null` if not printed. Never compute them. `summary_type` says how they are summarised (`median and IQR`, `mean and SD`, `count and percent`, ...); `null` when neither value is printed.
- `load_method` on every `Parasitaemia` or `Parasite DNA load (qPCR)` row: `capillary smear`, `venous smear`, `smear, site not stated`, `qPCR`, `other`, `not stated`. `null` on other rows.

`not_extracted`: one entry for each result against severity that you could not extract (figure with no numbers, garbled table, supplement not in the text, unclear group sizes). This is what the package reports as "what could not be extracted", so fill it honestly.

## Host and parasite factors

Extract them with the same care as laboratory markers, whenever the article compares them between severity or outcome groups (including "no difference" statements with numbers or a test): age, sex, neuter status, breed, body weight, days sick before presentation, antibody status, co-infection, splenectomy, prior treatment, parasitaemia, parasite genotype or species. Canonical names: `Age`, `Sex / neuter status`, `Breed`, `Body weight / body condition`, `Duration of illness before presentation`, `Antibody titre / serostatus`, `Co-infection`, `Splenectomy`, `Treatment factors`, `Parasitaemia`, `Parasite DNA load (qPCR)`, `Parasite species or genotype`.

## Marker names

Use a canonical name from `/core/data/severity/marker_map.csv` (rows with a `pattern`) or from `/experiments/SV-G2/marker_map_v2_additions.csv` (rows with `canonical` = `yes`). If none fits, give a short new name and add one line to your proposals file `/experiments/SV-G2/marker_map_additions/<batch>.csv`, with the header:

```
alias,marker,marker_class,canonical,id,note
```

`alias` = the name as reported, lower case; `marker` = your proposed name; `marker_class` = a class from the schema; `canonical` = `yes` if you propose a new canonical marker, `no` if you map the alias to an existing canonical name; `id` = the article.

## Copyright

The article texts are copyrighted. Put in the JSON only the short verbatim quotes the schema asks for: the shortest span that carries the numbers, one or two sentences at most, or one table row. No other article text in any file.

## Before you finish

1. Run the checker on all your IDs. Every quote must be `exact` or `near`; fix the others. Fix every schema error. For each number "not in text", correct it or explain it in that row's `note`.
2. If an article in your batch reports nothing against severity (only infected vs healthy, or only descriptive), still write its file with `severity_definitions: []`, `associations: []`, and say why in `article_notes`.
3. Your final message: one line per article (ID, definitions, rows, quote check result, anything uncertain), and the path of your proposals file. Do not paste article text.
