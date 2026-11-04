import { provideHttpClient, withXhr } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed, fakeAsync, tick } from '@angular/core/testing';
import { BehaviorSubject } from 'rxjs';
import { AuthService } from 'app/core/services/auth.service';
import { BackgroundJobsService } from 'app/core/services/background-jobs.service';
import { ConfigurationService } from 'app/core/services/configuration.service';
import { JOB_POLL_ACTIVE_MS, JOB_POLL_IDLE_MS } from 'app/core/types/background-job';

/**
 * The parts of the poll loop that only exist over time: when it starts, how fast
 * it ticks, when it stops. The cadence *rule* is asserted purely in
 * `background-job.spec.ts`; this asserts the loop actually obeys it.
 */
describe('BackgroundJobsService', () => {

  const ROUTE = '/api/core/jobs-background-get';

  let http: HttpTestingController;
  let user$: BehaviorSubject<unknown>;

  function job(id = 'job-1') {
    return {
      jobId: id,
      kind: { name: 'DatasetDeployment', value: 1 },
      status: { name: 'AwaitingApproval', value: 2 },
      action: { name: 'Deploy', value: 1 },
      datasetInstanceId: 'ds-1',
      datasetName: 'Client Positions',
      datasetType: { name: 'Entity', value: 1 },
      canAction: true,
      createdDate: '2026-08-24T09:12:00Z',
    };
  }

  /** Answers the one pending request, if there is one. Returns whether there was. */
  function respond(jobs: unknown[]): boolean {
    const pending = http.match(ROUTE);
    if (!pending.length) return false;
    pending[0].flush({ jobs, count: jobs.length, hasMore: false });
    return true;
  }

  function create(): BackgroundJobsService {
    const service = TestBed.inject(BackgroundJobsService);
    // The loop is gated on document visibility. Karma's browser is normally
    // visible, but asserting that from a spec would make it depend on how the
    // runner was launched — so it is pinned explicitly.
    (service as unknown as { documentVisible: { set(v: boolean): void } })
      .documentVisible.set(true);
    TestBed.tick();
    return service;
  }

  beforeEach(() => {
    user$ = new BehaviorSubject<unknown>(null);

    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withXhr()),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: { user$, isAuthenticated: true } },
        { provide: ConfigurationService, useValue: { coreAPI: (u: string) => `/api/core${u}` } },
      ],
    });

    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    http.verify({ ignoreCancelled: true });
  });

  /**
   * The bell belongs to a session. Polling before anyone has signed in would
   * fire an unauthenticated request on every page load of the login screen.
   */
  it('does not poll until a user is signed in', fakeAsync(() => {
    create();

    tick(JOB_POLL_IDLE_MS * 2);
    http.expectNone(ROUTE);

    user$.next({ instanceId: 'u1' });
    TestBed.tick();

    expect(respond([])).toBeTrue();
    discardLoop();
  }));

  /**
   * The requirement in one test: an empty feed must not tick at the fast rate.
   * Getting this wrong doubles or triples the request volume of every idle
   * session in the product.
   */
  it('polls at the idle cadence while nothing is parked', fakeAsync(() => {
    const service = create();
    user$.next({ instanceId: 'u1' });
    TestBed.tick();
    respond([]);

    expect(service.count()).toBe(0);

    // Just short of the idle interval: still nothing.
    tick(JOB_POLL_IDLE_MS - 1);
    http.expectNone(ROUTE);

    tick(1);
    expect(respond([])).toBeTrue();
    discardLoop();
  }));

  /**
   * Once something is parked the loop escalates and monitors it — this is the
   * "then watch that entry until it completes" half of the rule.
   */
  it('escalates to the active cadence once something is parked', fakeAsync(() => {
    const service = create();
    user$.next({ instanceId: 'u1' });
    TestBed.tick();
    respond([job()]);

    expect(service.count()).toBe(1);

    tick(JOB_POLL_ACTIVE_MS - 1);
    http.expectNone(ROUTE);

    tick(1);
    expect(respond([job()])).toBeTrue();
    discardLoop();
  }));

  /**
   * Drop-off is server-authoritative: an approved run is simply absent from the
   * next response. The client must not hold on to it.
   */
  it('drops a job when the server stops returning it, and falls back to idle', fakeAsync(() => {
    const service = create();
    user$.next({ instanceId: 'u1' });
    TestBed.tick();
    respond([job()]);
    expect(service.count()).toBe(1);

    tick(JOB_POLL_ACTIVE_MS);
    respond([]);
    expect(service.count()).toBe(0);

    // Back to discovery: nothing at the active interval.
    tick(JOB_POLL_ACTIVE_MS);
    http.expectNone(ROUTE);

    tick(JOB_POLL_IDLE_MS - JOB_POLL_ACTIVE_MS);
    expect(respond([])).toBeTrue();
    discardLoop();
  }));

  /**
   * Signing out has to empty the bell immediately — leaving one user's pending
   * approvals on screen for the next one is a disclosure, not just a stale view.
   */
  it('stops polling and clears the feed on sign-out', fakeAsync(() => {
    const service = create();
    user$.next({ instanceId: 'u1' });
    TestBed.tick();
    respond([job()]);
    expect(service.count()).toBe(1);

    user$.next(null);
    TestBed.tick();

    expect(service.count()).toBe(0);
    expect(service.state()).toBe('idle');

    tick(JOB_POLL_IDLE_MS * 2);
    http.expectNone(ROUTE);
  }));

  /** A hidden tab is a tab nobody is looking at; polling it is pure waste. */
  it('suspends while the document is hidden', fakeAsync(() => {
    const service = create();
    user$.next({ instanceId: 'u1' });
    TestBed.tick();
    respond([]);

    (service as unknown as { documentVisible: { set(v: boolean): void } })
      .documentVisible.set(false);
    TestBed.tick();

    tick(JOB_POLL_IDLE_MS * 2);
    // Asserted through `match` rather than `expectNone`: the latter throws on
    // failure but registers no expectation, so the spec would pass silently if
    // the body ever stopped exercising the gate at all.
    expect(http.match(ROUTE).length).toBe(0);
  }));

  /**
   * fakeAsync fails a test that ends with a timer still queued, and this loop is
   * designed never to stop on its own. Cancelling the session is how a real
   * consumer ends it, so it is how the specs end too.
   */
  function discardLoop(): void {
    user$.next(null);
    TestBed.tick();
  }
});
