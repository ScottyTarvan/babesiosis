import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, tap } from 'rxjs';
import {
  parseServerTiming,
  timingsEnabled,
} from 'app/core/diagnostics/request-timings';

/**
 * Logs how long each API call took, and — when the backend was started with
 * `DM_REQUEST_TIMINGS=1` — the server's own breakdown of that time.
 *
 * <p>The two numbers together are the point. `wall` is what the browser waited;
 * the server's `total` is what the function spent. The difference is network,
 * queueing and the worker's dispatch, which is the part no amount of backend
 * instrumentation can see and is exactly where a "slight delay" can hide.</p>
 *
 * <p>Off unless `localStorage['fs.timings'] === '1'` — see `request-timings.ts`.
 * When off, `intercept` returns the untouched stream and adds one boolean check
 * per request.</p>
 *
 * <p><b>Known gap: mock mode records nothing.</b> `MockApiHttpInterceptor` runs
 * ahead of this one and short-circuits every `/api/core/*` call without calling
 * `next.handle`, so those calls never reach here — verified by probe, and true
 * from EITHER end of the `HTTP_INTERCEPTORS` list, so it is not simply a
 * provider-order mistake. In mock mode only `assets/config.json` is recorded.
 * That costs nothing in practice: mock latency is a hard-coded 150ms constant,
 * so there is no real timing to lose, and against a real backend — the only
 * configuration where these numbers mean anything — no mock interceptor is in
 * the chain and every call is recorded.</p>
 *
 * <p>The manage-data edit cycle does not depend on this: its per-request phases
 * are measured in the component itself (`TimingRun`), which sits above the HTTP
 * layer and works in mock mode too.</p>
 */
@Injectable()
export class RequestTimingHttpInterceptor implements HttpInterceptor {

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (!timingsEnabled()) {
      return next.handle(req);
    }

    const startedAt = performance.now();

    return next.handle(req).pipe(
      tap(event => {
        if (!(event instanceof HttpResponse)) return;
        this.log(req, event, performance.now() - startedAt);
      }),
    );
  }

  private log(req: HttpRequest<unknown>, response: HttpResponse<unknown>, wallMs: number): void {
    // Only the last path segment: the endpoints are flat (`/api/core/manage-data-edit`)
    // and the prefix is the same on every line.
    const name = req.url.split('?')[0].split('/').filter(Boolean).pop() ?? req.url;
    const server = parseServerTiming(response.headers.get('Server-Timing'));

    console.groupCollapsed(
      `%c[http] ${name} — ${Math.round(wallMs)}ms wall`, 'color:#07a');

    if (server.length === 0) {
      // Either the backend flag is off, or — deployed — the gateway did not pass
      // the header through. Say which is being shown rather than imply the
      // server spent no time at all.
      console.log('No Server-Timing header (set DM_REQUEST_TIMINGS=1 on the Functions host).');
    } else {
      const rows: Record<string, { ms: number }> = {};
      server.forEach((phase, index) => {
        rows[`${index}. ${phase.label}`] = { ms: phase.durationMs };
      });
      console.table(rows);
    }

    console.groupEnd();
  }
}
