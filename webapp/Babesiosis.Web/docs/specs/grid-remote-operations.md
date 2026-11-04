# `<fs-data-grid>` — Remote operations (server-side filtering + paging) — feature spec

Status: **proposed** · Scope: frontend shell wiring + one new engine function + gallery demo · Backend: **no changes required**
Spec section number: **§30** (the engine and types already cite §30 — this document is that section).

---

## 1. Summary & goals

The grid today is client-side only: every row is loaded up front and filtering, sorting and
paging run in memory. This spec delivers **remote operations** — the grid delegates
**filtering** and **paging** (and **sorting**, which falls out naturally: the engine composer
and the backend ordering pipeline both already support it — it is in scope) to a consumer-supplied
backend, emitting a load-options descriptor whenever its query state changes and rendering
whatever page of rows the consumer writes back.

Design pillars:

1. **The grid never fetches.** It emits a `remoteLoad` event; the consumer issues the HTTP
   request through its own service, then writes `[data]` (+ `[totalCount]`) and drives
   `[loading]`. This keeps the grid free of `HttpClient`, auth, and endpoint knowledge.
2. **Reuse the existing backend contract.** The wire shape is exactly the backend's
   `SearchCommand.loadOptions` envelope (`skip`/`take`/`sort`/`filter`/`requireTotalCount`)
   already consumed by every `*-get` search function. No new wire format, no backend change.
3. **The engine work is already done.** `engine/remote.ts` (flag resolution, descriptor
   composition, structural dedupe) exists with full unit coverage. What remains is the shell
   wiring, one filter-lowering function, the pager's server `totalCount`, and the gallery demo.

Goals: opt-in per operation; zero behavior change for existing client-side consumers; a
first-class consumer recipe that plugs straight into `ItemsViewModel<T>`/`PagedResult<T>`
responses.

Non-goals (v1): remote grouping, remote summaries, remote group paging, remote header-filter
distinct values, infinite/virtual scrolling against a remote source, a generic data-source
abstraction object.

## 2. Reference behavior

The reference grid's custom-data-source pattern (verified against its live demo):

- A load function receives the data-processing settings the grid needs delegated:
  `{ skip, take, requireTotalCount, sort, filter }` (plus group/summary dimensions we do not
  delegate in v1). Only dimensions whose operation is remote appear.
- The load function returns `{ data, totalCount }`; `totalCount` is required whenever
  `requireTotalCount` was set (remote paging), because the grid can no longer count rows itself.
- `remoteOperations: true` delegates everything; an object (`{ filtering: true, paging: true }`)
  delegates per operation; anything not delegated stays in the client engine.
- Loading state: the grid shows its loading overlay while the consumer's request is in flight.
- Error state: the reference implementation throws a generic "data loading error"; rows keep
  their previous content. We match this: errors are the consumer's to surface (toast /
  `noDataText`), the grid just stops loading. See §12 for the optional error-surface question.

Our deviation from the reference: instead of a store object handed into the grid, we emit an
**output event** and take **inputs** back (`data`, `totalCount`, `loading`) — idiomatic for a
signal-based standalone component and it keeps the grid presentation-pure.

## 3. Current state

### 3.1 Frontend — engine (done)

`Babesiosis.Web/src/app/shared/components/fs-data-grid/engine/remote.ts` is complete and
pure (no Angular, no DOM):

- `resolveRemoteFlags(config)` — `remote.ts:32-44`: `true` → all three ops; object → per-op;
  `false | null | undefined` → fully client-side.
- `composeRemoteLoadOptions({flags, leaves, filterParts, pageIndex, pageSize})` —
  `remote.ts:89-122`: composes the wire descriptor. Paging → `skip = pageIndex * pageSize`,
  `take = pageSize`, `requireTotalCount: true` (`remote.ts:100-104`). Sorting → `sort` entries
  from `activeSortColumns` (grouped columns by `groupIndex` first, then `sortIndex`), selector
  = `dataField ?? id` (`remote.ts:106-112`). Filtering → the combined §16.2 expression via
  `getCombinedFilterExpression`, with predicate-**function** parts (custom
  `calculateFilterExpression` hooks, display-text search matchers) recursively stripped and
  the strip reported as `hasNonSerializableFilters` (`remote.ts:114-119`, stripper at
  `remote.ts:170-213`).
- `optionsEqual(a, b)` — `remote.ts:132-148`: deep structural dedupe compare (Dates by time,
  `NaN` self-equal, `requireTotalCount` `undefined ≡ false`, `sort` `undefined ≡ []`).

