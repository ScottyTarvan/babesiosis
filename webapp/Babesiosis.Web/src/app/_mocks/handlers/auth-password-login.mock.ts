import { LoginCommand } from 'app/modules/auth/login/commands/login.command';
import { LoginViewModel } from 'app/modules/auth/login/viewmodels/login.viewmodel';
import { MockRegistration } from 'app/_mocks/mock-handler';

/**
 * Mirrors `Babesiosis.Core.Api/Auth/Controllers/PasswordLoginController.HandleCommand`.
 *
 * Real backend behavior: HTTP 200 with a LoginViewModel whose `passed` is true
 * on valid credentials; on failure `passed` is false and `message` carries the
 * reason. The frontend short-circuits on anything but `passed` (see
 * LoginComponent.onSubmit).
 *
 * Mock behavior: any credentials succeed. Flip `passed` to false and set a
 * `message` to exercise the failure path.
 */
export const authPasswordLoginMock: MockRegistration<LoginCommand, LoginViewModel> = {
  route: 'auth-password-login',
  handler: (body) => ({
    passed: true,
    message: '',
    authToken: 'mock-jwt-token',
    refreshToken: '',
    user: {
      instanceId: '00000000-0000-0000-0000-000000000001',
      rowVersion: undefined,
      firstName: 'Chad',
      lastName: 'Goldsworthy',
      email: body?.email ?? 'chad@example.com',
      password: '',
      mobileNumberCode: '+27',
      mobileNumber: '5550100',
      landlineNumberCode: '',
      landlineNumber: '',
      isAdministrator: true,
      isDeleted: false,
      // Not part of the backend contract — see UserViewModel. Kept true in the
      // mock so the super-admin-only nav stays reachable while developing
      // against mocks.
      isSuperAdministrator: true,
      permissions: {
        canViewManage: true,
        canViewPipelines: true,
        canViewReporting: true,
        canViewSetup: true,
        canViewTeams: true,
        canViewDataHealth: true,
        canViewStatistics: true,
      }
    }
  } as unknown as LoginViewModel)
};
