using System.Collections.Generic;
using System.Text;

namespace Babesiosis.Core.DynamicQuery.SqlParser
{
  public class DynamicQueryLoadOptions
  {
    public int Skip { get; set; }
    public int Take { get; set; }
    public List<SqlGenerator> Sorters { get; set; } = new List<SqlGenerator>();
    public List<SqlGenerator> Filters { get; set; } = new List<SqlGenerator>();

    public string CreateOrderSql()
    {
      StringBuilder sql = new StringBuilder();
      foreach (var sort in Sorters)
      {
        sql.Append(sort.CreateSql());
        sql.Append(" ");
      }

      return sql.ToString();
    }

    public string CreateWhereSql()
    {
      StringBuilder sql = new StringBuilder();
      foreach (var filter in Filters)
      {
        sql.Append(filter.CreateSql());
        sql.Append(" ");
      }

      return sql.ToString();
    }
  }
}
