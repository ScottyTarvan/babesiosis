using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum FileType : byte
  {
    None = 0,
    [Description("Excel")]
    Excel = 1,
    [Description("Csv")]
    Csv = 2
  }
}
