using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum SortOrder : short
  {
    None = 0,
    [Description("ASC")]
    Ascending = 1,
    [Description("DESC")]
    Descending = 2,
    [Description("NULL")]
    Null = 3
  }
}
