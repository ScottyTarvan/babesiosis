using System;

namespace Babesiosis.Core.Configurations.Configurations
{
  public class JwtConfiguration
  {
    public string Audience { get; set; }
    public TimeSpan ExpiryTimeSpan { get; set; }
    public string Issuer { get; set; }
    public TimeSpan RefreshTokenExpiryTimeSpan { get; set; }
    public string SecurityKey { get; set; }
  }
}
