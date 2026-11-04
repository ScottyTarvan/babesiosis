using Azure.Core;
using Azure.Messaging.ServiceBus;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Extensions;
using System;
using System.Collections.Concurrent;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Singleton manager for Azure Service Bus clients with caching and connection pooling
  /// Addresses critical performance issues by eliminating client recreation overhead
  /// </summary>
  internal class ServiceBusClientManager
  {
    private static ServiceBusClientManager _instance;
    private static readonly object _lock = new object();

    private readonly IAppSettings _appSettings;
    private readonly ConcurrentDictionary<string, ServiceBusClient> _clients;
    private readonly ConcurrentDictionary<string, ServiceBusSender> _senders;

    /// <summary>
    /// Private constructor for singleton pattern
    /// </summary>
    private ServiceBusClientManager(IAppSettings appSettings)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _clients = new ConcurrentDictionary<string, ServiceBusClient>();
      _senders = new ConcurrentDictionary<string, ServiceBusSender>();
    }

    /// <summary>
    /// Gets the singleton instance of ServiceBusClientManager
    /// </summary>
    public static ServiceBusClientManager GetInstance(IAppSettings appSettings)
    {
      if (_instance == null)
      {
        lock (_lock)
        {
          if (_instance == null)
          {
            _instance = new ServiceBusClientManager(appSettings);
          }
        }
      }

      return _instance;
    }

    /// <summary>
    /// Gets or creates a cached ServiceBusClient for the given connection string and retry options
    /// </summary>
    public ServiceBusClient GetServiceBusClient(string connectionString = null, ServiceBusRetryOptions retryOptions = null)
    {
      var connection = connectionString.HasValue() ? connectionString : _appSettings.Connections.ServiceBus;

      // Use connection string as cache key (retry options are set on client creation)
      return _clients.GetOrAdd(connection, (conn) => CreateServiceBusClientInternal(conn, retryOptions));
    }

    /// <summary>
    /// Gets or creates a cached ServiceBusSender for the given queue/topic name and connection
    /// </summary>
    public ServiceBusSender GetSender(string queueOrTopicName, string connectionString = null, ServiceBusRetryOptions retryOptions = null)
    {
      var connection = connectionString.HasValue() ? connectionString : _appSettings.Connections.ServiceBus;
      var cacheKey = $"{connection}::{queueOrTopicName}";

      return _senders.GetOrAdd(cacheKey, (key) =>
      {
        var client = GetServiceBusClient(connection, retryOptions);
        return client.CreateSender(queueOrTopicName);
      });
    }

    /// <summary>
    /// Clears all cached clients and senders - primarily for testing purposes
    /// </summary>
    public void ClearCache()
    {
      _clients.Clear();
      _senders.Clear();
    }

    /// <summary>
    /// Creates a new ServiceBusClient with proper retry configuration and credential selection
    /// </summary>
    private ServiceBusClient CreateServiceBusClientInternal(string connection, ServiceBusRetryOptions retryOptions = null)
    {
      var serviceBusConfig = _appSettings.ServiceBus;

      // Configure retry options - use provided or load from config
      var options = new ServiceBusClientOptions();

      if (retryOptions != null)
      {
        options.RetryOptions = retryOptions;
      }
      else
      {
        options.RetryOptions = new ServiceBusRetryOptions()
        {
          MaxRetries = serviceBusConfig.MaxRetries,
          MaxDelay = TimeSpan.FromSeconds(serviceBusConfig.MaxDelaySeconds),
          Mode = serviceBusConfig.RetryMode?.ToLowerInvariant() == "exponential"
            ? ServiceBusRetryMode.Exponential
            : ServiceBusRetryMode.Fixed
        };
      }

      // Set network timeout
      options.RetryOptions.TryTimeout = TimeSpan.FromSeconds(serviceBusConfig.NetworkTimeoutSeconds);

      // Determine if connection string contains shared access key (key-based access)
      if (IsKeyAccess(connection))
      {
        return new ServiceBusClient(connection, options);
      }
      else
      {
        // Shared, tenant-pinned credential - see AzureCredentialFactory for why this must not be per-client
        TokenCredential credential = AzureCredentialFactory.GetCredential(
          serviceBusConfig.TenantId,
          serviceBusConfig.ManagedIdentityClientId);

        return new ServiceBusClient(connection, credential, options);
      }
    }

    /// <summary>
    /// Determines if the connection string uses key-based access
    /// Example: Endpoint=sb://namespace.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=...
    /// </summary>
    private bool IsKeyAccess(string connection)
    {
      if (string.IsNullOrWhiteSpace(connection))
        return false;

      var lowerConnection = connection.ToLower();
      return lowerConnection.Contains("sharedaccesskey")
        && lowerConnection.Contains("endpoint");
    }
  }
}
