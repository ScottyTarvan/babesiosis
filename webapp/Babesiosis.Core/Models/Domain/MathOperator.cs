using System.ComponentModel;
using Babesiosis.Core.Annotations;

namespace Babesiosis.Core.Models.Domain
{
  public enum MathOperator : byte
  {
    None = 0,
    [Symbol("+")]
    [Description("Add")]
    Add = 1,
    [Symbol("-")]
    [Description("Subtract")]
    Subtract = 2,
    [Symbol("/")]
    [Description("Divide")]
    Divide = 3,
    [Symbol("*")]
    [Description("Multiply")]
    Multiply = 4
  }
}
