using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// Positional text: the analyst supplies the column windows, the file supplies only characters.
  ///
  /// <para>
  /// This is the one format whose field list does not come from the file. There is nothing in a
  /// fixed-width file that says where one column ends and the next begins, so
  /// <see cref="SourceParseOptions.FixedWidthLayout"/> is the sole authority and a header row, if
  /// present, is only something to skip.
  /// </para>
  /// </summary>
  public class FixedWidthSourceParser : ISourceParser
  {
    public SourceParseResult Parse(Stream stream, SourceParseOptions options)
    {
      var settings = options ?? new SourceParseOptions();

      // Layout first, before the stream is touched. A contradictory layout is the analyst's mistake
      // and is knowable without a single byte of their file; reading first would mean a 5 MB decode
      // whose only possible outcome is the error we already had in hand.
      var layout = ValidateLayout(settings.FixedWidthLayout);

      if (stream == null)
      {
        throw SourceParseException.ParseFailed("No source file was supplied.");
      }

      var text = SourceTextReader.ReadAll(stream, settings);
      if (text.Length == 0)
      {
        throw SourceParseException.ParseFailed("The source file is empty.");
      }

      var lines = SplitLines(text);
      if (lines.Count == 0)
      {
        throw SourceParseException.ParseFailed("The source file contains no rows.");
      }

      var skip = 0;
      if (settings.HasHeaderRow)
      {
        var headerIndex = settings.HeaderRowIndex < 1 ? 1 : settings.HeaderRowIndex;
        if (lines.Count < headerIndex)
        {
          throw SourceParseException.ParseFailed(
            $"Header row {headerIndex} was not found — the file has {lines.Count} row(s).",
            headerIndex);
        }

        skip = headerIndex;
      }

      // Names come from the layout even when a header row exists, because the header of a
      // fixed-width file is itself just padded text and slicing it would re-derive names the
      // analyst already gave us — differently, wherever a name does not fill its window.
      var header = layout.Select(c => c.Name).ToList();
      var dataRows = lines.Skip(skip).Select(l => Slice(l, layout));

      return SourceParseResult.Build(header, dataRows, settings.MaxSampleRows);
    }

    public Task<SourceParseResult> ParseAsync(Stream stream, SourceParseOptions options,
      CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();
      return Task.FromResult(Parse(stream, options));
    }

    /// <summary>
    /// Rejects a layout that cannot describe a file, with <c>INVALID_FIXED_WIDTH_LAYOUT</c>.
    ///
    /// <para>
    /// Positions are 1-based (PRD §2 Story 2), so <c>Start</c> below 1 is out of the file, and a
    /// length of zero or less names no characters at all. Overlap is checked against the previous
    /// window after ordering by start, which is sufficient once the list is sorted: any pair that
    /// overlaps must do so with its immediate predecessor somewhere in the ordering.
    /// </para>
    ///
    /// <para>
    /// Gaps between windows are legal and common — filler and reserved regions are exactly what a
    /// fixed-width layout leaves out. Only overlap is a contradiction, because it would put one
    /// character in two fields.
    /// </para>
    /// </summary>
    private static IReadOnlyList<FixedWidthColumn> ValidateLayout(
      IList<FixedWidthColumn> layout)
    {
      if (layout == null || layout.Count == 0)
      {
        throw SourceParseException.InvalidFixedWidthLayout(
          "A fixed-width source needs at least one column in its layout.");
      }

      var ordinal = 0;
      foreach (var column in layout)
      {
        ordinal++;

        if (column == null)
        {
          throw SourceParseException.InvalidFixedWidthLayout(
            $"Column {ordinal} of the fixed-width layout is missing.");
        }

        if (column.Start < 1)
        {
          throw SourceParseException.InvalidFixedWidthLayout(
            $"Column {ordinal} ('{column.Name}') starts at position {column.Start}. " +
            "Positions are 1-based and must be 1 or greater.");
        }

        if (column.Length < 1)
        {
          throw SourceParseException.InvalidFixedWidthLayout(
            $"Column {ordinal} ('{column.Name}') has a length of {column.Length}. " +
            "Lengths must be 1 or greater.");
        }
      }

      var ordered = layout.OrderBy(c => c.Start).ThenBy(c => c.End).ToList();
      for (var i = 1; i < ordered.Count; i++)
      {
        var previous = ordered[i - 1];
        var current = ordered[i];

        if (current.Start <= previous.End)
        {
          throw SourceParseException.InvalidFixedWidthLayout(
            $"Columns '{previous.Name}' ({previous.Start}-{previous.End}) and " +
            $"'{current.Name}' ({current.Start}-{current.End}) overlap.");
        }
      }

      // Returned in the analyst's declared order, not the sorted order: the sort exists only to make
      // the overlap check linear, while ordinals must match the list the analyst is looking at.
      return layout.ToList();
    }

    /// <summary>
    /// Splits on LF and CRLF, discarding blank lines for the same reason the delimited parser does —
    /// a blank line in a positional file is filler, and every field it could yield is empty.
    /// </summary>
    private static List<string> SplitLines(string text)
    {
      return text
        .Replace("\r\n", "\n")
        .Replace('\r', '\n')
        .Split('\n')
        .Where(l => l.Trim().Length > 0)
        .ToList();
    }

    /// <summary>
    /// Cuts one line into its windows.
    ///
    /// <para>
    /// A line shorter than the layout yields empty strings for the windows past its end rather than
    /// throwing: short final records and optional trailing columns are ordinary in these files, and
    /// refusing to preview a file over a missing trailing field would be useless to the analyst.
    /// </para>
    ///
    /// <para>
    /// Values are trimmed. Padding is how the format encodes a boundary, not part of the value, so
    /// leaving it in would make every preview cell and every inferred type wrong. This is unrelated
    /// to the per-binding <c>trim</c> flag, which is a load-time instruction for the loader.
    /// </para>
    /// </summary>
    private static string[] Slice(string line, IReadOnlyList<FixedWidthColumn> layout)
    {
      var values = new string[layout.Count];

      for (var i = 0; i < layout.Count; i++)
      {
        var column = layout[i];
        var start = column.Start - 1;

        if (start >= line.Length)
        {
          values[i] = string.Empty;
          continue;
        }

        var available = line.Length - start;
        var take = column.Length < available ? column.Length : available;
        values[i] = line.Substring(start, take).Trim();
      }

      return values;
    }
  }
}
