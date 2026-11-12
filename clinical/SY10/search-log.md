# SY10 search log

Run 2026-11-12. "Kept" = used on the page.

| Date | Source | Query | Hits | Kept |
|---|---|---|---|---|
| 2026-11-12 | `/core/search/clinical_treatment/combined_set.csv` | `syndromes` contains "shock" | 6 | 3 (CB200, CB217, CB263) |
| 2026-11-12 | `/core/data/terms/` | CB articles with Shock, Septic Shock, Hypotensive Shock, Hypotensive, Hyperlactatemia | 78 | 9 |
| 2026-11-12 | `/core/data/markdown/CB*.md` | full-text grep "hypotens", "blood pressure", "arterial pressure", "lactate" | 40 files ranked | 12 (CB487, CB463, CB485, CB483 (not cited), CB473, CB040, CB516, CB106, CB493, CB533, CB200, CB263) |
| 2026-11-12 | PubMed | (babesiosis OR babesia) AND dog AND (hypotension OR "blood pressure" OR shock OR lactate OR collapse) | 80 | 9 (Jacobson 2000, Böhm 2006, Jacobson 2006, Jacobson 2005, Nel 2004, Matijatko 2009, Zambelli 2009, Zygner 2014 x2) |
| 2026-11-12 | PubMed | Jacobson LS[Author] AND babesiosis AND (blood pressure OR hypotension OR nitric oxide) | 8 | 2 (Jacobson 2000, Leisewitz 2001) |
| 2026-11-12 | PubMed | (Zygner W OR Gójska-Zygner O)[Author] AND babesiosis | 19 | 4 |
| 2026-11-12 | PubMed | (babesiosis OR babesia) AND (dog OR canine) AND (fluid therapy OR crystalloid OR colloid OR hydroxyethyl starch OR hypertonic saline OR vasopressor OR noradrenaline OR dopamine OR hydrocortisone OR dexamethasone OR resuscitation) | 16 | 1 (Schoeman 2008); no fluid or vasopressor trial in babesiosis |
| 2026-11-12 | Web | AAHA 2024 fluid therapy guidelines (bolus, hypertonic saline, HES) | 10 | 0: JAAHA and aaha.org pages returned HTTP 403; not read, not cited |
| 2026-11-12 | PubMed | canine septic shock vasopressor review, free full text | 12 | 1 (Montealegre and Lyons 2021, read in PMC) |
| 2026-11-12 | PubMed | FEAST (Maitland 2011); Hanson falciparum malaria fluid resuscitation | 2 + 3 | 2 |
| 2026-11-12 | PubMed | hydroxyethyl starch dogs acute kidney injury death retrospective cohort | 1 | 1 (Hayes 2016) |
| 2026-11-12 | PubMed | dogs septic shock hydrocortisone CIRCI retrospective | 1 | 1 (Summers 2021) |
| 2026-11-12 | PubMed | hypertonic saline 7.5% dogs shock resuscitation mL/kg clinical | 5 | 1 (Borrelli 2021); the others were experimental models |
| 2026-11-12 | Europe PMC | (babesiosis OR babesia) AND (dog OR canine) AND (hypotension OR septic shock OR vasopressor OR norepinephrine OR fluid therapy OR blood volume), first 50 of 508 | 508 | 1 new (Goggs 2026 septic shock consensus, read in PMC); no new treatment |
| 2026-11-12 | Web, Hrčak | Torti 2014 Veterinarski arhiv record | 1 | 1 (abstract and record only; the PDF link was fetched by the tool but not read or used) |
| 2026-11-12 | Crossref | DOIs of CB200, CB217, CB263 | 3 | 3 |

## Stop

The last two searches (Europe PMC, PubMed hypertonic saline) gave no new treatment tested in babesiosis and no new diagnostic criterion. Search stopped there.

## Not found

- No trial of fluid type, volume or end point in babesiosis.
- No vasopressor other than dopamine (one uncontrolled series) used in babesiosis; no vasopressin source.
- No oxygen therapy data in shocked dogs with babesiosis.
- No hypertonic saline, albumin or corticosteroid use in babesiosis.
- No hydrocortisone dose in the sources read (Summers 2021 abstract does not state it).
