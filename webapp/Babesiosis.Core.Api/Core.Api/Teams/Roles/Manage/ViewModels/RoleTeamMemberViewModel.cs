using Babesiosis.Core.ViewModels;
using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Teams.Roles.Manage.ViewModels
{
  /// <summary>One user currently assigned to a role.</summary>
  public class RoleTeamMemberViewModel : ViewModel
  {
    public Guid MemberId { get; set; }
    public string MemberFullName { get; set; }
    public string MemberEmail { get; set; }
  }

  /// <summary>
  /// The role members page payload — role name, the assigned users, and the
  /// capability echo the screen gates its assign / remove actions on.
  /// </summary>
  public class RoleTeamMembersResponseViewModel
  {
    public string RoleName { get; set; }
    public IEnumerable<RoleTeamMemberViewModel> Members { get; set; } = new List<RoleTeamMemberViewModel>();
    public Dictionary<string, bool> Permissions { get; set; } = new Dictionary<string, bool>();
  }
}
