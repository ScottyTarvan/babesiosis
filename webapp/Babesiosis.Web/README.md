# Babesiosis Web

Angular 20 frontend for the Babesiosis time-tracking and billing linkedService, deployed to **Azure Static Web Apps**. This document covers installing, building, and deploying the app to both the **dev** and **prod** environments.

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Node.js | **22.x** | Matches CI. Angular 20 requires Node ≥ 20.19. |
| npm | 10+ | Ships with Node 22. |
| Azure SWA CLI | 2.x | Install once: `npm install -g @azure/static-web-apps-cli` |

You also need a **deployment token** for each Static Web App resource you deploy to (see [Deploy](#deploy)).

---

## Install

The shared `fs-*` components come from the private package **`@fundstream-ai/gnome-ui`** on
GitHub Packages (repository fundstream-ai/gnome-ui). The committed [`.npmrc`](.npmrc) routes the
`@fundstream-ai` scope there and reads the token from the **`NODE_AUTH_TOKEN`** environment
variable; no token is ever written to a file in this repository. Set it before any `npm install`
(npm fails with `E401` when it is unset, and the project `.npmrc` overrides a token in `~/.npmrc`):

```powershell
# GitHub CLI login with the read:packages scope (once: gh auth refresh -s read:packages)
$env:NODE_AUTH_TOKEN = gh auth token
# or a classic personal access token with read:packages (fine-grained tokens are not accepted)
$env:NODE_AUTH_TOKEN = '<classic PAT>'

cd Babesiosis.Web
npm install --legacy-peer-deps
```

```bash
export NODE_AUTH_TOKEN=$(gh auth token)
```

> `--legacy-peer-deps` is required — the dependency tree has peer conflicts that npm's strict resolver rejects (`@ng-bootstrap/ng-bootstrap` → `@angular/localize`). The gnome-ui package and its chart / rich-editor packages themselves need no flag or override.

The package version is pinned exactly in `package.json`. To upgrade, change the pin (published
versions: `gh api orgs/fundstream-ai/packages/npm/gnome-ui/versions --jq '.[].name'`), run
`npm install`, `npm run build`, `npm test`, and look at the screens in light and dark mode.

---

## Local development

```powershell
npm start
```

Runs `ng serve` on **http://127.0.0.1:4400/** with hot reload, using the `local` configuration.

`Babesiosis.Proxy.App` is **bypassed** — you only need the function hosts running: **`Babesiosis.Core.Functions` on `:6060`** and, if you touch reporting, **`Babesiosis.Reports.Functions` on `:7070`**. Alternatively set `useMockApi: true` (see [`src/app/_mocks`](src/app/_mocks/README.md)) and run no backend at all.

How it works — no application code is involved:

| Piece | Effect |
|---|---|
| [`public-local/assets/config.json`](public-local/assets/config.json) | Overlays the committed `config.json` (the `local` build config ignores the `public` copy). Sets `proxyBaseUrl: ""`, so `ConfigurationService` resolves **same-origin**. |
| [`proxy.conf.json`](proxy.conf.json) | The dev server forwards `/api/core/*` → `:6060/api/*` and `/api/reports/*` → `:7070/api/*`, matching the gateway's `PathRemovePrefix` transform. |

Because it is same-origin there is no CORS to configure, and the browser never holds a function key. What you lose versus the real gateway: the edge JWT check, deny-by-default routing, and privileged-header stripping. None of that is load-bearing locally — the functions re-validate the JWT and enforce `[RequiredPermission]` themselves, and the local Functions host does not enforce `AuthorizationLevel.Function` keys.

> **Local func hosts only.** Never repoint `proxy.conf.json` at a deployed function app — those require `x-functions-key`, which is exactly the secret the gateway exists to keep out of the browser.

> There is no separate "gateway" serve configuration. If you need to exercise `Babesiosis.Proxy.App` locally, point `public-local/assets/config.json`'s `proxyBaseUrl` at the running gateway's absolute URL — that file is git-tracked, so revert it before committing.

---

## Build

All builds output to **`dist/babesiosis-web/browser/`** (the folder that gets deployed).

| Command | Angular config | Optimized | Budgets enforced |
|---------|----------------|-----------|------------------|
| `npm run build` | `local` (default) | ❌ | ❌ |
| `npm start` | `local` (serve) | ❌ | ❌ |
| `npm run build:dev` | `development` | ❌ | ❌ |
| `npm run build:prod` | `production` | ✅ (hashed, minified) | ✅ |

**The build config no longer selects a backend** — the configs differ only in optimisation, source maps, hashing, and budgets. One artifact is built and promoted across environments, with the `#{token}#` placeholders in `assets/config.json` substituted at deploy time. `npm run build:prod` is therefore the right build for every environment.

> **Nothing substitutes the placeholders for a CLI deploy — you must do it by hand.**
> `ng build` copies `public/assets/config.json` into `dist/` verbatim, tokens intact, and
> `swa deploy` uploads it as-is. The deployed app then boots, `ConfigurationService` detects the
> unsubstituted token, logs an error and falls back to relative paths — which **bypasses the
> gateway**, so every API call hits the Static Web App itself and 404s. See
> [Full recipes](#full-recipes) for the build → substitute → deploy sequence.

---

## Deploy

Deployment uses the SWA CLI, driven by **`swa-cli.config.json`** in this folder. That file holds deployment tokens, so it is **git-ignored** — each developer maintains their own copy.

> **History note.** This file was *tracked* until 2026-09-14, so the `dev` and `prod` deployment
> tokens exist in git history. They grant push access to those Static Web Apps. Rotate them
> (portal → the SWA resource → _Manage deployment token_ → **Reset**), and treat any token
> committed before that date as compromised.

### One-time setup

Create `Babesiosis.Web/swa-cli.config.json` with an entry per environment:

```json
{
  "$schema": "https://aka.ms/azure/static-web-apps-cli/schema",
  "configurations": {
    "dev": {
      "appLocation": ".",
      "outputLocation": "dist/babesiosis-web/browser",
      "deploymentToken": "<DEV_SWA_DEPLOYMENT_TOKEN>"
    },
    "prod": {
      "appLocation": ".",
      "outputLocation": "dist/babesiosis-web/browser",
      "deploymentToken": "<PROD_SWA_DEPLOYMENT_TOKEN>"
    },
    "perpetua": {
      "appLocation": ".",
      "outputLocation": "dist/babesiosis-web/browser",
      "deploymentToken": "<PERPETUA_SWA_DEPLOYMENT_TOKEN>"
    }
  }
}
```

Get each token from the **Azure portal → the Static Web App resource → _Manage deployment token_**. The entries point at **separate SWA resources** (typically in separate resource groups); the token is what selects the resource.

### Deploy commands

| Command | Target | Runs |
|---------|--------|------|
| `npm run deploy:dev` | dev SWA resource | `npm run build:dev && swa deploy dev --env production` |
| `npm run deploy:prod` | prod SWA resource | `npm run build:prod && swa deploy prod --env production` |
| `npm run deploy:perpetua` | perpetua SWA resource | `npm run build:prod && swa deploy perpetua --env production` |

> `--env production` means "the live environment **of that resource**" — it does **not** cross resource groups. The config name (`dev` / `prod` / `perpetua`) is what selects the resource.

> ⚠️ **These one-shot scripts chain build *and* deploy**, leaving no window to substitute the
> `assets/config.json` placeholders. They ship a bundle that deploys successfully and is broken at
> runtime. Use the two-step recipe below instead; the scripts are only safe once something
> automates the substitution.

### Full recipes

Three steps, and the middle one is not optional.

**1. Build** (one artifact, same for every environment):
```powershell
npm run build:prod
```

**2. Substitute** the placeholders in `dist/babesiosis-web/browser/assets/config.json`:
```json
{
  "proxyBaseUrl": "https://<gateway-host>",
  "userDataKey": "authf649fc9a5f55",
  "allowEntraLogin": true,
  "allowEmailLogin": true,
  "client": "fundstream",
  "useMockApi": false
}
```
`proxyBaseUrl` is the `Babesiosis.Proxy.App` gateway for that environment — e.g.
`https://dm-perpetua-za-proxy-app.azurewebsites.net`. Set `allowEntraLogin` to `false` unless
that environment has the `AppSettings:Security:EntraId*` keys configured, or the login page shows
an Entra button that fails. Booleans may be real JSON booleans or the strings `"true"`/`"false"`.

**3. Deploy** without rebuilding — a rebuild overwrites your edits:
```powershell
npx swa deploy perpetua --env production
```

Substitute-then-deploy must happen in one sitting: `swa deploy` uploads whatever is currently in
`dist/babesiosis-web/browser/`, so an intervening build (or a stale `dist/`) ships the wrong
thing.

**Verify after deploying.** Open the site and check the browser console: if you see
`[config] proxyBaseUrl is an unsubstituted token`, step 2 didn't make it into the upload.

---

## Testing & linting

```powershell
npm test        # Karma/Jasmine unit tests (the fs-* component specs live in the gnome-ui repository)
npm run lint     # fs-guard (feature template discipline) + import-guard (no relative imports)
```

---

## Shared components, styles and icons

- **Imports.** Import `fs-*` components, types and helpers from the package entry points:
  `@fundstream-ai/gnome-ui`, `@fundstream-ai/gnome-ui/chart`, `@fundstream-ai/gnome-ui/rich-editor`,
  `@fundstream-ai/gnome-ui/layout-designer`. The `@core` barrel (`src/app/core/index.ts`)
  re-exports all four plus Babesiosis's own pipes and helpers. A component change is made in the
  gnome-ui repository and released; it reaches this app by bumping the pin.
- **Styles.** [`src/styles.scss`](src/styles.scss) loads the vendor layer (Bootstrap and the app
  theme), then `@use '@fundstream-ai/gnome-ui/styles/gnome-ui'` (design tokens, layout utilities,
  base reset, body typography, overlay stacking). The tokens are frozen and read-only in
  `node_modules`; never restyle a component's internal classes from the app.
- **Icons.** `provideGnomeUi({ icons: APP_ICONS })` in `app.module.ts` registers icons offline;
  nothing is fetched from `api.iconify.design`. The library bundles the Tabler icons its own
  components use; [`src/app/app-icons.ts`](src/app/app-icons.ts) is the generated subset of the
  Tabler icons Babesiosis's own screens use. After using an icon name that is not yet in it (a
  dev-mode console warning `fs-symbol: icon 'tabler:x' is not registered` says so), regenerate it
  from a gnome-ui checkout (its dev dependencies include `@iconify-json/tabler`):

  ```powershell
  cd C:\Workspaces\gnome-ui
  node scripts/icons.mjs --app ../Babesiosis/webapp/Babesiosis.Web/src --out ../Babesiosis/webapp/Babesiosis.Web/src/app/app-icons.ts
  ```

---

## Reference

- **Routing/SPA config:** [`public/staticwebapp.config.json`](public/staticwebapp.config.json) — navigation fallback and asset excludes. This file **is** committed (it ships with the app). Each `exclude` route may contain **at most one `*` wildcard**, or Azure rejects the deploy.
- **Runtime config:** [`public/assets/config.json`](public/assets/config.json), fetched at bootstrap by `src/app/core/services/configuration.service.ts` via `provideAppInitializer`. Holds `proxyBaseUrl`, `client`, `userDataKey`, the `allowEntraLogin`/`allowEmailLogin` flags, and `useMockApi`. **No secrets** — the backend function key never reaches the browser; `Babesiosis.Proxy.App` injects `x-functions-key` server-side. There are no `src/environments/*` files.
- **Style budgets:** `angular.json` → production `budgets` → `anyComponentStyle` caps per-component CSS (currently **20 kB warn / 32 kB error**), alongside an `initial` bundle budget of 2.75 MB warn / 4 MB error.

---

## Troubleshooting

| Symptom | Cause & fix |
|---------|-------------|
| `Could not find StaticSitesClient local binary` | First-run download of the deploy helper failed (network, or antivirus locking the fresh `.exe`). Just re-run the deploy. If it persists, delete `%USERPROFILE%\.swa` to force a clean re-download, and add a Defender exclusion for that folder. |
| `Deployment failed with exit code 1` / "install native dependencies / run ldd" | Generic fallback masking the real error. Re-run with `-- --verbose silly` to see it. Most common: an invalid `staticwebapp.config.json` (e.g. an `exclude` pattern with **two** `*` wildcards). |
| `... exceeded maximum budget` on build | A component's compiled CSS exceeds the `anyComponentStyle` budget in `angular.json`. Either trim the SCSS or raise the budget. |
| `swa deploy` picks the wrong/no config | With multiple configs you **must** name one: `swa deploy dev` / `swa deploy prod`. Bare `swa deploy` only auto-selects when there is a single configuration. |
| `Could not find the '@angular-devkit/build-angular:application' builder's node package` | `node_modules` is missing or incomplete — run `npm install --legacy-peer-deps`. Note `npm start` chains its own install and so hides this, but `build:*` and `deploy:*` do not. In a `deploy:*` script the build fails first and the `&&` short-circuits, so **nothing is deployed** despite the command looking like a deploy failure. |
| Deployed site loads but every API call 404s | `assets/config.json` shipped with unsubstituted `#{...}#` placeholders — step 2 of the deploy recipe was skipped. The browser console shows `[config] proxyBaseUrl is an unsubstituted token`. |
| Browser reports a CORS error against the gateway | First check the gateway is actually **up** (`curl -i https://<gateway-host>/health`). A crashed App Service returns an error page with no `Access-Control-Allow-Origin`, which the browser reports as a CORS failure. Only if it is up and still missing the header is this genuinely `AppSettings:Proxy:AllowedOrigins`. |

---

## CI/CD PIPELINES

Deployment is manual via the SWA CLI, per the [Deploy](#deploy) section. The Azure Pipelines
definition [`../Babesiosis.Pipelines/angular-pipeline.yaml`](../Babesiosis.Pipelines/angular-pipeline.yaml)
builds this app; its `npm install` step reads `NODE_AUTH_TOKEN` from the secret pipeline variable
**`GITHUB_PACKAGES_TOKEN`** (a classic PAT with `read:packages` on the fundstream-ai organisation).
Set that secret in the pipeline's variables before the next run, or the install fails with `E401`.

When a pipeline is reintroduced, the thing it most needs to own is **token substitution in
`assets/config.json`** (the `#{proxy-base-url}#` family). That is the one step of the deploy that
is currently manual and silently ships a broken site when forgotten.
