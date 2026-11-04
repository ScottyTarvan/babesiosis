using Babesiosis.Core.Configurations;
using Babesiosis.Core.Services.Impl;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System;

namespace Babesiosis.Core.Services.Providers
{
  public static class ServiceBusServiceProvider
  {
    public static IServiceBusService GetService(IServiceProvider services)
    {
      var appSettingsService = services.GetRequiredService<IAppSettingsService>();
      var logger = services.GetRequiredService<ILogger<AzureServiceBusService>>();
      var appSettings = appSettingsService.GetAppSettings();

      // Get or create singleton ServiceBusClientManager
      var clientManager = ServiceBusClientManager.GetInstance(appSettings);

      return new AzureServiceBusService(appSettings, clientManager, logger);
    }
  }
}
