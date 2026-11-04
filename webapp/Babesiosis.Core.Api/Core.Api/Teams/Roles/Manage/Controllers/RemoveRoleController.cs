using Babesiosis.Core.Assertions;
using Babesiosis.Core.Commands;
using Babesiosis.Core.Data;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  /// <summary>
  /// Deletes a role along with its assignments and grants.
  ///
  /// The legacy delete refuses when the role has permissions, which forces a
  /// two-step "clear then delete" dance. The new UI warns the user that members
  /// will be unassigned and then does the whole thing in one call — the FK on
  /// RolePermissionItem cascades, and legacy RolePermission rows and user
  /// assignments are removed explicitly.
  /// </summary>
  public class RemoveRoleController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public RemoveRoleController(IDbContextService dbContextService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _dbContextService = dbContextService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }

    public async Task HandleCommand(Guid userId, ActionItemCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>(trackChanges: true);

      var role = await dbContext.Roles
        .Include(r => r.UserRoles)
        .FirstOrDefaultAsync(r => r.InstanceId == command.ItemId);

      Assertion.IsNotNull(role, "Role", "Role does not exist");
      Assertion.RowVersionCheck(role.RowVersion, command.RowVersion,
        "The role has changed since the page first loaded, please refresh and try again");

      var legacyGrants = await dbContext.RolePermissions
        .Where(rp => rp.RoleId == role.Id)
        .ToListAsync();

      var grants = await dbContext.RolePermissionItems
        .Where(rp => rp.RoleId == role.Id)
        .ToListAsync();

      // Captured before the UserRole rows are removed below — once the role is
      // deleted, querying its members would find nobody left to invalidate.
      List<Guid> memberInstanceIds = await dbContext.UserRoles
        .Where(ur => ur.RoleId == role.Id)
        .Select(ur => ur.User.InstanceId)
        .ToListAsync();

      dbContext.RolePermissions.RemoveRange(legacyGrants);
      dbContext.RolePermissionItems.RemoveRange(grants);

      if (role.UserRoles != null && role.UserRoles.Count > 0)
      {
        dbContext.UserRoles.RemoveRange(role.UserRoles);
      }

      dbContext.Roles.Remove(role);
      await dbContext.SaveChangesAsync();

      // Revoke immediately: the middleware authorises from the cache, not the database.
      foreach (Guid memberInstanceId in memberInstanceIds)
      {
        await _userPermissionsCacheService.ClearUserPermissionsFromCacheAsync(memberInstanceId);
      }
    }
  }
}
