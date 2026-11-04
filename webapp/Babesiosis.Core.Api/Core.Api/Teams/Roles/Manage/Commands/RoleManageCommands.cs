using Babesiosis.Core.Api.Teams.Roles.ViewModels;
using Babesiosis.Core.ViewModels;
using DevExtreme.AspNet.Data;
using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Commands
{
  /// <summary>Server-mode grid load for the roles list.</summary>
  public class GetRoleListCommand
  {
    public DataSourceLoadOptionsBase LoadOptions { get; set; }
  }

  /// <summary>
  /// Create / update payload. Reuses the existing
  /// <see cref="RoleViewModel"/> row shape — the new web application sends the
  /// same fields, so a second near-identical view model would only drift.
  /// </summary>
  public class RoleItemCommand
  {
    public RoleViewModel Role { get; set; }
  }

  /// <summary>
  /// The full permission tree as the user left it. Only leaf nodes carry a
  /// permission id; intermediate nodes are folder rows and are ignored.
  /// </summary>
  public class UpdateRolePermissionsCommand
  {
    public Guid RoleId { get; set; }
    public List<TreeItemViewModel> Permissions { get; set; } = new List<TreeItemViewModel>();
  }

  /// <summary>Assign or remove a single user on a role. Committed immediately.</summary>
  public class RoleMemberCommand
  {
    public Guid RoleId { get; set; }
    public Guid MemberId { get; set; }
  }
}
