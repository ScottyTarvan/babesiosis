using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Extensions
{
  public static class EnumerableExtensions
  {
    public static void Each<T>(this IEnumerable<T> instance, Action<T> action)
    {
      foreach (T item in instance)
      {
        action(item);
      }
    }

    public static bool Any(this IEnumerable enumerable)
    {
      foreach (var item in enumerable)
      {
        return true;
      }
      return false;
    }

    public static int IndexOf(this IEnumerable source, object item)
    {
      int index = 0;
      foreach (object i in source)
      {
        if (Equals(i, item))
        {
          return index;
        }

        index++;
      }

      return -1;
    }

    public static int Count(this IEnumerable enumerable)
    {
      int cnt = 0;
      foreach (var item in enumerable)
      {
        cnt++;
      }
      return cnt;
    }

    public static T First<T>(this IEnumerable enumerable)
    {
      foreach (var item in enumerable)
      {
        return (T)item;
      }
      return default(T);
    }

    public static T Last<T>(this IEnumerable enumerable)
    {
      object last = default(T);
      foreach (var item in enumerable)
      {
        last = item;
      }
      return (T)last;
    }

    public static IEnumerable<TSource> AntiJoin<TSource, TTarget, TKey>(this IEnumerable<TSource> source,
            IEnumerable<TTarget> target,
            Func<TSource, TKey> sourceKeySelector,
            Func<TTarget, TKey> targetKeySelector)
    {
      var secondSet = new HashSet<TKey>(target.Select(targetKeySelector));
      return source.Where(item => !secondSet.Contains(sourceKeySelector(item)));
    }

    public static (List<T> Added, List<(T Source, T Target)> Matched, List<T> Deleted) Difference<T>(this IEnumerable<T> source,
      IEnumerable<T> target)
    { 
      var comparer = new DefaultComparer<T>();
      return Difference(source, target, comparer);
    }

    public static (List<T> Added, List<(T Source, T Target)> Matched, List<T> Deleted) Difference<T>(this IEnumerable<T> source,
      IEnumerable<T> target,
      IEqualityComparer<T> comparer)
    {
      var added = source.Except(target, comparer).ToList();
      var deleted = target.Except(source, comparer).ToList();
      var modified = source.Join(target, outer => outer, inner => inner, (outer, inner) => (outer, inner), comparer).ToList();

      return (added, modified, deleted);
    }

    public static async Task<List<T>> ToListAsync<T>(this IAsyncEnumerable<T> source)
    {
      var result = new List<T>();
      await foreach(var item in source)
      {
        result.Add(item);
      }
      return result;
    }

    private class DefaultComparer<T> : IEqualityComparer<T>
    {
      public bool Equals(T x, T y) => x.Equals(y);
      public int GetHashCode(T obj) => obj.GetHashCode();
    }
  }
}
