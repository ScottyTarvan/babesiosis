namespace Babesiosis.Core.DynamicQuery.SqlParser.Filters
{
  public class OperatorFilter : SqlGenerator
  {
    public string Operator { get; set; }

    public override string CreateSql()
    {
      if(Operator?.ToLower() == "between")
      {
        return " BETWEEN ";
      }
      else if (Operator?.ToLower() == "contains")      
      {
        return " LIKE ";
      }
      else if (Operator?.ToLower() == "startswith")
      {
        return " LIKE ";
      }
      else if (Operator?.ToLower() == "endswith")
      {
        return " LIKE ";
      }

      return $"{Operator.ToUpper()}";
    }

    public override string ToString()
    {
      return Operator;
    }
  }
}
