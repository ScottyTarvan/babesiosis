import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpResponse,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { delay, map, switchMap } from 'rxjs/operators';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { mockRegistrations } from 'app/_mocks';
import { MockHandler } from 'app/_mocks/mock-handler';

const MOCK_LATENCY_MS = 150;

/**
 * MockApiHttpInterceptor — when `useMockApi` is true in assets/config.json,
 * intercept any request to `/api/core/<route>` and respond from the in-app
 * fixture registry.
 *
 * Unregistered routes return HTTP 501 with a console warning telling you
 * which file to create — letting you ramp up coverage incrementally.
 *
 * Must be registered as the FIRST HTTP_INTERCEPTORS provider so it short-
 * circuits before the auth-header / error-mapping interceptors run.
 */
@Injectable()
export class MockApiHttpInterceptor implements HttpInterceptor {
  private readonly handlers: Map<string, MockHandler>;

  constructor(private readonly configService: ConfigurationService) {
    this.handlers = new Map<string, MockHandler>(
      mockRegistrations.map(reg => [reg.route, reg.handler])
    );
  }

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // Read per request rather than cached in a field — the interceptor is
    // constructed by the config.json fetch itself, before load() has resolved.
    if (!this.configService.useMockApi) {
      return next.handle(req);
    }

    const route = this.extractRoute(req.url);
    if (!route) {
      return next.handle(req);
    }

    const handler = this.handlers.get(route);
    if (!handler) {
      console.warn(
        `[mock-api] No mock handler for "${route}". ` +
        `Create src/app/_mocks/handlers/${route}.mock.ts and register it in src/app/_mocks/index.ts. ` +
        `See src/app/_mocks/README.md for the full workflow.`
      );
      return throwError(() => new HttpErrorResponse({
        status: 501,
        statusText: 'Not Mocked',
        error: { message: `No mock handler registered for ${route}` },
        url: req.url
      }));
    }

    return of(null).pipe(
      delay(MOCK_LATENCY_MS),
      switchMap(() => {
        const result = handler(req.body, req as HttpRequest<unknown>);
        const stream$ = result instanceof Observable ? result : of(result);
        return stream$.pipe(
          map(body => new HttpResponse<unknown>({ status: 200, body, url: req.url }))
        );
      })
    );
  }

  private extractRoute(url: string): string | null {
    // Full path after the gateway prefix — routes may be nested
    // (e.g. member-projected-hours-get). The `core/` | `reports/` segment that
    // ConfigurationService.coreAPI()/reportsAPI() prepend is stripped so the
    // registry keys stay plain function names.
    const m = url.match(/\/api\/(?:core|reports)\/([^?#]+)/);
    return m ? m[1] : null;
  }
}
