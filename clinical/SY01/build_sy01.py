"""Build SY01.json: named citation keys [@x] are renumbered R1.. in order of first use."""
import json, re, sys

OUT = sys.argv[1]

REFS = {
 "leis19": dict(authors="Leisewitz AL, Goddard A, Clift S, et al.", year=2019, title="A clinical and pathological description of 320 cases of naturally acquired Babesia rossi infection in dogs", journal="Veterinary Parasitology", volume_pages="271:22-30", doi="10.1016/j.vetpar.2019.06.005", pmid="31303199", url="", article_id="CB040", type="cohort", species="B. rossi", n_dogs=320, read="full text"),
 "reyers98": dict(authors="Reyers F, Leisewitz AL, Lobetti RG, et al.", year=1998, title="Canine babesiosis in South Africa: more than one disease. Does this serve as a model for falciparum malaria?", journal="Annals of Tropical Medicine and Parasitology", volume_pages="92(4):503-511", doi="10.1080/00034989859474", pmid="9683901", url="", article_id="", type="cohort", species="B. rossi", n_dogs=662, read="abstract"),
 "scheep11": dict(authors="Scheepers E, Leisewitz AL, Thompson PN, et al.", year=2011, title="Serial haematology results in transfused and non-transfused dogs naturally infected with Babesia rossi", journal="Journal of the South African Veterinary Association", volume_pages="82(3):136-143", doi="10.4102/jsava.v82i3.51", pmid="22332296", url="", article_id="CB418", type="cohort", species="B. rossi", n_dogs=86, read="full text"),
 "leis23": dict(authors="Leisewitz AL, Mrljak V, Dear JD, et al.", year=2023, title="The diverse pathogenicity of various Babesia parasite species that infect dogs", journal="Pathogens", volume_pages="12(12):1437", doi="10.3390/pathogens12121437", pmid="38133320", url="", article_id="CB119", type="review", species="B. rossi, B. canis, B. vogeli, B. gibsoni", n_dogs=None, read="full text"),
 "jac06": dict(authors="Jacobson LS", year=2006, title="The South African form of severe and complicated canine babesiosis: clinical advances 1994-2004", journal="Veterinary Parasitology", volume_pages="138(1-2):126-139", doi="10.1016/j.vetpar.2006.01.047", pmid="16503090", url="", article_id="", type="review", species="B. rossi", n_dogs=None, read="abstract"),
 "zamb09": dict(authors="Zambelli AB, Leisewitz AL", year=2009, title="A prospective, randomized comparison of Oxyglobin (HB-200) and packed red blood cell transfusion for canine babesiosis", journal="Journal of Veterinary Emergency and Critical Care", volume_pages="19(1):102-112", doi="10.1111/j.1476-4431.2009.00386.x", pmid="19691591", url="", article_id="CB368", type="trial", species="B. rossi", n_dogs=12, read="abstract"),
 "nel04": dict(authors="Nel M, Lobetti RG, Keller N, et al.", year=2004, title="Prognostic value of blood lactate, blood glucose, and hematocrit in canine babesiosis", journal="Journal of Veterinary Internal Medicine", volume_pages="18(4):471-476", doi="10.1892/0891-6640(2004)18<471:pvoblb>2.0.co;2", pmid="15320582", url="", article_id="", type="cohort", species="B. rossi", n_dogs=90, read="abstract"),
 "keller04": dict(authors="Keller N, Jacobson LS, Nel M, et al.", year=2004, title="Prevalence and risk factors of hypoglycemia in virulent canine babesiosis", journal="Journal of Veterinary Internal Medicine", volume_pages="18(3):265-270", doi="10.1892/0891-6640(2004)18<265:parfoh>2.0.co;2", pmid="15188810", url="", article_id="", type="cohort", species="B. rossi", n_dogs=250, read="abstract"),
 "koster15": dict(authors="Köster LS, Lobetti RG, Kelly P", year=2015, title="Canine babesiosis: a perspective on clinical complications, biomarkers, and treatment", journal="Veterinary Medicine: Research and Reports", volume_pages="6:119-128", doi="10.2147/VMRR.S60431", pmid="30155438", url="", article_id="CB493", type="review", species="", n_dogs=None, read="full text"),
 "bumby24": dict(authors="Bumby MM, Clift SJ, Hooijberg EH, et al.", year=2024, title="Cytological and histopathological bone marrow findings in dogs with natural Babesia rossi infection", journal="Journal of the South African Veterinary Association", volume_pages="95(2):156-166", doi="10.36303/JSAVA.626", pmid="39995030", url="", article_id="CB129", type="case series", species="B. rossi", n_dogs=6, read="abstract"),
 "destef22": dict(authors="DeStefano IM, Wayne AS, Cudney SE, et al.", year=2022, title="Successful treatment of suspect Babesia-induced ARDS in a dog using lung-protective positive-pressure ventilation and neuromuscular blockade", journal="Clinical Case Reports", volume_pages="10(8):e6234", doi="10.1002/ccr3.6234", pmid="35957771", url="", article_id="CB102", type="case report", species="B. vogeli", n_dogs=1, read="full text"),
 "karas22": dict(authors="Karasová M, Tóthová C, Grelová S, et al.", year=2022, title="The etiology, incidence, pathogenesis, diagnostics, and treatment of canine babesiosis caused by Babesia gibsoni infection", journal="Animals", volume_pages="12(6):739", doi="10.3390/ani12060739", pmid="35327136", url="", article_id="CB094", type="review", species="B. gibsoni", n_dogs=None, read="full text"),
 "bohm06": dict(authors="Böhm M, Leisewitz AL, Thompson PN, et al.", year=2006, title="Capillary and venous Babesia canis rossi parasitaemias and their association with outcome of infection and circulatory compromise", journal="Veterinary Parasitology", volume_pages="141(1-2):18-29", doi="10.1016/j.vetpar.2006.05.002", pmid="16806713", url="", article_id="", type="cohort", species="B. rossi", n_dogs=100, read="abstract"),
 "piane16": dict(authors="Piane L, Young KM, Giraud L, et al.", year=2016, title="Spurious reticulocyte profiles in dogs with large form babesiosis: a retrospective study", journal="Veterinary Clinical Pathology", volume_pages="45(4):598-603", doi="10.1111/vcp.12396", pmid="27701759", url="", article_id="CB538", type="case series", species="large Babesia (unnamed)", n_dogs=92, read="abstract"),
 "merck": dict(authors="Blois S", year=2024, title="Blood transfusions in animals (Merck Veterinary Manual; reviewed Nov 2024, modified Mar 2026)", journal="Merck Veterinary Manual", volume_pages="online", doi="", pmid="", url="https://www.merckvetmanual.com/circulatory-system/blood-groups-and-blood-transfusions/blood-transfusions-in-animals", article_id="", type="textbook", species="", n_dogs=None, read="full text"),
 "herter22": dict(authors="Herter L, Weingart C, Merten N, et al.", year=2022, title="Alloimmunization in dogs after transfusion: a serial cross-match study", journal="Journal of Veterinary Internal Medicine", volume_pages="36(5):1660-1668", doi="10.1111/jvim.16521", pmid="36161382", url="", article_id="", type="cohort", species="", n_dogs=21, read="abstract"),
 "collett00": dict(authors="Collett MG", year=2000, title="Survey of canine babesiosis in South Africa", journal="Journal of the South African Veterinary Association", volume_pages="71(3):180-186", doi="10.4102/jsava.v71i3.710", pmid="11205168", url="", article_id="", type="case series", species="B. rossi", n_dogs=None, read="abstract"),
 "mathews26": dict(authors="Mathews SM, Ajith Y, Madhavan Unny N, et al.", year=2026, title="Clinicopathological evaluation and molecular detection of haemoparasites in severely anaemic dogs referred for emergency blood transfusion", journal="JIVA (Journal of the Indian Veterinary Association, Kerala)", volume_pages="24(2):39-53", doi="10.55296/jiva/24.2.2026.39-53", pmid="", url="", article_id="CB315", type="case series", species="B. gibsoni", n_dogs=13, read="full text"),
 "adebayo25": dict(authors="Adebayo OO, Takeet MI, Oyewusi IK, et al.", year=2025, title="Relationship between dog erythrocyte antigen (DEA) and susceptibility of dogs to babesiosis", journal="BMC Veterinary Research", volume_pages="21(1):684", doi="10.1186/s12917-025-05117-9", pmid="41291669", url="", article_id="CB143", type="cohort", species="Babesia spp.", n_dogs=200, read="full text"),
 "jacswan95": dict(authors="Jacobson LS, Swan GE", year=1995, title="Supportive treatment of canine babesiosis", journal="Journal of the South African Veterinary Association", volume_pages="66(2):95-105", doi="", pmid="8544169", url="", article_id="", type="review", species="B. rossi", n_dogs=None, read="abstract"),
 "halder22": dict(authors="Halder B, Gupta AR", year=2022, title="Haemato-biochemical alteration and therapeutic management of canine babesiosis", journal="Indian Journal of Animal Health", volume_pages="61(2):379-382", doi="10.36062/ijah.2022.05322", pmid="", url="", article_id="CB221", type="case report", species="B. gibsoni", n_dogs=1, read="full text"),
 "klein17": dict(authors="Klein HG", year=2017, title="The red cell storage lesion(s): of dogs and men", journal="Blood Transfusion", volume_pages="15(2):107-111", doi="10.2450/2017.0306-16", pmid="28263166", url="", article_id="", type="review", species="", n_dogs=None, read="abstract"),
 "abakpa23": dict(authors="Abakpa SAV, Mustapha EI, Mshelbwala FM, et al.", year=2023, title="Prevalence and role of anemia in mortalities of dogs with babesiosis", journal="World's Veterinary Journal", volume_pages="13(3):373-378", doi="10.54203/scil.2023.wvj41", pmid="", url="", article_id="CB238", type="cohort", species="Babesia spp. (smear)", n_dogs=80, read="full text"),
}

