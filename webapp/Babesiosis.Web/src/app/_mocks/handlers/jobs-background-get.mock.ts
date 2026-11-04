import { MockRegistration } from 'app/_mocks/mock-handler';

/**
 * `jobs-background-get` — the topbar bell's feed.
 *
 * The real endpoint returns every deployment run parked at AwaitingApproval that
 * this user may read. Under approval-always that is every run in flight, which
 * is why the bell exists at all.
 *
 * **The mock is a scripted sequence, not a fixed payload.** The whole feature is
 * a state machine over time — quiet, then something arrives, then it clears —
 * and a static response can only ever demonstrate one frame of it. Successive
 * calls walk the script below and then hold on the last step, so the bell can be
 * watched going red and clearing again without touching a database. At the
 * mock's own 60s/30s cadence that is slow to observe; click the panel's refresh
 * button to step it by hand.
 */
interface WireJob {
  jobId: string;
  kind: { name: string; value: number };
  status: { name: string; value: number };
  action: { name: string; value: number };
  datasetInstanceId: string;
  datasetName: string;
  datasetType: { name: string; value: number };
  canAction: boolean;
  createdDate: string;
}

interface WireFeed {
  jobs: WireJob[];
  count: number;
  hasMore: boolean;
}

/** `BackgroundJobKind.DatasetDeployment`. */
const DEPLOYMENT_KIND = { name: 'DatasetDeployment', value: 1 };
/** `DatasetDeploymentStatus.AwaitingApproval`. */
const AWAITING = { name: 'AwaitingApproval', value: 2 };
const DEPLOY = { name: 'Deploy', value: 1 };
const DELETE = { name: 'Delete', value: 3 };
/** `DatasetType.Entity` / `DatasetType.Fact` — Fact's route slug is `data-tables`. */
const ENTITY = { name: 'Entity', value: 1 };
const FACT = { name: 'Fact', value: 4 };

function job(overrides: Partial<WireJob> & Pick<WireJob, 'jobId' | 'datasetName'>): WireJob {
  return {
    kind: DEPLOYMENT_KIND,
    status: AWAITING,
    action: DEPLOY,
    datasetInstanceId: 'a1b2c3d4-0000-4000-8000-000000000001',
    datasetType: ENTITY,
    canAction: true,
    createdDate: '2026-08-24T09:12:00Z',
    ...overrides,
  };
}

const CLIENT_POSITIONS = job({
  jobId: '7f000001-0000-4000-8000-00000000a001',
  datasetName: 'Client Positions',
  datasetInstanceId: 'a1b2c3d4-0000-4000-8000-000000000001',
});

const TRADE_LEDGER = job({
  jobId: '7f000001-0000-4000-8000-00000000a002',
  datasetName: 'Trade Ledger',
  datasetInstanceId: 'a1b2c3d4-0000-4000-8000-000000000002',
  datasetType: FACT,
  action: DELETE,
  createdDate: '2026-08-24T09:31:00Z',
});

/**
 * Not actionable by this user: it renders muted, inert and without a link, which
 * is the one row state a happy-path fixture would never produce.
 */
const HR_DATA = job({
  jobId: '7f000001-0000-4000-8000-00000000a003',
  datasetName: 'HR Headcount',
  datasetInstanceId: 'a1b2c3d4-0000-4000-8000-000000000003',
  canAction: false,
  createdDate: '2026-08-24T09:44:00Z',
});

const SCRIPT: WireJob[][] = [
  [],                                            // quiet — bell absent
  [CLIENT_POSITIONS],                            // one arrives — bell goes red, badge 1
  [CLIENT_POSITIONS, TRADE_LEDGER, HR_DATA],     // backlog, including one inert row
  [TRADE_LEDGER],                                // two approved elsewhere — badge drops
  [],                                            // cleared — bell disappears again
];

let step = 0;

export const jobsBackgroundGetMock: MockRegistration<unknown, WireFeed> = {
  route: 'jobs-background-get',
  handler: () => {
    const jobs = SCRIPT[Math.min(step, SCRIPT.length - 1)];
    step += 1;

    return { jobs, count: jobs.length, hasMore: false };
  },
};
