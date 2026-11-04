using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum ReferentialAction : short
  {
    [Description("NONE")]
    None = 0,
    [Description("NO ACTION")]
    NoAction = 1,
    [Description("CASCADE")]
    Cascade = 2,
    [Description("SET NULL")]
    SetNull = 3,
    [Description("SET DEFAULT")]
    SetDefault = 4
  }
}
