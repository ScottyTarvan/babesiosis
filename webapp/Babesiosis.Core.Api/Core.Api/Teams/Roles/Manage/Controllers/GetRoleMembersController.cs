using Babesiosis.Core.Api.Teams.Roles.Manage.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Commands;
using Babesiosis.Core.Data;
using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  public class GetRoleMembersController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionItemsService _userPermissionsService;

    public GetRoleMembersController(IDbContextService dbContextService,
      IUserPermissionItemsService userPermissionsService)
    {
      _dbContextService = dbContextService;
      _userPermissionsService = userPermissionsService;
    }

    public async Task<RoleTeamMembersResponseViewModel> HandleCommand(Guid userId, ActionItemCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var role = await dbContext.Roles
        .FirstOrDefaultAsync(r => r.InstanceId == command.ItemId);

      Assertion.IsNotNull(role, "Role", "Role does not exist");

      var members = await dbContext.UserRoles
        .Where(ur => ur.RoleId == role.Id && !ur.User.IsDeleted)
        .OrderBy(ur => ur.User.FirstName)
          .ThenBy(ur => ur.User.LastName)
        .Select(ur => new RoleTeamMemberViewModel
        {
          InstanceId = ur.User.InstanceId,
          MemberId = ur.User.InstanceId,
          MemberFullName = ur.User.FirstName + " " + ur.User.LastName,
          MemberEmail = ur.User.Email
        })
        .ToListAsync();

      var permissions = await _userPermissionsService.GetUserPermissionsAsync(userId);

      return new RoleTeamMembersResponseViewModel
      {
        RoleName = role.Name,
        Members = members,
        Permissions = new Dictionary<string, bool>
        {
          { "canView", permissions.HasPermission(Guid.Parse(TeamsPermissions.RoleMemberReadId)) },
          { "canEdit", permissions.HasPermission(Guid.Parse(TeamsPermissions.RoleMemberEditId)) },
          // Deliberately the USER read grant, not a role-member one - the Assign Members
          // dialog's picker calls teams-user-list-get to list assignable users, so the
          // echo needs to be able to say the user directory (not the role) is what the
          // caller may not see when that dialog opens empty.
          { "canReadUsers", permissions.HasPermission(Guid.Parse(TeamsPermissions.UserReadId)) }
        }
      };
    }
  }
}
