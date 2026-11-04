
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
  isDevMode,
  output,
} from '@angular/core';
import { MENU, type MenuItem } from '@layouts/menu-meta';
import { AuthService } from 'app/core/services/auth.service';
import { FsSymbolComponent } from '@core';
import { FsShellSidebarItem } from '@layouts/fs-shell-sidebar-item';

@Component({
  selector: 'fs-shell-sidebar',
  standalone: true,
  imports: [FsShellSidebarItem, FsSymbolComponent],
  templateUrl: './fs-shell-sidebar.html',
  styleUrls: ['./fs-shell-sidebar.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FsShellSidebar {
  readonly activePath = input<string>('');
  /** Renders the icon rail. The shell only ever sets this at desktop widths —
   *  below its narrow boundary the sidebar is an overlay drawer and always
   *  shows full labels. */
  readonly collapsed = input<boolean>(false);

  readonly collapseToggled = output<void>();

  private readonly authService = inject(AuthService);

  // Small arrow for the seam handle: points right (expand) when collapsed,
  // left (collapse) when open.
  protected readonly collapseIcon = computed(() =>
    this.collapsed() ? 'chevron-right' : 'chevron-left',
  );

  protected readonly collapseLabel = computed(() =>
    this.collapsed() ? 'Expand sidebar' : 'Collapse sidebar',
  );

  /** Administrators see every menu item; others have `adminOnly` items hidden. */
  protected readonly isAdmin = computed(
    () => this.authService.user?.isAdministrator ?? false,
  );

  /** Super administrators additionally see `superAdminOnly` items (none at
   *  present). Regular administrators do not. */
  protected readonly isSuperAdmin = computed(
    () => this.authService.user?.isSuperAdministrator ?? false,
  );

  /** The menu, with `adminOnly` / `superAdminOnly` items filtered out for
   *  members without the matching privilege, and `devOnly` items filtered out in
   *  production (their routes don't exist there). */
  protected readonly menu = computed<MenuItem[]>(() => {
    const admin = this.isAdmin();
    const superAdmin = this.isSuperAdmin();
    return MENU.filter((item) =>
      (!item.adminOnly || admin)
      && (!item.superAdminOnly || superAdmin)
      && (!item.devOnly || isDevMode()));
  });

  /**
   * Sidebar width, as an inline style so the collapse can transition it.
   *
   * The open width reads --fs-nav-width (232px, the style guideline's figure)
   * rather than a rem value: the document sets `html { font-size: 14px }`, so
   * rem units here resolve against 14px and every "obvious" conversion is out
   * by 12.5%. The guideline's numbers are all absolute px, so the token is too.
   *
   * The collapsed rail is ours, not the guideline's — it has no icon-rail
   * concept — so that arm keeps the width it already had.
   */
  protected readonly widthRem = computed(() =>
    this.collapsed() ? '4.5rem' : 'var(--fs-nav-width)',
  );

  protected onCollapseToggle(): void {
    this.collapseToggled.emit();
  }

  /**
   * The one link the current path belongs to: the LONGEST link that is the
   * path itself or a segment-prefix of it.
   *
   * Plain prefix matching would light two items at once wherever one link
   * nests under another. The longest match is the most specific destination,
   * and it alone is the active one; the shorter link still owns its own
   * sub-routes because nothing longer claims them.
   */
  private readonly activeLink = computed<string | null>(() => {
    const current = this.activePath();
    if (!current) return null;
    let best: string | null = null;
    for (const { link } of this.menu()) {
      if (link && (current === link || current.startsWith(`${link}/`))
        && (best === null || link.length > best.length)) {
        best = link;
      }
    }
    return best;
  });

  protected isActive(item: MenuItem): boolean {
    return !!item.link && item.link === this.activeLink();
  }
}
