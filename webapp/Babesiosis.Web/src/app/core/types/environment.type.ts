/**
 * The deployment environment every environment-scoped endpoint is filtered by.
 *
 * This is an application-wide concept, not a pipelines one — roughly 50 backend
 * commands across Manage, Setup, Search and Lookup carry
 * an `EnvironmentType`. It lives in `core` so the root-provided
 * {@link EnvironmentService} can own it without importing from a feature area.
 *
 * Mirrors `Babesiosis.Core.Models.Domain.EnvironmentType`. The numeric values
 * are the wire contract.
 */
export enum EnvironmentType {
  None = 0,
  Dev = 1,
  Uat = 2,
  PreProd = 3,
  Prod = 4,
}

/** Labels come from the backend enum's `[Description]` attributes. */
export const ENVIRONMENT_LABELS: ReadonlyMap<EnvironmentType, string> = new Map([
  [EnvironmentType.Dev, 'DEV'],
  [EnvironmentType.Uat, 'UAT'],
  [EnvironmentType.PreProd, 'PRE-PROD'],
  [EnvironmentType.Prod, 'PROD'],
]);

/**
 * Declaration order. The per-environment permission constants that used to live
 * here (`ENVIRONMENT_PERMISSION_ACTIONS`, `ENVIRONMENTS_PERMISSION_SUBJECT`)
 * went with the top-bar environment switcher — they existed only to gate its
 * segments against the legacy `environments` subject, and the scope is now
 * fixed at DEV. See `EnvironmentService`.
 */
export const ENVIRONMENT_ORDER: readonly EnvironmentType[] = [
  EnvironmentType.Dev,
  EnvironmentType.Uat,
  EnvironmentType.PreProd,
  EnvironmentType.Prod,
];
