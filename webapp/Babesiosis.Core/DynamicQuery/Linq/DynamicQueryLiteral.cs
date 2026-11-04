using Babesiosis.Core.ViewModels;
using Newtonsoft.Json.Linq;
using System;
using System.Globalization;

namespace Babesiosis.Core.DynamicQuery.Linq
{
  /// <summary>
  /// Turns a filter value as it arrives on the wire into the typed literal a condition compares
  /// against (platform/list-queries.md §3.2).
  /// <para>
  /// The typing rules are the ones the list helpers have always applied, kept so that every
  /// filter which worked before returns the same rows: number-like text is read as a number,
  /// the number's text decides its type (whole numbers are <see cref="int"/>, then
  /// <see cref="long"/>, then <see cref="decimal"/>; anything with a decimal point is
  /// <see cref="double"/>), text that reads as a date becomes a date, a lookup object
  /// contributes its integer value, and everything else stays text.
  /// </para>
  /// <para>
  /// Dates are read month-first (<see cref="CultureInfo.InvariantCulture"/>), which is what the
  /// production hosts did; a date value is cut to whole seconds, as its text form always was.
  /// </para>
  /// </summary>
  internal static class DynamicQueryLiteral
  {
    /// <summary>Unwraps a <see cref="JValue"/> so the rest of the builder sees plain CLR values.</summary>
    public static object Unwrap(object token) => token is JValue value ? value.Value : token;

    public static object From(object raw)
    {
      raw = Unwrap(raw);

      if (raw is string text && decimal.TryParse(text, NumberStyles.Any, CultureInfo.InvariantCulture, out var number))
        raw = number;

      switch (raw)
      {
        case null:
          return null;
        case decimal or double or float:
          return ParseNumber(Convert.ToDecimal(raw, CultureInfo.InvariantCulture).ToString(CultureInfo.InvariantCulture));
        case DateTime date:
          return new DateTime(date.Ticks - date.Ticks % TimeSpan.TicksPerSecond, DateTimeKind.Unspecified);
        case JArray:
          throw new NotSupportedException("A list value is only valid for operators this filter does not support.");
      }

      if (DateTime.TryParse(Convert.ToString(raw, CultureInfo.InvariantCulture), CultureInfo.InvariantCulture, DateTimeStyles.None, out var parsed))
        return parsed;

      switch (raw)
      {
        case string value:
          return value;
        case JObject lookup:
          return lookup.ToObject<NameValueViewModel<int>>().Value;
        case bool flag:
          return flag;
        default:
          return ParseNumber(Convert.ToString(raw, CultureInfo.InvariantCulture));
      }
    }

    /// <summary>
    /// The text a text operator searches for on a text field (§3.5): exactly what was typed.
    /// A value that did not arrive as text keeps its literal form; a date the JSON reader
    /// recognised is written back in the ISO form it arrived in.
    /// </summary>
    public static object ForTextSearch(object raw)
    {
      raw = Unwrap(raw);

      return raw switch
      {
        null => null,
        string text => text,
        DateTime date => date.ToString("yyyy-MM-dd'T'HH:mm:ss.FFFFFFFK", CultureInfo.InvariantCulture),
        _ => From(raw),
      };
    }

    private static object ParseNumber(string text)
    {
      if (text.Contains('.')) return double.Parse(text, CultureInfo.InvariantCulture);
      if (int.TryParse(text, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out var small)) return small;
      if (long.TryParse(text, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture, out var large)) return large;
      return decimal.Parse(text, NumberStyles.AllowLeadingSign, CultureInfo.InvariantCulture);
    }
  }
}
