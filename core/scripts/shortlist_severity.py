"""Shortlist the articles that test markers or parameters against clinical severity or outcome, and seed the
marker map used to normalise the extracted associations.

1. Candidate sentences. From the scispaCy mentions (data/syndromes/mentions.jsonl), every distinct sentence in a
   section that reports the article's own work (title, abstract, results, case, conclusion, unlabelled) that
   names a severity or outcome (OUTCOME: non-survivors, died, complicated, MODS, prognosis, severity...).
   A sentence is "tested" when it also carries an association or statistic (TEST: correlated, p <, odds
   ratio, ROC...). Marker hints are the sentence's non-negated biomarker-type concepts (UMLS link >=
   MIN_LINK, minus method and outcome words); they are pointers for the extractor, not results.
2. Shortlist. Human comparator articles, reviews (they restate other studies) and single-case reports (no
   comparison to test) are left out. Each article
   gets a rank score: 2 x tested sentences + other outcome sentences + aim bonus (BIOM 3, CLIN 1) + its
   studied SEV score. Tier A: full text with >= 2 tested sentences; B: full text with any outcome sentence,
   or abstract only with a tested sentence; C: the rest with any outcome sentence. Linked cohorts
   (articles.jsonl cohort_id) are shown so a re-analysis of the same dogs is not counted as a replication.
3. Marker map (data/severity/marker_map.csv). One row per alias: alias (lower case), marker (canonical
   name), marker_class, pattern (regex over the lower-cased alias; canonical rows only), cui, source, note,
   articles. Canonical rows come from SEED, in matching order (first pattern match wins, so specific markers
   such as lactate dehydrogenase sit before lactate). scispaCy concepts in candidate sentences are added as
   aliases (source "scispacy") with the marker their name matches, or blank. The file is meant for editing:
   rows with any other source ("manual", or "extracted" rows added by check_associations.py) are kept as
   they are, and a manual row replaces the seed or scispaCy row with the same alias. Set marker to "-" to
   drop an alias.

Outputs in data/severity/: shortlist.csv, candidate_sentences.jsonl, marker_map.csv

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/shortlist_severity.py
"""
import collections
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from categorise_articles import BIOMARKER_TYPES, EXCLUDE, MIN_LINK  # noqa: E402
SYN = ROOT / "data" / "syndromes"
OUT = ROOT / "data" / "severity"
MAP = OUT / "marker_map.csv"
SECTIONS = {"title", "abstract", "results", "results_discussion", "case", "conclusion", "unlabelled"}
OUTCOME = re.compile(r"non-?surviv|surviv(ed|ors?|al)|\bdied\b|\bdeath|mortality|fatal|euthan|outcome|prognos|"
                     r"(un)?complicated|complication|\bmods\b|multiple organ|organ (dysfunction|failure)|"
                     r"severity|severe (form|disease|babesiosis|cases?|clinical)|mild (form|disease|babesiosis|cases?)|"
                     r"hospitali[sz]|length of stay|critical(ly)? ill", re.I)
TEST = re.compile(r"correlat|associat|odds ratio|hazard|relative risk|\bor\b ?[=:(]|\bauc\b|\broc\b|receiver operating|"
                  r"area under|cut-?off|sensitivity|specificity|predict|regression|significan|\bp ?[<=>≤]|"
                  r"higher in|lower in|differ(ed|ence)", re.I)
AIM_BONUS = {"BIOM": 3, "CLIN": 1}
# biomarker-type concepts that are methods, outcomes or generic words, not markers
HINT_STOP = re.compile(r"^(diagnosis|positive|negative|biological markers|analysis of substances|hematologic tests|"
                       r"laboratory procedures?|proteins?|metabolite|prognostic factors?|cessation of life|death|survival|"
                       r"polymerase chain reaction|microscopy|blood smear|blood test|clinical chemistry tests|"
                       r"hematology procedure|physical examination|evaluation procedure|measurement|test result)$", re.I)