page = {
 "schema_version": 1,
 "id": "SY01",
 "title": "Severe haemolytic anaemia",
 "updated": "2026-11-12",
 "definition": "Anaemia from intravascular and extravascular haemolysis caused by the parasite, usually with haemoglobinuria. In B. rossi studies, severe anaemia is a haematocrit below 0.15 L/L (15%), the level at which most dogs were transfused [@leis19][@reyers98][@scheep11].",
 "definition_note": "Working definition confirmed, with two changes. The published limit for severe anaemia is a haematocrit below 0.15 L/L, not 'about' 0.15. Haemoglobinuria is common (84% of 320 B. rossi dogs) but is not part of any published definition [@leis23]. Jacobson judged the old split into 'severe' (anaemic) and 'complicated' disease artificial and proposed grouping dogs by severity and prognosis [@jac06].",
 "key_points": [
  "Severe anaemia (haematocrit below 0.15 L/L) was present in about a third of 320 B. rossi dogs, and in half of the admitted dogs of an older Onderstepoort series [@leis19][@reyers98].",
  "Severe anaemia alone did not reliably predict death: mortality was 14.2% with severe anaemia and 8 to 11% with moderate or mild anaemia [@leis19].",
  "Transfusion is standard care. Onderstepoort clinicians used a haematocrit below 0.15 L/L as a guide and also considered collapse [@scheep11].",
  "No study has compared transfusion with no transfusion. The only randomised trial compared packed red cells with a haemoglobin-based oxygen carrier and found similar short-term effects [@zamb09].",
  "Measure glucose and lactate in every severely anaemic dog: hypoglycaemia and persistent hyperlactataemia were associated with death [@nel04][@keller04].",
  "Screen blood donors for Babesia, preferably by PCR [@koster15]."
 ],
 "description": [
  {"heading": "What it is", "text": "Babesia parasites live in red cells, and the anaemia comes from intravascular and extravascular haemolysis. In B. rossi the haemolysis can be fast enough to make the urine black and the plasma port-wine coloured [@leis23]. In B. rossi dogs the anaemia was normocytic and normochromic, and only mildly to moderately regenerative [@scheep11]."},
  {"heading": "How common, and in which dogs", "text": "Of 320 B. rossi dogs, 35.6% were severely, 25.5% moderately and 22.1% mildly anaemic, and 15.7% had a normal haematocrit [@leis19]. B. canis causes mostly mild to moderate anaemia, and few of these dogs are transfused [@leis23]. Severely anaemic B. rossi dogs were young: mean age 0.83 years against 2.66 years in non-anaemic dogs [@reyers98], and transfused dogs had a median age of 10 months against 21 months [@scheep11]."},
  {"heading": "When in the course of disease", "text": "Dogs are usually anaemic when they present. In non-transfused B. rossi dogs the haematocrit fell further on day 1 after diminazene, then rose. On day 6 the median was 0.36 L/L without and 0.31 L/L with transfusion, still below the reference interval [@scheep11]. Most B. rossi dogs that die do so in the first 24 h in hospital [@leis23]."},
  {"heading": "Mechanism", "text": "The marrow response is weaker than the haemolysis would predict. The absolute reticulocyte count was below 100 x 10^9/L in 61.9% of the B. rossi dogs tested [@leis19]. The marrow of fatal cases showed dyserythropoiesis and more stored iron [@bumby24]. Tissue hypoxia is thought to drive much of the disease [@jac06]. In anaemic B. rossi dogs, central venous oxygen tension stayed low even after transfusion [@zamb09]."}
 ],
 "species_notes": [
  {"species": "B. rossi", "note": "The most severe anaemia and the most transfusions. Almost all South African evidence is from this species, mainly from one hospital (Onderstepoort) [@leis19][@leis23]."},
  {"species": "B. canis", "note": "Mostly mild to moderate anaemia. In one series, haemoglobin was visible in the urine or blood in more than two thirds of cases [@leis23]."},
  {"species": "B. vogeli", "note": "The least pathogenic species; haemolytic anaemia is reported less often [@leis23]. One B. vogeli dog had no PCV rise after 15 mL/kg of packed red cells [@destef22]."},
  {"species": "B. gibsoni", "note": "Anaemia in over 80% of 60 dogs; just over 10% had a haematocrit below 0.20 L/L [@leis23]. A review gives a haematocrit below 15% with severe dyspnoea or tachypnoea as the indication for transfusion [@karas22]. For immune-mediated haemolysis, see SY02."}
 ],
 "diagnosis": {
  "criteria": [
   {"criterion": "Severe anaemia", "threshold": "haematocrit below 0.15 L/L (15%)", "basis": "babesiosis", "note": "Used in 320 B. rossi dogs; about a third had it.", "refs": ["@leis19"]},
   {"criterion": "Transfusion guide", "threshold": "haematocrit below 0.15 L/L, or a collapsed dog", "basis": "babesiosis", "note": "A guideline at Onderstepoort, not a fixed rule: the clinical state also decided. A B. gibsoni review: below 15% with severe dyspnoea or tachypnoea.", "refs": ["@scheep11", "@karas22"]},
   {"criterion": "Haemoconcentration (exclude)", "threshold": "haematocrit above 0.55 L/L with haemolysis", "basis": "babesiosis", "note": "3 of 4 such B. rossi dogs died. See SY14.", "refs": ["@leis19"]},
   {"criterion": "Hyperlactataemia", "threshold": "above 5 mmol/L at admission; above 2.5 mmol/L at 8 to 24 h", "basis": "babesiosis", "note": "90 dogs with severe or complicated babesiosis. Converted from the source's units.", "refs": ["@nel04"]},
   {"criterion": "Hypoglycaemia", "threshold": "below 3.3 mmol/L", "basis": "babesiosis", "note": "Converted from the source's units. Present in 19.8% of admitted B. rossi dogs.", "refs": ["@nel04", "@keller04"]}
  ],
  "clinical_signs": [
   {"sign": "Pallor, weakness, collapse", "note": "22.5% of 320 B. rossi dogs were collapsed at presentation. Collapsed dogs had a lower haematocrit.", "refs": ["@leis19"]},
   {"sign": "Haemoglobinuria (red-brown to black urine)", "note": "Present in 84% of 320 B. rossi dogs. Haemoglobin in urine can falsely raise the urine specific gravity.", "refs": ["@leis23", "@leis19"]},
   {"sign": "Haemoglobinaemia (port-wine plasma)", "note": "A sign of rapid intravascular haemolysis, seen in the PCV tube.", "refs": ["@leis23"]},
   {"sign": "Tachycardia, fever, depression, anorexia", "note": "Found in 12 B. rossi dogs with a haematocrit of 0.10 to 0.20 L/L. Blood pressure was normal.", "refs": ["@zamb09"]},
   {"sign": "Icterus", "note": "From haemolysis and liver injury (see SY06). Icterus was a risk factor for hypoglycaemia.", "refs": ["@leis23", "@keller04"]}
  ],
  "tests": [
   {"test": "PCV and total protein (microhaematocrit)", "finding": "Grades the anaemia. Look at the colour of the plasma.", "note": "Basic practice. The decision to transfuse rested on PCV and the clinical state.", "refs": ["@scheep11", "@leis23"]},
   {"test": "Thin smear from ear-tip capillary blood", "finding": "Parasites. Capillary parasitaemia was higher than venous parasitaemia.", "note": "Capillary blood is the best sample for diagnosis.", "refs": ["@bohm06"]},
   {"test": "In-saline agglutination", "finding": "Positive in 10.3% of 320 B. rossi dogs. It did not change the outcome or the haematocrit at admission.", "note": "If positive, see SY02.", "refs": ["@leis19"]},
   {"test": "Blood glucose", "finding": "Hypoglycaemia in 19.8% of admitted dogs. Severe anaemia was a risk factor on univariate analysis.", "note": "The authors advised measuring it in all inpatients, and always in collapsed dogs, puppies and dogs with severe anaemia, vomiting or icterus.", "refs": ["@keller04"]},
   {"test": "Blood lactate, serial", "finding": "Admission and 8 to 24 h values predicted death.", "note": "See the criteria for the limits.", "refs": ["@nel04"]},
   {"test": "Reticulocyte count", "finding": "Usually a weak response at presentation.", "note": "Analyser reticulocyte profiles can be spurious in large-form babesiosis. Check a stained smear.", "refs": ["@leis19", "@piane16"]},
   {"test": "DEA 1 blood typing and cross-match", "finding": "Compatibility of donor and recipient.", "note": "Type donor and recipient for DEA 1. Cross-match any dog that was transfused before.", "refs": ["@merck", "@herter22"]}
  ],
  "differentials": [
   {"condition": "Secondary immune-mediated haemolytic anaemia (SY02)", "distinguish": "Positive in-saline agglutination. Haemolysis that continues after antibabesial treatment.", "refs": ["@leis19"]},
   {"condition": "Haemoconcentrated ('red') babesiosis (SY14)", "distinguish": "A high haematocrit despite haemolysis, with multiple organ failure and a much higher mortality.", "refs": ["@leis19", "@jac06"]},
   {"condition": "Non-regenerative anaemia or marrow failure (SY04)", "distinguish": "No reticulocyte response. In B. rossi a moderate response is expected by day 3 of treatment.", "refs": ["@scheep11"]},
   {"condition": "Ehrlichia canis co-infection", "distinguish": "Look for morulae and test by PCR. A low neutrophil response in babesiosis can be mistaken for ehrlichiosis.", "refs": ["@scheep11"]},
   {"condition": "Collapse from hypoglycaemia", "distinguish": "Measure glucose. Hypoglycaemia should be suspected in any dog with coma or neurological signs.", "refs": ["@keller04"]}
  ],
  "grading": [
   {"grade": "Severe", "criteria": "Haematocrit below 0.15 L/L.", "refs": ["@leis19"]},
   {"grade": "Moderate", "criteria": "Haematocrit 0.15 to 0.24 L/L.", "refs": ["@leis19"]},
   {"grade": "Mild", "criteria": "Haematocrit 0.25 to 0.36 L/L.", "refs": ["@leis19"]}
  ]
 },
 "approach": [
  {"step": 1, "action": "Triage", "detail": "Check for collapse, breathing pattern, mucous membranes and urine colour. Collapse at presentation was strongly associated with death [@leis19]. Measure PCV and total protein, make an ear-tip smear and measure glucose [@bohm06][@keller04].", "setting": "practice"},
  {"step": 2, "action": "Treat the parasite", "detail": "Give antibabesial treatment at diagnosis (see TX00). Expect the haematocrit to fall further over the first day [@scheep11].", "setting": "practice"},
  {"step": 3, "action": "Decide on transfusion", "detail": "Onderstepoort used a haematocrit below 0.15 L/L as a guide and also took collapse into account [@scheep11]. Haematocrit alone did not predict death, so judge the whole dog [@leis19].", "setting": "practice"},
  {"step": 4, "action": "Prepare the blood", "detail": "Donors should test negative for Babesia, preferably by PCR [@koster15]. Type donor and recipient for DEA 1. Cross-match any dog transfused before [@merck][@herter22]. Whole blood and packed red cells gave the same haematology results [@scheep11].", "setting": "practice"},
  {"step": 5, "action": "Give and monitor the transfusion", "detail": "Calculate the volume (see the doses) and give it over about 4 h [@scheep11][@zamb09]. Record vital signs every 15 min for the first hour, then hourly [@merck]. Recheck the PCV after the transfusion and daily [@scheep11].", "setting": "practice"},
  {"step": 6, "action": "Follow lactate and glucose", "detail": "Repeat lactate at 8 to 24 h. A value above 2.5 mmol/L, or a fall of less than 50%, was associated with death [@nel04].", "setting": "practice"},
  {"step": 7, "action": "Intensive care for high-risk dogs", "detail": "Collapse, haemoconcentration, persistent hyperlactataemia and organ complications carried the highest mortality [@leis19][@nel04]. These dogs need intensive care; see SY11.", "setting": "referral"}
 ],
 "treatments": [
  {
   "name": "Packed red cell transfusion",
   "class": "supportive",
   "aim": "To restore oxygen-carrying capacity until the haemolysis stops and the marrow responds.",
   "status": "standard",
   "evidence_level": "A",
   "independent_studies": 2,
   "evidence_summary": "Standard care for severely anaemic B. rossi dogs at Onderstepoort [@scheep11][@leis19]. Of 86 B. rossi dogs, 32 were transfused (median haematocrit 0.09 L/L) and 54 were not (0.28 L/L); 2 died in each group, but the groups were not randomised [@scheep11]. A randomised trial in 12 B. rossi dogs found packed cells and a haemoglobin-based oxygen carrier gave similar blood gas, acid-base and blood pressure results [@zamb09]. No trial compared transfusion with none.",
   "doses": [
    {"drug": "packed red blood cells", "dose": "20 mL/kg", "route": "IV (central venous catheter)", "frequency": "once, over 4 h", "duration": "single dose", "context": "B. rossi, haematocrit 0.10 to 0.20 L/L, randomised trial of 12 dogs", "note": "Followed by lactated Ringer's solution.", "refs": ["@zamb09"]},
    {"drug": "packed red blood cells or whole blood", "dose": "body weight (kg) x 90 x (25 - recipient PCV) / donor PCV, in mL", "route": "IV", "frequency": "once", "duration": "", "context": "B. rossi, 86 dogs, Onderstepoort protocol", "note": "Target PCV 25%. PCV values in %. The same formula was used for whole blood and packed cells.", "refs": ["@scheep11"]},
    {"drug": "packed red blood cells", "dose": "(desired PCV - recipient PCV) / unit PCV x 80 to 90 mL/kg x body weight (kg)", "route": "IV", "frequency": "once", "duration": "", "context": "general canine, veterinary manual", "note": "80 to 90 mL/kg is the estimated blood volume of the dog. Rapid rates for unstable dogs, about 4 h for stable dogs; slower in heart or kidney disease.", "refs": ["@merck"]}
   ],
   "cautions": "Babesia is transmitted in donor blood [@koster15][@karas22]. The haematocrit of transfused dogs rose more slowly, possibly because donor cells were destroyed [@scheep11]. Reactions include fever, haemolysis, circulatory overload and allergy; stop the transfusion if one is suspected [@merck]. In 12 of 21 anaemic dogs, alloantibodies appeared within 4 days of a first transfusion [@herter22]. In a South African survey, most practices never cross-matched, and reactions were said to be rare [@collett00].",
   "monitoring": "Vital signs every 15 min for the first hour, then hourly to the end, and again 15 min, 1 h and 24 h after. Some clinics first give 0.25 mL/kg over 15 min [@merck]. Check the PCV after the transfusion and daily [@scheep11].",
   "availability": "",
   "refs": ["@scheep11", "@leis19", "@zamb09", "@merck", "@koster15", "@karas22", "@herter22", "@collett00"]
  },
  {
   "name": "Fresh whole blood transfusion",
   "class": "supportive",
   "aim": "To restore oxygen-carrying capacity when packed cells are not available.",
   "status": "standard",
   "evidence_level": "B",
   "independent_studies": 1,
   "evidence_summary": "The Onderstepoort protocol allowed whole blood or packed red cells. In 86 B. rossi dogs, the type of product had no significant effect on any blood cell result over 6 days [@scheep11][@leis19]. No babesiosis study compared outcomes between the two products.",
   "doses": [
    {"drug": "whole blood", "dose": "body weight (kg) x 90 x (25 - recipient PCV) / donor PCV, in mL", "route": "IV", "frequency": "once", "duration": "", "context": "B. rossi, 86 dogs, Onderstepoort protocol", "note": "Target PCV 25%. PCV values in %.", "refs": ["@scheep11"]}
   ],
   "cautions": "Screen donors for Babesia, preferably by PCR [@koster15]. The same reaction risks as packed cells; circulatory overload is a risk with larger volumes [@merck].",
   "monitoring": "As for packed red cells [@merck].",
   "availability": "",
   "refs": ["@scheep11", "@leis19", "@koster15", "@merck"]
  },
  {
   "name": "Blood typing, cross-matching and donor screening",
   "class": "supportive",
   "aim": "To prevent haemolytic transfusion reactions and transmission of Babesia.",
   "status": "standard",
   "evidence_level": "D",
   "independent_studies": 1,
   "evidence_summary": "A veterinary manual advises DEA 1 typing of donors and recipients; DEA 1-positive dogs can receive DEA 1-negative cells, and dogs transfused more than 4 days before should be cross-matched [@merck]. In 21 transfused anaemic dogs (not a babesiosis study), cross-matches became positive within 4 days in 12, so the authors advised a cross-match before every later transfusion [@herter22]. In 13 severely anaemic Indian dogs, 12 with B. gibsoni, all first donor-recipient pairs were compatible [@mathews26]. DEA 1 type did not change the rate of Babesia infection in 200 Nigerian dogs [@adebayo25].",
   "doses": [],
   "cautions": "A compatible cross-match does not rule out a reaction [@herter22]. A DEA 1 weak-positive recipient should receive DEA 1-negative blood [@merck].",
   "monitoring": "",
   "availability": "",
   "refs": ["@merck", "@herter22", "@mathews26", "@adebayo25"]
  },
  {
   "name": "Haemoglobin-based oxygen carrier",
   "class": "supportive",
   "aim": "To carry oxygen without donor red cells.",
   "status": "proposed",
   "evidence_level": "A",
   "independent_studies": 1,
   "evidence_summary": "In a randomised trial of 12 B. rossi dogs (haematocrit 0.10 to 0.20 L/L), Oxyglobin gave blood gas, acid-base and blood pressure results similar to packed cells. Dogs given packed cells regained demeanour and appetite sooner and had a higher arterial oxygen content at 72 h [@zamb09].",
   "doses": [
    {"drug": "Oxyglobin (HB-200)", "dose": "20 mL/kg", "route": "IV (central venous catheter)", "frequency": "once, over 4 h", "duration": "single dose", "context": "B. rossi, haematocrit 0.10 to 0.20 L/L, randomised trial of 12 dogs", "note": "Followed by lactated Ringer's solution.", "refs": ["@zamb09"]}
   ],
   "cautions": "Only 12 dogs and 72 h of follow-up. Survival was not reported in the abstract [@zamb09].",
   "monitoring": "Blood gas, blood pressure, demeanour and appetite were followed for 72 h in the trial [@zamb09].",
   "availability": "",
   "refs": ["@zamb09"]
  },
  {
   "name": "Oxygen supplementation",
   "class": "supportive",
   "aim": "To raise arterial oxygen content in anaemic hypoxia.",
   "status": "proposed",
   "evidence_level": "E",
   "independent_studies": 0,
   "evidence_summary": "A 1995 South African review debated the benefit of oxygen in anaemic hypoxia without a definitive recommendation [@jacswan95]. In anaemic B. rossi dogs, central venous oxygen tension stayed below normal for 72 h after either packed cells or an oxygen carrier [@zamb09]. No study tested oxygen therapy for babesial anaemia.",
   "doses": [],
   "cautions": "No data in babesiosis. For hypoxaemia from lung injury, see SY08.",
   "monitoring": "",
   "availability": "",
   "refs": ["@jacswan95", "@zamb09"]
  },
  {
   "name": "Intravenous crystalloid fluids",
   "class": "supportive",
   "aim": "To correct dehydration and support perfusion in the anaemic dog.",
   "status": "proposed",
   "evidence_level": "E",
   "independent_studies": 0,
   "evidence_summary": "Standard Onderstepoort care gave fluids as needed, with no fixed protocol for the anaemia [@leis19][@scheep11]. Before treatment, anaemic B. rossi dogs had a hypoalbuminaemic alkalosis with a hyperchloraemic, dilutional acidosis [@zamb09]. A 1995 review discussed the problems of fluid therapy in complicated disease, in particular oliguria, cerebral babesiosis and pulmonary oedema [@jacswan95]. No study tested a fluid strategy for babesial anaemia.",
   "doses": [],
   "cautions": "Circulatory overload during transfusion presents as new tachypnoea or cough within 24 h; slower rates are advised in heart or kidney disease [@merck]. For fluids in complicated disease, see SY05, SY08 and SY10.",
   "monitoring": "Respiratory rate and effort during and for 24 h after a transfusion [@merck].",
   "availability": "",
   "refs": ["@leis19", "@scheep11", "@zamb09", "@jacswan95", "@merck"]
  },
  {
   "name": "Haematinics (iron, vitamin B complex)",
   "class": "adjunct",
   "aim": "To support red cell production after haemolysis.",
   "status": "proposed",
   "evidence_level": "C",
   "independent_studies": 1,
   "evidence_summary": "Used with many other drugs in single case reports, with no measured effect; for example an oral haematinic syrup in a B. gibsoni dog [@halder22]. A 1995 review examined the rationale for haematinics without a definitive recommendation [@jacswan95]. Fatal B. rossi cases had more stored marrow iron, not less [@bumby24]. No source gave a dose in mg/kg for babesiosis.",
   "doses": [],
   "cautions": "In a canine pneumonia model, intravenous iron was as toxic as old red cells. The author advised caution with intravenous iron in infected patients (level D) [@klein17].",
   "monitoring": "",
   "availability": "",
   "refs": ["@halder22", "@jacswan95", "@bumby24", "@klein17"]
  }
 ],
 "prognosis": {
  "text": "Most B. rossi dogs survive. In 320 dogs, 10.6% died, including dogs euthanased for a poor prognosis [@leis19]. Mortality in admitted cases was 12% in an earlier review [@jac06]. Severe anaemia raises the risk only a little. Collapse, haemoconcentration, hyperlactataemia and hypoglycaemia matter more [@leis19][@nel04].",
  "indicators": [
   {"finding": "Severe anaemia (haematocrit below 0.15 L/L)", "meaning": "Mortality was 14.2%, against 8% (moderate), 11.3% (mild) and 4% (normal haematocrit). Not a reliable predictor.", "refs": ["@leis19"]},
   {"finding": "Collapse at presentation", "meaning": "Odds ratio 8.36 for death. 24 of the 34 dogs that died had been collapsed.", "refs": ["@leis19"]},
   {"finding": "Haematocrit above 0.55 L/L", "meaning": "Odds ratio 32.7 for death; 3 of 4 died. See SY14.", "refs": ["@leis19"]},
   {"finding": "Lactate above 5 mmol/L at admission, above 2.5 mmol/L at 8 to 24 h, or less than a 50% fall", "meaning": "Associated with death. A value persistently above 4.4 mmol/L indicated a very poor prognosis.", "refs": ["@nel04"]},
   {"finding": "Hypoglycaemia at admission", "meaning": "Associated with death.", "refs": ["@nel04"]},
   {"finding": "High parasitaemia", "meaning": "Capillary and venous parasitaemias were higher in dogs that died.", "refs": ["@bohm06"]},
   {"finding": "Positive in-saline agglutination", "meaning": "Did not change the outcome in B. rossi dogs.", "refs": ["@leis19"]},
   {"finding": "Lower PCV and haemoglobin (Nigeria, species not identified)", "meaning": "Lower in dogs that died, on univariate analysis only.", "refs": ["@abakpa23"]}
  ]
 },
 "related": [
  {"id": "TX00", "why": "Antibabesial drugs and doses."},
  {"id": "SY02", "why": "Haemolysis that continues after treatment, positive agglutination, immunosuppression."},
  {"id": "SY04", "why": "Non-regenerative anaemia and marrow failure."},
  {"id": "SY14", "why": "Haemolysis with a high haematocrit."},
  {"id": "SY05", "why": "Kidney injury and haemoglobinuria."},
  {"id": "SY11", "why": "Triage and order of care in complicated disease."}
 ],
 "evidence_gaps": [
  "No trial compared transfusion with no transfusion, or different haematocrit triggers, in any Babesia species.",
  "No study tested oxygen therapy, a fluid strategy or haematinics for babesial anaemia.",
  "The rate of transfusion reactions in dogs with babesiosis is unknown. The only South African statement is from a survey of practices in 1993 [@collett00].",
  "No DEA 1 prevalence for South African dogs was found in this search.",
  "Recovery of the haematocrit after day 6 of treatment has not been described [@scheep11].",
  "In 1993, 96% of South African practices gave routine corticosteroids, vitamins or 'liver support' [@collett00]. No study of their effect on the anaemia was found.",
  "Almost all the evidence is from B. rossi at one hospital; data for B. canis, B. vogeli and B. gibsoni anaemia management are few."
 ],
 "search": {
  "date": "2026-11-12",
  "sources": ["Local review: combined_set.csv (221 rows tagged haemolytic anaemia), article notes, full texts, ERY synthesis", "PubMed", "Europe PMC", "Crossref", "Merck Veterinary Manual", "Journal of the South African Veterinary Association website"],
  "note": "Case reports of transfusion from India, Brazil, Ukraine and Nigeria, and the reports on cryopreserved red cells, were not used: they add no dose or outcome beyond the cited studies. The AVHTM transfusion reaction consensus (2021) was read as an abstract only and is not cited; the guidance is cited from a veterinary manual. The antibabesial drugs are in TX00."
 }
}

# renumber
order = []
def visit(o):
    if isinstance(o, dict):
        for k, v in o.items():
            visit(v)
    elif isinstance(o, list):
        for v in o: visit(v)
    elif isinstance(o, str):
        for m in re.findall(r"@([a-z0-9]+)", o):
            if m not in order: order.append(m)
visit(page)
missing = [k for k in order if k not in REFS]
if missing: sys.exit(f"missing refs {missing}")
unused = [k for k in REFS if k not in order]
if unused: print("unused refs:", unused)
num = {k: f"R{i+1}" for i, k in enumerate(order)}
def sub(o):
    if isinstance(o, dict): return {k: sub(v) for k, v in o.items()}
    if isinstance(o, list): return [sub(v) for v in o]
    if isinstance(o, str):
        o = re.sub(r"\[@([a-z0-9]+)\]", lambda m: f"[{num[m.group(1)]}]", o)
        return re.sub(r"^@([a-z0-9]+)$", lambda m: num[m.group(1)], o)
    return o
page = sub(page)
page["references"] = [dict(ref=num[k], **REFS[k]) for k in order]
# keep 'references' before 'search' as in example
s = page.pop("search"); page["search"] = s
json.dump(page, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for k in order: print(num[k], k)
