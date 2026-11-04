using System;
using System.Collections.Generic;
using System.Text;

namespace Babesiosis.Core.Extensions
{
  public static class ByteExtensions
  {
    public static string ToBase64String(this byte[] bytes)
    {
      if(bytes == null)
      {
        bytes = Encoding.UTF8.GetBytes("BLANK");
      }
      return Convert.ToBase64String(bytes);
    }

    public static byte[] FromBase64String(this string str)
    {
      return Convert.FromBase64String(str);
    }
  }
}
