using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum FtpOperation
  {
    None = 0,
    [Description("Upload")]
    Upload = 1,
    [Description("Download")]
    Download = 2,
    [Description("Move")]
    Move = 3,
  }
}
