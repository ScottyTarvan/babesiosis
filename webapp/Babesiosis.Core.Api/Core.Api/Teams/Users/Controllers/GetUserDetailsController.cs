using AutoMapper;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Services;
using Babesiosis.Core.ViewModels;
using Microsoft.EntityFrameworkCore;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class GetUserDetailsController
  {
    private readonly IDbContextService _dbContextService;
    private readonly IMapper _mapper;
    private readonly IBlobStorageService _blobStorageService;
    private readonly IAppSettings _appSettings;
    private readonly IUserPermissionsService _permissionsService;

    public GetUserDetailsController(IDbContextService dbContextService,
      IMapper mapper,
      IBlobStorageService blobStorageService,
      IAppSettingsService appSettingsService,
      IUserPermissionsService permissionsService
      )
    {
      _dbContextService = dbContextService;
      _mapper = mapper;
      _blobStorageService = blobStorageService;
      _appSettings = appSettingsService.GetAppSettings();
      _permissionsService = permissionsService;
    }

    public async Task<UserViewModel> HandleCommand(Guid userId, Guid lookupUserId)
    {
      _permissionsService.Assert(userId, "read", "teams-user-detail");
            
      using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();

      var user = await dbContext.Users
        .FirstOrDefaultAsync(u => u.InstanceId == lookupUserId);

      Assertion.IsNotNull(user, "User", $"User does not exist for id {lookupUserId}");

      var result = _mapper.Map<UserViewModel>(user);

      return result;
    }
  }
}
