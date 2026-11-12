# SV-INT spec: integration report

Written 2026-11-12, before the synthesis table was built.

## Question

Across the 22 Done experiments of the programme, which lines of explanation for severe against mild canine babesiosis (time, load,
host, parasite, response) do the data support, contradict, or fail to address, and how strong is each piece of evidence?

## What is done

1. One row per contributing experiment in `scripts/synthesis.json`: line, what was asked, what was found, effect with interval, n,
   independent sources, what the analysis could have detected, and a strength class. Every number is copied from the package report
   (or from the `summary` column of `dbo.experiment`), and every row carries one or more literal quotes from the report.
2. `scripts/build.py` checks every quote against the cited report (after removing markdown emphasis and normalising the minus sign
   and white space). The build stops if a quote is not found. This is the guard that numbers come from reports, not memory.
3. A verdict per line, from these rules (fixed now):
   - **Supported**: at least one primary, pre-specified result in the predicted direction with an interval that excludes no effect,
     replicated in a second independent source.
   - **Contradicted**: a pre-specified rule that counts against the line was met, with the analysis able to detect a moderate effect.
   - **Not supported (underpowered)**: tests were run, none supports the line, and only large effects were detectable.
   - **Cannot address**: the files or the literature hold no usable data for the line, or the measuring instrument failed validation.
4. Independent sources are counted after SV-07's linkage findings (DS03 natural dogs = S-CB050 dogs = SRC-A; DS03 experimental dogs =
   DS02 Beagles = SRC-B), not by file or article.
5. Candidates (lactate, MCP-1, band neutrophils, interferon signature, haemoglobin beta, cortisol and thyroid, antibody) are listed
   with the reason each is not a predictor.
6. Every "decision for the user" in the reports is collected into one de-duplicated list, with the package(s) that raised it.
7. Every package's `exposure.md` is combined into one log (`out/exposure_log.md`).

## Outcome lock

SV-INT opens no outcomes file and computes no new statistic. No spec hash applies to an outcome; the spec hash is recorded for
completeness. Role `descriptive`.

## Rules

No predictive model, no "subtypes", no new test. A null result is reported with what it could have detected.
