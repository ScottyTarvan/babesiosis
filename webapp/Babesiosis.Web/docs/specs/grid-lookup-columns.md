# fs-data-grid — Full Lookup Columns (in-memory + remote-searched)

Status: **SPEC — not implemented**
Component: `src/app/shared/components/fs-data-grid/`
Convention: this document is vendor-name-free; "the reference grid" denotes the
commercial grid whose behavioural spec (`Babesiosis.Agents.Docs/Specs/data-grid-feature-spec.md`,
§5.3) the component follows.

---

## 1. Summary & goals

A **lookup column** stores a key in the row (`statusId: 3`) but displays a text
resolved from a lookup list (`'Paused'`). Today the grid supports this only for
**static in-memory arrays**. This feature completes lookup columns with a
**remote (deferred) variant**: the lookup list lives behind a backend search
endpoint (e.g. a 10k-row products list); the editor dropdown searches
server-side with a text query and pages results, and display cells resolve
keys they have never seen through a batch resolve-by-keys callback.

Goals:

1. Keep the existing in-memory lookup contract 100 % backward compatible.
2. Add a remote lookup variant: `{ searchText, skip, take } → { items, totalCount }`
   load callback + `resolveByKeys` for off-page display resolution.
3. A searchable, paged dropdown editor (cell editor, edit form, filter row,
   filter builder) with debounce, min-search-length, load-more paging,
   loading/error states and a clear affordance.
4. Deterministic display pipeline: sync for in-memory, cached-async for remote,
   with defined rendering while unresolved.
5. Explicit, documented sorting / filtering / grouping semantics per variant.

Non-goals (v1 of this feature):

- Multi-key lookup cells (arrays of keys in one cell).
- Cascading lookups (editor options depending on another column's draft value).
- Server-side computation of header-filter distinct lists (stays client-side
  over the loaded rows, consistent with §30.5).
- Virtualised (windowed) rendering inside the dropdown — paging is load-more.

---

## 2. Reference behavior

From the reference grid's lookup-column documentation (fetched 2026-07-21; the
public page is sparse, the semantics below combine it with the documented
behavioural spec):

- Column config: `lookup: { dataSource, valueExpr, displayExpr, allowClearing }`.
  - `dataSource`: "a collection of objects that map the column's actual values
    to display values", or a plain array when actual and display values
    coincide. It may also be a store or a **function receiving load options**
    including `searchValue`, `skip`, `take` — this is the remote path.
  - `valueExpr` produces the stored key, `displayExpr` the visible text.
  - `allowClearing: true` adds a button in edit state that nullifies the value.
- Display cells resolve key → text through the lookup.
- The generated editor is a select-box UI component; with a remote source it
  delegates searching/paging to the store.
- **Sorting, filtering and grouping operate on the display text** in the
  reference implementation (rows order by `'Paused' < 'Running'`, not `3 < 1`).
  Where this spec deviates it says so explicitly (§7).

---

## 3. Current state (file:line evidence)

Authoritative contract: `README.md` — "Editors are `fs-*` primitives:
`fs-select` (lookup) …" (README.md:126), lookup display note (README.md:681-684),
cell-editor lookup input (README.md:1238), filter-row select cells
(README.md:1277-1278). `remoteOperations`-adjacent gaps list is at README.md:151-153.

### 3.1 Type contract

- `FsGridLookup` — `fs-data-grid.types.ts:88-97`: `dataSource: readonly unknown[]`
  ("Array of lookup items (**client-side only in v1**)"), `displayExpr`,
  `valueExpr`, `allowClearing`. Attached per column at
  `fs-data-grid.types.ts:894` (`lookup?: FsGridLookup`).

### 3.2 Display resolution (cells, group text, filter-panel text, export)

- `normalize-columns.ts:477-485` — `lookupAccessor()` builds display/value
  accessors (field name | function | identity).
- `normalize-columns.ts:497-524` — `makeDisplayText()`: an explicit `format`
  wins; otherwise the lookup resolves value → item via a **synchronous linear
  `dataSource.find`** (line 520) and returns the item's display text; misses
  fall through to the dataType default. Wired as the column's `getDisplayText`
  at `normalize-columns.ts:571` (`fs-data-grid.types.ts:1240`).
