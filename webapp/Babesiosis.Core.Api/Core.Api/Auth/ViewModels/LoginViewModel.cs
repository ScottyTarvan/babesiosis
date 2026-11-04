using Babesiosis.Core.ViewModels;
using System;

namespace Babesiosis.Core.Api.Auth.ViewModels
{
  public class LoginViewModel
  {
    public bool Passed { get; set; }
    public string Message { get; set; }
    public UserViewModel User { get; set; }
    public string AuthToken { get; set; }
    public string RefreshToken { get; set; }
  }
}
