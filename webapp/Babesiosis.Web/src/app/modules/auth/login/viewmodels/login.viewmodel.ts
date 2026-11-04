import { UserViewModel } from 'app/core/viewmodels/user.viewmodel';

/**
 * LoginViewModel — the response of both `auth-password-login` and
 * `auth-sso-exchange`. Mirrors the backend
 * `Babesiosis.Core.Api.Auth.ViewModels.LoginViewModel`.
 *
 * `passed` is the success discriminator; on failure `message` carries the
 * reason and `user` / `authToken` are absent.
 */
export class LoginViewModel {
  passed = false;
  message: string;
  authToken: string;
  refreshToken: string;
  user = new UserViewModel();

  constructor(login?: LoginViewModel | Partial<LoginViewModel>) {
    this.passed = login?.passed ?? false;
    this.message = login?.message;
    this.authToken = login?.authToken;
    this.refreshToken = login?.refreshToken;
    this.user = new UserViewModel(login?.user);
  }
}
