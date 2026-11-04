using Newtonsoft.Json.Linq;
using System;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Filters
{
  public class ValueFilter : SqlGenerator
  {
    public JToken JToken { get; set; }
    public string Value { get; set; }

    public override string CreateSql()
    {
      if (JToken.Type == JTokenType.Date && DateTime.TryParse(Value, out var dateResult))
      {
        return $"'{dateResult.Date:s}'";
      }
      else if (JToken.Type == JTokenType.Integer && int.TryParse(Value, out var intResult))
      {
        return intResult.ToString();
      }
      else if (JToken.Type == JTokenType.Float && double.TryParse(Value, out var doubleResult))
      {
        return doubleResult.ToString("F8").Replace(",", ".");
      }
      else if (JToken.Previous.Value<string>()?.ToLower() == Operators.STARTS_WITH)
      {
        return $"'{Value}%'";
      }
      else if (JToken.Previous.Value<string>()?.ToLower() == Operators.ENDS_WITH)
      {
        return $"'%{Value}'";
      }
      else if (JToken.Previous.Value<string>()?.ToLower() == Operators.CONTAINS)
      {
        return $"'%{Value}%'";
      }
      else if (JToken.Previous.Value<string>()?.ToLower() == Operators.IS)
      {
        return "NULL";
      }

      return $"'{Value}'";
    }

    public override string ToString()
    {
      return Value;
    }
  }
}
