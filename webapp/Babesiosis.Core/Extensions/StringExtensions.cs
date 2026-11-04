using NPOI.HSSF.Record;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;

namespace Babesiosis.Core.Extensions
{
  public static class StringExtensions
  {
    static Regex WhiteSpaceRegEx = new Regex(@"\s+");
    static Regex SpecialCharactersRegEx = new Regex(@"[^a-zA-Z0-9_]+");

    /// <summary>
    /// Converts a string to pascal case where the first letter of each word is upper case. An examples
    /// is "the data" -> "The Data"
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static string ToPascalCase(this string str)
    {
      // If there are 0 or 1 characters, just return the string.
      if (str == null) return str;
      if (str.Length < 2) return str.ToUpper();

      // Split the string into words.
      string[] words = str.Split(
          new char[] { },
          StringSplitOptions.RemoveEmptyEntries);

      // Combine the words.
      List<string> result = new List<string>();
      foreach (string word in words)
      {
        result.Add(word.Substring(0, 1).ToUpper() + word.Substring(1));
      }

      return String.Join(' ', result);
    }


    /// <summary>
    /// Converts a string to camel case where the first letter of each word except the first word is upper case. An examples
    /// is "the data" -> "theData"
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static string ToCamelCase(this string str)
    {
      // If there are 0 or 1 characters, just return the string.
      if (str == null || str.Length < 2)
        return str;

      // Split the string into words.
      string[] words = str.Split(
          new char[] { },
          StringSplitOptions.RemoveEmptyEntries);

      // Combine the words.
      string result = words[0].ToLower();
      for (int i = 1; i < words.Length; i++)
      {
        result +=
            words[i].Substring(0, 1).ToUpper() +
            words[i].Substring(1);
      }

      return result;
    }

    /// <summary>
    /// Returns true if string is null or empty
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static bool HasNoValue(this string str)
    {
      return String.IsNullOrEmpty(str);
    }

    /// <summary>
    /// Returns true if the string is not empty or null
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static bool HasValue(this string str)
    {
      return !String.IsNullOrEmpty(str);
    }

    /// <summary>
    /// Removes all white space characters from a string 
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static string RemoveSpaces(this string str)
    {
      return WhiteSpaceRegEx.Replace(str, "");
    }

    /// <summary>
    /// Removes all spaces and characters except for letters, numbers and under scores
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static string RemoveSpecialCharacters(this string str)
    {
      if (str.HasNoValue())
        return str;

      return SpecialCharactersRegEx.Replace(str, "");
    }

    /// <summary>
    /// Removes all spaces and makes lower case, mainly used for unit tests
    /// </summary>
    /// <param name="str"></param>
    /// <param name="len"></param>
    /// <returns></returns>
    public static string Compact(this string str)
    {
      if (str.HasValue())
      {
        return str
          .RemoveSpaces()
          .ToLower();
      }
      return str;
    }

    /// <summary>
    /// Returns true if the string can be converted to an integer
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static bool IsANumber(this string str)
    {
      return int.TryParse(str, out _);
    }

    /// <summary>
    /// Masks a string by showing only the first 2 and last 2 characters.
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static string MaskSensitiveData(this string str)
    {
      if (str.Length < 4)
      {
        str = str.PadRight(4, '*');
      }

      return str.Substring(0, 2) + new String('*', str.Length - 4) + str.Substring(str.Length - 3, 2);
    }

    /// <summary>
    /// Truncates a string to a specified length and adds two ellipsis such as "foobar..", 
    /// the final length of the string will not exceed the desired length.
    /// </summary>
    /// <param name="str"></param>
    /// <param name="len"></param>
    /// <returns></returns>
    public static string TruncateWithEllipsis(this string str, int len)
    {
      if(str.HasValue() && str.Length > len)
      {
        return str.Substring(0, Math.Max(0, len - 2)) + "..";
      }
      return str;
    }

    /// <summary>
    /// Truncates a string to a specified length
    /// </summary>
    /// <param name="str"></param>
    /// <param name="len"></param>
    /// <returns></returns>
    public static string Truncate(this string str, int len)
    {
      if (str.HasValue() && str.Length > len)
      {
        return str.Substring(0, len);
      }
      return str;
    }

    /// <summary>
    /// Match the current string with a non-regex pattern
    /// </summary>
    /// <param name="str"></param>
    /// <param name="pattern"></param>
    /// <returns></returns>
    public static bool MatchPattern(this string str, string pattern)
    {
      if (str.HasNoValue() || pattern.HasNoValue())
      {
        return false;
      }
      string regular = "^" + Regex.Escape(pattern).Replace("\\?", ".").Replace("\\*", ".*") + "$";
      return Regex.IsMatch(str.ToLower(), regular.ToLower()); ;
    }

    /// <summary>
    /// Ensure leading and trailing square brackets
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    public static string Wrap(this string str, string delimiter)
    {
      if (string.IsNullOrWhiteSpace(str))
        return "[]";

      str = str.Trim();

      bool startsWithBracket = str.StartsWith(delimiter);
      bool endsWithBracket = str.EndsWith(delimiter);

      if (!startsWithBracket)
        str = "[" + str;
      if (!endsWithBracket)
        str = str + "]";

      return str;
    }
  }
}
