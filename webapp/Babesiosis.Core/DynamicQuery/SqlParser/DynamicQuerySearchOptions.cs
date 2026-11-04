using Babesiosis.Core.Extensions;

namespace Babesiosis.Core.DynamicQuery.SqlParser
{
  public class DynamicQuerySearchOptions
  {
    public string SearchExpr { get; set; }
    public string SearchOperation { get; set; }
    public string SearchValue { get; set; }
    public int Take { get; set; } = 100;
    public int Skip { get; set; } = 0;

    /// <summary>
    /// The WHERE fragment for one search term, or null when the caller gave less than a
    /// complete triple — which the query builders read as "no filter", not as an error.
    /// <para>
    /// <b>The value is quote-doubled.</b> Every branch below closes it inside a SQL string
    /// literal and nothing downstream parameterises the fragment: the V1 query builders
    /// concatenate it and <c>ExecuteReader(sql)</c> takes the result as text. Without this an
    /// apostrophe in ordinary data ended the literal and failed the query — searching the
    /// country list for "Côte d'Ivoire" is the everyday case — and anything a user could type
    /// into a lookup's search box was an injection into that statement.
    /// </para>
    /// <para>
    /// Escaping the value is the fix that fits here; it is not parameterisation. The operator
    /// on the fallback branch is still interpolated raw, and LIKE wildcards in the value
    /// (<c>%</c>, <c>_</c>, <c>[</c>) are still wildcards rather than literal characters. The
    /// V2 manage reads next door do this properly through <c>SqlFilterParameter</c>, and that
    /// is where this path should end up.
    /// </para>
    /// </summary>
    public string CreateWhereSql()
    {
      string operation = this.SearchOperation?.ToLower();

      if(SearchExpr.HasNoValue() || SearchOperation.HasNoValue() || SearchValue.HasNoValue())
      {
        return null;
      }

      string value = SearchValue.Replace("'", "''");

      if (operation == "contains")
      {
        return $" {SearchExpr} LIKE '%{value}%' ";
      }
      else if (operation == "startswith")
      {
        return $" {SearchExpr} LIKE '{value}%' ";
      }
      else if (operation == "endswith")
      {
        return $" {SearchExpr} LIKE '%{value}' ";
      }
      else if (operation == "notcontains")
      {
        return $" {SearchExpr} NOT LIKE '%{value}%' ";
      }
      else
      {
        if(int.TryParse(SearchValue, out _))
        {
          return $" {SearchExpr} {SearchOperation} {SearchValue} ";
        }
        else
        {
          return $" {SearchExpr} {SearchOperation} '{value}' ";
        }
      }
    }

    private string ToSqlOperator(string operation, string value)
    {
      switch (operation)
      {
        case "contains": return $" LIKE '%{value}%' ";
        case "startswith": return $" LIKE '{value}%' ";
        case "endswith": return $" LIKE '%{value}' ";
        case "notcontains": return $" NOT LIKE '%{value}%' ";
        default: return $" {operation} '{value}' ";
      }
    }
  }
}
