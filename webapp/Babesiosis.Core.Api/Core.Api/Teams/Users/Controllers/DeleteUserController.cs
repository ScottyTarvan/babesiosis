using System;
using System.Threading.Tasks;
using AutoMapper;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Commands;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class DeleteUserController
  {
    private readonly IMapper _mapper;
    private readonly IDbContextService _dbContextService;
    private readonly IUserPermissionsService _permissionsService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public DeleteUserController(
      IMapper mapper,
      IDbContextService dbContextService,
      IUserPermissionsService permissionsService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _mapper = mapper;
      _dbContextService = dbContextService;
      _permissionsService = permissionsService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }
    public async Task<UserViewModel> HandleCommand(Guid userId, ActionItemCommand command)
    {
      _permissionsService.Assert(userId, "delete", "teams-user");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
          .FirstOrDefaultAsync(a => a.InstanceId == userId);

      var deletedUser = await dbContext.Users
          .FirstOrDefaultAsync(a => a.InstanceId == command.ItemId);

      Assertion.IsNotNull(deletedUser, "User", $"User does not exist for id {command.ItemId}");

      var isMyUser = await dbContext.Users.AnyAsync(u => deletedUser.InstanceId != user.InstanceId);
      Assertion.True(isMyUser, "A user cannot remove themself as this action would result in an error.");

      Assertion.RowVersionCheck(deletedUser.RowVersion, command.RowVersion, "The user has changed since the page was loaded, refresh and try again");

      deletedUser.IsDeleted = true;

      dbContext.Update(deletedUser);
      await dbContext.SaveChangesAsync();

      // Revoke immediately: the middleware authorises from the cache, not the database.
      // Retire rather than clear: a deleted user's record is also scheduled for removal,
      // so it does not sit in the cache container until the lifecycle rule sweeps it.
      await _userPermissionsCacheService.RetireUserPermissionsFromCacheAsync(deletedUser.InstanceId);

      var userViewModel = _mapper.Map<UserViewModel>(user);
      return userViewModel;
    }
  }
}
