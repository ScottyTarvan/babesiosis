"""SV-10 sample sizes for the three design memos.

Standard library only (statistics.NormalDist). Normal-approximation formulas, no random numbers.
Writes out/power.csv (every scenario) and out/power.json (the same rows grouped by memo, plus the calibration check).

Formulas
- Case-control, binary exposure (Fleiss, uncorrected; Schlesselman):
    p1 = OR p0 / (1 + p0 (OR - 1))
    n_cases = [z_a sqrt((1 + 1/k) pbar (1 - pbar)) + z_b sqrt(p1 (1 - p1) + p0 (1 - p0) / k)]^2 / (p1 - p0)^2
  with k controls per case and pbar = (p1 + k p0) / (1 + k).
- Adjustment for covariates (age, days sick, load): variance inflation 1 / (1 - R2) (Hsieh, Bloch & Larsen 1998),
  R2 = squared multiple correlation of the exposure with the covariates.
- Allelic test (host genetics, diploid): the case-control formula on alleles (2 alleles per dog), allelic OR.
  Divided by 2 for dogs, then multiplied by a relatedness inflation for the within-breed mixed model.
- Haploid parasite genotype: one call per infection; the case-control formula on infections.
- Continuous exposure, logistic regression (Hsieh 1989): n = (z_a + z_b)^2 / (P (1 - P) beta^2) / (1 - R2), beta = ln(OR per SD).
- Cohort size = cases needed / proportion with the outcome.
- Rank tests: n multiplied by 1 / 0.955 (asymptotic relative efficiency 3/pi).
"""
import csv
import json
import math
import pathlib
from statistics import NormalDist

OUT = pathlib.Path(__file__).resolve().parent.parent / "out"
Z = NormalDist().inv_cdf
PHI = NormalDist().cdf


def z_alpha(alpha):
    return Z(1 - alpha / 2)


def cc_cases(p0, odds_ratio, alpha=0.05, power=0.8, k=1.0):
    """Cases needed for a case-control comparison of a binary exposure with frequency p0 in controls."""
    p1 = odds_ratio * p0 / (1 + p0 * (odds_ratio - 1))
    pbar = (p1 + k * p0) / (1 + k)
    num = (z_alpha(alpha) * math.sqrt((1 + 1 / k) * pbar * (1 - pbar))
           + Z(power) * math.sqrt(p1 * (1 - p1) + p0 * (1 - p0) / k)) ** 2
    return num / (p1 - p0) ** 2, p1


def cc_power(n_cases, n_controls, p0, odds_ratio, alpha=0.05):
    p1 = odds_ratio * p0 / (1 + p0 * (odds_ratio - 1))
    k = n_controls / n_cases
    pbar = (p1 + k * p0) / (1 + k)
    se0 = math.sqrt((1 / n_cases + 1 / n_controls) * pbar * (1 - pbar))
    se1 = math.sqrt(p1 * (1 - p1) / n_cases + p0 * (1 - p0) / n_controls)
    return PHI((abs(p1 - p0) - z_alpha(alpha) * se0) / se1)


def detectable_or(n_cases, n_controls, p0, alpha=0.05, power=0.8, above=True):
    """Smallest OR (> 1, or largest < 1) detectable with these group sizes; bisection on the log scale."""
    lo, hi = (0.0, math.log(1000.0)) if above else (math.log(0.001), 0.0)
    for _ in range(200):
        mid = (lo + hi) / 2
        pw = cc_power(n_cases, n_controls, p0, math.exp(mid), alpha)
        if above:
            lo, hi = (lo, mid) if pw >= power else (mid, hi)
        else:
            lo, hi = (mid, hi) if pw >= power else (lo, mid)
    return math.exp(hi if above else lo)


def logistic_cont_n(prev, or_per_sd, alpha=0.05, power=0.8, r2=0.0):
    beta = math.log(or_per_sd)
    return (z_alpha(alpha) + Z(power)) ** 2 / (prev * (1 - prev) * beta ** 2) / (1 - r2)


ROWS = []


def add(memo, scenario, design, **kw):
    row = {"memo": memo, "scenario": scenario, "design": design}
    row.update(kw)
    ROWS.append(row)


def ceil(x):
    return int(math.ceil(x - 1e-9))


