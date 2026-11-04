using AutoMapper;
using Babesiosis.Core.Api.Teams.Roles.Manage.Commands;
using Babesiosis.Core.Api.Teams.Roles.ViewModels;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.Controllers
{
  public class CreateRoleController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;

    public CreateRoleController(IDbContextService dbContextService, IMapper mapper)
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
    }

    public async Task<RoleViewModel> HandleCommand(Guid userId, RoleItemCommand command)
    {
      Assertion.IsNotNull(command?.Role, "Role", "Role is required");
      Assertion.False(string.IsNullOrWhiteSpace(command.Role.Name), "Role name is required");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var duplicate = await dbContext.Roles.AnyAsync(r => r.Name == command.Role.Name);
      Assertion.False(duplicate, $"A role already exists with the name {command.Role.Name}");

      var role = _mapper.Map<Role>(command.Role);
      role.InstanceId = Guid.NewGuid();

      dbContext.Roles.Add(role);
      await dbContext.SaveChangesAsync();

      return _mapper.Map<RoleViewModel>(role);
    }
  }
}
