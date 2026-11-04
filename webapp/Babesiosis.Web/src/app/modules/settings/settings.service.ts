import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ServiceBase } from 'app/core/services/service-base';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { map, Observable } from 'rxjs';
import { ChangePasswordCommand } from 'app/modules/settings/commands/change-password.command';
import { ChangePasswordViewModel } from 'app/modules/settings/viewmodels/change-password.viewmodel';
import { UpdateProfileCommand } from 'app/modules/settings/commands/update-profile.command';
import { UpdateProfileViewModel } from 'app/modules/settings/viewmodels/update-profile.viewmodel';
import { ActionItemCommand } from 'app/core/commands/action-item.command';
import { CreatePersonalAccessTokenCommand } from 'app/modules/settings/commands/create-personal-access-token.command';
import {
  CreatedPersonalAccessTokenViewModel,
  normalisePersonalAccessToken,
  PersonalAccessTokenViewModel,
  PersonalAccessTokensViewModel,
} from 'app/modules/settings/viewmodels/personal-access-token.viewmodel';

@Injectable({
  providedIn: 'root'
})
export class SettingsService extends ServiceBase {
  private URL: string;

  constructor(
    httpClient: HttpClient,
    authService: AuthService,
    configService: ConfigurationService) {
    super(httpClient, authService);
    this.URL = configService.coreAPI('');
  }

  changePassword(command: ChangePasswordCommand): Observable<ChangePasswordViewModel> {
    return this.post<ChangePasswordViewModel>(
      `${this.URL}/change-password`,
      command
    );
  }

  /**
   * Triggers the same "email me a reset link" flow as the anonymous forgot-password
   * page. Backend: `Babesiosis.Core.Functions.Auth.ForgotPassword`, which answers
   * with a bare JSON boolean — true when it matched an account and queued the mail.
   */
  resetPassword(email: string): Observable<boolean> {
    return this.post<boolean>(
      `${this.URL}/auth-password-forgot`,
      { email }
    );
  }

  updateProfile(command: UpdateProfileCommand): Observable<UpdateProfileViewModel> {
    return this.post<UpdateProfileViewModel>(
      `${this.URL}/update-profile`,
      command
    );
  }

  /** The caller's own MCP access tokens (platform/mcp-server.md §3.13). */
  searchMcpTokens(): Observable<PersonalAccessTokensViewModel> {
    return this.post<PersonalAccessTokensViewModel>(`${this.URL}/platform-mcp-tokens-search`, {})
      .pipe(map(r => ({ ...r, tokens: (r.tokens ?? []).map(normalisePersonalAccessToken) })));
  }

  /** Creates a token for the caller; the response is the only place the secret ever appears. */
  createMcpToken(command: CreatePersonalAccessTokenCommand): Observable<CreatedPersonalAccessTokenViewModel> {
    return this.post<CreatedPersonalAccessTokenViewModel>(`${this.URL}/platform-mcp-tokens-create`, command)
      .pipe(map(r => ({ ...r, token: normalisePersonalAccessToken(r.token) })));
  }

  revokeMcpToken(command: ActionItemCommand): Observable<PersonalAccessTokenViewModel> {
    return this.post<PersonalAccessTokenViewModel>(`${this.URL}/platform-mcp-tokens-revoke`, command)
      .pipe(map(normalisePersonalAccessToken));
  }
}
