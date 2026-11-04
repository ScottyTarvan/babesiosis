
import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  ElementRef,
  inject,
  input,
  model,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NavigationEnd, Router } from '@angular/router';
import { filter } from 'rxjs/operators';
import { FsBadgeComponent, FsBannerComponent, FsButtonComponent, FsPopoverComponent, FsSymbolComponent } from '@core';
import { BackgroundJobsService } from 'app/core/services/background-jobs.service';

/**
 * The bell's dropdown: what is currently waiting on a person.
 *
 * Rows are read-only: the dataset deployment log they used to open was removed
 * with the data module.
 */
@Component({
  selector: 'fs-shell-jobs-panel',
  standalone: true,
  imports: [
    FsBadgeComponent,
    FsBannerComponent,
    FsButtonComponent,
    FsPopoverComponent,
    FsSymbolComponent
],
  templateUrl: './fs-shell-jobs-panel.html',
  styleUrls: ['./fs-shell-jobs-panel.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FsShellJobsPanel {

  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);
  protected readonly service = inject(BackgroundJobsService);

  readonly anchor = input.required<HTMLElement | ElementRef<HTMLElement>>();
  readonly open = model<boolean>(false);

  constructor() {
    // A sidebar link sits behind the backdrop and cannot be clicked while the
    // panel is open — but a route change from anywhere else (a toast action, the
    // back button) would otherwise leave the panel floating over a page it has
    // nothing to do with.
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(() => this.open.set(false));
  }

  protected onRetry(): void {
    this.service.refresh();
  }
}
