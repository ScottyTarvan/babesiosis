import { UserPermissionsViewModel } from 'app/core/viewmodels/user-permissions.viewmodel';

/**
 * UserViewModel — the authenticated user profile carried on the login
 * response and held by the AuthService. Mirrors the backend
 * `Babesiosis.Core.ViewModels.UserViewModel`.
 *
 * Deliberately does NOT extend the frontend `ViewModel` base: that base
 * declares `permissions` as the per-row `Map<string, boolean>` grid-action map,
 * whereas the login payload's `permissions` is a `UserPermissionsViewModel`.
 * The two are unrelated despite sharing a name on the wire, so this model
 * declares the handful of base fields it actually needs instead.
 */
export class UserViewModel {
  instanceId?: string;
  rowVersion?: string;
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  mobileNumberCode: string;
  mobileNumber: string;
  landlineNumberCode: string;
  landlineNumber: string;
  isAdministrator = false;
  isDeleted = false;
  permissions = new UserPermissionsViewModel();

  /**
   * Mirrors `Babesiosis.Core.ViewModels.UserViewModel.IsSuperAdministrator`.
   * Super administrators hold every declared permission, including the
   * `SuperAdminOnly` ones that the ordinary administrator grant-all bypass
   * skips. Read by the shell nav and SuperAdminRoleGuard.
   */
  isSuperAdministrator = false;

  constructor(user?: UserViewModel | Partial<UserViewModel>) {
    this.instanceId = user?.instanceId;
    this.rowVersion = user?.rowVersion;
    this.firstName = user?.firstName;
    this.lastName = user?.lastName;
    this.email = user?.email;
    this.password = user?.password;
    this.mobileNumberCode = user?.mobileNumberCode;
    this.mobileNumber = user?.mobileNumber;
    this.landlineNumberCode = user?.landlineNumberCode;
    this.landlineNumber = user?.landlineNumber;
    this.isAdministrator = user?.isAdministrator ?? false;
    this.isDeleted = user?.isDeleted ?? false;
    this.isSuperAdministrator = user?.isSuperAdministrator ?? false;
    this.permissions = new UserPermissionsViewModel(user?.permissions);
  }

  toString() {
    return this.getFullName();
  }

  getFullName(): string {
    return `${this.firstName || ''} ${this.lastName || ''}`.trim();
  }

  getMobileNumber(): string {
    if (!this.mobileNumber) return '-';
    return this.mobileNumberCode
      ? `${this.mobileNumberCode} ${this.mobileNumber}`
      : this.mobileNumber;
  }

  getLandlineNumber(): string {
    if (!this.landlineNumber) return '-';
    return this.landlineNumberCode
      ? `${this.landlineNumberCode} ${this.landlineNumber}`
      : this.landlineNumber;
  }
}
