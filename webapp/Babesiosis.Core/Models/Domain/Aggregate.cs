using System.ComponentModel;
using Babesiosis.Core.Annotations;

namespace Babesiosis.Core.Models.Domain
{
  public enum Aggregate: byte
  {
    None = 0,
    [Symbol("AVG")]
    [Description("Average")]
    Average = 1,
    [Symbol("COUNT")]
    [Description("Count")]
    Count = 2,
    [Symbol("SUM")]
    [Description("Sum")]
    Sum = 3
  }
}