- Plain cell text: `fs-data-grid.component.ts:1549,1556` (`cellContextFor` /
  `cellTextFor`), rendered at `fs-data-grid.component.html:552`; adaptive
  detail rows at `fs-data-grid.component.ts:5106` and
  `fs-data-grid.component.html:859`.
- Group row text: `engine/grouping.ts:178` —
  `` `${caption}: ${getDisplayText(node.value)}` `` (group VALUE stays the raw key).
- Filter-panel condition text: `engine/filtering.ts:891-899` (`valueText` via
  `getDisplayText`).
- CSV export: `engine/export.ts:58` (`getDisplayText(getCellValue(row))`).

### 3.3 Editors

- Generated cell editor: `fs-data-grid-cell-editor.component.ts:107-108`
  (`lookup` input forces editor kind `'lookup'`), `:137-147` (`lookupOptions`
  maps `dataSource` → `FsSelectOption[]`, `allowClearing` prepends a blank
  null option), `:191-193` (`onLookupChange` emits the key). Rendered as
  `<fs-select>` at `fs-data-grid-cell-editor.component.html:3-12`.
- Inline cell/batch/row editing passes `[lookup]="col.def.lookup"` at
  `fs-data-grid.component.html:513` and `:531` (showEditorAlways).
- Edit form / popup: `fs-data-grid-edit-form.component.html:62-71` — same
  cell-editor with the same `[lookup]` input.

### 3.4 Filter row

- `fs-data-grid-filter-row.component.ts:183` — a lookup (or boolean) column
  renders a **select** filter cell; `:188-196` the operation chooser is
  suppressed (always filters by exact value); `:196-215` options = `'(All)'`
  clear item + every `lookup.dataSource` item (display label, key value);
  `:311-320` a local copy of `lookupAccessor`.

### 3.5 Header filter

- Distinct list: `engine/filtering.ts:919-947` — unique values from the
  **loaded rows** (`workingData()` at `fs-data-grid.component.ts:2607`), text
  via `col.getDisplayText` (filtering.ts:944). Popup search
  (`fs-data-grid-header-filter.component.ts:69-81`) filters that item list
  client-side by its resolved text.

### 3.6 Filter builder

- `fs-data-grid-filter-builder.component.ts:29` (`lookup?: FsGridLookup` on
  the builder column descriptor, populated at `fs-data-grid.component.ts:2738`)
  and `:148-150` (`lookupOf`); the value editor receives
  `[lookup]="lookupOf(child)"` at `fs-data-grid-filter-builder.component.html:124`.

### 3.7 Search panel

- Live search predicate matches the **display text** for lookup columns
  (`engine/filtering.ts:639`); the expression form embeds a display-text
  predicate function for lookup/format columns (`engine/filtering.ts:780-785`),
  flagged non-serialisable for `remoteLoad` (README.md:220-224,
  `fs-data-grid.types.ts:785-796`).

### 3.8 Sorting & grouping order

- `engine/sorting.ts:24-29` — `resolveSortValue` uses `calculateSortValue` or
  the **raw cell value**: lookup columns currently sort by KEY, not display
  text (a deviation from the reference — see §7). Grouped columns sort the
  same way (`sorting.ts:80-100`), so group order is key order while group
  labels show display text.

### 3.9 Editor primitives available

- `fs-select` (`fs-select/fs-select.component.ts:38-56`) — native `<select>`,
  static `options` input, CVA. No search, no paging. Current lookup editor.
- `fs-autocomplete` (`fs-autocomplete/fs-autocomplete.component.ts:48-90`) —
  typeahead single-select, CDK overlay, CVA; `options` is a **required static
  input** filtered **client-side** (`:81-88`). No async search, no loading
  state, no paging, no `sm` size gap (has `sm | md`). Closest primitive to the
  remote editor; needs extension (§8.1).
- `fs-multi-select` (`fs-multi-select/fs-multi-select.component.ts:76-90`) —
  chip multi-select with client-side search; wrong shape for single-key cell
  editing, unchanged by this feature.

### 3.10 Backend conventions (context only)

- `Babesiosis.Core/Commands/LoadOptions.cs:17-40` — `skip`, `take`,
  `requireTotalCount`, `sort[]`, nested `filter` array; wrapped by
  `SearchCommand` (`Babesiosis.Core/Commands/SearchCommand.cs:3-6`). A real
  lookup-search endpoint would accept this envelope (searchText expressed as a
  `[displayField, 'contains', text]` filter) — the gallery demo simulates it
  in-memory (§10).

