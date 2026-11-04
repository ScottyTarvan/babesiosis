using System;
using System.Collections.Generic;
using System.Linq;
using System.Linq.Expressions;
using System.Threading.Tasks;
using DevExtreme.AspNet.Data;
using Babesiosis.Core.DynamicQuery.Linq;
using Babesiosis.Core.Models.Domain;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Extensions
{
  /// <summary>
  /// The shared list helpers (platform/list-queries.md §3.4): request filter, then the
  /// endpoint's fixed condition, then sort, then total and page.
  /// <para>
  /// The page arithmetic is kept exactly as it was, defects included (§5 D1, D2, L2): the page
  /// count is computed before the record count is set, the page size carries <c>Skip</c>, and a
  /// <c>Take</c> of 0 returns no rows.
  /// </para>
  /// </summary>
  public static class DynamicQueryLoadOptionsExtensions
  {
    public static async Task<PagedResult<T>> LoadPageAsync<T>(this DataSourceLoadOptionsBase loadOptions,
        IQueryable<T> query,
        Expression<Func<T, bool>> where = null)
        where T : class
    {
      query = Query(loadOptions, query, where);

      //prevent divide by zero
      var take = loadOptions.Take == 0 ? 1000 : loadOptions.Take;

      var result = new PagedResult<T>
      {
        Page = (loadOptions.Skip / take) + 1,
        PageSize = loadOptions.Skip,
        TotalRecordCount = await query.CountAsync()
      };

      var pageCount = (double)result.RecordCount / loadOptions.Take;
      result.PageCount = (int)Math.Ceiling(pageCount);

      result.Results = await query.Skip(loadOptions.Skip).Take(loadOptions.Take).ToListAsync();
      result.RecordCount = result.Results.Count();

      return result;
    }

    public static PagedResult<T> LoadPage<T>(this DataSourceLoadOptionsBase loadOptions,
      IQueryable<T> query,
      Expression<Func<T, bool>> where = null)
      where T : class
    {
      query = Query(loadOptions, query, where);

      //prevent divide by zero
      var take = loadOptions.Take == 0 ? 1000 : loadOptions.Take;

      var result = new PagedResult<T>
      {
        Page = (loadOptions.Skip / take) + 1,
        PageSize = loadOptions.Skip,
        TotalRecordCount = query.Count()
      };

      var pageCount = (double)result.RecordCount / loadOptions.Take;
      result.PageCount = (int)Math.Ceiling(pageCount);

      result.Results = query.Skip(loadOptions.Skip).Take(loadOptions.Take).ToList();
      result.RecordCount = result.Results.Count();

      return result;
    }

    public static async Task<PagedResult<T>> ToPagedAsync<T>(this DataSourceLoadOptionsBase loadOptions,
        IQueryable<T> query,
        Expression<Func<T, bool>> where = null)
        where T : class
    {
      query = Query(loadOptions, query, where);

      var result = new PagedResult<T>
      {
        Page = (loadOptions.Skip / Math.Max(loadOptions.Take, 1)) + 1,
        PageSize = loadOptions.Skip,
        TotalRecordCount = await query.CountAsync()
      };

      var pageCount = (double)result.RecordCount / loadOptions.Take;
      result.PageCount = (int)Math.Ceiling(pageCount);

      result.Results = await query.Skip(loadOptions.Skip).Take(loadOptions.Take).ToListAsync();
      result.RecordCount = result.Results.Count();

      return result;
    }

    /// <summary>The whole filtered list, unpaged; <paramref name="sort"/> applies only when the request has no sort.</summary>
    public static async Task<IEnumerable<T>> LoadAsync<T, TKey>(this DataSourceLoadOptionsBase loadOptions,
      IQueryable<T> query,
      Expression<Func<T, bool>> where = null,
      Expression<Func<T, TKey>> sort = null,
      bool sortByDescending = false)
      where T : class
    {
      return await Unpaged(loadOptions, query, where, sort, sortByDescending).ToListAsync();
    }

    /// <inheritdoc cref="LoadAsync{T, TKey}"/>
    public static IEnumerable<T> Load<T, TKey>(this DataSourceLoadOptionsBase loadOptions,
      IQueryable<T> query,
      Expression<Func<T, bool>> where = null,
      Expression<Func<T, TKey>> sort = null,
      bool sortByDescending = false)
      where T : class
    {
      return Unpaged(loadOptions, query, where, sort, sortByDescending).ToList();
    }

    private static IQueryable<T> Unpaged<T, TKey>(DataSourceLoadOptionsBase loadOptions, IQueryable<T> query,
      Expression<Func<T, bool>> where, Expression<Func<T, TKey>> sort, bool sortByDescending)
    {
      query = Query(loadOptions, query, where);

      if (loadOptions.Sort == null && sort != null)
      {
        query = sortByDescending ? query.OrderByDescending(sort) : query.OrderBy(sort);
      }

      return query;
    }

    private static IQueryable<T> Query<T>(DataSourceLoadOptionsBase loadOptions, IQueryable<T> query, Expression<Func<T, bool>> where)
    {
      if (loadOptions.Filter != null)
      {
        var predicate = DynamicQueryPredicateBuilder.Build<T>(loadOptions.Filter);
        if (predicate != null) query = query.Where(predicate);
      }

      if (where != null)
      {
        query = query.Where(where);
      }

      if (loadOptions.Sort != null)
      {
        query = DynamicQuerySortBuilder.Apply(query, loadOptions.Sort.Select(s => (s.Selector, s.Desc)));
      }

      return query;
    }
  }
}
