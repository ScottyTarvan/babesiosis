# `<fs-data-grid>` — cell editing mode + editor-chrome display option

Status: SPEC (no implementation). Scope: `src/app/shared/components/fs-data-grid/`.
Behavioural contract references (§n) follow `Babesiosis.Agents.Docs/Specs/data-grid-feature-spec.md`,
the same numbering the grid README uses. This document is vendor-name-free by repo
convention — the comparison grid is called "the reference grid" throughout.

---

## 1. Summary & goals

Two asks:

1. **Full in-cell editing** (`editing.mode: 'cell'`): click a cell → it becomes its
   type-specific editor; the edit commits on blur / Enter / navigation to another
   cell; each committed cell edit saves immediately (per-cell validation, per-cell
   repaint). **Finding: this is already fully implemented and gallery-demoed** —
   see §3. The deliverable for this half is *verification + documentation*, not new
   code.
2. **Editor-chrome display option** (new): the reference grid renders in-cell
   editors *without* the full input outline — the edited cell shows only an
   underline. Add a configuration switch choosing between:
   - `'outlined'` — today's look: the standard `fs-*` control chrome (1px full
     border, radius, focus ring). Remains the default.
   - `'underlined'` — borderless editor: transparent background, no radius, no
     focus ring; a bottom underline is the only chrome (accent-coloured while
     focused). The cell content should appear to stay "in place" while becoming
     editable.

Non-goals: no change to commit semantics, validation, the change-set engine, the
filter row, or the generated edit form/popup (those keep outlined chrome); no new
npm dependencies; no visual change for any existing consumer that does not opt in.

## 2. Reference behavior

From the reference grid's cell-editing demo and its documented semantics:

- `editing.mode: 'cell'` — clicking a cell (with updating allowed) swaps the cell
  content for the column's type-specific editor (text, number, date, checkbox,
  lookup dropdown).
- Commit model: "changes save immediately after focus leaves the cell" — blur,
  Enter, Tab, or clicking another cell all commit; Escape discards the open
  cell's draft. There is no Save/Cancel button pair in cell mode (unlike batch).
- Validation runs per cell at commit; an invalid value keeps the editor open with
  the error shown, blocking the commit.
- Repaint is per cell — the rest of the grid does not re-enter edit state.
- **Editor chrome**: in the reference theme, the in-cell editor is *borderless* —
  no outlined input box inside the cell. The editing cell is indicated by an
  underline at the bottom edge of the cell (accent-coloured while the editor is
  focused), and the editor text sits exactly where the display text sat. The
  checkbox editor for boolean cells renders as a bare checkbox (no field box) in
  both styles.

## 3. Current state (evidence)

### 3.1 `'cell'` mode is fully implemented

Types (contract):

- `FsGridEditingMode = 'row' | 'cell' | 'batch' | 'form' | 'popup'` —
  `fs-data-grid.types.ts:174`; `FsGridEditing.mode` default `'row'`
  (`fs-data-grid.types.ts:213-237`).

Shell (`fs-data-grid.component.ts`) — the cell/batch state machine (§5.2):

- `modeUsesCellEditing` computed: `mode === 'cell' || mode === 'batch'` — lines
  2984–2987.
- Pointer entry `maybeStartEditFromPointer` (honours
  `editing.startEditAction: 'click' | 'dblClick'`) — lines 3272–3286, wired from
  `onCellClicked`/`onCellDblClicked` at 2901/2910; sets
  `suppressNextRowClickForEdit` so the bubbling row click skips selection.
- `startCellEdit` — lines 3295–3326: commits any open editor first (moving to
  another cell commits the previous one, line 3309), **cell mode persists other
  rows' pending changes when focus leaves a row** (lines 3311–3314, the §5.2
  new-row focus-leaves-row rule), fires cancellable `editingStart` with `column`,
  then `setEditState(row.key, col.id)`.
