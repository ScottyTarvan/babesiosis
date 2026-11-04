import { Injectable } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';
import { retry } from 'rxjs/operators';

/**
 * Retry policy for outbound requests. Nothing else — errors are reported by the screen
 * that made the request, never from here.
 *
 * This interceptor used to answer a 500 with a global toast in the topbar, and to
 * navigate to an `/error` page when the response carried a marker header. Both are gone:
 *
 *  - The toast duplicated what the originating screen already showed. `catchError` here
 *    rethrew, so the component's own handler ran too and the same sentence appeared twice,
 *    in two unrelated toast systems (this one, and `FsToastService` in the shell). It also
 *    fired for unattended background polling, which `BackgroundJobsService` explicitly does
 *    not want — see its `handlePollError` doc comment.
 *  - The `/error` navigation could never run. It tested for an `app-server-error-page`
 *    header that no endpoint sends (`HttpFunctionBase` echoes `fit-server-error-page`, and
 *    only when the request already carried it), and the `error` route is commented out in
 *    `app-routing.module.ts`.
 *
 * A failed request now surfaces exactly once, next to the thing that failed: an
 * `<fs-banner intent="danger">` on the page or dialog, or `FsToastService` for a
 * page-level action. See `core/http-error.ts` for the render rule and the message
 * extractor every screen uses.
 *
 * Retries are limited to GET and HEAD, the only methods safe to repeat: replaying a POST
 * that the server had already applied would double the write.
 */
@Injectable()
export class ServerErrorHttpInterceptor implements HttpInterceptor {

  intercept(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    const shouldRetry = req.method === 'GET' || req.method === 'HEAD';

    return next.handle(req).pipe(
      retry({ count: shouldRetry ? 2 : 0 }),
    );
  }

}
