using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// The parse configuration for one source file — the in-memory twin of PRD §4
  /// <c>source_definition</c>. It is a plain settings bag with no validation in its setters, because
  /// it arrives straight off a request body: every rule is enforced by the parser at parse time so a
  /// bad value produces a coded <see cref="SourceParseException"/> and not a binding error the UI
  /// cannot explain.
  /// </summary>
  public class SourceParseOptions
  {
    /// <summary>
    /// The format to parse as. PRD §6 is explicit that the *declared* format wins over the file
    /// extension — a .txt holding a workbook is a parse failure, not a silent re-interpretation.
    /// </summary>
    public SourceFileType FileType { get; set; } = SourceFileType.Delimited;

    /// <summary>
    /// Whether a header row supplies the field names. When false the fields are named
    /// <c>COLUMN_1 … COLUMN_N</c> off the first data row's width (PRD §2 Story 2).
    /// </summary>
    public bool HasHeaderRow { get; set; } = true;

    /// <summary>
    /// Which row is the header, 1-based, counted over non-blank records only. Rows above it are
    /// discarded — this is how a file with a title banner above the real header is handled.
    /// Ignored when <see cref="HasHeaderRow"/> is false.
    /// </summary>
    public int HeaderRowIndex { get; set; } = 1;

    /// <summary>
    /// The field separator for <see cref="SourceFileType.Delimited"/>. Any single character: comma
    /// and pipe are UI presets, but tab and anything else must work, so this is a raw
    /// <see cref="char"/> and not an enum.
    /// </summary>
    public char Delimiter { get; set; } = ',';

    /// <summary>
    /// The quote character for <see cref="SourceFileType.Delimited"/>. A delimiter inside a quoted
    /// field does not split it, and a doubled quote inside one resolves to a single literal quote.
    /// </summary>
    public char QuoteCharacter { get; set; } = '"';

    /// <summary>
    /// Text encoding name, resolved by <see cref="ResolveEncoding"/>.
    /// TODO(spec) Q7: UTF-8 is the interim default and the field is exposed; the accepted set is
    /// whatever the platform reports through <see cref="Encoding.GetEncodings"/> rather than a
    /// hard-coded list, so it tracks the runtime instead of drifting from it.
    /// </summary>
    public string Encoding { get; set; } = "UTF-8";

    /// <summary>
    /// Worksheet to read for <see cref="SourceFileType.Excel"/>. Null or blank means the first
    /// sheet. <see cref="SourceParseResult.SheetNames"/> comes back populated so the UI can offer a
    /// picker without a second round trip.
    /// </summary>
    public string SheetName { get; set; }

    /// <summary>
    /// Column layout for <see cref="SourceFileType.FixedWidth"/>, 1-based. Validated in full before
    /// the file is opened.
    /// </summary>
    public IList<FixedWidthColumn> FixedWidthLayout { get; set; }

    /// <summary>
    /// Ceiling on preview rows. PRD §2 Story 2 fixes 10; it is a property rather than a constant
    /// only so tests can pin smaller numbers. Values below 1 are treated as 0 — fields still
    /// extract, the preview is simply empty.
    /// </summary>
    public int MaxSampleRows { get; set; } = 10;

    /// <summary>
    /// Turns <see cref="Encoding"/> into a real encoding, or refuses it.
    ///
    /// <para>
    /// Two steps on purpose. <c>Encoding.GetEncoding</c> resolves aliases ("utf8", "latin1") that a
    /// straight list lookup would reject, and the <see cref="System.Text.Encoding.GetEncodings"/>
    /// check then confirms the result is actually registered in this process — on .NET the
    /// single-byte code pages are absent unless a provider was registered, and a name that resolves
    /// but cannot decode would fail later as a mangled field name instead of an honest error.
    /// </para>
    /// </summary>
    public Encoding ResolveEncoding()
    {
      var name = string.IsNullOrWhiteSpace(Encoding) ? "UTF-8" : Encoding.Trim();

      Encoding resolved;
      try
      {
        resolved = System.Text.Encoding.GetEncoding(name);
      }
      catch (ArgumentException)
      {
        throw SourceParseException.ParseFailed(
          $"'{name}' is not a supported text encoding.");
      }

      if (!System.Text.Encoding.GetEncodings().Any(e => e.CodePage == resolved.CodePage))
      {
        throw SourceParseException.ParseFailed(
          $"'{name}' is not a supported text encoding.");
      }

      return resolved;
    }
  }

  /// <summary>
  /// One column of a fixed-width layout: a name plus the 1-based character window it occupies.
  /// Positions are 1-based because that is what an analyst reads off a ruler in a text editor, and
  /// PRD §2 Story 2 fixes it; the parser subtracts one exactly once, at extraction.
  /// </summary>
  public class FixedWidthColumn
  {
    public FixedWidthColumn()
    {
    }

    public FixedWidthColumn(string name, int start, int length)
    {
      Name = name;
      Start = start;
      Length = length;
    }

    /// <summary>Field name. Blank falls back to <c>COLUMN_{ordinal}</c>, matching a blank header cell.</summary>
    public string Name { get; set; }

    /// <summary>1-based first character of the window. Must be ≥ 1.</summary>
    public int Start { get; set; }

    /// <summary>Character count. Must be ≥ 1 — a zero-length column can never carry a value.</summary>
    public int Length { get; set; }

    /// <summary>1-based last character of the window, inclusive.</summary>
    public int End
    {
      get { return Start + Length - 1; }
    }
  }

  /// <summary>
  /// Decodes a source stream to text under the caller's <see cref="SourceParseOptions.Encoding"/>.
  ///
  /// <para>
  /// It lives beside the option it applies, and is shared by the delimited and fixed-width parsers
  /// so the two cannot decode differently — a BOM stripped by one and not the other would show up
  /// as a corrupted first field name in exactly one format, which is a miserable bug to chase.
  /// </para>
  /// </summary>
  internal static class SourceTextReader
  {
    /// <summary>
    /// Reads the whole stream. Whole, not streamed, because PRD §7 caps a source at 5 MB and pins
    /// parsing inside the request: buffering the lot buys a quoted field that spans line breaks and
    /// a single decode pass, at a bounded cost.
    ///
    /// <para>
    /// Byte-order-mark detection is left on, so a file whose BOM contradicts the declared encoding
    /// is read as its BOM says. That is the friendlier failure: the analyst picked "UTF-8" from a
    /// drop-down, the file is UTF-16, and honouring the declared name would hand them a field list
    /// of interleaved null characters instead of their columns. The explicit strip afterwards covers
    /// the case where the mark survives decoding — PRD §6 forbids a BOM reaching the first field
    /// name.
    /// </para>
    ///
    /// <para>The stream is left open: the caller owns it and may re-parse it under new options.</para>
    /// </summary>
    internal static string ReadAll(Stream stream, SourceParseOptions options)
    {
      var encoding = options.ResolveEncoding();

      if (stream.CanSeek)
      {
        stream.Position = 0;
      }

      string text;
      using (var reader = new StreamReader(stream, encoding, true, 8192, true))
      {
        text = reader.ReadToEnd();
      }

      if (text.Length > 0 && text[0] == ParsedField.BomCharacter)
      {
        text = text.Substring(1);
      }

      return text;
    }
  }
}