# ---------------------------------------------------------------- calibration against SV-05
# SV-05: S-CB050, 50 young (6 died) vs 90 adult (9 died); "only OR >= 3.7 detectable" with 15 deaths.
# Our check: cases = 15 deaths, controls = 125 survivors, exposure = young; p0 = young among survivors = 44/125.
CAL = {
    "source": "SV-05-01-age-death (S-CB050, 15 deaths, 125 survivors, young 44/125 among survivors)",
    "cohort_framing_detectable_or": round(detectable_or(50, 90, 9 / 90), 2),
    "cohort_framing_note": "groups = 50 young vs 90 adult, outcome risk 9/90 in adults (the SV-05 formula)",
    "case_control_framing_detectable_or_above": round(detectable_or(15, 125, 44 / 125), 2),
    "case_control_framing_detectable_or_below": round(detectable_or(15, 125, 44 / 125, above=False), 2),
    "case_control_framing_note": "groups = 15 deaths vs 125 survivors, exposure young 44/125 in survivors (the memo formula)",
    "sv05_reported": "about 3.7 or more, or 0.28 or less",
}


# ---------------------------------------------------------------- shared assumptions
DEATH = 0.11       # S-CB050: 15 of 140 died (SV-05); died includes euthanasia for poor prognosis
SEVERE = 0.30      # assumed share of the severe outcome set (memo 3) in a B. rossi cohort
COMPLICATED = 0.40 # memo 1: assumed share of complicated disease (sensitivity 0.30 to 0.50)
LOSS = 1.15        # memo 1: 15% failed amplification, mixed genotypes, loss to follow-up
RELATED = 1.15     # memo 2: inflation for relatedness in a within-breed mixed model (assumption)


def cohort(cases, share, extra=1.0):
    return ceil(cases / share * extra)


# ---------------------------------------------------------------- memo 1: parasite genotype
# Design A: genotype19 vs all other BrEMA1 genotypes (CB379's four "poor prognosis" genotypes cover 90% of isolates,
# so they give no contrast). Complicated vs uncomplicated in one cohort: 1.5 uncomplicated per complicated.
K_A = (1 - COMPLICATED) / COMPLICATED
for p0 in (0.25, 0.35, 0.45):
    for odds in (2.0, 2.5, 3.0, 4.0):
        n, p1 = cc_cases(p0, odds, k=K_A)
        n_adj = n / (1 - 0.20)
        add("parasite_genotype", f"Genotype19, freq {p0:.2f} in uncomplicated, OR {odds:g}",
            "Design A: BrEMA1 genotype19 vs others, complicated vs uncomplicated, R2 0.20",
            exposure_freq_controls=p0, exposure_freq_cases=round(p1, 3), odds_ratio=odds, alpha=0.05, power=0.8,
            r2_covariates=0.20, controls_per_case=round(K_A, 2), n_cases=ceil(n_adj), n_controls=ceil(K_A * n_adj),
            n_total=ceil(n_adj * (1 + K_A)), cohort_needed=cohort(n_adj, COMPLICATED, LOSS),
            cohort_basis="complicated 40%, +15% loss",
            note="Haploid call per infection; mixed-genotype infections carry the genotype (sensitivity: excluded)")
# Secondary outcome: death, genotype19 at 0.35
K_D = (1 - DEATH) / DEATH
for odds in (2.5, 4.0):
    n, p1 = cc_cases(0.35, odds, k=K_D)
    n_adj = n / (1 - 0.20)
    add("parasite_genotype", f"Genotype19, freq 0.35 in survivors, death 11%, OR {odds:g}",
        "Design A, secondary outcome: died vs survived, R2 0.20",
        exposure_freq_controls=0.35, exposure_freq_cases=round(p1, 3), odds_ratio=odds, alpha=0.05, power=0.8,
        r2_covariates=0.20, controls_per_case=round(K_D, 2), n_cases=ceil(n_adj), n_controls=ceil(K_D * n_adj),
        n_total=ceil(n_adj * (1 + K_D)), cohort_needed=cohort(n_adj, DEATH, LOSS), cohort_basis="death 11%, +15% loss",
        note="Died includes euthanasia for poor prognosis at Onderstepoort")
