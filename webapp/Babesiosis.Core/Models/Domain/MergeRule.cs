using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum MergeRule : byte
  {
    None = 0,
    [Description("Row")]
    Row = 1,
    [Description("Set")]
    Set = 2,
  }
}
