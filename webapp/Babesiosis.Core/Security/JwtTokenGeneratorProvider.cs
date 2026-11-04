using Babesiosis.Core.Configurations;
using System;

namespace Babesiosis.Core.Security
{
  public static class JwtTokenGeneratorProvider
  {
    public static IJwtTokenGenerator GetService(IServiceProvider services)
    {
      var appSettingsService = services.GetService(typeof(IAppSettingsService)) as IAppSettingsService;
      var appSettings = appSettingsService.GetAppSettings();

      return new JwtTokenGenerator(appSettings.Jwt.SecurityKey, appSettings.Jwt.Audience, appSettings.Jwt.Issuer, appSettings.Jwt.ExpiryTimeSpan);
    }
  }
}
