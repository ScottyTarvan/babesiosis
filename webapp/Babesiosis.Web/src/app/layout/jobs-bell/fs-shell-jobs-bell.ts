import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';
import { FsSymbolComponent } from '@core';
import { BackgroundJobsService } from 'app/core/services/background-jobs.service';
import { FsShellJobsPanel } from '@layouts/jobs-bell/fs-shell-jobs-panel';

/**
 * The topbar alert: something is waiting for a person.
 *
 * Two states only, because the feed carries one thing — runs parked at
 * AwaitingApproval. Quiet when there is nothing, red and pulsing when there is.
 * There is no neutral "work is happening" state: the feed does not surface
 * running deployments, so the bell would have nothing to say.
 *
 * Lives under `layout/` rather than in the gnome-ui library: it is shell furniture,
 * not a reusable primitive, and `scripts/fs-guard.mjs` exempts this folder so it
 * can render a bare `<button>` instead of bending `fs-button` into a shape that
 * does not quite fit.
 *
 * Its button styling is its own (see the scss). The topbar's
 * `.fs-shell-topbar__icon-btn` looks like the obvious thing to reuse, but that
 * rule is view-encapsulated to the topbar's template and silently does nothing
 * here — the button would fall back to the UA default border and fill.
 */
@Component({
  selector: 'fs-shell-jobs-bell',
  standalone: true,
  imports: [FsSymbolComponent, FsShellJobsPanel],
  templateUrl: './fs-shell-jobs-bell.html',
  styleUrls: ['./fs-shell-jobs-bell.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FsShellJobsBell {

  private readonly service = inject(BackgroundJobsService);

  protected readonly open = signal(false);
  protected readonly count = this.service.count;

  protected readonly icon = computed(() => (this.count() > 0 ? 'bell-ringing' : 'bell'));

  /** Two digits is all the badge has room for; past that the number stops mattering. */
  protected readonly badgeText = computed(() => (this.count() > 9 ? '9+' : String(this.count())));

  protected readonly ariaLabel = computed(() => {
    const count = this.count();
    if (count === 0) return 'Background jobs';
    return count === 1
      ? 'Background jobs, 1 waiting for your approval'
      : `Background jobs, ${count} waiting for your approval`;
  });

  /**
   * The screen-reader announcement, held separately from {@link ariaLabel}.
   *
   * Written ONLY when the count rises. A live region that echoed every poll
   * would re-announce the same backlog every 30 seconds, and one that announced
   * decreases would narrate the user's own approvals back at them. Arrival is
   * the only event worth interrupting for.
   */
  protected readonly liveMessage = signal('');

  constructor() {
    let previous = 0;
    effect(() => {
      const count = this.count();
      if (count > previous) {
        this.liveMessage.set(count === 1
          ? '1 deployment is waiting for your approval'
          : `${count} deployments are waiting for your approval`);
      } else if (count === 0) {
        // Cleared rather than left standing, so a later re-arrival is a genuine
        // change to the region rather than an identical string the reader skips.
        this.liveMessage.set('');
      }
      previous = count;
    });
  }

  protected toggle(): void {
    this.open.update(v => !v);
  }
}
