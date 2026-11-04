using Babesiosis.Core.DynamicQuery.SqlParser.Parsers;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

namespace Babesiosis.Core.DynamicQuery.SqlParser
{
  public abstract class Parser
  {
    public static List<SqlGenerator> Parse(JToken jToken)
    {
      if (FieldFilterParser.IsField(jToken))
      {
        return new FieldFilterParser().Parse(jToken);
      }
      else if (OperatorFilterParser.IsOperator(jToken))
      {
        return new OperatorFilterParser().Parse(jToken);
      }
      else if (BetweenValueFilterParser.IsBetweenValue(jToken))
      {
        return new BetweenValueFilterParser().Parse(jToken);
      }
      else if (ValueFilterParser.IsValue(jToken))
      { 
        return new ValueFilterParser().Parse(jToken);
      }
      else if (GroupFilterParser.IsGroup(jToken))
      {
        return new GroupFilterParser().Parse(jToken);
      }
      else if (ArrayFilterParser.IsArray(jToken))
      {
        return new ArrayFilterParser().Parse(jToken);
      }

      return new List<SqlGenerator>();
    }

    
  }
}