# Design B: gene-level burden over 3,098 genes (alpha 0.05/3,098 = 1.6e-5) and variant level over ~30,000 common SNPs
for label, alpha in (("gene burden, alpha 1.6e-5 (0.05 / 3,098 genes)", 0.05 / 3098),
                     ("variant level, alpha 1.7e-6 (0.05 / 30,000 SNPs)", 0.05 / 30000)):
    for p0 in (0.15, 0.30, 0.50):
        for odds in (3.0, 5.0):
            n, p1 = cc_cases(p0, odds, alpha=alpha, k=K_A)
            n_adj = n / (1 - 0.20)
            add("parasite_genotype", f"{label}, carrier freq {p0:.2f}, OR {odds:g}",
                "Design B: genome-wide parasite association, complicated vs uncomplicated",
                exposure_freq_controls=p0, exposure_freq_cases=round(p1, 3), odds_ratio=odds, alpha=alpha, power=0.8,
                r2_covariates=0.20, controls_per_case=round(K_A, 2), n_cases=ceil(n_adj), n_controls=ceil(K_A * n_adj),
                n_total=ceil(n_adj * (1 + K_A)), cohort_needed=cohort(n_adj, COMPLICATED, LOSS / 0.6),
                cohort_basis="complicated 40%, +15% loss, 60% monoclonal",
                note="One sequenced monoclonal infection per dog; population structure by principal components")

# ---------------------------------------------------------------- memo 2: host genetics
# Pit bull-type dogs with B. rossi; severe vs mild, 1:1. 20 candidate tests (DEA 1: 1, haptoglobin: 2, cytokine SNPs: 8,
# TLR4/MYD88: 2, DLA haplotypes: 7), alpha 0.05 / 20 = 0.0025. Primary analysis not adjusted for load (load may be a mediator).
A_CAND = 0.05 / 20
for label, freqs in (("DEA 1 positive", (0.40, 0.50, 0.60)), ("DLA haplotype carrier", (0.15, 0.30))):
    for p0 in freqs:
        for odds in (1.5, 2.0, 3.0):
            n, p1 = cc_cases(p0, odds, alpha=A_CAND, k=1.0)
            n_adj = n / (1 - 0.10) * RELATED
            add("host_genetics", f"{label}, freq {p0:.2f} in mild, OR {odds:g}",
                "Candidate loci: pit bull-type, severe vs mild, 1:1, 20 candidates (alpha 0.0025)",
                exposure_freq_controls=p0, exposure_freq_cases=round(p1, 3), odds_ratio=odds, alpha=A_CAND, power=0.8,
                r2_covariates=0.10, controls_per_case=1, n_cases=ceil(n_adj), n_controls=ceil(n_adj), n_total=ceil(2 * n_adj),
                cohort_needed=cohort(n_adj, SEVERE), cohort_basis="severe 30% of pit bull-type cases",
                note=f"Carrier or phenotype frequency; R2 0.10 with age and days sick; relatedness inflation {RELATED}")
# Within-breed GWAS, allelic test, alpha 5e-7 (Bonferroni on about 100,000 SNPs after quality control)
for maf in (0.20, 0.40):
    for odds in (1.5, 2.0, 3.0):
        n_alleles, p1 = cc_cases(maf, odds, alpha=5e-7, k=1.0)
        dogs = n_alleles / 2 * RELATED
        add("host_genetics", f"GWAS allelic test, MAF {maf:.2f}, allelic OR {odds:g}, alpha 5e-7",
            "Within-breed GWAS on a canine SNP array, pit bull-type, severe vs mild, 1:1",
            exposure_freq_controls=maf, exposure_freq_cases=round(p1, 3), odds_ratio=odds, alpha=5e-7, power=0.8,
            r2_covariates=0.0, controls_per_case=1, n_cases=ceil(dogs), n_controls=ceil(dogs), n_total=ceil(2 * dogs),
            cohort_needed=cohort(dogs, SEVERE), cohort_basis="severe 30% of pit bull-type cases",
            note=f"Diploid, additive; relatedness inflation {RELATED}; long within-breed LD")

# ---------------------------------------------------------------- memo 3: minimum dataset
# (a) A binary host factor as in SV-05 (young vs adult, 35% young), death 11% in the unexposed: cohort size for OR 2 to 3.
#     Cohort framing (the SV-05 formula): exposure groups are fixed, the outcome is counted.
def cohort_n(frac_exposed, risk0, odds_ratio, alpha=0.05, power=0.8):
    lo, hi = 10.0, 1e6
    for _ in range(200):
        mid = (lo + hi) / 2
        pw = cc_power(mid * frac_exposed, mid * (1 - frac_exposed), risk0, odds_ratio, alpha)
        lo, hi = (lo, mid) if pw >= power else (mid, hi)
    return hi


