using AutoMapper;
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
  public class GetUsersController
  {
    private readonly IMapper _mapper;
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionsService _permissionsService;

    public GetUsersController(IDbContextService dbContextService,
      IUserPermissionsService permissionsService,
      IMapper mapper)
    {
      _dbContextService = dbContextService;
      _permissionsService = permissionsService;
      _mapper = mapper;
    }

    public async Task<UsersViewModel> HandleCommand(Guid userId, GetUsersCommand command)
    {
      _permissionsService.Assert(userId, "read", "teams-user");
            
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      //only active users
      var users = dbContext.Users
        .AsQueryable();

      if( command.LoadOptions.Filter == null)
      {
        users = users.Where(u => !u.IsDeleted);
      }

      var page = await command.LoadOptions.LoadPageAsync(users);

      UsersViewModel result = new UsersViewModel()
      {
        Pager = new PagerViewModel(page),
        Users = page.Results.Select(u => _mapper.Map<UserViewModel>(u, opt => opt.AfterMap((src, tgt) => tgt.Password = null)))
      };

      return result;
    }
  }
}
