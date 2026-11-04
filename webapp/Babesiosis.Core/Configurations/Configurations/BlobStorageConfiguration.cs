namespace Babesiosis.Core.Configurations.Configurations
{
  public class BlobStorageConfiguration
  {
    public int MaxRetries { get; set; } = 3;
    public int RetryDelaySeconds { get; set; } = 2;
    public int OperationTimeoutSeconds { get; set; } = 120;
    public int DefaultSasExpirationHours { get; set; } = 24;
    public int NonExpiringSasExpirationYears { get; set; } = 5;
    public int BatchOperationSize { get; set; } = 256;
    public bool EnableContentValidation { get; set; } = false;
    public string TenantId { get; set; }
    public string ManagedIdentityClientId { get; set; }
  }
}