for odds in (2.0, 2.5, 3.0):
    frac = 0.35
    n = cohort_n(frac, DEATH, odds)
    r1 = odds * DEATH / (1 + DEATH * (odds - 1))
    deaths = n * (frac * r1 + (1 - frac) * DEATH)
    add("minimum_dataset", f"Binary host factor (e.g. age < 12 months), 35% exposed, death 11%, OR {odds:g}",
        "Prospective cohort, death as outcome, all enrolled dogs",
        exposure_freq_controls=frac, exposure_freq_cases=None, odds_ratio=odds, alpha=0.05, power=0.8, r2_covariates=0.0,
        controls_per_case=None, n_cases=ceil(deaths), n_controls=ceil(n - deaths),
        n_total=ceil(n), cohort_needed=ceil(n), cohort_basis="all enrolled dogs",
        note=f"Risk {r1:.3f} exposed vs {DEATH} unexposed; SV-05 could detect only OR >= 3.7 with 15 deaths")
# (b) Continuous exposure (log load, a marker) per SD, death 11% and severe set 30%, R2 0.2 with the other covariates
for prev, plabel in ((DEATH, "death 11%"), (SEVERE, "severe outcome set 30%")):
    for orsd in (1.5, 2.0):
        n = logistic_cont_n(prev, orsd, r2=0.2)
        add("minimum_dataset", f"Continuous exposure (log load or a marker), OR {orsd:g} per SD, {plabel}, R2 0.2",
            "Prospective cohort, logistic regression adjusted for age, days sick and antibody status",
            exposure_freq_controls=None, exposure_freq_cases=None, odds_ratio=orsd, alpha=0.05, power=0.8, r2_covariates=0.2,
            controls_per_case=None, n_cases=ceil(n * prev), n_controls=ceil(n * (1 - prev)), n_total=ceil(n),
            cohort_needed=ceil(n), cohort_basis="all enrolled dogs",
            note="Load x antibody interaction of the same size needs about 4 times this n")
# (c) Replication of an Onderstepoort marker (band neutrophils) outside Onderstepoort, died vs survived, rank test
for d in (0.5, 0.65, 0.8):
    k = (1 - DEATH) / DEATH
    n1 = (z_alpha(0.05) + Z(0.8)) ** 2 * (1 + 1 / k) / d ** 2 / 0.955
    add("minimum_dataset", f"Marker replication outside Onderstepoort, died vs survived, {d:g} SD, rank test",
        "Second B. rossi cohort (not Onderstepoort), death as outcome",
        exposure_freq_controls=None, exposure_freq_cases=None, odds_ratio=None, alpha=0.05, power=0.8, r2_covariates=0.0,
        controls_per_case=round(k, 2), n_cases=ceil(n1), n_controls=ceil(n1 * k), n_total=ceil(n1 * (1 + k)),
        cohort_needed=ceil(n1 * (1 + k)), cohort_basis="all enrolled dogs at non-Onderstepoort sites",
        note="Standardised difference; ARE 0.955 for the rank test")

OUT.mkdir(exist_ok=True)
fields = ["memo", "scenario", "design", "exposure_freq_controls", "exposure_freq_cases", "odds_ratio", "alpha", "power",
          "r2_covariates", "controls_per_case", "n_cases", "n_controls", "n_total", "cohort_needed", "cohort_basis", "note"]
with open(OUT / "power.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    for r in ROWS:
        w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})

ASSUMPTIONS = {
    "death_proportion": DEATH, "death_source": "S-CB050 15 of 140 (SV-05); died includes euthanasia for poor prognosis",
    "severe_set_proportion": SEVERE, "severe_source": "assumption for a B. rossi cohort; to be checked in the first 100 dogs",
    "complicated_proportion": COMPLICATED, "loss_inflation": LOSS,
    "relatedness_inflation": RELATED, "power": 0.8,
}
with open(OUT / "power.json", "w", encoding="utf-8") as fh:
    json.dump({"calibration": CAL, "assumptions": ASSUMPTIONS, "rows": ROWS}, fh, indent=1, allow_nan=False)
print(json.dumps(CAL))
print(len(ROWS), "rows")
