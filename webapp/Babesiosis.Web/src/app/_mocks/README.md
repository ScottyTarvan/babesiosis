# In-app API mocks

A frontend-only mock layer that lets the UI run without the .NET backend or SQL Server. Switch on/off with one flag — no backend code paths change.

## Toggle

`public-local/assets/config.json` — runtime config, so this is a page reload rather than a rebuild:

```json
"useMockApi": true    // mocks
"useMockApi": false   // real backend
```

Edit `public-local`, not `public`. The `local` build configuration overlays `public-local`
on top of `public`, so locally the overlay is the file actually served and changes to
`public/assets/config.json` have no effect.

Both ship as `false`, and the release pipeline does not substitute this key, so deployed
builds never use mocks.

## How it works

`MockApiHttpInterceptor` is registered first in the HTTP interceptor chain ([app.module.ts](../app.module.ts)). When `useMockApi` is true and the request URL matches `/api/core/<route>` (or `/api/reports/<route>`):

1. Looks up `<route>` in the registry in [`./index.ts`](./index.ts).
2. If found, runs the handler and returns its value as an HTTP 200 response (~150ms simulated latency).
3. If not found, returns HTTP 501 and logs a console warning naming the file you need to create.

If `useMockApi` is false the interceptor is a no-op — every request goes to the real backend.

## Adding a new endpoint mock

When you hit a screen that fails with `[mock-api] No mock handler for "foo-bar"`:

1. Find the real backend contract:
   - **Request shape** — the `*Command` class in `Babesiosis.Core.API/**/Commands/`.
   - **Response shape** — the `*ViewModel` class returned by the controller's `HandleCommand` method in `Babesiosis.Core.API/**/Controllers/`.
   - C# PascalCase serializes to camelCase on the wire.
2. Find the TypeScript mirrors in `src/app/.../commands/` and `src/app/.../viewmodels/` (the frontend already has them — use those types for compile-time safety).
3. Create `src/app/_mocks/handlers/foo-bar.mock.ts`:

```ts
import { FooBarCommand } from '@feature/commands/foo-bar.command';
import { FooBarViewModel } from '@feature/viewmodels/foo-bar.viewmodel';
import { MockRegistration } from '../mock-handler';

export const fooBarMock: MockRegistration<FooBarCommand, FooBarViewModel> = {
  route: 'foo-bar',
  handler: (body) => ({
    // ...realistic data shaped exactly like FooBarViewModel
  } as FooBarViewModel)
};
```

4. Register it in `./index.ts`:

```ts
import { fooBarMock } from './handlers/foo-bar.mock';

export const mockRegistrations: MockRegistration[] = [
  authLoginMock,
  fooBarMock,
];
```

5. Save — Angular hot-reloads. Refresh the screen.

## Common patterns

**Echo back input:**
```ts
handler: (body) => ({ ...body, id: 'mock-id', createdDate: new Date() })
```

**Return a list with variable size for empty-state / many-rows UI testing:**
```ts
handler: () => Array.from({ length: 25 }, (_, i) => ({ id: `${i}`, name: `Item ${i}` }))
```

**Simulate a 500 error:**
```ts
import { throwError } from 'rxjs';
import { HttpErrorResponse } from '@angular/common/http';

handler: () => throwError(() => new HttpErrorResponse({
  status: 500, error: { message: 'Simulated failure' }
}))
```

**Latency override (per handler):** wrap the return in `of(value).pipe(delay(3000))`.

## When you switch back to the real backend

1. Flip `useMockApi: false` in `public-local/assets/config.json` and reload.
2. Start the backends. Locally the gateway is bypassed, so you do **not** need to run
   `Babesiosis.Proxy.App` — `public-local` sets `proxyBaseUrl: ""`, which keeps API paths
   relative so [proxy.conf.json](../../../proxy.conf.json) routes them straight through:
   - `/api/core` → Functions host on **6060** (`Babesiosis.Core.Functions`)
   - `/api/reports` → Reports host on **7070**
3. No other changes needed — the mock files stay in source and reactivate the next time you set the flag true.

Deployed builds are the opposite: they ship `public/assets/config.json`, whose
`#{proxy-base-url}#` token the release pipeline replaces with the gateway's absolute URL,
so every call goes through `Babesiosis.Proxy.App` (which injects `x-functions-key`
server-side). See [configuration.service.ts](../core/services/configuration.service.ts).
