import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot } from '@angular/router';
import { AuthService } from 'app/core/services/auth.service';

@Injectable({ providedIn: 'root' })
export class MemberRoleGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) { }

  canActivate(_route: ActivatedRouteSnapshot, _state: RouterStateSnapshot): boolean {
    if (!this.authService.isAuthenticated) {
      this.authService.logout();
      return false;
    }

    // TODO: tighten when JWT 'role' claim lands. Today the user view model has no
    // explicit Member role; allow when authenticated to keep dev navigation working.
    return true;
  }
}
