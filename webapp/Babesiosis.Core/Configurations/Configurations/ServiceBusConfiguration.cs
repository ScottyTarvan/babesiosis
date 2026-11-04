namespace Babesiosis.Core.Configurations.Configurations
{
  /// <summary>
  /// Configuration settings for Azure Service Bus service operations
  /// </summary>
  public class ServiceBusConfiguration
  {
    /// <summary>
    /// Maximum number of retry attempts for failed operations (default: 3)
    /// </summary>
    public int MaxRetries { get; set; } = 3;

    /// <summary>
    /// Maximum delay between retries in seconds (default: 30)
    /// </summary>
    public int MaxDelaySeconds { get; set; } = 30;

    /// <summary>
    /// Retry mode: "Exponential" or "Fixed" (default: "Exponential")
    /// </summary>
    public string RetryMode { get; set; } = "Exponential";

    /// <summary>
    /// Network timeout for Service Bus operations in seconds (default: 120)
    /// </summary>
    public int NetworkTimeoutSeconds { get; set; } = 120;

    /// <summary>
    /// Entra ID tenant that owns the Service Bus namespace. Must be set when the namespace lives in a
    /// tenant other than the developer's home tenant, otherwise the credential asks the wrong tenant
    /// for a token and auth fails intermittently. Falls back to AZURE_TENANT_ID when not configured.
    /// </summary>
    public string TenantId { get; set; }

    /// <summary>
    /// Client id of the user-assigned managed identity to use in Production.
    /// Leave empty to use the system-assigned identity.
    /// </summary>
    public string ManagedIdentityClientId { get; set; }
  }
}
