using Babesiosis.Core.Data;
using Babesiosis.Core.Services.Impl;
using System;

namespace Babesiosis.Core.Services.Providers
{
  public static class UserPermissionsServiceProvider
    {
        public static IUserPermissionsService GetService(IServiceProvider services)
        {
            IDbContextService dbContextService = services.GetService(typeof(IDbContextService)) as IDbContextService;
            IPermissionContext permissionContext = services.GetService(typeof(IPermissionContext)) as IPermissionContext;

            return new UserPermissionService(dbContextService, permissionContext);
        }
    }
}
