import type { PermissionsViewModel } from 'app/core/viewmodels/permissions.viewmodel';

/**
 * The permissions **echo** contract — every capability key a controller can put
 * on a list/get response, in one place.
 *
 * ## Why this file exists
 *
 * The new permission model does not ship a login-time grant cache. Each screen
 * learns what its user may do from a `Dictionary<string, bool>` echoed on its
 * own read response, wrapped client-side in
 * {@link PermissionsViewModel}. That view model **stores only truthy entries**,
 * so `has('canEdit')` and `has('canEddit')` are indistinguishable at runtime:
 * a mistyped key silently disables a control forever, on every screen, for
 * every user — and nothing fails loudly enough to notice.
 *
 * So the strings are declared once, here, and screens import them instead of
 * typing quoted literals. `PermissionKey` is the union of every legal value; a
 * key that is not in this file is not a key the backend emits.
 *
 * ## Keeping it honest
 *
 * The authority for this list is the C# controllers, not this file —
 * specifically the `Permissions = new Dictionary<string, bool> { … }` block in
 * each of them (canonical example:
 * `Babesiosis.Core.Api/Core.Api/Setup/LinkedServices/Controllers/GetLinkedServiceListController.cs`).
 * Every entry below was transcribed from a controller that emits it. When a
 * controller gains a key, add it here in the same commit; when one is removed,
 * delete it here and the compiler will point at every screen that read it.
 *
 * ## Naming
 *
 * Wire keys are camelCase and always start with `can`. Property names are the
 * bare capability, so a screen reads `PERMISSION_KEYS.add` rather than
 * `'canAdd'`. Where two echoes disagree on a name for the same idea — role
 * members echo `canView` where everything else echoes `canRead` — both are
 * listed, because renaming one is a coordinated backend + frontend change and
 * is deliberately out of scope here (alignment-map R9).
 */
