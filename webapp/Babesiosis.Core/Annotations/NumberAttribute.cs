using System;

namespace Babesiosis.Core.Annotations
{
  [AttributeUsage(AttributeTargets.Field | AttributeTargets.Property)]
  public class NumberAttribute : Attribute
  {
    public NumberAttribute(int number)
    {
      Number = number;
    }

    public int Number { get; set; }
  }
}
