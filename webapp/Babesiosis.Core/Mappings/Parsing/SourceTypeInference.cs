using System;
using System.Collections.Generic;
using System.Globalization;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// Guesses a source field's type from the handful of values in the preview.
  ///
  /// <para>
  /// TODO(spec) Q2: the answer is advisory and nothing may gate on it. That decision is what makes a
  /// ten-row sample defensible — the cost of a wrong guess is an advisory icon next to a binding the
  /// analyst can save anyway, so the design-time gain of never reading the whole file outweighs the
  /// occasional miss. If this ever starts driving coercion, the sample size becomes a correctness
  /// bug rather than a display one.
  /// </para>
  /// </summary>
  public static class SourceTypeInference
  {
    public const string String = "STRING";
    public const string Integer = "INTEGER";
    public const string Decimal = "DECIMAL";
    public const string Date = "DATE";
    public const string Boolean = "BOOLEAN";

    /// <summary>
    /// The words treated as boolean. Deliberately excludes <c>0</c> and <c>1</c>: a column of flags
    /// stored as digits is indistinguishable from a column of small integers, and calling it BOOLEAN
    /// would be a guess about intent rather than about shape.
    /// </summary>
    private static readonly HashSet<string> BooleanWords =
      new HashSet<string>(StringComparer.OrdinalIgnoreCase)
      {
        "true", "false", "yes", "no", "y", "n"
      };

    /// <summary>
    /// Narrowest type every non-blank value satisfies, or <see cref="String"/> when they disagree.
    ///
    /// <para>
    /// Blank values are skipped rather than counted against the column, because a blank is an absent
    /// value in every one of these types; a column of five integers and five empties is an integer
    /// column with gaps, not a string column.
    /// </para>
    ///
    /// <para>
    /// An all-blank or empty sample answers <see cref="String"/> rather than null so callers never
    /// have to branch. STRING is the honest answer there — nothing was seen that narrows it.
    /// </para>
    ///
    /// <para>
    /// Order matters. BOOLEAN is tested first because its vocabulary cannot collide with the numeric
    /// tests once digits are excluded; INTEGER precedes DECIMAL so a whole-number column is not
    /// widened; DATE comes last because <c>DateTime.TryParse</c> is the most permissive of the four
    /// and would otherwise claim values the tighter tests already explained.
    /// </para>
    /// </summary>
    public static string Infer(IEnumerable<string> values)
    {
      var seen = 0;
      var allBoolean = true;
      var allInteger = true;
      var allDecimal = true;
      var allDate = true;

      if (values != null)
      {
        foreach (var raw in values)
        {
          if (string.IsNullOrWhiteSpace(raw))
          {
            continue;
          }

          seen++;
          var value = raw.Trim();

          if (allBoolean && !BooleanWords.Contains(value))
          {
            allBoolean = false;
          }

          if (allInteger && !IsInteger(value))
          {
            allInteger = false;
          }

          if (allDecimal && !IsDecimal(value))
          {
            allDecimal = false;
          }

          if (allDate && !IsDate(value))
          {
            allDate = false;
          }

          if (!allBoolean && !allInteger && !allDecimal && !allDate)
          {
            return String;
          }
        }
      }

      if (seen == 0)
      {
        return String;
      }

      if (allBoolean)
      {
        return Boolean;
      }

      if (allInteger)
      {
        return Integer;
      }

      if (allDecimal)
      {
        return Decimal;
      }

      return allDate ? Date : String;
    }

    /// <summary>
    /// Invariant culture throughout, and no thousands separators. A source file is machine output;
    /// reading it through the server's current culture is how a European decimal comma silently
    /// becomes a thousands separator, and the answer changes with the machine the parse ran on.
    /// </summary>
    private static bool IsInteger(string value)
    {
      long parsed;
      return long.TryParse(value, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture,
        out parsed);
    }

    private static bool IsDecimal(string value)
    {
      decimal parsed;
      return decimal.TryParse(value,
        NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint,
        CultureInfo.InvariantCulture, out parsed);
    }

    /// <summary>
    /// Date parsing is guarded, because <c>DateTime.TryParse</c> on its own is far too eager: under
    /// the invariant culture it accepts <c>1,5</c> and answers a date, so a European decimal that no
    /// numeric test claimed would be advised to the analyst as DATE.
    ///
    /// <para>
    /// The guard is the cheapest thing that separates a written date from a number that happens to
    /// contain punctuation — a real date carries a separator between its parts and is never as short
    /// as three characters. Anything shorter or unseparated has already been offered to the numeric
    /// tests, which are stricter and answer first.
    /// </para>
    /// </summary>
    private static bool IsDate(string value)
    {
      if (value.Length < 6 || value.IndexOfAny(DateSeparators) < 0)
      {
        return false;
      }

      DateTime parsed;
      return DateTime.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.None,
        out parsed);
    }

    /// <summary>The characters a written date puts between its parts: <c>2026-08-24</c>, <c>24/08/2026</c>, <c>24 Aug 2026</c>.</summary>
    private static readonly char[] DateSeparators = { '-', '/', '.', ' ' };
  }
}
