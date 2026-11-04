using Azure.Identity;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Configuration.AzureAppConfiguration;
using Microsoft.Identity.Client.Platforms.Features.DesktopOs.Kerberos;
using System;
using System.Diagnostics;

namespace Babesiosis.Core.Configurations
{
  public class AppSettingsService : IAppSettingsService
  {
    private IConfiguration _configuration;
    private AppSettings _appSettings;

    public AppSettingsService(string basePath)
    {
      var environment = Environment.GetEnvironmentVariable("AZURE_FUNCTIONS_ENVIRONMENT");
      var isDevelopment = string.Equals(environment, "Development", StringComparison.OrdinalIgnoreCase);

      // Note: Debugger.IsAttached is unreliable in the isolated worker model — VS attaches to the
      // worker process a beat after host build, so the env check is the primary local-dev signal.
      if (isDevelopment || Debugger.IsAttached)
      {
        this._configuration = new ConfigurationBuilder()
           .SetBasePath(basePath)
           .AddJsonFile("debug-appsettings.json", optional: false, reloadOnChange: true)
           .AddEnvironmentVariables()
           .Build();
      }
      else
      {
        // Read through the configuration env-var provider rather than
        // Environment.GetEnvironmentVariable("A:B:C"): Linux env var names cannot contain ':',
        // so on Linux App Service the setting is "AppSettings__Connections__AppConfiguration"
        // and the colon lookup returns null (-> AzureAppConfiguration.Connect(null) aborts the
        // process). The provider maps BOTH the Windows colon form and the Linux double-underscore
        // form to the same key, so this works on both hosts.
        var envConfig = new ConfigurationBuilder().AddEnvironmentVariables().Build();
        var cn = envConfig["AppSettings:Connections:AppConfiguration"];
        var env = envConfig["AppSettings:Environment"];
        var credential = new DefaultAzureCredential();

        this._configuration = new ConfigurationBuilder()
          .AddAzureAppConfiguration(options =>
          {
            options.Connect(cn)
                 .Select(KeyFilter.Any, LabelFilter.Null)
                 .Select(KeyFilter.Any, env)
                 .ConfigureKeyVault(kv => kv.SetCredential(credential))
                 .ConfigureRefresh(refresh => refresh.Register("AppSettings:AppConfig:Sentinel", refreshAll: true));
          }).Build();
      }
    }

    public IAppSettings GetAppSettings()
    {
      if (_appSettings == null)
      {
        _appSettings = new AppSettings(this._configuration);
      }

      return _appSettings;
    }
  }
}