---

## 4. Gap analysis

| Surface | In-memory today | Remote gap |
| --- | --- | --- |
| Type contract | `dataSource` array only (types.ts:88-97) | No load/search callback, no resolve-by-keys, no debounce/minSearchLength/paging knobs |
| Cell display | Sync `find` over array (normalize-columns.ts:520) | No async path: a key absent from any loaded page renders as the raw key with no way to resolve it |
| Cell editor | `<fs-select>` with the full array (cell-editor.ts:137-147) | Unusable at 10k items; no search-as-you-type against the server, no paging, no loading/error UI |
| Edit form | Same editor (edit-form.html:62-71) | Same gap |
| Filter row | Static select over the full array (filter-row.ts:196-215) | Cannot enumerate 10k options; needs the searchable editor |
| Filter builder | Static select via `[lookup]` (filter-builder.html:124) | Same gap |
| Header filter | Distinct keys of loaded rows, text via sync lookup (filtering.ts:919-947) | Texts for keys unresolved client-side render as raw keys |
| Search panel | Display-text predicate (filtering.ts:780-785) | Predicate must read the async cache, not the array |
| Sorting | By key (sorting.ts:24-29) — deviates from reference already | Display-text sort impossible until keys resolve; needs an explicit decision |
| Grouping | Buckets by key, label by text (grouping.ts:178) | Labels need the cache; group order decision |
| Export | Display text sync (export.ts:58) | Unresolved keys would export raw keys |
| Primitives | `fs-select` / `fs-autocomplete` static | No async-search/paged dropdown primitive exists |

---

## 5. Proposed API

`fs-data-grid.types.ts` — `FsGridLookup` becomes a union. The in-memory shape
is **unchanged** (no consumer breaks); the remote shape is discriminated by the
presence of `load`.

```ts
// ---------------------------------------------------------------------------
// Lookup + editor configuration (§5.3) — v2: in-memory | remote
// ---------------------------------------------------------------------------

/** Shared expressions — unchanged semantics (field name | accessor | identity). */
export interface FsGridLookupBase {
  /** Field name or accessor producing the visible text. */
  displayExpr?: string | ((item: unknown) => string);
  /** Field name or accessor producing the stored value. Omitted = the item itself. */
  valueExpr?: string | ((item: unknown) => unknown);
  /** Adds a clear affordance to the lookup editor (commits `null`). */
  allowClearing?: boolean;
}

/** In-memory lookup — IDENTICAL to the current FsGridLookup. */
export interface FsGridLocalLookup extends FsGridLookupBase {
  /** Array of lookup items, resolved synchronously client-side. */
  dataSource: readonly unknown[];
}

/** One editor/search page request. */
export interface FsGridLookupLoadOptions {
  /** Trimmed query text ('' = unfiltered first page). */
  searchText: string;
  /** Items to skip (page * pageSize). */
  skip: number;
  /** Page size. */
  take: number;
}

export interface FsGridLookupLoadResult {
  /** The page of lookup ITEMS (displayExpr/valueExpr apply to each). */
  items: readonly unknown[];
  /** Total matches for `searchText` — drives the load-more affordance. */
  totalCount: number;
}

/** Remote (deferred) lookup — the grid never fetches; the consumer's callbacks do. */
export interface FsGridRemoteLookup extends FsGridLookupBase {
  /**
   * Search + page the lookup list. Called by the dropdown editor (debounced)
   * and by the first-page prefetch. Rejections surface as the editor error
   * state (§8.1). The grid dedupes identical in-flight requests and discards
   * stale responses (monotonic request id per editor instance).
   */
  load: (options: FsGridLookupLoadOptions) => Promise<FsGridLookupLoadResult>;
  /**
   * Batch-resolve display ITEMS for keys visible in cells but absent from the
   * cache (§6.2). Called with deduped keys, chunked (max 100/call). Omitted =
   * unresolved keys render their raw-key fallback permanently (documented).
   */
  resolveByKeys?: (keys: readonly unknown[]) => Promise<readonly unknown[]>;
  /** Min characters before `load` fires with a query; below it the editor
   *  shows the unfiltered first page. Default 0. */
  minSearchLength?: number;
  /** Query debounce in ms. Default 300. */
  searchTimeout?: number;
  /** Page size for `load`. Default 30. */
  pageSize?: number;
}

export type FsGridLookup = FsGridLocalLookup | FsGridRemoteLookup;

/** Discriminator helper (exported from the types file). */
export function isRemoteLookup(l: FsGridLookup): l is FsGridRemoteLookup;
```

