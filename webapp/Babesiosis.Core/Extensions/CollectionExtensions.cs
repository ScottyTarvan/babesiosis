using System.Collections.Generic;

namespace Babesiosis.Core.Extensions
{
  public static class CollectionExtensions
  {
    public static void AddRange<T>(this ICollection<T> instance, IEnumerable<T> collection)
    {
      foreach (T item in collection)
      {
        instance.Add(item);
      }
    }
  }
}