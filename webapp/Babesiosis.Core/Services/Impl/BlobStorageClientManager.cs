using Azure.Core;
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Extensions;
using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Singleton manager for Azure Blob Storage clients with caching and connection pooling
  /// Addresses critical performance issues by eliminating client recreation overhead
  /// </summary>
  internal class BlobStorageClientManager
  {
    private static BlobStorageClientManager _instance;
    private static readonly object _lock = new object();

    private readonly IAppSettings _appSettings;
    private readonly ConcurrentDictionary<string, BlobServiceClient> _serviceClients;
    private readonly ConcurrentDictionary<string, BlobContainerClient> _containerClients;

    // One credential per process. Azure.Identity caches tokens inside the credential instance, so
    // creating a new one per client re-walks the whole probe chain and can pick a different credential
    // (and therefore a different tenant) each time - the main source of intermittent 401/403s.
    private readonly Lazy<TokenCredential> _credential;

    // User delegation keys are expensive (token + round trip to storage) and valid for up to 7 days.
    // Cache per storage account so SAS generation is not an auth call every time.
    private readonly ConcurrentDictionary<string, UserDelegationKeyCacheEntry> _delegationKeys
      = new ConcurrentDictionary<string, UserDelegationKeyCacheEntry>();

    /// <summary>
    /// Maximum lifetime Azure allows for a user delegation key / user delegation SAS.
    /// </summary>
    public static readonly TimeSpan MaxUserDelegationSasLifetime = TimeSpan.FromDays(7);

    /// <summary>
    /// Private constructor for singleton pattern
    /// </summary>
    private BlobStorageClientManager(IAppSettings appSettings)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _serviceClients = new ConcurrentDictionary<string, BlobServiceClient>();
      _containerClients = new ConcurrentDictionary<string, BlobContainerClient>();
      _credential = new Lazy<TokenCredential>(BuildCredential, LazyThreadSafetyMode.ExecutionAndPublication);
    }

    /// <summary>
    /// Gets the singleton instance of BlobStorageClientManager
    /// </summary>
    public static BlobStorageClientManager GetInstance(IAppSettings appSettings)
    {
      if (_instance == null)
      {
        lock (_lock)
        {
          if (_instance == null)
          {
            _instance = new BlobStorageClientManager(appSettings);
          }
        }
      }

      return _instance;
    }

    /// <summary>
    /// Gets or creates a cached BlobServiceClient for the given connection string
    /// </summary>
    public BlobServiceClient GetServiceClient(string connectionString = null)
    {
      var connection = connectionString.HasValue() ? connectionString : _appSettings.Connections.Storage;

      // Use connection string as cache key
      return _serviceClients.GetOrAdd(connection, (conn) => CreateServiceClientInternal(conn));
    }

    /// <summary>
    /// Gets or creates a cached BlobContainerClient for the given container name and connection
    /// </summary>
    public BlobContainerClient GetContainerClient(string containerName, string connectionString = null)
    {
      var connection = connectionString.HasValue() ? connectionString : _appSettings.Connections.Storage;
      var cacheKey = $"{connection}::{containerName}";

      return _containerClients.GetOrAdd(cacheKey, (key) =>
      {
        var serviceClient = GetServiceClient(connection);
        return serviceClient.GetBlobContainerClient(containerName);
      });
    }

    /// <summary>
    /// Clears all cached clients - primarily for testing purposes
    /// </summary>
    public void ClearCache()
    {
      _serviceClients.Clear();
      _containerClients.Clear();
      _delegationKeys.Clear();
    }

    /// <summary>
    /// Creates a new BlobServiceClient with proper retry configuration and credential selection
    /// </summary>
    private BlobServiceClient CreateServiceClientInternal(string connection)
    {
      var blobConfig = _appSettings.BlobStorage;

      // Configure retry options
      var options = new BlobClientOptions();
      options.Retry.MaxRetries = blobConfig.MaxRetries;
      options.Retry.Delay = TimeSpan.FromSeconds(blobConfig.RetryDelaySeconds);
      options.Retry.NetworkTimeout = TimeSpan.FromSeconds(blobConfig.OperationTimeoutSeconds);

      // Determine if connection string contains account key (key-based access)
      if (IsKeyAccess(connection))
      {
        return new BlobServiceClient(connection, options);
      }
      else
      {
        // Managed identity access - use appropriate credential based on environment
        return new BlobServiceClient(new Uri(connection), _credential.Value, options);
      }
    }

    /// <summary>
    /// Builds the process-wide credential - see AzureCredentialFactory for why this must not be per-client.
    /// </summary>
    private TokenCredential BuildCredential()
    {
      var blobConfig = _appSettings.BlobStorage;

      return AzureCredentialFactory.GetCredential(
        blobConfig.TenantId,
        blobConfig.ManagedIdentityClientId);
    }

    /// <summary>
    /// Gets a cached user delegation key for the account behind <paramref name="serviceClient"/>.
    /// Keys are reused until shortly before they expire, so SAS generation does not hit Entra ID
    /// and the storage service on every link.
    /// </summary>
    public async Task<UserDelegationKey> GetUserDelegationKeyAsync(
      BlobServiceClient serviceClient,
      DateTimeOffset startsOn,
      DateTimeOffset expiresOn)
    {
      var cacheKey = serviceClient.Uri.Host;

      if (_delegationKeys.TryGetValue(cacheKey, out var cached) && cached.Covers(startsOn, expiresOn))
      {
        return cached.Key;
      }

      // Request the maximum lifetime so the key is reusable, regardless of this caller's window.
      // Azure measures the 7 day cap from the start time, so it must be based on keyStart - not
      // "now" - or the request is rejected outright.
      var keyStart = startsOn;
      var keyEnd = keyStart.Add(MaxUserDelegationSasLifetime);

      var key = await serviceClient.GetUserDelegationKeyAsync(keyStart, keyEnd, default);
      var entry = new UserDelegationKeyCacheEntry(key.Value, keyStart, keyEnd);
      _delegationKeys[cacheKey] = entry;

      return entry.Key;
    }

    private sealed class UserDelegationKeyCacheEntry
    {
      private readonly DateTimeOffset _validFrom;
      private readonly DateTimeOffset _validTo;

      internal UserDelegationKeyCacheEntry(UserDelegationKey key, DateTimeOffset validFrom, DateTimeOffset validTo)
      {
        Key = key;
        _validFrom = validFrom;
        _validTo = validTo;
      }

      internal UserDelegationKey Key { get; }

      /// <summary>
      /// True when the cached key can sign a SAS for the requested window, with a safety margin
      /// so a key about to expire is not handed out.
      /// </summary>
      internal bool Covers(DateTimeOffset startsOn, DateTimeOffset expiresOn)
      {
        return startsOn >= _validFrom && expiresOn <= _validTo.AddMinutes(-15);
      }
    }

    /// <summary>
    /// Determines if the connection string uses key-based access
    /// Example: DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net
    /// </summary>
    private bool IsKeyAccess(string connection)
    {
      if (string.IsNullOrWhiteSpace(connection))
        return false;

      var lowerConnection = connection.ToLower();
      return lowerConnection.Contains("accountkey")
        && lowerConnection.Contains("accountname")
        && lowerConnection.Contains("defaultendpointsprotocol");
    }
  }
}
