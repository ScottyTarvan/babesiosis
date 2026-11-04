using Azure.Core;
using Azure.Identity;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Extensions;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using System;
using System.Diagnostics;

namespace Babesiosis.Core.Data
{
  public class DbContextService : IDbContextService
  {
    private static readonly DefaultAzureCredential _credential =
      new DefaultAzureCredential(new DefaultAzureCredentialOptions
      {
        ExcludeInteractiveBrowserCredential = true
      });

    private static AccessToken? _cachedToken;
    private static DateTimeOffset _expiresOn = DateTimeOffset.MinValue;

    private readonly IAppSettingsService _appSettingsService;

    public DbContextService(IAppSettingsService appSettingsService)
    {
      _appSettingsService = appSettingsService;
    }
    
    public TDbContext CreateDbContext<TDbContext>(bool trackChanges = false)
      where TDbContext : DbContext
    {
      IAppSettings appSettings = _appSettingsService.GetAppSettings();
      var cnString = _appSettingsService.GetAppSettings().Connections.Database;
      var cnBuilder = new SqlConnectionStringBuilder(cnString);
      var connection = new SqlConnection(cnBuilder.ConnectionString);
      
      return CreateDbContext<TDbContext>(connection, trackChanges);
    }

    public TDbContext CreateDbContext<TDbContext>(string cnString, bool trackChanges = false)
     where TDbContext : DbContext
    {
      var cnBuilder = new SqlConnectionStringBuilder(cnString);
      var connection = new SqlConnection(cnBuilder.ConnectionString);

      return CreateDbContext<TDbContext>(connection, trackChanges);
    }

    public TDbContext CreateDbContext<TDbContext>(SqlConnection connection, bool trackChanges = false)
      where TDbContext : DbContext
    {
      var cnBuilder = new SqlConnectionStringBuilder(connection.ConnectionString);

      if (Debugger.IsAttached && !cnBuilder.IsSqlAuthentication() && cnBuilder.Authentication == SqlAuthenticationMethod.NotSpecified)
      {
        connection.AccessToken = GetToken(new[] { "https://database.windows.net//.default" });
      }
      
      var optionsBuilder = new DbContextOptionsBuilder<TDbContext>();
      optionsBuilder
        .UseSqlServer(connection, opt => opt.EnableRetryOnFailure())
        .UseLoggerFactory(DbLoggerFactory.Create());

      var dbContext = (TDbContext)Activator.CreateInstance(typeof(TDbContext), optionsBuilder.Options);

      dbContext.ChangeTracker.QueryTrackingBehavior =
        trackChanges ? QueryTrackingBehavior.TrackAll
        : QueryTrackingBehavior.NoTracking;

      return dbContext;
    }

    private string GetToken(string[] scopes)
    {
      var now = DateTimeOffset.UtcNow;
      // refresh if never fetched, or within 5 minutes of expiry
      if (!_cachedToken.HasValue || _expiresOn <= now.AddMinutes(5))
      {
        var trc = new TokenRequestContext(scopes);
        var token = _credential.GetToken(trc, default);
        _cachedToken = token;
        _expiresOn = token.ExpiresOn;
      }

      return _cachedToken.Value.Token;
    }
  }
}
