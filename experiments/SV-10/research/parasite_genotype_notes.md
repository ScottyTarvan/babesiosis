# Research notes: parasite genotype design memo (SV-10)

Date: 2026-11-12. Source of literature facts: PubMed (via the PubMed MCP tool) and the project's own
article notes under `core/articles/`. Every literature claim below carries a DOI link.

## 1. CB379 (Matjila et al. 2009) — what it actually reports

Source: project note `core/articles/CB379_2009_preliminary-evaluation-brema1-gene-tool-associating.md`
and the PubMed abstract record, [DOI](https://doi.org/10.1128/jcm.01110-08) (PMID 19741079,
PMC2772643). The PMC record returns an empty full-text body, so this remains an abstract-level
reading. No text was copied.

Numbers as reported:

| Item | Value |
|---|---|
| Blood samples | 141 total |
| From Onderstepoort Veterinary Academic Hospital | 121 |
| From private clinics (Onderstepoort, Johannesburg, Durban, White River, Cape Town areas) | 20 |
| Diagnosis | thin blood smear, then BrEMA1 PCR + sequencing of the hexapeptide-repeat region |
| Gel profiles | 11 |
| Sequence genotypes | 12, repeat numbers 6 to 31 (named genotype6 … genotype31) |
| genotype19 | 36.2% of parasites typed |
| genotype28 | 20.6% |
| genotype29 | 20.6% |
| genotype11 | 12.7% |
| Sum of the four | 90.1% |
| Outcome contrast | "uncomplicated" (good prognosis) vs "complicated" (poor prognosis), compared retrospectively |

**Critical point for the power calculation.** The abstract gives no 2x2 table: no n per genotype per
outcome, no test, no effect size. It reports only that the four commonest genotypes were also the
ones with the poorest prognosis. Those four cover 90.1% of isolates, so "carries a putatively
virulent genotype" as defined in CB379 is almost universal. A design that copies that grouping has
almost no contrast. The replication must therefore re-define exposure before data collection.
Percentages convert to counts of roughly 51, 29, 29 and 18 of 141 if all 141 were typed — this is my
arithmetic from the published percentages, not a reported count, and should be treated as indicative
only.

## 2. Other canine parasite-genotype work in the review set

Grep of `core/articles/` for BrEMA1, EMA1, genotype, 18S, Bc28, "rossi genome" returned 18 notes.
Only CB379 is a BrEMA1 study. The closest neighbours:

- CB030 (2019): 60 dogs split into three equal groups of 20 by *B. canis* 18S rRNA genotype
  (A/B/C, dinucleotide at positions 150-151). Reports that clinical course differed between
  genotypes but gives no figures. Equal group sizes indicate selection by genotype, so it cannot
  give outcome frequencies.
- CB010 (2017): genome-wide expression work, not genotype-outcome.
- No note in the set reports a *B. rossi* BrEMA1 replication.

