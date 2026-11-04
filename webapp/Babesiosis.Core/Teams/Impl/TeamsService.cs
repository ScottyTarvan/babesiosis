using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Services;
using Babesiosis.Core.Teams.Services;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Teams.Impl
{
  internal class TeamsService : ITeamsService
  {
    private readonly IDbContextService _dbContextService;
    internal TeamsService(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<User> GetUserAync(Guid userId)
    {
      using var dbContext = _dbContextService.CreateDbContext<DbContextBase>(); 

      var user = await dbContext.Users.FirstOrDefaultAsync(a => a.InstanceId == userId);

      Assertion.IsNotNull(user, "User", $"User does not exist for id '{userId}'");

      return user;
    }

    public async Task<User> GetUserAync(int userId)
    {
      using var dbContext = _dbContextService.CreateDbContext<DbContextBase>();

      var user = await dbContext.Users.FirstOrDefaultAsync(a => a.Id == userId);

      Assertion.IsNotNull(user, "User", $"User does not exist for id '{userId}'");

      return user;
    }
  }
}
