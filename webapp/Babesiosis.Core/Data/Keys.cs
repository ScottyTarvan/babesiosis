using System;

namespace Babesiosis.Core.Data
{
  public  class Keys
  {
    public static string CombineKeys(long longVal, int intVal)
    {
      byte[] bytes = new byte[12];
      Buffer.BlockCopy(BitConverter.GetBytes(longVal), 0, bytes, 0, 8);
      Buffer.BlockCopy(BitConverter.GetBytes(intVal), 0, bytes, 8, 4);
      return Convert.ToBase64String(bytes);
    }
  }
}
