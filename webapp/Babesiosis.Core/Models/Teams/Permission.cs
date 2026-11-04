using System.Collections.Generic;
using Babesiosis.Core.Models.Domain;

namespace Babesiosis.Core.Models.Teams
{
  public class Permission : InstanceModel
  {
    public byte[] RowVersion { get; set; }
    public string Subject { get; set; }
    public string Action { get; set; }
    public string Description { get; set; }

    public virtual List<RolePermission> RolePermissions { get; set; }
  }
}
