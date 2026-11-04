using System;
using System.Linq;
using System.Threading.Tasks;
using AutoMapper;
using Babesiosis.Core.Api.Teams.Users.Commands;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Babesiosis.Core.Teams.Users.Commands;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class EditUserController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;
    private readonly IPasswordEncryptor _passwordEncryptor;
    private readonly IUserPermissionsService _permissionsService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public EditUserController(IDbContextService dbContextService,
      IMapper mapper,
      IPasswordEncryptor passwordEncryptor,
      IUserPermissionsService permissionsService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
      _passwordEncryptor = passwordEncryptor;
      _permissionsService = permissionsService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }
    public async Task<UserViewModel> HandleCommand(Guid userId, UserCommand command)
    {
      _permissionsService.Assert(userId, "update", "teams-user");

      Assertion.IsNotNull(command.User, "User");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
          .FirstOrDefaultAsync(a => a.InstanceId == command.User.InstanceId);

      Assertion.IsNotNull(user, "User", $"User does not exist for id {command.User.InstanceId}");
      Assertion.False(dbContext.Users.Any(a => a.Email == command.User.Email && a.Id != user.Id), $"User with email: {command.User.Email} already exists");
      Assertion.RowVersionCheck(user.RowVersion, command.User.RowVersion, "The user has changed since the page was loaded, refresh and try again");

      _mapper.Map(command.User, user);

      if (!string.IsNullOrEmpty(command.User.Password))
      {
        user.Password = _passwordEncryptor.EncryptAndHashPassword
        (
          command.User.Password,
          user.IV,
          user.Salt
        );
      }

      dbContext.Update(user);
      await dbContext.SaveChangesAsync();

      // Revoke immediately: the middleware authorises from the cache, not the database. This is
      // the primary demotion path for IsAdministrator (and the only live path that can flip
      // IsSuperAdministrator, were the map above not ignoring it) so a stale cache entry here
      // would keep a demoted user's old grants for up to the L1/blob trust window.
      await _userPermissionsCacheService.ClearUserPermissionsFromCacheAsync(user.InstanceId);

      var result = _mapper.Map<UserViewModel>(user);
      return result;
    }
  }
}
