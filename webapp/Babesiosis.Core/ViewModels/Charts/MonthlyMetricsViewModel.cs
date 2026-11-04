using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.ViewModels.Charts
{
  public class MonthlyMetricsViewModel
  {
    public int Year { get; set; }
    public int Month { get; set; }
    public string MonthName { get; set; }
    public List<WeeklyMetricsViewModel> Weeks { get; set; } = new List<WeeklyMetricsViewModel>();

    public override string ToString()
    {
      return $"{Year}:{Month}";
    }
  }
}