- `commitCellEdit(saveAfter)` — lines 3336–3361: validates modified fields only
  (§5.4; invalid keeps the editor open with the error, lines 3352–3355), stages
  via `upsertChange`, closes the editor, and **cell mode saves existing rows
  immediately** (`saveAfter = mode === 'cell'`, line 3359; pending inserts stage
  only).
- Editor events: `onCellEditorCommit` (Enter/blur → commit, cell mode saves) —
  lines 3370–3382; `onCellEditorCancel` (Esc → `discardCellEdit`, lines
  3364–3367, 3384–3388); `armEnterMove`/`moveEnterFocus` (§19.1
  `enterKeyDirection` post-commit focus move) — lines 3394–3411.
- Keyboard entry `tryStartEditFromKeyboard` (Enter/F2/`editOnKeyPress` printable
  seeds) routes to `startCellEdit` in cell mode — lines 4873–4906.
- API: `editCell()` warns unless mode is `'cell' | 'batch'` then starts the edit
  (lines 6660–6669); `closeEditCell()` (6966–6977); `addRow()` commits the open
  cell editor on entry (6593–6598); `cellValue(...)` stages through the same
  buffer (6724).
- Escape at grid level discards the cell edit (`handleEscapeKey` branch, 4586).

Editor sub-component (`fs-data-grid-cell-editor.component.ts`):

- Type→primitive mapping (text/number/boolean/date/lookup) — `editorKind`
  computed, lines 107–120; template `fs-data-grid-cell-editor.component.html`
  mounts `fs-select` / `fs-checkbox` / `fs-date-picker` / `fs-text-input`.
- `commitRequested` on Enter and on focus leaving the editor entirely
  (`onKeydown`/`onFocusOut`, lines 197–211); `cancelRequested` on Escape;
  `enterPressed` emitted before the commit so the shell can distinguish
  Enter-commit from blur-commit; `autoFocus` + `selectTextOnFocus` (constructor,
  lines 149–164).

Shell template mounts (`fs-data-grid.component.html`): the in-cell editor at
lines 510–524 (`[autoFocus]="true"`, `size="sm"`, commit/cancel/enter wired) and
the `showEditorAlways` editor at 528–537. `editCellTemplate` outlet at 507–508.

