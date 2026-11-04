import { MockRegistration } from 'app/_mocks/mock-handler';

/**
 * Mirrors `Babesiosis.Core.Api/Auth/Controllers/ForgotPasswordController`.
 *
 * Real backend behavior: returns a bare JSON boolean — true when it matched a
 * non-deleted user and queued the reset email, false when no such account
 * exists. Mock behavior: any address succeeds. Return false to exercise the
 * "no account for that email" path.
 */
export const authPasswordForgotMock: MockRegistration<{ email: string }, boolean> = {
  route: 'auth-password-forgot',
  handler: () => true
};
