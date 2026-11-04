using Babesiosis.Core.Api.Teams.Roles.Manage.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  public class RemoveRoleMemberController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public RemoveRoleMemberController(IDbContextService dbContextService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _dbContextService = dbContextService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }

    public async Task HandleCommand(Guid userId, RoleMemberCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>(trackChanges: true);

      var role = await dbContext.Roles.FirstOrDefaultAsync(r => r.InstanceId == command.RoleId);
      Assertion.IsNotNull(role, "Role", "Role does not exist");

      var user = await dbContext.Users.FirstOrDefaultAsync(u => u.InstanceId == command.MemberId);
      Assertion.IsNotNull(user, "User", "User does not exist");

      var assignment = await dbContext.UserRoles
        .FirstOrDefaultAsync(ur => ur.RoleId == role.Id && ur.UserId == user.Id);

      // Removing an assignment that is already gone is a no-op, not an error.
      if (assignment == null)
      {
        return;
      }

      dbContext.UserRoles.Remove(assignment);
      await dbContext.SaveChangesAsync();

      // Revoke immediately: the middleware authorises from the cache, not the database.
      await _userPermissionsCacheService.ClearUserPermissionsFromCacheAsync(user.InstanceId);
    }
  }
}