Gallery: the "Data types & formats" demo runs `editing: { mode: 'cell',
allowUpdating: true }` — `gallery.component.ts:2824-2827`, bound at
`gallery.component.html:1804-1811` ("`mode: 'cell'` editing swaps any cell to its
type-specific editor on click"). Behaviour specs exercise cell mode end-to-end
(`fs-data-grid.behavior.spec.ts:62-92` save-pipeline suite runs under
`mode: 'cell'`).

README §5 coverage: "Editing internals (S5)" documents the whole machine,
including the documented §5.2 nuance that a pending *new-row insert* persists on
next-row edit rather than on grid blur (README "Documented v1 gaps", editing
bullet: "Cell mode §5.2 … implemented as save-on-next-edit").

### 3.2 Editor chrome today: always outlined

Every generated editor renders the full `fs-*` control chrome:

- `fs-text-input.component.scss:16-67` — 1px `--fs-color-border` border,
  `--fs-radius-md`, focus = primary border + 3px `box-shadow` ring.
- `fs-select.component.scss:9-48` — same box chrome + chevron.
- `fs-date-picker.component.scss:7-27` — same chrome on the field wrapper
  (`:focus-within` ring).
- `fs-checkbox` — no field box (already matches the reference in both styles).

The grid only trims cell padding while an editor is open
(`.fs-data-grid__cell--editor`, `fs-data-grid.component.scss:821-824`). There is
no option anywhere to suppress the editor outline. None of the primitives has a
chrome/variant input today (`fs-text-input.component.ts:41-56` — `type`, `size`,
`invalid`, etc. only).

## 4. Gap analysis

| Requirement | Status |
|---|---|
| Cell mode: click-to-edit, type-specific editors | Done (evidence §3.1) |
| Commit on blur / Enter / navigation; immediate save per cell | Done |
| Per-cell validation blocking commit | Done |
| Esc discards; keyboard entry (Enter/F2/editOnKeyPress) | Done |
| Gallery demo of cell mode | Done ("Data types & formats") |
| Editor-chrome option (`outlined` vs `underlined`) | **Missing — the whole delta** |
| Underline styling across all editor kinds (text/number/date/select; checkbox exempt) | Missing |
| README §5 + gallery coverage of the new option | Missing |

The feature is therefore a *presentation-layer* addition: one new config key, one
new input threaded through the editor component into the primitives, SCSS in each
primitive, and demo/docs/tests. The editing engine is untouched.

## 5. Proposed API

### 5.1 Types (`fs-data-grid.types.ts`)

```ts
/** §5.2 — visual chrome of generated in-cell editors. */
export type FsGridEditorStyle = 'outlined' | 'underlined';

export interface FsGridEditing<T = unknown> {
  // … existing members unchanged …
  /**
   * Chrome of the generated editors rendered INSIDE data cells (cell/batch/row
   * inline editors and `showEditorAlways` editors). 'outlined' (default) keeps
   * the standard control look; 'underlined' renders a borderless editor whose
   * only chrome is a bottom underline (accent while focused) — the reference
   * grid's in-cell look. The filter row and the generated edit form/popup are
   * NOT affected. Boolean checkbox editors render identically in both styles.
   */
  editorStyle?: FsGridEditorStyle;
}
```

Naming decision: `editorStyle` on the `editing` config object (not a standalone
grid input) — it only has meaning while editing renders editors, and it keeps the
one-config-object-per-spec-area pattern (README "State ownership"). Default
`'outlined'` = zero visual change for existing consumers.

Rejected alternatives: `editorChrome` (reads as markup, not style);
a per-column override (deferred — see open questions); a grid-level `display`
config (no such config area exists; would be a new surface for one key).

### 5.2 Primitive inputs (shared components — additive, non-breaking)

Each boxed editor primitive gains one optional input, defaulting to today's look:

```ts
// fs-text-input.component.ts, fs-select.component.ts, fs-date-picker.component.ts
readonly chrome = input<'outlined' | 'underlined'>('outlined');
```

`chrome === 'underlined'` adds a modifier class inside the primitive's own
stylesheet (`fs-text-input--underlined`, `fs-select--underlined`,
`fs-date-picker--underlined`). Styling lives *in the primitive* because emulated
view encapsulation prevents the grid from restyling the inner control without
`::ng-deep` (deliberately avoided). `fs-checkbox` is untouched.

The input name is `chrome` at primitive level (a primitive has no "editor";
`variant` is left free for future tonal variants). Other consumers (forms,
filter row, topbar) never pass it → no visual change anywhere.

### 5.3 README §5 wording (to append to the S5 editing internals / v1-gaps area)

> `editing.editorStyle` (§5.2, default `'outlined'`): `'underlined'` renders the
> in-cell editors (cell/batch/row inline + `showEditorAlways`) without the boxed
> control chrome — transparent background, no border/radius/focus-ring, a 1px
> bottom underline that thickens to 2px accent while the editor has focus. Applies
> only to editors mounted inside data cells: the filter row, the generated §8
> edit form and the popup form always render outlined editors. The boolean
> checkbox editor is chrome-free in both styles. The underline is drawn by the
> editor primitives themselves (`chrome` input on `fs-text-input`, `fs-select`,
> `fs-date-picker`); the shell only forwards the configured style.

## 6. Engine changes (`engine/editing.ts`)

**None.** The editing engine is a pure change-set/validation model
(`engine/editing.ts:12-19` — "the shell owns the `changes` signal"); editor
chrome is presentation-only and never reaches the engine. `editing.spec.ts` is
untouched. (This is a deliberate statement, not an omission — reviewers should
reject any implementation that threads a style flag into the engine.)

## 7. Component changes

### 7.1 Shell (`fs-data-grid.component.ts` / `.html`)

- New protected computed:
  `editorChromeStyle = computed(() => this.editingCfg().editorStyle ?? 'outlined')`
  (`editingCfg` already normalises the editing config).
- Template: forward `[chrome]="editorChromeStyle()"` at both cell-editor mount
  sites — the in-cell editor (`fs-data-grid.component.html:510`) and the
  `showEditorAlways` editor (`:528`). The `editCellTemplate` outlet (507) is a
  consumer-owned escape hatch and receives nothing (documented).
- Cell modifier: stamp `fs-data-grid__cell--editor-underlined` alongside the
  existing `__cell--editor` class when the style is underlined, so the grid can
  keep the editing cell's padding *identical to a display cell* (the underline
  look reads as "the text became editable in place"; the outlined style keeps
  its existing reduced padding, `fs-data-grid.component.scss:821-824`).
