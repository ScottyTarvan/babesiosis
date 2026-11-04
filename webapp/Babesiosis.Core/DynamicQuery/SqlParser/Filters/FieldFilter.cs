namespace Babesiosis.Core.DynamicQuery.SqlParser.Filters
{
  public class FieldFilter : SqlGenerator
  {
    public string Field { get; set; }

    public override string CreateSql()
    {
      return Field;
    }

    public override string ToString()
    {
      return Field;
    }
  }
}
