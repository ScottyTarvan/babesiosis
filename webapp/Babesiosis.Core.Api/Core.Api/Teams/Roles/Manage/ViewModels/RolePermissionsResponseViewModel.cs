using Babesiosis.Core.ViewModels;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.ViewModels
{
  /// <summary>
  /// The role-permissions matrix: a category -> group -> action tree built from
  /// the declared permission configs, with the leaves the role currently holds
  /// flagged selected.
  ///
  /// The role name rides along so the drill-down page can render its header
  /// without a second call.
  /// </summary>
  public class RolePermissionsResponseViewModel
  {
    public string RoleName { get; set; }
    public PagedItemsViewModel<TreeItemViewModel> Page { get; set; } = new PagedItemsViewModel<TreeItemViewModel>();
    public Dictionary<string, bool> Permissions { get; set; } = new Dictionary<string, bool>();
  }
}
