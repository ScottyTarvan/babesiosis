# SV-META. Meta experiment: a final review of all experiments for research leads

| | |
|---|---|
| Wave | 4 (last) |
| Lane | Meta review |
| Effort | Medium to large |
| Working folder | `/experiments/SV-META/` |
| Experiment code | `SV-META-01-research-leads` (method `meta_review`) |
| Status | See [index.md](index.md) |

**Read first:** [rules.md](rules.md), [run-instructions.md](run-instructions.md), [ledger.md](ledger.md), then all of [data.md](data.md). Then the `report.md` of every package and the files in its `out/` folder.

- **Question.** Does any result of the 23 experiments, alone or together with results of other experiments, show a finding that is worth further research? The user looks for three kinds of finding:
  1. **Severity.** A correlation between a measurement and the severity of disease.
  2. **Mechanism.** A mechanism of disease that is not established in canine babesiosis.
  3. **Human parallel.** A correlation with a similar human disease (falciparum malaria, human babesiosis, sepsis) that the canine literature has not made.
- **Aim.** A ranked list of areas for further research. The experiment is hypothesis-generating. It does not confirm a hypothesis.
- **Depends on.** All other packages (all are `Done`; SV-02c was not run and stays a user decision).
- **How it differs from SV-INT.** SV-INT asked if five lines of explanation that were set before the work are supported. Its answer was "none", and it used the primary results. SV-META reads for discovery:
  - It uses every result: primary, secondary, sensitivity, descriptive, positive controls, and observations that a package made in passing. It reads the `out/` files, not only the reports. It does not start from the SV-INT table.
  - It looks for agreement between independent sources. A weak result that points the same way in three independent sources can be a better lead than one strong result from one file.
  - It checks if each candidate is new: against the 444 `CB` articles, and against the human literature.
  - It tries to refute each candidate before it reports it.

## Steps

1. **Spec first.** Write `spec.md` before you score a result: the screen of step 3, the tier rules, the list of themes of step 4 with one indicator for each independent source, and the combination method. All labelled files are already seen (see "Outcome lock" in [rules.md](rules.md)), so the role of the experiment is `descriptive`. Record the spec hash as the other packages do.
2. **Result census.** Make one row for each quantitative result of each experiment in `out/census.csv`: experiment code, what was measured, the outcome or comparison, species, dataset, independent source (counted after SV-07, as SV-INT section 4.4 does), n, effect size with its interval, p and q if they exist, the size of the test family, the role of the result, and the file and line it comes from. Add the observations that have no test (for example a linkage fact, or a gene missing from a matrix) with the type `observation`. Each number must come from a file: write a check that finds each number in its source file, as `SV-INT/scripts/build.py` does for quotes.
3. **Screen.** Give each census row these answers:
   - **Statistical.** Does the interval exclude no effect? Does the result pass the false discovery rate of its own family? For 5 dogs: is the direction the same in all dogs?
   - **Independence.** How many independent sources show it?
   - **Circularity.** Is the measurement a part of the severity label, or does it restate a known driver (anaemia, band neutrophils, the label itself)?
   - **Novelty.** Is it in the article that published the dataset? Is it reported elsewhere in the canine literature? Is it known in a human disease? Search `/core/articles.jsonl` (stream it), `/core/articles/`, `SV-G2/associations_v2.csv` and the database search (`dbo.search_articles`, `dbo.search_passages`; see `/docs/database.md`). Then search PubMed.
   - **Power.** What effect could the analysis detect?
4. **Agreement between sources (the new calculation).** Put the census rows in mechanism themes. Examples: neutrophil activation and left shift; monocytes, macrophages and chemokines; type 1 interferon; haemolysis and cell-free haemoglobin; endothelium and coagulation; the endocrine stress response; anaemia and regeneration; antibody and parasite load; host factors. For each theme:
   - Use one indicator for each independent source, declared in `spec.md`. Do not count two files of the same dogs twice.
   - If an indicator is not on a common scale, you may calculate it from the tidy files in `shared/tidy/` (Cliff's delta or Spearman's rho, with a bootstrap interval, by dog). Calculate only what the theme needs. Do not search the files for new markers.
   - Report the direction and the effect of each source, a sign test, and a combined test (Stouffer or Fisher, one p-value for each independent source). Do a leave-one-source-out check.
   - The themes are chosen after the results were seen. Say this beside each combined p-value, and correct for the number of themes.
   - Keep *B. rossi* and *B. canis* apart first (rule 6), then show the two together as a transfer check.
