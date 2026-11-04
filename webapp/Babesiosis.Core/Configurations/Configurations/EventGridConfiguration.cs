namespace Babesiosis.Core.Configurations.Configurations
{
  public class EventGridConfiguration
  {
    public string EndPoint { get; set; }
    public string Key { get; set; }
    public int MaxRetries { get; set; } = 3;
    public int RetryDelaySeconds { get; set; } = 2;
    public int MaxRetryDelaySeconds { get; set; } = 30;
    public string RetryMode { get; set; } = "Exponential";
    public int OperationTimeoutSeconds { get; set; } = 120;
    public bool UseKeyBasedAuth { get; set; } = true;
    public string TenantId { get; set; }
    public string ManagedIdentityClientId { get; set; }
  }
}
