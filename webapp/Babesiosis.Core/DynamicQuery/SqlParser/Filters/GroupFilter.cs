using System;
using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.DynamicQuery.SqlParser.Filters
{
  public class GroupFilter : SqlGenerator
  {
    public List<SqlGenerator> Filters { get; set; }

    public override string CreateSql()
    {
      return string.Join(Environment.NewLine, Filters.Select(f => f.CreateSql()));
    }

    public override string ToString()
    {
      return string.Join(Environment.NewLine, Filters.Select(f => f.CreateSql()));
    }
  }
}