- The generated edit form (`fs-data-grid-edit-form.component.html:62` mounts the
  same editor component) does NOT receive the input — its default `'outlined'`
  keeps form/popup mode unchanged. Likewise the filter row.

### 7.2 Editor component (`fs-data-grid-cell-editor.component.ts` / `.html`)

- New input `chrome = input<'outlined' | 'underlined'>('outlined')`, forwarded to
  the `fs-select`, `fs-date-picker` and both `fs-text-input` branches of the
  template. The `fs-checkbox` branch ignores it.
- Host/root class `fs-data-grid-cell-editor--underlined` for the error-text and
  layout tweaks local to the editor wrapper (e.g. error text alignment when the
  cell padding differs).

### 7.3 Primitive SCSS (the underline chrome — one block per primitive)

All values are tokens from the `@fundstream-ai/gnome-ui` package (`styles/tokens.scss`); both themes work
automatically. Shared recipe (adapted per primitive):

```scss
// fs-text-input.component.scss (mirror in fs-select / fs-date-picker)
.fs-text-input--underlined {
  background-color: transparent;
  border-color: transparent;            // keep the 1px border for geometry —
  border-radius: 0;                     // no layout shift vs the outlined box
  border-bottom-color: rgb(var(--fs-color-border));

  &:hover:not(:disabled, [readonly]) {
    border-color: transparent;
    border-bottom-color: rgb(var(--fs-color-muted));
  }

  &:focus,
  &:focus-visible {
    box-shadow: inset 0 -1px 0 rgb(var(--fs-color-primary)); // 2px visual underline
    border-color: transparent;
    border-bottom-color: rgb(var(--fs-color-primary));
  }

  &.fs-text-input--invalid {
    border-bottom-color: rgb(var(--fs-color-danger));
    &:focus, &:focus-visible {
      box-shadow: inset 0 -1px 0 rgb(var(--fs-color-danger));
    }
  }
}
```

Per-primitive notes:

- `fs-select--underlined`: same recipe on the `<select>`; the chevron is
  unchanged. Focus state uses `:focus`/`:focus-visible` as today
  (`fs-select.component.scss:43-48`).
- `fs-date-picker--underlined`: recipe applies to the `.fs-date-picker` wrapper
  (the chrome owner); focus state is `:focus-within` / `--open`
  (`fs-date-picker.component.scss:23-27`); the calendar popup is untouched.
- Disabled/readonly states keep their existing muted background treatments but
  with the transparent side/top borders.
- Grid-side `.fs-data-grid__cell--editor-underlined`: padding stays the display
  cell's padding (overriding the reduced `--editor` padding) and the editor's
  horizontal padding is zeroed to align the editor text with the display text
  (editor left padding 12px/8px vs cell padding — the alignment offset must be
  neutralised here, not in the primitives, since only the grid knows its cell
  metrics).
- The `__cell--invalid` inset danger ring (`fs-data-grid.component.scss:862-864`)
  continues to apply in both styles — the underline turning danger is additive.

