using Babesiosis.Core.Assertions;
using Babesiosis.Core.Excel.Styles;
using Babesiosis.Core.Extensions;
using NPOI.SS.UserModel;
using NPOI.SS.Util;
using NPOI.XSSF.UserModel;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;

namespace Babesiosis.Core.Excel
{
  public class ExcelWriter
  {
    private XSSFWorkbook _workbook;
    private Dictionary<string, ISheet> _sheets = new Dictionary<string, ISheet>();
    private Dictionary<string, ICellStyle> _styles = new Dictionary<string, ICellStyle>();
    private Dictionary<string, IFont> _fonts = new Dictionary<string, IFont>();

    private Lazy<ICellStyle> _defaultStyle;
    private Lazy<ICellStyle> _dateStyle;
    private Lazy<ICellStyle> _currencyStyle;
    private Lazy<ICellStyle> _boldStyle;
    private Lazy<ICellStyle> _numberStyle;
    private Lazy<ICellStyle> _decimalStyle;
    private int _defaultFontSize = 10;
    private Lazy<IFont> _defaultFont;
    private Lazy<IFont> _boldFont;

    public ExcelWriter(int defaultFontSize = 10)
    {
      _defaultFontSize = defaultFontSize;
      _workbook = new XSSFWorkbook();
      _defaultStyle = new Lazy<ICellStyle>(GetDefaultStyle);
      _dateStyle = new Lazy<ICellStyle>(GetDateStyle);
      _currencyStyle = new Lazy<ICellStyle>(GetCurrencyStyle);
      _boldStyle = new Lazy<ICellStyle>(GetBoldStyle);
      _numberStyle = new Lazy<ICellStyle>(GetNumberStyle);
      _decimalStyle = new Lazy<ICellStyle>(GetDecimalStyle);
      _defaultFont = new Lazy<IFont>(GetDefaultFont);
      _boldFont = new Lazy<IFont>(GetBoldFont);
    }

    public ICellStyle DefaultStyle => _defaultStyle.Value;
    public ICellStyle DateStyle => _dateStyle.Value;
    public ICellStyle CurrencyStyle => _currencyStyle.Value;
    public ICellStyle BoldStyle => _boldStyle.Value;
    public IFont DefaultFont => _defaultFont.Value;
    public IFont BoldFont => _boldFont.Value;

    public ISheet CreateSheet(string sheetName)
    {
      if (!_sheets.ContainsKey(sheetName))
      {
        var sheet = _workbook.CreateSheet(sheetName.Truncate(30));
        _sheets.Add(sheetName, sheet);
      }

      return _sheets[sheetName];
    }

    public IFont CreateFont(FontOptions options)
    {
      if (_fonts.ContainsKey(options.FontName))
      {
        return _fonts[options.FontName];
      }

      var font = _workbook.CreateFont();
      _fonts.Add(options.FontName, font);

      if (options.FontColor != Color.Empty)
      {
        font.Color = options.FontColor.ToExcelColor().Index;
      }
      font.IsBold = options.IsBold;
      font.IsItalic = options.IsItalic;
      font.FontHeightInPoints = options.Size;
      return font;
    }

    public ICellStyle CreateStyle(StyleOptions options)
    {
      if (_styles.ContainsKey(options.StyleName))
      {
        return _styles[options.StyleName];
      }

      var style = _workbook.CreateCellStyle();
      _styles.Add(options.StyleName, style);

      style.VerticalAlignment = options.VerticalAlignment.ToExcelVertical();
      style.Alignment = options.HorizontalAlignment.ToExcelHorizontal();
      style.FillPattern = options.Fill.ToExcelFill();
      style.FillForegroundColor = options.ForegroundColor == Color.Empty ? (short)0 : options.ForegroundColor.ToExcelColor().Index;
      style.WrapText = options.WrapText;
      style.BorderTop = options.TopBorder != null ? options.TopBorder.Border.ToExcelBorder() : BorderStyle.None;
      style.BorderBottom = options.BottomBorder != null ? options.BottomBorder.Border.ToExcelBorder() : BorderStyle.None;
      style.BorderLeft = options.LeftBorder != null ? options.LeftBorder.Border.ToExcelBorder() : BorderStyle.None;
      style.BorderRight = options.RightBorder != null ? options.RightBorder.Border.ToExcelBorder() : BorderStyle.None;

      if (options.Format.HasValue())
      {
        var format = _workbook.CreateDataFormat();
        style.DataFormat = format.GetFormat(options.Format);
      }

      if (options.Font != null)
      {
        IFont font = CreateFont(options.Font);
        style.SetFont(font);
      }

      return style;
    }

