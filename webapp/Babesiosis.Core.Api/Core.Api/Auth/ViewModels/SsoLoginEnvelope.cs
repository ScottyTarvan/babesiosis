using System;

namespace Babesiosis.Core.Api.Auth.ViewModels
{
  // Internal wrapper persisted to the sso-login blob container. Carries the
  // creation timestamp so the exchange endpoint can enforce a short expiry.
  public class SsoLoginEnvelope
  {
    public DateTime CreatedUtc { get; set; }
    public LoginViewModel Login { get; set; }
  }
}