## 8. Keyboard & accessibility spec

All existing behaviour is preserved; the chrome option must not change any of it.
Normative summary (current implementation cited in §3.1):

- **Enter an edit**: pointer per `startEditAction` (default click); keyboard
  Enter or F2 on the focused cell; any printable character when
  `keyboardNavigation.editOnKeyPress` is true (character seeds the draft). The
  editor autofocuses; `selectTextOnEditStart` selects the text.
- **Enter** (in the editor): commits the cell. With
  `keyboardNavigation.enterKeyDirection: 'column' | 'row'`, focus then moves to
  the next cell in that direction (Shift+Enter reverses); with `'none'` focus
  returns to the (now display) cell. Cell mode saves the committed change
  immediately; validation failure keeps the editor open with the error.
- **Escape**: discards the open cell's draft, closes the editor, returns focus
  to the cell (roving tabindex unchanged). Grid-level Escape does the same when
  the editor's own handler didn't catch it.
- **Tab / focus-out**: focus leaving the editor entirely commits it (editor
  `focusout` → `commitRequested`); focus moves per natural tab order. Clicking
  another editable cell commits the current editor first, then opens the new one.
- **Arrow keys inside a text editor** move the caret (they do not leave the
  cell); grid arrow navigation resumes once the editor closes.
- **Focus retention**: after commit-and-close, cell focus (`focusedCell` signal)
  remains on the edited cell unless an Enter move was armed; `focusedCellChanged`
  fires only when the cell actually changes.
- **ARIA**: editors carry `aria-label="Edit {column caption}"`
  (`fs-data-grid.component.html:518/536`); the validation message renders with
  `role="alert"` (`fs-data-grid-cell-editor.component.html:53-55`); invalid state
  is conveyed by the primitives' `invalid` input plus the message, and must ALSO
  remain non-colour-dependent (message text) in underlined style.
- **Underlined-style requirement (new)**: the focused editor must keep a visible
  focus indicator with ≥3:1 non-text contrast (WCAG 1.4.11) — the 2px accent
  underline satisfies this; the resting 1px border-token underline distinguishes
  "editable now" from plain display cells. No information may be conveyed by the
  ring's absence alone: the caret + underline + (for select/date) chevron/icon
  remain visible.

## 9. Gallery demo plan

Extend the existing `fs-data-grid` gallery page (slug unchanged, one
registration):

1. **"Data types & formats" demo** (`gallery.component.ts:2788-2827`): add a
   small `fs-select`/segmented toggle above the grid — "Editor chrome:
   outlined | underlined" — backed by a signal;
   `gridTypesEditing` becomes a computed deriving
   `{ mode: 'cell', allowUpdating: true, editorStyle: chrome() }`. This
   exercises every editor kind (string, lookup, number, date, nullable date,
   datetime, boolean) under both styles in one place.
2. **Demo note copy**: extend the existing paragraph
   (`gallery.component.html:1795-1803`) with one sentence describing
   `editorStyle: 'underlined'` as the borderless in-cell look of the reference
   grid.
3. No new panel; the editing-modes duo (row vs popup) stays outlined,
   implicitly demonstrating the option's scoping.

## 10. Test plan

Unit specs (Karma; CHROME_BIN → Edge per project setup):

- **Primitive specs** (`fs-text-input`, `fs-select`, `fs-date-picker`):
  - default `chrome` renders without the `--underlined` class (regression
    guard for every existing consumer);
  - `chrome="underlined"` stamps the modifier class on the chrome-owning
    element (input / select / wrapper respectively);
  - invalid + underlined coexist (both classes present).
- **`fs-data-grid-cell-editor` spec** (new or extended):
  - `chrome` forwards to text, number, select and date branches;
  - checkbox branch renders identically for both values;
  - existing commit/cancel/enter event behaviour unchanged with
    `chrome="underlined"` (events are chrome-independent).
