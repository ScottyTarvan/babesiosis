using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Babesiosis.Core.Excel
{
  public class ExcelReader
  {
    private XSSFWorkbook _workbook;
    private ISheet _sheet;

    public bool isSheetValid;

    public ExcelReader(Stream stream, int sheet = 0)
    {
      stream.Position = 0;
      _workbook = new XSSFWorkbook(stream);
      _sheet = _workbook.GetSheetAt(sheet);
    }
    public ExcelReader(Stream stream, string sheet)
    {
      stream.Position = 0;
      _workbook = new XSSFWorkbook(stream);
      _sheet = _workbook.GetSheet(sheet);
      isSheetValid = _sheet != null;
    }
    public void SetActiveSheet(string sheet)
    {
      _sheet = _workbook.GetSheet(sheet);
      isSheetValid = _sheet != null;
    }

    public IEnumerable<IRow> ReadRows()
    {
      for (int i = _sheet.FirstRowNum; i <= _sheet.LastRowNum; i++)
      {
        IRow row = _sheet.GetRow(i);
        if (row == null) continue;
        if (row.Cells.All(d => d.CellType == CellType.Blank)) continue;
        yield return row;
      }
    }

    public string GetSheetName(int sheetInd = 0)
    {
      return _workbook.GetSheetName(sheetInd);
    }
  }
}
