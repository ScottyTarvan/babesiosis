namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// The three source shapes a mapping can be built from (PRD §4 <c>source_definition.file_type</c>).
  ///
  /// <para>
  /// This enum belongs to the parser, not to persistence. The parser module is deliberately free of
  /// EF and of the <c>meta.</c> entities so it can be exercised with <c>new</c>, so it cannot reach
  /// for a model-layer enum; the persistence layer converts to and from this one at its boundary.
  /// </para>
  ///
  /// <para>
  /// Values are pinned so a stored integer keeps its meaning. The wire form the PRD fixes
  /// (<c>EXCEL</c> / <c>DELIMITED</c> / <c>FIXED_WIDTH</c>) is translated by
  /// <see cref="SourceParserFactory.FromWireValue"/> — never by <c>Enum.Parse</c> against these
  /// member names, which do not match.
  /// </para>
  /// </summary>
  public enum SourceFileType
  {
    /// <summary>Any single-character-separated text file — .csv, .txt, tab-separated, pipe.</summary>
    Delimited = 1,

    /// <summary>.xlsx or .xls. Read through NPOI's <c>WorkbookFactory</c> so both formats work.</summary>
    Excel = 2,

    /// <summary>Column positions supplied by the analyst as (name, start, length), 1-based.</summary>
    FixedWidth = 3
  }
}
