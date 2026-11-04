using System;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Api.Teams.Roles.ViewModels
{
  public class RoleViewModel : NameValueViewModel<string>
  {
    public bool HasPermissions { get; set; }
    public bool IsDefault { get; set; }
  }
}
