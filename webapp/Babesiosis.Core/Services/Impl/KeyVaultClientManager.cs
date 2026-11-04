using Azure.Core;
using Azure.Security.KeyVault.Secrets;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Extensions;
using System;
using System.Collections.Concurrent;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Singleton manager for Azure Key Vault clients with caching and connection pooling
  /// Addresses critical performance issues by eliminating client recreation overhead
  /// </summary>
  internal class KeyVaultClientManager
  {
    private static KeyVaultClientManager _instance;
    private static readonly object _lock = new object();

    private readonly IAppSettings _appSettings;
    private readonly ConcurrentDictionary<string, SecretClient> _clients;

    /// <summary>
    /// Private constructor for singleton pattern
    /// </summary>
    private KeyVaultClientManager(IAppSettings appSettings)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _clients = new ConcurrentDictionary<string, SecretClient>();
    }

    /// <summary>
    /// Gets the singleton instance of KeyVaultClientManager
    /// </summary>
    public static KeyVaultClientManager GetInstance(IAppSettings appSettings)
    {
      if (_instance == null)
      {
        lock (_lock)
        {
          if (_instance == null)
          {
            _instance = new KeyVaultClientManager(appSettings);
          }
        }
      }

      return _instance;
    }

    /// <summary>
    /// Gets or creates a cached SecretClient for the given vault URL
    /// </summary>
    public SecretClient GetSecretClient(string vaultUrl = null)
    {
      var vault = vaultUrl.HasValue() ? vaultUrl : _appSettings.Connections.KeyVault;

      // Use vault URL as cache key
      return _clients.GetOrAdd(vault, (vaultUri) => CreateSecretClientInternal(vaultUri));
    }

    /// <summary>
    /// Clears all cached clients - primarily for testing purposes
    /// </summary>
    public void ClearCache()
    {
      _clients.Clear();
    }

    /// <summary>
    /// Creates a new SecretClient with proper retry configuration and credential selection
    /// </summary>
    private SecretClient CreateSecretClientInternal(string vaultUrl)
    {
      var keyVaultConfig = _appSettings.KeyVault;

      // Configure retry options
      var options = new SecretClientOptions();
      options.Retry.MaxRetries = keyVaultConfig.MaxRetries;
      options.Retry.Delay = TimeSpan.FromSeconds(keyVaultConfig.RetryDelaySeconds);
      options.Retry.MaxDelay = TimeSpan.FromSeconds(keyVaultConfig.MaxRetryDelaySeconds);
      options.Retry.Mode = keyVaultConfig.RetryMode?.ToLowerInvariant() == "exponential"
        ? RetryMode.Exponential
        : RetryMode.Fixed;
      options.Retry.NetworkTimeout = TimeSpan.FromSeconds(keyVaultConfig.OperationTimeoutSeconds);

      // Shared, tenant-pinned credential - see AzureCredentialFactory for why this must not be per-client
      TokenCredential credential = AzureCredentialFactory.GetCredential(
        keyVaultConfig.TenantId,
        keyVaultConfig.ManagedIdentityClientId);

      return new SecretClient(new Uri(vaultUrl), credential, options);
    }
  }
}
