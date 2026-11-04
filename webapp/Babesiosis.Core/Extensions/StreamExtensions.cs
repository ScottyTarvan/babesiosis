using System;
using System.IO;

namespace Babesiosis.Core.Extensions
{
  public static class StreamExtensions
  {
    public static string ToBase64String(this Stream stream)
    {
      byte[] bytes;
      using (var memoryStream = new MemoryStream())
      {
        stream.CopyTo(memoryStream);
        bytes = memoryStream.ToArray();
      }

      return Convert.ToBase64String(bytes);
    }

    public static byte[] ToBytes(this Stream stream)
    {
      var memoryStream = new MemoryStream();
      stream.CopyTo(memoryStream);
      return memoryStream.ToArray();
    }
  }
}