Notes:

- `searchText` matching semantics are the consumer's (typically
  case-insensitive `contains` server-side); the grid imposes nothing.
- `resolveByKeys` returns **items** (not `{key, text}` pairs) so
  `displayExpr`/`valueExpr` stay the single mapping vocabulary; items whose
  `valueExpr` doesn't match a requested key are ignored, requested keys missing
  from the result are marked failed (§6.2).
- `allowClearing` keeps today's semantics in `<fs-select>` (blank null option)
  and maps to the ✕ clear affordance in the searchable editor.
- The wire envelope maps 1:1 onto the backend's `LoadOptions`
  (`skip`/`take`/`filter`) — consumers translate in their service layer, the
  grid stays transport-agnostic (same stance as `remoteLoad`, types.ts:748-767).

---

## 6. Display resolution pipeline

### 6.1 Sync path (in-memory) — unchanged

`makeDisplayText` keeps the current behaviour (normalize-columns.ts:497-524):
`format` wins → lookup `find` → dataType fallback. Perf note (existing,
documented): resolution is O(n) per cell; normalization will build a
`Map<serializedKey, text>` once per lookup array identity instead — a pure
optimisation with identical observable behaviour.

### 6.2 Async path (remote)

New pure engine module `engine/lookup-resolution.ts` (no Angular, unit-testable
like the other engine modules):

- **Cache**: per column id, `Map<string /* serializeKey(key) */, LookupCacheEntry>`
  where `LookupCacheEntry = { text: string } | { failed: true }`. Seeded from
  every source that sees items: editor `load` pages, `resolveByKeys` results,
  and (optionally) consumer-provided warm-up via `columnOption`.
- **Collection**: a planner function takes the current render rows + remote
  lookup columns and returns the deduped set of unresolved keys per column
  (skipping keys already cached, failed, or in flight).
- **Batching**: the shell flushes the planner once per compute pass
  (microtask-coalesced, same pattern as README.md:1121), chunks ≤ 100 keys,
  calls `resolveByKeys`, writes results, marks missing keys `failed`.
- **Reactivity**: the cache lives behind a `signal` version counter on the
  shell; `getDisplayText` for a remote-lookup column closes over a resolver
  handle `(key) => string | undefined` instead of the array `find`. Bumping the
  version recomputes the leaves' dependents (OnPush-safe), so cells, group
  labels, header-filter texts, filter-panel text and export all pick up
  resolved texts through the **existing** `getDisplayText` call sites — no new
  per-surface wiring.

### 6.3 What renders while unresolved

- Cell text: **empty**, with modifier class `fs-data-grid__cell--resolving`
  (subtle reduced-opacity pulse via existing tokens; no spinner per cell).
- After resolution: the text, normally.
- After failure (`resolveByKeys` missing, rejected, or key absent from its
  result): fallback to the dataType default text of the RAW key
  (`String(key)` path, normalize-columns.ts:500-513) with modifier
  `fs-data-grid__cell--unresolved`; no automatic retry (avoids request storms).
  `refresh()` and any `lookup` config identity change clear the cache and
  failed set.
- Export (§27) serialises whatever `getDisplayText` returns at export time:
  resolved text, or the raw-key fallback for unresolved/failed keys —
  documented in the README v1-gaps list. (Open question 4 offers a stricter
  alternative.)

---

## 7. Sorting / filtering / grouping semantics (explicit decisions)

