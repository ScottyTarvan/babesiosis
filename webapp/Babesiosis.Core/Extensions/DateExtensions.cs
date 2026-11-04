using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Extensions
{
  public static class DateExtensions
  {
    public static DateTime ToStartOfDay(this DateTime date)
    {
      return new DateTime(date.Year, date.Month, date.Day);
    }

    public static DateTime ToEndOfDay(this DateTime date)
    {
      return new DateTime(date.Year, date.Month, date.Day, 23, 59, 59);
    }

    public static DateTime ToStartOfMonth(this DateTime date)
    {
      return new DateTime(date.Year, date.Month, 1);
    }

    public static DateTime ToEndOfMonth(this DateTime date)
    {
      return new DateTime(date.Year, date.Month, DateTime.DaysInMonth(date.Year, date.Month));
    }

    public static int MonthDiff(this DateTime date, DateTime endDate)
    {
      int months = 0;
      while(date.ToEndOfMonth() <= endDate.ToEndOfMonth())
      {
        date = date.AddMonths(1);
        months++;
      }

      return months;
    }
  }
}
