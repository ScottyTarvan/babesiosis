using Babesiosis.Core.Configurations;
using Babesiosis.Core.Services.Impl;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System;

namespace Babesiosis.Core.Services.Providers
{
  public static class BlobStorageServiceProvider
  {
    public static IBlobStorageService GetService(IServiceProvider services)
    {
      var appSettingsService = services.GetRequiredService<IAppSettingsService>();
      var logger = services.GetRequiredService<ILogger<AzureBlobStorageService>>();
      var appSettings = appSettingsService.GetAppSettings();

      // Get or create singleton BlobStorageClientManager
      var clientManager = BlobStorageClientManager.GetInstance(appSettings);

      return new AzureBlobStorageService(appSettings, clientManager, logger);
    }
  }
}
