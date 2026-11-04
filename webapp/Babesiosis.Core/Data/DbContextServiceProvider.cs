using Babesiosis.Core.Configurations;
using System;

namespace Babesiosis.Core.Data
{
  public static class DbContextServiceProvider
  {
    public static IDbContextService GetService(IServiceProvider services)
    {
      IAppSettingsService appSettingsService = services.GetService(typeof(IAppSettingsService)) as IAppSettingsService;

      return new DbContextService(appSettingsService);
    }
  }
}
