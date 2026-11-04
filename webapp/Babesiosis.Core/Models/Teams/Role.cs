using System.Collections.Generic;
using Babesiosis.Core.Models.Domain;

namespace Babesiosis.Core.Models.Teams
{
    public class Role : NameDescriptionModel
  {
    public byte[] RowVersion { get; set; }
    public bool IsDefault { get; set; }

    public virtual List<UserRole> UserRoles { get; set; }

    /// <summary>Legacy subject/action grants — read and written by Babesiosis.Angular.</summary>
    public virtual IEnumerable<RolePermission> Permissions { get; set; }

    /// <summary>
    /// Grants against the code-declared permission configs. Used by the new web
    /// application only; see <see cref="RolePermissionItem"/>.
    /// </summary>
    public virtual List<RolePermissionItem> PermissionItems { get; set; }
  }
}
