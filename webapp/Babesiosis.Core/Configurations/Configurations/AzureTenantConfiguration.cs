namespace Babesiosis.Core.Configurations.Configurations
{
  /// <summary>
  /// Azure AD tenant that hosts the resources accessed via managed identity / DefaultAzureCredential.
  /// Leave empty to fall back to the credential's own default tenant resolution.
  /// </summary>
  public class AzureTenantConfiguration
  {
    public string TenantId { get; set; }
  }
}
