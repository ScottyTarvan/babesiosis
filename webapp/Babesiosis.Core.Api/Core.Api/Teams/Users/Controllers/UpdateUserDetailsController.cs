using AutoMapper;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Services;
using Babesiosis.Core.Teams.Users.Commands;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class UpdateUserDetailsController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;
    private readonly IBlobStorageService _blobStorageService;
    private readonly IAppSettings _appSettings;
    private readonly IUserPermissionsService _permissionsService;
    private readonly IUserPermissionsCacheService _userPermissionsCacheService;

    public UpdateUserDetailsController(IDbContextService dbContextService,
      IMapper mapper,
      IBlobStorageService blobStorageService,
      IAppSettingsService appSettingsService,
      IUserPermissionsService permissionsService,
      IUserPermissionsCacheService userPermissionsCacheService)
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
      _blobStorageService = blobStorageService;
      _appSettings = appSettingsService.GetAppSettings();
      _permissionsService = permissionsService;
      _userPermissionsCacheService = userPermissionsCacheService;
    }

    public async Task<UserViewModel> HandleCommand(Guid userId, UpdateUserDetailsCommand command)
    {
      _permissionsService.Assert(userId, "update", "teams-user-detail");

      Assertion.IsNotNull(command.User, "User");

      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
      .Include(u => u.UserRoles)
      .FirstOrDefaultAsync(a => a.InstanceId == command.User.InstanceId);

      Assertion.IsNotNull(user, "User", $"User does not exist for id {command.User.InstanceId}");
      Assertion.False(dbContext.Users.Any(a => a.Email == command.User.Email && a.Id != user.Id), $"User with email: {command.User.Email} already exists");

      Assertion.RowVersionCheck(user.RowVersion, command.User.RowVersion, "User details have changed since the page was loaded, refresh and try again");

      user.FirstName = command.User.FirstName;
      user.LastName = command.User.LastName;
      user.Email = command.User.Email;
      user.MobileNumber = command.User.MobileNumber;
      user.MobileNumberCode = command.User.MobileNumberCode;
      user.LandlineNumber = command.User.LandlineNumber;
      user.LandlineNumberCode = command.User.LandlineNumberCode;

      if (user.IsAdministrator)
      {
        user.IsAdministrator = command.User.IsAdministrator;
      }

      dbContext.Update(user);
      await dbContext.SaveChangesAsync();

      // Revoke immediately: the middleware authorises from the cache, not the database.
      await _userPermissionsCacheService.ClearUserPermissionsFromCacheAsync(user.InstanceId);

      var viewModel = _mapper.Map<UserViewModel>(user);

      return viewModel;
    }
  }
}
