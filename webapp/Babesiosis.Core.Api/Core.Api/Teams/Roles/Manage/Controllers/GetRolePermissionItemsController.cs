using Babesiosis.Core.Api.Teams.Roles.Manage.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Commands;
using Babesiosis.Core.Data;
using Babesiosis.Core.Permissions;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  /// <summary>
  /// Builds the role-permissions matrix from the declared permission catalogue
  /// rather than from a database table — the catalogue is the source of truth,
  /// so a permission added in code shows up here on the next deployment with no
  /// data migration.
  /// </summary>
  public class GetRolePermissionItemsController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IPermissionsConfigService _permissionsConfigService;
    private readonly IUserPermissionItemsService _userPermissionsService;

    public GetRolePermissionItemsController(IDbContextService dbContextService,
      IPermissionsConfigService permissionsConfigService,
      IUserPermissionItemsService userPermissionsService)
    {
      _dbContextService = dbContextService;
      _permissionsConfigService = permissionsConfigService;
      _userPermissionsService = userPermissionsService;
    }

    public async Task<RolePermissionsResponseViewModel> HandleCommand(Guid userId, ActionItemCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var role = await dbContext.Roles
        .FirstOrDefaultAsync(r => r.InstanceId == command.ItemId);

      Assertion.IsNotNull(role, "Role", "Role does not exist");

      var granted = await dbContext.RolePermissionItems
        .Where(rp => rp.RoleId == role.Id)
        .Select(rp => rp.PermissionId)
        .ToListAsync();

      var callerPermissions = await _userPermissionsService.GetUserPermissionsAsync(userId);

      return new RolePermissionsResponseViewModel
      {
        RoleName = role.Name,
        Page = new PagedItemsViewModel<TreeItemViewModel>
        {
          Items = BuildPermissionTree(new HashSet<Guid>(granted))
        },
        Permissions = new Dictionary<string, bool>
        {
          { "canEdit", callerPermissions.HasPermission(Guid.Parse(TeamsPermissions.RolePermissionEditId)) }
        }
      };
    }

    /// <summary>
    /// Category -> group -> action. Only the leaves carry a real permission id;
    /// the two levels above exist so the UI can group and cascade-toggle, and
    /// are given throwaway ids.
    ///
    /// SuperAdminOnly permissions are excluded outright: they cannot be
    /// obtained through a role, so offering them as checkboxes would be a lie.
    /// </summary>
    private List<TreeItemViewModel> BuildPermissionTree(HashSet<Guid> granted)
    {
      var categories = _permissionsConfigService
        .GetPermissions().Values
        .Where(p => !p.SuperAdminOnly)
        .GroupBy(p => p.Category)
        .OrderBy(g => g.Key);

      var treeItems = new List<TreeItemViewModel>();

      foreach (var category in categories)
      {
        var categoryNode = new TreeItemViewModel
        {
          Id = Guid.NewGuid().ToString(),
          Name = category.Key,
          IsDirectory = true,
          HasItems = true,
          Expanded = true
        };
        treeItems.Add(categoryNode);

        var groups = category
          .GroupBy(p => p.Group)
          .OrderBy(g => g.Key);

        foreach (var group in groups)
        {
          var groupNode = new TreeItemViewModel
          {
            Id = Guid.NewGuid().ToString(),
            ParentId = categoryNode.Id,
            Name = group.Key.ToLower(),
            IsDirectory = true,
            HasItems = true,
            Expanded = true
          };
          categoryNode.Children.Add(groupNode);

          foreach (var permission in group.OrderBy(p => p.Action))
          {
            groupNode.Children.Add(new TreeItemViewModel
            {
              Id = permission.Id.ToString(),
              InstanceId = permission.Id,
              ParentId = groupNode.Id,
              Name = permission.Action.ToString().ToLower(),
              IsDirectory = false,
              HasItems = false,
              Selected = granted.Contains(permission.Id)
            });
          }
        }
      }

      return treeItems;
    }
  }
}
