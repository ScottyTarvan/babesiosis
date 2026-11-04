using Babesiosis.Core.Configurations;
using Babesiosis.Core.Services.Impl;
using System;

namespace Babesiosis.Core.Services.Azure
{
  public static class TableStorageServiceProvider
  {
    public static ITableStorageService GetService(IServiceProvider services)
    {
      IAppSettingsService appSettingsService = services.GetService(typeof(IAppSettingsService)) as IAppSettingsService;

      return new AzureTableStorageService(appSettingsService);
    }
  }
}
