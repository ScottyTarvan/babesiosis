namespace Babesiosis.Core.DynamicQuery.SqlParser.Syntax
{
  public class SqlSyntax : SqlGenerator
  {
    public SqlSyntax(string syntax)
    {
      Syntax = syntax;
    }

    public string Syntax { get; set; }

    public override string CreateSql()
    {
      return $"{Syntax.ToUpper()}";
    }

    public override string ToString()
    {
      return Syntax;
    }
  }
}
