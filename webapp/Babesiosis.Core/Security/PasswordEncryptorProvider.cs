using Babesiosis.Core.Configurations;
using System;

namespace Babesiosis.Core.Security
{
  public static class PasswordEncryptorProvider
  {
    public static IPasswordEncryptor GetService(IServiceProvider services)
    {
      var appSettingsService = services.GetService(typeof(IAppSettingsService)) as IAppSettingsService;
      return new PasswordEncryptor(appSettingsService.GetAppSettings().Security.EncryptionKey);
    }
  }
}