    public void CreateRow(ISheet sheet, int rowIndex)
    {
      sheet.CreateRow(rowIndex);
    }

    public void CreateRow(ISheet sheet,
      int index,
      short rowHeight,
      object[] values,
      IFont font = null,
      ICellStyle style = null)
    {
      var row = sheet.CreateRow(index);
      row.Height = rowHeight;

      var iCell = 0;
      while (iCell < values.Length)
      {
        var value = values[iCell];
        CreateCell(sheet, row.RowNum, iCell, value, font, style);

        iCell++;
      }
    }

    public void CreateRow(ISheet sheet,
      int index,
      object[] values,
      IFont font = null,
      ICellStyle style = null)
    {
      var row = sheet.CreateRow(index);

      var iCell = 0;
      while (iCell < values.Length)
      {
        var value = values[iCell];
        CreateCell(sheet, row.RowNum, iCell, value, font, style);

        iCell++;
      }
    }

    public ICell CreateCell(ISheet sheet,
      int rowIndex,
      int colIndex,
      object value,
      IFont font = null,
      ICellStyle style = null)
    {
      if (style == null)
      {
        style = DefaultStyle;
      }

      if (font == null)
      {
        font = DefaultFont;
      }

      var row = sheet.GetRow(rowIndex);
      var cell = row.CreateCell(colIndex);

      if (style != null)
      {
        cell.CellStyle = style;
      }

      if (font != null)
      {
        Assertion.IsNotNull(style, "Style cannot be null when font is provided");
        style.SetFont(font);
      }

      if (value is double || value is double?)
      {
        cell.SetCellValue(Convert.ToDouble(value));
      }
      else if (value is decimal || value is decimal?)
      {
        cell.SetCellValue(Convert.ToDouble(value));
      }
      else if (value is int || value is int?)
      {
        cell.SetCellValue(Convert.ToDouble(value));
      }
      else if (value is short || value is short?)
      {
        cell.SetCellValue(Convert.ToInt16(value));
      }
      else if (value is long || value is long?)
      {
        cell.SetCellValue(Convert.ToInt64(value));
      }
      else if (value is DateTime || value is DateTime?)
      {
        cell.SetCellValue(Convert.ToDateTime(value));
      }
      else if (value is bool || value is bool?)
      {
        cell.SetCellValue(Convert.ToBoolean(value));
      }
      else
      {
        cell.SetCellValue(Convert.ToString(value));
      }

      return cell;
    }

    public void SetRowStyle(ISheet sheet, int rowIndex, ICellStyle style)
    {
      var row = sheet.GetRow(rowIndex);
      Assertion.IsNotNull(row, $"Row index {rowIndex} is invalid");

      int numberOfColumns = row.PhysicalNumberOfCells;
      for (int i = 0; i < numberOfColumns; i++)
      {
        row.GetCell(i, MissingCellPolicy.CREATE_NULL_AS_BLANK).CellStyle = style;
      }
    }

    public void SetCellStyle(ISheet sheet, string columnReference, int rowIndex, ICellStyle style)
    {
      var cellReference = new CellReference($"{columnReference}{rowIndex}");
      var row = sheet.GetRow(cellReference.Row);
      Assertion.IsNotNull(row, $"Cell reference {columnReference}:{rowIndex} is invalid");
      var cell = row.GetCell(cellReference.Col);

      cell.CellStyle = style;
    }

    public void SetCellStyle(ISheet sheet, int colIndex, int rowIndex, ICellStyle style)
    {
      var row = sheet.GetRow(rowIndex);
      var cell = row.GetCell(colIndex);

      Assertion.IsNotNull(cell, $"Cell address {colIndex}:{rowIndex} is invalid");

      cell.CellStyle = style;
    }

    public void SetBoldRowStyle(ISheet sheet, int rowIndex)
    {
      SetRowStyle(sheet, rowIndex, _boldStyle.Value);
    }

