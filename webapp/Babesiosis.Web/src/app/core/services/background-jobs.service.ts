import { HttpClient } from '@angular/common/http';
import { DestroyRef, Injectable, computed, effect, inject, signal } from '@angular/core';
import { takeUntilDestroyed, toObservable, toSignal } from '@angular/core/rxjs-interop';
import {
  EMPTY,
  Observable,
  Subject,
  defer,
  fromEvent,
  race,
  repeat,
  retry,
  switchMap,
  tap,
  throwError,
  timer,
} from 'rxjs';
import { AuthService } from 'app/core/services/auth.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { EnvironmentService } from 'app/core/services/environment.service';
import { ServiceBase } from 'app/core/services/service-base';
import {
  BackgroundJob,
  JOB_MAX_POLL_FAILURES,
  JOB_POLL_ACTIVE_MS,
  JOB_POLL_BACKOFF_CAP_MS,
  jobPollDelayMs,
  toBackgroundJobFeed,
} from 'app/core/types/background-job';

/** What the loop is currently doing, for the panel's chrome. */
export type BackgroundJobsState =
  /** Not polling — signed out. */
  | 'idle'
  /** First read in flight; nothing to render yet. */
  | 'loading'
  /** Polling. */
  | 'live'
  /** Suspended — hidden tab, or externally disabled. */
  | 'paused'
  /** Repeated failures; the loop has stopped and the user must retry. */
  | 'error';

/**
 * The background-jobs feed, polled for the lifetime of the session.
 *
 * ## What it is for
 *
 * Under approval-always every dataset deployment parks at AwaitingApproval and
 * waits for a person. The person who must approve is by design not the person
 * who started it, so without this they have no way of knowing. This service is
 * the only thing in the application that knows something is waiting.
 *
 * ## The cadence rule
 *
 * One loop, two speeds — see {@link jobPollDelayMs}. Empty feed polls every 60s
 * purely to discover a new arrival; a non-empty feed polls every 30s, monitoring
 * what is parked until the server stops returning it. That is the whole of
 * "only poll when there is something to poll for" that a browser can honestly
 * offer: without a push channel, *something* has to ask.
 *
 * ## Why the loop is shaped this way
 *
 * `defer(...).pipe(repeat({delay}), retry({delay}))`, not `timer(0, n)`. A fixed
 * timer with `switchMap` cancels a slow request and issues another, which under
 * load never completes one; this shape schedules the next request only after the
 * current one settles. Lifted from
 * `setup/datasets/deployment-log/deployment-tracking.service.ts`, which solved
 * the same problem for a single run and documents SignalR as the eventual
 * replacement. Keep the public signal surface stable and that swap replaces
 * {@link startLoop} alone.
 *
 * Deliberately NOT built on `reports/shared/polling.ts`: `createPoller` self-
 * terminates when its id list empties (this loop must stay armed on an empty
 * feed — that is its discovery mode), fixes its cadence at subscribe time, and
 * stops permanently on the first error. Three properties two reports screens
 * depend on, and all three are wrong here.
 */
@Injectable({ providedIn: 'root' })
export class BackgroundJobsService extends ServiceBase {

  private readonly destroyRef = inject(DestroyRef);
  private readonly environmentService = inject(EnvironmentService);
  private readonly url: string;

  constructor(
    httpClient: HttpClient,
    authService: AuthService,
    configService: ConfigurationService,
  ) {
    super(httpClient, authService);
    this.url = configService.coreAPI('');

    this.watchVisibility();
    this.watchEnvironment();
    this.startLoop();
  }

  // --------------------------------------------------------------- state ----
  private readonly jobsSignal = signal<readonly BackgroundJob[]>([]);
  private readonly hasMoreSignal = signal(false);
  private readonly stateSignal = signal<BackgroundJobsState>('idle');
  private readonly errorSignal = signal<string | null>(null);
  private readonly updatedSignal = signal<Date | null>(null);

  readonly jobs = this.jobsSignal.asReadonly();
  readonly hasMore = this.hasMoreSignal.asReadonly();
  readonly state = this.stateSignal.asReadonly();
  readonly lastError = this.errorSignal.asReadonly();
  readonly lastUpdatedAt = this.updatedSignal.asReadonly();

  /** What the bell's badge shows. */
  readonly count = computed(() => this.jobsSignal().length);
  /** Whether the bell is in its alert state at all. */
  readonly needsAttention = computed(() => this.count() > 0);

  private readonly documentVisible = signal(true);
  private readonly externallyEnabled = signal(true);
  private readonly consecutiveFailures = signal(0);

  /**
   * Seeded from localStorage by `AuthService`, so a page refresh re-arms the
   * loop without waiting for a login.
   */
  private readonly user = toSignal(this.authService.user$, { initialValue: null });
  private readonly authed = computed(() => !!this.user());

  /** The digest the last accepted response produced — the "nothing moved" gate. */
  private lastDigest = ' ';

  private readonly refreshNow$ = new Subject<void>();