export const PERMISSION_KEYS = Object.freeze({
  // -------------------- Standard CRUD --------------------
  // Emitted by nearly every echo: linked services, file uploads / downloads,
  // event triggers and their parameters, entity groups, dataset fields /
  // indexes, dataset lists, users, roles, pipelines.
  /** May load the screen at all. A false `canRead` blocks the page, not a button. */
  read: 'canRead',
  add: 'canAdd',
  edit: 'canEdit',
  delete: 'canDelete',

  // -------------------- Dataset lifecycle --------------------
  /**
   * `setup-datasets-get`, `setup-datasets-hub-get`, deployment log — and
   * `setup-linked-service-list-get`, which echoes it for the Import Reference
   * Lists row action. That action provisions and deploys Reference datasets, so
   * it is gated on the Reference type's Deploy grant rather than on any
   * linked-service grant.
   */
  deploy: 'canDeploy',
  /**
   * `setup-linked-service-list-get` — the Remove Reference Lists row action, which drops the
   * tables an import built.
   *
   * Its own key rather than `delete`, which on that same echo is the LINKED SERVICE's delete
   * grant: a user may be allowed to delete a linked service and not to destroy the platform's
   * reference tables inside it, or the reverse. Backed by the Reference type's delete
   * permission, the same one `RemoveSystemDatasets` asserts.
   */
  removeReferenceLists: 'canRemoveReferenceLists',
  /** Link Table / Continue Link / Resume Link. Distinct from `add` on purpose. */
  link: 'canLink',
  /** Detaches metadata, leaves the physical table standing. Distinct from `delete`. */
  unlink: 'canUnlink',
  /** Dataset JSON import. No longer borrows `canAdd`. */
  import: 'canImport',
  /**
   * Dataset JSON export, manage-data grid export, deployment task-log export.
   * Also emitted by: `manage-event-triggers-get`, `manage-file-uploads-get`,
   * `manage-file-downloads-get`, `teams-role-list-get`, `teams-user-list-get`
   * (grid Export button on those screens, gated to Download grant as of 2026-09-21).
   */
  export: 'canExport',
  /**
   * `setup-datasets-deployments-get` — the deployment log's row Delete, which purges one
   * run out of the history along with its plan steps and their logs.
   *
   * Its own key rather than `delete`, which on that same echo is the dataset TYPE's delete
   * grant and already gates approving a Delete run. Erasing the record that a dataset was
   * deleted and deleting one are separate authorities, and the two keys read almost the
   * same — which is exactly why they must not share one. Backed by
   * `SetupPermissions.DatasetDeploymentDelete`.
   */
  deleteLog: 'canDeleteLog',

  // -------------------- File movement --------------------
  /** `manage-file-uploads-get` — push a file into a drop point. */
  upload: 'canUpload',
  /** `manage-file-downloads-get` / `-get-files` — browse and pull a pick-up point. */
  download: 'canDownload',

  // -------------------- Operator actions --------------------
  /** `manage-event-triggers-get` — fire an activator. */
  run: 'canRun',
  /** `manage-datasets-get` / `manage-data-get` — open and work the data grid. */
  manage: 'canManage',
  /**
   * `manage-data-get` / `manage-data-audit-get` — read the audit trail of manual
   * edits. Its own grant per dataset type (`<type>-data-audit`), never implied by
   * `manage`.
   */
  viewAudit: 'canViewAudit',

  // -------------------- Navigation into a second screen --------------------
  /** `setup-entity-groups-get` — open the builder from the list row. */
  openDesigner: 'canOpenDesigner',
  /** `setup-event-triggers-get` — expand the nested parameters grid. */
  readParameters: 'canReadParameters',
  /** `setup-datasets-hub-get` — sidebar link to the deployment log. */
  readDeploymentLog: 'canReadDeploymentLog',

  // -------------------- Dataset hub sub-resources --------------------
  // The hub echo carries the whole tab strip in one response so the strip can
  // render disabled tabs before any tab has loaded. Each tab's own read echo
  // repeats the same grants under the plain CRUD names above.
  readFields: 'canReadFields',
  addFields: 'canAddFields',
  editFields: 'canEditFields',
  deleteFields: 'canDeleteFields',
  readKeys: 'canReadKeys',
  editKeys: 'canEditKeys',
  readIndexes: 'canReadIndexes',
  addIndexes: 'canAddIndexes',
  editIndexes: 'canEditIndexes',
  deleteIndexes: 'canDeleteIndexes',
  /** Deployment (assets) tab — generated DDL/script disclosure. */
  readAssets: 'canReadAssets',
  /** Validations **and** Diagnostics tabs — one grant covers both. */
  readDiagnostics: 'canReadDiagnostics',

  // -------------------- Reports --------------------
  // The reports area is served by a separate function app
  // (`Babesiosis.Reports.Functions`) whose get controllers echo these
  // alongside the standard CRUD keys above. Source of truth: the mapping table
  // in `.claude/specs/reports-migration-plan.md` §6, and the mock handlers
  // under `src/app/_mocks/handlers/reports-*.mock.ts` which already emit them.
  /** `reports-setup-schedules-get` — archive **and** restore. One grant covers
   *  both directions: they are the same capability pointed two ways, and the
   *  legacy screen asserted `delete` for each. */
  archive: 'canArchive',
  /** `reports-setup-component-entities-get` — include/exclude an entity or
   *  element on a component. The command carries the desired state (plan D5),
   *  so one grant covers both directions. */
  toggle: 'canToggle',
  /** `reports-setup-component-<family>-get` — drag-reorder the element rows. */
  reorder: 'canReorder',
  /** `reports-run-report-instances-get` — open the rendered PDF.
   *  Independently grantable: it derives from its own `InstancePreview`
   *  PermissionItem, not from instance read (user decision 2026-08-15). The
   *  versions dialog's View reads the same key rather than the `read` the
   *  legacy screen used there, so one row action means one thing. */
  preview: 'canPreview',
  // Navigation into a second reports screen, all echoed on `reports-setup-get`
  // so the list's row actions can render disabled before any of them loads.
  viewSchedules: 'canViewSchedules',
  /** `reports-setup-get` — through to the report's Groups screen (Report Read). */
  viewGroups: 'canViewGroups',
  viewComponents: 'canViewComponents',
  /** `reports-setup-get` — the fourth row action, through to Report ▸ Distribution
   *  (`.claude/specs/report-distribution-channels.md` §8). */
  viewDistribution: 'canViewDistribution',
  /**
   * `reports-setup-distribution-get` — whether the caller may also see the
   * channel CATALOGUE behind the assignments.
   *
   * Distinct from `read`, which on that same echo is the report's own
   * distribution list: a user may be allowed to see which channels a report
   * delivers through without being allowed to browse every configured
   * destination in the environment.
   */
  readChannels: 'canReadChannels',
  /** `reports-run-reports-get` — row link through to the instances screen. */
  viewInstances: 'canViewInstances',
  /**
   * `reports-run-reports-get` — the run card's Schedule button
   * (`.claude/specs/report-run-schedules-plan.md` §5.3).
   *
   * Its own key rather than `add`, which that echo does not carry: creating a
   * recurrence rule for a report is a `run-schedule` grant, while everything
   * else on the run deck is a `reporting-run-report` one.
   */
  schedule: 'canSchedule',
  /**
   * `reports-run-schedules-get` — the list's Run Now row action.
   *
   * Distinct from `edit` on the same echo: Run Now is backed by the report's
   * RUN grant, not by any schedule grant, so a user may be allowed to change
   * when a report runs without being allowed to make it run — and the reverse.
   */
  runNow: 'canRunNow',
  /** `reports-distribute-*-get` — approve / revoke a Pending or Approved document. */
  approve: 'canApprove',
  /** `reports-distribute-*-get` — distribute an Approved document. */
  distribute: 'canDistribute',
  // `reports-content-manage-get` — the content hub's header echo, one key per
  // panel type so the tabs can gate before any panel loads, plus the pdf
  // download. Per-element echoes on the panel gets reuse the standard
  // `canEdit`/`canDownload` keys above.
  editColours: 'canEditColours',
  editCommentary: 'canEditCommentary',
  editImages: 'canEditImages',
  editPdfs: 'canEditPdfs',
  downloadPdfs: 'canDownloadPdfs',

  // -------------------- Teams / pipelines --------------------
  /** `teams-role-members-get` only. Everything else spells this `canRead` (R9). */
  view: 'canView',
  /** `teams-role-list-get` — row shield → the role's permission matrix. */
  viewPermissions: 'canViewPermissions',
  /** `teams-role-list-get` — row users icon → the role's members. */
  manageMembers: 'canManageMembers',
  /**
   * `teams-role-members-get` — whether the caller may also browse the USER
   * DIRECTORY behind the member picker.
   *
   * Distinct from `view`, which on that same echo is the role's own member
   * list: a user may be allowed to see who is in a role without being allowed
   * to browse every user in the environment.
   */
  readUsers: 'canReadUsers',
  /**
   * `teams-user-list-get` — setting or clearing a user's `IsAdministrator`
   * flag.
   *
   * Its own key rather than `edit`, which on that same echo is the ordinary
   * user-edit grant: promoting someone to administrator confers every
   * permission in the system at once, and a user allowed to correct a phone
   * number should not thereby be allowed to do that.
   */
  elevate: 'canElevate',
  viewRoles: 'canViewRoles',
  editRoles: 'canEditRoles',
  /** `pipeline-list-get` — reach the pipeline logs screen. */
  viewLogs: 'canViewLogs',
  /** `pipeline-expectation-list-get`, `pipeline-expectation-event-list-get` —
   *  mark a breach event as seen. Its own `ExpectationAcknowledge` item, so a
   *  user may be allowed to acknowledge without being allowed to edit the rule. */
  acknowledge: 'canAcknowledge',
  /** `dataset-expectation-list` — manual manifest republish. Its own key rather
   *  than `edit`, though it is currently backed by the same `DatasetExpectationEditId`
   *  grant server-side (`GetDatasetExpectationsController`) — kept distinct because the
   *  two actions read differently on the tab and could diverge later. */
  publish: 'canPublish',

  // -------------------- Platform / MCP --------------------
  /** `platform-mcp-tokens-search` — Generate a personal access token (MCP Access grant). */
  create: 'canCreate',
  /** `platform-mcp-tokens-search` — revoke one's own token. Sign-in only, so always true;
   *  a row is revocable only while its status is Active. */
  revoke: 'canRevoke',
} as const);

