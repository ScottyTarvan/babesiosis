using Babesiosis.Core.DynamicQuery.SqlParser.Syntax;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Parsers
{
  public class BetweenValueFilterParser : Parser
  {
    /// <summary>
    /// A between value is an array that comes after a between operator
    /// </summary>
    /// <param name="jToken"></param>
    /// <returns></returns>
    public static bool IsBetweenValue(JToken jToken)
    {
      return jToken != null
        && OperatorFilterParser.IsBetweenOperator(jToken.Previous);
    }

    public List<SqlGenerator> Parse(JToken jToken)
    {
      var filters = new List<SqlGenerator>();
      var children = jToken.Children().ToList();
      var iChild = 1;
      foreach (var child in children)
      {
        var valueParser = new ValueFilterParser();
        filters.AddRange(valueParser.Parse(child));
        if (iChild < children.Count)
        {
          var andSyntax = new SqlSyntax("AND");
          filters.Add(andSyntax);
        }
        iChild++;
      }

      //the grid sends a request with no values until both have been selected 
      if(!filters.Any())
      {
        var noValues = new SqlSyntax("NULL AND NULL");
        filters.Add(noValues);
      }
      return filters;
    }
  }
}
