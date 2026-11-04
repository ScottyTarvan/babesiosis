import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { AuthService } from 'app/core/services/auth.service';

/**
 * Restricts a route to super administrators. Unlike AdminRoleGuard (a
 * placeholder that lets any authenticated member through), this guard actually
 * enforces the privilege: it backs super-admin-only routes
 * as defence-in-depth alongside the nav hiding and the backend
 * permission checks.
 */
@Injectable({ providedIn: 'root' })
export class SuperAdminRoleGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) { }

  canActivate(_route: ActivatedRouteSnapshot, _state: RouterStateSnapshot): boolean | UrlTree {
    if (!this.authService.isAuthenticated) {
      this.authService.logout();
      return false;
    }

    if (this.authService.user?.isSuperAdministrator) {
      return true;
    }

    // Not a super admin — send them back to the app landing rather than exposing
    // the guarded area.
    return this.router.createUrlTree(['/']);
  }
}
