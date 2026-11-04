using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum EditorType : short
  {
    None = 0,
    [Description("Default")]
    Default = 1,
    [Description("Lookup")]
    Lookup = 2
   
  }
}
