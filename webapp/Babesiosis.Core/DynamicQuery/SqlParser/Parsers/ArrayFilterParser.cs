using Babesiosis.Core.DynamicQuery.SqlParser.Syntax;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Parsers
{
  public class ArrayFilterParser : Parser
  {
    public static bool IsArray(JToken jToken)
    {
      return jToken != null
        && jToken.Type == JTokenType.Array;
    }

    public List<SqlGenerator> Parse(JToken jToken)
    {
      var filters = new List<SqlGenerator>();
      var openBracketSyntax = new SqlSyntax("(");
      filters.Add(openBracketSyntax);
      foreach (var childToken in jToken.Children())
      {
        filters.AddRange(Parser.Parse(childToken));
      }
      var closedBracketSyntax = new SqlSyntax(")");
      filters.Add(closedBracketSyntax);
      return filters;
    }
  }
}