| Operation | In-memory lookup | Remote lookup |
| --- | --- | --- |
| **Sorting** | **CHANGE — sort by display text** (reference parity). Implemented as a default sort-value resolver in `resolveSortValue`: when the column has a lookup and neither `calculateSortValue` nor `sortingMethod`, the sort value is `getDisplayText(cellValue)`. Explicit hooks always win. | **Sort by KEY** (documented deviation): display order would be nondeterministic while the cache fills and would reshuffle as keys resolve. Consumers wanting text order use `remoteOperations`/server sorting or supply `calculateSortValue`. The header still shows the sort affordance; the README documents the semantics. |
| **Grouping** | Buckets by key (unchanged — distinct keys with identical texts stay distinct groups, documented); group ORDER follows the sorting decision → text order. Group label = display text (unchanged, grouping.ts:178). | Buckets by key, order by key, label from the cache (resolving/fallback states as §6.3). |
| **Filter row** | Exact-key equality via select (unchanged, filter-row.ts:183-215). | Exact-key equality; the cell renders the searchable editor (§8.3) instead of a static select. |
| **Header filter** | Distinct keys of loaded rows, `anyof`/`noneof` by key (unchanged). | Same mechanics; item texts resolve through the cache (the distinct pass enqueues its keys like cells do). Popup search filters the resolved texts client-side — it does NOT call `load` (the candidate set is only the loaded rows' keys; searching the full remote list would produce filter values matching zero loaded rows). |
| **Filter builder** | Exact-key select (unchanged). | Searchable editor, `=`/`<>`/`anyof`/`noneof` by key. |
| **Search panel** | Display-text predicate (unchanged, filtering.ts:780-785). | Predicate reads the cache: matches resolved texts, plus raw-key text for unresolved keys — i.e. it matches exactly what is rendered. Stays an embedded (non-serialisable) predicate for `remoteLoad`, unchanged flag semantics. |
| **Filter expressions / getCombinedFilter / remoteLoad** | Values are KEYS in all expressions (unchanged) — keys serialise cleanly to the backend `LoadOptions.filter`. | Same. This is the deliberate deviation from "filtering by display text": expressions stay key-valued and serialisable; only the UI affordances speak text. |

The one behavioural change for existing consumers is the in-memory sort order
(key → text). It matches the reference grid and the visible expectation
('Paused' sorts under P). Consumers relying on key order can pin it with
`calculateSortValue: col.dataField`.

---

## 8. Editor integration

### 8.1 The searchable paged dropdown — extend `fs-autocomplete`

Decision: extend `fs-autocomplete` (no new dependency, reusable outside the
grid) with an **externally-driven mode**, rather than a grid-private clone:

```ts
/** When set, filtering/paging are the parent's job: the component stops
 *  filtering `options` client-side and emits query/paging intents instead. */
readonly serverDriven = input(false);
readonly loading = input(false);
readonly errorText = input<string | undefined>(undefined);   // error row + Retry
/** Total matches server-side; > options().length shows the load-more row. */
readonly totalCount = input<number | undefined>(undefined);
readonly minSearchLength = input(0);   // renders the "Type N+ characters" hint row
readonly debounce = input(0);          // ms; 0 = emit immediately

readonly queryChanged = output<string>();      // debounced, trimmed
readonly loadMoreRequested = output<void>();   // load-more row clicked / list end reached
readonly retryRequested = output<void>();
```

Behaviour in `serverDriven` mode: `filteredOptions` ≡ `options` (no client
filter); opening emits `queryChanged('')`; the selected value's label may be
absent from `options` — a new optional `selectedLabel` input bridges it (the
grid passes the cache text so the closed editor shows 'Paused', not blank).
Everything else (overlay, keyboard model, clear ✕, CVA) is reused. Default
mode is untouched — existing consumers unaffected.

### 8.2 Cell editor (`fs-data-grid-cell-editor`)

- `editorKind` (cell-editor.ts:107-120) gains `'remoteLookup'` when
  `isRemoteLookup(lookup())`.
- The remote branch renders the extended `<fs-autocomplete serverDriven>` and
  owns the load state machine per editor instance:
  - open → `load({searchText:'', skip:0, take:pageSize})` (skipped when
    `minSearchLength > 0`? No — the empty query is exempt from
    minSearchLength; it always shows the first unfiltered page);
  - `queryChanged` (debounced by `searchTimeout`) → new request, `skip: 0`,
    replaces items; queries shorter than `minSearchLength` (except '') show
    the hint row and do not fire;
  - `loadMoreRequested` → same query, `skip += pageSize`, appends;
  - stale responses discarded (request id); identical query+page in-flight
    dedup; per-open LRU (last 10 queries) so backspacing re-renders instantly;
  - picked option → `valueChange.emit(key)` + cache seed `{key → label}` so
    the committed cell renders instantly without a resolve round-trip;
  - clear ✕ (shown when `allowClearing`) → `valueChange.emit(null)`.
- In-memory lookups keep the `'lookup'` kind and `<fs-select>` **unchanged**.
  (Follow-up option, out of scope: auto-upgrade large in-memory lists to the
  client-filtered `fs-autocomplete`.)

### 8.3 Edit form / popup editing

No structural change: `fs-data-grid-edit-form.component.html:62-71` already
delegates to the cell editor, which now branches per lookup variant. Size `md`
per existing form styling.

### 8.4 Filter row

`filter-row.ts` `editorKindFor` (line 183): a **remote** lookup maps to the
cell editor's remote branch (rendered like the `'between'`/default path via
`<fs-data-grid-cell-editor>`, filter-row html) instead of the static
`<fs-select>`; committing a pick writes `filterValue = key`, clearing writes
`null` ('(All)' semantics preserved via the editor's ✕, which is always
enabled in the filter row regardless of `allowClearing`). The operation
chooser stays suppressed (exact value, filter-row.ts:188-196). In-memory
lookups keep the static select.

