import { ChangeDetectionStrategy, Component, DestroyRef, inject, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { FsSpinnerComponent } from '@core';
import { homeUrl } from '@layouts/constants';
import { LoginService } from 'app/modules/auth/login/login.service';
import { LoginViewModel } from 'app/modules/auth/login/viewmodels/login.viewmodel';
import { AuthService } from 'app/core/services/auth.service';

/**
 * Landing point for the Entra redirect. The identity provider sends the browser
 * back here with `?code=…` (or `?error=…`); this component trades the code for
 * a Babesiosis JWT and then hands off to the app.
 *
 * Every failure path funnels back to /login with `?error=` so the login page is
 * the single place that renders auth errors.
 */
@Component({
  selector: 'fs-sso-callback',
  standalone: true,
  imports: [FsSpinnerComponent],
  templateUrl: './sso-callback.component.html',
  styleUrls: ['./sso-callback.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SsoCallbackComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);
  private readonly loginService = inject(LoginService);
  private readonly destroyRef = inject(DestroyRef);

  ngOnInit(): void {
    const code = this.route.snapshot.queryParamMap.get('code');
    const error = this.route.snapshot.queryParamMap.get('error');
    const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');

    if (error) {
      this.failTo(error);
      return;
    }

    if (!code) {
      this.failTo('SSO login failed');
      return;
    }

    this.loginService.exchangeSso(code)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: data => {
          const login = new LoginViewModel(data);
          if (login.passed) {
            this.authService.saveLogin(login);
            this.router.navigateByUrl(returnUrl || homeUrl);
          } else {
            this.failTo(login.message || 'SSO login failed');
          }
        },
        error: () => this.failTo('SSO login failed'),
      });
  }

  private failTo(error: string): void {
    this.router.navigate(['/login'], { queryParams: { error } });
  }
}
