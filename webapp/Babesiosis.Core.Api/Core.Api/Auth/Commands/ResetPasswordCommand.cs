namespace Babesiosis.Core.Api.Auth.Commands
{
  public class ResetPasswordCommand
  {
    public string Token { get; set; }
    public string Password { get; set; }
  }
}
