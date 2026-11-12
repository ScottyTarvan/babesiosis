# SV-10 report: designs that need new data

Run 2026-11-12. Experiments `SV-10-01-parasite-genotype`, `SV-10-02-host-genetics` and `SV-10-03-minimum-dataset`, method
`study_design`, role `descriptive`. No data analysed, no test (0 of 0). Every number below is a planning assumption or a power
calculation.

## 1. Question and hypothesis

Which new studies would answer the questions that the existing public files cannot: does parasite genotype change the outcome, do host
genes change it within one breed, and what minimum dataset would a prospective cohort need? There is no hypothesis test; the "hypothesis"
is that each question is answerable at a feasible size (spec: primary question needs no more than about 2,000 dogs).

## 2. Inputs

| File | SHA-256 |
|---|---|
| `spec.md` | `37d9c576a99cb40c7ce4cc73280a70d5fd416bec85b75f9fd7e78f813dd529f1` |
| `scripts/power.py` (script version `9507f20d0e18`) | `9507f20d0e1803ebc784a1442bebfacd282b2bf598414d292b878fa20aa0e093` |
| `scripts/build_load.py` | `5e7412ffd5e59683535eb6681810573c0334e65cee2a1836df3036014c0c3089` |
| `scripts/design.json` | `584a0b88ee80b73a6eb6fc5f3b4fb07e75f5971bc9d6529f7711f6250fb2adad` |
| `memos/memo_parasite_genotype.md` | `7ee7c182b390cdcb42aee9f75095ab74bef2f57aa53a145cffb837144c9db80d` |
| `memos/memo_host_genetics.md` | `df0e3c73b762daaa32a3ee3745dc86c1ce53ac6ef45cd4cbcbef87e1a392f567` |
| `memos/memo_minimum_dataset.md` | `7535d7e2816feaf3f4b2129fea62de74d5dca1369847bf6d59364417a6e96d9d` |
| `research/parasite_genotype_notes.md` | `088c24a52fdf72c4e6129d542535008fe17c5d60d9433c37040a24b7728403c0` |
| `research/host_genetics_notes.md` (PubMed search log) | `80a0442bb934254b6d1bd5871df542ded31b61d45d777e440aa7da5aff50b476` |
| `/experiments/SV-03/out/definition_components.csv` | `590dd4169cdcd118dc3417409c5fd46c381013fec7f709cc7382f42fd0712385` |

Also read: sections 4, 7 and 9 of the SV-01, SV-02, SV-03, SV-04, SV-05 and SV-07 reports; appraisal notes CB379, CB143, CB125 and
others found by grep in `/core/articles/`; PubMed records. No outcomes file was opened (`exposure.md`). The host-genetics sub-agent
counted breeds in the DS05 raw file (no outcome label; DS05 is on the "already seen" list).

Python 3.12.12 (uv), standard library only. No random numbers, no seed.

## 3. What was done

- Two sub-agents (one per memo) researched and drafted memos 1 and 2; the package agent wrote memo 3, set every sample-size scenario
  in `scripts/power.py`, and edited the three memos for consistency (sample-size sections, recommendations, open question 7 of memo 2).
- `scripts/power.py`: 54 scenarios. Fleiss case-control formula for binary exposures with 1 / (1 − R²) covariate inflation; diploid
  allelic test for the host GWAS times 1.15 for relatedness; Hsieh's formula for a continuous exposure; rank tests / 0.955.
- `scripts/build_load.py` fills each memo's table, writes `out/memo_*.md` and the three load files; the console loader wrote them.
- **Formula check (spec):** the formula gives a detectable OR of **3.66** for the S-CB050 age contrast (50 young vs 90 adult, 9/90 adult
  deaths), matching SV-05's "about 3.7". Conditioning the other way (15 deaths vs 125 survivors) gives 4.68: the case-control direction is
  more conservative with few events. Both are in `out/power.json`.
- Repeat check: `out/` deleted and rebuilt twice; `power.csv` and the three memos are byte-identical; load files differ only in `run_utc`.

**Deviations**

- **D1.** `spec.md` was written after the sub-agents had started and after the first draft of memo 3 (no outcome lock applies; nothing
  was tested).
- **D2.** Memo 3 was written by the package agent, not by a sub-agent (the package file says one sub-agent per memo). The package agent
  held the finished-package results that memo 3 needs.
- **D3.** Load adjustment differs by memo. Memo 1 adjusts for load (the package file asks for it: parasite genotype at a given load).
  Memo 2 does not adjust for load in its primary analysis, because load may lie between host genotype and severity; a secondary analysis
  adjusts for it. The package file's phrase "avoiding collider bias by conditioning on load" was read as "avoid the bias that conditioning
  on load can cause".
- **D4.** Memo 3's stored-plasma panel is not ranked by SV-06a: SV-06a was still running. The panel covers its seven mechanism families.
- **D5.** Memos 1 and 2 are about 1,850 to 1,900 words of text plus the scenario table, slightly above "3 pages".
- **D6.** CB379's exposure is re-defined, not replicated as published: its four "poor prognosis" genotypes cover 90% of the 141 isolates
  and no genotype-by-outcome table is in the abstract (the full text could not be read).

