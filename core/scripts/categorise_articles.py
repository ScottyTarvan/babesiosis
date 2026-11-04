"""Assign each article a primary pathophysiological category (and secondary tags) from its extracted UMLS
concepts, and compare with the categories the review's screening agents assigned.

Categories are the review's 11 (research-map.md): ERY, INF, END, COA, REN, PUL, NEU, CAR, MET, OXO, SEV.

1. Concept map (data/syndromes/category_map.csv). Every concept in mentions.jsonl gets a category from name
   rules (RULES, first match wins, so "immune-mediated haemolytic anaemia" is ERY before INF), or none.
   Routine panel analytes and counts (albumin, ALP, platelet count...) and method terms (ELISA, gene
   expression) are excluded: being measured is not a finding. Rules apply to disorder concepts and, for
   mechanism categories, to biomarker-type concepts (proteins,
   enzymes, hormones, immune factors, laboratory/diagnostic procedures); cells, organisms and generic
   qualifiers are never mapped. The file is meant for editing: rows with source "manual" are kept as they
   are when the map is regenerated; set category to "-" to exclude a concept.
2. Scores. For each article and category: sum over the category's concepts of
       idf(concept) * log(1 + sum of location weights of its non-negated mentions)
   Only mentions linked with score >= MIN_LINK count. A leukogram family (neutrophilia, lymphopenia, ...)
   contributes once per article, its strongest concept. Two scores per category: studied, from what the
   article measured (title 6, abstract 3, results/case 2, conclusion 2, unlabelled 1.5, methods 1, other
   headings 1), and mentioned, from the introduction and discussion (weight 1; studied for reviews), which mostly describe what
   the disease can cause. idf = ln((N+1)/(df+1)) + 1 over articles, so concepts reported almost everywhere
   (anaemia, thrombocytopenia) weigh less.
3. Primary. No mapped evidence: none. Else, if three or more organ categories each reach SEV_SPREAD of the
   top organ score, or SEV itself is top: SEV (multisystem phenotype/outcome, the review's own rule).
   Else the top category; `confidence` is top/second (high >= MARGIN). Secondary: categories >= SECONDARY of top.
   All from the studied scores. Mentioned: other categories whose studied + mentioned score >= MENTIONED_MIN.
   Study aim (AIMS): rule-based, from the title, then the abstract's objective sentence (AIM_RULES).
4. Comparison with the agent labels in articles.jsonl (agent_primary_category, agent_secondary_tags). These
   were assigned by LLM agents without human review, so this measures agreement between two automatic
   methods, not accuracy. nlp_primary and nlp_secondary are the review's categories: build_outputs.py
   copies them into articles.jsonl primary_category / secondary_tags. There is no human review step.

Outputs in data/syndromes/: category_map.csv, article_categories.csv, category_comparison.md

Usage (from canine-babesiosis-review/; standard library only):
    python -I scripts/categorise_articles.py
"""
import collections
import csv
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SYN = ROOT / "data" / "syndromes"
MAP = SYN / "category_map.csv"
CATS = ["ERY", "INF", "END", "COA", "REN", "PUL", "NEU", "CAR", "MET", "OXO", "SEV"]
# categories whose spread makes an article multisystem (SEV); INF included, a multisystem picture usually has it
ORGAN = ["ERY", "COA", "REN", "PUL", "NEU", "CAR", "MET", "END", "INF"]
# Studied: what the article measured and reported. Other headings (a review's own topic sections) count 1.
WEIGHTS = {"title": 6, "abstract": 3, "results": 2, "case": 2, "results_discussion": 2, "conclusion": 2,
           "unlabelled": 1.5, "methods": 1}
# Mentioned only: background and discussion of what the disease can cause, usually citing other studies
MENTION_SECTIONS = {"introduction", "discussion"}
MARGIN, SEV_SPREAD, SECONDARY = 1.5, 0.6, 0.35
MENTIONED_MIN = 4.0  # combined score a non-studied category needs to be listed as mentioned
MIN_LINK = 0.9  # UMLS link score needed for a mention to count (mislinks cluster below it)
# Leukogram changes are one finding family: a routine differential reports several at once, so per article
# the family contributes once (its strongest concept) instead of stacking up INF
LEUKOGRAM = re.compile(r"leu[ck]o(cyt|pen)|neutro(phil|pen)|lympho(cyt|pen)|monocyt|eosino(phil|pen)|basophil|"
                       r"white blood cell|leu[ck]ocyte count|neutrophil count|lymphocyte count", re.I)

