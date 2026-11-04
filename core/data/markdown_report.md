# Markdown conversion report

Generated 2026-10-28T20:27:45+00:00 by `scripts/to_markdown.py`. 540 articles: 255 from full text (100 JATS XML, 155 PDF), of which 210 pass every check; 285 abstract-only (full text not retrieved; see the last section).

## Flags

| Flag | Articles | Meaning |
|---|---|---|
| `no_sections_detected` | 17 | no standard section headings found; text is one block |
| `no_results_or_case_section` | 12 | primary study or case report without a Results or Case heading |
| `language:non-english-latin` | 11 | not English; translate or use a multilingual model |
| `language:cyrillic` | 10 | not English; translate or use a multilingual model |
| `title_check:unchecked` | 5 | fetcher could not confirm the title (see fulltext_missing.md) |
| `references_not_found` | 5 | no reference heading found; reference list may remain in the text |
| `short_text` | 4 | under 800 words (short case reports, or incomplete text) |
| `little_text_per_page` | 3 | probably scanned pages; needs OCR |
| `garbled_text` | 1 | PDF fonts lack a Unicode map; text is unusable without OCR |
| `title_check:low` | 1 | fetcher could not confirm the title (see fulltext_missing.md) |

## Articles to review

| ID | Source | Words | Tables | Sections | Flags |
|---|---|---|---|---|---|
| [CB277](markdown/CB277.md) | pdf | 204 | 1 |  | garbled_text, little_text_per_page, short_text, no_sections_detected, references_not_found, title_check:low |
| [CB537](markdown/CB537.md) | pdf | 3420 | 0 | introduction, methods, conclusion, abstract | language:cyrillic, no_results_or_case_section, references_not_found, title_check:unchecked |
| [CB158](markdown/CB158.md) | pdf | 2744 | 14 | abstract, introduction, conclusion | language:cyrillic, no_results_or_case_section, title_check:unchecked |
| [CB187](markdown/CB187.md) | pdf | 2191 | 2 |  | language:cyrillic, no_sections_detected, title_check:unchecked |
| [CB226](markdown/CB226.md) | pdf | 2426 | 0 |  | language:cyrillic, no_sections_detected, title_check:unchecked |
| [CB058](markdown/CB058.md) | pdf | 1825 | 1 | abstract | language:non-english-latin, no_sections_detected |
| [CB157](markdown/CB157.md) | pdf | 3877 | 0 |  | language:non-english-latin, no_sections_detected |
| [CB192](markdown/CB192.md) | pdf | 2489 | 0 | introduction, conclusion | language:cyrillic, no_results_or_case_section |
| [CB194](markdown/CB194.md) | pdf | 1890 | 4 | abstract, introduction, methods, conclusion | language:cyrillic, no_results_or_case_section |
| [CB200](markdown/CB200.md) | pdf | 2933 | 3 | introduction, conclusion | language:cyrillic, no_results_or_case_section |
| [CB213](markdown/CB213.md) | pdf | 2563 | 2 | introduction, conclusion | language:cyrillic, no_results_or_case_section |
| [CB261](markdown/CB261.md) | pdf | 2451 | 1 |  | language:non-english-latin, no_sections_detected |
| [CB267](markdown/CB267.md) | pdf | 2887 | 1 | abstract | language:cyrillic, no_sections_detected |
| [CB281](markdown/CB281.md) | pdf | 2609 | 1 | abstract, introduction, methods, conclusion | language:non-english-latin, no_results_or_case_section |
| [CB413](markdown/CB413.md) | pdf | 6605 | 5 | abstract, introduction, methods, results, discussion | little_text_per_page, references_not_found |
| [CB045](markdown/CB045.md) | jats_xml | 2271 | 1 | abstract | no_sections_detected |
| [CB047](markdown/CB047.md) | pdf | 1246 | 2 | introduction | no_results_or_case_section |
| [CB101](markdown/CB101.md) | jats_xml | 4852 | 4 | abstract | no_sections_detected |
| [CB155](markdown/CB155.md) | pdf | 5072 | 0 |  | no_sections_detected |
| [CB156](markdown/CB156.md) | pdf | 1360 | 1 | introduction | language:non-english-latin |
| [CB164](markdown/CB164.md) | pdf | 2353 | 0 | abstract, introduction, methods, conclusion | no_results_or_case_section |
| [CB175](markdown/CB175.md) | pdf | 1792 | 2 | abstract, introduction, case, discussion | language:non-english-latin |
| [CB189](markdown/CB189.md) | pdf | 3656 | 0 | abstract, introduction, methods, results, discussion, conclusion | language:non-english-latin |
| [CB204](markdown/CB204.md) | pdf | 3009 | 1 | abstract, introduction, methods, results, discussion, conclusion | language:non-english-latin |
| [CB216](markdown/CB216.md) | pdf | 581 | 0 | abstract, introduction, case, discussion | short_text |
| [CB218](markdown/CB218.md) | pdf | 858 | 0 | introduction, conclusion | language:cyrillic |
| [CB221](markdown/CB221.md) | pdf | 1362 | 1 | abstract | no_sections_detected |
| [CB223](markdown/CB223.md) | pdf | 2266 | 3 | introduction, methods, conclusion | no_results_or_case_section |
| [CB234](markdown/CB234.md) | pdf | 1837 | 2 | abstract, conclusion | no_sections_detected |
| [CB240](markdown/CB240.md) | pdf | 1920 | 0 | introduction, case, discussion, conclusion | language:non-english-latin |
| [CB245](markdown/CB245.md) | pdf | 3495 | 1 | introduction, methods, results, discussion | references_not_found |
| [CB250](markdown/CB250.md) | pdf | 2708 | 2 | abstract, introduction, case, discussion, conclusion | language:non-english-latin |
| [CB275](markdown/CB275.md) | pdf | 767 | 1 | abstract, introduction, case, discussion | short_text |
| [CB290](markdown/CB290.md) | pdf | 1690 | 2 | abstract, introduction | no_results_or_case_section |
| [CB296](markdown/CB296.md) | pdf | 2744 | 1 | abstract, introduction | language:non-english-latin |
| [CB336](markdown/CB336.md) | pdf | 3533 | 0 |  | no_sections_detected |
| [CB359](markdown/CB359.md) | pdf | 4607 | 0 | methods, discussion | no_results_or_case_section |
| [CB375](markdown/CB375.md) | pdf | 4094 | 1 | abstract, introduction | references_not_found |
| [CB380](markdown/CB380.md) | pdf | 3733 | 2 | abstract | no_sections_detected |
| [CB397](markdown/CB397.md) | pdf | 4907 | 2 | abstract, introduction, methods, results_discussion | little_text_per_page |
| [CB454](markdown/CB454.md) | jats_xml | 1600 | 0 | abstract | no_sections_detected |
| [CB463](markdown/CB463.md) | pdf | 796 | 2 | abstract, introduction, methods, results_discussion | short_text |
| [CB507](markdown/CB507.md) | pdf | 4925 | 1 | abstract, introduction, case, conclusion | title_check:unchecked |
| [CB514](markdown/CB514.md) | pdf | 4414 | 3 | abstract | no_sections_detected |
| [CB529](markdown/CB529.md) | pdf | 1656 | 2 |  | no_sections_detected |

