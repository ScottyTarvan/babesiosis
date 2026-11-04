using Babesiosis.Core.Excel.Styles;
using NPOI.SS.UserModel;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Globalization;
using System.Text;

namespace Babesiosis.Core.Excel
{
    public static class Extensions
  {
    public static string GetSafeStringValue(this IRow row, int index)
    {
      var cell = row.GetCell(index);

      if (cell != null)
      {
        return cell.StringCellValue;
      }

      return null;
    }

    public static decimal GetSafeNumericValue(this IRow row, int index)
    {
      var cell = row.GetCell(index);
      
      if(cell != null)
      { 
        if(cell.CellType == CellType.String)
        {
          try
          {
            return Convert.ToDecimal(cell.StringCellValue);
          }
          catch (SystemException)
          {
            return 0m;
          }
          
        }
        return (decimal)cell.NumericCellValue;
      } 

      return 0m;
    }

    public static DateTime GetSafeDateValue(this IRow row, int index, string dateFormat = "dd/MM/yyyy")
    {
      var cell = row.GetCell(index);

      if (cell != null && cell.CellType == CellType.Formula)
      {
        return DateTime.ParseExact(cell.StringCellValue, dateFormat, CultureInfo.InvariantCulture, DateTimeStyles.None);
      }
      else if (cell != null)
      {
        return cell.DateCellValue.Value;
      }

      return DateTime.Now;
    }

    public static VerticalAlignment ToExcelVertical(this Direction direction)
    {
      if(direction == Direction.Top)
      {
        return VerticalAlignment.Top;
      }
      else if (direction == Direction.Bottom)
      {
        return VerticalAlignment.Bottom;
      }

      return VerticalAlignment.Center;
    }

    public static HorizontalAlignment ToExcelHorizontal(this Direction direction)
    {
      if (direction == Direction.Left)
      {
        return HorizontalAlignment.Left;
      }
      else if (direction == Direction.Right)
      {
        return HorizontalAlignment.Right;
      }

      return HorizontalAlignment.Left;
    }

    public static FillPattern ToExcelFill(this Fill fill)
    {
      if (fill == Fill.Solid)
      {
        return FillPattern.SolidForeground;
      }
      
      return FillPattern.NoFill;
    }

    public static BorderStyle ToExcelBorder(this Border border)
    {
      if (border == Border.Double)
      {
        return BorderStyle.Double;
      }
      else if (border == Border.Dashed)
      {
        return BorderStyle.Dashed;
      }
      if (border == Border.Thin)
      {
        return BorderStyle.Thin;
      }
      if (border == Border.Thick)
      {
        return BorderStyle.Thick;
      }
      return BorderStyle.None;
    }

    /// <summary>
    /// Not all colors are supported, see https://poi.apache.org/apidocs/4.0/org/apache/poi/ss/usermodel/IndexedColors.html
    /// </summary>
    /// <param name="color"></param>
    /// <returns></returns>
    public static IndexedColors ToExcelColor(this Color color)
    {
      IndexedColors indexedColor = IndexedColors.ValueOf(color.Name);
      Assertions.Assertion.IsNotNull(indexedColor, $"Color {color} is invalid");
      return indexedColor;
    }
  }
}