# Concepts never categorised: the infection under study, generic disease words, qualifiers
EXCLUDE = re.compile(r"babesi|piroplasm|theileri|hepatozo|ehrlichi|anaplasm|leishman|malaria|plasmodium|tick|parasit(e|ic disease)s?$|"
                     r"^(disease|diseases|syndrome|infection|infections|communicable diseases|complication|finding|reduced|infected|"
                     r"observation parameter|abnormal|abnormality|illness|disorder|signs and symptoms|symptoms|lesion|pathology|"
                     r"tissue damage|injury|chronic disease|acute disease|tick-borne diseases|infections of musculoskeletal system|"
                     # methods, not findings
                     r"enzyme-linked immunosorbent assay|gene expression|antibodies|immune|immune response|immunoassay)$|"
                     r"immunofluoresc|fluorescent antibody|antibody titer|radioimmunoassay|complement fixation|serolog|"
                     # routine panel analytes and counts: being measured is not a finding (abnormal states still count)
                     r"^(albumins?|serum albumin|alkaline phosphatase|alanine (transaminase|aminotransferase)|aspartate (transaminase|aminotransferase)|"
                     r"glucose|blood glucose|cholesterol|creatinine|urea|blood urea nitrogen|bilirubin|total protein|globulins?|calcium|"
                     r"phosphates?|sodium|potassium|chlorides?|hemoglobin|haemoglobin|hematocrit|"
                     r"[\w ,-]*count measurement|hematocrit procedure|hemoglobin measurement|[\w ]*concentration measurement)$", re.I)
# Name rules, first match wins (ERY before INF so immune-mediated haemolysis is ERY; SEV outcomes first)
RULES = [
    ("SEV", r"cessation of life|death|mortality|multiple organ (failure|dysfunction)|\bmods\b|critical illness|moribund|fatal outcome"),
    ("ERY", r"an(a)?emi|h(a)?emoly|h(a)?emoglobin(uria|emia|aemia)|spherocyt|autoagglutin|agglutination|reticulocyt|anisocyt|"
            r"polychromas|erythro(cyt|pen|phag|blast)|red (blood )?cell|icter|jaundice|hyperbilirubin|bilirubinuria|pallor|"
            r"coombs|erythropoie|dyserythrop|h(a)?ematocrit decreased|pancytopeni"),
    ("COA", r"thrombocytop|platelet|coagul|disseminated intravascular|\bdic\b|h(a)?emorrhag|bleeding|petechi|ecchym|purpura|"
            r"thrombo(sis|embol|tic|cytosis)|fibrin|epistaxis|mel(a)?ena|hematochezia|d-dimer|antithrombin|prothrombin|"
            r"thromboplastin|von willebrand|thrombin"),
    ("REN", r"kidney|renal|nephr|azot(a)?emi|ur(a)?emi|proteinuri|glomerul|tubul|oliguri|anuri|polyuri|creatinine|cystatin|"
            r"urinary|urine protein|h(a)?ematuria|pigmenturia"),
    ("PUL", r"lung|pulmonar|respiratory distress|\bards\b|pneumon|dyspn|tachypn|pleural|hypox(a)?emi|respiratory (failure|insufficiency)|"
            r"bronch|thoracic radiograph|blood gas"),
    ("NEU", r"cerebr|brain|seizure|convuls|\bcoma\b|neurolog|ataxi|nystagm|pares[ie]s|stupor|encephal|mening|mental status|"
            r"consciousness|tremor|opisthotonus|nervous system"),
    ("CAR", r"cardi|myocard|arrhythm|tachycardia|bradycardia|\bheart\b|troponin|ventricul|atrial|pericard|electrocardiogra|"
            r"echocardiogra|natriuretic"),
    ("MET", r"hypoglyc|hyperglyc|glucose|hepat|liver|cholest|bile|acidos|alkalos|acid-base|electrolyte|hypokal|hyponatr|hyperkal|"
            r"hypernatr|hypocalc|hypercalc|hypophosph|hyperphosph|hypochlor|hyperchlor|pancrea|lipase|amylase|endocrin|thyro|"
            r"cortisol|adrenal|hypoadren|insulin|alanine aminotransferase|aspartate aminotransferase|alkaline phosphatase|"
            r"gamma-glutamyl|hypoalbumin|hypoprotein|albumin|dehydrat|ketos|lipid metab|cholesterol|triglycer"),
    ("END", r"endotheli|vascul(itis|ar (leak|permeab|injur))|microcirc|perfusion|tissue hypoxia|^hypoxia$|isch(a)?emi|shock|"
            r"hypotens|capillary (leak|refill)|lactat|angiopoietin|glycocalyx|syndecan|vasculopath|edema|oedema|nitric oxide"),
    ("INF", r"inflamm|systemic inflammatory|\bsirs\b|sepsis|septic|cytokine|interleukin|tumou?r necrosis|interferon|chemokine|"
            r"acute[- ]phase|c-reactive|haptoglobin|serum amyloid|ceruloplasmin|leukocyt|leucocyt|leukopeni|leucopeni|neutroph|"
            r"lymphocyt|lymphopeni|monocyt|eosinop|fever|pyrexi|hyperthermi|immun|antibod|splenomegal|lymphadenopath|"
            r"complement|macrophage activation|hemophagocyt|ferritin|hepcidin"),
    ("OXO", r"oxidat|antioxid|malondialdehyde|lipid peroxid|peroxid|glutathione|superoxide|catalase|free radical|reactive oxygen|"
            r"paraoxonase|isoprostane|proteom|transcriptom|metabolom|genom|virulence|gene expression|polymorphism|microbiom"),
]
DISORDER_TYPES = {"Acquired Abnormality", "Anatomical Abnormality", "Cell or Molecular Dysfunction", "Congenital Abnormality",
                  "Disease or Syndrome", "Experimental Model of Disease", "Finding", "Injury or Poisoning",
                  "Mental or Behavioral Dysfunction", "Neoplastic Process", "Pathologic Function", "Sign or Symptom"}
