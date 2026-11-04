import {
  JOB_POLL_ACTIVE_MS,
  JOB_POLL_IDLE_MS,
  jobPollDelayMs,
  toBackgroundJobFeed,
} from 'app/core/types/background-job';

/**
 * The two pure pieces of the background-jobs feature: the cadence rule, and the
 * fold from wire shape to the panel's contract. Neither needs a TestBed — which
 * is the point of keeping them out of the service.
 */
describe('background-job', () => {

  describe('jobPollDelayMs', () => {

    /**
     * The whole "don't poll when there's nothing to poll for" requirement lives
     * in this one function. An empty feed must back off to the slow discovery
     * tick, and anything parked must be watched at the faster one.
     */
    it('polls slowly while the feed is empty and faster once something is parked', () => {
      expect(jobPollDelayMs(0)).toBe(JOB_POLL_IDLE_MS);
      expect(jobPollDelayMs(1)).toBe(JOB_POLL_ACTIVE_MS);
      expect(jobPollDelayMs(12)).toBe(JOB_POLL_ACTIVE_MS);
    });

    /** A monitoring tick that was slower than the discovery tick would be a bug. */
    it('never monitors more slowly than it discovers', () => {
      expect(JOB_POLL_ACTIVE_MS).toBeLessThan(JOB_POLL_IDLE_MS);
    });
  });

  describe('toBackgroundJobFeed', () => {

    const wireJob = (overrides: Record<string, unknown> = {}) => ({
      jobId: '7f000001-0000-4000-8000-00000000a001',
      kind: { name: 'DatasetDeployment', value: 1 },
      status: { name: 'AwaitingApproval', value: 2 },
      action: { name: 'Deploy', value: 1 },
      datasetInstanceId: 'a1b2c3d4-0000-4000-8000-000000000001',
      datasetName: 'Client Positions',
      datasetType: { name: 'Entity', value: 1 },
      canAction: true,
      createdDate: '2026-08-24T09:12:00Z',
      ...overrides,
    });

    it('maps a row onto the panel contract', () => {
      const feed = toBackgroundJobFeed({ jobs: [wireJob()], hasMore: false });

      expect(feed.jobs.length).toBe(1);
      const job = feed.jobs[0];
      expect(job.id).toBe('7f000001-0000-4000-8000-00000000a001');
      expect(job.kind).toBe('dataset-deployment');
      expect(job.title).toBe('Client Positions');
      expect(job.subtitle).toBe('Deploy');
      expect(job.needsAction).toBeTrue();
      expect(job.target.datasetType).toBe(1);
      expect(job.createdAt instanceof Date).toBeTrue();
    });

    /**
     * `AwaitingApproval` must never reach a user's eyes as written. The label is
     * derived rather than mapped so a status added server-side degrades to
     * something readable instead of blank.
     */
    it('humanises the PascalCase status name', () => {
      const feed = toBackgroundJobFeed({ jobs: [wireJob()] });
      expect(feed.jobs[0].statusLabel).toBe('Awaiting approval');
    });

    /**
     * `canAction` decides whether the row is a link at all, so anything other
     * than an explicit `true` has to read as "not actionable" — a missing field
     * must not silently offer an action the server never granted.
     */
    it('treats a missing or non-true canAction as not actionable', () => {
      const feed = toBackgroundJobFeed({
        jobs: [
          wireJob({ canAction: false }),
          wireJob({ jobId: 'b', canAction: undefined }),
          wireJob({ jobId: 'c', canAction: null }),
        ],
      });

      expect(feed.jobs.map(j => j.needsAction)).toEqual([false, false, false]);
    });

    /** A row with no id has no key and no deep link, so it is dropped rather than rendered blank. */
    it('drops rows with no job id', () => {
      const feed = toBackgroundJobFeed({ jobs: [wireJob(), wireJob({ jobId: null })] });
      expect(feed.jobs.length).toBe(1);
    });

    /**
     * This runs on a timer against a response nobody is watching. A shape
     * surprise has to degrade the row, never throw inside the poll loop — a
     * throw there would trip the backoff and eventually stop the bell entirely.
     */
    it('survives null, junk and missing fields without throwing', () => {
      expect(toBackgroundJobFeed(null).jobs).toEqual([]);
      expect(toBackgroundJobFeed(undefined).jobs).toEqual([]);
      expect(toBackgroundJobFeed({}).jobs).toEqual([]);
      expect(toBackgroundJobFeed({ jobs: null }).jobs).toEqual([]);
      expect(toBackgroundJobFeed({ jobs: 'nonsense' }).jobs).toEqual([]);
      expect(toBackgroundJobFeed({ jobs: [null, undefined] }).jobs).toEqual([]);

      const sparse = toBackgroundJobFeed({ jobs: [{ jobId: 'x' }] });
      expect(sparse.jobs.length).toBe(1);
      expect(sparse.jobs[0].title).toBe('Untitled dataset');
      expect(sparse.jobs[0].subtitle).toBeNull();
      expect(sparse.jobs[0].statusLabel).toBe('—');
      expect(sparse.jobs[0].createdAt).toBeNull();
      expect(sparse.jobs[0].target.datasetId).toBeNull();
      expect(sparse.jobs[0].target.datasetType).toBeNull();
    });

    /** An unparseable date must be null, not an Invalid Date the template renders as NaN. */
    it('rejects an unparseable createdDate', () => {
      const feed = toBackgroundJobFeed({ jobs: [wireJob({ createdDate: 'not-a-date' })] });
      expect(feed.jobs[0].createdAt).toBeNull();
    });

    it('reports hasMore only when the server says so', () => {
      expect(toBackgroundJobFeed({ jobs: [], hasMore: true }).hasMore).toBeTrue();
      expect(toBackgroundJobFeed({ jobs: [] }).hasMore).toBeFalse();
      expect(toBackgroundJobFeed({ jobs: [], hasMore: 'yes' }).hasMore).toBeFalse();
    });
  });
});
