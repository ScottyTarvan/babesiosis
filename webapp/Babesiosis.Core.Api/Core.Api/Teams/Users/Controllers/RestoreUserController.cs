using System;
using System.Threading.Tasks;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Services;
using Babesiosis.Core.Teams.Users.Commands;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class RestoreUserController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionsService _permissionsService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public RestoreUserController(
      IDbContextService dbContextService,
      IUserPermissionsService permissionsService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _permissionsService = permissionsService;
      _dbContextService = dbContextService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }

    public async Task HandleCommand(Guid userId, RestoreUserCommand command)
    {
      _permissionsService.Assert(userId, "update", "teams-user");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
          .FirstOrDefaultAsync(a => a.InstanceId == command.User.InstanceId);
      Assertion.IsNotNull(user, "User", $"User does not exist for id {command.User.InstanceId}");

      Assertion.RowVersionCheck(user.RowVersion, command.User.RowVersion, "The user has changed since the page was loaded, refresh and try again");

      user.IsDeleted = false;

      dbContext.Update(user);
      await dbContext.SaveChangesAsync();

      // A prior delete may have cached an Exists=false record for this user; without this the
      // restore would read as still-deleted (fail-closed, but stale) until that entry ages out.
      await _userPermissionsCacheService.ClearUserPermissionsFromCacheAsync(user.InstanceId);
    }
  }
}
