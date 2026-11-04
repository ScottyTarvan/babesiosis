import { ChangeDetectionStrategy, Component, inject, OnInit } from '@angular/core';
import { AuthService } from 'app/core/services/auth.service';

/**
 * Route-addressable sign-out (`/logout`), ported from the legacy auth module.
 * The topbar and settings page call `AuthService.logout()` directly; this exists
 * so the action is also reachable as a plain URL — bookmarks, an external "sign
 * me out" link, or an idle-timeout redirect.
 *
 * Renders nothing: `logout()` clears local state and navigates to /login on the
 * same tick, so there is no frame where a template would be visible.
 */
@Component({
  selector: 'fs-logout',
  standalone: true,
  templateUrl: './logout.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LogoutComponent implements OnInit {
  private readonly authService = inject(AuthService);

  ngOnInit(): void {
    this.authService.logout();
  }
}
