namespace Babesiosis.Core.Configurations.Configurations
{
  public class KeyVaultConfiguration
  {
    public int MaxRetries { get; set; } = 5;
    public int RetryDelaySeconds { get; set; } = 2;
    public int MaxRetryDelaySeconds { get; set; } = 16;
    public string RetryMode { get; set; } = "Exponential";
    public int OperationTimeoutSeconds { get; set; } = 120;
    public string TenantId { get; set; }
    public string ManagedIdentityClientId { get; set; }
  }
}
