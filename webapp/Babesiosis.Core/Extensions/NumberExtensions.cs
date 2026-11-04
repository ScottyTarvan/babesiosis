using System.Text;

namespace Babesiosis.Core.Extensions
{
  public static class NumberExtensions
  {
    /// <summary>
    /// Returns a max length of 11 characters
    /// </summary>
    /// <param name="number"></param>
    /// <returns></returns>
    public static string ToBase62(this long number)
    {
      const string ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
      const long BASIS = 62;

      StringBuilder builder = new StringBuilder();
      while (number > 0)
      {
        long index = number % BASIS;
        builder.Insert(0, ALPHABET[(int)index]);
        number = (number / BASIS);
      }
      return builder.ToString();
    }

    /// <summary>
    /// Returns a max length of 13 characters and always excludes 0 G N Y   
    /// </summary>
    /// <param name="number"></param>
    /// <returns></returns>
    public static string ToBase32(this long number)
    {
      const string ALPHABET = "123456789ABCDEFHIJKLMOPRSTUVWXYZ";
      const long BASIS = 32;

      StringBuilder builder = new StringBuilder();
      while (number > 0)
      {
        long index = number % BASIS;
        builder.Insert(0, ALPHABET[(int)index]);
        number = (number / BASIS);
      }
      return builder.ToString();
    }
  }
}
