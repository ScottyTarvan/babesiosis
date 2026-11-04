using System.ComponentModel;
using Babesiosis.Core.Annotations;

namespace Babesiosis.Core.Models.Domain
{
  public enum LogicalOperator: byte
  {
    None = 0,
    [Symbol("<")]
    [Description("Less Than")]
    LessThan = 1,
    [Symbol("<=")]
    [Description("Less Than Equals")]
    LessThanEquals = 2,
    [Symbol("=")]
    [Description("Equals")]
    Equals = 3,
    [Symbol("!=")]
    [Description("Not Equals")]
    NotEquals = 4,
    [Symbol(">")]
    [Description("Greater Than")]
    GreaterThan = 5,
    [Symbol(">=")]
    [Description("Greater Than Equals")]
    GreaterThanEquals = 6,
    [Symbol("between")]
    [Description("Between")]
    Between = 7
  }
}