  // ---------------------------------------------------------- the poll gate ----
  private readonly pollEnabled = computed(() =>
    this.authed()
    && this.documentVisible()
    && this.externallyEnabled()
    && this.consecutiveFailures() < JOB_MAX_POLL_FAILURES);

  private startLoop(): void {
    const poll$ = defer(() => this.fetch()).pipe(
      tap(response => this.apply(response)),
      repeat({ delay: () => race(timer(jobPollDelayMs(this.count())), this.refreshNow$) }),
      retry({ delay: (error: unknown) => this.handlePollError(error) }),
    );

    toObservable(this.pollEnabled).pipe(
      switchMap(on => {
        if (!on) {
          // Signing out must empty the bell at once rather than leave another
          // user's approvals on screen until the next login's first response.
          if (!this.authed()) this.reset();
          else if (this.stateSignal() === 'live') this.stateSignal.set('paused');
          return EMPTY;
        }
        if (this.stateSignal() === 'idle') this.stateSignal.set('loading');
        return poll$;
      }),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe();
  }

  private fetch(): Observable<unknown> {
    return this.post<unknown>(`${this.url}/jobs-background-get`, {
      // Misspelled to match the wire contract every environment-scoped command uses.
      enviroment: this.environmentService.current(),
    });
  }

  // ------------------------------------------------------- folding a poll ----
  private apply(response: unknown): void {
    this.consecutiveFailures.set(0);
    this.errorSignal.set(null);
    this.updatedSignal.set(new Date());
    this.stateSignal.set('live');

    const feed = toBackgroundJobFeed(response);
    this.hasMoreSignal.set(feed.hasMore);

    // A parked run is unchanged on most ticks. Writing the signal anyway would
    // re-render the panel and, worse, re-fire the bell's announcement effect
    // every 30 seconds.
    const digest = feed.jobs.map(j => `${j.id}|${j.statusLabel}|${j.needsAction}`).join('~');
    if (digest === this.lastDigest) return;

    this.lastDigest = digest;
    // Replaced wholesale, never merged: the response only contains what is still
    // parked, so a run that has been approved is simply absent. Drop-off is the
    // server's to decide, not something the client reconciles.
    this.jobsSignal.set(feed.jobs);
  }

  /**
   * Exponential backoff, and a hard stop.
   *
   * A dropped tick is not worth mentioning; five consecutive failures means the
   * endpoint is gone, and the loop stops rather than hammering it — the panel
   * shows the reason with a Retry. Poll failures are NEVER toasted: this runs
   * unattended in the background, and a toast for it would interrupt whatever
   * the user is actually doing to report something they did not ask about.
   */
  private handlePollError(error: unknown): Observable<unknown> {
    const failures = this.consecutiveFailures() + 1;
    this.consecutiveFailures.set(failures);

    if (failures >= JOB_MAX_POLL_FAILURES) {
      this.errorSignal.set(this.messageOf(error, 'Lost contact with the background jobs service'));
      this.stateSignal.set('error');
      // Rethrowing ends the retry chain; `pollEnabled` has already gone false on
      // the failure count, so nothing restarts it until the user asks.
      return throwError(() => error);
    }

    return timer(Math.min(JOB_POLL_ACTIVE_MS * 2 ** (failures - 1), JOB_POLL_BACKOFF_CAP_MS));
  }

  /**
   * A hidden tab must not poll — and on return it must not wait out a full 60s
   * before showing what happened while the user was away.
   */
  private watchVisibility(): void {
    this.documentVisible.set(document.visibilityState === 'visible');
    fromEvent(document, 'visibilitychange').pipe(
      takeUntilDestroyed(this.destroyRef),
    ).subscribe(() => {
      const visible = document.visibilityState === 'visible';
      this.documentVisible.set(visible);
      if (!visible) return;
      this.consecutiveFailures.set(0);
      this.refreshNow$.next();
    });
  }

  /**
   * The feed is environment-scoped, so a switch has to drop what is on screen
   * before the next response arrives — otherwise one environment's approvals
   * linger in the bell while the user is looking at another.
   */
  private watchEnvironment(): void {
    let seen = this.environmentService.current();
    effect(() => {
      const current = this.environmentService.current();
      if (current === seen) return;
      seen = current;
      this.reset();
      this.refreshNow$.next();
    });
  }

  // ------------------------------------------------------------- surface ----
  /** Re-read now, and clear a stopped loop's failure count so it re-arms. */
  refresh(): void {
    this.consecutiveFailures.set(0);
    this.errorSignal.set(null);
    this.refreshNow$.next();
  }

  /** Suspend the loop without signing out. */
  setEnabled(enabled: boolean): void {
    this.externallyEnabled.set(enabled);
    if (enabled) this.refreshNow$.next();
  }

  private reset(): void {
    this.jobsSignal.set([]);
    this.hasMoreSignal.set(false);
    this.errorSignal.set(null);
    this.updatedSignal.set(null);
    this.stateSignal.set('idle');
    this.lastDigest = ' ';
  }

  private messageOf(error: unknown, fallback: string): string {
    const e = error as { error?: { message?: string }; message?: string } | null;
    return e?.error?.message ?? e?.message ?? fallback;
  }
}
