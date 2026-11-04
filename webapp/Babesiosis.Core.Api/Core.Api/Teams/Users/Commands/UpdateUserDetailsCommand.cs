using System.IO;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Teams.Users.Commands
{
  public class UpdateUserDetailsCommand
  {
    public UserViewModel User { get; set; }

    [Newtonsoft.Json.JsonIgnore()]
    public Stream File { get; set; }
  }
}
