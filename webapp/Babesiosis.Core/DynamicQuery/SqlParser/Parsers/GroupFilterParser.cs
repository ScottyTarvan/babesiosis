using Babesiosis.Core.DynamicQuery.SqlParser.Filters;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Parsers
{
  public class GroupFilterParser : Parser
  {
    public static bool IsGroup(JToken jToken)
    {
      return jToken != null
        && jToken.Type == JTokenType.String
        && Operators.LOGIC_OPERATORS.Contains(jToken.Value<string>()?.ToLower());
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
