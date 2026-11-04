using Babesiosis.Core.Configurations;
using Babesiosis.Core.Services.Impl;
using System;

namespace Babesiosis.Core.Services.Providers
{
  public static class EmailServiceProvider
    {
        public static IEmailService GetService(IServiceProvider services)
        {
            var appSettingsService = services.GetService(typeof(IAppSettingsService)) as IAppSettingsService;
            return new AzureCommunicationEmailService(appSettingsService);
        }
    }
}