## 4. Results

| Memo | Recommended design | Required sample size | Detects |
|---|---|---|---|
| 1. Parasite genotype (`SV-10-01`) | BrEMA1 genotype19 against all others, complicated vs uncomplicated *B. rossi*, one pre-treatment EDTA sample, Firth logistic adjusted for age, log days sick, log load | **80 complicated + 120 uncomplicated = 199**, from about **229 enrolled** (40% complicated, 15% loss) | Adjusted OR 2.5 (genotype19 at 35% in uncomplicated) |
| 1, secondary | Death as outcome | 53 deaths + 422 survivors, about **545 enrolled** | OR 2.5 |
| 1, Design B | Genome-wide (sWGA + sequencing, 3,098 genes, about 30,000 SNPs) | 230 to 280 analysed for OR 5 per gene; 481 to 640 for OR 3 | Hypothesis-generating only |
| 2. Host genetics (`SV-10-02`) | Within pit bull-type dogs with *B. rossi*, severe vs mild 1:1, 20 candidate loci (DEA 1, haptoglobin, cytokine SNPs, TLR4/MYD88, DLA) and a SNP-array GWAS | **142 severe + 142 mild = 283**, from about **471 pit bull-type cases** (about 14 hospital-years) | DEA 1 OR 3 at alpha 0.0025; allelic OR about 3 genome-wide (5e-7) |
| 2, smaller effects | Same | OR 2: 330 to 500 severe; OR 1.5: more than 900 severe | Not feasible in one breed |
| 3. Minimum dataset (`SV-10-03`) | Multi-centre prospective *B. rossi* cohort, outcome components stored separately (death and euthanasia apart), smear + qPCR load, days sick, IFAT, signalment with neuter status, pre-treatment and 24 h samples, stored plasma, permanent dog ID | **610 dogs (about 67 deaths)**, at least 200 outside Onderstepoort | OR 1.5 per SD of log load or a marker (R² 0.2); OR about 2 for a binary host factor (559 needed); 0.65 SD marker replication in 200 non-Onderstepoort dogs |

PubMed (memo 2): 13 queries and 5 known-item lookups, 365 hits, 280 unique records screened, about 41 relevant. **No canine study has
genotyped dogs against babesiosis severity or outcome.** DEA 1 was tested only against infection (CB143, Nigeria; Zimbabwe), both null.

The three designs fit together: the 610-dog cohort of memo 3 holds memo 1's primary contrast (229) and its death contrast (545), but only
about 30 severe pit bull-type dogs, so memo 2 needs its own breed-focused enrolment under the same protocol.

## 5. Stability and sensitivity

Each memo's table gives the range of its assumptions: memo 1, genotype19 frequency 0.25 to 0.45 changes the primary n from 199 to 218
(OR 2.5); memo 2, DEA 1 frequency 0.40 to 0.60 changes it from 264 to 327 (OR 3); memo 3, the binary-factor n falls from 559 (OR 2) to
195 (OR 3). The largest unknown is the share of severe or complicated disease (30% and 40% assumed): n scales inversely with it.

## 6. Confounders

Listed per memo: site and parasite population structure (memo 1), within-breed exposure (bites, ticks, housing) and referral selection
(memo 2), euthanasia for cost or prognosis, treatment before sampling, and owner-reported days sick (all three).

## 7. What this does not show

- No data were analysed. The sample sizes are normal approximations with assumed frequencies; they are planning figures, not results.
- The designs are for *B. rossi*. They must be re-run for *B. canis* or *B. gibsoni*.
- None of them supports prediction, a risk score or "subtypes"; treatment effects cannot be estimated.

## 8. Verified, documented, inferred

- **Verified in files:** the SV-05 formula check; the SV-03 definition components; the finished packages' numbers quoted in memo 3.
- **Taken from documentation:** CB379 numbers (abstract and appraisal note); PubMed findings and DOIs (sub-agent research notes, not
  re-checked one by one by the package agent); the B. rossi genome facts (3,098 genes).
- **Inferred:** every frequency, OR, R² and loss assumption; the case throughput per hospital.

## 9. Next step and decisions for the user

1. **Decide whether to pursue any design.** These are drafts; nothing was sent to anyone.
2. **Severity thresholds** for the outcome set (memo 3, open question 3): one published definition, or a new consensus.
3. **Load adjustment** (D3): accept the split between memo 1 and memo 2, or set one rule.
4. When SV-06a reports, rank the stored-plasma assays of memo 3 by its list.
5. CB379's full text would give the original genotype-by-outcome table (memo 1, open questions).

Versions: Python 3.12.12 (uv), standard library; console loader `/console/Babesiosis.Console` (.NET 10); Angular build of
`/webapp/Babesiosis.Web`.
