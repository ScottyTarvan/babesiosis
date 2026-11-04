using Babesiosis.Core.DynamicQuery.SqlParser.Filters;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Parsers
{
  public class FieldFilterParser : Parser
  {
    /// <summary>
    /// A field comes first
    /// </summary>
    /// <param name="jToken"></param>
    /// <returns></returns>
    public static bool IsField(JToken jToken)
    {
      return jToken != null
        && jToken.Previous == null
        && jToken.Type == JTokenType.String;
    }

    public List<SqlGenerator> Parse(JToken jToken)
    {
      var filter = new FieldFilter
      {
        Field = jToken.Value<string>()
      };

      return new List<SqlGenerator> { filter };
    }
  }
}
