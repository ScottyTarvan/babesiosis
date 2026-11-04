using System;
using System.Collections.Generic;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Api.Teams.Users.ViewModels
{
  public class UserRolesViewModel
  {
    public IEnumerable<TreeItemViewModel> Roles { get; set; }
  }
}
