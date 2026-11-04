using Babesiosis.Core.Services.Impl;
using System;

namespace Babesiosis.Core.Services.Providers
{
  public static class UserPermissionItemsServiceProvider
  {
    public static IUserPermissionItemsService GetService(IServiceProvider services)
    {
      IUserPermissionsCacheService userPermissionsCacheService = services.GetService(typeof(IUserPermissionsCacheService)) as IUserPermissionsCacheService;
      IPermissionsConfigService permissionsConfigService = services.GetService(typeof(IPermissionsConfigService)) as IPermissionsConfigService;

      return new UserPermissionItemsService(userPermissionsCacheService, permissionsConfigService);
    }
  }
}
