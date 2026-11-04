using NPOI.SS.UserModel;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// Workbooks, both .xlsx and .xls.
  ///
  /// <para>
  /// Deliberately <b>not</b> built on <c>Babesiosis.Core.Excel.ExcelReader</c>. That class news up
  /// an <c>XSSFWorkbook</c> directly, which reads only the OOXML format and throws on a .xls the
  /// analyst is equally entitled to upload. <c>WorkbookFactory.Create</c> sniffs the container and
  /// returns the right implementation for either, which is the whole reason this parser does not
  /// reuse it.
  /// </para>
  /// </summary>
  public class ExcelSourceParser : ISourceParser
  {
    public SourceParseResult Parse(Stream stream, SourceParseOptions options)
    {
      if (stream == null)
      {
        throw SourceParseException.ParseFailed("No source file was supplied.");
      }

      var settings = options ?? new SourceParseOptions();

      using (var seekable = AsSeekable(stream))
      using (var workbook = OpenWorkbook(seekable))
      {
        var sheetNames = new List<string>();
        for (var i = 0; i < workbook.NumberOfSheets; i++)
        {
          sheetNames.Add(workbook.GetSheetName(i));
        }

        if (sheetNames.Count == 0)
        {
          throw SourceParseException.ParseFailed("The workbook contains no worksheets.");
        }

        var sheet = SelectSheet(workbook, settings.SheetName, sheetNames);
        var rows = MaterialiseRows(sheet);

        if (rows.Count == 0)
        {
          throw SourceParseException.ParseFailed(
            $"Worksheet '{sheet.SheetName}' contains no rows.");
        }

        IReadOnlyList<string> header;
        IEnumerable<string[]> dataRows;

        if (settings.HasHeaderRow)
        {
          // The worksheet row as Excel numbers it (mappings-source.md §3.2): blank rows above the
          // header do not shift it, because the analyst reads the number straight off Excel.
          var headerIndex = settings.HeaderRowIndex < 1 ? 1 : settings.HeaderRowIndex;
          var lastRowNumber = sheet.LastRowNum + 1;
          if (headerIndex > lastRowNumber)
          {
            throw SourceParseException.ParseFailed(
              $"Header row {headerIndex} was not found — worksheet '{sheet.SheetName}' ends at " +
              $"row {lastRowNumber}.", headerIndex);
          }

          var headerRow = sheet.GetRow(headerIndex - 1);
          if (headerRow == null || IsBlank(headerRow) || Width(headerRow) == 0)
          {
            throw SourceParseException.ParseFailed(
              $"Header row {headerIndex} of worksheet '{sheet.SheetName}' is empty.",
              headerIndex);
          }

          var width = Width(headerRow);
          header = ReadRow(headerRow, width);
          // Blank rows are already dropped, so the sample is every non-blank row below the header.
          dataRows = rows.Where(r => r.RowNum > headerRow.RowNum).Select(r => ReadRow(r, width));
        }
        else
        {
          var width = Width(rows[0]);
          if (width == 0)
          {
            throw SourceParseException.ParseFailed(
              $"The first row of worksheet '{sheet.SheetName}' is empty.");
          }

          header = new string[width];
          dataRows = rows.Select(r => ReadRow(r, width));
        }

        // Sheet names ride back on the result so the UI can populate its picker from the first
        // upload. Without them the analyst would have to know the sheet name before parsing, which
        // is exactly the knowledge the parse was supposed to supply.
        return SourceParseResult.Build(header, dataRows, settings.MaxSampleRows, sheetNames);
      }
    }

    public Task<SourceParseResult> ParseAsync(Stream stream, SourceParseOptions options,
      CancellationToken cancellationToken = default)
    {
      cancellationToken.ThrowIfCancellationRequested();
      return Task.FromResult(Parse(stream, options));
    }

    /// <summary>
    /// NPOI needs to seek around a workbook's container. A request body stream may not allow it, so
    /// a non-seekable stream is copied first. Bounded by the 5 MB upload ceiling the endpoint
    /// enforces before this module is ever reached.
    /// </summary>
    private static Stream AsSeekable(Stream stream)
    {
      if (stream.CanSeek)
      {
        stream.Position = 0;
        // Wrapped so the using in Parse disposes the wrapper and leaves the caller's stream open —
        // the caller owns it and re-parses it when the analyst changes a parse option.
        return new NonDisposingStreamWrapper(stream);
      }

      var buffer = new MemoryStream();
      stream.CopyTo(buffer);
      buffer.Position = 0;
      return buffer;
    }

    /// <summary>
    /// Opens the workbook, turning every NPOI failure into <c>PARSE_FAILED</c>.
    ///
    /// <para>
    /// The catch is broad because NPOI's failure modes for "these bytes are not a workbook" are
    /// not one type — a zero-byte stream, a CSV renamed to .xlsx and an encrypted file each throw
    /// something different. PRD §6 wants one answer for all of them: the declared format could not
    /// read this file.
    /// </para>
    /// </summary>
    private static IWorkbook OpenWorkbook(Stream stream)
    {
      try
      {
        return WorkbookFactory.Create(stream);
      }
      catch (Exception ex)
      {
        throw SourceParseException.ParseFailed(
          "The file could not be read as an Excel workbook. " + ex.Message);
      }
    }

    private static ISheet SelectSheet(IWorkbook workbook, string sheetName,
      IReadOnlyList<string> sheetNames)
    {
      if (string.IsNullOrWhiteSpace(sheetName))
      {
        return workbook.GetSheetAt(0);
      }

      var sheet = workbook.GetSheet(sheetName.Trim());
      if (sheet == null)
      {
        throw SourceParseException.ParseFailed(
          $"Worksheet '{sheetName}' was not found. The workbook contains: " +
          string.Join(", ", sheetNames) + ".");
      }

      return sheet;
    }

    /// <summary>
    /// The rows that carry anything, in order.
    ///
    /// <para>
    /// A worksheet is sparse: <c>GetRow</c> answers null for a row that was never written, and a row
    /// object can survive with nothing but blank cells after its content is deleted. Both would
    /// otherwise land in the preview as empty rows, so they are dropped here. The header row is NOT
    /// counted in this list: it is addressed by its physical row number (<see cref="IRow.RowNum"/>),
    /// so a blank row above it never shifts the number the analyst chose.
    /// </para>
    /// </summary>
    private static List<IRow> MaterialiseRows(ISheet sheet)
    {
      var rows = new List<IRow>();

      for (var i = sheet.FirstRowNum; i <= sheet.LastRowNum; i++)
      {
        var row = sheet.GetRow(i);
        if (row == null || IsBlank(row))
        {
          continue;
        }

        rows.Add(row);
      }

      return rows;
    }

    private static bool IsBlank(IRow row)
    {
      return row.Cells.Count == 0 || row.Cells.All(c => c.CellType == CellType.Blank);
    }

    private static int Width(IRow row)
    {
      // LastCellNum is the last used index plus one, and -1 for a row with no cells at all.
      return row.LastCellNum < 0 ? 0 : row.LastCellNum;
    }

    private static string[] ReadRow(IRow row, int width)
    {
      var values = new string[width];
      for (var i = 0; i < width; i++)
      {
        values[i] = ReadCell(row.GetCell(i));
      }

      return values;
    }

    /// <summary>
    /// One cell as text.
    ///
    /// <para>
    /// Formula cells resolve to the value Excel last computed and stored, never to the formula
    /// string. PRD §6 is explicit, and the alternative is worse than it sounds: NPOI can evaluate
    /// formulas, but evaluation of a workbook we did not write can hit unsupported functions and
    /// external links, and the analyst is trying to confirm the numbers they already see in Excel.
    /// The cached value is that number.
    /// </para>
    /// </summary>
    private static string ReadCell(ICell cell)
    {
      if (cell == null)
      {
        return string.Empty;
      }

      switch (cell.CellType)
      {
        case CellType.String:
          return cell.StringCellValue ?? string.Empty;

        case CellType.Numeric:
          return ReadNumeric(cell);

        case CellType.Boolean:
          return cell.BooleanCellValue ? "TRUE" : "FALSE";

        case CellType.Formula:
          return ReadCachedFormulaResult(cell);

        // Blank, Error and Unknown all mean "no value an analyst can bind". An error cell is shown
        // as empty rather than as #DIV/0! so a broken formula does not become a plausible-looking
        // sample value.
        default:
          return string.Empty;
      }
    }

    private static string ReadCachedFormulaResult(ICell cell)
    {
      switch (cell.CachedFormulaResultType)
      {
        case CellType.String:
          return cell.StringCellValue ?? string.Empty;

        case CellType.Numeric:
          return ReadNumeric(cell);

        case CellType.Boolean:
          return cell.BooleanCellValue ? "TRUE" : "FALSE";

        default:
          return string.Empty;
      }
    }

    /// <summary>
    /// Numbers and dates share one cell type in Excel; only the number format tells them apart.
    ///
    /// <para>
    /// Whole numbers are rendered without a decimal point so an integer column infers as INTEGER
    /// rather than DECIMAL, and the general format is fixed-point rather than round-trip so a long
    /// account number does not reach the analyst as <c>1.234567891E+09</c>. Invariant culture
    /// throughout — the same workbook must parse identically on every machine.
    /// </para>
    /// </summary>
    private static string ReadNumeric(ICell cell)
    {
      if (DateUtil.IsCellDateFormatted(cell))
      {
        DateTime? date = cell.DateCellValue;
        if (date.HasValue)
        {
          return date.Value.TimeOfDay == TimeSpan.Zero
            ? date.Value.ToString("yyyy-MM-dd", CultureInfo.InvariantCulture)
            : date.Value.ToString("yyyy-MM-dd HH:mm:ss", CultureInfo.InvariantCulture);
        }

        return string.Empty;
      }

      var number = cell.NumericCellValue;
      if (Math.Abs(number % 1) < double.Epsilon && Math.Abs(number) < 1e15)
      {
        return ((long)number).ToString(CultureInfo.InvariantCulture);
      }

      return number.ToString("0.##########", CultureInfo.InvariantCulture);
    }

    /// <summary>
    /// Passes every call through to the caller's stream but swallows <c>Dispose</c>.
    ///
    /// <para>
    /// NPOI takes ownership of what it is handed, and the upload endpoint re-parses the same buffer
    /// when the analyst changes a delimiter or a sheet. Letting the workbook close it would make the
    /// second parse fail on a disposed stream — a bug that only appears on the second interaction.
    /// </para>
    /// </summary>
    private sealed class NonDisposingStreamWrapper : Stream
    {
      private readonly Stream _inner;

      public NonDisposingStreamWrapper(Stream inner)
      {
        _inner = inner;
      }

      public override bool CanRead => _inner.CanRead;
      public override bool CanSeek => _inner.CanSeek;
      public override bool CanWrite => false;
      public override long Length => _inner.Length;

      public override long Position
      {
        get { return _inner.Position; }
        set { _inner.Position = value; }
      }

      public override void Flush()
      {
        _inner.Flush();
      }

      public override int Read(byte[] buffer, int offset, int count)
      {
        return _inner.Read(buffer, offset, count);
      }

      public override long Seek(long offset, SeekOrigin origin)
      {
        return _inner.Seek(offset, origin);
      }

      public override void SetLength(long value)
      {
        throw new NotSupportedException();
      }

      public override void Write(byte[] buffer, int offset, int count)
      {
        throw new NotSupportedException();
      }

      protected override void Dispose(bool disposing)
      {
        // Intentionally does not dispose _inner.
      }
    }
  }
}
