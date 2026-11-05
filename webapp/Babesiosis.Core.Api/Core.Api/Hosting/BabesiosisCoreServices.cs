using AutoMapper;
using AutoMapper.EquivalencyExpression;
using Babesiosis.Agents;
using Babesiosis.Core.Api.Auth.Mapping;
using Babesiosis.Core.Api.Teams.Roles.Mapping;
using Babesiosis.Core.Api.Teams.Users.Mapping;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Babesiosis.Core.Services.Azure;
using Babesiosis.Core.Services.Impl;
using Babesiosis.Core.Services.Providers;
using Babesiosis.Core.Teams.Services;
using Babesiosis.Core.Teams.Services.Providers;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging.Abstractions;
using System;

namespace Babesiosis.Core.Api.Hosting
{
  /// <summary>
  /// The services every function app built on Core.Api registers: settings, the AutoMapper
  /// profiles, and the platform and permission services the controllers depend on. Each app
  /// still owns its host concerns (telemetry, logging, middleware) and its function-specific
  /// controller scan.
  /// </summary>
  public static class BabesiosisCoreServices
  {
    /// <param name="configureMapper">Extra AutoMapper profiles of the calling app.</param>
    public static IServiceCollection AddBabesiosisCore(this IServiceCollection services,
      Action<IMapperConfigurationExpression> configureMapper = null)
    {
      IAppSettingsService appSettingsService = new AppSettingsService(AppContext.BaseDirectory);
      services.AddSingleton(appSettingsService);

      var mapperConfig = new MapperConfiguration(config =>
      {
        config.AddCollectionMappers();
        config.AddProfile(new UsersProfile());
        config.AddProfile(new RolesProfile());
        config.AddProfile(new AuthProfile());
        configureMapper?.Invoke(config);
      },
      NullLoggerFactory.Instance);

      IMapper mapper = mapperConfig.CreateMapper();
      services.AddSingleton(mapper);

      services.Add(new ServiceDescriptor(typeof(IPasswordEncryptor), PasswordEncryptorProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(IJwtTokenGenerator), JwtTokenGeneratorProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(ITableStorageService), TableStorageServiceProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(IBlobStorageService), BlobStorageServiceProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(IServiceBusService), ServiceBusServiceProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(IEventGridService), EventGridServiceProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(IDbContextService), DbContextServiceProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(IEmailService), EmailServiceProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(IEmailFactory), EmailFactoryProvider.GetService, ServiceLifetime.Transient));
      services.Add(new ServiceDescriptor(typeof(ITeamsService), TeamsServiceProvider.GetService, ServiceLifetime.Transient));
      // Scoped: one per function invocation, which is the lifetime the
      // pre-authorization flag must have.
      services.AddScoped<IPermissionContext, PermissionContext>();

      services.Add(new ServiceDescriptor(typeof(IUserPermissionsService), UserPermissionsServiceProvider.GetService, ServiceLifetime.Transient));

      // Code-declared permissions, the whole catalogue via the one shared provider, so every
      // app resolves the shared permissions cache identically.
      services.Add(new ServiceDescriptor(typeof(IPermissionsConfigService),
        PermissionsConfigServiceProvider.GetService, ServiceLifetime.Singleton));

      services.Add(new ServiceDescriptor(typeof(IUserPermissionItemsService), UserPermissionItemsServiceProvider.GetService, ServiceLifetime.Transient));

      // Singleton: the per-instance L1 dictionary it holds must outlive a
      // single request, or every request pays the blob round-trip that the L1
      // exists to avoid. Blob Storage remains the layer shared across function
      // app instances. The provider's Debugger.IsAttached switch (blob-backed
      // vs. LocalUserPermissionsCacheService) is therefore evaluated once, at
      // first resolution, not per request.
      services.Add(new ServiceDescriptor(typeof(IUserPermissionsCacheService), UserPermissionsCacheServiceProvider.GetService, ServiceLifetime.Singleton));
      services.Add(new ServiceDescriptor(typeof(IKeyVaultService), KeyVaultServiceProvider.GetService, ServiceLifetime.Transient));

      // Controller scans only discover controllers named in a function's constructor. The
      // Teams Manage layer delegates to these three — the create, edit and list logic lives in
      // exactly one place — but reaches them one level down, from a controller constructor
      // rather than a function constructor, which a scan never walks.
      services.AddTransient<Babesiosis.Core.Api.Teams.Users.Controllers.AddUserController>();
      services.AddTransient<Babesiosis.Core.Api.Teams.Users.Controllers.EditUserController>();
      services.AddTransient<Babesiosis.Core.Api.Teams.Users.Controllers.GetUsersController>();

      // The article question agent (OpenRouter models, vector search on dbo.article). Nothing
      // calls OpenRouter until a question is asked, and AppSettings:AiAgents:Enabled gates that.
      services.AddBabesiosisAgents();

      return services;
    }
  }
}
