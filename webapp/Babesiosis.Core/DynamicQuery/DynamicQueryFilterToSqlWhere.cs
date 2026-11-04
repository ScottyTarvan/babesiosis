using Babesiosis.Core.Extensions;
using Newtonsoft.Json.Linq;
using System;
using System.Collections;
using System.Linq;
using System.Text;

namespace Babesiosis.Core.DynamicQuery
{
  public static class DynamicQueryFilterToSqlWhere
  {
    const string NEGATION_OPERATOR = "!";
    static string[] groupOperators = new string[] { "and", "or" };
    static string[] functions = new string[] { "contains", "notcontains", "startswith", "endswith" };
    const string SQL_LIKE = "LIKE";
    const string SQL_NOT = "NOT";

    static string ParseBinaryExpression(IList objects)
    {
      string field = objects[0].ToString();
      string op = objects[1].ToString().Trim();
      object value = objects[2];
      return BuildBinaryExpression(field, op, value);
    }
    static string BuildBinaryExpression(string field, string op, object value)
    {
      string sqlOp = functions.Contains(op) ? DynamicQueryFunctionToSqlOperator(op) : op;
      string sValue = FormatValue(value, sqlOp, op);
      return string.Format("({0} {1} {2})", field, sqlOp, sValue);
    }
    static string FormatValue(object value, string sqlOp, string op)
    {
      if (value == null) return "null";
      if (sqlOp.Contains(SQL_LIKE))
      {
        StringBuilder sb = new StringBuilder();
        sb.Append("'");
        if (op == "startswith" || op.Contains("contains")) sb.Append("%");
        sb.Append(value.ToString());
        if (op == "endswith" || op.Contains("contains")) sb.Append("%");
        sb.Append("'");
        return sb.ToString();
      }
      else
      {
        DateTime dt;
        if (value.GetType() == typeof(string) || DateTime.TryParse(value.ToString(), out dt))
        {
          return string.Format("'{0}'", value.ToString());
        }
        return value.ToString();
      }
    }
    public static string Convert(IList filter)
    {
      if (filter == null || !filter.Any()) return string.Empty;
      string filterConverted = ConvertFilter(filter);
      return filterConverted;
    }
    static string ConvertFilter(IList filter)
    {
      object[] filterParts = new object[filter.Count];
      filter.CopyTo(filterParts, 0);
      return ConvertCore(filterParts);
    }
    static string ConvertFilter(JArray filter)
    {
      object[] filterParts = filter.Select(token => GetTokenValue(token)).ToArray();
      return ConvertCore(filterParts);
    }
    static string ConvertCore(object[] filter)
    {
      StringBuilder sb = new StringBuilder();
      if (filter[0] is string)
      {
        if (filter[0].ToString() == NEGATION_OPERATOR)
        {
          sb.Append(SQL_NOT + " ");
          sb.Append(ConvertFilter(filter[1] as JArray));
        }
        else
        {
          sb.Append(ParseBinaryExpression(filter));
          return sb.ToString();
        }
      }
      if (filter[1] is string && groupOperators.Contains(filter[1].ToString()))
      {
        sb.Append("(");
        foreach (object filterPart in filter)
        {
          if (groupOperators.Contains(filterPart.ToString()))
            sb.Append(string.Format(" {0} ", filterPart));
          else
          {
            sb.Append(ConvertFilter(filterPart as JArray));
          }
        }
        sb.Append(")");
        return sb.ToString();
      }
      return sb.ToString();
    }
    static object GetTokenValue(object token)
    {
      if (token is string) return (string)token;
      if (token is JValue) return ((JValue)token).Value;
      return token;
    }
    static string DynamicQueryFunctionToSqlOperator(string func)
    {
      switch (func)
      {
        case "contains": return SQL_LIKE;
        case "startswith": return SQL_LIKE;
        case "endswith": return SQL_LIKE;
        case "notcontains": return string.Format("{0} {1}", SQL_NOT, SQL_LIKE);
        default: return func;
      }
    }
  }
}
