---
title: "Dashboard widget: clinical syndrome and sign frequency"
status: proposed
date: 2026-11-04
depends_on: core/data/terms/*.json (pipeline stage S12, run 2026-10-30)
---

# Dashboard widget: clinical syndrome and sign frequency

## Goal

A card on the Literature Review dashboard that shows how often clinical
syndromes and signs (anaemia, thrombocytopenia, acute kidney injury, seizures,
icterus, ...) appear across the 444 canine articles, as a starting point for
research. Each term shows two numbers: articles that **studied** it and
articles that only **mentioned** it.

## Source data

Stage S12 of the pipeline writes one file per article,
`core/data/terms/<ID>.json`, for all 481 live articles (444 CB). Per file:

| Field | Meaning |
|---|---|
| `source_format` | `abstract`, `jats_xml` or `pdf`: whether the terms come from the abstract alone or the full text |
| `terms[].term` | UMLS CUI, e.g. `C0002871` |
| `terms[].concept` | UMLS preferred name, e.g. `Anemia` |
| `terms[].semantic_types` | UMLS Disorders-group types only (T033 "Finding" excluded) |
| `terms[].mentions`, `mentions_affirmed`, `mentions_negated` | Counts after NegEx |
| `terms[].sections` | Mentions per section: `title`, `abstract`, `introduction`, `methods`, `results`, `case`, `discussion`, `conclusion`, ... |
| `terms[].forms` | Surface forms, e.g. `anaemia`, `anemia` |
| `terms[].best_score` | Best UMLS link score (threshold 0.85) |

Nothing from these files is in SQL Server yet. The database holds articles,
categories and tags only.

### What a raw count looks like (CB articles, affirmed mentions, 2026-11-04)

| Concept | Articles | Studied |
|---|---:|---:|
| Babesiosis | 382 | 256 |
| Disease | 273 | 68 |
| Anemia | 267 | 93 |
| Communicable Diseases | 254 | 103 |
| Thrombocytopenia | 212 | 70 |
| Fever | 199 | 54 |
| Infections of musculoskeletal system (mislink of "infection") | 156 | 34 |
| Icterus | 142 | 36 |
| Hypoxia | 83 | 8 |
| Kidney Failure, Acute | 76 | 8 |

Two things follow. Generic and mislinked concepts must be curated out, and
"studied" versus "mentioned" is the more useful number.

## Design decisions

1. **Unit is the article, not the mention.** One full-text paper can mention
   anaemia fifty times. Each term counts an article once.
2. **Studied versus mentioned.** A term is *studied* in an article when it has
   an affirmed mention in `title`, `results`, `case` or `conclusion`. For
   abstract-only articles (`source_format = abstract`) the `abstract` section
   counts as studied too, because the abstract is the only place findings can
   appear. Everything else is *mentioned only*.
3. **Negated mentions do not count** (`mentions_affirmed = 0` drops the term for
   that article). "No seizures were observed" is not a seizure.
4. **Curated display layer, kept in the pipeline, not the app.** A CSV in
   `core/data/terms/` lists terms to hide (generic disease words, the parasite
   itself, known mislinks) and terms to merge under one display name. Manual rows
   survive regeneration, as `category_map.csv` already does for categories.
   The loader applies it; the app never hard-codes a term list.
5. **Canine articles only.** HU and BG are out of the count (the loader already
   excludes human comparators; the query also restricts to `CB` codes).
6. **Chart: horizontal stacked bar, top 20.** Dark segment = studied, light
   segment = mentioned only, sorted by total. No word cloud: it cannot show
   magnitude or the split.
7. **No new filters yet.** The command carries `top` only. Category and year
   filters arrive with the dashboard filter bar, and then this card becomes a
   syndrome profile per mechanism.

## Work packages

### WP1. Term display map (pipeline, `core/`)

- New script `core/scripts/build_term_display.py`: reads every
  `data/terms/*.json`, ranks CUIs by CB article count, and writes or updates
  `data/terms/term_display.csv` with columns
  `cui, concept, articles, action, display_name, note`.
  - `action` is `show` or `hide`. New rows default to `show`.
  - `display_name` merges several CUIs under one label; blank = use `concept`.
  - Existing rows keep their `action`, `display_name` and `note` on re-run;
    only `articles` is refreshed.
- Seed the first `hide` and merge rows by hand (needs the user's domain
  review). Proposed starting hide list: Babesiosis, Disease, Communicable
  Diseases, Infection by Babesia canis, Parasitic Diseases, Tick-Borne
  Diseases, Pathogenesis, Complication, Signs and Symptoms, disease
  transmission, Tissue damage, Malaria, Infections of musculoskeletal system
  (mislink), Mental Depression (mislink of the clinical sign "depression";
  alternatively merge into a "Depression (clinical sign)" display name).
  Proposed merges to decide: Anemia + Anemia, Hemolytic; Kidney Failure,
  Acute + Azotemia (or keep separate: azotaemia is a finding, AKI a diagnosis).
- Document the file in `core/docs/nlp-and-severity.md` and the
  `core/CLAUDE.md` table ("Which file answers which question").

### WP2. Schema and loader (`console/Babesiosis.Console`)

- `Database/schema.sql`: add
  - `dbo.term` (`term_id` identity PK, `cui VARCHAR(10)` unique,
    `concept NVARCHAR(200)`, `semantic_type NVARCHAR(100)`,
    `display_name NVARCHAR(200) NULL`, `hidden BIT NOT NULL DEFAULT 0`,
    `note NVARCHAR(400) NULL`).
  - `dbo.article_term` (`article_id` FK cascade, `term_id` FK,
    `mentions INT`, `mentions_affirmed INT`, `mentions_negated INT`,
    `studied BIT`, `sections JSON`, `forms JSON`, `best_score DECIMAL(4,3)`,
    PK (`article_id`, `term_id`)).
  - `dbo.article.text_source VARCHAR(20) NULL` (`abstract` / `jats_xml` /
    `pdf`, from the term file).
  - While there: add the `dbo.category.label` column that exists in the
    database but not in `schema.sql`.
- New `TermLoader.cs`, run after `ArticleLoader` in `Program.cs`:
  - reads `<ReviewRoot>/data/terms/*.json` and `term_display.csv`;
  - upserts `dbo.term` (CUI is the key; `hidden` and `display_name` from the
    CSV);
  - for each loaded article, deletes and re-inserts its `dbo.article_term`
    rows and sets `text_source`; applies decision 2 to compute `studied`;
  - skips articles the settings exclude (human comparators, `BG007`) and
    warns on a term file with no article row;
  - prints counts: terms, article-term rows, articles with no term file.
  - `--dry-run` reports without writing, like the article loader.
- Fix `appsettings.json` `Articles:ReviewRoot`, which points at
  `C:\Workspaces\DevResearch\...` (gone); point it at `core/`.
- EF: `Term` and `ArticleTerm` entities and `DbSet`s in
  `webapp/Babesiosis.Core/Articles/Data/ArticlesDbContext.cs`, plus
  `Article.TextSource`.

### WP3. API (`webapp/Babesiosis.Core.Api`, `webapp/Babesiosis.Core.Functions`)

Same shape as the category-year chart:

- `Review/Commands/GetTermCountsCommand.cs`: `int Top = 20`.
- `Review/Controllers/GetTermCountsController.cs`: for CB articles only,
  join `article_term` to `term` where `hidden = 0`, group by
  `COALESCE(display_name, concept)`, count distinct articles and distinct
  studied articles, order by total desc, take `Top`. Also return
  `articleCount` (CB articles with any term row) and `abstractOnlyCount`
  (`text_source = 'abstract'`), for the subtitle.
- `Review/ViewModels/TermCountsViewModel.cs`:
  `{ articleCount, abstractOnlyCount, terms: [{ name, studied, mentionedOnly, total }] }`.
- `Core.Functions/Review/GetTermCounts.cs`: route `review-term-counts-get`,
  anonymous like the rest of Review. Controllers are registered by reflection.

### WP4. Widget (`webapp/Babesiosis.Web/src/app/modules/literature-review`)

- `commands/get-term-counts.command.ts`, `viewmodels/term-counts.viewmodel.ts`,
  `getTermCounts()` in `literature-review.service.ts`.
- In the component: `termCounts` signal, `loadTermCounts()` wired into
  `refresh()` and `refreshing()`, the same loading / error-with-retry / empty
  pattern as the other cards.
- In the template: replace the "Cases by breed" dummy card (the slot beside
  "Articles by country") with:
  - title "Clinical syndromes and signs";
  - subtitle "Top 20 - studied (dark) and mentioned only (light) - N of 444
    articles abstract-only";
  - `fs-chart-bar` horizontal, `[stacked]="true"`, two series "Studied" and
    "Mentioned only", categories = term names, height to fit 20 rows
    (about 520 px), colours: primary and a muted grey from `fsChartGreys()`.
- Remove the `casesByBreed` dummy data from the component.

### WP5. Verification

- `dotnet run -- --dry-run` then `dotnet run` for the loader; compare the
  loader's counts with a Python recount over `data/terms/*.json`
  (`python -I` from `core/`), for three terms at least.
- `npx ng build --configuration local` passes.
- In the browser on port 4400: the card renders 20 bars, each with two
  segments, no console errors; a hidden term (for example Babesiosis) does
  not appear; the subtitle's abstract-only count matches the loader.
- Screenshot as proof.

## Acceptance

- The card shows the top 20 curated terms by CB article count with the
  studied / mentioned-only split, from the database, not from files.
- Re-running the pipeline's term extraction and the loader updates the card
  without code changes; curation lives only in `term_display.csv`.
- The two caveats are visible on the card: abstract-only share in the
  subtitle, and "automatic UMLS linking, curated list" in a hover or footnote.

## Decisions needed from the user

1. Review the seed `hide` list and the proposed merges in WP1 (domain call).
2. Confirm decision 2, that the abstract counts as "studied" for
   abstract-only articles. The alternative is to show those articles as
   "mentioned only", which understates them.
3. Confirm the card replaces "Cases by breed". The alternative is "Cases by
   diagnostic test"; both are dummy data and both should go eventually.

## Caveats to keep on the record

- Terms come from full text for 230 CB articles and from the abstract alone
  for 214, so full-text papers contribute more terms and more "mentioned only"
  rows. The subtitle says so.
- UMLS linking is automatic (scispaCy, threshold 0.85) with no human review.
  The curated map removes the known problems, not all of them.
- Article counts are not independent evidence (38 shared-animal cohorts). The
  filter bar can add an "independent cohorts" toggle later.
- `core/data/syndromes/` (the richer mention-level files) is not in this
  checkout; this plan uses only `core/data/terms/`, which is.
