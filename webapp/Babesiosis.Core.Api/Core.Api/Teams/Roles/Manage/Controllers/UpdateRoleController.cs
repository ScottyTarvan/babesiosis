using AutoMapper;
using Babesiosis.Core.Api.Teams.Roles.Manage.Commands;
using Babesiosis.Core.Api.Teams.Roles.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Microsoft.EntityFrameworkCore;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  public class UpdateRoleController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;

    public UpdateRoleController(IDbContextService dbContextService, IMapper mapper)
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
    }

    public async Task<RoleViewModel> HandleCommand(Guid userId, RoleItemCommand command)
    {
      Assertion.IsNotNull(command?.Role, "Role", "Role is required");
      Assertion.False(string.IsNullOrWhiteSpace(command.Role.Name), "Role name is required");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>(trackChanges: true);

      var role = await dbContext.Roles
        .FirstOrDefaultAsync(r => r.InstanceId == command.Role.InstanceId);

      Assertion.IsNotNull(role, "Role", "Role does not exist");
      Assertion.RowVersionCheck(role.RowVersion, command.Role.RowVersion,
        "The role has changed since the page first loaded, please refresh and try again");

      var duplicate = await dbContext.Roles
        .AnyAsync(r => r.Name == command.Role.Name && r.InstanceId != role.InstanceId);
      Assertion.False(duplicate, $"A role already exists with the name {command.Role.Name}");

      role.Name = command.Role.Name;
      role.Description = command.Role.Description;

      await dbContext.SaveChangesAsync();

      return _mapper.Map<RoleViewModel>(role);
    }
  }
}
