# Research notes: within-breed host-genetics design (SV-10)

Written 2026-11-12 for `../memo_host_genetics.md`. Sources: PubMed (via the PubMed tool), local appraisal notes in `/core/articles/`, and one breed count from `/core/data/raw/DS05/` (read only, not changed). No full text was quoted.

## 1. PubMed search log

All searches run 2026-11-12, no date limit. "Screened" means title and abstract read. "New" means not already screened in an earlier row.

| # | Query (PubMed syntax as sent) | Hits | Screened | Relevant PMIDs |
|---|---|---|---|---|
| Q1 | `Babesia AND (dog OR dogs OR canine) AND (genetic OR polymorphism OR SNP OR genome-wide OR DLA OR MHC OR breed OR heritability OR heritable)` | 742 | 0 one by one (see note) | superseded by Q2 |
| Q2 | `Babesia[tiab] AND (dog[tiab] OR dogs[tiab] OR canine[tiab]) AND (breed[tiab] OR breeds[tiab] OR DLA[tiab] OR MHC[tiab] OR "host genetic"[tiab] OR "host genetics"[tiab] OR heritability[tiab] OR "genome-wide"[tiab] OR "single nucleotide polymorphism"[tiab] OR "blood type"[tiab] OR "blood group"[tiab] OR "erythrocyte antigen"[tiab] OR susceptibility[tiab] OR predisposition[tiab] OR predisposed[tiab])` | 123 | 123 | 41291669, 27796108, 21489239, 16715235, 3705420, 9683901, 38735268, 40303684, 15188810, 23994336, 17970851, 11829262, 31334887, 41600682, 35327127, 19271995, 15353837, 41463922 |
| Q3 | `"Babesia gibsoni" AND breed` | 47 | 47 (10 new) | none new |
| Q4 | `("Babesia canis" OR "Babesia rossi" OR "Babesia vogeli") AND (breed predisposition OR breed OR predisposed)` | 80 | 80 (14 new) | none new |
| Q5 | `canine babesiosis susceptibility` | 29 | 29 (16 new) | 21985148 |
| Q6 | `("dog leukocyte antigen" OR DLA-DRB1 OR "DLA class II" OR "major histocompatibility complex") AND (dog OR dogs OR canine) AND (Babesia OR Ehrlichia OR Anaplasma OR Hepatozoon OR Leishmania OR Trypanosoma OR "vector-borne")` | 13 | 13 | 12715244, 29704945 (both Leishmania) |
| Q7 | `(dog OR dogs OR canine) AND ("genome-wide association" OR GWAS OR "candidate gene" OR "gene polymorphism" OR SNP) AND (Babesia OR Ehrlichia OR Anaplasma OR Hepatozoon OR Leishmania OR Trypanosoma OR babesiosis OR ehrlichiosis OR leishmaniasis OR leishmaniosis)` | 22 | 22 | 22558142, 26348501, 27736777, 29742167, 33152678, 31079826, 18307968, 27655108, 38570155, 28987807 |
| Q8 | `(dog OR dogs OR canine) AND haptoglobin AND (polymorphism OR genotype OR allele OR phenotype)` | 13 | 13 | 1955840, 8328222, 9807725 (typing only, no infection) |
| Q9 | `Babesia AND (dog OR dogs OR canine) AND ("gene expression" OR transcriptome OR transcriptomic OR RNA-seq OR microarray) AND host` | 4 | 4 | 34399690 |
| Q10 | `(dog OR dogs OR canine) AND ("high potassium" OR "HK erythrocytes" OR "HK red cells") AND (inherited OR breed OR Babesia)` | 12 | 12 | 16539007, 20929429, 14740901, 1646472, 25792769, 24405428 |
| Q11 | `("dog erythrocyte antigen" OR "DEA 1") AND (prevalence OR frequency) AND (breed OR breeds) AND (Africa OR Europe OR Labrador OR "German shepherd" OR Boerboel OR "pit bull")` | 13 | 13 | 12240769, 21554361, 29147599, 32375793, 39330828, 41291669, 27796108 |
| Q12 | `(dog OR dogs OR canine) AND (cytokine OR TNF OR IL-10 OR IL-6 OR TLR4) AND ("gene polymorphism" OR "promoter polymorphism" OR SNP) AND (infection OR sepsis OR parasite)` | 6 | 6 | 19254251, 25266752 (method precedents; not Babesia) |
| Q13 | `(Babesia OR babesiosis) AND (dog OR dogs OR canine) AND ("genetic susceptibility" OR "genetic resistance" OR "genetic predisposition" OR "genetic background" OR "innate resistance" OR "dog leukocyte antigen" OR "erythrocyte potassium")` | 3 | 3 (0 new) | 21985148, 16715235 |
| L1-L4 | Known-item lookups: DOI 10.1645/GE-2036.1; Karlsson 2007; Lindblad-Toh 2005; Wilbe 2010; Tengvall 2013 | 1 each | 5 | 20929429, 17906626, 16341006, 20101241, 23671420 |

