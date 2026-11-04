using Babesiosis.Core.Configurations;
using Babesiosis.Core.Services.Impl;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using System;

namespace Babesiosis.Core.Services.Providers
{
  public static class EventGridServiceProvider
  {
    public static IEventGridService GetService(IServiceProvider services)
    {
      var appSettingsService = services.GetRequiredService<IAppSettingsService>();
      var appSettings = appSettingsService.GetAppSettings();
      var logger = services.GetRequiredService<ILogger<AzureEventGridService>>();

      // Get or create singleton EventGridClientManager
      var clientManager = EventGridClientManager.GetInstance(appSettings);

      return new AzureEventGridService(appSettings, clientManager, logger);
    }
  }
}
