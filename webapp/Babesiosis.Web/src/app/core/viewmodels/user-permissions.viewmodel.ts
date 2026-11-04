/**
 * UserPermissionsViewModel — the coarse `canView*` navigation flags that ship
 * with the authenticated user, one per permission category.
 * Mirrors the backend `Babesiosis.Core.ViewModels.UserPermissionsViewModel`.
 *
 * These decide which modules the shell offers, nothing more. Screens are gated
 * by the `permissions` echo their own read response carries
 * (`PermissionsViewModel` + `app/core/permissions/permission-keys`), computed
 * server-side from the code-declared `PermissionItem` catalogue.
 *
 * The flat subject/action grant list and the `can(subject, action)` check that
 * used to live here were the last of the client-side ability model; they were
 * removed once every screen had moved onto its endpoint's echo.
 */
export class UserPermissionsViewModel {
  canViewManage = false;
  canViewPipelines = false;
  canViewReporting = false;
  canViewSetup = false;
  canViewTeams = false;
  /** Data Health Dashboard: Read or Edit — the `/health` sidebar entry (health.md §3.12). */
  canViewDataHealth = false;
  /** Data Health Collector Settings: Read or Edit — the Setup › Statistics entry (settings §3.7). */
  canViewStatistics = false;

  constructor(userPermissions?: UserPermissionsViewModel | Partial<UserPermissionsViewModel>) {
    this.canViewManage = userPermissions?.canViewManage ?? false;
    this.canViewPipelines = userPermissions?.canViewPipelines ?? false;
    this.canViewReporting = userPermissions?.canViewReporting ?? false;
    this.canViewSetup = userPermissions?.canViewSetup ?? false;
    this.canViewTeams = userPermissions?.canViewTeams ?? false;
    this.canViewDataHealth = userPermissions?.canViewDataHealth ?? false;
    this.canViewStatistics = userPermissions?.canViewStatistics ?? false;
  }
}
