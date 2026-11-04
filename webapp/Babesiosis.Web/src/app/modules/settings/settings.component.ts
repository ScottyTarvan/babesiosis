import { CommonModule } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  inject,
  OnInit,
  signal,
} from '@angular/core';
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
import { Observable } from 'rxjs';
import { AuthService } from 'app/core/services/auth.service';
import { UserViewModel } from 'app/core/viewmodels/user.viewmodel';
import {
  FsButtonComponent,
  FsCardComponent,
  FsFormFieldComponent,
  FsPageHeaderComponent,
  FsSymbolComponent,
  FsTextInputComponent,
  FsToastService,
} from '@core';
import { ChangePasswordCommand } from 'app/modules/settings/commands/change-password.command';
import { UpdateProfileCommand } from 'app/modules/settings/commands/update-profile.command';
import { SettingsService } from 'app/modules/settings/settings.service';
import { McpTokensCardComponent } from 'app/modules/settings/mcp-tokens/mcp-tokens-card.component';

@Component({
  selector: 'fs-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss'],
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    FsButtonComponent,
    FsCardComponent,
    FsFormFieldComponent,
    FsPageHeaderComponent,
    FsSymbolComponent,
    FsTextInputComponent,
    McpTokensCardComponent,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SettingsComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly settingsService = inject(SettingsService);
  private readonly authService = inject(AuthService);
  private readonly toast = inject(FsToastService);
  private readonly destroyRef = inject(DestroyRef);

  protected readonly isLoading = signal(false);
  protected readonly isResetting = signal(false);
  protected readonly isSavingProfile = signal(false);
  protected readonly formError = signal<string | null>(null);
  protected readonly profileError = signal<string | null>(null);

  protected readonly currentUser$: Observable<UserViewModel> = this.authService.user$;

  protected profileForm!: FormGroup;
  protected changePasswordForm!: FormGroup;

  ngOnInit(): void {
    const user = this.authService.user;
    this.profileForm = this.fb.group({
      firstName: [user?.firstName ?? '', [Validators.required]],
      lastName: [user?.lastName ?? '', [Validators.required]],
      email: [user?.email ?? '', [Validators.required, Validators.email]],
    });

    this.changePasswordForm = this.fb.group({
      currentPassword: ['', [Validators.required]],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', [Validators.required]],
    }, {
      validators: this.passwordsMatchValidator,
    });
  }

  private passwordsMatchValidator(control: AbstractControl): ValidationErrors | null {
    const np = control.get('newPassword');
    const cp = control.get('confirmPassword');
    if (!np || !cp) return null;
    return np.value === cp.value ? null : { passwordsMismatch: true };
  }

  protected hasError(form: FormGroup, controlName: string, errorName: string): boolean {
    const c = form.get(controlName);
    return c ? c.hasError(errorName) && c.touched : false;
  }

  protected getFieldError(form: FormGroup, field: string): string | null {
    const c = form.get(field);
    if (!c || !c.touched || c.valid) return null;
    if (c.hasError('required')) return `${this.label(field)} is required`;
    if (c.hasError('email')) return 'Enter a valid email address';
    if (c.hasError('minlength')) {
      const min = c.getError('minlength').requiredLength;
      return `${this.label(field)} must be at least ${min} characters`;
    }
    return null;
  }

  protected getMismatchError(): string | null {
    const f = this.changePasswordForm;
    const confirm = f.get('confirmPassword');
    if (!confirm?.touched) return null;
    return f.hasError('passwordsMismatch') ? 'Passwords do not match.' : null;
  }

  protected onSaveProfile(): void {
    if (this.isSavingProfile()) return;
    if (this.profileForm.invalid) {
      this.profileForm.markAllAsTouched();
      return;
    }

    this.profileError.set(null);
    this.isSavingProfile.set(true);
    const command: UpdateProfileCommand = {
      firstName: this.profileForm.get('firstName')?.value?.trim(),
      lastName: this.profileForm.get('lastName')?.value?.trim(),
      email: this.profileForm.get('email')?.value?.trim(),
    };

    this.settingsService.updateProfile(command)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (response) => {
          this.isSavingProfile.set(false);
          if (response.success) {
            this.applyProfileToUser(command);
            this.profileForm.markAsPristine();
            this.toast.success('Profile updated successfully');
          } else {
            const msg = response.message || 'Failed to update profile.';
            this.profileError.set(msg);
            this.toast.danger(msg);
          }
        },
        error: (err) => {
          this.isSavingProfile.set(false);
          const msg = err?.error?.message ?? err?.message ?? 'An error occurred while updating your profile.';
          this.profileError.set(msg);
          this.toast.danger(msg);
        },
      });
  }

  private applyProfileToUser(command: UpdateProfileCommand): void {
    const current = this.authService.user;
    if (!current) return;
    const updated = new UserViewModel({
      ...current,
      firstName: command.firstName,
      lastName: command.lastName,
      email: command.email,
    });
    this.authService.user = updated;
    this.authService.userSubject.next(updated);
  }

  protected onChangePassword(): void {
    if (this.isLoading()) return;
    if (this.changePasswordForm.invalid) {
      this.changePasswordForm.markAllAsTouched();
      return;
    }

    this.formError.set(null);
    this.isLoading.set(true);
    const command: ChangePasswordCommand = {
      currentPassword: this.changePasswordForm.get('currentPassword')?.value,
      newPassword: this.changePasswordForm.get('newPassword')?.value,
      confirmPassword: this.changePasswordForm.get('confirmPassword')?.value,
    };

    this.settingsService.changePassword(command)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (response) => {
          this.isLoading.set(false);
          if (response.success) {
            this.toast.success('Password changed successfully');
            this.changePasswordForm.reset();
          } else {
            const msg = response.message || 'Failed to change password.';
            this.formError.set(msg);
            this.toast.danger(msg);
          }
        },
        error: (err) => {
          this.isLoading.set(false);
          const msg = err?.error?.message ?? err?.message ?? 'An error occurred while changing password.';
          this.formError.set(msg);
          this.toast.danger(msg);
        },
      });
  }

  protected onResetPassword(): void {
    if (this.isResetting()) return;
    const user = this.authService.user;
    if (!user?.email) {
      this.toast.danger('Unable to reset password: no email on file.');
      return;
    }

    this.isResetting.set(true);
    this.settingsService.resetPassword(user.email)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe({
        next: (sent: boolean) => {
          this.isResetting.set(false);
          if (sent) {
            this.toast.success('Password reset link sent to your email');
          } else {
            this.toast.danger('Failed to send reset link.');
          }
        },
        error: (err) => {
          this.isResetting.set(false);
          const msg = err?.error?.message ?? err?.message ?? 'An error occurred while resetting password.';
          this.toast.danger(msg);
        },
      });
  }

  protected onLogout(): void {
    this.authService.logout();
  }

  private label(field: string): string {
    if (field === 'currentPassword') return 'Current password';
    if (field === 'newPassword') return 'New password';
    if (field === 'confirmPassword') return 'Confirm password';
    if (field === 'firstName') return 'First name';
    if (field === 'lastName') return 'Last name';
    if (field === 'email') return 'Email address';
    return field;
  }
}
