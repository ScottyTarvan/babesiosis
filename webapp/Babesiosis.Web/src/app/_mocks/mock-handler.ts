import { HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';

/**
 * MockHandler — a function that produces a fake response for a single
 * backend route. Faithfully mirror the C# ViewModel returned by the real
 * controller (field names + types + optionality). When the user later
 * points at the real backend, behavior must be identical.
 *
 * Return shape:
 *  - Return a plain value -> wrapped in HTTP 200 with that value as body.
 *  - Return an Observable -> the emitted value is wrapped in HTTP 200.
 *  - To simulate an error, return `throwError(() => new HttpErrorResponse({...}))`.
 */
export type MockHandler<TReq = unknown, TRes = unknown> = (
  body: TReq,
  req: HttpRequest<TReq>
) => Observable<TRes> | TRes;

export interface MockRegistration<TReq = unknown, TRes = unknown> {
  /**
   * Function route name as it appears in the URL path,
   * e.g. 'auth-password-login' for `/api/auth-password-login`.
   * Must match the `[Function("...")]` name on the real Azure Function.
   */
  route: string;
  handler: MockHandler<TReq, TRes>;
}
