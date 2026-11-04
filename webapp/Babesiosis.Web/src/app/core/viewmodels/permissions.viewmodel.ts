import type { PermissionKey } from 'app/core/permissions/permission-keys';

/**
 * The capability echo a screen received with its own data.
 *
 * The new permission model has no login-time grant cache: each list/get
 * response carries a `Dictionary<string, bool>` computed server-side from the
 * caller's grants against the code-declared `PermissionItem` catalogue, and the
 * UI never reasons about permissions itself — it reads flags.
 *
 * ## Only truthy entries are kept
 *
 * A `false` and an absent key are stored identically, so {@link has} cannot
 * tell "the server said no" from "nobody ever emits that key". A mistyped key
 * therefore disables its control permanently and silently. That is the reason
 * {@link PermissionKey} exists: pass keys from
 * `app/core/permissions/permission-keys`, not quoted literals.
 *
 * ## An absent echo is a denial
 *
 * A screen that has not loaded yet holds no view model at all. Call sites read
 * `this.permissions()?.has(key) ?? false` (or `hasPermission(...)` from the key
 * module) so a control is denied until the server has actually said otherwise —
 * never enabled optimistically for the length of the first request.
 */
export class PermissionsViewModel {

  permissions: Map<string, boolean> = new Map();

  constructor(permissions?: Map<string, boolean> | Record<string, boolean> | null) {
    this.permissions = new Map();
    if (!permissions) {
      return;
    }
    const entries: Iterable<[string, boolean]> =
      permissions instanceof Map ? permissions.entries() : Object.entries(permissions);
    for (const [key, value] of entries) {
      if (value) {
        this.permissions.set(key, true);
      }
    }
  }

  /**
   * True when the echo granted this capability.
   *
   * The parameter is `PermissionKey` and NOT widened. It used to be
   * `PermissionKey | (string & {})`, which made every string assignable and so
   * defeated the whole point of the registry — `has('canEddit')` compiled, and a
   * mistyped key disables its control permanently and silently (see above). The
   * widening was there for call sites that build their key through a lookup map,
   * but every such map in the tree is itself built from `PERMISSION_KEYS`
   * members and therefore already indexes to `PermissionKey`.
   *
   * If a genuinely dynamic string ever needs looking up, add an explicit
   * `hasUnchecked(key: string)` rather than re-widening this one, so the unsafe
   * path is visible in review.
   */
  has(key: PermissionKey): boolean {
    return this.permissions.has(key);
  }
}