Outside the review set, PubMed holds exactly two BrEMA1 papers: CB379 itself and Adamu et al. 2014,
[DOI](https://doi.org/10.1186/1756-3305-7-119), which screened 100 dogs in Jos, Nigeria, found
*B. rossi* in 38 of 72 pathogen-positive specimens, and detected **no** BrEMA1 gene at all by RT-PCR.
That is the only follow-up: it tests presence, not genotype-outcome association, and its authors
infer that Nigerian *B. rossi* may be less virulent. So the association in CB379 has never been
tested again. Takeet et al. 2017, [DOI](https://doi.org/10.1515/ap-2017-0023), found minimal 18S
diversity among Nigerian *B. rossi* with one divergent sequence, and speculates about clinical
implications without testing them.

## 3. The genome

Redekar et al. 2025, [DOI](https://doi.org/10.1186/s12864-025-11495-z): first near-complete,
chromosome-level assembly of *B. rossi* strain PMB from a sick dog in Pietermaritzburg, South
Africa. 21.06 Mbp, five chromosome-level scaffolds plus an apicoplast scaffold and 54 unplaced
low-gene-density scaffolds, N50 1.32 Mb, 96.6% BUSCO apicomplexan completeness, 3,098
protein-coding genes, 71 tRNA, 16 rRNA, 6.4 Kbp mitochondrial genome. Two further field isolates
were assembled. Comparative analysis found four syntenic inversions and many polymorphisms, with
SNP and indel density higher in gene-poor regions; 99% of orthologous gene sets conserved across the
three isolates; about 76% of PMB protein-coding genes shared with four other *Babesia* species.

Implications I used in the memo: a reference exists, so reference-based variant calling is possible;
3,098 genes sets the natural denominator for a gene-based test; only three isolates are assembled,
so population structure and gene-family repertoire in the field are unknown.

## 4. Analogous designs borrowed from malaria and *B. bovis*

- Selective whole genome amplification (sWGA) to get parasite sequence out of blood with host DNA
  dominating and low parasitaemia: Girgis et al. 2025 for *P. malariae*/*P. ovale*,
  [DOI](https://doi.org/10.1186/s12864-025-11292-8); Joste et al. 2022 for *P. ovale*,
  [DOI](https://doi.org/10.1128/spectrum.00726-22). Both show the method works on clinical samples
  with no culture available — the same constraint *B. rossi* has.
- Large open parasite variation resources and sWGA-based genotyping at scale: MalariaGEN Pf7,
  [DOI](https://doi.org/10.12688/wellcomeopenres.18681.1).
- Mixed-clone infections: Fogang et al. 2025, [DOI](https://doi.org/10.1099/mgen.0.001386), compared
  MOI estimators (incl. THE REAL McCOIL, runs-of-homozygosity) against amplicon sequencing in 65
  severe paediatric malaria cases, found amplicon sequencing more sensitive than WGS-based MOI, and
  found clearance rate was **not** associated with MOI. It also found genotypes appearing 16 h after
  treatment started in 60.9% of participants — strong argument for sampling strictly before
  treatment and for not relying on one sample.
- Genome-wide scans for selection in field *P. falciparum* isolates: Amambua-Ngwa style design in
  Ghana, [DOI](https://doi.org/10.3389/fcimb.2021.630797); drug-resistance and selection surveillance
  in Mozambique, [DOI](https://doi.org/10.1128/mbio.01768-23). These are the template for the
  analysis pipeline (WGS of field isolates, filtering, structure, scan).
- Variant surface antigen gene families and virulence in a *Babesia*: Lau et al. 2011,
  [DOI](https://doi.org/10.1186/1471-2164-12-410) — attenuation of *B. bovis* reduced genome
  diversity overall and reduced *ves* multigene family diversity; no single consistent amino-acid
  change explained attenuation. This is the direct precedent for (a) testing gene families with a
  burden/diversity test rather than single SNPs, and (b) expecting no single causal variant.
- Example of covariate-adjusted genotype-outcome regression in a malaria setting (host side, but the
  analysis shape is what I copied): Kisia et al. 2019,
  [DOI](https://doi.org/10.1186/s12881-019-0866-z).

## 5. Covariate measurement — why these three

- **Parasite load.** Böhm et al. 2006, [DOI](https://doi.org/10.1016/j.vetpar.2006.05.002), 100
  naturally infected *B. rossi* dogs, 10 died: capillary and venous parasitaemia were both higher in
  dogs that died (P=0.002 vs recovered-after-hospitalisation, P<0.0001 vs outpatients); capillary
  median 0.61% (IQR 0.22-3.75%) was higher than venous median 0.14% (IQR 0.046-0.52%), P<0.0001.
  Therefore: measure load on a **capillary** smear, and also by qPCR, and log-transform it. Note the
  package rule: SV-02a found no *B. rossi* unit reporting load against a clinical outcome reaching
  three independent units, so load remains a covariate here, not an established effect.
- **Days sick.** SV-03's definition map found illness duration exists in only one dataset (DS05) and
  there without an outcome. It must be collected prospectively with a fixed question.
- **Age.** SV-05 found, in S-CB050 (Onderstepoort, *B. rossi*, 140 dogs, 15 deaths, where "died"
  includes euthanasia for poor prognosis), an age OR for death of 1.23 (0.34 to 4.15), with only
  OR >= 3.7 detectable at that size. So age is a confounder that nobody has estimated usefully;
  adjust for it, do not claim to have estimated it.
- Infectious dose shapes the early inflammatory response in experimental *B. rossi*
  (Atkinson et al. 2022, [DOI](https://doi.org/10.1016/j.vetpar.2022.109717)), which supports load
  and days sick being on the causal path rather than simple nuisance terms — hence the pre-specified
  decision to report both adjusted and unadjusted estimates.

## 6. Recommended assumptions for the power script

### Design A (targeted BrEMA1 replication)

| Assumption | Recommended value | Why |
|---|---|---|
| Exposure definition | genotype19 alone vs all others (primary); secondary: "long repeat" class, >= 19 repeats | the CB379 four-genotype group covers 90.1%, which leaves no contrast |
| Exposure frequency in controls | 0.35 (sensitivity 0.25 and 0.45) | genotype19 was 36.2% of typed parasites in CB379 |
| Primary outcome | complicated disease (composite, pre-specified) | death alone is too rare at this size |
| Outcome proportion, complicated | 0.40 (sensitivity 0.30 and 0.50) | Onderstepoort case mix; keep wide |
| Secondary outcome | death including euthanasia for poor prognosis | matches S-CB050 and SV-03's commonest outcome |
| Outcome proportion, death | 0.12 (sensitivity 0.08 and 0.15) | 15/140 in S-CB050; 10/100 in Böhm 2006 |
| Target OR to detect | 2.5 primary; also tabulate 2.0, 3.0, 4.0 | smaller than the only comparable published canine effect sizes, and still clinically meaningful |
| Alpha | 0.05, two-sided | one pre-registered primary test |
| Power | 0.80 and 0.90 | tabulate both |
| Covariate inflation | multiply n by 1/(1 - R^2), R^2 = 0.20 between exposure and {age, log days sick, log load} | standard variance-inflation allowance for three covariates |
| Non-evaluable allowance | add 15% (failed amplification, mixed genotype excluded from primary, loss to follow-up) | mixed infections are common in the region |
| Analysis | Firth-penalised logistic regression; exact logistic as sensitivity | small cell counts and likely separation in rare genotypes |

Indicative scale, which the power script should confirm: an unmatched case-control contrast with
control exposure 0.35 and OR 2.5 at 80% power needs on the order of 150-180 dogs per outcome group,
so roughly 350 to 450 enrolled after inflation; death as the primary outcome would need a cohort in
the high hundreds to low thousands, which is why complicated disease is the primary.

### Design B (genome-wide parasite association)

| Assumption | Recommended value | Why |
|---|---|---|
| Genes tested | 3,098 protein-coding genes | the PMB annotation, [DOI](https://doi.org/10.1186/s12864-025-11495-z) |
| Gene-based alpha | 0.05 / 3098 = 1.6e-5 | Bonferroni over genes for the burden test |
| Common SNPs after filtering (MAF >= 0.05, call rate >= 0.9) | assume 30,000 (range 15,000-60,000) | 21 Mbp genome, SNP-dense gene deserts excluded |
| SNP-level alpha | 0.05 / 30,000 = 1.7e-6 | Bonferroni; report permutation-based threshold too |
| Secondary family-level test | the BrEMA1 / variant antigen families as a pre-declared set, alpha 0.05/number of families | *B. bovis* precedent, [DOI](https://doi.org/10.1186/1471-2164-12-410) |
| Detectable effect at n = 400 | only OR >= 3 at MAF >= 0.15 | state this plainly; Design B is hypothesis-generating |
| Monoclonal subset for the primary scan | expect 50-70% of isolates | mixed infections; MOI estimated as in [DOI](https://doi.org/10.1099/mgen.0.001386) |

## 7. Things I could not establish

- No 2x2 table from CB379 (full text not retrievable; PMC body empty). All genotype-by-outcome
  counts in the memo are percentages of isolates, not outcome-stratified counts.
- No published *B. rossi* BrEMA1 genotype frequencies from a non-Onderstepoort South African
  cohort — SV-03's requirement for a second site cannot be met from the literature, only by
  recruiting one.
- No published estimate of *B. rossi* MOI in natural canine infection.
- GenBank accessions for the CB379 BrEMA1 sequences were not verified.
