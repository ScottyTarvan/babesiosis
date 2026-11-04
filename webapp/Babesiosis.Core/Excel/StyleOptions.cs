using Babesiosis.Core.Excel.Styles;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Text;

namespace Babesiosis.Core.Excel
{
    public class StyleOptions
  {
    //public const string CURRENCY_FORMAT = "€ ### 000;-€ ### 000";
    public const string CURRENCY_FORMAT = "_-€* ###\\ ###\\ ###\\ ###.00;";
    public const string DATE_FORMAT = "yyyy/MM/dd";
    public const string DECIMAL_TWO_PLACES_FORMAT = "#,##0.00";
    public string StyleName { get; set; } = Guid.NewGuid().ToString();
    public Direction HorizontalAlignment { get; set; }
    public Direction VerticalAlignment { get; set; }
    public Fill Fill { get; set; }
    public Color ForegroundColor { get; set; } = Color.Empty;
    public BorderOptions LeftBorder { get; set; }
    public BorderOptions RightBorder { get; set; }
    public BorderOptions TopBorder { get; set; }
    public BorderOptions BottomBorder { get; set; }
    public bool WrapText { get; set; }
    public string Format { get; set; }
    public FontOptions Font { get; set; }
  }
}
