
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  input,
  OnInit,
  output,
  signal,
} from '@angular/core';
import { Store } from '@ngrx/store';
import { changetheme } from '@layouts/layout-action';
import { getLayoutColor } from '@layouts/layout-selector';
import { FsSymbolComponent } from '@core';
// The approvals bell — see FsShellJobsBell's own doc comment. The topbar used to
// carry a global error toast beside it; that is gone. A failed request is now
// reported only by the screen that made it, next to the thing that failed.
import { FsShellJobsBell } from '@layouts/jobs-bell/fs-shell-jobs-bell';

@Component({
  selector: 'fs-shell-topbar',
  standalone: true,
  imports: [
    FsSymbolComponent,
    FsShellJobsBell
],
  templateUrl: './fs-shell-topbar.html',
  styleUrls: ['./fs-shell-topbar.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FsShellTopbar implements OnInit {
  /** Whether the shell's overlay navigation drawer is currently showing. */
  readonly drawerOpen = input<boolean>(false);

  readonly menuToggled = output<void>();

  private readonly store = inject(Store);

  protected readonly theme = signal<'light' | 'dark'>('light');

  // The desktop collapse lives on the sidebar's own seam handle; this button is
  // only ever the drawer opener, and only ever visible below the boundary.
  protected readonly menuButtonLabel = computed(() =>
    this.drawerOpen() ? 'Close navigation' : 'Open navigation',
  );

  protected readonly themeIcon = computed(() => this.theme() === 'dark' ? 'sun' : 'moon');

  ngOnInit(): void {
    this.store.select(getLayoutColor).subscribe((color) => {
      this.theme.set(color === 'dark' ? 'dark' : 'light');
    });
  }

  protected onMenuToggle(): void {
    this.menuToggled.emit();
  }

  protected changeTheme(): void {
    const next = this.theme() === 'light' ? 'dark' : 'light';
    this.store.dispatch(changetheme({ color: next }));
  }
}