`engine/remote.spec.ts` covers all of the above (~60 cases: flag resolution, dimension gating,
sort ordering, filter composition, predicate stripping incl. connective bookkeeping, equality).

### 3.2 Frontend — types (done)

`fs-data-grid.types.ts`:

- `FsGridRemoteOperations { filtering?; sorting?; paging? }` — `types.ts:742-746`.
- `FsGridRemoteLoadOptions { skip?; take?; requireTotalCount?; sort?; filter? }` —
  `types.ts:756-767`; doc comment states the shape "mirrors the backend's existing
  `SearchCommand.loadOptions` envelope" (`types.ts:748-755`).
- `FsGridRemoteLoadReason = 'init' | 'filter' | 'sort' | 'page' | 'search' | 'refresh' | 'save' | 'state'`
  — `types.ts:770-778`.
- `FsGridRemoteLoadEvent { options; reason; hasNonSerializableFilters }` — `types.ts:785-796`.

### 3.3 Frontend — shell (NOT wired)

`fs-data-grid.component.ts`:

- `remoteOperations = input<unknown>(undefined)` — `component.ts:405`, doc'd "typed but
  unsupported in v1".
- The only runtime behavior is a one-time `console.warn` — `component.ts:6072-6075`
  (`remoteOpsWarned` flag at `:5815`).
- **Nothing else exists**: no `remoteLoad` output, no `totalCount` input, no pipeline bypass.
  The computed chain (`workingData → filteredRows → sortedRows → renderRows →
  pagedRenderRows`, README "The computed pipeline", README:385-406) always filters/sorts/pages
  client-side. `README.md:114` and `README.md:153` record the v1 gap.
- Pager (`fs-data-grid-pager.component.ts`) derives `pageCount` from `totalRenderRows` —
  `pager.component.ts:77-81` — i.e. from the **loaded** rows; it has no server-count concept.
  `infoText {2}` substitutes `totalRows` (`:122-127`); the `'all'` page-size option maps to
  the loaded render-row count (`:96-111`).
- `loading = input(false)` already exists (`component.ts:369`) and renders the loading overlay.
- Existing input debounces that remote mode inherits for free: filter-row `applyFilter:'auto'`
  commits after a 400ms per-column debounce (README:587-593), search panel applies after
  250ms (README:580-583). Every filter mutation already resets `pageIndex` to 0
  (`resetPageIndexAfterFilterChange`, README:605-606).

### 3.4 Frontend — filter expression grammar (client)

`engine/filtering.ts` — the §14.2 grammar the combined filter is built in
(`types.ts:52-56`): condition `[selector, op, value]`, shorthand `[selector, value]`,
negation `['!', expr]`, connective groups `[expr, 'and'|'or', expr, …]` ('and' implied).
Operation tokens (`filtering.ts:39-43`):
`=  <>  >  >=  <  <=  startswith  endswith  contains  notcontains  between  anyof  noneof`.

Productions that matter for the wire:

- Filter row `between` → `[selector, 'between', [start, end]]` (`filtering.ts:544-552`).
- Header filter include/exclude → `[selector, 'anyof' | 'noneof', values[]]`
  (`filtering.ts:568-588`); the "(Blanks)" item contributes the `FS_GRID_BLANKS` sentinel
  (`filtering.ts:25`, `:231`) which client-side matches `null`/`undefined`/`''`.
- Search panel → per-string-column `[selector, 'contains', text]` conditions or-joined
  (`filtering.ts:745`, `:787`); columns with display-text matchers contribute predicate
  functions (stripped on the wire).
- Client string matching is **case-insensitive** (`comparableString` lowercases,
  `filtering.ts:107-110`).

### 3.5 Backend (already fits — read-only evidence)

- `Babesiosis.Core/Commands/LoadOptions.cs:17-40` — `LoadOptions { Skip, Take, Sort:
  List<SortOption{Selector, Desc}>, RequireTotalCount, Filter: IList }`. The `Filter` array
  uses exactly the grid's grammar: "binary `[selector, op, value]`, group
  `[expr, "and"|"or", expr]`, negation `["!", expr]`" (doc comment `:8-16`);
  `FilterArrayJsonConverter` (`:58-102`) materializes leaves as CLR primitives
  (numbers as `double`).
