import { ChangeDetectionStrategy, Component, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import {
  FsButtonComponent,
  FsFormFieldComponent,
  FsSymbolComponent,
  FsTextInputComponent,
} from '@core';
import { homeUrl } from '@layouts/constants';
import { LoginCommand } from 'app/modules/auth/login/commands/login.command';
import { LoginService } from 'app/modules/auth/login/login.service';
import { LoginViewModel } from 'app/modules/auth/login/viewmodels/login.viewmodel';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';

@Component({
  selector: 'fs-login',
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    FsButtonComponent,
    FsFormFieldComponent,
    FsSymbolComponent,
    FsTextInputComponent,
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly loginService = inject(LoginService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  private readonly configService = inject(ConfigurationService);

  protected readonly allowEntraLogin = this.configService.allowEntraLogin;
  protected readonly allowEmailLogin = this.configService.allowEmailLogin;

  protected readonly loading = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly form: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email, Validators.maxLength(320)]],
    password: ['', [Validators.required, Validators.minLength(4), Validators.maxLength(100)]],
  });

  ngOnInit(): void {
    // A failed SSO round trip bounces back here with ?error=… — surface it in
    // the same banner the password path uses.
    const error = this.route.snapshot.queryParamMap.get('error');
    if (error) {
      this.errorMessage.set(error);
    }

    // Already signed in (e.g. opened /login from a bookmark) — don't make them
    // authenticate again.
    if (this.authService.isAuthenticated) {
      this.router.navigateByUrl(this.returnUrl);
    }
  }

  /** Deep link the user was bounced off, else the default landing page. */
  private get returnUrl(): string {
    return this.route.snapshot.queryParamMap.get('returnUrl') || homeUrl;
  }

  /**
   * Hands the browser to the identity provider. This is a full-page navigation
   * rather than an XHR because the function replies with a 302 that the browser
   * must follow itself.
   */
  protected onEntraLogin(): void {
    this.errorMessage.set(null);
    window.location.href = this.loginService.ssoInitiateUrl;
  }

  protected onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    const { email, password } = this.form.value;
    const returnUrl = this.returnUrl;

    this.loginService.passwordLogin(new LoginCommand(email, password))
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => this.loading.set(false)),
      )
      .subscribe({
        next: data => {
          const login = new LoginViewModel(data);
          if (login.passed) {
            this.authService.saveLogin(login);
            this.router.navigateByUrl(returnUrl);
          } else {
            this.errorMessage.set(login.message || 'The login details are incorrect.');
          }
        },
        error: () => this.errorMessage.set('Something went wrong. Please try again.'),
      });
  }

  protected hasError(controlName: string, errorName: string): boolean {
    const c = this.form.get(controlName);
    return c ? c.hasError(errorName) && c.touched : false;
  }

  protected getErrorMessage(field: string): string | null {
    const c = this.form.get(field);
    if (!c || !c.touched || c.valid) return null;
    if (c.hasError('required')) return `${this.label(field)} is required`;
    if (c.hasError('email')) return 'Please enter a valid email address';
    if (c.hasError('minlength')) {
      const min = c.getError('minlength').requiredLength;
      return `${this.label(field)} must be at least ${min} characters`;
    }
    if (c.hasError('maxlength')) {
      const max = c.getError('maxlength').requiredLength;
      return `${this.label(field)} must be at most ${max} characters`;
    }
    return null;
  }

  private label(field: string): string {
    return field
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, c => c.toUpperCase())
      .trim();
  }
}
