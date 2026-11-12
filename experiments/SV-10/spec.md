# SV-10 spec: designs that need new data

Written 2026-11-12, after the sub-agents had started and after the first draft of memo 3 (deviation D1 in `report.md`). SV-10 opens no outcomes file and runs no test, so the outcome lock of
`rules.md` does not apply; this spec fixes what the memos must contain and how the sample sizes are computed.

## Experiments

| Code | Method | Memo |
|---|---|---|
| SV-10-01-parasite-genotype | study_design | `out/memo_parasite_genotype.md` |
| SV-10-02-host-genetics | study_design | `out/memo_host_genetics.md` |
| SV-10-03-minimum-dataset | study_design | `out/memo_minimum_dataset.md` |

Role `descriptive`. No dataset, no independent source, no seed (no random numbers).

## Each memo

- At most about 3 pages (about 1,800 words).
- Builds on what the finished packages (SV-01, SV-02, SV-03, SV-04, SV-05, SV-07) could not answer, and says which gap it closes.
- Memo 1: BrEMA1 replication of CB379 and a genome-wide parasite alternative using the *B. rossi* assembly; adjustment for age,
  days sick and load; a sample size.
- Memo 2: a PubMed search for existing canine host-genetic work first (search log with counts); then a within-breed severe-against-mild
  design reviewing red cell traits, DEA 1, haptoglobin and cytokine loci; a sample size.
- Memo 3: one outcome set from SV-03's definition map; capillary and qPCR load; days sick; antibody status; breed, age, neuter status;
  a sample before treatment; stored plasma for the mechanisms SV-06a ranks highest; a sample size.
- No predictive model, no risk score, no "subtype". Every literature claim with a DOI. No article text beyond short paraphrase.

## Sample sizes

`scripts/power.py`, standard library, normal approximations, power 0.8, two-sided:

- Binary exposure, case-control (Fleiss, uncorrected); covariate adjustment by 1 / (1 - R²) (Hsieh 1998).
- Diploid allelic test for the host GWAS (dogs = alleles / 2), times a relatedness inflation.
- Continuous exposure in logistic regression (Hsieh 1989).
- Rank tests: n / 0.955.
- Death proportion 0.11 from S-CB050 (SV-05: 15 of 140).
- **Check:** the formula must reproduce SV-05's detectable OR of about 3.7 for the S-CB050 age contrast. If it does not, report it.

## What would count against a design

A design whose required n is beyond any plausible multi-centre cohort (more than about 2,000 dogs for its primary question) is
reported as not feasible, not hidden.

## Sub-agents

One per memo for memos 1 and 2 (literature research and draft). Memo 3 is written by the package agent.
