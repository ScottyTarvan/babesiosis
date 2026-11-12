# Design memo: does the parasite's genotype change the outcome in *Babesia rossi*?

SV-10 design memo. Draft, 2026-11-12. Literature facts are from PubMed; each carries a DOI link.

## 1 Question and why now

Dogs with *B. rossi* babesiosis do not all get the same disease. Some recover as outpatients. Some
die. We mostly look for the reason in the dog. One study looked for it in the parasite.

The question: **does the genotype of the infecting *B. rossi* parasite predict severe disease or
death, once we allow for the dog's age, how long it has been sick, and how many parasites it
carries?**

Two things make now the right time. First, the one study that reported such a link, CB379
(Matjila et al. 2009, [DOI](https://doi.org/10.1128/jcm.01110-08)), has never been repeated. The only
follow-up work looked for the gene in Nigeria and did not find it at all
([DOI](https://doi.org/10.1186/1756-3305-7-119)). Second, there is now a near-complete *B. rossi*
genome ([DOI](https://doi.org/10.1186/s12864-025-11495-z)), so we are no longer limited to one gene.

## 2 What is known

CB379 collected 141 blood samples from infected dogs: 121 at the Onderstepoort Veterinary Academic
Hospital and 20 from private clinics in several parts of South Africa. Diagnosis was by thin blood
smear. The authors amplified and sequenced the hexapeptide-repeat region of the BrEMA1 gene. Gel
electrophoresis gave 11 profiles. Sequencing resolved 12 genotypes, with 6 to 31 repeats, named
genotype6 to genotype31. Four genotypes dominated: genotype19 at 36.2%, genotype28 and genotype29 at
20.6% each, and genotype11 at 12.7%. Those four were also the ones linked to the poorest prognosis.
Clinical presentation was grouped as uncomplicated (good prognosis) or complicated (poor prognosis),
and the comparison with clinical records was retrospective.

The limits matter more than the finding. The published abstract gives no table of dogs by genotype
and outcome, no statistical test, and no effect size. The four "virulent" genotypes together make up
90.1% of isolates, so almost every dog carried one; a frequency effect and a virulence effect cannot
be separated. There was no adjustment for host age, treatment delay or parasite load, and most dogs
were hospital cases. The authors themselves call it preliminary.

The genome is new ground. The PMB strain assembly, from a sick dog in Pietermaritzburg, is 21.06 Mbp
across five chromosome-level scaffolds plus an apicoplast scaffold and 54 unplaced scaffolds, N50
1.32 Mb, 96.6% BUSCO completeness, with 3,098 protein-coding genes. Two more field isolates were
assembled; they share 99% of orthologous gene sets, differ by four syntenic inversions, and carry
most of their SNPs in gene-poor regions ([DOI](https://doi.org/10.1186/s12864-025-11495-z)).

## 3 Design A: targeted BrEMA1 replication

**Setting.** Two sites, enrolling in parallel. One is Onderstepoort, so the result is comparable with
the original. The second must be a different hospital, in a different part of South Africa. This is
not optional: every replicated *B. rossi* signal in this review comes from Onderstepoort, so a
single-site result would add nothing about generalisability.

**Eligibility.** Client-owned dogs with a first episode of babesiosis, large *Babesia* on a capillary
smear, and *B. rossi* confirmed by species-specific PCR. Excluded: dogs already given an antibabesial
drug for this episode, mixed *Babesia* species infections, and owners who decline follow-up.

**Sampling.** One EDTA blood sample taken **before the first antibabesial dose**. This is strict.
In malaria, genotypes undetectable at admission appeared in the blood 16 hours after treatment began
in 61% of patients ([DOI](https://doi.org/10.1099/mgen.0.001386)); a post-treatment sample would
genotype a different parasite population from the one that caused the presentation.

**Genotyping.** PCR of the BrEMA1 hexapeptide-repeat region as in CB379, followed by **amplicon deep
sequencing** rather than Sanger sequencing. Sanger reads the dominant clone only. Amplicon
sequencing detects minority clones, and in malaria it detected mixed infections that whole-genome
methods missed ([DOI](https://doi.org/10.1099/mgen.0.001386)).

**Mixed genotypes.** Declare the rule in advance. Primary analysis: the dominant genotype, defined as
the one with the highest read fraction when it exceeds 70% of reads. Dogs with no genotype above 70%
are a separate "mixed" category, analysed as its own exposure level, never silently dropped. Report
how many dogs fall in each class.

**Outcome.** Primary: complicated disease, defined before recruitment by a fixed list of organ
complications recorded at or during admission. Secondary: death, which at Onderstepoort includes
euthanasia for poor prognosis and must be reported that way, because a euthanasia decision is partly
a clinical judgement and partly an owner's. Outcomes are assessed by a clinician blind to genotype.

**Covariates and how each is measured.**
- *Age*: years, from the owner's record, entered as a continuous term plus a spline. The only
  comparable published estimate is imprecise (OR for death 1.23, 0.34 to 4.15, in a 140-dog
  Onderstepoort cohort), so age enters as a confounder, not as a result.
- *Days sick*: whole days from the owner first noticing illness to presentation, asked with one fixed
  question at enrolment. This has to be collected prospectively; it exists in only one dataset in
  this review, and there without an outcome.
- *Parasite load*: percent parasitised red cells counted on a **capillary** smear by a blinded
  observer, plus a *B. rossi* qPCR copy number. Capillary parasitaemia is higher than venous and is
  associated with death ([DOI](https://doi.org/10.1016/j.vetpar.2006.05.002)). Analysed as log load.

**Analysis.** Pre-registered before enrolment closes, with a fixed primary model. Logistic regression
of outcome on genotype class, adjusted for age, log days sick and log load, fitted with **Firth
penalisation**, because rare genotypes will produce small or empty cells and ordinary maximum
likelihood will break down. Exact logistic regression as a sensitivity analysis. Site is a fixed
effect; a site-by-genotype interaction is reported but is not the primary test. Report adjusted and
unadjusted odds ratios side by side with 95% confidence intervals, and say plainly if the interval
includes 1. No model selection, no stepwise, no prediction.

## 4 Design B: genome-wide parasite association

Design A tests one gene chosen in 2009. Design B asks the genome.

**Material.** The same pre-treatment blood samples. No *B. rossi* culture exists, host DNA dominates,
and parasitaemia is often below 1%, so parasite DNA must be enriched. Use **selective whole genome
amplification** with primer sets designed against the *B. rossi* reference; the method was built for
exactly this problem in neglected malaria species
([DOI](https://doi.org/10.1186/s12864-025-11292-8), [DOI](https://doi.org/10.1128/spectrum.00726-22)).
Dogs with higher parasitaemia go to direct whole-genome sequencing; low-parasitaemia dogs get a
targeted amplicon panel covering the candidate genes and a structure-marker set, so they are not lost
from the study.

**Calling.** Map to the PMB reference ([DOI](https://doi.org/10.1186/s12864-025-11495-z)), call
variants haploid, since the blood stage is haploid. Filter on depth, call rate and mapping quality,
and exclude the low-gene-density unplaced scaffolds from the primary scan.

**Mixed infection.** Estimate multiplicity of infection per isolate with at least two methods — a
within-sample allele-frequency method and runs of homozygosity — and cross-check against the amplicon
data ([DOI](https://doi.org/10.1099/mgen.0.001386)). The primary scan uses monoclonal isolates. Mixed
isolates are analysed separately, with the dominant haplotype, as a sensitivity analysis.

**Structure.** Compute principal components from genome-wide variants and include the leading
components in every model, so that a parasite subpopulation that happens to circulate near one
hospital is not mistaken for a virulence effect. Report the structure itself: nobody has described
*B. rossi* population structure in the field.

**Tests.** Two pre-declared layers. A single-variant scan across common variants, and a gene-based
burden test that aggregates rare variants within each of the 3,098 annotated genes. A third,
pre-declared, family-level test treats BrEMA1 and other variant antigen gene families as units and
tests diversity and copy number, because in *B. bovis* attenuation showed up as reduced diversity
across the *ves* family rather than as one causal amino-acid change
([DOI](https://doi.org/10.1186/1471-2164-12-410)). All models carry the same host covariates as
Design A.

**Threshold.** Bonferroni across genes for the burden test and across common variants for the
single-variant scan, with a permutation threshold reported alongside. Exact numbers are in the
research notes; they follow from the 3,098-gene annotation and the variant count after filtering.

## 5 Sample size

Normal approximations from `scripts/power.py`, two-sided alpha 0.05, power 0.8. Assumptions: genotype19 in 35% of uncomplicated
infections (sensitivity 25% and 45%); complicated disease in 40% of enrolled dogs (1.5 uncomplicated per complicated); R² 0.20 between
genotype and the covariates (age, log days sick, log load), so n is multiplied by 1 / 0.8; 15% added to the cohort for failed
amplification, mixed genotypes and loss to follow-up. Design B thresholds: 0.05 / 3,098 genes = 1.6e-5 for the burden test, and
0.05 / 30,000 common SNPs = 1.7e-6 for the single-variant scan; Design B also assumes that 60% of infections are monoclonal.

SAMPLE_SIZE_TABLE

**Recommendation.** Design A with genotype19 against all others, OR 2.5: **80 complicated and 120 uncomplicated dogs (199), from a
cohort of about 229 enrolled dogs**. Death as the outcome needs about 545 enrolled dogs for the same OR, so death is secondary; it
becomes reachable inside the 610-dog cohort of memo 3. Design B in the same 610 dogs can detect only large effects (OR of about 5 for a
gene with a carrier frequency of 0.15 to 0.5): it is hypothesis-generating, not a test.

## 6 Bias and confounders

- **Referral bias.** Both sites are referral centres, so complications will be common. That limits
  who the result applies to.
- **Treatment delay.** Days sick is both a confounder and part of the causal path. Report adjusted
  and unadjusted estimates.
- **Parasite population structure.** Handled in Design B; in Design A, site is the crude proxy.
- **Mixed infections** can make a dog look like it carries the dominant genotype only.
- **Euthanasia.** Where "died" includes euthanasia for poor prognosis, owner finances and clinician
  judgement enter the outcome. Report the two components separately as well as combined.
- **Blinding.** Genotype must not be known to the clinician recording the outcome, and the smear
  counter must not know the genotype or the outcome.
- **Survivor sampling.** A dog that dies before a pre-treatment sample is taken never enters. Count
  those dogs.

## 7 What it cannot show

It cannot show that a genotype *causes* severe disease. It is an observational association in
naturally infected dogs, and the parasite genotype travels with the tick, the place and the season.
It cannot separate a frequency effect from a virulence effect if the commonest genotype is again the
one linked to bad outcomes — which is why the exposure must be re-defined before data collection, not
after. It cannot support a predictive model or a risk score, and the genotype groups it finds are not
subtypes of disease. Design B at a realistic size is hypothesis-generating: it can nominate genes,
not confirm them. Confirmation would need a second, independent cohort, and ultimately a functional
experiment.

## 8 Open questions

1. Is a second, non-Onderstepoort South African site with enough *B. rossi* caseload willing and able
   to recruit prospectively?
2. What is the real multiplicity of infection in natural canine *B. rossi* infection? Nobody has
   measured it, and it drives the usable sample size in Design B.
3. Does BrEMA1 repeat number vary within one dog over the course of an infection?
4. Can sWGA primer sets designed against *B. rossi* reach usable coverage at 0.1% parasitaemia?
5. Should the primary exposure be genotype identity or repeat number as a continuous trend?
6. Are the CB379 BrEMA1 sequences in GenBank? If so, the 2009 and new genotypes can be aligned
   directly rather than matched by repeat count.
