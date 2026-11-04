using Babesiosis.Core.Api.Teams.Roles.Manage.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Permissions;
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
  /// Diffs the submitted tree against the role's stored grants and applies the
  /// difference. Writes only to <c>team.RolePermissionItem</c> — the legacy
  /// <c>team.RolePermission</c> grants the old application reads are never
  /// touched by this endpoint.
  /// </summary>
  public class UpdateRolePermissionItemsController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IPermissionsConfigService _permissionsConfigService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public UpdateRolePermissionItemsController(IDbContextService dbContextService,
      IPermissionsConfigService permissionsConfigService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _dbContextService = dbContextService;
      _permissionsConfigService = permissionsConfigService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }

    public async Task HandleCommand(Guid userId, UpdateRolePermissionsCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>(trackChanges: true);

      var role = await dbContext.Roles
        .Include(r => r.PermissionItems)
        .FirstOrDefaultAsync(r => r.InstanceId == command.RoleId);

      Assertion.IsNotNull(role, "Role", "Role does not exist");

      // Only ids that exist in the catalogue are honoured, and SuperAdminOnly
      // permissions are refused outright — they are not role-grantable, so a
      // crafted request must not be able to store one.
      var grantable = _permissionsConfigService.GetPermissions().Values
        .Where(p => !p.SuperAdminOnly)
        .Select(p => p.Id)
        .ToHashSet();

      var submitted = FlattenLeaves(command.Permissions)
        .Where(p => Guid.TryParse(p.Id, out var id) && grantable.Contains(id))
        .GroupBy(p => Guid.Parse(p.Id))
        .ToDictionary(g => g.Key, g => g.Any(p => p.Selected));

      var existing = role.PermissionItems ?? new List<RolePermissionItem>();
      var existingIds = existing.Select(p => p.PermissionId).ToHashSet();

      var added = submitted
        .Where(p => p.Value && !existingIds.Contains(p.Key))
        .Select(p => new RolePermissionItem { RoleId = role.Id, PermissionId = p.Key })
        .ToList();

      var removed = existing
        .Where(p => submitted.TryGetValue(p.PermissionId, out var selected) && !selected)
        .ToList();

      dbContext.RolePermissionItems.AddRange(added);
      dbContext.RolePermissionItems.RemoveRange(removed);

      await dbContext.SaveChangesAsync();

      // Revoke immediately: the middleware authorises from the cache, not the database.
      await _userPermissionsCacheService.ClearUsersInRoleFromCacheAsync(role.Id);
    }

    /// <summary>
    /// Walks the tree and returns only the leaves — the branch nodes are UI
    /// grouping rows whose ids are throwaway GUIDs, not permissions.
    /// </summary>
    private static IEnumerable<TreeItemViewModel> FlattenLeaves(IEnumerable<TreeItemViewModel> nodes)
    {
      foreach (var node in nodes ?? Enumerable.Empty<TreeItemViewModel>())
      {
        if (node.Children == null || node.Children.Count == 0)
        {
          yield return node;
          continue;
        }

        foreach (var leaf in FlattenLeaves(node.Children))
        {
          yield return leaf;
        }
      }
    }
  }
}
