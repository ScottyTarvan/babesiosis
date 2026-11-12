"""Build SV-G2/association_schema_v2.json from the pilot schema /core/data/severity/association_schema.json.

Schema v2 = the pilot schema plus the fields that SV-G2-literature-extraction.md asks for. Standard library only.
Usage: python -I scripts/make_schema_v2.py   (from /experiments/SV-G2/)
"""
import copy
import json
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent
CORE = PKG.parent.parent / "core"
src = json.loads((CORE / "data" / "severity" / "association_schema.json").read_text(encoding="utf-8"))
s = copy.deepcopy(src)
s["$id"] = "association_schema_v2.json"
s["title"] = "Marker-severity associations extracted from one article (schema v2, SV-G2)"
s["description"] = src["description"].replace("data/severity/extractions/<ID>.json", "/experiments/SV-G2/extractions/<ID>.json") + \
    " Schema v2 adds: article setting and sample timing; definition components, euthanasia, definition source and follow-up horizon; per-group values with summary type; load method for parasite load rows; a list of what could not be extracted."

top = s["properties"]
top["schema_version"] = {"const": "v2"}
top["setting"] = {"enum": ["referral hospital", "primary clinic", "laboratory submissions", "shelter", "experimental",
                           "field survey", "mixed", "not stated"],
                  "description": "Where the dogs came from. referral hospital: university or referral hospital (e.g. Onderstepoort OVAH, Zagreb faculty clinic). primary clinic: first-opinion practice. laboratory submissions: samples sent to a diagnostic laboratory. field survey: dogs sampled in the community or at kennels. mixed: more than one. experimental: induced infection."}
top["sample_timing"] = {"enum": ["before treatment", "hours after treatment", "days after treatment", "mixed", "not stated"],
                        "description": "When the samples used for the severity comparisons were taken relative to antibabesial treatment, as the article states it. Admission samples with no statement about treatment: not stated (say so in article_notes if the article implies it)."}
top["not_extracted"] = {
    "type": "array",
    "description": "What the article reports against severity that could not be extracted, and why (e.g. a figure with no numbers, a garbled table, a supplement that is not in the text). Empty array if nothing.",
    "items": {"type": "object", "required": ["what", "reason"], "additionalProperties": False,
              "properties": {"what": {"type": "string"},
                             "reason": {"enum": ["figure only", "garbled table", "supplement not in text", "group sizes unclear",
                                                 "no per-group result", "outcome groups mixed with controls", "other"]},
                             "note": {"type": ["string", "null"]}}}}
s["required"] = src["required"] + ["schema_version", "setting", "sample_timing", "not_extracted"]

d = top["severity_definitions"]["items"]
d["properties"]["components"] = {
    "type": "array", "minItems": 1,
    "items": {"enum": ["death", "collapse", "cerebral", "renal", "hepatic or icterus", "pulmonary", "hypotension or shock",
                       "coagulopathy", "haemoconcentration", "hypoglycaemia", "hyperlactataemia", "pancreatitis",
                       "rhabdomyolysis", "SIRS", "MODS", "anaemia grade", "score", "other"]},
    "description": "What makes a dog 'severe' under this definition. For complicated vs uncomplicated: the complications the authors list. For mortality: ['death']. For a score: ['score'] (plus the components if the score is built from named ones). 'other' when a component is not in the list (say which in definition)."}
d["properties"]["euthanasia_included"] = {"enum": ["yes", "no", "not stated", "not applicable"],
                                          "description": "Whether dogs euthanised are counted in the severe group. not applicable: definitions that are not about death."}
d["properties"]["definition_source"] = {"type": "string",
                                        "description": "Where the definition comes from: 'WHO malaria criteria', 'Jacobson and Clark 1994 / Welzl 2001 complications', 'SIRS criteria', 'MODS criteria', 'IRIS AKI grading', 'author-defined', 'not stated', or the reference as the article cites it."}
d["properties"]["follow_up_horizon"] = {"type": ["string", "null"],
                                        "description": "For outcomes over time: e.g. 'to discharge', '28 days', '7 days'. null if not stated or not applicable."}
d["required"] = d["required"] + ["components", "euthanasia_included", "definition_source"]

a = top["associations"]["items"]
a["properties"]["severe_value"] = {"type": ["string", "null"],
                                   "description": "The value printed for the severe group, copied as printed with its spread, e.g. '6.1 (3.2-9.8)' or '12/15 (80%)'. null if not printed. Never computed."}
a["properties"]["comparison_value"] = {"type": ["string", "null"], "description": "The value printed for the comparison group, as above."}
a["properties"]["summary_type"] = {"enum": ["mean and SD", "mean and SEM", "mean and range", "median and IQR", "median and range",
                                            "count and percent", "other", None],
                                   "description": "How severe_value and comparison_value are summarised. null when neither value is printed."}
a["properties"]["load_method"] = {"enum": ["capillary smear", "venous smear", "smear, site not stated", "qPCR", "other", "not stated", None],
                                  "description": "Required for rows whose marker is Parasitaemia or Parasite DNA load (qPCR); null otherwise."}
s["properties"] = top
out = PKG / "association_schema_v2.json"
out.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {out}")
