using System;

namespace Babesiosis.Core.Configurations.Configurations
{
  public class SecurityConfiguration
  {
    public string EncryptionKey { get; set; }
    public TimeSpan ResetPasswordExpiryTimeSpan { get; set; }
    public string ReCaptchaSecretKey { get; set; }
    public string EntraIdTenantId { get; set; }
    public string EntraIdClientId { get; set; }
    public string EntraIdClientSecret { get; set; }
    public string EntraIdRedirectUri { get; set; }
  }
}