## English translations

Machine translations (LLM, not reviewed by a person) of non-English articles, made by `scripts/finish_translations.py` from translated bodies in `data/markdown/translations/`. Use `<ID>.en.md` for extraction where it exists. *Numbers kept*: share of the original's numbers found in the translation. *Length*: translated words / original words. *Stale*: the original was re-converted after translating, so the translation should be redone.

| ID | From | Translation | Numbers kept | Length | Sections | Flags | Stale |
|---|---|---|---|---|---|---|---|
| CB058 | tr | [CB058.en.md](markdown/CB058.en.md) | 99% | 1.21 | introduction, methods, results, discussion | ok |  |
| CB156 | pt | [CB156.en.md](markdown/CB156.en.md) | 100% | 1.01 | introduction | ok |  |
| CB157 | pl | [CB157.en.md](markdown/CB157.en.md) | 99% | 1.24 |  | no_sections_detected |  |
| CB158 | ru | [CB158.en.md](markdown/CB158.en.md) | 100% | 1.23 | introduction, results_discussion, conclusion | title_check:unchecked |  |
| CB175 | pt | [CB175.en.md](markdown/CB175.en.md) | 100% | 1.01 | introduction, case, discussion | ok |  |
| CB187 | uk | [CB187.en.md](markdown/CB187.en.md) | 100% | 1.25 |  | no_sections_detected, title_check:unchecked |  |
| CB189 | pt | [CB189.en.md](markdown/CB189.en.md) | 100% | 1.03 | abstract, introduction, methods, results, discussion, conclusion | ok |  |
| CB192 | uk | [CB192.en.md](markdown/CB192.en.md) | 100% | 1.22 | introduction, conclusion | no_results_or_case_section |  |
| CB194 | ru | [CB194.en.md](markdown/CB194.en.md) | 100% | 1.20 | introduction, methods, results_discussion, conclusion | ok |  |
| CB200 | uk | [CB200.en.md](markdown/CB200.en.md) | 99% | 1.20 | introduction, conclusion | no_results_or_case_section |  |
| CB204 | pt | [CB204.en.md](markdown/CB204.en.md) | 100% | 0.99 | abstract, introduction, methods, results, discussion, conclusion | ok |  |
| CB213 | uk | [CB213.en.md](markdown/CB213.en.md) | 100% | 1.22 | introduction, conclusion | no_results_or_case_section |  |
| CB218 | ru | [CB218.en.md](markdown/CB218.en.md) | 100% | 1.12 | introduction, conclusion | ok |  |
| CB226 | uk | [CB226.en.md](markdown/CB226.en.md) | 100% | 1.19 |  | no_sections_detected, title_check:unchecked |  |
| CB240 | pt | [CB240.en.md](markdown/CB240.en.md) | 100% | 1.00 | introduction, case, discussion, conclusion | ok |  |
| CB250 | pt | [CB250.en.md](markdown/CB250.en.md) | 99% | 1.00 | introduction, case, discussion, conclusion | ok |  |
| CB261 | tr | [CB261.en.md](markdown/CB261.en.md) | 100% | 1.16 | introduction, methods, results, discussion | ok |  |
| CB262 | pt | [CB262.en.md](markdown/CB262.en.md) | 100% | 1.00 | abstract | abstract_only |  |
| CB264 | fr | [CB264.en.md](markdown/CB264.en.md) | 100% | 0.80 | abstract | abstract_only |  |
| CB267 | ru | [CB267.en.md](markdown/CB267.en.md) | 98% | 1.20 |  | no_sections_detected |  |
| CB281 | ro | [CB281.en.md](markdown/CB281.en.md) | 100% | 1.01 | introduction, methods, results_discussion, conclusion | ok |  |
| CB296 | ro | [CB296.en.md](markdown/CB296.en.md) | 100% | 1.09 | introduction | ok |  |
| CB299 | sr | [CB299.en.md](markdown/CB299.en.md) | 100% | 1.08 | abstract | abstract_only |  |
| CB308 | uk | [CB308.en.md](markdown/CB308.en.md) | 100% | 1.18 | abstract | abstract_only |  |
| CB364 | unknown | [CB364.en.md](markdown/CB364.en.md) | 100% | 1.06 | abstract | abstract_only |  |
| CB429 | unknown | [CB429.en.md](markdown/CB429.en.md) | 100% | 0.25 | abstract | abstract_only |  |
| CB448 | pt | [CB448.en.md](markdown/CB448.en.md) | 100% | 0.99 | abstract | abstract_only |  |
| CB457 | ru | [CB457.en.md](markdown/CB457.en.md) | 100% | 1.43 | abstract | abstract_only |  |
| CB475 | ru | [CB475.en.md](markdown/CB475.en.md) | 100% | 0.96 | abstract | abstract_only |  |
| CB488 | unknown | [CB488.en.md](markdown/CB488.en.md) | 100% | 0.14 | abstract | abstract_only |  |
| CB522 | unknown | [CB522.en.md](markdown/CB522.en.md) | 100% | 1.20 | abstract | abstract_only |  |
| CB537 | ru | [CB537.en.md](markdown/CB537.en.md) | 100% | 1.20 | introduction, methods, results_discussion, conclusion | references_not_found, title_check:unchecked, unclear_passages |  |
| CB539 | unknown | [CB539.en.md](markdown/CB539.en.md) | 100% | 1.04 | abstract | abstract_only |  |

