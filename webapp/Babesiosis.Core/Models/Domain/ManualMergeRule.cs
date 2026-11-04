using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum ManualMergeRule : byte
  {
    None = 0,
    [Description("Manual | Loaded")]
    ManualLoaded = 1,
    [Description("Loaded | Manual")]
    LoadedManual = 2,
    [Description("Manual Only")]
    ManualOnly = 3,
    [Description("Loaded Only")]
    LoadedOnly = 4,
  }
}
