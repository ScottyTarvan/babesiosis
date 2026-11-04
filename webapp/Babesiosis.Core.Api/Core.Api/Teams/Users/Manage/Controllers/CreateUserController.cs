using System;
using System.Threading.Tasks;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Api.Teams.Users.Controllers;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Api.Teams.Users.Manage.Controllers
{
  /// <summary>
  /// The create-user endpoint for the new web application. Delegates the
  /// actual create logic to the legacy <see cref="AddUserController"/> —
  /// same reasoning as <see cref="GetUserListController"/>, keeping the
  /// validation and password handling in exactly one place — and adds the
  /// one check the legacy controller cannot express.
  /// <para>
  /// GAP-2: promoting a user to Administrator short-circuits every
  /// permission in the new model (<c>UserPermissionItemsService</c>) and
  /// bypasses the legacy one too (<c>UserPermissionService.Assert</c>), so
  /// setting it needs its own grant on top of the ordinary Add permission
  /// the [RequiredPermission] attribute already checks. This can't be a
  /// [RequiredPermission] attribute because whether it applies depends on
  /// the payload (is IsAdministrator being set?), not on which endpoint was
  /// called.
  /// </para>
  /// </summary>
  public class CreateUserController
  {
    private readonly AddUserController _controller;
    private readonly IUserPermissionItemsService _userPermissionsService;

    public CreateUserController(AddUserController controller,
      IUserPermissionItemsService userPermissionsService)
    {
      _controller = controller;
      _userPermissionsService = userPermissionsService;
    }

    public async Task<UserViewModel> HandleCommand(Guid userId, UserCommand command)
    {
      if (command.User.IsAdministrator)
      {
        var granted = await _userPermissionsService.HasPermissionAsync(userId, Guid.Parse(TeamsPermissions.UserElevateId));
        Assertion.True(granted, "You do not have access to grant administrator rights");
      }

      return await _controller.HandleCommand(userId, command);
    }
  }
}
