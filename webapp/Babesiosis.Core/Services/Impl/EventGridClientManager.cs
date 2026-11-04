using Azure;
using Azure.Core;
using Azure.Messaging.EventGrid;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Extensions;
using System;
using System.Collections.Concurrent;

namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Singleton manager for Azure Event Grid clients with caching and connection pooling
  /// Addresses critical performance issues by eliminating client recreation overhead
  /// </summary>
  internal class EventGridClientManager
  {
    private static EventGridClientManager _instance;
    private static readonly object _lock = new object();

    private readonly IAppSettings _appSettings;
    private readonly ConcurrentDictionary<string, EventGridPublisherClient> _clients;

    /// <summary>
    /// Private constructor for singleton pattern
    /// </summary>
    private EventGridClientManager(IAppSettings appSettings)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _clients = new ConcurrentDictionary<string, EventGridPublisherClient>();
    }

    /// <summary>
    /// Gets the singleton instance of EventGridClientManager
    /// </summary>
    public static EventGridClientManager GetInstance(IAppSettings appSettings)
    {
      if (_instance == null)
      {
        lock (_lock)
        {
          if (_instance == null)
          {
            _instance = new EventGridClientManager(appSettings);
          }
        }
      }

      return _instance;
    }

    /// <summary>
    /// Gets or creates a cached EventGridPublisherClient for the given endpoint
    /// </summary>
    public EventGridPublisherClient GetPublisherClient(string endpoint = null, string accessKey = null)
    {
      var endpointUrl = endpoint.HasValue() ? endpoint : _appSettings.EventGrid.EndPoint;
      var key = accessKey.HasValue() ? accessKey : _appSettings.EventGrid.Key;

      // Use endpoint as cache key (auth method is determined at creation time)
      var cacheKey = $"{endpointUrl}::{(key.HasValue() ? "key" : "managed")}";

      return _clients.GetOrAdd(cacheKey, (k) => CreatePublisherClientInternal(endpointUrl, key));
    }

    /// <summary>
    /// Clears all cached clients - primarily for testing purposes
    /// </summary>
    public void ClearCache()
    {
      _clients.Clear();
    }

    /// <summary>
    /// Creates a new EventGridPublisherClient with proper retry configuration and authentication
    /// </summary>
    private EventGridPublisherClient CreatePublisherClientInternal(string endpoint, string accessKey)
    {
      var eventGridConfig = _appSettings.EventGrid;

      // Configure retry options
      var options = new EventGridPublisherClientOptions();
      options.Retry.MaxRetries = eventGridConfig.MaxRetries;
      options.Retry.Delay = TimeSpan.FromSeconds(eventGridConfig.RetryDelaySeconds);
      options.Retry.MaxDelay = TimeSpan.FromSeconds(eventGridConfig.MaxRetryDelaySeconds);
      options.Retry.Mode = eventGridConfig.RetryMode?.ToLowerInvariant() == "exponential"
        ? RetryMode.Exponential
        : RetryMode.Fixed;
      options.Retry.NetworkTimeout = TimeSpan.FromSeconds(eventGridConfig.OperationTimeoutSeconds);

      // Determine authentication method
      // Use key-based auth if UseKeyBasedAuth is true OR if an access key is provided
      if (eventGridConfig.UseKeyBasedAuth || accessKey.HasValue())
      {
        // Key-based authentication
        var credential = new AzureKeyCredential(accessKey);
        return new EventGridPublisherClient(new Uri(endpoint), credential, options);
      }
      else
      {
        // Shared, tenant-pinned credential - see AzureCredentialFactory for why this must not be per-client
        TokenCredential credential = AzureCredentialFactory.GetCredential(
          eventGridConfig.TenantId,
          eventGridConfig.ManagedIdentityClientId);

        return new EventGridPublisherClient(new Uri(endpoint), credential, options);
      }
    }
  }
}