- `Babesiosis.Core/Commands/SearchCommand.cs:3-6` — `SearchCommand { LoadOptions }`.
- `Babesiosis.Core/Search/DynamicLinqFilter.cs` — translates the array into a parameterized
  dynamic-LINQ predicate. **Supported operators** (`:152-189`): `=`/`==`, `<>`/`!=`, `>`,
  `<`, `>=`, `<=`, `contains`, `notcontains`, `startswith`, `endswith`, plus the
  two-element `=` shorthand (`:126-130`), null equality without parameters (`:146-150`),
  groups and `!` negation (`:82-112`). **Anything else throws**
  `Unsupported filter operator` (`:187-188`) — notably **no `between`, `anyof`, `noneof`**.
  Selectors are regex-validated and reflection-resolved to real CLR property paths
  (`:24-25`, `:211-231`) — unknown fields throw. Values are coerced to the member type
  (`:233-285`): ISO strings → `DateTime`/`DateTimeOffset`/`DateOnly` (round-trip parse),
  strings/numbers → enums, `Guid.Parse`, `IConvertible` numerics.
- `Babesiosis.Core/Extensions/LoadOptionsExtensions.cs:32-71` — `LoadPageAsync`: applies
  filter + ordering, **`Take == 0` falls back to 1000** (`:55`), computes `totalCount` via
  `CountAsync()` **unconditionally** (`:58` — `RequireTotalCount` is not consulted), returns
  `PagedResult<T> { Items, Paging { TotalCount, PageIndex, PageSize } }` (`:61-70`).
- Response envelope: `ItemsViewModel<T> { Page: PagedResult<T> }`
  (`Babesiosis.Core.API/Manage/Roles/ViewModels/ItemsViewModel.cs:7-10`) + a `Permissions`
  dictionary on the base `ViewModel` (see `GetMembersController.BuildResponse`).
- Representative controller: `Babesiosis.Core.API/Manage/Members/Controllers/GetMembersController.cs:65-108`
  — `HandleCommand(userId, SearchCommand)` → `command.LoadOptions.LoadPageAsync(query, map)`
  (`:84`). Note `:164-171`: the **serialized `LoadOptions` JSON is a cache-key component** —
  descriptor stability matters (§12).
- Function wrapper: `Babesiosis.Core.Functions/Manage/Members/GetMembers.cs:30-42` —
  `[Function("members-get")]`, POST, JWT validation, `ReadFromJsonAsync<SearchCommand>()`.
- Frontend service convention: `Babesiosis.Web/src/app/manage/projects/projects.service.ts:30-32`
  — `post<ItemsViewModel<ProjectViewModel>>(`${this.URL}/projects-get`, command)` where
  `this.URL = configService.coreAPI('')` is assigned in the constructor from `ConfigurationService`
  where `command: SearchCommand` from `app/core/commands/search.command.ts` (a `LoadOptions`
  mirror, `search.command.ts:9-26`); `ServiceBase` + the auth service attach the JWT.

## 4. Gap analysis