### 8.5 Header filter

Unchanged UI (`fs-data-grid-header-filter`). The shell's item computation
(`fs-data-grid.component.ts:2607`) runs the distinct keys through the cache
and enqueues unresolved ones; items render with resolving/fallback texts and
update as the batch resolves (items input is signal-derived).

### 8.6 Filter builder

`lookupOf` (filter-builder.ts:148-150) flows the union type through to the
value editor; the cell editor branches as in §8.2. `anyof`/`noneof` value
lists in the builder pick keys one at a time via the same editor (v1: single
pick appends — matches current builder value-editing pattern).

---

## 9. Component changes

| File | Change |
| --- | --- |
| `fs-data-grid.types.ts` | §5 union (`FsGridLocalLookup`/`FsGridRemoteLookup` + load option/result types + `isRemoteLookup`); README §-refs updated |
| `engine/lookup-resolution.ts` (**new**) | Pure cache + unresolved-key planner + chunking; no Angular |
| `engine/lookup-resolution.spec.ts` (**new**) | Engine tests (§11) |
| `engine/normalize-columns.ts` | `makeDisplayText`: map-based in-memory resolution; remote branch takes a resolver handle parameter supplied by the shell (signature of `normalizeColumns` gains an optional resolver-provider argument; existing callers/spec fixtures unaffected by default) |
| `engine/sorting.ts` | `resolveSortValue`: display-text default for in-memory lookup columns (§7); remote columns keep raw key |
| `fs-data-grid.component.ts` | Owns the per-column cache signal + version; microtask-coalesced resolve flush over `displayRows`; header-filter item enqueue; passes resolver into normalization; `refresh()`/lookup-identity-change invalidation |
| `fs-data-grid-cell-editor.component.ts/.html` | `'remoteLookup'` kind + load state machine (§8.2) |
| `fs-autocomplete.component.ts/.html/.scss` | `serverDriven` mode (§8.1): loading/error/load-more/hint rows, `selectedLabel`, outputs |
| `fs-data-grid-filter-row.component.ts/.html` | Remote lookup cells → cell editor instead of static select (§8.4) |
| `fs-data-grid-filter-builder.component.ts` | Union type flows through `FsDataGridFilterBuilderColumn.lookup` |
| `fs-data-grid.component.scss` | `--resolving` / `--unresolved` cell modifiers |
| `README.md` | Contract section for remote lookups; v1-gaps additions (remote sort-by-key, export raw-key fallback, header-filter search scope) |
| `gallery.component.ts/.html` | §10 demos |

No new dependencies; Angular 20 standalone + signals + OnPush throughout; all
sub-components stay presentational (README rules 10-11).

---

## 10. Gallery demo plan

Extend the existing `fs-data-grid` gallery section (`shared/gallery/gallery.component.ts`,
demos at :2782+; status lookup fixture `gridStatusLookup` already exercises the
in-memory path at :2633, :2794, :2890).

**Demo: "Lookup columns" (new dedicated demo)**

1. **In-memory lookup** — the existing status column shape
   (`{ dataField: 'status', lookup: { dataSource, valueExpr, displayExpr, allowClearing: true } }`)
   with editing + filter row + header filter + grouping enabled, demonstrating
   the NEW text-order sorting.
