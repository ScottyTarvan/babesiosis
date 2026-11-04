import { SsoExchangeCommand } from 'app/modules/auth/login/commands/sso-exchange.command';
import { LoginViewModel } from 'app/modules/auth/login/viewmodels/login.viewmodel';
import { MockRegistration } from 'app/_mocks/mock-handler';
import { authPasswordLoginMock } from 'app/_mocks/handlers/auth-password-login.mock';

/**
 * Mirrors `Babesiosis.Core.Api/Auth/Controllers/SsoExchangeController`.
 *
 * Real backend behavior: trades the identity provider's authorization code for
 * the same LoginViewModel the password path returns.
 *
 * Mock behavior: reuses the password-login mock's user so both sign-in routes
 * land on an identical session. Note the initiate leg (`auth-sso-initiate`) is
 * a full-page 302 to the identity provider and so cannot be mocked here —
 * exercising the real Entra round trip needs a deployed environment.
 */
export const authSsoExchangeMock: MockRegistration<SsoExchangeCommand, LoginViewModel> = {
  route: 'auth-sso-exchange',
  handler: (body, req) =>
    authPasswordLoginMock.handler({ email: 'sso@example.com', password: '' }, req as never) as LoginViewModel
};
