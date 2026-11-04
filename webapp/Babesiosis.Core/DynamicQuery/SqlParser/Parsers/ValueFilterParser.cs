using Babesiosis.Core.DynamicQuery.SqlParser.Filters;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Parsers
{
  public class ValueFilterParser : Parser
  {
    /// <summary>
    /// A value comes after an operator 
    /// </summary>
    /// <param name="jToken"></param>
    /// <returns></returns>
    public static bool IsValue(JToken jToken)
    {
      return jToken != null
        && OperatorFilterParser.IsOperator(jToken.Previous)
        && jToken.Type != JTokenType.Array;
    }

    public List<SqlGenerator> Parse(JToken jToken)
    {
      var filter = new ValueFilter
      {
        JToken = jToken,
        Value = jToken.Value<string>()
      };

      return new List<SqlGenerator> { filter };
    }
  }
}
