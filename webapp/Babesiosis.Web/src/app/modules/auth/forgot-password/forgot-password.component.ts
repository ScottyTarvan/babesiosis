import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import {
  FsButtonComponent,
  FsFormFieldComponent,
  FsSymbolComponent,
  FsTextInputComponent,
} from '@core';
import { PasswordResetService } from 'app/modules/auth/password-reset/password-reset.service';

@Component({
  selector: 'fs-forgot-password',
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
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ForgotPasswordComponent {
  private readonly fb = inject(FormBuilder);
  private readonly passwordResetService = inject(PasswordResetService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly loading = signal(false);
  protected readonly submitted = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly form: FormGroup = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
  });

  protected onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    const email = this.form.value.email?.trim();
    this.passwordResetService.forgotPassword(email)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => this.loading.set(false)),
      )
      .subscribe({
        // `auth-password-forgot` returns true only when it matched an account
        // and queued the mail, false otherwise — so a false here means nothing
        // was sent and telling the user to check their inbox would be a lie.
        // This mirrors the legacy module's error/no-error split.
        next: (sent: boolean) => {
          if (sent) {
            this.submitted.set(true);
          } else {
            this.errorMessage.set('We could not find an account for that email address.');
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
    if (c.hasError('required')) return 'Email address is required';
    if (c.hasError('email')) return 'Please enter a valid email address';
    return null;
  }
}