- **Shell behaviour spec** (`fs-data-grid.behavior.spec.ts` additions):
  - `editing.editorStyle` omitted → in-cell editor renders outlined (no
    modifier class in the fixture DOM);
  - `editorStyle: 'underlined'` + `mode: 'cell'` → opening an editor stamps
    `fs-data-grid__cell--editor-underlined` on the `<td>` and the primitive
    carries its `--underlined` class;
  - the filter row's editors do NOT pick up the underlined class while
    `editorStyle: 'underlined'` (scoping guard);
  - form mode (`mode: 'form'`) editors stay outlined under
    `editorStyle: 'underlined'` (scoping guard);
  - `showEditorAlways` editor honours the style.
- **No engine spec changes** (`engine/editing.spec.ts` untouched — §6).
- Existing cell-mode behaviour suites (save-pipeline concurrency etc.) must pass
  unmodified — they are the proof that chrome stayed presentation-only.

Manual/visual: gallery toggle in both app themes (tokens-only styling should make
dark mode automatic); keyboard walk per §8.

## 11. Risks & open questions

Risks:

- **Text alignment shift** on edit-start in underlined style: the primitives pad
  horizontally (12px/8px) while grid cells pad differently. Mitigated by the
  grid-side `--editor-underlined` padding neutralisation (§7.3); needs a visual
  check per editor kind (select's chevron reserves right padding; date picker
  has a trailing trigger button).
- **Primitive input creep**: `chrome` must stay a two-value presentation switch;
  anything richer belongs in a future variant system.
- **`editCellTemplate` consumers** provide their own editors and will not follow
  `editorStyle` — documented, not solved.
- **Concurrent work**: `src/app/time-tracking/reports` is being edited in another
  session — this feature touches nothing under that path (and must not).

Open questions (product owner):

1. **Scope of the underline**: apply to row-mode inline editors and
   `showEditorAlways` editors too (proposed: yes — "editors inside data cells"),
   or strictly `mode: 'cell' | 'batch'`?
2. **Filter row**: keep it outlined always (proposed), or should
   `editorStyle: 'underlined'` also restyle filter-row editors for visual
   consistency?
3. **Resting underline**: show the 1px underline from the moment the editor
   opens (proposed — it marks the editable cell even before focus settles), or
   only the focused 2px accent underline with no resting chrome at all?
4. **Per-column override** (`column.editorStyle`)? Proposed: not in v1; the
   grid-level option covers the reference behaviour.
5. **Naming sign-off**: `editing.editorStyle: 'outlined' | 'underlined'` and the
   primitive-level input name `chrome`.

## 12. Estimated scope

| File | Change | Size |
|---|---|---|
| `fs-data-grid.types.ts` | `FsGridEditorStyle` + `FsGridEditing.editorStyle` | ~10 lines |
| `fs-data-grid.component.ts` | `editorChromeStyle` computed | ~5 lines |
| `fs-data-grid.component.html` | forward `[chrome]` (2 sites) + cell class | ~6 lines |
| `fs-data-grid.component.scss` | `__cell--editor-underlined` padding rules | ~15 lines |
| `fs-data-grid-cell-editor.component.ts/.html` | `chrome` input + forwarding | ~12 lines |
| `fs-text-input.component.ts/.scss` | `chrome` input + `--underlined` block | ~30 lines |
| `fs-select.component.ts/.scss` | same | ~30 lines |
| `fs-date-picker.component.ts/.scss` | same (wrapper-level) | ~30 lines |
| `fs-data-grid/README.md` | §5 wording (§5.3 above) | ~10 lines |
| `gallery.component.ts/.html` | chrome toggle on the types demo | ~25 lines |
| Specs (3 primitives + cell-editor + behaviour) | per §10 | ~150 lines |

Engine: 0 files. New components: 0. New dependencies: 0. Total ≈ 11 source files
plus specs; a half-day implementation with the visual-alignment check being the
only genuinely fiddly part.