/** Property names of {@link PERMISSION_KEYS} — the capability, not the wire key. */
export type PermissionKeyName = keyof typeof PERMISSION_KEYS;

/**
 * Every capability key the backend echoes. Anything outside this union is a
 * typo, and a typo reads as "denied" forever.
 */
export type PermissionKey = (typeof PERMISSION_KEYS)[PermissionKeyName];

/** Flat list of the legal wire keys — handy for mocks and parity assertions. */
export const PERMISSION_KEY_LIST: readonly PermissionKey[] =
  Object.freeze(Object.values(PERMISSION_KEYS) as PermissionKey[]);

/** Narrowing guard for values that arrive as plain strings (mocks, wire payloads). */
export function isPermissionKey(value: string): value is PermissionKey {
  return (PERMISSION_KEY_LIST as readonly string[]).includes(value);
}

/**
 * Read one capability off an echo that may not have arrived yet.
 *
 * A screen that has not loaded reads as **fully denied** — never as permitted —
 * so an action can't flash enabled during the first request. Equivalent to the
 * `this.permissions()?.has(key) ?? false` that every screen writes by hand;
 * use whichever reads better at the call site.
 */
export function hasPermission(
  permissions: PermissionsViewModel | null | undefined,
  key: PermissionKey,
): boolean {
  return permissions?.has(key) ?? false;
}

/**
 * The tooltip on a control that is disabled for want of a grant.
 *
 * Denied actions are **disabled, never hidden** — a user has to be able to see
 * that the capability exists and ask for it. Matches the legacy
 * `title="No Permission"` hover the migration is reproducing.
 */
export const NO_PERMISSION_TOOLTIP = 'No Permission';

/**
 * The same message for a disabled `<fs-data-grid>` overflow-menu item.
 *
 * Menu items take a `hint` rather than a tooltip: a natively disabled button
 * swallows pointer events, so `fsTooltip` never fires on one.
 */
export const NO_PERMISSION_HINT = 'You do not have permission';

/** `label` when permitted, the "No Permission" tooltip when not. */
export function permissionTooltip(allowed: boolean, label: string): string {
  return allowed ? label : NO_PERMISSION_TOOLTIP;
}

/**
 * The `hint` for a grid menu item: absent when permitted, the standard denial
 * message when not. Returns `undefined` rather than `''` so it can be spread
 * straight onto an `FsGridMenuItem`.
 */
export function permissionHint(allowed: boolean): string | undefined {
  return allowed ? undefined : NO_PERMISSION_HINT;
}
