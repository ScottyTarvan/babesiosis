using Babesiosis.Core.Models.Domain;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Threading.Tasks;

namespace Babesiosis.Core.Extensions
{
  public static class QueryableExtensions
  {
    public static PagedResult<T> ToPaged<T>(this IQueryable<T> query,
      int page,
      int pageSize) where T : class
    {
      var result = new PagedResult<T>
      {
        Page = page,
        PageSize = pageSize,
        TotalRecordCount = query.Count()
      };

      var pageCount = (double)result.RecordCount / pageSize;
      result.PageCount = (int)Math.Ceiling(pageCount);

      var skip = (page - 1) * pageSize;
      result.Results = query.Skip(skip).Take(pageSize).ToList();
      result.RecordCount = result.Results.Count();

      return result;
    }

    public static async Task<PagedResult<T>> ToPagedAsync<T>(this IQueryable<T> query,
      int page,
      int pageSize) where T : class
    {
      var result = new PagedResult<T>
      {
        Page = page,
        PageSize = pageSize,
        TotalRecordCount = await query.CountAsync()
      };

      var pageCount = (double)result.TotalRecordCount / pageSize;
      result.PageCount = (int)Math.Ceiling(pageCount);

      var skip = (page - 1) * pageSize;
      result.Results = await query.Skip(skip).Take(pageSize).ToListAsync();
      result.RecordCount = result.Results.Count();

      return result;
    }

    private static Expression<Func<T, object>> ToLambda<T>(string propertyName)
    {
      string[] levels = propertyName.Split('/');
      if(levels.Length > 1)
      {
        ParameterExpression parameter = Expression.Parameter(typeof(T));
        MemberExpression property = Expression.Property(parameter, levels[0]); ;
        for(int i = 1; i < levels.Length; i++)
        {
          property = Expression.Property(property, levels[i]);
        }

        Expression conversion = Expression.Convert(property, typeof(object));

        return Expression.Lambda<Func<T, object>>(conversion, parameter);
      }
      else
      {
        ParameterExpression parameter = Expression.Parameter(typeof(T));
        MemberExpression property = Expression.Property(parameter, propertyName);
        Expression conversion = Expression.Convert(property, typeof(object));

        return Expression.Lambda<Func<T, object>>(conversion, parameter);
      }

    }

    public static IOrderedQueryable<T> OrderByDynamic<T>(this IQueryable<T> query,
      string sortBy,
      SortOrder sortOrder)
    {
      if(sortBy.HasNoValue())
      {
        return query.OrderBy(p => 0);
      }

      if(sortOrder == SortOrder.Ascending)
      {
        return query.OrderBy(ToLambda<T>(sortBy));
      }
      else
      {
        return query.OrderByDescending(ToLambda<T>(sortBy));
      }
    }

    public static IOrderedQueryable<T> ThenByDynamic<T>(this IOrderedQueryable<T> query,
      string sortBy,
      SortOrder sortOrder)
    {
      if(sortBy.HasNoValue())
      {
        return query;
      }

      if(sortOrder == SortOrder.Ascending)
      {
        return query.ThenBy(ToLambda<T>(sortBy));
      }
      else
      {
        return query.ThenByDescending(ToLambda<T>(sortBy));
      }
    }

    public static IQueryable<TOutput> LeftOuterJoin<TLeft, TRight, TKey, TOutput>(
    this IQueryable<TLeft> left,
    IEnumerable<TRight> right,
    Expression<Func<TLeft, TKey>> leftKey,
    Expression<Func<TRight, TKey>> rightKey,
    Expression<Func<TLeft, TRight?, TOutput>> join)
    {
      var paramJ = Expression.Parameter(typeof(LeftJoinInternal<TLeft, TRight>));
      var paramR = Expression.Parameter(typeof(TRight));
      var body = Expression.Invoke(join, Expression.Field(paramJ, "L"), paramR);
      var l = Expression.Lambda<Func<LeftJoinInternal<TLeft, TRight>, TRight, TOutput>>(body, paramJ, paramR);

      return left
          .GroupJoin(right, leftKey, rightKey, (l, r) => new LeftJoinInternal<TLeft, TRight> { L = l, R = r })
          .SelectMany(j => j.R.DefaultIfEmpty()!, l);
    }

    private sealed class LeftJoinInternal<TLeft, TRight>
    {
      public TLeft L = default!;
      public IEnumerable<TRight> R = default!;
    }
  }
}
