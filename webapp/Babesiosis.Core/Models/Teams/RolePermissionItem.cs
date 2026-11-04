namespace Babesiosis.Core.Models.Teams
{
  /// <summary>
  /// A grant of one code-declared <c>PermissionItem</c> to a role.
  ///
  /// This is deliberately a separate table from <see cref="RolePermission"/>:
  /// that one keys on the integer id of a <c>team.Permission</c> row and is what
  /// the legacy application reads and writes. The new permission model has no
  /// permission table at all — <see cref="PermissionId"/> is the GUID declared
  /// in a config class under <c>Babesiosis.Core/Permissions/Configs/</c> — so
  /// it could not be stored there without changing the legacy primary key.
  /// </summary>
  public class RolePermissionItem
  {
    public int RoleId { get; set; }
    public System.Guid PermissionId { get; set; }

    public virtual Role Role { get; set; }
  }
}
