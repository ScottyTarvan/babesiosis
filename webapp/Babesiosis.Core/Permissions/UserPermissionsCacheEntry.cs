using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Permissions
{
  /// <summary>
  /// The cached record for one user's permission grants — the payload stored in
  /// Blob Storage and mirrored in the per-instance L1 cache in front of it.
  ///
  /// This is deliberately NOT the resolved permission set. It holds the raw
  /// facts a SQL query would answer with, so the effective set can be resolved
  /// at read time against whatever the declared permission catalogue
  /// (<see cref="Babesiosis.Core.Services.IPermissionsConfigService.GetPermissions"/>)
  /// looks like right now — a deployment that adds a permission item needs no
  /// re-login. See <c>UserPermissionsCacheServiceBase.Resolve</c> for the rule
  /// this record is resolved through.
  /// <para>
  /// Plain settable properties, not a positional record, so
  /// <c>System.Text.Json</c> round-trips it without a custom converter.
  /// </para>
  /// </summary>
  public class UserPermissionsCacheEntry
  {
    /// <summary>
    /// False for an unknown or deleted user. Every other field is meaningless
    /// when this is false — the resolved permission set is empty regardless.
    /// </summary>
    public bool Exists { get; set; }

    public bool IsAdministrator { get; set; }

    public bool IsSuperAdministrator { get; set; }

    /// <summary>
    /// Permission ids granted through <c>team.UserRole</c> joined to
    /// <c>team.RolePermissionItem</c>.
    /// </summary>
    public HashSet<Guid> GrantedIds { get; set; } = new HashSet<Guid>();

    /// <summary>When this record was last loaded from SQL.</summary>
    public DateTimeOffset RefreshedAtUtc { get; set; }
  }
}