# Canonical markers in matching order: (marker, class, pattern over the lower-cased, dash-normalised name)
SEED = [
    # specific names first where a general pattern would also match
    ("Lactate dehydrogenase", "biochemistry", r"lactate dehydrogenase|\bldh\b"),
    ("Neutrophil-to-lymphocyte ratio", "haematology", r"neutrophil-? ?to-? ?lymphocyte|\bnlr\b"),
    ("Platelet-to-lymphocyte ratio", "haematology", r"platelet-? ?to-? ?lymphocyte|\bplr\b"),
    ("Urine protein:creatinine ratio", "urine", r"protein ?[:/-] ?creatinine|protein-? ?to-? ?creatinine|\bupcr?\b|proteinuria"),
    ("Plasma NGAL", "biochemistry", r"(plasma|serum) (ngal|neutrophil gelatinase)|\b[ps]ngal\b"),
    ("Urine specific gravity", "urine", r"specific gravity|\busg\b"),
    ("Urine osmolality", "urine", r"osmolal|osmolar|\buosm"),
    ("Urinary kidney injury biomarkers", "urine", r"\bngal\b|lipocalin|\bkim-?1\b|urinary (ggt|gamma)|\buggt|retinol[- ]binding|\bu?nag\b|clusterin"),
    ("Cortisol:ACTH ratio", "endocrine", r"cortisol ?[:/-] ?acth|cortisol-? ?to-? ?acth"),
    ("CK-MB", "cardiac", r"ck-?mb"),
    ("Plasma free haemoglobin", "haematology", r"free h(a)?emoglobin|plasma h(a)?emoglobin|h(a)?emoglobin(a)?emia"),
    ("Haemoglobinuria", "urine", r"h(a)?emoglobinuria|pigmenturia"),
    ("Red cell indices", "haematology", r"\bmcv\b|\bmchc?\b|mean (corpuscular|cell) (volume|h(a)?emoglobin)"),
    ("Blood gases and oxygenation", "acid-base and perfusion",
     r"\bpa?o2\b|\bpa?co2\b|partial pressure|oxygen (saturation|tension|content|extraction|delivery)|\bs[ap]o2\b|"
     r"oxyh(a)?emoglobin|meth(a)?emoglobin|carboxyh(a)?emoglobin|\bp50\b|oxygen dissociation|hypox(a)?emi"),
    ("Albumin:globulin ratio", "biochemistry", r"albumin ?[:/] ?globulin|albumin-? ?to-? ?globulin|\ba ?[:/] ?g ratio"),
    ("Serum protein electrophoresis fractions", "biochemistry", r"electrophore|(alpha|beta|gamma)-? ?[12]?-? ?globulin"),
    ("Angiopoietin-2:angiopoietin-1 ratio", "endothelial", r"angiopoietin.*ratio|ang-?2 ?[:/] ?ang-?1"),
    ("Asymmetric dimethylarginine / nitric oxide", "endothelial", r"asymmetric dimethylarginine|\badma\b|nitric oxide|nitrite|nitrate|\bnox\b"),
    ("SDMA", "biochemistry", r"\bsdma\b|(?<!a)symmetric dimethylarginine"),
    ("Thrombin-antithrombin complex / thrombin generation", "coagulation", r"thrombin-? ?antithrombin|\btat\b|thrombin generation"),
    ("Platelet function", "coagulation", r"platelet (function|aggregation|activation)|p-selectin"),
    ("Mean platelet volume and platelet indices", "haematology", r"mean platelet volume|\bmpv\b|platelet indices|plateletcrit|platelet distribution width"),
    ("MCP-1 (CCL2)", "cytokine", r"monocyte chemo(attractant|tactic) protein|\bmcp-?1|\bccl-?2\b"),
    ("Myeloperoxidase / MPXI", "haematology", r"myeloperoxidase|\bmpxi\b|\bmpo\b"),
    ("Band neutrophils", "haematology", r"band (neutrophil|form|cell)s?|\bbands\b|left shift|immature neutrophil"),
    ("Lymphocyte subsets", "immunology", r"\bcd(4|8|21)\b|\b[bt][- ]cells?\b|\b[bt][- ]lymphocyte|lymphocyte subset"),
    ("Parasite DNA load (qPCR)", "parasitology", r"(dna|copy) (load|number)|quantitative pcr|\bqpcr\b|\bct value|cycle threshold"),
    ("Icterus", "clinical sign", r"icter|jaundice"),
    ("Ferritin", "acute phase protein", r"ferritin"),
    # haematology
    ("Haematocrit/PCV", "haematology", r"h(a)?ematocrit|packed cell volume|\bpcv\b|\bhct\b"),
    ("Haemoglobin", "haematology", r"h(a)?emoglobin|\bhgb\b|\bhb\b"),
    ("Red blood cell count", "haematology", r"red (blood )?cell count|erythrocyte count|\brbc\b|^erythrocytes?$"),
    ("Red cell distribution width", "haematology", r"\brdw\b|red (blood )?cell distribution width"),
    ("Reticulocytes", "haematology", r"reticulocyt"),
    ("Nucleated red blood cells", "haematology", r"nucleated red|\bnrbcs?\b|normoblast"),
    ("Autoagglutination", "haematology", r"agglutinat"),
    ("Spherocytes", "haematology", r"spherocyt"),
    ("Direct antiglobulin (Coombs) test", "immunology", r"coombs|antiglobulin"),
    ("White blood cell count", "haematology", r"white (blood )?cell|leu[ck]ocyt|leu[ck]open|\bwbc\b"),
    ("Neutrophil count", "haematology", r"neutroph"),
    ("Lymphocyte count", "haematology", r"lymphocyt|lymphopen"),
    ("Monocyte count", "haematology", r"monocyt"),
    ("Eosinophil count", "haematology", r"eosinop"),
    ("Platelet count", "haematology", r"platelet|thrombocyt|\bplt\b"),
    # parasitology and infection
    ("Parasitaemia", "parasitology", r"parasit(a)?emia|parasite (load|density|burden|count)|parasiti[sz]ed (red|erythro)|infected (red|erythro)"),
    ("Parasite species or genotype", "parasitology", r"genotyp|haplotype|strain|\bbc ?28|\bbr1\b|18s"),
    ("Co-infection", "parasitology", r"co-?infect|concurrent infection|ehrlichi|anaplasm|hepatozo|leishman|dirofilari"),
    ("Antibody titre / serostatus", "immunology", r"antibod|titre|titer|seropositiv|\big[gm]\b|serostatus"),
    ("Immune complexes / complement", "immunology", r"immune complex|complement|\bc3\b"),
    # acute phase and inflammation
    ("C-reactive protein", "acute phase protein", r"c-?reactive|\bcrp\b"),
    ("Haptoglobin", "acute phase protein", r"haptoglobin|\bhp\b"),
    ("Serum amyloid A", "acute phase protein", r"amyloid a|\bsaa\b"),
    ("Ceruloplasmin", "acute phase protein", r"c(a)?eruloplasmin"),
    ("Procalcitonin", "acute phase protein", r"procalcitonin"),
    ("Hepcidin", "acute phase protein", r"hepcidin"),
    ("IL-1 beta", "cytokine", r"(\bil|interleukin)-? ?1(?![0-9])"),
    ("IL-2", "cytokine", r"(\bil|interleukin)-? ?2(?![0-9])"),
    ("IL-6", "cytokine", r"(\bil|interleukin)-? ?6(?![0-9])"),
    ("IL-8 (CXCL8)", "cytokine", r"(\bil|interleukin)-? ?8(?![0-9])|cxcl-?8"),
    ("IL-10", "cytokine", r"(\bil|interleukin)-? ?10(?![0-9])"),
    ("IL-18", "cytokine", r"(\bil|interleukin)-? ?18"),
    ("TNF-alpha", "cytokine", r"tumou?r necrosis factor|\btnf"),
    ("IFN-gamma", "cytokine", r"interferon|\bifn"),
    ("KC-like (CXCL1)", "cytokine", r"\bkc-? ?like|cxcl-?1\b"),
    ("GM-CSF", "cytokine", r"gm-?csf|granulocyte-? ?macrophage colony"),
    ("Cytokine linear combination", "cytokine", r"linear combination"),
    ("Other cytokines and chemokines", "cytokine", r"cytokine|chemokine|(\bil|interleukin)-? ?\d|\bcxcl|\bccl"),
    # endothelium
    ("Angiopoietin-1", "endothelial", r"angiopoietin-? ?1|\bang-?1\b"),
    ("Angiopoietin-2", "endothelial", r"angiopoietin-? ?2|\bang-?2\b"),
    ("VEGF", "endothelial", r"vascular endothelial growth|\bvegf"),
    ("Syndecan-1", "endothelial", r"syndecan"),
    ("Hyaluronan / glycocalyx", "endothelial", r"hyaluron|glycocalyx|heparan"),
    ("Adhesion molecules (ICAM-1, VCAM-1, selectins)", "endothelial", r"icam|vcam|selectin|adhesion molecule"),
    ("von Willebrand factor", "endothelial", r"willebrand|\bvwf"),
    ("Endothelin-1", "endothelial", r"endothelin"),
    # coagulation
    ("Fibrinogen", "coagulation", r"fibrinogen"),
    ("Coagulation factor activity", "coagulation", r"coagulation factor|factor (ii|v|vii|viii|ix|x|xi|xii)\b|\bf(ii|v|vii|viii|ix|x|xi|xii)\b"),
    ("Fibrinolysis (plasminogen, antiplasmin)", "coagulation", r"plasmin|fibrinoly|\bpai-?1\b|\btafi\b"),
    ("Prothrombin time", "coagulation", r"prothrombin time|\bpt\b"),
    ("aPTT", "coagulation", r"partial thromboplastin|\ba?ptt\b"),
    ("D-dimer", "coagulation", r"d-?dimer|fibrin fragment d"),
    ("Fibrin(ogen) degradation products", "coagulation", r"degradation product|\bfdps?\b"),
    ("Antithrombin", "coagulation", r"antithrombin|\bat ?iii\b"),
    ("Protein C / protein S", "coagulation", r"protein [cs]\b"),
    ("Viscoelastic testing (TEG/ROTEM)", "coagulation", r"thromboelasto|\bteg\b|rotem|viscoelastic|maximum amplitude"),
    ("DIC", "coagulation", r"disseminated intravascular|\bdic\b"),
    # biochemistry
    ("Urea", "biochemistry", r"\burea\b|urea nitrogen|\bbun\b|azot(a)?emi"),
    ("Creatinine", "biochemistry", r"creatinin"),
    ("Cystatin C", "biochemistry", r"cystatin"),
    ("Glomerular filtration rate", "biochemistry", r"glomerular filtration|\bgfr\b|iohexol|clearance"),
    ("ALT", "biochemistry", r"alanine (amino)?trans(ferase|aminase)|\balt\b|\bsgpt\b|\bgpt\b"),
    ("AST", "biochemistry", r"aspartate (amino)?trans(ferase|aminase)|\bast\b|\bsgot\b|\bgot\b"),
    ("ALP", "biochemistry", r"alkaline phosphatase|\balp\b|\bsap\b"),
    ("GGT", "biochemistry", r"gamma-? ?glutamyl|\bggt\b"),
    ("Bilirubin", "biochemistry", r"bilirubin"),
    ("Bile acids", "biochemistry", r"bile acid"),
    ("Total protein", "biochemistry", r"total (serum |plasma )?protein|\btp\b|^proteins?$|(hypo|hyper)protein"),
    ("Albumin", "biochemistry", r"albumin"),
    ("Globulins", "biochemistry", r"globulin|gammopath"),
    ("Glucose", "biochemistry", r"glucose|glyc(a)?emi"),
    ("Cholesterol", "biochemistry", r"cholesterol"),
    ("Triglycerides", "biochemistry", r"triglycerid"),
    ("Lipoproteins", "biochemistry", r"lipoprotein|\bhdl\b|\bldl\b"),
    ("Creatine kinase", "biochemistry", r"creatine (phospho)?kinase|\bck\b|\bcpk\b"),
    ("Pancreatic enzymes (lipase, amylase, cPLI)", "biochemistry", r"lipase|amylase|\bc?pli\b|pancreatic"),
    ("Sodium", "electrolyte", r"sodium|natr(a)?emi"),
    ("Potassium", "electrolyte", r"potassium|kal(a)?emi"),
    ("Chloride", "electrolyte", r"chlorid|chlor(a)?emi"),
    ("Ionised calcium", "electrolyte", r"ioni[sz]ed calcium|\bica\b"),
    ("Calcium", "electrolyte", r"calcium|calc(a)?emi"),
    ("Phosphate", "electrolyte", r"phosph(ate|orus)|phosphat(a)?emi"),
    ("Magnesium", "electrolyte", r"magnes"),
    ("Iron and iron indices", "biochemistry", r"\biron\b|transferrin|\btibc\b"),
    ("Ammonia", "biochemistry", r"ammonia"),
    ("Zinc", "biochemistry", r"\bzinc\b|\bzn\b"),
    ("Copper", "biochemistry", r"\bcopper\b|\bcu\b"),
    ("Selenium", "biochemistry", r"selenium"),
    # acid-base and perfusion
    ("Lactate", "acid-base and perfusion", r"lactat"),
    ("Acid-base (pH, bicarbonate, base excess, anion gap)", "acid-base and perfusion",
     r"\bph\b|acid(o|e)mi|acidos|alkal(osis|emia|aemia)|acid-base|bicarbonate|\bhco3|base (excess|deficit)|anion gap|"
     r"strong ion|\bt?co2\b|total co2"),
    # cardiac
    ("Cardiac troponin", "cardiac", r"troponin|\bctn[it]\b"),
    ("Natriuretic peptides", "cardiac", r"natriuretic|\bbnp\b|\banp\b"),
    ("ECG abnormalities", "cardiac", r"electrocardiog|\becg\b|\bekg\b|arrhythm|premature (ventricular|complex)|st-? ?segment|qt interval"),
    ("Echocardiographic findings", "cardiac", r"echocardiog"),
    # endocrine
    ("Cortisol", "endocrine", r"cortisol"),
    ("ACTH", "endocrine", r"\bacth\b|adrenocorticotrop"),
    ("Thyroid hormones", "endocrine", r"thyrox|\bf?t4\b|\bf?t3\b|triiodothyronine|thyroid hormone"),
    ("TSH", "endocrine", r"\btsh\b|thyroid-? ?stimulating"),
    ("Insulin", "endocrine", r"insulin"),
    ("Erythropoietin", "endocrine", r"erythropoietin|\bepo\b"),
    ("Renin-angiotensin-aldosterone", "endocrine", r"aldosteron|\brenin\b|angiotensin"),
    ("Vasopressin / copeptin", "endocrine", r"vasopressin|copeptin"),
    # oxidative stress
    ("Malondialdehyde / TBARS", "oxidative stress", r"malondialdehyde|\bmda\b|tbars|thiobarbituric|lipid peroxid"),
    ("Catalase", "oxidative stress", r"catalase"),
    ("Superoxide dismutase", "oxidative stress", r"superoxide dismutase|\bsod\b"),
    ("Glutathione / glutathione peroxidase", "oxidative stress", r"glutathione|\bgsh\b|\bgpx\b"),
    ("Total antioxidant capacity", "oxidative stress", r"total antioxidant|\btac\b|\btas\b|\bfrap\b|cuprac|\babts\b"),
    ("Paraoxonase-1", "oxidative stress", r"paraoxonase|\bpon-?1"),
    ("Other oxidative stress markers", "oxidative stress", r"oxidat|antioxid|peroxid|reactive oxygen|\bros\b|\btos\b|isoprostane|carbonyl"),
    # clinical findings
    ("Body temperature", "clinical sign", r"temperature|fever|pyrexi|hypotherm|hypertherm"),
    ("Heart rate", "clinical sign", r"heart rate|pulse rate|tachycardi|bradycardi"),
    ("Respiratory rate / dyspnoea", "clinical sign", r"respiratory rate|tachypn|dyspn"),
    ("Blood pressure", "clinical sign", r"blood pressure|hypotensi|hypertensi|arterial pressure|\bmap\b"),
    ("Mentation / neurological signs", "clinical sign", r"mentation|collapse|neurolog|seizure|\bcoma\b|stupor|recumben"),
    ("Mucous membranes / capillary refill", "clinical sign", r"mucous membrane|capillary refill|\bcrt\b|pallor|\bpale\b"),
    ("Splenomegaly / lymphadenopathy", "clinical sign", r"splenomegal|hepatomegal|lymphadenopath|lymph node"),
    ("Gastrointestinal signs", "clinical sign", r"vomit|diarrh|gastrointestinal sign|mel(a)?ena|anorexi|inappeten"),
    ("Urine output", "clinical sign", r"oligur|anuri|urine output|polyuri"),
    ("Clinical severity score", "clinical score", r"severity score|clinical score|\bsirs\b|systemic inflammatory response|apple(fast|full)?\b|organ dysfunction score"),
    ("Travel / import history", "clinical history", r"travel|import"),
    ("Duration of illness before presentation", "clinical history", r"duration of (illness|clinical signs)|before presentation|time to (presentation|treatment)"),
    # signalment
    ("Age", "signalment", r"\bage\b|puppy|puppies|young"),
    ("Sex / neuter status", "signalment", r"\bsex\b|gender|neuter|castrat|spay|gonadectom|\bintact\b"),
    ("Breed", "signalment", r"breed"),
    ("Body weight / body condition", "signalment", r"body ?weight|body condition|\bbcs\b"),
    # imaging, omics, treatment
    ("Ultrasonographic findings", "imaging", r"ultraso|sonograph|doppler|resistive index"),
    ("Radiographic findings", "imaging", r"radiograph"),
    ("Gene expression / transcriptomics", "omics", r"gene expression|transcriptom|\bmrna\b|rna-?seq"),
    ("Proteomics / metabolomics", "omics", r"proteom|metabolom|lipidom"),
    ("Treatment factors", "treatment", r"transfusion|imidocarb|diminazene|atovaquone|azithromycin|clindamycin"),
]
FIELDS = ["alias", "marker", "marker_class", "pattern", "cui", "source", "note", "articles"]


