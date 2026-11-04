# Absolute imports only

Every TS import/export/dynamic-import specifier in `src/app/**/*.ts` must use a
`tsconfig.json` path alias — never a relative specifier (`./x`, `../x`).

Enforced by `scripts/import-guard.mjs` (`npm run lint:imports`, folded into `npm run lint`).
Zero-tolerance, no baseline: unlike `fs-guard.mjs`, this has no grandfathered violations —
the codebase was swept clean in one pass, so any relative import found is new.

## Why

- One way to reach a file, regardless of how deep the importing file sits. Moving a file
  no longer breaks every `../../../` import into it.
- The aliases already exist for this — the guard adds no new tsconfig surface, it just
  stops relative paths from creeping back in.

## Which alias to use

Pick the most specific alias whose target directory contains the file, per the `paths` map
in `tsconfig.json`:

| Alias | Target |
|---|---|
| `@core` | `src/app/core/index.ts` (the barrel — only when importing exactly that file) |
| `@core/commands/*` | `src/app/core/commands/*` |
| `@core/guards/*` | `src/app/core/guards/*` |
| `@core/services/*` | `src/app/core/services/*` |
| `@core/viewmodels/*` | `src/app/core/viewmodels/*` |
| `@layouts/*` | `src/app/layout/*` |
| `@auth/*` | `src/app/modules/auth/*` |
| `@settings/*` | `src/app/modules/settings/*` |
| `@reports/*` | `src/app/modules/reports/*` |
| `@roles/*` | `src/app/modules/data/manage/roles/*` |
| `@users/*` | `src/app/teams/users/*` |
| `@employees/*` | `src/app/teams/employees/*` |
| `@component/*` | `src/app/components/*` |
| `app/*` | `src/app/*` (catch-all — anything not covered above) |

If a new area of the app gets its own alias later, add it to `tsconfig.json` `paths` first,
then use it here — don't invent an alias the compiler doesn't know about.

## What this does NOT cover

Template/style loader paths (`templateUrl`, `styleUrl(s)` in `@Component` decorators) are
file-loader references, not TS module specifiers — they stay relative (`./foo.html`,
`./foo.scss`) and the guard does not touch them.

## History

Swept 2026-09-20: 377 files / 1346 relative specifiers converted in one pass (codemod over
the TypeScript AST, mapping each resolved target to its most-specific alias). Verified with
`npx tsc --noEmit -p tsconfig.app.json` and `-p tsconfig.spec.json` (both clean).
