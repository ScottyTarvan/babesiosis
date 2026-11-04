using Babesiosis.Core.Configurations;
using Babesiosis.Core.Services.Impl;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System;
using System.Diagnostics;

namespace Babesiosis.Core.Services.Providers
{
  public static class KeyVaultServiceProvider
  {
    public static IKeyVaultService GetService(IServiceProvider services)
    {
      var appSettingsService = services.GetRequiredService<IAppSettingsService>();
      var appSettings = appSettingsService.GetAppSettings();
      var logger = services.GetRequiredService<ILogger<AzureKeyVaultService>>();
      var clientManager = KeyVaultClientManager.GetInstance(appSettings);

      //if (Debugger.IsAttached)
      //{
      //  return new LocalKeyVaultService(AppContext.BaseDirectory, appSettings, clientManager, logger);
      //}
      return new AzureKeyVaultService(appSettings, clientManager, logger);
    }
  }
}
