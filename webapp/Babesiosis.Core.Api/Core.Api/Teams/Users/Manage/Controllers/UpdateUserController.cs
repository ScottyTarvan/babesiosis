using System;
using System.Threading.Tasks;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Api.Teams.Users.Controllers;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams.Users.Manage.Controllers
{
  /// <summary>
  /// The edit-user endpoint for the new web application. Delegates the
  /// actual update logic to the legacy <see cref="EditUserController"/> —
  /// same reasoning as <see cref="GetUserListController"/> — and adds the
  /// GAP-2 admin-elevation check on top.
  /// <para>
  /// The stored value has to be read here, before delegating, because the
  /// legacy controller overwrites it as part of the same call. Asserting
  /// only when IsAdministrator is changing — set OR cleared — means an
  /// ordinary edit that leaves the flag untouched never needs the grant;
  /// otherwise every routine user edit would start failing for anyone
  /// without it.
  /// </para>
  /// </summary>
  public class UpdateUserController
  {
    private readonly EditUserController _controller;
    private readonly IUserPermissionItemsService _userPermissionsService;
    private readonly IDbContextService _dbContextService;

    public UpdateUserController(EditUserController controller,
      IUserPermissionItemsService userPermissionsService,
      IDbContextService dbContextService)
    {
      _controller = controller;
      _userPermissionsService = userPermissionsService;
      _dbContextService = dbContextService;
    }

    public async Task<UserViewModel> HandleCommand(Guid userId, UserCommand command)
    {
      using (var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>())
      {
        var existing = await dbContext.Users.AsNoTracking()
          .FirstOrDefaultAsync(u => u.InstanceId == command.User.InstanceId);

        Assertion.IsNotNull(existing, "User", $"User does not exist for id {command.User.InstanceId}");

        if (command.User.IsAdministrator != existing.IsAdministrator)
        {
          var granted = await _userPermissionsService.HasPermissionAsync(userId, Guid.Parse(TeamsPermissions.UserElevateId));
          Assertion.True(granted, "You do not have access to grant administrator rights");
        }
      }

      return await _controller.HandleCommand(userId, command);
    }
  }
}
