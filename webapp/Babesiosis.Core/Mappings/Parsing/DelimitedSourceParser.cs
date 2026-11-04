using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// Separated-value text: comma, pipe, tab, or whatever single character the analyst typed.
  ///
  /// <para>
  /// Hand-rolled on purpose. There is no CSV library in this solution and PRD §0.1 forbids adding
  /// one, so the quoting rules are implemented here as an explicit character state machine rather
  /// than as <c>string.Split</c> plus repair work. Split cannot express the one rule that actually
  /// matters — a delimiter inside quotes is data — and every attempt to patch it up afterwards gets
  /// the doubled-quote case wrong.
  /// </para>
  /// </summary>
  public class DelimitedSourceParser : ISourceParser
  {
    public SourceParseResult Parse(Stream stream, SourceParseOptions options)
    {
      if (stream == null)
      {
        throw SourceParseException.ParseFailed("No source file was supplied.");
      }

      var settings = options ?? new SourceParseOptions();
      ValidateSeparators(settings);

      var text = SourceTextReader.ReadAll(stream, settings);
      if (text.Length == 0)
      {
        // PRD §6: a zero-byte file is a parse failure, distinct from a file with a header and no
        // data rows, which is not. There is no line to name — the failure is the whole file.
        throw SourceParseException.ParseFailed("The source file is empty.");
      }

      var records = SplitRecords(text, settings.Delimiter, settings.QuoteCharacter);
      if (records.Count == 0)
      {
        throw SourceParseException.ParseFailed("The source file contains no rows.");
      }

      IReadOnlyList<string> header;
      IEnumerable<string[]> dataRows;

      if (settings.HasHeaderRow)
      {
        // A value below 1 is taken as 1 rather than refused. The column's schema default is 1 and an
        // unset integer on the wire arrives as 0, so refusing would turn a client's omission into a
        // parse failure the analyst cannot act on.
        var headerIndex = settings.HeaderRowIndex < 1 ? 1 : settings.HeaderRowIndex;
        if (records.Count < headerIndex)
        {
          throw SourceParseException.ParseFailed(
            $"Header row {headerIndex} was not found — the file has {records.Count} row(s).",
            headerIndex);
        }

        header = records[headerIndex - 1];
        dataRows = records.Skip(headerIndex);
      }
      else
      {
        // No header: the field count comes from the first record and the names are generated. The
        // nulls are what ParsedField.Disambiguate turns into COLUMN_1 … COLUMN_N.
        header = new string[records[0].Length];
        dataRows = records;
      }

      return SourceParseResult.Build(header, dataRows, settings.MaxSampleRows);
    }

    public Task<SourceParseResult> ParseAsync(Stream stream, SourceParseOptions options,
      CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();
      return Task.FromResult(Parse(stream, options));
    }

    /// <summary>
    /// Refuses separator settings that cannot describe a file, before anything is read.
    ///
    /// <para>
    /// Each of these would otherwise parse "successfully" into nonsense — one giant column, or a
    /// file where every field looks quoted — and the analyst would be left staring at a field list
    /// with no error to explain it. Failing loudly here is the whole point.
    /// </para>
    /// </summary>
    private static void ValidateSeparators(SourceParseOptions options)
    {
      if (options.Delimiter == '\0')
      {
        throw SourceParseException.ParseFailed("A delimiter character is required.");
      }

      if (options.Delimiter == '\r' || options.Delimiter == '\n')
      {
        throw SourceParseException.ParseFailed(
          "A line break cannot be used as the delimiter.");
      }

      if (options.QuoteCharacter != '\0' && options.Delimiter == options.QuoteCharacter)
      {
        throw SourceParseException.ParseFailed(
          "The delimiter and the quote character must differ.");
      }
    }

    /// <summary>
    /// The state machine. Walks the text once and yields one <c>string[]</c> per record.
    ///
    /// <para>
    /// Three rules it exists to get right, all from PRD §6:
    /// a delimiter inside a quoted field does not split it;
    /// a doubled quote inside a quoted field is one literal quote;
    /// LF and CRLF both end a record, and a line break inside quotes ends nothing.
    /// </para>
    ///
    /// <para>
    /// A quote only opens a field when it is the field's first character. Anywhere else it is data:
    /// <c>5" pipe</c> is a measurement, not a malformed field, and treating it as an opening quote
    /// would swallow the rest of the file into one value.
    /// </para>
    /// </summary>
    private static List<string[]> SplitRecords(string text, char delimiter, char quote)
    {
      var records = new List<string[]>();
      var record = new List<string>();
      var field = new StringBuilder();

      var inQuotes = false;
      var atFieldStart = true;
      var recordHadQuotes = false;
      var line = 1;
      var quoteOpenedOnLine = 1;
      var i = 0;

      while (i < text.Length)
      {
        var c = text[i];

        if (inQuotes)
        {
          if (c == quote)
          {
            if (i + 1 < text.Length && text[i + 1] == quote)
            {
              field.Append(quote);
              i += 2;
            }
            else
            {
              inQuotes = false;
              i++;
            }

            continue;
          }

          // Line breaks inside quotes are data. The counter still advances so a later error names
          // the right line of the file.
          if (c == '\n')
          {
            line++;
          }

          field.Append(c);
          i++;
          continue;
        }

        if (c == quote && atFieldStart)
        {
          inQuotes = true;
          recordHadQuotes = true;
          quoteOpenedOnLine = line;
          atFieldStart = false;
          i++;
          continue;
        }

        if (c == delimiter)
        {
          record.Add(field.ToString());
          field.Clear();
          atFieldStart = true;
          i++;
          continue;
        }

        if (c == '\r' || c == '\n')
        {
          i += c == '\r' && i + 1 < text.Length && text[i + 1] == '\n' ? 2 : 1;
          line++;

          record.Add(field.ToString());
          field.Clear();
          Emit(records, record, recordHadQuotes);

          record.Clear();
          recordHadQuotes = false;
          atFieldStart = true;
          continue;
        }

        field.Append(c);
        atFieldStart = false;
        i++;
      }

      if (inQuotes)
      {
        throw SourceParseException.ParseFailed(
          $"A quoted field opened on line {quoteOpenedOnLine} is never closed.",
          quoteOpenedOnLine);
      }

      // Anything still buffered is the final record of a file that does not end in a line break.
      if (field.Length > 0 || record.Count > 0)
      {
        record.Add(field.ToString());
        Emit(records, record, recordHadQuotes);
      }

      return records;
    }

    /// <summary>
    /// Adds a record, unless it is a blank line.
    ///
    /// <para>
    /// A blank line reaches here as a single empty field. Emitting it would put an all-empty row in
    /// the ten-row preview and feed empties into type inference, and — more visibly — a file that
    /// simply ends in a newline followed by nothing would gain a phantom trailing row. The quote
    /// flag is what separates a blank line from a line holding one deliberately empty quoted field,
    /// which is real data and is kept.
    /// </para>
    /// </summary>
    private static void Emit(List<string[]> records, List<string> record, bool recordHadQuotes)
    {
      if (!recordHadQuotes && record.Count == 1 && record[0].Length == 0)
      {
        return;
      }

      records.Add(record.ToArray());
    }
  }
}
