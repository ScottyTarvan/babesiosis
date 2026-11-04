using System.Collections.Generic;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Api.Teams.Users.ViewModels
{
  public class UsersViewModel
  {
    public PagerViewModel Pager { get; set; }
    public IEnumerable<UserViewModel> Users { get; set; }

    /// <summary>
    /// Capability echo for the new web application's grid actions. Left null on
    /// the legacy endpoint, which has no use for it.
    /// </summary>
    public Dictionary<string, bool> Permissions { get; set; }
  }
}
