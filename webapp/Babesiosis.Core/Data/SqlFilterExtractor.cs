using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace Babesiosis.Core.Data
{
 public static class SqlFilterExtractor
  {
    // Matches only (=) inside (...) blocks; ignores other operators.
    // Supports identifiers: bare, [bracketed], "quoted", `backticked`
    // Supports values: 'single-quoted' (with '' escapes), optional N'..', "double-quoted", or bare tokens
    private static readonly Regex EqualsClause = new Regex(
        @"(?x)                                   # verbose mode
          \(                                    # opening paren
            \s*
            (?<key>
                (?:\[[^\]\r\n]+\])              # [Bracketed Identifier]
              | (?:""[^""]+"")                  # ""Quoted Identifier""
              | (?:`[^`]+`)                     # `Backticked`
              | (?:[A-Za-z_][A-Za-z0-9_]*)
            )
            \s*=\s*
            (?<value>
                N?'(?:''|[^'])*'                # N'...' or '...' (with '' escape)
              | (?:""(?:""""|[^""])*"")         # ""..."" (rare as string literal)
              | [^)\s]+                         # bare token until ) or whitespace
            )
            \s*
          \)                                    # closing paren
        ",
        RegexOptions.Compiled);

    public static Dictionary<string, string?> ExtractEqualsPairs(string filter)
    {
      if (filter == null) throw new ArgumentNullException(nameof(filter));

      if (!filter.TrimStart().StartsWith("("))
      {
        filter = "(" + filter + ")";
      }

      var dict = new Dictionary<string, string?>(StringComparer.OrdinalIgnoreCase);

      foreach (Match m in EqualsClause.Matches(filter))
      {
        var rawKey = m.Groups["key"].Value;
        var rawVal = m.Groups["value"].Value;

        var key = NormalizeIdentifier(rawKey);
        var val = NormalizeValue(rawVal);

        // last one wins on duplicate keys
        dict[key] = val;
      }

      return dict;
    }

    private static string NormalizeIdentifier(string ident)
    {
      ident = ident.Trim();

      // Strip [brackets]
      if (ident.StartsWith("[") && ident.EndsWith("]"))
        return ident.Substring(1, ident.Length - 2);

      // Strip "quotes"
      if (ident.StartsWith("\"") && ident.EndsWith("\""))
        return ident.Substring(1, ident.Length - 2);

      // Strip `backticks`
      if (ident.StartsWith("`") && ident.EndsWith("`"))
        return ident.Substring(1, ident.Length - 2);

      return ident;
    }

    private static string? NormalizeValue(string raw)
    {
      string s = raw.Trim();

      // Handle NULL literal (case-insensitive): map to null
      if (s.Equals("NULL", StringComparison.OrdinalIgnoreCase))
        return null;

      // N'...' or '...'
      if (s.Length >= 2 && (s[0] == 'N' || s[0] == 'n') && s[1] == '\'' && s.EndsWith("'"))
      {
        var inner = s.Substring(2, s.Length - 3);
        return inner.Replace("''", "'"); // unescape doubled quotes
      }
      if (s.Length >= 2 && s[0] == '\'' && s.EndsWith("'"))
      {
        var inner = s.Substring(1, s.Length - 2);
        return inner.Replace("''", "'");
      }

      // ""..."" (rare as string literal in SQL Server; supported just in case)
      if (s.Length >= 2 && s[0] == '"' && s.EndsWith("\""))
      {
        var inner = s.Substring(1, s.Length - 2);
        return inner.Replace("\"\"", "\"");
      }

      // Bare token (number, date literal without quotes, identifiers, etc.)
      return s;
    }
  }

}
