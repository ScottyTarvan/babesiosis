using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.DynamicQuery
{
  public enum DynamicQueryGridFormats
  {
    None = 0,
    [Description("decimal")]
    Decimal = 1,
    [Description("currency")]
    Currency = 2,
    [Description("perxcent")]
    Percent = 3,
    [Description("thousands")]
    Thousands = 4,
    [Description("millions")]
    Millions = 5,
    [Description("billions")]
    Billions = 6,
    [Description("trillions")]
    Trillions = 7,
    [Description("shortDate")]
    ShortDate = 8,
    [Description("longDate")]
    LongDate = 9,
    [Description("shortTime")]
    ShortTime = 10,
    [Description("longTime")]
    LongTime = 11,
    [Description("day")]
    Day = 12,
    [Description("month")]
    Month = 13,
    [Description("quarter")]
    Quarter = 14,
    [Description("year")]
    Year = 15
  }
}