# non-disorder concepts that can carry a category (biomarkers, tests); cells, organisms, qualifiers never do
BIOMARKER_TYPES = {"Amino Acid, Peptide, or Protein", "Biologically Active Substance", "Enzyme", "Immunologic Factor", "Hormone",
                   "Lipid", "Organic Chemical", "Inorganic Chemical", "Element, Ion, or Isotope", "Cell Function",
                   "Molecular Function", "Genetic Function", "Laboratory Procedure", "Diagnostic Procedure", "Organism Function",
                   "Physiologic Function", "Organ or Tissue Function", "Laboratory or Test Result", "Clinical Attribute"}


def rule_category(name, types, disorder):
    if not name or EXCLUDE.search(name):
        return "-", "excluded (study infection or generic term)"
    if not disorder and not set(types) & BIOMARKER_TYPES:
        return "-", "non-disorder type not used"
    low = name.lower()
    for cat, pat in RULES:
        if re.search(pat, low):
            return cat, f"rule {cat}"
    return "-", "no rule matched"


# Study aim, from the title, then the objective sentence of the abstract (first match wins per text)
AIMS = {
    "PREV": "Prevalence, epidemiology, risk factors",
    "DIAG": "Diagnostic or detection method (PCR, serology, smear, test accuracy)",
    "BIOM": "Biomarker or pathophysiology linked to severity or outcome",
    "CLIN": "Clinical and laboratory description of natural cases (case series)",
    "CASE": "Single case report",
    "TRT": "Treatment or drug efficacy",
    "PREVN": "Prevention: vaccine, acaricide, vector control",
    "EXP": "Experimental infection or pathogenesis model",
    "MOL": "Parasite molecular characterisation, genotyping, phylogeny",
    "REV": "Review",
}
AIM_RULES = [
    ("EXP", r"experimental(ly)? (infect|inocul|model|babesi)|inoculated (with|dogs)|challenge (infection|study)"),
    ("PREVN", r"vaccin|acaricid|prophyla|\bprevent|repellen|collar|fluralaner|afoxolaner|sarolaner|lotilaner|tick control"),
    ("TRT", r"efficacy|therapeutic|\btreatment (of|with|outcome)|imidocarb|atovaquone|diminazene|clindamycin|azithromycin|"
            r"buparvaquone|drug"),
    ("DIAG", r"diagnostic (performance|accuracy|test)|(develop|evaluat|compar|validat|novel|new|improved)\w* .{0,40}"
             r"\b(assays?|pcr|lamp|elisa|tests?|methods?|techniques?)\b|sensitivity and specificity|point-of-care|rapid test|loop-mediated"),
    ("PREV", r"prevalen|seroprevalen|epidemiolog|risk factor|survey|occurrence|geographic|distribution of|seroepidem|"
             r"molecular detectionb|risk (assessment|analysis)|detection of babesi|frequency of|in (stray|shelter|hunting|owned) dogs"),
    ("MOL", r"genotyp|phylogen|genetic(ally)? (divers|characteri|variab|distinct)|molecular characteri|strains?\b|isolates?\b|18s|"
            r"sequence analysis|\bbc28|merozoite surface|virulence factor|parasite gene"),
    ("BIOM", r"biomarker|marker|predict|prognos|severity|severe|outcome|surviv|mortality|associat|correlat|concentration|"
             r"activit(y|ies)|\bserum\b|plasma|levels?\b"),
    ("CLIN", r"clinical|haematolog|hematolog|clinicopatholog|laboratory|findings|naturally (occurring|infected)|retrospective|"
             r"case series|presentation|complication"),
]
OBJECTIVE = re.compile(r"[^.]*\b(aims?|aimed|objectives?|purpose|goal|we (investigated|evaluated|assessed|determined|describe|"
                       r"compared|report|examined|studied)|this study|the present study)\b[^.]*\.", re.I)