**Totals.** Q2 to Q13: 365 hits, 280 unique records screened by title and abstract. About 41 were relevant to host genetics, breed or method. Plus 5 known-item records.

**Note on Q1.** Q1 has 742 hits because "genetic" and "polymorphism" match parasite genotyping (18S, cytb, BrEMA1). I did not screen its 742 records one by one. Q2 is the same idea restricted to title/abstract and to host-side terms. Q3 to Q5 and Q13 catch breed and susceptibility papers that Q2 might miss. They added one key record (21985148). So the Q1 gap is unlikely to hide a canine host-genotype study of babesiosis, but it is not proven. A reviewer who needs a full Q1 screen should run it.

**Local sources not found by PubMed queries.** CB125 (gonadectomy and severity, Onderstepoort) is in the local appraisal notes. It did not match Q2 because the abstract uses "breed category" with no other host-genetic term.

## 2. What exists: canine host-genetic work on babesiosis

**No study has genotyped dogs for any locus against babesiosis severity or outcome.** The closest items:

| Study | What it did | Relevance |
|---|---|---|
| Adebayo 2025, CB143 ([doi](https://doi.org/10.1186/s12917-025-05117-9)) | DEA 1 typing (card test) in 200 suspect dogs, Nigeria; PCR positivity 63.0% DEA 1+ vs 60.3% DEA 1-. | Infection only. No severity, no species, breed confounded. |
| Dhliwayo 2016 ([doi](https://doi.org/10.4102/jsava.v87i1.1409)) | DEA 1.1 in 100 rural Zimbabwean dogs; Babesia PCR in 58 (6.9% positive); no association. | Infection only, tiny. |
| Yamasaki 2005 ([doi](https://doi.org/10.1645/GE-509R.1)); Yamasaki 2009 ([doi](https://doi.org/10.1645/GE-2036.1)); Yamasaki 2003 ([doi](https://doi.org/10.1645/GE-86R)) | In vitro: B. gibsoni multiplies well in inherited high-K (HK) red cells; HK cells change drug effects. | Red cell trait. In vitro only, B. gibsoni only. |
| Maede 1991 ([doi](https://doi.org/10.1016/0034-5288(91)90067-x)); Tanabe 2007 ([doi](https://doi.org/10.2183/pjab.82.375)) | HK red cells inherited; 11/24 Shiba, 0 of 79 dogs of 24 other breeds; mainly Japanese/East Asian dogs. | HK is near absent in European-derived breeds, so not useful for B. rossi in South Africa. |
| Mellanby 2011 ([doi](https://doi.org/10.1111/j.1939-1676.2011.00779.x)) | Onderstepoort 2004-2010: 1,222 cases, 11,484 non-infected; toy breeds lower odds of diagnosis vs Labrador; intact females lowest. | Breed and diagnosis, not severity. Authors raise genetics or exposure. |
| Reyers 1998 ([PubMed 9683901](https://pubmed.ncbi.nlm.nih.gov/9683901/), no DOI) | 662 hospitalised B. rossi cases; fighting breeds (bull terrier types) over-represented among non-survivors of the inflammatory, non-anaemic form. | Only breed-and-severity signal for B. rossi found. Old, abstract-level, no model. |
| Knobel 2024, CB125 ([doi](https://doi.org/10.1016/j.prevetmed.2024.106293)) | Onderstepoort 2013-2020; gonadectomy RR 0.72 for severe disease; adjusted for breed category and weight. | Host factor, not genetic. Must be a covariate. |
| Janjic 2024 ([doi](https://doi.org/10.1016/j.vetpar.2024.110197)) | 61 B. canis dogs; purebred had more band neutrophils than mixed breed. | Weak, lab values only. |
| Hornok 2006 ([doi](https://doi.org/10.1007/s00436-006-0218-8)) | B. canis seroprevalence higher in German shepherds and komondors, Hungary. | Seropositivity, exposure confounded. |
| Martinod 1986 ([doi](https://doi.org/10.1016/0304-4017(86)90072-5)) | France: some breeds called "more resistant", others "more susceptible". | Descriptive, no statistics in abstract. |
| Penzhorn 2011 ([doi](https://doi.org/10.1186/1756-3305-4-51)) | Argues B. rossi is virulent because dogs in SA are recently introduced breeds, not co-adapted. | Hypothesis only. |
| Atapattu 2023 ([doi](https://doi.org/10.1155/2023/9467314)) | Sri Lanka: clinical VBP disease more often in exotic breeds (German shepherd, Rottweiler) than local breeds. | Not species-specific for Babesia severity. |
| Smith 2021 ([doi](https://doi.org/10.1186/s12864-021-07889-4)) | Experimental B. rossi, 5 dogs, whole-blood RNA-seq over 8 days. | Gene expression, not genotype. Gives candidate pathways (haemolysis, interferon). |
| Ma 2025 ([doi](https://doi.org/10.3390/ani15243634)) | Miniature Schnauzer with PKLR (pyruvate kinase) truncation; haemolysis persisted after a haemoparasite infection. | Inherited red cell disease can mimic or worsen "severe babesiosis". Exclusion criterion. |

**B. gibsoni and pit bull types.** Many reports show B. gibsoni concentrated in American pit bull terriers and other fighting breeds: Macintire 2002 ([doi](https://doi.org/10.2460/javma.2002.220.325)), Jefferies 2007 ([doi](https://doi.org/10.1111/j.1751-0813.2007.00220.x)), Imre 2013 ([doi](https://doi.org/10.1016/j.ttbdis.2013.06.006)), Barash 2019 for B. vulpes ([doi](https://doi.org/10.1111/jvim.15560)), Davitkov 2025 ([doi](https://doi.org/10.3390/vetsci13010026)), Tosa dogs in Japan ([doi](https://doi.org/10.1292/jvms.66.893)). All tie this to bite transmission, not genetics. This shows why breed alone cannot separate exposure from genes.

**Many prevalence studies** (about 40 in Q2 to Q4) list breed as a risk factor for infection. Results go both ways (mixed breed higher in Hong Kong, local breed higher in India, no effect in Japan, Switzerland, Romania). None addresses severity.

## 3. Related canine vector-borne disease: host-genetic precedents (Leishmania)

| Study | Design | Result |
|---|---|---|
| Quinnell 2003 ([doi](https://doi.org/10.1007/s00251-003-0545-1)) | DLA class II sequence typing, Brazilian mongrel cohort | DLA-DRB1*01502 linked to higher IgG and parasite positivity |
| Soutter 2018 ([doi](https://doi.org/10.1016/j.tvjl.2018.03.001)) | DLA class II in experimentally infected Beagles | Limited DLA diversity; inconsistent association |
| Sanchez-Robert 2008 ([doi](https://doi.org/10.1051/vetres:2008013)) | SLC11A1, 164 dogs of 19 breeds | 2 of 24 polymorphisms linked to disease |
| Quilez 2012 ([doi](https://doi.org/10.1371/journal.pone.0035349)) | GWAS, 219 Boxers, ~170k SNPs | Heritability up to 60%; no genome-wide significant locus |
| Utsunomiya 2015 ([doi](https://doi.org/10.1371/journal.pone.0136749)) | GWAS, mixed-breed, 20 cases / 28 controls, 149,648 SNPs, mixed model | Two candidate loci (IL2RA/IL15RA region, TLE1) |
| Batista 2016 ([doi](https://doi.org/10.1128/IAI.00486-16)) | GWAS of immune phenotypes, 189 dogs, 110,165 SNPs | Loci for TNF-alpha and other responses |
| Soutter 2019 ([doi](https://doi.org/10.1016/j.vetpar.2019.04.011)) | Immune-gene SNP panel, 62 cases / 101 controls | CIITA SNP lost significance after multiple-testing correction |
| Sanz 2024 ([doi](https://doi.org/10.1016/j.ijpara.2024.03.006)) | 35,669 hospital dogs plus selection scans | Breed, weight, lifestyle linked to clinical stage |
| Necesankova 2016 ([doi](https://doi.org/10.1007/s11033-016-4078-8)) | Kenyan village dogs, candidate immune SNPs (MYD88, TLR4, DLA) vs several infections incl. Hepatozoon | MYD88/TLR4 SNPs linked to more than one infection |
| Review: 2017 ([doi](https://doi.org/10.1016/j.meegid.2017.10.005)) | Systematic review of genetics of canine leishmaniasis | Genetic work is scarce |

Lesson: infection-outcome GWAS in dogs with 50 to 220 animals has mostly given suggestive loci, not robust ones. Candidate-gene hits often fail after correction.

## 4. Candidate loci: evidence summary

| Candidate | Evidence for babesiosis | Evidence it varies in dogs | Practical note |
|---|---|---|---|
| DEA 1 | Infection only (CB143, Dhliwayo 2016); null | Breed-dependent: Onderstepoort 47% overall, mongrels 48%, German shepherd and Boxer <20%, Rottweiler, Great Dane >75% ([doi](https://doi.org/10.4102/jsava.v73i2.555)); Portugal 56.9% ([doi](https://doi.org/10.1111/j.1939-165X.2011.00311.x)); Italy 61.2% of 7,414 ([doi](https://doi.org/10.1155/2017/5914629)); Italy/Spain donors 42.8% ([doi](https://doi.org/10.1186/s12917-020-02351-1)); Angola 52.7% ([doi](https://doi.org/10.3390/vetsci11090449)); Nigeria Boerboel 73-86% (CB143) | Cheap card test. Note: card typing is serological; post-transfusion samples are invalid. Type before transfusion. |
| HK red cells | B. gibsoni grows well in HK cells (in vitro) | Asian breeds only | Not relevant to B. rossi in South Africa. Measure only if a cohort has Asian breeds. |
| Haptoglobin | Hp is an acute-phase protein measured as a marker in babesiosis (many local notes), never as a genotype | Two common electrophoretic phenotypes in German shepherd, Doberman and pit bull ([PubMed 1955840](https://pubmed.ncbi.nlm.nih.gov/1955840/)); HP genetic variants in race hounds ([doi](https://doi.org/10.1111/j.1439-0442.1993.tb00613.x)) | Canine HP has no known functional variant like human Hp1/Hp2. Genotype via SNP array or sequencing, not by phenotype (phenotype changes with disease). |
| Cytokine promoter SNPs (TNF, IL6, IL10, CXCL8, IL1B) | Cytokines track severity in B. rossi (CB037 [doi](https://doi.org/10.1111/pim.12630), CB517 [doi](https://doi.org/10.1371/journal.pone.0150113), S-CB050); no genotype data | TNFA SNP haplotypes exist; in German shepherds a TNFA signal was due to LD with DLA-DRB1 ([doi](https://doi.org/10.1111/j.1399-0039.2008.01188.x)) | Analyse TNFA jointly with DLA because of LD. |
| DLA class II (DRB1, DQA1, DQB1) | None | Within-breed diversity is low (Soutter 2018); associations seen for Leishmania (Quinnell 2003) | Sequence-based typing; expect few common haplotypes per breed. |
| TLR4, MYD88 | None | Village-dog associations with several infections | Optional extra candidates. |
| PKLR and other inherited haemolytic defects | Case report | Breed-specific | Exclusion, not exposure. |

## 5. Breed choice: which breed gives enough cases

**DS05 breed count** (my count from `/core/data/raw/DS05/BET Study Dataset.xlsx`, sheet 3, 150 B. rossi dogs, one South African clinic): crossbreed 90 (60%), pit bull 25 (17%), Boerboel 15 (10%), Rottweiler 5, greyhound 5, German shepherd 4, others 6. S-CB050 has no breed column.

**Throughput.** Mellanby 2011: 1,222 cases in about 6.5 years at one hospital, so about 190 per year. Reyers 1998: 31% of affected dogs were hospitalised as seriously ill. If pit bull types are about 17% of cases, one hospital sees about 30 pit bull cases a year, about 10 of them severe. These are rough, single-site, dated numbers. Re-count with current hospital records before planning.

**Recommendation: pit bull-type dogs with B. rossi in South Africa.**
- Most common named breed among B. rossi cases in DS05.
- The only breed-and-severity signal for B. rossi points at bull-terrier types (Reyers 1998).
- One parasite species in one region. B. rossi is the most virulent, so severe cases are common.
- Weakness: "pit bull" is owner-reported and not a closed registry breed in South Africa. Confirm membership by genotype (genetic relationship matrix clustering) and drop outliers.
- Back-up: Boerboel (10% of DS05; a South African breed, more closed). DEA 1 is probably mostly positive there (73-86% in Nigeria), so DEA 1 has little variance.
- Alternative: crossbreeds (60% of cases) with a mixed-model GWAS, as in Utsunomiya 2015. More cases, but more stratification and less LD.
- Europe (B. canis): no breed dominates case series (Maltese and crossbreeds in Romania, CB043 [doi](https://doi.org/10.1645/18-137); German shepherds in Hungary seroprevalence). Mortality is lower, so severe cases are fewer. Not recommended as the first site.

## 6. Recommended power assumptions (for the coordinator)

| Item | Value to use | Basis |
|---|---|---|
| Severe proportion among B. rossi cases | 0.30 (range 0.2-0.4) | Reyers 1998 (31% hospitalised as seriously ill); severity definitions differ |
| DEA 1 positive, controls, pit bull type | 0.50 (range 0.40-0.60) | Onderstepoort mongrels 48%, overall 47%; no pit bull-specific figure found |
| DEA 1 positive, Boerboel | 0.80 | CB143 Nigeria 73-86% |
| Candidate allele frequency (cytokine SNPs, HP) | 0.20 and 0.40 | Assumption; no canine within-breed data found |
| DLA-DRB1 haplotype carrier frequency | 0.15 to 0.30 for common haplotypes | Assumption; low within-breed diversity (Soutter 2018) |
| Plausible OR, candidate | 1.5, 2.0, 3.0 | DLA-DRB1/TNFA haplotype OR 3.7 and TNFA OR 2.5 in anal furunculosis (Barnes 2009); SV-05 shows OR < 3.7 is not detectable with 15 events |
| Number of candidate tests | 20 (DEA 1: 1; HP: 2; cytokine SNPs: 8; TLR4/MYD88: 2; DLA haplotypes: 7) | Bonferroni alpha 0.05/20 = 0.0025 |
| Genome-wide threshold | Bonferroni on SNPs after QC, about 5e-7 (0.05/~100k informative SNPs); or permutation genome-wide p < 0.05 | Tengvall 2013: raw p 3.1e-7 gave permutation genome-wide p 0.03 ([doi](https://doi.org/10.1371/journal.pgen.1003475)) |
| Array | ~220k canine SNP array (or CanineHD ~170k) | Within-breed LD is long, so 15k-170k SNPs suffice (Lindblad-Toh 2005 [doi](https://doi.org/10.1038/nature04338); Wilbe 2010) |
| Successful within-breed GWAS sizes | Mendelian: ~20 dogs (Karlsson 2007 [doi](https://doi.org/10.1038/ng.2007.10)). Complex: 81 cases / 57 controls, 5 loci (Wilbe 2010 [doi](https://doi.org/10.1038/ng.525)); 91 / 88, one locus (Tengvall 2013). Infection outcome: 219 Boxers, no genome-wide hit (Quilez 2012) | Suggests at least 150 severe and 150 mild for a complex infection trait; more if OR < 2 |
| Heritability scenario (optional) | 0.2 and 0.4 on liability scale | Quilez 2012 estimated up to 0.6 for Leishmania in Boxers; treat as an upper bound |

## 7. Bias notes for the memo

- Parasite load: genotype may act through load (mediator). Adjusting for load estimates only the part not through load. Load is also affected by days sick, parasite strain and treatment before arrival. Adjusting for it can open a collider path (genotype -> load <- strain -> severity). So: primary analysis without load; load-adjusted analysis as secondary, with strain and days sick also adjusted.
- Case-only sampling: only infected dogs that reach a hospital are studied. A locus that changes the chance of infection or of presentation can bias the severe-vs-mild contrast (index-event bias). Record referral route.
- Euthanasia for poor prognosis is in "died" (SV-05). Cost-driven euthanasia must be separated.
- Transfusion before sampling invalidates DEA typing and adds donor DNA to blood. Sample before transfusion, or use buccal swabs for DNA.
- Gonadectomy (CB125), sex, age, weight are host covariates.
