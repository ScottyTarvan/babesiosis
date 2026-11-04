using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Services;
using Babesiosis.Core.Services.Impl;
using Microsoft.Extensions.Logging;
using System;
using System.Diagnostics;

namespace Babesiosis.Core.Services.Providers
{
  public static class UserPermissionsCacheServiceProvider
  {
    public static IUserPermissionsCacheService GetService(IServiceProvider services)
    {
      IAppSettingsService appSettingsService = services.GetService(typeof(IAppSettingsService)) as IAppSettingsService;
      IAppSettings appSettings = appSettingsService.GetAppSettings();
      IBlobStorageService blobStorageService = services.GetService(typeof(IBlobStorageService)) as IBlobStorageService;
      IDbContextService dbContextService = services.GetService(typeof(IDbContextService)) as IDbContextService;
      IPermissionsConfigService permissionsConfigService = services.GetService(typeof(IPermissionsConfigService)) as IPermissionsConfigService;
      IServiceBusService serviceBusService = services.GetService(typeof(IServiceBusService)) as IServiceBusService;
      ILoggerFactory loggerFactory = services.GetService(typeof(ILoggerFactory)) as ILoggerFactory;
      ILogger logger = loggerFactory?.CreateLogger<UserPermissionsCacheService>();

      if (Debugger.IsAttached)
      {
        return new LocalUserPermissionsCacheService(dbContextService, permissionsConfigService, TimeProvider.System);
      }

      return new UserPermissionsCacheService(appSettings, blobStorageService, dbContextService, permissionsConfigService, TimeProvider.System, logger, serviceBusService);
    }
  }
}
