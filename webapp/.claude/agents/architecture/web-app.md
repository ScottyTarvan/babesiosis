# ANGULAR WEB APPLICATION

## Project Structure
- **Project Name**: DataManager.Web
- **Framework**: Angular 20, Bootstrap 5 + NgBootstrap, Iconify (Tabler), standalone
  signal-based components. The shared `fs-*` library is the `@fundstream-ai/gnome-ui` package (repository fundstream-ai/gnome-ui).
- **Architecture Pattern**: Components and Services
- **Data Transfer Objects**: Use classes (NOT interfaces) for DTOs/ViewModels in dedicated files

## Folder Organization
- Feature areas sit directly under `src/app/`: `manage/`, `auth/`, `settings/`, `support/`,
  `help/`. Cross-cutting folders: `core/`, `common/`, `core/`, `layout/`,
  `store/`, `helper/`, `_mocks/`. There is **no** `src/app/features/` folder.
- Organize by feature, with components, view models, commands, and services in the same
  feature folder; a nested folder is acceptable for a dialog or child component.
- Example structure (mirrors `src/app/manage/members/`):
  ```
  src/app/[area]/[feature-name]/
    ├── [feature].component.ts
    ├── [feature].component.html
    ├── [feature].component.scss
    ├── [feature].service.ts
    ├── [feature].viewmodel.ts
    ├── [feature].command.ts
    └── [feature]-form-dialog/
  ```

## Development Requirements

### Angular Components
- always create separate typescript, html templates and scss files
- do not create an inline component
- build UI from the shared `fs-*` components (`@fundstream-ai/gnome-ui`) — see the
  `fs-component` skill. All data grids use `<fs-data-table>`.

### Imports
- Always use the `tsconfig.json` path aliases (`app/*`, `@core`, `@core/services/*`,
  `@reports/*`, `@layouts/*`, etc.) — never a relative specifier (`./x`, `../x`), including
  same-folder imports. Enforced zero-tolerance by `npm run lint:imports`
  (`DataManager.Web/scripts/import-guard.mjs`). See `DataManager.Web/rules/absolute-imports.md`
  for the alias table. `templateUrl`/`styleUrl(s)` stay relative — they're loader paths, not
  TS module specifiers.

### View Models
- Create view models instead of interfaces
- View models in their own files

### Build Verification
- **CRITICAL**: After making changes, run `ng build` to check for compilation errors
- Fix all TypeScript errors and warnings before considering work complete
- Verify no breaking changes to existing functionality