| # | Gap | Where |
|---|-----|-------|
| G1 | Shell ignores `remoteOperations` (warn-only); input typed `unknown` | `component.ts:405`, `:6072-6075` |
| G2 | No `remoteLoad` output; no emission scheduling, dedupe application, or reason tracking | shell |
| G3 | No `totalCount` input; pager/pageCount/infoText derive from loaded rows only | `component.ts`, `pager.component.ts:77-127` |
| G4 | Client pipeline always filters/sorts/pages — no per-flag bypass | README:385-406 pipeline |
| G5 | **Wire mismatch**: grid emits `between` / `anyof` / `noneof` / `FS_GRID_BLANKS`, backend `DynamicLinqFilter` throws on all four | `filtering.ts:39-43` vs `DynamicLinqFilter.cs:187-188` |
| G6 | `'all'` page-size option is meaningless under remote paging (grid doesn't know "all") and `take: 0` triggers the backend's 1000 fallback | `pager.component.ts:96-111`, `LoadOptionsExtensions.cs:55` |
| G7 | No gallery demo, no consumer recipe | gallery |
| G8 | Case-sensitivity semantics differ (client lowercases; server uses provider collation) | `filtering.ts:107-110` vs `DynamicLinqFilter.cs:171-190` |

G5 is the load-bearing one: we close it **on the frontend** with a wire-lowering pass
(§5.3/§6) so the backend stays untouched.

## 5. Proposed API

### 5.1 Grid inputs / outputs (shell surface)

```ts
// fs-data-grid.component.ts — replaces the unknown-typed input (component.ts:405)
readonly remoteOperations = input<boolean | FsGridRemoteOperations | undefined>(undefined);

/**
 * §30.4 — total row count on the SERVER after filtering, from the consumer's
 * last load response (PagedResult.Paging.TotalCount). Required whenever remote
 * paging is on (the emitted options carry requireTotalCount: true); ignored —
 * with a one-time console.warn if set — when it is not.
 */
readonly totalCount = input<number | undefined>(undefined);

// Already exists (component.ts:369) — drives the loading overlay.
readonly loading = input(false);

/**
 * §30.3 — fires whenever the delegated query state changes (structurally, per
 * optionsEqual) and once on init when any operation is remote. The grid never
 * fetches: handle this, call your service, then write [data] (+ [totalCount])
 * and drive [loading].
 */
readonly remoteLoad = output<FsGridRemoteLoadEvent>();
```

All event/config types already exist (`types.ts:742-796`) and are re-used verbatim:
`FsGridRemoteOperations`, `FsGridRemoteLoadOptions`, `FsGridRemoteLoadReason`,
`FsGridRemoteLoadEvent`.

### 5.2 Consumer contract (the "load function")

The consumer-side shape, standardized for docs/gallery (not a grid import — it is just the
existing service convention):

```ts
// What the grid hands you:
interface FsGridRemoteLoadEvent {
  options: FsGridRemoteLoadOptions;   // → SearchCommand.loadOptions, verbatim
  reason: FsGridRemoteLoadReason;
  hasNonSerializableFilters: boolean; // predicate-function parts were dropped from options.filter
}

// What you do with it (canonical recipe, mirrors projects.service.ts:30-32):
onRemoteLoad(e: FsGridRemoteLoadEvent): void {
  this.loadRequests$.next(e.options);           // subject piped through switchMap → stale
}                                                // responses cancel themselves (§7.4)

// service:
search(options: FsGridRemoteLoadOptions): Observable<ItemsViewModel<RowVm>> {
  return this.post<ItemsViewModel<RowVm>>(`${this.URL}/things-get`,
    new SearchCommand(options as LoadOptions));  // shapes are wire-identical
}

// response → grid inputs:
rows.set(vm.page.items);
total.set(vm.page.paging.totalCount);
```

`FsGridRemoteLoadOptions` and `app/core/commands/search.command.ts#LoadOptions` are
field-for-field compatible (`skip`, `take`, `sort[{selector,desc}]`, `filter`,
`requireTotalCount`); no adapter is needed. Consumers whose server field names differ from
column `dataField`s transform `options.sort[].selector` / `options.filter` selectors in
their own handler (documented; the grid does not remap).

### 5.3 Wire filter serialization — mapping onto the backend grammar

`options.filter` is the grid's §14.2 expression **after a lowering pass** that removes the
three grid-only operators the backend translator rejects (`DynamicLinqFilter.cs:187-188`).
JSON encoding is plain `JSON.stringify` of the arrays — `Date` values serialize to ISO-8601
strings via `toJSON`, which the backend round-trip-parses per the member's CLR type
(`DynamicLinqFilter.cs:250-265`).

| Grid expression | Wire (lowered) form | Backend translation |
|---|---|---|
| `['age', '=', 30]` | unchanged | `Age == @0` |
| `['name', 'Bob']` (shorthand) | unchanged | `Name == @0` (`:126-130`) |
| `['age', '<>', 30]` | unchanged | `Age != @0` |
| `['age', '<', 30]` / `['age', '>', 30]` | unchanged | `Age < @0` / `Age > @0` |
| `['age', '<=', 30]` / `['age', '>=', 30]` | unchanged | `Age <= @0` / `Age >= @0` |
| `['due', 'between', [a, b]]` | `[['due', '>=', a], 'and', ['due', '<=', b]]` | `(Due >= @0 && Due <= @1)` |
| `['due', 'between', [a, null]]` (open end) | `['due', '>=', a]` (and mirror for `[null, b]`) | `Due >= @0` |
| `['name', 'contains', 'ann']` | unchanged | `(Name != null && Name.Contains(@0))` |
| `['name', 'notcontains', 'ann']` | unchanged | `(Name != null && !Name.Contains(@0))` |
| `['name', 'startswith', 'A']` | unchanged | `(Name != null && Name.StartsWith(@0))` |
| `['name', 'endswith', 'Z']` | unchanged | `(Name != null && Name.EndsWith(@0))` |
| `['status', 'anyof', [1, 2]]` | `[['status', '=', 1], 'or', ['status', '=', 2]]` | `(Status == @0 \|\| Status == @1)` |
| `['status', 'anyof', [1]]` | `['status', '=', 1]` (single unwraps) | `Status == @0` |
| `['status', 'noneof', [1, 2]]` | `['!', [['status', '=', 1], 'or', ['status', '=', 2]]]` | `!((Status == @0 \|\| Status == @1))` |
| `['tag', 'anyof', [FS_GRID_BLANKS]]` | `['tag', '=', null]` | `Tag == null` (`:146-150`) |
| `['tag', 'anyof', ['x', FS_GRID_BLANKS]]` | `[['tag', '=', 'x'], 'or', ['tag', '=', null]]` | `(Tag == @0 \|\| Tag == null)` |
| `[c1, 'and', c2]` / `[c1, 'or', c2]` | operands lowered recursively, connectives kept | `(… && …)` / `(… \|\| …)` |
| `[c1, c2]` (implied and) | `[c1', 'and', c2']` — the lowering pass makes implied connectives **explicit** | `(… && …)` |
| `['!', expr]` | `['!', lowered(expr)]` | `!(…)` |
| `(row) => boolean` anywhere | stripped (existing `remote.ts:170-213`), `hasNonSerializableFilters: true` | n/a |

Blanks caveat: the client blanks sentinel matches `null`/`undefined`/`''`; the wire lowers it
to `= null` only. For string columns where empty-string rows exist this is a documented
semantic narrowing (open question Q2 offers `[['tag','=',null],'or',['tag','=','']]` for
`dataType: 'string'` columns).

### 5.4 Loading + error events

- Loading: consumer-driven via the existing `[loading]` input; the recipe sets it `true` on
  emission and `false` on response/error. The grid does not auto-toggle it (it cannot know
  when the consumer's request settles).
- Error: v1 defines **no grid-side error UI**. On failure the consumer keeps the previous
  `[data]` (rows stay), clears `[loading]`, and surfaces its own toast — matching the
  reference grid's behavior where a failed load leaves the grid content unchanged. (Optional
  `errorText` input: open question Q5.)

## 6. Engine changes

One new pure function in `engine/remote.ts` (+ tests), slotted between composition and
emission:

```ts
/**
 * §30.6 — lowers a combined filter expression to the backend translator's
 * operator subset: 'between' → >=/<= and-pair (open ends drop their half),
 * 'anyof' → or-group of '=' conditions, 'noneof' → ['!', or-group],
 * FS_GRID_BLANKS → null comparison, implied 'and' connectives made explicit,
 * single-operand groups unwrapped. Conditions with supported operators pass
 * through by reference. Pure; never mutates.
 */
export function lowerFilterExpressionForWire(
  expr: FsGridFilterExpression | null,
): FsGridFilterExpression | null;
```

`composeRemoteLoadOptions` gains the call after predicate-stripping (`remote.ts:114-119`):
`options.filter = lowerFilterExpressionForWire(stripped.expr)`. `optionsEqual` needs no
change (it compares the lowered descriptors). Everything else in the engine is already built
(§3.1).

Also: no change to `filtering.ts` — client-side evaluation keeps the richer operator set.

## 7. Shell / component changes

All in `FsDataGridComponent` (`fs-data-grid.component.ts`); member names below are the
contract for the implementation session.

### 7.1 Flags + pipeline bypass

- `resolvedRemoteFlags = computed(() => resolveRemoteFlags(this.remoteOperations()))`.
  Delete the v1 warning block (`component.ts:6072-6075`) and the `remoteOpsWarned` field.
- `filteredRows`: when `flags.filtering`, **bypass** `combinedPredicate` entirely — return
  `workingData()` as-is. Stripped predicate parts are NOT applied locally either (the server
  owns filtering; `hasNonSerializableFilters` tells the consumer what was lost). Filter UIs
  (filter row, header filter, panel, builder, search box) stay fully interactive — they now
  edit *query state* instead of filtering rows.
- `sortedRows`: when `flags.sorting`, bypass `sortRows` — server order is display order.
  Header sort indicators still render from column state.
- `pagedRenderRows`: when `flags.paging`, **no slice** — `workingData` already is the page.
  `clampedPageIndex` clamps against the server page count (`ceil(totalCount / pageSize)`),
  not the loaded-row count.
- Operations *not* delegated keep running client-side over the loaded set (e.g. remote
  filtering + client paging pages the filtered result the server returned).

### 7.2 Pager `totalCount`

`fs-data-grid-pager.component.ts` gets one new optional input:

- `serverTotalRows = input<number | undefined>(undefined)` — when set (shell passes
  `totalCount()` under remote paging): `pageCount = ceil(serverTotalRows / pageSize)`
  (replacing the `totalRenderRows` derivation at `pager.component.ts:77-81`), `infoText {2}`
  substitutes it (`:122-127`), and the `'all'` page-size entry is **omitted** from
  `sizeOptions` (`:96-111`) with a one-time shell `console.warn` (an unbounded `take` would
  otherwise hit the backend's `Take == 0 → 1000` fallback, `LoadOptionsExtensions.cs:55`).
- Shell passes `totalRows`/`totalRenderRows` unchanged when paging is client-side.
- If remote paging is on and `totalCount` was never supplied after the first data write:
  `console.error` once (loud, per project convention for contract violations) and fall back
  to `pageCount = 1`.

### 7.3 Emission scheduling, debounce, dedupe

- A single `effect` tracks `composeRemoteLoadOptions(...)` over: `resolvedRemoteFlags`,
  `leaves` (sort state), the §16.2 filter parts (`dataSourceFilter`, `filterValue` gated by
  `filterPanelEnabledState`, per-column row/header parts, `searchText`),
  `clampedPageIndex`, `pageSizeModel`.
- **Debounce**: none added. Angular effects coalesce same-tick signal writes, and the
  expensive inputs are already debounced upstream — filter-row 400ms (README:587-593),
  search 250ms (README:580-583). Filter mutations already reset `pageIndex` to 0
  (README:605-606), so "type in filter" produces exactly one emission carrying both changes.
- **Dedupe**: keep the last emitted descriptor (`lastRemoteOptions`); skip emission when
  `optionsEqual(next, last)` (`remote.ts:132-148`). `refresh()` bypasses the dedupe and
  re-emits with reason `'refresh'`; `saveEditData()` completion re-emits with `'save'`
  (consumers reload after mutations); §22 state restore emits `'state'`; first emission after
  flags become active is `'init'`.
- **Reason attribution**: the effect diffs which dimension changed against `lastRemoteOptions`
  (filter → `'filter'`, sort → `'sort'`, skip/take → `'page'`); a search-text change that
  produced the filter delta reports `'search'`. When several dimensions change in one tick,
  precedence: `filter > sort > page` (matches user perception: the filter change caused the
  page reset).

### 7.4 Race handling / cancellation of stale requests

The grid does not own the HTTP call, so cancellation lives in the consumer — and the grid's
job is to make the safe pattern trivial and the unsafe one visible:

- Grid guarantees: emissions are **ordered** and **structurally deduped**; every emission
  reflects the complete current query state (never a partial delta). A consumer that pipes
  emissions through `switchMap` therefore always ends on the latest state — stale in-flight
  requests cancel themselves. This is the documented canonical recipe (§5.2, gallery §10).
- Late responses: a consumer that instead fires parallel requests may write stale `data`.
  Mitigation is consumer-side (`switchMap` / request-id check); the README gets an explicit
  "always `switchMap`" warning box.
- The grid tolerates `data`/`totalCount` arriving in any order and any number of times per
  emission (each write just re-renders); `loading` is purely cosmetic and never gates input.

### 7.5 Interactions with existing shell features

- `keyExpr`/selection/focused row: unchanged mechanics; see matrix (§9).
- State persistence (§22): `pageIndex`, `pageSize`, sort and filter state persist exactly as
  today; a restore recomputes the descriptor and emits `'state'`.
- Editing (§5-§8): row/cell/batch editing operates on the loaded page as today. The §7.4
  change overlay applies to `workingData`; after save the `'save'` re-emission refreshes.
- `refresh()` API: in remote mode re-emits (see §7.3) *and* still resets `workingData` from
  `data` as today.

## 8. Backend changes

**None required.** The emitted descriptor is consumed verbatim by the existing
`SearchCommand → LoadOptions → DynamicLinqFilter/LoadPageAsync` pipeline (§3.5); the lowering
pass (§6) keeps the wire inside the translator's operator subset. A demo endpoint is *not*
added — the gallery fakes the server in memory (§10).

Deliberately rejected alternative: extending `DynamicLinqFilter` with `between`/`anyof`/
`noneof`. It would work (and produce `IN (...)` SQL instead of or-chains) but forces a
lock-step backend+frontend deploy for a frontend feature and duplicates semantics in two
codebases. Revisit only if or-chain SQL for large header-filter selections measures badly
(risk R4).

Two backend behaviors the frontend must respect (documented, not changed):

- `Take == 0` → 1000-row fallback (`LoadOptionsExtensions.cs:55`): the grid always sends a
  positive `take` under remote paging; `'all'` is suppressed (§7.2).
- `totalCount` is computed on every call regardless of `requireTotalCount`
  (`LoadOptionsExtensions.cs:58`) — harmless; the grid sends `requireTotalCount: true` anyway
  for forward compatibility.

## 9. Feature-interaction matrix (remote filtering + paging on)

| Feature | Behavior under remote ops | Loud or silent |
|---|---|---|
| Filter row / builder / panel / header-filter UI | Fully interactive; edits emit `remoteLoad` instead of filtering locally | silent (by design) |
| Header-filter **distinct value list** | Built from **loaded rows only** — under remote paging the list shows the current page's values, not the dataset's | documented degrade; README caveat + open question Q3 (backend distinct endpoint is out of scope v1) |
| Search panel | Serializes to or-joined `contains` conditions on string columns; display-text matchers are stripped → `hasNonSerializableFilters: true` | silent + flagged on the event |
| Custom `calculateFilterExpression` returning a function | Stripped from the wire, not applied locally | flagged via `hasNonSerializableFilters` |
| Sorting (when `sorting: true`) | Server-ordered; indicators unchanged | silent |
| Sorting (when only filtering/paging remote) | Client sorts the loaded page — cross-page order is NOT global | documented degrade; README caveat recommends enabling remote sorting with remote paging |
| Grouping / group panel | Client-side over the **loaded page**; groups are page-scoped and may repeat across pages. Grouped columns do join the `sort` descriptor (groupIndex-first) when remote sorting is on, so page-scoped groups stay contiguous | documented degrade (`types.ts:735-741` already states grouping is client-side v1) |
| Summaries (total/group) | Computed over loaded rows only — a "total" is a page total. `skipEmptyValues` caveat already documented for remote sources (feature spec §skipEmptyValues, docs/data-grid-feature-spec.md:380) | one-time `console.warn` when summaries + remote paging are both configured |
| Virtual / infinite scrolling (`scrolling.mode: 'virtual' \| 'infinite'`) | **Unsupported with remote paging** (incremental window loads are a different contract) | **loud**: one-time `console.error`, scrolling falls back to `'standard'` |
| Selection (`selectedRowKeys`) | Keys persist across page loads (keys, not row refs). `selectAll` selects the **loaded page** only; header checkbox shows indeterminate when `selectedRowKeys.length` < `totalCount` | `console.warn` once on `selectAll` under remote paging |
| Deferred selection (`selectionFilter`) | Evaluated client-side against loaded rows only | documented degrade |
| Focused row + `autoNavigateToFocusedRow` | Navigates only within the loaded page; cannot page the server to find a key (feature spec docs/data-grid-feature-spec.md:739 documents this reference-grid failure mode — we do not replicate the key-probing requests) | documented |
| Editing | Operates on the loaded page; `'save'` re-emission after `saveEditData` | silent |
| Export | Exports loaded rows only (the current page under remote paging) | documented; README caveat |
| State persistence (§22) | Persists/restores as today; restore emits `'state'` | silent |
| `'all'` page size | Removed from the pager under remote paging | `console.warn` once if configured explicitly |

## 10. Gallery demo plan

New card in `shared/gallery/gallery.component.ts` next to the existing grid demos
(`GalleryGridAssignment` dataset, `gallery.component.ts:285-289`): **"Data grid — remote
operations (simulated server)"**.

- **Fake server**: a 500-row in-memory `GalleryGridAssignment[]`; a `fakeServerLoad(options:
  FsGridRemoteLoadOptions): Promise<{ items; totalCount }>` helper that (a) evaluates
  `options.filter` with the *engine's own* client evaluator, (b) applies `options.sort`,
  (c) slices `skip/take`, (d) resolves after a 400 ms artificial latency. This proves the
  descriptor is self-sufficient without any backend.
- **Console-visible load options**: every load `console.log`s
  `{ reason, options: JSON.stringify(options) }` and the demo card renders the last emitted
  descriptor in a `<pre>` under the grid — reviewers see exactly what would cross the wire.
- **Wiring**: `remoteOperations: { filtering: true, sorting: true, paging: true }`,
  `(remoteLoad)` → subject → `switchMap(fakeServerLoad)` → writes `rows` / `total` signals →
  `[data]`, `[totalCount]`, `[loading]` — i.e. the canonical §5.2 recipe, copy-pasteable.
- **Controls on the card**: latency slider (0–2000 ms), "fail next request" toggle (exercises
  the error recipe: toast + rows retained), per-operation checkboxes to flip
  `remoteOperations` flags live, and a request counter proving dedupe (paging back and forth
  to the same page state does not re-fire).
- Demonstrated surfaces: filter row (`between` on a date column — shows the lowered wire
  form), header filter (`anyof` incl. Blanks), search panel, sort, pager with server
  `totalCount` (info text "Page 2 of 25 (500 items)").

## 11. Test plan

Engine (`engine/remote.spec.ts` — extend):
- `lowerFilterExpressionForWire`: each row of the §5.3 table; nested groups; implied-and
  explicitation; open-ended between; single-element anyof unwrap; blanks-in-anyof; noneof;
  negation wrapping; pass-through-by-reference for already-lowered trees; null/empty in/out.
- Composition + lowering integration: `composeRemoteLoadOptions` output contains only
  backend-supported operators for every filter-UI production.

Shell (`fs-data-grid.behavior.spec.ts` — new describe blocks; Karma via Edge `CHROME_BIN`):
- Emission: `'init'` fires once when flags active; no emission when fully client-side;
  filter-row commit emits once with reason `'filter'` and `skip: 0`; page change emits
  `'page'`; sort click emits `'sort'`; search apply emits `'search'`; `refresh()` re-emits
  identical options; structurally-equal state does not re-emit (dedupe); reason precedence
  filter > sort > page.
- Bypass: with remote filtering, rows render unfiltered while filter UIs hold state; with
  remote paging, 20 supplied rows render in full with `totalCount: 500` and pager shows 25
  pages; with remote sorting, supplied order is preserved.
- Pager: server pageCount / infoText `{2}` / `'all'` suppression / missing-`totalCount`
  `console.error` fallback.
- Interaction guards: virtual scrolling + remote paging → `console.error` + standard mode;
  summaries warn; `selectAll` warn; selection keys survive a page swap.
- Data/loading: multiple `data` writes per emission tolerated; late `totalCount` write
  updates pager.

Backend: no changes → no new tests. (Existing `DynamicLinqFilter` coverage already exercises
the operator subset the lowered wire uses.)

Manual/UI pass: gallery demo card against the checklist in §10, both themes, `ui-test` skill
sweep on the gallery route.

## 12. Risks & open questions

Risks:
- **R1 — case-sensitivity drift**: client `contains` is case-insensitive
  (`filtering.ts:107-110`); server `Contains` follows the database collation (SQL Server
  default: case-insensitive; EF InMemory in tests: case-sensitive). Same filter, different
  rows across modes/tests. Mitigation: document; backend tests should assert against SQL
  collation semantics.
- **R2 — selector validity**: the wire selector is `dataField ?? column id`; unknown
  properties make `DynamicLinqFilter.ResolveMember` throw (`:211-231`) → a 500 from the
  function wrapper. Consumers with computed/unbound columns must set `allowFiltering: false`
  on them or remap selectors in the handler. README caveat.
- **R3 — cache-key stability**: `GetMembersController.BuildCacheKey` hashes the
  `LoadOptions` JSON (`:164-171`). The lowering pass must be deterministic (stable operand
  order) so identical grid state always produces byte-identical JSON. Covered by engine
  tests.
- **R4 — or-chain SQL for big header-filter selections**: 50 selected values → 50 `==`
  parameters. Acceptable v1; revisit backend `anyof` (`IN`) if profiling says so.
- **R5 — double data copy**: `workingData = [...data()]` per data write is unchanged, but
  remote paging writes happen per page navigation. Page-sized arrays (≤ ~100 rows) make this
  negligible.

Open questions (product owner):
- **Q1**: When remote **filtering** is on but remote **paging** is off, should the grid warn?
  (The server returns the full filtered set and the client pages it — legitimate but easy to
  misconfigure into huge responses. Proposal: allow silently, document.)
- **Q2**: Blanks lowering for string columns — `= null` only (proposed) or
  `(= null or = '')`? Depends on whether tenant data uses empty strings.
- **Q3**: Header-filter distinct values under remote paging are page-scoped. Ship v1 with the
  documented degrade, or prioritize a follow-up `*-distinct` backend endpoint + grid hook?
- **Q4**: `'save'` re-emission — always reload after `saveEditData`, or make it opt-in
  (`remoteOperations.reloadOnSave`, default true)?
- **Q5**: Add an optional `errorText` input (grid-rendered error strip) in v1, or keep errors
  100% consumer-side (proposed)?
- **Q6**: Reason precedence when multiple dimensions change in one tick (proposed:
  filter > sort > page) — acceptable, or should the event carry a reason *set*?

## 13. Estimated scope

| Work item | Size |
|---|---|
| Engine: `lowerFilterExpressionForWire` + tests | S (~120 LOC + ~150 LOC tests) |
| Shell: flags, pipeline bypass, emission effect, reasons, dedupe, guards | M (~250–350 LOC across `fs-data-grid.component.ts`) |
| Pager: `serverTotalRows` input + derivations | S (~40 LOC) |
| Shell behavior tests | M (~300 LOC) |
| Gallery demo card (fake server, controls, recipe) | M (~200 LOC) |
| README §30 section + caveat boxes; remove v1-gap lines (`README.md:114`, `:153`) | S |
| Backend | none |

Total: roughly **2–3 focused sessions**; frontend-only, deployable independently of any
backend release (the wire contract already exists in production).
