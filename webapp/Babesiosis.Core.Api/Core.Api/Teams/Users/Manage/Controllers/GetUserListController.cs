using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Api.Teams.Users.Controllers;
using Babesiosis.Core.Api.Teams.Users.ViewModels;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Users.Manage.Controllers
{
  /// <summary>
  /// The users list for the new web application: identical rows to the legacy
  /// endpoint, plus the capability echo the grid gates its actions on.
  ///
  /// Delegating rather than duplicating keeps the query, the soft-delete filter
  /// and the password scrubbing in exactly one place.
  /// </summary>
  public class GetUserListController
  {
    private readonly GetUsersController _controller;
    private readonly IUserPermissionItemsService _userPermissionsService;

    public GetUserListController(GetUsersController controller,
      IUserPermissionItemsService userPermissionsService)
    {
      _controller = controller;
      _userPermissionsService = userPermissionsService;
    }

    public async Task<UsersViewModel> HandleCommand(Guid userId, GetUsersCommand command)
    {
      var result = await _controller.HandleCommand(userId, command);

      var permissions = await _userPermissionsService.GetUserPermissionsAsync(userId);

      result.Permissions = new Dictionary<string, bool>
      {
        { "canRead", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserReadId)) },
        { "canAdd", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserAddId)) },
        { "canEdit", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserEditId)) },
        { "canDelete", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserDeleteId)) },
        { "canViewRoles", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserRoleReadId)) },
        { "canEditRoles", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserRoleEditId)) },
        // GAP-2: lets the grid show/hide the Administrator toggle's own gate,
        // distinct from ordinary Edit — see TeamsPermissions.UserElevate.
        { "canElevate", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserElevateId)) },
        // The users grid export carries user PII and was ungated before
        // 2026-09-21.
        { "canExport", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserDownloadId)) }
      };

      return result;
    }
  }
}
