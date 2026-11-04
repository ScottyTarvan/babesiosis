import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { Observable } from 'rxjs';

/**
 * Anonymous password-reset endpoints — both run before the user has a JWT, so
 * no auth state is required (the interceptor's empty Authorization header is
 * ignored server-side).
 */
@Injectable({
  providedIn: 'root'
})
export class PasswordResetService {
  private readonly URL: string;

  constructor(private httpClient: HttpClient, configService: ConfigurationService) {
    this.URL = configService.coreAPI('');
  }

  /**
   * Backend: `Babesiosis.Core.Functions.Auth.ForgotPassword`. Answers the same
   * way for every well-formed address so the endpoint can't be used to probe
   * which accounts exist.
   */
  forgotPassword(email: string): Observable<boolean> {
    return this.httpClient.post<boolean>(`${this.URL}/auth-password-forgot`, { email });
  }

  /**
   * Backend: `Babesiosis.Core.Functions.Auth.ResetPassword`. Returns a bare
   * 200 with no body on success and a 500 on any failure, so the caller keys
   * off the error channel rather than a result flag.
   */
  resetPassword(token: string, password: string): Observable<void> {
    return this.httpClient.post<void>(`${this.URL}/auth-password-reset`, { token, password });
  }
}