def norm_name(s):
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = re.sub(r"[‐‑‒–—−]", "-", s)
    return s.replace("β", "beta").replace("α", "alpha").replace("γ", "gamma").replace("κ", "kappa")


def match_marker(name, canon):
    low = norm_name(name)
    for marker, cls, pat in canon:
        if pat and re.search(pat, low):
            return marker, cls
    return "", ""


def build_map(concepts, arts):
    old = []
    if MAP.exists():
        with open(MAP, encoding="utf-8") as fh:
            old = list(csv.DictReader(fh))
    kept = [r for r in old if r["source"] not in ("seed", "scispacy")]
    kept_alias = {r["alias"] for r in kept}
    # manual rows with a pattern define or override canonical markers and match first
    canon = [(r["marker"], r["marker_class"], r["pattern"]) for r in kept if r["pattern"]]
    canon += [(m, c, p) for m, c, p in SEED]
    rows = [{"alias": norm_name(m), "marker": m, "marker_class": c, "pattern": p, "cui": "", "source": "seed",
             "note": "canonical", "articles": ""} for m, c, p in SEED if norm_name(m) not in kept_alias]
    seen = {r["alias"] for r in rows} | kept_alias
    for cui, name in sorted(concepts.items(), key=lambda kv: (-len(arts[kv[0]]), kv[1])):
        alias = norm_name(name)
        if alias in seen:
            continue
        seen.add(alias)
        marker, cls = match_marker(name, canon)
        rows.append({"alias": alias, "marker": marker, "marker_class": cls, "pattern": "", "cui": cui, "source": "scispacy",
                     "note": "pattern match" if marker else "unmatched: fill in marker or set '-'", "articles": len(arts[cui])})
    rows = kept + rows
    with open(MAP, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cats = {}
    with open(SYN / "article_categories.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            cats[r["id"]] = r
    recs = {}
    with open(ROOT / "articles.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            recs[r["id"]] = r

    sentences = {}  # (id, section, sentence) -> {"tested", "markers"}
    concepts, arts = {}, collections.defaultdict(set)
    with open(SYN / "mentions.jsonl", encoding="utf-8") as fh:
        for line in fh:
            m = json.loads(line)
            if m["section"] not in SECTIONS or not OUTCOME.search(m["sentence"]):
                continue
            key = (m["id"], m["section"], m["sentence"])
            s = sentences.setdefault(key, {"tested": bool(TEST.search(m["sentence"])), "markers": []})
            types = {t["name"] for t in m["semantic_types"] or []}
            if (m["cui"] and not m["negated"] and (m["score"] or 0) >= MIN_LINK and not EXCLUDE.search(m["concept"] or "")
                    and types & BIOMARKER_TYPES and not HINT_STOP.search(m["concept"])):
                if m["concept"] not in s["markers"]:
                    s["markers"].append(m["concept"])
                concepts[m["cui"]] = m["concept"]
                arts[m["cui"]].add(m["id"])

    per = collections.defaultdict(lambda: {"tested": 0, "outcome": 0, "markers": collections.Counter()})
    with open(OUT / "candidate_sentences.jsonl", "w", encoding="utf-8") as fh:
        for (aid, section, sent), s in sentences.items():
            fh.write(json.dumps({"id": aid, "section": section, "tested": s["tested"], "sentence": sent,
                                 "marker_hints": s["markers"]}, ensure_ascii=False) + "\n")
            p = per[aid]
            p["tested" if s["tested"] else "outcome"] += 1
            p["markers"].update(s["markers"])

    rows, skipped = [], collections.Counter()
    for aid, p in per.items():
        c, rec = cats.get(aid, {}), recs.get(aid, {})
        if c.get("scope_label") == "human comparator" or aid.startswith("HU"):
            skipped["human comparator"] += 1
            continue
        if c.get("aim") == "REV" or rec.get("include_type") == "review":
            skipped["review"] += 1
            continue
        if rec.get("include_type") == "case_report":
            skipped["case report"] += 1
            continue
        full = c.get("source_format", "abstract") != "abstract"
        score = (2 * p["tested"] + p["outcome"] + AIM_BONUS.get(c.get("aim"), 0)
                 + float(c.get("score_SEV") or 0))
        tier = ("A" if full and p["tested"] >= 2 else
                "B" if full or p["tested"] >= 1 else "C")
        rows.append({"id": aid, "tier": tier, "rank_score": round(score, 2), "tested_sentences": p["tested"],
                     "outcome_sentences": p["outcome"], "source_format": c.get("source_format", ""),
                     "aim": c.get("aim", ""), "nlp_primary": c.get("nlp_primary", ""),
                     "species": rec.get("species_short", ""), "n_infected": rec.get("n_infected_dogs") or "",
                     "design": rec.get("design", ""), "cohort": rec.get("cohort_id") or "",
                     "marker_hints": "; ".join(m for m, _ in p["markers"].most_common(12)),
                     "title": c.get("title") or rec.get("title", "")})
    rows.sort(key=lambda r: (r["tier"], -r["rank_score"]))
    with open(OUT / "shortlist.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    mrows = build_map(concepts, arts)
    tiers = collections.Counter(r["tier"] for r in rows)
    print(f"candidate sentences: {len(sentences)} ({sum(s['tested'] for s in sentences.values())} tested)")
    print(f"shortlist: {len(rows)} articles  " + "  ".join(f"tier {t}: {tiers[t]}" for t in "ABC")
          + f"  (left out: {dict(skipped)})")
    unmatched = sum(1 for r in mrows if r["source"] == "scispacy" and not r["marker"])
    print(f"marker map: {len(mrows)} rows, {sum(r['source'] == 'seed' for r in mrows)} canonical, "
          f"{unmatched} scispaCy aliases unmatched")


if __name__ == "__main__":
    main()
