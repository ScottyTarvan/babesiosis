using System;

namespace Babesiosis.Core.Models.Teams
{
  public class RolePermission
  {
    public int RoleId { get; set; }
    public Guid PermissionId { get; set; }

    public virtual Role Role { get; set; }
    public virtual Permission Permission { get; set; }
  }
}
