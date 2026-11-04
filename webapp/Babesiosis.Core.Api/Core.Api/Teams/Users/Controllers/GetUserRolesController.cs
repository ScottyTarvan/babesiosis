using AutoMapper;
using Babesiosis.Core.Api.Teams.Roles.ViewModels;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Api.Teams.Users.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class GetUserRolesController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;
    private readonly IUserPermissionsService _permissionsService;
    public GetUserRolesController(IDbContextService dbContextService,
      IMapper mapper,
      IUserPermissionsService permissionsService)
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
      _permissionsService = permissionsService;
    }

    public async Task<UserRolesViewModel> HandleCommand(Guid userId, GetUserRolesCommand command)
    {
      _permissionsService.Assert(userId, "read", "teams-user-role");
      
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
        .FirstOrDefaultAsync(g => g.InstanceId == command.UserId);

      Assertion.IsNotNull(user, "User", "User does not exist");

      var roles = dbContext.Roles
      .Include(r => r.Permissions)
      .OrderBy(r => r.Name)
      .GroupJoin(
          dbContext.UserRoles.Where(rp => rp.UserId == user.Id),
          role => role.Id,
          userRole => userRole.RoleId,
          (role, userRoles) => new { Role = role, UserRoles = userRoles }
      )
      .SelectMany(
          x => x.UserRoles.DefaultIfEmpty(),
          (role, userRole) => new TreeItemViewModel
          {
            InstanceId = role.Role.InstanceId,
            Id = role.Role.InstanceId.ToString(),
            Name = role.Role.Name,
            Selected = userRole != null,
            HasItems = false
          })
      .ToList();

      return new UserRolesViewModel()
      {
        Roles = roles 
      };
    }
  }
}