def article_text(aid):
    md = ROOT / "data" / "markdown"
    p = md / f"{aid}.en.md" if (md / f"{aid}.en.md").exists() else md / f"{aid}.md"
    if not p.exists():
        return ""
    body = p.read_text(encoding="utf-8").split("\n---\n", 1)[-1]
    m = re.search(r"^## Abstract\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    return m.group(1) if m else body[:3000]


def study_aim(a, abstract):
    """(aim, evidence): REV and CASE from the screening record, else the first rule matching the title, then the objective."""
    design = (a.get("design") or "").lower()
    if a.get("include_type") == "review" or "review" in design:
        return "REV", "record: review"
    if a.get("include_type") == "case_report" or re.search(r"\bcase report", design):
        return "CASE", "record: case report"
    obj = OBJECTIVE.search(abstract)
    for where, text in (("title", a["title"]), ("objective", obj.group(0) if obj else "")):
        for aim, pat in AIM_RULES:
            m = re.search(pat, text, re.I)
            if m:
                return aim, f"{where}: {m.group(0).strip()}"
    m = re.search(AIM_RULES[-2][1], abstract, re.I)  # BIOM wording anywhere in the abstract, else CLIN
    return ("BIOM", f"abstract: {m.group(0)}") if m else ("CLIN", "default")


def build_map(mentions):
    old = {}
    if MAP.exists():
        with open(MAP, encoding="utf-8") as fh:
            old = {r["cui"]: r for r in csv.DictReader(fh)}
    info = {}
    arts = collections.defaultdict(set)
    for m in mentions:
        if not m["cui"]:
            continue
        info.setdefault(m["cui"], (m["concept"], [t["name"] for t in m["semantic_types"]], m["disorder"]))
        arts[m["cui"]].add(m["id"])
    rows = []
    for cui, (name, types, disorder) in info.items():
        if old.get(cui, {}).get("source") == "manual":
            r = dict(old[cui])
        else:
            cat, why = rule_category(name, types, disorder)
            r = {"cui": cui, "concept": name, "semantic_types": "; ".join(types), "category": cat, "source": "rule", "note": why}
        r["articles"] = len(arts[cui])
        rows.append(r)
    rows.sort(key=lambda r: (-int(r["articles"]), r["concept"]))
    with open(MAP, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["cui", "concept", "semantic_types", "category", "source", "note", "articles"])
        w.writeheader()
        w.writerows(rows)
    return {r["cui"]: r["category"] for r in rows}


def main():
    mentions = [json.loads(l) for l in open(SYN / "mentions.jsonl", encoding="utf-8")]
    arts = {a["id"]: a for a in map(json.loads, open(ROOT / "articles.jsonl", encoding="utf-8"))}
    cmap = build_map(mentions)
    used = [m for m in mentions if m["cui"] and not m["negated"] and (m["score"] or 0) >= MIN_LINK
            and cmap.get(m["cui"], "-") in CATS]
    docs = {m["id"] for m in mentions} | set(arts)
    seen = collections.defaultdict(set)
    for m in used:
        seen[m["cui"]].add(m["id"])
    n = len(docs)
    idf = {c: math.log((n + 1) / (len(ids) + 1)) + 1 for c, ids in seen.items()}

    names = {m["cui"]: m["concept"] for m in used}
    evidence = collections.defaultdict(lambda: collections.defaultdict(list))

    def score(ms, ev=None):
        weight = collections.defaultdict(float)  # (article, cui) -> summed location weight
        for m in ms:
            weight[(m["id"], m["cui"])] += 1.0 if m["section"] in MENTION_SECTIONS else WEIGHTS.get(m["section"], 1.0)
        out = collections.defaultdict(lambda: collections.defaultdict(float))
        leuko = collections.defaultdict(lambda: collections.defaultdict(float))
        for (aid, cui), w in weight.items():
            cat = cmap[cui]
            s = idf[cui] * math.log1p(w)
            if LEUKOGRAM.search(names[cui]):
                leuko[aid][cat] = max(leuko[aid][cat], s)
            else:
                out[aid][cat] += s
            if ev is not None:
                ev[aid][cat].append((s, names[cui]))
        for aid, by_cat in leuko.items():
            for cat, s in by_cat.items():
                out[aid][cat] += s
        return out

    # a review studies the literature, so its introduction and discussion are its content, not background
    aims = {aid: study_aim(a, article_text(aid)) for aid, a in arts.items()}
    is_rev = lambda m: aims.get(m["id"], ("",))[0] == "REV"
    scores = score([m for m in used if m["section"] not in MENTION_SECTIONS or is_rev(m)], evidence)  # studied
    mscores = score([m for m in used if m["section"] in MENTION_SECTIONS and not is_rev(m)])  # mentioned only

    fmt = {}
    for m in mentions:
        fmt.setdefault(m["id"], m["source_format"])
    rows = []
    for aid in sorted(arts):
        a, sc = arts[aid], scores.get(aid, {})
        ranked = sorted(((sc.get(c, 0.0), c) for c in CATS), reverse=True)
        top_s, top = ranked[0]
        second_s = ranked[1][0]
        organ = sorted((sc.get(c, 0.0) for c in ORGAN), reverse=True)
        if top_s == 0:
            primary, conf = "none", "none"
        else:
            spread = sum(s >= SEV_SPREAD * organ[0] for s in organ if s > 0) if organ[0] else 0
            primary = "SEV" if top == "SEV" or spread >= 3 else top
            ratio = top_s / second_s if second_s else float("inf")
            conf = "high" if ratio >= MARGIN and primary == top else "low"
        p_score = sc.get(primary, top_s) if primary != "none" else 0
        secondary = [c for s, c in ranked if c != primary and s > 0 and s >= SECONDARY * max(top_s, p_score)]
        msc = mscores.get(aid, {})
        mentioned = [c for c in CATS if c != primary and c not in secondary and sc.get(c, 0.0) + msc.get(c, 0.0) >= MENTIONED_MIN]
        aim, aim_ev = aims[aid]
        # articles.jsonl primary_category is now this script's own result (build_outputs.py); the agents' labels
        # are kept in agent_primary_category / agent_secondary_tags.
        # Rows that build_outputs.py categorised (category_source set) keep the agents' labels in agent_*;
        # supporting HU/BG rows keep their own labels.
        own = bool(a.get("category_source"))
        ap = a.get("agent_primary_category") if own else a.get("primary_category")
        agent_p = ap if ap in CATS else None
        agent_s = [t for t in (a.get("agent_secondary_tags" if own else "secondary_tags") or []) if t in CATS]
        ev = sorted(evidence[aid].get(primary, []), reverse=True)[:5] if primary in CATS else []
        rows.append({"id": aid, "title": a["title"], "scope_label": a["scope_label"], "source_format": fmt.get(aid),
                     "aim": aim, "aim_evidence": aim_ev,
                     "nlp_primary": primary, "confidence": conf, "nlp_secondary": " ".join(secondary),
                     "nlp_mentioned": " ".join(mentioned),
                     "agent_primary": agent_p or "", "agent_secondary": " ".join(agent_s),
                     "agree_primary": (primary == agent_p) if agent_p else "",
                     "agent_primary_in_nlp": (agent_p == primary or agent_p in secondary) if agent_p else "",
                     "primary_evidence": "; ".join(f"{nm} ({s:.1f})" for s, nm in ev),
                     **{f"score_{c}": round(sc.get(c, 0.0), 2) for c in CATS},
                     **{f"mscore_{c}": round(msc.get(c, 0.0), 2) for c in CATS}})
    with open(SYN / "article_categories.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    write_comparison(rows)


def kappa(pairs, labels):
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    pe = sum(ca[l] * cb[l] for l in labels) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def write_comparison(rows):
    lab = [r for r in rows if r["agent_primary"]]
    pairs = [(r["nlp_primary"], r["agent_primary"]) for r in lab]
    agree = sum(a == b for a, b in pairs)
    within = sum(r["agent_primary_in_nlp"] is True for r in lab)
    hi = [r for r in lab if r["confidence"] == "high"]
    L = ["# Category comparison: scispaCy scoring vs agent labels", "",
         "The agent labels (articles.jsonl `primary_category`, `secondary_tags`) were assigned by LLM agents without human "
         "review, so this is agreement between two automatic methods, not accuracy. Articles where they disagree are the "
         "first candidates for human review. Method: `scripts/categorise_articles.py`.", "",
         f"- Articles with an agent primary category: {len(lab)}",
         f"- Same primary category: {agree} ({agree / len(lab):.0%}); Cohen's kappa {kappa(pairs, CATS + ['none']):.2f}",
         f"- Agent primary found among the scispaCy primary or secondary categories: {within} ({within / len(lab):.0%})",
         f"- High-confidence scispaCy primaries: {len(hi)}, of which {sum(r['agree_primary'] is True for r in hi)} agree "
         f"({sum(r['agree_primary'] is True for r in hi) / max(1, len(hi)):.0%})",
         f"- Abstract-only articles: agreement {sum(r['agree_primary'] is True for r in lab if r['source_format'] == 'abstract')}"
         f" / {sum(r['source_format'] == 'abstract' for r in lab)}; full text "
         f"{sum(r['agree_primary'] is True for r in lab if r['source_format'] != 'abstract')} / {sum(r['source_format'] != 'abstract' for r in lab)}",
         "", "## Confusion matrix", "", "Rows: agent primary. Columns: scispaCy primary.", "",
         "| agent \\ scispaCy | " + " | ".join(CATS + ["none"]) + " | total |", "|---" * (len(CATS) + 3) + "|"]
    cm = collections.Counter(pairs)
    for c in CATS:
        L.append(f"| **{c}** | " + " | ".join(str(cm[(x, c)] or "") for x in CATS + ["none"]) + f" | {sum(cm[(x, c)] for x in CATS + ['none'])} |")
    L += ["", "## Per category", "", "| Category | Agent primary | scispaCy primary | Both | Agreement (of agent's) |", "|---|---|---|---|---|"]
    for c in CATS:
        a_n = sum(b == c for _, b in pairs)
        n_n = sum(a == c for a, _ in pairs)
        both = cm[(c, c)]
        L.append(f"| {c} | {a_n} | {n_n} | {both} | {both / a_n:.0%} |" if a_n else f"| {c} | 0 | {n_n} | 0 | |")
    aims = collections.Counter(r["aim"] for r in rows)
    L += ["", "## Study aim (rule-based)", "", "From the title, then the abstract's objective sentence; REV and CASE from the screening record.", "",
          "| Aim | Articles | Description |", "|---|---|---|"]
    L += [f"| {k} | {aims[k]} | {v} |" for k, v in AIMS.items()]
    L += ["", "## Disagreements", "", "Sorted with high-confidence scispaCy calls first (most likely to be informative).", "",
          "| ID | Title | Agent | scispaCy | Confidence | scispaCy secondary | Evidence for scispaCy primary |", "|---|---|---|---|---|---|---|"]
    for r in sorted((r for r in lab if r["agree_primary"] is not True), key=lambda r: (r["confidence"] != "high", r["id"])):
        L.append(f"| {r['id']} | {r['title'][:70].replace('|', '/')} | {r['agent_primary']} | {r['nlp_primary']} | {r['confidence']} | "
                 f"{r['nlp_secondary']} | {r['primary_evidence'][:120].replace('|', '/')} |")
    (SYN / "category_comparison.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(lab)} labelled; same primary {agree} ({agree / len(lab):.0%}); agent primary within scispaCy categories {within} ({within / len(lab):.0%})")


if __name__ == "__main__":
    main()
