# Refutation brief (SV-META step 6)

You are a sceptical reviewer. Your only job is to try to **reject** one candidate research lead from a programme of experiments
on canine babesiosis severity, and to record honestly whether it survives. A candidate that survives is still only a lead
(hypothesis-generating); you are not asked to confirm it.

Repository: `C:\Workspaces\Babesiosis`. Read `/CLAUDE.md` rules first (short). Relevant facts:

- Only `CB` articles are canine evidence. Article appraisal notes: `/core/articles/<ID>_*.md`. Full texts (copyrighted, read only,
  never copy text into your output): `/core/data/markdown/<ID>.md`.
- Independent sources after the linkage audit (`/experiments/SV-07/report.md`): SRC-A = S-CB050 = S-CB517 = DS03 natural dogs
  (Onderstepoort, *B. rossi*, died vs survived; died includes euthanasia); SRC-B = DS02 = DS06 = DS03 experimental (5 Beagles);
  SRC-C = DS07 (archived serum, complicated vs uncomplicated, may share numbering with DS04); SRC-D = S-CB017 (*B. canis*, Zagreb);
  SRC-F = DS05 (Eastern Cape clinic, habitus only, no hard outcome); SRC-O = S-CB516 (*B. canis*).
- Tidy files: `/experiments/shared/tidy/*.features.json` and `*.outcomes.json` (contract in `/experiments/rules.md`).
- The theme indicators: `/experiments/SV-META/out/themes.csv` and `out/theme_indicators.json`. Spec: `/experiments/SV-META/spec.md`.
- A Python 3.12 environment with numpy and scipy: `C:\Workspaces\Babesiosis\experiments\SV-META\env\py\Scripts\python.exe`.
  Run it with `-I`. You may compute checks from the tidy files (rank statistics, partial correlations, bootstrap by dog). Fix seed
  20261112. Put any script you write in `/experiments/SV-META/refutation/scripts/<candidate_id>_*.py`.
- PubMed is available through the PubMed MCP tools (load them with ToolSearch, query "pubmed search_articles"). Put no user name,
  email address or project details in a query. Cite each literature claim with a DOI.

Reasons you may use to reject: the same dogs counted twice; the marker is in the severity label; the result does not survive the
correction for the number of tests or themes; the finding is already published in a CB article (for a gap lead: canine severity data
already exist); an artefact of the sample, the assay or the plex/batch; the direction changes in a sensitivity analysis; a confounder
explains it (for example anaemia, stage, total leukocytes). Do not use the words "subtype" or "endotype". Do not fit a predictive model.

**Write exactly one file**: `/experiments/SV-META/refutation/<candidate_id>.json` with this shape (valid JSON, no NaN):

```json
{"candidate_id": "K01", "attempts": [
  {"reason_tested": "short name of the rejection reason", "method": "what you checked, with file paths or queries",
   "result": "what you found, with numbers and DOIs", "rejects": false}],
 "verdict": "survives | survives_weakened | refuted",
 "verdict_reason": "two or three sentences",
 "suggested_tier": "A | B | C | D | X",
 "human_counterpart": [{"claim": "...", "doi": "10.xxxx/...", "direction_agrees": true}],
 "canine_parallel_already_made": "yes/no, with CB IDs"}
```

Do not edit any other file in the repository. Do not commit. Do not contact anyone. Finish with a three-line summary.
