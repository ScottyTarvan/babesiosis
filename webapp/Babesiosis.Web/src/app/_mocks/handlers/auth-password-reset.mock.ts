import { HttpErrorResponse } from '@angular/common/http';
import { throwError } from 'rxjs';
import { MockRegistration } from 'app/_mocks/mock-handler';

/**
 * Mirrors `Babesiosis.Core.Api/Auth/Controllers/ResetPasswordController`.
 *
 * Real backend behavior: a bare 200 with no body on success; any failure
 * (invalid, expired, or already-used token) surfaces as a 500. There is no
 * success flag on a body — the frontend keys off the error channel.
 *
 * Mock behavior: any non-empty token succeeds; an empty one 500s so the
 * failure branch stays exercisable.
 */
export const authPasswordResetMock: MockRegistration<{ token: string, password: string }, void> = {
  route: 'auth-password-reset',
  handler: (body) => body?.token
    ? undefined
    : throwError(() => new HttpErrorResponse({
      status: 500,
      statusText: 'Internal Server Error',
      error: { message: 'This reset link is invalid or has expired.' }
    }))
};