    public void SetDateCellStyle(ISheet sheet, string columnReference, int rowIndex)
    {
      SetCellStyle(sheet, columnReference, rowIndex, _dateStyle.Value);
    }

    public void SetDateCellStyle(ISheet sheet, int colIndex, int rowIndex)
    {
      SetCellStyle(sheet, colIndex, rowIndex, _dateStyle.Value);
    }

    public void SetCurrencyCellStyle(ISheet sheet, string columnReference, int rowIndex)
    {
      SetCellStyle(sheet, columnReference, rowIndex, _currencyStyle.Value);
    }

    public void SetCurrencyCellStyle(ISheet sheet, int colIndex, int rowIndex)
    {
      SetCellStyle(sheet, colIndex, rowIndex, _currencyStyle.Value);
    }

    public void SetNumberCellStyle(ISheet sheet, int colIndex, int rowIndex)
    {
      SetCellStyle(sheet, colIndex, rowIndex, _numberStyle.Value);
    }

    public void SetDecimalCellStyle(ISheet sheet, int colIndex, int rowIndex)
    {
      SetCellStyle(sheet, colIndex, rowIndex, _decimalStyle.Value);
    }

    public void Autosize()
    {
      foreach (var sheet in _sheets)
      {
        int numberOfColumns = sheet.Value.GetRow(0).PhysicalNumberOfCells;
        for (int i = 0; i < numberOfColumns; i++)
        {
          sheet.Value.AutoSizeColumn(i);
          GC.Collect();
        }
      }
    }

    public void MergeCells(ISheet sheet, int firstRow, int lastRow, int firstCol, int lastCol)
    {
      CellRangeAddress merge = new CellRangeAddress(firstRow, lastRow, firstCol, lastCol);
      sheet.AddMergedRegion(merge);
    }

    public void Save(Stream stream)
    {
      _workbook.Write(stream, true);
    }

    public ISheet GetSheetAt(int index)
    {
      return _workbook.GetSheetAt(index);
    }

    ICellStyle GetDefaultStyle()
    {
      return CreateStyle(new StyleOptions()
      {
        HorizontalAlignment = Direction.Left,
        Font = CreateDefaultFontOptions(),
      });
    }

    ICellStyle GetDateStyle()
    {
      return CreateStyle(new StyleOptions()
      {
        Format = StyleOptions.DATE_FORMAT,
        Font = CreateDefaultFontOptions(),
        HorizontalAlignment = Direction.Left,
      });
    }

    ICellStyle GetCurrencyStyle()
    {
      return CreateStyle(new StyleOptions()
      {
        Format = StyleOptions.CURRENCY_FORMAT,
        Font = CreateDefaultFontOptions(),
        HorizontalAlignment = Direction.Left,
      });
    }

    ICellStyle GetNumberStyle()
    {
      return CreateStyle(new StyleOptions()
      {
        Font = CreateDefaultFontOptions(),
        HorizontalAlignment = Direction.Right,
      });
    }

    ICellStyle GetDecimalStyle()
    {
      return CreateStyle(new StyleOptions()
      {
        Format = StyleOptions.DECIMAL_TWO_PLACES_FORMAT,
        Font = CreateDefaultFontOptions(),
        HorizontalAlignment = Direction.Right,
      });
    }

    ICellStyle GetBoldStyle()
    {
      return CreateStyle(new StyleOptions()
      {
        HorizontalAlignment = Direction.Left,
        Font = new FontOptions()
        {
          IsBold = true,
          Size = _defaultFontSize
        }
      });
    }

    IFont GetDefaultFont()
    {
      return CreateFont(new FontOptions()
      {
        Size = _defaultFontSize
      });
    }

    IFont GetBoldFont()
    {
      return CreateFont(new FontOptions()
      {
        Size = _defaultFontSize,
        IsBold = true
      });
    }
    FontOptions CreateDefaultFontOptions()
    {
      return new FontOptions { Size = _defaultFontSize };
    }

    public XSSFWorkbook GetWorkbook()
    {
      return _workbook;
    }

    public void SetWorkbook(XSSFWorkbook workbook)
    {
      _workbook = workbook;
    }
  }
}