2. **Simulated remote lookup** — a `productId` column against a generated
   10 000-item product list held in the component:
   - `load`: in-memory `contains` filter + `skip`/`take` slice behind a
     ~400 ms `setTimeout` promise; logs each call to a small request console
     under the grid (proves debounce, paging, dedup);
   - `resolveByKeys`: ~300 ms latency batch resolve (proves the cells'
     resolving → resolved transition on first paint and after paging);
   - a "fail resolves" toggle making `resolveByKeys` reject (proves the
     raw-key fallback + `--unresolved` styling);
   - `minSearchLength: 0`, `pageSize: 30`, `searchTimeout: 300`,
     `allowClearing: true`;
   - editing enabled in cell mode + a popup-form variant toggle; filter row +
     header filter + search panel on.
   - The demo's `load` translates its arguments through the backend
     `LoadOptions` envelope shape in the snippet text, so the copy-paste
     example shows the real service-layer mapping.

Demo snippet strings updated accordingly (gallery pattern at :2925-2946).

---

## 11. Test plan

**Engine (Karma/Jasmine, pure — CHROME_BIN=Edge per project setup):**

- `lookup-resolution.spec.ts`: cache hit/miss; dedup of in-flight keys;
  chunking >100; failed-key marking (reject, partial result); invalidation;
  planner ignores in-memory columns and cached/failed keys.
- `normalize-columns.spec.ts` (extend :494-608): map-based in-memory
  resolution keeps all existing expectations; remote column + resolver handle
  → resolved text / '' while pending / raw-key fallback on failed; `format`
  still wins over both variants.
- `sorting.spec.ts`: in-memory lookup sorts by display text asc/desc; explicit
  `calculateSortValue`/`sortingMethod` win; remote lookup sorts by key.
- `filtering.spec.ts`: search predicate/expression against cache-resolved and
  unresolved texts; header-filter distinct items for a remote column.

**Component behaviour specs (`fs-data-grid.behavior.spec.ts` pattern):**

- Remote cell display: rows render, keys enqueue, one batched `resolveByKeys`
  per compute pass, cells update; failure path styling.
- Cell editor remote flow: open → first page; type (fakeAsync debounce) →
  replaced page; load-more appends and respects `totalCount`; stale-response
  discard; pick commits key and closed editor shows the label; clear commits
  null; Escape cancels (no commit).
- Filter row remote cell: pick filters by `=` key; clear resets; expression
  appears in `getCombinedFilter()` with the KEY value.
- Edit form remote editor renders and commits through §7.4 changes.

**`fs-autocomplete` specs:** `serverDriven` mode — no client filtering,
`queryChanged` debounce, load-more/hint/error rows, `selectedLabel`, and
regression of default mode.

**Manual gallery checklist:** latency/console demo, fail-toggle, keyboard-only
editor pass, adaptive/narrow layout.

---

## 12. Risks & open questions

Risks:

- **In-memory sort-order change** (§7) is user-visible in every existing grid
  with a lookup column (gallery status columns; any feature consumers).
  Mitigation: release note + `calculateSortValue` escape hatch.
- **Cache-driven re-render churn**: each resolve bump recomputes leaf-derived
  signals. Mitigation: one version bump per batch, not per key.
- **`normalizeColumns` signature growth** ripples into engine spec fixtures —
  kept optional/defaulted.
- **Filter-row editor width**: the searchable editor in a 90 px filter cell —
  overlay width decouples from trigger width (CDK overlay min-width), needs
  design eyes in the gallery pass.
- **Keys that are objects**: `serializeKey` handles them (engine/keys.ts), but
  `resolveByKeys` consumers receive raw keys — documented that keys should be
  JSON-stable primitives for remote lookups.

Open questions: see the executive summary list (decision needed before build).

---

## 13. Estimated scope

| Work package | Estimate |
| --- | --- |
| Types + engine (resolution module, normalize-columns, sorting) + engine tests | 1.5 d |
| `fs-autocomplete` serverDriven mode + specs | 1 d |
| Shell resolution pipeline (cache signal, flush, invalidation) | 1 d |
| Cell editor remote branch + edit form + behaviour specs | 1 d |
| Filter row / builder / header filter integration + specs | 1 d |
| Gallery demos + README/contract updates + manual pass | 0.5–1 d |
| **Total** | **~6–6.5 dev-days** |

Sequencing: types+engine → autocomplete → shell pipeline → editors → filter
surfaces → gallery/docs. Each stage lands green independently (in-memory path
never breaks mid-build).
