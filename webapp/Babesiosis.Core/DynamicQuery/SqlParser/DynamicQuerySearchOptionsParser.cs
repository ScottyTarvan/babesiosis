using Babesiosis.Core.DynamicQuery.SqlParser.Parsers;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Babesiosis.Core.DynamicQuery.SqlParser
{
  public class DynamicQuerySearchOptionsParser
  {
    public static DynamicQuerySearchOptions Parse(string json)
    {
      var jsonDom = JsonConvert.DeserializeObject<JObject>(json);

      var options = new DynamicQuerySearchOptions();
      options.SearchExpr = jsonDom["searchExpr"]?.Value<string>();
      options.SearchOperation = jsonDom["searchOperation"]?.Value<string>();
      options.SearchValue = jsonDom["searchValue"]?.Value<string>();
      options.Skip = 0;
      if (jsonDom.TryGetValue("skip", out var skipProperty))
      {
        options.Skip = skipProperty.Value<int>();
      }
      options.Take = 10000;
      if (jsonDom.TryGetValue("take", out var takeProperty))
      {
        options.Take = takeProperty.Value<int>();
      }

      return options;
    }
  }
}
