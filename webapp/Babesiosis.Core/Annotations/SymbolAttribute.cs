using System;
using System.Collections.Generic;
using System.Text;

namespace Babesiosis.Core.Annotations
{
  [AttributeUsage(AttributeTargets.Field | AttributeTargets.Property)]
  public class SymbolAttribute : Attribute
  {
    public SymbolAttribute(string symbol)
    {
      Symbol = symbol;
    }

    public string Symbol { get; set; }
  }
}
