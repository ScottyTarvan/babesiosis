using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Extensions
{
  public static class TypeExtensions
  {
    private static readonly HashSet<Type> SimpleCoreTypes = new()
    {
      typeof(bool),
      typeof(byte),
      typeof(sbyte),
      typeof(short),
      typeof(ushort),
      typeof(int),
      typeof(uint),
      typeof(long),
      typeof(ulong),
      typeof(float),
      typeof(double),
      typeof(decimal),
      typeof(char),
      typeof(string),
      typeof(Guid),
      typeof(DateTime),
      typeof(DateTimeOffset),
      typeof(TimeSpan)
    };

    /// <summary>
    /// Returns <c>true</c> if the current type is a value / primitive / string /
    /// enum / Guid / DateTime / TimeSpan (plus nullable counterparts).
    /// </summary>
    public static bool IsSimple(this Type type)
    {
      type = Nullable.GetUnderlyingType(type) ?? type;

      return type.IsEnum || SimpleCoreTypes.Contains(type);
    }
  }
}
