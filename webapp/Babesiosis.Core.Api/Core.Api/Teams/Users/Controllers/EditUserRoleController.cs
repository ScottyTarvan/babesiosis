using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using Babesiosis.Core.Api.Teams.Roles.ViewModels;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Api.Teams.Users.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class EditUserRoleController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionsService _permissionsService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public EditUserRoleController(IDbContextService dbContextService,
      IUserPermissionsService permissionsService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _dbContextService = dbContextService;
      _permissionsService = permissionsService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }
    public async Task HandleCommand(Guid userId, EditUserRoleCommand command)
    {
      _permissionsService.Assert(userId, "update", "teams-user-role");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
        .Include(g => g.UserRoles)
          .ThenInclude(g => g.Role)
        .FirstOrDefaultAsync(g => g.InstanceId == command.UserId);

      Assertion.IsNotNull(user, "User", "User does not exist");

      var role = await dbContext.Roles.FirstOrDefaultAsync(p => p.InstanceId == command.Role.InstanceId);
      Assertion.IsNotNull(role, "Role", "Role does not exist");

      var userRole = user.UserRoles.FirstOrDefault(p => p.RoleId == role.Id);

      if (command.Role.Selected && userRole == null)
      {
        userRole = new UserRole()
        {
          UserId = user.Id,
          RoleId = role.Id
        };
        dbContext.UserRoles.Add(userRole);
      }
      else if (!command.Role.Selected && userRole != null)
      {
        dbContext.Entry(userRole).State = EntityState.Deleted;
      }

      await dbContext.SaveChangesAsync();

      // Revoke immediately: the middleware authorises from the cache, not the database.
      await _userPermissionsCacheService.ClearUserPermissionsFromCacheAsync(user.InstanceId);
    }
  }
}
