import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { AuthService } from 'app/core/services/auth.service';

/**
 * Route guard on `/manage/roles`, `/manage/roles/:id/members`,
 * `/manage/roles/:id/permissions` and `/manage/users`.
 *
 * ## It is an authentication guard, not a permission guard
 *
 * Read the body: both branches return `true`. Any signed-in user reaches the
 * roles and users screens; the name promises a gate this class does not
 * implement. The `isAdministrator` branch is kept deliberately — it is the
 * shape the real check will take, and marks the line to change — but it decides
 * nothing today.
 *
 * That is **intentional and unchanged by the permissions alignment work**
 * (alignment-map R8). Tightening it needs a `role` claim on the JWT that does
 * not exist yet, and guessing at it from `UserViewModel.isAdministrator` —
 * which is written by the client from the login response — would be a gate a
 * user can edit in local storage, i.e. no gate at all.
 *
 * ## What actually protects these screens
 *
 * 1. The `permissions` echo on each screen's own read response disables every
 *    action the caller may not perform (`teams-role-list-get`,
 *    `teams-user-list-get`, `teams-role-permissions-get`).
 * 2. The server asserts on every write and 403s regardless of what the UI
 *    allowed. That is the real boundary.
 *
 * So an unauthorised user can currently *navigate* to `/manage/users` and see
 * a grid whose buttons are all disabled — an ugly outcome, not an unsafe one.
 *
 * ## When the claim lands
 *
 * Gate on the claim and **redirect** (to the landing route) rather than
 * returning `false` into an error page — a denied navigation should look like
 * a wrong turn, not a fault. `SuperAdminRoleGuard` is the only guard in the app
 * that denies today; follow its shape.
 */
@Injectable({ providedIn: 'root' })
export class AdminRoleGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) { }

  canActivate(_route: ActivatedRouteSnapshot, _state: RouterStateSnapshot): boolean {
    if (!this.authService.isAuthenticated) {
      this.authService.logout();
      return false;
    }

    // TODO: tighten when JWT 'role' claim lands. Today only isAdministrator on
    // UserViewModel is available; allow when authenticated to keep dev navigation working.
    const user = this.authService.user;
    if (user?.isAdministrator) {
      return true;
    }

    return true;
  }
}
