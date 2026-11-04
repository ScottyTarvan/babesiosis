using Babesiosis.Core.Api.Teams.Roles.Manage.Commands;
using Babesiosis.Core.Api.Teams.Roles.Manage.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  public class AssignRoleMemberController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public AssignRoleMemberController(IDbContextService dbContextService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _dbContextService = dbContextService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }

    public async Task<RoleTeamMemberViewModel> HandleCommand(Guid userId, RoleMemberCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var role = await dbContext.Roles.FirstOrDefaultAsync(r => r.InstanceId == command.RoleId);
      Assertion.IsNotNull(role, "Role", "Role does not exist");

      var user = await dbContext.Users
        .FirstOrDefaultAsync(u => u.InstanceId == command.MemberId && !u.IsDeleted);
      Assertion.IsNotNull(user, "User", "User does not exist");

      var alreadyAssigned = await dbContext.UserRoles
        .AnyAsync(ur => ur.RoleId == role.Id && ur.UserId == user.Id);

      // Assign is idempotent — the dialog can be double-clicked, and a second
      // assignment is not an error worth surfacing to the user.
      if (!alreadyAssigned)
      {
        dbContext.UserRoles.Add(new UserRole { RoleId = role.Id, UserId = user.Id });
        await dbContext.SaveChangesAsync();

        // Revoke immediately: the middleware authorises from the cache, not the database.
        await _userPermissionsCacheService.ClearUserPermissionsFromCacheAsync(user.InstanceId);
      }

      return new RoleTeamMemberViewModel
      {
        InstanceId = user.InstanceId,
        MemberId = user.InstanceId,
        MemberFullName = $"{user.FirstName} {user.LastName}".Trim(),
        MemberEmail = user.Email
      };
    }
  }
}
