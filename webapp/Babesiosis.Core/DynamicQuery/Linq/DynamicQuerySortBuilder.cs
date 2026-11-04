using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;

namespace Babesiosis.Core.DynamicQuery.Linq
{
  /// <summary>
  /// Applies a list request's sort entries (platform/list-queries.md §3.3): each field resolves
  /// as a filter field does, entries apply in the order given, and an unknown field throws.
  /// </summary>
  public static class DynamicQuerySortBuilder
  {
    public static IQueryable<T> Apply<T>(IQueryable<T> query, IEnumerable<(string Selector, bool Desc)> sort)
    {
      if (sort == null) return query;

      var parameter = Expression.Parameter(typeof(T), "Param_0");
      var expression = query.Expression;
      var first = true;

      foreach (var (selector, desc) in sort)
      {
        var member = DynamicQueryMember.Resolve(parameter, selector);
        var method = first
          ? (desc ? nameof(Queryable.OrderByDescending) : nameof(Queryable.OrderBy))
          : (desc ? nameof(Queryable.ThenByDescending) : nameof(Queryable.ThenBy));

        expression = Expression.Call(
          typeof(Queryable), method, new[] { typeof(T), member.Type },
          expression, Expression.Quote(Expression.Lambda(member, parameter)));

        first = false;
      }

      return first ? query : query.Provider.CreateQuery<T>(expression);
    }
  }
}
