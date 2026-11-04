using System;
using System.Net.NetworkInformation;

namespace Babesiosis.Core.Extensions
{
  public static class GUIDExtensions
  {
    /// <summary>
    /// N Format : 00000000000000000000000000000000
    /// </summary>
    /// <param name="guid"></param>
    /// <returns></returns>
    public static string ToN(this Guid guid)
    {
      return guid.ToString("N");
    }

    public static Guid FromNFormat(this string guid)
    {
      return Guid.ParseExact(guid, "N");
    }

    /// <summary>
    /// D Format : 00000000-0000-0000-0000-000000000000
    /// </summary>
    /// <param name="guid"></param>
    /// <returns></returns>
    public static string ToD(this Guid guid)
    {
      return guid.ToString("D");
    }

    public static Guid FromD(this string guid)
    {
      return Guid.ParseExact(guid, "D");
    }

    /// <summary>
    ///B Format : {00000000-0000-0000-0000-000000000000}
    /// </summary>
    /// <param name="guid"></param>
    /// <returns></returns>
    public static string ToB(this Guid guid)
    {
      return guid.ToString("B");
    }

    public static Guid FromB(this string guid)
    {
      return Guid.ParseExact(guid, "B");
    }

    /// <summary>
    /// P Format : (00000000-0000-0000-0000-000000000000)
    /// </summary>
    /// <param name="guid"></param>
    /// <returns></returns>
    public static string ToP(this Guid guid)
    {
      return guid.ToString("P");
    }

    public static Guid FromP(this string guid)
    {
      return Guid.ParseExact(guid, "P");
    }

    /// <summary>
    /// Returns the first character of a guid excluding any braces.
    /// </summary>
    /// <param name="guid"></param>
    /// <returns></returns>
    public static string FirstChar(this Guid guid)
    {
      return guid.ToD()[0].ToString();
    }

    /// <summary>
    /// Returns true if the guid is null or empty
    /// </summary>
    /// <param name="guid"></param>
    /// <returns></returns>
    public static bool IsNullOrEmpty(this Guid? guid)
    {
      return guid == null || guid == Guid.Empty;
    }
  }
}
