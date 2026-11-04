using Babesiosis.Core.DynamicQuery.SqlParser.Filters;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Parsers
{
  public class OperatorFilterParser : Parser
  {
    public static bool IsOperator(JToken jToken)
    {
      return jToken != null
        && jToken.Type == JTokenType.String
        && Operators.OPERATORS.Contains(jToken.Value<string>()?.ToLower());
    }

    public static bool IsBetweenOperator(JToken jToken)
    {
      return jToken != null
        && jToken.Type == JTokenType.String
        && jToken.Value<string>()?.ToLower() == Operators.BETWEEN;
    }

    public List<SqlGenerator> Parse(JToken jToken)
    {
      var filter = new OperatorFilter
      {
        Operator = jToken.Value<string>()
      };

      return new List<SqlGenerator> { filter };
    }
  }
}
