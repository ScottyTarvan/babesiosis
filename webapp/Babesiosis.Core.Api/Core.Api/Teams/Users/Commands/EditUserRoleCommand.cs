using System;
using Babesiosis.Core.Api.Teams.Users.ViewModels;

namespace Babesiosis.Core.Api.Teams.Users.Commands
{
  public class EditUserRoleCommand
  {
    public Guid UserId { get; set; }
    public UserRoleViewModel Role { get; set; }
  }
}
