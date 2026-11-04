using System;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;

namespace Babesiosis.Core.DynamicQuery.Linq
{
  /// <summary>
  /// Resolves a field name from a request to a property chain (platform/list-queries.md §3.1).
  /// Names match case-insensitively, a dotted path walks related objects, and an unknown name
  /// throws — it never degrades to an unfiltered or unsorted result. Only public, readable,
  /// non-indexed instance properties are reachable: no fields, methods or indexers.
  /// </summary>
  internal static class DynamicQueryMember
  {
    public static Expression Resolve(Expression instance, string path)
    {
      if (string.IsNullOrWhiteSpace(path))
        throw new MissingMemberException("A filter or sort entry has no field name.");

      var current = instance;

      foreach (var segment in path.Split('.'))
      {
        var property = Find(current.Type, segment)
          ?? throw new MissingMemberException($"Member '{current.Type.Name}.{segment}' not found.");

        current = Expression.Property(current, property);
      }

      return current;
    }

    private static PropertyInfo Find(Type type, string name)
    {
      var candidates = type
        .GetProperties(BindingFlags.Public | BindingFlags.Instance)
        .Where(p => p.CanRead && p.GetGetMethod() != null && p.GetIndexParameters().Length == 0)
        .ToList();

      var match = candidates.Where(p => p.Name == name).ToList();

      if (match.Count == 0)
        match = candidates.Where(p => string.Equals(p.Name, name, StringComparison.OrdinalIgnoreCase)).ToList();

      // A property re-declared with 'new' appears once per level; the most derived one wins.
      return match
        .OrderByDescending(p => Depth(p.DeclaringType))
        .FirstOrDefault();
    }

    private static int Depth(Type type)
    {
      var depth = 0;
      for (var t = type; t != null; t = t.BaseType) depth++;
      return depth;
    }
  }
}
