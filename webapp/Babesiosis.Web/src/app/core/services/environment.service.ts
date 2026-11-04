import { Injectable, signal } from '@angular/core';
import { toObservable } from '@angular/core/rxjs-interop';
import { EnvironmentType } from 'app/core/types/environment.type';

/**
 * The application-wide environment scope.
 *
 * Every environment-scoped endpoint (`pipeline-list-get`, `pipeline-log-list-get`,
 * the Manage / Setup / Analytics reads) filters on this, so it is a single
 * shared selection rather than per-screen state. Features inject this service
 * and read {@link current}.
 *
 * **The scope is fixed at DEV and there is no control that changes it.** The
 * top-bar environment switcher was removed; the per-environment grants on the legacy
 * `environments` subject went with it, since nothing reads them any more.
 *
 * The service itself stays because ~30 screens ask it what to put on the wire,
 * and because environment selection is expected to come back in some form —
 * when it does, this is where it lands, and every consumer is already reading
 * from it reactively. That is also why `current` is still a signal rather than
 * a constant: consumers that recompute on it keep working unchanged.
 */
@Injectable({ providedIn: 'root' })
export class EnvironmentService {

  private readonly _current = signal<EnvironmentType>(EnvironmentType.Dev);

  /** The environment every environment-scoped request is filtered by. */
  readonly current = this._current.asReadonly();

  /** Rx view of {@link current}, for consumers composing request pipelines. */
  readonly current$ = toObservable(this._current);
}
