import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { LoginCommand } from "app/modules/auth/login/commands/login.command";
import { SsoExchangeCommand } from "app/modules/auth/login/commands/sso-exchange.command";
import { LoginViewModel } from "app/modules/auth/login/viewmodels/login.viewmodel";
import { AuthService } from "app/core/services/auth.service";
import { ConfigurationService } from "app/core/services/configuration.service";
import { ServiceBase } from "app/core/services/service-base";
import { Observable } from "rxjs";

// Root-provided rather than declared on AuthModule: SsoCallbackComponent is a
// standalone `loadComponent` route outside that module, so a module-scoped
// provider is invisible to it (NG0201).
@Injectable({ providedIn: 'root' })
export class LoginService extends ServiceBase {

  private readonly URL: string;

  constructor(httpClient: HttpClient, authService: AuthService, configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  /** Email + password sign-in. Backend: `Babesiosis.Core.Functions.Auth.PasswordLogin`. */
  passwordLogin(command: LoginCommand): Observable<LoginViewModel> {
    return this.httpClient.post<LoginViewModel>(`${this.URL}/auth-password-login`, command);
  }

  /**
   * Trades the identity provider's authorization code for a Babesiosis JWT.
   * Backend: `Babesiosis.Core.Functions.Auth.SsoExchange`.
   */
  exchangeSso(code: string): Observable<LoginViewModel> {
    return this.httpClient.post<LoginViewModel>(
      `${this.URL}/auth-sso-exchange`,
      new SsoExchangeCommand(code));
  }

  /**
   * Full-page redirect target that starts the Entra sign-in dance. This is a
   * browser navigation rather than an XHR — the function answers with a 302 to
   * the identity provider, which eventually lands back on /sso-callback.
   */
  get ssoInitiateUrl(): string {
    return `${this.URL}/auth-sso-initiate`;
  }
}
