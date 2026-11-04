using Babesiosis.Core.ViewModels;
using System.IO;

namespace Babesiosis.Core.Teams.Users.Commands
{
  public class UploadAvatarCommand
  {
    public Stream File { get; set; }
    public string ContentType { get; set; }
  }
}
