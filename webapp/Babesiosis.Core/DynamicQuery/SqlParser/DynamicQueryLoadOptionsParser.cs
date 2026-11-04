using Babesiosis.Core.DynamicQuery.SqlParser.Parsers;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Babesiosis.Core.DynamicQuery.SqlParser
{
  public class DynamicQueryLoadOptionsParser
  {
    public static DynamicQueryLoadOptions Parse(string json)
    {
      var jsonDom = JsonConvert.DeserializeObject<JObject>(json);

      var options = new DynamicQueryLoadOptions();

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

      if (jsonDom["sort"]?.Value<JArray>() != null)
      {
        var sortArray = jsonDom["sort"]?.Value<JArray>();
        options.Sorters.AddRange(SortParser.Parse(sortArray));
      }

      if (jsonDom["filter"]?.Value<JArray>() != null)
      {
        var filterArray = jsonDom["filter"]?.Value<JArray>();
        foreach (var jToken in filterArray.Children())
        {
          options.Filters.AddRange(Parser.Parse(jToken));
        }
      }

      return options;
    }
  }
}
