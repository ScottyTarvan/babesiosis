# CL-00: the Clinical screen

Owner: the coordinator. The page agents do not change any file listed here.

**Status: built on 2026-11-12** (not committed). The code is in `/webapp/Babesiosis.Web/src/app/modules/clinical/`; the route is in `layout/layout.module.ts`. Checked with the example page in `babesiosis-web-mock`: every section, the citation and reference links, a missing page, the filter, the dark theme and a phone width. The print layout was written but not seen in a print preview.

What differs from the specification below:

- The menu icon is `checkup-list`. `stethoscope` and `printer` are not in the app's icon set (`src/app/app-icons.ts`, a generated file).
- The screen reads every page file of the index when it opens, to know which pages are written. A page that is not written gives one 404 line in the browser console. That is expected.
- A local article ID is shown as a badge, not a link: "Reference Articles" has no route for one article.
- A page file that is added while the dev server runs is not served until the server is restarted (it shows as "not written").
- The print rules for the shell (menu and top bar hidden) are in `src/styles.scss` and apply to every screen.

Read first: `/webapp/.claude/agents/agents.md` and the architecture files that it names for frontend work. The Experiments screen (`/webapp/Babesiosis.Web/src/app/modules/experiments/`) is the pattern for a screen with a side rail and one route for the list and the detail.

## What to build

| Part | Requirement |
|---|---|
| Menu | One item in `layout/menu-meta.ts`: key `clinical`, label `Clinical`, link `/clinical`, a Tabler icon (for example `stethoscope`), after "Experiments" |
| Route | `/clinical` and `/clinical/<ID>` with one URL matcher, so that the rail keeps its state when the page changes. `/clinical` opens the first page of the index |
| Module | `src/app/modules/clinical/`: page component, service, view model classes (one class for each object of [content-format.md](content-format.md)), in separate `.ts`, `.html` and `.scss` files |
| Data | Static files, read with a plain HTTP GET (no API, no database): `assets/clinical/index.json` (the rail), `assets/clinical/<ID>.json` (a page). The mock API interceptor must let these requests through. A page file that is missing shows "This page is not written yet", not an error |
| Side rail | The pages of `index.json`, in its order, under its group headings. Each link shows the title. A page that is not written is shown dimmed. The rail has a text filter. On a narrow screen the rail collapses above the page |
| Page | The sections below, in this order, from one page file |
| Notice | A fixed notice on every page: "Compiled by AI agents from the published literature. Not peer reviewed. Check every dose against the product label before use. This manual does not replace clinical judgement." |

## The rail index

`/webapp/Babesiosis.Web/public/assets/clinical/index.json`, owned by the coordinator:

```json
{
  "groups": [
    { "group": "Parasite treatment", "pages": [ { "id": "TX00", "title": "Antibabesial treatment and persistence" } ] },
    { "group": "Blood", "pages": [ { "id": "SY01", "title": "Severe haemolytic anaemia" } ] }
  ]
}
```

The groups, the order and the titles are those of the table in [index.md](index.md).

## The sections of a page

1. **Header.** Title, definition, date updated, the species named in `species_notes`.
2. **Key points.** A highlighted list.
3. **Description.** Each `{heading, text}` as a short section. Then the species notes.
4. **Diagnosis.** Criteria as a table (criterion, threshold, basis as a badge, note). Then clinical signs, tests, differentials and grading as tables or lists.
5. **Approach.** Numbered steps. A badge marks the steps that need referral.
6. **Treatments.** One card for each treatment: name, class, a status badge, an evidence level badge with its meaning on hover, the aim, the evidence summary, the dose table (drug, dose, route, frequency, duration, context, note, source), cautions, monitoring, availability. Colour the status: `standard` neutral or green, `proposed` blue, `conflicting` amber, `no_benefit` grey, `harmful` red. Do not rely on colour alone: show the word.
7. **Prognosis.** Text, then the indicators as a table.
8. **Evidence gaps.**
9. **Related pages.** Links to `/clinical/<ID>`.
10. **References.** A numbered list. Each entry: authors, year, title, journal, volume and pages, a link that opens in a new tab (`https://doi.org/<doi>`, else `https://pubmed.ncbi.nlm.nih.gov/<pmid>/`, else `url`), the kind of study, the number of dogs, "abstract only" when `read` is `abstract`, and the local article ID when present (a link to the article in "Reference Articles" if that screen has a route for one article).
11. **Search note and the legend** of the evidence levels and status values ([rules.md](rules.md)).

Citation markers `[R1]` in any text become links to the entry in the reference list. Keys in a `refs` list are shown the same way.

## Rules for the build

- Use the shared `fs-*` components and the theme tokens. The screen must be readable in the light and the dark theme, and on a phone.
- The text of a page file is plain text: bind it as text, never as HTML.
- The screen must print: the rail and the menu are hidden in print, and the treatment cards do not break across pages where the browser can avoid it.
- Unknown fields in a page file are ignored. A missing optional field hides its part.
- No new npm package without asking the user.

## Check

1. `npx ng build` in `/webapp/Babesiosis.Web` ends with no error.
2. Copy `shared/example.json` to `public/assets/clinical/SY99.json` and add it to a test group in `index.json`. Start `babesiosis-web-mock` from `/.claude/launch.json`, open `/clinical/SY99`, and confirm every section, the citation links, the reference links, a missing page, the filter, both themes and the print preview.
3. Remove `SY99` from the assets and the index when the check is done.
4. Add the screen to `/docs/index.md` (Web app section) if a new document describes it.
