using System;

namespace Babesiosis.Core.Extensions
{
  public static class ObjectExtensions
  {
    public static bool IsNull(this object obj)
    {
      return obj == null;
    }
    
    public static bool IsNotNull(this object obj)
    {
      return obj != null;
    }

    public static Guid? ToGuid(this object obj)
    {
      return obj != null ? Guid.Parse(obj.ToString()) : new Guid?();
    }

    public static bool? ToBool(this object obj)
    {
      return obj != null ? Convert.ToBoolean(obj) : new bool?();
    }

    public static int? ToInt(this object obj)
    {
      return obj != null ? Convert.ToInt32(obj) : new int?();
    }

    public static decimal? ToDecimal(this object obj)
    {
      return obj != null ? Convert.ToDecimal(obj) : new decimal?();
    }

    public static DateTime? ToDateTime(this object obj)
    {
      return obj != null ? Convert.ToDateTime(obj) : new DateTime?();
    }
  }
}
