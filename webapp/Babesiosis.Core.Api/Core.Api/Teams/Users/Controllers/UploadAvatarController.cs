using AutoMapper;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Services;
using Babesiosis.Core.Teams.Users.Commands;
using Babesiosis.Core.ViewModels;
using System;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Teams.Users.Controllers
{
  public class UploadAvatarController
  {
    private readonly IAppSettingsService _appSettingsService;
    private readonly IDbContextService _dbContextService;
    private readonly IBlobStorageService _blobStorageService;
    private readonly IMapper _mapper;
    private readonly IUserPermissionsService _permissionsService;

    public UploadAvatarController(IAppSettingsService appSettingsService,
      IDbContextService dbContextService,
      IBlobStorageService blobStorageService,
      IMapper mapper,
      IUserPermissionsService permissionsService)
    {
      _appSettingsService = appSettingsService;
      _dbContextService = dbContextService;
      _blobStorageService = blobStorageService;
      _mapper = mapper;
      _permissionsService = permissionsService;
    }

    public async Task<NameValueViewModel<string>> HandleCommand(Guid userId, UploadAvatarCommand command)
    {
      _permissionsService.Assert(userId, "update", "teams-user-detail");

      var blob = await _blobStorageService.AddBlobAsync
        ( 
          _appSettingsService.GetAppSettings().Containers.Avatars, 
          command.File, 
          command.ContentType
        );
      command.File.Close();
            
      return new NameValueViewModel<string>(blob.Link, blob.Link);
    }
  }
}
