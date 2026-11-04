import { ChangeDetectionStrategy, Component, DestroyRef, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  AbstractControl,
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import {
  FsButtonComponent,
  FsFormFieldComponent,
  FsSymbolComponent,
  FsTextInputComponent,
} from '@core';
import { PasswordResetService } from 'app/modules/auth/password-reset/password-reset.service';

@Component({
  selector: 'fs-reset-password',
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
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ResetPasswordComponent {
  private readonly fb = inject(FormBuilder);
  private readonly passwordResetService = inject(PasswordResetService);
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);

  // Token arrives via the emailed link: /reset-password?token=...
  private readonly token = this.route.snapshot.queryParamMap.get('token');

  protected readonly hasToken = signal(!!this.token);
  protected readonly loading = signal(false);
  protected readonly completed = signal(false);
  protected readonly errorMessage = signal<string | null>(null);

  protected readonly form: FormGroup = this.fb.group({
    newPassword: ['', [Validators.required, Validators.minLength(8)]],
    confirmPassword: ['', [Validators.required]],
  }, {
    validators: this.passwordsMatchValidator,
  });

  private passwordsMatchValidator(control: AbstractControl): ValidationErrors | null {
    const np = control.get('newPassword');
    const cp = control.get('confirmPassword');
    if (!np || !cp) return null;
    return np.value === cp.value ? null : { passwordsMismatch: true };
  }

  protected onSubmit(): void {
    if (!this.token) return;
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.loading.set(true);
    this.errorMessage.set(null);

    this.passwordResetService.resetPassword(this.token, this.form.value.newPassword)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => this.loading.set(false)),
      )
      .subscribe({
        // `auth-password-reset` answers with a bare 200 on success and a 500 on
        // any failure (bad, expired, or already-used token), so success is the
        // absence of an error rather than a flag on a body.
        next: () => this.completed.set(true),
        error: () => this.errorMessage.set('This reset link is invalid or has expired.'),
      });
  }

  protected hasError(controlName: string, errorName: string): boolean {
    const c = this.form.get(controlName);
    return c ? c.hasError(errorName) && c.touched : false;
  }

  protected getErrorMessage(field: string): string | null {
    const c = this.form.get(field);
    if (!c || !c.touched || c.valid) return null;
    if (c.hasError('required')) return field === 'newPassword' ? 'New password is required' : 'Confirm password is required';
    if (c.hasError('minlength')) {
      const min = c.getError('minlength').requiredLength;
      return `Password must be at least ${min} characters`;
    }
    return null;
  }

  protected getMismatchError(): string | null {
    const confirm = this.form.get('confirmPassword');
    if (!confirm?.touched) return null;
    return this.form.hasError('passwordsMismatch') ? 'Passwords do not match.' : null;
  }
}