## Abstract-only articles

Full text could not be retrieved (see `data/fulltext_missing.md`); the file holds the title, the authors' abstract and keywords, written by `scripts/abstracts_to_markdown.py`. Re-running `to_markdown.py` after adding a full text replaces it.

| ID | Scope | Words | Language | Abstract source |
|---|---|---|---|---|
| [BG002](markdown/BG002.md) | background | 274 | en | search background/comparator record |
| [BG003](markdown/BG003.md) | background | 144 | en | search background/comparator record |
| [BG005](markdown/BG005.md) | background | 106 | en | search background/comparator record |
| [BG006](markdown/BG006.md) | background | 142 | en | search background/comparator record |
| [BG009](markdown/BG009.md) | background | 113 | en | search background/comparator record |
| [BG011](markdown/BG011.md) | background | 319 | en | search background/comparator record |
| [BG016](markdown/BG016.md) | background | 241 | en | search background/comparator record |
| [CB001](markdown/CB001.md) | core canine evidence | 223 | en | search packet record |
| [CB002](markdown/CB002.md) | core canine evidence | 112 | en | search packet record |
| [CB007](markdown/CB007.md) | core canine evidence | 160 | en | search packet record |
| [CB008](markdown/CB008.md) | core canine evidence | 255 | en | search packet record |
| [CB009](markdown/CB009.md) | core canine evidence | 202 | en | search packet record |
| [CB011](markdown/CB011.md) | core canine evidence | 150 | en | search packet record |
| [CB012](markdown/CB012.md) | core canine evidence | 270 | en | search packet record |
| [CB014](markdown/CB014.md) | core canine evidence | 264 | en | search packet record |
| [CB018](markdown/CB018.md) | core canine evidence | 200 | en | search packet record |
| [CB021](markdown/CB021.md) | core canine evidence | 329 | en | search packet record |
| [CB024](markdown/CB024.md) | core canine evidence | 257 | en | search packet record |
| [CB025](markdown/CB025.md) | core canine evidence | 353 | en | search packet record |
| [CB030](markdown/CB030.md) | core canine evidence | 254 | en | search packet record |
| [CB034](markdown/CB034.md) | core canine evidence | 266 | en | search packet record |
| [CB037](markdown/CB037.md) | core canine evidence | 220 | en | search packet record |
| [CB043](markdown/CB043.md) | core canine evidence | 316 | en | search packet record |
| [CB049](markdown/CB049.md) | core canine evidence | 188 | en | search packet record |
| [CB051](markdown/CB051.md) | core canine evidence | 223 | en | search packet record |
| [CB054](markdown/CB054.md) | core canine evidence | 197 | en | search packet record |
| [CB056](markdown/CB056.md) | core canine evidence | 306 | en | search packet record |
| [CB057](markdown/CB057.md) | core canine evidence | 302 | en | search packet record |
| [CB061](markdown/CB061.md) | core canine evidence | 202 | en | search packet record |
| [CB063](markdown/CB063.md) | core canine evidence | 391 | en | search packet record |
| [CB067](markdown/CB067.md) | core canine evidence | 249 | en | search packet record |
| [CB068](markdown/CB068.md) | core canine evidence | 196 | en | search packet record |
| [CB069](markdown/CB069.md) | core canine evidence | 178 | en | search packet record |
| [CB073](markdown/CB073.md) | core canine evidence | 274 | en | search packet record |
| [CB074](markdown/CB074.md) | core canine evidence | 193 | en | search packet record |
| [CB078](markdown/CB078.md) | core canine evidence | 244 | en | search packet record |
| [CB079](markdown/CB079.md) | core canine evidence | 118 | en | search packet record |
| [CB084](markdown/CB084.md) | core canine evidence | 268 | en | search packet record |
| [CB086](markdown/CB086.md) | core canine evidence | 221 | en | search packet record |
| [CB087](markdown/CB087.md) | core canine evidence | 269 | en | search packet record |
| [CB089](markdown/CB089.md) | core canine evidence | 201 | en | search packet record |
| [CB092](markdown/CB092.md) | core canine evidence | 220 | en | manual: pasted by the user from the Springer article page, 2026-10-25 |
| [CB095](markdown/CB095.md) | canine review | 132 | en | search packet record |
| [CB097](markdown/CB097.md) | core canine evidence | 344 | en | search packet record |
| [CB099](markdown/CB099.md) | core canine evidence | 330 | en | search packet record |
| [CB100](markdown/CB100.md) | core canine evidence | 243 | en | search packet record |
| [CB103](markdown/CB103.md) | core canine evidence | 247 | en | search packet record |
| [CB104](markdown/CB104.md) | canine review | 97 | en | search packet record |
| [CB108](markdown/CB108.md) | core canine evidence | 223 | en | search packet record |
| [CB114](markdown/CB114.md) | canine review | 188 | en | search packet record |
| [CB116](markdown/CB116.md) | core canine evidence | 333 | en | search packet record |
| [CB118](markdown/CB118.md) | core canine evidence | 346 | en | search packet record |
| [CB122](markdown/CB122.md) | core canine evidence | 336 | en | search packet record |
| [CB123](markdown/CB123.md) | core canine evidence | 337 | en | search packet record |
| [CB124](markdown/CB124.md) | core canine evidence | 208 | en | search packet record |
| [CB127](markdown/CB127.md) | core canine evidence | 221 | en | search packet record |
| [CB128](markdown/CB128.md) | core canine evidence | 348 | en | search packet record |
| [CB132](markdown/CB132.md) | core canine evidence | 236 | en | search packet record |
| [CB140](markdown/CB140.md) | core canine evidence | 205 | en | search packet record |
| [CB142](markdown/CB142.md) | core canine evidence | 313 | en | search packet record |
| [CB144](markdown/CB144.md) | core canine evidence | 155 | en | search packet record |
| [CB146](markdown/CB146.md) | core canine evidence | 187 | en | search packet record |
| [CB151](markdown/CB151.md) | core canine evidence | 286 | en | search packet record |
| [CB153](markdown/CB153.md) | core canine evidence | 279 | en | search packet record |
| [CB154](markdown/CB154.md) | core canine evidence | 257 | en | search packet record |
| [CB159](markdown/CB159.md) | core canine evidence | 108 | en | search packet record |
| [CB165](markdown/CB165.md) | core canine evidence | 227 | en | search packet record |
| [CB166](markdown/CB166.md) | core canine evidence | 177 | en | search packet record |
| [CB168](markdown/CB168.md) | core canine evidence | 136 | en | search packet record |
| [CB169](markdown/CB169.md) | core canine evidence | 219 | en | search packet record |
| [CB182](markdown/CB182.md) | core canine evidence | 88 | en | search packet record |
| [CB184](markdown/CB184.md) | core canine evidence | 358 | en | search packet record |
| [CB193](markdown/CB193.md) | core canine evidence | 127 | en | search packet record |
| [CB208](markdown/CB208.md) | core canine evidence | 326 | en | search packet record |
| [CB212](markdown/CB212.md) | core canine evidence | 438 | en | search packet record |
| [CB214](markdown/CB214.md) | core canine evidence | 278 | en | search packet record |
| [CB217](markdown/CB217.md) | core canine evidence | 270 | en | search packet record |
| [CB219](markdown/CB219.md) | core canine evidence | 301 | en | search packet record |
| [CB230](markdown/CB230.md) | core canine evidence | 94 | en | search packet record |
| [CB231](markdown/CB231.md) | core canine evidence | 287 | en | search packet record |
| [CB233](markdown/CB233.md) | core canine evidence | 199 | en | search packet record |
| [CB235](markdown/CB235.md) | core canine evidence | 199 | en | search packet record |
| [CB237](markdown/CB237.md) | core canine evidence | 162 | en | search packet record |
| [CB239](markdown/CB239.md) | canine review | 41 | en | search packet record |
| [CB252](markdown/CB252.md) | core canine evidence | 266 | en | search packet record |
| [CB253](markdown/CB253.md) | core canine evidence | 100 | en | search packet record |
| [CB254](markdown/CB254.md) | core canine evidence | 295 | en | search packet record |
| [CB255](markdown/CB255.md) | core canine evidence | 183 | en | search packet record |
| [CB262](markdown/CB262.md) | core canine evidence | 191 | non-english-latin | search packet record |
| [CB264](markdown/CB264.md) | core canine evidence | 134 | non-english-latin | search packet record |
| [CB266](markdown/CB266.md) | core canine evidence | 165 | en | search packet record |
| [CB268](markdown/CB268.md) | core canine evidence | 227 | en | search packet record |
| [CB269](markdown/CB269.md) | core canine evidence | 146 | en | search packet record |
| [CB272](markdown/CB272.md) | core canine evidence | 176 | en | search packet record |
| [CB273](markdown/CB273.md) | core canine evidence | 412 | en | search packet record |
| [CB280](markdown/CB280.md) | core canine evidence | 415 | en | search packet record |
| [CB283](markdown/CB283.md) | core canine evidence | 63 | en | search packet record |
| [CB285](markdown/CB285.md) | core canine evidence | 352 | en | search packet record |
| [CB287](markdown/CB287.md) | canine review | 232 | en | search packet record |
| [CB291](markdown/CB291.md) | core canine evidence | 332 | en | search packet record |
| [CB292](markdown/CB292.md) | core canine evidence | 350 | en | search packet record |
| [CB298](markdown/CB298.md) | core canine evidence | 281 | en | search packet record |
| [CB299](markdown/CB299.md) | core canine evidence | 293 | cyrillic | search packet record |
| [CB306](markdown/CB306.md) | core canine evidence | 165 | en | manual: pasted by the user from the Springer article page, 2026-10-25 |
| [CB308](markdown/CB308.md) | core canine evidence | 341 | cyrillic | search packet record |
| [CB316](markdown/CB316.md) | core canine evidence | 310 | en | search packet record |
| [CB319](markdown/CB319.md) | canine review | 296 | en | search packet record |
| [CB320](markdown/CB320.md) | pending extraction | 190 | en | search packet record |
| [CB321](markdown/CB321.md) | pending extraction | 0 | none | none |
| [CB322](markdown/CB322.md) | pending extraction | 0 | none | none |
| [CB323](markdown/CB323.md) | pending extraction | 232 | en | search packet record |
| [CB324](markdown/CB324.md) | pending extraction | 114 | en | search packet record |
| [CB326](markdown/CB326.md) | pending extraction | 195 | en | search packet record |
| [CB327](markdown/CB327.md) | pending extraction | 0 | none | none |
| [CB328](markdown/CB328.md) | pending extraction | 0 | none | none |
| [CB329](markdown/CB329.md) | pending extraction | 0 | none | none |
| [CB330](markdown/CB330.md) | pending extraction | 209 | en | search packet record |
| [CB331](markdown/CB331.md) | pending extraction | 490 | en | search packet record |
| [CB332](markdown/CB332.md) | pending extraction | 109 | en | search packet record |
| [CB333](markdown/CB333.md) | pending extraction | 235 | en | search packet record |
| [CB334](markdown/CB334.md) | pending extraction | 200 | en | search packet record |
| [CB335](markdown/CB335.md) | pending extraction | 153 | en | search packet record |
| [CB338](markdown/CB338.md) | pending extraction | 213 | en | search packet record |
| [CB339](markdown/CB339.md) | pending extraction | 260 | en | search packet record |
| [CB340](markdown/CB340.md) | pending extraction | 269 | en | search packet record |
| [CB341](markdown/CB341.md) | pending extraction | 239 | en | search packet record |
| [CB343](markdown/CB343.md) | pending extraction | 0 | none | none |
| [CB344](markdown/CB344.md) | pending extraction | 199 | en | search packet record |
| [CB345](markdown/CB345.md) | pending extraction | 333 | en | search packet record |
| [CB346](markdown/CB346.md) | pending extraction | 219 | en | search packet record |
| [CB347](markdown/CB347.md) | pending extraction | 26 | en | search packet record |
| [CB348](markdown/CB348.md) | pending extraction | 0 | none | none |
| [CB349](markdown/CB349.md) | pending extraction | 0 | none | none |
| [CB350](markdown/CB350.md) | pending extraction | 0 | none | none |
| [CB351](markdown/CB351.md) | pending extraction | 49 | en | search packet record |
| [CB352](markdown/CB352.md) | pending extraction | 275 | en | search packet record |
| [CB353](markdown/CB353.md) | pending extraction | 277 | en | search packet record |
| [CB354](markdown/CB354.md) | pending extraction | 137 | en | search packet record |
| [CB355](markdown/CB355.md) | pending extraction | 263 | en | search packet record |
| [CB357](markdown/CB357.md) | pending extraction | 369 | en | search packet record |
| [CB358](markdown/CB358.md) | pending extraction | 37 | en | search packet record |
| [CB360](markdown/CB360.md) | pending extraction | 349 | en | search packet record |
| [CB361](markdown/CB361.md) | pending extraction | 229 | en | search packet record |
| [CB362](markdown/CB362.md) | pending extraction | 0 | none | none |
| [CB363](markdown/CB363.md) | pending extraction | 0 | none | none |
| [CB364](markdown/CB364.md) | pending extraction | 144 | non-english-latin | search packet record |
| [CB365](markdown/CB365.md) | pending extraction | 162 | en | search packet record |
| [CB366](markdown/CB366.md) | pending extraction | 73 | en | search packet record |
| [CB367](markdown/CB367.md) | pending extraction | 0 | none | none |
| [CB368](markdown/CB368.md) | pending extraction | 270 | en | search packet record |
| [CB369](markdown/CB369.md) | pending extraction | 236 | en | search packet record |
| [CB370](markdown/CB370.md) | pending extraction | 197 | en | search packet record |
| [CB371](markdown/CB371.md) | pending extraction | 94 | en | search packet record |
| [CB372](markdown/CB372.md) | pending extraction | 251 | en | search packet record |
| [CB374](markdown/CB374.md) | pending extraction | 254 | en | search packet record |
| [CB377](markdown/CB377.md) | pending extraction | 189 | en | search packet record |
| [CB379](markdown/CB379.md) | pending extraction | 247 | en | search packet record |
| [CB381](markdown/CB381.md) | pending extraction | 179 | en | search packet record |
| [CB382](markdown/CB382.md) | pending extraction | 266 | en | search packet record |
| [CB383](markdown/CB383.md) | pending extraction | 107 | en | search packet record |
| [CB384](markdown/CB384.md) | pending extraction | 228 | en | search packet record |
| [CB385](markdown/CB385.md) | pending extraction | 0 | none | none |
| [CB386](markdown/CB386.md) | pending extraction | 0 | none | none |
| [CB387](markdown/CB387.md) | pending extraction | 154 | en | search packet record |
| [CB388](markdown/CB388.md) | pending extraction | 0 | none | none |
| [CB389](markdown/CB389.md) | pending extraction | 169 | en | search packet record |
| [CB390](markdown/CB390.md) | pending extraction | 153 | en | search packet record |
| [CB391](markdown/CB391.md) | pending extraction | 90 | en | search packet record |
| [CB393](markdown/CB393.md) | pending extraction | 308 | en | search packet record |
| [CB395](markdown/CB395.md) | pending extraction | 61 | en | search packet record |
| [CB398](markdown/CB398.md) | pending extraction | 332 | en | search packet record |
| [CB399](markdown/CB399.md) | pending extraction | 543 | en | search packet record |
| [CB400](markdown/CB400.md) | pending extraction | 0 | none | none |
| [CB401](markdown/CB401.md) | pending extraction | 276 | en | search packet record |
| [CB402](markdown/CB402.md) | pending extraction | 182 | en | search packet record |
| [CB403](markdown/CB403.md) | pending extraction | 165 | en | search packet record |
| [CB404](markdown/CB404.md) | pending extraction | 106 | en | search packet record |
| [CB405](markdown/CB405.md) | pending extraction | 168 | en | search packet record |
| [CB406](markdown/CB406.md) | pending extraction | 87 | en | search packet record |
| [CB407](markdown/CB407.md) | pending extraction | 0 | none | none |
| [CB408](markdown/CB408.md) | pending extraction | 0 | none | none |
| [CB409](markdown/CB409.md) | pending extraction | 103 | en | search packet record |
| [CB410](markdown/CB410.md) | pending extraction | 0 | none | none |
| [CB411](markdown/CB411.md) | pending extraction | 0 | none | none |
| [CB412](markdown/CB412.md) | pending extraction | 234 | en | search packet record |
| [CB416](markdown/CB416.md) | pending extraction | 367 | en | search packet record |
| [CB417](markdown/CB417.md) | pending extraction | 0 | none | none |
| [CB419](markdown/CB419.md) | pending extraction | 269 | en | search packet record |
| [CB420](markdown/CB420.md) | pending extraction | 195 | en | search packet record |
| [CB421](markdown/CB421.md) | pending extraction | 0 | none | none |
| [CB422](markdown/CB422.md) | pending extraction | 277 | en | search packet record |
| [CB423](markdown/CB423.md) | pending extraction | 371 | en | search packet record |
| [CB426](markdown/CB426.md) | pending extraction | 0 | none | none |
| [CB427](markdown/CB427.md) | pending extraction | 0 | none | none |
| [CB428](markdown/CB428.md) | pending extraction | 245 | en | search packet record |
| [CB429](markdown/CB429.md) | pending extraction | 3 | non-english-latin | search packet record |
| [CB430](markdown/CB430.md) | pending extraction | 119 | en | search packet record |
| [CB431](markdown/CB431.md) | pending extraction | 192 | en | search packet record |
| [CB432](markdown/CB432.md) | pending extraction | 236 | en | search packet record |
| [CB433](markdown/CB433.md) | pending extraction | 0 | none | none |
| [CB434](markdown/CB434.md) | pending extraction | 264 | en | search packet record |
| [CB435](markdown/CB435.md) | pending extraction | 238 | en | search packet record |
| [CB436](markdown/CB436.md) | pending extraction | 0 | none | none |
| [CB437](markdown/CB437.md) | pending extraction | 166 | en | search packet record |
| [CB438](markdown/CB438.md) | pending extraction | 220 | en | search packet record |
| [CB442](markdown/CB442.md) | pending extraction | 221 | en | search packet record |
| [CB444](markdown/CB444.md) | pending extraction | 0 | none | none |
| [CB446](markdown/CB446.md) | pending extraction | 249 | en | search packet record |
| [CB447](markdown/CB447.md) | pending extraction | 149 | en | search packet record |
| [CB448](markdown/CB448.md) | pending extraction | 118 | non-english-latin | search packet record |
| [CB449](markdown/CB449.md) | pending extraction | 0 | none | none |
| [CB450](markdown/CB450.md) | pending extraction | 56 | en | search packet record |
| [CB451](markdown/CB451.md) | pending extraction | 209 | en | search packet record |
| [CB452](markdown/CB452.md) | pending extraction | 259 | en | search packet record |
| [CB453](markdown/CB453.md) | pending extraction | 230 | en | search packet record |
| [CB455](markdown/CB455.md) | pending extraction | 192 | en | search packet record |
| [CB456](markdown/CB456.md) | pending extraction | 168 | en | search packet record |
| [CB457](markdown/CB457.md) | pending extraction | 46 | cyrillic | search packet record |
| [CB458](markdown/CB458.md) | pending extraction | 337 | en | search packet record |
| [CB459](markdown/CB459.md) | pending extraction | 314 | en | search packet record |
| [CB461](markdown/CB461.md) | pending extraction | 97 | en | search packet record |
| [CB465](markdown/CB465.md) | pending extraction | 183 | en | search packet record |
| [CB466](markdown/CB466.md) | pending extraction | 0 | none | none |
| [CB467](markdown/CB467.md) | pending extraction | 241 | en | search packet record |
| [CB468](markdown/CB468.md) | pending extraction | 529 | en | search packet record |
| [CB469](markdown/CB469.md) | pending extraction | 238 | en | search packet record |
| [CB470](markdown/CB470.md) | pending extraction | 299 | en | search packet record |
| [CB471](markdown/CB471.md) | pending extraction | 177 | en | search packet record |
| [CB472](markdown/CB472.md) | pending extraction | 221 | en | search packet record |
| [CB475](markdown/CB475.md) | pending extraction | 13 | cyrillic | search packet record |
| [CB477](markdown/CB477.md) | pending extraction | 97 | en | search packet record |
| [CB478](markdown/CB478.md) | pending extraction | 238 | en | search packet record |
| [CB479](markdown/CB479.md) | pending extraction | 97 | en | search packet record |
| [CB480](markdown/CB480.md) | pending extraction | 144 | en | search packet record |
| [CB481](markdown/CB481.md) | pending extraction | 149 | en | search packet record |
| [CB482](markdown/CB482.md) | pending extraction | 230 | en | search packet record |
| [CB483](markdown/CB483.md) | pending extraction | 245 | en | search packet record |
| [CB485](markdown/CB485.md) | pending extraction | 254 | en | search packet record |
| [CB486](markdown/CB486.md) | pending extraction | 237 | en | search packet record |
| [CB487](markdown/CB487.md) | pending extraction | 696 | en | search packet record |
| [CB488](markdown/CB488.md) | pending extraction | 3 | non-english-latin | search packet record |
| [CB489](markdown/CB489.md) | pending extraction | 0 | none | none |
| [CB490](markdown/CB490.md) | pending extraction | 212 | en | search packet record |
| [CB494](markdown/CB494.md) | pending extraction | 85 | en | search packet record |
| [CB495](markdown/CB495.md) | pending extraction | 45 | en | search packet record |
| [CB496](markdown/CB496.md) | pending extraction | 0 | none | none |
| [CB497](markdown/CB497.md) | pending extraction | 626 | en | search packet record |
| [CB498](markdown/CB498.md) | pending extraction | 0 | none | none |
| [CB499](markdown/CB499.md) | pending extraction | 355 | en | search packet record |
| [CB500](markdown/CB500.md) | pending extraction | 282 | en | search packet record |
| [CB503](markdown/CB503.md) | pending extraction | 282 | en | search packet record |
| [CB504](markdown/CB504.md) | pending extraction | 279 | en | search packet record |
| [CB505](markdown/CB505.md) | pending extraction | 214 | en | search packet record |
| [CB506](markdown/CB506.md) | pending extraction | 310 | en | search packet record |
| [CB509](markdown/CB509.md) | pending extraction | 191 | en | search packet record |
| [CB510](markdown/CB510.md) | pending extraction | 219 | en | search packet record |
| [CB511](markdown/CB511.md) | pending extraction | 0 | none | none |
| [CB512](markdown/CB512.md) | pending extraction | 193 | en | search packet record |
| [CB513](markdown/CB513.md) | pending extraction | 235 | en | search packet record |
| [CB515](markdown/CB515.md) | pending extraction | 545 | en | search packet record |
| [CB519](markdown/CB519.md) | pending extraction | 95 | en | search packet record |
| [CB520](markdown/CB520.md) | pending extraction | 46 | en | search packet record |
| [CB521](markdown/CB521.md) | pending extraction | 0 | none | none |
| [CB522](markdown/CB522.md) | pending extraction | 242 | non-english-latin | search packet record |
| [CB523](markdown/CB523.md) | pending extraction | 324 | en | search packet record |
| [CB524](markdown/CB524.md) | pending extraction | 0 | none | none |
| [CB525](markdown/CB525.md) | pending extraction | 0 | none | none |
| [CB526](markdown/CB526.md) | pending extraction | 115 | en | search packet record |
| [CB528](markdown/CB528.md) | pending extraction | 154 | en | search packet record |
| [CB530](markdown/CB530.md) | pending extraction | 262 | en | search packet record |
| [CB531](markdown/CB531.md) | pending extraction | 0 | none | none |
| [CB534](markdown/CB534.md) | pending extraction | 0 | none | none |
| [CB535](markdown/CB535.md) | pending extraction | 179 | en | search packet record |
| [CB538](markdown/CB538.md) | pending extraction | 249 | en | search packet record |
| [CB539](markdown/CB539.md) | pending extraction | 170 | non-english-latin | search packet record |
| [CB540](markdown/CB540.md) | pending extraction | 214 | en | search packet record |
| [HU001](markdown/HU001.md) | human comparator | 255 | en | PubMed efetch (28273010), retrieved 2026-10-25 |
| [HU007](markdown/HU007.md) | human comparator | 180 | en | PubMed efetch (11283800), retrieved 2026-10-25 |
| [HU008](markdown/HU008.md) | human comparator | 271 | en | PubMed efetch (31162936), retrieved 2026-10-25 |
| [HU014](markdown/HU014.md) | human comparator | 276 | en | PubMed efetch (39873391), retrieved 2026-10-25 |
| [HU016](markdown/HU016.md) | human comparator | 295 | en | PubMed efetch (30585748), retrieved 2026-10-25 |
| [HU020](markdown/HU020.md) | human comparator | 331 | en | PubMed efetch (33652253), retrieved 2026-10-25 |
| [HU022](markdown/HU022.md) | human comparator | 263 | en | PubMed efetch (37703350), retrieved 2026-10-25 |
| [HU024](markdown/HU024.md) | human comparator | 268 | en | PubMed efetch (35983604), retrieved 2026-10-25 |
| [HU027](markdown/HU027.md) | human comparator | 154 | en | PubMed efetch (28722598), retrieved 2026-10-25 |
