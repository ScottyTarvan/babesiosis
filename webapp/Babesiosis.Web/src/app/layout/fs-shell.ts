import { A11yModule } from '@angular/cdk/a11y';
import { BreakpointObserver } from '@angular/cdk/layout';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  inject,
  signal,
  untracked,
  OnInit,
  OnDestroy,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import {
  NavigationCancel,
  NavigationEnd,
  NavigationError,
  NavigationStart,
  Router,
  RouterOutlet,
} from '@angular/router';
import { Store } from '@ngrx/store';
import { Subscription } from 'rxjs';
import { filter } from 'rxjs/operators';
import { FsShellSidebar } from '@layouts/fs-shell-sidebar';
import { FsShellTopbar } from '@layouts/fs-shell-topbar';
import { FsSpinnerComponent, FsToastContainerComponent } from '@fundstream-ai/gnome-ui';

/**
 * The shell's narrow boundary — Bootstrap's `lg` edge, the same value the
 * `.fs-kpi-grid` utility switches at. Below it the sidebar
 * stops taking layout width and becomes an overlay drawer.
 *
 * **`fs-shell.scss` owns the layout half of this decision.** The media query
 * there is what actually takes the sidebar out of flow, so the content area is
 * full-width at narrow widths even before a single line of TypeScript runs.
 * This query only drives *behaviour* — whether the drawer can be opened, the
 * focus trap, and whether the sidebar renders as an icon rail. Keep the two
 * values identical.
 */
const NARROW_QUERY = '(max-width: 1023.98px)';

/** Where the manual desktop collapse choice is remembered between sessions. */
const COLLAPSED_KEY = 'fs-sidebar-collapsed';

@Component({
  selector: 'fs-shell',
  standalone: true,
  imports: [
    A11yModule,
    FsShellSidebar,
    FsShellTopbar,
    FsSpinnerComponent,
    FsToastContainerComponent,
    RouterOutlet,
  ],
  templateUrl: './fs-shell.html',
  styleUrls: ['./fs-shell.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FsShell implements OnInit, OnDestroy {
  private readonly breakpoint = inject(BreakpointObserver);
  private readonly store = inject(Store);
  private readonly router = inject(Router);
  private routerSub?: Subscription;

  /**
   * The user's manual collapse choice. Desktop-only state: the responsive
   * behaviour never writes to it, so crossing the breakpoint and coming back
   * lands on whatever the user last chose. Persisted so a reload does too.
   */
  protected readonly collapsed = signal<boolean>(readCollapsedPreference());

  /** Whether the overlay drawer is showing. Only meaningful below `NARROW_QUERY`. */
  protected readonly drawerOpen = signal<boolean>(false);

  protected readonly activePath = signal<string>(this.router.url);
  protected readonly navigating = signal<boolean>(false);
  private navigatingTimer?: ReturnType<typeof setTimeout>;

  /** Mirrors `NARROW_QUERY`. Behavioural only — see the constant's comment. */
  private readonly narrow = signal<boolean>(matchesNarrow());

  /**
   * The sidebar renders as an icon rail only when the user asked for it *and*
   * we're wide enough for the rail to be the sidebar. As a drawer it always
   * shows full labels — an overlay that costs a tap to open has no reason to
   * hide the thing it was opened for.
   */
  protected readonly railCollapsed = computed(() => this.collapsed() && !this.narrow());

  constructor() {
    this.breakpoint
      .observe(NARROW_QUERY)
      .pipe(takeUntilDestroyed())
      .subscribe((state) => this.setNarrow(state.matches));

    // Close the drawer whenever the route changes. Unconditional: at desktop
    // widths `drawerOpen` is already false, so there is nothing to guard.
    effect(() => {
      this.activePath();
      untracked(() => {
        if (this.drawerOpen()) this.drawerOpen.set(false);
      });
    });
  }

  ngOnInit(): void {
    // Mirror the NgRx layout theme into the document so unmigrated
    // (Material) pages keep their dark mode wiring.
    this.store.select('layout').subscribe((data: { LAYOUT_THEME: string }) => {
      document.documentElement.setAttribute('data-bs-theme', data.LAYOUT_THEME);
    });

    this.routerSub = this.router.events
      .pipe(
        filter(
          (e): e is NavigationStart | NavigationEnd | NavigationCancel | NavigationError =>
            e instanceof NavigationStart ||
            e instanceof NavigationEnd ||
            e instanceof NavigationCancel ||
            e instanceof NavigationError,
        ),
      )
      .subscribe((event) => {
        if (event instanceof NavigationStart) {
          // Delay the busy indicator so instant navigations (tab switches
          // within a shell) don't flash it; slow ones (lazy chunk download,
          // entry-route project resolution) show pulse dots.
          clearTimeout(this.navigatingTimer);
          this.navigatingTimer = setTimeout(() => this.navigating.set(true), 150);
          return;
        }

        clearTimeout(this.navigatingTimer);
        this.navigating.set(false);

        if (!(event instanceof NavigationEnd)) return;

        this.activePath.set(event.urlAfterRedirects);
      });
  }

  ngOnDestroy(): void {
    this.routerSub?.unsubscribe();
    clearTimeout(this.navigatingTimer);
  }

  /** The seam handle — the manual desktop collapse. Never called at narrow
   *  widths: the handle is hidden there by media query. */
  protected toggleCollapsed(): void {
    this.collapsed.update((v) => !v);
    writeCollapsedPreference(this.collapsed());
  }

  protected toggleDrawer(): void {
    // Re-read the query rather than trust the cached flag: `matchMedia` change
    // events are only delivered while the page is painting, so a tab that was
    // resized while hidden can hold a stale value until it renders again. The
    // layout itself is CSS-driven and already correct; this keeps the rail /
    // focus-trap decisions correct too.
    this.syncNarrow();
    this.drawerOpen.update((v) => !v);
  }

  protected closeDrawer(): void {
    this.drawerOpen.set(false);
  }

  protected onSidebarKeydown(event: KeyboardEvent): void {
    if (event.key === 'Escape' && this.drawerOpen()) {
      event.preventDefault();
      this.closeDrawer();
    }
  }

  private setNarrow(value: boolean): void {
    if (this.narrow() === value) return;
    this.narrow.set(value);
    // Growing past the breakpoint retires the overlay. `collapsed` is left
    // exactly as the user set it — the two pieces of state never touch.
    if (!value) this.drawerOpen.set(false);
  }

  private syncNarrow(): void {
    this.setNarrow(matchesNarrow());
  }
}

function matchesNarrow(): boolean {
  return typeof window !== 'undefined' && !!window.matchMedia
    ? window.matchMedia(NARROW_QUERY).matches
    : false;
}

function readCollapsedPreference(): boolean {
  try {
    return localStorage.getItem(COLLAPSED_KEY) === 'true';
  } catch {
    // Storage can throw outright under a locked-down privacy mode.
    return false;
  }
}

function writeCollapsedPreference(value: boolean): void {
  try {
    localStorage.setItem(COLLAPSED_KEY, String(value));
  } catch {
    // Preference is a nicety; losing it must never break the toggle.
  }
}
