using Babesiosis.Core.DynamicQuery.SqlParser.Sorters;
using Babesiosis.Core.DynamicQuery.SqlParser.Syntax;
using Newtonsoft.Json.Linq;
using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Parsers
{
  public class SortParser : Parser
  {
    public static List<SqlGenerator> Parse(JToken jToken)
    {
      var sorters = new List<SqlGenerator>();

      var children = jToken.Children().ToList();
      var iChild = 1;
      foreach (var child in children)
      {
        var sort = new Sort
        {
          Name = child["selector"].Value<string>(),
          Descending = child["desc"].Value<bool>()
        };
        sorters.Add(sort);
        if (iChild < children.Count)
        {
          var commaSyntax = new SqlSyntax(", ");
          sorters.Add(commaSyntax);
        }
        iChild++;
      }

      return sorters;
    }
  }
}