5. **Human parallels.** For each candidate of steps 3 and 4, for the top gaps of SV-06a and for the signatures of SV-08: name the counterpart in falciparum malaria, human babesiosis or sepsis. State if the direction agrees. Cite each claim with a DOI link. State if the canine literature already makes this parallel. Use the `HU` articles as comparators. A parallel is "new" only if no `CB` article and no PubMed record that you found makes it.
6. **Try to refute.** For each candidate, make a separate attempt to reject it (a sub-agent with a fresh context is a good tool for this). Reasons to reject: the same dogs counted twice; the marker is in the label; the result does not survive the correction for the number of tests or themes; it is already published; it is an artefact of the sample or the assay; the direction changes in a sensitivity analysis. Record the attempt and its result for each candidate, also when the candidate survives.
7. **Tiers.** Give each candidate one tier. Sharpen these definitions in `spec.md`; do not make them easier to pass.
   - **A, significant finding:** passes the statistical screen in two or more independent sources, is not circular, and is not already published as a severity finding.
   - **B, signal:** passes the statistical screen in one source, is not circular.
   - **C, convergent lead:** no single result passes, but the direction agrees in two or more independent sources and the combined test supports it.
   - **D, gap lead:** no canine data, strong human evidence, and a measurement that is possible in dogs.
   - **X, rejected:** null, circular, artefact, or refuted in step 6. Keep these rows: they show what was examined.
8. **Research leads.** Write 10 leads at most, in rank order. Each lead has: the hypothesis in one sentence; the kind of finding (severity, mechanism, human parallel); the tier; the evidence (experiment codes, effects, sources); the human counterpart with its citation; what result would refute it; the cheapest next study with data that exist (for example the DS03 to S-CB050 join, a new quantification of DS06, an author data request) and the study that needs new dogs (link to the SV-10 designs); and the measurement to add to the minimum dataset of SV-10-03.

## Rules that matter most here

- **Report what is there.** If no candidate reaches tier A or B, say so in the first sentence of the summary. Do not raise a tier to have a finding. A lead of tier C or D is a useful result: say what it is.
- Do not fit a predictive model. Do not use the words "subtype" or "endotype". A candidate is a thing to measure, not a predictor.
- "Died" includes euthanasia in the Onderstepoort files. One species for each source: do not attribute a difference between files to the species.
- Do not put article text in an output. Do not put the user's name, email address or project details in an outside request.
- Do not contact an author. Do not change `/core/`, the shared plan files, or the files of another package.

## Outputs

- `SV-META/spec.md`, `exposure.md`, `environment.md`, `run.md`, `report.md` (template in [rules.md](rules.md)).
- `out/census.csv`, `out/themes.csv` (one row for each theme and source, and the combined rows), `out/leads.csv`, `out/refutation.csv`.
- The rows of `SV-META-01-research-leads` in the database, and a view for the method `meta_review` (step 4 of [run-instructions.md](run-instructions.md)). The view shows first: the number of candidates in each tier and the answer in one sentence. Then the leads as cards in rank order (tier, kind of finding, hypothesis, evidence, human counterpart, next study). Then a chart of the themes: one row for each theme and source, with the effect and its interval. Then the census as a table that the reader can filter by tier and by experiment.
- The row in [ledger.md](ledger.md).

**The place on the Experiments screen.** The coordinator has pinned the package `SV-META` to the top of the rail (in `experiments.component.ts`). Do not change the page component, the rail or the routes. Give the experiment a `name` that starts with "Meta experiment:".
