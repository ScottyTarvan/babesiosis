# Design memo (draft): within-breed host genetics of severe canine babesiosis

SV-10 draft, 2026-11-12. Research notes and PubMed search log: [research/host_genetics_notes.md](research/host_genetics_notes.md).

## 1. Question and why within-breed

**Question.** Among dogs of one breed infected with one Babesia species, do host gene variants differ between dogs that become severely ill and dogs that stay mild?

**Why within one breed.** Breed mixes genes with exposure. Pit bull types carry B. gibsoni far more often than other dogs, but the reports tie this to bites, not genes ([doi](https://doi.org/10.2460/javma.2002.220.325), [doi](https://doi.org/10.1111/j.1751-0813.2007.00220.x)). In our own data, breed also tracks weight and age (DS05, SV-05). A between-breed comparison cannot separate these. Within one breed, size, coat, use and lifestyle vary less. Linkage disequilibrium is also long within a breed, so fewer SNPs and fewer dogs are needed for a genome scan ([doi](https://doi.org/10.1038/nature04338), [doi](https://doi.org/10.1038/ng.525)).

**Why new data.** No existing public file can answer this. data.md says breed or host genetics against a hard outcome cannot be studied with what we hold. S-CB050 has 15 deaths and no breed. DS05 has breed but no outcome.

## 2. What is known

**PubMed search.** Thirteen queries plus five known-item lookups (log in the notes). The main title/abstract query gave 123 hits. Across queries, 280 unique records were screened by title and abstract. About 41 were relevant to breed, host genetics or method. One broad query (742 hits, mostly parasite genotyping) was not screened record by record.

**Canine host genetics of babesiosis: nothing on severity.** No study has genotyped dogs against babesiosis severity or outcome. What exists:

- **DEA 1 and infection.** Two studies typed DEA 1 and tested for Babesia DNA. Neither found an association with infection: Nigeria, 200 suspect dogs (CB143, [doi](https://doi.org/10.1186/s12917-025-05117-9)); Zimbabwe, 58 dogs ([doi](https://doi.org/10.4102/jsava.v87i1.1409)). Neither looked at severity. CB143 did not name the species and is confounded by breed.
- **Red cell traits.** Inherited high-potassium (HK) red cells support B. gibsoni growth in vitro ([doi](https://doi.org/10.1645/GE-509R.1), [doi](https://doi.org/10.1645/GE-2036.1)). HK cells occur in Japanese and East Asian dogs and were absent in 24 other breeds ([doi](https://doi.org/10.1016/0034-5288(91)90067-x)). So this trait does not help for B. rossi in South Africa.
- **Breed and diagnosis.** At Onderstepoort (1,222 cases), toy breeds had lower odds of a babesiosis diagnosis than Labradors ([doi](https://doi.org/10.1111/j.1939-1676.2011.00779.x)). The authors say this could be genes or exposure. Hungary: German shepherds had higher B. canis seroprevalence ([doi](https://doi.org/10.1007/s00436-006-0218-8)).
- **Breed and severity.** One old signal: in 662 hospitalised B. rossi cases, bull-terrier types were over-represented among non-survivors of the inflammatory, non-anaemic form ([PubMed 9683901](https://pubmed.ncbi.nlm.nih.gov/9683901/)). It is descriptive.
- **Non-genetic host factor.** Gonadectomy went with lower risk of severe disease (RR 0.72), adjusted for breed category and weight (CB125, [doi](https://doi.org/10.1016/j.prevetmed.2024.106293)). One hospital.
- **Gene expression, not genotype.** Five experimentally infected dogs showed haemolysis and interferon pathways in blood RNA ([doi](https://doi.org/10.1186/s12864-021-07889-4)).

**Precedent in another canine vector-borne disease.** Leishmania has the only canine infection-outcome genetics. DLA-DRB1 was linked to infection in mongrels ([doi](https://doi.org/10.1007/s00251-003-0545-1)) but not consistently in Beagles ([doi](https://doi.org/10.1016/j.tvjl.2018.03.001)). A Boxer GWAS (219 dogs, about 170k SNPs) estimated heritability up to 60% but found no genome-wide locus ([doi](https://doi.org/10.1371/journal.pone.0035349)). A mixed-breed scan of 20 cases and 28 controls gave suggestive loci only ([doi](https://doi.org/10.1371/journal.pone.0136749)). Lesson: 50 to 220 dogs gave hints, not firm loci.

**Which breed gives enough cases.** In DS05 (150 B. rossi dogs, one South African clinic) the counts were: crossbreed 90, pit bull 25, Boerboel 15, and no other breed above 5. Pit bull types are the most common named breed. One hospital diagnosed about 190 cases a year (2004-2010), and about 31% of affected dogs were hospitalised as seriously ill in an older series. So one hospital may see about 10 severe pit bull cases a year. These numbers are old and from single sites. Re-count before planning. European B. canis series show no dominant breed (CB043: Maltese and crossbreeds, [doi](https://doi.org/10.1645/18-137)), and severe cases are fewer.

**Recommended breed: pit bull-type dogs with B. rossi in South Africa.** Back-up: Boerboel. Fallback: crossbreeds with a mixed model.

**Candidates and their evidence.**

| Candidate | Evidence for babesiosis | Varies in the breed? |
|---|---|---|
| DEA 1 | Infection only, null | About half of Onderstepoort mongrels are positive (48%) ([doi](https://doi.org/10.4102/jsava.v73i2.555)); Boerboels mostly positive (CB143) |
| Haptoglobin | Measured as a marker only | Two common phenotypes in pit bulls and other breeds ([PubMed 1955840](https://pubmed.ncbi.nlm.nih.gov/1955840/)); no known functional variant |
| Cytokine promoter SNPs (TNF, IL6, IL10, CXCL8, IL1B) | Cytokine levels track severity (CB037 [doi](https://doi.org/10.1111/pim.12630), CB517 [doi](https://doi.org/10.1371/journal.pone.0150113)); no genotypes | TNFA haplotypes exist but are in LD with DLA ([doi](https://doi.org/10.1111/j.1399-0039.2008.01188.x)) |
| DLA class II | None | Low diversity within breeds |
| TLR4, MYD88 | None | Linked to several infections in Kenyan village dogs ([doi](https://doi.org/10.1007/s11033-016-4078-8)) |

## 3. Design

**Frame.** A within-breed case-control study nested in a prospective multi-centre cohort. Enrol every pit bull-type dog with B. rossi confirmed by PCR, at three or more South African hospitals, over two or more seasons. Record breed by owner and confirm it by genotype.

**Case: severe.** Any one of: death or euthanasia for poor prognosis within 7 days; collapse at admission; neurological signs; acute kidney injury; ARDS; hypoglycaemia; persistent hyperlactataemia; secondary IMHA. Record euthanasia for cost separately. Lock the list before enrolment.

**Control: mild.** Same breed, same parasite, same hospital and season. Outpatient treatment, no complication, recovered at day 7 recheck. Dogs in between are kept in the cohort but not genotyped in the first round. This sharpens the contrast, but it can inflate the odds ratios.

**Matching.** Match on hospital and month. Match on age band and days sick before arrival, or adjust for them. Puppies form a separate stratum.

**Exposure measurement.**
- DEA 1 by card test, before any transfusion.
- DNA from blood taken before transfusion, or from a buccal swab.
- Candidate genotyping: haptoglobin and cytokine promoter SNPs by targeted assay; DLA-DRB1, DQA1 and DQB1 by sequence-based typing.
- Genome-wide: a canine SNP array of about 220k markers.

**Covariates.** Sex, neuter status, age, weight, days sick, treatment before arrival, coinfection (Ehrlichia), referral route, and parasite genotype where typed.

**Analysis.**
- Candidate loci: conditional logistic regression, with a Bonferroni-corrected threshold.
- GWAS: a linear mixed model with a genomic relationship matrix (for example GEMMA). Check genomic inflation. Drop dogs that do not cluster with the breed.
- DLA and TNFA are analysed together, because of LD.
- No predictive model. No polygenic score for prediction. No clustering into "subtypes".

**Parasite load.** Load may lie on the path from genotype to severity. Load is also shaped by days sick, parasite strain and earlier treatment. If we adjust for load, we can open a collider path and create a false genotype effect. So the primary analysis does not adjust for load. A secondary analysis adjusts for load together with days sick and parasite strain. We report both.

## 4. Sample size

Normal approximations from `scripts/power.py`, two-sided, power 0.8, 1 mild per severe dog, matched within pit bull-type dogs.
Candidates: 20 tests (DEA 1: 1, haptoglobin: 2, cytokine SNPs: 8, TLR4/MYD88: 2, DLA haplotypes: 7), alpha 0.05 / 20 = 0.0025;
R² 0.10 with age and days sick; times 1.15 for relatedness in the mixed model. GWAS: allelic test, alpha 5e-7 (Bonferroni on about
100,000 SNPs after quality control), times 1.15. Severe disease in 30% of pit bull-type cases (range 0.2 to 0.4).

SAMPLE_SIZE_TABLE

**Recommendation.** Plan for the candidate stage with DEA 1 at 50% in mild dogs and OR 3: **142 severe and 142 mild pit bull-type
dogs (283), from about 471 enrolled pit bull-type cases**. At about 10 severe pit bull-type cases per hospital per year, that is about
14 hospital-years (for example 5 hospitals for 3 years). The same 300 dogs on a SNP array detect only an allelic OR of about 3 (138 to
162 per group needed), which matches the size of successful within-breed canine GWAS of complex traits. An OR of 2 needs 330 to 500
severe dogs (about 35 to 50 hospital-years), and an OR of 1.5 needs more than 900 severe dogs: not feasible in one breed. A null result
at this size rules out only large effects. The 610-dog mixed-breed cohort of memo 3 gives only about 30 severe pit bull-type dogs, so
this study needs its own breed-focused enrolment; the protocol, outcome set and samples are shared with memo 3.

## 5. Bias and confounders

- **Exposure within breed.** Fighting and dog bites spread B. gibsoni in pit bulls. For B. rossi, tick exposure and lifestyle still vary. Record housing, tick control and bite scars.
- **Stratification.** Pit bull types are not a closed breed in South Africa. The mixed model handles relatedness, but hidden sub-populations can still mislead. Check by hospital.
- **Selection.** Only infected dogs that reach a hospital are studied. A gene that changes the chance of infection or of being brought in can bias the severe-against-mild contrast. Record the referral route.
- **Outcome.** Death includes euthanasia (as in S-CB050). Owner finances drive some euthanasia. Separate it.
- **Single-site signals.** SV-03 found that every replicated B. rossi signal comes from one hospital. This design needs several hospitals so that it does not repeat that problem.
- **Transfusion.** Donor cells change DEA typing and add donor DNA. Sample before transfusion.
- **Inherited red cell disease.** A dog with pyruvate kinase deficiency can look like severe babesiosis ([doi](https://doi.org/10.3390/ani15243634)). Exclude dogs with persistent haemolysis after cure.
- **Multiple testing.** Fix the candidate list before analysis.

## 6. What it cannot show

- It cannot show cause. An associated SNP marks a region. Function needs other work.
- It cannot speak for other breeds or other Babesia species.
- It cannot separate host effects from parasite-strain effects unless the parasite is typed too.
- It cannot give a clinical test. The sample is too small for prediction.
- A null result at about 150 cases rules out only large effects.
- Associations found in a sample enriched for extremes overstate the odds ratio.

## 7. Open questions

1. Can partner hospitals give current breed counts for B. rossi cases? The DS05 and Mellanby figures are old or from one site.
2. Is pit bull type genetically coherent enough in South Africa? A pilot of about 50 genotyped dogs would show this.
3. Should the outcome set use a published severity score, or our own list?
4. Is DEA 1 worth typing in Boerboels, where most dogs are positive?
5. Should parasite genotype (see the sister memo on parasite genotype) be measured in the same dogs? That would let us look at host and parasite together.
6. Ethics and owner consent for storing DNA and sharing genotypes.
7. Load adjustment. This memo does not adjust for load in the primary analysis, because load may lie between host genotype and severity; memo 1 does adjust for load, because there the question is damage at a given parasite genotype and load. The package agent accepted this split (SV-10 report, deviation D3); the user may prefer one rule for both.
