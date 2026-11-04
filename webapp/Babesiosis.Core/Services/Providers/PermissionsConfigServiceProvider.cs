using Babesiosis.Core.Permissions.Configs;
using Babesiosis.Core.Services.Impl;
using System;

namespace Babesiosis.Core.Services.Providers
{
  /// <summary>
  /// The single source of truth for the code-declared permission catalogue: every
  /// config class under <c>Babesiosis.Core/Permissions/Configs/</c> (Teams,
  /// Pipelines, Setup, Manage, Reports), registered here once. Every consumer that
  /// needs the full catalogue — <c>Core.Functions/Program.cs</c>,
  /// <c>Reports.Functions/Program.cs</c>, <c>Babesiosis.Test/Test/TestsBase.cs</c> —
  /// obtains it through <see cref="GetService"/> instead of hand-listing the config
  /// classes itself, so a sixth config class only has to be added here to reach
  /// every consumer. Registering a config class an app does not enforce is
  /// harmless: resolving a permission id is a dictionary lookup, so the shared
  /// catalogue costs nothing extra to carry around.
  /// </summary>
  public static class PermissionsConfigServiceProvider
  {
    /// <summary>
    /// The <paramref name="services"/> parameter matches the <c>Func&lt;IServiceProvider,
    /// object&gt;</c> shape the other <c>*Provider.GetService</c> factories use for
    /// <see cref="Microsoft.Extensions.DependencyInjection.ServiceDescriptor"/>
    /// registration, but is unused: the catalogue depends on nothing else in the
    /// container, so it is safe to call directly (even with a null provider) outside
    /// of DI, as the test helpers do.
    /// </summary>
    public static IPermissionsConfigService GetService(IServiceProvider services)
    {
      PermissionsConfigService permissionsConfigService = new PermissionsConfigService();
      permissionsConfigService.AddPermissionConfiguration(typeof(TeamsPermissions));
      permissionsConfigService.AddPermissionConfiguration(typeof(PipelinesPermissions));
      permissionsConfigService.AddPermissionConfiguration(typeof(SetupPermissions));
      permissionsConfigService.AddPermissionConfiguration(typeof(ManagePermissions));
      permissionsConfigService.AddPermissionConfiguration(typeof(ReportsPermissions));
      permissionsConfigService.AddPermissionConfiguration(typeof(PlatformPermissions));

      return permissionsConfigService;
    }
  }
}
