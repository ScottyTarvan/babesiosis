# Marker-severity extraction guide

Instructions for the agent (or person) extracting one article. The goal is a table of every marker or parameter that an article **tested against clinical severity or outcome** in canine babesiosis, with the result, whether or not it was significant.

## Inputs

- The article text: `data/markdown/<ID>.md`. If `data/markdown/<ID>.en.md` exists, use that (English translation). Read the YAML front matter first: `source_format: abstract` means only the abstract is available.
- The schema: `data/severity/association_schema.json`. Its `description` fields define every field and allowed value. Read it fully before starting.
- The marker names: `data/severity/marker_map.csv`. Rows with `source` = `seed` (or `manual` with a `pattern`) are the canonical markers, with their class. Use those exact names in `marker`.
- Search hints (optional): `data/severity/candidate_sentences.jsonl` (grep for the ID) lists sentences that mention severity or outcome. They are pointers only. Tables are not in them, so read the whole Results section and every table.

## Output

`data/severity/extractions/<ID>.json`, UTF-8, matching the schema. Write only this file.

## Procedure

1. **Read the whole article**, including every table. Note the study population, the *Babesia* species and how it was confirmed, and how the authors grouped dogs by severity or outcome.
2. **Severity definitions.** Add one entry to `severity_definitions` for each way the authors split or graded dogs by severity or outcome (S1, S2, ...). Examples: survivors vs non-survivors; complicated vs uncomplicated; dogs with AKI vs without; a clinical score. Quote the sentence that defines the groups. Give group sizes in `severe_group` and `comparison_group`.
3. **Associations.** Go through the Results text and every table. Add one row for each marker × severity definition × subgroup × analysis:
   - Each marker in a table that compares outcome groups is its own row, including the ones that did not differ (`significant` = `no`).
   - If the same marker has a group comparison and a ROC or regression, add one row for each analysis.
   - If values are given per group with no test, use `descriptive_only` with `significant` = `not_tested`.
   - Correlations of a marker with a severity measure (a score, the number of organ dysfunctions, the degree of anaemia) are rows too.
   - With three or more ordered groups (for example uncomplicated / complicated / died) tested together, define them as one `severity_grade` definition. If the authors also give pairwise tests between groups, extract the pairwise result that matches a definition you created.
4. **Quotes must be verbatim.** Copy the quote from the file, character for character. Never paraphrase or retype it. For a table row, copy the row as it appears in the Markdown, including the `|` separators if you like. Put the table name and column headings in `location`. Use the shortest span that carries the numbers.
5. **Numbers.** In `statistic`, `p_value`, `effect_value`, `effect_ci`, `cutoff`, `sensitivity` and `specificity`, copy the numbers as printed. Do not compute new numbers. If you must derive one (for example a percentage from counts), say so in `note`.
6. **Check your file.** Run:

   ```bash
   python -I scripts/check_associations.py --ids <ID>
   ```

   It prints schema errors, quotes it cannot find in the text, and numbers that occur nowhere in the text. Fix these and run it again until the file is clean, or explain any remaining issue in the row's `note` (for example, a number read from a figure). Do not run the checker without `--ids`: the full run writes shared files.

## Do not extract

- **Infected vs healthy control comparisons.** These are not severity. Count them in `skipped_infected_vs_healthy`.
- Findings from other studies cited in the introduction or discussion.
- Changes over time after experimental infection or treatment, unless they are compared between outcome groups.
- Treatment response, unless treatment is the marker and outcome is the severity measure.

## Edge cases

- **Marker part of the definition.** Examples: creatinine when the groups are AKI vs no AKI; PCV when the groups are anaemia grades. Extract the row, and write `marker part of the severity definition` in `note`.
- **Parasitaemia.** When it is measured and compared between outcome groups, it is a marker (`Parasitaemia`). When the authors define the groups by it, it is a severity definition (`parasitaemia_level`).
- **Categorical findings.** Examples: icterus, collapse, sex, co-infection, compared between outcome groups. Use `proportion_comparison` and the `more_frequent_in_severe` or `less_frequent_in_severe` direction.
- **Garbled PDF tables.** If you cannot tell which number belongs to which group, extract only what you can read with confidence. Set `confidence` = `low`, and describe the problem in `article_notes`.
- **Overlapping cohorts.** If the article says its dogs were also reported elsewhere, say so in `article_notes`.
- **No canonical marker fits.** Give a short new name in `marker`. The checker lists it for the map.
