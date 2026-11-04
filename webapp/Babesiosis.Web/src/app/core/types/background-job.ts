/**
 * The background-jobs feed — what the topbar bell shows.
 *
 * ## Why this lives in `core/` and knows nothing about routes
 *
 * The service that polls this feed is root-provided, so it must not depend on a
 * feature area. {@link BackgroundJob.target} therefore carries the dataset type
 * as the raw enum value rather than a url segment: turning that into
 * `/setup/datasets/entities/…` needs `datasetTypeRoute` from
 * `setup/datasets/datasets.types.ts`, and that resolution happens in the panel
 * component under `layout/`, which is allowed to import from a feature.
 *
 * ## Why the shape is generic
 *
 * v1 has one source. The contract is written as though it has several, because
 * the whole point of a "background jobs" bell is that a second source (pipeline
 * runs, file imports) is a new {@link BackgroundJobKind} plus a mapper — not a
 * reshaped UI. The panel reads only the fields below; it does no domain
 * reasoning of its own.
 */

import { parseUtcDate } from 'app/core/types/utc-date';

/** Which subsystem produced a job. The server stamps this; never infer it. */
export type BackgroundJobKind = 'dataset-deployment';

/** One row in the bell's dropdown. */
export interface BackgroundJob {
  /** Deployment run `InstanceId`. Row key, and the `?deployment=` value. */
  readonly id: string;
  readonly kind: BackgroundJobKind;
  /** Dataset name. */
  readonly title: string;
  /** The run's verb — "Deploy", "Delete", … Null when unresolvable. */
  readonly subtitle: string | null;
  /** Human-facing status text, resolved server-side of the enum. */
  readonly statusLabel: string;
  /**
   * Whether this user holds the permission gating control of this run. False
   * rows render muted and inert: visible, but not offered a link they cannot
   * use.
   */
  readonly needsAction: boolean;
  readonly createdAt: Date | null;
  /** Everything the panel needs to build a router link, and nothing more. */
  readonly target: {
    readonly datasetId: string | null;
    readonly datasetType: number | null;
  };
}

/** The feed as one poll saw it. */
export interface BackgroundJobFeed {
  readonly jobs: readonly BackgroundJob[];
  /** More jobs are waiting than the server's cap returned. */
  readonly hasMore: boolean;
}

// ------------------------------------------------------------------ cadence ----

/**
 * Discovery cadence — nothing is parked, so this tick only asks "has anything
 * appeared?". This is the floor the feature cannot go below: a browser cannot
 * observe a database insert without either a heartbeat like this one or a push
 * channel, and push is the documented later phase.
 */
export const JOB_POLL_IDLE_MS = 60_000;

/**
 * Monitoring cadence — something is parked and is being watched until it clears.
 *
 * Deliberately slower than the deployment log's 2s: a run held at
 * AwaitingApproval only moves when a *person* acts on it, so a fast tick buys
 * nothing but load. The same argument `POLLED_RUN_STATUSES` in
 * `setup/datasets/datasets.types.ts` makes for keeping AwaitingApproval out of
 * the datasets grid's poll entirely. 30s is the compromise: a second operator
 * approving something clears this user's badge within half a minute.
 */
export const JOB_POLL_ACTIVE_MS = 30_000;

export const JOB_POLL_BACKOFF_CAP_MS = 60_000;

/** Consecutive failures before the loop stops and the panel offers Retry. */
export const JOB_MAX_POLL_FAILURES = 5;

/**
 * The cadence rule, as a pure function so it can be asserted without a TestBed.
 *
 * Empty feed → discovery. Anything parked → monitor it until it drops off.
 */
export function jobPollDelayMs(jobCount: number): number {
  return jobCount === 0 ? JOB_POLL_IDLE_MS : JOB_POLL_ACTIVE_MS;
}

// ------------------------------------------------------------------ mapping ----

interface WireNameValue {
  name?: string | null;
  value?: number | null;
}

interface WireJob {
  jobId?: string | null;
  kind?: WireNameValue | null;
  status?: WireNameValue | null;
  action?: WireNameValue | null;
  datasetInstanceId?: string | null;
  datasetName?: string | null;
  datasetType?: WireNameValue | null;
  canAction?: boolean | null;
  createdDate?: string | null;
}

interface WireFeed {
  jobs?: readonly WireJob[] | null;
  hasMore?: boolean | null;
}

/**
 * Title Case for a PascalCase enum name — `AwaitingApproval` → `Awaiting
 * approval`. Used as the fallback when the server sends a member this build has
 * no label for, so a status added server-side degrades to something readable
 * rather than blank.
 */
function humanise(name: string | null | undefined): string {
  if (!name) return '—';
  const spaced = name.replace(/([a-z0-9])([A-Z])/g, '$1 $2');
  return spaced.charAt(0).toUpperCase() + spaced.slice(1).toLowerCase();
}

function toDate(value: string | null | undefined): Date | null {
  return parseUtcDate(value);
}

/**
 * Folds a `jobs-background-get` response into the feed.
 *
 * Defensive throughout, in the same spirit as `toDeploymentHeader`: this runs on
 * a timer against a response nobody is watching, so a shape surprise must
 * degrade a row rather than throw inside the poll loop and trip the backoff.
 */
export function toBackgroundJobFeed(source: unknown): BackgroundJobFeed {
  const wire = (source ?? {}) as WireFeed;
  const rows = Array.isArray(wire.jobs) ? wire.jobs : [];

  const jobs = rows
    .filter((row): row is WireJob => !!row && typeof row === 'object')
    .map(toBackgroundJob)
    .filter((job): job is BackgroundJob => job !== null);

  return { jobs, hasMore: wire.hasMore === true };
}

function toBackgroundJob(row: WireJob): BackgroundJob | null {
  // No id means no row key and no deep link — there is nothing useful to render.
  if (!row.jobId) return null;

  return {
    id: row.jobId,
    kind: 'dataset-deployment',
    title: row.datasetName || 'Untitled dataset',
    subtitle: row.action?.name ? humanise(row.action.name) : null,
    statusLabel: humanise(row.status?.name),
    needsAction: row.canAction === true,
    createdAt: toDate(row.createdDate),
    target: {
      datasetId: row.datasetInstanceId ?? null,
      datasetType: typeof row.datasetType?.value === 'number' ? row.datasetType.value : null,
    },
  };
}
