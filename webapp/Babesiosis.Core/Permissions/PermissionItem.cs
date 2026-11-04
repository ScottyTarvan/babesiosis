using System;

namespace Babesiosis.Core.Permissions
{
  /// <summary>
  /// A single permission, declared in code by a static config class under
  /// <c>Babesiosis.Core/Permissions/Configs/</c> and discovered at startup by
  /// <c>PermissionsConfigService</c>.
  ///
  /// The triple (<see cref="Category"/>, <see cref="Group"/>,
  /// <see cref="Action"/>) is what the role-permissions screen renders as a
  /// breadcrumb — "Teams -> Role -> Edit". The <see cref="Id"/> is the stable
  /// identity: it is what a <c>team.RolePermissionItem</c> row stores and what
  /// <c>[RequiredPermission]</c> references. Once an Id ships it must never
  /// change, or every existing grant for it is silently lost.
  ///
  /// This is the new, code-declared permission model. It runs alongside — and
  /// deliberately does not replace — the legacy <c>team.Permission</c> subject/
  /// action rows that Babesiosis.Angular still runs off.
  /// </summary>
  public class PermissionItem
  {
    public Guid Id { get; set; }
    public string Category { get; set; }
    public string Group { get; set; }
    public PermissionAction Action { get; set; }

    /// <summary>
    /// When true, this permission is granted ONLY to super administrators.
    /// The ordinary administrator "grant-all" bypass does not cover it, and it
    /// cannot be obtained through role assignment. See UserPermissionItemsService.
    /// </summary>
    public bool SuperAdminOnly { get; set; }

    public override string ToString()
    {
      return $"{Category}: {Group}: {Action} [{Id}]";
    }
  }
}
