using System;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// Picks the parser for a declared format.
  ///
  /// <para>
  /// A class with virtual members rather than a static helper, so a controller can hold it as a
  /// field and a test can substitute a fake parser without a container. It has no state and no
  /// dependencies, so <c>new SourceParserFactory()</c> at a call site is as legitimate as resolving
  /// one — the parser module stays free of DI.
  /// </para>
  ///
  /// <para>
  /// Note what this does not do: it never looks at a file name. PRD §6 requires the *declared*
  /// format to win over the extension, so that a .txt holding pipe-separated data parses and a .csv
  /// that is really a workbook fails honestly instead of being silently re-interpreted.
  /// </para>
  /// </summary>
  public class SourceParserFactory
  {
    /// <summary>The PRD §4 wire value for <see cref="SourceFileType.Excel"/>.</summary>
    public const string ExcelWireValue = "EXCEL";

    /// <summary>The PRD §4 wire value for <see cref="SourceFileType.Delimited"/>.</summary>
    public const string DelimitedWireValue = "DELIMITED";

    /// <summary>The PRD §4 wire value for <see cref="SourceFileType.FixedWidth"/>.</summary>
    public const string FixedWidthWireValue = "FIXED_WIDTH";

    /// <summary>
    /// The parser for <paramref name="fileType"/>. Throws <c>UNSUPPORTED_FILE_TYPE</c> for anything
    /// outside the enum — which is reachable, because an integer off the wire cast to an enum is not
    /// validated by the runtime.
    /// </summary>
    public virtual ISourceParser For(SourceFileType fileType)
    {
      switch (fileType)
      {
        case SourceFileType.Delimited:
          return new DelimitedSourceParser();

        case SourceFileType.Excel:
          return new ExcelSourceParser();

        case SourceFileType.FixedWidth:
          return new FixedWidthSourceParser();

        default:
          throw SourceParseException.UnsupportedFileType(
            $"'{fileType}' is not a source format this system can parse.");
      }
    }

    /// <summary>
    /// The parser for a PRD §4 wire value — <c>EXCEL</c>, <c>DELIMITED</c>, <c>FIXED_WIDTH</c>.
    /// Convenience for the HTTP layer, which receives the string form.
    /// </summary>
    public virtual ISourceParser For(string fileType)
    {
      return For(FromWireValue(fileType));
    }

    /// <summary>
    /// Translates a PRD §4 wire value to <see cref="SourceFileType"/>.
    ///
    /// <para>
    /// Written out rather than delegated to <c>Enum.Parse</c> because the two vocabularies do not
    /// match: the wire says <c>FIXED_WIDTH</c> and the enum member is <c>FixedWidth</c>. A parse
    /// would fail on precisely the value most likely to be sent, and the underscore-free spellings
    /// are accepted too so a client that sends <c>FIXEDWIDTH</c> gets a parser rather than a
    /// support ticket.
    /// </para>
    /// </summary>
    public static SourceFileType FromWireValue(string fileType)
    {
      var value = (fileType ?? string.Empty).Trim().Replace("_", string.Empty);

      if (value.Equals("DELIMITED", StringComparison.OrdinalIgnoreCase))
      {
        return SourceFileType.Delimited;
      }

      if (value.Equals("EXCEL", StringComparison.OrdinalIgnoreCase))
      {
        return SourceFileType.Excel;
      }

      if (value.Equals("FIXEDWIDTH", StringComparison.OrdinalIgnoreCase))
      {
        return SourceFileType.FixedWidth;
      }

      throw SourceParseException.UnsupportedFileType(
        $"'{fileType}' is not a source format this system can parse. " +
        $"Expected {ExcelWireValue}, {DelimitedWireValue} or {FixedWidthWireValue}.");
    }

    /// <summary>The wire value for a <see cref="SourceFileType"/>, for responses and persistence.</summary>
    public static string ToWireValue(SourceFileType fileType)
    {
      switch (fileType)
      {
        case SourceFileType.Delimited:
          return DelimitedWireValue;

        case SourceFileType.Excel:
          return ExcelWireValue;

        case SourceFileType.FixedWidth:
          return FixedWidthWireValue;

        default:
          throw SourceParseException.UnsupportedFileType(
            $"'{fileType}' is not a source format this system can parse.");
      }
    }
  }
}
